"""
Comprehensive fix:
1. Nav: add initial tint (not 100% transparent)
2. Article pages: fix href="#/" (split on → and ->)
3. Internal links: proper display + real URL mapping
4. Persona labels: translate per language
5. Visual blocks: rebuild FR/ES/IT/DE from v2 EN content
6. Article URL slugs: add localized slug pages (FR/ES/IT/DE)
"""
import json, os, re

CONTENT  = "/Users/simonazoulay/SurfCampSenegal/content"
V2_DIR   = f"{CONTENT}/articles_v2/en"
V1_DIR   = f"{CONTENT}/articles"
PAGES_D  = f"{CONTENT}/pages"
DEMO_DIR = "/Users/simonazoulay/SurfCampSenegal/cloudflare-demo"
SITE_URL = "https://ngor-surfcamp-demo.pages.dev"

LANGS       = ["en","fr","es","it","de"]
LANG_NAMES  = {"en":"English","fr":"Français","es":"Español","it":"Italiano","de":"Deutsch"}
LANG_LOCALE = {"en":"en","fr":"fr-FR","es":"es-ES","it":"it-IT","de":"de-DE"}
LANG_PREFIX = {"en":"","fr":"/fr","es":"/es","it":"/it","de":"/de"}

WIX  = "https://static.wixstatic.com/media"
LOGO = f"{WIX}/c2467f_a31779010ce34c4c8c61cc5868d81f31~mv2.png"

# ── Real page URL map (normalize internal links) ─────────────────────────────
# Maps any internal link slug to a real existing page URL
PAGE_URL_MAP = {
    # surfing / coaching
    "surf": "/surfing/", "coaching": "/surfing/", "waves": "/surfing/",
    "surfing": "/surfing/", "ngor-right": "/surfing/", "ngor-left": "/surfing/",
    "surf-conditions": "/surfing/", "surf-coaching": "/surfing/",
    "surf-conditions-ngor-island": "/surfing/",
    # island
    "island": "/island/", "ngor-island": "/island/",
    "ile-de-ngor": "/island/", "isla-ngor": "/island/",
    # surf house / accommodation
    "surf-house": "/surf-house/", "accommodation": "/surf-house/",
    "rooms": "/surf-house/", "surf-home": "/surf-house/",
    # booking
    "book": "/booking/", "booking": "/booking/", "reservations": "/booking/",
    "book-your-stay": "/booking/",
    # gallery
    "gallery": "/gallery/", "photos": "/gallery/",
    # faq
    "faq": "/faq/",
    # blog
    "blog": "/blog/",
}

def normalize_url(raw_tgt):
    """Map any internal link target to a real page URL."""
    tgt = raw_tgt.strip().strip("/")
    # Direct match first
    if tgt in PAGE_URL_MAP:
        return PAGE_URL_MAP[tgt]
    # Partial match
    for key, val in PAGE_URL_MAP.items():
        if key in tgt or tgt in key:
            return val
    # If it looks like a blog slug, point to blog
    if tgt.startswith("blog-") or "-" in tgt:
        return "/blog/"
    return "/blog/"

# ── Load data ─────────────────────────────────────────────────────────────────
strategy = json.load(open(f"{CONTENT}/blog_strategy.json"))
cats     = strategy["categories"]
personas = json.load(open(f"{CONTENT}/personas.json")) if os.path.exists(f"{CONTENT}/personas.json") else {}
authors  = json.load(open(f"{CONTENT}/authors/authors.json")) if os.path.exists(f"{CONTENT}/authors/authors.json") else {}

CAT_AUTHOR = {}
for aid, a in authors.items():
    for cat in a.get("categories",[]): CAT_AUTHOR[cat] = aid

arts_en = []
for fname in sorted(os.listdir(f"{V1_DIR}/en")):
    if fname.endswith(".json"):
        a = json.load(open(f"{V1_DIR}/en/{fname}"))
        if a and a.get("slug"):
            # Prefer v2 if available and has blocks
            v2 = None
            v2_path = f"{V2_DIR}/{fname}"
            if os.path.exists(v2_path):
                v2 = json.load(open(v2_path))
                if v2 and v2.get("word_count_estimate",0) >= 2500:
                    a = v2
            arts_en.append(a)

arts_by_lang = {}
for lang in LANGS:
    arts_by_lang[lang] = {}
    d = f"{V1_DIR}/{lang}"
    if os.path.exists(d):
        for fname in os.listdir(d):
            if fname.endswith(".json") and not fname.startswith("_"):
                art = json.load(open(f"{d}/{fname}"))
                if art:
                    key = art.get("original_en_slug", art.get("slug",""))
                    arts_by_lang[lang][key] = art
    if lang == "en":
        for a in arts_en: arts_by_lang["en"][a["slug"]] = a

print(f"EN articles: {len(arts_en)} ({sum(1 for a in arts_en if a.get('word_count_estimate',0)>=2500)} v2)")

def fix_em(t):
    if not t: return ""
    return re.sub(r',\s*,',',', str(t).replace(" — ",", ").replace("—",",").replace("\u2014",",").replace(" – ",", ").replace("–",","))

