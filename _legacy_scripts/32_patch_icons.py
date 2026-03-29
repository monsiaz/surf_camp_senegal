"""
Patch feat-icon sections on surf-house and surfing pages for all langs.
Uses real icon images when available, SVG inline as fallback.
"""
import os, re

DEMO     = "/Users/simonazoulay/SurfCampSenegal/cloudflare-demo"
ICONS_DIR= f"{DEMO}/assets/images/icons"
ICO_BASE = "/assets/images/icons"

LANGS    = ["en","fr","es","it","de"]
LANG_PFX = {"en":"","fr":"/fr","es":"/es","it":"/it","de":"/de"}

# ── Premium SVG icons (inline, always available) ─────────────────────────────
SVG = {
    "feat-transfer": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21 14H3l2-7h14l2 7z"/><path d="M3 14c3 3 15 3 18 0"/><path d="M8 7V5a2 2 0 014 0v2"/></svg>',
    "feat-food":     '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18M3 12h12M3 18h8"/><circle cx="17" cy="15" r="4"/><path d="M17 11v4h4"/></svg>',
    "feat-guide":    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2C6 2 2 8 2 14c0 3.5 2.5 6 5 8"/><path d="M22 14c0-4-2-8-6-11"/><path d="M8 19s1-1 4-1 4 1 4 1"/><circle cx="12" cy="12" r="3"/><path d="M12 9V2M12 22v-7"/></svg>',
    "feat-theory":   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="14" rx="2"/><path d="M7 21h10M12 17v4"/><path d="M7 8h10M7 11h6"/></svg>',
    "feat-pool":     '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12c2-3 4-3 6 0s4 3 6 0 4-3 6 0"/><path d="M2 17c2-3 4-3 6 0s4 3 6 0 4-3 6 0"/><path d="M8 7V4a1 1 0 011-1h2a1 1 0 011 1v3M16 7V5a1 1 0 011-1h1"/></svg>',
    "feat-wifi":     '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M1.5 8.5A14.5 14.5 0 0122.5 8.5"/><path d="M5 12.5a10 10 0 0114 0"/><path d="M8.5 16a5.5 5.5 0 017 0"/><circle cx="12" cy="20" r="1" fill="currentColor"/></svg>',
    "feat-coaching": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="7" r="4"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/><path d="M17 12l3 2-3 2"/></svg>',
    "feat-video":    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="6" width="14" height="12" rx="2"/><path d="M16 10l5-3v10l-5-3V10z"/><circle cx="9" cy="12" r="2"/></svg>',
    "feat-calendar": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/><circle cx="12" cy="16" r="2" fill="currentColor" stroke="none"/></svg>',
    "feat-check":    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5"/></svg>',
    "feat-location": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2C8 2 5 5 5 9c0 6 7 13 7 13s7-7 7-13c0-4-3-7-7-7z"/><circle cx="12" cy="9" r="2.5"/></svg>',
    "feat-star":     '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2l2.7 8.3H23l-7 5.1 2.7 8.3L12 18.6l-6.7 5.1L8 15.4 1 10.3h8.3z"/></svg>',
}

def get_icon(name, size=28):
    """Get icon img tag if file exists, else inline SVG."""
    png = f"{ICONS_DIR}/{name}.png"
    if os.path.exists(png) and os.path.getsize(png) > 5000:
        return f'<img src="{ICO_BASE}/{name}.png" alt="" width="{size}" height="{size}" style="object-fit:contain;display:block">'
    # Fallback: inline SVG styled to current color
    svg = SVG.get(name, SVG.get("feat-check",""))
    return f'<span style="width:{size}px;height:{size}px;display:inline-flex;align-items:center;justify-content:center;color:currentColor">{svg}</span>'

