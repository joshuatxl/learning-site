"""Turn Article objects into the Markdown that MkDocs builds.

Front page = the "What's going on in AI?" banner, then story-card sections
by level. Level 0 (entered today) is at the top; each day every article
drops one level; level 7 (entered a week ago) is the bottom; at level 8 the
article is deleted by age_out_articles().

Cards show a plain-text preview and link to the original source. The AI
summary is produced on demand in the browser, never here.
"""
from __future__ import annotations

import html
import json
import os
import re
from datetime import date, datetime, timedelta, timezone

from .article import Article
from .config import (
    DIGEST_END,
    DIGEST_START,
    DOCS_DIR,
    GRID_END,
    GRID_START,
    INDEX_PAGE,
    NEWS_DIR,
    RETENTION_DAYS,
)


def _today() -> date:
    """Reference 'now' for aging. Override with BRIEFING_TODAY=YYYY-MM-DD
    (used for local testing / backfill); otherwise real UTC date."""
    override = os.environ.get("BRIEFING_TODAY", "").strip()
    if override:
        try:
            return date.fromisoformat(override)
        except ValueError:
            pass
    return datetime.now(timezone.utc).date()


# --- reads ---------------------------------------------------------------
def _article_files() -> list[str]:
    return [f for f in os.listdir(NEWS_DIR) if f.endswith(".md") and f != "index.md"]


def existing_slugs() -> set[str]:
    """Slugs already on disk, for cross-run dedupe (slug is date-independent)."""
    slugs = set()
    for name in _article_files():
        stem = name[:-3]
        slugs.add(stem[11:] if len(stem) > 11 and stem[10] == "-" else stem)
    return slugs


def load_articles() -> list[Article]:
    """Every live article — newest first by the day it entered the site."""
    articles = []
    for name in _article_files():
        try:
            articles.append(Article.from_file(os.path.join(NEWS_DIR, name)))
        except Exception as e:
            print(f"  skipping unreadable {name}: {e}")
    articles.sort(key=lambda a: a.title)
    articles.sort(key=lambda a: a.published, reverse=True)
    articles.sort(key=lambda a: a.entered_on, reverse=True)
    return articles


# --- writes -----------------------------------------------------------
def save_article(article: Article) -> None:
    os.makedirs(NEWS_DIR, exist_ok=True)
    with open(os.path.join(NEWS_DIR, article.filename), "w", encoding="utf-8") as f:
        f.write(article.to_markdown())
    print(f"  saved {article.filename}")


def age_out_articles() -> None:
    """Delete anything that has aged past the bottom level."""
    today = _today()
    for name in _article_files():
        path = os.path.join(NEWS_DIR, name)
        try:
            age = (today - Article.from_file(path).entered_on).days
        except Exception:
            continue
        if age > RETENTION_DAYS:
            os.remove(path)
            print(f"  removed (level {age}) {name}")


# --- front-page HTML ----------------------------------------------
def _esc(s: str) -> str:
    return html.escape(s or "")


def _meta(a: Article) -> str:
    bits = [a.source] if a.source else []
    bits.append(a.published.strftime("%b %d"))
    return _esc(" · ".join(bits))


def _story_card_html(a: Article) -> str:
    light = "" if a.image else " light"
    banner = (
        f'<img class="banner" src="{_esc(a.image)}" alt="" loading="lazy" '
        f'onerror="this.style.display=\'none\'">\n          '
        if a.image else ""
    )
    preview = f'<p class="preview clamp">{_esc(a.preview)}</p>\n            ' if a.preview else ""
    return (
        f'        <article class="story-card{light}" '
        f'data-id="{_esc(a.doc_id)}" data-href="{_esc(a.url)}" data-title="{_esc(a.title)}" '
        f'data-source="{_esc(a.source)}" data-date="{_esc(a.published.strftime("%b %d, %Y"))}" '
        f'data-image="{_esc(a.image or "")}" tabindex="0" role="link">\n'
        f'          {banner}<div class="body">\n'
        f'            <h4 class="clamp">{_esc(a.title)}</h4>\n'
        f'            {preview}<div class="meta">{_meta(a)}</div>\n'
        f'          </div>\n'
        f'        </article>'
    )


def _section_html(label: str, articles: list[Article]) -> str:
    pairs = []
    for i in range(0, len(articles), 2):
        cards = "\n".join(_story_card_html(a) for a in articles[i:i + 2])
        pairs.append(f'      <div class="pair">\n{cards}\n      </div>')
    return (
        f'  <section class="level-section">\n'
        f'    <div class="wrap">\n'
        f'      <div class="section-head">'
        f'<span class="section-dot"></span><h3>{_esc(label)}</h3><div class="rule"></div></div>\n'
        f'{chr(10).join(pairs)}\n'
        f'    </div>\n'
        f'  </section>'
    )


def _level_label(level: int) -> str:
    if level <= 0:
        return "Today"
    if level == 1:
        return "Yesterday"
    return f"{level} days ago"


def _digest_hero_html(refreshed: str) -> str:
    return (
        f'<section class="digest-hero">\n'
        f'  <span class="digest-glow"></span>\n'
        f'  <div class="wrap">\n'
        f'    <h1 class="digest-title">What&rsquo;s going on in AI?</h1>\n'
        f'    <p class="refreshed">Last refreshed {_esc(refreshed)}</p>\n'
        f'  </div>\n'
        f'</section>'
    )