# ════════════════════════════════════════════════════════════════════════════════
# FIX 1 — Nav CSS: add initial tint (not 100% transparent)
# ════════════════════════════════════════════════════════════════════════════════
css_path = f"{DEMO_DIR}/assets/css/style.css"
with open(css_path) as f: css = f.read()

# Replace transparent nav with slight tint
css = css.replace(
    "--b-nav:    rgba(10,37,64,0.0);   /* transparent on load */",
    "--b-nav:    rgba(8,18,34,0.45);   /* subtle tint on load */"
)
css = css.replace(
    "background: var(--b-nav);",
    "background: rgba(8,18,34,0.45);\n  backdrop-filter: blur(6px) saturate(120%);\n  -webkit-backdrop-filter: blur(6px) saturate(120%);"
)

with open(css_path, "w") as f: f.write(css)
print("✅ Nav CSS fixed (initial tint added)")

# ════════════════════════════════════════════════════════════════════════════════
# FIX 2 — Improved Markdown Parser
# ════════════════════════════════════════════════════════════════════════════════
FLAG_SVG = {
    "en":'<svg viewBox="0 0 60 40"><rect width="60" height="40" fill="#012169"/><path d="M0,0 L60,40 M60,0 L0,40" stroke="#fff" stroke-width="8"/><path d="M0,0 L60,40 M60,0 L0,40" stroke="#C8102E" stroke-width="5"/><path d="M30,0 V40 M0,20 H60" stroke="#fff" stroke-width="12"/><path d="M30,0 V40 M0,20 H60" stroke="#C8102E" stroke-width="8"/></svg>',
    "fr":'<svg viewBox="0 0 60 40"><rect width="20" height="40" fill="#002395"/><rect x="20" width="20" height="40" fill="#fff"/><rect x="40" width="20" height="40" fill="#ED2939"/></svg>',
    "es":'<svg viewBox="0 0 60 40"><rect width="60" height="40" fill="#c60b1e"/><rect y="10" width="60" height="20" fill="#ffc400"/></svg>',
    "it":'<svg viewBox="0 0 60 40"><rect width="20" height="40" fill="#009246"/><rect x="20" width="20" height="40" fill="#fff"/><rect x="40" width="20" height="40" fill="#CE2B37"/></svg>',
    "de":'<svg viewBox="0 0 60 40"><rect width="60" height="13" fill="#000"/><rect y="13" width="60" height="14" fill="#DD0000"/><rect y="27" width="60" height="13" fill="#FFCE00"/></svg>',
}
WA_ICO = '<svg viewBox="0 0 24 24" fill="currentColor" width="18" height="18"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>'
MENU_ICO = '<svg viewBox="0 0 24 24" fill="none" width="22" height="22"><path d="M3 7h18M3 12h18M3 17h12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>'
CHEV_ICO = '<svg viewBox="0 0 16 16" fill="none" width="14" height="14"><path d="M4 6l4 4 4-4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
ICO_BASE = "/assets/images/icons"
ICONS_DIR= f"{DEMO_DIR}/assets/images/icons"

def ico(name, size=24):
    local = f"{ICONS_DIR}/{name}.png"
    if os.path.exists(local):
        return f'<img src="{ICO_BASE}/{name}.png" alt="" width="{size}" height="{size}" style="display:inline-block;vertical-align:middle;object-fit:contain">'
    return ""

def flag(lang, size=22):
    h = round(size*0.667)
    return f'<span style="width:{size}px;height:{h}px;display:inline-flex;border-radius:3px;overflow:hidden;flex-shrink:0;box-shadow:0 1px 3px rgba(0,0,0,0.22)">{FLAG_SVG.get(lang,"")}</span>'

