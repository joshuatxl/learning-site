"""One-off: scrape og:image for existing articles that have no `image:` field.

Reads each docs/news/*.md, fetches its stored `url`, writes the og:image URL
back into frontmatter. Body is left untouched. Safe to re-run — only touches
files still missing an image. Run: python scripts/backfill_images.py
"""
import os
import sys
import time

import frontmatter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ingest.images import _scrape_og_image

NEWS_DIR = "docs/news"


def main() -> int:
    found = missing = skipped = 0
    for name in sorted(os.listdir(NEWS_DIR)):
        if not name.endswith(".md") or name == "index.md":
            continue
        path = os.path.join(NEWS_DIR, name)
        post = frontmatter.load(path)

        if post.get("image"):
            skipped += 1
            continue
        url = str(post.get("url", "")).strip()
        if not url:
            missing += 1
            continue

        img = _scrape_og_image(url)
        if img:
            post["image"] = img
            with open(path, "w", encoding="utf-8") as f:
                f.write(frontmatter.dumps(post) + "\n")
            found += 1
            print(f"  + {name}\n    {img}")
        else:
            missing += 1
            print(f"  - {name} (no og:image)")
        time.sleep(0.5)  # be polite to source sites

    print(f"\n{found} images added, {missing} without og:image, {skipped} already had one")
    return 0


if __name__ == "__main__":
    sys.exit(main())
