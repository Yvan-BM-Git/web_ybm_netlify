"""
actualizar_scholar.py
=====================
Genera un bloque HTML con tus métricas, gráfico de barras por año
y publicaciones de Google Scholar para insertarlo en tu página web.

INSTALACIÓN (una sola vez):
    pip install scholarly

USO:
    python actualizar_scholar.py

RESULTADO:
    Crea el archivo  scholar_widget.html  listo para copiar en tu index.html
"""

from scholarly import scholarly
from datetime import date
from collections import Counter

# ── Tu ID de Google Scholar ──
SCHOLAR_ID = "nsXyT_cAAAAJ"

print("🔍 Conectando con Google Scholar...")
print("   (puede tardar 10-30 segundos)\n")

# ── Obtener datos del autor ──
author = scholarly.search_author_id(SCHOLAR_ID)
author = scholarly.fill(author, sections=["basics", "indices", "publications", "counts"])

name        = author.get("name", "")
affiliation = author.get("affiliation", "")
citedby     = author.get("citedby", 0)
hindex      = author.get("hindex", 0)
i10index    = author.get("i10index", 0)
scholar_url = f"https://scholar.google.com/citations?user={SCHOLAR_ID}&hl=es"

print(f"✅ Datos obtenidos para: {name}")
print(f"   Citas totales : {citedby}")
print(f"   h-index       : {hindex}")
print(f"   i10-index     : {i10index}")

# ── Publicaciones ordenadas ──
pubs = author.get("publications", [])
pubs_sorted = sorted(
    pubs,
    key=lambda p: p.get("bib", {}).get("pub_year", "0"),
    reverse=True
)
print(f"   Publicaciones : {len(pubs_sorted)}\n")

# ── Citas por año (desde el perfil de Scholar) ──
cites_per_year = author.get("cites_per_year", {})  # dict {año: citas}

# ── Publicaciones por año ──
pub_years = [p.get("bib", {}).get("pub_year", "") for p in pubs]
pub_years = [y for y in pub_years if y]
pubs_per_year = dict(sorted(Counter(pub_years).items()))

# ── Normalizar años a enteros ──
cites_per_year = {int(k): v for k, v in cites_per_year.items()}

pubs_per_year = {int(k): v for k, v in pubs_per_year.items()}

# ── Rango de años combinado ──
all_years = sorted(set(cites_per_year.keys()) | set(pubs_per_year.keys()))
all_years_str = [str(y) for y in all_years]

# Valores para los gráficos
cites_values = [cites_per_year.get(int(y), cites_per_year.get(str(y), 0)) for y in all_years_str]
pubs_values  = [pubs_per_year.get(y, 0) for y in all_years_str]
max_cites    = max(cites_values) if cites_values else 1
max_pubs     = max(pubs_values)  if pubs_values  else 1

# ── Generar barras: CITAS por año ──
bars_cites = ""
for yr, val in zip(all_years_str, cites_values):
    pct = round((val / max_cites) * 100) if max_cites else 0
    bars_cites += f"""
        <div class="schart-col">
            <div class="schart-bar-wrap">
                <span class="schart-val">{val if val > 0 else ""}</span>
                <div class="schart-bar" style="height:{pct}%" title="{yr}: {val} citas"></div>
            </div>
            <div class="schart-label">{yr}</div>
        </div>"""

# ── Generar barras: PUBLICACIONES por año ──
bars_pubs = ""
for yr, val in zip(all_years_str, pubs_values):
    pct = round((val / max_pubs) * 100) if max_pubs else 0
    bars_pubs += f"""
        <div class="schart-col">
            <div class="schart-bar-wrap">
                <span class="schart-val">{val if val > 0 else ""}</span>
                <div class="schart-bar schart-bar--pubs" style="height:{pct}%" title="{yr}: {val} publicación(es)"></div>
            </div>
            <div class="schart-label">{yr}</div>
        </div>"""

