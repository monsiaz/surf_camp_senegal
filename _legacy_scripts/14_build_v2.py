"""
Build Cloudflare site v2:
- Liquid glass DA with 3-color palette (navy / sand / fire)
- Surf-themed SVG icons
- Proper multilingual URLs: /fr/, /es/, /it/, /de/
- Full hreflang on every page
- H1/H2/H3 SEO hierarchy enforced
- Optimized meta per page per lang
- Internal linking / maillage
- Responsive + article content formatting
"""
import json, os, re, shutil

CONTENT   = "/Users/simonazoulay/SurfCampSenegal/content"
ARTICLES  = f"{CONTENT}/articles"
PAGES_DIR = f"{CONTENT}/pages"
DEMO_DIR  = "/Users/simonazoulay/SurfCampSenegal/cloudflare-demo"
IMAGES_V2 = f"{CONTENT}/images_v2"
SITE_URL  = "https://ngor-surfcamp-demo.pages.dev"

LANGS = ["en", "fr", "es", "it", "de"]
LANG_NAMES  = {"en": "English",   "fr": "Français", "es": "Español",  "it": "Italiano", "de": "Deutsch"}
LANG_FLAGS  = {"en": "🇬🇧",        "fr": "🇫🇷",        "es": "🇪🇸",        "it": "🇮🇹",        "de": "🇩🇪"}
LANG_LOCALE = {"en": "en",        "fr": "fr-FR",     "es": "es-ES",     "it": "it-IT",     "de": "de-DE"}

# URL prefixes: en = root, others = /xx/
LANG_PREFIX = {"en": "", "fr": "/fr", "es": "/es", "it": "/it", "de": "/de"}

PAGE_SLUGS = {
    "home":       "",
    "surf-house": "/surf-house",
    "island":     "/island",
    "surfing":    "/surfing",
    "booking":    "/booking",
    "gallery":    "/gallery",
    "faq":        "/faq",
    "blog":       "/blog",
}

def load(path):
    if os.path.exists(path):
        try:
            with open(path) as f: return json.load(f)
        except: return None
    return None

def save_html(rel_path, html):
    full = DEMO_DIR + rel_path
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(html)

def load_page(lang, page_key):
    names = {
        "home": "homepage", "surf-house": "surf_house",
        "island": "island", "surfing": "surfing",
        "booking": "book_online", "gallery": "gallery", "faq": "faq"
    }
    n = names.get(page_key, page_key)
    return load(f"{PAGES_DIR}/{lang}_{n}.json") or {}

# ── Load articles ─────────────────────────────────────────────────────────────
strategy = load(f"{CONTENT}/blog_strategy.json")
cats     = strategy["categories"]
arts_en  = []
for fname in sorted(os.listdir(f"{ARTICLES}/en")):
    if fname.endswith(".json"):
        a = load(f"{ARTICLES}/en/{fname}")
        if a and a.get("slug"): arts_en.append(a)

arts_by_lang = {}
for lang in LANGS:
    arts_by_lang[lang] = {}
    lang_dir = f"{ARTICLES}/{lang}"
    if os.path.exists(lang_dir):
        for fname in os.listdir(lang_dir):
            if fname.endswith(".json") and not fname.startswith("_"):
                a = load(f"{lang_dir}/{fname}")
                if a and a.get("original_en_slug" if lang != "en" else "slug"):
                    key = a.get("original_en_slug", a.get("slug",""))
                    arts_by_lang[lang][key] = a
        if lang == "en":
            for a in arts_en:
                arts_by_lang["en"][a["slug"]] = a

print(f"Articles: { {l: len(arts_by_lang[l]) for l in LANGS} }")

# ══════════════════════════════════════════════════════════════════════════════
# DESIGN SYSTEM
# ══════════════════════════════════════════════════════════════════════════════

# ── SVG Icons (surf-themed) ───────────────────────────────────────────────────
ICONS = {
    "wave": '<svg viewBox="0 0 40 20" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M0 14 C5 8, 10 4, 15 8 C20 12, 25 16, 30 10 C35 4, 38 8, 40 6 L40 20 L0 20 Z" fill="currentColor" opacity="0.8"/><path d="M0 18 C8 12, 14 16, 20 14 C26 12, 32 8, 40 12 L40 20 L0 20 Z" fill="currentColor"/></svg>',
    "surfboard": '<svg viewBox="0 0 24 48" fill="none" xmlns="http://www.w3.org/2000/svg"><ellipse cx="12" cy="20" rx="6" ry="18" fill="currentColor" rx="3"/><rect x="10" y="36" width="4" height="6" rx="2" fill="currentColor" opacity="0.6"/></svg>',
    "location": '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z" fill="currentColor"/><circle cx="12" cy="9" r="2.5" fill="white"/></svg>',
    "calendar": '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="3" y="4" width="18" height="17" rx="3" stroke="currentColor" stroke-width="2" fill="none"/><path d="M3 9h18" stroke="currentColor" stroke-width="2"/><path d="M8 2v3M16 2v3" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><circle cx="8" cy="14" r="1.5" fill="currentColor"/><circle cx="12" cy="14" r="1.5" fill="currentColor"/><circle cx="16" cy="14" r="1.5" fill="currentColor"/></svg>',
    "star": '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M12 2l2.4 7.4H22l-6.2 4.5 2.4 7.4L12 17l-6.2 4.3 2.4-7.4L2 9.4h7.6z" fill="currentColor"/></svg>',
    "check": '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="12" r="10" fill="currentColor" opacity="0.15"/><path d="M7 12l4 4 6-7" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "arrow": '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "coach": '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="7" r="4" stroke="currentColor" stroke-width="2" fill="none"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" fill="none"/><path d="M16 11l4 2-4 2" fill="currentColor" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/></svg>',
    "video": '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="2" y="5" width="15" height="14" rx="3" stroke="currentColor" stroke-width="2" fill="none"/><path d="M17 9l5-3v12l-5-3V9z" fill="currentColor"/></svg>',
    "food": '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 2C7 2 3 6 3 11c0 3 1.5 5.5 4 7v3h10v-3c2.5-1.5 4-4 4-7 0-5-4-9-9-9z" stroke="currentColor" stroke-width="2" fill="none"/><path d="M9 15h6M10 11h4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>',
    "pool": '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M2 16c2-2 4-2 6 0s4 2 6 0 4-2 6 0" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><path d="M2 12c2-2 4-2 6 0s4 2 6 0 4-2 6 0" stroke="currentColor" stroke-width="2" stroke-linecap="round" opacity="0.5"/><rect x="8" y="3" width="3" height="7" rx="1.5" fill="currentColor" opacity="0.7"/><rect x="13" y="3" width="3" height="7" rx="1.5" fill="currentColor" opacity="0.7"/></svg>',
    "wifi": '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M1 7C5 3 10 1 12 1s7 2 11 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" fill="none"/><path d="M5 11c2-2 4-3 7-3s5 1 7 3" stroke="currentColor" stroke-width="2" stroke-linecap="round" fill="none"/><path d="M8.5 14.5c1-1 2.2-1.5 3.5-1.5s2.5.5 3.5 1.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" fill="none"/><circle cx="12" cy="18" r="1.5" fill="currentColor"/></svg>',
    "transfer": '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M3 12c0-5 3-8 6-8l9 0" stroke="currentColor" stroke-width="2" stroke-linecap="round" fill="none"/><path d="M14 8l4 4-4 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M3 17c1 2 3 3 5 3h4" stroke="currentColor" stroke-width="2" stroke-linecap="round" fill="none"/></svg>',
    "whatsapp": '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" fill="currentColor"/></svg>',
    "instagram": '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z" fill="currentColor"/></svg>',
    "tiktok": '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M19.59 6.69a4.83 4.83 0 01-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 01-2.88 2.5 2.89 2.89 0 01-2.89-2.89 2.89 2.89 0 012.89-2.89c.28 0 .54.04.79.1V9.01a6.28 6.28 0 00-.79-.05 6.34 6.34 0 00-6.34 6.34 6.34 6.34 0 006.34 6.34 6.34 6.34 0 006.33-6.34V8.69a8.22 8.22 0 004.84 1.56V6.79a4.85 4.85 0 01-1.07-.1z" fill="currentColor"/></svg>',
    "menu": '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M3 7h18M3 12h18M3 17h12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
    "close": '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
    "chevron": '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M6 9l6 6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "sun": '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="12" r="5" stroke="currentColor" stroke-width="2" fill="none"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
    "blog": '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="3" y="3" width="18" height="18" rx="3" stroke="currentColor" stroke-width="2" fill="none"/><path d="M7 8h10M7 12h10M7 16h6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
}

def icon(name, size=20, cls=""):
    svg = ICONS.get(name, "")
    return f'<span class="icon {cls}" style="width:{size}px;height:{size}px;display:inline-flex;align-items:center;justify-content:center;flex-shrink:0">{svg}</span>'

# ── Multilang helper ──────────────────────────────────────────────────────────
def ml(texts, default_key="en"):
    """Render multilang spans."""
    parts = []
    for l in LANGS:
        text = texts.get(l, texts.get(default_key, ""))
        style = "" if l == "en" else ' style="display:none"'
        parts.append(f'<span data-lang="{l}"{style}>{text}</span>')
    return "".join(parts)

# ── Image URLs ────────────────────────────────────────────────────────────────
WIX   = "https://static.wixstatic.com/media"
LOGO  = f"{WIX}/c2467f_a31779010ce34c4c8c61cc5868d81f31~mv2.png"
IMGS  = {
    "home":      f"{WIX}/df99f9_da0cf7c72b1a4606bcfa1f7c8e089dc4f000.jpg",
    "house":     f"{WIX}/df99f9_2ec6248367cd4e21a5e6c26c2b0a1c35~mv2.jpg",
    "island":    f"{WIX}/df99f9_56b9af6efe2841eea44109b3b08b7da1~mv2.jpg",
    "surf":      f"{WIX}/11062b_89a070321f814742a620b190592d51ad~mv2.jpg",
    "house2":    f"{WIX}/df99f9_eba4c24ec6a746b58d60a975b8d20946~mv2.jpg",
    "house3":    f"{WIX}/df99f9_d8e77cf4807249f6953119f18be64166~mv2.jpg",
    "island2":   f"{WIX}/b28af82dbec544138f16e2bc5a85f2cb.jpg",
    "ngor_right":f"{WIX}/11062b_7f89d2db0ace4027ac4a00928a6aca08~mv2.jpg",
    "surf2":     f"{WIX}/df99f9_dd89cc4d86d4402189d7e9516ce672a3~mv2.jpg",
    "surf3":     f"{WIX}/df99f9_961b0768e713457f93025f4ce6fb1419~mv2.jpg",
    "food":      f"{WIX}/df99f9_753890483d8e4cca8e2051a13f9c558e~mv2.jpg",
    "pool":      f"{WIX}/df99f9_a18d512828d9487e9a4987b9903960e0~mv2.jpg",
    "sunset":    f"{WIX}/df99f9_d6e404dd3cf74396b6ea874cb7021a27~mv2.jpg",
    "art":       f"{WIX}/df99f9_d81668a18a9d49d1b5ebb0ea3a0abbc7~mv2.jpg",
    "review":    f"{WIX}/11062b_772a661c20f742c7baca38ad28c5f7fc~mv2.jpeg",
    "gallery": [
        f"{WIX}/df99f9_16fcc19c812d49a9a05e361aacdc9cea~mv2.jpg",
        f"{WIX}/df99f9_25cc88706ffb42debadac4787bab4f02~mv2.jpg",
        f"{WIX}/df99f9_6a9de50280094c06b4bb439b5d0a7ca7~mv2.jpg",
        f"{WIX}/df99f9_bb61f8a278004fccb5f55351a772472c~mv2.jpg",
        f"{WIX}/df99f9_6fae936c12864930a0e7413cdccf6fd0~mv2.jpeg",
        f"{WIX}/df99f9_27471c09c19d473896e650316f2a0622~mv2.jpg",
        f"{WIX}/df99f9_42ff8407b442474fa5d54253fac98133~mv2.jpg",
        f"{WIX}/df99f9_64a5d28bf1d94191ad2fa45af7de6782~mv2.jpg",
        f"{WIX}/df99f9_0d4a03baee4f46b68bc1aa085ed28e35~mv2.jpg",
        f"{WIX}/df99f9_796b6115065145eabddfe3ae32b8f4d5~mv2.jpg",
        f"{WIX}/df99f9_81e322c4e48d4bcbb444c6535daed131~mv2.jpg",
        f"{WIX}/df99f9_bde010e1296b478cbbe4f885c2714338~mv2.jpg",
    ],
}

