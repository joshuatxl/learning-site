"""Turn a scraped article page into a small, safe "reader" HTML fragment:
section headings, paragraphs, lists, quotes and code blocks — and nothing
else (no nav / ads / scripts / styles / metrics tables).

`extract(html, url)` -> (reader_html, plain_text)

The fragment only ever contains this tag allow-list, with no attributes
except a validated href on <a>, so it is safe to assign with innerHTML:
  h2 h3 h4 p ul ol li blockquote pre code strong em a br
"""
from __future__ import annotations

import html as _htmllib
import re
from html.parser import HTMLParser
from urllib.parse import urljoin

_WS = re.compile(r"\s+")

_SKIP = {
    "script", "style", "noscript", "template", "svg", "math",
    "nav", "header", "footer", "aside", "form", "button", "select",
    "table", "figure", "figcaption", "iframe", "object", "video", "audio", "img",
}
_HEADINGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
_BLOCKS = _HEADINGS | {"p", "pre", "blockquote", "li"}
_INLINE_KEEP = {"a", "code", "strong", "b", "em", "i", "br"}
_VOID = {"br", "hr", "img", "meta", "link", "input", "source", "col", "wbr"}

# Containers whose class/id marks the real article body.
_CONTENT_HINT = re.compile(
    r"\b(prose|post-content|post-body|article-content|article-body|articlebody|"
    r"entry-content|blog-content|blog-post-content|markdown-body|rich-text|"
    r"story-body|content-body|main-content|post__content|c-content)\b", re.I
)
# Containers that are definitely NOT the article — comments, related, etc.
_NEG_HINT = re.compile(
    r"\b(comment|related|recirc|newsletter|promo|share|social|footer|sidebar|"
    r"subscribe|paywall|author-bio|more-from|read-next|toc|breadcrumb)\b", re.I
)

_BOILERPLATE = re.compile(
    r"(sign up|subscribe now|cookie|accept all|enable javascript|we use cookies|"
    r"create an account|all rights reserved|disrupt 20\d\d|industry stages|"
    r"off tickets|newsletter|arxiv-issued doi|submission history|view email|"
    r"which authors of this paper|\d{1,2}:\d{2}\s*[ap]m|image credits?:|"
    r"more articles from our blog|models? mentioned in this article|"
    r"datasets? mentioned in this article|test comment|read more|"
    r"related (stories|reading|posts|articles)|follow us)",
    re.I,
)
_CODEY = re.compile(
    r"(\$\s|\suv\s+run\s|--[a-z][\w-]+\s|\s\\\s|={6,}|\bpassed\s*[\(\)]|"
    r"\bpython\s+-m\s|\bnpm\s+(run|i|install)\b|\bpip\s+install\b|localhost:\d|"
    r"results/|data/test|--n-threads|--max-tokens)",
    re.I,
)


def _norm(cls_map: list, key: str) -> str:
    for k, v in cls_map:
        if k and k.lower() == key:
            return v or ""
    return ""


