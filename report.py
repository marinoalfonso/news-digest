# report.py
import os
import re
from datetime import datetime
from config import OUTPUT_DIR

CATEGORY_LABELS = {
    "economia":      ("Economia & Finanza", "💹"),
    "tech":          ("Tech & AI", "🤖"),
    "geopolitica":   ("Geopolitica", "🌍"),
    "italia_europa": ("Italia & Europa", "🇮🇹"),
    "scienza_salute": ("Scienza & Salute", "🔬"),
}

CATEGORY_COLORS = {
    "economia":      "#3B8BD4",
    "tech":          "#7F77DD",
    "geopolitica":   "#D85A30",
    "italia_europa": "#1D9E75",
    "scienza_salute": "#D4537E",
}

def markdown_to_html(text: str) -> str:
    """Converte il markdown basilare di Claude in HTML."""
    # Bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    # Italic
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    # Bullet list items
    lines = text.split("\n")
    html_lines = []
    in_list = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- "):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            html_lines.append(f"<li>{stripped[2:]}</li>")
        else:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            if stripped:
                html_lines.append(f"<p>{stripped}</p>")
    if in_list:
        html_lines.append("</ul>")
    return "\n".join(html_lines)


def build_sources_html(articles: list[dict]) -> str:
    """Genera la lista delle fonti linkate per una categoria."""
    if not articles:
        return ""
    items = []
    for art in articles:
        url = art.get("url", "#")
        title = art.get("title", "Articolo")
        source = art.get("source", "")
        items.append(
            f'<li><a href="{url}" target="_blank" rel="noopener">'
            f'{title}</a> <span class="source-tag">{source}</span></li>'
        )
    return "<ul class='sources-list'>" + "".join(items) + "</ul>"


def generate_html(
    summaries: dict[str, str],
    articles_by_category: dict[str, list[dict]],
) -> str:
    now = datetime.now()
    date_str = now.strftime("%A %d %B %Y, %H:%M")

    # Costruisce le sezioni per categoria
    sections_html = ""
    for cat, summary_text in summaries.items():
        label, emoji = CATEGORY_LABELS.get(cat, (cat, "📰"))
        color = CATEGORY_COLORS.get(cat, "#888")
        articles = articles_by_category.get(cat, [])
        summary_html = markdown_to_html(summary_text)
        sources_html = build_sources_html(articles)

        sections_html += f"""
        <section class="category-section" id="{cat}">
          <div class="category-header" style="border-left: 4px solid {color}">
            <span class="category-emoji">{emoji}</span>
            <h2>{label}</h2>
            <span class="article-count">{len(articles)} articoli</span>
          </div>
          <div class="summary-content">
            {summary_html}
          </div>
          <details class="sources-details">
            <summary>Fonti ({len(articles)})</summary>
            {sources_html}
          </details>
        </section>
        """

    # Nav links
    nav_links = ""
    for cat in summaries:
        label, emoji = CATEGORY_LABELS.get(cat, (cat, "📰"))
        nav_links += f'<a href="#{cat}">{emoji} {label}</a>'

    return f"""<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>News Digest — {now.strftime("%d/%m/%Y")}</title>
  <style>
    :root {{
      --bg: #0f1117;
      --bg2: #1a1d27;
      --bg3: #22263a;
      --text: #e2e4ed;
      --text2: #9499b0;
      --border: #2e3250;
      --link: #7eb8f7;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.7;
      font-size: 16px;
    }}
    header {{
      background: var(--bg2);
      border-bottom: 1px solid var(--border);
      padding: 24px 0;
      text-align: center;
    }}
    header h1 {{ font-size: 1.6rem; font-weight: 600; letter-spacing: -0.02em; }}
    header .date {{ color: var(--text2); font-size: 0.9rem; margin-top: 4px; }}
    nav {{
      background: var(--bg2);
      border-bottom: 1px solid var(--border);
      padding: 12px 40px;
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }}
    nav a {{
      color: var(--text2);
      text-decoration: none;
      font-size: 0.85rem;
      padding: 4px 12px;
      border-radius: 20px;
      border: 1px solid var(--border);
      transition: all .15s;
    }}
    nav a:hover {{ color: var(--text); border-color: #4a5180; background: var(--bg3); }}
    main {{ max-width: 860px; margin: 0 auto; padding: 40px 24px; }}
    .category-section {{
      background: var(--bg2);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 28px 32px;
      margin-bottom: 28px;
    }}
    .category-header {{
      display: flex;
      align-items: center;
      gap: 12px;
      padding-left: 16px;
      margin-bottom: 20px;
    }}
    .category-emoji {{ font-size: 1.3rem; }}
    .category-header h2 {{ font-size: 1.15rem; font-weight: 600; }}
    .article-count {{
      margin-left: auto;
      font-size: 0.8rem;
      color: var(--text2);
      background: var(--bg3);
      padding: 2px 10px;
      border-radius: 12px;
    }}
    .summary-content p {{ margin-bottom: 12px; color: var(--text); }}
    .summary-content strong {{ color: #fff; font-weight: 600; }}
    .summary-content ul {{ margin: 8px 0 16px 20px; }}
    .summary-content li {{ margin-bottom: 6px; color: var(--text); }}
    .sources-details {{
      margin-top: 20px;
      border-top: 1px solid var(--border);
      padding-top: 16px;
    }}
    .sources-details summary {{
      cursor: pointer;
      font-size: 0.85rem;
      color: var(--text2);
      user-select: none;
    }}
    .sources-details summary:hover {{ color: var(--text); }}
    .sources-list {{
      margin-top: 12px;
      padding-left: 16px;
      list-style: none;
    }}
    .sources-list li {{ margin-bottom: 8px; font-size: 0.85rem; }}
    .sources-list a {{ color: var(--link); text-decoration: none; }}
    .sources-list a:hover {{ text-decoration: underline; }}
    .source-tag {{
      font-size: 0.75rem;
      color: var(--text2);
      background: var(--bg3);
      padding: 1px 7px;
      border-radius: 4px;
      margin-left: 4px;
    }}
    footer {{
      text-align: center;
      padding: 32px;
      font-size: 0.8rem;
      color: var(--text2);
      border-top: 1px solid var(--border);
    }}
  </style>
</head>
<body>
  <header>
    <h1>📰 News Digest</h1>
    <div class="date">{date_str}</div>
  </header>
  <nav>{nav_links}</nav>
  <main>
    {sections_html}
  </main>
  <footer>Generato con Claude API · {now.strftime("%d/%m/%Y %H:%M")}</footer>
</body>
</html>"""


def save_report(html: str) -> str:
    """Salva il file HTML e restituisce il path."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filename = datetime.now().strftime("digest_%Y%m%d_%H%M.html")
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return path
