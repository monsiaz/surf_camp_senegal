"""
Build the complete Cloudflare Pages demo site.
Reads all our content JSON files + scrapes live site structure.
Generates: index.html, all pages, blog listing, 30 article pages.
All with JS-based multilingual switching + country selector.
"""
import json, os, re, requests

CONTENT   = "/Users/simonazoulay/SurfCampSenegal/content"
ARTICLES  = f"{CONTENT}/articles"
PAGES_DIR = f"{CONTENT}/pages"
DEMO_DIR  = "/Users/simonazoulay/SurfCampSenegal/cloudflare-demo"
LIVE_BASE = "https://www.surfcampsenegal.com"

def load(path):
    if os.path.exists(path):
        try:
            with open(path) as f: return json.load(f)
        except: return None
    return None

def load_page(lang, name):
    slug = name.lower().replace(" ","_").replace("/","")
    for suffix in [slug, slug.replace("-","_"), slug.replace("_","-")]:
        p = load(f"{PAGES_DIR}/{lang}_{suffix}.json")
        if p: return p
    return {}

# ── Image map ─────────────────────────────────────────────────────────────────
LOGO     = "https://static.wixstatic.com/media/c2467f_a31779010ce34c4c8c61cc5868d81f31~mv2.png"
LOGO2    = "https://static.wixstatic.com/media/c2467f_149b1700ca514fc994661c4179580bd3~mv2.png"

IMGS = {
    "hero_home":     "https://static.wixstatic.com/media/df99f9_da0cf7c72b1a4606bcfa1f7c8e089dc4f000.jpg",
    "hero_house":    "https://static.wixstatic.com/media/df99f9_2ec6248367cd4e21a5e6c26c2b0a1c35~mv2.jpg",
    "hero_island":   "https://static.wixstatic.com/media/df99f9_56b9af6efe2841eea44109b3b08b7da1~mv2.jpg",
    "hero_surf":     "https://static.wixstatic.com/media/11062b_89a070321f814742a620b190592d51ad~mv2.jpg",
    "hero_book":     "https://static.wixstatic.com/media/df99f9_f1a26a92f0044c95bab016044d325706~mv2.png",
    "hero_gallery":  "https://static.wixstatic.com/media/df99f9_4e96b6efc2fc4520a145e43c8ac7d71f~mv2.png",
    "hero_blog":     "https://static.wixstatic.com/media/df99f9_961b0768e713457f93025f4ce6fb1419~mv2.jpg",
    "island1":       "https://static.wixstatic.com/media/b28af82dbec544138f16e2bc5a85f2cb.jpg",
    "island2":       "https://static.wixstatic.com/media/df99f9_5e1d04de46d74d1ca722aeeb6a640dad~mv2.jpg",
    "ngor_right":    "https://static.wixstatic.com/media/11062b_7f89d2db0ace4027ac4a00928a6aca08~mv2.jpg",
    "house1":        "https://static.wixstatic.com/media/df99f9_eba4c24ec6a746b58d60a975b8d20946~mv2.jpg",
    "house2":        "https://static.wixstatic.com/media/df99f9_81e322c4e48d4bcbb444c6535daed131~mv2.jpg",
    "house3":        "https://static.wixstatic.com/media/df99f9_d8e77cf4807249f6953119f18be64166~mv2.jpg",
    "surf1":         "https://static.wixstatic.com/media/df99f9_961b0768e713457f93025f4ce6fb1419~mv2.jpg",
    "surf2":         "https://static.wixstatic.com/media/df99f9_dd89cc4d86d4402189d7e9516ce672a3~mv2.jpg",
    "surf3":         "https://static.wixstatic.com/media/df99f9_0d4a03baee4f46b68bc1aa085ed28e35~mv2.jpg",
    "surf4":         "https://static.wixstatic.com/media/df99f9_796b6115065145eabddfe3ae32b8f4d5~mv2.jpg",
    "gallery1":      "https://static.wixstatic.com/media/df99f9_16fcc19c812d49a9a05e361aacdc9cea~mv2.jpg",
    "gallery2":      "https://static.wixstatic.com/media/df99f9_25cc88706ffb42debadac4787bab4f02~mv2.jpg",
    "gallery3":      "https://static.wixstatic.com/media/df99f9_6a9de50280094c06b4bb439b5d0a7ca7~mv2.jpg",
    "gallery4":      "https://static.wixstatic.com/media/df99f9_bb61f8a278004fccb5f55351a772472c~mv2.jpg",
    "gallery5":      "https://static.wixstatic.com/media/df99f9_6fae936c12864930a0e7413cdccf6fd0~mv2.jpeg",
    "gallery6":      "https://static.wixstatic.com/media/df99f9_27471c09c19d473896e650316f2a0622~mv2.jpg",
    "gallery7":      "https://static.wixstatic.com/media/df99f9_42ff8407b442474fa5d54253fac98133~mv2.jpg",
    "gallery8":      "https://static.wixstatic.com/media/df99f9_64a5d28bf1d94191ad2fa45af7de6782~mv2.jpg",
    "review":        "https://static.wixstatic.com/media/11062b_772a661c20f742c7baca38ad28c5f7fc~mv2.jpeg",
    "food":          "https://static.wixstatic.com/media/df99f9_753890483d8e4cca8e2051a13f9c558e~mv2.jpg",
    "pool":          "https://static.wixstatic.com/media/df99f9_a18d512828d9487e9a4987b9903960e0~mv2.jpg",
    "sunset":        "https://static.wixstatic.com/media/df99f9_d6e404dd3cf74396b6ea874cb7021a27~mv2.jpg",
    "art":           "https://static.wixstatic.com/media/df99f9_d81668a18a9d49d1b5ebb0ea3a0abbc7~mv2.jpg",
}

# ── Load all articles ─────────────────────────────────────────────────────────
strategy = load(f"{CONTENT}/blog_strategy.json")
all_articles_en = []
for fname in sorted(os.listdir(f"{ARTICLES}/en")):
    if fname.endswith(".json"):
        a = load(f"{ARTICLES}/en/{fname}")
        if a and a.get("slug"): all_articles_en.append(a)

print(f"Loaded {len(all_articles_en)} EN articles")

# ── Load page content for all languages ──────────────────────────────────────
LANGS   = ["en", "fr", "es", "it", "de"]
LANG_NAMES  = {"en":"English","fr":"Français","es":"Español","it":"Italiano","de":"Deutsch"}
LANG_FLAGS  = {"en":"🇬🇧","fr":"🇫🇷","es":"🇪🇸","it":"🇮🇹","de":"🇩🇪"}

# Load all page translations
page_content = {}
for lang in LANGS:
    page_content[lang] = {}
    for name in ["homepage", "surf_house", "island", "surfing", "book_online", "gallery", "faq"]:
        d = load(f"{PAGES_DIR}/{lang}_{name}.json")
        if d:
            slug_key = {"homepage":"/","surf_house":"/ngor-surf-house","island":"/ngor-island",
                        "surfing":"/surfing","book_online":"/book-surf-trip",
                        "gallery":"/gallery","faq":"/faq"}[name]
            page_content[lang][slug_key] = d

# ── HTML templates ────────────────────────────────────────────────────────────
def head(title, desc, canon="", lang="en"):
    hreflang_pages = [
        ('/', '/'), ('/surf-house.html', '/ngor-surf-house'),
        ('/island.html', '/ngor-island'), ('/surfing.html', '/surfing'),
        ('/booking.html', '/book-surf-trip'), ('/gallery.html', '/gallery'),
        ('/faq.html', '/faq')
    ]
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{title}</title>
  <meta name="description" content="{desc}"/>
  <meta property="og:title" content="{title}"/>
  <meta property="og:description" content="{desc}"/>
  <meta property="og:image" content="{IMGS['hero_home']}"/>
  <meta property="og:type" content="website"/>
  {'<link rel="canonical" href="' + canon + '"/>' if canon else ''}
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
  <link href="https://fonts.googleapis.com/css2?family=Raleway:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet"/>
  <link rel="stylesheet" href="/assets/css/style.css"/>
  <script>
    // Language persistence
    const LANG = localStorage.getItem('ngor_lang') || 'en';
    document.documentElement.lang = LANG;
  </script>
</head>
<body>"""

def nav(active="home"):
    nav_items = [
        ("home","Home","Accueil","Inicio","Home","Startseite","/"),
        ("surf-house","Surf House","Surf House","Surf House","Surf House","Surf House","/surf-house.html"),
        ("island","Island","Île","Isla","Isola","Insel","/island.html"),
        ("surfing","Surfing","Surf","Surf","Surf","Surfen","/surfing.html"),
        ("blog","Blog","Blog","Blog","Blog","Blog","/blog/"),
        ("gallery","Gallery","Galerie","Galería","Galleria","Galerie","/gallery.html"),
        ("book","Book Now","Réserver","Reservar","Prenota","Jetzt buchen","/booking.html"),
    ]
    items_html = ""
    for key, en, fr, es, it, de, href in nav_items:
        cls = "active" if active == key else ""
        book_cls = " nav-cta" if key == "book" else ""
        items_html += f'''<a href="{href}" class="nav-link {cls}{book_cls}">
          <span data-lang="en">{en}</span>
          <span data-lang="fr" style="display:none">{fr}</span>
          <span data-lang="es" style="display:none">{es}</span>
          <span data-lang="it" style="display:none">{it}</span>
          <span data-lang="de" style="display:none">{de}</span>
        </a>'''

    lang_opts = "".join([f'<option value="{l}">{LANG_FLAGS[l]} {LANG_NAMES[l]}</option>' for l in LANGS])

    return f"""<header id="site-header">
  <nav class="nav-container">
    <a href="/" class="nav-logo">
      <img src="{LOGO}" alt="Ngor Surfcamp Teranga" height="50"/>
    </a>
    <div class="nav-links" id="nav-links">
      {items_html}
    </div>
    <div class="nav-right">
      <div class="lang-selector">
        <select id="lang-select" onchange="setLang(this.value)">
          {lang_opts}
        </select>
      </div>
      <a href="https://wa.me/221789257025" target="_blank" class="whatsapp-btn">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
          <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
        </svg>
        <span data-lang="en">WhatsApp</span>
        <span data-lang="fr" style="display:none">WhatsApp</span>
        <span data-lang="es" style="display:none">WhatsApp</span>
        <span data-lang="it" style="display:none">WhatsApp</span>
        <span data-lang="de" style="display:none">WhatsApp</span>
      </a>
      <button class="nav-toggle" onclick="toggleMenu()" aria-label="Menu">
        <span></span><span></span><span></span>
      </button>
    </div>
  </nav>
</header>"""

def hero(img_url, title_en, title_fr, title_es, title_it, title_de,
         sub_en="", sub_fr="", sub_es="", sub_it="", sub_de="", cta=True):
    subs = {"en":sub_en,"fr":sub_fr,"es":sub_es,"it":sub_it,"de":sub_de}
    sub_parts = []
    for l in LANGS:
        if subs[l]:
            style = '' if l == 'en' else ' style="display:none"'
            sub_parts.append(f'<p class="hero-subtitle" data-lang="{l}"{style}>{subs[l]}</p>')
    sub_html = "".join(sub_parts)
    cta_html = """<div class="hero-cta">
      <a href="/booking.html" class="btn btn-primary">
        <span data-lang="en">Book Your Stay</span>
        <span data-lang="fr" style="display:none">Réserver</span>
        <span data-lang="es" style="display:none">Reservar</span>
        <span data-lang="it" style="display:none">Prenota</span>
        <span data-lang="de" style="display:none">Jetzt buchen</span>
      </a>
      <a href="https://wa.me/221789257025" target="_blank" class="btn btn-outline">
        <span data-lang="en">Contact via WhatsApp</span>
        <span data-lang="fr" style="display:none">Contacter sur WhatsApp</span>
        <span data-lang="es" style="display:none">Contactar por WhatsApp</span>
        <span data-lang="it" style="display:none">Contatta su WhatsApp</span>
        <span data-lang="de" style="display:none">WhatsApp Kontakt</span>
      </a>
    </div>""" if cta else ""

    return f"""<section class="hero" style="background-image:url('{img_url}')">
  <div class="hero-overlay"></div>
  <div class="hero-content">
    <h1 class="hero-title">
      <span data-lang="en">{title_en}</span>
      <span data-lang="fr" style="display:none">{title_fr}</span>
      <span data-lang="es" style="display:none">{title_es}</span>
      <span data-lang="it" style="display:none">{title_it}</span>
      <span data-lang="de" style="display:none">{title_de}</span>
    </h1>
    {sub_html}
    {cta_html}
  </div>
