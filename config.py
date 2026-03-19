# config.py
# Modifica questo file per aggiungere/rimuovere fonti e categorie.

# --- Categorie attive ---
CATEGORIES = ["economia", "tech", "geopolitica", "italia_europa", "scienza_salute"]

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
    "italia_europa": [
        "https://www.ansa.it/sito/ansait_rss.xml",
        "https://feeds.bbci.co.uk/news/world/europe/rss.xml",
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
    "italia_europa": "Italy OR European Union OR EU policy",
    "scienza_salute": "health OR medicine OR scientific research OR WHO",,
}
NEWSAPI_LANGUAGE = "en"       # "it" per italiano, "en" per inglese
NEWSAPI_PAGE_SIZE = 5         # articoli per categoria da NewsAPI

# --- Comportamento generale ---
MAX_ARTICLES_PER_CATEGORY = 8   # articoli totali (RSS + NewsAPI) per categoria
HOURS_LOOKBACK = 24             # quante ore indietro guardare
OUTPUT_DIR = "outputs"          # cartella dove salvare i digest HTML
