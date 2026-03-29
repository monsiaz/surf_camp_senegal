"""
Comprehensive fix:
1. Translated URL slugs: /fr/ile/, /es/isla/, /it/isola/, /de/insel/ etc.
2. Updated nav with correct localized slugs
3. Updated hreflang pointing to localized URLs
4. Language selector navigates to correct localized URL
5. Redirect pages at old slug locations
6. Fix block labels: EN content → always EN labels regardless of page lang
7. Redesign buttons to match DA
"""
import os, re, shutil

DEMO     = "/Users/simonazoulay/SurfCampSenegal/cloudflare-demo"
SITE_URL = "https://ngor-surfcamp-demo.pages.dev"
LANGS    = ["en","fr","es","it","de"]
LANG_PFX = {"en":"","fr":"/fr","es":"/es","it":"/it","de":"/de"}

# ── Localized slug map ────────────────────────────────────────────────────────
SLUG = {
    "en": {"surf-house":"surf-house","island":"island","surfing":"surfing","booking":"booking","gallery":"gallery","faq":"faq","blog":"blog"},
    "fr": {"surf-house":"surf-house","island":"ile","surfing":"surf","booking":"reservation","gallery":"galerie","faq":"faq","blog":"blog"},
    "es": {"surf-house":"surf-house","island":"isla","surfing":"surf","booking":"reservar","gallery":"galeria","faq":"faq","blog":"blog"},
    "it": {"surf-house":"surf-house","island":"isola","surfing":"surf","booking":"prenota","gallery":"galleria","faq":"faq","blog":"blog"},
    "de": {"surf-house":"surf-house","island":"insel","surfing":"surfen","booking":"buchen","gallery":"galerie","faq":"faq","blog":"blog"},
}

# Reverse map: for a given lang+old_slug → new_slug
def old_to_new(lang, old_slug):
    return SLUG[lang].get(old_slug, old_slug)

# All static pages: page_key → (old_slug, build_fn_exists)
STATIC_PAGES = ["surf-house","island","surfing","booking","gallery","faq"]

# ── Step 1: Copy pages to new localized slug paths ────────────────────────────
print("=== Step 1: Copy pages to localized slugs ===")
for lang in LANGS:
    if lang == "en": continue  # EN slugs stay as-is
    pfx  = LANG_PFX[lang]
    spfx = f"/{lang}"
    for page_key in STATIC_PAGES:
        new_slug = SLUG[lang][page_key]
        if new_slug == page_key: continue  # No change for this lang
        
        old_path = f"{DEMO}{spfx}/{page_key}/index.html"
        new_dir  = f"{DEMO}{spfx}/{new_slug}"
        new_path = f"{new_dir}/index.html"
        
        if not os.path.exists(old_path):
            print(f"  ⚠️  Missing: {old_path}")
            continue
        
        os.makedirs(new_dir, exist_ok=True)
        with open(old_path) as f: html = f.read()
        
        # Update canonical URL
        old_can = f'href="{SITE_URL}/{lang}/{page_key}/"'
        new_can = f'href="{SITE_URL}/{lang}/{new_slug}/"'
        html = html.replace(old_can, new_can)
        
        with open(new_path,'w') as f: f.write(html)
        print(f"  ✅ {lang}/{page_key} → {lang}/{new_slug}")

# ── Step 2: Create redirect pages at old slug locations ───────────────────────
print("\n=== Step 2: Create redirects old→new ===")
def make_redirect(from_url, to_url):
    return f'''<!DOCTYPE html><html><head>
<meta http-equiv="refresh" content="0;url={to_url}">
<link rel="canonical" href="{to_url}">
<title>Redirecting...</title>
</head><body>
<script>location.href="{to_url}";</script>
</body></html>'''

for lang in LANGS:
    if lang == "en": continue
    spfx = f"/{lang}"
    for page_key in STATIC_PAGES:
        new_slug = SLUG[lang][page_key]
        if new_slug == page_key: continue
        
        old_dir  = f"{DEMO}{spfx}/{page_key}"
        old_path = f"{old_dir}/index.html"
        new_url  = f"{SITE_URL}/{lang}/{new_slug}/"
        
        # Overwrite old path with redirect
        redirect_html = make_redirect(f"{SITE_URL}/{lang}/{page_key}/", new_url)
        with open(old_path,'w') as f: f.write(redirect_html)
        print(f"  ↩️  /{lang}/{page_key}/ → /{lang}/{new_slug}/")

