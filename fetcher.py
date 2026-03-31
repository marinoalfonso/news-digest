# fetcher.py
import os
import re
import requests
import feedparser
from datetime import datetime, timezone, timedelta
from config import (
    RSS_FEEDS, NEWSAPI_QUERIES, NEWSAPI_LANGUAGE,
    ARTICLES_PER_RSS_FEED, ARTICLES_FROM_NEWSAPI, HOURS_LOOKBACK
)
from logger import get_logger

log = get_logger("fetcher")


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
    """Scarica esattamente ARTICLES_PER_RSS_FEED articoli per ogni feed RSS.
    Il pool risultante è bilanciato per costruzione — ogni fonte contribuisce ugualmente.
    """
    feeds = RSS_FEEDS.get(category, [])
    articles = []

    for url in feeds:
        feed_articles = []
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                if not is_recent(entry.get("published")):
                    continue
                title = clean_html(entry.get("title", ""))
                summary = clean_html(
                    entry.get("summary", "") or entry.get("description", "")
                )
                summary = summary[:500] if summary else ""
                link = entry.get("link", "")
                source = feed.feed.get("title", url)

                if title:
                    feed_articles.append({
                        "title": title,
                        "summary": summary,
                        "url": link,
                        "source": source,
                        "category": category,
                        "origin": "rss",
                    })

                if len(feed_articles) >= ARTICLES_PER_RSS_FEED:
                    break

        except Exception as e:
            log.error(f"Errore RSS su {url}: {e}")

        log.info(f"{len(feed_articles)}/{ARTICLES_PER_RSS_FEED} articoli da {url[:60]}")
        articles.extend(feed_articles)

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
        "pageSize": ARTICLES_FROM_NEWSAPI,
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
        log.error(f"NewsAPI errore per '{category}': {e}")
        return []


def fetch_all(categories: list[str]) -> dict[str, list[dict]]:
    """Punto di ingresso principale: scarica articoli bilanciati per fonte."""
    newsapi_key = os.getenv("NEWSAPI_KEY", "")
    if not newsapi_key:
        log.warning("NEWSAPI_KEY non trovata in .env — salto NewsAPI.")

    result = {}
    for cat in categories:
        log.info(f"Fetching categoria: {cat}")
        rss_articles = fetch_rss(cat)
        api_articles = fetch_newsapi(cat, newsapi_key)

        seen_titles = set()
        combined = []
        for art in rss_articles + api_articles:
            key = art["title"].lower()[:60]
            if key not in seen_titles:
                seen_titles.add(key)
                combined.append(art)

        result[cat] = combined
        log.info(f"Pool {cat}: {len(result[cat])} articoli ({len(rss_articles)} RSS + {len(api_articles)} NewsAPI)")

    return result