# config.py
# Modifica questo file per aggiungere/rimuovere fonti e categorie.

# --- Categorie attive ---
CATEGORIES = ["economia", "tech", "geopolitica", "italia", "scienza_salute"]

# --- Feed RSS per categoria ---
RSS_FEEDS = {
    "economia": [
        "https://feeds.reuters.com/reuters/businessNews",
        "https://www.ft.com/rss/home/uk",                    # FT: titoli + abstract gratuiti
        "https://feeds.bloomberg.com/markets/news.rss",
    ],
    "tech": [
        "https://feeds.arstechnica.com/arstechnica/index",
        "https://techcrunch.com/feed/",
        "https://hnrss.org/frontpage",                       # Hacker News top stories
    ],
    "geopolitica": [
        "https://feeds.reuters.com/Reuters/worldNews",
        "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
        "https://feeds.bbci.co.uk/news/world/rss.xml",
    ],
    "italia": [
        "https://www.ansa.it/sito/ansait_rss.xml",
        "https://www.repubblica.it/rss/homepage/rss2.0.xml",
        "https://www.corriere.it/rss/homepage.xml",
    ],
    "scienza_salute": [
        "https://feeds.reuters.com/reuters/scienceNews",
        "https://feeds.bbci.co.uk/news/health/rss.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/Health.xml",
    ],
}

# --- NewsAPI ---
# Ottieni la tua chiave gratuita su https://newsapi.org
# Mettila nel file .env come: NEWSAPI_KEY=la_tua_chiave
NEWSAPI_QUERIES = {
    "economia":      "economy OR inflation OR markets OR stocks",
    "tech":          "artificial intelligence OR machine learning OR tech",
    "geopolitica":   "geopolitics OR war OR diplomacy OR UN",
    "italia": "Italy OR Italia OR governo italiano OR politica italiana",
    "scienza_salute": "health OR medicine OR scientific research OR WHO"
}
NEWSAPI_LANGUAGE = "en"       # "it" per italiano, "en" per inglese

# --- Comportamento generale ---
ARTICLES_PER_RSS_FEED = 5        # articoli per ogni singolo feed RSS
ARTICLES_FROM_NEWSAPI = 5        # articoli da NewsAPI per categoria
HOURS_LOOKBACK = 24             # quante ore indietro guardare
OUTPUT_DIR = "outputs"          # cartella dove salvare i digest HTML