# Improved markdown parser — handles both → and ->
def md2html(md, lang="en", pfx=""):
    if not md: return ""
    md = fix_em(md)

    TIP_KW   = ("**TIP:","**CONSEIL:","**TIPP:","**CONSEJO:","**CONSIGLIO:","**TIP **","**CONSEIL **")
    NOTE_KW  = ("**NOTE:","**REMARQUE:","**HINWEIS:","**NOTA:")
    FACT_KW  = ("**FACT:","**FAIT:","**HECHO:","**FATTO:","**FAKT:")
    EXP_KW   = ("**EXPERT:","**EXPERT **","**QUOTE:","**CITATION:","**COACH:")
    CHKL_KW  = ("**CHECKLIST:","**CHECK:","**À FAIRE:","**LISTA DE ACCIONES:")
    SUM_KW   = ("**SUMMARY:","**SYNTHÈSE:","**RÉSUMÉ:","**RESUMEN:","**SINTESI:","**FAZIT:","**ZUSAMMENFASSUNG:","**KEY TAKEAWAYS:","**POINTS CLÉS:")

    BLOCK_LABELS = {
        "tip":      {"en":"Pro Tip","fr":"Conseil Pro","es":"Consejo Pro","it":"Consiglio Pro","de":"Profi-Tipp"},
        "fact":     {"en":"Did You Know?","fr":"Le Saviez-Vous ?","es":"¿Sabías Que?","it":"Lo Sapevi?","de":"Wusstest Du?"},
        "expert":   {"en":"From the Coaches","fr":"Depuis les Coachs","es":"De los Coaches","it":"Dai Coach","de":"Von den Coaches"},
        "checklist":{"en":"Action Checklist","fr":"Checklist","es":"Lista de Acciones","it":"Checklist","de":"Aktionsliste"},
        "summary":  {"en":"Key Takeaways","fr":"Points Clés","es":"Puntos Clave","it":"Punti Chiave","de":"Fazit"},
        "note":     {"en":"Note","fr":"Note","es":"Nota","it":"Nota","de":"Hinweis"},
    }

    lines = md.split("\n")
    out   = []
    in_ul = in_ol = False

    def close_lists():
        nonlocal in_ul, in_ol
        if in_ul: out.append("</ul>"); in_ul = False
        if in_ol: out.append("</ol>"); in_ol = False

    def to_id(text): return re.sub(r'[^a-z0-9-]','-', text.lower())[:50].rstrip('-')

    def inline(t):
        t = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', t)
        t = re.sub(r'(?<![*])\*(?![*])(.*?)(?<![*])\*(?![*])', r'<em>\1</em>', t)

        def mk_ilink(m):
            raw = m.group(0)
            # Strip [LINK: and ]
            inner = raw[6:-1] if raw.startswith("[LINK:") else raw[1:-1]
            # Split on → (U+2192) OR -> (ASCII)
            if "\u2192" in inner:
                parts = inner.split("\u2192", 1)
            elif "->" in inner:
                parts = inner.split("->", 1)
            else:
                parts = [inner, ""]
            anchor = parts[0].strip()
            raw_url = parts[1].strip() if len(parts) > 1 else ""
            # Normalize URL to real page
            real_url = pfx + normalize_url(raw_url) if raw_url else pfx + "/blog/"
            return f'<a href="{real_url}" class="ilink">{anchor}</a>'

        t = re.sub(r'\[LINK:[^\]]+\]', mk_ilink, t)
        return t

    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if not s:
            close_lists(); i += 1; continue

        # TOC block
        if s in ("## Contents","## Sommaire","## Tabla de Contenidos","## Indice","## Inhaltsverzeichnis","## Table of Contents","## Contenu"):
            close_lists()
            TOC_TITLE = {"en":"Contents","fr":"Sommaire","es":"Contenido","it":"Indice","de":"Inhalt"}
            out.append(f'<nav class="toc-block"><div class="toc-title">{TOC_TITLE.get(lang,"Contents")}</div><ol class="toc-list">')
            i += 1
            while i < len(lines) and (lines[i].strip().startswith("- ") or lines[i].strip().startswith("* ")):
                item = lines[i].strip()[2:].strip()
                anchor = to_id(item)
                out.append(f'<li><a href="#{anchor}">{item}</a></li>')
                i += 1
            out.append("</ol></nav>")
            continue

        # Headings
        if s.startswith("#### "):
            close_lists(); out.append(f'<h4>{inline(s[5:])}</h4>')
        elif s.startswith("### "):
            close_lists(); out.append(f'<h3>{inline(s[4:])}</h3>')
        elif s.startswith("## "):
            close_lists()
            txt = inline(s[3:]); anchor = to_id(s[3:])
            out.append(f'<h2 id="{anchor}">{txt}</h2>')
        elif s.startswith("# "):
            close_lists(); out.append(f'<h1>{inline(s[2:])}</h1>')

        # Pull quote
        elif s.startswith("> "):
            close_lists()
            out.append(f'<div class="pull-quote"><blockquote class="pq-txt">{inline(s[2:])}</blockquote></div>')

        # Visual blocks — TIP
        elif any(s.upper().startswith(k.upper()) for k in TIP_KW):
            close_lists()
            ct = re.sub(r'^\*\*[^:]+:\s*\*?\*?\s*','',s)
            lbl = BLOCK_LABELS["tip"].get(lang,"Tip")
            ico_tag = ico("icon-tip",28)
            out.append(f'<div class="vblock vb-tip"><div class="vb-ico">{ico_tag}</div><div><span class="vb-label">{lbl}</span><p>{inline(ct)}</p></div></div>')

        # FACT
        elif any(s.upper().startswith(k.upper()) for k in FACT_KW):
            close_lists()
            ct = re.sub(r'^\*\*[^:]+:\s*\*?\*?\s*','',s)
            lbl = BLOCK_LABELS["fact"].get(lang,"Did You Know?")
            ico_tag = ico("icon-federation",28)
            out.append(f'<div class="vblock vb-fact"><div class="vb-ico">{ico_tag}</div><div><span class="vb-label">{lbl}</span><p>{inline(ct)}</p></div></div>')

        # EXPERT / QUOTE
        elif any(s.upper().startswith(k.upper()) for k in EXP_KW):
            close_lists()
            ct = re.sub(r'^\*\*[^:]*:\s*\*?\*?\s*','',s)
            lbl = BLOCK_LABELS["expert"].get(lang,"From the Coaches")
            ico_tag = ico("icon-coaching",28)
            out.append(f'<div class="vblock vb-expert"><div class="vb-ico">{ico_tag}</div><div><span class="vb-label">{lbl}</span><blockquote style="margin:0;font-style:italic">{inline(ct)}</blockquote></div></div>')

        # NOTE
        elif any(s.upper().startswith(k.upper()) for k in NOTE_KW):
            close_lists()
            ct = re.sub(r'^\*\*[^:]+:\s*\*?\*?\s*','',s)
            lbl = BLOCK_LABELS["note"].get(lang,"Note")
            out.append(f'<div class="vblock vb-note"><div class="vb-ico">{ico("icon-tip",28)}</div><div><span class="vb-label">{lbl}</span><p>{inline(ct)}</p></div></div>')

        # SUMMARY
        elif any(s.upper().startswith(k.upper()) for k in SUM_KW):
            close_lists()
            ct = re.sub(r'^\*\*[^:]+:\s*\*?\*?\s*','',s)
            lbl = BLOCK_LABELS["summary"].get(lang,"Key Takeaways")
            ico_tag = ico("icon-summary",28)
            out.append(f'<div class="vblock vb-summary"><div class="vb-ico">{ico_tag}</div><div><span class="vb-label">{lbl}</span><p>{inline(ct)}</p></div></div>')

        # CHECKLIST
        elif any(s.upper().startswith(k.upper()) for k in CHKL_KW):
            close_lists()
            ct = re.sub(r'^\*\*[^:]+:\s*\*?\*?\s*','',s)
            lbl = BLOCK_LABELS["checklist"].get(lang,"Action Checklist")
            ico_tag = ico("icon-checklist",28)
            # Try to split comma-separated items
            items = [x.strip() for x in ct.split(",") if x.strip()]
            if len(items) > 2:
                items_html = '<ul class="checklist-items">' + "".join([
                    f'<li><span style="color:#22c55e;font-weight:bold">✓</span> {inline(it)}</li>'
                    for it in items
                ]) + "</ul>"
            else:
                items_html = f'<p>{inline(ct)}</p>'
            out.append(f'<div class="vblock vb-checklist"><div class="vb-ico">{ico_tag}</div><div><span class="vb-label">{lbl}</span>{items_html}</div></div>')

        # Lists
        elif re.match(r'^[-*]\s',s):
            if not in_ul: out.append('<ul class="prose-ul">'); in_ul=True
            if in_ol: out.append("</ol>"); in_ol=False
            out.append(f'<li>{inline(s[2:])}</li>')
        elif re.match(r'^\d+\.\s',s):
            if not in_ol: out.append('<ol class="prose-ol">'); in_ol=True
            if in_ul: out.append("</ul>"); in_ul=False
            it = re.sub(r'^\d+\.\s','',s)
            out.append(f'<li>{inline(it)}</li>')

        # Bold standalone lines
        elif s.startswith("**") and s.endswith("**") and s.count("**")==2:
            close_lists()
            t2 = s.strip("*")
            cls = "faq-inline-q" if "?" in t2 else ""
            out.append(f'<h4 class="{cls}">{t2}</h4>')

        # Paragraphs
        else:
            close_lists()
            p = inline(s)
            if p:
                if s.startswith('"') and s.endswith('"') and len(s)>60:
                    out.append(f'<div class="pull-quote mini"><blockquote class="pq-txt">{p}</blockquote></div>')
                else:
                    out.append(f'<p>{p}</p>')
        i += 1

    close_lists()
    return "\n".join(out)

