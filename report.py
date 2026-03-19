# report.py
import os
from datetime import datetime
from config import OUTPUT_DIR

CATEGORY_LABELS = {
    "economia":       "Economia & Finanza",
    "tech":           "Tech & AI",
    "geopolitica":    "Geopolitica",
    "italia_europa":  "Italia & Europa",
    "scienza_salute": "Scienza & Salute",
}


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
            f'<li>'
            f'<a href="{url}" target="_blank" rel="noopener">{title}</a>'
            f'<span class="source-tag">{source}</span>'
            f'</li>'
        )
    return "<ul class='sources-list'>" + "".join(items) + "</ul>"


def build_dots(score: int) -> str:
    """Genera i 3 pallini indicatori di rilevanza (score 1-3)."""
    dots = ""
    for i in range(1, 4):
        if i <= score:
            cls = "filled-high" if score == 3 else "filled-mid"
        else:
            cls = "empty"
        dots += f'<div class="dot {cls}"></div>'
    return dots


def build_card(notizia: dict) -> str:
    """Costruisce una card HTML da un oggetto notizia del JSON."""
    titolo = notizia.get("titolo", "")
    corpo = notizia.get("corpo", "")
    rilevanza = notizia.get("rilevanza", "")
    score = int(notizia.get("score", 2))
    dots = build_dots(score)
    score_label = {3: "Alta rilevanza", 2: "Media rilevanza", 1: "Bassa rilevanza"}.get(score, "")

    return f"""
      <div class="card">
        <div class="card-top">
          <span class="card-title">{titolo}</span>
          <div class="relevance" title="{score_label}">{dots}</div>
        </div>
        <p class="card-body">{corpo}</p>
        <span class="card-relevance-label">{rilevanza}</span>
      </div>"""


