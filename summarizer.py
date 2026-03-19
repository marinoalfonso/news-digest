# summarizer.py
import os
import re
import json
import anthropic

CATEGORY_LABELS = {
    "economia":       "Economia & Finanza",
    "tech":           "Tech & AI",
    "geopolitica":    "Geopolitica",
    "italia_europa":  "Italia & Europa",
    "scienza_salute": "Scienza & Salute",
}

# ── Passaggio 1: selezione tematica ──────────────────────────────────────────

SELECTION_SYSTEM_PROMPT = """Sei un editor che deve selezionare le notizie più importanti da un pool di articoli.
Il tuo unico compito è identificare i macro temi del giorno e scegliere gli articoli più rappresentativi.
Rispondi ESCLUSIVAMENTE con un oggetto JSON valido, senza testo prima o dopo, senza backtick. Solo JSON puro."""

def build_selection_prompt(category: str, articles: list[dict]) -> str:
    label = CATEGORY_LABELS.get(category, category)
    lines = [f"Categoria: {label}", f"Hai {len(articles)} articoli disponibili:\n"]

    for i, art in enumerate(articles, 1):
        fonte = art.get("source", "")
        lines.append(f"{i}. [{fonte}] {art['title']}")

    lines.append("""
Il tuo compito:
1. Identifica i macro temi distinti che emergono da questi articoli
2. Per ogni tema scegli l'articolo più rappresentativo
3. Seleziona in totale 6-8 articoli che insieme coprono la maggior varietà tematica possibile
4. Dove possibile, evita di selezionare più articoli dalla stessa fonte
5. Preferisci articoli con impatto ampio rispetto a notizie di dettaglio

Restituisci SOLO questo JSON:
{
  "temi": [
    {
      "tema": "Nome breve del macro tema",
      "indice": 3
    }
  ]
}

Dove "indice" è il numero dell'articolo nella lista sopra (da 1 a N).
JSON valido, nessun testo aggiuntivo.
""")
    return "\n".join(lines)


def parse_json_safe(raw: str) -> dict | None:
    """Estrae e parsa il primo blocco JSON valido da una stringa."""
    raw = raw.strip()
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        raw = match.group(0)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def select_articles(category: str, articles: list[dict], client: anthropic.Anthropic) -> list[dict]:
    """Passaggio 1: chiede a Claude di identificare i temi e selezionare gli articoli."""
    if len(articles) <= 8:
        return articles

    prompt = build_selection_prompt(category, articles)

    for attempt in range(2):
        try:
            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=512,
                system=SELECTION_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            data = parse_json_safe(message.content[0].text)
            if not data or "temi" not in data:
                raise ValueError("JSON mancante o malformato")

            selected = []
            seen_indices = set()
            for item in data["temi"]:
                idx = int(item.get("indice", 0)) - 1
                if 0 <= idx < len(articles) and idx not in seen_indices:
                    seen_indices.add(idx)
                    selected.append(articles[idx])

            if selected:
                print(f"    Temi individuati: {[t['tema'] for t in data['temi']]}")
                return selected

        except Exception as e:
            print(f"[!] Selezione tentativo {attempt + 1}/2 per '{category}': {e}")

    print(f"[!] Selezione fallita per '{category}', uso i primi 8.")
    return articles[:8]


# ── Passaggio 2: sintesi e card ───────────────────────────────────────────────

SYNTHESIS_SYSTEM_PROMPT = """Sei un editor senior di un briefing giornaliero di qualità.
Ricevi una selezione di articoli già filtrati per varietà tematica e devi produrre un digest approfondito.
Rispondi SEMPRE in italiano, anche se gli articoli sono in inglese.
Sii diretto e analitico. Evita frasi generiche come "è importante sottolineare".
Ragiona su cause, conseguenze e collegamenti tra le notizie.

IMPORTANTE: Rispondi ESCLUSIVAMENTE con un oggetto JSON valido, senza testo prima o dopo,
senza backtick, senza markdown. Solo JSON puro."""

def build_synthesis_prompt(category: str, articles: list[dict]) -> str:
    label = CATEGORY_LABELS.get(category, category)
    lines = [f"Categoria: {label}\n"]

    for i, art in enumerate(articles, 1):
        lines.append(f"{i}. {art['title']}")
        if art.get("summary"):
            lines.append(f"   {art['summary']}")
        lines.append(f"   Fonte: {art['source']}")
        lines.append("")

    lines.append("""
Restituisci SOLO questo JSON:

{
  "sintesi": "Un paragrafo di 5-6 frasi che inquadra il momento attuale. Costruisci una narrativa che colleghi i temi, evidenzi i fili comuni e offra una lettura critica di quello che sta succedendo.",
  "notizie": [
    {
      "titolo": "Titolo breve e chiaro della notizia",
      "corpo": "2-3 frasi: cosa è successo, perché è successo, quali sono le conseguenze immediate.",
      "rilevanza": "Una frase sull'impatto più ampio — economico, politico, sociale.",
      "score": 3,
      "source_index": 1
    }
  ],
  "watch": "2-3 frasi su un trend da monitorare nelle prossime ore/giorni. Indica cosa osservare e quale scenario potrebbe aprirsi."
}

Regole:
- "notizie": includi le 3-4 notizie più rilevanti tra quelle disponibili
- "score": da 1 (bassa rilevanza) a 3 (alta rilevanza) — valuta impatto e ampiezza
- "source_index": numero dell'articolo in questa lista (da 1 a N) da cui proviene la notizia
- Tutti i valori stringa in italiano
- JSON valido, nessun testo aggiuntivo
""")
    return "\n".join(lines)


def synthesize_category(category: str, articles: list[dict], client: anthropic.Anthropic) -> dict:
    """Passaggio 2: genera sintesi, card e watch dagli articoli selezionati."""
    if not articles:
        return {"sintesi": "Nessun articolo trovato per questa categoria.", "notizie": [], "watch": "", "selected_articles": []}

    prompt = build_synthesis_prompt(category, articles)

    for attempt in range(2):
        try:
            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2048,
                system=SYNTHESIS_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            data = parse_json_safe(message.content[0].text)
            if not data:
                raise ValueError("JSON non valido")

            # Risolvi source_index → articolo reale
            for n in data.get("notizie", []):
                idx = int(n.get("source_index", 1)) - 1
                if 0 <= idx < len(articles):
                    n["_article"] = articles[idx]
                else:
                    n["_article"] = articles[0] if articles else {}

            data["selected_articles"] = articles
            return data

        except Exception as e:
            print(f"[!] Sintesi tentativo {attempt + 1}/2 per '{category}': {e}")

    return {"sintesi": "Digest non disponibile.", "notizie": [], "watch": "", "selected_articles": articles}


# ── Entry point ───────────────────────────────────────────────────────────────

def summarize_all(articles_by_category: dict[str, list[dict]]) -> dict[str, dict]:
    """Esegue i due passaggi per tutte le categorie e restituisce i digest."""
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY non trovata in .env")

    client = anthropic.Anthropic(api_key=api_key)
    summaries = {}

    for category, articles in articles_by_category.items():
        print(f"\n[→] Categoria: {category} ({len(articles)} articoli nel pool)")

        print(f"    [1/2] Selezione tematica...")
        selected = select_articles(category, articles, client)
        print(f"    → {len(selected)} articoli selezionati")

        print(f"    [2/2] Sintesi e card...")
        summaries[category] = synthesize_category(category, selected, client)
        print(f"    → Digest generato")

    return summaries