# ════════════════════════════════════════════════════════════════════════════════
# CSS v2 — Liquid Glass + 3 Color System
# ════════════════════════════════════════════════════════════════════════════════
CSS_V2 = """
@import url('https://fonts.googleapis.com/css2?family=Raleway:wght@300;400;500;600;700;800;900&family=Inter:wght@300;400;500;600&display=swap');

/* ── 3-Color System ─────────────────────────────────────────────────────── */
:root {
  /* Primary: Deep Ocean Navy */
  --deep:      #0a2540;
  --deep-90:   rgba(10, 37, 64, 0.9);
  --deep-75:   rgba(10, 37, 64, 0.75);
  --deep-50:   rgba(10, 37, 64, 0.5);
  --deep-20:   rgba(10, 37, 64, 0.2);
  --deep-10:   rgba(10, 37, 64, 0.1);

  /* Secondary: Warm Sand */
  --sand:      #f0d6a4;
  --sand-dark: #c8a96e;
  --sand-light:#fdf4e3;

  /* Accent: Sunset Fire */
  --fire:      #ff6b35;
  --fire-dark: #e05a28;
  --fire-light:rgba(255, 107, 53, 0.15);

  /* Glass system */
  --glass-bg:      rgba(255, 255, 255, 0.07);
  --glass-bg-mid:  rgba(255, 255, 255, 0.12);
  --glass-bg-high: rgba(255, 255, 255, 0.18);
  --glass-border:  rgba(255, 255, 255, 0.14);
  --glass-shine:   rgba(255, 255, 255, 0.08);
  --glass-shadow:  0 8px 32px rgba(10, 37, 64, 0.22), inset 0 1px 0 rgba(255,255,255,0.1);

  /* Typography */
  --font-display: 'Raleway', sans-serif;
  --font-body:    'Inter', -apple-system, sans-serif;

  /* Layout */
  --max-w:  1240px;
  --radius: 16px;
  --radius-sm: 10px;
  --radius-pill: 50px;

  /* Transitions */
  --ease: cubic-bezier(0.4, 0, 0.2, 1);
  --t:    0.3s var(--ease);
}

/* ── Reset ──────────────────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; -webkit-text-size-adjust: 100%; }
body {
  font-family: var(--font-body);
  color: var(--deep);
  line-height: 1.7;
  background: #fff;
  overflow-x: hidden;
}
img { max-width: 100%; height: auto; display: block; }
a { color: inherit; text-decoration: none; }
h1,h2,h3,h4,h5,h6 {
  font-family: var(--font-display);
  font-weight: 700;
  line-height: 1.15;
  letter-spacing: -0.025em;
}
button { cursor: pointer; border: none; background: none; font-family: inherit; }

/* ── Liquid Glass Utility ───────────────────────────────────────────────── */
.glass {
  background: var(--glass-bg);
  backdrop-filter: blur(24px) saturate(180%);
  -webkit-backdrop-filter: blur(24px) saturate(180%);
  border: 1px solid var(--glass-border);
  box-shadow: var(--glass-shadow);
}
.glass-mid {
  background: var(--glass-bg-mid);
  backdrop-filter: blur(20px) saturate(160%);
  -webkit-backdrop-filter: blur(20px) saturate(160%);
  border: 1px solid rgba(255,255,255,0.18);
  box-shadow: 0 4px 24px rgba(10,37,64,0.15), inset 0 1px 0 rgba(255,255,255,0.15);
}
.glass-dark {
  background: rgba(10, 37, 64, 0.72);
  backdrop-filter: blur(24px) saturate(180%);
  -webkit-backdrop-filter: blur(24px) saturate(180%);
  border: 1px solid rgba(255,255,255,0.1);
}

/* ── Navigation ─────────────────────────────────────────────────────────── */
#nav {
  position: fixed; top: 0; left: 0; right: 0; z-index: 200;
  background: rgba(10, 37, 64, 0.82);
  backdrop-filter: blur(28px) saturate(200%);
  -webkit-backdrop-filter: blur(28px) saturate(200%);
  border-bottom: 1px solid rgba(255,255,255,0.08);
  transition: background var(--t), border-color var(--t);
}
#nav.scrolled {
  background: rgba(10, 37, 64, 0.95);
  border-color: rgba(255,255,255,0.12);
}
.nav-inner {
  max-width: var(--max-w);
  margin: 0 auto;
  padding: 0 24px;
  height: 68px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}
.nav-logo img { height: 44px; width: auto; }
.nav-links {
  display: flex;
  align-items: center;
  gap: 2px;
  flex: 1;
  justify-content: center;
}
.nav-link {
  color: rgba(255,255,255,0.82);
  padding: 7px 13px;
  border-radius: var(--radius-sm);
  font-size: 13.5px;
  font-weight: 500;
  transition: var(--t);
  white-space: nowrap;
  position: relative;
}
.nav-link:hover { color: #fff; background: rgba(255,255,255,0.1); }
.nav-link.active {
  color: #fff;
  background: rgba(255,255,255,0.1);
}
.nav-link.nav-cta {
  background: var(--fire);
  color: #fff;
  font-weight: 700;
  padding: 8px 18px;
  border-radius: var(--radius-pill);
  font-size: 13px;
  letter-spacing: 0.02em;
}
.nav-link.nav-cta:hover { background: var(--fire-dark); transform: translateY(-1px); }

.nav-right { display: flex; align-items: center; gap: 10px; }

/* Language selector */
.lang-picker {
  position: relative;
}
.lang-picker select {
  appearance: none;
  background: var(--glass-bg-mid);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid var(--glass-border);
  color: #fff;
  padding: 7px 30px 7px 10px;
  border-radius: var(--radius-sm);
  font-size: 13px;
  cursor: pointer;
  outline: none;
  font-family: var(--font-body);
}
.lang-picker::after {
  content: '▾';
  position: absolute; right: 10px; top: 50%;
  transform: translateY(-50%);
  color: rgba(255,255,255,0.6);
  pointer-events: none;
  font-size: 10px;
}
.lang-picker select option { background: var(--deep); }

/* WhatsApp nav button */
.nav-wa {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 8px 14px;
  border-radius: var(--radius-pill);
  background: #25D366;
  color: #fff;
  font-size: 13px;
  font-weight: 700;
  transition: var(--t);
}
.nav-wa:hover { background: #1da851; transform: translateY(-1px); }
.nav-wa .icon { color: #fff; }
.nav-wa .wa-label { display: none; }
@media (min-width: 1100px) { .nav-wa .wa-label { display: inline; } }

/* Mobile toggle */
.nav-toggle {
  width: 38px; height: 38px;
  border-radius: var(--radius-sm);
  background: var(--glass-bg-mid);
  border: 1px solid var(--glass-border);
  display: none;
  align-items: center;
  justify-content: center;
  color: #fff;
}
.nav-toggle .icon { color: #fff; }

/* ── Hero ────────────────────────────────────────────────────────────────── */
.hero {
  position: relative;
  min-height: 100vh;
  display: flex; align-items: center; justify-content: center;
  background-size: cover; background-position: center;
  background-attachment: fixed;
  text-align: center; padding: 100px 24px 80px;
  overflow: hidden;
}
.hero::before {
  content: '';
  position: absolute; inset: 0; z-index: 1;
  background: linear-gradient(
    170deg,
    rgba(10,37,64,0.72) 0%,
    rgba(10,37,64,0.45) 50%,
    rgba(0,0,0,0.6) 100%
  );
}
.hero-grain {
  position: absolute; inset: 0; z-index: 1;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E");
  opacity: 0.5;
}
.hero-content {
  position: relative; z-index: 2;
  max-width: 820px;
}
.hero-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 16px;
  border-radius: var(--radius-pill);
  background: rgba(255,107,53,0.2);
  border: 1px solid rgba(255,107,53,0.35);
  color: var(--sand);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  margin-bottom: 20px;
  backdrop-filter: blur(10px);
}
.hero-h1 {
  font-size: clamp(38px, 6.5vw, 80px);
  color: #fff;
  font-weight: 900;
  margin-bottom: 20px;
  text-shadow: 0 2px 30px rgba(0,0,0,0.25);
  letter-spacing: -0.03em;
}
.hero-sub {
  font-size: clamp(16px, 2.2vw, 22px);
  color: rgba(255,255,255,0.87);
  margin-bottom: 40px;
  font-weight: 300;
  line-height: 1.6;
}
.hero-cta { display: flex; gap: 14px; justify-content: center; flex-wrap: wrap; }

/* Wave divider */
.wave-divider {
  position: absolute; bottom: -2px; left: 0; right: 0; z-index: 3;
  line-height: 0;
}
.wave-divider svg { width: 100%; height: 60px; }

/* ── Buttons ─────────────────────────────────────────────────────────────── */
.btn {
  display: inline-flex;
  align-items: center; gap: 8px;
  padding: 13px 28px;
  border-radius: var(--radius-pill);
  font-family: var(--font-display);
  font-weight: 700; font-size: 14px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  transition: var(--t);
  position: relative;
  overflow: hidden;
  border: none;
}
.btn::after {
  content: '';
  position: absolute; inset: 0;
  background: radial-gradient(circle at 50% 0%, rgba(255,255,255,0.25) 0%, transparent 60%);
  opacity: 0;
  transition: opacity var(--t);
}
.btn:hover::after { opacity: 1; }

.btn-fire { background: var(--fire); color: #fff; }
.btn-fire:hover { background: var(--fire-dark); transform: translateY(-2px); box-shadow: 0 8px 24px rgba(255,107,53,0.4); }

.btn-deep { background: var(--deep); color: #fff; }
.btn-deep:hover { background: #0d3060; transform: translateY(-2px); box-shadow: 0 8px 20px var(--deep-20); }

.btn-glass {
  background: var(--glass-bg-mid);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  color: #fff;
  border: 1px solid var(--glass-border);
}
.btn-glass:hover { background: var(--glass-bg-high); transform: translateY(-2px); }

.btn-sand { background: var(--sand); color: var(--deep); }
.btn-sand:hover { background: var(--sand-dark); color: #fff; transform: translateY(-2px); }

.btn-outline-fire { background: transparent; color: var(--fire); border: 2px solid var(--fire); }
.btn-outline-fire:hover { background: var(--fire); color: #fff; }

.btn-wa { background: #25D366; color: #fff; }
.btn-wa:hover { background: #1da851; transform: translateY(-2px); box-shadow: 0 8px 20px rgba(37,211,102,0.35); }

.btn-sm { padding: 8px 18px; font-size: 12px; }
.btn-lg { padding: 16px 36px; font-size: 15px; }

/* ── Layout ──────────────────────────────────────────────────────────────── */
.container { max-width: var(--max-w); margin: 0 auto; padding: 0 24px; }
.container-sm { max-width: 800px; margin: 0 auto; padding: 0 24px; }
.section { padding: 96px 0; }
.section-sm { padding: 64px 0; }

/* Section labels */
.s-label {
  display: inline-flex; align-items: center; gap: 8px;
  font-size: 11px; font-weight: 700; letter-spacing: 0.16em;
  text-transform: uppercase; color: var(--fire);
  margin-bottom: 14px;
}
.s-label::before {
  content: '';
  width: 24px; height: 2px;
  background: var(--fire);
  border-radius: 2px;
  display: inline-block;
}
.s-title { font-size: clamp(28px, 4vw, 48px); margin-bottom: 16px; }
.s-sub { font-size: 18px; color: #4b5563; max-width: 580px; line-height: 1.7; }

/* Dark section */
.sec-dark {
  background: var(--deep);
  color: #fff;
}
.sec-dark .s-sub { color: rgba(255,255,255,0.7); }

/* Sand section */
.sec-sand { background: var(--sand-light); }

/* ── Cards ────────────────────────────────────────────────────────────────── */
.card {
  border-radius: var(--radius);
  overflow: hidden;
  background: #fff;
  box-shadow: 0 2px 20px var(--deep-10);
  transition: var(--t);
}
.card:hover { transform: translateY(-6px); box-shadow: 0 16px 48px var(--deep-20); }

.card-glass {
  border-radius: var(--radius);
  overflow: hidden;
  background: var(--glass-bg-mid);
  backdrop-filter: blur(20px) saturate(160%);
  -webkit-backdrop-filter: blur(20px) saturate(160%);
  border: 1px solid var(--glass-border);
  box-shadow: var(--glass-shadow);
  transition: var(--t);
}
.card-glass:hover { background: var(--glass-bg-high); transform: translateY(-4px); }

.card-img { width: 100%; aspect-ratio: 16/10; object-fit: cover; }
.card-body { padding: 24px; }
.card-tag {
  font-size: 11px; font-weight: 700; letter-spacing: 0.1em;
  text-transform: uppercase; color: var(--fire); margin-bottom: 10px;
}
.card-h3 { font-size: 19px; margin-bottom: 10px; line-height: 1.3; }
.card-text { font-size: 14.5px; color: #6b7280; line-height: 1.65; }

/* ── Feature list ────────────────────────────────────────────────────────── */
.feat {
  display: flex; gap: 16px; align-items: flex-start;
  padding: 20px; border-radius: var(--radius-sm);
  background: rgba(10,37,64,0.03);
  transition: background var(--t);
}
.feat:hover { background: rgba(10,37,64,0.06); }
.feat-icon {
  width: 48px; height: 48px; flex-shrink: 0;
  border-radius: 14px;
  background: linear-gradient(135deg, var(--deep), #1a4a7a);
  display: flex; align-items: center; justify-content: center;
  color: var(--sand);
}
.feat-icon .icon { color: var(--sand); }
.feat-title { font-size: 16px; font-weight: 700; margin-bottom: 5px; }
.feat-text { font-size: 14px; color: #6b7280; line-height: 1.6; }

/* ── Grid ────────────────────────────────────────────────────────────────── */
.grid-2 { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 28px; }
.grid-3 { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 24px; }
.grid-4 { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }

/* Split 50/50 */
.split { display: grid; grid-template-columns: 1fr 1fr; gap: 80px; align-items: center; }
.split-img { border-radius: var(--radius); overflow: hidden; }
.split-img img { width: 100%; height: 440px; object-fit: cover; }

/* ── Stats bar ───────────────────────────────────────────────────────────── */
.stats { padding: 56px 0; background: var(--deep); color: #fff; }
.stats-inner { display: flex; justify-content: center; flex-wrap: wrap; gap: 56px; }
.stat { text-align: center; }
.stat-n { font-size: clamp(40px, 5vw, 60px); font-weight: 900; color: var(--sand); font-family: var(--font-display); display: block; }
.stat-l { font-size: 12px; letter-spacing: 0.12em; text-transform: uppercase; opacity: 0.7; }

/* ── Testimonial ─────────────────────────────────────────────────────────── */
.testimonial {
  padding: 36px 40px;
  border-radius: var(--radius);
  background: #fff;
  border-left: 4px solid var(--fire);
  box-shadow: 0 4px 24px var(--deep-10);
  position: relative;
}
.testimonial::before {
  content: '"';
  position: absolute; top: 16px; left: 36px;
  font-size: 80px; line-height: 1; font-family: Georgia, serif;
  color: var(--fire); opacity: 0.2;
}
.testimonial-text { font-size: 18px; font-style: italic; line-height: 1.75; margin-bottom: 20px; position: relative; z-index: 1; }
.testimonial-author { font-weight: 700; font-size: 15px; }
.testimonial-role { font-size: 13px; color: #9ca3af; }

/* ── Gallery ─────────────────────────────────────────────────────────────── */
.gallery-masonry {
  columns: 3 280px;
  column-gap: 16px;
}
.gallery-item {
  break-inside: avoid;
  margin-bottom: 16px;
  border-radius: var(--radius-sm);
  overflow: hidden;
  cursor: pointer;
  position: relative;
}
.gallery-item img { width: 100%; display: block; transition: transform 0.5s var(--ease); }
.gallery-item::after {
  content: '';
  position: absolute; inset: 0;
  background: linear-gradient(transparent 60%, rgba(10,37,64,0.5));
  opacity: 0; transition: opacity 0.3s;
}
.gallery-item:hover img { transform: scale(1.04); }
.gallery-item:hover::after { opacity: 1; }

/* Lightbox */
#lb {
  display: none; position: fixed; inset: 0; z-index: 1000;
  background: rgba(0,0,0,0.92);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  align-items: center; justify-content: center;
  cursor: pointer;
}
#lb.open { display: flex; }
#lb img { max-width: 90vw; max-height: 90vh; border-radius: var(--radius); object-fit: contain; cursor: default; box-shadow: 0 32px 80px rgba(0,0,0,0.5); }
#lb-close {
  position: absolute; top: 20px; right: 20px;
  width: 44px; height: 44px; border-radius: 50%;
  background: rgba(255,255,255,0.15); color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 20px; cursor: pointer; transition: background var(--t);
}
#lb-close:hover { background: rgba(255,255,255,0.25); }

/* ── FAQ ─────────────────────────────────────────────────────────────────── */
.faq-item {
  border: 1px solid rgba(10,37,64,0.1);
  border-radius: var(--radius-sm);
  overflow: hidden;
  margin-bottom: 10px;
  transition: box-shadow var(--t);
}
.faq-item:hover { box-shadow: 0 4px 16px var(--deep-10); }
.faq-q {
  width: 100%; text-align: left;
  padding: 20px 24px;
  display: flex; align-items: center; justify-content: space-between; gap: 16px;
  font-weight: 600; font-size: 16px; color: var(--deep);
  background: #fff; transition: background var(--t);
}
.faq-q:hover { background: var(--sand-light); }
.faq-arrow { color: var(--fire); flex-shrink: 0; transition: transform 0.25s var(--ease); }
.faq-a { padding: 0 24px 20px; color: #4b5563; line-height: 1.75; font-size: 15px; }
.faq-item.open .faq-arrow { transform: rotate(180deg); }
.faq-item.closed .faq-a { display: none; }

/* ── Blog ────────────────────────────────────────────────────────────────── */
.blog-cat-badge {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 5px 13px; border-radius: var(--radius-pill);
  background: var(--fire-light);
  color: var(--fire-dark);
  font-size: 11.5px; font-weight: 700;
  letter-spacing: 0.04em;
}
.blog-card-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 28px; }

/* Article content */
.article-hero {
  position: relative; min-height: 70vh;
  background-size: cover; background-position: center;
  display: flex; align-items: flex-end;
  padding-bottom: 0;
  overflow: hidden;
}
.article-hero::before {
  content: '';
  position: absolute; inset: 0;
  background: linear-gradient(transparent 20%, rgba(10,37,64,0.88) 100%);
}
.article-hero-content {
  position: relative; z-index: 1;
  padding: 48px;
  width: 100%;
  max-width: 900px;
  margin: 0 auto;
  color: #fff;
}
.article-meta { font-size: 13px; opacity: 0.7; margin-bottom: 12px; }

.prose { max-width: 720px; margin: 0 auto; }
.prose h1 { font-size: clamp(28px, 4vw, 44px); margin-bottom: 28px; color: var(--deep); }
.prose h2 {
  font-size: clamp(22px, 3vw, 30px);
  margin: 52px 0 18px;
  color: var(--deep);
  padding-bottom: 10px;
  border-bottom: 2px solid var(--sand);
}
.prose h3 { font-size: clamp(18px, 2.5vw, 22px); margin: 32px 0 12px; color: var(--deep); }
.prose h4 { font-size: 17px; margin: 24px 0 10px; color: var(--deep); font-weight: 700; }
.prose p { font-size: 17px; line-height: 1.82; color: #374151; margin-bottom: 22px; }
.prose ul, .prose ol { margin: 16px 0 24px 20px; }
.prose li { font-size: 16px; line-height: 1.7; color: #374151; margin-bottom: 10px; }
.prose li::marker { color: var(--fire); }
.prose strong { color: var(--deep); font-weight: 700; }
.prose em { color: #6b7280; }
.prose blockquote {
  border-left: 4px solid var(--fire);
  padding: 16px 24px;
  margin: 32px 0;
  background: var(--sand-light);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  font-style: italic;
}
.prose a { color: var(--fire); border-bottom: 1px solid var(--fire-light); transition: var(--t); }
.prose a:hover { color: var(--fire-dark); border-color: var(--fire); }

/* Internal link badges */
.ilink {
  display: inline-flex; align-items: center; gap: 6px;
  color: var(--fire) !important; font-weight: 600;
  border-bottom: none !important;
}

/* Article CTA box */
.article-cta {
  margin: 56px 0;
  padding: 40px;
  border-radius: var(--radius);
  background: linear-gradient(135deg, var(--deep), #1a4a7a);
  color: #fff;
  text-align: center;
  position: relative;
  overflow: hidden;
}
.article-cta::before {
  content: '';
  position: absolute; inset: 0;
  background: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 80' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0 60 C40 40, 80 50, 120 40 C160 30, 180 50, 200 40 L200 80 L0 80Z' fill='rgba(255,255,255,0.04)'/%3E%3C/svg%3E") bottom center;
  background-size: 100% auto;
  background-repeat: no-repeat;
}

/* ── Booking form ────────────────────────────────────────────────────────── */
.form-card {
  background: #fff;
  border-radius: var(--radius);
  padding: 40px;
  box-shadow: 0 4px 32px var(--deep-10);
}
.form-group { margin-bottom: 20px; }
.form-label { display: block; font-weight: 600; font-size: 13.5px; margin-bottom: 7px; color: var(--deep); }
.form-input, .form-select, .form-textarea {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e5e7eb;
  border-radius: var(--radius-sm);
  font-family: var(--font-body); font-size: 15px;
  color: var(--deep);
  transition: var(--t);
  outline: none;
  background: #fff;
}
.form-input:focus, .form-select:focus, .form-textarea:focus {
  border-color: var(--fire);
  box-shadow: 0 0 0 3px var(--fire-light);
}
.form-textarea { resize: vertical; min-height: 90px; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
.form-check { display: flex; align-items: center; gap: 10px; cursor: pointer; }
.form-check input { accent-color: var(--fire); width: 17px; height: 17px; }

/* ── Page header (non-hero) ──────────────────────────────────────────────── */
.page-header {
  padding: 140px 24px 80px;
  background: var(--deep);
  color: #fff;
  text-align: center;
  background-size: cover;
  background-position: center;
  position: relative;
  overflow: hidden;
}
.page-header::before {
  content: '';
  position: absolute; inset: 0;
  background: linear-gradient(rgba(10,37,64,0.65), rgba(10,37,64,0.85));
}
.page-header > * { position: relative; z-index: 1; }
.page-header h1 { font-size: clamp(32px, 5vw, 60px); margin-bottom: 14px; }
.page-header p { font-size: 18px; opacity: 0.85; max-width: 560px; margin: 0 auto; }

/* ── CTA Banner ──────────────────────────────────────────────────────────── */
.cta-band {
  padding: 96px 0;
  background: var(--deep);
  color: #fff;
  text-align: center;
  position: relative;
  overflow: hidden;
}
.cta-band::before {
  content: '';
  position: absolute; inset: 0;
  background: radial-gradient(ellipse at 50% 100%, rgba(255,107,53,0.18) 0%, transparent 60%);
}
.cta-band h2 { font-size: clamp(28px, 4vw, 48px); margin-bottom: 14px; position: relative; z-index: 1; }
.cta-band p { font-size: 18px; opacity: 0.82; max-width: 520px; margin: 0 auto 40px; position: relative; z-index: 1; line-height: 1.7; }
.cta-band .cta-btns { display: flex; gap: 14px; justify-content: center; flex-wrap: wrap; position: relative; z-index: 1; }

/* ── Footer ──────────────────────────────────────────────────────────────── */
footer {
  background: var(--deep);
  color: #fff;
  padding: 72px 0 32px;
  border-top: 1px solid rgba(255,255,255,0.06);
}
.footer-grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: 48px;
  margin-bottom: 56px;
}
.footer-brand img { height: 48px; margin-bottom: 18px; }
.footer-brand p { font-size: 14px; opacity: 0.65; line-height: 1.75; max-width: 260px; }

.footer-col h4 {
  font-size: 12px; font-weight: 700; letter-spacing: 0.12em;
  text-transform: uppercase; color: var(--sand);
  margin-bottom: 18px;
}
.footer-col a {
  display: block; font-size: 14px;
  color: rgba(255,255,255,0.65);
  margin-bottom: 10px; transition: color var(--t);
}
.footer-col a:hover { color: #fff; }

.footer-social { display: flex; gap: 10px; margin-top: 20px; }
.social-btn {
  width: 42px; height: 42px; border-radius: 12px;
  background: rgba(255,255,255,0.09);
  border: 1px solid rgba(255,255,255,0.1);
  display: flex; align-items: center; justify-content: center;
  color: rgba(255,255,255,0.75);
  transition: var(--t);
}
.social-btn:hover { background: rgba(255,255,255,0.18); color: #fff; transform: translateY(-2px); }
.social-btn.wa-btn:hover { background: #25D366; border-color: transparent; }
.social-btn.ig-btn:hover { background: linear-gradient(135deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888); border-color: transparent; }
.social-btn.tt-btn:hover { background: #010101; border-color: transparent; }

.footer-bottom {
  border-top: 1px solid rgba(255,255,255,0.07);
  padding-top: 28px;
  display: flex; align-items: center; justify-content: space-between;
  flex-wrap: wrap; gap: 14px;
}
.footer-bottom p { font-size: 13px; color: rgba(255,255,255,0.45); }
.footer-bottom .hreflang-links a {
  font-size: 12px; color: rgba(255,255,255,0.4);
  margin-left: 14px; transition: color var(--t);
}
.footer-bottom .hreflang-links a:hover { color: rgba(255,255,255,0.7); }

/* ── Scroll reveal ───────────────────────────────────────────────────────── */
.reveal { opacity: 0; transform: translateY(28px); transition: opacity 0.65s var(--ease), transform 0.65s var(--ease); }
.reveal.up { opacity: 1; transform: none; }

/* ── Responsive ──────────────────────────────────────────────────────────── */
@media (max-width: 1024px) {
  .footer-grid { grid-template-columns: 1fr 1fr; }
  .split { grid-template-columns: 1fr; gap: 40px; }
  .split-img img { height: 300px; }
}

@media (max-width: 768px) {
  .nav-links { display: none; flex-direction: column; position: fixed; top: 68px; left: 0; right: 0; padding: 20px; background: rgba(10,37,64,0.97); border-bottom: 1px solid rgba(255,255,255,0.1); }
  .nav-links.open { display: flex; }
  .nav-toggle { display: flex; }
  .nav-wa .wa-label { display: none; }
  .hero { background-attachment: scroll; }
  .stats-inner { gap: 32px; }
  .form-row { grid-template-columns: 1fr; }
  .footer-grid { grid-template-columns: 1fr; gap: 32px; }
  .gallery-masonry { columns: 2 180px; }
  .article-hero-content { padding: 24px; }
  .form-card { padding: 24px; }
}

@media (max-width: 480px) {
  .hero-cta { flex-direction: column; align-items: stretch; }
  .btn { justify-content: center; }
  .cta-btns { flex-direction: column; align-items: center; }
  .gallery-masonry { columns: 1; }
  .testimonial { padding: 24px; }
}

/* ── Language-specific URL indicator ────────────────────────────────────── */
.lang-url-bar {
  background: rgba(240, 214, 164, 0.15);
  border-bottom: 1px solid rgba(240, 214, 164, 0.25);
  padding: 6px 0;
  text-align: center;
  font-size: 12px;
  color: rgba(255,255,255,0.6);
  display: flex; align-items: center; justify-content: center; gap: 8px;
}
.lang-url-bar a { color: var(--sand); }
"""