def _hot_row_html(hot: list[dict]) -> str:
    if not hot:
        return ""
    chips = "".join(
        f'<a class="brief-hot-chip" href="{_esc(h["url"])}" target="_blank" rel="noopener" '
        f'title="{_esc(", ".join(h["sources"]))}">'
        f'{_esc(h["label"])}<span class="brief-hot-n">{len(h["sources"])} feeds</span></a>'
        for h in hot
    )
    return (
        '<p class="brief-hot">'
        '<span class="brief-hot-flag">Hot</span>'
        f'{chips}</p>'
    )


def _digest_window_html(text: str, when: str, hot: list[dict]) -> str:
    """The 'Today in AI' brief between the banner and the newest articles."""
    if not text.strip() and not hot:
        return f'<div class="wrap">\n  {DIGEST_START}\n  {DIGEST_END}\n</div>'
    paras = "".join(
        f"<p>{_esc(p.strip())}</p>" for p in re.split(r"\n{2,}", text) if p.strip()
    ) or "<p>Today&rsquo;s brief will appear here after the next update.</p>"
    return (
        f'<div class="wrap">\n'
        f'  {DIGEST_START}\n'
        f'  <section class="ai-brief" aria-label="Today in AI">\n'
        f'    <p class="ai-brief-kicker"><span class="ai-brief-dot"></span>Today in AI</p>\n'
        f'    {_hot_row_html(hot)}\n'
        f'    <div class="ai-brief-body">{paras}</div>\n'
        f'  </section>\n'
        f'  {DIGEST_END}\n'
        f'</div>'
    )


def _homepage_block(articles: list[Article], digest: tuple[str, str], refreshed: str) -> str:
    today = _today()
    buckets: dict[int, list[Article]] = {}
    for a in articles:
        level = max((today - a.entered_on).days, 0)
        if level <= RETENTION_DAYS:
            buckets.setdefault(level, []).append(a)

    from . import hotnews
    hot = hotnews.hot_topics(buckets.get(0, []) + buckets.get(1, []))

    parts = [_digest_hero_html(refreshed), _digest_window_html(digest[0], digest[1], hot)]
    for level in sorted(buckets):
        parts.append(_section_html(_level_label(level), buckets[level]))

    inner = "\n\n".join(parts)
    return f'<div class="briefing">\n{inner}\n</div>'


def _now_str() -> str:
    # Perth, Australia — AWST is a fixed UTC+8, no daylight saving.
    now = datetime.now(timezone(timedelta(hours=8)))
    return f"{now.day} {now:%b %Y at %H:%M} AWST"


def write_article_data(articles: list[Article]) -> None:
    """docs/article-data.json — readable article text for the popup's reader
    view (used when a publisher blocks iframe embedding). Same-origin, fetched
    once by briefing.js."""
    data = {
        a.doc_id: {
            "title": a.title,
            "url": a.url,
            "source": a.source,
            "date": a.published.strftime("%b %d, %Y"),
            "image": a.image or "",
            "body": a.body or a.preview,
            "frameable": a.frameable,
        }
        for a in articles
    }
    with open(os.path.join(DOCS_DIR, "article-data.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    print(f"  article-data.json: {len(data)} articles")


DIGEST_FILE = os.path.join(DOCS_DIR, "digest.json")


def load_digest() -> tuple[str, str]:
    """(text, 'D Mon YYYY') from docs/digest.json, or ('', '')."""
    try:
        with open(DIGEST_FILE, encoding="utf-8") as f:
            d = json.load(f)
        return str(d.get("text", "")), str(d.get("when", ""))
    except (OSError, ValueError):
        return "", ""


def write_digest(text: str) -> None:
    now = datetime.now(timezone(timedelta(hours=8)))
    when = f"{now.day} {now:%b %Y}"
    with open(DIGEST_FILE, "w", encoding="utf-8") as f:
        json.dump({"text": text.strip(), "when": when}, f, ensure_ascii=False)
    print(f"  digest.json: {len(text.strip())} chars")


def rebuild_homepage(articles: list[Article] | None = None, digest: str | None = None) -> None:
    """Regenerate docs/index.md between the markers. Frontmatter is left as-is.
    digest=None keeps the stored brief; a string replaces it (and is saved)."""
    articles = articles if articles is not None else load_articles()
    refreshed = _now_str()
    if digest is not None:
        write_digest(digest)
    write_article_data(articles)
    block = _homepage_block(articles, load_digest(), refreshed)

    if not os.path.exists(INDEX_PAGE):
        with open(INDEX_PAGE, "w", encoding="utf-8") as f:
            f.write(f"---\nhide:\n  - navigation\n  - toc\n---\n\n{GRID_START}\n{GRID_END}\n")

    with open(INDEX_PAGE, encoding="utf-8") as f:
        existing = f.read()

    if GRID_START in existing and GRID_END in existing:
        pre = existing.split(GRID_START)[0]
        post = existing.split(GRID_END)[1]
        new = f"{pre}{GRID_START}\n{block}\n{GRID_END}{post}"
    else:
        new = f"{existing.rstrip()}\n\n{GRID_START}\n{block}\n{GRID_END}\n"

    with open(INDEX_PAGE, "w", encoding="utf-8") as f:
        f.write(new)
    print(f"  front page: {len(articles)} live stories, refreshed {refreshed}")
