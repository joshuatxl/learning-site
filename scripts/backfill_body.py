"""One-off: re-scrape every stored article into the reader model — a small
HTML fragment (headings / paragraphs / lists / code blocks) + the `frameable`
flag. Falls back to the source feed's own text for pages we can't scrape
(e.g. openai.com, which serves a JS-only shell).

Run: python scripts/backfill_body.py
"""
import os
import re
import sys
import time

import feedparser
import frontmatter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ingest import reader  # noqa: E402
from ingest.article import READ_MORE, clean_text  # noqa: E402
from ingest.config import FEEDS, PREVIEW_CHARS  # noqa: E402
from ingest.images import (  # noqa: E402
    fetch_page,
    jina_markdown,
    og_image_from,
    page_excerpt_from,
)

NEWS_DIR = "docs/news"


def feed_text_map() -> dict[str, str]:
    """url -> richest HTML/text the feed itself carries for that entry."""
    out: dict[str, str] = {}
    for name, url in FEEDS:
        try:
            f = feedparser.parse(url)
        except Exception as e:
            print(f"  feed {name}: {e}")
            continue
        for e in f.entries:
            link = e.get("link", "")
            if not link:
                continue
            body = ""
            if e.get("content"):
                body = e["content"][0].get("value", "") or ""
            out[link] = body or e.get("summary", "") or ""
    print(f"  feed map: {len(out)} entries")
    return out


def main() -> int:
    feeds = feed_text_map()
    updated = skipped = 0
    for name in sorted(os.listdir(NEWS_DIR)):
        if not name.endswith(".md") or name == "index.md":
            continue
        path = os.path.join(NEWS_DIR, name)
        post = frontmatter.load(path)
        url = str(post.get("url", "")).strip()
        title = str(post.get("title", "")).strip()
        if not url:
            continue

        html, frameable = fetch_page(url)
        body, plain = reader.extract(html, url)
        jina_img = ""

        if len(plain) < 200 and feeds.get(url):
            fb_body, fb_plain = reader.extract(feeds[url], url)
            if len(fb_plain) > len(plain):
                body, plain = fb_body, fb_plain

        if len(plain) < 200:                       # JS-only page — render via r.jina.ai
            j_body, j_plain, jina_img = reader.from_markdown(jina_markdown(url))
            if len(j_plain) > len(plain):
                body, plain = j_body, j_plain

        if len(plain) < 120:                       # last resort — the feed blurb
            blurb = clean_text(feeds.get(url, "")) or str(post.get("preview", ""))
            if len(blurb) >= 40:
                body, plain = reader.paragraphs_html(blurb), blurb

        if len(plain) < 40:
            skipped += 1
            print(f"  --  {name}  (no text anywhere)")
            continue

        preview = clean_text(plain, PREVIEW_CHARS)
        if len(preview) < 90:
            preview = clean_text(page_excerpt_from(html, url) or plain, PREVIEW_CHARS)

        post["preview"] = preview
        img = str(post.get("image", "")).strip() or jina_img or og_image_from(html, url)
        if img:
            post["image"] = img
        if frameable:
            post["frameable"] = True
        elif "frameable" in post.metadata:
            del post["frameable"]
        post.content = f"# {title}\n\n{body}\n\n{READ_MORE}({url})\n"

        with open(path, "w", encoding="utf-8") as f:
            f.write(frontmatter.dumps(post) + "\n")
        updated += 1
        print(f"  {name}  [{'iframe' if frameable else 'reader'}]  {len(body)} html chars")
        time.sleep(0.35)

    print(f"\n{updated} refreshed, {skipped} left as-is")
    return 0


if __name__ == "__main__":
    sys.exit(main())
