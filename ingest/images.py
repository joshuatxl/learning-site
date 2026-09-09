"""Scrape a feed entry's article page for what the feed omits: a cover image,
a short excerpt, the readable body text, and whether the page allows being
shown inside an <iframe>. Best-effort; never raises.

Fetch once with `fetch_page(url)` and pass the html/headers to the `*_from`
helpers — the pipeline does this so each article page is fetched a single time.
"""
from __future__ import annotations

import html as _htmllib
import re
import urllib.request
from urllib.parse import urljoin, urlparse

_OG_IMAGE = (
    r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']',
    r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',
)
_DESC = (
    r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']*)["\']',
    r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+property=["\']og:description["\']',
    r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)["\']',
    r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+name=["\']description["\']',
)
_P_RE = re.compile(r"<p[^>]*>(.*?)</p>", re.IGNORECASE | re.DOTALL)
_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")

# Whole regions that are never article prose — stripped before <p> scanning.
_STRIP_BLOCKS = re.compile(
    r"<(script|style|pre|code|table|figure|figcaption|nav|header|footer|aside|form|svg|noscript)"
    r"[^>]*>.*?</\1>",
    re.IGNORECASE | re.DOTALL,
)

_JUNK_IMAGE_RE = re.compile(r"(arxiv-logo|/static/browse/|placeholder|default-og)", re.I)

_BOILERPLATE_RE = re.compile(
    r"(journey to advance and democratize|sign up|subscribe now|cookie|accept all|"
    r"enable javascript|we use cookies|create an account|all rights reserved|"
    r"disrupt 20\d\d|industry stages|off tickets|newsletter|arxiv-issued doi|"
    r"submission history|view email|which authors of this paper|"
    r"\d{1,2}:\d{2}\s*[ap]m|image credits?:)",
    re.I,
)
_ABSTRACT_RE = re.compile(
    r'<blockquote[^>]*class="[^"]*abstract[^"]*"[^>]*>(.*?)</blockquote>',
    re.IGNORECASE | re.DOTALL,
)

# Signals that a "paragraph" is actually code / CLI output / a metrics dump.
_CODEY_RE = re.compile(
    r"(\$\s|\suv\srun\s|--[a-z][\w-]+\s|\s\\\s|={6,}|/v\d+\b|localhost:\d|"
    r"\bpassed\s*\(|\bpassed\)|\bpython\s+-m\s|\bnpm\s+(run|i|install)\b|"
    r"\bpip\s+install\b|\bcurl\s+-|\bwget\s|```|\bjson\b\s*:\s*\d|\.jsonl\b|"
    r"results/|data/test|--n-threads|--max-tokens)",
    re.I,
)


# A realistic browser header set — some publishers (e.g. openai.com) 403 a
# bare urllib request.
_BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
}


def _fetch(url: str, timeout: int = 8):
    """Return (html, headers-dict-lowercased) or ("", {})."""
    if not url:
        return "", {}
    try:
        req = urllib.request.Request(url, headers=_BROWSER_HEADERS)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            html = resp.read(500_000).decode("utf-8", errors="ignore")
            headers = {k.lower(): v for k, v in resp.headers.items()}
            return html, headers
    except Exception as e:  # network error, timeout, blocked — non-fatal
        print(f"  page fetch failed for {url}: {e}")
        return "", {}


# Hosts that pass the header check but still won't render in an iframe
# (client-side frame-busting, JS-gated content, etc.) — always use reader text.
_NEVER_FRAME = ("openai.com",)


def fetch_page(url: str):
    """Fetch once; return (html, frameable). `frameable` is True only when no
    response header forbids embedding the page in a cross-origin iframe."""
    html, headers = _fetch(url)
    return html, _frameable(headers, url)


def jina_markdown(url: str, timeout: int = 25) -> str:
    """Render a JS-only page through the free r.jina.ai reader → markdown.
    Used only as a last resort when direct scraping yields nothing."""
    if not url:
        return ""
    try:
        req = urllib.request.Request(
            "https://r.jina.ai/" + url, headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read(300_000).decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"  jina reader failed for {url}: {e}")
        return ""


def _frameable(headers: dict, url: str = "") -> bool:
    if any(host in url for host in _NEVER_FRAME):
        return False
    xfo = (headers.get("x-frame-options") or "").lower()
    if "deny" in xfo or "sameorigin" in xfo or "allow-from" in xfo:
        return False
    csp = (headers.get("content-security-policy") or "").lower()
    m = re.search(r"frame-ancestors([^;]*)", csp)
    if m:
        directive = m.group(1).strip()
        # only a bare wildcard is permissive enough to rely on
        return directive in ("", "*") or directive.split() == ["*"]
    return True


def _first(patterns, html: str):
    for pat in patterns:
        m = re.search(pat, html, re.IGNORECASE)
        if m and m.group(1).strip():
            return m.group(1).strip()
    return None


def _clean(s: str) -> str:
    s = _htmllib.unescape(_TAG_RE.sub(" ", s or ""))
    return _WS_RE.sub(" ", s).strip()


def _is_prose(text: str) -> bool:
    if len(text) < 40 or _BOILERPLATE_RE.search(text) or _CODEY_RE.search(text):
        return False
    letters = sum(c.isalpha() or c.isspace() for c in text)
    if letters / len(text) < 0.75:          # too many symbols/digits
        return False
    if "." not in text and "?" not in text and "!" not in text:
        return False
    return True


# --- images --------------------------------------------------------------
def extract_image(entry, html: str | None = None) -> str | None:
    if getattr(entry, "media_thumbnail", None):
        return entry.media_thumbnail[0].get("url")
    if getattr(entry, "media_content", None):
        return entry.media_content[0].get("url")
    for link in entry.get("links", []):
        if link.get("type", "").startswith("image"):
            return link.get("href")
    link = entry.get("link", "")
    return og_image_from(html if html is not None else _fetch(link)[0], link)


def og_image(url: str):
    return og_image_from(_fetch(url)[0], url)


def og_image_from(html: str, url: str):
    raw = _first(_OG_IMAGE, html)
    if not raw:
        return None
    img = urljoin(url, _htmllib.unescape(raw.strip()))
    if not urlparse(img).scheme.startswith("http") or _JUNK_IMAGE_RE.search(img):
        return None
    return img


# --- text -------------------------------------------------------------
def _abstract(html: str):
    m = _ABSTRACT_RE.search(html)
    return re.sub(r"^abstract:?\s*", "", _clean(m.group(1)), flags=re.I) if m else ""


def page_excerpt(url: str) -> str:
    return page_excerpt_from(_fetch(url)[0], url)


def page_excerpt_from(html: str, url: str) -> str:
    if "arxiv.org" in url:
        abs = _abstract(html)
        if abs:
            return abs
    stripped = _STRIP_BLOCKS.sub(" ", html)
    for m in _P_RE.finditer(stripped):
        para = _clean(m.group(1))
        if _is_prose(para):
            return para
    desc = _clean(_first(_DESC, html) or "")
    return desc if len(desc) >= 20 and not _BOILERPLATE_RE.search(desc) else ""


def page_text(url: str, max_chars: int = 16000) -> str:
    return page_text_from(_fetch(url)[0], url, max_chars)


def page_text_from(html: str, url: str, max_chars: int = 16000) -> str:
    """Readable article body — substantial prose <p> elements joined by blank
    lines. Code blocks, tables, nav and CLI/metrics dumps are excluded."""
    if "arxiv.org" in url:
        abs = _abstract(html)
        if abs:
            return abs[:max_chars]

    stripped = _STRIP_BLOCKS.sub(" ", html)
    out, total = [], 0
    for m in _P_RE.finditer(stripped):
        para = _clean(m.group(1))
        if not _is_prose(para):
            continue
        out.append(para)
        total += len(para)
        if total >= max_chars:
            break
    return "\n\n".join(out)[:max_chars]
