# main.py
import os
import webbrowser
from dotenv import load_dotenv
from config import CATEGORIES
from fetcher import fetch_all
from summarizer import summarize_all
from report import generate_html, save_report

def main():
    load_dotenv()
    print("=" * 50)
    print("  NEWS DIGEST — avvio")
    print("=" * 50)

    print("\n[1/3] Scarico gli articoli...")
    articles = fetch_all(CATEGORIES)

    total = sum(len(v) for v in articles.values())
    print(f"\n    Totale articoli raccolti: {total}")

    print("\n[2/3] Genero i digest con Claude...")
    summaries = summarize_all(articles)

    print("\n[3/3] Costruisco il report HTML...")
    html = generate_html(summaries, articles)
    path = save_report(html)

    print(f"\n✓ Report salvato in: {path}")

if __name__ == "__main__":
    main()
