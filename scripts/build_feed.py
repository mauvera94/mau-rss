import json
import os
from datetime import datetime, timezone
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator


CONFIG_PATH = "feeds.json"
OUTPUT_DIR = "feeds"


def utc_now():
    return datetime.now(timezone.utc)


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

    now = utc_now()
    fg.pubDate(now)

    for item_title, link in items[:max_items]:
        fe = fg.add_entry()
        fe.title(item_title)
        fe.link(href=link)
        fe.guid(link, permalink=True)
        fe.pubDate(now)  # fallback

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"{feed_id}.xml")
    fg.rss_file(out_path)
    print(f"Wrote: {out_path} ({min(len(items), max_items)} items)")


def main():
    cfg = load_config()
    feeds = cfg.get("feeds", [])

    if not feeds:
        raise RuntimeError("No feeds found in feeds.json")

    for f in feeds:
        feed_id = f["id"]
        title = f["title"]
        source_url = f["source_url"]
        match = f["match_url_contains"]
        max_items = int(f.get("max_items", 50))

        items = fetch_links(source_url, match)
        write_rss(feed_id, title, source_url, items, max_items)


if __name__ == "__main__":
    main()