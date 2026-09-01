import feedparser
import os
import re
from datetime import datetime, timedelta
from summarise_news import summarise

FEEDS = [
    "https://rss.arxiv.org/rss/cs.AI",
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://deepmind.google/blog/feed/basic/",
    "https://huggingface.co/blog/feed.xml",
]
NEWS_DIR = "docs/news"
RETENTION_DAYS = 30

def slugify(title):
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug[:60]

def already_saved(slug):
    return any(slug in f for f in os.listdir(NEWS_DIR))

def save_article(title, link, summary, date_str):
    slug = slugify(title)
    filename = f"{date_str}-{slug}.md"
    path = os.path.join(NEWS_DIR, filename)
    content = f"""---
title: "{title}"
url: "{link}"
date: {date_str}
---

# {title}

{summary}

[Read the full article →]({link})
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Saved: {filename}")

def cleanup_old_articles():
    cutoff = datetime.now() - timedelta(days=RETENTION_DAYS)
    for filename in os.listdir(NEWS_DIR):
        if filename == "index.md":
            continue  # never delete the section landing page
        date_str = filename[:10]  # expects YYYY-MM-DD prefix
        try:
            file_date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            continue  # skip files that don't match the naming pattern
        if file_date < cutoff:
            os.remove(os.path.join(NEWS_DIR, filename))
            print(f"Removed (older than {RETENTION_DAYS} days): {filename}")

def rebuild_index():
    files = sorted(
        [f for f in os.listdir(NEWS_DIR) if f.endswith(".md") and f != "index.md"],
        reverse=True  # newest first
    )
    lines = ["# News\n"]
    for filename in files:
        path = os.path.join(NEWS_DIR, filename)
        with open(path, encoding="utf-8") as f:
            content = f.read()
        # pull the title back out of the frontmatter
        title_line = next((l for l in content.splitlines() if l.startswith("title:")), None)
        title = title_line.split(":", 1)[1].strip().strip('"') if title_line else filename
        page_link = filename.replace(".md", "")
        lines.append(f"- [{title}]({page_link}.md)")
    with open(os.path.join(NEWS_DIR, "index.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def main():
    os.makedirs(NEWS_DIR, exist_ok=True)
    for feed_url in FEEDS:
        feed = feedparser.parse(feed_url)
        print(f"Feed status: {feed.get('status', 'unknown')}, entries found: {len(feed.entries)}")
        for entry in feed.entries[:5]:
            slug = slugify(entry.title)
            if already_saved(slug):
                continue
            summary = summarise(entry.get("summary", ""), title=entry.title)
            date_str = datetime.now().strftime("%Y-%m-%d")
            save_article(entry.title, entry.link, summary, date_str)
    cleanup_old_articles()
    rebuild_index()

if __name__ == "__main__":
    main()