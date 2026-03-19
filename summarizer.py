# summarizer.py
import os
import re
import json
import anthropic

CATEGORY_LABELS = {
    "economia":      "Economia & Finanza",
    "tech":          "Tech & AI",
    "geopolitica":   "Geopolitica",
    "italia_europa": "Italia & Europa",
    "calcio":        "Calcio",
}

SYSTEM_PROMPT = """Sei un editor senior di un briefing giornaliero di qualità.
Ricevi una lista di articoli di notizie e devi produrre un digest approfondito e utile.
Rispondi SEMPRE in italiano, anche se gli articoli sono in inglese.
Sii diretto e analitico. Evita frasi generiche come "è importante sottolineare".
Quando scrivi le sintesi, ragiona su cause, conseguenze e collegamenti tra le notizie.

IMPORTANTE: Rispondi ESCLUSIVAMENTE con un oggetto JSON valido, senza testo prima o dopo,
senza backtick, senza markdown. Solo JSON puro."""

def build_user_prompt(category: str, articles: list[dict]) -> str:
    label = CATEGORY_LABELS.get(category, category)
    lines = [f"Categoria: {label}\n"]
    for i, art in enumerate(articles, 1):
        lines.append(f"{i}. {art['title']}")
        if art.get("summary"):
            lines.append(f"   {art['summary']}")
        lines.append(f"   Fonte: {art['source']}")
        lines.append("")

    lines.append("""
Restituisci SOLO questo JSON (nessun testo aggiuntivo):

{
  "sintesi": "Un paragrafo di 5-7 frasi che inquadra il momento attuale. Costruisci una narrativa che colleghi le notizie, evidenzi i temi ricorrenti e offra una lettura critica.",
  "notizie": [
    {
      "titolo": "Titolo breve e chiaro della notizia",
      "corpo": "3-4 frasi: cosa è successo, perché è successo, quali sono le conseguenze immediate.",
      "rilevanza": "Una frase sull'impatto più ampio — economico, politico, sociale.",
      "score": 3
    }
  ],
  "watch": "2-3 frasi su un trend da monitorare nelle prossime ore/giorni. Indica cosa osservare e quale scenario potrebbe aprirsi."
}

Regole:
- "notizie": includi le 3-5 notizie più importanti
- "score": da 1 (bassa rilevanza) a 3 (alta rilevanza)
- Tutti i valori stringa in italiano
- JSON valido, nessun carattere fuori dal JSON
""")
    return "\n".join(lines)


def summarize_category(category: str, articles: list[dict], client: anthropic.Anthropic) -> dict:
    """Chiama Claude e restituisce il digest come dizionario strutturato."""
    if not articles:
        return {"sintesi": "Nessun articolo trovato per questa categoria.", "notizie": [], "watch": ""}

    prompt = build_user_prompt(category, articles)
    for attempt in range(2):
        try:
            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2048,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = message.content[0].text.strip()
            # Rimuovi backtick residui
            raw = re.sub(r"^```json\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)
            # Estrai solo il blocco JSON se c'è testo attorno
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                raw = match.group(0)
            return json.loads(raw)
        except json.JSONDecodeError as e:
            print(f"[!] Tentativo {attempt + 1}/2 — JSON non valido per '{category}': {e}")
            if attempt == 1:
                return {"sintesi": "Digest non disponibile per questa categoria.", "notizie": [], "watch": ""}
        except Exception as e:
            print(f"[!] Errore API per '{category}': {e}")
            return {"sintesi": "Digest non disponibile per questa categoria.", "notizie": [], "watch": ""}


def summarize_all(articles_by_category: dict[str, list[dict]]) -> dict[str, dict]:
    """Genera i digest strutturati per tutte le categorie."""
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY non trovata in .env")

    client = anthropic.Anthropic(api_key=api_key)
    summaries = {}

    for category, articles in articles_by_category.items():
        print(f"[→] Riassumendo: {category} ({len(articles)} articoli)")
        summaries[category] = summarize_category(category, articles, client)

    return summaries