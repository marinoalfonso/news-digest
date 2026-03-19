# News Digest

Pipeline Python automatizzata che aggrega notizie da feed RSS e NewsAPI, genera digest giornalieri con Claude API e produce un report HTML consultabile nel browser. Lo scheduling è gestito tramite launchd su macOS e l'esecuzione avviene in un container Docker.

## Come funziona

1. **Fetch** — scarica fino a 8 articoli per categoria dalle ultime 24 ore tramite feed RSS e NewsAPI
2. **Summarize** — manda gli articoli a Claude API, che produce una sintesi approfondita per ogni categoria in italiano
3. **Report** — genera un file HTML con navigazione, sintesi, notizie principali e link alle fonti originali
4. **Scheduling** — launchd avvia il container Docker automaticamente ogni mattina alle 9

## Categorie

- 💹 Economia & Finanza
- 🤖 Tech & AI
- 🌍 Geopolitica
- 🇮🇹 Italia & Europa
- 🔬 Scienza & Salute

## Requisiti

- Docker
- Anthropic API key — [console.anthropic.com](https://console.anthropic.com)
- NewsAPI key — [newsapi.org](https://newsapi.org) (free tier: 100 req/giorno)

## Setup

```bash
# 1. Clona la repository
git clone https://github.com/marinoalfonso/news-digest.git
cd news-digest

# 2. Crea il file .env con le tue chiavi
cp .env.example .env
# Apri .env e inserisci ANTHROPIC_API_KEY e NEWSAPI_KEY

# 3. Costruisci l'immagine Docker
docker build -t news-digest .

# 4. Esegui
docker run --rm --env-file .env -v $(pwd)/outputs:/app/outputs news-digest
```

Il report HTML viene salvato in `outputs/` e può essere aperto direttamente nel browser.

## Scheduling automatico (macOS)

Per avviare il digest automaticamente ogni mattina alle 9 tramite launchd:

```bash
# Copia il file plist in LaunchAgents
cp com.alfonso.newsdigest.plist ~/Library/LaunchAgents/

# Carica il job
launchctl load ~/Library/LaunchAgents/com.alfonso.newsdigest.plist

# Test immediato
launchctl start com.alfonso.newsdigest

# Controlla i log
cat logs/digest.log
```

## Configurazione

Modifica `config.py` per personalizzare il comportamento:

```python
CATEGORIES          # categorie attive
RSS_FEEDS           # feed RSS per categoria
NEWSAPI_QUERIES     # query per NewsAPI per categoria
HOURS_LOOKBACK      # quante ore indietro guardare (default: 24)
MAX_ARTICLES_PER_CATEGORY  # articoli massimi per categoria (default: 8)
```

Dopo ogni modifica al codice, ricostruisci l'immagine Docker:

```bash
docker build -t news-digest .
```

## Struttura del progetto

```
news-digest/
├── config.py         # fonti e impostazioni
├── fetcher.py        # scarica da RSS e NewsAPI
├── summarizer.py     # genera digest con Claude API
├── report.py         # costruisce il report HTML
├── main.py           # entry point
├── Dockerfile
├── requirements.txt
├── com.alfonso.newsdigest.plist  # scheduling macOS
├── outputs/          # digest generati (ignorati da git)
└── logs/             # log di esecuzione (ignorati da git)
```