</section>"""

def footer():
    return """<footer class="site-footer">
  <div class="footer-content">
    <div class="footer-logo">
      <img src="{logo}" alt="Ngor Surfcamp Teranga" height="60"/>
    </div>
    <div class="footer-links">
      <a href="/" data-lang-key="home">Home</a>
      <a href="/surf-house.html">Surf House</a>
      <a href="/island.html">Island</a>
      <a href="/surfing.html">Surfing</a>
      <a href="/blog/">Blog</a>
      <a href="/gallery.html">Gallery</a>
      <a href="/booking.html">Book Now</a>
      <a href="/faq.html">FAQ</a>
    </div>
    <div class="footer-social">
      <a href="https://wa.me/221789257025" target="_blank" class="social-link" title="WhatsApp">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
      </a>
      <a href="https://www.instagram.com/ngorsurfcampteranga" target="_blank" class="social-link" title="Instagram">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>
      </a>
      <a href="https://www.tiktok.com/@ngorsurfcampteranga" target="_blank" class="social-link" title="TikTok">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M19.59 6.69a4.83 4.83 0 01-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 01-2.88 2.5 2.89 2.89 0 01-2.89-2.89 2.89 2.89 0 012.89-2.89c.28 0 .54.04.79.1V9.01a6.28 6.28 0 00-.79-.05 6.34 6.34 0 00-6.34 6.34 6.34 6.34 0 006.34 6.34 6.34 6.34 0 006.33-6.34V8.69a8.22 8.22 0 004.84 1.56V6.79a4.85 4.85 0 01-1.07-.1z"/></svg>
      </a>
    </div>
    <div class="footer-info">
      <p>Ngor Island, 800m west of Cap-Vert peninsula, Dakar, Senegal</p>
      <p>+221 78 925 70 25 · info@surfcampsenegal.com</p>
      <p>© 2025 Ngor Surfcamp Teranga. All rights reserved.</p>
    </div>
  </div>
</footer>""".replace("{logo}", LOGO)

I18N_JS = """
<script>
const LANG_STORAGE_KEY = 'ngor_lang';
const LANGS = ['en','fr','es','it','de'];

function getLang() {
  return localStorage.getItem(LANG_STORAGE_KEY) || 'en';
}

function setLang(lang) {
  localStorage.setItem(LANG_STORAGE_KEY, lang);
  applyLang(lang);
  // Update select
  const sel = document.getElementById('lang-select');
  if (sel) sel.value = lang;
}

function applyLang(lang) {
  document.documentElement.lang = lang;
  // Hide all lang spans, show current
  document.querySelectorAll('[data-lang]').forEach(el => {
    el.style.display = el.getAttribute('data-lang') === lang ? '' : 'none';
  });
}

// Init on load
document.addEventListener('DOMContentLoaded', () => {
  const lang = getLang();
  applyLang(lang);
  const sel = document.getElementById('lang-select');
  if (sel) sel.value = lang;
  
  // Get lang from URL param
  const urlLang = new URLSearchParams(window.location.search).get('lang');
  if (urlLang && LANGS.includes(urlLang)) {
    setLang(urlLang);
  }
});

function toggleMenu() {
  document.getElementById('nav-links').classList.toggle('open');
}

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    const target = document.querySelector(a.getAttribute('href'));
    if (target) { e.preventDefault(); target.scrollIntoView({behavior:'smooth'}); }
  });
});
</script>
"""

# ════════════════════════════════════════════════════════════════════════════════
# CSS
# ════════════════════════════════════════════════════════════════════════════════
CSS = """
:root {
  --navy: #0a2540;
  --blue: #1565c0;
  --ocean: #29b6f6;
  --sand: #f5e6c8;
  --sunset: #ff6b35;
  --white: #ffffff;
  --text: #1a1a2e;
  --muted: #6b7280;
  --light-bg: #f8fafc;
  --border: #e2e8f0;
  --radius: 12px;
  --shadow: 0 4px 24px rgba(10,37,64,0.10);
  --transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html { scroll-behavior: smooth; }

body {
  font-family: 'Inter', -apple-system, sans-serif;
  color: var(--text);
  line-height: 1.7;
  background: var(--white);
}

h1,h2,h3,h4,h5,h6 {
  font-family: 'Raleway', sans-serif;
  font-weight: 700;
  line-height: 1.2;
  letter-spacing: -0.02em;
}

a { color: inherit; text-decoration: none; }
img { max-width: 100%; height: auto; display: block; }

/* ── Header / Nav ── */
#site-header {
  position: fixed; top: 0; left: 0; right: 0; z-index: 100;
  background: rgba(10,37,64,0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255,255,255,0.1);
}
.nav-container {
  max-width: 1280px; margin: 0 auto;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 24px; height: 70px;
}
.nav-logo img { height: 46px; width: auto; }
.nav-links {
  display: flex; align-items: center; gap: 4px;
}
.nav-link {
  color: rgba(255,255,255,0.85);
  padding: 8px 14px;
  border-radius: 8px;
  font-size: 14px; font-weight: 500;
  transition: var(--transition);
  white-space: nowrap;
}
.nav-link:hover, .nav-link.active { color: white; background: rgba(255,255,255,0.1); }
.nav-link.nav-cta {
  background: var(--sunset); color: white;
  padding: 8px 20px; font-weight: 600;
}
.nav-link.nav-cta:hover { background: #e05a28; transform: translateY(-1px); }
.nav-right { display: flex; align-items: center; gap: 12px; }
.lang-selector select {
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.2);
  color: white; padding: 6px 10px;
  border-radius: 8px; font-size: 13px; cursor: pointer;
  outline: none;
}
.lang-selector select option { background: var(--navy); color: white; }
.whatsapp-btn {
  display: flex; align-items: center; gap: 8px;
  background: #25D366; color: white;
  padding: 8px 16px; border-radius: 50px;
  font-size: 13px; font-weight: 600;
  transition: var(--transition);
}
.whatsapp-btn:hover { background: #1da851; transform: translateY(-1px); }
.nav-toggle { display: none; flex-direction: column; gap: 5px; background: none; border: none; cursor: pointer; padding: 4px; }
.nav-toggle span { width: 24px; height: 2px; background: white; border-radius: 2px; transition: var(--transition); }

/* ── Hero ── */
.hero {
  position: relative;
  min-height: 100vh;
  display: flex; align-items: center; justify-content: center;
  background-size: cover; background-position: center; background-attachment: fixed;
  text-align: center; padding: 100px 24px 60px;
}
.hero-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(135deg, rgba(10,37,64,0.7) 0%, rgba(0,0,0,0.4) 100%);
}
.hero-content {
  position: relative; z-index: 2;
  max-width: 800px;
}
.hero-title {
  font-size: clamp(36px, 6vw, 72px);
  color: white; margin-bottom: 16px;
  text-shadow: 0 2px 20px rgba(0,0,0,0.3);
  font-weight: 800;
}
.hero-subtitle {
  font-size: clamp(16px, 2.5vw, 22px);
  color: rgba(255,255,255,0.9);
  margin-bottom: 32px;
  font-weight: 300;
}
.hero-cta { display: flex; gap: 16px; justify-content: center; flex-wrap: wrap; margin-top: 32px; }

