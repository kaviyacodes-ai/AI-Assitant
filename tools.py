"""Free helper tools (no extra API keys needed).

- get_news:     headlines from Google News RSS
- find_places:  places from OpenStreetMap (Nominatim)
"""
from urllib.parse import quote
import feedparser
import requests


def get_news(topic="top stories", limit=5):
    url = (f"https://news.google.com/rss/search?q={quote(topic)}"
           "&hl=en-IN&gl=IN&ceid=IN:en")
    feed = feedparser.parse(url)
    return [f"{e.title} ({e.link})" for e in feed.entries[:limit]]


def find_places(what, city, limit=5):
    """Example: find_places('cafe', 'Chennai')"""
    response = requests.get(
        "https://nominatim.openstreetmap.org/search",
        params={"q": f"{what} in {city}", "format": "json", "limit": limit},
        headers={"User-Agent": "beginner-ai-assistant/1.0"},  # required by OSM
        timeout=10,
    )
    response.raise_for_status()
    return [
        f"{p['display_name']} "
        f"(map: https://www.openstreetmap.org/?mlat={p['lat']}&mlon={p['lon']})"
        for p in response.json()
    ]