# ── Step 3: Update all nav links + hreflang everywhere ───────────────────────
print("\n=== Step 3: Update nav + hreflang in all HTML files ===")

# Build complete URL tables for hreflang
def page_hreflang(page_key):
    """Generate hreflang links for a page across all languages."""
    lines = [f'<link rel="alternate" hreflang="x-default" href="{SITE_URL}/{SLUG["en"][page_key]}/">']
    lines.append(f'<link rel="alternate" hreflang="en" href="{SITE_URL}/{SLUG["en"][page_key]}/">')
    for lang in ["fr","es","it","de"]:
        s = SLUG[lang][page_key]
        lines.append(f'<link rel="alternate" hreflang="{{"fr":"fr-FR","es":"es-ES","it":"it-IT","de":"de-DE"}}[lang]" href="{SITE_URL}/{lang}/{s}/">')
    return "\n".join(lines)

LANG_LOCALE = {"fr":"fr-FR","es":"es-ES","it":"it-IT","de":"de-DE"}

def get_hreflang(page_key):
    lines = [
        f'<link rel="alternate" hreflang="x-default" href="{SITE_URL}/{SLUG["en"][page_key]}/">',
        f'<link rel="alternate" hreflang="en" href="{SITE_URL}/{SLUG["en"][page_key]}/">',
    ]
    for lang in ["fr","es","it","de"]:
        s = SLUG[lang][page_key]
        lines.append(f'<link rel="alternate" hreflang="{LANG_LOCALE[lang]}" href="{SITE_URL}/{lang}/{s}/">')
    return "\n".join(lines)

# Build new nav HTML for each language (using localized slugs)
LANG_NAMES = {"en":"English","fr":"Français","es":"Español","it":"Italiano","de":"Deutsch"}

NAV_LABELS = {
    "home":     {"en":"Home","fr":"Accueil","es":"Inicio","it":"Home","de":"Start"},
    "surf-house":{"en":"Surf House","fr":"Surf House","es":"Surf House","it":"Surf House","de":"Surf House"},
    "island":   {"en":"Island","fr":"Île","es":"Isla","it":"Isola","de":"Insel"},
    "surfing":  {"en":"Surfing","fr":"Surf","es":"Surf","it":"Surf","de":"Surfen"},
    "blog":     {"en":"Blog","fr":"Blog","es":"Blog","it":"Blog","de":"Blog"},
    "gallery":  {"en":"Gallery","fr":"Galerie","es":"Galería","it":"Galleria","de":"Galerie"},
    "booking":  {"en":"Book Now","fr":"Réserver","es":"Reservar","it":"Prenota","de":"Buchen"},
}

FLAG_SVG = {
    "en":'<svg viewBox="0 0 60 40"><rect width="60" height="40" fill="#012169"/><path d="M0,0 L60,40 M60,0 L0,40" stroke="#fff" stroke-width="8"/><path d="M0,0 L60,40 M60,0 L0,40" stroke="#C8102E" stroke-width="5"/><path d="M30,0 V40 M0,20 H60" stroke="#fff" stroke-width="12"/><path d="M30,0 V40 M0,20 H60" stroke="#C8102E" stroke-width="8"/></svg>',
    "fr":'<svg viewBox="0 0 60 40"><rect width="20" height="40" fill="#002395"/><rect x="20" width="20" height="40" fill="#fff"/><rect x="40" width="20" height="40" fill="#ED2939"/></svg>',
    "es":'<svg viewBox="0 0 60 40"><rect width="60" height="40" fill="#c60b1e"/><rect y="10" width="60" height="20" fill="#ffc400"/></svg>',
    "it":'<svg viewBox="0 0 60 40"><rect width="20" height="40" fill="#009246"/><rect x="20" width="20" height="40" fill="#fff"/><rect x="40" width="20" height="40" fill="#CE2B37"/></svg>',
    "de":'<svg viewBox="0 0 60 40"><rect width="60" height="13" fill="#000"/><rect y="13" width="60" height="14" fill="#DD0000"/><rect y="27" width="60" height="13" fill="#FFCE00"/></svg>',
}

