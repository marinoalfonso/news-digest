# main.py
import os
import webbrowser
from dotenv import load_dotenv
from config import CATEGORIES
from fetcher import fetch_all
from summarizer import summarize_all
from report import generate_html, save_report
from logger import get_logger

log = get_logger("main")

def main():
    load_dotenv()
    log.info("=" * 44)
    log.info("NEWS DIGEST — avvio")
    log.info("=" * 44)

    log.info("[1/3] Scarico gli articoli...")
    articles = fetch_all(CATEGORIES)
    total = sum(len(v) for v in articles.values())
    log.info(f"Totale articoli raccolti: {total}")

    log.info("[2/3] Genero i digest con Claude...")
    summaries = summarize_all(articles)

    log.info("[3/3] Costruisco il report HTML...")
    html = generate_html(summaries, articles)
    path = save_report(html)

    log.info(f"Report salvato in: {path}")

if __name__ == "__main__":
    main()