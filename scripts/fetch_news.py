"""
Fetch ~100 extreme-weather climate news headlines from free RSS feeds.
Saves to data/news_headlines.json.

Usage:
    python scripts/fetch_news.py
"""

import json
import re
import sys
from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from xml.etree import ElementTree as ET

import requests

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUT_FILE = DATA_DIR / "news_headlines.json"

FEEDS = [
    {"source": "BBC Science & Environment",      "url": "http://feeds.bbci.co.uk/news/science_and_environment/rss.xml",       "filter": True},
    {"source": "The Guardian - Climate Crisis",  "url": "https://www.theguardian.com/environment/climate-crisis/rss",         "filter": False},
    {"source": "The Guardian - Environment",     "url": "https://www.theguardian.com/environment/rss",                        "filter": True},
    {"source": "Inside Climate News",            "url": "https://insideclimatenews.org/feed/",                                "filter": True},
    {"source": "Climate Home News",              "url": "https://www.climatechangenews.com/feed/",                            "filter": True},
    {"source": "Carbon Brief",                   "url": "https://www.carbonbrief.org/feed/",                                  "filter": True},
    {"source": "Phys.org - Environment",         "url": "https://phys.org/rss-feed/earth-news/environment/",                  "filter": True},
    {"source": "Mongabay",                       "url": "https://news.mongabay.com/feed/",                                    "filter": True},
    {"source": "Grist",                          "url": "https://grist.org/feed/",                                            "filter": True},
    {"source": "ScienceDaily - Weather",         "url": "https://www.sciencedaily.com/rss/earth_climate/weather.xml",         "filter": True},
]

EXTREME_WEATHER_KEYWORDS = [
    # Events
    "flood", "flooding", "flooded", "hurricane", "typhoon", "cyclone", "tornado",
    "wildfire", "forest fire", "bushfire", "heatwave", "heat wave", "heat dome",
    "drought", "megadrought", "storm", "blizzard", "snowstorm", "avalanche",
    "flash flood", "superstorm", "monsoon", "landslide", "mudslide",
    # Records & extremes
    "record heat", "record temperature", "record rainfall", "record-breaking",
    "record high", "record low", "hottest", "coldest", "wettest", "driest",
    "unprecedented", "extreme weather", "extreme event", "catastrophic",
    "deadly", "devastating", "destructive", "severe weather",
    # Climate indicators that reflect extreme events
    "sea level rise", "sea level", "ice sheet", "glacier melt", "arctic ice",
    "coral bleach", "permafrost", "ice cap",
    # Impacts
    "climate disaster", "climate emergency", "climate crisis", "climate refugee",
    "displaced", "evacuation", "death toll", "casualties", "damage",
]

HEADERS = {"User-Agent": "Mozilla/5.0 (climate-disinformation-lab/1.0)"}


def _matches(title: str, desc: str, keywords: list) -> bool:
    text = (title + " " + (desc or "")).lower()
    return any(kw in text for kw in keywords)


def _clean_html(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"&lt;", "<", text)
    text = re.sub(r"&gt;", ">", text)
    text = re.sub(r"&quot;", '"', text)
    text = re.sub(r"&#?\w+;", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _parse_date(raw: str) -> str:
    if not raw:
        return ""
    try:
        return parsedate_to_datetime(raw).isoformat()
    except Exception:
        return raw.strip()


def fetch_feed(cfg: dict) -> list:
    source = cfg["source"]
    try:
        resp = requests.get(cfg["url"], headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as exc:
        print(f"  [SKIP] {source}: {exc}")
        return []

    try:
        root = ET.fromstring(resp.content)
    except ET.ParseError as exc:
        print(f"  [SKIP] {source}: XML parse error - {exc}")
        return []

    ns = {"atom": "http://www.w3.org/2005/Atom"}
    items = root.findall(".//item") or root.findall(".//atom:entry", ns)

    articles = []
    for item in items:
        def _t(tag, ns_tag=None):
            el = item.find(tag)
            if el is None and ns_tag:
                el = item.find(ns_tag, ns)
            return (el.text or "").strip() if el is not None else ""

        title = _clean_html(_t("title"))
        desc  = _clean_html(_t("description") or _t("summary"))
        link  = _t("link") or _t("atom:link", "atom:link")
        date  = _parse_date(_t("pubDate") or _t("published"))

        if not title:
            continue
        if not _matches(title, desc, EXTREME_WEATHER_KEYWORDS):
            continue

        articles.append({
            "title": title,
            "description": desc[:350] if desc else "",
            "url": link,
            "published": date,
            "source": source,
        })

    print(f"  {source}: {len(articles)}")
    return articles


def main(target: int = 110):
    print(f"Fetching extreme-weather climate headlines (target={target})...\n")

    seen: set = set()
    all_articles: list = []

    for cfg in FEEDS:
        for art in fetch_feed(cfg):
            norm = art["title"].lower().strip()
            if norm in seen:
                continue
            seen.add(norm)
            all_articles.append(art)

    def _date_key(a):
        try:
            return datetime.fromisoformat(a["published"]) if a["published"] else datetime.min
        except Exception:
            return datetime.min

    all_articles.sort(key=_date_key, reverse=True)
    all_articles = all_articles[:target]

    for i, art in enumerate(all_articles):
        art["index"] = i

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_articles, f, indent=2, ensure_ascii=False)

    total = len(all_articles)
    print(f"\nSaved {total} headlines to {OUT_FILE}")

    counts = {}
    for a in all_articles:
        counts[a["source"]] = counts.get(a["source"], 0) + 1
    for src, n in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {src}: {n}")


if __name__ == "__main__":
    main()
