"""Gemini summariser — ~300 words, on demand only.

The daily pipeline does NOT call this. It exists for:
  * a Python summarisation backend, if you prefer one over the Cloudflare
    Worker in workers/ (import `summarise` and expose it over HTTP), and
  * local testing.

The client is created lazily so importing this module never needs a key.
"""
from __future__ import annotations

import time

from google import genai
from google.genai import errors

from .config import GEMINI_API_KEY, SUMMARY_MODEL

_client: genai.Client | None = None

PROMPT = (
    "Summarise the following article in about 300 words. Be specific and "
    "factual, focus on what is new or notable, and do not add a preamble or "
    "sign-off.\n\nTitle: {title}\n\n{text}"
)


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        if not GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY is not set")
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


def summarise(text: str, title: str = "", max_attempts: int = 3) -> str | None:
    """Return a ~300-word summary string, or None on hard failure."""
    prompt = PROMPT.format(title=title, text=text)
    for attempt in range(max_attempts):
        try:
            resp = _get_client().models.generate_content(
                model=SUMMARY_MODEL, contents=prompt
            )
            return (resp.text or "").strip() or None
        except errors.ServerError:
            if attempt < max_attempts - 1:
                time.sleep(2 ** attempt)
            else:
                return None
        except errors.ClientError as e:
            print(f"  client error (not retryable): {e}")
            return None
        except Exception as e:
            print(f"  unexpected error calling Gemini: {e}")
            return None


if __name__ == "__main__":
    print(summarise(
        "Anthropic released a new open-source retrieval-augmented model today.",
        title="Test Article",
    ))