# ── Generar lista de publicaciones ──
today = date.today().strftime("%d/%m/%Y")
html_pubs = ""
for i, pub in enumerate(pubs_sorted, 1):
    bib     = pub.get("bib", {})
    title   = bib.get("title", "Sin título")
    authors = bib.get("author", "")
    journal = bib.get("venue", bib.get("journal", ""))
    year    = bib.get("pub_year", "")
    cites   = pub.get("num_citations", 0)
    pub_url = pub.get("pub_url", "")

    link_html  = f'<a href="{pub_url}" target="_blank" class="scholar-pub-link">Ver publicación ↗</a>' if pub_url else ""
    cite_badge = f'<span class="scholar-cite-badge">📖 {cites} cita{"s" if cites != 1 else ""}</span>' if cites > 0 else ""

    html_pubs += f"""
            <div class="scholar-pub-item">
                <div class="scholar-pub-number">{i}</div>
                <div class="scholar-pub-content">
                    <div class="scholar-pub-title">{title}</div>
                    <div class="scholar-pub-authors">{authors}</div>
                    <div class="scholar-pub-meta">
                        <span class="scholar-pub-journal">{journal}</span>
                        {f'<span class="scholar-pub-year">{year}</span>' if year else ""}
                    </div>
                    <div class="scholar-pub-footer">
                        {cite_badge}
                        {link_html}
                    </div>
                </div>
            </div>"""

