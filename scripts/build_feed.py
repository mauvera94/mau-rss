import json
import os
from datetime import datetime, timezone
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

TARGET_URL = "https://www.brianlagerstrom.com/recipes?category=All%20Recipes"
OUT_FEED_PATH = "feeds/all.xml"
STATE_PATH = "state/seen.json"
MAX_ITEMS = 50


def utc_now():
    return datetime.now(timezone.utc)


def load_state():
    if not os.path.exists(STATE_PATH):
        return {"seen_links": []}
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def fetch_recipe_links():
    headers = {
        "User-Agent": "mauvera94-mau-rss (+https://github.com/mauvera94/mau-rss)"
    }
    r = requests.get(TARGET_URL, headers=headers, timeout=30)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    candidates = []
    for a in soup.select("a[href]"):
        href = (a.get("href") or "").strip()
        if not href:
            continue

        full = urljoin(TARGET_URL, href)

        # Heuristic: recipe pages typically live under /recipes/<slug>
        if "brianlagerstrom.com/recipes/" in full:
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


def write_rss(items):
    fg = FeedGenerator()
    fg.title("Brian Lagerstrom — All Recipes (Unofficial RSS)")
    fg.link(href=TARGET_URL, rel="alternate")
    fg.description("Auto-generated RSS feed for Brian Lagerstrom's All Recipes page.")
    fg.language("en")

    now = utc_now()
    fg.pubDate(now)

    for title, link in items[:MAX_ITEMS]:
        fe = fg.add_entry()
        fe.title(title)
        fe.link(href=link)
        fe.guid(link, permalink=True)
        fe.pubDate(now)  # fallback if listing page doesn't provide dates

    os.makedirs(os.path.dirname(OUT_FEED_PATH), exist_ok=True)
    fg.rss_file(OUT_FEED_PATH)


def main():
    state = load_state()
    items = fetch_recipe_links()

    # Track seen links (optional but handy later)
    seen_links = set(state.get("seen_links", []))
    for _, link in items:
        seen_links.add(link)
    state["seen_links"] = sorted(seen_links)

    write_rss(items)
    save_state(state)


if __name__ == "__main__":
    main()
