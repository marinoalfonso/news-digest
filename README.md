# News Digest

Script Python che aggrega notizie da feed RSS e NewsAPI, le riassume con Claude, e genera un digest HTML giornaliero.

## Setup

```bash
# 1. Installa le dipendenze
pip install -r requirements.txt

# 2. Copia il file di esempio e inserisci le tue chiavi
cp .env.example .env

# 3. Lancia
python main.py
```

Il report si apre automaticamente nel browser e viene salvato in `outputs/`.

## Configurazione

Modifica `config.py` per:
- aggiungere/rimuovere categorie (`CATEGORIES`)
- aggiungere feed RSS (`RSS_FEEDS`)
- cambiare le query NewsAPI (`NEWSAPI_QUERIES`)
- modificare quante ore indietro guardare (`HOURS_LOOKBACK`)

## API Keys

- **Anthropic**: [console.anthropic.com](https://console.anthropic.com)
- **NewsAPI**: [newsapi.org](https://newsapi.org) — free tier: 100 req/giorno

## Struttura

```
news-digest/
├── config.py        # fonti e impostazioni
├── fetcher.py       # scarica da RSS e NewsAPI
├── summarizer.py    # genera digest con Claude
├── report.py        # costruisce l'HTML
├── main.py          # entry point
└── outputs/         # digest generati (ignorati da git)
```
