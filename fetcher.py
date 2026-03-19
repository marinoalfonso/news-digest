# fetcher.py
import os
import re
import requests
import feedparser
from datetime import datetime, timezone, timedelta
from config import (
    RSS_FEEDS, NEWSAPI_QUERIES, NEWSAPI_LANGUAGE,
    NEWSAPI_PAGE_SIZE, MAX_ARTICLES_PER_CATEGORY, HOURS_LOOKBACK
)


def clean_html(text: str) -> str:
    """Rimuove tag HTML e spazi extra da una stringa."""
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def is_recent(published_str: str | None) -> bool:
    """Restituisce True se l'articolo è nelle ultime HOURS_LOOKBACK ore."""
    if not published_str:
        return True  # se non c'è data, lo includiamo per sicurezza
    try:
        from email.utils import parsedate_to_datetime
        dt = parsedate_to_datetime(published_str)
        dt = dt.astimezone(timezone.utc)
        cutoff = datetime.now(timezone.utc) - timedelta(hours=HOURS_LOOKBACK)
        return dt >= cutoff
    except Exception:
        return True


def fetch_rss(category: str) -> list[dict]:
    """Scarica e normalizza articoli dai feed RSS di una categoria."""
    feeds = RSS_FEEDS.get(category, [])
    articles = []

    for url in feeds:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                if not is_recent(entry.get("published")):
                    continue
                title = clean_html(entry.get("title", ""))
                summary = clean_html(
                    entry.get("summary", "") or entry.get("description", "")
                )
                # Tronca summary a 500 caratteri per non sprecare token
                summary = summary[:500] if summary else ""
                link = entry.get("link", "")
                source = feed.feed.get("title", url)

                if title:
                    articles.append({
                        "title": title,
                        "summary": summary,
                        "url": link,
                        "source": source,
                        "category": category,
                        "origin": "rss",
                    })
        except Exception as e:
            print(f"[RSS] Errore su {url}: {e}")

    return articles


def fetch_newsapi(category: str, api_key: str) -> list[dict]:
    """Scarica articoli da NewsAPI per una categoria."""
    query = NEWSAPI_QUERIES.get(category, "")
    if not query or not api_key:
        return []

    url = "https://newsapi.org/v2/everything"
    from_date = (datetime.now(timezone.utc) - timedelta(hours=HOURS_LOOKBACK)).strftime("%Y-%m-%dT%H:%M:%S")

    params = {
        "q": query,
        "language": NEWSAPI_LANGUAGE,
        "sortBy": "publishedAt",
        "pageSize": NEWSAPI_PAGE_SIZE,
        "from": from_date,
        "apiKey": api_key,
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        articles = []
        for item in data.get("articles", []):
            title = clean_html(item.get("title", ""))
            summary = clean_html(item.get("description", ""))
            summary = summary[:500] if summary else ""
            if title and "[Removed]" not in title:
                articles.append({
                    "title": title,
                    "summary": summary,
                    "url": item.get("url", ""),
                    "source": item.get("source", {}).get("name", "NewsAPI"),
                    "category": category,
                    "origin": "newsapi",
                })
        return articles
    except Exception as e:
        print(f"[NewsAPI] Errore per '{category}': {e}")
        return []


def fetch_all(categories: list[str]) -> dict[str, list[dict]]:
    """Punto di ingresso principale: scarica tutto e raggruppa per categoria."""
    newsapi_key = os.getenv("NEWSAPI_KEY", "")
    if not newsapi_key:
        print("[!] NEWSAPI_KEY non trovata in .env — salto NewsAPI.")

    result = {}
    for cat in categories:
        print(f"[→] Fetching: {cat}")
        rss_articles = fetch_rss(cat)
        api_articles = fetch_newsapi(cat, newsapi_key)

        # Unisci, deduplicando per titolo (case-insensitive)
        seen_titles = set()
        combined = []
        for art in rss_articles + api_articles:
            key = art["title"].lower()[:60]
            if key not in seen_titles:
                seen_titles.add(key)
                combined.append(art)

        # Limita al massimo configurato
        result[cat] = combined[:MAX_ARTICLES_PER_CATEGORY]
        print(f"    {len(result[cat])} articoli trovati")

    return result