def generate_html(
    summaries: dict[str, dict],
    articles_by_category: dict[str, list[dict]],
) -> str:
    now = datetime.now()
    date_str = now.strftime("%A %d %B %Y").capitalize()

    sections_html = ""
    for i, (cat, digest) in enumerate(summaries.items()):
        label = CATEGORY_LABELS.get(cat, cat)
        articles = articles_by_category.get(cat, [])
        delay = f"{0.05 + i * 0.07:.2f}"

        sintesi = digest.get("sintesi", "")
        notizie = digest.get("notizie", [])
        watch = digest.get("watch", "")

        # Card delle notizie
        cards_html = "".join(build_card(n) for n in notizie)

        # Fonti espandibili
        sources_html = build_sources_html(articles)

        sections_html += f"""
        <section class="category-section" id="{cat}" style="animation-delay:{delay}s">
          <div class="category-label">
            <div class="category-line"></div>
            <span class="category-title">{label}</span>
            <div class="category-line"></div>
          </div>

          <p class="sintesi">{sintesi}</p>

          <p class="notizie-label">Notizie principali</p>
          <div class="cards">{cards_html}</div>

          <div class="watch">
            <p class="watch-label">Da tenere d'occhio</p>
            <p>{watch}</p>
          </div>

          <details class="sources-details">
            <summary>Fonti ({len(articles)})</summary>
            {sources_html}
          </details>
        </section>
        """

    nav_links = ""
    for cat, label in CATEGORY_LABELS.items():
        if cat in summaries:
            nav_links += f'<a href="#{cat}">{label}</a>\n'

    return f"""<!DOCTYPE html>
<html lang="it" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>News Digest — {now.strftime("%d/%m/%Y")}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
  <style>
    :root {{
      --serif: 'Playfair Display', Georgia, serif;
      --sans: 'DM Sans', sans-serif;
      --ease: cubic-bezier(.4,0,.2,1);
    }}
    [data-theme="dark"] {{
      --bg:        #0c0d0f;
      --bg2:       #13151a;
      --bg3:       #1c1f28;
      --border:    rgba(255,255,255,.07);
      --border2:   rgba(255,255,255,.13);
      --text:      #e8eaf0;
      --text2:     #7a7f96;
      --text3:     #4a4f66;
      --accent:    #f0e6c8;
      --tag-bg:    rgba(240,230,200,.08);
      --tag-text:  #c8b98a;
      --progress:  #c8b98a;
      --card-bg:   #13151a;
      --card-hover:#1c1f28;
      --dot-high:  #c8b98a;
      --dot-mid:   #7a7f96;
      --dot-low:   #2e3248;
      --link:      #7eb8f7;
    }}
    [data-theme="light"] {{
      --bg:        #f5f3ee;
      --bg2:       #ffffff;
      --bg3:       #eeece7;
      --border:    rgba(0,0,0,.07);
      --border2:   rgba(0,0,0,.13);
      --text:      #1a1b22;
      --text2:     #6b6f84;
      --text3:     #b0b4c8;
      --accent:    #8b6f3a;
      --tag-bg:    rgba(139,111,58,.08);
      --tag-text:  #8b6f3a;
      --progress:  #8b6f3a;
      --card-bg:   #ffffff;
      --card-hover:#f5f3ee;
      --dot-high:  #8b6f3a;
      --dot-mid:   #b0b4c8;
      --dot-low:   #dddbe5;
      --link:      #185fa5;
    }}
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      font-family: var(--sans);
      background: var(--bg);
      color: var(--text);
      font-size: 16px;
      line-height: 1.75;
      transition: background .3s var(--ease), color .3s var(--ease);
    }}
    #progress-bar {{
      position: fixed; top: 0; left: 0;
      height: 2px; width: 0%;
      background: var(--progress);
      z-index: 1000;
      transition: width .1s linear;
    }}
    header {{
      position: sticky; top: 0; z-index: 100;
      background: var(--bg);
      border-bottom: 1px solid var(--border);
      padding: 0 40px;
      display: flex; align-items: center; justify-content: space-between;
      height: 64px;
      backdrop-filter: blur(12px);
    }}
    .header-left {{ display: flex; align-items: baseline; gap: 16px; }}
    .logo {{
      font-family: var(--serif);
      font-size: 1.15rem; font-weight: 700;
      color: var(--text); letter-spacing: -.01em;
    }}
    .date-tag {{
      font-size: 0.75rem; color: var(--text2);
      font-weight: 300; letter-spacing: .04em; text-transform: uppercase;
    }}
    .header-right {{ display: flex; align-items: center; gap: 20px; }}
    .theme-toggle {{
      width: 36px; height: 20px;
      background: var(--bg3); border: 1px solid var(--border2);
      border-radius: 10px; cursor: pointer;
      position: relative; transition: background .3s; flex-shrink: 0;
    }}
    .theme-toggle::after {{
      content: ''; position: absolute;
      top: 3px; left: 3px; width: 12px; height: 12px;
      background: var(--accent); border-radius: 50%;
      transition: transform .25s var(--ease);
    }}
    [data-theme="light"] .theme-toggle::after {{ transform: translateX(16px); }}
    nav {{ display: flex; gap: 6px; flex-wrap: wrap; }}
    nav a {{
      font-size: 0.75rem; font-weight: 500;
      color: var(--text2); text-decoration: none;
      padding: 4px 12px; border-radius: 20px;
      border: 1px solid var(--border); letter-spacing: .02em;
      transition: all .2s var(--ease);
    }}
    nav a:hover {{ color: var(--text); border-color: var(--border2); background: var(--bg3); }}
    main {{ max-width: 720px; margin: 0 auto; padding: 56px 24px 80px; }}
    .category-section {{
      margin-bottom: 72px;
      opacity: 0; transform: translateY(16px);
      animation: fadeUp .5s var(--ease) forwards;
    }}
    .category-section:last-child {{ margin-bottom: 0; }}
    @keyframes fadeUp {{ to {{ opacity: 1; transform: translateY(0); }} }}
    .category-label {{
      display: flex; align-items: center; gap: 16px; margin-bottom: 24px;
    }}
    .category-line {{ flex: 1; height: 1px; background: var(--border); }}
    .category-title {{
      font-size: 0.68rem; font-weight: 500;
      letter-spacing: .14em; text-transform: uppercase;
      color: var(--text3); white-space: nowrap;
    }}
    .sintesi {{
      font-family: var(--serif);
      font-size: 1.02rem; line-height: 1.85;
      color: var(--text);
      margin-bottom: 32px; padding-bottom: 32px;
      border-bottom: 1px solid var(--border);
    }}
    .notizie-label {{
      font-size: 0.68rem; font-weight: 500;
      letter-spacing: .1em; text-transform: uppercase;
      color: var(--text3); margin-bottom: 12px;
    }}
    .cards {{ display: flex; flex-direction: column; gap: 2px; margin-bottom: 28px; }}
    .card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 10px; padding: 20px 24px;
      transition: background .2s var(--ease), border-color .2s var(--ease);
    }}
    .card:hover {{ background: var(--card-hover); border-color: var(--border2); }}
    .card-top {{
      display: flex; align-items: flex-start;
      justify-content: space-between; gap: 16px; margin-bottom: 10px;
    }}
    .card-title {{
      font-family: var(--serif);
      font-size: 1rem; font-weight: 600;
      color: var(--text); line-height: 1.4;
    }}
    .relevance {{ display: flex; gap: 4px; align-items: center; flex-shrink: 0; margin-top: 4px; }}
    .dot {{ width: 6px; height: 6px; border-radius: 50%; }}
    .dot.filled-high {{ background: var(--dot-high); }}
    .dot.filled-mid  {{ background: var(--dot-mid); }}
    .dot.empty       {{ background: var(--dot-low); }}
    .card-body {{
      font-size: 0.88rem; color: var(--text2);
      line-height: 1.7; margin-bottom: 12px;
    }}
    .card-relevance-label {{
      display: inline-block;
      font-size: 0.75rem; color: var(--tag-text);
      background: var(--tag-bg);
      padding: 3px 10px; border-radius: 4px;
    }}
    .watch {{
      background: var(--tag-bg);
      border-left: 2px solid var(--accent);
      border-radius: 0 8px 8px 0;
      padding: 16px 20px; margin-bottom: 28px;
    }}
    .watch-label {{
      font-size: 0.68rem; font-weight: 500;
      letter-spacing: .1em; text-transform: uppercase;
      color: var(--tag-text); margin-bottom: 6px;
    }}
    .watch p {{ font-size: 0.88rem; color: var(--text2); line-height: 1.7; }}
    .sources-details {{
      border-top: 1px solid var(--border); padding-top: 16px;
    }}
    .sources-details summary {{
      cursor: pointer; font-size: 0.68rem; font-weight: 500;
      letter-spacing: .08em; text-transform: uppercase;
      color: var(--text3); user-select: none; transition: color .2s;
    }}
    .sources-details summary:hover {{ color: var(--text2); }}
    .sources-list {{
      margin-top: 14px; padding: 0; list-style: none;
      display: flex; flex-direction: column; gap: 8px;
    }}
    .sources-list li {{ font-size: 0.83rem; display: flex; align-items: baseline; gap: 8px; }}
    .sources-list a {{ color: var(--link); text-decoration: none; }}
    .sources-list a:hover {{ text-decoration: underline; }}
    .source-tag {{
      font-size: 0.7rem; font-weight: 500;
      letter-spacing: .06em; text-transform: uppercase;
      color: var(--text3); flex-shrink: 0;
    }}
    footer {{
      text-align: center; padding: 32px;
      font-size: 0.72rem; letter-spacing: .06em; text-transform: uppercase;
      color: var(--text3); border-top: 1px solid var(--border);
    }}
  </style>
</head>
<body>
  <div id="progress-bar"></div>
  <header>
    <div class="header-left">
      <span class="logo">News Digest</span>
      <span class="date-tag">{date_str}</span>
    </div>
    <div class="header-right">
      <nav>{nav_links}</nav>
      <button class="theme-toggle" id="toggle" aria-label="Cambia tema"></button>
    </div>
  </header>
  <main>
    {sections_html}
  </main>
  <footer>Generato con Claude API &nbsp;&middot;&nbsp; {now.strftime("%d/%m/%Y %H:%M")}</footer>
  <script>
    window.addEventListener('scroll', () => {{
      const el = document.documentElement;
      const pct = (el.scrollTop / (el.scrollHeight - el.clientHeight)) * 100;
      document.getElementById('progress-bar').style.width = pct + '%';
    }});
    document.getElementById('toggle').addEventListener('click', () => {{
      const html = document.documentElement;
      html.dataset.theme = html.dataset.theme === 'dark' ? 'light' : 'dark';
    }});
  </script>
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