class _Reader(HTMLParser):
    def __init__(self, base_url: str):
        super().__init__(convert_charrefs=True)
        self.base = base_url
        self.blocks: list[str] = []
        self.depth = 0
        self._skip_from = None        # depth at which a _SKIP region started
        self._scope_from = None       # depth at which the content container opened
        self._scope_done = False      # already captured one content container
        self._buf: list[str] | None = None
        self._tag = ""
        self._pre = False
        self._list_stack: list[tuple[int, str]] = []

    # -- collecting? -------------------------------------------------
    def _live(self) -> bool:
        return self._skip_from is None and (self._scope_from is not None or self._scope_done is None)

    # -- buffers --------------------------------------------------
    def _open(self, tag: str):
        self._buf, self._tag, self._pre = [], tag, tag == "pre"

    def _flush(self):
        if self._buf is None:
            return
        raw = "".join(self._buf)
        tag, pre = self._tag, self._pre
        self._buf, self._tag, self._pre = None, "", False

        if pre:
            text = _htmllib.unescape(re.sub(r"<[^>]+>", "", raw))
            text = re.sub(r"[ \t]+\n", "\n", text).strip("\n").strip()
            if len(text) < 2:
                return
            if len(text) > 1400:
                text = text[:1400].rstrip() + "\n…"
            self.blocks.append("<pre>" + _htmllib.escape(text) + "</pre>")
            return

        inner = _WS.sub(" ", raw).strip()
        plain = _WS.sub(" ", re.sub(r"<[^>]+>", "", raw)).strip()
        if len(plain) < 2:
            return
        if tag in ("p", "blockquote"):
            if _BOILERPLATE.search(plain) or _CODEY.search(plain):
                return
            if len(plain) < 25 and not plain.endswith((".", ":", "?", "!")):
                return
        htag = "h2" if tag in ("h1", "h2") else "h3" if tag in ("h3", "h4", "h5", "h6") else tag
        self.blocks.append(f"<{htag}>{inner}</{htag}>" if tag != "li" else f"<li>{inner}</li>")

    # -- events -------------------------------------------------
    def handle_starttag(self, tag, attrs):
        void = tag in _VOID
        if not void:
            self.depth += 1

        if self._skip_from is not None:
            return
        if tag in _SKIP:
            self._skip_from = self.depth
            return

        # find the article container
        if self._scope_from is None and not self._scope_done:
            ident = _norm(attrs, "class") + " " + _norm(attrs, "id")
            if tag == "article" or (_CONTENT_HINT.search(ident) and not _NEG_HINT.search(ident)):
                self._scope_from = self.depth
        if self._scope_from is None:
            return  # not inside the article body yet

        # inside a negative sub-region? treat like skip
        if not void:
            ident = _norm(attrs, "class") + " " + _norm(attrs, "id")
            if ident.strip() and _NEG_HINT.search(ident):
                self._skip_from = self.depth
                return

        if tag in ("ul", "ol"):
            self._flush()
            self._list_stack.append((self.depth, tag))
            self.blocks.append(f"<{tag}>")
        elif tag in _BLOCKS:
            self._flush()
            self._open(tag)
        elif self._buf is not None and tag in _INLINE_KEEP:
            if tag == "br":
                self._buf.append("\n" if self._pre else " ")
            elif tag == "a":
                href = urljoin(self.base, _norm(attrs, "href").strip())
                self._buf.append(
                    f'<a href="{_htmllib.escape(href, quote=True)}">'
                    if href.startswith(("http://", "https://")) else "<a>"
                )
            else:
                self._buf.append("<" + _canon(tag) + ">")

    def handle_startendtag(self, tag, attrs):
        if tag == "br" and self._buf is not None and self._skip_from is None:
            self._buf.append("\n" if self._pre else " ")

    def handle_endtag(self, tag):
        closing = self.depth
        if tag not in _VOID:
            self.depth = max(self.depth - 1, 0)

        if self._skip_from is not None:
            if closing <= self._skip_from:
                self._skip_from = None
            return
        if self._scope_from is None:
            return
        if closing <= self._scope_from:          # article container closed
            self._flush()
            self._scope_from = None
            self._scope_done = True
            return
        if tag in ("ul", "ol"):
            self._flush()
            if self._list_stack:
                self._list_stack.pop()
            self.blocks.append(f"</{tag}>")
        elif tag in _BLOCKS:
            self._flush()
        elif self._buf is not None and tag in _INLINE_KEEP and tag != "br":
            self._buf.append("</" + _canon(tag) + ">")

    def handle_data(self, data):
        if self._skip_from is not None or self._buf is None:
            return
        self._buf.append(data if self._pre else _htmllib.escape(data))


def _canon(tag: str) -> str:
    return "strong" if tag in ("strong", "b") else "em" if tag in ("em", "i") else tag


_ABSTRACT = re.compile(
    r'<blockquote[^>]*class="[^"]*abstract[^"]*"[^>]*>(.*?)</blockquote>',
    re.IGNORECASE | re.DOTALL,
)


def paragraphs_html(text: str) -> str:
    """Wrap plain text (blank-line separated) into <p> blocks."""
    out = []
    for chunk in re.split(r"\n\s*\n", text or ""):
        chunk = _WS.sub(" ", chunk).strip()
        if chunk:
            out.append("<p>" + _htmllib.escape(chunk) + "</p>")
    return "".join(out)


