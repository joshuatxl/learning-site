"""One-off: move legacy articles to the preview/level model.

- add `preview:` (plain text) from the old AI `summary:` or the body
- add `fetched:` (YYYY-MM-DD) from the publish date, so leveling works
- drop the now-unused `matches:` field

Safe to re-run. Run: python scripts/migrate_preview.py
"""
import os
import sys

import frontmatter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ingest.article import clean_text  # noqa: E402
from ingest.config import PREVIEW_CHARS  # noqa: E402

NEWS_DIR = "docs/news"
READ_MORE = "[Read the full article →]"


def body_text(content: str) -> str:
    keep = []
    for line in content.splitlines():
        s = line.strip()
        if s.startswith("#") or s.startswith("![") or READ_MORE in s:
            continue
        keep.append(s)
    return " ".join(keep)


def main() -> int:
    changed = 0
    for name in sorted(os.listdir(NEWS_DIR)):
        if not name.endswith(".md") or name == "index.md":
            continue
        path = os.path.join(NEWS_DIR, name)
        post = frontmatter.load(path)
        dirty = False

        if not str(post.get("preview", "")).strip():
            source = str(post.get("summary", "")).strip() or body_text(post.content)
            post["preview"] = clean_text(source, PREVIEW_CHARS)
            dirty = True

        if not str(post.get("fetched", "")).strip():
            d = str(post.get("date") or post.get("published") or "")[:10]
            if d:
                post["fetched"] = d
                dirty = True

        if "matches" in post.metadata:
            del post["matches"]
            dirty = True

        if dirty:
            with open(path, "w", encoding="utf-8") as f:
                f.write(frontmatter.dumps(post) + "\n")
            changed += 1
            print(f"  migrated {name}")

    print(f"\n{changed} files migrated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