def flag(lang, size=22):
    h = round(size*0.667)
    return f'<span style="width:{size}px;height:{h}px;display:inline-flex;border-radius:3px;overflow:hidden;flex-shrink:0;box-shadow:0 1px 3px rgba(0,0,0,0.22)">{FLAG_SVG[lang]}</span>'

CHEV = '<svg viewBox="0 0 16 16" fill="none" width="14" height="14"><path d="M4 6l4 4 4-4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
WA   = '<svg viewBox="0 0 24 24" fill="currentColor" width="18" height="18"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>'
MENU = '<svg viewBox="0 0 24 24" fill="none" width="22" height="22"><path d="M3 7h18M3 12h18M3 17h12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>'
LOGO = "https://static.wixstatic.com/media/c2467f_a31779010ce34c4c8c61cc5868d81f31~mv2.png"

def build_nav(current_page_key, lang, current_page_slug=""):
    """Build nav for a given page and language."""
    pfx = LANG_PFX[lang]
    items = ""
    for key, labels in NAV_LABELS.items():
        label = labels.get(lang, labels["en"])
        if key == "home":
            href = f"{pfx}/"
        else:
            slug = SLUG[lang].get(key, key)
            href = f"{pfx}/{slug}/"
        
        is_active = (key == current_page_key) or (key == "home" and not current_page_key)
        cls = "nav-link active" if is_active else "nav-link"
        if key == "booking": cls += " nav-cta"
        items += f'<a href="{href}" class="{cls}">{label}</a>\n'
    
    # Language dropdown — navigates to localized slug
    opts = ""
    for other_lang in LANGS:
        if other_lang == lang: continue
        other_pfx = LANG_PFX[other_lang]
        if current_page_key and current_page_key != "home":
            other_slug = SLUG[other_lang].get(current_page_key, current_page_key)
            href = f"{other_pfx}/{other_slug}/" if other_lang != "en" else f"/{other_slug}/"
        else:
            href = f"{other_pfx}/" if other_lang != "en" else "/"
        opts += f'<a class="lang-dd-item" href="{href}" hreflang="{LANG_LOCALE.get(other_lang, other_lang)}">{flag(other_lang,18)} {LANG_NAMES[other_lang]}</a>'
    
    lang_dd = f'<div class="lang-dd" id="lang-dd"><button class="lang-dd-btn" onclick="toggleLangDD(event)">{flag(lang,20)} {lang.upper()} <span style="display:inline-flex">{CHEV}</span></button><div class="lang-dd-menu" role="menu">{opts}</div></div>'
    
    return f'''<nav id="nav">
  <div class="nav-inner">
    <a href="{pfx}/" class="nav-logo"><img src="{LOGO}" alt="Ngor Surfcamp Teranga" width="130" height="44" loading="eager"></a>
    <div class="nav-links" id="nav-links">{items}</div>
    <div class="nav-right">{lang_dd}<a href="https://wa.me/221789257025" target="_blank" rel="noopener" class="nav-wa" aria-label="WhatsApp"><span style="display:inline-flex">{WA}</span><span class="nav-wa-label">WhatsApp</span></a><button class="nav-toggle" id="nav-toggle" aria-label="Menu" onclick="toggleMenu()"><span style="display:inline-flex;color:#fff">{MENU}</span></button></div>
  </div>
</nav>'''

# Patch navigation in ALL HTML files
NAV_RE = re.compile(r'<nav id="nav">.*?</nav>', re.DOTALL)

def detect_page_key(fpath):
    """Guess the page key from file path."""
    path = fpath.replace(DEMO, "")
    for page_key in STATIC_PAGES:
        all_slugs = [SLUG[l][page_key] for l in LANGS]
        for s in all_slugs:
            if f'/{s}/' in path or path.endswith(f'/{s}/index.html'):
                return page_key
    if '/blog/' in path and not path.endswith('/blog/index.html'):
        return 'blog-article'
    if path.endswith('/blog/index.html') or '/blog/index.html' in path:
        return 'blog'
    return 'home'

def detect_lang(fpath):
    path = fpath.replace(DEMO, "")
    for lang in ["fr","es","it","de"]:
        if path.startswith(f'/{lang}/'):
            return lang
    return "en"

