"""Feed fetching and normalisation.

Yields (source_label, entry, published_dt) tuples, newest first, capped per
feed. Entries without a parseable date fall back to 'now' so they still flow
through rather than being silently dropped.
"""
from __future__ import annotations

import time
from datetime import datetime, timezone

import feedparser

from .config import ENTRIES_PER_FEED, FEEDS


def _published_dt(entry) -> datetime:
    for key in ("published_parsed", "updated_parsed"):
        parsed = entry.get(key)
        if parsed:
            return datetime.fromtimestamp(time.mktime(parsed), tz=timezone.utc)
    return datetime.now(timezone.utc)


def fetch_entries():
    """Generator of (source, entry, published_dt), newest first within each feed."""
    for source, url in FEEDS:
        feed = feedparser.parse(url)
        status = feed.get("status", "?")
        if not feed.entries:
            print(f"[{source}] status={status} — no entries (feed may have moved)")
            continue
        print(f"[{source}] status={status} entries={len(feed.entries)}")
        dated = sorted(
            ((e, _published_dt(e)) for e in feed.entries),
            key=lambda pair: pair[1],
            reverse=True,
        )
        for entry, published in dated[:ENTRIES_PER_FEED]:
            yield source, entry, published
