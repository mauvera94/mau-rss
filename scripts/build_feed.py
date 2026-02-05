import json
import os
from datetime import datetime, timezone
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

CONFIG_PATH = "feeds.json"
OUTPUT_DIR = "feeds"
INDEX_OUT_PATH = "index.html"
TEMPLATE_PATH = "site/template.html"

SITE_BASE = "https://mauvera94.github.io/mau-rss"


def utc_now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def fetch_links(source_url: str, match_url_contains: str):
    headers = {
        "User-Agent": "mauvera94-mau-rss (+https://github.com/mauvera94/mau-rss)"
    }
    r = requests.get(source_url, headers=headers, timeout=30)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    candidates = []
    for a in soup.select("a[href]"):
        href = (a.get("href") or "").strip()
        if not href:
            continue
        full = urljoin(source_url, href)

        if match_url_contains in full:
            title = a.get_text(" ", strip=True)
            if title and len(title) > 3:
                candidates.append((title, full))

    # De-dupe while preserving order
    seen = set()
    items = []
    for title, link in candidates:
        if link in seen:
            continue
        seen.add(link)
        items.append((title, link))

    return items


def write_rss(feed_id: str, title: str, source_url: str, items, max_items: int):
    fg = FeedGenerator()
    fg.title(title)
    fg.link(href=source_url, rel="alternate")
    fg.description(f"Auto-generated RSS feed for {source_url}")
    fg.language("en")

    now = datetime.now(timezone.utc)
    fg.pubDate(now)

    for item_title, link in items[:max_items]:
        fe = fg.add_entry()
        fe.title(item_title)
        fe.link(href=link)
        fe.guid(link, permalink=True)
        fe.pubDate(now)  # fallback if no per-item date

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"{feed_id}.xml")
    fg.rss_file(out_path)
    return out_path


def generate_index(feeds):
    # Load template
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    # Build list items
    lis = []
    for feed in feeds:
        feed_id = feed["id"]
        title = feed["title"]
        source_url = feed["source_url"]
        feed_url = f"{SITE_BASE}/feeds/{feed_id}.xml"

        lis.append(
            f'<li><strong>{title}</strong><br>'
            f'<span class="small">Source: <a href="{source_url}">{source_url}</a></span><br>'
            f'<span class="small">Feed: <a href="{feed_url}">{feed_url}</a> '
            f'(<code>feeds/{feed_id}.xml</code>)</span></li>'
        )

    feed_list_html = "<ul>\n" + "\n".join(lis) + "\n</ul>\n"

    html = html.replace("<!-- FEED_LIST -->", feed_list_html)
    html = html.replace("<!-- UPDATED_AT -->", utc_now_iso())

    with open(INDEX_OUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Wrote: {INDEX_OUT_PATH}")


def main():
    cfg = load_config()
    feeds = cfg.get("feeds", [])
    if not feeds:
        raise RuntimeError("No feeds found in feeds.json")

    # Build each feed
    for feed in feeds:
        feed_id = feed["id"]
        title = feed["title"]
        source_url = feed["source_url"]
        match = feed["match_url_contains"]
        max_items = int(feed.get("max_items", 50))

        items = fetch_links(source_url, match)
        out_path = write_rss(feed_id, title, source_url, items, max_items)
        print(f"Wrote: {out_path}")

    # Build homepage
    generate_index(feeds)


if __name__ == "__main__":
    main()