total_patched = 0
for root, dirs, files in os.walk(DEMO):
    dirs[:] = [d for d in dirs if not d.startswith('.')]
    for fname in files:
        if not fname.endswith('.html'): continue
        fpath = os.path.join(root, fname)
        with open(fpath) as f: html = f.read()
        
        # Skip redirect pages
        if 'http-equiv="refresh"' in html: continue
        
        lang     = detect_lang(fpath)
        page_key = detect_page_key(fpath)
        pfx      = LANG_PFX[lang]
        
        # Determine current_page_slug for nav
        if page_key in STATIC_PAGES:
            ps = SLUG[lang].get(page_key, page_key)
        elif page_key == 'blog-article':
            ps = 'blog-article'
        else:
            ps = ''
        
        new_nav = build_nav(page_key if page_key in list(NAV_LABELS.keys()) else '', lang)
        new_html = NAV_RE.sub(new_nav, html, count=1)
        
        # Also update hreflang if this is a static page
        if page_key in STATIC_PAGES:
            new_hrl = get_hreflang(page_key)
            # Replace old hreflang block
            new_html = re.sub(
                r'<link rel="alternate" hreflang="x-default".*?(?=<link rel="(?!alternate)|\n<[^l])',
                new_hrl + '\n',
                new_html, flags=re.DOTALL, count=1
            )
        
        # Fix canonical for localized slug pages
        if page_key in STATIC_PAGES and lang != "en":
            new_slug = SLUG[lang][page_key]
            old_can = f'href="{SITE_URL}/{lang}/{page_key}/"'
            new_can = f'href="{SITE_URL}/{lang}/{new_slug}/"'
            new_html = new_html.replace(old_can, new_can)
        
        if new_html != html:
            with open(fpath,'w') as f: f.write(new_html)
            total_patched += 1

print(f"  Patched {total_patched} HTML files with new nav")

# ── Step 4: Fix block labels — use EN labels when rendering EN content ────────
print("\n=== Step 4: Fix block label language mismatch ===")
# In article pages: if the page lang is non-EN but content is EN (has blocks like "Key Takeaways")
# replace French labels with English ones
EN_LABELS = {
    "Conseil Pro":      "Pro Tip",
    "Points Clés":      "Key Takeaways",
    "Le Saviez-Vous ?": "Did You Know?",
    "De nos Coachs":    "From the Coaches",
    "Liste d'Actions":  "Action Checklist",
    "Fazit":            "Key Takeaways",
    "Consejo Pro":      "Pro Tip",
    "Punti Chiave":     "Key Takeaways",
    "Dai Coach":        "From the Coaches",
    "Lista d'Azioni":   "Action Checklist",
    "Profi-Tipp":       "Pro Tip",
    "Aktionsliste":     "Action Checklist",
    "Von den Coaches":  "From the Coaches",
    "Wusstest Du?":     "Did You Know?",
    "Consiglio Pro":    "Pro Tip",
    "Lo Sapevi?":       "Did You Know?",
}

fixed_labels = 0
# Find article pages that have non-EN page lang but EN content (contain "Key Takeaways" in different language but text is EN)
for root, dirs, files in os.walk(DEMO):
    dirs[:] = [d for d in dirs if not d.startswith('.')]
    for fname in files:
        if not fname.endswith('.html'): continue
        fpath = os.path.join(root, fname)
        if '/blog/' not in fpath: continue
        with open(fpath) as f: html = f.read()
        if 'http-equiv="refresh"' in html: continue
        
        lang = detect_lang(fpath)
        if lang == "en": continue  # EN pages are fine
        
        # Check if article content is in English (has English prose)
        # Simple heuristic: if body contains "surf camp" text in English AND non-EN labels
        has_en_content = any(kw in html for kw in [
            'the waves', 'you can', 'it is a', 'ngor island is', 'surfing in senegal'
        ])
        has_non_en_label = any(f'vb-label">{lbl}</span>' in html for lbl in EN_LABELS.keys())
        
        if has_en_content and has_non_en_label:
            new_html = html
            for non_en, en in EN_LABELS.items():
                new_html = new_html.replace(f'vb-label">{non_en}</span>', f'vb-label">{en}</span>')
            if new_html != html:
                with open(fpath,'w') as f: f.write(new_html)
                fixed_labels += 1