# ── New CSS for feat-icons ────────────────────────────────────────────────────
ICON_CSS = """
/* ══ FEATURE ICONS v2 ══════════════════════════════════════════ */
.feat-icon {
  width: 52px; height: 52px;
  border-radius: 16px;
  background: linear-gradient(135deg, var(--navy), #1a4a7a);
  box-shadow: 0 4px 16px rgba(10,37,64,0.30), inset 0 1px 0 rgba(255,255,255,0.08);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  color: var(--sand);
  transition: transform 0.25s var(--spring), box-shadow 0.25s;
  position: relative;
  overflow: hidden;
}
.feat-icon::before {
  content: '';
  position: absolute; inset: 0;
  background: radial-gradient(circle at 30% 30%, rgba(255,255,255,0.12), transparent 60%);
}
.feat:hover .feat-icon {
  transform: scale(1.08) rotate(4deg);
  box-shadow: 0 8px 24px rgba(10,37,64,0.35), 0 0 0 1.5px rgba(255,107,53,0.3);
}
.feat-icon img { position: relative; z-index: 1; filter: brightness(0) invert(1) sepia(1) saturate(2) hue-rotate(5deg); }
.feat-icon span svg { position: relative; z-index: 1; }
"""

css_path = f"{DEMO}/assets/css/style.css"
with open(css_path,'a') as f: f.write('\n/* feat-icon v2 */\n' + ICON_CSS)
print("✅ feat-icon CSS updated")

# ── Map emoji/old icons to new icon names ─────────────────────────────────────
# For surf house page
SURF_HOUSE_ICONS = {
    "en": [
        ("feat-transfer",  "Surf Transfers",       "Daily boat to Ngor Right & Left. Minibus to Dakar's best breaks."),
        ("feat-food",      "Breakfast & Dinner",    "Authentic Senegalese meals daily. Filtered water, tea & coffee."),
        ("feat-guide",     "Daily Surf Guiding",    "We guide you to the best spot of the day. All levels."),
        ("feat-theory",    "Surf Theory Classes",   "Free theory: paddling, pop-up, turns, wave reading."),
        ("feat-pool",      "Pool & Common Areas",   "Outdoor pool, terraces and chill spaces. Ngor Island is your backyard."),
        ("feat-wifi",      "Free Wi-Fi & Cleaning", "Stay connected. Rooms cleaned daily. Focus on the waves."),
    ],
    "fr": [
        ("feat-transfer",  "Transferts Surf",       "Pirogue quotidienne vers Ngor Right & Left. Minibus vers les meilleurs spots."),
        ("feat-food",      "Petit-déjeuner & Dîner","Plats sénégalais authentiques. Eau filtrée, thé et café inclus."),
        ("feat-guide",     "Guide Surf Quotidien",  "Nous vous guidons vers le meilleur spot chaque jour. Tous niveaux."),
        ("feat-theory",    "Cours de Théorie Surf", "Gratuit : paddle, pop-up, virages et lecture de l'océan."),
        ("feat-pool",      "Piscine & Espaces Communs","Piscine extérieure, terrasses. L'île de Ngor est votre arrière-cour."),
        ("feat-wifi",      "Wi-Fi Gratuit & Ménage Quotidien","Restez connecté. Chambres nettoyées quotidiennement."),
    ],
    "es": [
        ("feat-transfer",  "Traslados Surf",        "Bote diario a Ngor Right & Left. Minibús a los mejores spots de Dakar."),
        ("feat-food",      "Desayuno y Cena",       "Comidas senegalesas auténticas diariamente. Agua filtrada, té y café."),
        ("feat-guide",     "Guía Surf Diario",      "Te llevamos al mejor spot del día. Todos los niveles."),
        ("feat-theory",    "Clases de Teoría Surf", "Gratuitas: remo, pop-up, giros y lectura del océano."),
        ("feat-pool",      "Piscina & Áreas Comunes","Piscina exterior, terrazas. La isla de Ngor es tu patio."),
        ("feat-wifi",      "Wi-Fi Gratis & Limpieza","Mantente conectado. Habitaciones limpias diariamente."),
    ],
    "it": [
        ("feat-transfer",  "Trasferimenti Surf",    "Barca giornaliera a Ngor Right & Left. Minibus verso i migliori spot."),
        ("feat-food",      "Colazione e Cena",      "Pasti senegalesi autentici quotidianamente. Acqua filtrata, tè e caffè."),
        ("feat-guide",     "Guida Surf Giornaliera","Ti guidiamo verso il miglior spot ogni giorno. Tutti i livelli."),
        ("feat-theory",    "Lezioni di Teoria Surf","Gratuite: paddling, pop-up, virate e lettura dell'oceano."),
        ("feat-pool",      "Piscina & Aree Comuni", "Piscina esterna, terrazze. L'isola di Ngor è il tuo giardino."),
        ("feat-wifi",      "Wi-Fi Gratuito & Pulizia","Rimani connesso. Camera pulita quotidianamente."),
    ],
    "de": [
        ("feat-transfer",  "Surf-Transfers",        "Tägliches Boot zu Ngor Right & Left. Minibus zu Dakars besten Spots."),
        ("feat-food",      "Frühstück & Abendessen","Authentische senegalesische Mahlzeiten täglich. Gefiltertes Wasser, Tee und Kaffee."),
        ("feat-guide",     "Tägliche Surf-Führung", "Wir führen Sie täglich zum besten Spot. Alle Level willkommen."),
        ("feat-theory",    "Surf-Theoriestunden",   "Kostenlos: Paddeln, Pop-up, Kurven und Ozean lesen."),
        ("feat-pool",      "Pool & Gemeinschaftsbereiche","Außenpool, Terrassen. Ngor Island ist Ihr Garten."),
        ("feat-wifi",      "Kostenloses WLAN & Reinigung","Bleiben Sie verbunden. Zimmer täglich gereinigt."),
    ],
}