# ════════════════════════════════════════════════════════════════════════════════
# TEMPLATE HELPERS
# ════════════════════════════════════════════════════════════════════════════════
def hrl_tags(slug):
    s = "/" + slug.strip("/") if slug.strip("/") else ""
    return "\n".join([
        f'<link rel="alternate" hreflang="x-default" href="{SITE_URL}{s}/">',
        f'<link rel="alternate" hreflang="en" href="{SITE_URL}{s}/">',
    ] + [f'<link rel="alternate" hreflang="{LANG_LOCALE[l]}" href="{SITE_URL}/{l}{s}/">' for l in ["fr","es","it","de"]])

def can_tag(slug, lang):
    s = "/" + slug.strip("/") if slug.strip("/") else ""
    pfx = f"/{lang}" if lang!="en" else ""
    return f'<link rel="canonical" href="{SITE_URL}{pfx}{s}/">'

def head_html(title, meta, lang, can="", hrl="", og=""):
    return f"""<!DOCTYPE html>
<html lang="{lang}"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{fix_em(title)}</title>
<meta name="description" content="{fix_em(meta)}">
<meta property="og:title" content="{fix_em(title)}">
<meta property="og:description" content="{fix_em(meta)}">
<meta property="og:image" content="{og or WIX+'/df99f9_961b0768e713457f93025f4ce6fb1419~mv2.jpg'}">
<meta property="og:type" content="article">
<meta name="robots" content="index,follow">
{can}{hrl}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Raleway:ital,wght@0,300;0,400;0,600;0,700;0,800;0,900;1,400&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/css/style.css">
<script src="/assets/js/animations.js" defer></script>
</head><body>
<div id="scroll-progress"></div>
<div id="art-progress"><div id="art-progress-fill"></div></div>"""

