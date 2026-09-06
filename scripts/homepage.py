import os

NEWS_DIR = "docs/news"
INDEX_PAGE = "docs/index.md"
PLACEHOLDER_IMAGE = "https://placehold.co/400x200?text=No+Image"
GRID_START = "<!-- NEWS-GRID-START -->"
GRID_END = "<!-- NEWS-GRID-END -->"

def _parse_field(lines, field):
    line = next((l for l in lines if l.startswith(f"{field}:")), None)
    if not line:
        return None
    return line.split(":", 1)[1].strip().strip('"')

def rebuild_homepage():
    """Regenerate the article grid on docs/index.md, between marker comments.
    Everything outside the markers (e.g. a hand-written intro) is left untouched."""
    files = sorted(
        [f for f in os.listdir(NEWS_DIR) if f.endswith(".md") and f != "index.md"],
        reverse=True
    )

    cards = []
    for filename in files:
        path = os.path.join(NEWS_DIR, filename)
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
        title = _parse_field(lines, "title") or filename
        summary = _parse_field(lines, "summary") or ""
        image = _parse_field(lines, "image") or PLACEHOLDER_IMAGE
        page_slug = filename[:-3]  # strip .md; relies on mkdocs' default directory URLs
        cards.append(
            f'  <a class="news-card" href="news/{page_slug}/" target="_blank" rel="noopener">\n'
            f'    <img src="{image}" alt="">\n'
            f'    <div class="news-card-body">\n'
            f'      <p class="news-card-title">{title}</p>\n'
            f'      <p class="news-card-summary">{summary}</p>\n'
            f'    </div>\n'
            f'  </a>'
        )

    grid_html = '<div class="news-grid">\n' + "\n".join(cards) + "\n</div>"

    if not os.path.exists(INDEX_PAGE):
        with open(INDEX_PAGE, "w", encoding="utf-8") as f:
            f.write(f"# JT's learning site\n\n{GRID_START}\n{GRID_END}\n")

    with open(INDEX_PAGE, encoding="utf-8") as f:
        existing = f.read()

    if GRID_START in existing and GRID_END in existing:
        pre = existing.split(GRID_START)[0]
        post = existing.split(GRID_END)[1]
        new_content = f"{pre}{GRID_START}\n{grid_html}\n{GRID_END}{post}"
    else:
        new_content = f"{existing.rstrip()}\n\n{GRID_START}\n{grid_html}\n{GRID_END}\n"

    with open(INDEX_PAGE, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"Rebuilt homepage grid with {len(files)} articles")

if __name__ == "__main__":
    # standalone use: rebuild the homepage grid from whatever's already in docs/news/,
    # without fetching or summarising anything new
    rebuild_homepage()
