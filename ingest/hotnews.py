"""Spot 'hot' / breaking topics: a story covered by two or more different
feeds on the same day. Pure text, no API.

Two titles from different feeds are linked when they share a distinctive
name phrase, or two-plus terms of which at least one is rare across the day's
titles. Linked articles are unioned into clusters; a cluster spanning >=2
feeds is 'hot'.
"""
from __future__ import annotations

import re
from collections import Counter

from .article import Article

_STOP = {
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "with", "is",
    "are", "was", "were", "be", "as", "at", "by", "it", "its", "this", "that",
    "how", "why", "what", "who", "new", "now", "from", "into", "up", "down",
    "not", "no", "but", "has", "have", "will", "can", "your", "you", "our",
    "we", "more", "says", "said", "after", "amid", "over", "about", "than",
    "ai", "llm", "llms", "model", "models", "tech", "using", "use", "first",
    "could", "would", "get", "gets", "make", "makes", "one", "two", "vs",
    "research", "paper", "system", "systems", "study", "report", "data",
    "week", "day", "today", "inside", "story", "view", "future", "latest",
}
_CAP = re.compile(r"[A-Z][A-Za-z0-9.\-+&]*(?:\s+[A-Z][A-Za-z0-9.\-+&]*){1,2}")
_WORD = re.compile(r"[A-Za-z0-9][A-Za-z0-9.\-+]{2,}")


def _trim_phrase(p: str) -> str:
    toks = p.split()
    while toks and toks[0].lower() in _STOP:
        toks.pop(0)
    while toks and toks[-1].lower() in _STOP:
        toks.pop()
    return " ".join(toks)


def _terms(title: str):
    words = [w for w in _WORD.findall(title)
             if w.lower() not in _STOP and not w.isdigit()]
    phrases = [p for m in _CAP.finditer(title)
               if len((p := _trim_phrase(m.group(0).strip(" .,-"))).split()) >= 2]
    disp = {}                              # lower -> nicest original form
    sig = set()
    for t in words + phrases:
        low = t.lower()
        sig.add(low)
        if low not in disp or (" " in t and " " not in disp[low]):
            disp[low] = t
    return sig, disp


def hot_topics(articles: list[Article], min_sources: int = 2, limit: int = 5) -> list[dict]:
    n = len(articles)
    if n < 2:
        return []
    sigs, disps = [], {}
    for a in articles:
        s, d = _terms(a.title)
        sigs.append(s)
        for k, v in d.items():
            disps.setdefault(k, v)

    df = Counter(t for s in sigs for t in s)
    rare_cut = max(3, int(n * 0.06))

    parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i in range(n):
        for j in range(i + 1, n):
            if articles[i].source == articles[j].source:
                continue
            common = sigs[i] & sigs[j]
            if not common:
                continue
            name_phrase = any(" " in c and df[c] <= rare_cut for c in common)
            rare_pair = len(common) >= 2 and any(df[c] <= rare_cut for c in common)
            if name_phrase or rare_pair:
                parent[find(i)] = find(j)

    clusters: dict[int, list[int]] = {}
    for i in range(n):
        clusters.setdefault(find(i), []).append(i)

    out = []
    for members in clusters.values():
        if len(members) < 2:
            continue
        arts = [articles[i] for i in members]
        sources = sorted({a.source for a in arts if a.source})
        if len(sources) < min_sources:
            continue

        shared = Counter()
        for i in members:
            for t in sigs[i]:
                shared[t] += 1
        shared = {t: c for t, c in shared.items() if c >= 2}
        phrases = sorted((t for t in shared if " " in t),
                         key=lambda t: (shared[t], -df[t]), reverse=True)
        singles = sorted((t for t in shared if " " not in t),
                         key=lambda t: (df[t] <= rare_cut, shared[t]), reverse=True)
        picks = (phrases[:1] or singles[:2])
        label = " · ".join(disps.get(t, t.title()) for t in picks) \
            or min((a.title for a in arts), key=len)

        arts.sort(key=lambda a: a.published, reverse=True)
        out.append({
            "label": label,
            "sources": sources,
            "count": len(arts),
            "url": arts[0].url,
            "doc_ids": [a.doc_id for a in arts],
        })

    out.sort(key=lambda t: (len(t["sources"]), t["count"]), reverse=True)
    return out[:limit]
