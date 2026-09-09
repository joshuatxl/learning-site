"""Daily ingest: fetch -> save -> age out -> rebuild front page.

No AI summaries are generated here. Each card shows a plain-text preview of
the article; summaries are produced on demand from the browser (see
docs/javascripts/briefing.js + workers/).

Run with:  python -m ingest.pipeline
"""
from __future__ import annotations

import os
from datetime import datetime, timezone

from . import digest, hotnews, store
from .article import Article, clean_text, slugify
from .config import NEWS_DIR, PREVIEW_CHARS
from .feeds import fetch_entries
from . import reader
from .images import extract_image, fetch_page, jina_markdown, page_excerpt_from
from .render import (
    age_out_articles,
    existing_slugs,
    load_articles,
    rebuild_homepage,
    save_article,
)


def _entry_body(entry) -> str:
    """Richest text the feed gives us for an entry."""
    if entry.get("content"):
        return entry["content"][0].get("value", "") or ""
    return entry.get("summary", "") or ""


def run() -> None:
    os.makedirs(NEWS_DIR, exist_ok=True)
    seen = existing_slugs()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    new_articles: list[Article] = []

    for source, entry, published in fetch_entries():
        title = (entry.get("title") or "").strip()
        if not title:
            continue
        slug = slugify(title)
        if slug in seen:
            continue

        link = entry.get("link", "")
        html, frameable = fetch_page(link)

        # reader HTML (headings / paragraphs / lists / code blocks) + its plain text
        body, plain = reader.extract(html, link)
        jina_img = ""
        if len(plain) < 200:                               # thin — try the feed's own content
            fb_body, fb_plain = reader.extract(_entry_body(entry), link)
            if len(fb_plain) > len(plain):
                body, plain = fb_body, fb_plain
        if len(plain) < 200:                               # JS-only page — render it via r.jina.ai
            j_body, j_plain, jina_img = reader.from_markdown(jina_markdown(link))
            if len(j_plain) > len(plain):
                body, plain = j_body, j_plain
        if len(plain) < 120:                               # last resort — the feed blurb
            blurb = clean_text(_entry_body(entry))
            if len(blurb) > len(plain):
                body, plain = reader.paragraphs_html(blurb), blurb

        preview = clean_text(plain, PREVIEW_CHARS)
        if len(preview) < 90:
            preview = clean_text(page_excerpt_from(html, link) or plain, PREVIEW_CHARS)

        image = extract_image(entry, html) or ""
        if jina_img and (not image or "seo-card" in image.lower()):
            image = jina_img                       # prefer a real content image over a social card

        article = Article(
            title=title,
            url=link,
            source=source,
            published=published,
            preview=preview,
            image=image,
            body=body,
            frameable=frameable,
            fetched=today,
        )
        save_article(article)
        seen.add(slug)
        new_articles.append(article)
        print(f"[{source}] + {title}")

    age_out_articles()
    articles = load_articles()

    # "Today in AI" brief — one Gemini call over today's articles (or None to
    # keep the stored brief when there's no key / nothing new / the call fails).
    todays = [a for a in articles if a.fetched == today] or articles[:20]
    hot = hotnews.hot_topics(todays)
    if hot:
        print(f"hot: {', '.join(h['label'] + ' (' + str(len(h['sources'])) + ')' for h in hot)}")
    brief = digest.generate(todays, hot)
    rebuild_homepage(articles, digest=brief or None)

    store.upsert_articles(new_articles)
    print(f"done: {len(new_articles)} new, {len(articles)} live")


if __name__ == "__main__":
    run()