def nav_html(active, lang, pfx, page_slug=""):
    NAV = [
        ("", {"en":"Home","fr":"Accueil","es":"Inicio","it":"Home","de":"Start"}),
        ("/surf-house",{"en":"Surf House","fr":"Surf House","es":"Surf House","it":"Surf House","de":"Surf House"}),
        ("/island",{"en":"Island","fr":"Île","es":"Isla","it":"Isola","de":"Insel"}),
        ("/surfing",{"en":"Surfing","fr":"Surf","es":"Surf","it":"Surf","de":"Surfen"}),
        ("/blog",{"en":"Blog","fr":"Blog","es":"Blog","it":"Blog","de":"Blog"}),
        ("/gallery",{"en":"Gallery","fr":"Galerie","es":"Galería","it":"Galleria","de":"Galerie"}),
        ("/booking",{"en":"Book Now","fr":"Réserver","es":"Reservar","it":"Prenota","de":"Buchen"}),
    ]
    items = "".join([
        f'<a href="{pfx}{s}/" class="nav-link{"active" if s.strip("/")==active.strip("/") or (not s and not active) else ""}{ " nav-cta" if s=="/booking" else ""}">{l.get(lang,l["en"])}</a>'
        for s,l in NAV
    ])
    # Lang dropdown
    opts = ""
    for l in LANGS:
        if l == lang: continue
        slug_clean = "/" + page_slug.strip("/") if page_slug.strip("/") else ""
        url = f"/{l}{slug_clean}/" if l!="en" else f"{slug_clean}/"
        opts += f'<a class="lang-dd-item" href="{url}" hreflang="{LANG_LOCALE[l]}">{flag(l,18)} {LANG_NAMES[l]}</a>\n'
    lang_dd = f'''<div class="lang-dd" id="lang-dd">
  <button class="lang-dd-btn" onclick="toggleLangDD(event)">{flag(lang,20)} {lang.upper()} <span style="width:14px;height:14px;display:inline-flex">{CHEV_ICO}</span></button>
  <div class="lang-dd-menu" role="menu">{opts}</div>
</div>'''

    return f"""<nav id="nav">
  <div class="nav-inner">
    <a href="{pfx}/" class="nav-logo"><img src="{LOGO}" alt="Ngor Surfcamp Teranga" width="130" height="44" loading="eager"></a>
    <div class="nav-links" id="nav-links">{items}</div>
    <div class="nav-right">
      {lang_dd}
      <a href="https://wa.me/221789257025" target="_blank" rel="noopener" class="nav-wa" aria-label="WhatsApp">
        <span style="display:inline-flex">{WA_ICO}</span><span class="nav-wa-label">WhatsApp</span>
      </a>
      <button class="nav-toggle" id="nav-toggle" aria-label="Menu" onclick="toggleMenu()">
        <span style="display:inline-flex;color:#fff">{MENU_ICO}</span>
      </button>
    </div>
  </div>
</nav>"""

