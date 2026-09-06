import feedparser
import os
import re
import urllib.request
from datetime import datetime, timedelta
from summarise_news import summarise
from homepage import rebuild_homepage

FEEDS = [
    "https://rss.arxiv.org/rss/cs.AI",
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://deepmind.google/blog/feed/basic/",
    "https://huggingface.co/blog/feed.xml",
]
NEWS_DIR = "docs/news"
RETENTION_DAYS = 30
MAX_SUMMARIES_PER_RUN = 15  # stay under the ~20/day free-tier quota across all feeds combined

def slugify(title):
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug[:60]

def already_saved(slug):
    return any(f.endswith(f"-{slug}.md") for f in os.listdir(NEWS_DIR))

def extract_image(entry):
    """Pull an image URL from an RSS entry, trying the common feedparser fields first.
    Most feeds here (TechCrunch, Hugging Face) don't embed image data at all, so
    fall back to scraping the article page's og:image meta tag."""
    if hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
        return entry.media_thumbnail[0].get("url")
    if hasattr(entry, "media_content") and entry.media_content:
        return entry.media_content[0].get("url")
    for link in entry.get("links", []):
        if link.get("type", "").startswith("image"):
            return link.get("href")
    return extract_og_image(entry.link)

def extract_og_image(url, timeout=5):
    """Fetch the article page and pull its og:image meta tag, if present."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            html = response.read(200_000).decode("utf-8", errors="ignore")
        match = re.search(
            r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']',
            html, re.IGNORECASE
        )
        if not match:
            # some sites order the attributes the other way round
            match = re.search(
                r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',
                html, re.IGNORECASE
            )
        return match.group(1) if match else None
    except Exception as e:
        print(f"Could not fetch og:image for {url}: {e}")
        return None

def save_article(title, link, summary, date_str, image_url=None):
    slug = slugify(title)
    filename = f"{date_str}-{slug}.md"
    path = os.path.join(NEWS_DIR, filename)

    # keep frontmatter values on one line and quote-safe
    safe_summary = summary.replace('"', "'").replace("\n", " ").strip()

    frontmatter = [
        "---",
        f'title: "{title}"',
        f'url: "{link}"',
        f"date: {date_str}",
        f'summary: "{safe_summary}"',
    ]
    if image_url:
        frontmatter.append(f'image: "{image_url}"')
    frontmatter.append("---")

    body = f"\n# {title}\n"
    if image_url:
        body += f"\n![]({image_url})\n"
    body += f"\n{summary}\n\n[Read the full article →]({link})\n"

    content = "\n".join(frontmatter) + body
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
    lines_out = ["# News\n"]
    for filename in files:
        path = os.path.join(NEWS_DIR, filename)
        with open(path, encoding="utf-8") as f:
            content = f.read()
        lines = content.splitlines()
        title_line = next((l for l in lines if l.startswith("title:")), None)
        title = title_line.split(":", 1)[1].strip().strip('"') if title_line else filename
        page_link = filename.replace(".md", "")
        lines_out.append(f"- [{title}]({page_link}.md)")
    with open(os.path.join(NEWS_DIR, "index.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines_out))

def main():
    os.makedirs(NEWS_DIR, exist_ok=True)
    summaries_this_run = 0
    for feed_url in FEEDS:
        feed = feedparser.parse(feed_url)
        print(f"Feed status: {feed.get('status', 'unknown')}, entries found: {len(feed.entries)}")
        for entry in feed.entries[:5]:
            if summaries_this_run >= MAX_SUMMARIES_PER_RUN:
                print(f"Reached per-run cap ({MAX_SUMMARIES_PER_RUN}), stopping early")
                cleanup_old_articles()
                rebuild_index()
                rebuild_homepage()
                return
            slug = slugify(entry.title)
            if already_saved(slug):
                continue
            summary = summarise(entry.get("summary", ""), title=entry.title)
            summaries_this_run += 1
            if summary is None:
                print(f"Skipped (summarizer unavailable): {entry.title}")
                continue
            date_str = datetime.now().strftime("%Y-%m-%d")
            image_url = extract_image(entry)
            save_article(entry.title, entry.link, summary, date_str, image_url)
    cleanup_old_articles()
    rebuild_index()
    rebuild_homepage()

if __name__ == "__main__":
    main()