# Write CSS v2
with open(f"{DEMO_DIR}/assets/css/style.css", "w") as f:
    f.write(CSS_V2)
print("✅ CSS v2 written")

# ════════════════════════════════════════════════════════════════════════════════
# TEMPLATE HELPERS
# ════════════════════════════════════════════════════════════════════════════════

def hreflang_tags(page_slug, lang_prefix_map=None):
    """Generate hreflang link tags for a page in all languages."""
    tags = []
    slug = page_slug.strip("/")
    if slug: slug = "/" + slug
    # x-default and en
    tags.append(f'<link rel="alternate" hreflang="x-default" href="{SITE_URL}{slug}/">')
    tags.append(f'<link rel="alternate" hreflang="en" href="{SITE_URL}{slug}/">')
    for l in ["fr","es","it","de"]:
        tags.append(f'<link rel="alternate" hreflang="{LANG_LOCALE[l]}" href="{SITE_URL}/{l}{slug}/">')
    return "\n  ".join(tags)

def canonical(page_slug, lang="en"):
    slug = page_slug.strip("/")
    if slug: slug = "/" + slug
    if lang == "en":
        return f'<link rel="canonical" href="{SITE_URL}{slug}/">'
    else:
        return f'<link rel="canonical" href="{SITE_URL}/{lang}{slug}/">'