print(f"  Fixed labels in {fixed_labels} article pages")

# ── Step 5: Redesign buttons + "view more" ───────────────────────────────────
print("\n=== Step 5: Redesign buttons ===")
BUTTON_CSS = """
/* ══ BUTTON IMPROVEMENTS ════════════════════════════════════ */
.btn-view-more {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 14px 32px;
  background: linear-gradient(135deg, var(--navy), #1a4a7a);
  color: #fff;
  border-radius: var(--r-pill);
  font-family: var(--fh);
  font-weight: 700;
  font-size: 14px;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  border: 1.5px solid rgba(255,255,255,0.12);
  box-shadow: 0 4px 20px rgba(10,37,64,0.25), inset 0 1px 0 rgba(255,255,255,0.08);
  transition: transform 0.2s var(--spring), box-shadow 0.2s, background 0.2s;
  cursor: pointer;
  text-decoration: none;
}
.btn-view-more:hover {
  background: linear-gradient(135deg, #1a4a7a, #236aab);
  transform: translateY(-2px);
  box-shadow: 0 10px 32px rgba(10,37,64,0.35), inset 0 1px 0 rgba(255,255,255,0.12);
}
.btn-view-more svg { flex-shrink: 0; }
"""
with open(f"{DEMO}/assets/css/style.css",'a') as f: f.write('\n' + BUTTON_CSS)

# Update gallery CTA buttons with translations
VIEW_MORE = {
    "en": "View Photos & Surf Moments",
    "fr": "Voir les Photos & Sessions",
    "es": "Ver Fotos y Sesiones",
    "it": "Vedi Foto e Sessioni",
    "de": "Fotos & Sessions ansehen",
}
BOOK_NOW = {
    "en": "Book Your Stay",
    "fr": "Réserver",
    "es": "Reservar",
    "it": "Prenota",
    "de": "Jetzt buchen",
}

# Patch gallery pages
GALLERY_CTA_RE = re.compile(r'<div class="cta-band">.*?</div>', re.DOTALL)
for lang in LANGS:
    spfx = f"/{lang}" if lang!="en" else ""
    gal_slug = SLUG[lang].get("gallery","gallery")
    hp = f"{DEMO}{spfx}/{gal_slug}/index.html"
    if not os.path.exists(hp): continue
    with open(hp) as f: html = f.read()
    pfx = LANG_PFX[lang]
    book_slug = SLUG[lang]["booking"]
    
    # Build better gallery CTA
    new_cta = f'''<div class="cta-band">
    <div class="container">
      <h2>{"Your next chapter starts here." if lang=="en" else "Votre prochain chapitre commence ici." if lang=="fr" else "Tu próximo capítulo empieza aquí." if lang=="es" else "Il tuo prossimo capitolo inizia qui." if lang=="it" else "Dein nächstes Kapitel beginnt hier."}</h2>
      <div class="cta-btns">
        <a href="{pfx}/{book_slug}/" class="btn btn-fire btn-lg">{BOOK_NOW[lang]}</a>
        <a href="https://wa.me/221789257025" target="_blank" rel="noopener" class="btn-view-more">
          <svg viewBox="0 0 24 24" fill="currentColor" width="18" height="18"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
          WhatsApp
        </a>
      </div>
    </div>
  </div>'''
    
    new_html = GALLERY_CTA_RE.sub(new_cta, html, count=1)
    if new_html != html:
        with open(hp,'w') as f: f.write(new_html)
        print(f"  ✅ Gallery CTA updated: {lang}")

# ── Step 6: Report all slug URLs ─────────────────────────────────────────────
print("\n=== Slug URL Summary ===")
for page_key in STATIC_PAGES:
    print(f"\n  {page_key}:")
    for lang in LANGS:
        slug = SLUG[lang][page_key]
        pfx  = LANG_PFX[lang]
        url  = f"/{slug}/" if lang=="en" else f"{pfx}/{slug}/"
        exists = os.path.exists(f"{DEMO}{url}index.html")
        print(f"    {lang}: {url} {'✅' if exists else '❌'}")

print("\n✅ All fixes complete!")