# For surfing page
SURFING_ICONS = {
    "en": [
        ("feat-video",    "Video Analysis",        "We film your sessions and review the footage together on a tablet at the beach."),
        ("feat-coaching", "All Levels Welcome",    "Beginner to advanced, we tailor every session to your exact level and goals."),
        ("feat-check",    "Licensed Federation",   "Officially licensed by the Senegalese Federation of Surfing. Safety first."),
        ("feat-guide",    "Ngor Right & Left",     "Two world-class breaks: Ngor Right for intermediate/advanced, Left for all levels."),
    ],
    "fr": [
        ("feat-video",    "Analyse Vidéo",         "Nous filmons vos sessions et analysons les images avec vous sur la plage."),
        ("feat-coaching", "Tous Niveaux Bienvenus","Du débutant à l'avancé, chaque session est adaptée à votre niveau exact."),
        ("feat-check",    "Fédération Agréée",     "Officiellement agréé par la Fédération Sénégalaise de Surf. Sécurité en premier."),
        ("feat-guide",    "Ngor Right & Left",     "Deux breaks de classe mondiale : Ngor Right pour intermédiaires/avancés, Left pour tous."),
    ],
    "es": [
        ("feat-video",    "Análisis de Vídeo",     "Filmamos tus sesiones y analizamos las grabaciones contigo en la playa."),
        ("feat-coaching", "Todos los Niveles",     "De principiante a avanzado, adaptamos cada sesión a tu nivel exacto."),
        ("feat-check",    "Federación Licenciada", "Oficialmente licenciado por la Federación Senegalesa de Surf. Seguridad primero."),
        ("feat-guide",    "Ngor Right & Left",     "Dos breaks de clase mundial: Ngor Right para intermedios/avanzados, Left para todos."),
    ],
    "it": [
        ("feat-video",    "Analisi Video",         "Filmiamo le tue sessioni e analizziamo le riprese con te sulla spiaggia."),
        ("feat-coaching", "Tutti i Livelli",       "Dal principiante all'avanzato, adattiamo ogni sessione al tuo livello esatto."),
        ("feat-check",    "Federazione Autorizzata","Ufficialmente autorizzato dalla Federazione Senegalese di Surf."),
        ("feat-guide",    "Ngor Right & Left",     "Due break di classe mondiale: Ngor Right per intermedi/avanzati, Left per tutti."),
    ],
    "de": [
        ("feat-video",    "Videoanalyse",          "Wir filmen Ihre Sessions und analysieren die Aufnahmen mit Ihnen am Strand."),
        ("feat-coaching", "Alle Level Willkommen", "Von Anfänger bis Fortgeschrittener, jede Session wird genau angepasst."),
        ("feat-check",    "Lizenzierte Fédération","Offiziell lizenziert vom senegalesischen Surfverband. Sicherheit zuerst."),
        ("feat-guide",    "Ngor Right & Left",     "Zwei Weltklasse-Breaks: Ngor Right für Fortgeschrittene, Left für alle."),
    ],
}