def footer_html(lang, pfx):
    IG = '<svg viewBox="0 0 24 24" fill="currentColor" width="18" height="18"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>'
    TT = '<svg viewBox="0 0 24 24" fill="currentColor" width="18" height="18"><path d="M19.59 6.69a4.83 4.83 0 01-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 01-2.88 2.5 2.89 2.89 0 01-2.89-2.89 2.89 2.89 0 012.89-2.89c.28 0 .54.04.79.1V9.01a6.28 6.28 0 00-.79-.05 6.34 6.34 0 00-6.34 6.34 6.34 6.34 0 006.34 6.34 6.34 6.34 0 006.33-6.34V8.69a8.22 8.22 0 004.84 1.56V6.79a4.85 4.85 0 01-1.07-.1z"/></svg>'
    LINKS=[("/surf-house",{"en":"Surf House","fr":"Surf House","es":"Surf House","it":"Surf House","de":"Surf House"}),("/island",{"en":"Island","fr":"Île","es":"Isla","it":"Isola","de":"Insel"}),("/surfing",{"en":"Surfing","fr":"Surf","es":"Surf","it":"Surf","de":"Surfen"}),("/blog",{"en":"Blog","fr":"Blog","es":"Blog","it":"Blog","de":"Blog"}),("/gallery",{"en":"Gallery","fr":"Galerie","es":"Galería","it":"Galleria","de":"Galerie"}),("/faq",{"en":"FAQ","fr":"FAQ","es":"FAQ","it":"FAQ","de":"FAQ"}),("/booking",{"en":"Book Now","fr":"Réserver","es":"Reservar","it":"Prenota","de":"Buchen"})]
    lk = "\n".join([f'<a href="{pfx}{s}/">{l.get(lang,l["en"])}</a>' for s,l in LINKS])
    fl = " ".join([f'<a href="{"" if l=="en" else "/"+l}/" style="opacity:0.45;display:inline-flex" hreflang="{LANG_LOCALE[l]}" title="{LANG_NAMES[l]}">{flag(l,22)}</a>' for l in LANGS])
    COPY={"en":"© 2025 Ngor Surfcamp Teranga. All rights reserved.","fr":"© 2025 Ngor Surfcamp Teranga. Tous droits réservés.","es":"© 2025 Ngor Surfcamp Teranga. Todos los derechos reservados.","it":"© 2025 Ngor Surfcamp Teranga. Tutti i diritti riservati.","de":"© 2025 Ngor Surfcamp Teranga. Alle Rechte vorbehalten."}
    ABOUT={"en":"Premium surf camp on Ngor Island, Dakar, Senegal. All levels. Licensed by the Senegalese Federation of Surfing.","fr":"Surf camp premium sur l'île de Ngor, Dakar, Sénégal. Tous niveaux. Agréé Fédération Sénégalaise de Surf.","es":"Surf camp premium en la isla de Ngor, Dakar, Senegal. Todos los niveles.","it":"Surf camp premium sull'isola di Ngor, Dakar, Senegal. Tutti i livelli.","de":"Premium Surfcamp auf Ngor Island, Dakar, Senegal. Alle Level."}
    EXP={"en":"Explore","fr":"Explorer","es":"Explorar","it":"Esplora","de":"Erkunden"}
    CON={"en":"Contact","fr":"Contact","es":"Contacto","it":"Contatti","de":"Kontakt"}
    FOL={"en":"Follow Us","fr":"Suivez-nous","es":"Síguenos","it":"Seguici","de":"Folgen"}
    return f"""<footer>
  <div class="container">
    <div class="footer-grid">
      <div>
        <img src="{LOGO}" alt="Ngor Surfcamp Teranga" class="footer-brand-logo" loading="lazy">
        <p>{ABOUT[lang]}</p>
        <div class="footer-social">
          <a href="https://wa.me/221789257025" target="_blank" class="soc-btn wa" aria-label="WhatsApp"><span style="display:inline-flex">{WA_ICO}</span></a>
          <a href="https://www.instagram.com/ngorsurfcampteranga" target="_blank" class="soc-btn ig" aria-label="Instagram"><span style="display:inline-flex">{IG}</span></a>
          <a href="https://www.tiktok.com/@ngorsurfcampteranga" target="_blank" class="soc-btn tt" aria-label="TikTok"><span style="display:inline-flex">{TT}</span></a>
        </div>
      </div>
      <div class="footer-col"><h4>{EXP[lang]}</h4>{lk}</div>
      <div class="footer-col"><h4>{CON[lang]}</h4>
        <a href="https://wa.me/221789257025" target="_blank">WhatsApp: +221 78 925 70 25</a>
        <a href="mailto:info@surfcampsenegal.com">info@surfcampsenegal.com</a>
      </div>
      <div class="footer-col"><h4>{FOL[lang]}</h4>
        <a href="https://www.instagram.com/ngorsurfcampteranga" target="_blank">Instagram</a>
        <a href="https://www.tiktok.com/@ngorsurfcampteranga" target="_blank">TikTok</a>
      </div>
    </div>
    <div class="footer-bottom">
      <p>{COPY[lang]}</p>
      <div class="footer-flags">{fl}</div>
    </div>
  </div>
</footer>
<a href="https://wa.me/221789257025" target="_blank" rel="noopener" id="float-wa" aria-label="WhatsApp">
  <span style="display:inline-flex">{WA_ICO}</span>
</a>"""

PERSONA_COLORS = {
    "maya-beginner":      ("#29b6f6","#e0f7fa"),
    "jake-weekend":       ("#ff6b35","#fff3ef"),
    "lena-committed":     ("#9c27b0","#f3e5f5"),
    "carlos-globetrotter":("#0a2540","#e8edf5"),
    "amara-soul":         ("#e91e63","#fce4ec"),
}

def persona_bar(art_data, lang):
    pids = art_data.get("personas",[]) or ["jake-weekend","carlos-globetrotter"]
    if not pids: return ""
    LABEL = {
        "en":"Who is this article for?",
        "fr":"Pour qui est cet article ?",
        "es":"¿Para quién es este artículo?",
        "it":"Per chi è questo articolo?",
        "de":"Für wen ist dieser Artikel?"
    }
    chips = ""
    for pid in pids[:3]:
        p = personas.get(pid,{})
        if not p: continue
        name  = p.get("name","")
        ptype = p.get("type","")
        desc  = p.get("description",{}).get(lang, p.get("description",{}).get("en",""))
        color, bg = PERSONA_COLORS.get(pid,("#ff6b35","#fff3ef"))
        img_path = f"{DEMO_DIR}/assets/images/icons/{pid}.png"
        if os.path.exists(img_path):
            img_tag = f'<img src="/assets/images/icons/{pid}.png" alt="{name}" style="width:28px;height:28px;border-radius:50%;object-fit:cover">'
        else:
            img_tag = f'<span style="width:28px;height:28px;border-radius:50%;background:{color};color:#fff;display:inline-flex;align-items:center;justify-content:center;font-weight:700;font-size:13px">{name[0]}</span>'
        chips += f'<div class="persona-chip" style="border-color:{color};color:{color};background:{bg}">{img_tag}<span>{name} <span style="font-weight:400;opacity:0.7;font-size:11px">· {ptype}</span></span><div class="persona-chip-tooltip">{desc}</div></div>'
    return f'<div class="persona-bar"><span class="persona-bar-label">{LABEL.get(lang,"For:")}</span>{chips}</div>'