I18N_JS = """<script>
const LANGS = ['en','fr','es','it','de'];
function getLang(){ return localStorage.getItem('ngor_lang') || document.documentElement.lang || 'en'; }
function setLang(l){
  if(!LANGS.includes(l)) return;
  localStorage.setItem('ngor_lang', l);
  document.documentElement.lang = l;
  document.querySelectorAll('[data-lang]').forEach(el => {
    el.style.display = el.getAttribute('data-lang') === l ? '' : 'none';
  });
  const sel = document.getElementById('lang-sel');
  if(sel) sel.value = l;
}
document.addEventListener('DOMContentLoaded', () => {
  const stored = localStorage.getItem('ngor_lang');
  const pageLang = document.documentElement.lang || 'en';
  const lang = stored || pageLang;
  setLang(lang);
  const sel = document.getElementById('lang-sel');
  if(sel){ sel.value = lang; sel.addEventListener('change', e => setLang(e.target.value)); }
  // Scroll reveal
  const obs = new IntersectionObserver(entries => entries.forEach(e => { if(e.isIntersecting) e.target.classList.add('up'); }), {threshold:0.1});
  document.querySelectorAll('.reveal').forEach(el => obs.observe(el));
  // Nav scroll
  const nav = document.getElementById('nav');
  if(nav){ window.addEventListener('scroll', () => nav.classList.toggle('scrolled', scrollY > 40)); }
  // FAQ
  document.querySelectorAll('.faq-q').forEach(q => q.addEventListener('click', () => {
    const item = q.closest('.faq-item');
    item.classList.toggle('open'); item.classList.toggle('closed');
  }));
  // Lightbox
  document.querySelectorAll('.gallery-item').forEach(item => {
    item.addEventListener('click', () => {
      const lb = document.getElementById('lb');
      const img = document.getElementById('lb-img');
      if(lb && img){ img.src = item.querySelector('img').src; lb.classList.add('open'); }
    });
  });
  const lb = document.getElementById('lb');
  const lbClose = document.getElementById('lb-close');
  if(lb){ lb.addEventListener('click', e => { if(e.target === lb) lb.classList.remove('open'); }); }
  if(lbClose){ lbClose.addEventListener('click', () => lb.classList.remove('open')); }
  // Mobile nav
  document.getElementById('nav-toggle')?.addEventListener('click', () => {
    document.getElementById('nav-links').classList.toggle('open');
  });
  // Form → WhatsApp
  document.getElementById('booking-form')?.addEventListener('submit', function(e){
    e.preventDefault();
    const fname = this.querySelector('.f-name')?.value || '';
    const dates = this.querySelector('.f-dates')?.value || '';
    const level = this.querySelector('.f-level')?.value || '';
    const msg = encodeURIComponent('Hello Ngor Surfcamp! My name is ' + fname + '. ' + (dates ? 'Dates: ' + dates + '. ' : '') + (level ? 'Level: ' + level + '.' : ''));
    window.open('https://wa.me/221789257025?text=' + msg, '_blank');
  });
});
function toggleMenu(){ document.getElementById('nav-links').classList.toggle('open'); }
</script>"""

