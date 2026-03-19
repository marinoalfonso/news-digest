# summarizer.py
import os
import anthropic

CATEGORY_LABELS = {
    "economia":      "Economia & Finanza",
    "tech":          "Tech & AI",
    "geopolitica":   "Geopolitica",
    "italia_europa": "Italia & Europa",
    "scienza_salute": "Scienza & Salute",
}

SYSTEM_PROMPT = """Sei un editor senior di un briefing giornaliero di qualità.
Ricevi una lista di articoli di notizie e devi produrre un digest approfondito e utile.
Rispondi SEMPRE in italiano, anche se gli articoli sono in inglese.
Sii diretto e analitico. Evita frasi generiche come "è importante sottolineare".
Quando scrivi le sintesi, ragiona sulle cause, le conseguenze e i collegamenti tra le notizie — non limitarti a riassumere i fatti."""

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
Produci un briefing strutturato così:

**Sintesi generale**
Un paragrafo di 5-7 frasi che inquadra il momento attuale per questa categoria di notizie.
Non elencare i fatti uno per uno: costruisci una narrativa che colleghi le notizie tra loro,
evidenzi i temi ricorrenti e offra una lettura critica di quello che sta succedendo.

**Notizie principali**
Per ciascuna delle 4-5 notizie più rilevanti:
- **Titolo breve e chiaro**
- 3-4 frasi di spiegazione: cosa è successo, perché è successo, quali sono le conseguenze immediate
- *Perché è rilevante:* una frase che spiega l'impatto più ampio — economico, politico, sociale

**Da tenere d'occhio**
2-3 frasi su un trend o sviluppo da monitorare nelle prossime ore/giorni.
Indica cosa osservare e quale scenario potrebbe aprirsi.
""")
    return "\n".join(lines)


def summarize_category(category: str, articles: list[dict], client: anthropic.Anthropic) -> str:
    """Chiama Claude e restituisce il briefing testuale per una categoria."""
    if not articles:
        return "_Nessun articolo trovato per questa categoria._"

    prompt = build_user_prompt(category, articles)
    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text
    except Exception as e:
        return f"_Errore nella generazione del digest: {e}_"


def summarize_all(articles_by_category: dict[str, list[dict]]) -> dict[str, str]:
    """Genera i digest per tutte le categorie."""
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY non trovata in .env")

    client = anthropic.Anthropic(api_key=api_key)
    summaries = {}

    for category, articles in articles_by_category.items():
        print(f"[→] Riassumendo: {category} ({len(articles)} articoli)")
        summaries[category] = summarize_category(category, articles, client)

    return summaries