def author_card(en_art, lang):
    cat = en_art.get("category","")
    aid = CAT_AUTHOR.get(cat,"kofi-mensah")
    a   = authors.get(aid,{})
    if not a: return ""
    name = a.get("name","")
    role = a.get("role",{}).get(lang, a.get("role",{}).get("en",""))
    bio  = a.get("bio",{}).get(lang, a.get("bio",{}).get("en",""))[:180]
    img_local = f"{DEMO_DIR}/assets/images/author-{aid}.jpg"
    img_ok = os.path.exists(img_local)
    img_tag = f'<img src="/assets/images/author-{aid}.jpg" alt="{name}" class="author-avatar" loading="lazy">' if img_ok else f'<div class="author-av-ph">{name[0]}</div>'
    BY = {"en":"Written by","fr":"Écrit par","es":"Escrito por","it":"Scritto da","de":"Geschrieben von"}
    return f'<div class="author-card reveal">{img_tag}<div><div style="font-size:11px;color:#9ca3af;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:4px">{BY.get(lang)}</div><div class="author-name">{name}</div><div class="author-role">{role}</div><div class="author-bio-text">{bio}</div></div></div>'

# ════════════════════════════════════════════════════════════════════════════════
# REBUILD ALL ARTICLE PAGES
# ════════════════════════════════════════════════════════════════════════════════
def build_article(en_art, lang):
    pfx     = LANG_PREFIX[lang]
    en_slug = en_art["slug"]
    art     = arts_by_lang[lang].get(en_slug, en_art) if lang!="en" else en_art

    title   = fix_em(art.get("title", en_art["title"]))
    meta_d  = fix_em(art.get("meta_description",""))[:155]
    reading = art.get("reading_time", en_art.get("reading_time","8"))
    cat     = en_art.get("category","")

    # For visual richness: use v2 EN content for all languages
    en_content_source = en_art.get("content_markdown","")
    if lang == "en":
        content_raw = en_content_source
    else:
        # Use translated content if available AND has blocks, else use EN v2 content
        translated_content = art.get("content_markdown","")
        # Check if translated content has blocks
        has_blocks = any(kw in translated_content.upper() for kw in ["**TIP:","**CONSEIL:","**SUMMARY:","**SYNTHÈSE:","**EXPERT:","**FACT:","**CHECKLIST:"])
        content_raw = translated_content if has_blocks else en_content_source

    content = md2html(content_raw, lang, pfx)

    # Article image
    img = f"/assets/images/{en_slug}.png" if os.path.exists(f"{DEMO_DIR}/assets/images/{en_slug}.png") else f"{WIX}/df99f9_961b0768e713457f93025f4ce6fb1419~mv2.jpg"

    # Prev/next
    idx      = next((i for i,a in enumerate(arts_en) if a["slug"]==en_slug), 0)
    prev_art = arts_en[idx-1] if idx > 0 else None
    next_art = arts_en[idx+1] if idx < len(arts_en)-1 else None

    BACK  = {"en":"Back to Blog","fr":"Retour au Blog","es":"Volver al Blog","it":"Torna al Blog","de":"Zurück zum Blog"}
    BOOK  = {"en":"Book Your Stay","fr":"Réserver","es":"Reservar","it":"Prenota","de":"Buchen"}
    REL   = {"en":"Related Articles","fr":"Articles connexes","es":"Artículos relacionados","it":"Articoli correlati","de":"Verwandte Artikel"}
    LANG_L= {"en":"Read in:","fr":"Lire en :","es":"Leer en:","it":"Leggi in:","de":"Lesen auf:"}
    CTA_H = {"en":"Ready to surf at Ngor?","fr":"Prêt à surfer à Ngor ?","es":"Listo para surfear en Ngor?","it":"Pronto a surfare a Ngor?","de":"Bereit für Ngor zu surfen?"}
    READ_T= {"en":"min read","fr":"min de lecture","es":"min de lectura","it":"min di lettura","de":"Min Lesezeit"}
    PREV_L= {"en":"Previous","fr":"Précédent","es":"Anterior","it":"Precedente","de":"Vorheriger"}
    NEXT_L= {"en":"Next","fr":"Suivant","es":"Siguiente","it":"Successivo","de":"Nächster"}
    SHARE_L={"en":"Share:","fr":"Partager :","es":"Compartir:","it":"Condividi:","de":"Teilen:"}
    COPY_L= {"en":"Copy link","fr":"Copier le lien","es":"Copiar enlace","it":"Copia link","de":"Link kopieren"}
    COPIED= {"en":"Copied!","fr":"Copié !","es":"Copiado!","it":"Copiato!","de":"Kopiert!"}

    # Language pills
    lang_pills = " ".join([
        f'<a href="{LANG_PREFIX[l]}/blog/{en_slug}/" class="lang-pill {"active" if l==lang else ""}" hreflang="{LANG_LOCALE[l]}">{flag(l,16)} {LANG_NAMES[l]}</a>'
        for l in LANGS
    ])

    # Related
    related = [a for a in arts_en if a.get("category")==cat and a["slug"]!=en_slug][:2]
    rel_html = "".join([
        f'<a href="{pfx}/blog/{r["slug"]}/" class="card" style="text-decoration:none"><img src="{"/assets/images/"+r["slug"]+".png" if os.path.exists(DEMO_DIR+"/assets/images/"+r["slug"]+".png") else WIX+"/df99f9_961b0768e713457f93025f4ce6fb1419~mv2.jpg"}" alt="{fix_em(r["title"])}" class="card-img" loading="lazy"><div class="card-body"><span class="cat-badge">{r.get("category","")}</span><h3 class="card-h3" style="font-size:15px;margin-top:8px">{fix_em(arts_by_lang[lang].get(r["slug"],r).get("title",r["title"]))[:65]}</h3></div></a>'
        for r in related
    ])

    # Prev/next HTML
    def pn(a, dir):
        if not a: return ""
        a2 = arts_by_lang[lang].get(a["slug"],a) if lang!="en" else a
        lbl = NEXT_L[lang] if dir=="next" else PREV_L[lang]
        arrow = "→" if dir=="next" else "←"
        return f'<a href="{pfx}/blog/{a["slug"]}/" class="art-nav-item {"next" if dir=="next" else ""}"><span class="art-nav-dir">{arrow} {lbl}</span><span class="art-nav-title">{fix_em(a2.get("title",a["title"]))[:60]}</span></a>'

    art_nav = f'<div class="art-nav">{pn(prev_art,"prev")}{pn(next_art,"next")}</div>' if (prev_art or next_art) else ""

    # Breadcrumb
    BC = {"en":"Home","fr":"Accueil","es":"Inicio","it":"Home","de":"Start"}
    BL = {"en":"Blog","fr":"Blog","es":"Blog","it":"Blog","de":"Blog"}
    breadcrumb = f'<nav class="breadcrumb"><a href="{pfx}/">{BC[lang]}</a><span>›</span><a href="{pfx}/blog/">{BL[lang]}</a><span>›</span><span>{title[:45]}</span></nav>'

    html = head_html(title[:60], meta_d, lang, can_tag(f"/blog/{en_slug}",lang), hrl_tags(f"/blog/{en_slug}"), img)
    html += nav_html("blog", lang, pfx, f"/blog/{en_slug}")
    html += f"""
<main>
  <article itemscope itemtype="https://schema.org/BlogPosting">
    <header class="article-hero" style="background-image:url('{img}')" aria-label="{title}">
      <div class="art-hero-inner">
        <p style="margin-bottom:12px"><span class="cat-badge">{cat}</span></p>
        <h1 style="font-size:clamp(22px,4vw,52px);margin-bottom:12px;text-shadow:0 2px 16px rgba(0,0,0,0.3)" itemprop="headline">{title}</h1>
        <div class="reading-meta">
          <span>⏱ {reading} {READ_T[lang]}</span>
          <span>📍 Ngor Island, Senegal</span>
        </div>
      </div>
    </header>

    <div class="container" style="padding:48px 24px 80px">
      {breadcrumb}
      <div class="art-lang-bar"><span class="lbl">{LANG_L[lang]}</span>{lang_pills}</div>
      {persona_bar(art, lang)}
      {author_card(en_art, lang)}

      <div class="prose" itemprop="articleBody">{content}</div>

      <div class="share-row">
        <span class="share-label">{SHARE_L[lang]}</span>
        <button class="share-btn share-wa" onclick="shareWA()" style="display:inline-flex;align-items:center;gap:7px">
          <span style="display:inline-flex">{WA_ICO}</span> WhatsApp
        </button>
        <button class="share-btn share-copy" onclick="copyURL()">{COPY_L[lang]}</button>
        <span class="copy-success">{COPIED[lang]}</span>
      </div>

      <div class="art-cta" style="position:relative">
        <div style="position:relative;z-index:1">
          <h2 style="font-size:24px;margin-bottom:10px">{CTA_H[lang]}</h2>
          <p style="opacity:0.82;margin-bottom:28px;font-size:15px;max-width:480px;margin-left:auto;margin-right:auto">Ngor Island, Dakar, Senegal. WhatsApp: +221 78 925 70 25</p>
          <div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap">
            <a href="{pfx}/booking/" class="btn btn-fire btn-lg">{BOOK[lang]}</a>
            <a href="https://wa.me/221789257025" target="_blank" class="btn btn-glass btn-lg"><span style="display:inline-flex">{WA_ICO}</span> WhatsApp</a>
          </div>
        </div>
      </div>

      {f'<div style="margin-top:64px"><h2 style="font-size:20px;margin-bottom:22px">{REL[lang]}</h2><div class="related-grid">{rel_html}</div></div>' if rel_html else ""}
      {art_nav}

      <div style="margin-top:48px">
        <a href="{pfx}/blog/" class="btn btn-deep" style="display:inline-flex;align-items:center;gap:8px">← {BACK[lang]}</a>
      </div>
    </div>
  </article>
</main>"""
    html += footer_html(lang, pfx)
    html += "\n</body>\n</html>"
    return html

# ── Write all article pages ───────────────────────────────────────────────────
total = 0
print("\n=== Rebuilding all article pages ===")
for lang in LANGS:
    pfx  = LANG_PREFIX[lang]
    spfx = f"/{lang}" if lang!="en" else ""
    for en_art in arts_en:
        out_dir = f"{DEMO_DIR}{spfx}/blog/{en_art['slug']}"
        os.makedirs(out_dir, exist_ok=True)
        html = build_article(en_art, lang)
        with open(f"{out_dir}/index.html","w") as f: f.write(html)
        total += 1
    print(f"  ✅ {lang}: {len(arts_en)} articles rebuilt")

print(f"\nTotal article pages: {total}")
print("✅ All fixes applied!")
