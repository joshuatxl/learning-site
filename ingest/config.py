"""Central configuration for the ingest pipeline.

Everything tunable lives here so the other modules stay logic-only.
"""
from __future__ import annotations

import os

# --- Feeds -----------------------------------------------------------------
# (source label, feed URL). The label is stored on each article.
FEEDS: list[tuple[str, str]] = [
    ("TechCrunch", "https://techcrunch.com/category/artificial-intelligence/feed/"),
    ("Hugging Face", "https://huggingface.co/blog/feed.xml"),
    ("Google AI", "https://blog.google/technology/ai/rss/"),
    ("OpenAI", "https://openai.com/news/rss.xml"),
    ("MIT Tech Review", "https://www.technologyreview.com/topic/artificial-intelligence/feed"),
    ("Data Science Weekly", "https://datascienceweekly.substack.com/feed"),
    ("Import AI", "https://jack-clark.net/feed/"),
    ("Alpha Signal", "https://alphasignalai.substack.com/feed"),
    ("DeepMind", "https://deepmind.com/blog/feed/basic"),
    ("arXiv cs.AI", "https://rss.arxiv.org/rss/cs.AI"),
]

# Max entries to inspect per feed per run (newest first).
ENTRIES_PER_FEED = 12

# Plain-text article preview length shown on each card (no AI involved).
PREVIEW_CHARS = 260

# --- Paths ---------------------------------------------------------------
DOCS_DIR = "docs"
NEWS_DIR = os.path.join(DOCS_DIR, "news")
INDEX_PAGE = os.path.join(DOCS_DIR, "index.md")

# Aging: articles live for 7 levels. Level 0 = entered today (top),
# level 7 = entered 7 days ago (bottom). At level 8 they are deleted.
RETENTION_DAYS = 7

# --- Models (only used by ingest/summarise.py, which the daily run no
#     longer calls — kept for the on-demand summariser / future reuse) ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
SUMMARY_MODEL = "gemini-3.6-flash"
EMBED_MODEL = "text-embedding-004"

# --- Second-brain data layer ----------------------------------------
CHROMA_PATH = os.environ.get("CHROMA_PATH", "")
CHROMA_COLLECTION = "news"

# Marker comments delimiting generated content on the front page.
GRID_START = "<!-- NEWS-GRID-START -->"
GRID_END = "<!-- NEWS-GRID-END -->"
DIGEST_START = "<!-- AI-DIGEST-START -->"
DIGEST_END = "<!-- AI-DIGEST-END -->"
