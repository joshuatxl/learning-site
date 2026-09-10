"""One Gemini call → the "Today in AI" brief.

Feeds the model the day's article titles + short previews in a single prompt
(not one call per article), so it is cheap enough for the free tier — a single
request per daily run. Returns "" when there is no key or on any error, so the
pipeline just skips the window that day.
"""
from __future__ import annotations

from .article import Article, clean_text
from .config import GEMINI_API_KEY, SUMMARY_MODEL

_PROMPT = (
    "You write the short top-of-page brief for an AI news site. Below are the "
    "articles added today, as 'title — preview'. Write 110–150 words of plain "
    "prose (two short paragraphs, no lists, no headings, no preamble) on what "
    "is going on in AI today. Lead with the biggest theme, name the specific "
    "companies, models and papers involved, and keep it factual and readable. "
    "Plain text only — no markdown, asterisks, underscores, headings or bullets."
    "{hot}\n\n{items}"
)


def generate(articles: list[Article], hot: list[dict] | None = None, limit: int = 45) -> str:
    if not GEMINI_API_KEY or not articles:
        return ""
    items = "\n".join(
        f"- {a.title} — {clean_text(a.preview or a.body, 240)}"
        for a in articles[:limit]
    )
    hot_line = ""
    if hot:
        names = ", ".join(h["label"] for h in hot)
        hot_line = (
            f"\n\nThese topics were covered by multiple feeds today and are the "
            f"hot stories — lead with them: {names}."
        )
    try:
        from google import genai

        client = genai.Client(api_key=GEMINI_API_KEY)
        resp = client.models.generate_content(
            model=SUMMARY_MODEL, contents=_PROMPT.format(hot=hot_line, items=items)
        )
        return (resp.text or "").strip()
    except Exception as e:  # missing dep, quota, network — non-fatal
        print(f"  digest: Gemini call failed ({e})")
        return ""