# ── HTML final ──
html_output = f"""<!-- ══ BLOQUE SCHOLAR — generado el {today} ══ -->
<!-- Pega este bloque ANTES de <div class="collaborators-container"> en tu index.html -->

<div class="scholar-widget">

    <!-- ── Tarjeta de métricas ── -->
    <div class="scholar-metrics-card">
        <div class="scholar-metrics-header">
            <svg viewBox="0 0 48 48" width="36" height="36">
                <path fill="#4285F4" d="M24 4L4 16l20 12 20-12z"/>
                <path fill="#356AC3" d="M4 16v16l20 12V28z"/>
                <path fill="#A8C7FA" d="M44 16v16L24 44V28z"/>
            </svg>
            <div>
                <div class="scholar-name">{name}</div>
                <div class="scholar-affiliation">{affiliation}</div>
            </div>
        </div>

        <div class="scholar-metrics-row">
            <div class="scholar-metric">
                <span class="scholar-metric-value">{citedby}</span>
                <span class="scholar-metric-label">Citas</span>
            </div>
            <div class="scholar-metric">
                <span class="scholar-metric-value">{hindex}</span>
                <span class="scholar-metric-label">h-index</span>
            </div>
            <div class="scholar-metric">
                <span class="scholar-metric-value">{i10index}</span>
                <span class="scholar-metric-label">i10-index</span>
            </div>
        </div>

        <!-- ── Gráfico: citas por año ── -->
        <div class="schart-section">
            <div class="schart-title">Citas por año</div>
            <div class="schart-bars">
                {bars_cites}
            </div>
        </div> 

        <div class="scholar-footer">
            <a href="{scholar_url}" target="_blank" class="scholar-profile-btn">
                Ver perfil completo en Google Scholar ↗
            </a>
            <span class="scholar-updated">Actualizado: {today}</span>
        </div>
    </div>
</div>

<!-- ══ ESTILOS ══ -->
<style>
.scholar-widget {{
    width: 100%;
    margin-top: 2rem;
    font-family: inherit;
}}
.scholar-metrics-card {{
    background: #fff;
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 6px rgba(0,0,0,0.08);
}}
.scholar-metrics-header {{
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 1.2rem;
}}
.scholar-name {{
    font-weight: 700;
    font-size: 1.05rem;
    color: #0072ce;
}}
.scholar-affiliation {{
    font-size: 0.85rem;
    color: #555;
    margin-top: 2px;
}}
.scholar-metrics-row {{
    display: flex;
    gap: 1.2rem;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
}}
.scholar-metric {{
    display: flex;
    flex-direction: column;
    align-items: center;
    background: #f5f8ff;
    border-radius: 8px;
    padding: 0.7rem 1.4rem;
    min-width: 80px;
}}
.scholar-metric-value {{
    font-size: 1.6rem;
    font-weight: 800;
    color: #0072ce;
    line-height: 1;
}}
.scholar-metric-label {{
    font-size: 0.78rem;
    color: #555;
    margin-top: 4px;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}}
/* Gráficos de barras */
.schart-section {{
    margin-bottom: 1.6rem;
}}
.schart-title {{
    font-size: 0.82rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #555;
    margin-bottom: 0.6rem;
}}
.schart-bars {{
    display: flex;
    align-items: flex-end;
    gap: 5px;
    height: 120px;
    padding-bottom: 26px;
    border-bottom: 2px solid #e0e0e0;
    position: relative;
}}
.schart-col {{
    display: flex;
    flex-direction: column;
    align-items: center;
    flex: 1;
    height: 100%;
    justify-content: flex-end;
}}
.schart-bar-wrap {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-end;
    height: 94px;
    width: 100%;
}}
.schart-val {{
    font-size: 0.65rem;
    color: #444;
    font-weight: 600;
    margin-bottom: 2px;
    min-height: 13px;
    text-align: center;
}}
.schart-bar {{
    width: 80%;
    background: #4285F4;
    border-radius: 3px 3px 0 0;
    min-height: 2px;
    transition: opacity 0.2s;
    cursor: default;
}}
.schart-bar:hover {{ opacity: 0.7; }}
.schart-bar--pubs {{
    background: #00b0da;
}}
.schart-label {{
    font-size: 0.65rem;
    color: #777;
    margin-top: 5px;
    text-align: center;
    writing-mode: vertical-lr;
    transform: rotate(180deg);
    height: 24px;
    line-height: 1;
}}
/* Footer */
.scholar-footer {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 0.5rem;
}}
.scholar-profile-btn {{
    background: #4285F4;
    color: #fff !important;
    padding: 8px 16px;
    border-radius: 6px;
    font-size: 0.85rem;
    font-weight: 600;
    text-decoration: none;
    transition: background 0.2s;
}}
.scholar-profile-btn:hover {{ background: #2c6ee8; }}
.scholar-updated {{
    font-size: 0.78rem;
    color: #888;
}}
/* Lista publicaciones */
.scholar-pubs-heading {{
    font-size: 1rem;
    font-weight: 700;
    color: #0072ce;
    border-left: 5px solid #00b0da;
    padding-left: 1rem;
    margin-bottom: 1rem;
}}
.scholar-pub-item {{
    background: #fff;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
    display: flex;
    gap: 1rem;
    align-items: flex-start;
    box-shadow: 0 2px 4px rgba(0,0,0,0.06);
}}
.scholar-pub-number {{
    background: #0072ce;
    color: #fff;
    font-size: 0.78rem;
    font-weight: 700;
    width: 26px; height: 26px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0; margin-top: 2px;
}}
.scholar-pub-title {{
    font-weight: 600;
    margin-bottom: 0.3rem;
    color: #222;
    font-size: 0.95rem;
}}
.scholar-pub-authors {{
    font-size: 0.85rem;
    color: #555;
    margin-bottom: 0.3rem;
}}
.scholar-pub-meta {{
    font-size: 0.83rem;
    margin-bottom: 0.4rem;
}}
.scholar-pub-journal {{ font-style: italic; color: #555; }}
.scholar-pub-year {{
    margin-left: 0.5rem;
    background: #e8f0fe;
    color: #0072ce;
    padding: 1px 7px;
    border-radius: 10px;
    font-size: 0.78rem;
    font-weight: 600;
}}
.scholar-pub-footer {{
    display: flex;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
}}
.scholar-cite-badge {{
    font-size: 0.8rem;
    color: #555;
}}
.scholar-pub-link {{
    font-size: 0.82rem;
    color: #4285F4;
    font-weight: 600;
}}
.scholar-pub-link:hover {{ text-decoration: underline; }}
</style>
<!-- ══ FIN BLOQUE SCHOLAR ══ -->
"""

# ── Guardar archivo ──
output_file = "scholar_widget.html"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(html_output)

print(f"✅ Archivo generado: {output_file}")
print(f"\n📋 INSTRUCCIONES:")
print(f"   1. Abre tu index.html")
print(f"   2. Busca esta línea:  <div class=\"collaborators-container\">")
print(f"   3. Pega el contenido de {output_file} justo ANTES de esa línea")
print(f"   4. Sube el index.html actualizado a Netlify")
print(f"\n🔄 Repite cada vez que quieras actualizar tus métricas.")