def extract(html: str, url: str, max_chars: int = 20000) -> tuple[str, str]:
    if not html:
        return "", ""

    if "arxiv.org" in url:
        m = _ABSTRACT.search(html)
        if m:
            text = re.sub(r"^abstract:?\s*", "",
                          _WS.sub(" ", re.sub(r"<[^>]+>", " ", m.group(1))).strip(), flags=re.I)
            return ("<p>" + _htmllib.escape(text[:max_chars]) + "</p>", text[:max_chars])

    p = _Reader(url)
    try:
        p.feed(html)
        p._flush()
    except Exception:
        return "", ""

    # if no recognised container was found, retry treating <body> as the scope
    if not p.blocks:
        p2 = _Reader(url)
        p2._scope_done = None  # sentinel: collect everything below <body>
        p2._scope_from = 0
        try:
            p2.feed(html)
            p2._flush()
        except Exception:
            return "", ""
        p = p2

    frag = "".join(p.blocks)
    frag = re.sub(r"<(ul|ol)>\s*</\1>", "", frag)
    if len(frag) > max_chars:
        frag = frag[:max_chars].rsplit("</", 1)[0]
    plain = _WS.sub(" ", re.sub(r"<[^>]+>", " ", frag)).strip()
    return frag, plain


# ── markdown → reader HTML (for the r.jina.ai fallback) ─────────────
_MD_IMG = re.compile(r"!\[[^\]]*\]\((https?://[^)\s]+?)(?:\s+[^)]*)?\)")
_CAPTION_RE = re.compile(
    r"(^_.+_$|\b(credit|photo|photograph|source|image credit|illustration|"
    r"getty images|via reuters)\s*:|"
    r"\((left|right|top|bottom|above|below|centre|center)\))",
    re.I,
)


def _pick_image(md: str) -> str:
    for m in _MD_IMG.finditer(md):
        u = m.group(1)
        if not re.search(r"(seo-card|og-image|/og[?/]|favicon|sprite|/logo|avatar|1x1)", u, re.I):
            return u
    return ""


def _md_inline(s: str) -> str:
    s = _htmllib.escape(s).replace("(opens in a new window)", "")
    s = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", s)              # images → drop
    s = re.sub(
        r"\[([^\]]+)\]\((https?://[^)\s]+?)(?:\s+&quot;[^)]*&quot;)?\)",
        r'<a href="\2">\1</a>', s,
    )
    s = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", s)          # other link syntax → text
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", s)
    s = re.sub(r"(?<![\w`])_([^_\n]+)_(?![\w`])", r"\1", s)  # jina caption italics → plain
    return _WS.sub(" ", s).strip()


def from_markdown(md: str, max_chars: int = 20000) -> tuple[str, str, str]:
    """Convert r.jina.ai markdown to the tiny reader HTML used by extract().
    Returns (html, plain, first_content_image_url)."""
    if not md:
        return "", "", ""
    image = _pick_image(md)
    if "Markdown Content:" in md:
        md = md.split("Markdown Content:", 1)[1]

    blocks, total = [], 0
    for raw in re.split(r"\n{2,}", md):
        b = raw.strip()
        if not b:
            continue
        h = re.match(r"^(#{1,6})\s+(.+)$", b)
        if h:
            txt = _md_inline(h.group(2))
            if txt and not _BOILERPLATE.search(txt):
                tag = "h2" if len(h.group(1)) <= 2 else "h3"
                blocks.append(f"<{tag}>{txt}</{tag}>")
            continue
        if re.match(r"^([-*+]|\d+[.)])\s+", b):
            items = [
                f"<li>{_md_inline(m.group(2))}</li>"
                for line in b.splitlines()
                if (m := re.match(r"^([-*+]|\d+[.)])\s+(.*)$", line.strip()))
            ]
            if items:
                blocks.append("<ul>" + "".join(items) + "</ul>")
            continue
        text = _WS.sub(" ", b)
        if len(text) < 3 or _BOILERPLATE.search(text) or _CODEY.search(text):
            continue
        if _CAPTION_RE.search(text) and len(text) < 220:      # image caption / credit line
            continue
        if len(text) < 25 and not text.endswith((".", ":", "?", "!")):
            continue
        blocks.append(f"<p>{_md_inline(text)}</p>")
        total += len(text)
        if total >= max_chars:
            break

    frag = re.sub(r"<(ul|ol)>\s*</\1>", "", "".join(blocks))
    plain = _WS.sub(" ", re.sub(r"<[^>]+>", " ", frag)).strip()
    return frag, plain, image