def build_feat_grid(items):
    """Build a features grid with proper icons."""
    cells = ""
    for ico_name, title, desc in items:
        ico_html = get_icon(ico_name, 26)
        cells += f'''<div class="feat">
  <div class="feat-icon">{ico_html}</div>
  <div>
    <div class="feat-title">{title}</div>
    <div class="feat-text">{desc}</div>
  </div>
</div>'''
    return f'<div class="grid-3">{cells}</div>'

def build_surfing_feat(items):
    """Build surfing features (2-col grid)."""
    cells = ""
    for ico_name, title, desc in items:
        ico_html = get_icon(ico_name, 26)
        cells += f'''<div class="feat">
  <div class="feat-icon">{ico_html}</div>
  <div>
    <div class="feat-title">{title}</div>
    <div class="feat-text">{desc}</div>
  </div>
</div>'''
    return f'<div class="grid-2">{cells}</div>'

# Patch surf-house pages
print("\n=== Patching surf-house pages ===")
for lang in LANGS:
    pfx  = LANG_PFX[lang]
    spfx = f"/{lang}" if lang!="en" else ""
    hp   = f"{DEMO}{spfx}/surf-house/index.html"
    if not os.path.exists(hp): continue
    with open(hp) as f: html = f.read()

    items    = SURF_HOUSE_ICONS[lang]
    new_grid = build_feat_grid(items)

    # Replace any existing feat grid inside the amenities/inclusions section
    html_new = re.sub(
        r'<div class="grid-[23]">\s*(?:<div class="feat">.*?</div>\s*)+</div>',
        new_grid,
        html, flags=re.DOTALL, count=1
    )
    if html_new != html:
        with open(hp,'w') as f: f.write(html_new)
        print(f"  ✅ {lang} surf-house")
    else:
        print(f"  ⚠️  {lang} surf-house: pattern not matched, injecting")
        # Inject before </section> of the amenities section
        html_new = html.replace(
            '<h2 class="s-title reveal" style="text-align:center;margin-bottom:52px">',
            f'<!-- icons injected -->\n'
        )
        with open(hp,'w') as f: f.write(html_new)

# Patch surfing pages
print("\n=== Patching surfing pages ===")
for lang in LANGS:
    pfx  = LANG_PFX[lang]
    spfx = f"/{lang}" if lang!="en" else ""
    hp   = f"{DEMO}{spfx}/surfing/index.html"
    if not os.path.exists(hp): continue
    with open(hp) as f: html = f.read()

    items    = SURFING_ICONS[lang]
    new_grid = build_surfing_feat(items)

    html_new = re.sub(
        r'<div class="grid-[23]">\s*(?:<div class="feat">.*?</div>\s*)+</div>',
        new_grid,
        html, flags=re.DOTALL, count=1
    )
    if html_new != html:
        with open(hp,'w') as f: f.write(html_new)
        print(f"  ✅ {lang} surfing")
    else:
        print(f"  ⚠️  {lang} surfing: no match")

print("\n✅ Done!")
