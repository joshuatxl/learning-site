"""The Article schema — the single contract shared by every stage of the
pipeline (and, later, the second-brain store).

Serialised to a Markdown file with YAML frontmatter via python-frontmatter.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from datetime import date, datetime, timezone

import frontmatter

READ_MORE = "[Read the full article →]"
_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug[:60].strip("-")


def clean_text(html_or_text: str, limit: int | None = None) -> str:
    """Strip HTML, collapse whitespace, optionally truncate on a word boundary."""
    text = _WS_RE.sub(" ", _TAG_RE.sub(" ", html_or_text or "")).strip()
    if limit and len(text) > limit:
        cut = text[:limit].rsplit(" ", 1)[0].rstrip(",.;:—- ")
        text = f"{cut}…"
    return text


def _parse_dt(value) -> datetime:
    """Coerce whatever frontmatter / feedparser hands us into an aware UTC datetime."""
    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value)
        except ValueError:
            dt = datetime.strptime(value[:10], "%Y-%m-%d")
    else:  # date, or None
        try:
            dt = datetime(value.year, value.month, value.day)
        except AttributeError:
            dt = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


@dataclass
class Article:
    title: str
    url: str
    source: str
    published: datetime                 # publish time from the feed (aware, UTC)
    preview: str = ""                    # plain-text excerpt of the article
    summary: str = ""                    # AI summary — only ever set on demand
    image: str | None = None
    body: str = ""                       # readable article text
    frameable: bool = False              # page allows cross-origin <iframe> embed
    fetched: str = ""                    # YYYY-MM-DD this entered the site
    stem: str = ""                       # on-disk filename stem, set by from_file

    # ------------------------------------------------------------------
    @property
    def slug(self) -> str:
        return slugify(self.title)

    @property
    def date_str(self) -> str:
        return self.published.strftime("%Y-%m-%d")

    @property
    def filename(self) -> str:
        return f"{self.date_str}-{self.slug}.md"

    @property
    def doc_id(self) -> str:
        return self.stem or f"{self.date_str}-{self.slug}"

    @property
    def entered_on(self) -> date:
        """The day this article entered the site — drives level/aging."""
        if self.fetched:
            try:
                return datetime.strptime(self.fetched[:10], "%Y-%m-%d").date()
            except ValueError:
                pass
        return self.published.date()

    # ------------------------------------------------------------------
    def to_post(self) -> frontmatter.Post:
        meta = {
            "title": self.title,
            "url": self.url,
            "source": self.source,
            "date": self.date_str,
            "published": self.published.isoformat(),
            "preview": self.preview,
        }
        if self.summary:
            meta["summary"] = self.summary
        if self.image:
            meta["image"] = self.image
        if self.frameable:
            meta["frameable"] = True
        if self.fetched:
            meta["fetched"] = self.fetched

        # The markdown body holds the full article text (used by the hover
        # preview popup); the card itself only ever shows `preview`.
        body = self.body or self.preview
        lines = [f"# {self.title}", "", body, "", f"{READ_MORE}({self.url})", ""]
        return frontmatter.Post("\n".join(lines), **meta)

    def to_markdown(self) -> str:
        return frontmatter.dumps(self.to_post())

    # ------------------------------------------------------------------
    @classmethod
    def from_file(cls, path: str) -> "Article":
        post = frontmatter.load(path)
        return cls(
            title=str(post.get("title") or os.path.basename(path)),
            url=str(post.get("url", "")),
            source=str(post.get("source", "")),
            published=_parse_dt(post.get("published") or post.get("date")),
            preview=str(post.get("preview", "")).strip(),
            summary=str(post.get("summary", "")).strip(),
            image=post.get("image"),
            body=_strip_wrapper(post.content),
            frameable=bool(post.get("frameable", False)),
            fetched=str(post.get("fetched", "")),
            stem=os.path.basename(path)[:-3],
        )


def _strip_wrapper(content: str) -> str:
    """Drop the leading '# title' and trailing 'Read the full article' line
    that to_post() adds, leaving just the article text."""
    lines = content.strip().splitlines()
    if lines and lines[0].lstrip().startswith("#"):
        lines = lines[1:]
    while lines and not lines[0].strip():
        lines = lines[1:]
    if lines and READ_MORE in lines[-1]:
        lines = lines[:-1]
    return "\n".join(lines).strip()
