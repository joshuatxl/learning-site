"""One-off: bring legacy docs/news/*.md up to the current Article schema.

- backfill `summary:` from the article body
- backfill `published:` (ISO) from `date:` so chronological sort works
- add empty `source:` where missing
- drop zero-byte / title-less files

Body text is left untouched. Safe to re-run.
"""
import os
import re
import sys

import frontmatter

NEWS_DIR = "docs/news"
READ_MORE = "[Read the full article →]"


def body_summary(content: str) -> str:
    lines = content.splitlines()
    out = []
    for line in lines:
        s = line.strip()
        if s.startswith("#") or s.startswith("!["):
            continue
        if READ_MORE in s:
            break
        out.append(s)
    return re.sub(r"\s+", " ", " ".join(out)).strip()


def main() -> int:
    changed = removed = 0
    for name in sorted(os.listdir(NEWS_DIR)):
        if not name.endswith(".md") or name == "index.md":
            continue
        path = os.path.join(NEWS_DIR, name)
        post = frontmatter.load(path)

        if not post.get("title") or not post.content.strip():
            os.remove(path)
            removed += 1
            print(f"removed empty/titleless {name}")
            continue

        dirty = False
        if not str(post.get("summary", "")).strip():
            post["summary"] = body_summary(post.content)
            dirty = True
        if not post.get("published") and post.get("date"):
            post["published"] = f"{str(post['date'])[:10]}T00:00:00+00:00"
            dirty = True
        if "source" not in post.metadata:
            post["source"] = ""
            dirty = True

        if dirty:
            with open(path, "w", encoding="utf-8") as f:
                f.write(frontmatter.dumps(post) + "\n")
            changed += 1
            print(f"patched {name}")

    print(f"\n{changed} patched, {removed} removed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