/* ── Buttons ── */
.btn {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 14px 32px; border-radius: 50px;
  font-family: 'Raleway', sans-serif;
  font-weight: 700; font-size: 14px; letter-spacing: 0.05em;
  text-transform: uppercase; transition: var(--transition);
  cursor: pointer; border: none;
}
.btn-primary { background: var(--sunset); color: white; }
.btn-primary:hover { background: #e05a28; transform: translateY(-2px); box-shadow: 0 8px 24px rgba(255,107,53,0.4); }
.btn-secondary { background: var(--navy); color: white; }
.btn-secondary:hover { background: #0d3060; transform: translateY(-2px); }
.btn-outline { background: transparent; color: white; border: 2px solid rgba(255,255,255,0.7); }
.btn-outline:hover { background: rgba(255,255,255,0.15); border-color: white; }
.btn-ocean { background: var(--blue); color: white; }
.btn-ocean:hover { background: #0d47a1; transform: translateY(-2px); }

/* ── Sections ── */
.section { padding: 80px 24px; }
.section-sm { padding: 60px 24px; }
.section-dark { background: var(--navy); color: white; }
.section-light { background: var(--light-bg); }
.section-sand { background: var(--sand); }

.container { max-width: 1200px; margin: 0 auto; }
.container-sm { max-width: 800px; margin: 0 auto; }

.section-tag {
  font-size: 12px; font-weight: 700; letter-spacing: 0.15em;
  text-transform: uppercase; color: var(--ocean);
  margin-bottom: 12px; display: block;
}
.section-title {
  font-size: clamp(28px, 4vw, 48px);
  margin-bottom: 16px;
}
.section-subtitle {
  font-size: 18px; color: var(--muted); max-width: 600px;
  margin-bottom: 48px; line-height: 1.7;
}
.section-dark .section-subtitle { color: rgba(255,255,255,0.7); }
.section-dark .section-tag { color: var(--ocean); }

/* ── Grid ── */
.grid-2 { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 32px; }
.grid-3 { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 24px; }
.grid-4 { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }

/* ── Cards ── */
.card {
  background: white; border-radius: var(--radius);
  overflow: hidden; box-shadow: var(--shadow);
  transition: var(--transition);
}
.card:hover { transform: translateY(-4px); box-shadow: 0 12px 40px rgba(10,37,64,0.15); }
.card-img { aspect-ratio: 16/10; object-fit: cover; width: 100%; }
.card-body { padding: 24px; }
.card-tag { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: var(--ocean); margin-bottom: 8px; }
.card-title { font-size: 20px; margin-bottom: 12px; font-weight: 700; }
.card-text { font-size: 15px; color: var(--muted); margin-bottom: 16px; line-height: 1.6; }

/* ── Features ── */
.feature-item { display: flex; gap: 16px; align-items: flex-start; margin-bottom: 32px; }
.feature-icon {
  width: 48px; height: 48px; flex-shrink: 0;
  background: linear-gradient(135deg, var(--blue), var(--ocean));
  border-radius: 12px; display: flex; align-items: center; justify-content: center;
  font-size: 24px;
}
.feature-title { font-size: 18px; font-weight: 700; margin-bottom: 6px; }
.feature-text { font-size: 15px; color: var(--muted); line-height: 1.6; }

/* ── Gallery ── */
.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}
.gallery-item {
  aspect-ratio: 4/3; overflow: hidden; border-radius: 8px; cursor: pointer;
}
.gallery-item img {
  width: 100%; height: 100%; object-fit: cover;
  transition: transform 0.4s ease;
}
.gallery-item:hover img { transform: scale(1.05); }

/* ── Testimonial ── */
.testimonial {
  background: white; border-radius: var(--radius); padding: 32px;
  box-shadow: var(--shadow); border-left: 4px solid var(--ocean);
}
.testimonial-text { font-size: 18px; font-style: italic; color: var(--text); margin-bottom: 16px; line-height: 1.7; }
.testimonial-author { font-weight: 700; color: var(--navy); }

/* ── Booking Form ── */
.booking-form {
  background: white; border-radius: var(--radius);
  padding: 40px; box-shadow: var(--shadow);
}
.form-group { margin-bottom: 20px; }
.form-label { display: block; font-weight: 600; margin-bottom: 8px; font-size: 14px; }
.form-input, .form-select, .form-textarea {
  width: 100%; padding: 12px 16px;
  border: 2px solid var(--border); border-radius: 8px;
  font-family: inherit; font-size: 15px;
  transition: var(--transition); outline: none;
}
.form-input:focus, .form-select:focus, .form-textarea:focus {
  border-color: var(--ocean); box-shadow: 0 0 0 3px rgba(41,182,246,0.1);
}
.form-textarea { resize: vertical; min-height: 100px; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }

/* ── FAQ ── */
.faq-item {
  border: 1px solid var(--border); border-radius: 8px;
  margin-bottom: 12px; overflow: hidden;
}
.faq-question {
  padding: 20px 24px; cursor: pointer; display: flex;
  justify-content: space-between; align-items: center;
  font-weight: 600; font-size: 16px;
  background: white; transition: var(--transition);
}
.faq-question:hover { background: var(--light-bg); }
.faq-answer { padding: 0 24px 20px; color: var(--muted); line-height: 1.7; display: none; }
.faq-item.open .faq-answer { display: block; }
.faq-item.open .faq-arrow { transform: rotate(180deg); }
.faq-arrow { transition: transform 0.2s; }

/* ── Blog ── */
.blog-meta { font-size: 13px; color: var(--muted); margin-bottom: 8px; }
.blog-category {
  display: inline-block; padding: 4px 12px; border-radius: 20px;
  background: rgba(41,182,246,0.1); color: var(--blue);
  font-size: 12px; font-weight: 600; margin-bottom: 12px;
}
.article-content { max-width: 760px; margin: 0 auto; }
.article-content h1 { font-size: clamp(28px, 4vw, 42px); margin-bottom: 24px; }
.article-content h2 { font-size: 26px; margin: 40px 0 16px; color: var(--navy); }
.article-content h3 { font-size: 20px; margin: 28px 0 12px; }
.article-content p { margin-bottom: 20px; font-size: 17px; line-height: 1.8; color: #374151; }
.article-content ul, .article-content ol { margin: 16px 0 24px 24px; }
.article-content li { margin-bottom: 8px; font-size: 17px; line-height: 1.7; color: #374151; }
.article-content strong { color: var(--navy); }

/* ── Two-col split ── */
.split-section { display: grid; grid-template-columns: 1fr 1fr; gap: 80px; align-items: center; }
.split-section.reverse { direction: rtl; }
.split-section.reverse > * { direction: ltr; }
.split-img { border-radius: 16px; overflow: hidden; box-shadow: var(--shadow); }
.split-img img { width: 100%; height: 400px; object-fit: cover; }

/* ── Stat bar ── */
.stats-bar { display: flex; justify-content: center; flex-wrap: wrap; gap: 60px; padding: 48px 24px; background: var(--navy); }
.stat-item { text-align: center; color: white; }
.stat-number { font-size: 48px; font-weight: 800; color: var(--ocean); display: block; font-family: 'Raleway', sans-serif; }
.stat-label { font-size: 14px; opacity: 0.8; text-transform: uppercase; letter-spacing: 0.1em; }

/* ── Banner CTA ── */
.cta-banner {
  background: linear-gradient(135deg, var(--navy), var(--blue));
  padding: 80px 24px; text-align: center; color: white;
}
.cta-banner h2 { font-size: clamp(28px, 4vw, 48px); margin-bottom: 16px; }
.cta-banner p { font-size: 18px; opacity: 0.85; margin-bottom: 40px; max-width: 560px; margin-left: auto; margin-right: auto; }

/* ── Footer ── */
.site-footer {
  background: var(--navy); color: white; padding: 60px 24px 32px;
  border-top: 1px solid rgba(255,255,255,0.1);
}
.footer-content { max-width: 1200px; margin: 0 auto; }
.footer-logo { margin-bottom: 32px; }
.footer-logo img { height: 50px; }
.footer-links { display: flex; flex-wrap: wrap; gap: 8px 24px; margin-bottom: 32px; }
.footer-links a { color: rgba(255,255,255,0.75); font-size: 15px; transition: var(--transition); }
.footer-links a:hover { color: white; }
.footer-social { display: flex; gap: 16px; margin-bottom: 32px; }
.social-link {
  width: 44px; height: 44px; border-radius: 50%;
  background: rgba(255,255,255,0.1); display: flex; align-items: center; justify-content: center;
  transition: var(--transition);
}
.social-link:hover { background: var(--ocean); }
.footer-info { font-size: 14px; color: rgba(255,255,255,0.6); line-height: 1.8; }

/* ── Page header (non-hero pages) ── */
.page-header {
  background: var(--navy); color: white;
  padding: 140px 24px 80px; text-align: center;
  background-size: cover; background-position: center;
  position: relative;
}
.page-header::after {
  content: ''; position: absolute; inset: 0;
  background: rgba(10,37,64,0.7);
}
.page-header > * { position: relative; z-index: 1; }
.page-header h1 { font-size: clamp(36px, 5vw, 60px); margin-bottom: 12px; }
.page-header p { font-size: 18px; opacity: 0.85; max-width: 600px; margin: 0 auto; }

/* ── Language tag labels ── */
.lang-tag {
  display: inline-block; padding: 2px 8px; border-radius: 4px;
  font-size: 11px; font-weight: 700; margin-right: 6px;
  background: rgba(41,182,246,0.15); color: var(--blue);
}

/* ── Responsive ── */
@media (max-width: 900px) {
  .split-section { grid-template-columns: 1fr; gap: 40px; }
  .split-section.reverse { direction: ltr; }
  .form-grid { grid-template-columns: 1fr; }
}

@media (max-width: 768px) {
  .nav-links { 
    display: none; position: fixed; top: 70px; left: 0; right: 0;
    background: var(--navy); flex-direction: column; padding: 20px;
    border-top: 1px solid rgba(255,255,255,0.1);
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
  }
  .nav-links.open { display: flex; }
  .nav-toggle { display: flex; }
  .whatsapp-btn span { display: none; }
  .hero { background-attachment: scroll; }
  .stats-bar { gap: 32px; }
  .booking-form { padding: 24px; }
}

@media (max-width: 480px) {
  .hero-cta { flex-direction: column; align-items: center; }
  .btn { width: 100%; justify-content: center; }
  .grid-3, .grid-4 { grid-template-columns: 1fr; }
}

/* ── Scroll reveal (simple) ── */
.reveal { opacity: 0; transform: translateY(30px); transition: opacity 0.6s ease, transform 0.6s ease; }
.reveal.visible { opacity: 1; transform: translateY(0); }
"""

# Write CSS
with open(f"{DEMO_DIR}/assets/css/style.css", "w") as f:
    f.write(CSS)
print("✅ CSS written")

# ════════════════════════════════════════════════════════════════════════════════
# PAGE BUILDERS
# ════════════════════════════════════════════════════════════════════════════════

def close_page():
    return f"""
<script>
// Scroll reveal
const observer = new IntersectionObserver(entries => {{
  entries.forEach(e => {{ if(e.isIntersecting) e.target.classList.add('visible'); }});
}}, {{threshold: 0.1}});
document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

// FAQ accordion
document.querySelectorAll('.faq-question').forEach(q => {{
  q.addEventListener('click', () => {{
    const item = q.closest('.faq-item');
    item.classList.toggle('open');
  }});
}});
</script>
{I18N_JS}
</body>
</html>"""

def multilang(texts_dict):
    """Generate multilang spans from dict {lang: text}."""
    parts = []
    for l in LANGS:
        text = texts_dict.get(l, texts_dict.get("en", ""))
        style = '' if l == 'en' else ' style="display:none"'
        parts.append(f'<span data-lang="{l}"{style}>{text}</span>')
    return "".join(parts)

# ════════════════════════════════════════════════════════════════════════════════
# BUILD HOMEPAGE
# ════════════════════════════════════════════════════════════════════════════════
print("Building homepage...")
hp = {lang: page_content.get(lang, {}).get("/", {}) for lang in LANGS}

# Pre-compute complex multilang strings to avoid backslash-in-fstring issues
_testimonial = multilang({
    "en": "I had an amazing experience at Ngor Surfcamp Teranga. The coaching was top-notch, and I felt my surfing skills improve significantly during my stay.",
    "fr": "Une exp\u00e9rience incroyable au Ngor Surfcamp Teranga. Le coaching \u00e9tait excellent et mes comp\u00e9tences en surf ont vraiment progress\u00e9.",
    "es": "Una experiencia incre\u00edble en Ngor Surfcamp Teranga. El coaching fue excelente y mis habilidades de surf mejoraron significativamente.",
    "it": "Un'esperienza incredibile al Ngor Surfcamp Teranga. Il coaching era eccellente e le mie abilit\u00e0 nel surf sono migliorate in modo significativo.",
    "de": "Eine unglaubliche Erfahrung im Ngor Surfcamp Teranga. Das Coaching war erstklassig und meine Surfkenntnisse haben sich erheblich verbessert.",
})

homepage_html = head(
    hp["en"].get("title_tag", "Surf Camp Senegal | Ngor Surfcamp Teranga"),
    hp["en"].get("meta_description", "Premium surf camp on Ngor Island, Dakar, Senegal.")
) + nav("home") + hero(
    IMGS["hero_home"],
    hp["en"].get("h1", "Ngor Surfcamp Teranga"),
    hp["fr"].get("h1", "Ngor Surfcamp Teranga"),
    hp["es"].get("h1", "Ngor Surfcamp Teranga"),
    hp["it"].get("h1", "Ngor Surfcamp Teranga"),
    hp["de"].get("h1", "Ngor Surfcamp Teranga"),
    hp["en"].get("hero_subtitle", "Premium Surfcamp in Senegal"),
    hp["fr"].get("hero_subtitle", "Surf Camp Premium au Sénégal"),
    hp["es"].get("hero_subtitle", "Surf Camp Premium en Senegal"),
    hp["it"].get("hero_subtitle", "Surf Camp Premium in Senegal"),
    hp["de"].get("hero_subtitle", "Premium Surfcamp im Senegal"),
) + f"""

<!-- Stats bar -->
<div class="stats-bar reveal">
  <div class="stat-item">
    <span class="stat-number">3</span>
    <span class="stat-label">{multilang({"en":"Waves","fr":"Vagues","es":"Olas","it":"Onde","de":"Wellen"})}</span>
  </div>
  <div class="stat-item">
    <span class="stat-number">All</span>
    <span class="stat-label">{multilang({"en":"Levels","fr":"Niveaux","es":"Niveles","it":"Livelli","de":"Levels"})}</span>
  </div>
  <div class="stat-item">
    <span class="stat-number">5★</span>
    <span class="stat-label">{multilang({"en":"Coaching","fr":"Coaching","es":"Coaching","it":"Coaching","de":"Coaching"})}</span>
  </div>
  <div class="stat-item">
    <span class="stat-number">1964</span>
    <span class="stat-label">{multilang({"en":"Endless Summer","fr":"Endless Summer","es":"Endless Summer","it":"Endless Summer","de":"Endless Summer"})}</span>
  </div>
</div>

<!-- About section -->
<section class="section reveal">
  <div class="container">
    <div class="split-section">
      <div>
        <span class="section-tag">{multilang({"en":"Premium Surf Camp","fr":"Surf Camp Premium","es":"Surf Camp Premium","it":"Surf Camp Premium","de":"Premium Surfcamp"})}</span>
        <h2 class="section-title">{multilang({l: hp[l].get("sections",[{}])[0].get("h2","Serious about improving your surfing?") if hp[l].get("sections") else "Serious about improving your surfing?" for l in LANGS})}</h2>
        <p style="font-size:17px; color:var(--muted); margin-bottom:24px; line-height:1.8">
          {multilang({l: hp[l].get("intro","At Ngor Surfcamp Teranga, we offer professional surf coaching tailored to your level.") for l in LANGS})}
        </p>
        <div style="display:flex;gap:12px;flex-wrap:wrap">
          <a href="/surf-house.html" class="btn btn-secondary">{multilang({"en":"Our Surf House","fr":"Notre Surf House","es":"Nuestra Surf House","it":"La Surf House","de":"Unser Surf House"})}</a>
          <a href="/surfing.html" class="btn btn-ocean">{multilang({"en":"Surfing & Coaching","fr":"Surf & Coaching","es":"Surf y Coaching","it":"Surf e Coaching","de":"Surfen & Coaching"})}</a>
        </div>
      </div>
      <div class="split-img">
        <img src="{IMGS['surf2']}" alt="Surf coaching Ngor Island" loading="lazy"/>
      </div>
    </div>
  </div>
</section>

<!-- 3 pillars -->
<section class="section section-light reveal">
  <div class="container">
    <div style="text-align:center; margin-bottom:56px">
      <span class="section-tag">{multilang({"en":"Discover","fr":"Découvrir","es":"Descubrir","it":"Scoprire","de":"Entdecken"})}</span>
      <h2 class="section-title">{multilang({"en":"Everything at Ngor Surfcamp","fr":"Tout à Ngor Surfcamp","es":"Todo en Ngor Surfcamp","it":"Tutto a Ngor Surfcamp","de":"Alles im Ngor Surfcamp"})}</h2>
    </div>
    <div class="grid-3">
      <a href="/surf-house.html" class="card">
        <img src="{IMGS['house1']}" alt="Surf House" class="card-img" loading="lazy"/>
        <div class="card-body">
          <h3 class="card-title">{multilang({"en":"The Surf House","fr":"La Surf House","es":"La Surf House","it":"La Surf House","de":"Das Surf House"})}</h3>
          <p class="card-text">{multilang({"en":"Cozy rooms, pool, sea views — your home by the ocean on Ngor Island.","fr":"Chambres confortables, piscine, vue mer — votre maison au bord de l'océan.","es":"Habitaciones acogedoras, piscina, vistas al mar — tu hogar junto al océano.","it":"Camere accoglienti, piscina, vista mare — la tua casa sull'oceano.","de":"Gemütliche Zimmer, Pool, Meerblick — Ihr Zuhause am Ozean."})}</p>
          <span class="btn btn-secondary" style="font-size:13px;padding:8px 20px">{multilang({"en":"Explore","fr":"Explorer","es":"Explorar","it":"Esplora","de":"Entdecken"})}</span>
        </div>
      </a>
      <a href="/island.html" class="card">
        <img src="{IMGS['island1']}" alt="Ngor Island" class="card-img" loading="lazy"/>
        <div class="card-body">
          <h3 class="card-title">{multilang({"en":"Ngor Island","fr":"Île de Ngor","es":"Isla de Ngor","it":"Isola di Ngor","de":"Ngor Island"})}</h3>
          <p class="card-text">{multilang({"en":"No cars, world-class waves, legendary surf history. A tropical gem off Dakar.","fr":"Pas de voitures, vagues de classe mondiale, histoire légendaire du surf.","es":"Sin coches, olas de clase mundial, historia legendaria del surf.","it":"Niente auto, onde di classe mondiale, storia leggendaria del surf.","de":"Keine Autos, weltklasse Wellen, legendäre Surfgeschichte."})}</p>
          <span class="btn btn-secondary" style="font-size:13px;padding:8px 20px">{multilang({"en":"Discover","fr":"Découvrir","es":"Descubrir","it":"Scoprire","de":"Entdecken"})}</span>
        </div>
      </a>
      <a href="/surfing.html" class="card">
        <img src="{IMGS['surf1']}" alt="Surfing Senegal" class="card-img" loading="lazy"/>
        <div class="card-body">
          <h3 class="card-title">{multilang({"en":"Surfing & Coaching","fr":"Surf & Coaching","es":"Surf y Coaching","it":"Surf e Coaching","de":"Surfen & Coaching"})}</h3>
          <p class="card-text">{multilang({"en":"Professional coaching with video analysis. All levels, all year round.","fr":"Coaching professionnel avec analyse vidéo. Tous niveaux, toute l'année.","es":"Coaching profesional con análisis de vídeo. Todos los niveles, todo el año.","it":"Coaching professionale con analisi video. Tutti i livelli, tutto l'anno.","de":"Professionelles Coaching mit Videoanalyse. Alle Level, das ganze Jahr."})}</p>
          <span class="btn btn-secondary" style="font-size:13px;padding:8px 20px">{multilang({"en":"Learn More","fr":"En savoir plus","es":"Saber más","it":"Scopri di più","de":"Mehr erfahren"})}</span>
        </div>
      </a>
    </div>
  </div>
</section>

<!-- Testimonial -->
<section class="section reveal">
  <div class="container container-sm">
    <div style="text-align:center; margin-bottom:40px">
      <span class="section-tag">{multilang({"en":"Reviews","fr":"Avis","es":"Reseñas","it":"Recensioni","de":"Bewertungen"})}</span>
      <h2 class="section-title">{multilang({"en":"What surfers say","fr":"Ce que disent nos surfeurs","es":"Lo que dicen nuestros surfistas","it":"Cosa dicono i nostri surfisti","de":"Was Surfer sagen"})}</h2>
    </div>
    <div class="testimonial">
      <p class="testimonial-text">{_testimonial}</p>
      <div style="display:flex;align-items:center;gap:16px">
        <img src="{IMGS['review']}" alt="Marc Lecarpentier" style="width:50px;height:50px;border-radius:50%;object-fit:cover"/>
        <div>
          <div class="testimonial-author">Marc Lecarpentier</div>
          <div style="font-size:13px;color:var(--muted)">{multilang({"en":"Surfer, France","fr":"Surfeur, France","es":"Surfista, Francia","it":"Surfista, Francia","de":"Surfer, Frankreich"})}</div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Blog preview -->
<section class="section section-light reveal">
  <div class="container">
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:40px;flex-wrap:wrap;gap:16px">
      <div>
        <span class="section-tag">Blog</span>
        <h2 class="section-title">{multilang({"en":"Latest Articles","fr":"Derniers articles","es":"Últimos artículos","it":"Ultimi articoli","de":"Neueste Artikel"})}</h2>
      </div>
      <a href="/blog/" class="btn btn-ocean">{multilang({"en":"View all articles","fr":"Voir tous les articles","es":"Ver todos los artículos","it":"Vedi tutti gli articoli","de":"Alle Artikel anzeigen"})}</a>
    </div>
    <div class="grid-3">
"""

for art in all_articles_en[:3]:
    img_key = art["slug"]
    img_url_art = f"/assets/images/{img_key}.png" if os.path.exists(f"{DEMO_DIR}/assets/images/{img_key}.png") else IMGS["hero_blog"]
    # Load FR translation for title
    fr_art = load(f"{ARTICLES}/fr/{art['slug']}.json")
    fr_title = fr_art.get("title", art["title"]) if fr_art else art["title"]
    homepage_html += f"""
      <a href="/blog/{art['slug']}.html" class="card">
        <img src="{img_url_art}" alt="{art['title']}" class="card-img" loading="lazy" onerror="this.src='{IMGS['hero_blog']}'"/>
        <div class="card-body">
          <span class="blog-category">{art.get('category','')}</span>
          <h3 class="card-title" style="font-size:17px">
            <span data-lang="en">{art['title'][:70]}</span>
            <span data-lang="fr" style="display:none">{fr_title[:70]}</span>
            <span data-lang="es" style="display:none">{(load(f"{ARTICLES}/es/{art['slug']}.json") or {{}}).get('title', art['title'])[:70]}</span>
            <span data-lang="it" style="display:none">{(load(f"{ARTICLES}/it/{art['slug']}.json") or {{}}).get('title', art['title'])[:70]}</span>
            <span data-lang="de" style="display:none">{(load(f"{ARTICLES}/de/{art['slug']}.json") or {{}}).get('title', art['title'])[:70]}</span>
          </h3>
        </div>
      </a>"""

homepage_html += """
    </div>
  </div>
</section>

<!-- CTA Banner -->
<section class="cta-banner reveal">
  <h2>""" + multilang({"en":"Ready to ride? Book your stay","fr":"Prêt à surfer ? Réservez votre séjour","es":"¿Listo para surfear? Reserva tu estancia","it":"Pronto a surfare? Prenota il tuo soggiorno","de":"Bereit zum Surfen? Buche deinen Aufenthalt"}) + """</h2>
  <p>""" + multilang({"en":"Ngor Island, Dakar, Senegal — WhatsApp: +221 78 925 70 25","fr":"Île de Ngor, Dakar, Sénégal — WhatsApp : +221 78 925 70 25","es":"Isla de Ngor, Dakar, Senegal — WhatsApp: +221 78 925 70 25","it":"Isola di Ngor, Dakar, Senegal — WhatsApp: +221 78 925 70 25","de":"Ngor Island, Dakar, Senegal — WhatsApp: +221 78 925 70 25"}) + """</p>
  <a href="/booking.html" class="btn btn-primary" style="font-size:16px;padding:16px 40px">""" + multilang({"en":"Check Availability","fr":"Vérifier les disponibilités","es":"Consultar disponibilidad","it":"Controlla disponibilità","de":"Verfügbarkeit prüfen"}) + """</a>
</section>
""" + footer() + close_page()

with open(f"{DEMO_DIR}/index.html", "w") as f:
    f.write(homepage_html)
print("✅ Homepage written")

# ════════════════════════════════════════════════════════════════════════════════
# BUILD SURF HOUSE PAGE
# ════════════════════════════════════════════════════════════════════════════════
print("Building surf house page...")
sh = {lang: page_content.get(lang, {}).get("/ngor-surf-house", {}) for lang in LANGS}

surf_house_html = head(
    sh["en"].get("title_tag", "Ngor Surf House | Surf Camp Stay in Senegal"),
    sh["en"].get("meta_description", "Stay at our surf house on Ngor Island.")
) + nav("surf-house") + hero(
    IMGS["hero_house"],
    sh["en"].get("h1","Surf House on Ngor Island"),
    sh["fr"].get("h1","Surf House à l'Île de Ngor"),
    sh["es"].get("h1","Surf House en Ngor Island"),
    sh["it"].get("h1","Surf House a Ngor Island"),
    sh["de"].get("h1","Surf House auf Ngor Island"),
    sh["en"].get("hero_subtitle","Your home by the ocean"),
    sh["fr"].get("hero_subtitle","Votre maison au bord de l'océan"),
    sh["es"].get("hero_subtitle","Tu hogar junto al océano"),
    sh["it"].get("hero_subtitle","La tua casa sull'oceano"),
    sh["de"].get("hero_subtitle","Ihr Zuhause am Ozean"),
) + f"""
<section class="section reveal">
  <div class="container">
    <div class="split-section">
      <div>
        <span class="section-tag">{multilang({"en":"Accommodation","fr":"Hébergement","es":"Alojamiento","it":"Alloggio","de":"Unterkunft"})}</span>
        <h2 class="section-title">{multilang({l: sh[l].get("sections",[{}])[0].get("h2","Comfortable rooms steps from the waves") if sh[l].get("sections") else "Comfortable rooms steps from the waves" for l in LANGS})}</h2>
        <p style="font-size:17px;color:var(--muted);margin-bottom:32px;line-height:1.8">
          {multilang({l: sh[l].get("intro","") for l in LANGS})}
        </p>
        <a href="/booking.html" class="btn btn-primary">{multilang({"en":"Book Your Room","fr":"Réserver votre chambre","es":"Reservar tu habitación","it":"Prenota la tua stanza","de":"Zimmer buchen"})}</a>
      </div>
      <div class="split-img">
        <img src="{IMGS['house2']}" alt="Surf House Ngor" loading="lazy"/>
      </div>
    </div>
  </div>
</section>

<!-- Amenities -->
<section class="section section-light reveal">
  <div class="container">
    <div style="text-align:center;margin-bottom:48px">
      <span class="section-tag">{multilang({"en":"What's included","fr":"Inclus","es":"Incluido","it":"Incluso","de":"Inbegriffen"})}</span>
      <h2 class="section-title">{multilang({"en":"Private & Shared Rooms","fr":"Chambres privées et partagées","es":"Habitaciones privadas y compartidas","it":"Camere private e condivise","de":"Einzel- und Mehrbettzimmer"})}</h2>
    </div>
    <div class="grid-3">
      {"".join([f'''<div class="feature-item reveal">
        <div class="feature-icon">{icon}</div>
        <div>
          <div class="feature-title">{multilang(en_fr_es_it_de[0])}</div>
          <div class="feature-text">{multilang(en_fr_es_it_de[1])}</div>
        </div>
      </div>''' for icon, en_fr_es_it_de in [
          ("🏄", [{"en":"Surf Transfers","fr":"Transferts surf","es":"Traslados surf","it":"Trasferimenti surf","de":"Surf-Transfers"},
                  {"en":"Boat transfers to Ngor Right & Left, and minibus to Dakar's best spots.","fr":"Transferts en pirogue vers Ngor Right & Left, et minibus vers les meilleurs spots de Dakar.","es":"Traslados en bote a Ngor Right & Left, y minibús a los mejores spots de Dakar.","it":"Trasferimenti in barca a Ngor Right & Left, e minibus verso i migliori spot di Dakar.","de":"Bootüberfahrten zu Ngor Right & Left und Minibus zu Dakars besten Spots."}]),
          ("🍳", [{"en":"Breakfast & Dinner","fr":"Petit-déjeuner & Dîner","es":"Desayuno y Cena","it":"Colazione e Cena","de":"Frühstück & Abendessen"},
                  {"en":"Authentic Senegalese meals every day. Filtered water, tea and coffee included.","fr":"Plats sénégalais authentiques tous les jours. Eau filtrée, thé et café inclus.","es":"Comidas senegalesas auténticas todos los días. Agua filtrada, té y café incluidos.","it":"Pasti senegalesi autentici ogni giorno. Acqua filtrata, tè e caffè inclusi.","de":"Authentische senegalesische Gerichte täglich. Gefiltertes Wasser, Tee und Kaffee inklusive."}]),
          ("🌊", [{"en":"Daily Surf Guiding","fr":"Guide surf quotidien","es":"Guía surf diario","it":"Guida surf giornaliera","de":"Tägliche Surf-Führung"},
                  {"en":"We guide you to the best spot of the day, every day. All levels welcome.","fr":"Nous vous guidons vers le meilleur spot du jour, chaque jour. Tous niveaux bienvenus.","es":"Te llevamos al mejor spot del día, todos los días. Todos los niveles bienvenidos.","it":"Ti guidiamo verso il miglior spot del giorno, ogni giorno. Tutti i livelli benvenuti.","de":"Wir führen Sie täglich zum besten Spot des Tages. Alle Level willkommen."}]),
          ("📚", [{"en":"Surf Theory Classes","fr":"Cours de théorie surf","es":"Clases de teoría surf","it":"Lezioni di teoria surf","de":"Surf-Theoriestunden"},
                  {"en":"Free surf theory sessions: paddling, pop-up, turns and more.","fr":"Sessions de théorie surf gratuites : paddle, pop-up, virages et plus.","es":"Sesiones de teoría surf gratuitas: remo, pop-up, giros y más.","it":"Sessioni di teoria surf gratuite: paddling, pop-up, virate e altro.","de":"Kostenlose Surf-Theoriestunden: Paddeln, Pop-up, Kurven und mehr."}]),
          ("🏊", [{"en":"Pool & Common Areas","fr":"Piscine et espaces communs","es":"Piscina y áreas comunes","it":"Piscina e aree comuni","de":"Pool & Gemeinschaftsbereiche"},
                  {"en":"Relax in our outdoor swimming pool and chill spaces in the heart of the island.","fr":"Détendez-vous dans notre piscine extérieure et nos espaces de détente au cœur de l'île.","es":"Relájate en nuestra piscina al aire libre y espacios chill en el corazón de la isla.","it":"Rilassati nella nostra piscina all'aperto e negli spazi chill nel cuore dell'isola.","de":"Entspannen Sie sich in unserem Außenpool und den Chill-Bereichen im Herzen der Insel."}]),
          ("📶", [{"en":"Free Wi-Fi & Daily Cleaning","fr":"Wi-Fi gratuit & ménage quotidien","es":"Wi-Fi gratis y limpieza diaria","it":"Wi-Fi gratuito e pulizia giornaliera","de":"Kostenloses WLAN & tägliche Reinigung"},
                  {"en":"Stay connected and enjoy a clean room every day so you can focus on surfing.","fr":"Restez connecté et profitez d'une chambre propre chaque jour pour vous concentrer sur le surf.","es":"Mantente conectado y disfruta de una habitación limpia cada día para centrarte en el surf.","it":"Rimani connesso e goditi una camera pulita ogni giorno per concentrarti sul surf.","de":"Bleiben Sie verbunden und genießen Sie täglich ein sauberes Zimmer."}]),
      ]])}
    </div>
  </div>
</section>

<!-- Photo gallery of house -->
<section class="section reveal">
  <div class="container">
    <h2 class="section-title" style="text-align:center;margin-bottom:40px">{multilang({"en":"Life at the Surf House","fr":"La vie à la Surf House","es":"Vida en la Surf House","it":"La vita alla Surf House","de":"Leben im Surf House"})}</h2>
    <div class="gallery-grid">
      {"".join([f'<div class="gallery-item"><img src="{url}" alt="Ngor Surf House" loading="lazy"/></div>' for url in [IMGS['house1'],IMGS['house2'],IMGS['house3'],IMGS['food'],IMGS['pool'],IMGS['surf3']]])}
    </div>
  </div>
</section>

<!-- CTA -->
<section class="cta-banner reveal">
  <h2>{multilang({"en":"Ready to book your stay?","fr":"Prêt à réserver votre séjour ?","es":"¿Listo para reservar tu estancia?","it":"Pronto a prenotare il tuo soggiorno?","de":"Bereit, Ihren Aufenthalt zu buchen?"})}</h2>
  <p>{multilang({"en":"Contact us on WhatsApp for availability and prices.","fr":"Contactez-nous sur WhatsApp pour les disponibilités et les tarifs.","es":"Contáctenos por WhatsApp para disponibilidad y precios.","it":"Contattaci su WhatsApp per disponibilità e prezzi.","de":"Kontaktieren Sie uns per WhatsApp für Verfügbarkeit und Preise."})}</p>
  <div style="display:flex;gap:16px;justify-content:center;flex-wrap:wrap">
    <a href="/booking.html" class="btn btn-primary">{multilang({"en":"Book Now","fr":"Réserver maintenant","es":"Reservar ahora","it":"Prenota ora","de":"Jetzt buchen"})}</a>
    <a href="https://wa.me/221789257025" target="_blank" class="btn btn-outline">WhatsApp: +221 78 925 70 25</a>
  </div>
</section>
""" + footer() + close_page()

with open(f"{DEMO_DIR}/surf-house.html","w") as f:
    f.write(surf_house_html)
print("✅ Surf House page written")

# ════════════════════════════════════════════════════════════════════════════════
# BUILD ISLAND PAGE
# ════════════════════════════════════════════════════════════════════════════════
print("Building island page...")
ip = {lang: page_content.get(lang, {}).get("/ngor-island", {}) for lang in LANGS}

island_html = head(
    ip["en"].get("title_tag","Ngor Island Senegal | Surf, Stay & Relax"),
    ip["en"].get("meta_description","Discover Ngor Island — world-class waves, no cars, authentic West African atmosphere.")
) + nav("island") + hero(
    IMGS["hero_island"],
    ip["en"].get("h1","Discover Ngor Island"),
    ip["fr"].get("h1","Découvrir l'Île de Ngor"),
    ip["es"].get("h1","Descubre la Isla de Ngor"),
    ip["it"].get("h1","Scopri l'Isola di Ngor"),
    ip["de"].get("h1","Entdecke Ngor Island"),
    ip["en"].get("hero_subtitle","A hidden gem off the coast of Dakar"),
    ip["fr"].get("hero_subtitle","Un joyau caché au large de Dakar"),
    ip["es"].get("hero_subtitle","Una joya escondida frente a las costas de Dakar"),
    ip["it"].get("hero_subtitle","Un gioiello nascosto al largo di Dakar"),
    ip["de"].get("hero_subtitle","Ein verstecktes Juwel vor der Küste Dakars"),
) + f"""
<section class="section reveal">
  <div class="container">
    <div class="split-section">
      <div>
        <span class="section-tag">{multilang({"en":"Ngor Island","fr":"Île de Ngor","es":"Isla de Ngor","it":"Isola di Ngor","de":"Ngor Island"})}</span>
        <h2 class="section-title">{multilang({"en":"Two sides, two moods","fr":"Deux côtés, deux ambiances","es":"Dos lados, dos ambientes","it":"Due lati, due atmosfere","de":"Zwei Seiten, zwei Stimmungen"})}</h2>
        <p style="font-size:17px;color:var(--muted);margin-bottom:24px;line-height:1.8">
          {multilang({l: ip[l].get("intro","Just a few hundred meters from Dakar, Ngor Island is a peaceful escape from the city. A short pirogue ride takes you to this charming island known for its authentic vibe and world-class surf.") for l in LANGS})}
        </p>
      </div>
      <div class="split-img">
        <img src="{IMGS['island2']}" alt="Ngor Island" loading="lazy"/>
      </div>
    </div>
  </div>
</section>

<!-- Island features -->
<section class="section section-light reveal">
  <div class="container">
    <div class="grid-3">
      {"".join([f'''<div class="card">
        <img src="{img}" alt="{multilang(titles)}" class="card-img" loading="lazy"/>
        <div class="card-body">
          <h3 class="card-title">{multilang(titles)}</h3>
          <p class="card-text">{multilang(descs)}</p>
        </div>
      </div>''' for img, titles, descs in [
          (IMGS['ngor_right'],
           {"en":"Legendary Surf — Ngor Right","fr":"Surf Légendaire — Ngor Right","es":"Surf Legendario — Ngor Right","it":"Surf Leggendario — Ngor Right","de":"Legendäres Surfen — Ngor Right"},
           {"en":"One of West Africa's most famous waves, made legendary by The Endless Summer (1964/1966).","fr":"L'une des vagues les plus célèbres d'Afrique de l'Ouest, rendue légendaire par The Endless Summer.","es":"Una de las olas más famosas de África Occidental, hecha legendaria por The Endless Summer.","it":"Una delle onde più famose dell'Africa Occidentale, resa leggendaria da The Endless Summer.","de":"Eine der bekanntesten Wellen Westafrikas, legendär durch The Endless Summer."}),
          (IMGS['art'],
           {"en":"Bohemian Spirit","fr":"Esprit bohème","es":"Espíritu bohemio","it":"Spirito bohémien","de":"Böhmischer Geist"},
           {"en":"Street art, colorful houses, art galleries and cozy cafés — Ngor has a unique soul.","fr":"Street art, maisons colorées, galeries d'art et cafés cosy — Ngor a une âme unique.","es":"Arte callejero, casas coloridas, galerías de arte y cafés acogedores — Ngor tiene un alma única.","it":"Street art, case colorate, gallerie d'arte e caffè accoglienti — Ngor ha un'anima unica.","de":"Street Art, bunte Häuser, Kunstgalerien und gemütliche Cafés — Ngor hat eine einzigartige Seele."}),
          (IMGS['sunset'],
           {"en":"Magical Sunsets","fr":"Couchers de soleil magiques","es":"Atardeceres mágicos","it":"Tramonti magici","de":"Magische Sonnenuntergänge"},
           {"en":"The island's western shore offers breathtaking sunset views over the Atlantic. A must-see.","fr":"Le rivage ouest de l'île offre des vues époustouflantes sur les couchers de soleil sur l'Atlantique.","es":"La costa occidental de la isla ofrece impresionantes vistas al atardecer sobre el Atlántico.","it":"La riva occidentale dell'isola offre viste mozzafiato al tramonto sull'Atlantico.","de":"Die Westküste der Insel bietet atemberaubende Sonnenuntergangspanoramen über dem Atlantik."}),
      ]])}
    </div>
  </div>
</section>

<!-- Stats / Facts -->
<div class="stats-bar reveal">
  <div class="stat-item">
    <span class="stat-number">800m</span>
    <span class="stat-label">{multilang({"en":"from Dakar","fr":"de Dakar","es":"de Dakar","it":"da Dakar","de":"von Dakar"})}</span>
  </div>
  <div class="stat-item">
    <span class="stat-number">0</span>
    <span class="stat-label">{multilang({"en":"Cars on island","fr":"Voitures sur l'île","es":"Coches en la isla","it":"Auto sull'isola","de":"Autos auf der Insel"})}</span>
  </div>
  <div class="stat-item">
    <span class="stat-number">#43</span>
    <span class="stat-label">{multilang({"en":"most beautiful bay","fr":"plus belle baie","es":"bahía más bella","it":"baia più bella","de":"schönste Bucht"})}</span>
  </div>
  <div class="stat-item">
    <span class="stat-number">1964</span>
    <span class="stat-label">{multilang({"en":"Endless Summer","fr":"Endless Summer","es":"Endless Summer","it":"Endless Summer","de":"Endless Summer"})}</span>
  </div>
</div>

<section class="cta-banner reveal">
  <h2>{multilang({"en":"Experience Ngor Island","fr":"Vivre l'Île de Ngor","es":"Vive la Isla de Ngor","it":"Vivi l'Isola di Ngor","de":"Erlebe Ngor Island"})}</h2>
  <p>{multilang({"en":"Stay at Ngor Surfcamp Teranga and make the island your home.","fr":"Séjournez au Ngor Surfcamp Teranga et faites de l'île votre maison.","es":"Alójate en Ngor Surfcamp Teranga y convierte la isla en tu hogar.","it":"Soggiorna al Ngor Surfcamp Teranga e fai dell'isola la tua casa.","de":"Übernachten Sie im Ngor Surfcamp Teranga und machen Sie die Insel zu Ihrem Zuhause."})}</p>
  <a href="/booking.html" class="btn btn-primary">{multilang({"en":"Book Your Stay","fr":"Réserver","es":"Reservar","it":"Prenota","de":"Jetzt buchen"})}</a>
</section>
""" + footer() + close_page()

with open(f"{DEMO_DIR}/island.html","w") as f:
    f.write(island_html)
print("✅ Island page written")

# ════════════════════════════════════════════════════════════════════════════════
# BUILD SURFING PAGE
# ════════════════════════════════════════════════════════════════════════════════
print("Building surfing page...")
sp = {lang: page_content.get(lang, {}).get("/surfing", {}) for lang in LANGS}

surfing_html = head(
    sp["en"].get("title_tag","Surfing in Senegal | Coaching at Ngor Surfcamp"),
    sp["en"].get("meta_description","Professional surf coaching with video analysis. All levels, world-class waves.")
) + nav("surfing") + hero(
    IMGS["hero_surf"],
    sp["en"].get("h1","Ride World-Class Waves"),
    sp["fr"].get("h1","Surfez des vagues de classe mondiale"),
    sp["es"].get("h1","Surfea olas de clase mundial"),
    sp["it"].get("h1","Surfate onde di classe mondiale"),
    sp["de"].get("h1","Weltklasse-Wellen reiten"),
    sp["en"].get("hero_subtitle","Professional coaching on Ngor's legendary breaks"),
    sp["fr"].get("hero_subtitle","Coaching professionnel sur les vagues légendaires de Ngor"),
    sp["es"].get("hero_subtitle","Coaching profesional en los breaks legendarios de Ngor"),
    sp["it"].get("hero_subtitle","Coaching professionale sulle break leggendarie di Ngor"),
    sp["de"].get("hero_subtitle","Professionelles Coaching an Ngors legendären Breaks"),
) + f"""
<section class="section reveal">
  <div class="container">
    <div style="text-align:center;margin-bottom:56px">
      <span class="section-tag">{multilang({"en":"Surf Coaching","fr":"Coaching Surf","es":"Coaching Surf","it":"Coaching Surf","de":"Surf-Coaching"})}</span>
      <h2 class="section-title">{multilang({"en":"Waves, Coaching, Real Results","fr":"Vagues, Coaching, Vrais Résultats","es":"Olas, Coaching, Resultados Reales","it":"Onde, Coaching, Risultati Reali","de":"Wellen, Coaching, Echte Ergebnisse"})}</h2>
      <p class="section-subtitle">{multilang({l: sp[l].get("intro","") for l in LANGS})}</p>
    </div>
    <div class="grid-2">
      <div class="split-img"><img src="{IMGS['surf3']}" alt="Surf coaching" loading="lazy"/></div>
      <div>
        {"".join([f'''<div class="feature-item">
          <div class="feature-icon">{ico}</div>
          <div>
            <div class="feature-title">{multilang(t)}</div>
            <div class="feature-text">{multilang(d)}</div>
          </div>
        </div>''' for ico,t,d in [
            ("🎥",{"en":"Video Analysis","fr":"Analyse vidéo","es":"Análisis de vídeo","it":"Analisi video","de":"Videoanalyse"},
                  {"en":"Personalized sessions with video review to identify and fix your technique in real time.","fr":"Séances personnalisées avec analyse vidéo pour identifier et corriger votre technique en temps réel.","es":"Sesiones personalizadas con análisis de vídeo para identificar y corregir tu técnica en tiempo real.","it":"Sessioni personalizzate con analisi video per identificare e correggere la tua tecnica in tempo reale.","de":"Personalisierte Sessions mit Videoanalyse zur Technikoptimierung in Echtzeit."}),
            ("🏄",{"en":"All Levels Welcome","fr":"Tous niveaux bienvenus","es":"Todos los niveles bienvenidos","it":"Tutti i livelli benvenuti","de":"Alle Level willkommen"},
                  {"en":"Beginner, intermediate or advanced — we tailor coaching to your exact level and goals.","fr":"Débutant, intermédiaire ou avancé — nous adaptons le coaching à votre niveau exact.","es":"Principiante, intermedio o avanzado — adaptamos el coaching a tu nivel exacto.","it":"Principiante, intermedio o avanzato — adattiamo il coaching al tuo livello esatto.","de":"Anfänger, Fortgeschrittener oder Profi — wir passen das Coaching genau an Sie an."}),
            ("📋",{"en":"Licensed Federation","fr":"Fédération agréée","es":"Federación licenciada","it":"Federazione licenziata","de":"Lizenzierte Föderation"},
                  {"en":"Officially licensed with the Senegalese Federation of Surfing. Qualified, safety-first instructors.","fr":"Officiellement agréé par la Fédération Sénégalaise de Surf. Moniteurs qualifiés, sécurité en premier.","es":"Oficialmente licenciado por la Federación Senegalesa de Surf. Instructores cualificados.","it":"Ufficialmente autorizzato dalla Federazione Senegalese di Surf. Istruttori qualificati.","de":"Offiziell lizenziert von der senegalesischen Surfverband. Qualifizierte Instruktoren."}),
            ("🌊",{"en":"Ngor Right & Ngor Left","fr":"Ngor Right & Ngor Left","es":"Ngor Right & Ngor Left","it":"Ngor Right & Ngor Left","de":"Ngor Right & Ngor Left"},
                  {"en":"Two world-class breaks: Ngor Right (intermediate/advanced) and Ngor Left (all levels, softer).","fr":"Deux breaks de classe mondiale : Ngor Right (intermédiaire/avancé) et Ngor Left (tous niveaux).","es":"Dos breaks de clase mundial: Ngor Right (intermedio/avanzado) y Ngor Left (todos los niveles).","it":"Due break di classe mondiale: Ngor Right (intermedio/avanzato) e Ngor Left (tutti i livelli).","de":"Zwei Weltklasse-Breaks: Ngor Right (Fortgeschrittene) und Ngor Left (alle Level)."}),
        ]])}
      </div>
    </div>
  </div>
</section>

<!-- Photo grid -->
<section class="section section-light reveal">
  <div class="container">
    <h2 class="section-title" style="text-align:center;margin-bottom:40px">{multilang({"en":"Our surf trips in action","fr":"Nos sessions de surf en action","es":"Nuestros viajes de surf en acción","it":"I nostri viaggi surf in azione","de":"Unsere Surftrips in Aktion"})}</h2>
    <div class="gallery-grid">
      {"".join([f'<div class="gallery-item"><img src="{u}" alt="Surfing Senegal" loading="lazy"/></div>' for u in [IMGS['surf1'],IMGS['surf2'],IMGS['surf3'],IMGS['surf4'],IMGS['ngor_right'],IMGS['hero_surf']]])}
    </div>
  </div>
</section>

<section class="cta-banner reveal">
  <h2>{multilang({"en":"Start Your Surf Journey","fr":"Commencez votre aventure surf","es":"Comienza tu aventura surf","it":"Inizia il tuo viaggio surf","de":"Beginne deine Surfreise"})}</h2>
  <p>{multilang({"en":"Book a coaching package and take your surfing to the next level.","fr":"Réservez un package coaching et faites passer votre surf au niveau supérieur.","es":"Reserva un paquete de coaching y lleva tu surf al siguiente nivel.","it":"Prenota un pacchetto di coaching e porta il tuo surf al livello successivo.","de":"Buche ein Coaching-Paket und bringe dein Surfen auf das nächste Level."})}</p>
  <a href="/booking.html" class="btn btn-primary">{multilang({"en":"Book Coaching","fr":"Réserver le coaching","es":"Reservar coaching","it":"Prenota coaching","de":"Coaching buchen"})}</a>
</section>
""" + footer() + close_page()

with open(f"{DEMO_DIR}/surfing.html","w") as f:
    f.write(surfing_html)
print("✅ Surfing page written")

# ════════════════════════════════════════════════════════════════════════════════
# BUILD BOOKING PAGE
# ════════════════════════════════════════════════════════════════════════════════
print("Building booking page...")
bk = {lang: page_content.get(lang, {}).get("/book-surf-trip", {}) for lang in LANGS}

booking_html = head(
    bk["en"].get("title_tag","Book Your Surf Stay | Ngor Surfcamp Teranga"),
    bk["en"].get("meta_description","Check availability and book your surf camp stay at Ngor Island, Dakar.")
) + nav("book") + f"""
<div class="page-header" style="background-image:url('{IMGS['hero_book']}')">
  <h1>{multilang({"en":"Book Your Stay","fr":"Réserver votre séjour","es":"Reservar tu estancia","it":"Prenota il tuo soggiorno","de":"Ihren Aufenthalt buchen"})}</h1>
  <p>{multilang({"en":"Check availability and we'll take care of the rest!","fr":"Vérifiez les disponibilités et nous nous occupons du reste !","es":"Consulta la disponibilidad y nosotros nos encargamos del resto.","it":"Controlla la disponibilità e pensiamo noi al resto!","de":"Prüfen Sie die Verfügbarkeit und wir kümmern uns um den Rest!"})}</p>
</div>

<section class="section reveal">
  <div class="container">
    <div class="split-section">
      <div class="booking-form">
        <h2 style="margin-bottom:28px;font-size:26px">{multilang({"en":"Check Availability & Book","fr":"Vérifier disponibilités & Réserver","es":"Consultar disponibilidad y Reservar","it":"Controlla disponibilità e Prenota","de":"Verfügbarkeit prüfen & Buchen"})}</h2>
        <form id="booking-form" action="https://wa.me/221789257025" method="get" target="_blank">
          <div class="form-grid">
            <div class="form-group">
              <label class="form-label">{multilang({"en":"First Name","fr":"Prénom","es":"Nombre","it":"Nome","de":"Vorname"})}</label>
              <input type="text" class="form-input" required placeholder="John"/>
            </div>
            <div class="form-group">
              <label class="form-label">{multilang({"en":"Last Name","fr":"Nom","es":"Apellido","it":"Cognome","de":"Nachname"})}</label>
              <input type="text" class="form-input" required placeholder="Doe"/>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">{multilang({"en":"Email","fr":"Email","es":"Email","it":"Email","de":"E-Mail"})}</label>
            <input type="email" class="form-input" required placeholder="john@example.com"/>
          </div>
          <div class="form-group">
            <label class="form-label">{multilang({"en":"WhatsApp / Phone","fr":"WhatsApp / Téléphone","es":"WhatsApp / Teléfono","it":"WhatsApp / Telefono","de":"WhatsApp / Telefon"})}</label>
            <input type="tel" class="form-input" required placeholder="+33 6 12 34 56 78"/>
          </div>
          <div class="form-grid">
            <div class="form-group">
              <label class="form-label">{multilang({"en":"Arrival Date","fr":"Date d'arrivée","es":"Fecha de llegada","it":"Data di arrivo","de":"Anreisedatum"})}</label>
              <input type="date" class="form-input" required/>
            </div>
            <div class="form-group">
              <label class="form-label">{multilang({"en":"Departure Date","fr":"Date de départ","es":"Fecha de salida","it":"Data di partenza","de":"Abreisedatum"})}</label>
              <input type="date" class="form-input" required/>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">{multilang({"en":"Surf Level","fr":"Niveau de surf","es":"Nivel de surf","it":"Livello di surf","de":"Surf-Level"})}</label>
            <select class="form-select">
              <option value="">{multilang({"en":"Choose your level","fr":"Choisissez votre niveau","es":"Elige tu nivel","it":"Scegli il tuo livello","de":"Wählen Sie Ihr Level"})}</option>
              <option>{multilang({"en":"Beginner","fr":"Débutant","es":"Principiante","it":"Principiante","de":"Anfänger"})}</option>
              <option>{multilang({"en":"Intermediate","fr":"Intermédiaire","es":"Intermedio","it":"Intermedio","de":"Fortgeschrittener"})}</option>
              <option>{multilang({"en":"Advanced","fr":"Avancé","es":"Avanzado","it":"Avanzato","de":"Fortgeschritten"})}</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">{multilang({"en":"Number of guests","fr":"Nombre de participants","es":"Número de participantes","it":"Numero di partecipanti","de":"Anzahl der Teilnehmer"})}</label>
            <input type="number" class="form-input" min="1" max="20" placeholder="2"/>
          </div>
          <div class="form-group">
            <label class="form-label">{multilang({"en":"Your main goal for this trip","fr":"Votre objectif principal pour ce voyage","es":"Tu objetivo principal para este viaje","it":"Il tuo obiettivo principale per questo viaggio","de":"Ihr Hauptziel für diese Reise"})}</label>
            <textarea class="form-textarea" placeholder="{multilang({'en':'e.g. Learn to surf, improve my backhand...','fr':'ex. Apprendre à surfer, améliorer mon backhand...','es':'ej. Aprender a surfear, mejorar mi revés...','it':'es. Imparare a surfare, migliorare il mio rovescio...','de':'z.B. Surfen lernen, Rückhandtechnik verbessern...'})}"
></textarea>
          </div>
          <div class="form-group" style="display:flex;align-items:center;gap:10px">
            <input type="checkbox" id="flexible"/> 
            <label for="flexible" style="cursor:pointer">{multilang({"en":"I'm flexible on dates — tell me when the swell is best!","fr":"Je suis flexible sur les dates — dites-moi quand le swell est le meilleur !","es":"Soy flexible con las fechas — ¡dime cuándo es mejor el swell!","it":"Sono flessibile sulle date — dimmi quando il swell è migliore!","de":"Ich bin flexibel bei den Daten — sagen Sie mir, wann der Swell am besten ist!"})}</label>
          </div>
          <button type="submit" class="btn btn-primary" style="width:100%;font-size:16px;padding:16px">
            {multilang({"en":"Check Availability & Prices","fr":"Vérifier disponibilités & Prix","es":"Consultar disponibilidad y Precios","it":"Controlla disponibilità e Prezzi","de":"Verfügbarkeit & Preise prüfen"})}
          </button>
        </form>
        <p style="text-align:center;margin-top:20px;font-size:14px;color:var(--muted)">{multilang({"en":"No spam, just waves and logistics. We'll reply within 24h.","fr":"Pas de spam, juste des vagues et de la logistique. Réponse sous 24h.","es":"Sin spam, solo olas y logística. Responderemos en 24h.","it":"Nessuno spam, solo onde e logistica. Risponderemo entro 24h.","de":"Kein Spam, nur Wellen und Logistik. Antwort innerhalb von 24h."})}</p>
      </div>
      <div>
        <h3 style="margin-bottom:24px">{multilang({"en":"Or contact us directly","fr":"Ou contactez-nous directement","es":"O contáctenos directamente","it":"O contattaci direttamente","de":"Oder kontaktieren Sie uns direkt"})}</h3>
        {"".join([f'''<div class="feature-item">
          <div class="feature-icon">{ico}</div>
          <div>
            <div class="feature-title">{multilang(t)}</div>
            <div class="feature-text">{multilang(d)}</div>
          </div>
        </div>''' for ico,t,d in [
            ("📱",{"en":"WhatsApp","fr":"WhatsApp","es":"WhatsApp","it":"WhatsApp","de":"WhatsApp"},
                  {"en":"+221 78 925 70 25 — fastest way to reach us!","fr":"+221 78 925 70 25 — la façon la plus rapide de nous joindre !","es":"+221 78 925 70 25 — ¡la forma más rápida de contactarnos!","it":"+221 78 925 70 25 — il modo più rapido per contattarci!","de":"+221 78 925 70 25 — der schnellste Weg, uns zu erreichen!"}),
            ("📧",{"en":"Email","fr":"Email","es":"Email","it":"Email","de":"E-Mail"},
                  {"en":"info@surfcampsenegal.com","fr":"info@surfcampsenegal.com","es":"info@surfcampsenegal.com","it":"info@surfcampsenegal.com","de":"info@surfcampsenegal.com"}),
            ("📍",{"en":"Location","fr":"Localisation","es":"Ubicación","it":"Posizione","de":"Standort"},
                  {"en":"Ngor Island, 800m west of Cap-Vert peninsula, Dakar, Senegal","fr":"Île de Ngor, 800m à l'ouest de la péninsule du Cap-Vert, Dakar, Sénégal","es":"Isla de Ngor, 800m al oeste de la península de Cap-Vert, Dakar, Senegal","it":"Isola di Ngor, 800m a ovest della penisola di Cap-Vert, Dakar, Senegal","de":"Ngor Island, 800m westlich der Cap-Vert-Halbinsel, Dakar, Senegal"}),
        ]])}
        <div style="margin-top:32px;padding:24px;background:var(--light-bg);border-radius:var(--radius)">
          <h4 style="margin-bottom:12px">{multilang({"en":"Booking made easy","fr":"Réservation simplifiée","es":"Reserva fácil","it":"Prenotazione facile","de":"Einfache Buchung"})}</h4>
          <div style="display:flex;flex-direction:column;gap:12px">
            {"".join([f'<div style="display:flex;align-items:center;gap:12px"><div style="width:32px;height:32px;border-radius:50%;background:var(--ocean);color:white;display:flex;align-items:center;justify-content:center;font-weight:700;flex-shrink:0">{n}</div><span style="font-size:15px">{multilang(t)}</span></div>' for n,t in [
              ("1",{"en":"Choose your dates","fr":"Choisissez vos dates","es":"Elige tus fechas","it":"Scegli le tue date","de":"Wählen Sie Ihre Daten"}),
              ("2",{"en":"Fill the form or WhatsApp us","fr":"Remplissez le formulaire ou contactez-nous sur WhatsApp","es":"Rellena el formulario o escríbenos por WhatsApp","it":"Compila il modulo o contattaci su WhatsApp","de":"Füllen Sie das Formular aus oder schreiben Sie uns per WhatsApp"}),
              ("3",{"en":"We'll confirm your room & package","fr":"Nous confirmerons votre chambre & package","es":"Confirmaremos tu habitación y paquete","it":"Confermeremo la tua stanza e il pacchetto","de":"Wir bestätigen Ihr Zimmer und Paket"}),
            ]])}
          </div>
        </div>
      </div>
    </div>
  </div>
</section>
""" + footer() + f"""
<script>
document.getElementById('booking-form').addEventListener('submit', function(e) {{
  e.preventDefault();
  const fname = this.querySelector('input[type=text]').value;
  const msg = encodeURIComponent('Hello Ngor Surfcamp! I would like to book a stay. My name is ' + fname + '. Please send me availability and prices.');
  window.open('https://wa.me/221789257025?text=' + msg, '_blank');
}});
</script>
""" + close_page()

with open(f"{DEMO_DIR}/booking.html","w") as f:
    f.write(booking_html)
print("✅ Booking page written")

# ════════════════════════════════════════════════════════════════════════════════
# BUILD GALLERY PAGE
# ════════════════════════════════════════════════════════════════════════════════
print("Building gallery page...")
gallery_imgs = [IMGS[k] for k in ['gallery1','gallery2','gallery3','gallery4','gallery5','gallery6','gallery7','gallery8','surf1','surf2','surf3','surf4','house1','house2','house3','food','pool','sunset','island1','island2','ngor_right','art']]

gallery_html = head("Gallery | Ngor Surfcamp Teranga", "Browse photos from Ngor Surfcamp Teranga — waves, coaching, island life.") + nav("gallery") + f"""
<div class="page-header" style="background-image:url('{IMGS['hero_gallery']}')">
  <h1>{multilang({"en":"Gallery","fr":"Galerie","es":"Galería","it":"Galleria","de":"Galerie"})}</h1>
  <p>{multilang({"en":"Waves, coaching, island life — Ngor Surfcamp in pictures","fr":"Vagues, coaching, vie d'île — Ngor Surfcamp en images","es":"Olas, coaching, vida isleña — Ngor Surfcamp en fotos","it":"Onde, coaching, vita d'isola — Ngor Surfcamp in foto","de":"Wellen, Coaching, Inselleben — Ngor Surfcamp in Bildern"})}</p>
</div>
<section class="section reveal">
  <div class="container">
    <div class="gallery-grid" id="lightbox-gallery">
      {"".join(['<div class="gallery-item" onclick="openLightbox(this.children[0].src)" title="Ngor Surfcamp"><img src="' + url + '" alt="Ngor Surfcamp Teranga" loading="lazy"/></div>' for url in gallery_imgs])}
    </div>
  </div>
</section>
<!-- Lightbox -->
<div id="lightbox" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,0.9);z-index:1000;align-items:center;justify-content:center;cursor:pointer" onclick="closeLightbox()">
  <img id="lightbox-img" src="" style="max-width:90vw;max-height:90vh;border-radius:8px;object-fit:contain"/>
  <button onclick="closeLightbox()" style="position:absolute;top:20px;right:20px;background:rgba(255,255,255,0.2);border:none;color:white;font-size:28px;cursor:pointer;border-radius:50%;width:44px;height:44px">×</button>
</div>
<script>
function openLightbox(src){{document.getElementById('lightbox').style.display='flex';document.getElementById('lightbox-img').src=src;}}
function closeLightbox(){{document.getElementById('lightbox').style.display='none';}}
</script>
""" + footer() + close_page()

with open(f"{DEMO_DIR}/gallery.html","w") as f:
    f.write(gallery_html)
print("✅ Gallery page written")

# ════════════════════════════════════════════════════════════════════════════════
# BUILD FAQ PAGE
# ════════════════════════════════════════════════════════════════════════════════
print("Building FAQ page...")
fq = {lang: page_content.get(lang, {}).get("/faq", {}) for lang in LANGS}

faqs = [
    ({"en":"What surf level do I need?","fr":"Quel niveau de surf faut-il ?","es":"¿Qué nivel de surf necesito?","it":"Quale livello di surf è necessario?","de":"Welches Surflevel brauche ich?"},
     {"en":"We welcome all levels from complete beginners to experienced surfers. Our coaches adapt sessions to your exact level.","fr":"Nous accueillons tous les niveaux, des débutants complets aux surfeurs expérimentés. Nos coachs adaptent les sessions à votre niveau exact.","es":"Damos la bienvenida a todos los niveles, desde principiantes hasta surfistas experimentados. Nuestros coaches adaptan las sesiones a tu nivel exacto.","it":"Accogliamo tutti i livelli, dai principianti assoluti ai surfisti esperti. I nostri coach adattano le sessioni al tuo livello esatto.","de":"Wir begrüßen alle Level, von kompletten Anfängern bis zu erfahrenen Surfern. Unsere Coaches passen die Sessions genau an Ihr Level an."}),
    ({"en":"What's the best time to visit?","fr":"Quelle est la meilleure période pour visiter ?","es":"¿Cuál es la mejor época para visitar?","it":"Qual è il periodo migliore per visitare?","de":"Wann ist die beste Reisezeit?"},
     {"en":"The surf season in Senegal runs year-round, with the most consistent swells from October to April. Water temperature stays around 22-27°C.","fr":"La saison de surf au Sénégal se déroule toute l'année, avec les houles les plus régulières d'octobre à avril. La température de l'eau reste autour de 22-27°C.","es":"La temporada de surf en Senegal es todo el año, con los swells más consistentes de octubre a abril. La temperatura del agua se mantiene alrededor de 22-27°C.","it":"La stagione del surf in Senegal è tutto l'anno, con le onde più consistenti da ottobre ad aprile. La temperatura dell'acqua rimane intorno ai 22-27°C.","de":"Die Surfsaison im Senegal dauert das ganze Jahr, mit den beständigsten Swells von Oktober bis April. Die Wassertemperatur liegt bei 22-27°C."}),
    ({"en":"How do I get to Ngor Island?","fr":"Comment rejoindre l'Île de Ngor ?","es":"¿Cómo llego a la Isla de Ngor?","it":"Come raggiungere l'Isola di Ngor?","de":"Wie komme ich nach Ngor Island?"},
     {"en":"Take a taxi or Uber to Ngor beach in Dakar (about 20min from the airport), then a short pirogue (traditional boat) ride for less than €1 to the island.","fr":"Prenez un taxi ou Uber jusqu'à la plage de Ngor à Dakar (environ 20min de l'aéroport), puis une courte traversée en pirogue (bateau traditionnel) pour moins de 1€ jusqu'à l'île.","es":"Toma un taxi o Uber hasta la playa de Ngor en Dakar (unos 20min del aeropuerto), luego un corto trayecto en piragua (barco tradicional) por menos de 1€ hasta la isla.","it":"Prendi un taxi o Uber fino alla spiaggia di Ngor a Dakar (circa 20min dall'aeroporto), poi un breve tragitto in piroga (barca tradizionale) per meno di 1€ fino all'isola.","de":"Nehmen Sie ein Taxi oder Uber zum Ngor-Strand in Dakar (ca. 20min vom Flughafen), dann eine kurze Pirogenfahrt (traditionelles Boot) für weniger als 1€ zur Insel."}),
    ({"en":"Is video analysis included?","fr":"L'analyse vidéo est-elle incluse ?","es":"¿Está incluido el análisis de vídeo?","it":"L'analisi video è inclusa?","de":"Ist die Videoanalyse inbegriffen?"},
     {"en":"Yes! Video analysis is a key part of our coaching program. We film your sessions and review the footage together to accelerate your progression.","fr":"Oui ! L'analyse vidéo est un élément clé de notre programme de coaching. Nous filmons vos sessions et examinons les images ensemble pour accélérer votre progression.","es":"¡Sí! El análisis de vídeo es una parte clave de nuestro programa de coaching. Filmamos tus sesiones y revisamos el material juntos para acelerar tu progresión.","it":"Sì! L'analisi video è una parte fondamentale del nostro programma di coaching. Filmiamo le tue sessioni e rivediamo le riprese insieme per accelerare la tua progressione.","de":"Ja! Die Videoanalyse ist ein wesentlicher Teil unseres Coaching-Programms. Wir filmen Ihre Sessions und überprüfen die Aufnahmen gemeinsam, um Ihren Fortschritt zu beschleunigen."}),
    ({"en":"What's included in the price?","fr":"Qu'est-ce qui est inclus dans le prix ?","es":"¿Qué está incluido en el precio?","it":"Cosa è incluso nel prezzo?","de":"Was ist im Preis inbegriffen?"},
     {"en":"Accommodation, breakfast & dinner, daily surf guiding, theory classes, boat transfers to surf spots, pool access, Wi-Fi and daily room cleaning.","fr":"Hébergement, petit-déjeuner et dîner, guide surf quotidien, cours de théorie, transferts en bateau vers les spots, accès piscine, Wi-Fi et ménage quotidien.","es":"Alojamiento, desayuno y cena, guía surf diario, clases de teoría, traslados en barco a los spots, acceso a la piscina, Wi-Fi y limpieza diaria de la habitación.","it":"Alloggio, colazione e cena, guida surf giornaliera, lezioni di teoria, trasferimenti in barca verso gli spot, accesso alla piscina, Wi-Fi e pulizia giornaliera della camera.","de":"Unterkunft, Frühstück & Abendessen, tägliche Surf-Führung, Theoriestunden, Bootüberfahrten zu Surf-Spots, Poolzugang, WLAN und tägliche Zimmerreinigung."}),
    ({"en":"Can I book just accommodation without coaching?","fr":"Puis-je réserver uniquement l'hébergement sans coaching ?","es":"¿Puedo reservar solo alojamiento sin coaching?","it":"Posso prenotare solo l'alloggio senza coaching?","de":"Kann ich nur Unterkunft ohne Coaching buchen?"},
     {"en":"Yes, we offer accommodation-only options as well as full surf packages with coaching. Contact us on WhatsApp and we'll find the best option for you.","fr":"Oui, nous proposons des options d'hébergement uniquement ainsi que des packages surf complets avec coaching. Contactez-nous sur WhatsApp et nous trouverons la meilleure option pour vous.","es":"Sí, ofrecemos opciones de solo alojamiento así como paquetes de surf completos con coaching. Contáctanos por WhatsApp y encontraremos la mejor opción para ti.","it":"Sì, offriamo opzioni di solo alloggio così come pacchetti surf completi con coaching. Contattaci su WhatsApp e troveremo l'opzione migliore per te.","de":"Ja, wir bieten sowohl Unterkunft-nur-Optionen als auch vollständige Surf-Pakete mit Coaching an. Kontaktieren Sie uns per WhatsApp und wir finden die beste Option für Sie."}),
]

faq_html = head("FAQ | Ngor Surfcamp Teranga","Everything you need to know before booking your surf camp stay at Ngor Island, Senegal.") + nav() + f"""
<div class="page-header" style="background-image:url('{IMGS['hero_surf']}')">
  <h1>{multilang({"en":"Frequently Asked Questions","fr":"Questions fréquemment posées","es":"Preguntas frecuentes","it":"Domande frequenti","de":"Häufig gestellte Fragen"})}</h1>
  <p>{multilang({"en":"Everything you need to know before your surf trip","fr":"Tout ce que vous devez savoir avant votre voyage surf","es":"Todo lo que necesitas saber antes de tu viaje surf","it":"Tutto quello che devi sapere prima del tuo viaggio surf","de":"Alles, was Sie vor Ihrer Surfreise wissen müssen"})}</p>
</div>
<section class="section reveal">
  <div class="container container-sm">
    <div id="faq-list">
      {"".join([f'<div class="faq-item"><div class="faq-question">{multilang(q)}<span class="faq-arrow">▼</span></div><div class="faq-answer">{multilang(a)}</div></div>' for q,a in faqs])}
    </div>
    <div style="text-align:center;margin-top:48px">
      <p style="font-size:17px;margin-bottom:24px">{multilang({"en":"Still have questions? We're happy to help!","fr":"Vous avez encore des questions ? Nous sommes heureux de vous aider !","es":"¿Todavía tienes preguntas? ¡Estamos felices de ayudarte!","it":"Hai ancora domande? Siamo felici di aiutarti!","de":"Noch Fragen? Wir helfen gerne!"})}</p>
      <a href="https://wa.me/221789257025" target="_blank" class="btn btn-primary">{multilang({"en":"Chat on WhatsApp","fr":"Discuter sur WhatsApp","es":"Chatear en WhatsApp","it":"Chatta su WhatsApp","de":"WhatsApp-Chat"})}</a>
    </div>
  </div>
</section>
""" + footer() + close_page()

with open(f"{DEMO_DIR}/faq.html","w") as f:
    f.write(faq_html)
print("✅ FAQ page written")

# ════════════════════════════════════════════════════════════════════════════════
# BUILD BLOG LISTING PAGE
# ════════════════════════════════════════════════════════════════════════════════
print("Building blog listing page...")
os.makedirs(f"{DEMO_DIR}/blog", exist_ok=True)

blog_cards = ""
for art in all_articles_en:
    img_path_local = f"/assets/images/{art['slug']}.png"
    img_src = img_path_local if os.path.exists(f"{DEMO_DIR}{img_path_local}") else IMGS["hero_blog"]
    fr_art = load(f"{ARTICLES}/fr/{art['slug']}.json") or {}
    es_art = load(f"{ARTICLES}/es/{art['slug']}.json") or {}
    it_art = load(f"{ARTICLES}/it/{art['slug']}.json") or {}
    de_art = load(f"{ARTICLES}/de/{art['slug']}.json") or {}
    cat = art.get("category","")
    blog_cards += f"""
  <a href="/blog/{art['slug']}.html" class="card" style="text-decoration:none">
    <img src="{img_src}" alt="{art['title']}" class="card-img" loading="lazy" onerror="this.src='{IMGS['hero_blog']}'"/>
    <div class="card-body">
      <span class="blog-category">{cat}</span>
      <h3 class="card-title" style="font-size:17px;line-height:1.4">
        <span data-lang="en">{art['title'][:80]}</span>
        <span data-lang="fr" style="display:none">{fr_art.get('title',art['title'])[:80]}</span>
        <span data-lang="es" style="display:none">{es_art.get('title',art['title'])[:80]}</span>
        <span data-lang="it" style="display:none">{it_art.get('title',art['title'])[:80]}</span>
        <span data-lang="de" style="display:none">{de_art.get('title',art['title'])[:80]}</span>
      </h3>
      <p class="card-text" style="font-size:14px">
        <span data-lang="en">{art.get('meta_description','')[:120]}</span>
        <span data-lang="fr" style="display:none">{fr_art.get('meta_description','')[:120]}</span>
        <span data-lang="es" style="display:none">{es_art.get('meta_description','')[:120]}</span>
        <span data-lang="it" style="display:none">{it_art.get('meta_description','')[:120]}</span>
        <span data-lang="de" style="display:none">{de_art.get('meta_description','')[:120]}</span>
      </p>
      <span class="btn btn-ocean" style="font-size:12px;padding:6px 16px">
        <span data-lang="en">Read More</span>
        <span data-lang="fr" style="display:none">Lire la suite</span>
        <span data-lang="es" style="display:none">Leer más</span>
        <span data-lang="it" style="display:none">Leggi di più</span>
        <span data-lang="de" style="display:none">Weiterlesen</span>
      </span>
    </div>
  </a>"""

# Pre-compute category buttons (backslash-free)
_cat_buttons = ""
for c in strategy["categories"]:
    slug = c["slug"]
    name = c["name"]
    _cat_buttons += '<button class="btn btn-secondary" onclick="filterCat(' + chr(39) + slug + chr(39) + ')" id="cat-' + slug + '" style="font-size:13px;padding:8px 20px">' + name + '</button>'

blog_index = head("Blog | Ngor Surfcamp Teranga","Surf guides, tips and stories from Ngor Island, Dakar, Senegal.") + nav("blog") + f"""
<div class="page-header" style="background-image:url('{IMGS['hero_blog']}')">
  <h1>{multilang({"en":"Surf Blog","fr":"Blog Surf","es":"Blog Surf","it":"Blog Surf","de":"Surf-Blog"})}</h1>
  <p>{multilang({"en":"Guides, tips and stories from Ngor Island","fr":"Guides, conseils et histoires de l'Île de Ngor","es":"Guías, consejos e historias de la Isla de Ngor","it":"Guide, consigli e storie dall'Isola di Ngor","de":"Guides, Tipps und Geschichten von Ngor Island"})}</p>
</div>

<!-- Category filter -->
<section class="section-sm" style="background:var(--light-bg)">
  <div class="container">
    <div style="display:flex;gap:12px;flex-wrap:wrap;align-items:center;justify-content:center">
      <button class="btn btn-ocean" onclick="filterCat('all')" id="cat-all" style="font-size:13px;padding:8px 20px">{multilang({"en":"All Articles","fr":"Tous les articles","es":"Todos los artículos","it":"Tutti gli articoli","de":"Alle Artikel"})}</button>
      {_cat_buttons}
    </div>
  </div>
</section>

<section class="section reveal">
  <div class="container">
    <div class="grid-3" id="blog-grid">{blog_cards}</div>
  </div>
</section>
""" + footer() + f"""
<script>
function filterCat(cat) {{
  // Simple category filter based on card content
  document.querySelectorAll('#cat-all, [id^="cat-"]').forEach(b => b.className = 'btn btn-secondary');
  document.getElementById('cat-'+cat).className = 'btn btn-ocean';
  document.querySelectorAll('#blog-grid .card').forEach(card => {{
    const catEl = card.querySelector('.blog-category');
    if(!catEl) return;
    const catText = catEl.textContent.trim();
    const catSlug = catText.toLowerCase().replace(/[^a-z0-9]/g,'-').replace(/-+/g,'-');
    if(cat === 'all' || catSlug.includes(cat) || cat.includes(catSlug.substring(0,6))) {{
      card.style.display = '';
    }} else {{
      card.style.display = 'none';
    }}
  }});
}}
</script>
""" + close_page()

with open(f"{DEMO_DIR}/blog/index.html","w") as f:
    f.write(blog_index)
print("✅ Blog listing page written")

# ════════════════════════════════════════════════════════════════════════════════
# BUILD INDIVIDUAL BLOG ARTICLE PAGES
# ════════════════════════════════════════════════════════════════════════════════
print(f"Building {len(all_articles_en)} blog article pages...")

def md_to_html(md):
    """Simple markdown to HTML converter."""
    html = []
    lines = md.split('\n')
    in_ul = False
    for line in lines:
        line = line.strip()
        if not line:
            if in_ul: html.append('</ul>'); in_ul = False
            continue
        if line.startswith('## '):
            if in_ul: html.append('</ul>'); in_ul = False
            html.append(f'<h2>{line[3:]}</h2>')
        elif line.startswith('# '):
            if in_ul: html.append('</ul>'); in_ul = False
            html.append(f'<h1>{line[2:]}</h1>')
        elif line.startswith('### '):
            if in_ul: html.append('</ul>'); in_ul = False
            html.append(f'<h3>{line[4:]}</h3>')
        elif line.startswith('- ') or line.startswith('* '):
            if not in_ul: html.append('<ul>'); in_ul = True
            content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line[2:])
            content = re.sub(r'\[LINK:.*?\]', '', content)
            html.append(f'<li>{content}</li>')
        elif line.startswith('**') and line.endswith('**'):
            if in_ul: html.append('</ul>'); in_ul = False
            html.append(f'<h4 style="margin:20px 0 8px;color:var(--navy)">{line.strip("*")}</h4>')
        else:
            if in_ul: html.append('</ul>'); in_ul = False
            content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line)
            content = re.sub(r'\[LINK:.*?\]', '', content)
            if content:
                html.append(f'<p>{content}</p>')
    if in_ul: html.append('</ul>')
    return '\n'.join(html)

for art in all_articles_en:
    slug = art["slug"]
    fr_art = load(f"{ARTICLES}/fr/{slug}.json") or {}
    es_art = load(f"{ARTICLES}/es/{slug}.json") or {}
    it_art = load(f"{ARTICLES}/it/{slug}.json") or {}
    de_art = load(f"{ARTICLES}/de/{slug}.json") or {}

    img_src = f"/assets/images/{slug}.png" if os.path.exists(f"{DEMO_DIR}/assets/images/{slug}.png") else IMGS["hero_blog"]

    # Pre-compute lang switcher buttons (no backslash in f-string)
    _lang_btns = ""
    for _l in LANGS:
        _lang_btns += '<button onclick="setLang(' + chr(39) + _l + chr(39) + ')" style="padding:6px 14px;border:1px solid var(--border);border-radius:20px;background:none;cursor:pointer;font-size:13px" title="' + LANG_NAMES[_l] + '">' + LANG_FLAGS[_l] + ' ' + LANG_NAMES[_l] + '</button>'

    def art_content(a):
        return md_to_html(a.get("content_markdown",""))

    article_page = head(
        art.get("meta_description","")[:60] or art["title"],
        art.get("meta_description","")
    ) + nav("blog") + f"""
<article>
  <!-- Hero image -->
  <div style="height:60vh;min-height:400px;background-image:url('{img_src}');background-size:cover;background-position:center;display:flex;align-items:flex-end;padding-bottom:40px" 
       onerror="this.style.backgroundImage='url({IMGS['hero_blog']})'">
    <div style="background:linear-gradient(transparent,rgba(10,37,64,0.85));width:100%;padding:40px 24px">
      <div style="max-width:760px;margin:0 auto;color:white">
        <span class="blog-category" style="background:rgba(255,255,255,0.2);color:white">{art.get('category','')}</span>
        <h1 style="font-size:clamp(24px,4vw,48px);margin-top:8px;text-shadow:0 2px 10px rgba(0,0,0,0.3)">
          <span data-lang="en">{art['title']}</span>
          <span data-lang="fr" style="display:none">{fr_art.get('title',art['title'])}</span>
          <span data-lang="es" style="display:none">{es_art.get('title',art['title'])}</span>
          <span data-lang="it" style="display:none">{it_art.get('title',art['title'])}</span>
          <span data-lang="de" style="display:none">{de_art.get('title',art['title'])}</span>
        </h1>
      </div>
    </div>
  </div>

  <section class="section">
    <div class="container">
      <div class="article-content">
        <!-- Language switcher reminder -->
        <div style="display:flex;gap:8px;margin-bottom:32px;flex-wrap:wrap">
          {_lang_btns}
        </div>

        <!-- Article body per language -->
        <div data-lang="en">{art_content(art)}</div>
        <div data-lang="fr" style="display:none">{art_content(fr_art) if fr_art else art_content(art)}</div>
        <div data-lang="es" style="display:none">{art_content(es_art) if es_art else art_content(art)}</div>
        <div data-lang="it" style="display:none">{art_content(it_art) if it_art else art_content(art)}</div>
        <div data-lang="de" style="display:none">{art_content(de_art) if de_art else art_content(art)}</div>

        <!-- CTA -->
        <div style="margin:48px 0;padding:32px;background:linear-gradient(135deg,var(--navy),var(--blue));border-radius:var(--radius);text-align:center;color:white">
          <h3 style="margin-bottom:12px">{multilang({"en":"Ready to Ride? Book Your Stay","fr":"Prêt à Surfer ? Réservez","es":"¿Listo para Surfear? Reserva","it":"Pronto a Surfare? Prenota","de":"Bereit zum Surfen? Buche jetzt"})}</h3>
          <p style="opacity:0.85;margin-bottom:20px">{multilang({"en":"Ngor Surfcamp Teranga — Ngor Island, Dakar, Senegal","fr":"Ngor Surfcamp Teranga — Île de Ngor, Dakar, Sénégal","es":"Ngor Surfcamp Teranga — Isla de Ngor, Dakar, Senegal","it":"Ngor Surfcamp Teranga — Isola di Ngor, Dakar, Senegal","de":"Ngor Surfcamp Teranga — Ngor Island, Dakar, Senegal"})}</p>
          <div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap">
            <a href="/booking.html" class="btn btn-primary">{multilang({"en":"Book Now","fr":"Réserver","es":"Reservar","it":"Prenota","de":"Buchen"})}</a>
            <a href="https://wa.me/221789257025" target="_blank" class="btn btn-outline">WhatsApp</a>
          </div>
        </div>

        <!-- Back to blog -->
        <a href="/blog/" style="display:inline-flex;align-items:center;gap:8px;color:var(--blue);font-weight:600">
          ← <span data-lang="en">Back to Blog</span>
          <span data-lang="fr" style="display:none">Retour au Blog</span>
          <span data-lang="es" style="display:none">Volver al Blog</span>
          <span data-lang="it" style="display:none">Torna al Blog</span>
          <span data-lang="de" style="display:none">Zurück zum Blog</span>
        </a>
      </div>
    </div>
  </section>
</article>
""" + footer() + close_page()

    with open(f"{DEMO_DIR}/blog/{slug}.html","w") as f:
        f.write(article_page)

print(f"✅ {len(all_articles_en)} blog article pages written")

# ════════════════════════════════════════════════════════════════════════════════
# COUNT OUTPUT FILES
# ════════════════════════════════════════════════════════════════════════════════
html_files = []
for root, dirs, files in os.walk(DEMO_DIR):
    for f in files:
        if f.endswith('.html'):
            html_files.append(os.path.join(root,f))

print(f"\n{'='*60}")
print(f"CLOUDFLARE SITE BUILD COMPLETE")
print(f"{'='*60}")
print(f"  HTML pages: {len(html_files)}")
print(f"  CSS: 1 file")
print(f"  Worker: _worker.js (auth: simon/simon)")
print(f"  Output: {DEMO_DIR}")
print(f"  Ready to deploy with: wrangler pages deploy")