def head(title, meta_desc, canonical_url="", hreflang="", lang="en"):
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{meta_desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{meta_desc}">
<meta property="og:type" content="website">
<meta property="og:image" content="{IMGS['home']}">
<meta name="robots" content="index, follow">
{canonical_url}
{hreflang}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Raleway:wght@300;400;500;600;700;800;900&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/css/style.css">
</head>
<body>"""

def nav_html(active="", lang="en", lang_prefix=""):
    NAV_ITEMS = [
        ("", "Home", {"fr":"Accueil","es":"Inicio","it":"Home","de":"Start"}),
        ("/surf-house", "Surf House", {}),
        ("/island", "Island", {"fr":"Île","es":"Isla","it":"Isola","de":"Insel"}),
        ("/surfing", "Surfing", {"fr":"Surf","es":"Surf","it":"Surf","de":"Surfen"}),
        ("/blog", "Blog", {}),
        ("/gallery", "Gallery", {"fr":"Galerie","es":"Galería","it":"Galleria","de":"Galerie"}),
        ("/booking", "Book Now", {"fr":"Réserver","es":"Reservar","it":"Prenota","de":"Buchen"}),
    ]

    items_html = ""
    for slug, en_label, other in NAV_ITEMS:
        label = other.get(lang, en_label) if lang != "en" else en_label
        href  = f"{lang_prefix}{slug}/"
        cls   = "nav-link"
        if slug.strip("/") == active.strip("/") or (not slug and not active):
            cls += " active"
        if slug == "/booking":
            cls += " nav-cta"
        items_html += f'<a href="{href}" class="{cls}">{label}</a>\n'

    # Language selector options
    opts = "".join([f'<option value="{l}" {"selected" if l==lang else ""}>{LANG_FLAGS[l]} {LANG_NAMES[l]}</option>' for l in LANGS])

    return f"""<nav id="nav">
  <div class="nav-inner">
    <a href="{lang_prefix}/" class="nav-logo">
      <img src="{LOGO}" alt="Ngor Surfcamp Teranga" width="140" height="44">
    </a>
    <div class="nav-links" id="nav-links">
      {items_html}
    </div>
    <div class="nav-right">
      <div class="lang-picker">
        <select id="lang-sel" aria-label="Language">
          {opts}
        </select>
      </div>
      <a href="https://wa.me/221789257025" target="_blank" rel="noopener" class="nav-wa" aria-label="WhatsApp">
        {icon("whatsapp", 18)}
        <span class="wa-label">WhatsApp</span>
      </a>
      <button class="nav-toggle" id="nav-toggle" aria-label="Menu" onclick="toggleMenu()">
        {icon("menu", 22)}
      </button>
    </div>
  </div>
</nav>"""

def footer_html(lang="en", lang_prefix=""):
    PAGES_LINKS = [
        ("/surf-house", {"en":"Surf House","fr":"Surf House","es":"Surf House","it":"Surf House","de":"Surf House"}),
        ("/island",     {"en":"Island","fr":"Île","es":"Isla","it":"Isola","de":"Insel"}),
        ("/surfing",    {"en":"Surfing","fr":"Surf","es":"Surf","it":"Surf","de":"Surfen"}),
        ("/blog",       {"en":"Blog","fr":"Blog","es":"Blog","it":"Blog","de":"Blog"}),
        ("/gallery",    {"en":"Gallery","fr":"Galerie","es":"Galería","it":"Galleria","de":"Galerie"}),
        ("/faq",        {"en":"FAQ","fr":"FAQ","es":"FAQ","it":"FAQ","de":"FAQ"}),
        ("/booking",    {"en":"Book Now","fr":"Réserver","es":"Reservar","it":"Prenota","de":"Buchen"}),
    ]
    page_links_html = "\n".join([
        f'<a href="{lang_prefix}{s}/">{labels.get(lang, labels["en"])}</a>'
        for s, labels in PAGES_LINKS
    ])

    lang_links_html = " ".join([
        f'<a href="{"" if l == "en" else "/" + l}/" hreflang="{LANG_LOCALE[l]}">{LANG_FLAGS[l]} {l.upper()}</a>'
        for l in LANGS
    ])

    FOOTER_TEXTS = {
        "about": {"en":"Premium surf camp on Ngor Island, Dakar, Senegal. All levels welcome. Licensed by the Senegalese Federation of Surfing.",
                  "fr":"Surf camp premium sur l'île de Ngor, Dakar, Sénégal. Tous niveaux. Agréé par la Fédération Sénégalaise de Surf.",
                  "es":"Surf camp premium en la isla de Ngor, Dakar, Senegal. Todos los niveles. Licenciado por la Federación Senegalesa de Surf.",
                  "it":"Surf camp premium sull'isola di Ngor, Dakar, Senegal. Tutti i livelli. Autorizzato dalla Federazione Senegalese di Surf.",
                  "de":"Premium Surfcamp auf Ngor Island, Dakar, Senegal. Alle Level willkommen. Lizenziert vom senegalesischen Surfverband."},
        "explore": {"en":"Explore","fr":"Explorer","es":"Explorar","it":"Esplora","de":"Erkunden"},
        "contact": {"en":"Contact","fr":"Contact","es":"Contacto","it":"Contatti","de":"Kontakt"},
        "follow":  {"en":"Follow Us","fr":"Nous suivre","es":"Síguenos","it":"Seguici","de":"Folgen"},
        "copy":    {"en":"© 2025 Ngor Surfcamp Teranga. All rights reserved.","fr":"© 2025 Ngor Surfcamp Teranga. Tous droits réservés.",
                    "es":"© 2025 Ngor Surfcamp Teranga. Todos los derechos reservados.","it":"© 2025 Ngor Surfcamp Teranga. Tutti i diritti riservati.",
                    "de":"© 2025 Ngor Surfcamp Teranga. Alle Rechte vorbehalten."},
    }

    return f"""<footer>
  <div class="container">
    <div class="footer-grid">
      <div class="footer-brand">
        <img src="{LOGO}" alt="Ngor Surfcamp Teranga" width="130" height="42">
        <p>{FOOTER_TEXTS['about'][lang]}</p>
        <div class="footer-social">
          <a href="https://wa.me/221789257025" target="_blank" rel="noopener" class="social-btn wa-btn" title="WhatsApp" aria-label="WhatsApp">{icon("whatsapp",18)}</a>
          <a href="https://www.instagram.com/ngorsurfcampteranga" target="_blank" rel="noopener" class="social-btn ig-btn" title="Instagram" aria-label="Instagram">{icon("instagram",18)}</a>
          <a href="https://www.tiktok.com/@ngorsurfcampteranga" target="_blank" rel="noopener" class="social-btn tt-btn" title="TikTok" aria-label="TikTok">{icon("tiktok",18)}</a>
        </div>
      </div>
      <div class="footer-col">
        <h4>{FOOTER_TEXTS['explore'][lang]}</h4>
        {page_links_html}
      </div>
      <div class="footer-col">
        <h4>{FOOTER_TEXTS['contact'][lang]}</h4>
        <a href="https://wa.me/221789257025" target="_blank">WhatsApp: +221 78 925 70 25</a>
        <a href="mailto:info@surfcampsenegal.com">info@surfcampsenegal.com</a>
        <a href="{lang_prefix}/booking/">
          {"Book your stay" if lang=="en" else "Réserver votre séjour" if lang=="fr" else "Reservar" if lang=="es" else "Prenota" if lang=="it" else "Jetzt buchen"}
        </a>
      </div>
      <div class="footer-col">
        <h4>{FOOTER_TEXTS['follow'][lang]}</h4>
        <a href="https://www.instagram.com/ngorsurfcampteranga" target="_blank" rel="noopener">Instagram</a>
        <a href="https://www.tiktok.com/@ngorsurfcampteranga" target="_blank" rel="noopener">TikTok</a>
        <a href="https://wa.me/221789257025" target="_blank" rel="noopener">WhatsApp</a>
      </div>
    </div>
    <div class="footer-bottom">
      <p>{FOOTER_TEXTS['copy'][lang]}</p>
      <div class="hreflang-links" aria-label="Language versions">
        {lang_links_html}
      </div>
    </div>
  </div>
</footer>"""

def close():
    return f"\n{I18N_JS}\n</body>\n</html>"

# ════════════════════════════════════════════════════════════════════════════════
# ARTICLE MARKDOWN → HTML
# ════════════════════════════════════════════════════════════════════════════════
def md2html(md):
    if not md: return ""
    lines = md.split("\n")
    html  = []
    in_ul = in_ol = False

    def close_lists():
        nonlocal in_ul, in_ol
        if in_ul: html.append("</ul>"); in_ul = False
        if in_ol: html.append("</ol>"); in_ol = False

    def process_inline(text):
        # Bold
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'__(.*?)__', r'<strong>\1</strong>', text)
        # Italic
        text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
        # Internal link patterns: [LINK: text → /slug]
        def ilink_replace(m):
            parts = m.group(0).replace("[LINK:","").replace("]","").split("→")
            anchor = parts[0].strip()
            target_slug = parts[1].strip() if len(parts) > 1 else "#"
            return f'<a href="{target_slug}/" class="ilink">{icon("arrow",14)} {anchor}</a>'
        text = re.sub(r'\[LINK:[^\]]+\]', ilink_replace, text)
        return text

    for line in lines:
        stripped = line.strip()
        if not stripped:
            close_lists()
            continue
        if stripped.startswith("### "):
            close_lists(); html.append(f"<h3>{process_inline(stripped[4:])}</h3>")
        elif stripped.startswith("## "):
            close_lists(); html.append(f"<h2>{process_inline(stripped[3:])}</h2>")
        elif stripped.startswith("# "):
            close_lists(); html.append(f"<h1>{process_inline(stripped[2:])}</h1>")
        elif stripped.startswith("#### "):
            close_lists(); html.append(f"<h4>{process_inline(stripped[5:])}</h4>")
        elif re.match(r'^[-*]\s', stripped):
            if not in_ul: html.append("<ul>"); in_ul = True
            if in_ol: html.append("</ol>"); in_ol = False
            html.append(f"<li>{process_inline(stripped[2:])}</li>")
        elif re.match(r'^\d+\.\s', stripped):
            if not in_ol: html.append("<ol>"); in_ol = True
            if in_ul: html.append("</ul>"); in_ul = False
            item_text = re.sub(r'^\d+\.\s', '', stripped)
            html.append(f"<li>{process_inline(item_text)}</li>")
        elif stripped.startswith("**") and stripped.endswith("**") and stripped.count("**") == 2:
            close_lists()
            html.append(f"<h4>{process_inline(stripped.strip('*'))}</h4>")
        elif stripped.startswith(">"):
            close_lists()
            html.append(f"<blockquote><p>{process_inline(stripped[1:].strip())}</p></blockquote>")
        elif stripped.startswith("---") or stripped.startswith("==="):
            close_lists()
        else:
            close_lists()
            p = process_inline(stripped)
            if p: html.append(f"<p>{p}</p>")

    close_lists()
    return "\n".join(html)

# ════════════════════════════════════════════════════════════════════════════════
# BUILD PAGES FOR EVERY LANGUAGE
# ════════════════════════════════════════════════════════════════════════════════

def art_img(slug):
    local = f"/assets/images/{slug}.png"
    if os.path.exists(f"{DEMO_DIR}{local}"):
        return local
    return IMGS["surf3"]

# We build one function per page type that takes (lang) and returns HTML
# Then we call it for all 5 languages and save to the right path

def build_homepage(lang):
    pfx  = LANG_PREFIX[lang]
    p    = load_page(lang, "home") or {}
    data = {
        "title":  p.get("title_tag", "Surf Camp Senegal | Ngor Surfcamp Teranga"),
        "meta":   p.get("meta_description", "Premium surf camp on Ngor Island, Dakar, Senegal. Professional coaching. All levels."),
        "h1":     p.get("h1", "Ngor Surfcamp Teranga"),
        "sub":    p.get("hero_subtitle", "Premium Surfcamp in Senegal"),
        "intro":  p.get("intro",""),
    }
    sections = p.get("sections",[])

    # Featured 3 articles in this lang
    art_cards = ""
    lang_arts = arts_by_lang.get(lang, {})
    lang_en   = arts_by_lang.get("en", {})
    sample_slugs = [a["slug"] for a in arts_en[:3]]
    for en_slug in sample_slugs:
        en_art = lang_en.get(en_slug, {})
        if lang == "en":
            art = en_art
        else:
            art = lang_arts.get(en_slug, en_art)
        if not art: continue
        title = art.get("title","")
        meta  = art.get("meta_description","")[:120]
        cat   = en_art.get("category","")
        img   = art_img(en_slug)
        art_url = f"{pfx}/blog/{en_slug}/"
        art_cards += f"""
    <a href="{art_url}" class="card" style="text-decoration:none">
      <img src="{img}" alt="{title}" class="card-img" loading="lazy" onerror="this.src='{IMGS['surf3']}'">
      <div class="card-body">
        <span class="blog-cat-badge">{cat}</span>
        <h3 class="card-h3" style="margin-top:10px">{title[:80]}</h3>
        <p class="card-text">{meta}</p>
        <span class="btn btn-fire btn-sm" style="margin-top:14px">{"Read More" if lang=="en" else "Lire" if lang=="fr" else "Leer" if lang=="es" else "Leggi" if lang=="it" else "Lesen"}</span>
      </div>
    </a>"""

    FEAT_CARDS = [
        (IMGS["house2"], f"{pfx}/surf-house/",
         {"en":"The Surf House","fr":"La Surf House","es":"La Surf House","it":"La Surf House","de":"Das Surf House"},
         {"en":"Rooms, pool, sea views, daily meals — your home by the ocean on Ngor Island.",
          "fr":"Chambres, piscine, vue mer, repas quotidiens — votre maison au bord de l'océan.",
          "es":"Habitaciones, piscina, vista al mar, comidas diarias — tu hogar junto al océano.",
          "it":"Camere, piscina, vista mare, pasti quotidiani — la tua casa sull'oceano.",
          "de":"Zimmer, Pool, Meerblick, tägliche Mahlzeiten — Ihr Zuhause am Ozean."}),
        (IMGS["island2"], f"{pfx}/island/",
         {"en":"Ngor Island","fr":"Île de Ngor","es":"Isla de Ngor","it":"Isola di Ngor","de":"Ngor Island"},
         {"en":"No cars, world-class waves, legendary surf history. A tropical gem off Dakar.",
          "fr":"Pas de voitures, vagues de classe mondiale. Un joyau tropical au large de Dakar.",
          "es":"Sin coches, olas de clase mundial. Una joya tropical frente a Dakar.",
          "it":"Niente auto, onde di classe mondiale. Un gioiello tropicale al largo di Dakar.",
          "de":"Keine Autos, weltklasse Wellen. Ein tropisches Juwel vor Dakar."}),
        (IMGS["surf2"], f"{pfx}/surfing/",
         {"en":"Surf Coaching","fr":"Coaching Surf","es":"Coaching Surf","it":"Coaching Surf","de":"Surf-Coaching"},
         {"en":"Professional video analysis coaching. All levels, all year round.",
          "fr":"Coaching avec analyse vidéo. Tous niveaux, toute l'année.",
          "es":"Coaching con análisis de vídeo. Todos los niveles, todo el año.",
          "it":"Coaching con analisi video. Tutti i livelli, tutto l'anno.",
          "de":"Coaching mit Videoanalyse. Alle Level, das ganze Jahr."}),
    ]
    card3 = "".join([f"""<a href="{href}" class="card">
      <img src="{img_url}" alt="{titles[lang]}" class="card-img" loading="lazy">
      <div class="card-body">
        <h3 class="card-h3">{titles.get(lang, titles["en"])}</h3>
        <p class="card-text">{descs.get(lang, descs["en"])}</p>
        <span class="btn btn-deep btn-sm" style="margin-top:14px">
          {"Explore" if lang=="en" else "Explorer" if lang=="fr" else "Explorar" if lang=="es" else "Esplora" if lang=="it" else "Erkunden"}
        </span>
      </div>
    </a>""" for img_url, href, titles, descs in FEAT_CARDS])

    BOOK_TXT = {"en":"Check Availability","fr":"Vérifier disponibilités","es":"Consultar disponibilidad","it":"Controlla disponibilità","de":"Verfügbarkeit prüfen"}
    WA_TXT   = {"en":"WhatsApp","fr":"WhatsApp","es":"WhatsApp","it":"WhatsApp","de":"WhatsApp"}
    DISC_TXT = {"en":"Discover","fr":"Découvrir","es":"Descubrir","it":"Scoprire","de":"Entdecken"}
    BLOG_TXT = {"en":"All Articles","fr":"Tous les articles","es":"Todos los artículos","it":"Tutti gli articoli","de":"Alle Artikel"}
    LAT_TXT  = {"en":"Latest Articles","fr":"Derniers articles","es":"Últimos artículos","it":"Ultimi articoli","de":"Neueste Artikel"}
    INTRO_FALLBACK = {
        "en":"At Ngor Surfcamp Teranga, we offer professional surf coaching tailored to your level — beginner, intermediate or advanced — on Ngor Island, 800m off the coast of Dakar, Senegal.",
        "fr":"Au Ngor Surfcamp Teranga, nous offrons un coaching surf professionnel adapté à votre niveau — débutant, intermédiaire ou avancé — sur l'île de Ngor, à 800m de la côte de Dakar, Sénégal.",
        "es":"En Ngor Surfcamp Teranga ofrecemos coaching surf profesional adaptado a tu nivel — principiante, intermedio o avanzado — en la isla de Ngor, a 800m de la costa de Dakar, Senegal.",
        "it":"Al Ngor Surfcamp Teranga offriamo coaching surf professionale adattato al tuo livello — principiante, intermedio o avanzato — sull'isola di Ngor, a 800m dalla costa di Dakar, Senegal.",
        "de":"Im Ngor Surfcamp Teranga bieten wir professionelles Surfcoaching für Ihr Level — Anfänger, Fortgeschrittene oder Profis — auf Ngor Island, 800m vor der Küste von Dakar, Senegal.",
    }
    intro_text = data["intro"] or INTRO_FALLBACK.get(lang, INTRO_FALLBACK["en"])

    REVIEW_TEXT = {
        "en": "I had an amazing experience at Ngor Surfcamp Teranga. The coaching was top-notch and I felt my surfing improve significantly during my stay.",
        "fr": "Une expérience incroyable au Ngor Surfcamp Teranga. Le coaching était excellent et mes compétences en surf ont vraiment progressé.",
        "es": "Una experiencia increíble en Ngor Surfcamp Teranga. El coaching fue excelente y mis habilidades de surf mejoraron significativamente.",
        "it": "Un'esperienza incredibile al Ngor Surfcamp Teranga. Il coaching era eccellente e le mie abilità nel surf sono migliorate molto.",
        "de": "Eine unglaubliche Erfahrung im Ngor Surfcamp Teranga. Das Coaching war erstklassig und mein Surfen hat sich erheblich verbessert.",
    }

    hrl = hreflang_tags("")
    can = canonical("", lang)
    STAT_LABELS = {
        "waves":   {"en":"Waves","fr":"Vagues","es":"Olas","it":"Onde","de":"Wellen"},
        "levels":  {"en":"All Levels","fr":"Tous Niveaux","es":"Todos Niveles","it":"Tutti i Livelli","de":"Alle Level"},
        "coach":   {"en":"Coaching","fr":"Coaching","es":"Coaching","it":"Coaching","de":"Coaching"},
        "legend":  {"en":"Endless Summer","fr":"Endless Summer","es":"Endless Summer","it":"Endless Summer","de":"Endless Summer"},
    }

    return head(data["title"], data["meta"], can, hrl, lang) + nav_html("", lang, pfx) + f"""

<main>
  <!-- H1 Hero -->
  <section class="hero" style="background-image:url('{IMGS['home']}')" aria-label="Hero">
    <div class="hero-grain"></div>
    <div class="hero-content reveal">
      <div class="hero-eyebrow">
        {icon("wave", 16)}
        {"Ngor Island · Dakar · Senegal" if lang=="en" else "Île de Ngor · Dakar · Sénégal" if lang=="fr" else "Isla de Ngor · Dakar · Senegal" if lang=="es" else "Isola di Ngor · Dakar · Senegal" if lang=="it" else "Ngor Island · Dakar · Senegal"}
      </div>
      <h1 class="hero-h1">{data["h1"]}</h1>
      <p class="hero-sub">{data["sub"]}</p>
      <div class="hero-cta">
        <a href="{pfx}/booking/" class="btn btn-fire btn-lg">{BOOK_TXT[lang]}</a>
        <a href="https://wa.me/221789257025" target="_blank" rel="noopener" class="btn btn-glass btn-lg">
          {icon("whatsapp", 18)} {WA_TXT[lang]}
        </a>
      </div>
    </div>
    <div class="wave-divider">
      <svg viewBox="0 0 1440 60" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none"><path d="M0 30 C360 60 720 0 1080 40 C1260 60 1380 20 1440 30 L1440 60 L0 60 Z" fill="#fff"/></svg>
    </div>
  </section>

  <!-- Stats -->
  <div class="stats" role="region" aria-label="Key stats">
    <div class="stats-inner">
      <div class="stat"><span class="stat-n">3</span><span class="stat-l">{STAT_LABELS["waves"][lang]}</span></div>
      <div class="stat"><span class="stat-n">All</span><span class="stat-l">{STAT_LABELS["levels"][lang]}</span></div>
      <div class="stat"><span class="stat-n">5★</span><span class="stat-l">{STAT_LABELS["coach"][lang]}</span></div>
      <div class="stat"><span class="stat-n">1964</span><span class="stat-l">{STAT_LABELS["legend"][lang]}</span></div>
    </div>
  </div>

  <!-- About -->
  <section class="section" aria-label="About">
    <div class="container">
      <div class="split reveal">
        <div>
          <span class="s-label">{"Premium Surf Camp" if lang=="en" else "Surf Camp Premium" if lang in ["fr","es"] else "Premium Surf Camp"}</span>
          <h2 class="s-title">{sections[0]["h2"] if sections else ("Serious about improving your surfing?" if lang=="en" else "Prêt à progresser en surf ?" if lang=="fr" else "¿En serio sobre mejorar tu surf?" if lang=="es" else "Vuoi migliorare il tuo surf?" if lang=="it" else "Ernsthaft am Surfen verbessern?")}</h2>
          <p class="s-sub" style="margin-bottom:32px">{intro_text[:300]}</p>
          <div style="display:flex;gap:12px;flex-wrap:wrap">
            <a href="{pfx}/surf-house/" class="btn btn-deep">{"Our Surf House" if lang=="en" else "Notre Surf House" if lang=="fr" else "Nuestra Surf House" if lang=="es" else "La Surf House" if lang=="it" else "Unser Surf House"}</a>
            <a href="{pfx}/surfing/" class="btn btn-outline-fire">{"Surf Coaching" if lang=="en" else "Coaching Surf" if lang=="fr" else "Coaching Surf" if lang=="es" else "Coaching Surf" if lang=="it" else "Surf-Coaching"}</a>
          </div>
        </div>
        <div class="split-img">
          <img src="{IMGS['surf2']}" alt="Surf coaching Ngor Island" loading="lazy" width="600" height="440">
        </div>
      </div>
    </div>
  </section>

  <!-- 3 pillars -->
  <section class="section sec-sand" aria-label="{DISC_TXT[lang]}">
    <div class="container">
      <div style="text-align:center;margin-bottom:60px" class="reveal">
        <span class="s-label">{DISC_TXT[lang]}</span>
        <h2 class="s-title">{"Everything at Ngor Surfcamp" if lang=="en" else "Tout à Ngor Surfcamp" if lang=="fr" else "Todo en Ngor Surfcamp" if lang=="es" else "Tutto a Ngor Surfcamp" if lang=="it" else "Alles im Ngor Surfcamp"}</h2>
      </div>
      <div class="grid-3 reveal">{card3}</div>
    </div>
  </section>

  <!-- Testimonial -->
  <section class="section" aria-label="Reviews">
    <div class="container-sm">
      <div class="testimonial reveal">
        <p class="testimonial-text">{REVIEW_TEXT[lang]}</p>
        <div style="display:flex;align-items:center;gap:14px;margin-top:20px">
          <img src="{IMGS['review']}" alt="Marc Lecarpentier" style="width:52px;height:52px;border-radius:50%;object-fit:cover" loading="lazy">
          <div>
            <div class="testimonial-author">Marc Lecarpentier</div>
            <div class="testimonial-role">{"Surfer, France" if lang in ["en","fr"] else "Surfista, Francia" if lang in ["es","it"] else "Surfer, Frankreich"}</div>
          </div>
          <div style="margin-left:auto;display:flex;gap:2px">{"★"*5}</div>
        </div>
      </div>
    </div>
  </section>

  <!-- Blog preview -->
  <section class="section sec-sand" aria-label="Blog">
    <div class="container">
      <div style="display:flex;align-items:flex-end;justify-content:space-between;margin-bottom:48px;flex-wrap:wrap;gap:16px" class="reveal">
        <div>
          <span class="s-label">Blog</span>
          <h2 class="s-title">{LAT_TXT[lang]}</h2>
        </div>
        <a href="{pfx}/blog/" class="btn btn-fire">{BLOG_TXT[lang]}</a>
      </div>
      <div class="blog-card-grid reveal">{art_cards}</div>
    </div>
  </section>

  <!-- CTA band -->
  <div class="cta-band">
    <div class="container">
      <h2>{"Ready to ride? Book your stay" if lang=="en" else "Prêt à surfer ? Réservez votre séjour" if lang=="fr" else "¿Listo para surfear? Reserva tu estancia" if lang=="es" else "Pronto a surfare? Prenota il tuo soggiorno" if lang=="it" else "Bereit zum Surfen? Buche deinen Aufenthalt"}</h2>
      <p>{"Ngor Island, Dakar, Senegal · WhatsApp: +221 78 925 70 25" if lang=="en" else "Île de Ngor, Dakar, Sénégal · WhatsApp : +221 78 925 70 25" if lang=="fr" else "Isla de Ngor, Dakar, Senegal · WhatsApp: +221 78 925 70 25" if lang in ["es","it","de"] else "Ngor Island, Dakar, Senegal · WhatsApp: +221 78 925 70 25"}</p>
      <div class="cta-btns">
        <a href="{pfx}/booking/" class="btn btn-fire btn-lg">{BOOK_TXT[lang]}</a>
        <a href="https://wa.me/221789257025" target="_blank" rel="noopener" class="btn btn-glass btn-lg">{icon("whatsapp",18)} WhatsApp</a>
      </div>
    </div>
  </div>
</main>
""" + footer_html(lang, pfx) + close()

# ── Build article page ────────────────────────────────────────────────────────
def build_article(en_art, lang):
    pfx     = LANG_PREFIX[lang]
    en_slug = en_art["slug"]
    if lang == "en":
        art = en_art
    else:
        art = arts_by_lang[lang].get(en_slug, en_art)

    title    = art.get("title", en_art["title"])
    meta_d   = art.get("meta_description", en_art.get("meta_description",""))[:155]
    content  = md2html(art.get("content_markdown",""))
    cat      = en_art.get("category","")
    img      = art_img(en_slug)
    type_art = en_art.get("type","seo")

    hrl = hreflang_tags(f"/blog/{en_slug}", {})
    can = canonical(f"/blog/{en_slug}", lang)

    # Related articles (2 from same category)
    related = [a for a in arts_en if a.get("category")==cat and a["slug"] != en_slug][:2]
    related_html = ""
    for rel in related:
        rel_art = arts_by_lang[lang].get(rel["slug"], rel)
        rel_title = rel_art.get("title", rel["title"])
        related_html += f"""<a href="{pfx}/blog/{rel['slug']}/" class="card" style="text-decoration:none">
      <img src="{art_img(rel['slug'])}" alt="{rel_title}" class="card-img" loading="lazy" onerror="this.src='{IMGS['surf3']}'">
      <div class="card-body">
        <span class="blog-cat-badge">{rel.get('category','')}</span>
        <h3 class="card-h3" style="font-size:16px;margin-top:8px">{rel_title[:70]}</h3>
      </div>
    </a>"""

    BACK_TXT = {"en":"Back to Blog","fr":"Retour au Blog","es":"Volver al Blog","it":"Torna al Blog","de":"Zurück zum Blog"}
    READ_TXT = {"en":"Related Articles","fr":"Articles liés","es":"Artículos relacionados","it":"Articoli correlati","de":"Verwandte Artikel"}
    BOOK_TXT = {"en":"Book Your Stay","fr":"Réserver","es":"Reservar","it":"Prenota","de":"Buchen"}

    # Language switcher for this article
    lang_switch = " ".join([
        f'<a href="{LANG_PREFIX[l]}/blog/{en_slug}/" class="btn btn-deep btn-sm" style="padding:6px 12px;font-size:11px" hreflang="{LANG_LOCALE[l]}" aria-label="{LANG_NAMES[l]}">{LANG_FLAGS[l]} {l.upper()}</a>'
        for l in LANGS
    ])

    return head(title[:60], meta_d, can, hrl, lang) + nav_html("blog", lang, pfx) + f"""

<main>
  <article itemscope itemtype="https://schema.org/BlogPosting">
    <!-- Article Hero (H1 inside article context) -->
    <header class="article-hero" style="background-image:url('{img}')" itemprop="image" aria-label="{title}">
      <div class="article-hero-content">
        <div class="article-meta">
          <span class="blog-cat-badge">{cat}</span>
          &nbsp; <span itemprop="articleSection">{cat}</span>
        </div>
        <h1 style="font-size:clamp(24px,4vw,52px);margin:12px 0;text-shadow:0 2px 12px rgba(0,0,0,0.3)" itemprop="headline">{title}</h1>
        <div style="font-size:14px;opacity:0.75;margin-top:8px">
          <span itemprop="publisher" itemscope itemtype="https://schema.org/Organization">
            <span itemprop="name">Ngor Surfcamp Teranga</span>
          </span>
        </div>
      </div>
    </header>

    <div class="container" style="padding:48px 24px">
      <!-- Language switcher -->
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:32px;align-items:center">
        <span style="font-size:12px;color:#9ca3af;text-transform:uppercase;letter-spacing:0.08em;margin-right:4px">{"Language:" if lang=="en" else "Langue:" if lang=="fr" else "Idioma:" if lang=="es" else "Lingua:" if lang=="it" else "Sprache:"}</span>
        {lang_switch}
      </div>

      <div class="prose" itemprop="articleBody">
        {content}
      </div>

      <!-- Article CTA -->
      <div class="article-cta" style="position:relative">
        <div style="position:relative;z-index:1">
          <h3 style="font-size:26px;margin-bottom:12px">{"Ready to Ride?" if lang=="en" else "Prêt à Surfer ?" if lang=="fr" else "¿Listo para Surfear?" if lang=="es" else "Pronto a Surfare?" if lang=="it" else "Bereit zum Surfen?"}</h3>
          <p style="opacity:0.85;margin-bottom:28px;max-width:480px;margin-left:auto;margin-right:auto">Ngor Surfcamp Teranga · Ngor Island, Dakar, Senegal</p>
          <div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap">
            <a href="{pfx}/booking/" class="btn btn-fire btn-lg">{BOOK_TXT[lang]}</a>
            <a href="https://wa.me/221789257025" target="_blank" rel="noopener" class="btn btn-glass btn-lg">{icon("whatsapp",18)} WhatsApp</a>
          </div>
        </div>
      </div>

      <!-- Related articles -->
      {"<div style='margin-top:64px'><h2 style='font-size:24px;margin-bottom:28px'>" + READ_TXT[lang] + "</h2><div class='grid-2'>" + related_html + "</div></div>" if related_html else ""}

      <!-- Back to blog -->
      <div style="margin-top:48px">
        <a href="{pfx}/blog/" class="btn btn-deep">
          {icon("arrow", 16, "icon-flip")} {BACK_TXT[lang]}
        </a>
      </div>
    </div>
  </article>
</main>
<style>.icon-flip {{ transform: scaleX(-1); }}</style>
""" + footer_html(lang, pfx) + close()

# ════════════════════════════════════════════════════════════════════════════════
# BUILD BLOG LISTING
# ════════════════════════════════════════════════════════════════════════════════
def build_blog(lang):
    pfx = LANG_PREFIX[lang]
    TITLES = {"en":"Surf Blog","fr":"Blog Surf","es":"Blog Surf","it":"Blog Surf","de":"Surf-Blog"}
    SUBS   = {"en":"Guides, tips and stories from Ngor Island","fr":"Guides, conseils et histoires de l'Île de Ngor","es":"Guías, consejos e historias de la Isla de Ngor","it":"Guide, consigli e storie dall'Isola di Ngor","de":"Guides, Tipps und Geschichten von Ngor Island"}
    ALL    = {"en":"All","fr":"Tous","es":"Todos","it":"Tutti","de":"Alle"}
    META   = {"en":"Surf blog from Ngor Surfcamp Teranga — guides, tips and stories about surfing in Senegal, Ngor Island, Dakar.","fr":"Blog surf du Ngor Surfcamp Teranga — guides, conseils et histoires sur le surf au Sénégal, île de Ngor, Dakar.","es":"Blog surf de Ngor Surfcamp Teranga — guías, consejos e historias sobre el surf en Senegal, isla de Ngor, Dakar.","it":"Blog surf di Ngor Surfcamp Teranga — guide, consigli e storie sul surf in Senegal, isola di Ngor, Dakar.","de":"Surf-Blog von Ngor Surfcamp Teranga — Guides, Tipps und Geschichten über Surfen in Senegal, Ngor Island, Dakar."}

    hrl = hreflang_tags("/blog")
    can = canonical("/blog", lang)

    # Category buttons
    cat_btns = f'<button class="btn btn-fire btn-sm" onclick="filterCat(' + chr(39) + 'all' + chr(39) + ')" id="cat-all">{ALL[lang]}</button>\n'
    for c in cats:
        slug_c = c["slug"]
        name_c = c["name"]
        cat_btns += f'<button class="btn btn-deep btn-sm" onclick="filterCat(' + chr(39) + slug_c + chr(39) + ')" id="cat-' + slug_c + '">' + name_c + '</button>\n'

    # Article cards
    cards_html = ""
    for en_art in arts_en:
        en_slug  = en_art["slug"]
        if lang == "en":
            art = en_art
        else:
            art = arts_by_lang[lang].get(en_slug, en_art)
        title    = art.get("title", en_art["title"])[:80]
        meta_d   = art.get("meta_description", "")[:130]
        cat_name = en_art.get("category","")
        cat_slug = next((c["slug"] for c in cats if c["name"] == cat_name), "misc")
        img      = art_img(en_slug)
        art_url  = f"{pfx}/blog/{en_slug}/"
        feat     = "⭐ " if en_art.get("type")=="hero" else ""

        cards_html += f"""<a href="{art_url}" class="card" data-cat="{cat_slug}" style="text-decoration:none">
      <img src="{img}" alt="{title}" class="card-img" loading="lazy" onerror="this.src='{IMGS['surf3']}'">
      <div class="card-body">
        <span class="blog-cat-badge">{cat_name}</span>
        <h2 class="card-h3" style="font-size:16px;margin:10px 0">{feat}{title}</h2>
        <p class="card-text">{meta_d}</p>
      </div>
    </a>\n"""

    return head(f"Blog | {TITLES[lang]} | Ngor Surfcamp Teranga", META[lang], can, hrl, lang) + nav_html("blog", lang, pfx) + f"""
<main>
  <header class="page-header" style="background-image:url('{IMGS['surf3']}')" role="banner">
    <h1>{TITLES[lang]}</h1>
    <p>{SUBS[lang]}</p>
  </header>

  <!-- Category filter -->
  <div style="background:#f9fafb;padding:20px 0;border-bottom:1px solid #e5e7eb">
    <div class="container" style="display:flex;gap:10px;flex-wrap:wrap;align-items:center">
      {cat_btns}
    </div>
  </div>

  <section class="section" aria-label="Articles">
    <div class="container">
      <div class="blog-card-grid" id="blog-grid">
        {cards_html}
      </div>
    </div>
  </section>
</main>
<script>
function filterCat(cat){{
  document.querySelectorAll('[id^="cat-"]').forEach(b => b.className = 'btn btn-deep btn-sm');
  document.getElementById('cat-' + cat).className = 'btn btn-fire btn-sm';
  document.querySelectorAll('#blog-grid .card').forEach(c => {{
    c.style.display = (cat === 'all' || c.dataset.cat === cat) ? '' : 'none';
  }});
}}
</script>
""" + footer_html(lang, pfx) + close()

# ════════════════════════════════════════════════════════════════════════════════
# WRITE ALL FILES
# ════════════════════════════════════════════════════════════════════════════════
total_files = 0

def write(path, html):
    global total_files
    full = DEMO_DIR + path
    os.makedirs(os.path.dirname(full) if not full.endswith("/") else full, exist_ok=True)
    # Ensure it ends with /index.html
    if full.endswith("/"):
        full += "index.html"
    elif not full.endswith(".html"):
        os.makedirs(full, exist_ok=True)
        full += "/index.html"
    with open(full, "w") as f:
        f.write(html)
    total_files += 1

# Copy new images v2 to demo if they exist
if os.path.exists(IMAGES_V2):
    done = 0
    for fname in os.listdir(IMAGES_V2):
        if fname.endswith(".png"):
            src = f"{IMAGES_V2}/{fname}"
            dst = f"{DEMO_DIR}/assets/images/{fname}"
            if os.path.getsize(src) > 10000:
                shutil.copy2(src, dst); done += 1
    print(f"Copied {done} v2 images")

print("\nBuilding pages for all languages...")

for lang in LANGS:
    pfx  = LANG_PREFIX[lang]
    slug_prefix = f"/{lang}" if lang != "en" else ""

    # Homepage
    write(f"{slug_prefix}/", build_homepage(lang))
    print(f"  ✅ {lang}: /")

    # Blog listing
    write(f"{slug_prefix}/blog/", build_blog(lang))
    print(f"  ✅ {lang}: /blog/")

    # Blog articles
    for en_art in arts_en:
        write(f"{slug_prefix}/blog/{en_art['slug']}/", build_article(en_art, lang))

    print(f"  ✅ {lang}: {len(arts_en)} articles")

print(f"\nTotal HTML files written: {total_files}")

# ════════════════════════════════════════════════════════════════════════════════
# STATIC PAGES (EN only for now, extend as needed)
# ════════════════════════════════════════════════════════════════════════════════
# The surf house / island / surfing / booking / gallery / faq pages
# are kept from the v1 build but now need proper hreflang and lang versions
# We generate them for all languages using the content JSON

def build_simple_page(page_key, lang, hero_img, page_title_en, content_html_fn):
    pfx  = LANG_PREFIX[lang]
    p    = load_page(lang, page_key) or {}
    slug = PAGE_SLUGS.get(page_key, f"/{page_key}")
    hrl  = hreflang_tags(slug)
    can  = canonical(slug, lang)
    title_tag = p.get("title_tag", f"{page_title_en} | Ngor Surfcamp Teranga")
    meta_d    = p.get("meta_description", "")[:155]
    h1        = p.get("h1", page_title_en)
    hero_sub  = p.get("hero_subtitle","")

    return (head(title_tag, meta_d, can, hrl, lang) +
            nav_html(page_key, lang, pfx) +
            f"""<main>
  <header class="page-header" style="background-image:url('{hero_img}')" role="banner">
    <h1>{h1}</h1>
    {"<p>" + hero_sub + "</p>" if hero_sub else ""}
  </header>
  {content_html_fn(lang, p, pfx)}
</main>""" +
            footer_html(lang, pfx) + close())

# Surf House page content
def surf_house_content(lang, p, pfx):
    sections = p.get("sections",[])
    FEATS = [
        ("transfer", {"en":"Surf Transfers","fr":"Transferts surf","es":"Traslados surf","it":"Trasferimenti surf","de":"Surf-Transfers"},
                     {"en":"Boat to Ngor Right & Left. Minibus to Dakar's best spots daily.","fr":"Pirogue vers Ngor Right & Left. Minibus vers les meilleurs spots de Dakar.","es":"Bote a Ngor Right & Left. Minibús a los mejores spots de Dakar.","it":"Barca a Ngor Right & Left. Minibus verso i migliori spot di Dakar.","de":"Boot zu Ngor Right & Left. Minibus zu Dakars besten Spots täglich."}),
        ("food",     {"en":"Breakfast & Dinner","fr":"Petit-déj & Dîner","es":"Desayuno y Cena","it":"Colazione e Cena","de":"Frühstück & Abendessen"},
                     {"en":"Authentic Senegalese meals every day. Filtered water, tea & coffee.","fr":"Plats sénégalais authentiques. Eau filtrée, thé et café inclus.","es":"Comidas senegalesas auténticas. Agua filtrada, té y café incluidos.","it":"Pasti senegalesi autentici ogni giorno. Acqua filtrata, tè e caffè inclusi.","de":"Authentische senegalesische Mahlzeiten täglich. Gefiltertes Wasser, Tee und Kaffee."}),
        ("wave",     {"en":"Daily Surf Guiding","fr":"Guide surf quotidien","es":"Guía surf diario","it":"Guida surf giornaliera","de":"Tägliche Surf-Führung"},
                     {"en":"We guide you to the best spot of the day, every day. All levels.","fr":"Nous vous guidons vers le meilleur spot du jour. Tous niveaux.","es":"Te llevamos al mejor spot del día, todos los días. Todos los niveles.","it":"Ti guidiamo verso il miglior spot del giorno ogni giorno. Tutti i livelli.","de":"Wir führen Sie täglich zum besten Spot. Alle Level willkommen."}),
        ("coach",    {"en":"Surf Theory Classes","fr":"Cours de théorie","es":"Clases de teoría","it":"Lezioni di teoria","de":"Theoriestunden"},
                     {"en":"Free theory sessions: paddling, pop-up, turns and more.","fr":"Sessions théorie gratuites : paddle, pop-up, virages et plus.","es":"Sesiones de teoría gratuitas: remo, pop-up, giros y más.","it":"Sessioni di teoria gratuite: paddling, pop-up, virate e altro.","de":"Kostenlose Theoriestunden: Paddeln, Pop-up, Kurven und mehr."}),
        ("pool",     {"en":"Pool & Common Areas","fr":"Piscine & espaces communs","es":"Piscina & áreas comunes","it":"Piscina & aree comuni","de":"Pool & Gemeinschaftsbereiche"},
                     {"en":"Outdoor pool, terraces and chill spaces in the heart of Ngor Island.","fr":"Piscine extérieure, terrasses et espaces chill au cœur de l'île.","es":"Piscina al aire libre, terrazas y espacios chill en el corazón de la isla.","it":"Piscina esterna, terrazze e spazi relax nel cuore dell'isola.","de":"Außenpool, Terrassen und Chill-Bereiche im Herzen der Insel."}),
        ("wifi",     {"en":"Free Wi-Fi & Daily Cleaning","fr":"Wi-Fi gratuit & ménage quotidien","es":"Wi-Fi gratis y limpieza diaria","it":"Wi-Fi gratuito e pulizia giornaliera","de":"Kostenloses WLAN & tägliche Reinigung"},
                     {"en":"Stay connected, room cleaned daily. Focus on surfing.","fr":"Restez connecté, chambre nettoyée quotidiennement. Concentrez-vous sur le surf.","es":"Mantente conectado, habitación limpia diariamente. Céntrate en el surf.","it":"Rimani connesso, camera pulita quotidianamente. Concentrati sul surf.","de":"Bleiben Sie verbunden, Zimmer täglich gereinigt. Fokus auf Surfen."}),
    ]
    feats_html = "".join([f'<div class="feat reveal"><div class="feat-icon">{icon(ico, 24)}</div><div><div class="feat-title">{t.get(lang,t["en"])}</div><div class="feat-text">{d.get(lang,d["en"])}</div></div></div>' for ico, t, d in FEATS])
    gallery_imgs = [IMGS["house2"], IMGS["house3"], IMGS["food"], IMGS["pool"], IMGS["surf3"], IMGS["island2"]]
    gallery_html = "".join([f'<div class="gallery-item"><img src="{u}" alt="Ngor Surf House" loading="lazy"></div>' for u in gallery_imgs])
    intro_text = p.get("intro", "")
    INTRO_FB = {"en":"Tucked between turquoise ocean and the laid-back vibe of Ngor Island, our surf house is your home base for waves, culture and community.","fr":"Niché entre l'océan turquoise et l'ambiance détendue de l'île de Ngor, notre surf house est votre base pour les vagues, la culture et la communauté.","es":"Enclavada entre el océano turquesa y el ambiente relajado de la isla de Ngor, nuestra surf house es tu base para las olas, la cultura y la comunidad.","it":"Immersa tra l'oceano turchese e l'atmosfera rilassata di Ngor Island, la nostra surf house è la tua base per le onde, la cultura e la comunità.","de":"Zwischen dem türkisblauen Ozean und der entspannten Atmosphäre von Ngor Island ist unser Surf House Ihre Basis für Wellen, Kultur und Gemeinschaft."}
    BOOK_TXT = {"en":"Book Your Room","fr":"Réserver","es":"Reservar","it":"Prenota","de":"Zimmer buchen"}
    AMENITY_TITLE = {"en":"What's Included","fr":"Ce qui est inclus","es":"Qué está incluido","it":"Cosa è incluso","de":"Inbegriffen"}
    PHOTOS_TITLE = {"en":"Life at the Surf House","fr":"La vie à la Surf House","es":"Vida en la Surf House","it":"La vita alla Surf House","de":"Leben im Surf House"}

    return f"""
  <section class="section">
    <div class="container">
      <div class="split reveal">
        <div>
          <span class="s-label">{"Accommodation" if lang=="en" else "Hébergement" if lang=="fr" else "Alojamiento" if lang=="es" else "Alloggio" if lang=="it" else "Unterkunft"}</span>
          <h2 class="s-title">{"Private & Shared Rooms" if lang=="en" else "Chambres privées et partagées" if lang=="fr" else "Habitaciones privadas y compartidas" if lang=="es" else "Camere private e condivise" if lang=="it" else "Einzel- und Mehrbettzimmer"}</h2>
          <p class="s-sub" style="margin-bottom:28px">{intro_text or INTRO_FB.get(lang, INTRO_FB["en"])}</p>
          <a href="{pfx}/booking/" class="btn btn-fire btn-lg">{BOOK_TXT[lang]}</a>
        </div>
        <div class="split-img"><img src="{IMGS['house2']}" alt="Ngor Surf House room" loading="lazy" width="600" height="440"></div>
      </div>
    </div>
  </section>

  <section class="section sec-sand">
    <div class="container">
      <h2 class="s-title reveal" style="text-align:center;margin-bottom:52px">{AMENITY_TITLE[lang]}</h2>
      <div class="grid-3 reveal">{feats_html}</div>
    </div>
  </section>

  <section class="section">
    <div class="container">
      <h2 class="s-title reveal" style="text-align:center;margin-bottom:40px">{PHOTOS_TITLE[lang]}</h2>
      <div class="gallery-masonry reveal">{gallery_html}</div>
    </div>
    <div id="lb"><button id="lb-close">✕</button><img id="lb-img" src="" alt="Gallery"></div>
  </section>

  <div class="cta-band">
    <div class="container">
      <h2>{"Book your stay on Ngor Island" if lang=="en" else "Réservez votre séjour à l'Île de Ngor" if lang=="fr" else "Reserva tu estancia en Ngor Island" if lang=="es" else "Prenota il tuo soggiorno a Ngor Island" if lang=="it" else "Buche deinen Aufenthalt auf Ngor Island"}</h2>
      <p>{"Contact us on WhatsApp — we reply within 24h." if lang=="en" else "Contactez-nous sur WhatsApp — réponse sous 24h." if lang=="fr" else "Contáctanos por WhatsApp — respondemos en 24h." if lang=="es" else "Contattaci su WhatsApp — rispondiamo entro 24h." if lang=="it" else "Kontaktieren Sie uns per WhatsApp — Antwort innerhalb von 24h."}</p>
      <div class="cta-btns">
        <a href="{pfx}/booking/" class="btn btn-fire btn-lg">{BOOK_TXT[lang]}</a>
        <a href="https://wa.me/221789257025" target="_blank" rel="noopener" class="btn btn-glass btn-lg">{icon("whatsapp",18)} WhatsApp</a>
      </div>
    </div>
  </div>"""

print("\nBuilding static pages for all languages...")
for lang in LANGS:
    pfx      = LANG_PREFIX[lang]
    slug_pfx = f"/{lang}" if lang != "en" else ""
    # Surf House
    write(f"{slug_pfx}/surf-house/", build_simple_page("surf-house", lang, IMGS["house2"], "Surf House", surf_house_content))
    print(f"  ✅ {lang}: /surf-house/")

print(f"\nTotal HTML files: {total_files}")
print(f"Output: {DEMO_DIR}")
print("✅ Site v2 build complete. Run wrangler to deploy.")
