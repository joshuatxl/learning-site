"""One-off: legacy articles stored the old AI summary as their `preview:`.
Re-scrape a real excerpt from each article's source page; where scraping
yields nothing usable, clear the preview (card shows title + date only).
Also drop the now-unused `summary:` field.

Run: python scripts/backfill_preview.py
"""
import os
import sys
import time

import frontmatter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ingest.article import clean_text  # noqa: E402
from ingest.config import PREVIEW_CHARS  # noqa: E402
from ingest.images import page_excerpt  # noqa: E402

NEWS_DIR = "docs/news"


def main() -> int:
    scraped = cleared = 0
    for name in sorted(os.listdir(NEWS_DIR)):
        if not name.endswith(".md") or name == "index.md":
            continue
        path = os.path.join(NEWS_DIR, name)
        post = frontmatter.load(path)
        url = str(post.get("url", "")).strip()

        excerpt = clean_text(page_excerpt(url), PREVIEW_CHARS) if url else ""
        if excerpt:
            post["preview"] = excerpt
            scraped += 1
            print(f"  ok   {name}\n       {excerpt[:100]}")
        else:
            post["preview"] = ""
            cleared += 1
            print(f"  --   {name} (no excerpt, cleared)")

        if "summary" in post.metadata:
            del post["summary"]

        with open(path, "w", encoding="utf-8") as f:
            f.write(frontmatter.dumps(post) + "\n")
        time.sleep(0.4)

    print(f"\n{scraped} previews scraped, {cleared} cleared")
    return 0


if __name__ == "__main__":
    sys.exit(main())
