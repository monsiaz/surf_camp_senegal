#!/usr/bin/env python3
"""
Ngor Surfcamp Teranga — Single Source of Truth Build Script
Usage: python3 build.py

Output: cloudflare-demo/ (historical folder name) → deployed via Vercel.
Set PUBLIC_SITE_URL for canonical / hreflang / JSON-LD (default: production Vercel URL).
"""
import html as html_module
import importlib.util
import json, os, re, sys, subprocess, shutil
from datetime import datetime, timezone
from xml.sax.saxutils import escape

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_island_spec = importlib.util.spec_from_file_location(
    "island_md", os.path.join(_BASE_DIR, "scripts", "island_md.py")
)
_island_mod = importlib.util.module_from_spec(_island_spec)
_island_spec.loader.exec_module(_island_mod)
md2html_island = _island_mod.md2html_island

_surf_house_spec = importlib.util.spec_from_file_location(
    "surf_house_page", os.path.join(_BASE_DIR, "surf_house_page.py")
)
_surf_house_mod = importlib.util.module_from_spec(_surf_house_spec)
_surf_house_spec.loader.exec_module(_surf_house_mod)
SURF_HOUSE_PAGE = _surf_house_mod.SURF_HOUSE_PAGE
SURF_HOUSE_FEATS = _surf_house_mod.SURF_HOUSE_FEATS

_site_page_spec = importlib.util.spec_from_file_location(
    "site_page_json", os.path.join(_BASE_DIR, "scripts", "site_page_json.py")
)
_site_page_mod = importlib.util.module_from_spec(_site_page_spec)
_site_page_spec.loader.exec_module(_site_page_mod)

_site_assets_spec = importlib.util.spec_from_file_location(
    "site_assets", os.path.join(_BASE_DIR, "scripts", "site_assets.py")
)
_site_assets_mod = importlib.util.module_from_spec(_site_assets_spec)
_site_assets_spec.loader.exec_module(_site_assets_mod)
# Bump ASSET_VERSION in scripts/site_assets.py after CSS/JS changes (query-string cache bust).
ASSET_VERSION = _site_assets_mod.ASSET_VERSION
ASSET_CSS_MAIN = _site_assets_mod.ASSET_CSS_MAIN
ASSET_CSS_CONSENT = _site_assets_mod.ASSET_CSS_CONSENT
ASSET_JS_MAIN = _site_assets_mod.ASSET_JS_MAIN

DEMO_DIR  = os.path.join(_BASE_DIR, "cloudflare-demo")
CONTENT   = os.path.join(_BASE_DIR, "content")
# Absolute production origin (no trailing slash). Override for custom domain.
_SITE_RAW = (os.environ.get("PUBLIC_SITE_URL") or "https://surf-camp-senegal.vercel.app").strip().rstrip("/")
if _SITE_RAW.startswith("http://"):
    SITE_URL = _SITE_RAW
elif _SITE_RAW.startswith("https://"):
    SITE_URL = _SITE_RAW
else:
    SITE_URL = "https://" + _SITE_RAW.lstrip("/")

# Legacy hosts replaced in patch_legacy_public_host_all() after each build
LEGACY_PUBLIC_HOSTS = (
    "https://ngor-surfcamp-demo.pages.dev",
    "http://ngor-surfcamp-demo.pages.dev",
)

# ════════════════════════════════════════════════════════════════
# CONSTANTS
# ════════════════════════════════════════════════════════════════
LANGS    = ["en","fr","es","it","de","nl","ar"]
LANG_PFX = {"en":"","fr":"/fr","es":"/es","it":"/it","de":"/de","nl":"/nl","ar":"/ar","pt":"/pt","da":"/da"}
LANG_LOCALE = {"en":"en","fr":"fr-FR","es":"es-ES","it":"it-IT","de":"de-DE","nl":"nl-NL","ar":"ar-MA","pt":"pt-PT","da":"da-DK"}
LANG_NAMES  = {"en":"English","fr":"Français","es":"Español","it":"Italiano","de":"Deutsch","nl":"Nederlands","ar":"العربية","pt":"Português","da":"Dansk"}

# PT and DA exist as fully built pages but are outside the main LANGS build loop
EXTRA_LANGS = ["pt", "da"]
ALL_LANGS   = LANGS + EXTRA_LANGS

# Shared UI chrome (nav, footer, lightbox, home fixes) — avoid hard-coded English on localized pages
UI_CHROME = {
    "wa": {
        "en": "WhatsApp", "fr": "WhatsApp", "es": "WhatsApp", "it": "WhatsApp",
        "de": "WhatsApp", "nl": "WhatsApp", "ar": "واتساب",
    },
    "nav_menu": {
        "en": "Menu", "fr": "Menu", "es": "Menú", "it": "Menu",
        "de": "Menü", "nl": "Menu", "ar": "القائمة",
    },
    "breadcrumb": {
        "en": "Breadcrumb", "fr": "Fil d’Ariane", "es": "Miga de pan", "it": "Percorso",
        "de": "Brotkrumen", "nl": "Kruimelpad", "ar": "مسار التنقل",
    },
    "footer_home": {
        "en": "Ngor Surfcamp Teranga home", "fr": "Accueil Ngor Surfcamp Teranga",
        "es": "Inicio Ngor Surfcamp Teranga", "it": "Home Ngor Surfcamp Teranga",
        "de": "Startseite Ngor Surfcamp Teranga", "nl": "Home Ngor Surfcamp Teranga",
        "ar": "الصفحة الرئيسية — Ngor Surfcamp Teranga",
    },
    "lang_versions": {
        "en": "Language versions", "fr": "Versions linguistiques", "es": "Versiones de idioma",
        "it": "Versioni linguistiche", "de": "Sprachversionen", "nl": "Taalversies",
        "ar": "إصدارات اللغة",
    },
    "copy_ok": {
        "en": "OK", "fr": "OK", "es": "OK", "it": "OK", "de": "OK", "nl": "OK", "ar": "تم",
    },
    "reading_loc": {
        "en": "Ngor Island, Senegal", "fr": "Île de Ngor, Sénégal", "es": "Isla de Ngor, Senegal",
        "it": "Isola di Ngor, Senegal", "de": "Ngor Island, Senegal", "nl": "Ngor Island, Senegal",
        "ar": "جزيرة نغور، السنغال",
    },
    "gallery_prev": {
        "en": "Previous image", "fr": "Image précédente", "es": "Imagen anterior",
        "it": "Immagine precedente", "de": "Vorheriges Bild", "nl": "Vorige afbeelding",
        "ar": "الصورة السابقة",
    },
    "gallery_next": {
        "en": "Next image", "fr": "Image suivante", "es": "Imagen siguiente",
        "it": "Immagine successiva", "de": "Nächstes Bild", "nl": "Volgende afbeelding",
        "ar": "الصورة التالية",
    },
    "review_by": {
        "en": "Review by", "fr": "Avis de", "es": "Reseña de", "it": "Recensione di",
        "de": "Bewertung von", "nl": "Review van", "ar": "تقييم من",
    },
}

# Short brand label next to the G icon in the home reviews header (non-Latin where needed)
HOME_REVIEWS_GOOGLE_BADGE = {
    "en": "Google", "fr": "Google", "es": "Google", "it": "Google", "de": "Google", "nl": "Google", "ar": "جوجل",
}


def ui_chrome(key: str, lang: str) -> str:
    row = UI_CHROME[key]
    return row.get(lang, row["en"])


# Localized page slugs (translate URL slugs)
SLUG = {
    "en": {"surf-house":"surf-house","island":"island","surfing":"surfing",
           "booking":"booking","gallery":"gallery","faq":"faq","blog":"blog",
           "privacy-policy":"privacy-policy","category":"category",
           "surf-conditions":"surf-conditions"},
    "fr": {"surf-house":"surf-house","island":"ile","surfing":"surf",
           "booking":"reservation","gallery":"galerie","faq":"faq","blog":"blog",
           "privacy-policy":"politique-de-confidentialite","category":"categorie",
           "surf-conditions":"conditions-surf"},
    "es": {"surf-house":"surf-house","island":"isla","surfing":"surf",
           "booking":"reservar","gallery":"galeria","faq":"faq","blog":"blog",
           "privacy-policy":"politica-de-privacidad","category":"categoria",
           "surf-conditions":"condiciones-surf"},
    "it": {"surf-house":"surf-house","island":"isola","surfing":"surf",
           "booking":"prenota","gallery":"galleria","faq":"faq","blog":"blog",
           "privacy-policy":"informativa-sulla-privacy","category":"categoria",
           "surf-conditions":"condizioni-surf"},
    "de": {"surf-house":"surf-house","island":"insel","surfing":"surfen",
           "booking":"buchen","gallery":"galerie","faq":"faq","blog":"blog",
           "privacy-policy":"datenschutzrichtlinie","category":"kategorie",
           "surf-conditions":"surf-bedingungen"},
    "nl": {"surf-house":"surf-house","island":"eiland","surfing":"surfen",
           "booking":"boeken","gallery":"galerij","faq":"faq","blog":"blog",
           "privacy-policy":"privacybeleid","category":"categorie",
           "surf-conditions":"surf-condities"},
    "ar": {"surf-house":"surf-house","island":"ngor-island","surfing":"surf",
           "booking":"reservation","gallery":"galerie","faq":"faq","blog":"blog",
           "privacy-policy":"privacy-policy","category":"categorie",
           "surf-conditions":"surf-conditions"},
}

# ── Blog category definitions ─────────────────────────────────────────────
# EN category name (as stored in JSON) → per-lang slug + display name
BLOG_CATS = {
    "Island Life & Surf Camp": {
        "slug": {
            "en": "island-life",
            "fr": "vie-ile",
            "es": "vida-isla",
            "it": "vita-isola",
            "de": "insel-leben",
            "nl": "eiland-leven",
            "ar": "island-life",
        },
        "name": {
            "en": "Island Life & Surf Camp",
            "fr": "Vie sur l'île & Surf Camp",
            "es": "Vida en la isla & Surf Camp",
            "it": "Vita sull'isola & Surf Camp",
            "de": "Inselleben & Surf Camp",
            "nl": "Eilandleven & Surfcamp",
            "ar": "حياة الجزيرة ومخيم الأمواج",
        },
        "desc": {
            "en": "Discover what life at Ngor Surf Camp is really like — island living, local culture, what to pack, and why Senegal is an underrated surf destination.",
            "fr": "Découvrez la vie au Ngor Surf Camp — île sans voitures, culture locale, quoi emporter et pourquoi le Sénégal est une destination surf sous-estimée.",
            "es": "Descubre cómo es la vida en el Ngor Surf Camp — isla sin coches, cultura local, qué llevar y por qué Senegal es un destino surf infravalorado.",
            "it": "Scopri com'è la vita al Ngor Surf Camp — isola senza auto, cultura locale, cosa portare e perché il Senegal è una destinazione surf sottovalutata.",
            "de": "Entdecke das Leben im Ngor Surf Camp — autofreie Insel, lokale Kultur, Packliste und warum Senegal ein unterschätztes Surf-Ziel ist.",
            "nl": "Ontdek hoe het leven in het Ngor Surf Camp echt is — eilandleven, lokale cultuur, wat mee te nemen en waarom Senegal een onderschat surfbestemming is.",
            "ar": "اكتشف كيف هي الحياة في مخيم نغور للأمواج — العيش على الجزيرة، الثقافة المحلية، ما تحمله، ولماذا السنغال وجهة أمواج مهمَلة.",
        },
        "icon": "🏄",
    },
    "Surf Conditions & Spots": {
        "slug": {
            "en": "surf-conditions",
            "fr": "conditions-surf",
            "es": "condiciones-surf",
            "it": "condizioni-surf",
            "de": "surf-bedingungen",
            "nl": "surf-omstandigheden",
            "ar": "surf-conditions",
        },
        "name": {
            "en": "Surf Conditions & Spots",
            "fr": "Conditions & Spots de Surf",
            "es": "Condiciones & Spots de Surf",
            "it": "Condizioni & Spot di Surf",
            "de": "Surf-Bedingungen & Spots",
            "nl": "Surfomstandigheden & Spots",
            "ar": "ظروف الأمواج والمواقع",
        },
        "desc": {
            "en": "Everything about Ngor Island's waves, the best time to surf Senegal, surf season guides and detailed breakdowns of Ngor Right and Left.",
            "fr": "Tout sur les vagues de l'île de Ngor, la meilleure saison pour surfer au Sénégal et les guides détaillés de Ngor Right et Left.",
            "es": "Todo sobre las olas de la isla de Ngor, la mejor temporada para surfear en Senegal y guías detalladas de Ngor Right y Left.",
            "it": "Tutto sulle onde dell'isola di Ngor, il periodo migliore per fare surf in Senegal e guide dettagliate su Ngor Right e Left.",
            "de": "Alles über die Wellen der Insel Ngor, die beste Surfsaison in Senegal und detaillierte Guides zu Ngor Right und Left.",
            "nl": "Alles over de golven van Ngor Island, de beste tijd om te surfen in Senegal, gidsen per seizoen en gedetailleerde overzichten van Ngor Right en Left.",
            "ar": "كل شيء عن أمواج جزيرة نغور، أفضل وقت لركوب الأمواج في السنغال، أدلة موسم الأمواج والتحليل التفصيلي لـ Ngor Right وLeft.",
        },
        "icon": "🌊",
    },
    "Coaching & Progression": {
        "slug": {
            "en": "coaching-progression",
            "fr": "coaching-progression",
            "es": "coaching-progresion",
            "it": "coaching-progressione",
            "de": "coaching-fortschritt",
            "nl": "coaching-progressie",
            "ar": "coaching-progression",
        },
        "name": {
            "en": "Coaching & Progression",
            "fr": "Coaching & Progression",
            "es": "Coaching & Progresión",
            "it": "Coaching & Progressione",
            "de": "Coaching & Fortschritt",
            "nl": "Coaching & Progressie",
            "ar": "التدريب والتطور",
        },
        "desc": {
            "en": "Surf coaching guides, how to improve faster at a surf camp, video analysis, beginner tips and how to choose the best surf camp for your level.",
            "fr": "Guides de coaching surf, progresser plus vite en surf camp, analyse vidéo, conseils pour débutants et comment choisir le meilleur surf camp.",
            "es": "Guías de coaching surf, cómo mejorar más rápido en un surf camp, análisis de vídeo, consejos para principiantes y cómo elegir el mejor surf camp.",
            "it": "Guide al coaching surf, come migliorare più velocemente in un surf camp, analisi video, consigli per principianti e come scegliere il surf camp migliore.",
            "de": "Surf-Coaching-Guides, wie man im Surfcamp schneller besser wird, Videoanalyse, Anfänger-Tipps und wie man das beste Surfcamp wählt.",
            "nl": "Surfcoaching-gidsen, sneller verbeteren in een surfkamp, videoanalyse, tips voor beginners en hoe je het beste surfkamp kiest.",
            "ar": "أدلة تدريب ركوب الأمواج، كيفية التحسن بشكل أسرع في مخيم الأمواج، تحليل الفيديو، نصائح للمبتدئين وكيفية اختيار أفضل مخيم ركوب أمواج.",
        },
        "icon": "🎯",
    },
}

# Reverse lookup: cat_en_name → BLOG_CATS key (same thing here)
CAT_SLUG_FOR_LANG = {}  # (cat_en_name, lang) → slug
CAT_PAGE_HREF = {}       # (cat_en_name, lang) → full href
for _cat_en, _cdata in BLOG_CATS.items():
    for _lg in LANGS:
        _pfx = LANG_PFX[_lg]
        _blog_slug = SLUG[_lg]["blog"]
        _cat_slug_word = SLUG[_lg]["category"]
        _cat_slug = _cdata["slug"][_lg]
        CAT_SLUG_FOR_LANG[(_cat_en, _lg)] = _cat_slug
        CAT_PAGE_HREF[(_cat_en, _lg)] = f"{_pfx}/{_blog_slug}/{_cat_slug_word}/{_cat_slug}/"

_WIX = "/assets/images/wix"
_GAL = "/assets/images/gallery"
LOGO = f"{_WIX}/c2467f_a31779010ce34c4c8c61cc5868d81f31.webp"
FSS_LOGO = "/assets/images/logo-fede-transparant.png"

IMGS = {
    "home":    f"{_WIX}/df99f9_da0cf7c72b1a4606bcfa1f7c8e089dc4f000.webp",
    "house":   f"{_WIX}/df99f9_2ec6248367cd4e21a5e6c26c2b0a1c35.webp",
    "house2":  f"{_WIX}/df99f9_eba4c24ec6a746b58d60a975b8d20946.webp",
    "house3":  f"{_WIX}/df99f9_d8e77cf4807249f6953119f18be64166.webp",
    "island":  f"{_WIX}/df99f9_56b9af6efe2841eea44109b3b08b7da1.webp",
    "island2": f"{_WIX}/b28af82dbec544138f16e2bc5a85f2cb.webp",
    "surf":    f"{_WIX}/11062b_89a070321f814742a620b190592d51ad.webp",
    "surf2":   f"{_WIX}/df99f9_dd89cc4d86d4402189d7e9516ce672a3.webp",
    "surf3":   f"{_WIX}/df99f9_961b0768e713457f93025f4ce6fb1419.webp",
    "ngor_r":  f"{_WIX}/11062b_7f89d2db0ace4027ac4a00928a6aca08.webp",
    "sunset":  f"{_WIX}/df99f9_d6e404dd3cf74396b6ea874cb7021a27.webp",
    "art":     f"{_WIX}/df99f9_d81668a18a9d49d1b5ebb0ea3a0abbc7.webp",
    "food":    f"{_GAL}/CAML1098.webp",
    "pool":    f"{_WIX}/df99f9_a18d512828d9487e9a4987b9903960e0.webp",
    "review":  f"{_WIX}/df99f9_961b0768e713457f93025f4ce6fb1419.webp",
    "book_bg": f"{_WIX}/df99f9_0d4a03baee4f46b68bc1aa085ed28e35.webp",
    "gallery": [
        f"{_WIX}/df99f9_16fcc19c812d49a9a05e361aacdc9cea.webp",
        f"{_WIX}/df99f9_25cc88706ffb42debadac4787bab4f02.webp",
        f"{_WIX}/df99f9_6a9de50280094c06b4bb439b5d0a7ca7.webp",
        f"{_WIX}/df99f9_bb61f8a278004fccb5f55351a772472c.webp",
        f"{_WIX}/df99f9_6fae936c12864930a0e7413cdccf6fd0.webp",
        f"{_WIX}/df99f9_27471c09c19d473896e650316f2a0622.webp",
        f"{_WIX}/df99f9_42ff8407b442474fa5d54253fac98133.webp",
        f"{_WIX}/df99f9_64a5d28bf1d94191ad2fa45af7de6782.webp",
        f"{_WIX}/df99f9_0d4a03baee4f46b68bc1aa085ed28e35.webp",
        f"{_WIX}/df99f9_796b6115065145eabddfe3ae32b8f4d5.webp",
        f"{_WIX}/df99f9_bde010e1296b478cbbe4f885c2714338.webp",
        f"{_WIX}/df99f9_81e322c4e48d4bcbb444c6535daed131.webp",
    ],
}


def wix_thumb_url(full_url, w=520):
    """Self-hosted WebP assets — no transform needed, just return as-is."""
    return full_url


def build_gallery_thumb_buttons(urls, alt_raw, pe, thumb_w=560, eager_first=False):
    """Buttons with lazy thumbnails and data-full for lightbox (full resolution)."""
    alt = pe(alt_raw)
    n = len(urls)
    parts = []
    for i, full in enumerate(urls):
        thumb = wix_thumb_url(full, thumb_w)
        if i == 0 and eager_first:
            lz = 'loading="eager" fetchpriority="high"'
        else:
            lz = 'loading="lazy"'
        aw = n > 1 and f' aria-label="{alt} ({i + 1} / {n})"' or f' aria-label="{alt}"'
        parts.append(
            f'<button type="button" class="gallery-item reveal" role="listitem" data-full="{full}"{aw}>'
            f'<span class="gallery-item-inner">'
            f'<img src="{thumb}" alt="{alt}" width="{thumb_w}" height="{max(1, int(thumb_w * 0.75))}" '
            f'decoding="async" referrerpolicy="no-referrer" {lz}>'
            f"</span></button>"
        )
    return "".join(parts)


SURF_HOUSE_SHOTS = [
    f"{_GAL}/CAML1124_73024503.webp",
    f"{_GAL}/CAML1129_2323b4f6.webp",
    f"{_GAL}/CAML1133_c4e634ba.webp",
    f"{_GAL}/CAML1136_7887aa9f.webp",
    f"{_GAL}/CAML1138_615df811.webp",
    f"{_GAL}/CAML1142_092a767e.webp",
    f"{_GAL}/CAML1150_c1f8abfe.webp",
    f"{_GAL}/CAML1100_3a5f7e17.webp",
]

SURF_ACTION_SHOTS = [
    f"{_GAL}/4Y4A1344_890dc276.webp",
    f"{_GAL}/4Y4A1346_463ff1cc.webp",
    f"{_GAL}/4Y4A1347_0937fe77.webp",
    f"{_GAL}/4Y4A1349_2e925d77.webp",
    f"{_GAL}/4Y4A1351_4cd37638.webp",
    f"{_GAL}/4Y4A1352_39bf908a.webp",
    f"{_GAL}/4Y4A1353_cd947b75.webp",
    f"{_GAL}/4Y4A1354_b7dabb94.webp",
]

# Labels for the "Explore the Gallery" CTA on landing pages
EXPLORE_GAL = {
    "en": "Explore the Gallery",
    "fr": "Voir toute la galerie",
    "es": "Ver toda la galería",
    "it": "Esplora tutta la galleria",
    "de": "Zur Galerie",
    "nl": "Bekijk de galerij",
    "ar": "استكشف المعرض",
    "pt": "Ver a galeria completa",
    "da": "Udforsk galleriet",
}

VIDEO_BASE = "/assets/video/hero-ngor"

ICO_BASE  = "/assets/images/icons"
ICONS_DIR = f"{DEMO_DIR}/assets/images/icons"

# ════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════
def load(path):
    if os.path.exists(path):
        try:
            with open(path) as f: return json.load(f)
        except: return None
    return None

def fix_em(t):
    if not t: return ""
    s = str(t).replace(" — ",", ").replace("—",",").replace("\u2014",",").replace(" – ",", ").replace("–",",")
    s = re.sub(r'\*\*(.*?)\*\*', r'\1', s)
    s = re.sub(r'\*(.*?)\*', r'\1', s)
    s = re.sub(r'\*+', '', s)
    return re.sub(r',\s*,', ',', s)

def icon_img(name, size=24):
    """Get icon img or empty string."""
    png = f"{ICONS_DIR}/{name}.png"
    if os.path.exists(png) and os.path.getsize(png) > 5000:
        return (f'<img src="{ICO_BASE}/{name}.png" alt="" width="{size}" height="{size}" '
                f'style="object-fit:contain;display:block;filter:brightness(0)invert(1)sepia(1)saturate(3)hue-rotate(5deg)">')
    return ""

# ── Wave section dividers ──────────────────────────────────────────────
def wave_top(next_bg, prev_fill):
    """Wave strip: prev_fill shape on top fading into next_bg below."""
    return (
        f'<div class="wave-top" style="background:{next_bg}" aria-hidden="true">'
        f'<svg viewBox="0 0 1440 52" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">'
        f'<path d="M0 26 C240 50,480 2,720 28 C960 54,1200 4,1440 26 L1440 0 L0 0Z" fill="{prev_fill}"/>'
        f'</svg></div>'
    )

def wave_bottom(prev_bg, next_fill):
    """Wave strip: prev_bg on top fading into next_fill wave below."""
    return (
        f'<div class="wave-bottom" style="background:{prev_bg}" aria-hidden="true">'
        f'<svg viewBox="0 0 1440 52" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">'
        f'<path d="M0 26 C240 2,480 50,720 24 C960 -2,1200 48,1440 26 L1440 52 L0 52Z" fill="{next_fill}"/>'
        f'</svg></div>'
    )

# Home page background tokens (must match CSS)
_BG_WHITE   = "#ffffff"
_BG_LIGHT   = "#f7fafd"      # .sec-light
_BG_NAVY    = "#07192e"      # .sec-dark / reviews-section
_BG_SAND    = "#fff8ec"      # .sec-sand (sand3 start)
_BG_BLUE    = "#f0f8ff"      # .gh-teaser

HOME_WAVE_PATCHES = [
    # (search_before, wave_html)
    # NOTE: white→sec-light wave removed (contrast ~1.04:1, essentially invisible)
    (
        '\n\n  <section class="reviews-section"',
        lambda: f'\n\n  {wave_bottom(_BG_LIGHT, _BG_NAVY)}'
    ),
    # This wave sits between reviews (navy) and the forecast/ig/blog block.
    # It correctly marks the end of the navy section into sec-light.
    (
        '\n\n  <!-- BLOG PREVIEW -->',
        lambda: f'\n\n  {wave_top(_BG_LIGHT, _BG_NAVY)}'
    ),
    (
        '\n\n  \n  <!-- Getting Here teaser -->',
        lambda: f'\n\n  {wave_bottom(_BG_SAND, _BG_BLUE)}'
    ),
    (
        '\n\n  <!-- CTA BAND -->',
        lambda: f'\n\n  {wave_bottom(_BG_BLUE, _BG_NAVY)}'
    ),
]

HOME_PAGES = [
    "index.html",
    "fr/index.html",
    "es/index.html",
    "it/index.html",
    "de/index.html",
    "nl/index.html",
    "ar/index.html",
]

def patch_home_waves_all():
    """Insert wave SVG dividers between sections on all home pages."""
    n_files = 0
    for rel in HOME_PAGES:
        path = os.path.join(DEMO_DIR, rel)
        if not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8", errors="replace") as f:
            h = f.read()
        # Always strip any existing wave dividers before re-applying to prevent stacking
        import re as _re
        h = _re.sub(r'\s*<div class="wave-(?:top|bottom)"[^>]*>.*?</div>', '', h, flags=_re.DOTALL)
        h = _re.sub(r'\s*<div[^>]*class="[^"]*wave-divider[^"]*"[^>]*>.*?</div>', '', h, flags=_re.DOTALL)
        h2 = h
        for marker, wave_fn in HOME_WAVE_PATCHES:
            if marker in h2:
                h2 = h2.replace(marker, wave_fn() + marker, 1)
        if h2 != h:
            with open(path, "w", encoding="utf-8") as f:
                f.write(h2)
            n_files += 1
    print(f"  home waves: updated {n_files} files")


FLAG_SVG = {
    "en": '<svg viewBox="0 0 60 40"><rect width="60" height="40" fill="#012169"/><path d="M0,0 L60,40 M60,0 L0,40" stroke="#fff" stroke-width="8"/><path d="M0,0 L60,40 M60,0 L0,40" stroke="#C8102E" stroke-width="5"/><path d="M30,0 V40 M0,20 H60" stroke="#fff" stroke-width="12"/><path d="M30,0 V40 M0,20 H60" stroke="#C8102E" stroke-width="8"/></svg>',
    "fr": '<svg viewBox="0 0 60 40"><rect width="20" height="40" fill="#002395"/><rect x="20" width="20" height="40" fill="#fff"/><rect x="40" width="20" height="40" fill="#ED2939"/></svg>',
    "es": '<svg viewBox="0 0 60 40"><rect width="60" height="40" fill="#c60b1e"/><rect y="10" width="60" height="20" fill="#ffc400"/></svg>',
    "it": '<svg viewBox="0 0 60 40"><rect width="20" height="40" fill="#009246"/><rect x="20" width="20" height="40" fill="#fff"/><rect x="40" width="20" height="40" fill="#CE2B37"/></svg>',
    "de": '<svg viewBox="0 0 60 40"><rect width="60" height="13" fill="#000"/><rect y="13" width="60" height="14" fill="#DD0000"/><rect y="27" width="60" height="13" fill="#FFCE00"/></svg>',
    "nl": '<svg viewBox="0 0 60 40"><rect width="60" height="13" fill="#AE1C28"/><rect y="13" width="60" height="14" fill="#fff"/><rect y="27" width="60" height="13" fill="#21468B"/></svg>',
    "ar": '<svg viewBox="0 0 60 40"><rect width="60" height="40" fill="#C1272D"/><path d="M30,10 L31.8,16.1 L38.5,16.1 L33,19.9 L35,26 L30,22.1 L25,26 L27,19.9 L21.5,16.1 L28.2,16.1 Z" fill="none" stroke="#006233" stroke-width="1.2"/></svg>',
    "da": '<svg viewBox="0 0 60 40"><rect width="60" height="40" fill="#C60C30"/><rect x="20" width="8" height="40" fill="#fff"/><rect y="16" width="60" height="8" fill="#fff"/></svg>',
    "pt": '<svg viewBox="0 0 60 40"><rect width="22" height="40" fill="#006600"/><rect x="22" width="38" height="40" fill="#FF0000"/><circle cx="22" cy="20" r="8" fill="#FFD700" stroke="#006600" stroke-width="1"/></svg>',
}

def flag(lang, size=22):
    h2 = round(size*0.667)
    return (f'<span style="width:{size}px;height:{h2}px;display:inline-flex;'
            f'border-radius:3px;overflow:hidden;flex-shrink:0;box-shadow:0 1px 3px rgba(0,0,0,0.22)">'
            f'{FLAG_SVG[lang]}</span>')

WA_ICO   = '<svg viewBox="0 0 24 24" fill="currentColor" width="18" height="18"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>'
MENU_ICO = '<svg viewBox="0 0 24 24" fill="none" width="22" height="22"><path d="M3 7h18M3 12h18M3 17h12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>'
CHEV_ICO = '<svg viewBox="0 0 16 16" fill="none" width="14" height="14"><path d="M4 6l4 4 4-4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
IG_ICO   = '<svg viewBox="0 0 24 24" fill="currentColor" width="18" height="18"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>'
TT_ICO   = '<svg viewBox="0 0 24 24" fill="currentColor" width="18" height="18"><path d="M19.59 6.69a4.83 4.83 0 01-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 01-2.88 2.5 2.89 2.89 0 01-2.89-2.89 2.89 2.89 0 012.89-2.89c.28 0 .54.04.79.1V9.01a6.28 6.28 0 00-.79-.05 6.34 6.34 0 00-6.34 6.34 6.34 6.34 0 006.34 6.34 6.34 6.34 0 006.33-6.34V8.69a8.22 8.22 0 004.84 1.56V6.79a4.85 4.85 0 01-1.07-.1z"/></svg>'

def hreflang_tags(page_key):
    """Generate hreflang links for a given page key."""
    en_slug = SLUG["en"][page_key]
    tags = [
        f'<link rel="alternate" hreflang="x-default" href="{SITE_URL}/{en_slug}/">',
        f'<link rel="alternate" hreflang="en" href="{SITE_URL}/{en_slug}/">',
    ]
    for l in ["fr","es","it","de","nl","ar"]:
        s = SLUG[l][page_key]
        tags.append(f'<link rel="alternate" hreflang="{LANG_LOCALE[l]}" href="{SITE_URL}/{l}/{s}/">')
    return "\n".join(tags)

def canonical_tag(page_key, lang):
    pfx  = LANG_PFX[lang]
    slug = SLUG[lang][page_key]
    url  = f"{pfx}/{slug}/" if lang != "en" else f"/{slug}/"
    return f'<link rel="canonical" href="{SITE_URL}{url}">'

def page_head(title, meta, lang, page_key, og_img="", og_type="website"):
    can = canonical_tag(page_key, lang)
    hrl = hreflang_tags(page_key)
    _locale = LANG_LOCALE.get(lang, lang)
    _og_locale = {"en":"en_US","fr":"fr_FR","es":"es_ES","it":"it_IT","de":"de_DE","nl":"nl_NL","ar":"ar_MA"}.get(lang, "en_US")
    _dir = ' dir="rtl"' if lang == "ar" else ""
    _ar_font = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@400;600;700&display=swap">\n' if lang == "ar" else ""
    _img = og_img or IMGS['home']
    _abs_img = f"{SITE_URL}{_img}" if _img.startswith("/") else _img
    _pfx = LANG_PFX[lang]
    _slug = SLUG[lang].get(page_key, page_key)
    _url = f"{SITE_URL}{_pfx}/" if not page_key else f"{SITE_URL}{_pfx}/{_slug}/"
    return f"""<!DOCTYPE html>
<html lang="{_locale}"{_dir}>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
{_ar_font}<title>{fix_em(title)}</title>
<meta name="description" content="{fix_em(meta)}">
<meta property="og:title" content="{fix_em(title)}">
<meta property="og:description" content="{fix_em(meta)}">
<meta property="og:image" content="{_abs_img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:url" content="{_url}">
<meta property="og:type" content="{og_type}">
<meta property="og:locale" content="{_og_locale}">
<meta property="og:site_name" content="Ngor Surfcamp Teranga">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{fix_em(title)}">
<meta name="twitter:description" content="{fix_em(meta)}">
<meta name="twitter:image" content="{_abs_img}">
<meta name="robots" content="index,follow">
{can}
{hrl}

<link rel="preload" href="https://fonts.googleapis.com/css2?family=Raleway:ital,wght@0,400;0,700;0,800;0,900;1,400&family=Inter:wght@400;500;600&display=swap" as="style" onload="this.onload=null;this.rel='stylesheet'">
<noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Raleway:ital,wght@0,400;0,700;0,800;0,900;1,400&family=Inter:wght@400;500;600&display=swap"></noscript>
<link rel="stylesheet" href="/assets/css/{ASSET_CSS_MAIN}?v={ASSET_VERSION}">
<script src="/assets/js/{ASSET_JS_MAIN}?v={ASSET_VERSION}" defer></script>
<link rel="icon" type="image/x-icon" href="/favicon.ico">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#0a2540">
</head>
<body>
<div id="scroll-progress"></div>"""

def build_nav(active_key, lang, lang_switcher_hrefs=None):
    pfx = LANG_PFX[lang]
    NAV = [
        ("",          {"en":"Home","fr":"Accueil","es":"Inicio","it":"Home","de":"Start","nl":"Home","ar":"الرئيسية"}),
        ("surf-house",{"en":"Surf House","fr":"Surf House","es":"Surf House","it":"Surf House","de":"Surf House","nl":"Surf House","ar":"بيت الأمواج"}),
        ("island",    {"en":"Island","fr":"Île","es":"Isla","it":"Isola","de":"Insel","nl":"Eiland","ar":"الجزيرة"}),
        ("surfing",   {"en":"Surfing","fr":"Surf","es":"Surf","it":"Surf","de":"Surfen","nl":"Surfen","ar":"ركوب الأمواج"}),
        ("blog",      {"en":"Blog","fr":"Blog","es":"Blog","it":"Blog","de":"Blog","nl":"Blog","ar":"المدونة"}),
        ("gallery",   {"en":"Gallery","fr":"Galerie","es":"Galería","it":"Galleria","de":"Galerie","nl":"Galerij","ar":"معرض الصور"}),
        ("faq",       {"en":"FAQ","fr":"FAQ","es":"FAQ","it":"FAQ","de":"FAQ","nl":"FAQ","ar":"الأسئلة الشائعة"}),
        ("booking",   {"en":"Book Now","fr":"Réserver","es":"Reservar","it":"Prenota","de":"Buchen","nl":"Boeken","ar":"احجز الآن"}),
    ]
    items = ""
    for key, labels in NAV:
        label = labels.get(lang, labels["en"])
        slug  = SLUG[lang].get(key, key)
        href  = f"{pfx}/" if not key else f"{pfx}/{slug}/"
        cls   = "nav-link active" if key == active_key else "nav-link"
        if key == "booking": cls += " nav-cta"
        items += f'<a href="{href}" class="{cls}">{label}</a>'

    # Language dropdown — navigates to correct localized URL
    opts = ""
    for other_lang in ALL_LANGS:
        if other_lang == lang:
            continue
        if lang_switcher_hrefs and other_lang in lang_switcher_hrefs:
            href = lang_switcher_hrefs[other_lang]
        elif other_lang in LANGS:
            other_pfx = LANG_PFX[other_lang]
            if active_key and active_key in SLUG[other_lang]:
                href = f"{other_pfx}/{SLUG[other_lang][active_key]}/"
            else:
                href = f"{other_pfx}/"
        else:
            # EXTRA_LANGS (pt, da) — link to their home page
            href = LANG_PFX[other_lang] + "/"
        if not href.startswith("/"):
            href = "/" + href.lstrip("/")
        opts += f'<a class="lang-dd-item" href="{href}" hreflang="{LANG_LOCALE[other_lang]}" role="menuitem">{flag(other_lang,18)} {LANG_NAMES[other_lang]}</a>'

    lang_dd = (
        f'<div class="lang-dd" id="lang-dd">'
        f'<button class="lang-dd-btn" onclick="toggleLangDD(event)">'
        f'{flag(lang,20)} {lang.upper()} '
        f'<span style="display:inline-flex">{CHEV_ICO}</span></button>'
        f'<div class="lang-dd-menu" role="menu">{opts}</div></div>'
    )

    return (
        f'<nav id="nav"><div class="nav-inner">'
        f'<a href="{pfx}/" class="nav-logo">'
        f'<img src="{LOGO}" alt="Ngor Surfcamp Teranga" width="44" height="44" loading="eager"></a>'
        f'<div class="nav-links" id="nav-links">{items}</div>'
        f'<div class="nav-right">{lang_dd}'
        f'<a href="https://wa.me/221789257025" target="_blank" rel="noopener" class="nav-wa" aria-label="{escape(ui_chrome("wa", lang))}">'
        f'<span style="display:inline-flex">{WA_ICO}</span>'
        f'<span class="nav-wa-label">{escape(ui_chrome("wa", lang))}</span></a>'
        f'<button class="nav-toggle" id="nav-toggle" aria-label="{escape(ui_chrome("nav_menu", lang))}" onclick="toggleMenu()">'
        f'<span style="display:inline-flex;color:#fff">{MENU_ICO}</span></button>'
        f'</div></div></nav>'
    )

GETTING_HERE_FLAG_HREF = {
    "en": "/getting-here/",
    "fr": "/fr/comment-venir/",
    "es": "/es/como-llegar/",
    "it": "/it/come-arrivare/",
    "de": "/de/anreise/",
    "nl": "/nl/hoe-kom-je-er/",
    "ar": "/ar/كيف-تصل/",
}

GETTING_HERE_SEGMENT = {}
for _gh_lang in LANGS:
    _gh_path = GETTING_HERE_FLAG_HREF[_gh_lang].strip("/")
    GETTING_HERE_SEGMENT[_gh_lang] = _gh_path.split("/")[-1]

def build_footer(lang, flag_href_override=None):
    pfx = LANG_PFX[lang]
    # Only practical utility links not already prominent in the nav
    PLAN_LINKS = [
        ("surf-conditions", {
            "en":"Surf Forecast","fr":"Prévisions Surf","es":"Previsiones Surf",
            "it":"Previsioni Surf","de":"Surfvorhersage","nl":"Surfvoorspelling",
            "ar":"توقعات السيرف","pt":"Previsão Surf","da":"Surfudsigt",
        }),
    ]
    links_html = "\n".join([
        f'<a href="{pfx}/{SLUG[lang][k]}/">{l.get(lang,l["en"])}</a>'
        for k,l in PLAN_LINKS
    ])
    GH_L = {
        "en":"Getting here","fr":"Comment venir","es":"Cómo llegar",
        "it":"Come arrivare","de":"Anreise","nl":"Hoe kom je er",
        "ar":"كيف تصل","pt":"Como chegar","da":"Kom hertil",
    }
    gh_href = (flag_href_override if flag_href_override is not None else GETTING_HERE_FLAG_HREF)[lang]
    links_html += f'\n<a href="{gh_href}">{GH_L.get(lang, GH_L["en"])}</a>'
    flag_urls = flag_href_override if flag_href_override is not None else None
    flags_html = " ".join([
        f'<a href="{flag_urls[l] if flag_urls else LANG_PFX[l] + "/"}" class="footer-flag-link" '
        f'hreflang="{LANG_LOCALE[l]}" title="{LANG_NAMES[l]}">{flag(l,22)}</a>'
        for l in LANGS
    ])
    # Add DA (Danish) and PT (Portuguese) flags — pages exist but outside main LANGS pipeline
    _EXTRA_LANGS = [("da", "/da/", "da-DK", "Dansk"), ("pt", "/pt/", "pt-PT", "Português")]
    for _el, _ehref, _elocale, _ename in _EXTRA_LANGS:
        if _el in FLAG_SVG:
            _esize = 22; _eh2 = round(_esize*0.667)
            _eflag = (f'<span style="width:{_esize}px;height:{_eh2}px;display:inline-flex;'
                      f'border-radius:3px;overflow:hidden;flex-shrink:0;box-shadow:0 1px 3px rgba(0,0,0,0.22)">'
                      f'{FLAG_SVG[_el]}</span>')
            flags_html += f' <a href="{_ehref}" class="footer-flag-link" hreflang="{_elocale}" title="{_ename}">{_eflag}</a>'
    ABOUT = {
        "en":"Premium surf camp on Ngor Island, Dakar, Senegal. All levels welcome.",
        "fr":"Surf camp premium sur l'île de Ngor, Dakar, Sénégal. Tous niveaux bienvenus.",
        "es":"Surf camp premium en la isla de Ngor, Dakar, Senegal. Todos los niveles bienvenidos.",
        "it":"Surf camp premium sull'isola di Ngor, Dakar, Senegal. Tutti i livelli benvenuti.",
        "de":"Premium Surfcamp auf Ngor Island, Dakar, Senegal. Alle Level willkommen.",
        "nl":"Premium surfkamp op Ngor Island, Dakar, Senegal. Alle niveaus welkom.",
        "ar":"مخيم ركوب أمواج متميز في جزيرة نغور، داكار، السنغال. جميع المستويات مرحب بها.",
        "pt":"Surf camp premium na Ilha de Ngor, Dakar, Senegal. Todos os níveis bem-vindos.",
        "da":"Premium surfcamp på Ngor Island, Dakar, Senegal. Alle niveauer velkomne.",
    }
    FSS_CERT_LABEL = {"en":"Licensed &amp; Certified",
                      "fr":"Licencié &amp; Certifié",
                      "es":"Licenciado &amp; Certificado",
                      "it":"Autorizzato &amp; Certificato",
                      "de":"Lizenziert &amp; Zertifiziert",
                      "nl":"Erkend &amp; Gecertificeerd",
                      "ar":"مرخص &amp; معتمد"}
    FSS_CERT_SUB  = {"en":"Fédération Sénégalaise de Surf",
                     "fr":"Fédération Sénégalaise de Surf",
                     "es":"Federación Senegalesa de Surf",
                     "it":"Federazione Senegalese di Surf",
                     "de":"Senegalesischer Surfverband",
                     "nl":"Senegalese Surfbond",
                     "ar":"الاتحاد السنغالي للسرف"}
    CERT_H4 = {"en":"Accreditation","fr":"Accréditation","es":"Acreditación","it":"Accreditamento","de":"Akkreditierung","nl":"Accreditatie","ar":"الاعتماد"}
    GMB_REVIEWS_LBL = {"en":"reviews on Google","fr":"avis sur Google","es":"reseñas en Google",
                        "it":"recensioni su Google","de":"Bewertungen auf Google",
                        "nl":"beoordelingen op Google","ar":"مراجعة على Google"}
    FSS_LBL = {
        "en": "Licensed &amp; Certified",
        "fr": "Agréé &amp; Certifié",
        "es": "Licenciado &amp; Certificado",
        "it": "Autorizzato &amp; Certificato",
        "de": "Lizenziert &amp; Zertifiziert",
        "nl": "Erkend &amp; Gecertificeerd",
        "ar": "مرخص ومعتمد",
        "pt": "Licenciado &amp; Certificado",
        "da": "Licenseret &amp; Certificeret",
    }
    COPY  = {"en":"© 2025 Ngor Surfcamp Teranga. All rights reserved.",
             "fr":"© 2025 Ngor Surfcamp Teranga. Tous droits réservés.",
             "es":"© 2025 Ngor Surfcamp Teranga. Todos los derechos reservados.",
             "it":"© 2025 Ngor Surfcamp Teranga. Tutti i diritti riservati.",
             "de":"© 2025 Ngor Surfcamp Teranga. Alle Rechte vorbehalten.","nl":"© 2025 Ngor Surfcamp Teranga. Alle rechten voorbehouden.","ar":"© 2025 Ngor Surfcamp Teranga. جميع الحقوق محفوظة."}
    PP_LBL = {"en":"Privacy Policy","fr":"Politique de confidentialité",
              "es":"Política de privacidad","it":"Informativa sulla privacy",
              "de":"Datenschutzrichtlinie","nl":"Privacybeleid","ar":"سياسة الخصوصية"}
    pp_href = f"{pfx}/{SLUG[lang]['privacy-policy']}/"
    EXP = {
        "en":"Plan your trip","fr":"Infos pratiques","es":"Planifica tu viaje",
        "it":"Pianifica il viaggio","de":"Reise planen","nl":"Plan je reis",
        "ar":"خطط لرحلتك","pt":"Planeia a tua viagem","da":"Planlæg din rejse",
    }
    CON = {"en":"Contact","fr":"Contact","es":"Contacto","it":"Contatti","de":"Kontakt","nl":"Contact","ar":"اتصل بنا","pt":"Contacto","da":"Kontakt"}
    FOL = {"en":"Follow Us","fr":"Suivez-nous","es":"Síguenos","it":"Seguici","de":"Folgen","nl":"Volgen","ar":"تابعنا","pt":"Siga-nos","da":"Følg os"}

    return f"""<footer>
  <div class="container">
    <div class="footer-grid">
      <div class="footer-brand">
        <a href="{LANG_PFX[lang]}/" class="footer-brand-mark" aria-label="{escape(ui_chrome('footer_home', lang))}">
          <img src="{LOGO}" alt="" width="152" height="52" class="footer-brand-logo" loading="lazy">
        </a>
        <p class="footer-brand-text">{ABOUT[lang]}</p>
        <div class="footer-social">
          <a href="https://wa.me/221789257025" target="_blank" class="soc-btn wa" aria-label="{escape(ui_chrome('wa', lang))}"><span style="display:inline-flex">{WA_ICO}</span></a>
          <a href="https://www.instagram.com/ngorsurfcampteranga" target="_blank" class="soc-btn ig" aria-label="Instagram"><span style="display:inline-flex">{IG_ICO}</span></a>
          <a href="https://www.tiktok.com/@ngorsurfcampteranga" target="_blank" class="soc-btn tt" aria-label="TikTok"><span style="display:inline-flex">{TT_ICO}</span></a>
        </div>
        <a href="https://www.google.com/maps?cid=14555894641030809667" target="_blank" rel="noopener" class="footer-gmb-badge" aria-label="4.7 — 54 {GMB_REVIEWS_LBL[lang]}">
          <span class="footer-gmb-logo"><svg viewBox="0 0 24 24" width="16" height="16" xmlns="http://www.w3.org/2000/svg"><path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/><path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/><path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" fill="#FBBC05"/><path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/></svg></span>
          <span class="footer-gmb-stars" aria-hidden="true">★★★★★</span>
          <span class="footer-gmb-score">4.7</span>
          <span class="footer-gmb-count">· 54 {GMB_REVIEWS_LBL[lang]}</span>
        </a>
        <div class="footer-fss-badge" role="img" aria-label="{FSS_LBL[lang]}">
          <span class="footer-fss-logo-wrap"><img src="/assets/images/logo-fss-badge.webp" alt="FSS" width="36" height="36" loading="lazy"></span>
          <span class="footer-fss-text"><span class="footer-fss-title">{FSS_LBL[lang]}</span><span class="footer-fss-sub">Fédération Sénégalaise de Surf</span></span>
        </div>
      </div>
      <div class="footer-col"><p class="footer-col-title">{EXP[lang]}</p>{links_html}</div>
      <div class="footer-col">
        <p class="footer-col-title">{CON[lang]}</p>
        <a href="https://wa.me/221789257025" target="_blank">{escape(ui_chrome("wa", lang))}: +221 78 925 70 25</a>
        <a href="mailto:info@surfcampsenegal.com">info@surfcampsenegal.com</a>
      </div>
      <div class="footer-col">
        <p class="footer-col-title">{FOL[lang]}</p>
        <a href="https://www.instagram.com/ngorsurfcampteranga" target="_blank">Instagram</a>
        <a href="https://www.tiktok.com/@ngorsurfcampteranga" target="_blank">TikTok</a>
        <a href="https://wa.me/221789257025" target="_blank">{escape(ui_chrome("wa", lang))}</a>
      </div>
    </div>
    <div class="footer-bottom">
      <p>{COPY[lang]} &nbsp;·&nbsp; <a href="{pp_href}" class="footer-pp-link">{PP_LBL[lang]}</a></p>
      <div class="footer-flags" aria-label="{escape(ui_chrome('lang_versions', lang))}">{flags_html}</div>
    </div>
  </div>
</footer>"""

def page_close():
    """ONLY the closing tags — NO inline JS (site JS bundle handles interactions)."""
    return "\n</body>\n</html>"


def _sitemap_lang_for_rel(rel: str) -> str:
    for lg in ["fr", "es", "it", "de", "nl", "ar"]:
        if rel.startswith(f"{lg}/"):
            return lg
    return "en"


def _sitemap_path_parts(loc: str) -> list:
    base = SITE_URL.rstrip("/")
    tail = loc[len(base) :].strip("/")
    return [p for p in tail.split("/") if p]


def _sitemap_is_island_guide(parts: list) -> bool:
    if len(parts) == 2 and parts[0] == "island":
        return True
    _island_words = {"ile", "isla", "isola", "insel", "eiland", "ngor-island"}
    if len(parts) == 3 and parts[0] in ("fr", "es", "it", "de", "nl", "ar") and parts[1] in _island_words:
        return True
    return False


def _sitemap_priority(loc: str) -> str:
    parts = _sitemap_path_parts(loc)
    if not parts:
        return "1.0"
    if len(parts) == 1 and parts[0] in LANGS:
        return "1.0"
    if "blog" in parts:
        i = parts.index("blog")
        if i == len(parts) - 1:
            return "0.85"
        # Category pages: blog/category/slug → priority 0.78
        cat_words = set(SLUG[l]["category"] for l in LANGS)
        if len(parts) > i + 1 and parts[i + 1] in cat_words:
            return "0.78"
        return "0.65"
    if _sitemap_is_island_guide(parts):
        return "0.72"
    if len(parts) <= 2:
        return "0.9"
    return "0.8"


def _sitemap_changefreq(loc: str) -> str:
    parts = _sitemap_path_parts(loc)
    if not parts:
        return "weekly"
    if "blog" in parts:
        i = parts.index("blog")
        if i == len(parts) - 1:
            return "weekly"
        # Category pages update weekly
        cat_words = set(SLUG[l]["category"] for l in LANGS)
        if len(parts) > i + 1 and parts[i + 1] in cat_words:
            return "weekly"
        return "monthly"
    if _sitemap_is_island_guide(parts):
        return "monthly"
    if len(parts) == 1 and parts[0] in LANGS:
        return "weekly"
    return "monthly"


def write_sitemaps_and_robots():
    """Per-language sitemaps, sitemap index, robots.txt (basic SEO)."""
    base = SITE_URL.rstrip("/")
    entries = {lg: [] for lg in LANGS}

    for root, dirs, files in os.walk(DEMO_DIR):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "node_modules"]
        for fn in files:
            if not fn.endswith(".html"):
                continue
            full = os.path.join(root, fn)
            rel = os.path.relpath(full, DEMO_DIR).replace("\\", "/")
            if rel in ("faq.html", "surfing.html"):
                continue
            if fn != "index.html":
                continue
            try:
                with open(full, encoding="utf-8", errors="replace") as fh:
                    head = fh.read(6000)
            except OSError:
                continue
            if "http-equiv" in head and "refresh" in head.lower():
                continue

            parent = os.path.dirname(rel).replace("\\", "/")
            if parent in (".", ""):
                loc = f"{base}/"
            else:
                loc = f"{base}/{parent}/"

            lg = _sitemap_lang_for_rel(rel)
            pri = _sitemap_priority(loc)
            cf = _sitemap_changefreq(loc)
            try:
                lm = datetime.fromtimestamp(os.path.getmtime(full)).strftime("%Y-%m-%d")
            except OSError:
                lm = datetime.now(timezone.utc).strftime("%Y-%m-%d")

            line = (
                "  <url>\n"
                f"    <loc>{escape(loc)}</loc>\n"
                f"    <lastmod>{lm}</lastmod>\n"
                f"    <changefreq>{cf}</changefreq>\n"
                f"    <priority>{pri}</priority>\n"
                "  </url>"
            )
            entries[lg].append((loc, line))

    for lg in LANGS:
        entries[lg].sort(key=lambda x: x[0])
        body = "\n".join(x[1] for x in entries[lg])
        path = os.path.join(DEMO_DIR, f"sitemap-{lg}.xml")
        with open(path, "w", encoding="utf-8") as f:
            f.write(
                '<?xml version="1.0" encoding="UTF-8"?>\n'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                f"{body}\n</urlset>\n"
            )

    index_body = "\n".join(
        f"  <sitemap><loc>{escape(f'{base}/sitemap-{lg}.xml')}</loc></sitemap>" for lg in LANGS
    )
    sitemap_index_content = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{index_body}\n</sitemapindex>\n"
    )
    with open(os.path.join(DEMO_DIR, "sitemap-index.xml"), "w", encoding="utf-8") as f:
        f.write(sitemap_index_content)
    # /sitemap.xml alias — many tools and Google Search Console expect this canonical path
    with open(os.path.join(DEMO_DIR, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sitemap_index_content)

    robots = f"""User-agent: *
Allow: /

# CMS / admin — private, not indexable
Disallow: /admin/
Disallow: /admin

# Serverless API routes — internal only
Disallow: /api/

# Vercel internals
Disallow: /_vercel/
Disallow: /.well-known/

# Dev / build artefacts
Disallow: /node_modules/
Disallow: /.vercel/

Sitemap: {base}/sitemap.xml
Sitemap: {base}/sitemap-index.xml
"""
    with open(os.path.join(DEMO_DIR, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(robots)

    print(
        "  SEO: robots.txt + sitemap-index.xml + "
        + ", ".join(f"{lg}={len(entries[lg])}" for lg in LANGS)
    )


def patch_legacy_public_host_all():
    """Rewrite old Cloudflare Pages host → SITE_URL in HTML/XML/txt (canonical, hreflang, og, JSON-LD)."""
    from pathlib import Path as _Path

    new = SITE_URL.rstrip("/")
    exts = {".html", ".xml", ".txt"}
    n = 0
    for p in _Path(DEMO_DIR).rglob("*"):
        if not p.is_file() or p.suffix.lower() not in exts:
            continue
        try:
            t = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        t2 = t
        for old in LEGACY_PUBLIC_HOSTS:
            if old in t2:
                t2 = t2.replace(old, new)
        if t2 != t:
            p.write_text(t2, encoding="utf-8")
            n += 1
    if n:
        print(f"  SEO: migrated legacy host in {n} files → {new}")


def write_page(rel_path, html):
    """Write a page to the correct location."""
    full = DEMO_DIR + rel_path
    if full.endswith("/"): full += "index.html"
    elif not full.endswith(".html"):
        os.makedirs(full, exist_ok=True)
        full += "/index.html"
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(html)

def make_redirect(to_url):
    """Simple HTML redirect page."""
    return (f'<!DOCTYPE html><html><head>'
            f'<meta http-equiv="refresh" content="0;url={to_url}">'
            f'<link rel="canonical" href="{to_url}"></head>'
            f'<body><script>location.href="{to_url}";</script></body></html>')


ISLAND_GUIDES_DIR = os.path.join(CONTENT, "island_guides")

ISLAND_GUIDE_UI = {
    "en": {
        "read_in": "Read in:",
        "mins": "{n} min read",
        "share": "Share:",
        "copy": "Copy link",
        "related": "More island guides",
        "prev": "Previous",
        "next": "Next",
        "back": "Back to Island",
        "cta_h2": "Ready to surf at Ngor?",
        "cta_p": "Ngor Island, Dakar, Senegal. WhatsApp: +221 78 925 70 25",
        "book": "Book your stay",
        "who_lbl": "Who is this for?",
        "who_txt": "Visitors planning days on Ngor Island and Dakar.",
        "written": "Written by",
        "breadcrumb_home": "Home",
    },
    "fr": {
        "read_in": "Lire en :",
        "mins": "{n} min de lecture",
        "share": "Partager :",
        "copy": "Copier le lien",
        "related": "Autres guides île",
        "prev": "Précédent",
        "next": "Suivant",
        "back": "Retour à l'île",
        "cta_h2": "Prêt à surfer à Ngor ?",
        "cta_p": "Île de Ngor, Dakar, Sénégal. WhatsApp : +221 78 925 70 25",
        "book": "Réserver",
        "who_lbl": "Pour qui ?",
        "who_txt": "Voyageurs qui préparent un séjour sur l'île de Ngor et Dakar.",
        "written": "Rédigé par",
        "breadcrumb_home": "Accueil",
    },
    "es": {
        "read_in": "Leer en:",
        "mins": "{n} min de lectura",
        "share": "Compartir:",
        "copy": "Copiar enlace",
        "related": "Más guías de la isla",
        "prev": "Anterior",
        "next": "Siguiente",
        "back": "Volver a la isla",
        "cta_h2": "¿Listo para surfear en Ngor?",
        "cta_p": "Isla de Ngor, Dakar, Senegal. WhatsApp: +221 78 925 70 25",
        "book": "Reservar",
        "who_lbl": "¿Para quién es?",
        "who_txt": "Visitantes que planean días en la isla de Ngor y Dakar.",
        "written": "Escrito por",
        "breadcrumb_home": "Inicio",
    },
    "it": {
        "read_in": "Leggi in:",
        "mins": "{n} min di lettura",
        "share": "Condividi:",
        "copy": "Copia link",
        "related": "Altre guide all'isola",
        "prev": "Precedente",
        "next": "Successivo",
        "back": "Torna all'isola",
        "cta_h2": "Pronto a surfare a Ngor?",
        "cta_p": "Isola di Ngor, Dakar, Senegal. WhatsApp: +221 78 925 70 25",
        "book": "Prenota",
        "who_lbl": "Per chi è",
        "who_txt": "Visitatori che organizzano giorni a Ngor e Dakar.",
        "written": "Di",
        "breadcrumb_home": "Home",
    },
    "de": {
        "read_in": "Lesen auf:",
        "mins": "{n} Min. Lesezeit",
        "share": "Teilen:",
        "copy": "Link kopieren",
        "related": "Weitere Insel-Guides",
        "prev": "Zurück",
        "next": "Weiter",
        "back": "Zurück zur Insel",
        "cta_h2": "Bereit zum Surfen in Ngor?",
        "cta_p": "Ngor Island, Dakar, Senegal. WhatsApp: +221 78 925 70 25",
        "book": "Buchen",
        "who_lbl": "Für wen?",
        "who_txt": "Gäste, die Tage auf Ngor und in Dakar planen.",
        "written": "Von",
        "breadcrumb_home": "Start",
    },
    "nl": {
        "read_in": "Lezen in:",
        "mins": "{n} min. lezen",
        "share": "Delen:",
        "copy": "Link kopiëren",
        "related": "Meer eilandgidsen",
        "prev": "Vorige",
        "next": "Volgende",
        "back": "Terug naar het eiland",
        "cta_h2": "Klaar om te surfen in Ngor?",
        "cta_p": "Ngor Island, Dakar, Senegal. WhatsApp: +221 78 925 70 25",
        "book": "Boek je verblijf",
        "who_lbl": "Voor wie?",
        "who_txt": "Bezoekers die dagen op Ngor Island en Dakar plannen.",
        "written": "Geschreven door",
        "breadcrumb_home": "Home",
    },
    "ar": {
        "read_in": "اقرأ بـ:",
        "mins": "{n} دقائق قراءة",
        "share": "مشاركة:",
        "copy": "نسخ الرابط",
        "related": "المزيد من أدلة الجزيرة",
        "prev": "السابق",
        "next": "التالي",
        "back": "العودة إلى الجزيرة",
        "cta_h2": "هل أنت مستعد لركوب الأمواج في نغور؟",
        "cta_p": "جزيرة نغور، داكار، السنغال. واتساب: +221 78 925 70 25",
        "book": "احجز إقامتك",
        "who_lbl": "لمن هذا الدليل؟",
        "who_txt": "الزوار الذين يخططون لأيام في جزيرة نغور وداكار.",
        "written": "كتبه",
        "breadcrumb_home": "الرئيسية",
    },
}

ISLAND_HUB_GUIDES_SECTION = {
    "en": {"lbl": "Guides", "h2": "Plan your time on Ngor", "sub": "Deep dives written with local guides — from pirogue crossings to hidden surf spots and the best fish shacks."},
    "fr": {"lbl": "Guides", "h2": "Organisez votre temps à Ngor", "sub": "Guides détaillés rédigés avec les locaux — traversées en pirogue, spots cachés et meilleures baraques à poisson."},
    "es": {"lbl": "Guías", "h2": "Organiza tu tiempo en Ngor", "sub": "Guías escritas con los locales — cruces en piragua, spots secretos y los mejores chiringuitos de pescado."},
    "it": {"lbl": "Guide", "h2": "Organizza il tuo tempo a Ngor", "sub": "Guide scritte con operatori locali — traversate in piroga, spot nascosti e le migliori baracchine di pesce."},
    "de": {"lbl": "Guides", "h2": "Plant eure Zeit auf Ngor", "sub": "Mit lokalen Guides erstellt — Pirogenüberfahrten, versteckte Surfspots und die besten Fischbuden."},
    "nl": {"lbl": "Gidsen", "h2": "Plan je tijd op Ngor", "sub": "Geschreven met lokale gidsen — pirogevaarten, verborgen surfspots en de beste viskraampjes."},
    "ar": {"lbl": "الأدلة", "h2": "خطط لوقتك في نغور", "sub": "أدلة متعمقة مع نصائح الزوار المحدثة."},
}

AUTHOR_ISLAND = {
    "en": ("Sophie Renard", "Surf Travel Writer", "Freelance surf journalist based in France; focused on West Africa and warm-water destinations."),
    "fr": ("Sophie Renard", "Journaliste surf voyage", "Journaliste surf indépendante, spécialisée en Afrique de l'Ouest et destinations chaudes."),
    "es": ("Sophie Renard", "Periodista de surf y viajes", "Periodista independiente centrada en África Occidental y olas cálidas."),
    "it": ("Sophie Renard", "Giornalista surf e viaggi", "Giornalista freelance con focus su Africa occidentale e onde calde."),
    "de": ("Sophie Renard", "Surf-Reisejournalistin", "Freie Journalistin mit Schwerpunkt Westafrika und warmen Surfspots."),
    "nl": ("Sophie Renard", "Surf- en reisschrijfster", "Freelance surfjouraliste gericht op West-Afrika en warmwaterdestinaties."),
    "ar": ("Sophie Renard", "كاتبة سفر وركوب أمواج", "صحفية سفر متخصصة في غرب أفريقيا ووجهات الأمواج الدافئة."),
}


def island_guide_href_path(lang, guide):
    pfx = LANG_PFX[lang]
    isl = SLUG[lang]["island"]
    slug = guide["slugs"][lang]
    path = f"{pfx}/{isl}/{slug}/".replace("//", "/")
    if not path.startswith("/"):
        path = "/" + path
    return path


def load_island_guides():
    m = load(os.path.join(CONTENT, "island_guides_manifest.json"))
    if not m:
        return []
    guides = []
    for fn in m.get("guides", []):
        g = load(os.path.join(ISLAND_GUIDES_DIR, fn))
        if g and g.get("slugs"):
            guides.append(g)
    return guides


def _island_faq_json_ld(faq_schema, page_title):
    if not faq_schema:
        return ""
    ent = []
    for item in faq_schema:
        ent.append(
            {
                "@type": "Question",
                "name": item.get("q", ""),
                "acceptedAnswer": {"@type": "Answer", "text": item.get("a", "")},
            }
        )
    doc = {"@context": "https://schema.org", "@type": "FAQPage", "name": page_title, "mainEntity": ent}
    return json.dumps(doc, ensure_ascii=False)


def _island_faq_html(faq_schema):
    if not faq_schema:
        return ""
    blocks = []
    for i, item in enumerate(faq_schema, 1):
        q = item.get("q", "")
        a = item.get("a", "")
        blocks.append(
            f'<div class="article-faq-item" itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">'
            f'<button class="article-faq-q" data-num="{i}" onclick="toggleArticleFaq(this)" aria-expanded="false">'
            f'<span itemprop="name">{escape(fix_em(q))}</span>'
            f'<span class="faq-a-chevron"><svg viewBox="0 0 16 16" fill="none" width="14" height="14" '
            f'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
            f'<path d="M4 6l4 4 4-4"/></svg></span></button>'
            f'<div class="article-faq-answer" itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">'
            f'<div class="faq-answer-inner"><p itemprop="text">{escape(fix_em(a))}</p></div></div></div>'
        )
    return (
        '<div class="article-faq-section island-guide-faq" itemscope itemtype="https://schema.org/FAQPage">'
        + "".join(blocks)
        + "</div>"
    )


def _island_article_json_ld(guide, lang, loc, title, meta_desc, hero_url, date_pub):
    return json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": title,
            "description": meta_desc,
            "image": hero_url,
            "datePublished": date_pub,
            "author": {"@type": "Person", "name": AUTHOR_ISLAND[lang][0]},
            "publisher": {
                "@type": "Organization",
                "name": "Ngor Surfcamp Teranga",
                "logo": {"@type": "ImageObject", "url": LOGO},
            },
            "mainEntityOfPage": {"@type": "WebPage", "@id": loc},
        },
        ensure_ascii=False,
    )


def build_island_guide_page(guide, lang, all_guides, guide_index):
    L = guide["locales"][lang]
    ui = ISLAND_GUIDE_UI[lang]
    pfx = LANG_PFX[lang]
    book_href = f"{pfx}/{SLUG[lang]['booking']}/"
    if not book_href.startswith("/"):
        book_href = "/" + book_href.lstrip("/")
    island_hub = f"{pfx}/{SLUG[lang]['island']}/".replace("//", "/")
    if not island_hub.startswith("/"):
        island_hub = "/" + island_hub.lstrip("/")

    title = fix_em(L["title"])
    meta_d = fix_em(L["meta_description"])
    h1 = fix_em(L["h1"])
    deck = (L.get("deck") or "").strip()
    cat = escape(fix_em(L.get("category_label", "Island Guide")))
    hero_base = guide.get("hero_basename", guide["slugs"]["en"])
    hero_rel = f"/assets/images/bw-{hero_base}.webp"
    hero_abs = f"{SITE_URL.rstrip('/')}{hero_rel}"
    path_here = island_guide_href_path(lang, guide)
    canonical = f"{SITE_URL.rstrip('/')}{path_here}"

    href_lines = [
        f'<link rel="canonical" href="{escape(canonical)}">',
        f'<link rel="alternate" hreflang="x-default" href="{escape(SITE_URL.rstrip("/") + island_guide_href_path("en", guide))}">',
    ]
    for lg in LANGS:
        u = SITE_URL.rstrip("/") + island_guide_href_path(lg, guide)
        href_lines.append(f'<link rel="alternate" hreflang="{LANG_LOCALE[lg]}" href="{escape(u)}">')

    lang_switch = {lg: island_guide_href_path(lg, guide) for lg in LANGS}

    md = L.get("content_markdown", "")
    rt = L.get("reading_minutes")
    if rt is None:
        rt = max(5, min(25, len(md.split()) // 200))

    body_html = md2html_island(md, lang, ICONS_DIR, ICO_BASE)
    faq_schema = L.get("faq_schema") or []
    faq_html = _island_faq_html(faq_schema)
    faq_ld = _island_faq_json_ld(faq_schema, L["h1"])
    art_ld = _island_article_json_ld(
        guide, lang, canonical, L["title"], L["meta_description"], hero_abs, guide.get("date_published", "2026-03-27")
    )

    island_name = {"en": "Island", "fr": "Île", "es": "Isla", "it": "Isola", "de": "Insel", "nl": "Eiland", "ar": "جزيرة"}.get(lang, "Island")
    crumb_title = escape(fix_em(L["h1"]))[:72]
    if len(L["h1"]) > 72:
        crumb_title += "…"

    pills = ""
    for lg in LANGS:
        u = island_guide_href_path(lg, guide)
        active = " active" if lg == lang else ""
        pills += (
            f'<a href="{u}" class="lang-pill{active}" hreflang="{LANG_LOCALE[lg]}">{flag(lg, 16)} {LANG_NAMES[lg]}</a> '
        )

    aname, arole, abio = AUTHOR_ISLAND[lang]
    author_html = (
        f'<div class="author-card reveal"><img src="/assets/images/author-sophie-renard.webp" alt="{escape(aname)}" '
        f'class="author-avatar" loading="lazy" width="64" height="64"><div>'
        f'<div style="font-size:11px;color:#9ca3af;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:4px">'
        f'{escape(ui["written"])}</div>'
        f'<div class="author-name">{escape(aname)}</div>'
        f'<div class="author-role">{escape(arole)}</div>'
        f'<div class="author-bio-text">{escape(fix_em(abio))}</div></div></div>'
    )

    others = [g for i, g in enumerate(all_guides) if i != guide_index][:2]
    rel_cards = ""
    for og in others:
        ol = og["locales"][lang]
        ou = island_guide_href_path(lang, og)
        hb = og.get("hero_basename", og["slugs"]["en"])
        ocb = escape(fix_em(ol.get("category_label", "Island Guide")))
        rel_cards += (
            f'<a href="{ou}" class="card" style="text-decoration:none">'
            f'<img src="/assets/images/bw-{hb}.webp" alt="{escape(fix_em(ol["h1"]))}" class="card-img" loading="lazy" width="800" height="530" decoding="async">'
            f'<div class="card-body"><span class="cat-badge island-guide-badge">{ocb}</span>'
            f'<h3 class="card-h3" style="font-size:15px;margin-top:8px">{escape(fix_em(ol["h1"]))}</h3></div></a>'
        )

    prev_html = next_html = ""
    if guide_index > 0:
        pg = all_guides[guide_index - 1]
        pl = pg["locales"][lang]
        prev_html = (
            f'<a href="{island_guide_href_path(lang, pg)}" class="art-nav-item ">'
            f'<span class="art-nav-dir">← {escape(ui["prev"])}</span>'
            f'<span class="art-nav-title">{escape(fix_em(pl["h1"]))}</span></a>'
        )
    if guide_index < len(all_guides) - 1:
        ng = all_guides[guide_index + 1]
        nl = ng["locales"][lang]
        next_html = (
            f'<a href="{island_guide_href_path(lang, ng)}" class="art-nav-item next">'
            f'<span class="art-nav-dir">{escape(ui["next"])} →</span>'
            f'<span class="art-nav-title">{escape(fix_em(nl["h1"]))}</span></a>'
        )

    scripts_ld = ""
    if faq_ld:
        scripts_ld += f'<script type="application/ld+json">\n{faq_ld}\n</script>\n'
    scripts_ld += f'<script type="application/ld+json">\n{art_ld}\n</script>'

    _iloc = LANG_LOCALE.get(lang, lang)
    _idir = ' dir="rtl"' if lang == "ar" else ""
    _ifont = (
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@400;600;700&display=swap">\n'
        if lang == "ar"
        else ""
    )
    html = f"""<!DOCTYPE html>
<html lang="{_iloc}"{_idir}><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
{_ifont}<title>{escape(title)}</title>
<meta name="description" content="{escape(meta_d)}">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(meta_d)}">
<meta property="og:image" content="{escape(hero_abs)}">
<meta property="og:type" content="article">
<meta name="robots" content="index,follow">
{chr(10).join(href_lines)}


<link rel="preload" href="{hero_rel}" as="image" fetchpriority="high">
<link rel="preload" href="https://fonts.googleapis.com/css2?family=Raleway:ital,wght@0,400;0,700;0,800;0,900;1,400&family=Inter:wght@400;500;600&display=swap" as="style" onload="this.onload=null;this.rel='stylesheet'">
<noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Raleway:ital,wght@0,400;0,700;0,800;0,900;1,400&family=Inter:wght@400;500;600&display=swap"></noscript>
<link rel="stylesheet" href="/assets/css/{ASSET_CSS_MAIN}?v={ASSET_VERSION}">
<script src="/assets/js/{ASSET_JS_MAIN}?v={ASSET_VERSION}" defer></script>
{scripts_ld}
</head><body>
<div id="scroll-progress"></div>
<div id="art-progress"><div id="art-progress-fill"></div></div>
{build_nav("island", lang, lang_switch)}
<main>
  <article itemscope itemtype="https://schema.org/Article">
    <header class="article-hero island-guide-hero" style="background-image:url('{escape(hero_rel)}')" aria-label="{escape(h1)}">
      <div class="art-hero-inner">
        <p style="margin-bottom:12px"><span class="cat-badge island-guide-badge">{cat}</span></p>
        <h1 style="font-size:clamp(22px,4vw,52px);margin-bottom:12px;text-shadow:0 2px 16px rgba(0,0,0,0.3)" itemprop="headline">{escape(h1)}</h1>
        {f'<p style="max-width:640px;margin:0 auto 8px;opacity:0.95;font-size:clamp(15px,2vw,18px);line-height:1.5">{escape(deck)}</p>' if deck else ''}
        <div class="reading-meta"><span>⏱ {escape(ui["mins"].replace("{n}", str(rt)))}</span><span>📍 {escape(ui_chrome("reading_loc", lang))}</span></div>
      </div>
    </header>
    <div class="container" style="padding:48px 24px 80px">
      <nav class="breadcrumb" aria-label="{escape(ui_chrome('breadcrumb', lang))}"><a href="{(pfx + "/") if pfx else "/"}">{escape(ui["breadcrumb_home"])}</a><span>›</span><a href="{island_hub}">{escape(island_name)}</a><span>›</span><span>{crumb_title}</span></nav>
      <div class="art-lang-bar"><span class="lbl">{escape(ui["read_in"])}</span>{pills}</div>
      <div class="persona-bar"><span class="persona-bar-label">{escape(ui["who_lbl"])}</span><span style="font-size:14px;color:#374151">{escape(ui["who_txt"])}</span></div>
      {author_html}
      <div class="prose island-guide-prose" itemprop="articleBody">{body_html}
      {faq_html}
      </div>
      <div class="share-row">
        <span class="share-label">{escape(ui["share"])}</span>
        <button type="button" class="share-btn share-wa" onclick="shareWA()" style="display:inline-flex;align-items:center;gap:7px"><span style="display:inline-flex">{WA_ICO}</span> {escape(ui_chrome("wa", lang))}</button>
        <button type="button" class="share-btn share-copy" onclick="copyURL()">{escape(ui["copy"])}</button>
        <span class="copy-success">{escape(ui_chrome("copy_ok", lang))}</span>
      </div>
      <div class="art-cta" style="position:relative">
        <div style="position:relative;z-index:1">
          <h2 style="font-size:24px;margin-bottom:10px">{escape(ui["cta_h2"])}</h2>
          <p style="opacity:0.82;margin-bottom:28px;font-size:15px;max-width:480px;margin-left:auto;margin-right:auto">{escape(ui["cta_p"])}</p>
          <div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap">
            <a href="{book_href}" class="btn btn-fire btn-lg">{escape(ui["book"])}</a>
            <a href="https://wa.me/221789257025" target="_blank" rel="noopener" class="btn btn-glass btn-lg"><span style="display:inline-flex">{WA_ICO}</span> {escape(ui_chrome("wa", lang))}</a>
          </div>
        </div>
      </div>
      <div style="margin-top:64px"><h2 style="font-size:20px;margin-bottom:22px">{escape(ui["related"])}</h2><div class="related-grid">{rel_cards}</div></div>
      <div style="margin-top:48px"><a href="{island_hub}" class="btn btn-deep" style="display:inline-flex;align-items:center;gap:8px">← {escape(ui["back"])}</a></div>
    </div>
  </article>
</main>
{footer_quotes_block(lang)}
{build_footer(lang)}
{page_close()}
"""
    return html


def build_island_hub_guides_html(lang, guides):
    """Cards linking to localized island guide URLs."""
    if not guides:
        return ""
    ui = ISLAND_HUB_GUIDES_SECTION[lang]
    pfx = LANG_PFX[lang]
    blog_href = (pfx + "/" + SLUG[lang]["blog"] + "/").replace("//", "/")
    if not blog_href.startswith("/"):
        blog_href = "/" + blog_href.lstrip("/")
    cards = []
    for g in guides:
        L = g["locales"][lang]
        u = island_guide_href_path(lang, g)
        hb = g.get("hero_basename", g["slugs"]["en"])
        cards.append(
            f'<a href="{u}" class="card island-guide-card" style="text-decoration:none">'
            f'<img src="/assets/images/bw-{hb}.webp" alt="" class="card-img" loading="lazy" width="400" height="240">'
            f'<div class="card-body"><span class="cat-badge island-guide-badge">{escape(fix_em(L.get("category_label", "Guide")))}</span>'
            f'<h3 class="card-h3">{escape(fix_em(L["h1"]))}</h3>'
            f'<p class="card-text">{escape(fix_em(L.get("card_teaser", L["meta_description"][:140])))}</p></div></a>'
        )
    return (
        f'<section class="section sec-light island-guides-hub-section" id="island-guides">'
        f'<div class="container"><div style="text-align:center;margin-bottom:44px" class="reveal">'
        f'<span class="s-label">{escape(fix_em(ui["lbl"]))}</span>'
        f'<h2 class="s-title">{escape(fix_em(ui["h2"]))}</h2>'
        f'<p class="s-sub" style="max-width:640px;margin:12px auto 0">{escape(fix_em(ui["sub"]))}</p></div>'
        f'<div class="grid-3 reveal">{"".join(cards)}</div>'
        f'<p style="text-align:center;margin-top:28px"><a href="{blog_href}" class="btn btn-ocean">{escape({"en":"Visit the blog","fr":"Voir le blog","es":"Ver el blog","it":"Vai al blog","de":"Zum Blog"}[lang])}</a></p>'
        f"</div></section>"
    )


def patch_island_hub_guides_section(guides):
    """Inject or replace guides block on all localized island hub pages."""
    if not guides:
        return
    paths = [
        ("island/index.html", "en"),
        ("fr/ile/index.html", "fr"),
        ("es/isla/index.html", "es"),
        ("it/isola/index.html", "it"),
        ("de/insel/index.html", "de"),
    ]
    start_m = "<!--ISLAND_GUIDES_BLOCK_START-->"
    end_m = "<!--ISLAND_GUIDES_BLOCK_END-->"
    for rel, lang in paths:
        fp = os.path.join(DEMO_DIR, rel)
        if not os.path.isfile(fp):
            continue
        with open(fp, encoding="utf-8", errors="replace") as f:
            h = f.read()
        block = start_m + "\n" + build_island_hub_guides_html(lang, guides) + "\n" + end_m
        if start_m in h and end_m in h:
            h = re.sub(re.escape(start_m) + r"[\s\S]*?" + re.escape(end_m), block, h, count=1)
        else:
            needle = "  </section>\n  <div style=\"background:var(--navy);padding:48px 0\">"
            if needle in h:
                h = h.replace(
                    needle,
                    "  </section>\n" + block + "\n  <div style=\"background:var(--navy);padding:48px 0\">",
                    1,
                )
            else:
                continue
        with open(fp, "w", encoding="utf-8") as f:
            f.write(h)


def patch_waves_all_pages():
    """Add wave dividers sitewide on every page that transitions between color zones.

    Rules applied to every HTML file:
    1. white/light → footer-quotes (navy)  → wave_bottom before .footer-quotes
    2. white/light → .cta-band (navy)      → wave_bottom before .cta-band  (only if no wave already)
    3. white → sec-light sections           → wave_top / wave_bottom between them

    The patch is idempotent: existing waves are stripped first then re-inserted.
    Pages rebuilt by build.py already have correct waves in their template, so they
    skip the generic rules but still get the footer-quotes wave if missing.
    """
    import re as _re

    WAVE_RE = _re.compile(r'\s*<div class="wave-(?:top|bottom)"[^>]*>.*?</div>', _re.DOTALL)
    WAVE_DIV_RE = _re.compile(r'\s*<div[^>]*class="[^"]*wave-divider[^"]*"[^>]*>.*?</div>', _re.DOTALL)

    def _strip_waves(h):
        h = WAVE_RE.sub('', h)
        h = WAVE_DIV_RE.sub('', h)
        return h

    # Section class → background colour token
    def _sec_bg(cls):
        if 'sec-dark' in cls or 'cta-band' in cls or 'reviews-section' in cls:
            return _BG_NAVY
        if 'sec-sand' in cls:
            return _BG_SAND
        if 'sec-light' in cls:
            return _BG_LIGHT
        return _BG_WHITE

    n = 0
    for root, dirs, files in os.walk(DEMO_DIR):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
        for fn in files:
            if not fn.endswith('.html'):
                continue
            path = os.path.join(root, fn)
            try:
                with open(path, encoding='utf-8', errors='replace') as f:
                    h = f.read()
            except OSError:
                continue

            # Remove existing waves so we can re-apply cleanly
            h = _strip_waves(h)

            changed = False

            # ── Rule 1: insert wave_bottom before footer-quotes ──────────
            # footer-quotes is always navy. Content above is white or light.
            FQ_MARKER = '<div class="footer-quotes"'
            if FQ_MARKER in h:
                # Detect what's just above: look for last section class in main content
                idx = h.find(FQ_MARKER)
                preceding = h[max(0, idx-2500):idx]
                if 'cta-band' not in preceding:
                    if 'sec-light' in preceding or 'sec-sand' in preceding:
                        prev_bg = _BG_LIGHT
                    else:
                        prev_bg = _BG_WHITE
                    wave_html = '\n' + wave_bottom(prev_bg, _BG_NAVY) + '\n'
                    h = h.replace(FQ_MARKER, wave_html + FQ_MARKER, 1)
                    changed = True

            # ── Rule 2: insert wave_bottom before .cta-band ──────────────
            CTA_MARKER = '<div class="cta-band"'
            if CTA_MARKER in h:
                idx = h.find(CTA_MARKER)
                preceding = h[max(0, idx-400):idx]
                if 'sec-light' in preceding:
                    prev_bg = _BG_LIGHT
                else:
                    prev_bg = _BG_WHITE
                wave_html = '\n' + wave_bottom(prev_bg, _BG_NAVY) + '\n'
                h = h.replace(CTA_MARKER, wave_html + CTA_MARKER, 1)
                changed = True

            # ── Rule 3: waves between alternating white/sec-light sections ──
            # Find all <section ...> tags and insert waves between colour changes
            sec_tags = list(_re.finditer(
                r'(<section\b[^>]*class="([^"]*)"[^>]*>)',
                h
            ))
            if len(sec_tags) >= 2:
                # Process in reverse order so indices stay valid
                for i in range(len(sec_tags) - 1, 0, -1):
                    prev_cls = sec_tags[i-1].group(2)
                    curr_cls = sec_tags[i].group(2)
                    prev_bg = _sec_bg(prev_cls)
                    curr_bg = _sec_bg(curr_cls)
                    if prev_bg == curr_bg or curr_bg == _BG_NAVY:
                        continue  # same bg or going to navy (handled elsewhere)
                    # Insert wave_top before this section
                    pos = sec_tags[i].start()
                    wave_html = wave_top(curr_bg, prev_bg) + '\n  '
                    h = h[:pos] + wave_html + h[pos:]
                    changed = True

                # Rebuild sec_tags positions after insertions
                # Also add wave_bottom at end of each sec-light that's followed by white
                # (simpler: skip this for now — wave_top on next section is enough)

            if changed:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(h)
                n += 1

    print(f'  waves sitewide: patched {n} HTML files')


def patch_lang_switcher_all():
    """Fix language-switcher (lang-dd) dropdown across all static pages so it links
    to the SAME page in each language rather than a home page.

    Covers:
    - Blog articles   : same EN slug used in all lang prefixes
    - Blog index      : /blog/ → /fr/blog/ etc.
    - FAQ pages       : /faq/ → /fr/faq/ etc.
    - Privacy pages   : already correct (rebuilt)
    - Island guides   : already correct (rebuilt)
    - Getting-here    : already patched separately
    - Home/Nav pages  : already correct (rebuilt)
    """
    import re as _re

    # Build the lang-dd-menu HTML for a given mapping {lang → href}
    def _lang_menu(current_lang, href_map):
        opts = []
        for lg in ALL_LANGS:
            if lg == current_lang:
                continue
            href = href_map.get(lg, LANG_PFX[lg] + "/")
            if not href.startswith("/"):
                href = "/" + href
            opts.append(
                f'<a class="lang-dd-item" href="{href}" hreflang="{LANG_LOCALE[lg]}" role="menuitem">'
                f'{flag(lg, 18)} {LANG_NAMES[lg]}</a>'
            )
        return '<div class="lang-dd-menu" role="menu">' + "".join(opts) + "</div>"

    LANG_DD_MENU_RE = _re.compile(
        r'<div class="lang-dd-menu"[^>]*>.*?</div>',
        _re.DOTALL,
    )

    n = 0
    for root, dirs, files in os.walk(DEMO_DIR):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "node_modules"]
        for fn in files:
            if fn != "index.html":
                continue
            path = os.path.join(root, fn)
            rel = os.path.relpath(path, DEMO_DIR).replace("\\", "/")
            parts = rel.split("/")  # e.g. ['es', 'blog', 'learn-to-surf', 'index.html']

            # Determine lang and page type from path
            lang = parts[0] if parts[0] in LANGS and parts[0] != "en" else "en"
            rest = parts[1:] if lang != "en" else parts  # drop lang prefix
            # rest[0] is the section, rest[1] is the slug (if article), rest[-1] is index.html

            href_map = None

            # ── Home: index.html or {lang}/index.html ──
            if rest == ["index.html"]:
                href_map = {}
                for lg in LANGS:
                    href_map[lg] = LANG_PFX[lg] + "/" if LANG_PFX[lg] else "/"

            # ── Surfing / surf house / gallery / booking / island / privacy ──
            elif len(rest) == 2 and rest[-1] == "index.html":
                page_dir = rest[0]
                # Map localized path back to EN slug key
                matched_key = None
                for key in SLUG.get("en", {}):
                    if any(SLUG[lg].get(key) == page_dir for lg in LANGS):
                        matched_key = key
                        break
                if matched_key:
                    href_map = {}
                    for lg in LANGS:
                        pfx = LANG_PFX[lg]
                        s = SLUG[lg].get(matched_key, SLUG["en"].get(matched_key, page_dir))
                        href_map[lg] = f"{pfx}/{s}/" if pfx else f"/{s}/"

            # ── Blog article: {lang}/blog/{slug}/index.html ──
            if rest[:1] == ["blog"] and len(rest) >= 3 and rest[-1] == "index.html" and href_map is None:
                # Check if this is a category page: blog/{cat_word}/{cat_slug}/index.html
                cat_words = {SLUG[lg]["category"]: lg for lg in LANGS}
                if len(rest) == 4 and rest[1] in cat_words:
                    # Category page: find the EN cat name from slug
                    cat_slug_in_url = rest[2]
                    # Find matching BLOG_CATS entry
                    matched_cat_en = None
                    for _cen, _cdata in BLOG_CATS.items():
                        if _cdata["slug"].get(lang) == cat_slug_in_url:
                            matched_cat_en = _cen
                            break
                    if matched_cat_en:
                        href_map = {}
                        for lg in LANGS:
                            href_map[lg] = CAT_PAGE_HREF[(matched_cat_en, lg)]
                    else:
                        href_map = {lg: f"{LANG_PFX[lg]}/blog/" for lg in LANGS}
                else:
                    slug = rest[1]
                    href_map = {}
                    for lg in LANGS:
                        pfx = LANG_PFX[lg]
                        href_map[lg] = f"{pfx}/blog/{slug}/" if pfx else f"/blog/{slug}/"

            # ── Blog index: {lang}/blog/index.html ──
            elif rest[:1] == ["blog"] and len(rest) == 2 and rest[-1] == "index.html":
                href_map = {}
                for lg in LANGS:
                    pfx = LANG_PFX[lg]
                    href_map[lg] = f"{pfx}/blog/" if pfx else "/blog/"

            # ── FAQ: {lang}/faq/index.html ──
            elif len(rest) == 2 and rest[-1] == "index.html" and any(
                rest[0] == SLUG[lg].get("faq", "faq") for lg in LANGS
            ):
                href_map = {}
                for lg in LANGS:
                    pfx = LANG_PFX[lg]
                    faq_slug = SLUG[lg].get("faq", "faq")
                    href_map[lg] = f"{pfx}/{faq_slug}/" if pfx else f"/{faq_slug}/"

            if href_map is None:
                continue  # not a page type we need to fix

            try:
                with open(path, encoding="utf-8", errors="replace") as f:
                    h = f.read()
            except OSError:
                continue

            if 'id="lang-dd"' not in h:
                continue

            new_menu = _lang_menu(lang, href_map)
            h2, cnt = LANG_DD_MENU_RE.subn(new_menu, h, count=1)
            if cnt and h2 != h:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(h2)
                n += 1

    print(f"  lang-switcher: fixed {n} HTML files")


def _parse_index_html_rel(rel_path):
    """Return (lang, path_segments) for .../index.html under DEMO_DIR, or None."""
    rel_path = rel_path.replace("\\", "/")
    if not rel_path.endswith("index.html"):
        return None
    inner = rel_path[: -len("index.html")].strip("/")
    if not inner:
        return "en", []
    parts = inner.split("/")
    if parts[0] in LANGS:
        return parts[0], parts[1:]
    return "en", parts


def _normalize_site_path(path):
    if not path.startswith("/"):
        path = "/" + path
    if not path.endswith("/"):
        path += "/"
    return path.replace("//", "/")


def hreflang_paths_for_index(rel_path, island_guides):
    """Map lang → path (leading /, trailing /) for this page cluster, or None."""
    parsed = _parse_index_html_rel(rel_path)
    if not parsed:
        return None
    lang, segs = parsed

    if len(segs) == 0:
        return {lg: _normalize_site_path(LANG_PFX[lg] + "/") for lg in LANGS}

    if len(segs) == 1 and segs[0] == GETTING_HERE_SEGMENT.get(lang):
        return {lg: _normalize_site_path(GETTING_HERE_FLAG_HREF[lg]) for lg in LANGS}

    if len(segs) == 1:
        matched_key = None
        for key in SLUG.get("en", {}):
            if any(SLUG[lg].get(key) == segs[0] for lg in LANGS):
                matched_key = key
                break
        if matched_key:
            return {
                lg: _normalize_site_path(f"{LANG_PFX[lg]}/{SLUG[lg][matched_key]}/")
                for lg in LANGS
            }

    if len(segs) == 1 and segs[0] == SLUG[lang]["blog"]:
        return {lg: _normalize_site_path(f"{LANG_PFX[lg]}/{SLUG[lg]['blog']}/") for lg in LANGS}

    if len(segs) == 2 and segs[0] == SLUG[lang]["blog"]:
        slug = segs[1]
        return {
            lg: _normalize_site_path(f"{LANG_PFX[lg]}/{SLUG[lg]['blog']}/{slug}/")
            for lg in LANGS
        }

    if (
        len(segs) == 3
        and segs[0] == SLUG[lang]["blog"]
        and segs[1] == SLUG[lang]["category"]
    ):
        cat_slug_in_url = segs[2]
        matched_cat_en = None
        for _cen, _cdata in BLOG_CATS.items():
            if _cdata["slug"].get(lang) == cat_slug_in_url:
                matched_cat_en = _cen
                break
        if matched_cat_en:
            return {lg: _normalize_site_path(CAT_PAGE_HREF[(matched_cat_en, lg)]) for lg in LANGS}

    if len(segs) == 2 and segs[0] == SLUG[lang]["island"]:
        gslug = segs[1]
        for g in island_guides:
            if g.get("slugs", {}).get(lang) == gslug:
                return {lg: island_guide_href_path(lg, g) for lg in LANGS}

    return None


def _find_seo_link_cluster_span(html):
    """Start/end slice covering canonical + following alternate link tags."""
    import re as _re

    m = _re.search(r"<link\s+rel=[\"']canonical[\"'][^>]*>", html, _re.I)
    if not m:
        return None
    start = m.start()
    pos = m.end()
    while True:
        m2 = _re.match(r"\s*<link\s+rel=[\"']alternate[\"'][^>]*>", html[pos:], _re.I)
        if not m2:
            break
        pos += m2.end()
    return start, pos


def _render_seo_link_cluster(paths_by_lang, page_lang):
    base = SITE_URL.rstrip("/")

    def full_url(path):
        p = path if path.startswith("/") else "/" + path
        if not p.endswith("/"):
            p += "/"
        p = p.replace("//", "/")
        return base + p

    canon = full_url(paths_by_lang[page_lang])
    en_u = full_url(paths_by_lang["en"])
    lines = [
        f'<link rel="canonical" href="{escape(canon)}">',
        f'<link rel="alternate" hreflang="x-default" href="{escape(en_u)}">',
        f'<link rel="alternate" hreflang="en" href="{escape(en_u)}">',
    ]
    for lg in ["fr", "es", "it", "de", "nl", "ar"]:
        lines.append(
            f'<link rel="alternate" hreflang="{LANG_LOCALE[lg]}" href="{escape(full_url(paths_by_lang[lg]))}">'
        )
    return "\n".join(lines)


def patch_hreflang_canonical_all_pages():
    """Rewrite canonical + hreflang clusters so every locale cross-links (bidirectional SEO)."""
    guides = load_island_guides()
    n = 0
    skip = 0
    from pathlib import Path as _Path

    for html_path in _Path(DEMO_DIR).rglob("index.html"):
        rel = html_path.relative_to(_Path(DEMO_DIR)).as_posix()
        if rel.startswith("admin/") or "/admin/" in rel:
            continue
        pmap = hreflang_paths_for_index(rel, guides)
        if not pmap:
            skip += 1
            continue
        parsed = _parse_index_html_rel(rel)
        if not parsed:
            continue
        page_lang, _ = parsed
        block = _render_seo_link_cluster(pmap, page_lang)
        try:
            with open(html_path, encoding="utf-8", errors="replace") as f:
                h = f.read()
        except OSError:
            continue
        span = _find_seo_link_cluster_span(h)
        if not span:
            skip += 1
            continue
        a, b = span
        h2 = h[:a] + block + h[b:]
        if h2 != h:
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(h2)
            n += 1
    print(f"  hreflang/canonical: patched {n} pages (skipped {skip} non-cluster or no canonical)")


def patch_target_blank_rel_all():
    """Ensure every target=_blank link has rel=noopener noreferrer."""
    import re as _re
    from pathlib import Path as _Path

    def _add_missing_rel(html):
        return _re.sub(
            r'(<a\b[^>]*\btarget="_blank")(?![^>]*\brel=)',
            r'\1 rel="noopener noreferrer"',
            html,
            flags=_re.I,
        )

    rel_pat = _re.compile(
        r'(<a\b[^>]*\btarget="_blank"[^>]*\brel=)(["\'])([^"\']*)(\2)',
        _re.I,
    )

    def _normalize_rel(html):
        def repl(m):
            prefix, quote, rel_value, _ = m.groups()
            tokens = [t for t in rel_value.split() if t]
            lower = {t.lower() for t in tokens}
            if "noopener" not in lower:
                tokens.append("noopener")
            if "noreferrer" not in lower:
                tokens.append("noreferrer")
            return f'{prefix}{quote}{" ".join(tokens)}{quote}'

        return rel_pat.sub(repl, html)

    touched = 0
    for html_path in _Path(DEMO_DIR).rglob("*.html"):
        try:
            h = html_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        h2 = _normalize_rel(_add_missing_rel(h))
        if h2 != h:
            try:
                html_path.write_text(h2, encoding="utf-8")
                touched += 1
            except OSError:
                continue
    print(f"  target=_blank rel hardening: touched {touched} HTML files")


def verify_hreflang_alternate_count():
    """Lightweight post-build check: expect 8 alternate hreflang links when canonical exists."""
    import re as _re

    alt_n = _re.compile(r"<link\s+rel=[\"']alternate[\"'][^>]*hreflang=", _re.I)
    problems = []
    from pathlib import Path as _Path

    for html_path in _Path(DEMO_DIR).rglob("index.html"):
        rel = str(html_path.relative_to(_Path(DEMO_DIR)))
        if "admin/" in rel.replace("\\", "/"):
            continue
        try:
            h = html_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if "rel=\"canonical\"" not in h and "rel='canonical'" not in h:
            continue
        n_alt = len(alt_n.findall(h))
        if n_alt != 8:
            problems.append((rel, n_alt))
    if problems:
        sample = problems[:12]
        print(f"  hreflang verify: {len(problems)} pages without exactly 8 alternates (sample: {sample})")
    else:
        print("  hreflang verify: OK (8 alternates on pages with canonical)")


def patch_footer_bottom_pp_all():
    """Ensure every page footer-bottom has the full copyright + Privacy Policy link."""
    COPY_SHORT = {
        "en": "© 2025 Ngor Surfcamp Teranga.",
        "fr": "© 2025 Ngor Surfcamp Teranga.",
        "es": "© 2025 Ngor Surfcamp Teranga.",
        "it": "© 2025 Ngor Surfcamp Teranga.",
        "de": "© 2025 Ngor Surfcamp Teranga.",
    }
    COPY_FULL = {
        "en": "© 2025 Ngor Surfcamp Teranga. All rights reserved.",
        "fr": "© 2025 Ngor Surfcamp Teranga. Tous droits réservés.",
        "es": "© 2025 Ngor Surfcamp Teranga. Todos los derechos reservados.",
        "it": "© 2025 Ngor Surfcamp Teranga. Tutti i diritti riservati.",
        "de": "© 2025 Ngor Surfcamp Teranga. Alle Rechte vorbehalten.",
    }
    PP_LBL = {
        "en": "Privacy Policy",
        "fr": "Politique de confidentialité",
        "es": "Política de privacidad",
        "it": "Informativa sulla privacy",
        "de": "Datenschutzrichtlinie",
    }
    n = 0
    for root, dirs, files in os.walk(DEMO_DIR):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "node_modules"]
        for fn in files:
            if not fn.endswith(".html"):
                continue
            path = os.path.join(root, fn)
            try:
                with open(path, encoding="utf-8", errors="replace") as f:
                    h = f.read()
            except OSError:
                continue
            # Skip pages that already have the PP link
            if 'footer-pp-link' in h:
                continue
            if 'footer-bottom' not in h:
                continue
            # Determine language
            rel = os.path.relpath(path, DEMO_DIR).replace("\\", "/")
            pre = rel.split("/")[0]
            lang = pre if pre in LANGS and pre != "en" else "en"
            pfx = LANG_PFX[lang]
            pp_slug = SLUG[lang]["privacy-policy"]
            pp_href = f"{pfx}/{pp_slug}/" if pfx else f"/{pp_slug}/"
            full_copy = COPY_FULL[lang]
            pp_lbl = PP_LBL[lang]
            new_p = f'<p>{full_copy} &nbsp;·&nbsp; <a href="{pp_href}" class="footer-pp-link">{pp_lbl}</a></p>'
            # Try short copyright first, then full copyright (home pages use full)
            old_p_short = f'<p>{COPY_SHORT[lang]}</p>'
            old_p_full  = f'<p>{full_copy}</p>'
            if old_p_short in h:
                h2 = h.replace(old_p_short, new_p, 1)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(h2)
                n += 1
            elif old_p_full in h:
                h2 = h.replace(old_p_full, new_p, 1)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(h2)
                n += 1
    print(f"  footer-bottom PP link: patched {n} HTML files")


def patch_footer_brands_all():
    """Add .footer-brand wrapper + home link + logo dimensions on every page (one-time safe if already patched)."""
    logo_esc = re.escape(LOGO)
    pat = re.compile(
        r'(<div class="footer-grid">\s*)<div>\s*<img src="' + logo_esc
        + r'" alt="Ngor Surfcamp Teranga" class="footer-brand-logo" loading="lazy">\s*<p>',
    )
    nfiles = 0
    for root, _, files in os.walk(DEMO_DIR):
        for fn in files:
            if not fn.endswith(".html"):
                continue
            path = os.path.join(root, fn)
            try:
                with open(path, encoding="utf-8", errors="replace") as f:
                    h = f.read()
            except OSError:
                continue
            if 'class="footer-brand"' in h:
                continue
            if "footer-grid" not in h or "footer-brand-logo" not in h:
                continue
            rel = os.path.relpath(path, DEMO_DIR).replace("\\", "/")
            pre = rel.split("/")[0]
            lang = pre if pre in LANGS and pre != "en" else "en"
            pfx = LANG_PFX[lang]
            href = (pfx + "/") if pfx else "/"

            def repl(m, href=href):
                return (
                    m.group(1) + '<div class="footer-brand">\n        '
                    f'<a href="{href}" class="footer-brand-mark" aria-label="Ngor Surfcamp Teranga home">\n          '
                    f'<img src="{LOGO}" alt="" width="152" height="52" class="footer-brand-logo" loading="lazy">\n'
                    "        </a>\n        <p class=\"footer-brand-text\">"
                )

            h2, n = pat.subn(repl, h, count=1)
            if n:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(h2)
                nfiles += 1
    print(f"  footer-brand column: updated {nfiles} HTML files")

BOOK_FOOTER_LABEL = {
    "en": "Book Now",
    "fr": "Réserver",
    "es": "Reservar",
    "it": "Prenota",
    "de": "Buchen",
    "nl": "Boeken",
    "ar": "احجز الآن",
}
GH_FOOTER_LABEL = {
    "en": "Getting here",
    "fr": "Comment venir",
    "es": "Cómo llegar",
    "it": "Come arrivare",
    "de": "Anreise",
    "nl": "Hoe kom je er",
    "ar": "كيفية الوصول",
}


def patch_explore_footer_getting_here_all():
    """Add localized Getting here link after Book in Explore column (static HTML not rebuilt)."""
    n = 0
    for root, dirs, files in os.walk(DEMO_DIR):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "node_modules"]
        for fn in files:
            if not fn.endswith(".html"):
                continue
            path = os.path.join(root, fn)
            rel = os.path.relpath(path, DEMO_DIR).replace("\\", "/")
            pre = rel.split("/")[0]
            lang = pre if pre in LANGS and pre != "en" else "en"
            gh = GETTING_HERE_FLAG_HREF[lang]
            try:
                with open(path, encoding="utf-8", errors="replace") as f:
                    h = f.read()
            except OSError:
                continue
            if re.search(
                re.escape(BOOK_FOOTER_LABEL[lang])
                + r"</a>\s*<a href="
                + re.escape(f'"{gh}"')
                + r">",
                h,
            ):
                continue
            pfx = LANG_PFX[lang]
            slug = SLUG[lang]["booking"]
            book_href = f"{pfx}/{slug}/".replace("//", "/")
            if not book_href.startswith("/"):
                book_href = "/" + book_href
            old = f'<a href="{book_href}">{BOOK_FOOTER_LABEL[lang]}</a></div>'
            new = (
                f'<a href="{book_href}">{BOOK_FOOTER_LABEL[lang]}</a>\n'
                f'<a href="{gh}">{GH_FOOTER_LABEL[lang]}</a></div>'
            )
            if old not in h:
                continue
            h2 = h.replace(old, new, 1)
            with open(path, "w", encoding="utf-8") as f:
                f.write(h2)
            n += 1
    print(f"  footer Explore + getting-here link: updated {n} HTML files")


def patch_home_rotating_quotes():
    """Replace English rotating quotes with native language versions on nl/ar home pages."""
    PHRASES = {
        "fr": [
            "L'océan se fiche de ton niveau. Il ne se soucie que de ta présence.",
            "Pas de voitures. Pas de bruit. Juste le son des vagues à Ngor.",
            "La progression en surf se mesure en sourires, pas seulement en virages.",
            "Ngor Right appelle les surfeurs depuis 1964. C'est ton tour.",
            "Le meilleur trip de surf est celui où tu oublies de vérifier ton téléphone.",
            "Le meilleur secret surf d'Afrique de l'Ouest ? Plus pour longtemps.",
            "Une balade en pirogue sépare Dakar du paradis.",
            "Surfe mieux. Vis plus lentement. Ressens la différence.",
            "Teranga : l'art sénégalais de faire se sentir chaque hôte chez soi.",
            "Ngor Left enseigne la patience. Ngor Right la récompense.",
            "L'Atlantique est chaud ici. L'accueil encore plus.",
            "Six jours, six sessions, un surf camp qui change tout.",
            "Le vrai coaching commence là où les zones de confort s'arrêtent.",
            "Certains viennent à Ngor pour une semaine. Beaucoup reviennent chaque année.",
            "<strong>L'Endless Summer a commencé ici. Où commencera le tien ?</strong>",
        ],
        "es": [
            "Al océano no le importa tu nivel. Solo le importa tu presencia.",
            "Sin coches. Sin ruido. Solo el sonido de las olas en Ngor.",
            "El progreso en el surf se mide en sonrisas, no solo en giros.",
            "Ngor Right lleva llamando a los surfistas desde 1964. Tu turno.",
            "El mejor viaje de surf es aquel en el que olvidas revisar el teléfono.",
            "¿El mejor secreto surf de África Occidental? Ya no lo es tanto.",
            "Un viaje en piragua separa Dakar del paraíso.",
            "Surfa mejor. Vive más lento. Siente la diferencia.",
            "Teranga: el arte senegalés de hacer que cada huésped se sienta como en casa.",
            "Ngor Left enseña paciencia. Ngor Right la recompensa.",
            "El Atlántico está cálido aquí. El bienvenido aún más.",
            "Seis días, seis sesiones, un surf camp que lo cambia todo.",
            "El coaching real comienza donde terminan las zonas de confort.",
            "Algunos vienen a Ngor por una semana. Muchos vuelven cada año.",
            "<strong>El Endless Summer empezó aquí. ¿Dónde empezará el tuyo?</strong>",
        ],
        "it": [
            "L'oceano non si preoccupa del tuo livello. Si preoccupa solo della tua presenza.",
            "Niente macchine. Niente rumore. Solo il suono delle onde a Ngor.",
            "Il progresso nel surf si misura in sorrisi, non solo in virate.",
            "Ngor Right chiama i surfisti dal 1964. È il tuo turno.",
            "Il miglior viaggio surf è quello in cui dimentichi di controllare il telefono.",
            "Il miglior segreto surf dell'Africa Occidentale? Non più.",
            "Una gita in piroga separa Dakar dal paradiso.",
            "Surfa meglio. Vivi più lentamente. Senti la differenza.",
            "Teranga: l'arte senegalese di far sentire ogni ospite a casa.",
            "Ngor Left insegna la pazienza. Ngor Right la premia.",
            "L'Atlantico è caldo qui. L'accoglienza ancora di più.",
            "Sei giorni, sei sessioni, un surf camp che cambia tutto.",
            "Il vero coaching inizia dove finiscono le zone di comfort.",
            "Alcuni vengono a Ngor per una settimana. Molti tornano ogni anno.",
            "<strong>L'Endless Summer è iniziato qui. Dove inizierà il tuo?</strong>",
        ],
        "de": [
            "Der Ozean kümmert sich nicht um dein Level. Nur um deine Anwesenheit.",
            "Keine Autos. Kein Lärm. Nur das Rauschen der Wellen bei Ngor.",
            "Fortschritt beim Surfen wird in Lächeln gemessen, nicht nur in Kurven.",
            "Ngor Right ruft Surfer seit 1964. Du bist dran.",
            "Der beste Surf-Trip ist der, bei dem du vergisst, dein Handy zu checken.",
            "Westafrikas bestgehütetes Surf-Geheimnis? Nicht mehr lange.",
            "Eine Pirogenfahrt trennt Dakar vom Paradies.",
            "Besser surfen. Langsamer leben. Den Unterschied spüren.",
            "Teranga: die senegalesische Kunst, jeden Gast wie zuhause zu empfangen.",
            "Ngor Left lehrt Geduld. Ngor Right belohnt sie.",
            "Der Atlantik ist hier warm. Der Empfang noch wärmer.",
            "Sechs Tage, sechs Sessions, ein Surf-Camp, das alles verändert.",
            "Echtes Coaching beginnt, wo Komfortzonen enden.",
            "Manche kommen eine Woche nach Ngor. Viele kommen jedes Jahr zurück.",
            "<strong>Der Endless Summer begann hier. Wo beginnt deiner?</strong>",
        ],
        "nl": [
            "De oceaan geeft niet om je niveau. Het geeft alleen om je aanwezigheid.",
            "Geen auto\u2019s. Geen lawaai. Alleen het geluid van golven bij Ngor.",
            "Vooruitgang in surfen wordt gemeten in glimlachen, niet alleen in bochten.",
            "Ngor Right roept surfers al op sinds 1964. Nu is het jouw beurt.",
            "De beste surftrip is de trip waarbij je vergeet je telefoon te checken.",
            "West-Afrika\u2019s beste surfgeheim? Niet meer.",
            "Een piroguerit scheidt Dakar van het paradijs.",
            "Surf beter. Leef rustiger. Voel het verschil.",
            "Teranga: de Senegalese kunst om elke gast zich thuis te laten voelen.",
            "Ngor Left leert je geduld. Ngor Right beloont het.",
            "De Atlantische Oceaan is hier warm. Het welkom zelfs warmer.",
            "Zes dagen, zes sessies, \xe9\xe9n surfkamp dat alles verandert.",
            "Echte coaching begint waar comfort zones eindigen.",
            "Sommige mensen komen een week naar Ngor. Velen komen elk jaar terug.",
            "<strong>De Endless Summer begon hier. Waar begint die van jou?</strong>",
        ],
        "ar": [
            "\u0627\u0644\u0645\u062d\u064a\u0637 \u0644\u0627 \u064a\u0647\u062a\u0645 \u0628\u0645\u0633\u062a\u0648\u0627\u0643. \u0643\u0644 \u0645\u0627 \u064a\u0647\u0645\u0647 \u0647\u0648 \u062d\u0636\u0648\u0631\u0643.",
            "\u0644\u0627 \u0633\u064a\u0627\u0631\u0627\u062a. \u0644\u0627 \u0636\u062c\u064a\u062c. \u0641\u0642\u0637 \u0635\u0648\u062a \u0627\u0644\u0623\u0645\u0648\u0627\u062c \u0639\u0646\u062f \u0646\u063a\u0648\u0631.",
            "\u064a\u064f\u0642\u0627\u0633 \u0627\u0644\u062a\u0642\u062f\u0645 \u0641\u064a \u0631\u0643\u0648\u0628 \u0627\u0644\u0623\u0645\u0648\u0627\u062c \u0628\u0627\u0644\u0627\u0628\u062a\u0633\u0627\u0645\u0627\u062a.",
            "Ngor Right \u064a\u0646\u0627\u062f\u064a \u0631\u0627\u0643\u0628\u064a \u0627\u0644\u0623\u0645\u0648\u0627\u062c \u0645\u0646\u0630 1964. \u062d\u0627\u0646 \u062f\u0648\u0631\u0643.",
            "\u0623\u0641\u0636\u0644 \u0631\u062d\u0644\u0629 \u0623\u0645\u0648\u0627\u062c \u0647\u064a \u062a\u0644\u0643 \u0627\u0644\u062a\u064a \u062a\u0646\u0633\u0649 \u0641\u064a\u0647\u0627 \u0647\u0627\u062a\u0641\u0643.",
            "\u0623\u0641\u0636\u0644 \u0633\u0631 \u0644\u0644\u0623\u0645\u0648\u0627\u062c \u0641\u064a \u063a\u0631\u0628 \u0623\u0641\u0631\u064a\u0642\u064a\u0627? \u0644\u0645 \u064a\u0639\u062f \u0633\u0631\u0627\u064b.",
            "\u0631\u062d\u0644\u0629 \u0628\u0627\u0644\u0642\u0627\u0631\u0628 \u062a\u0641\u0635\u0644 \u062f\u0627\u0643\u0627\u0631 \u0639\u0646 \u0627\u0644\u062c\u0646\u0629.",
            "\u062a\u0635\u0641\u062d \u0628\u0634\u0643\u0644 \u0623\u0641\u0636\u0644. \u0639\u0634 \u0628\u062a\u0645\u0647\u0644. \u0627\u0634\u0639\u0631 \u0628\u0627\u0644\u0641\u0631\u0642.",
            "Teranga: \u0641\u0646 \u0633\u0646\u063a\u0627\u0644\u064a \u064a\u062c\u0639\u0644 \u0643\u0644 \u0636\u064a\u0641 \u064a\u0634\u0639\u0631 \u0628\u0623\u0646\u0647 \u0641\u064a \u0628\u064a\u062a\u0647.",
            "Ngor Left \u064a\u0639\u0644\u0645\u0643 \u0627\u0644\u0635\u0628\u0631. Ngor Right \u064a\u0643\u0627\u0641\u0626\u0643 \u0639\u0644\u064a\u0647.",
            "\u0627\u0644\u0645\u062d\u064a\u0637 \u0627\u0644\u0623\u0637\u0644\u0633\u064a \u062f\u0627\u0641\u0626\u0621 \u0647\u0646\u0627. \u0648\u0627\u0644\u062a\u0631\u062d\u064a\u0628 \u0623\u062f\u0641\u0623.",
            "\u0633\u062a\u0629 \u0623\u064a\u0627\u0645 \u0648\u0633\u062a \u062c\u0644\u0633\u0627\u062a \u0648\u0645\u062e\u064a\u0645 \u0648\u0627\u062d\u062f \u064a\u063a\u064a\u0631 \u0643\u0644 \u0634\u064a\u0621.",
            "\u0627\u0644\u062a\u062f\u0631\u064a\u0628 \u0627\u0644\u062d\u0642\u064a\u0642\u064a \u064a\u0628\u062f\u0623 \u062d\u064a\u062b \u062a\u0646\u062a\u0647\u064a \u0645\u0646\u0627\u0637\u0642 \u0627\u0644\u0631\u0627\u062d\u0629.",
            "\u0628\u0639\u0636 \u0627\u0644\u0646\u0627\u0633 \u064a\u0623\u062a\u0648\u0646 \u0625\u0644\u0649 \u0646\u063a\u0648\u0631 \u0644\u0623\u0633\u0628\u0648\u0639. \u0643\u062b\u064a\u0631\u0648\u0646 \u064a\u0639\u0648\u062f\u0648\u0646 \u0643\u0644 \u0639\u0627\u0645.",
            "<strong>\u0628\u062f\u0623 Endless Summer \u0647\u0646\u0627. \u0623\u064a\u0646 \u064a\u0628\u062f\u0623 \u0635\u064a\u0641\u0643 \u0627\u0644\u062e\u0627\u0644\u062f?</strong>",
        ],
    }
    import re as _re
    n = 0
    for lang, phrases in PHRASES.items():
        rel  = f"{lang}/index.html"
        path = os.path.join(DEMO_DIR, rel)
        if not os.path.isfile(path): continue
        with open(path, encoding="utf-8") as f:
            h = f.read()
        # Build translated span elements
        spans = "".join(
            f'<span class="fq-phrase{" active" if i==0 else ""}" data-idx="{i}">{p}</span>'
            for i, p in enumerate(phrases)
        )
        # Replace the inner content of fq-wrap-en with translated content
        # and change the id to match the lang
        old_id = f'id="fq-wrap-en"'
        new_id = f'id="fq-wrap-{lang}"'
        # Replace fq-wrap-en with new lang-specific id
        h2 = h.replace(old_id, new_id, 1)
        # Replace the phrases inside the new id wrapper
        h2 = _re.sub(
            rf'(<div class="fq-text-wrap" id="fq-wrap-{lang}">).*?(</div>)',
            lambda m: m.group(1) + spans + m.group(2),
            h2, count=1, flags=_re.S
        )
        if h2 != h:
            with open(path, "w", encoding="utf-8") as f:
                f.write(h2)
            n += 1
    print(f"  Rotating quotes: translated {n} home pages")


def patch_home_static_text_all():
    """Fix static English text (trust badge, CTA band) inherited on non-EN home pages."""
    STATIC_PATCHES = {
        "fr": {"all_levels": "Tous niveaux bienvenus",     "cta_h2": "Prêt à surfer\u00a0? Réservez votre séjour."},
        "es": {"all_levels": "Todos los niveles bienvenidos","cta_h2": "¿Listo para surfear? Reserva tu estancia."},
        "it": {"all_levels": "Tutti i livelli benvenuti",  "cta_h2": "Pronto a surfare? Prenota il tuo soggiorno."},
        "de": {"all_levels": "Alle Level willkommen",       "cta_h2": "Bereit zu surfen? Jetzt buchen."},
        "nl": {"all_levels": "Alle niveaus welkom",         "cta_h2": "Klaar om te surfen? Boek je verblijf."},
        "ar": {"all_levels": "جميع المستويات مرحب بها",   "cta_h2": "مستعد لركوب الأمواج؟ احجز إقامتك."},
    }
    n = 0
    for lang, patches in STATIC_PATCHES.items():
        rel  = f"{lang}/index.html"
        path = os.path.join(DEMO_DIR, rel)
        if not os.path.exists(path): continue
        with open(path, encoding="utf-8") as f:
            h = f.read()
        changed = False
        if "All levels welcome" in h:
            h = h.replace("All levels welcome", patches["all_levels"], 1)
            changed = True
        if "Ready to surf? Book your stay." in h:
            h = h.replace("Ready to surf? Book your stay.", patches["cta_h2"], 1)
            changed = True
        if changed:
            with open(path, "w", encoding="utf-8") as f:
                f.write(h)
            n += 1
    print(f"  Static home text patches: {n} pages")


def patch_home_nav_footer_all():
    """Replace nav and footer on ALL home pages with correctly-translated versions from build_nav/build_footer."""
    import re as _re
    NAV_RE    = _re.compile(r'<nav\s+id="nav".*?</nav>', _re.DOTALL)
    FOOTER_RE = _re.compile(r'<footer>.*?</footer>', _re.DOTALL)
    n = 0
    for rel in HOME_PAGES:
        lang = "en"
        if "/" in rel:
            lang = rel.split("/")[0]
        path = os.path.join(DEMO_DIR, rel)
        if not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8") as f:
            h = f.read()
        # Build correct href map (home links for all languages)
        home_hrefs = {lg: (LANG_PFX[lg] + "/") for lg in LANGS}
        new_nav    = build_nav("", lang, home_hrefs)
        new_footer = build_footer(lang)
        h2 = NAV_RE.sub(new_nav, h, count=1)
        h2 = FOOTER_RE.sub(new_footer, h2, count=1)
        if h2 != h:
            with open(path, "w", encoding="utf-8") as f:
                f.write(h2)
            n += 1
    print(f"  home nav+footer rebuilt: {n} pages")


def patch_home_discover_section_all():
    """Translate the 'Discover' section (heading + 3 cards) on non-EN home pages."""
    DISC_L = {
        "fr": {"lbl":"Découvrir","h2":"Tout au Ngor Surfcamp",
               "c1_t":"La Surf House","c1_d":"Chambres cosy, piscine, vue mer, repas sénégalais. Votre maison au bord de l'océan.","c1_btn":"Découvrir",
               "c2_t":"L'Île de Ngor","c2_d":"Pas de voitures, lineups déserts, héritage de The Endless Summer. À 5 min en pirogue de Dakar, un monde à part.","c2_btn":"Découvrir",
               "c3_t":"Le Surf","c3_d":"Vagues consistantes 365 jours par an, lineups déserts, coachs certifiés ISA. Le secret surf le mieux gardé d'Afrique de l'Ouest.","c3_btn":"Découvrir"},
        "es": {"lbl":"Descubrir","h2":"Todo en Ngor Surfcamp",
               "c1_t":"La Surf House","c1_d":"Habitaciones acogedoras, piscina, vistas al mar, comidas senegalesas. Tu hogar junto al océano.","c1_btn":"Descubrir",
               "c2_t":"Isla de Ngor","c2_d":"Sin coches, lineups vacíos, legado de The Endless Summer. A 5 min en piragua de Dakar, otro mundo.","c2_btn":"Descubrir",
               "c3_t":"El Surf","c3_d":"Olas consistentes 365 días al año, lineups tranquilos, coaches certificados ISA. El secreto surf mejor guardado de África Occidental.","c3_btn":"Descubrir"},
        "it": {"lbl":"Scoprire","h2":"Tutto al Ngor Surfcamp",
               "c1_t":"La Surf House","c1_d":"Camere accoglienti, piscina, vista mare, pasti senegalesi. La tua casa sull'oceano.","c1_btn":"Scopri",
               "c2_t":"Isola di Ngor","c2_d":"Niente auto, lineup deserti, eredità di The Endless Summer. A 5 min in piroga da Dakar, un altro mondo.","c2_btn":"Scopri",
               "c3_t":"Il Surf","c3_d":"Onde consistenti 365 giorni l'anno, lineup vuoti, coach certificati ISA. Il segreto surf meglio custodito dell'Africa Occidentale.","c3_btn":"Scopri"},
        "de": {"lbl":"Entdecken","h2":"Alles im Ngor Surfcamp",
               "c1_t":"Das Surf House","c1_d":"Gemütliche Zimmer, Pool, Meerblick, tägliche senegalesische Mahlzeiten. Ihr Zuhause am Ozean.","c1_btn":"Entdecken",
               "c2_t":"Ngor Island","c2_d":"Keine Autos, leere Lineups, das Erbe von The Endless Summer. 5 min mit der Piroge von Dakar — eine andere Welt.","c2_btn":"Entdecken",
               "c3_t":"Surfen","c3_d":"Konstante Wellen 365 Tage im Jahr, leere Lineups, ISA-zertifizierte Coaches. Westafrikas bestgehütetes Surfgeheimnis.","c3_btn":"Entdecken"},
        "nl": {"lbl":"Ontdek","h2":"Alles bij Ngor Surfcamp",
               "c1_t":"De Surf House","c1_d":"Gezellige kamers, zwembad, zeezicht, dagelijkse Senegalese maaltijden. Jouw thuis aan de oceaan.","c1_btn":"Ontdekken",
               "c2_t":"Ngor Eiland","c2_d":"Geen auto's, lege lineups, erfenis van The Endless Summer. 5 min per pirogue van Dakar — een andere wereld.","c2_btn":"Ontdekken",
               "c3_t":"Surfen","c3_d":"Consistente golven 365 dagen per jaar, lege lineups, ISA-gecertificeerde coaches. Het best bewaarde surfgeheim van West-Afrika.","c3_btn":"Ontdekken"},
        "ar": {"lbl":"اكتشف","h2":"كل شيء في نغور سيرف كامب",
               "c1_t":"بيت الأمواج","c1_d":"غرف مريحة، مسبح، إطلالة على البحر، وجبات سنغالية يومية. منزلك بجانب المحيط.","c1_btn":"اكتشف",
               "c2_t":"جزيرة نغور","c2_d":"لا سيارات، أمواج عالمية المستوى، إرث The Endless Summer. جوهرة قبالة داكار.","c2_btn":"اكتشف",
               "c3_t":"ركوب الأمواج","c3_d":"تحليل فيديو احترافي، جلسات مخصصة، جميع المستويات. مدربون معتمدون.","c3_btn":"اكتشف"},
    }
    # Map lang → (slug key, localized slug)
    PAGE_SLUGS = {
        lg: {
            "surf-house": SLUG[lg].get("surf-house", "surf-house"),
            "island":     SLUG[lg].get("island", "island"),
            "surfing":    SLUG[lg].get("surfing", "surfing"),
        }
        for lg in LANGS
    }
    n = 0
    for lang, L in DISC_L.items():
        rel  = f"{lang}/index.html"
        path = os.path.join(DEMO_DIR, rel)
        if not os.path.isfile(path): continue
        with open(path, encoding="utf-8") as f:
            h = f.read()
        pfx = LANG_PFX[lang]
        sh_href   = f"{pfx}/{PAGE_SLUGS[lang]['surf-house']}/"
        isl_href  = f"{pfx}/{PAGE_SLUGS[lang]['island']}/"
        surf_href = f"{pfx}/{PAGE_SLUGS[lang]['surfing']}/"
        new_heading = (
            f'<div class="reveal" style="text-align:center;margin-bottom:60px">\n'
            f'        <span class="s-label">{L["lbl"]}</span>\n'
            f'        <h2 class="s-title">{L["h2"]}</h2>\n'
            f'      </div>'
        )
        new_grid = (
            f'<div class="grid-3 reveal">\n'
            f'        <a href="{sh_href}" class="card">\n'
            f'          <img src="/assets/images/wix/df99f9_eba4c24ec6a746b58d60a975b8d20946.webp" alt="{L["c1_t"]}" class="card-img" loading="lazy">\n'
            f'          <div class="card-body">\n'
            f'            <h3 class="card-h3">{L["c1_t"]}</h3>\n'
            f'            <p class="card-text">{L["c1_d"]}</p>\n'
            f'            <span class="btn btn-deep btn-sm" style="margin-top:14px">{L["c1_btn"]}</span>\n'
            f'          </div>\n'
            f'        </a>\n'
            f'        <a href="{isl_href}" class="card">\n'
            f'          <img src="/assets/images/wix/b28af82dbec544138f16e2bc5a85f2cb.webp" alt="{L["c2_t"]}" class="card-img" loading="lazy">\n'
            f'          <div class="card-body">\n'
            f'            <h3 class="card-h3">{L["c2_t"]}</h3>\n'
            f'            <p class="card-text">{L["c2_d"]}</p>\n'
            f'            <span class="btn btn-deep btn-sm" style="margin-top:14px">{L["c2_btn"]}</span>\n'
            f'          </div>\n'
            f'        </a>\n'
            f'        <a href="{surf_href}" class="card">\n'
            f'          <img src="/assets/images/wix/11062b_89a070321f814742a620b190592d51ad.webp" alt="{L["c3_t"]}" class="card-img" loading="lazy">\n'
            f'          <div class="card-body">\n'
            f'            <h3 class="card-h3">{L["c3_t"]}</h3>\n'
            f'            <p class="card-text">{L["c3_d"]}</p>\n'
            f'            <span class="btn btn-deep btn-sm" style="margin-top:14px">{L["c3_btn"]}</span>\n'
            f'          </div>\n'
            f'        </a>\n'
            f'      </div>'
        )
        old_heading = (
            '<div class="reveal" style="text-align:center;margin-bottom:60px">\n'
            '        <span class="s-label">Discover</span>\n'
            '        <h2 class="s-title">Everything at Ngor Surfcamp</h2>\n'
            '      </div>'
        )
        old_grid_start = '<div class="grid-3 reveal">\n        <a href="/surf-house/" class="card">'
        changed = False
        if old_heading in h:
            h = h.replace(old_heading, new_heading, 1)
            changed = True
        elif '<span class="s-label">Discover</span>' in h:
            import re as _re2
            h = _re2.sub(
                r'<span class="s-label">Discover</span>',
                f'<span class="s-label">{L["lbl"]}</span>',
                h, count=1
            )
            h = _re2.sub(
                r'<h2 class="s-title">(?:Everything at Ngor Surfcamp|Alles im Ngor Surfcamp|Alles bij Ngor Surfcamp)</h2>',
                f'<h2 class="s-title">{L["h2"]}</h2>',
                h, count=1
            )
            changed = True
        if old_grid_start in h:
            # Replace the entire 3-card grid
            import re as _re3
            grid_pattern = _re3.compile(
                r'<div class="grid-3 reveal">\s*<a href="/surf-house/".*?</div>\s*</div>',
                _re3.DOTALL
            )
            m = grid_pattern.search(h)
            if m:
                h = h[:m.start()] + new_grid + h[m.end():]
                changed = True
        if changed:
            with open(path, "w", encoding="utf-8") as f:
                f.write(h)
            n += 1
    print(f"  home Discover section translated: {n} pages")


def patch_google_score_all():
    """Fix hardcoded Google score/count on all home pages to match real GBP."""
    from pathlib import Path as _P
    REAL_SCORE = "4.7"
    REAL_SCORE_COMMA = "4,7"
    REAL_COUNT = "54"
    OLD_SCORES = ["4.2", "4.1", "4,2", "4,1", "4٫2", "4٫1"]
    OLD_COUNTS = ["64 Google", "56 Google", "64 avis", "56 avis", "64 review", "56 review",
                  "64 reseñas", "56 reseñas", "64 recensioni", "56 recensioni",
                  "64 Google-Bewertung", "56 Google-Bewertung", "64 Google-recens", "56 Google-recens",
                  "64 تقييم", "56 تقييم"]
    n = 0
    for p in _P(DEMO_DIR).rglob("index.html"):
        h = p.read_text(encoding="utf-8", errors="replace")
        changed = False
        for old in OLD_SCORES:
            if old in h:
                replacement = REAL_SCORE_COMMA if "," in old or "٫" in old else REAL_SCORE
                if "٫" in old:
                    replacement = "4٫7"
                h = h.replace(f'>{old}<', f'>{replacement}<')
                h = h.replace(f'"{old}"', f'"{replacement}"')
                changed = True
        for old in OLD_COUNTS:
            new = old.replace("64", REAL_COUNT).replace("56", REAL_COUNT)
            if old in h and old != new:
                h = h.replace(old, new)
                changed = True
        if changed:
            p.write_text(h, encoding="utf-8")
            n += 1
    print(f"  Google score: updated {n} pages to {REAL_SCORE} ({REAL_COUNT} reviews)")


def patch_home_reviews_labels_all():
    """Translate 'View all on Google' and 'Leave a review' on non-EN home pages."""
    REVIEW_L = {
        "fr": {"view_all": "Voir tous sur Google", "leave": "Laisser un avis"},
        "es": {"view_all": "Ver todos en Google",  "leave": "Dejar una reseña"},
        "it": {"view_all": "Vedi tutti su Google", "leave": "Lascia una recensione"},
        "de": {"view_all": "Alle auf Google sehen","leave": "Bewertung schreiben"},
        "nl": {"view_all": "Bekijk alles op Google","leave": "Schrijf een recensie"},
        "ar": {"view_all": "عرض الكل على Google", "leave": "اترك تقييماً"},
    }
    n = 0
    for lang, L in REVIEW_L.items():
        rel  = f"{lang}/index.html"
        path = os.path.join(DEMO_DIR, rel)
        if not os.path.isfile(path): continue
        with open(path, encoding="utf-8") as f:
            h = f.read()
        changed = False
        for eng, translated in [("View all on Google", L["view_all"]), ("Leave a review", L["leave"])]:
            if eng in h:
                h = h.replace(eng, translated)
                changed = True
        if changed:
            with open(path, "w", encoding="utf-8") as f:
                f.write(h)
            n += 1
    print(f"  home reviews labels translated: {n} pages")


def patch_author_bios_all():
    """Replace truncated author bios ([:180]) with full bios in all pre-built blog HTML pages."""
    import json as _json
    from pathlib import Path as _Path
    _authors_path = os.path.join(os.path.dirname(_BASE_DIR), "SurfCampSenegal", "content", "authors", "authors.json")
    # Try relative path first
    _authors_path2 = os.path.join(_BASE_DIR, "content", "authors", "authors.json")
    _ap = _authors_path2 if os.path.isfile(_authors_path2) else _authors_path
    if not os.path.isfile(_ap):
        print("  author bios: authors.json not found, skipping")
        return
    with open(_ap, encoding="utf-8") as _f:
        _authors = _json.load(_f)
    n = 0
    for _html_path in _Path(DEMO_DIR).rglob("*.html"):
        try:
            with open(_html_path, encoding="utf-8", errors="replace") as _f:
                _h = _f.read()
            if 'author-bio-text' not in _h:
                continue
            _changed = False
            for _aid, _a in _authors.items():
                for _lang in list(_a.get("bio", {}).keys()):
                    _full_bio = _a["bio"][_lang]
                    _truncated = _full_bio[:180]
                    if len(_full_bio) > 180 and _truncated in _h:
                        _h = _h.replace(
                            f'<div class="author-bio-text">{_truncated}</div>',
                            f'<div class="author-bio-text">{_full_bio}</div>'
                        )
                        _changed = True
            if _changed:
                with open(_html_path, "w", encoding="utf-8") as _f:
                    _f.write(_h)
                n += 1
        except Exception as _e:
            pass
    print(f"  author bios: fixed in {n} pages")


def patch_home_getting_here_teaser():
    """Translate the Getting Here teaser section on all home pages."""
    TEASER_L10N = {
        "en": {
            "lbl": "How to Get There",
            "h2":  "Getting to Ngor Island",
            "sub": "Complete travel guide — flights, transfers and pirogue crossing.",
            "t1":  "airport", "t2": "from Dakar", "t3": "pirogue",
            "cta": "Read the guide",
        },
        "fr": {
            "lbl": "Comment venir",
            "h2":  "Rejoindre l'Île de Ngor",
            "sub": "Guide de voyage complet — vols, transferts et traversée en pirogue.",
            "t1":  "aéroport", "t2": "de Dakar", "t3": "pirogue",
            "cta": "Lire le guide",
        },
        "es": {
            "lbl": "Cómo llegar",
            "h2":  "Llegar a Ngor Island",
            "sub": "Guía de viaje completa — vuelos, traslados y travesía en piragua.",
            "t1":  "aeropuerto", "t2": "de Dakar", "t3": "piragua",
            "cta": "Leer la guía",
        },
        "it": {
            "lbl": "Come arrivare",
            "h2":  "Arrivare a Ngor Island",
            "sub": "Guida di viaggio completa — voli, trasferimenti e traversata in piroga.",
            "t1":  "aeroporto", "t2": "da Dakar", "t3": "piroga",
            "cta": "Leggi la guida",
        },
        "de": {
            "lbl": "Anreise",
            "h2":  "So kommst du nach Ngor Island",
            "sub": "Vollständiger Reiseführer — Flüge, Transfers und Pirogenfahrt.",
            "t1":  "Flughafen", "t2": "von Dakar", "t3": "Pirogge",
            "cta": "Zum Guide",
        },
        "nl": {
            "lbl": "Hoe kom je er",
            "h2":  "Naar Ngor Island",
            "sub": "Complete reisguide — vluchten, transfers en pirogueoversteek.",
            "t1":  "luchthaven", "t2": "van Dakar", "t3": "pirogue",
            "cta": "Lees de gids",
        },
        "ar": {
            "lbl": "كيفية الوصول",
            "h2":  "الوصول إلى جزيرة نغور",
            "sub": "دليل السفر الكامل — رحلات جوية، تنقلات وعبور بالقارب.",
            "t1":  "المطار", "t2": "من داكار", "t3": "قارب",
            "cta": "اقرأ الدليل",
        },
    }
    import re as _re
    EN = TEASER_L10N["en"]
    n = 0
    for lang in LANGS:
        if lang == "en":
            continue
        rel  = f"{lang}/index.html"
        path = os.path.join(DEMO_DIR, rel)
        if not os.path.isfile(path): continue
        T = TEASER_L10N.get(lang, EN)
        with open(path, encoding="utf-8") as f:
            h = f.read()
        if "gh-teaser" not in h: continue
        h = h.replace(f'>{EN["lbl"]}</span>', f'>{T["lbl"]}</span>', 1)
        h = h.replace(f'>{EN["h2"]}</h2>', f'>{T["h2"]}</h2>', 1)
        h = h.replace(f'>{EN["sub"]}</p>', f'>{T["sub"]}</p>', 1)
        h = h.replace(f'>{EN["t1"]}</span>', f'>{T["t1"]}</span>', 1)
        h = h.replace(f'>{EN["t2"]}</span>', f'>{T["t2"]}</span>', 1)
        h = h.replace(f'>{EN["t3"]}</span>', f'>{T["t3"]}</span>', 1)
        h = h.replace(f'>{EN["cta"]}</a>', f'>{T["cta"]}</a>', 1)
        with open(path, "w", encoding="utf-8") as f:
            f.write(h)
        n += 1
    print(f"  Getting Here teaser: translated {n} home pages")


patch_home_getting_here_teaser()


def patch_home_gh_slider():
    """Replace the Leaflet map in the gh-teaser section with a photo slider on all home pages."""
    import re as _re
    SLIDES = [
        ("/assets/images/gallery/4Y4A1355_1ceb02e3.webp",   "Surf session"),
        ("/assets/images/gallery/CAML1086_397acad4.webp",   "Ngor Surf Camp"),
        ("/assets/images/gallery/4Y4A1360_8f3b1641.webp",   "Wave riding"),
        ("/assets/images/gallery/CAML1109_303626ae.webp",   "Camp life"),
        ("/assets/images/gallery/38b93458-6718-461d-9e88-49510cb86f92_cef22f41.webp", "Ngor Island"),
        ("/assets/images/gallery/DSC01421_a10e8955.webp",   "Pirogue crossing"),
    ]
    dots = ''.join(
        f'<button class="gh-dot{" active" if i==0 else ""}" data-idx="{i}" aria-label="Photo {i+1}"></button>'
        for i in range(len(SLIDES))
    )
    slides_html = ''.join(
        f'<div class="gh-slide{" active" if i==0 else ""}" data-idx="{i}">'
        f'<img src="{src}" alt="{cap}" loading="{("eager" if i==0 else "lazy")}" width="600" height="380" decoding="async">'
        f'<div class="gh-slide-overlay"></div></div>'
        for i, (src, cap) in enumerate(SLIDES)
    )
    js = ('<script>(function(){'
          'var slides=document.querySelectorAll(".gh-slide"),'
          'dots=document.querySelectorAll(".gh-dot"),cur=0,timer;'
          'function go(n){slides[cur].classList.remove("active");dots[cur].classList.remove("active");'
          'cur=(n+slides.length)%slides.length;slides[cur].classList.add("active");dots[cur].classList.add("active");}'
          'function next(){go(cur+1);}timer=setInterval(next,4000);'
          'dots.forEach(function(d){d.addEventListener("click",function(){clearInterval(timer);go(+this.dataset.idx);timer=setInterval(next,4000);});});'
          'var prev=document.querySelector(".gh-slider-arrow.prev"),nxt=document.querySelector(".gh-slider-arrow.next");'
          'if(prev)prev.addEventListener("click",function(){clearInterval(timer);go(cur-1);timer=setInterval(next,4000);});'
          'if(nxt)nxt.addEventListener("click",function(){clearInterval(timer);go(cur+1);timer=setInterval(next,4000);});'
          '})();</script>')
    slider_html = (
        '<div class="gh-slider" aria-label="Photo slideshow">'
        '<div class="gh-slider-track">' + slides_html + '</div>'
        '<button class="gh-slider-arrow prev" aria-label="Previous photo">'
        '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>'
        '</button>'
        '<button class="gh-slider-arrow next" aria-label="Next photo">'
        '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>'
        '</button>'
        '<div class="gh-slider-dots">' + dots + '</div>'
        '</div>' + js
    )
    new_ending = (
        '<div class="gh-teaser-map-preview">\n          ' + slider_html
        + '\n        </div>\n      </div>\n    </div>\n  </section>'
    )
    old_pat = _re.compile(
        r'<div class="gh-teaser-map-preview">.*?</div>\s*</div>\s*</div>\s*</div>\s*</section>',
        _re.DOTALL
    )
    n = 0
    for lang in LANGS:
        path = os.path.join(DEMO_DIR, lang, "index.html") if lang else os.path.join(DEMO_DIR, "index.html")
        if not os.path.isfile(path):
            continue
        h = open(path, encoding="utf-8").read()
        if "gh-teaser-map-preview" not in h:
            continue
        new_h = old_pat.sub(new_ending, h)
        if new_h == h:
            continue
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_h)
        n += 1
    print(f"  gh-slider: patched {n} home pages")


patch_home_gh_slider()


def patch_getting_here_footers():
    """Replace stripped footers on Getting Here pages with full site footer + localized language flags."""
    gh = [
        ("getting-here/index.html", "en", "fq-wrap-en"),
        ("fr/comment-venir/index.html", "fr", "fq-wrap-fr"),
        ("es/como-llegar/index.html", "es", "fq-wrap-es"),
        ("it/come-arrivare/index.html", "it", "fq-wrap-it"),
        ("de/anreise/index.html", "de", "fq-wrap-de"),
    ]
    block_pat = re.compile(
        r"<!-- Footer \(inline simplified\) -->.*?</footer>\s*"
        r'(?:<a href="https://wa\.me/221789257025"[^>]*id="float-wa"[^>]*>.*?</a>\s*)?',
        re.DOTALL,
    )
    for rel, lang, fq in gh:
        path = os.path.join(DEMO_DIR, rel)
        if not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8", errors="replace") as f:
            h = f.read()
        quotes = (
            '<div class="footer-quotes" id="fq-quotes-block" aria-label="Surf quotes" aria-live="polite">\n'
            '  <div class="footer-quotes-inner">\n'
            f'    <div class="fq-text-wrap" id="{fq}"></div>\n'
            "  </div>\n"
            "</div>\n"
        )
        new_block = "<!-- Footer -->\n" + quotes + build_footer(lang, GETTING_HERE_FLAG_HREF)
        h2, n = block_pat.subn(new_block, h, count=1)
        if n:
            with open(path, "w", encoding="utf-8") as f:
                f.write(h2)
            print(f"  getting-here full footer: {rel}")

# ════════════════════════════════════════════════════════════════
# BOOKING PAGE — Google rating + review slider (sidebar)
# ════════════════════════════════════════════════════════════════
BOOKING_GOOGLE_MAPS = "https://www.google.com/maps?cid=14555894641030809667"
BOOKING_GOOGLE_REVIEW = "https://www.google.com/search?q=Ngor+Surfcamp+Teranga&kgmid=/g/11zjkpzzzd#lrd=/g/11zjkpzzzd,1,,,,"

BOOKING_SOCIAL_L10N = {
    "en": {
        "score": "4.7",
        "google_lbl": "Google rating",
        "count": "54 Google reviews",
        "maps": "View on Google Maps",
        "leave": "Leave a review",
        "rv_eyebrow": "Social proof",
        "rv_h": "What guests say",
        "rc_tip": "Click to read more",
    },
    "fr": {
        "score": "4,7",
        "google_lbl": "Note Google",
        "count": "54 avis Google",
        "maps": "Voir sur Google Maps",
        "leave": "Laisser un avis",
        "rv_eyebrow": "Ils nous font confiance",
        "rv_h": "Avis de nos clients",
        "rc_tip": "Cliquer pour lire la suite",
    },
    "es": {
        "score": "4,7",
        "google_lbl": "Valoración en Google",
        "count": "54 reseñas en Google",
        "maps": "Ver en Google Maps",
        "leave": "Dejar una reseña",
        "rv_eyebrow": "Confianza",
        "rv_h": "Opiniones de huéspedes",
        "rc_tip": "Clic para leer más",
    },
    "it": {
        "score": "4,7",
        "google_lbl": "Valutazione Google",
        "count": "54 recensioni Google",
        "maps": "Apri in Google Maps",
        "leave": "Lascia una recensione",
        "rv_eyebrow": "Recensioni",
        "rv_h": "Cosa dicono gli ospiti",
        "rc_tip": "Clicca per leggere di più",
    },
    "de": {
        "score": "4,7",
        "google_lbl": "Google-Bewertung",
        "count": "54 Google-Bewertungen",
        "maps": "Auf Google Maps ansehen",
        "leave": "Bewertung schreiben",
        "rv_eyebrow": "Vertrauen",
        "rv_h": "Das sagen unsere Gäste",
        "rc_tip": "Klicken zum Weiterlesen",
    },
    "nl": {
        "score": "4,7",
        "google_lbl": "Google-beoordeling",
        "count": "54 Google-recensies",
        "maps": "Bekijk op Google Maps",
        "leave": "Schrijf een recensie",
        "rv_eyebrow": "Beoordelingen",
        "rv_h": "Wat gasten zeggen",
        "rc_tip": "Klik om meer te lezen",
    },
    "ar": {
        "score": "4٫7",
        "google_lbl": "تقييم جوجل",
        "count": "54 تقييم على جوجل",
        "maps": "عرض على خرائط جوجل",
        "leave": "اترك تقييماً",
        "rv_eyebrow": "آراء الضيوف",
        "rv_h": "ماذا يقول الضيوف",
        "rc_tip": "انقر لقراءة المزيد",
    },
}

BOOKING_REVIEWS = {
    "en": [
        ("J", "#ff5a1f", "Julie F.", "🇫🇷", "France", "today", "Teranga Surf Camp is a fantastic place for all surf lovers! The camp, the spots, the coaching, the island, the atmosphere, the food, and the welcome... In short, it truly lives up to its name, it's Senegalese teranga! No hesitation in staying there!", "Verified review"),
        ("A", "#0ea5e9", "Addie W.", "🇺🇸", "USA", "2 months ago", "I have been to Dakar several times to surf and have stayed in different places. Abu is, in my opinion, the best surf guide in Dakar, and I follow him everywhere. He knows exactly how to position you on the wave and makes sure everyone stays safe. A must!", "Verified review"),
        ("F", "#9c27b0", "F. F.", "🇪🇺", "Europe", "3 weeks ago", "I just got back from an incredible week at Ngor Surfcamp with my 16-year-old daughter. Everything went wonderfully — professional airport pick-up, impeccable organisation, excellent coaching, delicious meals. I recommend it 100%!", "Verified review"),
        ("J", "#22c55e", "John Fairs", "🇬🇧", "UK", "3 weeks ago", "First class! Benoit is awesome, surf guide Abu is incredible, and Arame's cooking was fantastic. The waves were perfect every day. What more could you ask for!", "Verified review"),
        ("M", "#f59e0b", "Milo G.", "🇫🇷", "France", "2 months ago", "An exceptional stay! The organisation is impeccable — you surf twice a day and get taken to different spots depending on conditions and forecasts. Real progression in the water. I recommend 100%.", "Verified review"),
        ("S", "#10b981", "Stephan B.", "🇩🇪", "Germany", "5 days ago", "Two extraordinary weeks: fascinating conversations, great encounters, exceptional waves, impeccable service and food. The best surfcamp experience I've had. See you next season!", "Verified review"),
    ],
    "fr": [
        ("J", "#ff5a1f", "Julie F.", "🇫🇷", "France", "aujourd'hui", "Le surf camp Teranga est un lieu au top pour tous les passionnés de surf ! Le camp, les spots, le coaching, l'île, l'ambiance, la nourriture et l'accueil... Bref, il porte bien son nom, c'est la teranga sénégalaise ! Aucune hésitation à y séjourner !", "Avis vérifié"),
        ("A", "#0ea5e9", "Addie W.", "🇺🇸", "USA", "il y a 2 mois", "Je suis allée plusieurs fois à Dakar pour surfer. Abu est, à mon avis, le meilleur guide de surf de Dakar. Il sait parfaitement vous placer sur la vague et assure la sécurité de tout le monde. Incontournable !", "Avis vérifié"),
        ("F", "#9c27b0", "F. F.", "🇪🇺", "Europe", "il y a 3 semaines", "Je reviens d'une semaine incroyable avec ma fille de 16 ans. Prise en charge professionnelle à l'aéroport, organisation impeccable, coaching excellent, repas délicieux. Je recommande à 100% !", "Avis vérifié"),
        ("J", "#22c55e", "John Fairs", "🇬🇧", "Royaume-Uni", "il y a 3 semaines", "Première classe ! Benoit est génial, Abu est incroyable comme guide et la cuisine d'Arame était fantastique. Les vagues étaient parfaites chaque jour. Que demander de plus !", "Avis vérifié"),
        ("M", "#f59e0b", "Milo G.", "🇫🇷", "France", "il y a 2 mois", "Un séjour exceptionnel ! L'organisation est impeccable — on surfe deux fois par jour et on est emmené sur différents spots selon les conditions. Vraie progression dans l'eau. Je recommande à 100%.", "Avis vérifié"),
        ("L", "#10b981", "Laure M.", "🇫🇷", "France", "il y a 5 jours", "Benoit, Abou et Aram étaient très accueillants et chaleureux, ce qui a rendu l'expérience facile et détendue dès le départ. On s'y sent vraiment comme à la maison. Un surf camp de rêve !", "Avis vérifié"),
    ],
    "es": [
        ("J", "#ff5a1f", "Julie F.", "🇫🇷", "France", "hoy", "¡El surf camp Teranga es un lugar increíble para todos los apasionados del surf! El campamento, los spots, el coaching, la isla, el ambiente, la comida y la acogida... ¡Es la teranga senegalesa! ¡Sin dudarlo!", "Reseña verificada"),
        ("A", "#0ea5e9", "Addie W.", "🇺🇸", "USA", "hace 2 meses", "He ido varias veces a Dakar para surfear. Abu es, en mi opinión, el mejor guía de surf de Dakar. Sabe perfectamente cómo colocarte en la ola y garantiza la seguridad de todo el mundo. ¡Imprescindible!", "Reseña verificada"),
        ("F", "#9c27b0", "F. F.", "🇪🇺", "Europe", "hace 3 semanas", "Una semana increíble con mi hija de 16 años. Recogida profesional en el aeropuerto, organización impecable, coaching excelente, comidas deliciosas. ¡Lo recomiendo al 100%!", "Reseña verificada"),
        ("J", "#22c55e", "John Fairs", "🇬🇧", "Reino Unido", "hace 3 semanas", "¡De primera! Benoit es fantástico, Abu como guía es increíble y la cocina de Arame fue excepcional. Además, las olas fueron perfectas todos los días. ¡Qué más se puede pedir!", "Reseña verificada"),
        ("M", "#f59e0b", "Milo G.", "🇫🇷", "France", "hace 2 meses", "¡Una estancia excepcional! La organización es impecable: surfeas dos veces al día y te llevan a diferentes spots según las condiciones. Progresión real en el agua. ¡Lo recomiendo 100%!", "Reseña verificada"),
        ("G", "#10b981", "Garoe M.", "🇪🇸", "España", "hace 2 meses", "Ambiente cálido y acogedor, nos sentimos como en casa desde el primer momento. A pesar de un vuelo muy tardío, pudimos disfrutar de los espacios comunes todo el día. ¡Una experiencia que repetiría sin dudarlo!", "Reseña verificada"),
    ],
    "it": [
        ("J", "#ff5a1f", "Julie F.", "🇫🇷", "France", "oggi", "Il surf camp Teranga è un posto fantastico per tutti gli appassionati di surf! Il camp, gli spot, il coaching, l'isola, l'atmosfera, il cibo e l'accoglienza... È la vera teranga senegalese! Nessuna esitazione!", "Recensione verificata"),
        ("A", "#0ea5e9", "Addie W.", "🇺🇸", "USA", "2 mesi fa", "Sono andata più volte a Dakar per fare surf. Abu è, secondo me, la migliore guida di surf di Dakar. Sa perfettamente come posizionarti sull'onda e garantisce la sicurezza di tutti. Imperdibile!", "Recensione verificata"),
        ("F", "#9c27b0", "F. F.", "🇪🇺", "Europe", "3 settimane fa", "Una settimana incredibile con mia figlia di 16 anni. Presa in carico professionale all'aeroporto, organizzazione impeccabile, coaching eccellente, pasti deliziosi. Lo consiglio al 100%!", "Recensione verificata"),
        ("J", "#22c55e", "John Fairs", "🇬🇧", "Regno Unito", "3 settimane fa", "Di prima classe! Benoit è fantastico, Abu è incredibile come guida e la cucina di Arame era straordinaria. Inoltre, le onde erano perfette ogni giorno. Cosa si può chiedere di più!", "Recensione verificata"),
        ("N", "#f59e0b", "Niccolò P.", "🇮🇹", "Italia", "3 mesi fa", "Esperienza assolutamente fantastica. Dal mio balcone avevo una vista mozzafiato sull'oceano e sul tramonto su Ngor Right — sicuramente il miglior spot della regione. La cucina era deliziosa e la casa è davvero accogliente.", "Recensione verificata"),
        ("M", "#10b981", "Milo G.", "🇫🇷", "France", "2 mesi fa", "Un soggiorno eccezionale! L'organizzazione è impeccabile: surf due volte al giorno, portati su spot diversi in base alle condizioni. Vera progressione in acqua. Lo consiglio al 100%.", "Recensione verificata"),
    ],
    "de": [
        ("J", "#ff5a1f", "Julie F.", "🇫🇷", "Frankreich", "heute", "Das Teranga Surfcamp ist ein großartiger Ort für alle Surfbegeisterten! Das Camp, die Spots, das Coaching, die Insel, die Atmosphäre, das Essen und der Empfang... Es trägt seinen Namen zu Recht — das ist senegalesische Teranga!", "Verifizierte Bewertung"),
        ("A", "#0ea5e9", "Addie W.", "🇺🇸", "USA", "vor 2 Monaten", "Ich war schon mehrmals in Dakar zum Surfen. Abu ist meiner Meinung nach der beste Surfguide in Dakar. Er weiß genau, wie er dich auf der Welle positionieren muss, und sorgt für die Sicherheit aller. Ein Muss!", "Verifizierte Bewertung"),
        ("F", "#9c27b0", "F. F.", "🇪🇺", "Europa", "vor 3 Wochen", "Eine unglaubliche Woche mit meiner 16-jährigen Tochter. Professionelle Abholung am Flughafen, tadellose Organisation, hervorragendes Coaching, leckeres Essen. Ich empfehle es zu 100%!", "Verifizierte Bewertung"),
        ("J", "#22c55e", "John Fairs", "🇬🇧", "UK", "vor 3 Wochen", "Erstklassig! Benoit ist genial, Surfguide Abu ist unglaublich und Arames Küche war fantastisch. Außerdem waren die Wellen jeden Tag perfekt. Was will man mehr!", "Verifizierte Bewertung"),
        ("S", "#f59e0b", "Stephan B.", "🇩🇪", "Deutschland", "vor 5 Tagen", "Zwei außergewöhnliche Wochen: tolle Gespräche, großartige Begegnungen, außergewöhnliche Wellen, tadelloser Service und Essen. Das beste Surfcamp-Erlebnis, das ich je hatte. Bis nächste Saison!", "Verifizierte Bewertung"),
        ("M", "#10b981", "Mi Ck.", "🇩🇪", "Deutschland", "vor einem Monat", "Das Frühstück und Abendessen waren köstlich und reichhaltig. Die Zimmer waren sauber, das Bett bequem. Zweimal täglich surfen, mit Transfer zu den besten Spots. Absolut empfehlenswert!", "Verifizierte Bewertung"),
    ],
    "nl": [
        ("J", "#ff5a1f", "Julie F.", "🇫🇷", "Frankrijk", "vandaag", "Teranga Surf Camp is een geweldige plek voor alle surfliefhebbers! Het kamp, de spots, de coaching, het eiland, de sfeer, het eten en de ontvangst... Kortom, het draagt zijn naam terecht — het is Senegalese teranga! Geen twijfel!", "Geverifieerde recensie"),
        ("A", "#0ea5e9", "Addie W.", "🇺🇸", "USA", "2 maanden geleden", "Ik ben al meerdere keren naar Dakar geweest om te surfen. Abu is naar mijn mening de beste surfgids van Dakar. Hij weet precies hoe hij je op de golf moet plaatsen en zorgt voor ieders veiligheid. Een aanrader!", "Geverifieerde recensie"),
        ("F", "#9c27b0", "F. F.", "🇪🇺", "Europa", "3 weken geleden", "Net terug van een ongelooflijke week in Ngor Surfcamp met mijn 16-jarige dochter. Professionele ophaalservice, vlekkeloze organisatie, uitstekende coaching, heerlijke maaltijden. 100% aanbevolen!", "Geverifieerde recensie"),
        ("J", "#22c55e", "John Fairs", "🇬🇧", "VK", "3 weken geleden", "Eersteklas! Benoit is geweldig, surfgids Abu is ongelooflijk en Arame's kookkunst was fantastisch. De golven waren elke dag perfect. Wat wil je nog meer!", "Geverifieerde recensie"),
        ("M", "#f59e0b", "Milo G.", "🇫🇷", "Frankrijk", "2 maanden geleden", "Een uitzonderlijk verblijf! De organisatie is onberispelijk — je surft twee keer per dag en wordt naar verschillende spots gebracht op basis van de omstandigheden. Echte progressie in het water. 100% aanbevolen.", "Geverifieerde recensie"),
        ("S", "#10b981", "Stephan B.", "🇩🇪", "Duitsland", "5 dagen geleden", "Twee buitengewone weken: fascinerende gesprekken, geweldige ontmoetingen, uitzonderlijke golven, onberispelijke service en eten. De beste surfkamp-ervaring ooit. Tot volgend seizoen!", "Geverifieerde recensie"),
    ],
    "ar": [
        ("ج", "#ff5a1f", "Julie F.", "🇫🇷", "فرنسا", "اليوم", "مخيم Teranga للأمواج مكان رائع لجميع عشاق ركوب الأمواج! المخيم، المواقع، التدريب، الجزيرة، الأجواء، الطعام والترحيب... باختصار، يستحق اسمه — إنها الضيافة السنغالية! لا تتردد!", "تقييم موثق"),
        ("أ", "#0ea5e9", "Addie W.", "🇺🇸", "الولايات المتحدة", "منذ شهرين", "ذهبت إلى داكار عدة مرات لركوب الأمواج. أبو، في رأيي، أفضل مرشد ركوب أمواج في داكار. يعرف كيف يضعك على الموجة ويضمن سلامة الجميع. لا بد من التجربة!", "تقييم موثق"),
        ("ف", "#9c27b0", "F. F.", "🇪🇺", "أوروبا", "منذ 3 أسابيع", "عدت للتو من أسبوع مذهل في Ngor Surfcamp مع ابنتي البالغة 16 عاماً. استقبال احترافي في المطار، تنظيم لا تشوبه شائبة، تدريب ممتاز، وجبات لذيذة. أوصي به 100%!", "تقييم موثق"),
        ("ج", "#22c55e", "John Fairs", "🇬🇧", "المملكة المتحدة", "منذ 3 أسابيع", "من الدرجة الأولى! Benoit رائع، مرشد الأمواج Abu لا يصدق، وطبخ Arame كان رائعاً. كانت الأمواج مثالية كل يوم. ماذا تريد أكثر!", "تقييم موثق"),
        ("م", "#f59e0b", "Milo G.", "🇫🇷", "فرنسا", "منذ شهرين", "إقامة استثنائية! التنظيم لا تشوبه شائبة — تركب الأمواج مرتين يومياً وتُنقل إلى مواقع مختلفة حسب الظروف. تقدم حقيقي في الماء. أوصي به 100%.", "تقييم موثق"),
        ("س", "#10b981", "Stephan B.", "🇩🇪", "ألمانيا", "منذ 5 أيام", "أسبوعان استثنائيان: محادثات رائعة، لقاءات ممتازة، أمواج استثنائية، خدمة وطعام لا تشوبهما شائبة. أفضل تجربة مخيم أمواج مررت بها. إلى الموسم القادم!", "تقييم موثق"),
    ],
}


def build_home_reviews_inner_html(lang: str) -> str:
    """Localized review cards for home slider (static EN template is source layout)."""
    L = BOOKING_SOCIAL_L10N.get(lang, BOOKING_SOCIAL_L10N["en"])
    rc_tip = L["rc_tip"]
    prefix = ui_chrome("review_by", lang)
    rows = BOOKING_REVIEWS.get(lang, BOOKING_REVIEWS["en"])
    stars = (
        '<span style="font-size:14px;color:var(--sand)">★</span>'
        '<span style="font-size:14px;color:var(--sand)">★</span>'
        '<span style="font-size:14px;color:var(--sand)">★</span>'
        '<span style="font-size:14px;color:var(--sand)">★</span>'
        '<span style="font-size:14px;color:var(--sand)">★</span>'
    )
    verified_svg = (
        '<svg viewBox="0 0 16 16" fill="none"><path d="M8 1L9.8 4.7L14 5.3L11 8.2L11.7 12.4L8 10.4L4.3 12.4L5 8.2L2 5.3L6.2 4.7L8 1Z" '
        'fill="#4285f4" stroke="#4285f4" stroke-width="0.5"/></svg>'
    )
    chunks = []
    for initial, bg, name, flag, country, date, text, verified in rows:
        safe_name = html_module.escape(name)
        aria = html_module.escape(f"{prefix} {name}")
        chunks.append(
            f'<div class="review-card" data-slide aria-label="{aria}">\n'
            f'  <div class="rc-head">\n'
            f'    <div class="rc-avatar" style="background:{bg}">{html_module.escape(initial)}</div>\n'
            f"    <div class=\"rc-info\">\n"
            f'      <div class="rc-name">{safe_name}</div>\n'
            f'      <div class="rc-meta">\n'
            f'        <span class="rc-flag">{flag}</span>\n'
            f'        <span class="rc-country">{html_module.escape(country)}</span>\n'
            f'        <span class="rc-date">{html_module.escape(date)}</span>\n'
            f"      </div>\n"
            f"    </div>\n"
            f"  </div>\n"
            f'  <div class="rc-stars">{stars}</div>\n'
            f'  <p class="rc-text" title="{html_module.escape(rc_tip)}">{html_module.escape(text)}</p>\n'
            f'  <div class="rc-verified">\n'
            f"    {verified_svg}\n"
            f"    {html_module.escape(verified)}\n"
            f"  </div>\n"
            f"</div>"
        )
    return "\n".join(chunks)


def patch_home_reviews_slider_all():
    """Replace home review cards + Google badge label for non-EN locales (fixes mixed EN/AR slider)."""
    inner_re = re.compile(
        r'(<div class="reviews-inner" id="reviews-inner">)([\s\S]*?)(\s*</div>\s*</div>\s*<div class="reviews-nav">)',
        re.MULTILINE,
    )
    badge_re = re.compile(
        r'(<div class="google-badge"><svg viewBox="0 0 24 24">[\s\S]*?</svg>)\s*Google(\s*</div>)',
    )
    n = 0
    for lang in LANGS:
        if lang == "en":
            continue
        rel = f"{lang}/index.html"
        path = os.path.join(DEMO_DIR, rel)
        if not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8", errors="replace") as f:
            h = f.read()
        h2 = inner_re.sub(r"\1\n" + build_home_reviews_inner_html(lang) + r"\3", h, count=1)
        brand = HOME_REVIEWS_GOOGLE_BADGE.get(lang, "Google")
        h2 = badge_re.sub(r"\1 " + html_module.escape(brand) + r"\2", h2, count=1)
        if h2 != h:
            with open(path, "w", encoding="utf-8") as f:
                f.write(h2)
            n += 1
    print(f"  home reviews slider: rebuilt inner + badge for {n} non-EN home pages")


GOOGLE_G_ICON = (
    '<svg viewBox="0 0 24 24" width="28" height="28" aria-hidden="true">'
    '<path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>'
    '<path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>'
    '<path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>'
    '<path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>'
    "</svg>"
)


def _booking_review_card_row(initial, bg, name, flag, country, date, text, verified, rc_tip):
    stars = (
        '<span style="font-size:14px;color:#e8a317">★</span>'
        '<span style="font-size:14px;color:#e8a317">★</span>'
        '<span style="font-size:14px;color:#e8a317">★</span>'
        '<span style="font-size:14px;color:#e8a317">★</span>'
        '<span style="font-size:14px;color:#e8a317">★</span>'
    )
    safe_name = html_module.escape(name)
    return (
        f'<div class="booking-rv-card" aria-label="{safe_name}">'
        f'<div class="rc-head">'
        f'<div class="rc-avatar" style="background:{bg};flex-shrink:0">{html_module.escape(initial)}</div>'
        f'<div class="rc-info">'
        f'<div class="rc-name">{safe_name}</div>'
        f'<div class="rc-meta">'
        f'<span class="rc-flag">{flag}</span> '
        f'<span class="rc-country">{html_module.escape(country)}</span>'
        f'</div></div></div>'
        f'<div class="rc-stars" style="margin:10px 0 8px">{stars}</div>'
        f'<p class="rc-text" style="font-size:14px;line-height:1.6;color:#374151;margin:0 0 14px">{html_module.escape(text)}</p>'
        f'<div class="rc-verified" style="font-size:12px;color:#6b7280;display:flex;align-items:center;gap:5px">'
        f'<svg viewBox="0 0 16 16" fill="none" width="13" height="13"><path d="M8 1L9.8 4.7L14 5.3L11 8.2L11.7 12.4L8 10.4L4.3 12.4L5 8.2L2 5.3L6.2 4.7L8 1Z" fill="#4285f4" stroke="#4285f4" stroke-width="0.5"/></svg> '
        f'<span>{html_module.escape(verified)}</span> '
        f'<span style="margin-left:auto;color:#9ca3af">{html_module.escape(date)}</span>'
        f"</div></div>"
    )


def booking_social_proof_block(lang):
    """Google badge only — reviews moved to full-width section below."""
    L = BOOKING_SOCIAL_L10N.get(lang, BOOKING_SOCIAL_L10N["en"])
    stars_hdr = (
        '<span style="font-size:15px;color:#f0c060">★</span>'
        '<span style="font-size:15px;color:#f0c060">★</span>'
        '<span style="font-size:15px;color:#f0c060">★</span>'
        '<span style="font-size:15px;color:#f0c060">★</span>'
        '<span style="font-size:15px;color:rgba(240,192,96,0.35)">★</span>'
    )
    return f"""
          <div class="form-card reveal booking-google-card" style="margin-top:20px">
            <div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap">
              <div style="width:52px;height:52px;border-radius:12px;background:#fff;box-shadow:0 2px 10px rgba(10,37,64,0.08);display:flex;align-items:center;justify-content:center;border:1px solid rgba(10,37,64,0.06)">{GOOGLE_G_ICON}</div>
              <div style="flex:1;min-width:160px">
                <div style="font-size:11px;font-weight:800;color:#6b7280;text-transform:uppercase;letter-spacing:0.12em">{html_module.escape(L["google_lbl"])}</div>
                <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin-top:6px">
                  <span style="font-family:var(--fh);font-size:32px;font-weight:900;color:var(--navy);line-height:1">{html_module.escape(L["score"])}</span>
                  <span style="display:inline-flex;gap:2px;align-items:center">{stars_hdr}</span>
                </div>
                <div style="font-size:13px;color:#6b7280;margin-top:4px">{html_module.escape(L["count"])}</div>
              </div>
            </div>
            <div style="display:flex;gap:10px;margin-top:18px;flex-wrap:wrap">
              <a href="{BOOKING_GOOGLE_MAPS}" target="_blank" rel="noopener noreferrer" class="btn btn-deep btn-sm" style="font-size:12px">{html_module.escape(L["maps"])}</a>
              <a href="{BOOKING_GOOGLE_REVIEW}" target="_blank" rel="noopener noreferrer" class="btn btn-fire btn-sm" style="font-size:12px">{html_module.escape(L["leave"])}</a>
            </div>
          </div>"""


def booking_reviews_section(lang):
    """Full-width 2-column review grid rendered below the form/sidebar split."""
    L = BOOKING_SOCIAL_L10N.get(lang, BOOKING_SOCIAL_L10N["en"])
    rows = BOOKING_REVIEWS.get(lang, BOOKING_REVIEWS["en"])
    cards = "".join(_booking_review_card_row(*t, L["rc_tip"]) for t in rows)
    return f"""
  <section style="background:#f8fafc;padding:56px 24px 64px;border-top:1px solid rgba(10,37,64,0.07)">
    <div class="container">
      <div style="text-align:center;margin-bottom:36px">
        <span class="s-label" style="font-size:11px">{html_module.escape(L["rv_eyebrow"])}</span>
        <h2 style="font-size:clamp(22px,3vw,30px);font-weight:900;color:var(--navy);margin:10px 0 0">{html_module.escape(L["rv_h"])}</h2>
      </div>
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:20px;max-width:1100px;margin:0 auto">
        {cards}
      </div>
    </div>
  </section>"""


def _home_google_stars_partial():
    return (
        '<span style="font-size:14px;color:#e8a317">★</span>'
        '<span style="font-size:14px;color:#e8a317">★</span>'
        '<span style="font-size:14px;color:#e8a317">★</span>'
        '<span style="font-size:14px;color:#e8a317">★</span>'
        '<span style="font-size:14px;color:rgba(232,163,23,0.35)">★</span>'
    )


HOME_PROOF_L10N = {
    "en": {
        "aria": "Camp highlights",
        "eyebrow": "The essentials",
        "f1_n": "2×",
        "f1_t": "daily surf sessions",
        "f1_d": "Morning & afternoon — spots chosen by forecast",
        "f2_n": "1964",
        "f2_t": "Endless Summer",
        "f2_d": "The cult film that put Ngor on the global surf map",
        "f3_n": "All",
        "f3_t": "levels",
        "f3_d": "Beginner to advanced — Abu, best surf guide in Dakar",
    },
    "fr": {
        "aria": "Points forts",
        "eyebrow": "L’essentiel",
        "f1_n": "2×",
        "f1_t": "sessions surf/jour",
        "f1_d": "Matin & après-midi — spots selon les conditions",
        "f2_n": "1964",
        "f2_t": "Endless Summer",
        "f2_d": "Le film culte qui a placé Ngor sur la carte du surf mondial",
        "f3_n": "Tous",
        "f3_t": "niveaux",
        "f3_d": "Débutant à confirmé — Abu, meilleur guide surf de Dakar",
    },
    "es": {
        "aria": "Lo esencial",
        "eyebrow": "Lo esencial",
        "f1_n": "2×",
        "f1_t": "sesiones surf/día",
        "f1_d": "Mañana y tarde — spots según las condiciones",
        "f2_n": "1964",
        "f2_t": "Endless Summer",
        "f2_d": "La película de culto que puso Ngor en el mapa del surf mundial",
        "f3_n": "Todos",
        "f3_t": "los niveles",
        "f3_d": "Principiante a avanzado — Abu, mejor guía surf de Dakar",
    },
    "it": {
        "aria": "L’essenziale",
        "eyebrow": "L’essenziale",
        "f1_n": "2×",
        "f1_t": "sessioni surf/giorno",
        "f1_d": "Mattina e pomeriggio — spot scelti in base alle condizioni",
        "f2_n": "1964",
        "f2_t": "Endless Summer",
        "f2_d": "Il film culto che ha messo Ngor sulla mappa del surf mondiale",
        "f3_n": "Tutti",
        "f3_t": "i livelli",
        "f3_d": "Da principiante ad avanzato — Abu, miglior guida surf di Dakar",
    },
    "de": {
        "aria": "Highlights",
        "eyebrow": "Das Wichtigste",
        "f1_n": "2×",
        "f1_t": "Surfsessions täglich",
        "f1_d": "Morgens & nachmittags — Spots nach Forecast ausgewählt",
        "f2_n": "1964",
        "f2_t": "Endless Summer",
        "f2_d": "Der Kultfilm, der Ngor auf die Surf-Weltkarte brachte",
        "f3_n": "Alle",
        "f3_t": "Level",
        "f3_d": "Anfänger bis Profi — Abu, bester Surfguide in Dakar",
    },
    "nl": {
        "aria": "Camphoogtepunten",
        "eyebrow": "De essentie",
        "f1_n": "2×",
        "f1_t": "dagelijkse surfsessies",
        "f1_d": "Ochtend & middag — spots gekozen op basis van de voorspelling",
        "f2_n": "1964",
        "f2_t": "Endless Summer",
        "f2_d": "De cultfilm die Ngor op de wereldwijde surfkaart zette",
        "f3_n": "Alle",
        "f3_t": "niveaus",
        "f3_d": "Beginner tot gevorderd — Abu, beste surfgids van Dakar",
    },
    "ar": {
        "aria": "أبرز مزايا المخيم",
        "eyebrow": "الأساسيات",
        "f1_n": "2×",
        "f1_t": "حصص ركوب أمواج يومية",
        "f1_d": "صباحاً ومساءً — المواقع تُختار حسب التوقعات",
        "f2_n": "1964",
        "f2_t": "Endless Summer",
        "f2_d": "الفيلم الذي وضع نغور على الخريطة",
        "f3_n": "جميع",
        "f3_t": "المستويات",
        "f3_d": "من المبتدئين إلى المحترفين — أبو، أفضل مرشد أمواج في داكار",
    },
}


# ── Home Gallery: curated images ──────────────────────────────────────
HOME_GALLERY_IMGS = [
    f"{_WIX}/df99f9_dd89cc4d86d4402189d7e9516ce672a3.webp",   # surf coaching
    f"{_WIX}/df99f9_2ec6248367cd4e21a5e6c26c2b0a1c35.webp",   # surf house terrace
    f"{_WIX}/df99f9_eba4c24ec6a746b58d60a975b8d20946.webp",   # house & ocean
    f"{_WIX}/11062b_89a070321f814742a620b190592d51ad.webp",   # surf action
    f"{_WIX}/df99f9_a18d512828d9487e9a4987b9903960e0.webp",   # pool
    f"{_WIX}/df99f9_753890483d8e4cca8e2051a13f9c558e.webp",   # senegalese food
    f"{_WIX}/df99f9_d6e404dd3cf74396b6ea874cb7021a27.webp",   # sunset
    f"{_WIX}/11062b_7f89d2db0ace4027ac4a00928a6aca08.webp",   # ngor right wave
    f"{_WIX}/df99f9_961b0768e713457f93025f4ce6fb1419.webp",   # surf camp
    f"{_WIX}/df99f9_d8e77cf4807249f6953119f18be64166.webp",   # house interior
    f"{_WIX}/df99f9_d81668a18a9d49d1b5ebb0ea3a0abbc7.webp",   # island art
    f"{_WIX}/b28af82dbec544138f16e2bc5a85f2cb.webp",          # island aerial
]

HOME_GALLERY_L10N = {
    "en": {
        "lbl": "Gallery", "h2": "Island Life in Pictures", "cta": "View all photos",
        "caps": [
            "Morning coaching session", "Terrace with sea view", "Ocean view from the house",
            "Perfect wave at Ngor Right", "Poolside afternoon", "Homemade Senegalese cuisine",
            "Golden hour at Ngor", "The legendary Ngor Right wave", "Ngor Surfcamp Teranga",
            "Light & airy rooms", "Island vibes & local art", "Ngor Island from above",
        ],
    },
    "fr": {
        "lbl": "Galerie", "h2": "La vie sur l'île en images", "cta": "Voir toutes les photos",
        "caps": [
            "Session coaching du matin", "Terrasse vue mer", "Vue océan depuis la maison",
            "Vague parfaite à Ngor Right", "Après-midi au bord de la piscine", "Cuisine sénégalaise maison",
            "Coucher de soleil doré à Ngor", "La mythique vague Ngor Right", "Ngor Surfcamp Teranga",
            "Chambres lumineuses", "Ambiance île & art local", "L'île de Ngor depuis les airs",
        ],
    },
    "es": {
        "lbl": "Galería", "h2": "La isla en imágenes", "cta": "Ver todas las fotos",
        "caps": [
            "Sesión de coaching matutina", "Terraza con vistas al mar", "Vista al océano desde la casa",
            "Ola perfecta en Ngor Right", "Tarde junto a la piscina", "Cocina senegalesa casera",
            "Hora dorada en Ngor", "La legendaria ola Ngor Right", "Ngor Surfcamp Teranga",
            "Habitaciones luminosas", "Ambiente isla & arte local", "La isla de Ngor desde arriba",
        ],
    },
    "it": {
        "lbl": "Galleria", "h2": "La vita sull'isola in foto", "cta": "Vedi tutte le foto",
        "caps": [
            "Sessione di coaching mattutina", "Terrazza con vista mare", "Vista oceano dalla casa",
            "Onda perfetta a Ngor Right", "Pomeriggio in piscina", "Cucina senegalese fatta in casa",
            "Tramonto dorato a Ngor", "La leggendaria onda Ngor Right", "Ngor Surfcamp Teranga",
            "Camere luminose", "Atmosfera isola & arte locale", "L'isola di Ngor dall'alto",
        ],
    },
    "de": {
        "lbl": "Galerie", "h2": "Inselleben in Bildern", "cta": "Alle Fotos ansehen",
        "caps": [
            "Morgen-Coaching-Session", "Terrasse mit Meerblick", "Meerblick vom Haus",
            "Perfekte Welle bei Ngor Right", "Nachmittag am Pool", "Hausgemachte senegalesische Küche",
            "Goldene Stunde in Ngor", "Die legendäre Ngor Right Welle", "Ngor Surfcamp Teranga",
            "Helle & luftige Zimmer", "Inselatmosphäre & lokale Kunst", "Ngor Island von oben",
        ],
    },
    "nl": {
        "lbl": "Galerij", "h2": "Eilandleven in foto's", "cta": "Bekijk alle foto's",
        "caps": [
            "Ochtend coaching sessie", "Terras met zeezicht", "Oceaanzicht vanuit het huis",
            "Perfecte golf bij Ngor Right", "Middag bij het zwembad", "Huisgemaakte Senegalese keuken",
            "Gouden uur in Ngor", "De legendarische Ngor Right golf", "Ngor Surfcamp Teranga",
            "Lichte & luchtige kamers", "Eilandvibes & lokale kunst", "Ngor Island vanuit de lucht",
        ],
    },
    "ar": {
        "lbl": "معرض الصور", "h2": "حياة الجزيرة بالصور", "cta": "عرض جميع الصور",
        "caps": [
            "جلسة تدريب صباحية", "شرفة بإطلالة بحرية", "منظر المحيط من المنزل",
            "موجة مثالية في Ngor Right", "بعد الظهر بجانب المسبح", "المطبخ السنغالي الأصيل",
            "الساعة الذهبية في نغور", "الموجة الأسطورية Ngor Right", "Ngor Surfcamp Teranga",
            "غرف مضيئة ومريحة", "أجواء الجزيرة والفن المحلي", "جزيرة نغور من الجو",
        ],
    },
}

ARROW_ICO_PREV = '<svg viewBox="0 0 24 24" fill="none" width="18" height="18"><path d="M15 18l-6-6 6-6" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
ARROW_ICO_NEXT = '<svg viewBox="0 0 24 24" fill="none" width="18" height="18"><path d="M9 6l6 6-6 6" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
ARROW_ICO_RIGHT_SMALL = '<svg viewBox="0 0 16 16" fill="none" width="13" height="13"><path d="M4 8h8M8 4l4 4-4 4" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>'


def home_gallery_html(lang):
    """Refined split-layout gallery: copy left, crossfade slider right."""
    gl = HOME_GALLERY_L10N.get(lang, HOME_GALLERY_L10N["en"])
    pfx = LANG_PFX[lang]
    gal_href = f"{pfx}/{SLUG[lang]['gallery']}/" if pfx else f"/{SLUG['en']['gallery']}/"
    total = len(HOME_GALLERY_IMGS)

    caps = gl.get("caps", [""] * total)

    slides = ""
    for i, url in enumerate(HOME_GALLERY_IMGS):
        thumb = wix_thumb_url(url, 900)
        lazy = 'loading="eager" fetchpriority="high"' if i == 0 else 'loading="lazy"'
        active = " hg-active" if i == 0 else ""
        cap = caps[i] if i < len(caps) else ""
        slides += (
            f'<img class="hg-img{active}" src="{thumb}" '
            f'alt="{escape(gl["h2"])} {i+1}" width="900" height="600" '
            f'decoding="async" referrerpolicy="no-referrer" {lazy}'
            f' data-caption="{escape(cap)}">'
        )

    first_cap = escape(caps[0]) if caps else ""

    return f"""
  <section class="home-gallery-sec">
    <div class="hg-inner">

      <div class="hg-copy reveal">
        <span class="s-label">{escape(gl["lbl"])}</span>
        <h2 class="hg-title">{escape(gl["h2"])}</h2>
        <div class="hg-count-wrap">
          <span class="hg-cur-num" id="hg-cur-num">01</span>
          <span class="hg-sep">/</span>
          <span class="hg-tot-num">{total:02d}</span>
        </div>
        <a href="{gal_href}" class="hg-cta-link">{escape(gl["cta"])} {ARROW_ICO_RIGHT_SMALL}</a>
      </div>

      <div class="hg-frame-wrap">
        <div class="hg-frame" id="hg-viewport" aria-label="{escape(gl["h2"])}">
          {slides}
          <div class="hg-caption hg-cap-visible" id="hg-caption">{first_cap}</div>
          <div class="hg-frame-bar"><div class="hg-progress-fill" id="hg-progress-fill"></div></div>
        </div>
        <div class="hg-controls">
          <div class="hg-dots" id="hg-dots"></div>
          <div class="hg-arrows">
            <button class="hg-btn" id="hg-prev" aria-label="{escape(ui_chrome('gallery_prev', lang))}">{ARROW_ICO_PREV}</button>
            <button class="hg-btn" id="hg-next" aria-label="{escape(ui_chrome('gallery_next', lang))}">{ARROW_ICO_NEXT}</button>
          </div>
        </div>
      </div>

    </div>
  </section>"""


HOME_GALLERY_FILES = HOME_PAGES  # same 5 index files

# Marker: insert gallery before the wave that precedes <!-- BLOG PREVIEW -->
_HG_BEFORE = '\n\n  <div class="wave-top" style="background:#fff8ec"'


def patch_home_gallery_all():
    """Inject cinematic gallery slider before the blog section on all home pages."""
    n = 0
    for rel, lang in zip(HOME_GALLERY_FILES, LANGS):
        path = os.path.join(DEMO_DIR, rel)
        if not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8", errors="replace") as f:
            h = f.read()
        if 'home-gallery-sec' in h:
            # Remove ALL existing gallery sections before re-injecting
            import re as _re2
            # Use a broader pattern that works regardless of inner </section> nesting
            while '<section class="home-gallery-sec">' in h:
                start = h.find('<section class="home-gallery-sec">')
                # Walk forward to find the matching </section>
                depth = 0
                i = start
                while i < len(h):
                    if h[i:i+8] == '<section':
                        depth += 1
                    elif h[i:i+10] == '</section>':
                        depth -= 1
                        if depth == 0:
                            end = i + 10
                            # Also eat the preceding newline if any
                            pre = start - 1
                            while pre >= 0 and h[pre] in '\n\r ':
                                pre -= 1
                            h = h[:pre+1] + h[end:]
                            break
                    i += 1
                else:
                    break
        if _HG_BEFORE in h:
            gallery = home_gallery_html(lang)
            h2 = h.replace(_HG_BEFORE, gallery + _HG_BEFORE, 1)
            if h2 != h:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(h2)
                n += 1
    print(f"  home gallery: updated {n} files")


def home_proof_strip_html(lang):
    """Light hero-to-content bridge: facts + Google (home only)."""
    P = HOME_PROOF_L10N.get(lang, HOME_PROOF_L10N["en"])
    L = BOOKING_SOCIAL_L10N.get(lang, BOOKING_SOCIAL_L10N["en"])
    stars = _home_google_stars_partial()

    def fact(n, t, d):
        return (
            f'<div class="home-proof-fact">'
            f'<span class="home-proof-fact-n">{html_module.escape(n)}</span>'
            f'<div class="home-proof-fact-body">'
            f'<span class="home-proof-fact-t">{html_module.escape(t)}</span>'
            f'<span class="home-proof-fact-d">{html_module.escape(d)}</span>'
            f"</div></div>"
        )

    facts = fact(P["f1_n"], P["f1_t"], P["f1_d"]) + fact(P["f2_n"], P["f2_t"], P["f2_d"]) + fact(P["f3_n"], P["f3_t"], P["f3_d"])

    return f"""  <section class="home-proof-strip" aria-label="{html_module.escape(P["aria"])}">
    <div class="container">
      <p class="home-proof-eyebrow">{html_module.escape(P["eyebrow"])}</p>
      <div class="home-proof-grid">
        <div class="home-proof-facts">
          {facts}
        </div>
        <div class="home-proof-google-card">
          <div class="home-proof-google-top">
            <div class="home-proof-g-badge" aria-hidden="true">{GOOGLE_G_ICON}</div>
            <div class="home-proof-google-copy">
              <span class="home-proof-google-lbl">{html_module.escape(L["google_lbl"])}</span>
              <div class="home-proof-google-scoreline">
                <span class="home-proof-score-num">{html_module.escape(L["score"])}</span>
                <span class="home-proof-score-stars">{stars}</span>
              </div>
              <span class="home-proof-google-count">{html_module.escape(L["count"])}</span>
            </div>
          </div>
          <div class="home-proof-google-btns">
            <a href="{BOOKING_GOOGLE_MAPS}" target="_blank" rel="noopener noreferrer" class="btn btn-deep btn-sm">{html_module.escape(L["maps"])}</a>
            <a href="{BOOKING_GOOGLE_REVIEW}" target="_blank" rel="noopener noreferrer" class="btn btn-outline btn-sm" style="border-color:rgba(10,37,64,0.2);color:var(--navy)">{html_module.escape(L["leave"])}</a>
          </div>
        </div>
      </div>
    </div>
  </section>"""


def patch_home_proof_strip_all():
    """Inject / refresh home proof strip (facts + Google) on all home pages."""
    start_markers = (
        "  <!-- STATS with counter animation -->",
        "  <!-- Home proof strip -->",
    )
    end = "  <!-- ABOUT SPLIT -->"
    for lang in LANGS:
        rel = "index.html" if lang == "en" else f"{lang}/index.html"
        path = os.path.join(DEMO_DIR, rel)
        if not os.path.isfile(path):
            print(f"  skip home proof strip: missing {rel}")
            continue
        with open(path, encoding="utf-8") as f:
            h = f.read()
        i0 = -1
        for sm in start_markers:
            i0 = h.find(sm)
            if i0 >= 0:
                break
        i1 = h.find(end)
        if i0 < 0 or i1 < 0 or i1 <= i0:
            print(f"  skip home proof strip: markers not found in {rel}")
            continue
        block = f"  <!-- Home proof strip -->\n{home_proof_strip_html(lang)}\n\n"
        h2 = h[:i0] + block + h[i1:]
        with open(path, "w", encoding="utf-8") as f:
            f.write(h2)
        print(f"  home proof strip: {rel}")


# Inline SVG for surfing "included" cards (PNG assets are optional / often missing)
FEAT_SVG_INLINE = {
    # ── Surfing page icons ──────────────────────────────────────────
    "feat-guide":    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2C6 2 2 8 2 14c0 3.5 2.5 6 5 8"/><path d="M22 14c0-4-2-8-6-11"/><path d="M8 19s1-1 4-1 4 1 4 1"/><circle cx="12" cy="12" r="3"/><path d="M12 9V2M12 22v-7"/></svg>',
    "feat-video":    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="6" width="14" height="12" rx="2"/><path d="M16 10l5-3v10l-5-3V10z"/><circle cx="9" cy="12" r="2"/></svg>',
    "feat-coaching": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="7" r="4"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/><path d="M17 12l3 2-3 2"/></svg>',
    "feat-check":    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5"/></svg>',
    "feat-theory":   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="14" rx="2"/><path d="M7 21h10M12 17v4"/><path d="M7 8h10M7 11h6"/></svg>',
    "feat-location": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2C8 2 5 5 5 9c0 6 7 13 7 13s7-7 7-13c0-4-3-7-7-7z"/><circle cx="12" cy="9" r="2.5"/></svg>',
    "feat-transfer": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21 14H3l2-7h14l2 7z"/><path d="M3 14c3 3 15 3 18 0"/><path d="M8 7V5a2 2 0 014 0v2"/></svg>',
    "icon-federation": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.65" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l7 3v5c0 5-3 8-7 9-4-1-7-4-7-9V6l7-3z"/><path d="M9 12l2 2 4-5"/></svg>',
    # ── Surf-house feature icons ────────────────────────────────────
    # feat-check is REUSED from above (checkmark = "all included")
    "feat-food":      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8h1a4 4 0 010 8h-1"/><path d="M2 8h16v9a4 4 0 01-4 4H6a4 4 0 01-4-4V8z"/><line x1="6" y1="1" x2="6" y2="4"/><line x1="10" y1="1" x2="10" y2="4"/><line x1="14" y1="1" x2="14" y2="4"/></svg>',
    "feat-pool":      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12c1.5 2 3.5 2 5 0s3.5-2 5 0 3.5 2 5 0"/><path d="M2 17c1.5 2 3.5 2 5 0s3.5-2 5 0 3.5 2 5 0"/><path d="M7 4l3-3 4 3"/><path d="M14 4v8"/></svg>',
    "feat-wifi":      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M1.42 9A16 16 0 0122.58 9"/><path d="M5 12.55a11 11 0 0114.08 0"/><path d="M10.71 17.09a6 6 0 012.58 0"/><circle cx="12" cy="20" r="1" fill="currentColor" stroke="none"/></svg>',
    "feat-rooms":     '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21V7a2 2 0 012-2h14a2 2 0 012 2v14"/><path d="M3 21h18"/><path d="M9 10h6M9 10v5h6v-5"/></svg>',
    "icon-checklist": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/></svg>',
}

SURF_PAGE_INDEX_FILES = [
    "surfing/index.html",
    "fr/surf/index.html",
    "es/surf/index.html",
    "it/surf/index.html",
    "de/surfen/index.html",
]

FEAT_ICON_IMG_MAP = [
    ("/assets/images/icons/feat-guide.webp", "feat-guide"),
    ("/assets/images/icons/feat-video.webp", "feat-video"),
    ("/assets/images/icons/feat-coaching.webp", "feat-coaching"),
    ("/assets/images/icons/feat-check.webp", "feat-check"),
    ("/assets/images/icons/icon-theory.webp", "feat-theory"),
    ("/assets/images/icons/icon-location.webp", "feat-location"),
    ("/assets/images/icons/icon-transfer.webp", "feat-transfer"),
]


def patch_home_blog_preview_all():
    """Replace home page blog preview with 6 cards (2 rows of 3) in the correct language."""
    BLOG_LABEL = {"en":"Latest from the Blog","fr":"Derniers articles du Blog",
                  "es":"Últimos artículos del Blog","it":"Ultimi articoli dal Blog","de":"Neuestes aus dem Blog",
                  "nl":"Laatste van de Blog","ar":"أحدث المقالات"}
    BLOG_EYEBROW = {"en":"Blog","fr":"Blog","es":"Blog","it":"Blog","de":"Blog","nl":"Blog","ar":"المدونة"}
    ALL_LABEL  = {"en":"All Articles","fr":"Tous les articles","es":"Todos los artículos",
                  "it":"Tutti gli articoli","de":"Alle Artikel","nl":"Alle artikelen","ar":"كل المقالات"}
    FALLBACK_IMG = "/assets/images/wix/df99f9_961b0768e713457f93025f4ce6fb1419.webp"

    # Load English articles in sorted order
    en_art_dir = os.path.join(CONTENT, "articles", "en")
    if not os.path.isdir(en_art_dir):
        print("  home blog preview: articles/en dir not found, skipping")
        return
    en_slugs = sorted([f[:-5] for f in os.listdir(en_art_dir) if f.endswith(".json")])

    # Build per-lang translated articles lookup (articles/{lang} + articles_v2/{lang} only)
    arts_by_lang = {}
    for lang in LANGS:
        arts_by_lang[lang] = {}
        lang_dir = os.path.join(CONTENT, "articles", lang)
        v2_dir = os.path.join(CONTENT, "articles_v2", lang)
        if os.path.isdir(lang_dir):
            for fname in os.listdir(lang_dir):
                if not fname.endswith(".json"):
                    continue
                a = load(os.path.join(lang_dir, fname))
                if not a:
                    continue
                slug_key = a.get("original_en_slug", a.get("slug", ""))
                v2p = os.path.join(v2_dir, fname)
                v2a = load(v2p) if os.path.exists(v2p) else None
                if v2a and v2a.get("content_markdown", "").strip():
                    arts_by_lang[lang][slug_key] = v2a
                else:
                    arts_by_lang[lang][slug_key] = a
        if os.path.isdir(v2_dir):
            for fname in os.listdir(v2_dir):
                if not fname.endswith(".json"):
                    continue
                v2p = os.path.join(v2_dir, fname)
                v2a = load(v2p)
                if not v2a or not v2a.get("content_markdown", "").strip():
                    continue
                slug_key = v2a.get("original_en_slug") or v2a.get("hreflang_en") or v2a.get("slug") or fname[:-5]
                arts_by_lang[lang][slug_key] = v2a

    n_updated = 0
    for lang in LANGS:
        rel  = "index.html" if lang == "en" else f"{lang}/index.html"
        path = os.path.join(DEMO_DIR, rel)
        if not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8") as f:
            h = f.read()

        pfx = LANG_PFX[lang]

        # Build 6 blog cards
        cards_html = ""
        for slug in en_slugs[:6]:
            en_art  = load(os.path.join(en_art_dir, f"{slug}.json")) or {}
            art     = arts_by_lang[lang].get(slug, en_art) if lang != "en" else en_art
            title_  = fix_em(art.get("title", en_art.get("title", slug)))[:80]
            meta_   = fix_em(art.get("meta_description", en_art.get("meta_description", "")))[:120]
            cat_    = en_art.get("category", "")
            # Must check .webp (B&W preferred, then colour, then fallback)
            img_bw   = os.path.join(DEMO_DIR, "assets", "images", f"bw-{slug}.webp")
            img_webp = os.path.join(DEMO_DIR, "assets", "images", f"{slug}.webp")
            if os.path.exists(img_bw):
                img_src = f"/assets/images/bw-{slug}.webp"
            elif os.path.exists(img_webp):
                img_src = f"/assets/images/{slug}.webp"
            else:
                img_src = FALLBACK_IMG
            cards_html += (
                f'\n      <a href="{pfx}/blog/{slug}/" class="card" style="text-decoration:none">'
                f'\n        <img src="{img_src}" alt="{escape(title_)}" class="card-img" loading="lazy"'
                f' onerror="this.src=\'{FALLBACK_IMG}\'">'
                f'\n        <div class="card-body">'
                f'\n          <span class="cat-badge">{escape(BLOG_CATS.get(cat_, {}).get("name", {}).get(lang, cat_))}</span>'
                f'\n          <h3 class="card-h3" style="margin-top:10px;font-size:17px">{escape(title_)}</h3>'
                f'\n          <p class="card-text">{escape(meta_)}</p>'
                f'\n        </div>'
                f'\n      </a>'
            )

        # Build the new blog section
        blog_slug = SLUG[lang].get("blog", "blog")
        blog_href = f"{pfx}/{blog_slug}/"
        new_section = (
            f'\n\n  <!-- BLOG PREVIEW -->'
            f'\n  <section class="section sec-sand" style="padding-top:48px">'
            f'\n    <div class="container">'
            f'\n      <div class="reveal" style="display:flex;align-items:flex-end;justify-content:space-between;margin-bottom:48px;flex-wrap:wrap;gap:16px">'
            f'\n        <div>'
            f'\n          <span class="s-label">{escape(BLOG_EYEBROW[lang])}</span>'
            f'\n          <h2 class="s-title">{escape(BLOG_LABEL[lang])}</h2>'
            f'\n        </div>'
            f'\n        <a href="{blog_href}" class="btn btn-fire">{escape(ALL_LABEL[lang])}</a>'
            f'\n      </div>'
            f'\n      <div class="blog-grid reveal">{cards_html}'
            f'\n      </div>'
            f'\n    </div>'
            f'\n  </section>'
        )

        # Replace existing BLOG PREVIEW section
        h2 = re.sub(
            r'\n\n  <!-- BLOG PREVIEW -->.*?</section>',
            new_section,
            h, flags=re.DOTALL, count=1
        )
        if h2 == h:
            print(f"  home blog preview: marker not found in {rel}, skipping")
            continue
        with open(path, "w", encoding="utf-8") as f:
            f.write(h2)
        n_updated += 1

    print(f"  home blog preview: updated {n_updated} files with 6 cards")




def patch_home_forecast_all():
    """Inject the surf forecast widget into every home page, right before the Instagram section."""
    import re as _re
    FC_COPY = {
        "en": {"lbl":"Live Forecast","h2":"Surf Conditions at Ngor","now":"Right now","height":"Wave height","period":"Period","dir":"Direction","swell":"Swell","wind":"Wind","temp":"Water temp","day7":"7-day forecast","powered":"Data: Open-Meteo.com","err":"Forecast temporarily unavailable"},
        "fr": {"lbl":"Prévisions en direct","h2":"Conditions surf à Ngor","now":"En ce moment","height":"Hauteur des vagues","period":"Période","dir":"Direction","swell":"Houle","wind":"Vent","temp":"Temp. eau","day7":"Prévisions 7 jours","powered":"Données : Open-Meteo.com","err":"Prévisions temporairement indisponibles"},
        "es": {"lbl":"Previsión en directo","h2":"Condiciones surf en Ngor","now":"Ahora mismo","height":"Altura de ola","period":"Período","dir":"Dirección","swell":"Oleaje","wind":"Viento","temp":"Temp. agua","day7":"Previsión 7 días","powered":"Datos: Open-Meteo.com","err":"Previsión no disponible temporalmente"},
        "it": {"lbl":"Previsioni live","h2":"Condizioni surf a Ngor","now":"In questo momento","height":"Altezza onde","period":"Periodo","dir":"Direzione","swell":"Mareggiata","wind":"Vento","temp":"Temp. acqua","day7":"Previsioni 7 giorni","powered":"Dati: Open-Meteo.com","err":"Previsioni temporaneamente non disponibili"},
        "de": {"lbl":"Live-Vorhersage","h2":"Surfbedingungen in Ngor","now":"Gerade jetzt","height":"Wellenhöhe","period":"Periode","dir":"Richtung","swell":"Dünung","wind":"Wind","temp":"Wassertemp.","day7":"7-Tage-Vorhersage","powered":"Daten: Open-Meteo.com","err":"Vorhersage vorübergehend nicht verfügbar"},
        "nl": {"lbl":"Live voorspelling","h2":"Surfcondities in Ngor","now":"Nu","height":"Golfhoogte","period":"Periode","dir":"Richting","swell":"Deining","wind":"Wind","temp":"Watertemp.","day7":"7-daagse voorspelling","powered":"Data: Open-Meteo.com","err":"Voorspelling tijdelijk niet beschikbaar"},
        "ar": {"lbl":"توقعات مباشرة","h2":"أحوال الأمواج في نغور","now":"الآن","height":"ارتفاع الموج","period":"الفترة","dir":"الاتجاه","swell":"الموج الطويل","wind":"الرياح","temp":"حرارة الماء","day7":"توقعات 7 أيام","powered":"البيانات: Open-Meteo.com","err":"التوقعات غير متاحة مؤقتاً"},
    }
    n = 0
    for lang in LANGS:
        rel  = "index.html" if lang == "en" else f"{lang}/index.html"
        path_f = os.path.join(DEMO_DIR, rel)
        if not os.path.isfile(path_f):
            continue
        with open(path_f, encoding="utf-8") as f:
            h = f.read()
        # Remove any existing home forecast block to avoid duplication
        h = _re.sub(r'\s*<!-- home-forecast-start -->.*?<!-- home-forecast-end -->', '', h, flags=_re.DOTALL)
        marker = "\n  <!-- ig-feed-start -->"
        if marker not in h:
            print(f"  home forecast: ig-feed marker not found in {rel}, skipping")
            continue
        c = FC_COPY.get(lang, FC_COPY["en"])
        fc_html = f"""
  <!-- home-forecast-start -->
  <section class="section sec-light" id="home-surf-forecast">
    <div class="container">
      <div style="text-align:center;margin-bottom:40px" class="reveal">
        <span class="s-label">{c["lbl"]}</span>
        <h2 class="s-title">{c["h2"]}</h2>
      </div>
      <div class="forecast-widget fc-widget reveal"
           data-lbl-now="{c["now"]}"
           data-lbl-height="{c["height"]}"
           data-lbl-period="{c["period"]}"
           data-lbl-dir="{c["dir"]}"
           data-lbl-swell="{c["swell"]}"
           data-lbl-wind="{c["wind"]}"
           data-lbl-temp="{c["temp"]}"
           data-lbl-7day="{c["day7"]}"
           data-lbl-powered="{c["powered"]}"
           data-lbl-err="{c["err"]}">
        <div class="fc-loading"><div class="fc-spinner"></div></div>
      </div>
    </div>
  </section>
  <!-- home-forecast-end -->"""
        h = h.replace(marker, fc_html + marker, 1)
        with open(path_f, "w", encoding="utf-8") as f:
            f.write(h)
        n += 1
    print(f"  home forecast section: injected into {n} home pages")

def patch_home_insta_section_all():
    """Inject the Instagram feed section into every home page, just before the blog-preview section.
    Strips any previous ig-feed-start/end block first to avoid duplication."""
    import re as _re
    n = 0
    for lang in LANGS:
        rel  = "index.html" if lang == "en" else f"{lang}/index.html"
        path = os.path.join(DEMO_DIR, rel)
        if not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8") as f:
            h = f.read()
        # ── Remove ALL pre-existing IG sections (any build vintage) ──
        # 1. New-style: wrapped in ig-feed-start / ig-feed-end markers
        h = _re.sub(
            r'\s*<!-- ig-feed-start -->.*?<!-- ig-feed-end -->',
            '',
            h,
            flags=_re.DOTALL,
        )
        # 2. Old-style: section with id="ig-feed" (no markers) + preceding comment
        h = _re.sub(
            r'\s*<!--\s*Instagram[^-]*-->\s*(?:<div[^>]*class="[^"]*wave[^"]*"[^>]*>.*?</div>\s*)?'
            r'<section[^>]*id="ig-feed"[^>]*>.*?</section>'
            r'(?:\s*<div[^>]*class="[^"]*wave[^"]*"[^>]*>.*?</div>)?',
            '',
            h,
            flags=_re.DOTALL,
        )
        # 3. Any remaining bare section with id="ig-feed"
        h = _re.sub(
            r'\s*<section[^>]*\bid="ig-feed"[^>]*>.*?</section>',
            '',
            h,
            flags=_re.DOTALL,
        )
        # 4. Orphan embed.js scripts
        h = _re.sub(
            r'\s*<script[^>]*instagram\.com/embed\.js[^>]*></script>',
            '',
            h,
            flags=_re.DOTALL,
        )
        # ── Insert fresh section right before <!-- BLOG PREVIEW --> ──
        marker = "\n\n  <!-- BLOG PREVIEW -->"
        if marker not in h:
            print(f"  home insta section: blog marker not found in {rel}, skipping")
            continue
        ig_html = insta_section(lang, "home")
        h = h.replace(marker, ig_html + marker, 1)
        with open(path, "w", encoding="utf-8") as f:
            f.write(h)
        n += 1
    print(f"  home Instagram section: injected into {n} home pages")


def patch_home_lang_ui_cleanup_all():
    """Fix leftover English chrome on localized home pages (esp. AR): hero, trust, reviews, about CTAs."""
    AR_FIXES = [
        ("Ngor Island · Dakar · Senegal", "جزيرة نغور · داكار · السنغال"),
        ("Licensed by Senegal Surf Federation", "مرخص من الاتحاد السنغالي لركوب الأمواج"),
        ("Open year-round", "مفتوح طوال العام"),
        ('aria-label="Surf quotes"', 'aria-label="اقتباسات عن ركوب الأمواج"'),
        ('aria-label="Language versions"', 'aria-label="إصدارات اللغة"'),
        ('aria-label="Reviews"', 'aria-label="التقييمات"'),
        ("What surfers say", "ماذا يقول مرتادو الأمواج"),
        ("54 reviews", "54 تقييم"),
        ('title="Click to read more"', 'title="انقر لقراءة المزيد"'),
        ('aria-label="Previous reviews"', 'aria-label="التقييمات السابقة"'),
        ('aria-label="Next reviews"', 'aria-label="التقييمات التالية"'),
        ('id="fq-dots-en"', 'id="fq-dots-ar"'),
        (
            '<a href="/surf-house/" class="btn btn-deep">The Surf House</a>\n            <a href="/surfing/" class="btn btn-outline">Coaching</a>',
            '<a href="/ar/surf-house/" class="btn btn-deep">بيت الأمواج</a>\n            <a href="/ar/surf/" class="btn btn-outline">التدريب</a>',
        ),
        ('alt="Surf coaching Ngor Island Senegal"', 'alt="تدريب ركوب الأمواج في جزيرة نغور، السنغال"'),
        (
            "Ngor Island, Dakar, Senegal. WhatsApp: +221 78 925 70 25",
            "جزيرة نغور، داكار، السنغال. واتساب: +221 78 925 70 25",
        ),
    ]
    path = os.path.join(DEMO_DIR, "ar/index.html")
    if not os.path.isfile(path):
        return
    with open(path, encoding="utf-8", errors="replace") as f:
        h = f.read()
    h2 = h
    for old, new in AR_FIXES:
        if old in h2:
            h2 = h2.replace(old, new)
    # Secondary WhatsApp button labels (hero / CTA) still plain text
    h2 = h2.replace("> WhatsApp</a>", "> واتساب</a>")
    if h2 != h:
        with open(path, "w", encoding="utf-8") as f:
            f.write(h2)
        print("  home AR: cleaned leftover English UI strings")
    else:
        print("  home AR: UI cleanup (no changes)")


def patch_ar_whatsapp_word_in_html_all():
    """Replace visible English 'WhatsApp' with Arabic واتساب across /ar/ HTML (island guides, blog CTAs)."""
    ar_root = os.path.join(DEMO_DIR, "ar")
    if not os.path.isdir(ar_root):
        return
    subs = [
        ("تواصل مع <strong>Ngor Surfcamp Teranga على WhatsApp:", "تواصل مع <strong>Ngor Surfcamp Teranga على واتساب:"),
        ("Ngor Surfcamp Teranga على WhatsApp:", "Ngor Surfcamp Teranga على واتساب:"),
        ("عبر <strong>WhatsApp:", "عبر <strong>واتساب:"),
        ("راسل المخيم عبر <strong>WhatsApp", "راسل المخيم عبر <strong>واتساب"),
        ("<strong>WhatsApp +221", "<strong>واتساب +221"),
        ("WhatsApp: +221", "واتساب: +221"),
        ("WhatsApp +221", "واتساب +221"),
        ("احفظ رقم WhatsApp", "احفظ رقم واتساب"),
        ('aria-label="WhatsApp"', 'aria-label="واتساب"'),
        ("Message the team directly on WhatsApp", "راسل الفريق مباشرة على واتساب"),
        ("message on WhatsApp:", "على واتساب:"),
        ("Save the camp WhatsApp number", "احفظ رقم واتساب المعسكر"),
        ('<span class="vb-label">Key Takeaways</span>', '<span class="vb-label">أهم النقاط</span>'),
        ('alt="Key Takeaways"', 'alt="أهم النقاط"'),
        ('class="nav-wa-label">WhatsApp</span>', 'class="nav-wa-label">واتساب</span>'),
        ("send a WhatsApp message directly to", "أرسل رسالة واتساب مباشرة إلى"),
        ("</svg></span> WhatsApp</button>", "</svg></span> واتساب</button>"),
        ("</svg></span> WhatsApp</a>", "</svg></span> واتساب</a>"),
        # Hero / CTA: label after WA icon with whitespace before closing tag
        ("</svg></span> WhatsApp", "</svg></span> واتساب"),
        ("<!-- Floating WhatsApp -->", "<!-- واتساب عائم -->"),
        ("/* ── Booking form → WhatsApp ─────────────────────────── */", "/* ── نموذج الحجز → واتساب ─────────────────────────── */"),
    ]
    n_files = 0
    from pathlib import Path as _Path

    for p in _Path(ar_root).rglob("*.html"):
        try:
            h = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        h2 = h
        for old, new in subs:
            h2 = h2.replace(old, new)
        if h2 != h:
            p.write_text(h2, encoding="utf-8")
            n_files += 1
    print(f"  AR WhatsApp / UI wording: touched {n_files} files under ar/")


def patch_surfing_pages_visuals_all():
    """Replace missing PNG feat icons with SVG, fix extra closing div, improve services grid (all surf* index pages)."""
    dup_tail = "\n    </div>\n    </div>\n    \n  </section>\n\n  <!-- Surf levels -->"
    dup_fix = "\n    </div>\n    \n  </section>\n\n  <!-- Surf levels -->"
    fed_old = (
        '<span style="width:20px;height:20px;display:inline-flex">'
        '<img src="/assets/images/icons/icon-federation.webp" alt="" width="20" height="20" '
        'style="display:inline-block;object-fit:contain"></span>'
    )
    fed_new = (
        '<span style="width:20px;height:20px;display:inline-flex;align-items:center;justify-content:center;'
        'color:var(--navy)" aria-hidden="true">'
        f"{FEAT_SVG_INLINE['icon-federation']}</span>"
    )
    n_files = 0
    for rel in SURF_PAGE_INDEX_FILES:
        path = os.path.join(DEMO_DIR, rel)
        if not os.path.isfile(path):
            print(f"  skip surfing visuals: missing {rel}")
            continue
        with open(path, encoding="utf-8", errors="replace") as f:
            h = f.read()
        if "<!-- Services grid -->" not in h:
            continue
        h2 = h
        for png, key in FEAT_ICON_IMG_MAP:
            old = (
                f'<div class="feat-icon"><img src="{png}" alt="" width="24" height="24"></div>'
            )
            inner = FEAT_SVG_INLINE[key]
            new = (
                f'<div class="feat-icon"><span class="feat-ico-svg" aria-hidden="true">{inner}</span></div>'
            )
            h2 = h2.replace(old, new)
        h2 = h2.replace(
            'class="grid-2 reveal"><div class="feat"',
            'class="grid-2 feat-services-grid reveal"><div class="feat"',
            1,
        )
        if dup_tail in h2:
            h2 = h2.replace(dup_tail, dup_fix, 1)
        h2 = h2.replace(fed_old, fed_new)
        if h2 != h:
            with open(path, "w", encoding="utf-8") as f:
                f.write(h2)
            n_files += 1
    print(f"  surfing visuals + layout: updated {n_files} files")


# ════════════════════════════════════════════════════════════════
# BOOKING PAGE BUILDER
# ════════════════════════════════════════════════════════════════
def build_booking(lang):
    pfx  = LANG_PFX[lang]
    slug = SLUG[lang]["booking"]
    T = {
        "h1":     {"en":"Book Your Stay","fr":"Réservez votre séjour","es":"Reserva tu estancia","it":"Prenota il tuo soggiorno","de":"Jetzt buchen","nl":"Boek je verblijf","ar":"احجز إقامتك"},
        "sub":    {"en":"Check availability and we'll take care of the rest!","fr":"Vérifiez les disponibilités et nous nous occupons du reste !","es":"Consulta la disponibilidad y nosotros nos encargamos del resto.","it":"Controlla la disponibilità e pensiamo noi al resto!","de":"Prüfen Sie die Verfügbarkeit und wir kümmern uns um den Rest!","nl":"Controleer de beschikbaarheid en wij regelen de rest!","ar":"تحقق من التوفر وسنهتم بالباقي!"},
        "title":  {"en":"Book Your Surf Stay | Ngor Surfcamp Teranga","fr":"Réservez votre séjour surf | Ngor Surfcamp Teranga","es":"Reserva tu estancia surf | Ngor Surfcamp Teranga","it":"Prenota il tuo soggiorno surf | Ngor Surfcamp Teranga","de":"Buche deinen Aufenthalt | Ngor Surfcamp Teranga","nl":"Boek je surfverblijf | Ngor Surfcamp Teranga","ar":"احجز إقامتك في السيرف | Ngor Surfcamp Teranga"},
        "meta":   {"en":"Book your surf camp stay at Ngor Island, Dakar, Senegal. Check availability online.","fr":"Réservez votre séjour au surf camp de l'île de Ngor, Dakar, Sénégal.","es":"Reserva tu estancia en el surf camp de la isla de Ngor, Dakar, Senegal.","it":"Prenota il tuo soggiorno al surf camp sull'isola di Ngor, Dakar, Senegal.","de":"Buche deinen Aufenthalt im Surf Camp auf Ngor Island, Dakar, Senegal.","nl":"Boek je surfkampverblijf op Ngor Island, Dakar, Senegal.","ar":"احجز إقامتك في مخيم الأمواج في جزيرة نغور، داكار، السنغال."},
        "h2":     {"en":"Check Availability & Book Your Stay","fr":"Vérifiez les disponibilités & Réservez","es":"Consulta disponibilidad y Reserva","it":"Controlla disponibilità e Prenota","de":"Verfügbarkeit prüfen & Buchen","nl":"Controleer beschikbaarheid & Boek","ar":"تحقق من التوفر واحجز إقامتك"},
        "sub2":   {"en":"Tell us your dates and we'll find the perfect room for your surf adventure.","fr":"Donnez-nous vos dates et nous trouverons la chambre parfaite.","es":"Cuéntanos tus fechas y encontraremos la habitación perfecta.","it":"Dicci le tue date e troveremo la camera perfetta.","de":"Teilen Sie uns Ihre Daten mit und wir finden das perfekte Zimmer.","nl":"Geef ons je data en wij vinden de perfecte kamer voor je surfavontuur.","ar":"أخبرنا بتواريخك وسنجد الغرفة المثالية لمغامرتك."},
        "fname":  {"en":"First Name","fr":"Prénom","es":"Nombre","it":"Nome","de":"Vorname","nl":"Voornaam","ar":"الاسم الأول"},
        "lname":  {"en":"Last Name","fr":"Nom","es":"Apellido","it":"Cognome","de":"Nachname","nl":"Achternaam","ar":"اسم العائلة"},
        "email":  {"en":"E-mail","fr":"E-mail","es":"E-mail","it":"E-mail","de":"E-Mail","nl":"E-mail","ar":"البريد الإلكتروني"},
        "spam":   {"en":"No spam, just waves and logistics.","fr":"Pas de spam, juste des vagues.","es":"Sin spam, solo olas.","it":"Niente spam, solo onde.","de":"Kein Spam, nur Wellen.","nl":"Geen spam, alleen golven.","ar":"لا بريد مزعج، فقط أمواج."},
        "phone":  {"en":"WhatsApp / Phone Number","fr":"WhatsApp / Téléphone","es":"WhatsApp / Teléfono","it":"WhatsApp / Telefono","de":"WhatsApp / Telefon","nl":"WhatsApp / Telefoonnummer","ar":"واتساب / رقم الهاتف"},
        "level":  {"en":"What's your current surf level?","fr":"Quel est votre niveau de surf ?","es":"¿Cuál es tu nivel de surf?","it":"Qual è il tuo livello di surf?","de":"Was ist Ihr Surflevel?","nl":"Wat is jouw huidige surfniveau?","ar":"ما هو مستواك الحالي في ركوب الأمواج؟"},
        "choose": {"en":"Choose an option","fr":"Choisissez","es":"Elige una opción","it":"Scegli","de":"Wählen","nl":"Kies een optie","ar":"اختر خياراً"},
        "beg":    {"en":"Beginner — never surfed or just starting","fr":"Débutant — jamais surfé","es":"Principiante","it":"Principiante","de":"Anfänger","nl":"Beginner — nog nooit gesurft of net begonnen","ar":"مبتدئ — لم يمارس ركوب الأمواج قط"},
        "bas":    {"en":"Basic — can stand up, learning turns","fr":"Basique — debout, apprend les virages","es":"Básico","it":"Base","de":"Grundlagen","nl":"Basis — kan opstaan, leert draaien","ar":"أساسي — يستطيع الوقوف، يتعلم الالتفافات"},
        "int":    {"en":"Intermediate — comfortable, working on technique","fr":"Intermédiaire — à l'aise, technique","es":"Intermedio","it":"Intermedio","de":"Fortgeschrittene","nl":"Gemiddeld — werkt aan techniek","ar":"متوسط — يعمل على تطوير التقنية"},
        "adv":    {"en":"Advanced — ripping, pushing limits","fr":"Avancé — repousse ses limites","es":"Avanzado","it":"Avanzato","de":"Profi","nl":"Gevorderd — excelleert, verlegt grenzen","ar":"متقدم — يتخطى الحدود"},
        "guests": {"en":"How many guests?","fr":"Nombre de personnes ?","es":"¿Cuántas personas?","it":"Quante persone?","de":"Wie viele Personen?","nl":"Hoeveel gasten?","ar":"كم عدد الضيوف؟"},
        "arrive": {"en":"When do you arrive?","fr":"Quand arrivez-vous ?","es":"¿Cuándo llegas?","it":"Quando arrivi?","de":"Wann reisen Sie an?","nl":"Wanneer kom je aan?","ar":"متى تصل؟"},
        "leave":  {"en":"When do you leave?","fr":"Quand partez-vous ?","es":"¿Cuándo te vas?","it":"Quando parti?","de":"Wann reisen Sie ab?","nl":"Wanneer vertrek je?","ar":"متى تغادر؟"},
        "flex":   {"en":"I'm flexible — tell me when the swell is best!","fr":"Je suis flexible — dites-moi quand le swell est le meilleur !","es":"Soy flexible — ¡dime cuándo es mejor el swell!","it":"Sono flessibile — dimmi quando il swell è migliore!","de":"Ich bin flexibel — sagen Sie mir wann der Swell am besten ist!","nl":"Ik ben flexibel — vertel me wanneer het swell het beste is!","ar":"أنا مرن — أخبرني متى تكون الأمواج في أفضل حال!"},
        "goal":   {"en":"What is your #1 goal for this trip?","fr":"Quel est votre objectif principal ?","es":"¿Cuál es tu objetivo principal?","it":"Qual è il tuo obiettivo principale?","de":"Was ist Ihr Hauptziel?","nl":"Wat is jouw #1 doel voor deze reis?","ar":"ما هو هدفك الأول من هذه الرحلة؟"},
        "goal_ph":{"en":"e.g., Improving my cutback, exploring Dakar, relaxing by the pool.","fr":"ex. Améliorer mon cutback, explorer Dakar, me détendre.","es":"p.ej., Mejorar mi cutback, explorar Dakar.","it":"es. Migliorare il mio cutback, esplorare Dakar.","de":"z.B. Cutback verbessern, Dakar erkunden.","nl":"bijv. Cutback verbeteren, Dakar verkennen.","ar":"مثلاً: تحسين الكات باك، استكشاف داكار."},
        "cta":    {"en":"Check Availability & Prices","fr":"Vérifier disponibilités & Tarifs","es":"Consultar disponibilidad y Precios","it":"Controlla disponibilità e Prezzi","de":"Verfügbarkeit & Preise prüfen","nl":"Controleer beschikbaarheid & Prijzen","ar":"تحقق من التوفر والأسعار"},
        "reply":  {"en":"No spam. We reply within 24 hours.","fr":"Pas de spam. Réponse sous 24h.","es":"Sin spam. Respondemos en 24h.","it":"Nessuno spam. Rispondiamo entro 24h.","de":"Kein Spam. Antwort innerhalb von 24h.","nl":"Geen spam. We antwoorden binnen 24 uur.","ar":"لا بريد مزعج. نرد خلال 24 ساعة."},
        "or":     {"en":"Or contact us directly:","fr":"Ou contactez-nous directement :","es":"O contáctanos directamente:","it":"O contattaci direttamente:","de":"Oder kontaktieren Sie uns direkt:","nl":"Of neem direct contact op:","ar":"أو اتصل بنا مباشرة:"},
        "steps_h":{"en":"Booking made easy","fr":"Réservation simplifiée","es":"Reserva fácil","it":"Prenotazione facile","de":"Einfache Buchung","nl":"Eenvoudig boeken","ar":"حجز سهل"},
        "step1":  {"en":"Choose your dates","fr":"Choisissez vos dates","es":"Elige tus fechas","it":"Scegli le tue date","de":"Daten wählen","nl":"Kies je data","ar":"اختر تواريخك"},
        "step2":  {"en":"Fill the form or WhatsApp us","fr":"Remplissez le formulaire ou écrivez-nous","es":"Rellena el formulario o escríbenos","it":"Compila il modulo o scrivici","de":"Formular ausfüllen oder schreiben","nl":"Vul het formulier in of stuur een WhatsApp","ar":"املأ النموذج أو راسلنا عبر واتساب"},
        "step3":  {"en":"We confirm your room & package","fr":"Nous confirmons votre chambre","es":"Confirmamos tu habitación","it":"Confermiamo la tua stanza","de":"Wir bestätigen Zimmer & Paket","nl":"Wij bevestigen je kamer & pakket","ar":"سنؤكد غرفتك وباقتك"},
        "incl_h": {"en":"Everything included","fr":"Tout est inclus","es":"Todo incluido","it":"Tutto incluso","de":"Alles inklusive","nl":"Alles inbegrepen","ar":"كل شيء مشمول"},
        "i1":{"en":"Accommodation (private or shared room)","fr":"Hébergement (chambre privée ou partagée)","es":"Alojamiento (habitación privada o compartida)","it":"Alloggio (camera privata o condivisa)","de":"Unterkunft (Einzel- oder Mehrbettzimmer)","nl":"Accommodatie (privé of gedeelde kamer)","ar":"الإقامة (غرفة خاصة أو مشتركة)"},
        "i2":{"en":"Breakfast & dinner (authentic Senegalese cuisine)","fr":"Petit-déjeuner & dîner (cuisine sénégalaise)","es":"Desayuno y cena (cocina senegalesa)","it":"Colazione e cena (cucina senegalese)","de":"Frühstück & Abendessen (senegalesische Küche)","nl":"Ontbijt & avondeten (authentieke Senegalese keuken)","ar":"الإفطار والعشاء (مطبخ سنغالي أصيل)"},
        "i3":{"en":"Daily surf guiding to the best spots","fr":"Guide surf quotidien vers les meilleurs spots","es":"Guía surf diario a los mejores spots","it":"Guida surf giornaliera ai migliori spot","de":"Tägliche Surf-Führung zu den besten Spots","nl":"Dagelijkse surfbegeleiding naar de beste spots","ar":"إرشاد يومي إلى أفضل مواقع الأمواج"},
        "i4":{"en":"Boat transfers to Ngor Right & Left","fr":"Transferts en pirogue vers Ngor Right & Left","es":"Traslados en bote a Ngor Right & Left","it":"Trasferimenti in barca a Ngor Right & Left","de":"Bootüberfahrten zu Ngor Right & Left","nl":"Boottransfers naar Ngor Right & Left","ar":"تنقلات بالقارب إلى Ngor Right و Left"},
        "i5":{"en":"Free surf theory classes","fr":"Cours de théorie surf gratuits","es":"Clases de teoría surf gratuitas","it":"Lezioni di teoria surf gratuite","de":"Kostenlose Surf-Theoriestunden","nl":"Gratis surftheorielessen","ar":"دروس نظرية لركوب الأمواج مجانية"},
        "i6":{"en":"Pool access & shared spaces","fr":"Accès piscine & espaces communs","es":"Acceso piscina y áreas comunes","it":"Accesso piscina e aree comuni","de":"Poolzugang & Gemeinschaftsbereiche","nl":"Toegang tot zwembad & gemeenschappelijke ruimtes","ar":"الوصول إلى حمام السباحة والمساحات المشتركة"},
        "i7":{"en":"Free Wi-Fi & daily room cleaning","fr":"Wi-Fi gratuit & ménage quotidien","es":"Wi-Fi gratis y limpieza diaria","it":"Wi-Fi gratuito e pulizia giornaliera","de":"Kostenloses WLAN & tägliche Reinigung","nl":"Gratis Wi-Fi & dagelijkse kamerreiniging","ar":"واي فاي مجاني وتنظيف يومي للغرفة"},
        "trust":  {"en":"Licensed by the Senegalese Federation of Surfing","fr":"Agréé par la Fédération Sénégalaise de Surf","es":"Licenciado por la Federación Senegalesa de Surf","it":"Autorizzato dalla Federazione Senegalese di Surf","de":"Lizenziert vom senegalesischen Surfverband","nl":"Erkend door de Senegalese Surfbond","ar":"مرخص من قبل الاتحاد السنغالي لركوب الأمواج"},
        "err_fn": {"en":"Please enter your first name.","fr":"Veuillez entrer votre prénom.","es":"Por favor, introduce tu nombre.","it":"Per favore, inserisci il tuo nome.","de":"Bitte Vornamen eingeben.","nl":"Voer je voornaam in.","ar":"يرجى إدخال اسمك الأول."},
        "err_em": {"en":"Please enter a valid email.","fr":"Veuillez entrer un email valide.","es":"Por favor, introduce un email válido.","it":"Per favore, inserisci un'email valida.","de":"Bitte gültige E-Mail eingeben.","nl":"Voer een geldig e-mailadres in.","ar":"يرجى إدخال بريد إلكتروني صحيح."},
        "err_dt": {"en":"Departure must be after arrival.","fr":"Le départ doit être après l'arrivée.","es":"La salida debe ser después de la llegada.","it":"La partenza deve essere dopo l'arrivo.","de":"Abreise muss nach Anreise sein.","nl":"Vertrekdatum moet na aankomstdatum liggen.","ar":"يجب أن يكون تاريخ المغادرة بعد تاريخ الوصول."},
        "err_lvl": {"en":"Please choose your surf level.","fr":"Veuillez choisir votre niveau de surf.","es":"Elige tu nivel de surf.","it":"Scegli il tuo livello di surf.","de":"Bitte wähle dein Surf-Level.","nl":"Kies je surfniveau.","ar":"يرجى اختيار مستواك في ركوب الأمواج."},
        "err_net": {"en":"We couldn't send your request. Check your connection or message us on WhatsApp.","fr":"Envoi impossible pour le moment. Vérifiez votre connexion ou écrivez-nous sur WhatsApp.","es":"No pudimos enviar tu solicitud. Revisa la conexión o escríbenos por WhatsApp.","it":"Impossibile inviare la richiesta. Controlla la connessione o scrivici su WhatsApp.","de":"Senden fehlgeschlagen. Bitte Verbindung prüfen oder per WhatsApp melden.","nl":"Verzenden mislukt. Controleer je verbinding of stuur een WhatsApp.","ar":"تعذّر إرسال الطلب. تحقق من الاتصال أو راسلنا على واتساب."},
        "succ_h": {"en":"You're all set!","fr":"C'est bien enregistré !","es":"¡Listo!","it":"Richiesta ricevuta!","de":"Alles klar!","nl":"Ontvangen!","ar":"تم بنجاح!"},
        "succ_p": {"en":"Thank you — we've received your request. Our team will get back to you within 24 hours.","fr":"Merci — nous avons bien reçu votre demande. Notre équipe vous répond sous 24 h.","es":"Gracias — hemos recibido tu solicitud. Te responderemos en 24 horas.","it":"Grazie — abbiamo ricevuto la tua richiesta. Ti risponderemo entro 24 ore.","de":"Danke — wir haben deine Anfrage erhalten. Wir melden uns innerhalb von 24 Stunden.","nl":"Bedankt — we hebben je aanvraag ontvangen. We nemen binnen 24 uur contact op.","ar":"شكراً — استلمنا طلبك. سيتواصل فريقنا معك خلال 24 ساعة."},
        "succ_wa": {"en":"We've also opened WhatsApp with your details, so you can reach us instantly if you prefer.","fr":"WhatsApp s'ouvre aussi avec vos infos — vous pouvez nous écrire tout de suite si vous préférez.","es":"También abrimos WhatsApp con tus datos por si prefieres escribirnos al instante.","it":"Abbiamo anche aperto WhatsApp con i tuoi dati, se preferisci scriverci subito.","de":"WhatsApp öffnet sich ebenfalls mit deinen Angaben — du erreichst uns sofort, wenn du möchtest.","nl":"WhatsApp opent ook met je gegevens — zo kun je ons meteen bereiken als je wilt.","ar":"فتحنا واتساب أيضاً مع بياناتك — يمكنك التواصل فوراً إن أحببت."},
        "succ_btn": {"en":"Got it","fr":"Compris","es":"Entendido","it":"Ok","de":"Alles klar","nl":"Begrepen","ar":"حسناً"},
        "copied": {"en":"Copied!","fr":"Copié !","es":"Copiado!","it":"Copiato!","de":"Kopiert!","nl":"Gekopieerd!","ar":"تم النسخ!"},
        "eyebrow": {"en":"Book","fr":"Réserver","es":"Reservar","it":"Prenota","de":"Buchen","nl":"Boeken","ar":"احجز"},
        "isa_sub": {
            "en": "ISA certified coaches, safety first.",
            "fr": "Coachs certifiés ISA, sécurité avant tout.",
            "es": "Monitores certificados ISA, seguridad primero.",
            "it": "Coach certificati ISA, sicurezza al primo posto.",
            "de": "ISA-zertifizierte Coaches, Sicherheit zuerst.",
            "nl": "ISA-gecertificeerde coaches, veiligheid voorop.",
            "ar": "مدربون معتمدون من ISA، السلامة أولاً.",
        },
    }
    T = _site_page_mod.merge_booking_copy(_BASE_DIR, lang, T)

    def g(key): return T[key].get(lang, T[key]["en"])

    # Country codes dropdown — pre-select based on lang
    LANG_DEFAULT_CC = {"en":"+44","fr":"+33","es":"+34","it":"+39","de":"+49","nl":"+31","ar":"+212"}
    default_cc = LANG_DEFAULT_CC.get(lang, "+221")
    _cc_other = {
        "en": "🌍 Other", "fr": "🌍 Autre", "es": "🌍 Otro", "it": "🌍 Altro",
        "de": "🌍 Andere", "nl": "🌍 Overig", "ar": "🌍 أخرى",
    }
    CC_OPTIONS = [
        ("+221","🇸🇳 +221 Sénégal"),("+33","🇫🇷 +33 France"),("+34","🇪🇸 +34 España"),
        ("+39","🇮🇹 +39 Italia"),("+49","🇩🇪 +49 Deutschland"),("+44","🇬🇧 +44 UK"),
        ("+1","🇺🇸 +1 USA"),("+32","🇧🇪 +32 Belgique"),("+41","🇨🇭 +41 Suisse"),
        ("+31","🇳🇱 +31 Nederland"),("+351","🇵🇹 +351 Portugal"),
        ("+212","🇲🇦 +212 Maroc"),("other", _cc_other.get(lang, _cc_other["en"])),
    ]
    cc_opts = "\n".join([
        f'<option value="{v}"{" selected" if v == default_cc else ""}>{l}</option>'
        for v, l in CC_OPTIONS
    ])

    # Inclusion items
    incl_items = "".join([
        f'<div style="display:flex;align-items:flex-start;gap:10px;margin-bottom:12px">'
        f'<span style="width:18px;height:18px;display:inline-flex;color:#22c55e;flex-shrink:0;margin-top:1px">'
        f'<svg viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg></span>'
        f'<span style="font-size:14px;color:#374151">{T[k].get(lang, T[k]["en"])}</span></div>'
        for k in ["i1","i2","i3","i4","i5","i6","i7"]
    ])

    # Steps
    steps_html = "".join([
        f'<div style="display:flex;gap:14px;align-items:flex-start;margin-bottom:16px">'
        f'<div style="width:32px;height:32px;border-radius:50%;background:var(--fire);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:15px;flex-shrink:0">{n}</div>'
        f'<div style="font-size:14.5px;color:#374151;padding-top:4px">{T[k].get(lang, T[k]["en"])}</div></div>'
        for n,k in [(1,"step1"),(2,"step2"),(3,"step3")]
    ])

    # Trust badge labels
    TRUST_QUICK = {
        "en": ["No spam", "Reply in 24h", "Free cancellation"],
        "fr": ["Pas de spam", "Réponse sous 24h", "Annulation gratuite"],
        "es": ["Sin spam", "Respuesta en 24h", "Cancelación gratuita"],
        "it": ["Nessuno spam", "Risposta in 24h", "Cancellazione gratuita"],
        "de": ["Kein Spam", "Antwort in 24h", "Kostenlose Stornierung"],
        "nl": ["Geen spam", "Antwoord binnen 24u", "Gratis annulering"],
        "ar": ["لا بريد مزعج", "رد خلال 24 ساعة", "إلغاء مجاني"],
    }
    trust_badges = "".join([
        f'<span style="display:inline-flex;align-items:center;gap:6px;font-size:13px;color:rgba(255,255,255,0.85);background:rgba(255,255,255,0.12);border-radius:50px;padding:5px 14px">'
        f'<svg viewBox="0 0 20 20" fill="currentColor" width="14" height="14" style="color:#4ade80"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>'
        f'{badge}</span>'
        for badge in TRUST_QUICK.get(lang, TRUST_QUICK["en"])
    ])

    html = page_head(g("title"), g("meta"), lang, "booking", IMGS["book_bg"])
    html += build_nav("booking", lang)
    html += f"""
<main>
  <header class="main-hero" style="background-image:url('/assets/images/gallery/CAML6902_d756823d.webp')" role="banner">
    <div class="main-hero-inner">
      <div class="main-hero-eyebrow">
        <span class="main-hero-dot"></span>
        <span>Ngor Surfcamp Teranga</span>
      </div>
      <h1 class="main-hero-h1">{g("h1")}</h1>
      <p class="main-hero-tagline">{g("sub")}</p>
      <div class="main-hero-actions" style="flex-direction:column;gap:24px;align-items:center">
        <div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap">{trust_badges}</div>
        <a href="#booking-section" class="btn btn-outline-white btn-lg">&#8964;</a>
      </div>
    </div>
  </header>

  <link rel="stylesheet" href="/assets/css/availability-calendar.css?v={ASSET_VERSION}">
  <script src="/assets/js/availability-calendar.js?v={ASSET_VERSION}"></script>

  <section class="section" id="booking-section" style="padding-top:40px;padding-bottom:48px">
    <div class="container">
      <div class="split" style="gap:48px;align-items:flex-start">

        <div>
          <h2 class="s-title" style="margin-bottom:8px;font-size:clamp(22px,3vw,28px)">{g("h2")}</h2>
          <p style="color:#6b7280;font-size:15px;margin-bottom:28px">{g("sub2")}</p>

          <form id="booking-form" novalidate>
            <div id="booking-form-alert" class="booking-form-alert" style="display:none" role="alert" aria-live="assertive"></div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label" for="f-fname">{g("fname")} <span style="color:var(--fire)">*</span></label>
                <input type="text" id="f-fname" class="form-input f-name" placeholder="Kelly" autocomplete="given-name" required aria-describedby="err-fname">
                <div id="err-fname" class="booking-field-error" style="display:none" role="status">{g("err_fn")}</div>
              </div>
              <div class="form-group">
                <label class="form-label" for="f-lname">{g("lname")}</label>
                <input type="text" id="f-lname" class="form-input" placeholder="Slater" autocomplete="family-name">
              </div>
            </div>

            <div class="form-group">
              <label class="form-label" for="f-email">{g("email")} <span style="color:var(--fire)">*</span></label>
              <input type="email" id="f-email" class="form-input f-email" placeholder="yourname@email.com" autocomplete="email" required aria-describedby="err-email">
              <div id="err-email" class="booking-field-error" style="display:none" role="status">{g("err_em")}</div>
              <p style="font-size:12.5px;color:#9ca3af;margin-top:5px">{g("spam")}</p>
            </div>

            <div class="form-group">
              <label class="form-label">{g("phone")}</label>
              <div style="display:flex;gap:8px">
                <select class="form-select" id="f-cc" style="width:auto;min-width:130px;flex-shrink:0">{cc_opts}</select>
                <input type="tel" class="form-input" id="f-phone" placeholder="+221 78 925 70 25" autocomplete="tel" style="flex:1">
              </div>
            </div>

            <div class="form-group">
              <label class="form-label" for="f-level">{g("level")} <span style="color:var(--fire)">*</span></label>
              <select id="f-level" class="form-select f-level" required aria-describedby="err-level">
                <option value="">{g("choose")}</option>
                <option value="beginner">{g("beg")}</option>
                <option value="basic">{g("bas")}</option>
                <option value="intermediate">{g("int")}</option>
                <option value="advanced">{g("adv")}</option>
              </select>
              <div id="err-level" class="booking-field-error" style="display:none" role="status">{g("err_lvl")}</div>
            </div>

            <div class="form-group">
              <label class="form-label">{g("guests")}</label>
              <select class="form-select" id="f-guests">
                <option value="">—</option>
                {"".join([f'<option value="{n}">{n}</option>' for n in range(1,13)])}
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">{g("arrive")} / {g("leave")}</label>
              <div id="avail-calendar" class="ac-wrap" style="max-width:100%"></div>
              <input type="hidden" id="f-arrive" class="f-arrive">
              <input type="hidden" id="f-leave" class="f-leave">
              <input type="hidden" id="f-room" name="room_preference" value="dormitory">
              <div id="err-date" class="booking-field-error" style="display:none" role="status">{g("err_dt")}</div>
            </div>

            <div id="price-summary" class="bp-sum-box" style="display:none" hidden></div>

            <div class="form-group">
              <label class="form-check">
                <input type="checkbox" id="f-flex" style="accent-color:var(--fire);width:17px;height:17px">
                <span>{g("flex")}</span>
              </label>
            </div>

            <div class="form-group">
              <label class="form-label" for="f-goal">{g("goal")}</label>
              <textarea id="f-goal" class="form-textarea" rows="3" placeholder="{g("goal_ph")}"></textarea>
            </div>

            <button type="submit" class="btn btn-fire booking-submit-btn" style="width:100%;font-size:15px;padding:15px;justify-content:center">
              <span class="booking-submit-ico" aria-hidden="true" style="display:inline-flex">{WA_ICO}</span>
              <span class="booking-submit-label">{g("cta")}</span>
            </button>
            <p style="text-align:center;margin-top:12px;font-size:13px;color:#9ca3af">{g("reply")}</p>
          </form>

          <div id="booking-success-overlay" class="booking-success-overlay" hidden role="dialog" aria-modal="true" aria-labelledby="booking-success-title">
            <div class="booking-success-card">
              <div class="booking-success-check" aria-hidden="true">✓</div>
              <h3 id="booking-success-title" class="booking-success-title"></h3>
              <p class="booking-success-text"></p>
              <p class="booking-success-wa-note"></p>
              <button type="button" class="btn btn-fire booking-success-close" style="width:100%;margin-top:8px;justify-content:center"></button>
            </div>
          </div>

          <div style="margin-top:28px;padding:20px 24px;border-radius:14px;border:1px solid #e5e7eb;background:#fafafa">
            <p style="font-weight:600;font-size:14px;margin-bottom:14px">{g("or")}</p>
            <div style="display:flex;flex-wrap:wrap;gap:12px">
              <a href="https://wa.me/221789257025" target="_blank" rel="noopener" class="btn btn-wa btn-sm">
                <span style="display:inline-flex">{WA_ICO}</span> +221 78 925 70 25
              </a>
              <a href="mailto:info@surfcampsenegal.com" class="btn btn-deep btn-sm">
                info@surfcampsenegal.com
              </a>
            </div>
          </div>
        </div>

        <div style="position:sticky;top:80px;align-self:flex-start">
          <div class="form-card reveal" style="margin-bottom:20px">
            <h3 style="font-size:17px;margin-bottom:18px;font-weight:800">{g("steps_h")}</h3>
            {steps_html}
          </div>
          <div class="form-card reveal" style="margin-bottom:20px">
            <h3 style="font-size:17px;margin-bottom:18px;font-weight:800">{g("incl_h")}</h3>
            {incl_items}
          </div>
          <div style="display:inline-flex;flex-direction:row;align-items:center;background:#0a2540;border:1.5px solid #c9a227;border-radius:50px;padding:6px 18px 6px 6px;gap:12px;box-shadow:0 4px 14px rgba(0,0,0,0.18);max-width:100%;box-sizing:border-box">
            <div style="width:44px;height:44px;background:#fff;border-radius:50%;display:flex;align-items:center;justify-content:center;border:1.5px solid #c9a227;flex-shrink:0">
              <img src="{FSS_LOGO}" alt="Fédération Sénégalaise de Surf" width="32" height="32" loading="lazy" style="object-fit:contain;width:32px;height:32px">
            </div>
            <div style="display:flex;flex-direction:column;text-align:left">
              <strong style="color:#fff;font-size:13px;font-weight:700;line-height:1.25;margin:0">Licensed &amp; Certified</strong>
              <span style="color:#c9a227;font-size:11px;font-weight:500;line-height:1.3;margin-top:2px">Fédération Sénégalaise de Surf</span>
            </div>
          </div>
          {booking_social_proof_block(lang)}
        </div>

      </div>
    </div>
  </section>

  {booking_reviews_section(lang)}
</main>

<script>
(function(){{
  var J = {json.dumps(
        {
            "waIntro": {
                "en": "Hello! I would like to book a stay at Ngor Surfcamp Teranga.",
                "fr": "Bonjour ! Je souhaite réserver un séjour au Ngor Surfcamp Teranga.",
                "es": "Hola! Me gustaría reservar una estancia en Ngor Surfcamp Teranga.",
                "it": "Ciao! Vorrei prenotare un soggiorno al Ngor Surfcamp Teranga.",
                "de": "Hallo! Ich möchte einen Aufenthalt im Ngor Surfcamp Teranga buchen.",
                "nl": "Hallo! Ik wil graag een verblijf boeken bij Ngor Surfcamp Teranga.",
                "ar": "مرحباً! أود حجز إقامة في Ngor Surfcamp Teranga.",
            }[lang],
            "nameLbl": {"en": "Name", "fr": "Nom", "es": "Nombre", "it": "Nome", "de": "Name", "nl": "Naam", "ar": "الاسم"}.get(lang, "Name"),
            "emailLbl": {"en": "Email", "fr": "E-mail", "es": "Email", "it": "Email", "de": "E-Mail", "nl": "E-mail", "ar": "البريد"}.get(lang, "Email"),
            "phoneLbl": {"en": "Phone", "fr": "Téléphone", "es": "Teléfono", "it": "Telefono", "de": "Telefon", "nl": "Telefoon", "ar": "الهاتف"}.get(lang, "Phone"),
            "levelLbl": {"en": "Level", "fr": "Niveau", "es": "Nivel", "it": "Livello", "de": "Level", "nl": "Niveau", "ar": "المستوى"}.get(lang, "Level"),
            "guestsLbl": {"en": "Guests", "fr": "Personnes", "es": "Personas", "it": "Ospiti", "de": "Gäste", "nl": "Gasten", "ar": "الضيوف"}.get(lang, "Guests"),
            "arrLbl": {"en": "Arrival", "fr": "Arrivée", "es": "Llegada", "it": "Arrivo", "de": "Anreise", "nl": "Aankomst", "ar": "الوصول"}.get(lang, "Arrival"),
            "depLbl": {"en": "Departure", "fr": "Départ", "es": "Salida", "it": "Partenza", "de": "Abreise", "nl": "Vertrek", "ar": "المغادرة"}.get(lang, "Departure"),
            "roomLbl": {"en": "Room", "fr": "Chambre", "es": "Habitación", "it": "Camera", "de": "Zimmer", "nl": "Kamer", "ar": "الغرفة"}.get(lang, "Room"),
            "goalLbl": {"en": "Notes", "fr": "Objectif", "es": "Objetivo", "it": "Obiettivo", "de": "Ziel", "nl": "Doel", "ar": "ملاحظات"}.get(lang, "Notes"),
            "sending": {"en": "Sending…", "fr": "Envoi…", "es": "Enviando…", "it": "Invio…", "de": "Wird gesendet…", "nl": "Verzenden…", "ar": "جاري الإرسال…"}.get(lang, "Sending…"),
            "cta": g("cta"),
            "errNet": g("err_net"),
            "succH": g("succ_h"),
            "succP": g("succ_p"),
            "succWa": g("succ_wa"),
            "succBtn": g("succ_btn"),
        },
        ensure_ascii=False,
    )};
  var form = document.getElementById('booking-form');
  var ccSelect = document.getElementById('f-cc');
  var fArrive = document.getElementById('f-arrive');
  var fLeave = document.getElementById('f-leave');
  var topAlert = document.getElementById('booking-form-alert');
  var overlay = document.getElementById('booking-success-overlay');
  var priceSummary = document.getElementById('price-summary');

  /* ── Phone country code preselect (lang + browser locale) ─── */
  (function initPhoneCountryCode() {{
    if (!ccSelect) return;
    var byLang = {{ en:'+44', fr:'+33', es:'+34', it:'+39', de:'+49', nl:'+31', ar:'+212' }};
    var byRegion = {{
      SN:'+221', FR:'+33', ES:'+34', IT:'+39', DE:'+49', NL:'+31', MA:'+212',
      GB:'+44', UK:'+44', IE:'+353', US:'+1', CA:'+1', BE:'+32', CH:'+41', PT:'+351'
    }};
    function hasOption(v) {{
      if (!v) return false;
      for (var i = 0; i < ccSelect.options.length; i++) {{
        if (ccSelect.options[i].value === v) return true;
      }}
      return false;
    }}
    function parseRegion(loc) {{
      if (!loc) return '';
      var m = String(loc).toUpperCase().match(/[-_]([A-Z]{{2}})/);
      return m ? m[1] : '';
    }}
    function detectFromNavigator() {{
      var list = [];
      try {{
        if (navigator.languages && navigator.languages.length) list = navigator.languages.slice();
        else if (navigator.language) list = [navigator.language];
      }} catch(e) {{}}
      for (var i = 0; i < list.length; i++) {{
        var reg = parseRegion(list[i]);
        if (reg && byRegion[reg] && hasOption(byRegion[reg])) return byRegion[reg];
      }}
      return '';
    }}
    var docLang = ((document.documentElement.lang || 'en').split('-')[0] || 'en').toLowerCase();
    var fallback = byLang[docLang] || '+221';
    // For language-specific pages (fr, it, es, de, nl, ar) the page language
    // unambiguously identifies the user's country → use it directly.
    // For English (neutral language), fall back to browser region detection.
    var preferred = (docLang !== 'en') ? fallback : (detectFromNavigator() || fallback);
    if (hasOption(preferred)) ccSelect.value = preferred;
  }})();

  /* ── Price summary: fetch and display when dates change ─── */
  var _priceL = {{
    nights: {json.dumps({"en":"nights","fr":"nuits","es":"noches","it":"notti","de":"Nächte","nl":"nachten","ar":"ليالي"}.get(lang,"nights"), ensure_ascii=False)},
    from: {json.dumps({"en":"From","fr":"Dès","es":"Desde","it":"Da","de":"Ab","nl":"Vanaf","ar":"من"}.get(lang,"From"), ensure_ascii=False)},
    perNight: {json.dumps({"en":"/night","fr":"/nuit","es":"/noche","it":"/notte","de":"/Nacht","nl":"/nacht","ar":"/ليلة"}.get(lang,"/night"), ensure_ascii=False)},
    total: {json.dumps({"en":"Estimated total","fr":"Total estimé","es":"Total estimado","it":"Totale stimato","de":"Geschätzt","nl":"Geschat totaal","ar":"المجموع التقديري"}.get(lang,"Estimated total"), ensure_ascii=False)},
    avail: {json.dumps({"en":"places available","fr":"places dispo","es":"plazas disponibles","it":"posti disponibili","de":"Plätze frei","nl":"plaatsen beschikbaar","ar":"أماكن متاحة"}.get(lang,"places available"), ensure_ascii=False)},
    full: {json.dumps({"en":"Fully booked on some dates","fr":"Complet sur certaines dates","es":"Completo en algunas fechas","it":"Completo in alcune date","de":"An manchen Tagen ausgebucht","nl":"Volgeboekt op sommige dagen","ar":"محجوز بالكامل في بعض التواريخ"}.get(lang,"Fully booked"), ensure_ascii=False)},
    dorm: {json.dumps({"en":"Dormitory","fr":"Dortoir","es":"Dormitorio","it":"Dormitorio","de":"Schlafsaal","nl":"Slaapzaal","ar":"مهجع"}.get(lang,"Dormitory"), ensure_ascii=False)},
    single: {json.dumps({"en":"Single Room","fr":"Chambre Single","es":"Single","it":"Camera Singola","de":"Einzelzimmer","nl":"Eenpersoonskamer","ar":"غرفة فردية"}.get(lang,"Single"), ensure_ascii=False)},
    double: {json.dumps({"en":"Double Room","fr":"Chambre Double","es":"Doble","it":"Camera Doppia","de":"Doppelzimmer","nl":"Tweepersoonskamer","ar":"غرفة مزدوجة"}.get(lang,"Double"), ensure_ascii=False)},
    selBadge: {json.dumps({"en":"Selected","fr":"Sélectionné","es":"Seleccionado","it":"Selezionato","de":"Ausgewählt","nl":"Gekozen","ar":"محدد"}.get(lang,"Selected"), ensure_ascii=False)}
  }};
  var _priceCache = {{}};
  function rerenderPriceSummaryFromCache() {{
    if (!fArrive || !fLeave || !fArrive.value || !fLeave.value || !priceSummary) return;
    var ci = new Date(fArrive.value), co = new Date(fLeave.value);
    if (co <= ci) return;
    var nights = Math.round((co - ci) / 86400000);
    var key = fArrive.value + '_' + fLeave.value;
    if (_priceCache[key]) renderPriceSummary(_priceCache[key], nights);
  }}
  if (priceSummary && !priceSummary.dataset.bpDeleg) {{
    priceSummary.dataset.bpDeleg = '1';
    function bpPickCard(card) {{
      var rt = card.getAttribute('data-room');
      if (!rt) return;
      var fr = document.getElementById('f-room');
      if (fr) fr.value = rt;
      if (typeof window.__ngorAcSetRoomType === 'function') window.__ngorAcSetRoomType(rt);
      rerenderPriceSummaryFromCache();
    }}
    priceSummary.addEventListener('click', function(ev) {{
      var card = ev.target.closest('.bp-sum-card--ok');
      if (!card || !priceSummary.contains(card)) return;
      bpPickCard(card);
    }});
    priceSummary.addEventListener('keydown', function(ev) {{
      if (ev.key !== 'Enter' && ev.key !== ' ') return;
      var card = ev.target.closest('.bp-sum-card--ok');
      if (!card || !priceSummary.contains(card)) return;
      ev.preventDefault();
      bpPickCard(card);
    }});
  }}
  function updatePriceSummary() {{
    if (!fArrive.value || !fLeave.value || !priceSummary) return;
    var ci = new Date(fArrive.value), co = new Date(fLeave.value);
    if (co <= ci) {{ priceSummary.style.display='none'; priceSummary.setAttribute('hidden',''); return; }}
    var nights = Math.round((co - ci) / 86400000);
    var key = fArrive.value + '_' + fLeave.value;
    if (_priceCache[key]) {{ renderPriceSummary(_priceCache[key], nights); return; }}
    fetch('/api/availability?from=' + fArrive.value + '&to=' + fLeave.value)
      .then(function(r){{ return r.json(); }})
      .then(function(d){{ _priceCache[key] = d.days || {{}}; renderPriceSummary(_priceCache[key], nights); }})
      .catch(function(){{ priceSummary.style.display='none'; priceSummary.setAttribute('hidden',''); }});
  }}
  function renderPriceSummary(days, nights) {{
    var fRoomEl = document.getElementById('f-room');
    var sel = (fRoomEl && fRoomEl.value) ? fRoomEl.value : 'dormitory';
    var rooms = ['dormitory','single','double'];
    var labels = [_priceL.dorm, _priceL.single, _priceL.double];
    var html = '<div class="bp-sum-title">' + nights + ' ' + _priceL.nights + '</div>';
    html += '<div class="bp-sum-grid">';
    for (var i = 0; i < rooms.length; i++) {{
      var rt = rooms[i], total = 0, minAvail = 999, allOk = true;
      var d = new Date(fArrive.value);
      for (var n = 0; n < nights; n++) {{
        var ds = d.toISOString().slice(0,10);
        var info = days[ds] && days[ds][rt];
        if (info && info.available > 0) {{ total += info.price; if (info.available < minAvail) minAvail = info.available; }}
        else allOk = false;
        d.setDate(d.getDate() + 1);
      }}
      var avgPrice = nights > 0 ? Math.round(total / nights) : 0;
      var isSel = (sel === rt);
      var cls = 'bp-sum-card' + (allOk ? ' bp-sum-card--ok' : ' bp-sum-card--disabled');
      if (isSel) cls += ' bp-sum-card--selected';
      html += '<div class="' + cls + '" data-room="' + rt + '" tabindex="' + (allOk ? '0' : '-1') + '" role="button" aria-pressed="' + (isSel ? 'true' : 'false') + '">';
      html += '<div class="bp-sum-card-head"><span class="bp-sum-card-label">' + labels[i] + '</span>';
      if (isSel && allOk) html += '<span class="bp-sum-badge">' + _priceL.selBadge + '</span>';
      html += '</div>';
      if (allOk) {{
        html += '<div class="bp-sum-total">' + total + ' €</div>';
        html += '<div class="bp-sum-avg">' + avgPrice + '€' + _priceL.perNight + '</div>';
        html += '<div class="bp-sum-avail">' + minAvail + ' ' + _priceL.avail + '</div>';
      }} else {{
        html += '<div class="bp-sum-unavail">' + _priceL.full + '</div>';
      }}
      html += '</div>';
    }}
    html += '</div>';
    priceSummary.innerHTML = html;
    priceSummary.style.display = 'block';
    priceSummary.removeAttribute('hidden');
  }}
  if (fArrive) fArrive.addEventListener('change', updatePriceSummary);
  if (fLeave) fLeave.addEventListener('change', updatePriceSummary);

  /* ── Init calendar inline in the form ─── */
  (function _initCal(){{
    if(typeof initAvailabilityCalendar==='undefined'){{setTimeout(_initCal,100);return;}}
    initAvailabilityCalendar('avail-calendar',{{
      room:'dormitory',
      onDatesSelected:function(ci,co,room){{
        if(fArrive){{ fArrive.value=ci; fArrive.dispatchEvent(new Event('change',{{bubbles:true}})); }}
        if(fLeave){{ fLeave.value=co; fLeave.dispatchEvent(new Event('change',{{bubbles:true}})); }}
        var fr = document.getElementById('f-room');
        if (fr && room) fr.value = room;
        updatePriceSummary();
      }},
      onRoomChange:function(room){{
        var fr = document.getElementById('f-room');
        if (fr && room) fr.value = room;
        rerenderPriceSummaryFromCache();
      }}
    }});
  }})();

  function clearFieldErrors() {{
    ['f-fname','f-email','f-level','f-arrive','f-leave'].forEach(function(id) {{
      var el = document.getElementById(id);
      if (el) {{ el.classList.remove('form-invalid'); el.removeAttribute('aria-invalid'); }}
    }});
    ['err-fname','err-email','err-date','err-level'].forEach(function(id) {{
      var e = document.getElementById(id);
      if (e) e.style.display = 'none';
    }});
    if (topAlert) {{ topAlert.style.display = 'none'; topAlert.textContent = ''; }}
  }}

  function showInvalid(id, errId) {{
    var el = document.getElementById(id);
    var err = document.getElementById(errId);
    if (el) {{
      el.classList.add('form-invalid');
      el.setAttribute('aria-invalid', 'true');
      var grp = el.closest('.form-group');
      if (grp) {{
        grp.classList.remove('form-group--shake');
        void grp.offsetWidth;
        grp.classList.add('form-group--shake');
      }}
    }}
    if (err) err.style.display = 'block';
  }}

  function scrollToField(id) {{
    var el = document.getElementById(id);
    if (!el) return;
    el.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
    setTimeout(function() {{ try {{ el.focus({{ preventScroll: true }}); }} catch (x) {{}} }}, 400);
  }}

  if (form) {{
    form.addEventListener('input', function(ev) {{
      var t = ev.target;
      if (!t || !t.id) return;
      if (['f-fname','f-email','f-level','f-arrive','f-leave'].indexOf(t.id) >= 0) {{
        t.classList.remove('form-invalid');
        t.removeAttribute('aria-invalid');
        var map = {{'f-fname':'err-fname','f-email':'err-email','f-level':'err-level','f-arrive':'err-date','f-leave':'err-date'}};
        var er = document.getElementById(map[t.id]);
        if (er && (t.id !== 'f-arrive' && t.id !== 'f-leave')) er.style.display = 'none';
      }}
    }});
    form.addEventListener('change', function(ev) {{
      var t = ev.target;
      if (t && t.id === 'f-level') {{
        t.classList.remove('form-invalid');
        var er = document.getElementById('err-level');
        if (er) er.style.display = 'none';
      }}
      if (t && (t.id === 'f-arrive' || t.id === 'f-leave')) {{
        var errDt = document.getElementById('err-date');
        if (errDt) errDt.style.display = 'none';
        document.getElementById('f-arrive') && document.getElementById('f-arrive').classList.remove('form-invalid');
        document.getElementById('f-leave') && document.getElementById('f-leave').classList.remove('form-invalid');
      }}
    }});
  }}

  var today = new Date().toISOString().split('T')[0];
  if (fArrive) fArrive.setAttribute('min', today);
  if (fLeave) fLeave.setAttribute('min', today);
  if (fArrive) fArrive.addEventListener('change', function() {{ if (fLeave && this.value) fLeave.setAttribute('min', this.value); }});

  function openSuccessThenWa(msg) {{
    if (!overlay) {{
      window.open('https://wa.me/221789257025?text=' + encodeURIComponent(msg), '_blank');
      return;
    }}
    var card = overlay.querySelector('.booking-success-card');
    var h = overlay.querySelector('.booking-success-title');
    var p = overlay.querySelector('.booking-success-text');
    var w = overlay.querySelector('.booking-success-wa-note');
    var b = overlay.querySelector('.booking-success-close');
    if (h) h.textContent = J.succH;
    if (p) p.textContent = J.succP;
    if (w) w.textContent = J.succWa;
    if (b) b.textContent = J.succBtn;
    overlay.removeAttribute('hidden');
    requestAnimationFrame(function() {{
      overlay.classList.add('is-open');
    }});
    function closeOv() {{
      overlay.classList.remove('is-open');
      setTimeout(function() {{ overlay.setAttribute('hidden', ''); }}, 320);
      document.removeEventListener('keydown', onKey);
    }}
    function onKey(ev) {{ if (ev.key === 'Escape') closeOv(); }}
    document.addEventListener('keydown', onKey);
    if (b) {{
      b.onclick = function() {{ closeOv(); }};
    }}
    overlay.onclick = function(ev) {{ if (ev.target === overlay) closeOv(); }};
    setTimeout(function() {{
      window.open('https://wa.me/221789257025?text=' + encodeURIComponent(msg), '_blank');
    }}, 520);
  }}

  if (form) form.addEventListener('submit', function(e) {{
    e.preventDefault();
    clearFieldErrors();
    var fname = (document.getElementById('f-fname') || {{}}).value || '';
    var email = ((document.getElementById('f-email') || {{}}).value || '').trim().toLowerCase();
    var arrive = (fArrive || {{}}).value || '';
    var leave = (fLeave || {{}}).value || '';
    var levelEl = document.getElementById('f-level');
    var levelVal = levelEl ? levelEl.value : '';
    var issues = [];
    if (!fname.trim()) issues.push({{ id: 'f-fname', err: 'err-fname' }});
    if (!/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(email)) issues.push({{ id: 'f-email', err: 'err-email' }});
    if (!levelVal) issues.push({{ id: 'f-level', err: 'err-level' }});
    if (arrive && leave && leave <= arrive) issues.push({{ id: 'f-leave', err: 'err-date' }});
    if (issues.length) {{
      issues.forEach(function(it) {{ showInvalid(it.id, it.err); }});
      scrollToField(issues[0].id);
      return;
    }}
    var level = (levelEl.options || [])[levelEl.selectedIndex || 0];
    var levelText = level ? level.text : '';
    var cc = ((document.getElementById('f-cc') || {{}}).value || '');
    var phone = ((document.getElementById('f-phone') || {{}}).value || '').trim();
    var goal = ((document.getElementById('f-goal') || {{}}).value || '').trim();
    var roomType = ((document.getElementById('f-room') || {{}}).value || '').trim();
    var roomNames = {{ dormitory: _priceL.dorm, single: _priceL.single, double: _priceL.double }};
    var msg = J.waIntro;
    if (fname) msg += ' ' + J.nameLbl + ': ' + fname + '.';
    if (email) msg += ' ' + J.emailLbl + ': ' + email + '.';
    if (cc && phone) msg += ' ' + J.phoneLbl + ': ' + cc + ' ' + phone + '.';
    if (levelText) msg += ' ' + J.levelLbl + ': ' + levelText + '.';
    if (roomType && roomNames[roomType]) msg += ' ' + J.roomLbl + ': ' + roomNames[roomType] + '.';
    if (arrive) msg += ' ' + J.arrLbl + ': ' + arrive + '.';
    if (leave) msg += ' ' + J.depLbl + ': ' + leave + '.';
    var guests = ((document.getElementById('f-guests') || {{}}).value || '1');
    if (guests) msg += ' ' + J.guestsLbl + ': ' + guests + '.';
    if (goal) msg += ' ' + J.goalLbl + ': ' + goal;
    var btn = form.querySelector('button[type=submit]');
    var btnLabel = form.querySelector('.booking-submit-label');
    if (btn) btn.disabled = true;
    if (btnLabel) btnLabel.textContent = J.sending;
    fetch('/api/booking', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json' }},
      body: JSON.stringify({{
        firstName: fname, email: email,
        phone: (cc ? cc + ' ' : '') + phone,
        arrival: arrive, departure: leave,
        guests: guests, level: levelText,
        roomType: roomType || null,
        message: goal,
        lang: (document.documentElement.lang || 'en').split('-')[0],
        pageUrl: location.href
      }})
    }})
      .then(function(r) {{
        return r.json().catch(function() {{ return {{}}; }}).then(function(j) {{ return {{ ok: r.ok, j: j }}; }});
      }})
      .catch(function() {{ return {{ ok: false, j: {{}} }}; }})
      .then(function(res) {{
        if (btn) btn.disabled = false;
        if (btnLabel) btnLabel.textContent = J.cta;
        if (res.ok && res.j && res.j.ok) {{
          openSuccessThenWa(msg);
        }} else {{
          if (topAlert) {{
            topAlert.textContent = J.errNet;
            topAlert.style.display = 'block';
          }}
          scrollToField('f-fname');
        }}
      }});
  }});
}})();
</script>"""

    html += footer_quotes_block(lang)
    html += build_footer(lang)
    html += page_close()
    return html


def footer_quotes_block(lang):
    """Reuse home-page rotating quotes block (same JS ids per language)."""
    rel = "index.html" if lang == "en" else f"{lang}/index.html"
    path = os.path.join(DEMO_DIR, rel)
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            h = f.read()
    except OSError:
        return ""
    i = h.find("</main>")
    if i < 0:
        return ""
    j = h.find('<div class="footer-quotes"', i)
    if j < 0:
        return ""
    k = h.find("<footer", j)
    if k < 0:
        return ""
    return "\n" + h[j:k].strip() + "\n"


# Surfing page copy (EN source + FR/ES/IT/DE) — thumbnails use existing Wix assets until /assets/images/surfing/* exist
SURF_WIX_THUMBS = [
    "surf2",   # coaching (was thumbnail_surf instructor)
    "surf",    # guiding
    "surf3",   # video analysis
    "art",     # theory / school
    "ngor_r",  # reef & beach
    "island2", # trips
    "sunset",  # chill island
]

SURF_PAGE_COPY = {
    "en": {
        "title": "Surfing in Ngor | Ngor Surfcamp Teranga",
        "meta": "Surf Ngor Island, Dakar: coaching, guiding, video analysis, theory classes, reef breaks and surf trips. Surf better, live slower.",
        "h1": "Surfing in Ngor",
        "tag": "Surf better, live slower, feel the difference",
        "lbl_intro": "Surf at Ngor",
        "p1": "West Africa may not be the first place you think of for waves, but it has a serious surf pedigree. On the Cabo Verde Peninsula, Dakar picks up both northern and southern hemisphere swells \u2014 making it one of the most consistent surf destinations on the planet, 365 days a year.",
        "p2": "While Morocco’s famous spots draw hundreds of surfers at a time, Ngor’s lineups remain refreshingly uncrowded. Hit dawn patrol and you may share a session with fewer than half a dozen riders — an unspoken camaraderie in warm Atlantic water, just a short flight from Europe.",
        "p3": "Two sessions a day — morning and afternoon — at the best spot chosen by forecast and swell. Our surf guide Abu, rated the best in Dakar by our guests, knows exactly how to position you on the wave. Whether you are chasing your first green wave or refining your cutback, we guide your progression at your rhythm.",
        "p4": "Video analysis, free surf theory classes and personalised coaching make every session count. The instructors are local surfers with ISA qualifications who grew up on these reefs — they read these waves the way only locals can.",
        "p5": "Beyond the water, Ngor Island life takes over: no cars, no noise, just the sound of waves and the warmth of Senegalese teranga. From sunrise sessions to rooftop sunsets with African beats and fresh fish from the local shacks, you will grow in and out of the surf, surrounded by like-minded riders from around the world.",
        "thumb_lbl": "What you get",
        "thumb_h2": "Professional surf experience",
        "thumbs": [
            "Professional surf coaching — all levels",
            "Professional surf guiding",
            "Video analysis",
            "Surf theory classes — free: paddling, pop-up, bottom turn, cutback…",
            "Consistent reef and beach breaks",
            "Surf trips (swell dependent)",
            "Chill, safe island with local culture",
            "Authentic Senegalese meals — breakfast & dinner included",
        ],
        "lvl_lbl": "Your level at Ngor",
        "lvl_h2": "Your level at Ngor",
        "beg_t": "Beginner",
        "beg_d": "Never surfed, or just tried once or twice. You will start on a foam board at Ngor Left, a forgiving sandy-bottom wave perfect for building confidence. The warm water and gentle sets make learning feel natural — by the end of your stay, you will be standing and riding green waves.",
        "int_t": "Intermediate",
        "int_d": "You can consistently pop up and ride down the line. Ready to work on turns, reading waves and timing your take-off. Ngor Right on smaller days becomes your playground — a fast, hollow reef break made famous by The Endless Summer film.",
        "adv_t": "Advanced",
        "adv_d": "You surf turns and are pushing your performance. Ngor Right at full size is the wave — powerful, fast and demanding, with enough face to play with on the drop. Our coaches will also take you to the southern breaks of Les Almadies when conditions align. Video analysis will fast-track your specific weaknesses.",
        "team_lbl": "Our team",
        "team_h2": "Why Ngor Surfcamp Teranga?",
        "team_intro": "Meet Ben (owner & coach), Abu (head surf guide — rated the best in Dakar by our guests) and Arame (chef). Together they create an experience that international press and guests alike describe as ‘feeling like home’: impeccable organisation, expert coaching and authentic Senegalese cuisine that earns five stars on its own.",
        "team_isa": "The instructors are local surfers with industry-standard ISA qualifications and national diplomas.",
        "gal_h2": "Our surf trips in action",
        "cta_h2": "Meet like-minded surfers from around the world",
        "cta_sub": "Ngor Island, Dakar, Senegal. WhatsApp: +221 78 925 70 25",
        "book": "Book your surf package",
        "badge_isa": "ISA certified",
        "badge_fed": "Licenced by FSS",
        "badge_loc": "Local knowledge",
        "lb_close": "Close",
        "wa_btn": "WhatsApp",
    },
    "fr": {
        "title": "Surf à Ngor | Ngor Surfcamp Teranga",
        "meta": "Surf sur l’île de Ngor, Dakar : coaching, guidage, analyse vidéo, cours de théorie, reef et trips. Surfez mieux, vivez plus lentement.",
        "h1": "Surf à Ngor",
        "tag": "Surfez mieux, vivez plus lentement, ressentez la différence",
        "lbl_intro": "Le surf à Ngor",
        "p1": "L’Afrique de l’Ouest n’est peut-être pas la première destination surf qui vient à l’esprit, pourtant elle possède un pédigrée inégalable. Sur la presqu’île du Cap-Vert, Dakar capte les houles des deux hémisphères — ce qui en fait l’une des destinations surf les plus consistantes au monde, 365 jours par an.",
        "p2": "Alors que les spots marocains attirent des centaines de surfeurs, les lineups de Ngor restent déserts. Partez au dawn patrol et vous partagerez la session avec moins d’une demi-douzaine de riders — une complicité tacite dans les eaux chaudes de l’Atlantique, à quelques heures d’avion de l’Europe.",
        "p3": "Deux sessions par jour — matin et après-midi — sur le meilleur spot sélectionné selon les prévisions et le swell. Notre guide Abu, élu meilleur guide de surf de Dakar par nos clients, sait exactement comment vous placer sur la vague. Que vous visiez votre première vague verte ou que vous peaufiniez votre cutback, nous guidons votre progression à votre rythme.",
        "p4": "Analyse vidéo, cours de théorie gratuits et coaching personnalisé : chaque session compte. Les instructeurs sont des surfeurs locaux certifiés ISA, qui ont grandi sur ces récifs — ils lisent ces vagues comme seuls les locaux savent le faire.",
        "p5": "Hors de l’eau, la vie de l’île de Ngor prend le relais : pas de voitures, pas de bruit, juste le son des vagues et la chaleur de la teranga sénégalaise. Des sessions à l’aube aux couchers de soleil sur les toits aux rythmes africains, avec du poisson frais des baraques locales, vous grandirez dans et hors du surf, entouré de riders du monde entier.",
        "thumb_lbl": "Ce que nous proposons",
        "thumb_h2": "Une expérience surf professionnelle",
        "thumbs": [
            "Coaching surf professionnel — tous niveaux",
            "Guidage surf professionnel",
            "Analyse vidéo",
            "Cours de théorie surf — gratuits : paddle, take-off, bottom turn, cutback…",
            "Reefs et beach breaks réguliers",
            "Surf trips (selon le swell)",
            "Île chill et sûre, culture locale",
            "Repas sénégalais authentiques — petit-déjeuner & dîner inclus",
        ],
        "lvl_lbl": "Votre niveau à Ngor",
        "lvl_h2": "Votre niveau à Ngor",
        "beg_t": "Débutant",
        "beg_d": "Jamais surfé, ou essayé une ou deux fois. Vous commencerez sur mousse à Ngor Left, une vague douce sur fond de sable, idéale pour prendre confiance. L'eau chaude et les séries régulières rendent l'apprentissage naturel — en fin de séjour, vous serez debout sur des vagues vertes.",
        "int_t": "Intermédiaire",
        "int_d": "Vous enchaînez pop-up et ride sur la ligne. Prêt à travailler virages, lecture des vagues et timing. Ngor Right les petits jours devient votre terrain de jeu — un reef break rapide et creux rendu célèbre par le film The Endless Summer.",
        "adv_t": "Avancé",
        "adv_d": "Vous enchaînez les virages et cherchez la performance. Ngor Right taille réelle est la vague — puissante, rapide et exigeante, avec assez de face pour s’exprimer au take-off. Nos coachs vous emmènent aussi sur les breaks sud des Almadies quand les conditions s’alignent. L’analyse vidéo accélère vos axes de progrès.",
        "team_lbl": "Notre équipe",
        "team_h2": "Pourquoi Ngor Surfcamp Teranga ?",
        "team_intro": "Rencontrez Ben (propriétaire & coach), Abu (guide surf principal — élu meilleur guide de surf de Dakar) et Arame (chef). Ensemble, ils créent une expérience que nos clients décrivent comme \'se sentir chez soi\' : organisation impeccable, coaching expert et une cuisine cinq étoiles.",
        "team_isa": "Les instructeurs sont des surfeurs locaux, diplômés nationaux et qualifiés ISA aux standards de l’industrie.",
        "gal_h2": "Nos trips surf en images",
        "cta_h2": "Rencontrez des surfeurs du monde entier",
        "cta_sub": "Île de Ngor, Dakar, Sénégal. WhatsApp : +221 78 925 70 25",
        "book": "Réserver votre package surf",
        "badge_isa": "Certifié ISA",
        "badge_fed": "Licencié FSS",
        "badge_loc": "Connaissance locale",
        "lb_close": "Fermer",
        "wa_btn": "WhatsApp",
    },
    "es": {
        "title": "Surf en Ngor | Ngor Surfcamp Teranga",
        "meta": "Surf en la isla de Ngor, Dakar: coaching, guía, análisis de vídeo, teoría, reefs y viajes. Surfea mejor, vive más despacio.",
        "h1": "Surf en Ngor",
        "tag": "Surfea mejor, vive más despacio, siente la diferencia",
        "lbl_intro": "Surf en Ngor",
        "p1": "Puede que África Occidental no sea lo primero que pienses para surfear, pero su pedigrí es innegable. En la península de Cabo Verde, Dakar recibe swells de ambos hemisferios — convirtiéndolo en uno de los destinos surf más consistentes del planeta, los 365 días del año.",
        "p2": "Mientras los spots famosos de Marruecos atraen cientos de surfistas, los lineups de Ngor permanecen tranquilos. Sal al dawn patrol y compartirás sesión con menos de media docena de riders — complicidad tácita en aguas cálidas del Atlántico, a pocas horas de vuelo de Europa.",
        "p3": "Dos sesiones al día — mañana y tarde — en el mejor spot elegido según previsiones y swell. Nuestro guía Abu, elegido mejor guía de surf de Dakar por nuestros clientes, sabe exactamente cómo colocarte en la ola. Tanto si persigues tu primera ola verde como si afinas tu cutback, guiamos tu progresión a tu ritmo.",
        "p4": "Análisis de vídeo, clases de teoría gratuitas y coaching personalizado: cada sesión cuenta. Los instructores son surfistas locales con cualificación ISA que crecieron en estos arrecifes — leen estas olas como solo un local puede hacerlo.",
        "p5": "Fuera del agua, la vida en la isla de Ngor toma el relevo: sin coches, sin ruido, solo el sonido de las olas y la calidez de la teranga senegalesa. De las sesiones al amanecer a las puestas de sol en azoteas con ritmos africanos y pescado fresco de los chiringuitos locales, crecerás dentro y fuera del surf, rodeado de riders de todo el mundo.",
        "thumb_lbl": "Lo que ofrecemos",
        "thumb_h2": "Experiencia surf profesional",
        "thumbs": [
            "Coaching surf profesional — todos los niveles",
            "Guía surf profesional",
            "Análisis de vídeo",
            "Clases de teoría surf — gratis: remada, pop-up, bottom turn, cutback…",
            "Reefs y beach breaks consistentes",
            "Surf trips (según swell)",
            "Isla tranquila y segura, cultura local",
            "Comidas senegalesas auténticas — desayuno y cena incluidos",
        ],
        "lvl_lbl": "Tu nivel en Ngor",
        "lvl_h2": "Tu nivel en Ngor",
        "beg_t": "Principiante",
        "beg_d": "Nunca has surfado o lo probaste una o dos veces. Empiezas en espuma en Ngor Left, ola permisiva. Al final estarás de pie y deslizando.",
        "int_t": "Intermedio",
        "int_d": "Haces pop-up y recorres la pared con regularidad. Listo para giros, lectura de olas y timing. Ngor Right en días pequeños será tu campo de juego.",
        "adv_t": "Avanzado",
        "adv_d": "Enlazas maniobras y buscas rendimiento. Ngor Right en tamaño es tu ola: potente y exigente. El análisis de vídeo acelera tus puntos débiles.",
        "team_lbl": "Nuestro equipo",
        "team_h2": "¿Por qué Ngor Surfcamp Teranga?",
        "team_intro": "Conoce a Ben (propietario y coach), Abu (guía principal — elegido mejor guía de surf de Dakar) y Arame (chef). Juntos crean una experiencia que los clientes describen como \'sentirse en casa\': organización impecable, coaching experto y una cocina que merece sus propias estrellas.",
        "team_isa": "Los instructores son surfistas locales con cualificaciones ISA reconocidas y diplomas nacionales.",
        "gal_h2": "Nuestros surf trips en acción",
        "cta_h2": "Conoce surfistas afines de todo el mundo",
        "cta_sub": "Isla de Ngor, Dakar, Senegal. WhatsApp: +221 78 925 70 25",
        "book": "Reserva tu paquete surf",
        "badge_isa": "Certificado ISA",
        "badge_fed": "Licenciado FSS",
        "badge_loc": "Conocimiento local",
        "lb_close": "Cerrar",
        "wa_btn": "WhatsApp",
    },
    "it": {
        "title": "Surf a Ngor | Ngor Surfcamp Teranga",
        "meta": "Surf sull’isola di Ngor, Dakar: coaching, guida, video analisi, teoria, reef e trip. Surfa meglio, vivi più lentamente.",
        "h1": "Surf a Ngor",
        "tag": "Surfa meglio, vivi più lentamente, senti la differenza",
        "lbl_intro": "Il surf a Ngor",
        "p1": "L’Africa Occidentale forse non è la prima meta che viene in mente per il surf, eppure vanta un pedigree innegabile. Sulla penisola di Capo Verde, Dakar intercetta gli swell di entrambi gli emisferi — rendendola una delle destinazioni surf più consistenti al mondo, 365 giorni l’anno.",
        "p2": "Mentre gli spot più famosi del Marocco attirano centinaia di surfisti, i lineup di Ngor restano piacevolmente vuoti. Esci all’alba e potresti condividere la sessione con meno di mezza dozzina di rider — una complicità tacita nelle acque calde dell’Atlantico, a poche ore di volo dall’Europa.",
        "p3": "Due sessioni al giorno — mattina e pomeriggio — nello spot migliore scelto in base alle previsioni e allo swell. La nostra guida Abu, votata la migliore di Dakar dai nostri ospiti, sa esattamente come posizionarti sull’onda. Che tu stia cercando la tua prima onda verde o perfezionando il cutback, guidiamo la tua progressione al tuo ritmo.",
        "p4": "Analisi video, lezioni di teoria gratuite e coaching personalizzato: ogni sessione conta. Gli istruttori sono surfisti locali con qualifiche ISA, cresciuti su queste scogliere — leggono queste onde come solo un locale sa fare.",
        "p5": "Fuori dall’acqua, la vita sull’isola di Ngor prende il sopravvento: niente auto, niente rumore, solo il suono delle onde e il calore della teranga senegalese. Dalle sessioni all’alba ai tramonti sui tetti con ritmi africani e pesce fresco, crescerai dentro e fuori dal surf, circondato da rider di tutto il mondo.",
        "thumb_lbl": "Cosa offriamo",
        "thumb_h2": "Esperienza surf professionale",
        "thumbs": [
            "Coaching surf professionale — tutti i livelli",
            "Guida surf professionale",
            "Analisi video",
            "Lezioni di teoria surf — gratuite: paddling, pop-up, bottom turn, cutback…",
            "Reef e beach break consistenti",
            "Surf trip (in base allo swell)",
            "Isola tranquilla e sicura, cultura locale",
            "Pasti senegalesi autentici — colazione e cena incluse",
        ],
        "lvl_lbl": "Il tuo livello a Ngor",
        "lvl_h2": "Il tuo livello a Ngor",
        "beg_t": "Principiante",
        "beg_d": "Mai surfato o provato una o due volte. Inizi sulla soft a Ngor Left, onda permissiva. A fine soggiorno starai in piedi e scorrendo.",
        "int_t": "Intermedio",
        "int_d": "Pop-up costanti e discesa di parete. Pronto a curve, lettura onde e timing. Ngor Right nei giorni piccoli diventa il tuo playground.",
        "adv_t": "Avanzato",
        "adv_d": "Curve e performance. Ngor Right a misura è la tua onda: potente e impegnativa. La video analisi accelera i punti deboli.",
        "team_lbl": "Il nostro team",
        "team_h2": "Perché Ngor Surfcamp Teranga?",
        "team_intro": "Incontra Ben (proprietario e coach), Abu (guida surf principale — eletto miglior guida surf di Dakar dagli ospiti) e Arame (chef). Insieme creano un’esperienza che gli ospiti descrivono come ‘sentirsi a casa’: organizzazione impeccabile, coaching esperto e cucina da cinque stelle.",
        "team_isa": "Gli istruttori sono surfisti locali con qualifiche ISA riconosciute e diplomi nazionali.",
        "gal_h2": "I nostri surf trip in azione",
        "cta_h2": "Incontra surfisti come te da tutto il mondo",
        "cta_sub": "Isola di Ngor, Dakar, Senegal. WhatsApp: +221 78 925 70 25",
        "book": "Prenota il pacchetto surf",
        "badge_isa": "Certificato ISA",
        "badge_fed": "Autorizzato FSS",
        "badge_loc": "Conoscenza locale",
        "lb_close": "Chiudi",
        "wa_btn": "WhatsApp",
    },
    "de": {
        "title": "Surfen in Ngor | Ngor Surfcamp Teranga",
        "meta": "Surf auf Ngor Island, Dakar: Coaching, Guiding, Videoanalyse, Theorie, Riffs und Trips. Surf besser, lebe langsamer.",
        "h1": "Surfen in Ngor",
        "tag": "Surf besser, lebe langsamer, spüre den Unterschied",
        "lbl_intro": "Surf in Ngor",
        "p1": "Westafrika ist vielleicht nicht das Erste, woran man beim Surfen denkt, doch die Region hat ein einzigartiges Pedigree. Auf der Halbinsel Cap-Vert fängt Dakar Swells beider Hemisphären ein — und zählt damit zu den konstantesten Surfdestinationen der Welt, 365 Tage im Jahr.",
        "p2": "Während Marokkos berühmte Spots Hunderte Surfer anziehen, bleiben Ngors Lineups angenehm leer. Beim Dawn Patrol teilst du die Session vielleicht mit weniger als einem halben Dutzend Ridern — stille Verbundenheit im warmen Atlantik, nur wenige Flugstunden von Europa.",
        "p3": "Zwei Sessions täglich — morgens und nachmittags — am besten Spot nach Forecast und Swell. Unser Surfguide Abu, von unseren Gästen als bester Guide Dakars gewählt, weiß genau, wie er dich auf der Welle positioniert. Ob du deine erste grüne Welle ansteuerst oder deinen Cutback verfeinerst — wir begleiten deinen Fortschritt in deinem Tempo.",
        "p4": "Videoanalyse, kostenlose Surf-Theoriestunden und individuelles Coaching: jede Session zählt. Die Instruktoren sind lokale Surfer mit ISA-Qualifikation, die auf diesen Riffen aufgewachsen sind — sie lesen diese Wellen wie nur Einheimische es können.",
        "p5": "Außerhalb des Wassers übernimmt das Inselleben von Ngor: keine Autos, kein Lärm, nur das Rauschen der Wellen und die Wärme der senegalesischen Teranga. Von Sonnenaufgangssessions bis zu Dachterrassen-Sonnenuntergängen mit afrikanischen Beats und frischem Fisch — du wächst im und außerhalb des Surfs, umgeben von Gleichgesinnten aus aller Welt.",
        "thumb_lbl": "Das erwartet dich",
        "thumb_h2": "Professionelles Surf-Erlebnis",
        "thumbs": [
            "Professionelles Surf-Coaching — alle Level",
            "Professionelles Surf-Guiding",
            "Videoanalyse",
            "Surf-Theorie — kostenlos: Paddeln, Pop-up, Bottom Turn, Cutback…",
            "Konstante Riff- und Strand-Breaks",
            "Surf-Trips (swellabhängig)",
            "Chillige, sichere Insel mit lokaler Kultur",
            "Authentische senegalesische Mahlzeiten — Frühstück & Abendessen inklusive",
        ],
        "lvl_lbl": "Dein Level in Ngor",
        "lvl_h2": "Dein Level in Ngor",
        "beg_t": "Anfänger",
        "beg_d": "Noch nie gesurft oder ein-, zweimal probiert. Du startest auf Softboard an Ngor Left — verzeihende Welle. Am Ende des Aufenthalts stehst und fährst du.",
        "int_t": "Fortgeschritten",
        "int_d": "Du stehst zuverlässig und fährst die Linie. Bereit für Turns, Wellenlesen und Timing. Ngor Right an kleineren Tagen wird dein Spielplatz.",
        "adv_t": "Profi",
        "adv_d": "Du fährst Turns und willst Performance. Ngor Right in Größe ist deine Welle: kraftvoll und fordernd. Videoanalyse beschleunigt deine Schwachstellen.",
        "team_lbl": "Unser Team",
        "team_h2": "Warum Ngor Surfcamp Teranga?",
        "team_intro": "Lerne Ben (Inhaber & Coach), Abu (Head Surfguide — von Gästen zum besten Surfguide in Dakar gewählt) und Arame (Köchin) kennen. Zusammen schaffen sie ein Erlebnis, das Gäste als \'wie zu Hause\' beschreiben: makellose Organisation, Experten-Coaching und eine Küche, die ihre eigenen Sterne verdient.",
        "team_isa": "Die Coaches sind lokale Surfer mit anerkannten ISA-Qualifikationen und nationalen Diplomen.",
        "gal_h2": "Unsere Surf-Trips in Bildern",
        "cta_h2": "Triff gleichgesinnte Surfer aus aller Welt",
        "cta_sub": "Ngor Island, Dakar, Senegal. WhatsApp: +221 78 925 70 25",
        "book": "Surf-Paket buchen",
        "badge_isa": "ISA-zertifiziert",
        "badge_fed": "Lizenziert FSS",
        "badge_loc": "Lokales Know-how",
        "lb_close": "Schließen",
        "wa_btn": "WhatsApp",
    },
    "nl": {
        "title": "Surfen in Ngor | Ngor Surfcamp Teranga",
        "meta": "Surf op Ngor Island, Dakar: coaching, begeleiding, video-analyse, theorieklassen, rifbreken en surftrips. Surf beter, leef langzamer.",
        "h1": "Surfen in Ngor",
        "tag": "Surf beter, leef langzamer, voel het verschil",
        "lbl_intro": "Surfen bij Ngor",
        "p1": "West-Afrika is misschien niet de eerste plek die je aan surfen doet denken, maar het heeft een serieus surfpedigree. Op het schiereiland Kaap Verde vangt Dakar swells van beide halfronden op — wat het een van de meest consistente surfbestemmingen ter wereld maakt, 365 dagen per jaar.",
        "p2": "Terwijl Marokko’s beroemde spots honderden surfers aantrekken, blijven Ngor’s lineups heerlijk leeg. Ga bij zonsopgang het water in en je deelt de sessie misschien met minder dan een half dozijn riders — onuitgesproken verbondenheid in het warme Atlantische water, slechts een korte vlucht van Europa.",
        "p3": "Twee sessies per dag — ’s ochtends en ’s middags — naar de beste spot gekozen op basis van de voorspelling en swell. Onze surfgids Abu, door onze gasten uitgeroepen tot beste surfgids van Dakar, weet precies hoe hij je op de golf moet positioneren. Of je nu je eerste groene golf najaagt of je cutback verfijnt, we begeleiden je progressie op jouw tempo.",
        "p4": "Video-analyse, gratis surftheorielessen en persoonlijke coaching: elke sessie telt. De instructeurs zijn lokale surfers met ISA-kwalificaties die op deze riffen zijn opgegroeid — ze lezen deze golven zoals alleen locals dat kunnen.",
        "p5": "Buiten het water neemt het eilandleven van Ngor het over: geen auto’s, geen lawaai, alleen het geluid van de golven en de warmte van de Senegalese teranga. Van sessies bij zonsopgang tot zonsondergangen op het dak met Afrikaanse beats en verse vis — je groeit in en buiten de surf, omringd door gelijkgestemde riders van over de hele wereld.",
        "thumb_lbl": "Wat je krijgt",
        "thumb_h2": "Professionele surfervaring",
        "thumbs": [
            "Professionele surfcoaching — alle niveaus",
            "Professionele surfbegeleiding",
            "Video-analyse",
            "Surftheorie — gratis: peddelen, pop-up, bottom turn, cutback…",
            "Consistente rif- en strandbreken",
            "Surftrips (afhankelijk van swell)",
            "Rustig, veilig eiland met lokale cultuur",
            "Rustig, veilig eiland met lokale cultuur",
            "Authentieke Senegalese maaltijden — ontbijt & diner inbegrepen",
        ],
        "lvl_lbl": "Jouw niveau in Ngor",
        "lvl_h2": "Jouw niveau in Ngor",
        "beg_t": "Beginner",
        "beg_d": "Nooit gesurfd, of net een paar keer geprobeerd. Je start op een foamboard op Ngor Left, een vergevingsgezinde golf perfect voor beginners. Tegen het einde van je verblijf sta je en rijd je.",
        "int_t": "Gevorderd",
        "int_d": "Je kunt consistent opstaan en de lijn rijden. Klaar om aan turns, golfherkenning en timing te werken. Ngor Right op kleinere dagen wordt jouw speelplaats.",
        "adv_t": "Expert",
        "adv_d": "Je surft turns en wilt je performance verbeteren. Ngor Right op volle kracht is jouw golf: krachtig, snel en veeleisend. Video-analyse zet je specifieke zwakheden sneller aan.",
        "team_lbl": "Ons team",
        "team_h2": "Waarom Ngor Surfcamp Teranga?",
        "team_intro": "Maak kennis met Ben (eigenaar & coach), Abu (hoofd surfgids — door gasten uitgeroepen tot beste surfgids van Dakar) en Arame (kok). Samen creëren ze een ervaring die gasten omschrijven als 'voelt als thuis': onberispelijke organisatie, expert-coaching en eten dat op zichzelf vijf sterren verdient.",
        "team_isa": "De instructeurs zijn lokale surfers met ISA-kwalificaties en nationale diploma's.",
        "gal_h2": "Onze surftrips in actie",
        "cta_h2": "Ontmoet gelijkgestemde surfers van over de hele wereld",
        "cta_sub": "Ngor Island, Dakar, Senegal. WhatsApp: +221 78 925 70 25",
        "book": "Boek je surfpakket",
        "badge_isa": "ISA gecertificeerd",
        "badge_fed": "Erkend FSS",
        "badge_loc": "Lokale kennis",
        "lb_close": "Sluiten",
        "wa_btn": "WhatsApp",
    },
    "ar": {
        "title": "ركوب الأمواج في نغور | Ngor Surfcamp Teranga",
        "meta": "اركب الأمواج في جزيرة نغور، داكار: تدريب، إرشاد، تحليل فيديو، دروس نظرية، كسر الشعاب المرجانية ورحلات الأمواج. اركب أفضل، عش بتمهل.",
        "h1": "ركوب الأمواج في نغور",
        "tag": "اركب أفضل، عش بتمهل، أحسس بالفرق",
        "lbl_intro": "الأمواج في نغور",
        "p1": "قد لا تكون غرب أفريقيا أول ما يخطر ببالك لركوب الأمواج، لكنها تمتلك تاريخاً عريقاً في هذا المجال. على شبه جزيرة الرأس الأخضر، تستقبل داكار أمواج من نصفي الكرة الأرضية — مما يجعلها واحدة من أكثر وجهات ركوب الأمواج اتساقاً في العالم، 365 يوماً في السنة.",
        "p2": "بينما تجذب المغرب مئات راكبي الأمواج، تبقى لاين أب نغور فارغة بشكل منعش. اخرج عند الفجر وقد تشارك الجلسة مع أقل من ستة راكبين — تفاهم صامت في مياه الأطلسي الدافئة، على بعد ساعات قليلة من أوروبا.",
        "p3": "جلستان يومياً — صباحاً ومساءً — في أفضل موقع يختاره مرشدنا أبو، الذي اختاره ضيوفنا كأفضل مرشد في داكار. سواء كنت تطارد موجتك الخضراء الأولى أو تتقن المناورات، نرشد تقدمك بإيقاعك.",
        "p4": "تحليل فيديو، دروس نظرية مجانية وتدريب شخصي: كل جلسة مهمة. المدربون سيرفرز محليون حاصلون على شهادة ISA — يقرأون هذه الأمواج كما لا يستطيع أحد سواهم.",
        "p5": "خارج الماء، تسيطر حياة جزيرة نغور: لا سيارات، لا ضجيج، فقط صوت الأمواج ودفء التيرانجا السنغالية. من جلسات الفجر إلى غروب الشمس على الأسطح مع الإيقاعات الأفريقية والسمك الطازج، ستنمو داخل وخارج الأمواج، محاطاً براكبين من حول العالم.",
        "thumb_lbl": "ما ستحصل عليه",
        "thumb_h2": "تجربة ركوب أمواج احترافية",
        "thumbs": [
            "تدريب احترافي على ركوب الأمواج — جميع المستويات",
            "إرشاد احترافي في ركوب الأمواج",
            "تحليل الفيديو",
            "نظرية ركوب الأمواج — مجاناً: التجديف، الوقوف، المنعطف السفلي، الكاتباك...",
            "كسر الشعاب المرجانية والشواطئ المتسقة",
            "رحلات أمواج (تعتمد على السويل)",
            "جزيرة هادئة وآمنة بثقافة محلية",
            "جزيرة هادئة وآمنة بثقافة محلية",
            "وجبات سنغالية أصيلة — الإفطار والعشاء مشمولان",
        ],
        "lvl_lbl": "مستواك في نغور",
        "lvl_h2": "مستواك في نغور",
        "beg_t": "مبتدئ",
        "beg_d": "لم تركب الأمواج من قبل، أو جربتها مرة أو مرتين فقط. ستبدأ على لوح رغوي في Ngor Left، موجة سهلة مثالية للتعلم. بنهاية إقامتك ستكون تقف وتتزلج.",
        "int_t": "متوسط",
        "int_d": "يمكنك الوقوف باستمرار وركوب الخط. مستعد للعمل على المنعطفات وقراءة الأمواج وتوقيت الانطلاق. Ngor Right في الأيام الصغيرة ستصبح ملعبك.",
        "adv_t": "متقدم",
        "adv_d": "تركب المنعطفات وتسعى لتحسين أدائك. Ngor Right بالحجم الكامل هي موجتك: قوية وسريعة ومتطلبة. تحليل الفيديو سيُسرّع تحسين نقاط ضعفك.",
        "team_lbl": "فريقنا",
        "team_h2": "لماذا Ngor Surfcamp Teranga؟",
        "team_intro": "تعرف على بن (المالك والمدرب)، أبو (مرشد الأمواج الرئيسي — المُعلَّن عنه أفضل مرشد أمواج في داكار) وأرام (الطاهية). معاً يخلقون تجربة يصفها الضيوف بـ'كالمنزل': تنظيم لا تشوبه شائبة، تدريب متخصص وطعام يستحق نجوماً خمساً من تلقاء نفسه.",
        "team_isa": "المدربون محليون معتمدون بمؤهلات ISA والدبلومات الوطنية.",
        "gal_h2": "رحلاتنا على الأمواج في الصور",
        "cta_h2": "التقِ بمتزلجي أمواج من جميع أنحاء العالم",
        "cta_sub": "جزيرة نغور، داكار، السنغال. واتساب: +221 78 925 70 25",
        "book": "احجز باقة ركوب الأمواج",
        "badge_isa": "معتمد من ISA",
        "badge_fed": "مرخص FSS",
        "badge_loc": "معرفة محلية",
        "lb_close": "إغلاق",
        "wa_btn": "واتساب",
    },
}

GALLERY_PAGE_COPY = {
    "en": {
        "title": "Surf Camp Senegal Gallery | Ngor Teranga",
        "meta": "Browse the Ngor Surfcamp Teranga gallery: surf sessions, rooms, island life and the vibe of our surf camp in Senegal.",
        "h1": "Gallery",
        "sub": "Take a closer look at the waves, accommodation and laid-back spirit of Ngor Surfcamp Teranga in Senegal.",
        "eyebrow": "Photo gallery",
        "lead": "Tap an image to view it full size. Thumbnails load first for a faster page; the lightbox opens the full-resolution photo.",
        "img_alt": "Ngor Surfcamp Teranga",
        "lb_close": "Close",
        "cta_h2": "Your next chapter starts here.",
        "book": "Book your stay",
        "wa_btn": "WhatsApp",
    },
    "fr": {
        "title": "Galerie Surf Camp Sénégal | Ngor Teranga",
        "meta": "Parcourez la galerie de Ngor Surfcamp Teranga : sessions de surf, chambres, vie insulaire et ambiance de notre surf camp au Sénégal.",
        "h1": "Galerie",
        "sub": "Découvrez de plus près les vagues, l’hébergement et l’esprit détendu de Ngor Surfcamp Teranga au Sénégal.",
        "eyebrow": "Galerie photos",
        "lead": "Touchez une image pour l’agrandir. Les vignettes se chargent d’abord pour une page plus rapide ; la visionneuse ouvre la photo en pleine résolution.",
        "img_alt": "Ngor Surfcamp Teranga",
        "lb_close": "Fermer",
        "cta_h2": "Votre prochain chapitre commence ici.",
        "book": "Réserver",
        "wa_btn": "WhatsApp",
    },
    "es": {
        "title": "Galería Surf Camp Senegal | Ngor Teranga",
        "meta": "Explora la galería de Ngor Surfcamp Teranga y descubre sesiones de surf, habitaciones, vida isleña y el ambiente de nuestro surf camp en Senegal.",
        "h1": "Galería",
        "sub": "Descubre más de cerca las olas, el alojamiento y el espíritu relajado de Ngor Surfcamp Teranga en Senegal.",
        "eyebrow": "Galería de fotos",
        "lead": "Toca una imagen para verla a tamaño completo. Las miniaturas cargan primero para una página más rápida; el visor abre la foto a resolución completa.",
        "img_alt": "Ngor Surfcamp Teranga",
        "lb_close": "Cerrar",
        "cta_h2": "Tu próximo capítulo empieza aquí.",
        "book": "Reservar",
        "wa_btn": "WhatsApp",
    },
    "it": {
        "title": "Galleria Surf Camp Senegal | Ngor Teranga",
        "meta": "Sfoglia la galleria di Ngor Surfcamp Teranga: surf, camere, vita sull’isola e l’atmosfera del nostro surf camp in Senegal.",
        "h1": "Galleria",
        "sub": "Scopri più da vicino le onde, gli alloggi e lo spirito rilassato di Ngor Surfcamp Teranga in Senegal.",
        "eyebrow": "Galleria fotografica",
        "lead": "Tocca un’immagine per ingrandirla. Le anteprime si caricano prima per una pagina più veloce; la lightbox apre la foto a piena risoluzione.",
        "img_alt": "Ngor Surfcamp Teranga",
        "lb_close": "Chiudi",
        "cta_h2": "Il tuo prossimo capitolo inizia qui.",
        "book": "Prenota",
        "wa_btn": "WhatsApp",
    },
    "de": {
        "title": "Surfcamp Senegal Galerie | Ngor Teranga",
        "meta": "Entdecke die Galerie von Ngor Surfcamp Teranga mit Surf Sessions, Zimmern, Inselleben und der Atmosphäre unseres Surfcamps im Senegal.",
        "h1": "Galerie",
        "sub": "Wirf einen genaueren Blick auf die Wellen, die Unterkunft und den entspannten Spirit von Ngor Surfcamp Teranga im Senegal.",
        "eyebrow": "Fotogalerie",
        "lead": "Tippe auf ein Bild, um es groß zu sehen. Vorschaubilder laden zuerst — die Lightbox öffnet das Foto in voller Auflösung.",
        "img_alt": "Ngor Surfcamp Teranga",
        "lb_close": "Schließen",
        "cta_h2": "Dein nächstes Kapitel beginnt hier.",
        "book": "Jetzt buchen",
        "wa_btn": "WhatsApp",
    },
    "nl": {
        "title": "Surf Camp Senegal Galerij | Ngor Teranga",
        "meta": "Blader door de galerij van Ngor Surfcamp Teranga: surfsessies, kamers, eilandleven en de sfeer van ons surfkamp in Senegal.",
        "h1": "Galerij",
        "sub": "Bekijk de golven, accommodatie en relaxte sfeer van Ngor Surfcamp Teranga in Senegal van dichterbij.",
        "eyebrow": "Fotogalerij",
        "lead": "Tik op een afbeelding om hem op volledig formaat te zien. Miniaturen laden eerst voor een snellere pagina; de lightbox opent de foto op volledige resolutie.",
        "img_alt": "Ngor Surfcamp Teranga",
        "lb_close": "Sluiten",
        "cta_h2": "Jouw volgende avontuur begint hier.",
        "book": "Boek je verblijf",
        "wa_btn": "WhatsApp",
    },
    "ar": {
        "title": "معرض صور مخيم الأمواج في السنغال | Ngor Teranga",
        "meta": "تصفح معرض Ngor Surfcamp Teranga: حصص ركوب الأمواج، الغرف، حياة الجزيرة وأجواء مخيمنا في السنغال.",
        "h1": "معرض الصور",
        "sub": "ألقِ نظرة عن قرب على الأمواج والإقامة والروح المريحة لـ Ngor Surfcamp Teranga في السنغال.",
        "eyebrow": "معرض الصور",
        "lead": "انقر على صورة لعرضها بالحجم الكامل. تُحمَّل الصور المصغرة أولاً لصفحة أسرع؛ يفتح العارض الصورة بالدقة الكاملة.",
        "img_alt": "Ngor Surfcamp Teranga",
        "lb_close": "إغلاق",
        "cta_h2": "فصلك التالي يبدأ هنا.",
        "book": "احجز إقامتك",
        "wa_btn": "واتساب",
    },
}


_IG_HANDLE = "ngorsurfcampteranga"
_IG_URL    = "https://www.instagram.com/ngorsurfcampteranga"
_IG_ICO_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" '
    'aria-hidden="true" style="flex-shrink:0">'
    '<rect x="2" y="2" width="20" height="20" rx="5"/>'
    '<circle cx="12" cy="12" r="5"/>'
    '<circle cx="17.5" cy="6.5" r="1.2" fill="currentColor" stroke="none"/>'
    '</svg>'
)
_IG_CAM_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" '
    'aria-hidden="true">'
    '<path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>'
    '<circle cx="12" cy="13" r="4"/>'
    '</svg>'
)

# Real Instagram photos from @ngorsurfcampteranga — downloaded and hosted locally
# Each filename = the post shortcode (so links back to the exact post)
_IG = "/assets/images/ig"
_IG_PHOTOS = {
    # Home — destination feel + action + joy (6 photos, 2 rows)
    "home": [
        f"{_IG}/DMxiqEtI9UF.webp",    # aerial Ngor Island at golden hour
        f"{_IG}/DODf6KGjJtg.webp",    # surfer in perfect barrel
        f"{_IG}/DTfGteJjEno.webp",    # fiery orange sunset over sea
        f"{_IG}/DVtZNLUDFyE.webp",    # surfers entering water, Dakar skyline
        f"{_IG}/DTV-popgGNG.webp",    # group with surfboards at camp
        f"{_IG}/DS4iP3-jBut.webp",    # smiling surfer on beach
    ],
    # Surf House — action, community, people, surf vibes (6 photos)
    "surf-house": [
        f"{_GAL}/school_ig.webp",    # surf instructor
        f"{_GAL}/CAML1109.webp",     # group of surfers
        f"{_GAL}/salon_ig.webp",     # surf camp interior
        f"{_GAL}/4Y4A1359.webp",     # wave riding
        f"{_GAL}/CAML1121.webp",     # surf camp terrace
        f"{_GAL}/sunset_ig.webp",    # sunset
    ],
    # Surfing — action, waves, beach life (6 photos)
    "surfing": [
        f"{_IG}/DODf6KGjJtg.webp",    # surfer in perfect barrel (hero shot)
        f"{_IG}/DU2W_FoDHY_.webp",    # surfer on wave with fishing boat
        f"{_IG}/DVtZNLUDFyE.webp",    # paddling out from shore
        f"{_IG}/DTAt7IFDEQj.webp",    # surfer on wave, palm frond foreground
        f"{_IG}/DP3plCpCK7L.webp",    # surfboards on beach, local kids
        f"{_IG}/DS4iP3-jBut.webp",    # happy surfer holding board
    ],
}

# Real Instagram post shortcodes — @ngorsurfcampteranga
# Each entry is the shortcode extracted from the post URL
# Format: https://www.instagram.com/p/{shortcode}/
_IG_ALL_POSTS = [
    "DVtZNLUDFyE",   # most recent — surfers entering water, Dakar skyline
    "DU2W_FoDHY_",   # surfer on wave with fishing boat
    "DUfqawDgIGJ",   # group of surfers at camp mosaic wall
    "DUEPEulgNip",   # sunset (skip — low quality)
    "DTfGteJjEno",   # fiery orange sunset
    "DTV-popgGNG",   # group with surfboards at camp entrance
    "DTKjjWBAPNl",   # woman smiling at camp entrance
    "DTAt7IFDEQj",   # surfer on wave, palm frond
    "DS4j1ShjEH6",   # foosball at night
    "DS4iP3-jBut",   # smiling surfer on beach
    "DSw1akLjLNR",   # sky (skip — blank)
    "DMxiqEtI9UF",   # aerial Ngor Island golden hour
    "DNVJiQjIaxx",   # thiéboudienne (Senegalese rice)
    "DODf6KGjJtg",   # surfer in perfect barrel
    "DOvRcp2DE_g",   # pool with colourful mosaic
    "DOf0rNyDEbn",   # sky (skip — blurry)
    "DPTZ2EBjA9z",   # palm trees distant (skip)
    "DP3plCpCK7L",   # surfboards on beach, kids
    "DQeEuzdgNaY",   # mafé (peanut stew)
    "DRRRUDKjFYZ",   # foosball table
]

# Per-context post selection — shortcodes matching _IG_PHOTOS paths above
_IG_POSTS = {
    "home":       ["DMxiqEtI9UF", "DODf6KGjJtg", "DTfGteJjEno",
                   "DVtZNLUDFyE", "DTV-popgGNG",  "DS4iP3-jBut"],
    "surf-house": ["DTV-popgGNG",  "DUfqawDgIGJ",  "DS4iP3-jBut",
                   "DTKjjWBAPNl",  "DRRRUDKjFYZ",  "DSw1akLjLNR"],
    "surfing":    ["DODf6KGjJtg", "DU2W_FoDHY_",  "DVtZNLUDFyE",
                   "DTAt7IFDEQj", "DP3plCpCK7L",  "DS4iP3-jBut"],
}

_IG_COPY = {
    "eyebrow": {
        "en": "INSTAGRAM", "fr": "INSTAGRAM", "es": "INSTAGRAM",
        "it": "INSTAGRAM", "de": "INSTAGRAM", "nl": "INSTAGRAM", "ar": "انستغرام",
    },
    "h2": {
        "en": "Follow Our Waves",
        "fr": "Suivez nos vagues",
        "es": "Sigue nuestras olas",
        "it": "Segui le nostre onde",
        "de": "Folge unseren Wellen",
        "nl": "Volg onze golven",
        "ar": "تابع أمواجنا",
    },
    "sub": {
        "en": "Behind the scenes, sunsets & perfect barrels — live from Ngor Island.",
        "fr": "Coulisses, couchers de soleil et tubes parfaits — en direct de l'île de Ngor.",
        "es": "Bambalinas, atardeceres y tubos perfectos — en directo desde la isla de Ngor.",
        "it": "Dietro le quinte, tramonti e barrel perfetti — dal vivo dall'isola di Ngor.",
        "de": "Backstage, Sonnenuntergänge und perfekte Tubes — live von der Insel Ngor.",
        "nl": "Backstage, zonsondergangen en perfecte barrels — live vanaf Ngor Island.",
        "ar": "كواليس وغروب الشمس والأمواج المثالية — مباشرةً من جزيرة نغور.",
    },
    "follow": {
        "en": "Follow on Instagram",
        "fr": "Suivre sur Instagram",
        "es": "Seguir en Instagram",
        "it": "Seguici su Instagram",
        "de": "Auf Instagram folgen",
        "nl": "Volg op Instagram",
        "ar": "تابعنا على انستغرام",
    },
    "view": {
        "en": "View on Instagram",
        "fr": "Voir sur Instagram",
        "es": "Ver en Instagram",
        "it": "Vedi su Instagram",
        "de": "Auf Instagram ansehen",
        "nl": "Bekijk op Instagram",
        "ar": "عرض على انستغرام",
    },
    "cta_lbl": {
        "en": "Join our community",
        "fr": "Rejoignez notre communauté",
        "es": "Únete a nuestra comunidad",
        "it": "Unisciti alla nostra comunità",
        "de": "Werde Teil unserer Community",
        "nl": "Doe mee met onze community",
        "ar": "انضم إلى مجتمعنا",
    },
    "cta_text": {
        "en": "Share your experience with #NgorSurfcampTeranga",
        "fr": "Partagez votre expérience avec #NgorSurfcampTeranga",
        "es": "Comparte tu experiencia con #NgorSurfcampTeranga",
        "it": "Condividi la tua esperienza con #NgorSurfcampTeranga",
        "de": "Teile dein Erlebnis mit #NgorSurfcampTeranga",
        "nl": "Deel je ervaring met #NgorSurfcampTeranga",
        "ar": "شارك تجربتك مع #NgorSurfcampTeranga",
    },
    # Alt text per context — ordered to match _IG_PHOTOS paths
    "alt_home": {
        "en": ["Aerial view of Ngor Island at golden hour",
               "Surfer in a perfect barrel at Ngor",
               "Fiery orange sunset over Ngor Island",
               "Surfers paddling out with Dakar skyline",
               "Group of surfers with boards at surf camp",
               "Happy surfer smiling on Ngor beach"],
        "fr": ["Vue aérienne de l'île de Ngor à l'heure dorée",
               "Surfeur dans un tube parfait à Ngor",
               "Coucher de soleil orange sur l'île de Ngor",
               "Surfeurs entrant dans l'eau avec Dakar en fond",
               "Groupe de surfeurs avec leurs planches au camp",
               "Surfeur heureux souriant sur la plage de Ngor"],
    },
    "alt_surf_house": {
        "en": ["Surf instructor at Ngor beach",
               "Group of surfers chilling at the camp",
               "Surf camp interior and social area",
               "Surfer riding a wave at Ngor",
               "Sunny terrace at Ngor Surf House",
               "Beautiful sunset over the ocean"],
        "fr": ["Moniteur de surf sur la plage de Ngor",
               "Groupe de surfeurs se relaxant au camp",
               "Intérieur et espace social du surf camp",
               "Surfeur sur une vague à Ngor",
               "Terrasse ensoleillée à la Ngor Surf House",
               "Magnifique coucher de soleil sur l'océan"],
    },
    "alt_surfing": {
        "en": ["Surfer in a perfect barrel at Ngor",
               "Surfer on a wave with a fishing boat at Ngor",
               "Surfers entering the water at Ngor Island",
               "Surfer on a wave with palm frond",
               "Surfboards on the beach with local kids",
               "Smiling surfer holding board after a session"],
        "fr": ["Surfeur dans un tube parfait à Ngor",
               "Surfeur sur une vague avec un bateau de pêche",
               "Surfeurs entrant dans l'eau à l'île de Ngor",
               "Surfeur sur une vague avec feuille de palmier",
               "Planches de surf sur la plage avec des enfants locaux",
               "Surfeur souriant après une session"],
    },
}


_IG_SECTION_START = "<!-- ig-feed-start -->"
_IG_SECTION_END   = "<!-- ig-feed-end -->"


def insta_section(lang: str, context: str = "home") -> str:
    """Generate a clean Instagram-style photo grid using locally-hosted images.

    No external iframes — fast, always visible, matches site DA.
    Each photo links to the corresponding Instagram post.
    Wrapped in ig-feed-start / ig-feed-end comment markers so patch
    functions can cleanly remove and re-inject it.
    context: 'home' | 'surf-house' | 'surfing'
    """
    photos = _IG_PHOTOS.get(context, _IG_PHOTOS["home"])
    # Each image filename IS the shortcode → link directly to that post
    _ctx_posts = _IG_POSTS.get(context, _IG_POSTS["home"])
    post_urls = [f"https://www.instagram.com/p/{sc}/" for sc in _ctx_posts]
    t = _IG_COPY
    is_rtl = lang == "ar"
    dir_attr = ' dir="rtl"' if is_rtl else ""

    def tx(key):
        d = t.get(key, {})
        return d.get(lang) or d.get("en", "")

    alt_key = {
        "home": "alt_home",
        "surf-house": "alt_surf_house",
        "surfing": "alt_surfing",
    }.get(context, "alt_home")
    alts = (t.get(alt_key, {}).get(lang) or t.get(alt_key, {}).get("en")) or ([""] * len(photos))

    cells = []
    for i, (src, alt) in enumerate(zip(photos, alts)):
        href = post_urls[i % len(post_urls)]
        cells.append(
            f'<a class="ig-cell" href="{href}" target="_blank" rel="noopener noreferrer" '
            f'aria-label="{escape(alt)}">'
            f'<img class="ig-cell-img" src="{src}" alt="{escape(alt)}" '
            f'loading="lazy" width="400" height="400" decoding="async">'
            f'<span class="ig-cell-overlay" aria-hidden="true">'
            f'{_IG_CAM_SVG}'
            f'<span class="ig-cell-overlay-lbl">{escape(tx("view"))}</span>'
            f'</span>'
            f'</a>'
        )
    grid_html = "".join(cells)
    _grid_variant = "ig-grid--editorial" if context == "surf-house" else f"ig-grid--{len(photos)}"

    is_home = context == "home"
    # Home: ig section uses sec-light (same bg as forecast above → no wave_in needed).
    # wave_out transitions to the warm sand blog-preview section that follows on home.
    # Non-home: keep existing white bg with its own wave.
    wave_in  = ""
    # Home: ig is sec-light → smooth continuation from forecast → wave_out to sand blog.
    # Non-home: ig is also sec-light, keep wave_out to white for those page contexts.
    if context == "home":
        wave_out = wave_bottom(_BG_LIGHT, _BG_SAND)
    elif context in ("surf-house", "surfing"):
        wave_out = ""  # build_surf_house/build_surfing adds its own wave_out
    else:
        wave_out = wave_bottom(_BG_LIGHT, "#fff")
    sec_cls  = "ig-section sec-light"

    return f"""
  {_IG_SECTION_START}
  {wave_in}
  <section class="{sec_cls}" id="ig-feed"{dir_attr}>
    <div class="container">

      <div class="ig-intro reveal">
        <span class="s-label" style="color:#cc2366;letter-spacing:.1em">{escape(tx("eyebrow"))}</span>
        <h2 class="s-title" style="margin:10px 0 10px">{escape(tx("h2"))}</h2>
        <p class="ig-cta-text" style="margin:0">{escape(tx("sub"))}</p>
      </div>

      <div class="ig-bar reveal">
        <div class="ig-header-left">
          <div class="ig-avatar-wrap">
            <div class="ig-avatar-inner">
              <img src="{LOGO}" alt="@{_IG_HANDLE}" width="52" height="52" loading="lazy">
            </div>
          </div>
          <div class="ig-meta">
            <span class="ig-handle">@{_IG_HANDLE}</span>
            <span class="ig-sub">Ngor Island · Dakar · Senegal</span>
          </div>
        </div>
        <a class="ig-follow-btn" href="{_IG_URL}" target="_blank" rel="noopener noreferrer">
          {_IG_ICO_SVG}&nbsp;{escape(tx("follow"))}
        </a>
      </div>

      <div class="ig-grid {_grid_variant} reveal">{grid_html}</div>

      <div class="ig-cta reveal">
        <p class="ig-cta-text">
          <strong>#NgorSurfcampTeranga</strong> &middot; {escape(tx("cta_text"))}
        </p>
        <a class="ig-follow-btn" href="{_IG_URL}" target="_blank" rel="noopener noreferrer"
           style="display:inline-flex;margin-top:12px">
          {_IG_ICO_SVG}&nbsp;{escape(tx("cta_lbl"))}
        </a>
      </div>

    </div>
  </section>
  {wave_out}
  {_IG_SECTION_END}
"""


def build_gallery(lang):
    C = _site_page_mod.merge_gallery_copy(_BASE_DIR, lang, GALLERY_PAGE_COPY[lang])
    pfx = LANG_PFX[lang]
    book_href = f"{pfx}/{SLUG[lang]['booking']}/"
    if not book_href.startswith("/"):
        book_href = "/" + book_href.lstrip("/")
    hero = IMGS["gallery"][0]

    def pe(txt):
        return escape(fix_em(txt))

    grid = build_gallery_thumb_buttons(IMGS["gallery"], C["img_alt"], pe, thumb_w=560, eager_first=True)

    # Gallery Instagram CTA copy per language
    _gal_ig = {
        "en": ("Follow us on Instagram", "See more on Instagram"),
        "fr": ("Retrouvez-nous sur Instagram", "Voir + sur Instagram"),
        "es": ("Síguenos en Instagram", "Ver más en Instagram"),
        "it": ("Seguici su Instagram", "Vedi di più su Instagram"),
        "de": ("Folge uns auf Instagram", "Mehr auf Instagram sehen"),
        "nl": ("Volg ons op Instagram", "Meer zien op Instagram"),
        "ar": ("تابعونا على إنستغرام", "عرض المزيد على إنستغرام"),
    }
    _gal_ig_sub, _gal_ig_btn = _gal_ig.get(lang, _gal_ig["en"])

    html = page_head(C["title"], C["meta"], lang, "gallery", hero)
    html += build_nav("gallery", lang)
    html += f"""
<main>
  <header class="main-hero" style="background-image:url('{hero}')" role="banner">
    <div class="main-hero-inner">
      <div class="main-hero-eyebrow">
        <span class="main-hero-dot"></span>
        <span>Ngor Surfcamp Teranga</span>
      </div>
      <h1 class="main-hero-h1">{pe(C["h1"])}</h1>
      <p class="main-hero-tagline">{pe(C["sub"])}</p>
      <div class="main-hero-actions">
        <a href="{book_href}" class="btn btn-fire btn-lg">{pe(C.get("book", "Book now"))}</a>
        <a href="#gallery-content" class="btn btn-outline-white btn-lg">&#8964;</a>
      </div>
    </div>
  </header>
  <section id="gallery-content" class="section gallery-page-section">
    <div class="container">
      <div class="gallery-page-intro reveal">
        <span class="s-label">{pe(C["eyebrow"])}</span>
        <p class="gallery-page-lead">{pe(C["lead"])}</p>
      </div>
      <div class="gallery-masonry gallery-masonry--page" role="list">{grid}</div>
      <div class="ig-gallery-cta reveal">
        <div class="ig-gallery-cta-inner">
          <div class="ig-gallery-cta-avatar">
            <div class="ig-avatar-wrap" style="width:64px;height:64px">
              <div class="ig-avatar-inner">
                <img src="{LOGO}" alt="@{_IG_HANDLE}" width="60" height="60" loading="lazy">
              </div>
            </div>
          </div>
          <div class="ig-gallery-cta-text">
            <span class="ig-gallery-cta-handle">@{_IG_HANDLE}</span>
            <p class="ig-gallery-cta-sub">{escape(_gal_ig_sub)}</p>
          </div>
          <a class="ig-follow-btn ig-gallery-cta-btn" href="{_IG_URL}" target="_blank" rel="noopener noreferrer">
            {_IG_ICO_SVG}&nbsp;{escape(_gal_ig_btn)}
          </a>
        </div>
      </div>
    </div>
  </section>
  <div id="lb"><button type="button" id="lb-close" aria-label="{pe(C["lb_close"])}">✕</button><img id="lb-img" src="" alt=""></div>
  {wave_bottom(_BG_WHITE, _BG_NAVY)}
  <div class="cta-band">
    <div class="container">
      <h2>{pe(C["cta_h2"])}</h2>
      <div class="cta-btns">
        <a href="{book_href}" class="btn btn-fire btn-lg">{pe(C["book"])}</a>
        <a href="https://wa.me/221789257025" target="_blank" rel="noopener" class="btn-view-more">
          <span style="width:18px;height:18px;display:inline-flex">{WA_ICO}</span> {pe(C["wa_btn"])}</a>
      </div>
    </div>
  </div>
</main>"""
    html += footer_quotes_block(lang)
    html += build_footer(lang)
    html += page_close()
    return html


def build_surf_house(lang):
    C = _site_page_mod.merge_surf_house_copy(_BASE_DIR, lang, SURF_HOUSE_PAGE[lang])
    feats = SURF_HOUSE_FEATS[lang]
    pfx = LANG_PFX[lang]
    book_href = f"{pfx}/{SLUG[lang]['booking']}/"
    if not book_href.startswith("/"):
        book_href = "/" + book_href.lstrip("/")
    faq_href = f"{pfx}/{SLUG[lang]['faq']}/"
    if not faq_href.startswith("/"):
        faq_href = "/" + faq_href.lstrip("/")
    gal_href = f"{pfx}/{SLUG[lang]['gallery']}/"
    if not gal_href.startswith("/"):
        gal_href = "/" + gal_href.lstrip("/")
    lb_aria = escape(fix_em(GALLERY_PAGE_COPY[lang]["lb_close"]))
    explore_gal_lbl = EXPLORE_GAL.get(lang, EXPLORE_GAL["en"])

    def pe(txt):
        return escape(fix_em(txt))

    def sh_icon(nm):
        svg = FEAT_SVG_INLINE.get(nm)
        if svg:
            return f'<div class="sh-feat-ico" aria-hidden="true"><span style="display:inline-flex;width:22px;height:22px;color:var(--fire);align-items:center;justify-content:center">{svg}</span></div>'
        ico = icon_img(nm, 22)
        if ico:
            return f'<div class="sh-feat-ico">{ico}</div>'
        return f'<div class="sh-feat-ico" aria-hidden="true"><span style="display:inline-flex;width:22px;height:22px;color:var(--fire);align-items:center;justify-content:center">{FEAT_SVG_INLINE.get("feat-check","")}</span></div>'

    feat_cards = []
    for ic, tit, desc in feats:
        feat_cards.append(
            f'<article class="sh-feat-card reveal"><div class="sh-feat-card-inner">'
            f"{sh_icon(ic)}<h3 class=\"sh-feat-title\">{pe(tit)}</h3>"
            f'<p class="sh-feat-desc">{pe(desc)}</p></div></article>'
        )
    feat_html = "".join(feat_cards)

    gal_items = build_gallery_thumb_buttons(
        SURF_HOUSE_SHOTS, C["gal_h2"], pe, thumb_w=520, eager_first=True
    )

    caps = (C["bento_c1"], C["bento_c2"], C["bento_c3"], C["bento_c4"], C["bento_c5"])
    u = SURF_HOUSE_SHOTS
    bento_spec = [
        ("sh-bento__cell sh-bento__a", u[0], caps[0], 720),
        ("sh-bento__cell sh-bento__b", u[1], caps[1], 400),
        ("sh-bento__cell sh-bento__c", u[2], caps[2], 400),
        ("sh-bento__cell sh-bento__d", u[3], caps[3], 560),
        ("sh-bento__cell sh-bento__e", u[4], caps[4], 480),
    ]
    bento_html = ""
    for cls, url, cap, tw in bento_spec:
        thumb = wix_thumb_url(url, tw)
        bento_html += (
            f'<div class="{cls} reveal" style="--sh-bg:url(\'{thumb}\')" role="img" '
            f'aria-label="{pe(cap)}"><span class="sh-bento__glass"><span class="sh-bento__cap">{pe(cap)}</span></span></div>'
        )

    quote_img = wix_thumb_url(IMGS["house2"], 720)
    meals_thumb = wix_thumb_url(IMGS["food"], 640)

    html = page_head(C["title"], C["meta"], lang, "surf-house", IMGS["house"])
    html += f'<a class="skip-to-main" href="#main-content">{pe(C["skip"])}</a>'
    html += build_nav("surf-house", lang)
    html += f"""
<main id="main-content">
  <header class="main-hero" style="background-image:url('/assets/images/gallery/CAML1113_c1a068bf.webp')" role="banner">
    <div class="main-hero-inner">
      <div class="main-hero-eyebrow">
        <span class="main-hero-dot"></span>
        <span>{pe(C["hero_kicker"])}</span>
      </div>
      <h1 class="main-hero-h1">{pe(C["h1"])}</h1>
      <p class="main-hero-tagline">{pe(C["tagline"])}</p>
      <div class="main-hero-actions">
        <a href="{book_href}" class="btn btn-fire btn-lg">{pe(C["book"])}</a>
        <a href="#sh-logement" class="btn btn-outline-white btn-lg">&#8964;</a>
      </div>
    </div>
  </header>

  <section id="sh-logement" class="sh-welcome">
    <div class="container">
      <div class="sh-welcome-grid reveal">
        <div class="sh-welcome-left">
          <span class="s-label">{pe(C["welcome_lbl"])}</span>
          <h2 class="sh-welcome-h2">{pe(C["welcome_title"])}</h2>
          <a href="{book_href}" class="sh-welcome-cta">{pe(C["book"])} &#8594;</a>
        </div>
        <div class="sh-welcome-right">
          <p class="sh-welcome-lead">{pe(C["p2"])}</p>
          <p class="sh-welcome-body">{pe(C["p4"])}</p>
        </div>
      </div>
    </div>
  </section>

  {wave_top(_BG_WHITE, _BG_LIGHT)}
  <section class="sh-rooms-sec sec-light">
    <div class="container">
      <div class="sh-rooms-grid">
        <div class="sh-rooms-visual reveal">
          <img src="{quote_img}" alt="{pe(C["quote_h2"])}" width="720" height="540" loading="lazy" decoding="async" referrerpolicy="no-referrer" class="sh-rooms-img">
        </div>
        <div class="sh-rooms-copy reveal">
          <span class="s-label">{pe(C["rooms_lbl"])}</span>
          <h2 class="sh-rooms-h2">{pe(C["quote_h2"])}</h2>
          <p class="sh-rooms-strong">{pe(C["quote_line1"])}</p>
          <p class="sh-rooms-accent">{pe(C["quote_line2"])}</p>
          <a href="{book_href}" class="btn btn-navy btn-md" style="margin-top:20px">{pe(C["book"])}</a>
        </div>
      </div>
    </div>
  </section>

  {wave_bottom(_BG_LIGHT, _BG_NAVY)}
  <section class="sh-acc sh-acc--dark">
    <div class="container">
      <div class="sh-acc-split">
        <div class="sh-acc-photo-col reveal">
          <img src="/assets/images/gallery/CAML1150_c1f8abfe.webp" alt="{pe(C["acc_h2"])}" width="600" height="500" loading="lazy" decoding="async">
          <span class="sh-acc-photo-badge">Ngor Surf House · Île de Ngor</span>
        </div>
        <div class="sh-acc-feats-col reveal">
          <header class="sh-acc-head">
            <h2 class="sh-acc-title">{pe(C["acc_h2"])}</h2>
            <p class="sh-acc-sub">{pe(C["acc_sub"])}</p>
          </header>
          <div class="sh-feat-grid">{feat_html}</div>
        </div>
      </div>
    </div>
  </section>

  {wave_top(_BG_WHITE, _BG_NAVY)}
  <section class="sh-meals">
    <div class="container">
      <div class="sh-meals-grid reveal">
        <div class="sh-meals-copy">
          <span class="s-label" style="color:var(--fire)">{pe(C["meals_lbl"])}</span>
          <h2 class="sh-meals-h2">{pe(C["meals_h2"])}</h2>
          <p class="sh-meals-p">{pe(C["meals_p"])}</p>
        </div>
        <div class="sh-meals-photo sh-meals-photos">
          <img src="{meals_thumb}" alt="{pe(C["meals_h2"])}" width="640" height="280" loading="lazy" decoding="async" referrerpolicy="no-referrer" class="sh-meals-img sh-meals-img--1">
          <img src="/assets/images/gallery/CAML1103.webp" alt="{pe(C["meals_lbl"])}" width="640" height="170" loading="lazy" decoding="async" class="sh-meals-img sh-meals-img--2">
        </div>
      </div>
    </div>
  </section>

  <section class="section sh-gallery-sec">
    <div class="container">
      <h2 class="s-title reveal" style="text-align:center;margin-bottom:32px">{pe(C["gal_h2"])}</h2>
      <div class="gallery-masonry" role="list">{gal_items}</div>
      <div style="text-align:center;margin-top:36px" class="reveal">
        <button class="btn btn-ocean btn-lg" onclick="sessionStorage.setItem('ngor_gallery_filter','surf_house');window.location='{gal_href}'">{explore_gal_lbl}<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg></button>
      </div>
    </div>
    <div id="lb"><button type="button" id="lb-close" aria-label="{lb_aria}">✕</button><img id="lb-img" src="" alt=""></div>
  </section>

  {wave_bottom(_BG_WHITE, _BG_LIGHT)}
  {insta_section(lang, "surf-house")}
  {wave_bottom(_BG_LIGHT, _BG_NAVY)}
  <div class="cta-band">
    <div class="container">
      <h2>{pe(C["cta_h2"])}</h2>
      <p>{pe(C["cta_p"])}</p>
      <div class="cta-btns">
        <a href="{book_href}" class="btn btn-fire btn-lg">{pe(C["book"])}</a>
        <a href="https://wa.me/221789257025" target="_blank" rel="noopener" class="btn btn-glass btn-lg">
          <span style="width:18px;height:18px;display:inline-flex">{WA_ICO}</span> {pe(C["wa_btn"])}</a>
      </div>
    </div>
  </div>
</main>"""
    html += footer_quotes_block(lang)
    html += build_footer(lang)
    html += page_close()
    return html


SURF_SPLIT_COPY = {
    "en": {
        "h2_waves":      "World-class waves,<br>uncrowded lineups",
        "lbl_coaching":  "Expert Coaching",
        "h2_coaching":   "Two sessions a day,<br>guided by Abu",
        "lbl_community": "Island Life",
        "h2_community":  "No cars, no noise —<br>just island life",
        "fc_lbl": "Live Forecast",
        "fc_h2": "Surf conditions at Ngor",
        "fc_now": "Right now",
        "fc_height": "Wave height",
        "fc_period": "Period",
        "fc_dir": "Direction",
        "fc_swell": "Swell",
        "fc_wind": "Wind",
        "fc_temp": "Water temp",
        "fc_7day": "7-day forecast",
        "fc_powered": "Data: Open-Meteo.com",
        "fc_err": "Forecast temporarily unavailable",
    },
    "fr": {
        "h2_waves":      "Des vagues de haut niveau,<br>des lineups déserts",
        "lbl_coaching":  "Coaching Expert",
        "h2_coaching":   "Deux sessions par jour,<br>guidées par Abu",
        "lbl_community": "Vie d'île",
        "h2_community":  "Pas de voitures, pas de bruit —<br>juste la vie d'île",
        "fc_lbl": "Prévisions en direct",
        "fc_h2": "Conditions surf à Ngor",
        "fc_now": "En ce moment",
        "fc_height": "Hauteur des vagues",
        "fc_period": "Période",
        "fc_dir": "Direction",
        "fc_swell": "Houle",
        "fc_wind": "Vent",
        "fc_temp": "Temp. eau",
        "fc_7day": "Prévisions 7 jours",
        "fc_powered": "Données : Open-Meteo.com",
        "fc_err": "Prévisions temporairement indisponibles",
    },
    "es": {
        "h2_waves":      "Olas de primer nivel,<br>lineups vacíos",
        "lbl_coaching":  "Coaching Experto",
        "h2_coaching":   "Dos sesiones al día,<br>guiadas por Abu",
        "lbl_community": "Vida en la Isla",
        "h2_community":  "Sin coches, sin ruido —<br>solo vida isleña",
        "fc_lbl": "Previsión en directo",
        "fc_h2": "Condiciones surf en Ngor",
        "fc_now": "Ahora mismo",
        "fc_height": "Altura de ola",
        "fc_period": "Período",
        "fc_dir": "Dirección",
        "fc_swell": "Oleaje",
        "fc_wind": "Viento",
        "fc_temp": "Temp. agua",
        "fc_7day": "Previsión 7 días",
        "fc_powered": "Datos: Open-Meteo.com",
        "fc_err": "Previsión no disponible temporalmente",
    },
    "it": {
        "h2_waves":      "Onde mondiali,<br>anima dell'Africa Occidentale",
        "lbl_coaching":  "Coaching Esperto",
        "h2_coaching":   "Due sessioni al giorno,<br>guidate da Abu",
        "lbl_community": "Vita sull'Isola",
        "h2_community":  "Niente auto, niente rumore —<br>solo vita isolana",
        "fc_lbl": "Previsioni live",
        "fc_h2": "Condizioni surf a Ngor",
        "fc_now": "In questo momento",
        "fc_height": "Altezza onde",
        "fc_period": "Periodo",
        "fc_dir": "Direzione",
        "fc_swell": "Mareggiata",
        "fc_wind": "Vento",
        "fc_temp": "Temp. acqua",
        "fc_7day": "Previsioni 7 giorni",
        "fc_powered": "Dati: Open-Meteo.com",
        "fc_err": "Previsioni temporaneamente non disponibili",
    },
    "de": {
        "h2_waves":      "Weltklasse-Wellen,<br>leere Lineups",
        "lbl_coaching":  "Expertencoaching",
        "h2_coaching":   "Zwei Sessions täglich,<br>begleitet von Abu",
        "lbl_community": "Inselleben",
        "h2_community":  "Keine Autos, kein Lärm —<br>nur Inselleben",
        "fc_lbl": "Live-Vorhersage",
        "fc_h2": "Surfbedingungen in Ngor",
        "fc_now": "Gerade jetzt",
        "fc_height": "Wellenhöhe",
        "fc_period": "Periode",
        "fc_dir": "Richtung",
        "fc_swell": "Dünung",
        "fc_wind": "Wind",
        "fc_temp": "Wassertemp.",
        "fc_7day": "7-Tage-Vorhersage",
        "fc_powered": "Daten: Open-Meteo.com",
        "fc_err": "Vorhersage vorübergehend nicht verfügbar",
    },
    "nl": {
        "h2_waves":      "Wereldklasse golven,<br>lege lineups",
        "lbl_coaching":  "Expert Coaching",
        "h2_coaching":   "Twee sessies per dag,<br>begeleid door Abu",
        "lbl_community": "Eilandleven",
        "h2_community":  "Geen auto’s, geen lawaai —<br>alleen eilandleven",
        "fc_lbl": "Live voorspelling",
        "fc_h2": "Surfcondities in Ngor",
        "fc_now": "Nu",
        "fc_height": "Golfhoogte",
        "fc_period": "Periode",
        "fc_dir": "Richting",
        "fc_swell": "Deining",
        "fc_wind": "Wind",
        "fc_temp": "Watertemp.",
        "fc_7day": "7-daagse voorspelling",
        "fc_powered": "Data: Open-Meteo.com",
        "fc_err": "Voorspelling tijdelijk niet beschikbaar",
    },
    "ar": {
        "h2_waves":      "أمواج عالمية،<br>لاين أب فارغة",
        "lbl_coaching":  "تدريب احترافي",
        "h2_coaching":   "جلستان يومياً<br>بإرشاد أبو",
        "lbl_community": "حياة الجزيرة",
        "h2_community":  "بلا سيارات، بلا ضجيج —<br>فقط حياة الجزيرة",
        "fc_lbl": "توقعات مباشرة",
        "fc_h2": "أحوال الأمواج في نغور",
        "fc_now": "الآن",
        "fc_height": "ارتفاع الموج",
        "fc_period": "الفترة",
        "fc_dir": "الاتجاه",
        "fc_swell": "الموج الطويل",
        "fc_wind": "الرياح",
        "fc_temp": "حرارة الماء",
        "fc_7day": "توقعات 7 أيام",
        "fc_powered": "البيانات: Open-Meteo.com",
        "fc_err": "التوقعات غير متاحة مؤقتاً",
    },
}


def build_surfing(lang):
    C = _site_page_mod.merge_surfing_copy(_BASE_DIR, lang, SURF_PAGE_COPY[lang])
    SC = SURF_SPLIT_COPY.get(lang, SURF_SPLIT_COPY["en"])
    pfx = LANG_PFX[lang]
    book_href = f"{pfx}/{SLUG[lang]['booking']}/"
    if not book_href.startswith("/"):
        book_href = "/" + book_href.lstrip("/")
    gal_href = f"{pfx}/{SLUG[lang]['gallery']}/"
    if not gal_href.startswith("/"):
        gal_href = "/" + gal_href.lstrip("/")
    explore_gal_lbl = EXPLORE_GAL.get(lang, EXPLORE_GAL["en"])

    def pe(txt):
        return escape(fix_em(txt))

    FEAT_ICONS = [
        ("feat-coaching", "var(--fire)"),
        ("feat-guide",    "var(--ocean)"),
        ("feat-video",    "var(--navy)"),
        ("feat-theory",   "var(--fire)"),
        ("feat-location", "var(--ocean)"),
        ("feat-transfer", "var(--navy)"),
        ("icon-checklist","var(--fire)"),
        ("feat-food",     "var(--ocean)"),
    ]
    thumbs_html = ""
    for i, (icon_key, color) in enumerate(FEAT_ICONS):
        if i >= len(C["thumbs"]):
            break
        cap = C["thumbs"][i]
        svg = FEAT_SVG_INLINE.get(icon_key, "")
        thumbs_html += (
            f'<div class="surf-feat-card reveal">'
            f'<div class="surf-feat-icon" style="color:{color}">{svg}</div>'
            f'<h3 class="surf-feat-title">{pe(cap)}</h3></div>'
        )

    gal_items = build_gallery_thumb_buttons(
        SURF_ACTION_SHOTS, C["gal_h2"], pe, thumb_w=480, eager_first=True
    )

    html = page_head(C["title"], C["meta"], lang, "surfing", IMGS["surf"])
    html += build_nav("surfing", lang)
    html += f"""
<main>
  <header class="main-hero" style="background-image:url('{IMGS["surf"]}')" role="banner">
    <div class="main-hero-inner">
      <div class="main-hero-eyebrow">
        <span class="main-hero-dot"></span>
        <span>{pe(C["lbl_intro"])}</span>
      </div>
      <h1 class="main-hero-h1">{pe(C["h1"])}</h1>
      <p class="main-hero-tagline">{pe(C["tag"])}</p>
      <div class="main-hero-actions">
        <a href="{book_href}" class="btn btn-fire btn-lg">{pe(C.get("book", "Book now"))}</a>
        <a href="#surf-story" class="btn btn-outline-white btn-lg">&#8964;</a>
      </div>
    </div>
  </header>

  <!-- Story split 1: waves + vibe (text-left, img-right) -->
  <section id="surf-story" class="section surf-story-sec">
    <div class="container">
      <div class="split surf-story-split reveal">
        <div class="surf-story-text">
          <span class="s-label">{pe(C["lbl_intro"])}</span>
          <h2 class="s-title surf-story-h2">{SC["h2_waves"]}</h2>
          <p class="surf-story-p">{pe(C["p1"])}</p>
          <p class="surf-story-p">{pe(C["p2"])}</p>
        </div>
        <div class="split-img surf-story-img">
          <img src="{IMGS["island2"]}" alt="{pe(C["h1"])}" loading="eager" width="680" height="520" decoding="async">
        </div>
      </div>
    </div>
  </section>

  {wave_top(_BG_LIGHT, _BG_WHITE)}
  <!-- Story split 2: coaching (img-left, text-right) -->
  <section class="section sec-light surf-story-sec">
    <div class="container">
      <div class="split surf-story-split reveal">
        <div class="split-img surf-story-img">
          <img src="{IMGS["surf2"]}" alt="{pe(SC["lbl_coaching"])}" loading="lazy" width="680" height="520" decoding="async">
        </div>
        <div class="surf-story-text">
          <span class="s-label">{pe(SC["lbl_coaching"])}</span>
          <h2 class="s-title surf-story-h2">{SC["h2_coaching"]}</h2>
          <p class="surf-story-p">{pe(C["p3"])}</p>
          <p class="surf-story-p">{pe(C["p4"])}</p>
        </div>
      </div>
    </div>
  </section>
  {wave_bottom(_BG_LIGHT, _BG_WHITE)}

  <!-- Story split 3: community + lifestyle (text-left, img-right) -->
  <section class="section surf-story-sec">
    <div class="container">
      <div class="split surf-story-split reveal">
        <div class="surf-story-text">
          <span class="s-label">{pe(SC["lbl_community"])}</span>
          <h2 class="s-title surf-story-h2">{SC["h2_community"]}</h2>
          <p class="surf-story-p">{pe(C["p5"])}</p>
          <div style="margin-top:28px">
            <a href="{book_href}" class="btn btn-fire">{pe(C["book"])}</a>
          </div>
        </div>
        <div class="split-img surf-story-img">
          <img src="{IMGS["sunset"]}" alt="{pe(SC["lbl_community"])}" loading="lazy" width="680" height="520" decoding="async">
        </div>
      </div>
    </div>
  </section>

  {wave_top(_BG_LIGHT, _BG_WHITE)}
  <section class="section sec-light" id="surf-forecast">
    <div class="container">
      <div style="text-align:center;margin-bottom:48px" class="reveal">
        <span class="s-label">{SC.get("fc_lbl","Live Forecast")}</span>
        <h2 class="s-title">{SC.get("fc_h2","Surf conditions at Ngor")}</h2>
      </div>
      <div class="forecast-widget fc-widget reveal" id="fc-widget"
           data-lbl-now="{SC.get('fc_now','Right now')}"
           data-lbl-height="{SC.get('fc_height','Wave height')}"
           data-lbl-period="{SC.get('fc_period','Period')}"
           data-lbl-dir="{SC.get('fc_dir','Direction')}"
           data-lbl-swell="{SC.get('fc_swell','Swell')}"
           data-lbl-wind="{SC.get('fc_wind','Wind')}"
           data-lbl-temp="{SC.get('fc_temp','Water temp')}"
           data-lbl-7day="{SC.get('fc_7day','7-day forecast')}"
           data-lbl-powered="{SC.get('fc_powered','Data: Open-Meteo.com')}"
           data-lbl-err="{SC.get('fc_err','Forecast temporarily unavailable')}">
        <div class="fc-loading"><div class="fc-spinner"></div></div>
      </div>
    </div>
  </section>
  {wave_bottom(_BG_LIGHT, _BG_WHITE)}

  {wave_top(_BG_WHITE, _BG_LIGHT)}
  <section class="section">
    <div class="container">
      <div style="text-align:center;margin-bottom:48px" class="reveal">
        <span class="s-label">{pe(C["thumb_lbl"])}</span>
        <h2 class="s-title">{pe(C["thumb_h2"])}</h2>
      </div>
      <div class="surf-feat-grid reveal">{thumbs_html}</div>
    </div>
  </section>

  <section class="section">
    <div class="container">
      <div style="text-align:center;margin-bottom:48px" class="reveal">
        <span class="s-label">{pe(C["lvl_lbl"])}</span>
        <h2 class="s-title">{pe(C["lvl_h2"])}</h2>
      </div>
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:24px" class="reveal">
        <div style="border-radius:18px;overflow:hidden;box-shadow:0 8px 32px rgba(7,25,46,0.12);background:#fff;border-top:4px solid #29b6f6">
          <img src="/assets/images/gallery/school_4583f4a6.webp" alt="{pe(C["beg_t"])}" style="width:100%;height:220px;object-fit:cover;display:block" loading="lazy" width="460" height="220">
          <div style="padding:22px 20px">
            <div style="display:inline-flex;align-items:center;gap:6px;background:#29b6f615;color:#0288d1;padding:4px 12px;border-radius:20px;font-size:12px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;margin-bottom:12px">{pe(C["beg_t"])}</div>
            <p style="font-size:14.5px;color:#374151;margin:0;line-height:1.68">{pe(C["beg_d"])}</p>
          </div>
        </div>
        <div style="border-radius:18px;overflow:hidden;box-shadow:0 8px 32px rgba(7,25,46,0.12);background:#fff;border-top:4px solid #ff6b35">
          <img src="{IMGS["surf"]}" alt="{pe(C["int_t"])}" style="width:100%;height:220px;object-fit:cover;display:block" loading="lazy" width="460" height="220">
          <div style="padding:22px 20px">
            <div style="display:inline-flex;align-items:center;gap:6px;background:#ff6b3515;color:#e85d20;padding:4px 12px;border-radius:20px;font-size:12px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;margin-bottom:12px">{pe(C["int_t"])}</div>
            <p style="font-size:14.5px;color:#374151;margin:0;line-height:1.68">{pe(C["int_d"])}</p>
          </div>
        </div>
        <div style="border-radius:18px;overflow:hidden;box-shadow:0 8px 32px rgba(7,25,46,0.12);background:#fff;border-top:4px solid #0a2540">
          <img src="{IMGS["surf3"]}" alt="{pe(C["adv_t"])}" style="width:100%;height:220px;object-fit:cover;display:block" loading="lazy" width="460" height="220">
          <div style="padding:22px 20px">
            <div style="display:inline-flex;align-items:center;gap:6px;background:#0a254015;color:#0a2540;padding:4px 12px;border-radius:20px;font-size:12px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;margin-bottom:12px">{pe(C["adv_t"])}</div>
            <p style="font-size:14.5px;color:#374151;margin:0;line-height:1.68">{pe(C["adv_d"])}</p>
          </div>
        </div>
      </div>
    </div>
  </section>

  {wave_top(_BG_LIGHT, _BG_WHITE)}
  <section class="section sec-light">
    <div class="container reveal">
      <div style="text-align:center;max-width:780px;margin:0 auto">
        <span class="s-label">{pe(C["team_lbl"])}</span>
        <h2 class="s-title">{pe(C["team_h2"])}</h2>
        <p style="font-size:17px;color:#374151;line-height:1.85;margin-top:18px;text-align:left">{pe(C["team_intro"])}</p>
        <p style="font-size:17px;color:#374151;line-height:1.85;margin-top:16px;text-align:left;font-weight:600">{pe(C["team_isa"])}</p>
        <div style="display:flex;gap:16px;justify-content:center;flex-wrap:wrap;margin-top:32px">
          <div style="display:flex;align-items:center;gap:10px;padding:12px 20px;border-radius:50px;background:#fff;box-shadow:0 2px 12px rgba(10,37,64,0.08)"><span style="color:var(--fire);font-size:20px">★</span><span style="font-weight:600;font-size:14px">{pe(C["badge_isa"])}</span></div>
          <div style="display:flex;align-items:center;gap:10px;padding:10px 20px;border-radius:50px;background:#fff;box-shadow:0 2px 12px rgba(10,37,64,0.08)"><img src="{FSS_LOGO}" alt="FSS" width="28" height="28" loading="lazy" style="flex-shrink:0"><span style="font-weight:600;font-size:14px">{pe(C["badge_fed"])}</span></div>
          <div style="display:flex;align-items:center;gap:10px;padding:12px 20px;border-radius:50px;background:#fff;box-shadow:0 2px 12px rgba(10,37,64,0.08)"><span style="color:var(--ocean);font-size:20px">🌊</span><span style="font-weight:600;font-size:14px">{pe(C["badge_loc"])}</span></div>
        </div>
      </div>
    </div>
  </section>
  {wave_bottom(_BG_LIGHT, _BG_WHITE)}

  <section class="section">
    <div class="container">
      <h2 class="s-title reveal" style="text-align:center;margin-bottom:40px">{pe(C["gal_h2"])}</h2>
      <div class="gallery-masonry" role="list">{gal_items}</div>
      <div style="text-align:center;margin-top:36px" class="reveal">
        <button class="btn btn-ocean btn-lg" onclick="sessionStorage.setItem('ngor_gallery_filter','surf_action');window.location='{gal_href}'">{explore_gal_lbl}<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg></button>
      </div>
    </div>
    <div id="lb"><button id="lb-close" aria-label="{pe(C["lb_close"])}">✕</button><img id="lb-img" src="" alt=""></div>
  </section>

  {wave_bottom(_BG_WHITE, _BG_LIGHT)}
  {insta_section(lang, "surfing")}
  {wave_bottom(_BG_LIGHT, _BG_NAVY)}
  <div class="cta-band">
    <div class="container">
      <h2>{pe(C["cta_h2"])}</h2>
      <h3 style="font-size:20px;font-weight:300;opacity:0.82;margin-bottom:36px">{pe(C["cta_sub"])}</h3>
      <div class="cta-btns">
        <a href="{book_href}" class="btn btn-fire btn-lg">{pe(C["book"])}</a>
        <a href="https://wa.me/221789257025" target="_blank" rel="noopener" class="btn btn-glass btn-lg">
          <span style="width:18px;height:18px;display:inline-flex">{WA_ICO}</span> {pe(C["wa_btn"])}</a>
      </div>
    </div>
  </div>
</main>"""
    html += footer_quotes_block(lang)
    html += build_footer(lang)
    html += page_close()
    return html




# ─── Surf Conditions page ────────────────────────────────────────────────────


# ─── Surf Conditions page ────────────────────────────────────────────────────

def _load_surf_history():
    """Load pre-generated 2025 historical surf data."""
    import json as _j
    try:
        p = os.path.join(_BASE_DIR, "content", "surf_history_2025.json")
        with open(p, encoding="utf-8") as f:
            return _j.load(f)
    except Exception:
        return {}


def build_surf_conditions_page(lang):
    """Full surf conditions & forecast page — live data + 2025 historical recap."""
    pfx       = LANG_PFX[lang]
    slug      = SLUG[lang].get("surf-conditions", "surf-conditions")
    book_href = f"{pfx}/{SLUG[lang]['booking']}/"
    surf_href = f"{pfx}/{SLUG[lang]['surfing']}/"
    history   = _load_surf_history()

    # ── Translations ──────────────────────────────────────────────────────────
    T = {
        "title":      {"en":"Surf Forecast Ngor Island | Wave Conditions Dakar","fr":"Prévisions Surf Ngor | Conditions Vagues Dakar","es":"Previsiones Surf Ngor | Condiciones Olas Dakar","it":"Previsioni Surf Ngor | Condizioni Onde Dakar","de":"Surfvorhersage Ngor Island | Wellenbedingungen Dakar","nl":"Surfvoorspelling Ngor | Golfcondities Dakar","ar":"توقعات السيرف نغور | أحوال الأمواج داكار"},
        "meta":       {"en":"Live surf conditions, 16-day forecast and 2025 seasonal data for Ngor Island, Dakar. Compare Ngor surf with France and Morocco. Wave height, swell, wind, water temperature for all levels.","fr":"Conditions surf en direct, prévisions 16 jours et données saisonnières 2025 pour l'île de Ngor, Dakar. Comparaison avec la France et le Maroc. Hauteur des vagues, houle, vent, température de l'eau.","es":"Condiciones de surf en vivo, previsiones a 16 días y datos estacionales 2025 para la isla de Ngor, Dakar. Comparación con Francia y Marruecos. Altura de ola, swell, viento y temperatura del agua.","it":"Condizioni surf in diretta, previsioni 16 giorni e dati stagionali 2025 per Ngor Island, Dakar. Confronto con Francia e Marocco. Altezza onde, mareggiata, vento, temperatura dell'acqua.","de":"Live-Surfbedingungen, 16-Tage-Vorhersage und Saisondaten 2025 für Ngor Island, Dakar. Vergleich mit Frankreich und Marokko. Wellenhöhe, Dünung, Wind, Wassertemperatur.","nl":"Live surfcondities, 16-daagse voorspelling en seizoensdata 2025 voor Ngor Island, Dakar. Vergelijking met Frankrijk en Marokko. Golfhoogte, deining, wind, watertemperatuur.","ar":"أحوال أمواج مباشرة وتوقعات 16 يوماً وبيانات موسمية لعام 2025 لجزيرة نغور بداكار. مقارنة مع فرنسا والمغرب. ارتفاع الموج والحوله والرياح وحرارة الماء."},
        "h1":         {"en":"Surf Conditions at Ngor Island","fr":"Conditions Surf à Ngor","es":"Condiciones de Surf en Ngor","it":"Condizioni Surf a Ngor","de":"Surfbedingungen auf Ngor Island","nl":"Surfcondities bij Ngor Island","ar":"أحوال الأمواج في جزيرة نغور"},
        "sub":        {"en":"Live data from Open-Meteo · updated every hour · Ngor Island, Dakar, Senegal","fr":"Données en direct Open-Meteo · actualisées chaque heure · Île de Ngor, Dakar, Sénégal","es":"Datos en vivo Open-Meteo · actualizados cada hora · Isla de Ngor, Dakar, Senegal","it":"Dati in diretta Open-Meteo · aggiornati ogni ora · Ngor Island, Dakar, Senegal","de":"Live-Daten Open-Meteo · stündlich aktualisiert · Ngor Island, Dakar, Senegal","nl":"Live data Open-Meteo · elk uur bijgewerkt · Ngor Island, Dakar, Senegal","ar":"بيانات مباشرة Open-Meteo · تُحدَّث كل ساعة · جزيرة نغور، داكار، السنغال"},
        # How data works
        "how_lbl":    {"en":"How this data works","fr":"Comment fonctionnent ces données","es":"Cómo funcionan estos datos","it":"Come funzionano questi dati","de":"Wie diese Daten funktionieren","nl":"Hoe deze data werkt","ar":"كيف تعمل هذه البيانات"},
        "how_live":   {"en":"Live conditions","fr":"Conditions en direct","es":"Condiciones en vivo","it":"Condizioni in diretta","de":"Live-Bedingungen","nl":"Live condities","ar":"الأحوال المباشرة"},
        "how_live_p": {"en":"Wave height, period, swell and wind are fetched directly from the Open-Meteo Marine API each time you load this page. Data is sourced from ECMWF and NOAA ocean models updated every hour.","fr":"La hauteur des vagues, la période, la houle et le vent sont récupérés directement depuis l'API Marine Open-Meteo à chaque chargement de cette page. Les données proviennent des modèles océaniques ECMWF et NOAA, mis à jour toutes les heures.","es":"La altura de ola, período, swell y viento se obtienen directamente de la API Marina Open-Meteo cada vez que cargas esta página. Los datos provienen de los modelos oceánicos ECMWF y NOAA actualizados cada hora.","it":"Altezza onda, periodo, mareggiata e vento vengono recuperati direttamente dall'API Marina Open-Meteo ogni volta che carichi questa pagina. I dati provengono dai modelli oceanici ECMWF e NOAA aggiornati ogni ora.","de":"Wellenhöhe, Periode, Dünung und Wind werden bei jedem Seitenaufruf direkt von der Open-Meteo Marine API abgerufen. Die Daten stammen aus ECMWF- und NOAA-Ozeanmodellen, die stündlich aktualisiert werden.","nl":"Golfhoogte, periode, deining en wind worden direct opgehaald van de Open-Meteo Marine API elke keer dat je deze pagina laadt. De data komt van ECMWF- en NOAA-oceaanmodellen die elk uur worden bijgewerkt.","ar":"يتم جلب ارتفاع الموج والفترة والحوله والرياح مباشرة من واجهة Open-Meteo Marine API في كل مرة تحمّل فيها هذه الصفحة. البيانات مصدرها نماذج ECMWF وNOAA المحيطية المحدَّثة كل ساعة."},
        "how_fc":     {"en":"16-day forecast","fr":"Prévisions à 16 jours","es":"Previsión a 16 días","it":"Previsioni a 16 giorni","de":"16-Tage-Vorhersage","nl":"16-daagse voorspelling","ar":"توقعات 16 يوماً"},
        "how_fc_p":   {"en":"The 16-day marine forecast uses the GFS Wave and ECMWF WAM models, recomputed every 6 hours. Accuracy is highest for the first 5 days and diminishes gradually beyond that — a common characteristic of all numerical weather models.","fr":"Les prévisions marines à 16 jours utilisent les modèles GFS Wave et ECMWF WAM, recalculés toutes les 6 heures. La précision est maximale pour les 5 premiers jours et diminue progressivement au-delà — une caractéristique commune à tous les modèles numériques météo.","es":"Las previsiones marinas a 16 días utilizan los modelos GFS Wave y ECMWF WAM, recalculados cada 6 horas. La precisión es máxima para los primeros 5 días y disminuye gradualmente más allá — una característica común a todos los modelos numéricos meteorológicos.","it":"Le previsioni marine a 16 giorni utilizzano i modelli GFS Wave ed ECMWF WAM, ricalcolati ogni 6 ore. La precisione è massima per i primi 5 giorni e diminuisce gradualmente oltre — una caratteristica comune a tutti i modelli numerici meteorologici.","de":"Die 16-Tage-Seegangsvorhersage verwendet die GFS Wave- und ECMWF WAM-Modelle, die alle 6 Stunden neu berechnet werden. Die Genauigkeit ist für die ersten 5 Tage am höchsten und nimmt danach schrittweise ab — eine übliche Eigenschaft aller numerischen Wettermodelle.","nl":"De 16-daagse mariene voorspelling maakt gebruik van de GFS Wave- en ECMWF WAM-modellen, die elke 6 uur opnieuw worden berekend. De nauwkeurigheid is het grootst voor de eerste 5 dagen en neemt daarna geleidelijk af — een gebruikelijke eigenschap van alle numerieke weermodellen.","ar":"تستخدم توقعات 16 يوماً البحرية نماذج GFS Wave وECMWF WAM، التي تُعاد حسابها كل 6 ساعات. الدقة في أعلى مستوياتها خلال أول 5 أيام وتتناقص تدريجياً بعد ذلك — وهي خاصية شائعة لجميع نماذج الطقس العددية."},
        "how_hist":   {"en":"2025 historical data","fr":"Données historiques 2025","es":"Datos históricos 2025","it":"Dati storici 2025","de":"Historische Daten 2025","nl":"Historische data 2025","ar":"البيانات التاريخية لعام 2025"},
        "how_hist_p": {"en":"Monthly averages were computed from ERA5 ocean reanalysis data — a validated retrospective dataset from the European Centre for Medium-Range Weather Forecasts. This data was calculated once during site build and embedded directly into the page. It does not require a daily API call.","fr":"Les moyennes mensuelles ont été calculées à partir des données de réanalyse océanique ERA5 — un ensemble de données rétrospectif validé du Centre européen pour les prévisions météorologiques à moyen terme. Ces données ont été calculées une fois lors de la construction du site et intégrées directement dans la page. Elles ne nécessitent pas d'appel API quotidien.","es":"Las medias mensuales se calcularon a partir de datos de reanálisis oceánico ERA5 — un conjunto de datos retrospectivos validado del Centro Europeo de Previsiones Meteorológicas a Plazo Medio. Estos datos se calcularon una vez durante la construcción del sitio y se incrustaron directamente en la página. No requieren una llamada API diaria.","it":"Le medie mensili sono state calcolate dai dati di rianalisi oceanica ERA5 — un dataset retrospettivo validato del Centro Europeo per le Previsioni Meteorologiche a Medio Termine. Questi dati sono stati calcolati una volta durante la costruzione del sito e incorporati direttamente nella pagina. Non richiedono una chiamata API giornaliera.","de":"Die Monatsmittelwerte wurden aus ERA5-Ozeanreanalysedaten berechnet — einem validierten retrospektiven Datensatz des Europäischen Zentrums für mittelfristige Wettervorhersage. Diese Daten wurden einmalig beim Site-Build berechnet und direkt in die Seite eingebettet. Sie erfordern keinen täglichen API-Aufruf.","nl":"De maandgemiddelden werden berekend uit ERA5-oceaanreanalysedata — een gevalideerde retrospectieve dataset van het Europees Centrum voor Weersverwachtingen op Middellange Termijn. Deze data werd eenmalig berekend tijdens de sitebouw en direct in de pagina ingesloten. Er is geen dagelijkse API-aanroep nodig.","ar":"حُسبت المتوسطات الشهرية من بيانات إعادة تحليل المحيطات ERA5 — مجموعة بيانات تاريخية موثقة من المركز الأوروبي للتنبؤات الجوية متوسطة المدى. تمت معالجة هذه البيانات مرة واحدة أثناء بناء الموقع وتضمينها مباشرة في الصفحة، دون الحاجة إلى استدعاء API يومي."},
        # Current section
        "now_lbl":    {"en":"Right now","fr":"En ce moment","es":"Ahora mismo","it":"In questo momento","de":"Gerade jetzt","nl":"Nu","ar":"الآن"},
        "wave_h":     {"en":"Wave height","fr":"Hauteur des vagues","es":"Altura de ola","it":"Altezza onde","de":"Wellenhöhe","nl":"Golfhoogte","ar":"ارتفاع الموج"},
        "period":     {"en":"Period","fr":"Période","es":"Período","it":"Periodo","de":"Periode","nl":"Periode","ar":"الفترة"},
        "direction":  {"en":"Direction","fr":"Direction","es":"Dirección","it":"Direzione","de":"Richtung","nl":"Richting","ar":"الاتجاه"},
        "swell_h":    {"en":"Swell","fr":"Houle","es":"Swell","it":"Mareggiata","de":"Dünung","nl":"Deining","ar":"الحوله"},
        "wind_lbl":   {"en":"Wind","fr":"Vent","es":"Viento","it":"Vento","de":"Wind","nl":"Wind","ar":"الرياح"},
        "water_t":    {"en":"Water temp.","fr":"Temp. eau","es":"Temp. agua","it":"Temp. acqua","de":"Wassertemp.","nl":"Watertemp.","ar":"حرارة الماء"},
        "quality":    {"en":"Surf quality","fr":"Qualité surf","es":"Calidad surf","it":"Qualità surf","de":"Surfqualität","nl":"Surfkwaliteit","ar":"جودة السيرف"},
        # Forecast
        "fc_lbl":     {"en":"16-Day Forecast","fr":"Prévisions 16 Jours","es":"Previsión 16 Días","it":"Previsioni 16 Giorni","de":"16-Tage-Vorhersage","nl":"16-Daagse Voorspelling","ar":"توقعات 16 يوماً"},
        "fc_note":    {"en":"Forecast accuracy is highest for days 1–5. Beyond day 5, use as a general trend indicator.","fr":"La précision des prévisions est maximale pour les jours 1 à 5. Au-delà du 5e jour, utilisez-les comme indicateur de tendance générale.","es":"La precisión de las previsiones es máxima para los días 1–5. Más allá del día 5, úsalas como indicador de tendencia general.","it":"La precisione delle previsioni è massima per i giorni 1–5. Oltre il giorno 5, utilizzarle come indicatore di tendenza generale.","de":"Die Vorhersagegenauigkeit ist für die Tage 1–5 am höchsten. Nach Tag 5 als allgemeiner Trendindikator verwenden.","nl":"Voorspellingsnauwkeurigheid is het hoogst voor dag 1–5. Gebruik het na dag 5 als algemene trendindicator.","ar":"دقة التوقعات في أعلى مستوياتها للأيام 1-5. بعد اليوم 5، استخدمها كمؤشر للاتجاه العام."},
        # Historical
        "hist_lbl":   {"en":"2025 Season in Review","fr":"Bilan de la Saison 2025","es":"Balance de la Temporada 2025","it":"Stagione 2025 in Retrospettiva","de":"Saison 2025 im Rückblick","nl":"Seizoen 2025 Terugblik","ar":"مراجعة موسم 2025"},
        "hist_h2":    {"en":"Best months to surf Ngor Island","fr":"Les meilleurs mois pour surfer à Ngor","es":"Los mejores meses para surfear en Ngor","it":"I migliori mesi per fare surf a Ngor","de":"Die besten Monate zum Surfen auf Ngor","nl":"De beste maanden om te surfen op Ngor","ar":"أفضل الأشهر للسيرف في نغور"},
        "hist_sub":   {"en":"Monthly averages computed from 2025 ERA5 ocean reanalysis. Select your level for a personalised surf calendar.","fr":"Moyennes mensuelles calculées à partir de la réanalyse ERA5 2025. Sélectionnez votre niveau pour un calendrier surf personnalisé.","es":"Medias mensuales calculadas a partir de la reanálisis ERA5 de 2025. Selecciona tu nivel para un calendario surf personalizado.","it":"Medie mensili calcolate dalla rianalisi ERA5 2025. Seleziona il tuo livello per un calendario surf personalizzato.","de":"Monatsmittelwerte aus der ERA5-Reanalyse 2025. Wähle dein Level für einen personalisierten Surfkalender.","nl":"Maandgemiddelden berekend uit ERA5-reanalyse 2025. Selecteer je niveau voor een gepersonaliseerde surfkalender.","ar":"متوسطات شهرية محسوبة من إعادة تحليل ERA5 لعام 2025. اختر مستواك للحصول على تقويم سيرف مخصص."},
        "month_lbl":  {"en":"Monthly overview","fr":"Aperçu mensuel","es":"Vista mensual","it":"Panoramica mensile","de":"Monatsübersicht","nl":"Maandoverzicht","ar":"النظرة الشهرية"},
        "temp_lbl":   {"en":"Water temperature","fr":"Température de l'eau","es":"Temperatura del agua","it":"Temperatura dell'acqua","de":"Wassertemperatur","nl":"Watertemperatuur","ar":"درجة حرارة الماء"},
        "lev_beg":    {"en":"Beginner","fr":"Débutant","es":"Principiante","it":"Principiante","de":"Anfänger","nl":"Beginner","ar":"مبتدئ"},
        "lev_int":    {"en":"Intermediate","fr":"Intermédiaire","es":"Intermedio","it":"Intermedio","de":"Fortgeschritten","nl":"Gemiddeld","ar":"متوسط"},
        "lev_adv":    {"en":"Advanced","fr":"Avancé","es":"Avanzado","it":"Avanzato","de":"Profi","nl":"Gevorderd","ar":"متقدم"},
        "chart_wave": {"en":"Avg. wave height (m)","fr":"Hauteur vagues moy. (m)","es":"Altura media de ola (m)","it":"Altezza onde media (m)","de":"Mittl. Wellenhöhe (m)","nl":"Gem. golfhoogte (m)","ar":"متوسط ارتفاع الموج (م)"},
        "chart_wind": {"en":"Avg. wind (kt)","fr":"Vent moyen (kt)","es":"Viento medio (kt)","it":"Vento medio (kt)","de":"Mittl. Wind (kt)","nl":"Gem. wind (kt)","ar":"متوسط الرياح (عقدة)"},
        "chart_period":{"en":"Avg. wave period (s)","fr":"Période moy. (s)","es":"Período medio (s)","it":"Periodo medio (s)","de":"Mittl. Wellenperiode (s)","nl":"Gem. golfperiode (s)","ar":"متوسط فترة الموج (ث)"},
        "chart_temp": {"en":"Water temp. (°C)","fr":"Temp. eau (°C)","es":"Temp. agua (°C)","it":"Temp. acqua (°C)","de":"Wassertemp. (°C)","nl":"Watertemp. (°C)","ar":"حرارة الماء (°م)"},
        "score_lbl":  {"en":"Surf score (0–10)","fr":"Score surf (0–10)","es":"Puntuación surf (0–10)","it":"Punteggio surf (0–10)","de":"Surf-Score (0–10)","nl":"Surfscore (0–10)","ar":"نقاط السيرف (0-10)"},
        # Season boxes
        "seas_lbl":   {"en":"Seasonal guide","fr":"Guide saisonnier","es":"Guía estacional","it":"Guida stagionale","de":"Saisonaler Leitfaden","nl":"Seizoensgids","ar":"الدليل الموسمي"},
        "seas_peak_t": {"en":"Peak season","fr":"Haute saison","es":"Temporada alta","it":"Alta stagione","de":"Hauptsaison","nl":"Hoogseizoen","ar":"موسم الذروة"},
        "seas_peak_m": {"en":"Nov · Dec · Jan · Feb · Mar · Apr","fr":"Nov · Déc · Jan · Fév · Mar · Avr","es":"Nov · Dic · Ene · Feb · Mar · Abr","it":"Nov · Dic · Gen · Feb · Mar · Apr","de":"Nov · Dez · Jan · Feb · Mär · Apr","nl":"Nov · Dec · Jan · Feb · Mar · Apr","ar":"نوف · ديس · يناير · فبر · مارس · أبر"},
        "seas_peak_p": {"en":"North Atlantic swells 2–2.5m with long 11–12s periods. Ngor Right at its most powerful. Best for intermediate and advanced surfers.","fr":"Houles nord-atlantiques de 2 à 2,5m avec de longues périodes de 11 à 12s. Ngor Right à son plus puissant. Idéal pour les niveaux intermédiaire et avancé.","es":"Swells del Atlántico Norte de 2 a 2,5m con largos períodos de 11 a 12s. Ngor Right en su momento más potente. Ideal para surfistas de nivel intermedio y avanzado.","it":"Swell del Nord Atlantico da 2 a 2,5m con lunghi periodi da 11 a 12s. Ngor Right al massimo della potenza. Ideale per surfisti di livello intermedio e avanzato.","de":"Nordatlantik-Swells von 2 bis 2,5m mit langen 11–12s-Perioden. Ngor Right auf seinem mächtigsten. Am besten für Fortgeschrittene und Profis.","nl":"Noord-Atlantische swells van 2–2,5m met lange perioden van 11–12s. Ngor Right op zijn krachtigst. Ideaal voor gevorderde en professionele surfers.","ar":"أمواج شمال الأطلسي من 2 إلى 2.5م مع فترات طويلة من 11 إلى 12 ثانية. نغور رايت في أوج قوتها. مثالية للمستويين المتوسط والمتقدم."},
        "seas_trans_t":{"en":"Transition season","fr":"Saison de transition","es":"Temporada de transición","it":"Stagione di transizione","de":"Übergangssaison","nl":"Overgangsseizoen","ar":"موسم الانتقال"},
        "seas_trans_m":{"en":"May · Oct","fr":"Mai · Oct","es":"May · Oct","it":"Mag · Ott","de":"Mai · Okt","nl":"Mei · Okt","ar":"مايو · أكتوبر"},
        "seas_trans_p":{"en":"Mixed conditions: 1.8–2.1m waves, lighter winds. Good for all levels. Water temperature at its most comfortable (25–31°C).","fr":"Conditions mixtes : vagues de 1,8 à 2,1m, vents plus légers. Bon pour tous les niveaux. Température de l'eau à son plus confortable (25–31°C).","es":"Condiciones mixtas: olas de 1,8 a 2,1m, vientos más ligeros. Bueno para todos los niveles. Temperatura del agua en su punto más confortable (25–31°C).","it":"Condizioni miste: onde da 1,8 a 2,1m, venti più leggeri. Ottimo per tutti i livelli. Temperatura dell'acqua al massimo del comfort (25–31°C).","de":"Gemischte Bedingungen: 1,8–2,1m Wellen, leichtere Winde. Gut für alle Level. Wassertemperatur am angenehmsten (25–31°C).","nl":"Gemengde condities: 1,8–2,1m golven, lichtere winden. Goed voor alle niveaus. Watertemperatuur op comfortabelst (25–31°C).","ar":"ظروف متنوعة: أمواج من 1.8 إلى 2.1م ورياح أخف. مناسبة لجميع المستويات. أكثر درجات حرارة الماء راحة (25-31°م)."},
        "seas_sum_t":  {"en":"Summer season","fr":"Saison estivale","es":"Temporada estival","it":"Stagione estiva","de":"Sommersaison","nl":"Zomerseizoen","ar":"الموسم الصيفي"},
        "seas_sum_m":  {"en":"Jun · Jul · Aug · Sep","fr":"Jun · Jul · Aoû · Sep","es":"Jun · Jul · Ago · Sep","it":"Giu · Lug · Ago · Set","de":"Jun · Jul · Aug · Sep","nl":"Jun · Jul · Aug · Sep","ar":"يونيو · يوليو · أغسطس · سبتمبر"},
        "seas_sum_p":  {"en":"Smaller waves (1.4–1.7m) with lighter winds and minimal crowds. Ideal for beginners and longboarders. Water temperature reaches 29–30°C — no wetsuit needed.","fr":"Vagues plus petites (1,4–1,7m) avec des vents plus légers et très peu de monde. Idéal pour les débutants et les longboarders. La température de l'eau atteint 29–30°C — aucune combinaison requise.","es":"Olas más pequeñas (1,4–1,7m) con vientos más ligeros y mínimas multitudes. Ideal para principiantes y longboarders. La temperatura del agua alcanza 29–30°C — sin traje de neopreno necesario.","it":"Onde più piccole (1,4–1,7m) con venti più leggeri e folla minima. Ideale per principianti e longboarder. La temperatura dell'acqua raggiunge i 29–30°C — nessuna muta necessaria.","de":"Kleinere Wellen (1,4–1,7m) mit leichteren Winden und minimalen Menschenmassen. Ideal für Anfänger und Longboarder. Wassertemperatur erreicht 29–30°C — kein Neoprenanzug nötig.","nl":"Kleinere golven (1,4–1,7m) met lichtere winden en minimale drukte. Ideaal voor beginners en longboarders. Watertemperatuur bereikt 29–30°C — geen wetsuit nodig.","ar":"أمواج أصغر (1.4-1.7م) مع رياح أخف وحشود قليلة. مثالية للمبتدئين ولوحات الجلوس الطويلة. درجة حرارة الماء تصل إلى 29-30°م بدون بدلة غوص."},
        # Comparison radar
        "cmp_lbl":    {"en":"Spot comparison","fr":"Comparaison de spots","es":"Comparación de spots","it":"Confronto spot","de":"Spot-Vergleich","nl":"Spotvergelijking","ar":"مقارنة الأماكن"},
        "cmp_h2":     {"en":"Ngor Island vs Europe's top surf spots","fr":"Ngor Island face aux meilleurs spots d'Europe","es":"Ngor Island frente a los mejores spots de Europa","it":"Ngor Island vs i migliori spot europei","de":"Ngor Island vs. Europas Top-Surfspots","nl":"Ngor Island vs. Europa's topsurf spots","ar":"جزيرة نغور مقارنةً بأفضل نقاط السيرف الأوروبية"},
        "cmp_sub":    {"en":"Six key metrics compared between Ngor Island (Dakar), Hossegor (France) and Taghazout (Morocco). Scores reflect annual averages weighted for a typical surf holiday.","fr":"Six métriques clés comparées entre l'île de Ngor (Dakar), Hossegor (France) et Taghazout (Maroc). Les scores reflètent des moyennes annuelles pondérées pour des vacances surf typiques.","es":"Seis métricas clave comparadas entre la isla de Ngor (Dakar), Hossegor (Francia) y Taghazout (Marruecos). Las puntuaciones reflejan promedios anuales ponderados para unas vacaciones surf típicas.","it":"Sei metriche chiave confrontate tra Ngor Island (Dakar), Hossegor (Francia) e Taghazout (Marocco). I punteggi riflettono medie annuali ponderate per una tipica vacanza surf.","de":"Sechs Schlüsselmetriken im Vergleich zwischen Ngor Island (Dakar), Hossegor (Frankreich) und Taghazout (Marokko). Die Scores spiegeln gewichtete Jahresdurchschnitte für einen typischen Surfurlaub wider.","nl":"Zes kernmetrics vergeleken tussen Ngor Island (Dakar), Hossegor (Frankrijk) en Taghazout (Marokko). Scores weerspiegelen gewogen jaarlijkse gemiddelden voor een typische surfvakantie.","ar":"ست مقاييس رئيسية تُقارن بين جزيرة نغور (داكار) وهوسيغور (فرنسا) وتاغازوت (المغرب). تعكس النقاط متوسطات سنوية موزونة لعطلة سيرف نموذجية."},
        "cmp_axes":   {"en":["Wave size","Wave quality","Water temp.","Consistency","Uncrowded","Sunshine"],"fr":["Taille des vagues","Qualité des vagues","Temp. eau","Régularité","Peu fréquenté","Ensoleillement"],"es":["Tamaño de ola","Calidad de ola","Temp. agua","Consistencia","Sin masificación","Horas de sol"],"it":["Dimensione onde","Qualità onde","Temp. acqua","Consistenza","Poco affollato","Ore di sole"],"de":["Wellengröße","Wellenqualität","Wassertemp.","Konsistenz","Wenig Andrang","Sonnenschein"],"nl":["Golfgrootte","Golfkwaliteit","Watertemp.","Consistentie","Weinig drukte","Zonneschijn"],"ar":["حجم الموج","جودة الموج","حرارة الماء","الاستمرارية","قلة الازدحام","أشعة الشمس"]},
        "cmp_note":   {"en":"Scores are indicative annual averages based on typical meteorological conditions for each spot. Individual sessions may vary significantly.","fr":"Les scores sont des moyennes annuelles indicatives basées sur les conditions météorologiques typiques de chaque spot. Les sessions individuelles peuvent varier sensiblement.","es":"Las puntuaciones son medias anuales indicativas basadas en las condiciones meteorológicas típicas de cada spot. Las sesiones individuales pueden variar significativamente.","it":"I punteggi sono medie annuali indicative basate sulle tipiche condizioni meteorologiche di ogni spot. Le sessioni individuali possono variare significativamente.","de":"Die Scores sind indikative Jahresdurchschnitte basierend auf typischen meteorologischen Bedingungen für jeden Spot. Einzelne Sessions können erheblich abweichen.","nl":"Scores zijn indicatieve jaargemiddelden gebaseerd op typische meteorologische condities per spot. Individuele sessies kunnen aanzienlijk variëren.","ar":"النقاط متوسطات سنوية إرشادية مبنية على الظروف الجوية النموذجية لكل موقع. قد تتفاوت الجلسات الفردية بشكل ملحوظ."},
        # Informational text
        "info_h2":    {"en":"Reading surf conditions at Ngor Island","fr":"Lire les conditions surf à l'île de Ngor","es":"Leer las condiciones de surf en la isla de Ngor","it":"Come leggere le condizioni surf a Ngor Island","de":"Surfbedingungen auf Ngor Island lesen","nl":"Surfcondities bij Ngor Island begrijpen","ar":"قراءة أحوال الأمواج في جزيرة نغور"},
        "info_p1":    {"en":"Ngor Island sits on the Cabo Verde Peninsula, exposed to Atlantic swells from both northern and southern hemispheres. This unique positioning makes it one of West Africa's most consistent surf spots, with rideable waves recorded on every single day of 2025. The surf season follows a clear rhythm: powerful North Atlantic swells from November through April drive the best surf of the year, the transition months of May and October offer solid mid-range conditions, while the calmer months of June through September bring smaller but always surfable waves with lighter winds.","fr":"L'île de Ngor est située sur la presqu'île du Cap-Vert, exposée aux houles atlantiques des deux hémisphères. Cette position unique en fait l'un des spots surf les plus réguliers d'Afrique de l'Ouest, avec des vagues surfables enregistrées chaque jour de 2025. La saison surf suit un rythme clair : les puissantes houles nord-atlantiques de novembre à avril génèrent les meilleures conditions de l'année, les mois de transition mai et octobre offrent des conditions solides intermédiaires, tandis que les mois plus calmes de juin à septembre apportent des vagues plus petites mais toujours surfables avec des vents plus légers.","es":"La isla de Ngor se encuentra en la península de Cabo Verde, expuesta a los swells atlánticos de ambos hemisferios. Esta posición única la convierte en uno de los spots de surf más consistentes de África Occidental, con olas surfeables registradas todos los días de 2025. La temporada de surf sigue un ritmo claro: los potentes swells del Atlántico Norte de noviembre a abril generan las mejores condiciones del año, los meses de transición mayo y octubre ofrecen condiciones sólidas de nivel medio, mientras que los meses más tranquilos de junio a septiembre traen olas más pequeñas pero siempre surfeables con vientos más ligeros.","it":"Ngor Island si trova sulla penisola di Capo Verde, esposta agli swell atlantici di entrambi gli emisferi. Questa posizione unica la rende uno dei punti surf più consistenti dell'Africa Occidentale, con onde navigabili registrate ogni singolo giorno del 2025. La stagione surf segue un ritmo chiaro: i potenti swell del Nord Atlantico da novembre ad aprile generano le migliori condizioni dell'anno, i mesi di transizione maggio e ottobre offrono condizioni solide di livello medio, mentre i mesi più calmi da giugno a settembre portano onde più piccole ma sempre navigabili con venti più leggeri.","de":"Ngor Island liegt auf der Halbinsel Kap Verde und ist atlantischen Swells aus beiden Hemisphären ausgesetzt. Diese einzigartige Lage macht es zu einem der konstantesten Surfspots Westafrikas, mit fahrbaren Wellen an jedem einzelnen Tag des Jahres 2025. Die Surfsaison folgt einem klaren Rhythmus: Starke Nordatlantik-Swells von November bis April erzeugen die besten Bedingungen des Jahres, die Übergangsmonate Mai und Oktober bieten solide mittlere Bedingungen, während die ruhigeren Monate Juni bis September kleinere, aber immer noch fahrbare Wellen mit leichteren Winden bringen.","nl":"Ngor Island ligt op het Kaap Verde-schiereiland, blootgesteld aan Atlantische swells vanuit beide hemisferen. Deze unieke ligging maakt het tot een van de meest consistente surfspots in West-Afrika, met surffbare golven geregistreerd op elke dag van 2025. Het surfseizoen volgt een duidelijk ritme: krachtige Noord-Atlantische swells van november tot april genereren de beste condities van het jaar, de overgangsmaanden mei en oktober bieden solide middenniveau-condities, terwijl de rustigere maanden juni tot september kleinere maar nog steeds surffbare golven brengen met lichtere winden.","ar":"تقع جزيرة نغور في شبه جزيرة رأس الأخضر، معرضة لأمواج الأطلسي من كلا نصفي الكرة الأرضية. هذا الموقع الفريد يجعلها واحدة من أكثر نقاط السيرف استمرارية في غرب أفريقيا، مع أمواج صالحة للركوب في كل يوم من أيام 2025. يتبع موسم السيرف إيقاعاً واضحاً: أمواج شمال الأطلسي القوية من نوفمبر إلى أبريل تولد أفضل الظروف، وتقدم أشهر الانتقال (مايو وأكتوبر) ظروفاً متوسطة، بينما تجلب أشهر الصيف من يونيو إلى سبتمبر أمواجاً أصغر مع رياح أخف."},
        "info_p2":    {"en":"Wave period is as important as height when reading Ngor's surf. Periods above 10 seconds signal powerful ground swell from distant North Atlantic storms, producing the long, clean walls that make Ngor Right one of West Africa's most iconic waves. Shorter periods of 6 to 9 seconds reflect local wind swell, ideal for beginners at Ngor Left. Morning sessions are consistently the cleanest: the north-northwest trade winds blow offshore at dawn before turning cross-shore by midday.","fr":"La période des vagues est aussi importante que la hauteur pour lire le surf de Ngor. Des périodes supérieures à 10 secondes signalent une houle de fond puissante provenant de tempêtes nord-atlantiques lointaines, produisant les murs longs et propres qui font de Ngor Right l'une des vagues les plus iconiques d'Afrique de l'Ouest. Des périodes plus courtes de 6 à 9 secondes reflètent une houle de vent locale, idéale pour les débutants à Ngor Left. Les sessions matinales sont systématiquement les plus propres : les alizés nord-nord-ouest soufflent offshore à l'aube avant de passer croisés vers midi.","es":"El período de las olas es tan importante como la altura para leer el surf de Ngor. Los períodos superiores a 10 segundos señalan una potente groundswell de lejanas tormentas del Atlántico Norte, produciendo las largas y limpias paredes que hacen de Ngor Right una de las olas más icónicas de África Occidental. Los períodos más cortos de 6 a 9 segundos reflejan swells de viento locales, ideales para principiantes en Ngor Left. Las sesiones matutinas son sistemáticamente las más limpias: los vientos alisios del norte-noroeste soplan offshore al amanecer antes de girar cruzados hacia el mediodía.","it":"Il periodo delle onde è importante quanto l'altezza per leggere il surf di Ngor. I periodi superiori a 10 secondi segnalano potenti ground swell da tempeste lontane del Nord Atlantico, producendo le lunghe pareti pulite che rendono Ngor Right una delle onde più iconiche dell'Africa Occidentale. I periodi più brevi da 6 a 9 secondi riflettono swell di vento locali, ideali per principianti a Ngor Left. Le sessioni mattutine sono sistematicamente le più pulite: i venti alisei da nord-nordovest soffiano offshore all'alba prima di girare trasversali verso mezzogiorno.","de":"Die Wellenperiode ist genauso wichtig wie die Höhe beim Lesen des Surfs auf Ngor. Perioden über 10 Sekunden signalisieren kraftvollen Grundswell von fernen Nordatlantikstürmen, der die langen, sauberen Wände produziert, die Ngor Right zu einer der ikonischsten Wellen Westafrikas machen. Kürzere Perioden von 6 bis 9 Sekunden spiegeln lokalen Windswell wider, ideal für Anfänger an Ngor Left. Frühsessions sind durchweg die saubersten: Die Nord-Nordwest-Passatwinde wehen bei Tagesanbruch offshore bevor sie gegen Mittag quer drehen.","nl":"De golfperiode is net zo belangrijk als de hoogte bij het lezen van de surf op Ngor. Perioden boven 10 seconden signaleren krachtige ground swell van verre Noord-Atlantische stormen, die de lange, schone muren produceren die Ngor Right tot een van de meest iconische golven van West-Afrika maken. Kortere perioden van 6 tot 9 seconden weerspiegelen lokale windswell, ideaal voor beginners bij Ngor Left. Ochtendsessies zijn consequent het schoonst: de noord-noordwestelijke passaatwinden waaien bij dageraad offshore voordat ze rond het middaguur dwars draaien.","ar":"الفترة الزمنية للموج لا تقل أهمية عن الارتفاع عند قراءة سيرف نغور. تشير الفترات التي تتجاوز 10 ثوانٍ إلى حوله قوية من عواصف بعيدة في شمال الأطلسي، مما ينتج الجدران الطويلة والنظيفة التي تجعل نغور رايت واحدة من أكثر الأمواج أيقونية في غرب أفريقيا. تعكس الفترات الأقصر من 6 إلى 9 ثوانٍ حوله رياح محلية، مثالية للمبتدئين في نغور ليفت. الجلسات الصباحية هي الأنظف باستمرار: تهب الرياح التجارية الشمالية الشمالية الغربية offshore عند الفجر قبل أن تتحول عرضية بحلول الظهيرة."},
        "cta_h2":     {"en":"Ready to surf these conditions?","fr":"Prêt à surfer ces conditions ?","es":"¿Listo para surfear estas condiciones?","it":"Pronto a surfare queste condizioni?","de":"Bereit, diese Bedingungen zu surfen?","nl":"Klaar om deze condities te surfen?","ar":"مستعد لركوب هذه الأمواج؟"},
        "cta_p":      {"en":"Our coaches choose the best spot each morning based on the live forecast. Two sessions a day, warm water, uncrowded lineups.","fr":"Nos coachs choisissent le meilleur spot chaque matin selon les prévisions en direct. Deux sessions par jour, eau chaude, lineups déserts.","es":"Nuestros coaches eligen el mejor spot cada mañana según las previsiones en vivo. Dos sesiones al día, agua cálida, lineups sin gente.","it":"I nostri coach scelgono il posto migliore ogni mattina in base alle previsioni in diretta. Due sessioni al giorno, acqua calda, lineup deserti.","de":"Unsere Coaches wählen jeden Morgen den besten Spot basierend auf der Live-Vorhersage. Zwei Sessions täglich, warmes Wasser, leere Lineups.","nl":"Onze coaches kiezen elke ochtend de beste spot op basis van de live-voorspelling. Twee sessies per dag, warm water, lege lineups.","ar":"يختار مدربونا أفضل موقع كل صباح بناءً على التوقعات المباشرة. جلستان يومياً، ماء دافئ، لاين أب فارغة."},
        "book_btn":   {"en":"Book Your Stay","fr":"Réserver mon séjour","es":"Reservar mi estancia","it":"Prenota il soggiorno","de":"Aufenthalt buchen","nl":"Verblijf boeken","ar":"احجز إقامتك"},
        "surf_btn":   {"en":"Surf coaching","fr":"Coaching surf","es":"Coaching surf","it":"Coaching surf","de":"Surf-Coaching","nl":"Surfcoaching","ar":"تدريب السيرف"},
        "load_err":   {"en":"Live conditions temporarily unavailable.","fr":"Conditions en direct temporairement indisponibles.","es":"Condiciones en vivo temporalmente no disponibles.","it":"Condizioni in tempo reale temporaneamente non disponibili.","de":"Live-Bedingungen vorübergehend nicht verfügbar.","nl":"Live condities tijdelijk niet beschikbaar.","ar":"الأحوال المباشرة غير متاحة مؤقتاً."},
        "powered":    {"en":"Wave data: Open-Meteo Marine API (free, open source)","fr":"Données vagues : Open-Meteo Marine API (gratuit, open source)","es":"Datos olas: Open-Meteo Marine API (gratis, open source)","it":"Dati onde: Open-Meteo Marine API (gratuita, open source)","de":"Wellendaten: Open-Meteo Marine API (kostenlos, Open Source)","nl":"Golfdata: Open-Meteo Marine API (gratis, open source)","ar":"بيانات الأمواج: Open-Meteo Marine API (مجاني، مفتوح المصدر)"},
        "months":     {"en":["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],"fr":["Jan","Fév","Mar","Avr","Mai","Jun","Jul","Aoû","Sep","Oct","Nov","Déc"],"es":["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"],"it":["Gen","Feb","Mar","Apr","Mag","Giu","Lug","Ago","Set","Ott","Nov","Dic"],"de":["Jan","Feb","Mär","Apr","Mai","Jun","Jul","Aug","Sep","Okt","Nov","Dez"],"nl":["Jan","Feb","Mar","Apr","Mei","Jun","Jul","Aug","Sep","Okt","Nov","Dec"],"ar":["يناير","فبراير","مارس","أبريل","مايو","يونيو","يوليو","أغسطس","سبتمبر","أكتوبر","نوفمبر","ديسمبر"]},
    }

    def g(k): return T[k].get(lang, T[k]["en"])

    import json as _j
    hist_json   = _j.dumps(history, ensure_ascii=False, separators=(',',':'))
    months_json = _j.dumps(g("months"), ensure_ascii=False, separators=(',',':'))
    axes_json   = _j.dumps(g("cmp_axes"), ensure_ascii=False, separators=(',',':'))

    ICO_WAVE   = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12c2-3 4-3 6 0s4 3 6 0 4-3 6 0"/><path d="M2 17c2-3 4-3 6 0s4 3 6 0 4-3 6 0"/><path d="M7 4l3-3 4 3"/><path d="M14 4v3"/></svg>'
    ICO_CLK    = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 3"/></svg>'
    ICO_DIR    = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 3v2M12 19v2M3 12h2M19 12h2"/><path d="M12 8l-2 8 2-2 2 2z" fill="currentColor" stroke="none"/></svg>'
    ICO_SWELL  = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M2 10c2-3 4-3 6 0s4 3 6 0 4-3 6 0"/><path d="M2 16c2-3 4-3 6 0s4 3 6 0 4-3 6 0"/></svg>'
    ICO_WIND   = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M9.59 4.59A2 2 0 1111 8H2"/><path d="M12.59 19.41A2 2 0 1014 16H2"/><path d="M17.5 8A2.5 2.5 0 1120 10.5H2"/></svg>'
    ICO_TEMP   = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M14 14.76V3.5a2.5 2.5 0 00-5 0v11.26a4.5 4.5 0 105 0z"/></svg>'
    ICO_STAR   = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>'

    def stat(k, ico, lbl, col):
        return (f'<div class="sc-stat sc-stat-{k}">'
                f'<div class="sc-stat-icon" style="color:{col}">{ico}</div>'
                f'<div class="sc-stat-val" id="sc-v-{k}">...</div>'
                f'<div class="sc-stat-lbl">{lbl}</div></div>')

    seas_cards = f"""
      <div class="sc-seas-grid">
        <div class="sc-seas-card sc-seas-peak">
          <div class="sc-seas-badge">{escape(g("seas_peak_t"))}</div>
          <div class="sc-seas-months">{escape(g("seas_peak_m"))}</div>
          <p>{escape(g("seas_peak_p"))}</p>
        </div>
        <div class="sc-seas-card sc-seas-trans">
          <div class="sc-seas-badge">{escape(g("seas_trans_t"))}</div>
          <div class="sc-seas-months">{escape(g("seas_trans_m"))}</div>
          <p>{escape(g("seas_trans_p"))}</p>
        </div>
        <div class="sc-seas-card sc-seas-sum">
          <div class="sc-seas-badge">{escape(g("seas_sum_t"))}</div>
          <div class="sc-seas-months">{escape(g("seas_sum_m"))}</div>
          <p>{escape(g("seas_sum_p"))}</p>
        </div>
      </div>"""

    html = page_head(g("title"), g("meta"), lang, "surf-conditions", IMGS["surf"])
    html += build_nav("surf-conditions", lang)
    html += f"""
<main>
  <header class="main-hero" style="background-image:url('{IMGS["surf"]}')" role="banner">
    <div class="main-hero-inner">
      <div class="main-hero-eyebrow">
        <span class="main-hero-dot"></span>
        <span>Ngor Surfcamp Teranga</span>
      </div>
      <h1 class="main-hero-h1">{escape(g("h1"))}</h1>
      <p class="main-hero-tagline">{escape(g("sub"))}</p>
      <div class="main-hero-actions">
        <a href="{book_href}" class="btn btn-fire btn-lg">{escape(g("book_btn"))}</a>
        <a href="#live-conditions" class="btn btn-outline-white btn-lg">&#8964;</a>
      </div>
    </div>
  </header>

  {wave_top(_BG_LIGHT, _BG_NAVY)}
  <!-- ── Live conditions ── -->
  <section id="live-conditions" class="section sec-light">
    <div class="container">
      <div class="sc-now-label reveal"><span class="s-label sc-pulse-dot">{escape(g("now_lbl"))}</span></div>
      <div class="sc-stats-grid reveal">
        {stat("wave",  ICO_WAVE,  escape(g("wave_h")),    "var(--ocean)")}
        {stat("period",ICO_CLK,   escape(g("period")),    "var(--navy)")}
        {stat("dir",   ICO_DIR,   escape(g("direction")), "var(--fire)")}
        {stat("swell", ICO_SWELL, escape(g("swell_h")),   "var(--ocean)")}
        {stat("wind",  ICO_WIND,  escape(g("wind_lbl")),  "var(--navy)")}
        {stat("temp",  ICO_TEMP,  escape(g("water_t")),   "var(--fire)")}
        {stat("qual",  ICO_STAR,  escape(g("quality")),   "var(--fire)")}
      </div>
      <div id="sc-ctx" class="sc-ctx-text reveal" aria-live="polite"></div>
      <p class="sc-powered"><a href="https://open-meteo.com/" target="_blank" rel="noopener">{escape(g("powered"))}</a></p>
    </div>
  </section>
  {wave_bottom(_BG_LIGHT, _BG_WHITE)}

  <!-- ── 16-day forecast ── -->
  <section class="section">
    <div class="container">
      <div style="text-align:center;margin-bottom:28px" class="reveal">
        <span class="s-label">{escape(g("fc_lbl"))}</span>
        <p class="sc-fc-note">{escape(g("fc_note"))}</p>
      </div>
      <div id="sc-strip" class="sc-forecast-strip reveal"><div class="fc-loading"><div class="fc-spinner"></div></div></div>
    </div>
  </section>

  {wave_top(_BG_LIGHT, _BG_WHITE)}
  <!-- ── Season guide ── -->
  <section class="section sec-light">
    <div class="container">
      <div style="text-align:center;margin-bottom:32px" class="reveal">
        <span class="s-label">{escape(g("seas_lbl"))}</span>
      </div>
      {seas_cards}
    </div>
  </section>
  {wave_bottom(_BG_LIGHT, _BG_WHITE)}

  <!-- ── Historical 2025 charts ── -->
  <section class="section">
    <div class="container">
      <div style="text-align:center;margin-bottom:28px" class="reveal">
        <span class="s-label">{escape(g("hist_lbl"))}</span>
        <h2 class="s-title">{escape(g("hist_h2"))}</h2>
        <p style="font-size:15px;color:var(--muted);max-width:680px;margin:12px auto 0;line-height:1.7">{escape(g("hist_sub"))}</p>
      </div>
      <div class="sc-tabs reveal">
        <button class="sc-tab active" data-panel="all">{escape(g("month_lbl"))}</button>
        <button class="sc-tab" data-panel="temp">{escape(g("temp_lbl"))}</button>
        <button class="sc-tab" data-panel="beg">{escape(g("lev_beg"))}</button>
        <button class="sc-tab" data-panel="int">{escape(g("lev_int"))}</button>
        <button class="sc-tab" data-panel="adv">{escape(g("lev_adv"))}</button>
      </div>
      <div class="sc-chart-wrap reveal">
        <div id="sc-p-all"><canvas id="sc-chart-all" height="280"></canvas></div>
        <div id="sc-p-temp" style="display:none"><canvas id="sc-chart-temp" height="240"></canvas></div>
        <div id="sc-p-beg"  style="display:none"><canvas id="sc-chart-beg"  height="240"></canvas></div>
        <div id="sc-p-int"  style="display:none"><canvas id="sc-chart-int"  height="240"></canvas></div>
        <div id="sc-p-adv"  style="display:none"><canvas id="sc-chart-adv"  height="240"></canvas></div>
      </div>
    </div>
  </section>

  {wave_top(_BG_LIGHT, _BG_WHITE)}
  <!-- ── Spot comparison radar ── -->
  <section class="section sec-light">
    <div class="container">
      <div style="text-align:center;margin-bottom:28px" class="reveal">
        <span class="s-label">{escape(g("cmp_lbl"))}</span>
        <h2 class="s-title">{escape(g("cmp_h2"))}</h2>
        <p style="font-size:15px;color:var(--muted);max-width:680px;margin:12px auto 0;line-height:1.7">{escape(g("cmp_sub"))}</p>
      </div>
      <div class="sc-radar-wrap reveal">
        <canvas id="sc-chart-radar" style="max-height:440px"></canvas>
      </div>
      <p class="sc-radar-note reveal">{escape(g("cmp_note"))}</p>
    </div>
  </section>
  {wave_bottom(_BG_LIGHT, _BG_WHITE)}

  <!-- ── How data works ── -->
  <section class="section">
    <div class="container">
      <div class="sc-how-grid reveal">
        <div class="sc-how-card">
          <div class="sc-how-icon" style="color:var(--fire)">{ICO_WAVE}</div>
          <h3>{escape(g("how_live"))}</h3>
          <p>{escape(g("how_live_p"))}</p>
        </div>
        <div class="sc-how-card">
          <div class="sc-how-icon" style="color:var(--ocean)">{ICO_CLK}</div>
          <h3>{escape(g("how_fc"))}</h3>
          <p>{escape(g("how_fc_p"))}</p>
        </div>
        <div class="sc-how-card">
          <div class="sc-how-icon" style="color:var(--navy)">{ICO_SWELL}</div>
          <h3>{escape(g("how_hist"))}</h3>
          <p>{escape(g("how_hist_p"))}</p>
        </div>
      </div>
    </div>
  </section>

  <!-- ── Informational text ── -->
  {wave_top(_BG_LIGHT, _BG_WHITE)}
  <section class="section sec-light">
    <div class="container">
      <div class="sc-text-block reveal" style="max-width:820px">
        <h2 class="s-title" style="margin-bottom:24px">{escape(g("info_h2"))}</h2>
        <p class="surf-story-p">{escape(g("info_p1"))}</p>
        <p class="surf-story-p" style="margin-top:20px">{escape(g("info_p2"))}</p>
        <div style="margin-top:36px;display:flex;gap:14px;flex-wrap:wrap">
          <a href="{surf_href}" class="btn btn-deep">{escape(g("surf_btn"))}</a>
          <a href="{book_href}" class="btn btn-fire">{escape(g("book_btn"))}</a>
        </div>
      </div>
    </div>
  </section>
  {wave_bottom(_BG_LIGHT, _BG_NAVY)}

  <!-- ── CTA ── -->
  <div class="cta-band">
    <div class="container">
      <h2>{escape(g("cta_h2"))}</h2>
      <h3 style="font-size:20px;font-weight:300;opacity:.82;margin-bottom:36px">{escape(g("cta_p"))}</h3>
      <div class="cta-btns">
        <a href="{book_href}" class="btn btn-fire btn-lg">{escape(g("book_btn"))}</a>
        <a href="https://wa.me/221789257025" target="_blank" rel="noopener" class="btn btn-glass btn-lg"><span style="width:18px;height:18px;display:inline-flex">{WA_ICO}</span> WhatsApp</a>
      </div>
    </div>
  </div>
</main>

<script>
(function(){{
  var HIST={hist_json};
  var MON={months_json};
  var AXES={axes_json};
  var DIRS=['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW'];
  var LI=['en','fr','es','it','de','nl','ar'];
  var LANG=document.documentElement.lang.split('-')[0]||'en';
  function ddir(d){{return DIRS[Math.round(d/22.5)%16]||'N';}}
  function r1(v){{return Math.round(v*10)/10;}}
  function set(id,v){{var e=document.getElementById(id);if(e)e.textContent=v;}}
  function tl(arr){{return arr[LI.indexOf(LANG)]||arr[0];}}
  function qScore(h,p){{return Math.min(10,Math.round((Math.min(h/3*7,8)+(p>10?2:p>8?1:0))*10)/10);}}
  function qLabel(s){{
    var v=s>=7?['Excellent','Excellent','Excelente','Eccellente','Ausgezeichnet','Uitstekend','ممتاز']:
           s>=5?['Good','Bon','Bueno','Buono','Gut','Goed','جيد']:
           s>=3?['Fair','Correct','Regular','Discreto','Mäßig','Redelijk','معقول']:
                ['Small','Faible','Pequeño','Piccolo','Gering','Klein','صغير'];
    return tl(v);
  }}

  /* ── 1. Live fetch ── */
  var mURL='https://marine-api.open-meteo.com/v1/marine?latitude=14.75&longitude=-17.51'+
    '&current=wave_height,wave_direction,wave_period,swell_wave_height'+
    '&daily=wave_height_max,wave_period_max,wind_wave_height_max'+
    '&timezone=Africa%2FDakar&forecast_days=16';
  var wURL='https://api.open-meteo.com/v1/forecast?latitude=14.75&longitude=-17.51'+
    '&current=wind_speed_10m,wind_direction_10m,temperature_2m'+
    '&daily=wind_speed_10m_max,wind_direction_10m_dominant'+
    '&timezone=Africa%2FDakar&forecast_days=16';

  Promise.all([fetch(mURL).then(function(r){{return r.json();}}),fetch(wURL).then(function(r){{return r.json();}})])
  .then(function(res){{
    var m=res[0],w=res[1];
    var c=m.current||{{}},wc=w.current||{{}};
    var wh=r1(c.wave_height||0),wp=r1(c.wave_period||0),wd=ddir(c.wave_direction||0);
    var sh=r1(c.swell_wave_height||0);
    var ws=Math.round((wc.wind_speed_10m||0)/1.852),wdw=ddir(wc.wind_direction_10m||0);
    var wt=wc.temperature_2m?Math.round(wc.temperature_2m)+'°C':'--';
    var qs=qScore(c.wave_height||0,c.wave_period||0),ql=qLabel(qs);
    set('sc-v-wave',wh+'m'); set('sc-v-period',wp+'s'); set('sc-v-dir',wd);
    set('sc-v-swell',sh+'m'); set('sc-v-wind',ws+'kt · '+wdw);
    set('sc-v-temp',wt); set('sc-v-qual',qs+' / 10');

    /* Quality colour on qual card */
    var qCard=document.querySelector('.sc-stat-qual');
    if(qCard)qCard.style.borderTop='3px solid '+(qs>=7?'var(--ocean)':qs>=5?'var(--fire)':'rgba(10,37,64,.15)');

    /* Context sentence */
    var lvl=c.wave_height>2?tl(['advanced surfers','surfeurs avancés','surfistas avanzados','surfisti avanzati','Profis','gevorderde surfers','المتقدمين']):
            c.wave_height>1?tl(['all levels','tous niveaux','todos los niveles','tutti i livelli','alle Level','alle niveaus','جميع المستويات']):
            tl(['beginners','débutants','principiantes','principianti','Anfänger','beginners','المبتدئين']);
    var CTPL={{
      en:'Waves at '+wh+'m with a '+wp+'s period from '+wd+'. The '+sh+'m swell and '+ws+'kt winds create a '+ql.toLowerCase()+' surf day, best suited for '+lvl+'.',
      fr:'Vagues à '+wh+'m avec une période de '+wp+'s en provenance du '+wd+'. La houle de '+sh+'m et le vent de '+ws+' nœuds créent une journée surf '+ql.toLowerCase()+', idéale pour les '+lvl+'.',
      es:'Olas de '+wh+'m con un período de '+wp+'s desde '+wd+'. La houle de '+sh+'m y los vientos de '+ws+' nudos crean un día surf '+ql.toLowerCase()+', indicado para '+lvl+'.',
      it:'Onde a '+wh+'m con un periodo di '+wp+'s da '+wd+'. La mareggiata di '+sh+'m e i venti di '+ws+' nodi creano una giornata surf '+ql.toLowerCase()+', indicata per '+lvl+'.',
      de:'Wellen bei '+wh+'m mit einer '+wp+'s Periode aus '+wd+'. Die '+sh+'m Dünung und '+ws+' Knoten Wind erzeugen einen '+ql.toLowerCase()+' Surftag, optimal für '+lvl+'.',
      nl:'Golven van '+wh+'m met een periode van '+wp+'s vanuit '+wd+'. De '+sh+'m deining en '+ws+' knopen wind creëren een '+ql.toLowerCase()+' surfdag, ideaal voor '+lvl+'.',
      ar:'أمواج '+wh+'م بفترة '+wp+'ث من '+wd+'. تخلق الحوله '+sh+'م والرياح '+ws+' عقدة يوم سيرف '+ql+' مناسب لـ'+lvl+'.'
    }};
    var ctx=document.getElementById('sc-ctx');
    if(ctx)ctx.textContent=CTPL[LANG]||CTPL.en;

    /* ── 2. Forecast strip ── */
    var strip=document.getElementById('sc-strip');
    if(strip&&m.daily&&m.daily.time){{
      var days=m.daily.time,wh2=m.daily.wave_height_max,wp2=m.daily.wave_period_max;
      var ws2=w.daily&&w.daily.wind_speed_10m_max,wd2=w.daily&&w.daily.wind_direction_10m_dominant;
      var out='<div class="sc-fc-scroll-wrap"><div class="sc-fc-row">';
      for(var i=0;i<Math.min(16,days.length);i++){{
        var d=new Date(days[i]+'T12:00:00');
        var dn=d.toLocaleDateString(undefined,{{weekday:'short'}}).toUpperCase();
        var dm=d.toLocaleDateString(undefined,{{day:'numeric',month:'short'}});
        var h2=wh2[i]||0,p2=wp2?wp2[i]||0:0;
        var ws3=ws2?Math.round((ws2[i]||0)/1.852):0;
        var wd3=wd2?ddir(wd2[i]||0):'';
        var qs2=qScore(h2,p2);
        var cls=qs2>=7?'sc-fc-good':qs2>=4?'sc-fc-fair':'sc-fc-small';
        var barH=Math.max(6,Math.round(h2/3.5*100));
        var acc=i<5?'':' sc-fc-dim';
        out+='<div class="sc-fc-card '+cls+acc+'"><div class="sc-fc-day">'+dn+'</div><div class="sc-fc-date">'+dm+'</div>';
        out+='<div class="sc-fc-bar-wrap"><div class="sc-fc-bar" style="height:'+barH+'%"></div></div>';
        out+='<div class="sc-fc-wh">'+r1(h2)+'m</div><div class="sc-fc-wind">'+ws3+'kt '+wd3+'</div>';
        out+=(i<5?'<div class="sc-fc-acc-badge">'+(i===0?tl(['today','auj.','hoy','oggi','heute','vandaag','اليوم']):'')+'</div>':'');
        out+='</div>';
      }}
      strip.innerHTML=out+'</div></div>';
    }}
  }}).catch(function(){{
    var e=document.getElementById('sc-strip');
    if(e)e.innerHTML='<p class="sc-err">{escape(g("load_err"))}</p>';
  }});

  /* ── 3. Charts (Chart.js) ── */
  function loadCJS(cb){{if(window.Chart){{cb();return;}}var s=document.createElement('script');s.src='https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js';s.onload=cb;document.head.appendChild(s);}}

  loadCJS(function(){{
    var keys=Object.keys(HIST).sort();
    var labels=keys.map(function(k,i){{return MON[i]||k;}});
    var waveD  =keys.map(function(k){{return HIST[k].wave_h;}});
    var windD  =keys.map(function(k){{return HIST[k].wind_s;}});
    var periodD=keys.map(function(k){{return HIST[k].wave_p;}});
    var tempD  =keys.map(function(k){{return HIST[k].temp;}});
    var NAVY='#0a2540',FIRE='#ff5a1f',OCEAN='#0ea5e9',AMBER='#f59e0b',GRID='rgba(10,37,64,0.08)';
    var FF="'Raleway','Inter',system-ui,sans-serif";
    var baseFont={{family:FF,size:12}};
    var tickOpts={{font:baseFont,color:NAVY}};

    function mkOpts(y1lbl,y2lbl){{
      return {{
        responsive:true,maintainAspectRatio:true,
        interaction:{{mode:'index',intersect:false}},
        plugins:{{
          legend:{{position:'top',labels:{{font:baseFont,color:NAVY,boxWidth:12,padding:16}}}},
          tooltip:{{backgroundColor:NAVY,titleFont:{{family:FF,weight:'bold'}},bodyFont:{{family:FF}},padding:10,cornerRadius:8}}
        }},
        scales:{{
          x:{{grid:{{color:GRID}},ticks:tickOpts}},
          y:{{grid:{{color:GRID}},ticks:Object.assign({{}},tickOpts,{{callback:function(v){{return v+(y1lbl||'');}}}})}},
          ...(y2lbl?{{y2:{{position:'right',grid:{{drawOnChartArea:false}},ticks:Object.assign({{}},{{color:FIRE}},{{callback:function(v){{return v+y2lbl;}}}})}}}}:{{}})
        }}
      }};
    }}

    /* Chart 1: Overview — wave + wind + period */
    (function(){{
      var opts=mkOpts('m','kt');
      opts.scales.y3={{position:'right',grid:{{drawOnChartArea:false}},ticks:Object.assign({{}},{{color:AMBER}},{{callback:function(v){{return v+'s';}}}})}};;
      new Chart(document.getElementById('sc-chart-all'),{{
        type:'bar',
        data:{{labels:labels,datasets:[
          {{label:'{escape(g("chart_wave"))}',data:waveD,backgroundColor:OCEAN+'99',borderColor:OCEAN,borderWidth:2,borderRadius:5,order:3}},
          {{label:'{escape(g("chart_wind"))}',data:windD,type:'line',borderColor:FIRE,backgroundColor:FIRE+'22',fill:true,tension:0.4,pointRadius:5,pointBackgroundColor:FIRE,borderWidth:2,yAxisID:'y2',order:1}},
          {{label:'{escape(g("chart_period"))}',data:periodD,type:'line',borderColor:AMBER,backgroundColor:'transparent',tension:0.4,pointRadius:4,pointBackgroundColor:AMBER,borderWidth:2,borderDash:[5,3],yAxisID:'y3',order:2}},
        ]}},options:opts
      }});
    }})();

    /* Chart 2: Water temperature */
    new Chart(document.getElementById('sc-chart-temp'),{{
      type:'line',
      data:{{labels:labels,datasets:[{{
        label:'{escape(g("chart_temp"))}',
        data:tempD,
        borderColor:FIRE,
        backgroundColor:FIRE+'22',
        fill:true,tension:0.4,
        pointRadius:6,pointBackgroundColor:FIRE,pointBorderColor:'#fff',pointBorderWidth:2,
        borderWidth:2.5
      }}]}},
      options:{{
        responsive:true,maintainAspectRatio:true,
        interaction:{{mode:'index',intersect:false}},
        plugins:{{legend:{{labels:{{font:baseFont,color:NAVY}}}},tooltip:{{backgroundColor:NAVY,titleFont:{{family:FF,weight:'bold'}},bodyFont:{{family:FF}},padding:10,cornerRadius:8}}}},
        scales:{{
          x:{{grid:{{color:GRID}},ticks:tickOpts}},
          y:{{grid:{{color:GRID}},ticks:Object.assign({{}},tickOpts,{{callback:function(v){{return v+'°C';}}}}),min:20,max:35}}
        }}
      }}
    }});

    /* Level score helper */
    function lScore(h,p,lev){{
      if(lev==='beg'){{if(h<0.4)return 1;if(h<=1.0)return 7+(p>8?2:0);if(h<=1.6)return 5;return 2;}}
      if(lev==='int'){{if(h<0.8)return 2;if(h<=1.5)return 7+(p>9?1:0);if(h<=2.5)return 9+(p>10?1:0);return 5;}}
      if(h<1.5)return 2;if(h<=2.2)return 7+(p>10?1:0);if(h<=3.5)return 10;return 8;
    }}

    /* Charts 3–5: Level scores with data annotation */
    function scoreChart(id,lev,col){{
      var scores=keys.map(function(k){{return Math.min(10,lScore(HIST[k].wave_h,HIST[k].wave_p,lev));}});
      var bgc=scores.map(function(s){{return s>=8?col+'dd':s>=5?col+'88':col+'33';}});
      var opts=mkOpts('');
      opts.plugins.legend={{display:false}};
      opts.plugins.tooltip.callbacks={{label:function(ctx){{return ' '+ctx.parsed.y+' / 10';}}}};
      opts.scales.y=Object.assign({{}},opts.scales.y,{{min:0,max:10,ticks:Object.assign({{}},tickOpts,{{stepSize:2}})}});
      new Chart(document.getElementById(id),{{
        type:'bar',
        data:{{labels:labels,datasets:[{{
          label:'{escape(g("score_lbl"))}',data:scores,
          backgroundColor:bgc,borderColor:col,borderWidth:1.5,borderRadius:6,
        }}]}},
        options:opts
      }});
    }}
    scoreChart('sc-chart-beg','beg',OCEAN);
    scoreChart('sc-chart-int','int',FIRE);
    scoreChart('sc-chart-adv','adv',NAVY);

    /* Chart 6: Radar comparison */
    (function(){{
      var NGOR   =[7,7,9,10,10,9]; /* wave size, quality, water temp, consistency, uncrowded, sunshine */
      var FRANCE =[8,9, 4, 6, 4,7];
      var MOROCCO=[7,8, 7, 7, 6,9];
      var r_opts={{
        responsive:true,maintainAspectRatio:true,
        interaction:{{mode:'point'}},
        plugins:{{
          legend:{{position:'top',labels:{{font:baseFont,color:NAVY,boxWidth:12,padding:16}}}},
          tooltip:{{backgroundColor:NAVY,titleFont:{{family:FF,weight:'bold'}},bodyFont:{{family:FF}},padding:10,cornerRadius:8,callbacks:{{label:function(ctx){{return ' '+ctx.label+' : '+ctx.raw+' / 10';}}}}}}
        }},
        scales:{{r:{{
          min:0,max:10,
          ticks:{{stepSize:2,font:baseFont,color:NAVY,backdropColor:'transparent',showLabelBackdrop:false}},
          grid:{{color:GRID}},
          angleLines:{{color:GRID}},
          pointLabels:{{font:Object.assign({{}},baseFont,{{size:13,weight:'600'}}),color:NAVY}}
        }}}}
      }};
      new Chart(document.getElementById('sc-chart-radar'),{{
        type:'radar',
        data:{{
          labels:AXES,
          datasets:[
            {{label:'Ngor Island (Dakar)',data:NGOR,backgroundColor:OCEAN+'33',borderColor:OCEAN,borderWidth:2.5,pointBackgroundColor:OCEAN,pointRadius:5}},
            {{label:'Hossegor (France)',  data:FRANCE, backgroundColor:FIRE+'22',borderColor:FIRE,  borderWidth:2,  pointBackgroundColor:FIRE,  pointRadius:4,borderDash:[4,3]}},
            {{label:'Taghazout (Morocco)',data:MOROCCO,backgroundColor:'#a855f733',borderColor:'#a855f7',borderWidth:2,pointBackgroundColor:'#a855f7',pointRadius:4,borderDash:[2,4]}},
          ]
        }},
        options:r_opts
      }});
    }})();

    /* Tab switching */
    document.querySelectorAll('.sc-tab').forEach(function(btn){{
      btn.addEventListener('click',function(){{
        var p=this.dataset.panel;
        document.querySelectorAll('.sc-tab').forEach(function(b){{b.classList.remove('active');}});
        this.classList.add('active');
        ['all','temp','beg','int','adv'].forEach(function(id){{
          var el=document.getElementById('sc-p-'+id);
          if(el)el.style.display=id===p?'block':'none';
        }});
      }});
    }});
  }});
}})();
</script>"""
    html += build_footer(lang)
    html += page_close()
    return html


def build_privacy_policy(lang):
    pfx      = LANG_PFX[lang]
    slug     = SLUG[lang]["privacy-policy"]
    book_href = f"{pfx}/{SLUG[lang]['booking']}/"

    TITLES = {
        "en": "Privacy Policy | Ngor Surfcamp Teranga",
        "fr": "Politique de confidentialité | Ngor Surfcamp Teranga",
        "es": "Política de privacidad | Ngor Surfcamp Teranga",
        "it": "Informativa sulla privacy | Ngor Surfcamp Teranga",
        "de": "Datenschutzrichtlinie | Ngor Surfcamp Teranga",
        "nl": "Privacybeleid | Ngor Surfcamp Teranga",
        "ar": "سياسة الخصوصية | Ngor Surfcamp Teranga",
    }
    METAS = {
        "en": "Privacy Policy for Ngor Surfcamp Teranga. How we collect, use and protect your personal data.",
        "fr": "Politique de confidentialité de Ngor Surfcamp Teranga. Comment nous collectons, utilisons et protégeons vos données personnelles.",
        "es": "Política de privacidad de Ngor Surfcamp Teranga. Cómo recopilamos, usamos y protegemos sus datos personales.",
        "it": "Informativa sulla privacy di Ngor Surfcamp Teranga. Come raccogliamo, utilizziamo e proteggiamo i tuoi dati personali.",
        "de": "Datenschutzrichtlinie von Ngor Surfcamp Teranga. Wie wir Ihre personenbezogenen Daten erheben, verwenden und schützen.",
        "nl": "Privacybeleid van Ngor Surfcamp Teranga. Hoe wij uw persoonlijke gegevens verzamelen, gebruiken en beschermen.",
        "ar": "سياسة الخصوصية لـ Ngor Surfcamp Teranga. كيف نجمع بياناتك الشخصية ونستخدمها ونحميها.",
    }
    H1S = {
        "en": "Privacy Policy",
        "fr": "Politique de confidentialité",
        "es": "Política de privacidad",
        "it": "Informativa sulla privacy",
        "de": "Datenschutzrichtlinie",
        "nl": "Privacybeleid",
        "ar": "سياسة الخصوصية",
    }
    UPDATED = {
        "en": "Last updated: October 01, 2025",
        "fr": "Dernière mise à jour : 1er octobre 2025",
        "es": "Última actualización: 1 de octubre de 2025",
        "it": "Ultimo aggiornamento: 1 ottobre 2025",
        "de": "Zuletzt aktualisiert: 1. Oktober 2025",
        "nl": "Laatste update: 1 oktober 2025",
        "ar": "آخر تحديث: 1 أكتوبر 2025",
    }

    CONTENT = {
        "en": """
<p><strong>NGOR SURF CAMP</strong> (hereinafter referred to as "we", "our" or "the Company") values the privacy of its visitors and customers. This Privacy Policy describes how we collect, use, store and protect your personal information when you visit our website <a href="https://www.surfcampsenegal.com/">https://www.surfcampsenegal.com/</a>.</p>

<h2>1. Information We Collect</h2>
<p>We may collect the following types of personal data:</p>
<ul>
  <li><strong>Identification information:</strong> name, email address, phone number, postal address.</li>
  <li><strong>Booking and payment information:</strong> details required to process reservations and payments.</li>
  <li><strong>Technical data:</strong> IP address, device type, browser, browsing behaviour, pages visited.</li>
  <li><strong>Voluntary information</strong> you provide through contact forms, newsletters, reviews, etc.</li>
</ul>

<h2>2. How We Collect Your Information</h2>
<p>We collect information when:</p>
<ul>
  <li>You make a booking or contact us through our forms.</li>
  <li>You subscribe to our newsletter.</li>
  <li>You complete a payment through our secure payment providers.</li>
  <li>Cookies and analytics tools (such as Google Analytics) track your navigation on our website.</li>
</ul>

<h2>3. Purpose of Data Collection</h2>
<p>Your personal information is collected and used for:</p>
<ul>
  <li>Processing reservations and providing our services.</li>
  <li>Communicating important information regarding your stay.</li>
  <li>Customer support and service follow-up.</li>
  <li>Sending promotional offers and newsletters (if you have consented).</li>
  <li>Compliance with applicable legal and regulatory obligations.</li>
</ul>

<h2>4. Data Storage, Sharing and Security</h2>
<p>Your personal data is securely stored on our technical providers' servers. We only share your information with trusted third-party service providers (e.g., payment processors, hosting providers, email services) as required to deliver our services. Data may be disclosed if required by law or to respond to legal requests.</p>

<h2>5. Communication with Users</h2>
<p>We may contact you by email, phone, SMS, or postal mail to:</p>
<ul>
  <li>Confirm and manage your bookings.</li>
  <li>Provide updates or practical information regarding your stay.</li>
  <li>Send marketing and promotional content (if you have agreed).</li>
</ul>

<h2>6. Cookies and Tracking Tools</h2>
<p>Our website uses cookies and similar technologies in order to:</p>
<ul>
  <li>Improve site performance and navigation.</li>
  <li>Analyse traffic and visitor behaviour.</li>
  <li>Personalise content and offers.</li>
</ul>
<p>You may configure your browser to refuse cookies or to alert you when cookies are being used.</p>

<h2>7. Withdrawing Consent</h2>
<p>You may at any time:</p>
<ul>
  <li>Request access, correction, or deletion of your personal data.</li>
  <li>Withdraw your consent for marketing communications.</li>
</ul>
<p>To exercise your rights, please contact us at:<br>
<a href="mailto:fundistributionbws@gmail.com">fundistributionbws@gmail.com</a><br>
+221 78 925 70 25<br>
NGOR SURF CAMP – DKR 2025 A 28, Pikine Cité Baila Fall, Parcelle N° 49, Senegal</p>

<h2>8. Data Retention</h2>
<p>We keep your personal data only for as long as necessary to fulfil the purposes outlined in this Privacy Policy and in accordance with legal requirements.</p>

<h2>9. Policy Updates</h2>
<p>We may update this Privacy Policy from time to time. Any changes will be posted on this page with a revised "Last updated" date.</p>

<h2>10. Contact Us</h2>
<p>For any questions about this Privacy Policy or your personal data, please contact us at:<br>
<a href="mailto:fundistributionbws@gmail.com">fundistributionbws@gmail.com</a><br>
+221 78 925 70 25<br>
NGOR SURF CAMP – DKR 2025 A 28, Pikine Cité Baila Fall, Parcelle N° 49, Senegal</p>
""",
        "fr": """
<p><strong>NGOR SURF CAMP</strong> (ci-après dénommé "nous", "notre" ou "la Société") attache une grande importance à la vie privée de ses visiteurs et clients. La présente Politique de confidentialité décrit comment nous collectons, utilisons, stockons et protégeons vos informations personnelles lorsque vous visitez notre site web <a href="https://www.surfcampsenegal.com/">https://www.surfcampsenegal.com/</a>.</p>

<h2>1. Informations que nous collectons</h2>
<p>Nous pouvons collecter les types de données personnelles suivants :</p>
<ul>
  <li><strong>Informations d'identification :</strong> nom, adresse e-mail, numéro de téléphone, adresse postale.</li>
  <li><strong>Informations de réservation et de paiement :</strong> données nécessaires au traitement des réservations et des paiements.</li>
  <li><strong>Données techniques :</strong> adresse IP, type d'appareil, navigateur, comportement de navigation, pages visitées.</li>
  <li><strong>Informations volontaires</strong> que vous fournissez via des formulaires de contact, des newsletters, des avis, etc.</li>
</ul>

<h2>2. Comment nous collectons vos informations</h2>
<p>Nous collectons des informations lorsque :</p>
<ul>
  <li>Vous effectuez une réservation ou nous contactez via nos formulaires.</li>
  <li>Vous vous abonnez à notre newsletter.</li>
  <li>Vous effectuez un paiement via nos prestataires de paiement sécurisés.</li>
  <li>Les cookies et outils d'analyse (tels que Google Analytics) suivent votre navigation sur notre site.</li>
</ul>

<h2>3. Finalité de la collecte de données</h2>
<p>Vos informations personnelles sont collectées et utilisées pour :</p>
<ul>
  <li>Traiter les réservations et fournir nos services.</li>
  <li>Communiquer des informations importantes concernant votre séjour.</li>
  <li>Le support client et le suivi des services.</li>
  <li>L'envoi d'offres promotionnelles et de newsletters (si vous avez consenti).</li>
  <li>Le respect des obligations légales et réglementaires applicables.</li>
</ul>

<h2>4. Stockage, partage et sécurité des données</h2>
<p>Vos données personnelles sont stockées de manière sécurisée sur les serveurs de nos prestataires techniques. Nous partageons vos informations uniquement avec des prestataires tiers de confiance (ex. : processeurs de paiement, hébergeurs, services e-mail) dans la mesure nécessaire à la fourniture de nos services. Les données peuvent être divulguées si la loi l'exige ou pour répondre à des demandes légales.</p>

<h2>5. Communication avec les utilisateurs</h2>
<p>Nous pouvons vous contacter par e-mail, téléphone, SMS ou courrier postal pour :</p>
<ul>
  <li>Confirmer et gérer vos réservations.</li>
  <li>Fournir des mises à jour ou des informations pratiques concernant votre séjour.</li>
  <li>Envoyer du contenu marketing et promotionnel (si vous avez accepté).</li>
</ul>

<h2>6. Cookies et outils de suivi</h2>
<p>Notre site utilise des cookies et des technologies similaires afin de :</p>
<ul>
  <li>Améliorer les performances et la navigation du site.</li>
  <li>Analyser le trafic et le comportement des visiteurs.</li>
  <li>Personnaliser le contenu et les offres.</li>
</ul>
<p>Vous pouvez configurer votre navigateur pour refuser les cookies ou être alerté lorsque des cookies sont utilisés.</p>

<h2>7. Retrait du consentement</h2>
<p>Vous pouvez à tout moment :</p>
<ul>
  <li>Demander l'accès, la correction ou la suppression de vos données personnelles.</li>
  <li>Retirer votre consentement aux communications marketing.</li>
</ul>
<p>Pour exercer vos droits, veuillez nous contacter à :<br>
<a href="mailto:fundistributionbws@gmail.com">fundistributionbws@gmail.com</a><br>
+221 78 925 70 25<br>
NGOR SURF CAMP – DKR 2025 A 28, Pikine Cité Baila Fall, Parcelle N° 49, Sénégal</p>

<h2>8. Conservation des données</h2>
<p>Nous conservons vos données personnelles uniquement le temps nécessaire pour accomplir les finalités décrites dans cette Politique de confidentialité et conformément aux exigences légales.</p>

<h2>9. Mises à jour de la politique</h2>
<p>Nous pouvons mettre à jour cette Politique de confidentialité de temps à autre. Toute modification sera publiée sur cette page avec une date de "Dernière mise à jour" révisée.</p>

<h2>10. Nous contacter</h2>
<p>Pour toute question concernant cette Politique de confidentialité ou vos données personnelles, veuillez nous contacter à :<br>
<a href="mailto:fundistributionbws@gmail.com">fundistributionbws@gmail.com</a><br>
+221 78 925 70 25<br>
NGOR SURF CAMP – DKR 2025 A 28, Pikine Cité Baila Fall, Parcelle N° 49, Sénégal</p>
""",
        "es": """
<p><strong>NGOR SURF CAMP</strong> (en adelante denominado "nosotros", "nuestro" o "la Empresa") valora la privacidad de sus visitantes y clientes. Esta Política de privacidad describe cómo recopilamos, utilizamos, almacenamos y protegemos su información personal cuando visita nuestro sitio web <a href="https://www.surfcampsenegal.com/">https://www.surfcampsenegal.com/</a>.</p>

<h2>1. Información que recopilamos</h2>
<p>Podemos recopilar los siguientes tipos de datos personales:</p>
<ul>
  <li><strong>Información de identificación:</strong> nombre, dirección de correo electrónico, número de teléfono, dirección postal.</li>
  <li><strong>Información de reserva y pago:</strong> datos necesarios para procesar reservas y pagos.</li>
  <li><strong>Datos técnicos:</strong> dirección IP, tipo de dispositivo, navegador, comportamiento de navegación, páginas visitadas.</li>
  <li><strong>Información voluntaria</strong> que usted proporciona a través de formularios de contacto, boletines, reseñas, etc.</li>
</ul>

<h2>2. Cómo recopilamos su información</h2>
<p>Recopilamos información cuando:</p>
<ul>
  <li>Realiza una reserva o nos contacta a través de nuestros formularios.</li>
  <li>Se suscribe a nuestro boletín informativo.</li>
  <li>Realiza un pago a través de nuestros proveedores de pago seguros.</li>
  <li>Las cookies y herramientas de análisis (como Google Analytics) rastrean su navegación en nuestro sitio web.</li>
</ul>

<h2>3. Finalidad de la recopilación de datos</h2>
<p>Su información personal se recopila y utiliza para:</p>
<ul>
  <li>Procesar reservas y proporcionar nuestros servicios.</li>
  <li>Comunicar información importante sobre su estancia.</li>
  <li>Atención al cliente y seguimiento del servicio.</li>
  <li>Envío de ofertas promocionales y boletines (si ha dado su consentimiento).</li>
  <li>Cumplimiento de las obligaciones legales y reglamentarias aplicables.</li>
</ul>

<h2>4. Almacenamiento, intercambio y seguridad de datos</h2>
<p>Sus datos personales se almacenan de forma segura en los servidores de nuestros proveedores técnicos. Solo compartimos su información con proveedores de servicios de terceros de confianza (p. ej., procesadores de pago, proveedores de alojamiento, servicios de correo electrónico) según sea necesario para prestar nuestros servicios. Los datos pueden divulgarse si así lo exige la ley o para responder a solicitudes legales.</p>

<h2>5. Comunicación con los usuarios</h2>
<p>Podemos contactarle por correo electrónico, teléfono, SMS o correo postal para:</p>
<ul>
  <li>Confirmar y gestionar sus reservas.</li>
  <li>Proporcionar actualizaciones o información práctica sobre su estancia.</li>
  <li>Enviar contenido de marketing y promocional (si ha dado su consentimiento).</li>
</ul>

<h2>6. Cookies y herramientas de seguimiento</h2>
<p>Nuestro sitio web utiliza cookies y tecnologías similares para:</p>
<ul>
  <li>Mejorar el rendimiento y la navegación del sitio.</li>
  <li>Analizar el tráfico y el comportamiento de los visitantes.</li>
  <li>Personalizar el contenido y las ofertas.</li>
</ul>
<p>Puede configurar su navegador para rechazar las cookies o para recibir una alerta cuando se utilicen cookies.</p>

<h2>7. Retirada del consentimiento</h2>
<p>Puede en cualquier momento:</p>
<ul>
  <li>Solicitar el acceso, la corrección o la eliminación de sus datos personales.</li>
  <li>Retirar su consentimiento para las comunicaciones de marketing.</li>
</ul>
<p>Para ejercer sus derechos, contáctenos en:<br>
<a href="mailto:fundistributionbws@gmail.com">fundistributionbws@gmail.com</a><br>
+221 78 925 70 25<br>
NGOR SURF CAMP – DKR 2025 A 28, Pikine Cité Baila Fall, Parcelle N° 49, Senegal</p>

<h2>8. Conservación de datos</h2>
<p>Conservamos sus datos personales solo durante el tiempo necesario para cumplir los fines descritos en esta Política de privacidad y de conformidad con los requisitos legales.</p>

<h2>9. Actualizaciones de la política</h2>
<p>Podemos actualizar esta Política de privacidad de vez en cuando. Cualquier cambio se publicará en esta página con una fecha de "Última actualización" revisada.</p>

<h2>10. Contáctenos</h2>
<p>Para cualquier pregunta sobre esta Política de privacidad o sus datos personales, contáctenos en:<br>
<a href="mailto:fundistributionbws@gmail.com">fundistributionbws@gmail.com</a><br>
+221 78 925 70 25<br>
NGOR SURF CAMP – DKR 2025 A 28, Pikine Cité Baila Fall, Parcelle N° 49, Senegal</p>
""",
        "it": """
<p><strong>NGOR SURF CAMP</strong> (di seguito denominata "noi", "nostro" o "la Società") tiene in grande considerazione la privacy dei propri visitatori e clienti. La presente Informativa sulla privacy descrive come raccogliamo, utilizziamo, conserviamo e proteggiamo le sue informazioni personali quando visita il nostro sito web <a href="https://www.surfcampsenegal.com/">https://www.surfcampsenegal.com/</a>.</p>

<h2>1. Informazioni che raccogliamo</h2>
<p>Possiamo raccogliere i seguenti tipi di dati personali:</p>
<ul>
  <li><strong>Informazioni identificative:</strong> nome, indirizzo e-mail, numero di telefono, indirizzo postale.</li>
  <li><strong>Informazioni di prenotazione e pagamento:</strong> dati necessari per elaborare prenotazioni e pagamenti.</li>
  <li><strong>Dati tecnici:</strong> indirizzo IP, tipo di dispositivo, browser, comportamento di navigazione, pagine visitate.</li>
  <li><strong>Informazioni volontarie</strong> che fornisce tramite moduli di contatto, newsletter, recensioni, ecc.</li>
</ul>

<h2>2. Come raccogliamo le sue informazioni</h2>
<p>Raccogliamo informazioni quando:</p>
<ul>
  <li>Effettua una prenotazione o ci contatta tramite i nostri moduli.</li>
  <li>Si iscrive alla nostra newsletter.</li>
  <li>Completa un pagamento tramite i nostri fornitori di pagamento sicuri.</li>
  <li>I cookie e gli strumenti di analisi (come Google Analytics) tracciano la sua navigazione sul nostro sito web.</li>
</ul>

<h2>3. Finalità della raccolta dati</h2>
<p>Le sue informazioni personali sono raccolte e utilizzate per:</p>
<ul>
  <li>Elaborare le prenotazioni e fornire i nostri servizi.</li>
  <li>Comunicare informazioni importanti riguardanti il suo soggiorno.</li>
  <li>Assistenza clienti e follow-up del servizio.</li>
  <li>Invio di offerte promozionali e newsletter (se ha dato il consenso).</li>
  <li>Rispetto degli obblighi legali e normativi applicabili.</li>
</ul>

<h2>4. Conservazione, condivisione e sicurezza dei dati</h2>
<p>I suoi dati personali sono conservati in modo sicuro sui server dei nostri fornitori tecnici. Condividiamo le sue informazioni solo con fornitori di servizi terzi affidabili (ad es., elaboratori di pagamento, fornitori di hosting, servizi e-mail) nei limiti necessari per erogare i nostri servizi. I dati possono essere divulgati se richiesto dalla legge o per rispondere a richieste legali.</p>

<h2>5. Comunicazione con gli utenti</h2>
<p>Potremmo contattarla tramite e-mail, telefono, SMS o posta ordinaria per:</p>
<ul>
  <li>Confermare e gestire le sue prenotazioni.</li>
  <li>Fornire aggiornamenti o informazioni pratiche riguardanti il suo soggiorno.</li>
  <li>Inviare contenuti di marketing e promozionali (se ha dato il suo consenso).</li>
</ul>

<h2>6. Cookie e strumenti di tracciamento</h2>
<p>Il nostro sito web utilizza cookie e tecnologie simili al fine di:</p>
<ul>
  <li>Migliorare le prestazioni e la navigazione del sito.</li>
  <li>Analizzare il traffico e il comportamento dei visitatori.</li>
  <li>Personalizzare contenuti e offerte.</li>
</ul>
<p>Può configurare il browser per rifiutare i cookie o per ricevere un avviso quando vengono utilizzati.</p>

<h2>7. Revoca del consenso</h2>
<p>Può in qualsiasi momento:</p>
<ul>
  <li>Richiedere l'accesso, la rettifica o la cancellazione dei suoi dati personali.</li>
  <li>Revocare il consenso alle comunicazioni di marketing.</li>
</ul>
<p>Per esercitare i suoi diritti, ci contatti a:<br>
<a href="mailto:fundistributionbws@gmail.com">fundistributionbws@gmail.com</a><br>
+221 78 925 70 25<br>
NGOR SURF CAMP – DKR 2025 A 28, Pikine Cité Baila Fall, Parcelle N° 49, Senegal</p>

<h2>8. Conservazione dei dati</h2>
<p>Conserviamo i suoi dati personali solo per il tempo necessario a soddisfare le finalità descritte nella presente Informativa sulla privacy e in conformità con i requisiti legali.</p>

<h2>9. Aggiornamenti della policy</h2>
<p>Potremmo aggiornare questa Informativa sulla privacy di volta in volta. Eventuali modifiche saranno pubblicate su questa pagina con una data di "Ultimo aggiornamento" rivista.</p>

<h2>10. Contattaci</h2>
<p>Per qualsiasi domanda su questa Informativa sulla privacy o sui suoi dati personali, ci contatti a:<br>
<a href="mailto:fundistributionbws@gmail.com">fundistributionbws@gmail.com</a><br>
+221 78 925 70 25<br>
NGOR SURF CAMP – DKR 2025 A 28, Pikine Cité Baila Fall, Parcelle N° 49, Senegal</p>
""",
        "de": """
<p><strong>NGOR SURF CAMP</strong> (im Folgenden als "wir", "unser" oder "das Unternehmen" bezeichnet) legt großen Wert auf den Datenschutz seiner Besucher und Kunden. Diese Datenschutzrichtlinie beschreibt, wie wir Ihre personenbezogenen Daten erheben, verwenden, speichern und schützen, wenn Sie unsere Website <a href="https://www.surfcampsenegal.com/">https://www.surfcampsenegal.com/</a> besuchen.</p>

<h2>1. Informationen, die wir erheben</h2>
<p>Wir können folgende Arten personenbezogener Daten erheben:</p>
<ul>
  <li><strong>Identifikationsdaten:</strong> Name, E-Mail-Adresse, Telefonnummer, Postanschrift.</li>
  <li><strong>Buchungs- und Zahlungsdaten:</strong> Angaben, die für die Verarbeitung von Reservierungen und Zahlungen erforderlich sind.</li>
  <li><strong>Technische Daten:</strong> IP-Adresse, Gerätetyp, Browser, Surfverhalten, besuchte Seiten.</li>
  <li><strong>Freiwillige Informationen,</strong> die Sie über Kontaktformulare, Newsletter, Bewertungen usw. bereitstellen.</li>
</ul>

<h2>2. Wie wir Ihre Daten erheben</h2>
<p>Wir erheben Daten, wenn:</p>
<ul>
  <li>Sie eine Buchung vornehmen oder uns über unsere Formulare kontaktieren.</li>
  <li>Sie unseren Newsletter abonnieren.</li>
  <li>Sie eine Zahlung über unsere sicheren Zahlungsanbieter abschließen.</li>
  <li>Cookies und Analyse-Tools (wie Google Analytics) Ihre Navigation auf unserer Website verfolgen.</li>
</ul>

<h2>3. Zweck der Datenerhebung</h2>
<p>Ihre personenbezogenen Daten werden erhoben und verwendet für:</p>
<ul>
  <li>Die Bearbeitung von Reservierungen und die Erbringung unserer Dienstleistungen.</li>
  <li>Die Übermittlung wichtiger Informationen zu Ihrem Aufenthalt.</li>
  <li>Kundensupport und Nachverfolgung der Dienstleistungen.</li>
  <li>Den Versand von Werbeaktionen und Newslettern (sofern Sie zugestimmt haben).</li>
  <li>Die Einhaltung geltender gesetzlicher und behördlicher Anforderungen.</li>
</ul>

<h2>4. Datenspeicherung, -weitergabe und Sicherheit</h2>
<p>Ihre personenbezogenen Daten werden sicher auf den Servern unserer technischen Anbieter gespeichert. Wir geben Ihre Daten nur an vertrauenswürdige Drittanbieter weiter (z. B. Zahlungsabwickler, Hosting-Anbieter, E-Mail-Dienste), soweit dies zur Erbringung unserer Dienstleistungen erforderlich ist. Daten können offengelegt werden, wenn dies gesetzlich vorgeschrieben ist oder um rechtlichen Anfragen nachzukommen.</p>

<h2>5. Kommunikation mit Nutzern</h2>
<p>Wir können Sie per E-Mail, Telefon, SMS oder Post kontaktieren, um:</p>
<ul>
  <li>Ihre Buchungen zu bestätigen und zu verwalten.</li>
  <li>Aktualisierungen oder praktische Informationen zu Ihrem Aufenthalt bereitzustellen.</li>
  <li>Marketing- und Werbeinhalte zu versenden (sofern Sie zugestimmt haben).</li>
</ul>

<h2>6. Cookies und Tracking-Tools</h2>
<p>Unsere Website verwendet Cookies und ähnliche Technologien, um:</p>
<ul>
  <li>Die Leistung und Navigation der Website zu verbessern.</li>
  <li>Den Datenverkehr und das Besucherverhalten zu analysieren.</li>
  <li>Inhalte und Angebote zu personalisieren.</li>
</ul>
<p>Sie können Ihren Browser so konfigurieren, dass Cookies abgelehnt werden oder Sie benachrichtigt werden, wenn Cookies verwendet werden.</p>

<h2>7. Widerruf der Einwilligung</h2>
<p>Sie können jederzeit:</p>
<ul>
  <li>Den Zugriff auf, die Berichtigung oder Löschung Ihrer personenbezogenen Daten beantragen.</li>
  <li>Ihre Einwilligung in Marketingkommunikation widerrufen.</li>
</ul>
<p>Um Ihre Rechte auszuüben, kontaktieren Sie uns bitte unter:<br>
<a href="mailto:fundistributionbws@gmail.com">fundistributionbws@gmail.com</a><br>
+221 78 925 70 25<br>
NGOR SURF CAMP – DKR 2025 A 28, Pikine Cité Baila Fall, Parcelle N° 49, Senegal</p>

<h2>8. Datenspeicherdauer</h2>
<p>Wir speichern Ihre personenbezogenen Daten nur so lange, wie es zur Erfüllung der in dieser Datenschutzrichtlinie genannten Zwecke erforderlich ist und in Übereinstimmung mit den gesetzlichen Anforderungen.</p>

<h2>9. Aktualisierungen der Richtlinie</h2>
<p>Wir können diese Datenschutzrichtlinie von Zeit zu Zeit aktualisieren. Änderungen werden auf dieser Seite mit einem aktualisierten Datum "Zuletzt aktualisiert" veröffentlicht.</p>

<h2>10. Kontakt</h2>
<p>Bei Fragen zu dieser Datenschutzrichtlinie oder Ihren personenbezogenen Daten wenden Sie sich bitte an:<br>
<a href="mailto:fundistributionbws@gmail.com">fundistributionbws@gmail.com</a><br>
+221 78 925 70 25<br>
NGOR SURF CAMP – DKR 2025 A 28, Pikine Cité Baila Fall, Parcelle N° 49, Senegal</p>
""",
        "nl": """
<p><strong>NGOR SURF CAMP</strong> (hierna "wij", "ons" of "het Bedrijf") hecht waarde aan de privacy van zijn bezoekers en klanten. Dit privacybeleid beschrijft hoe wij uw persoonlijke gegevens verzamelen, gebruiken, opslaan en beschermen wanneer u onze website bezoekt.</p>

<h2>1. Informatie die wij verzamelen</h2>
<p>Wij kunnen de volgende soorten persoonlijke gegevens verzamelen:</p>
<ul>
  <li><strong>Identificatiegegevens:</strong> naam, e-mailadres, telefoonnummer, postadres.</li>
  <li><strong>Reserverings- en betalingsgegevens:</strong> gegevens die nodig zijn voor het verwerken van reserveringen en betalingen.</li>
  <li><strong>Technische gegevens:</strong> IP-adres, apparaattype, browser, surfgedrag, bezochte pagina's.</li>
  <li><strong>Vrijwillige informatie</strong> die u verstrekt via contactformulieren, nieuwsbrieven, reviews, enz.</li>
</ul>

<h2>2. Hoe wij uw gegevens verzamelen</h2>
<p>Wij verzamelen informatie wanneer u een reservering maakt, contact met ons opneemt, onze website gebruikt of een nieuwsbrief aanvraagt.</p>

<h2>3. Gebruik van uw gegevens</h2>
<p>Wij gebruiken uw gegevens om uw reservering te verwerken, u te informeren, onze diensten te verbeteren en te voldoen aan onze wettelijke verplichtingen. Wij delen uw gegevens niet met derden voor marketingdoeleinden.</p>

<h2>4. Uw rechten</h2>
<p>U heeft het recht om inzage, rectificatie, verwijdering en overdraagbaarheid van uw gegevens te verzoeken. Neem contact met ons op via <a href="mailto:fundistributionbws@gmail.com">fundistributionbws@gmail.com</a>.</p>

<h2>5. Contact</h2>
<p>NGOR SURF CAMP – DKR 2025 A 28, Pikine Cité Baila Fall, Parcelle N° 49, Senegal<br>
<a href="mailto:fundistributionbws@gmail.com">fundistributionbws@gmail.com</a> | +221 78 925 70 25</p>
""",
        "ar": """
<p><strong>NGOR SURF CAMP</strong> (يُشار إليها فيما يلي بـ "نحن" أو "شركتنا") تُقدّر خصوصية زوارها وعملائها. تصف سياسة الخصوصية هذه كيفية جمعنا لبياناتك الشخصية واستخدامها وتخزينها وحمايتها عند زيارتك لموقعنا الإلكتروني.</p>

<h2>1. المعلومات التي نجمعها</h2>
<p>قد نجمع أنواعًا مختلفة من البيانات الشخصية:</p>
<ul>
  <li><strong>معلومات التعريف:</strong> الاسم، عنوان البريد الإلكتروني، رقم الهاتف، العنوان البريدي.</li>
  <li><strong>معلومات الحجز والدفع:</strong> التفاصيل المطلوبة لمعالجة الحجوزات والمدفوعات.</li>
  <li><strong>البيانات التقنية:</strong> عنوان IP، نوع الجهاز، المتصفح، سلوك التصفح، الصفحات المزارة.</li>
  <li><strong>المعلومات الطوعية</strong> التي تقدمها عبر نماذج الاتصال والنشرات الإخبارية والمراجعات.</li>
</ul>

<h2>2. كيف نجمع معلوماتك</h2>
<p>نجمع المعلومات عند إجراء حجز، أو التواصل معنا، أو استخدام موقعنا الإلكتروني، أو الاشتراك في النشرة الإخبارية.</p>

<h2>3. استخدام بياناتك</h2>
<p>نستخدم بياناتك لمعالجة حجوزاتك، وإعلامك، وتحسين خدماتنا، والامتثال لالتزاماتنا القانونية. لا نشارك بياناتك مع أطراف ثالثة لأغراض تسويقية.</p>

<h2>4. حقوقك</h2>
<p>لك الحق في طلب الاطلاع على بياناتك وتصحيحها وحذفها ونقلها. تواصل معنا عبر <a href="mailto:fundistributionbws@gmail.com">fundistributionbws@gmail.com</a>.</p>

<h2>5. التواصل</h2>
<p>NGOR SURF CAMP – DKR 2025 A 28, Pikine Cité Baila Fall, Parcelle N° 49, السنغال<br>
<a href="mailto:fundistributionbws@gmail.com">fundistributionbws@gmail.com</a> | +221 78 925 70 25</p>
""",
    }

    # Build lang-switcher hrefs
    lang_switch = {}
    for lg in LANGS:
        other_pfx  = LANG_PFX[lg]
        other_slug = SLUG[lg]["privacy-policy"]
        lang_switch[lg] = f"{other_pfx}/{other_slug}/" if lg != "en" else f"/{other_slug}/"

    LEGAL_LBL = {"en":"Legal","fr":"Mentions légales","es":"Legal","it":"Legale","de":"Rechtliches","nl":"Juridisch","ar":"قانوني"}
    Q_LBL     = {"en":"Have questions?","fr":"Des questions ?","es":"¿Tiene preguntas?",
                 "it":"Hai domande?","de":"Haben Sie Fragen?","nl":"Heeft u vragen?","ar":"هل لديك أسئلة؟"}
    CTA_LBL   = {"en":"Contact us","fr":"Contactez-nous","es":"Contáctenos",
                 "it":"Contattaci","de":"Kontaktieren Sie uns","nl":"Neem contact op","ar":"تواصل معنا"}

    html  = page_head(TITLES[lang], METAS[lang], lang, "privacy-policy")
    html += build_nav("", lang, lang_switch)
    html += f"""
<main>
  <section class="section sec-light" style="padding-top:100px">
    <div class="container" style="max-width:800px">
      <span class="s-label">{LEGAL_LBL[lang]}</span>
      <h1 style="font-size:clamp(28px,4vw,48px);color:var(--navy);margin:12px 0 6px;font-weight:900">{H1S[lang]}</h1>
      <p style="color:#6b7280;font-size:14px;margin-bottom:40px"><em>{UPDATED[lang]}</em></p>
      <div class="prose-body" style="font-size:16.5px;line-height:1.85;color:#374151">
        {CONTENT.get(lang, CONTENT["en"])}
      </div>
      <div style="margin-top:48px;padding:24px 28px;background:var(--sand3,#fdf6ec);border-radius:14px;border-left:4px solid var(--fire,#ff6b35)">
        <p style="margin:0;font-size:15px;color:#374151">
          {Q_LBL[lang]}
          &nbsp;<a href="{book_href}" style="color:var(--fire,#ff6b35);font-weight:700;text-decoration:none">{CTA_LBL[lang]}</a>
        </p>
      </div>
    </div>
  </section>
</main>"""
    html += build_footer(lang, lang_switch)
    html += page_close()
    return html


# ════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════
total = 0
def wp(rel, html):
    global total
    write_page(rel, html)
    total += 1

print("Patching footer markup site-wide…")
patch_footer_brands_all()


patch_home_getting_here_teaser()
patch_home_rotating_quotes()
patch_home_static_text_all()
patch_getting_here_footers()
patch_explore_footer_getting_here_all()
patch_footer_bottom_pp_all()

print("Patching language switcher sitewide…")
patch_lang_switcher_all()

print("Translating home page nav + footer (AR/NL)…")
patch_home_nav_footer_all()

print("Translating home page Discover section (AR/NL)…")
patch_home_discover_section_all()

print("Fixing Google score to match real GBP (4.7 / 54 reviews)…")
patch_google_score_all()

print("Translating home reviews labels (AR/NL)…")
patch_home_reviews_labels_all()

print("Fixing author bio truncation…")
patch_author_bios_all()

print("Patching wave dividers sitewide…")
patch_waves_all_pages()

print("Patching home proof strip (hero → content)…")
patch_home_proof_strip_all()

print("Patching home wave dividers…")
patch_home_waves_all()

print("Patching home gallery slider…")
patch_home_gallery_all()

print("Patching home blog preview (6 cards)…")
patch_home_blog_preview_all()

print("Injecting Instagram feed section into home pages…")
patch_home_insta_section_all()

print("Injecting surf forecast widget into home pages…")
patch_home_forecast_all()

print("Patching home localized UI leftovers (AR)…")
patch_home_lang_ui_cleanup_all()

print("Patching home reviews slider (localized cards, non-EN)…")
patch_home_reviews_slider_all()

def patch_head_all_pages():
    """Update <head> on ALL HTML pages: asset version, async fonts, preconnects."""
    import re as _re
    old_versions = ["20260327f","20260328a","20260328b","20260328c","20260328d","20260329a","20260329b","20260329c","20260329d","20260329e","20260329f","20260329g","20260330o","20260401a","20260401b"]
    new_v = ASSET_VERSION
    FONT_URL = "/assets/fonts/fonts.css"
    OLD_FONT_BLOCKING = _re.compile(
        r'<link\s+href="https://fonts\.googleapis\.com/css2[^"]*"\s+rel="stylesheet">'
        r'|<link\s+rel="stylesheet"\s+href="https://fonts\.googleapis\.com/css2[^"]*">',
        _re.DOTALL
    )
    ASYNC_FONT = f'<link rel="stylesheet" href="{FONT_URL}">'
    n_updated = 0
    from pathlib import Path as _Path
    for html_path in _Path(DEMO_DIR).rglob("*.html"):
        try:
            with open(html_path, encoding="utf-8", errors="replace") as f:
                h = f.read()
            changed = False
            # Legacy asset URLs → live filenames (older HTML / partial builds)
            for _old_href, _new_href in (
                ("/assets/css/style.css", f"/assets/css/{ASSET_CSS_MAIN}"),
                ("/assets/js/animations.js", f"/assets/js/{ASSET_JS_MAIN}"),
                ("/assets/css/cmp-brand.css", f"/assets/css/{ASSET_CSS_CONSENT}"),
            ):
                if _old_href in h:
                    h = h.replace(_old_href, _new_href)
                    changed = True
            _old_inline = "animations.js (single listener)"
            if _old_inline in h:
                h = h.replace(_old_inline, f"{ASSET_JS_MAIN} (site bundle)")
                changed = True
            # Update asset version
            for old_v in old_versions:
                if old_v in h:
                    h = h.replace(old_v, new_v)
                    changed = True
            # Replace ALL Google Fonts references with self-hosted fonts.css
            if 'fonts.googleapis.com' in h:
                # Remove preload+onload async pattern (any variant)
                h2 = _re.sub(
                    r'<link\b[^>]+fonts\.googleapis\.com[^>]*>\n?',
                    '', h
                )
                # Remove noscript fallback wrapping a Google Fonts link
                h2 = _re.sub(
                    r'<noscript>\s*<link\b[^>]+fonts\.googleapis\.com[^>]*>\s*</noscript>\n?',
                    '', h2
                )
                # Inject local fonts.css once (before </head>) if not already there
                if FONT_URL not in h2 and '</head>' in h2:
                    h2 = h2.replace('</head>',
                        f'<link rel="stylesheet" href="{FONT_URL}">\n</head>', 1)
                if h2 != h:
                    h = h2
                    changed = True
            # Remove any lingering Wix preconnect hints (assets are now self-hosted)
            for _wix_pc in (
                '<link rel="preconnect" href="https://static.wixstatic.com" crossorigin>',
                '<link rel="preconnect" href="https://static.wixstatic.com">',
                '<link rel="preconnect" href="https://video.wixstatic.com" crossorigin>',
                '<link rel="preconnect" href="https://video.wixstatic.com">',
            ):
                if _wix_pc in h:
                    h = h.replace(_wix_pc + '\n', '').replace(_wix_pc, '')
                    changed = True
            # Inject favicon / PWA tags if not already present
            if 'rel="icon"' not in h and '</head>' in h:
                _fav_tags = (
                    '<link rel="icon" type="image/x-icon" href="/favicon.ico">\n'
                    '<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">\n'
                    '<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">\n'
                    '<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">\n'
                    '<link rel="manifest" href="/site.webmanifest">\n'
                    '<meta name="theme-color" content="#0a2540">\n'
                )
                h = h.replace('</head>', _fav_tags + '</head>', 1)
                changed = True
            # Inject og:url if missing
            if 'og:url' not in h and 'og:title' in h and '</head>' in h:
                _rel = str(html_path.relative_to(_Path(DEMO_DIR))).replace("\\", "/")
                if _rel.endswith("/index.html"):
                    _rel = _rel[:-len("index.html")]
                elif _rel == "index.html":
                    _rel = ""
                _page_url = f"{SITE_URL}/{_rel}" if _rel else f"{SITE_URL}/"
                _og_url_tag = f'<meta property="og:url" content="{_page_url}">\n'
                h = h.replace('</head>', _og_url_tag + '</head>', 1)
                changed = True
            # Make relative og:image absolute
            if 'og:image" content="/' in h:
                h = h.replace('og:image" content="/', f'og:image" content="{SITE_URL}/')
                changed = True
            # Inject og:site_name if missing
            if 'og:site_name' not in h and 'og:title' in h and '</head>' in h:
                h = h.replace('</head>', '<meta property="og:site_name" content="Ngor Surfcamp Teranga">\n</head>', 1)
                changed = True
            # Inject twitter:card if missing
            if 'twitter:card' not in h and 'og:title' in h and '</head>' in h:
                h = h.replace('</head>', '<meta name="twitter:card" content="summary_large_image">\n</head>', 1)
                changed = True
            # Clean up excessive blank lines in <head>
            while '\n\n\n' in h:
                h = h.replace('\n\n\n', '\n\n')
                changed = True
            if changed:
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(h)
                n_updated += 1
        except Exception as e:
            print(f"  head patch error {html_path}: {e}")
    print(f"  head: updated {n_updated} HTML pages")


def inject_homepage_jsonld():
    """Inject LocalBusiness + WebSite structured data into all homepage variants."""
    import json as _json
    from pathlib import Path as _Path
    n = 0
    for lang in LANGS:
        pfx = LANG_PFX[lang]
        p = _Path(DEMO_DIR) / (pfx.lstrip("/") + "/index.html" if pfx else "index.html")
        if not p.exists():
            continue
        h = p.read_text(encoding="utf-8", errors="replace")
        if 'LocalBusiness' in h and 'aggregateRating' in h:
            continue
        # If LocalBusiness exists but lacks aggregateRating, strip the old tag and re-inject
        if 'LocalBusiness' in h and 'aggregateRating' not in h:
            import re as _re2
            h = _re2.sub(r'<script type="application/ld\+json">\{"@context":"https://schema\.org","@graph":\[.*?"@type":"LocalBusiness".*?</script>\n?', '', h, flags=_re2.DOTALL)
        _url = f"{SITE_URL}{pfx}/" if pfx else f"{SITE_URL}/"
        ld = _json.dumps({
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "LocalBusiness",
                    "@id": f"{SITE_URL}/#organization",
                    "name": "Ngor Surfcamp Teranga",
                    "url": SITE_URL,
                    "logo": f"{SITE_URL}/assets/images/wix/c2467f_a31779010ce34c4c8c61cc5868d81f31.webp",
                    "image": f"{SITE_URL}/assets/images/wix/df99f9_da0cf7c72b1a4606bcfa1f7c8e089dc4f000.webp",
                    "description": "Surf camp accommodation in Senegal near Dakar with easy access to Ngor Island waves.",
                    "address": {
                        "@type": "PostalAddress",
                        "addressLocality": "Ngor",
                        "addressRegion": "Dakar",
                        "addressCountry": "SN"
                    },
                    "geo": {
                        "@type": "GeoCoordinates",
                        "latitude": 14.7469,
                        "longitude": -17.5139
                    },
                    "telephone": "+221789257025",
                    "priceRange": "$$",
                    "openingHoursSpecification": {
                        "@type": "OpeningHoursSpecification",
                        "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
                        "opens": "07:00",
                        "closes": "22:00"
                    },
                    "aggregateRating": {
                        "@type": "AggregateRating",
                        "ratingValue": "4.7",
                        "bestRating": "5",
                        "worstRating": "1",
                        "reviewCount": "54",
                        "url": "https://www.google.com/maps?cid=14555894641030809667"
                    },
                    "review": {
                        "@type": "Review",
                        "reviewRating": {"@type": "Rating", "ratingValue": "5", "bestRating": "5"},
                        "author": {"@type": "Person", "name": "Stéphane M."},
                        "reviewBody": "Best surf camp I've tried! Amazing team, perfect waves every day at Ngor Island. Abu is the best surf guide in Dakar.",
                        "datePublished": "2025-03-01"
                    },
                    "sameAs": [
                        "https://www.instagram.com/ngor_surfcamp_teranga/",
                        "https://www.google.com/maps?cid=14555894641030809667"
                    ]
                },
                {
                    "@type": "WebSite",
                    "@id": f"{SITE_URL}/#website",
                    "url": SITE_URL,
                    "name": "Ngor Surfcamp Teranga",
                    "publisher": {"@id": f"{SITE_URL}/#organization"},
                    "inLanguage": [
                        {"@type": "Language", "name": "English", "alternateName": "en"},
                        {"@type": "Language", "name": "French", "alternateName": "fr"},
                        {"@type": "Language", "name": "Spanish", "alternateName": "es"},
                        {"@type": "Language", "name": "Italian", "alternateName": "it"},
                        {"@type": "Language", "name": "German", "alternateName": "de"},
                        {"@type": "Language", "name": "Dutch", "alternateName": "nl"},
                        {"@type": "Language", "name": "Arabic", "alternateName": "ar"}
                    ]
                }
            ]
        }, ensure_ascii=False)
        tag = f'<script type="application/ld+json">{ld}</script>\n'
        h = h.replace('</head>', tag + '</head>', 1)
        p.write_text(h, encoding="utf-8")
        n += 1
    print(f"  JSON-LD: injected LocalBusiness+WebSite into {n} homepages")


def patch_all_footers():
    """Replace footer on every HTML page with freshly-generated build_footer() output.
    Ensures GMB badge and any footer changes propagate to all pages including static ones."""
    import re as _re
    FOOTER_RE = _re.compile(r'<footer>.*?</footer>', _re.DOTALL)
    n = 0
    for root, dirs, files in os.walk(DEMO_DIR):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
        for fn in files:
            if not fn.endswith('.html'):
                continue
            path = os.path.join(root, fn)
            # Detect language from path
            rel = os.path.relpath(path, DEMO_DIR).replace("\\", "/")
            lang = "en"
            for lg in ["fr", "es", "it", "de", "nl", "ar"]:
                if rel.startswith(lg + "/"):
                    lang = lg
                    break
            try:
                with open(path, encoding="utf-8", errors="replace") as f:
                    h = f.read()
            except OSError:
                continue
            if '<footer>' not in h:
                continue
            # Build correct footer for this page's language
            # For getting-here page, use GETTING_HERE_FLAG_HREF
            if 'getting-here' in rel or 'comment-venir' in rel or 'como-llegar' in rel:
                new_footer = build_footer(lang, GETTING_HERE_FLAG_HREF)
            else:
                new_footer = build_footer(lang)
            h2 = FOOTER_RE.sub(new_footer, h, count=1)
            if h2 != h:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(h2)
                n += 1
    print(f"  footers refreshed: {n} HTML pages")


def inject_nonblog_org_schema():
    """Inject compact Organization schema (with AggregateRating) on all non-blog, non-homepage pages."""
    import json as _json
    from pathlib import Path as _Path
    import re as _re

    ORG_LD = _json.dumps({
        "@context": "https://schema.org",
        "@type": "Organization",
        "@id": f"{SITE_URL}/#organization",
        "name": "Ngor Surfcamp Teranga",
        "url": SITE_URL,
        "logo": f"{SITE_URL}/assets/images/wix/c2467f_a31779010ce34c4c8c61cc5868d81f31.webp",
        "telephone": "+221789257025",
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": "4.7",
            "bestRating": "5",
            "worstRating": "1",
            "reviewCount": "54",
            "url": "https://www.google.com/maps?cid=14555894641030809667"
        },
        "sameAs": [
            "https://www.instagram.com/ngor_surfcamp_teranga/",
            "https://www.google.com/maps?cid=14555894641030809667"
        ]
    }, ensure_ascii=False)
    tag = f'<script type="application/ld+json">{ORG_LD}</script>\n'

    n = 0
    for html_path in _Path(DEMO_DIR).rglob("index.html"):
        rel = str(html_path.relative_to(DEMO_DIR)).replace("\\", "/")
        # Skip homepages (handled by inject_homepage_jsonld)
        if rel in ("index.html",) or rel.endswith("/index.html") and rel.count("/") == 1 and rel[:2] in ("fr", "es", "it", "de", "nl", "ar"):
            continue
        # Skip blog pages
        if "/blog/" in rel:
            continue
        try:
            h = html_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if '"@type":"Organization"' in h or 'Organization' in h and 'aggregateRating' in h:
            continue
        h = h.replace("</head>", tag + "</head>", 1)
        html_path.write_text(h, encoding="utf-8")
        n += 1
    print(f"  JSON-LD: injected Organization+AggregateRating into {n} non-blog pages")


def patch_remove_float_wa_all():
    """Remove legacy floating WhatsApp FAB (#float-wa) from every static HTML file."""
    import re as _re
    from pathlib import Path as _Path

    pat = _re.compile(
        r'<a\b[^>]*\bid=["\']float-wa["\'][^>]*>[\s\S]*?</a>',
        _re.IGNORECASE,
    )
    n_pages = 0
    n_removed = 0
    for html_path in _Path(DEMO_DIR).rglob("*.html"):
        try:
            with open(html_path, encoding="utf-8", errors="replace") as f:
                h = f.read()
            h2, count = pat.subn("", h)
            if count:
                n_removed += count
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(h2)
                n_pages += 1
        except Exception as e:
            print(f"  float-wa strip error {html_path}: {e}")
    print(f"  float-wa: removed {n_removed} anchor(s) from {n_pages} HTML file(s)")


def patch_cmp_all_pages():
    """Inject vanilla-cookieconsent v3 (MIT) + Google Consent Mode v2 defaults (gtag stub)."""
    _av = ASSET_VERSION
    CMP_HEAD_BLOCK = (
        '<script id="gcm-consent-default">'
        "window.dataLayer=window.dataLayer||[];"
        "function gtag(){dataLayer.push(arguments);}"
        "gtag('consent','default',{"
        "ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied',"
        "analytics_storage:'denied',functionality_storage:'granted',"
        "personalization_storage:'denied',security_storage:'granted',wait_for_update:500"
        "});"
        "</script>\n"
        '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/vanilla-cookieconsent@3/dist/cookieconsent.css">\n'
        f'<link rel="stylesheet" href="/assets/css/{ASSET_CSS_CONSENT}?v={_av}">'
    )
    CMP_JS = """<script type="module">
(async function(){
try {
const _cc = await import('https://cdn.jsdelivr.net/npm/vanilla-cookieconsent@3/dist/cookieconsent.esm.js');
const { run, acceptedCategory } = _cc;
window.CookieConsent = _cc;
var lang=(document.documentElement.getAttribute('lang')||'en').toLowerCase().split('-')[0].split('_')[0];
var T={
  en:{title:'We value your privacy',desc:'We use essential cookies to keep the site running. With your consent we also measure traffic anonymously via Google Analytics.',accept:'Accept all',reject:'Continue without accepting',manage:'Cookie settings',save:'Save choices',nec:'Essential cookies',necD:'Required for security, forms and basic site function. Always on.',sta:'Analytics & measurement',staD:'Helps us see which pages are useful (anonymous usage).'},
  fr:{title:'Nous respectons votre vie privée',desc:'Nous utilisons des cookies indispensables au fonctionnement du site. Avec votre accord, des cookies de mesure d’audience peuvent aussi être utilisés.',accept:'Tout accepter',reject:'Continuer sans accepter',manage:'Paramètres des cookies',save:'Enregistrer',nec:'Cookies indispensables',necD:'Nécessaires à la sécurité, aux formulaires et au bon fonctionnement du site. Toujours actifs.',sta:'Mesure d’audience',staD:'Nous aide à comprendre l’usage du site (données agrégées).'},
  es:{title:'Respetamos tu privacidad',desc:'Usamos cookies esenciales para que el sitio funcione. Con tu permiso, también cookies de analítica para entender el tráfico.',accept:'Aceptar todo',reject:'Continuar sin aceptar',manage:'Configurar cookies',save:'Guardar',nec:'Cookies esenciales',necD:'Imprescindibles para seguridad, formularios y funcionamiento básico. Siempre activas.',sta:'Analítica y medición',staD:'Nos ayuda a ver qué páginas son útiles (uso agregado).'},
  it:{title:'Rispettiamo la tua privacy',desc:'Usiamo cookie essenziali per il funzionamento del sito. Con il tuo consenso anche cookie di statistica per capire il traffico.',accept:'Accetta tutto',reject:'Continua senza accettare',manage:'Impostazioni cookie',save:'Salva',nec:'Cookie essenziali',necD:'Necessari per sicurezza, moduli e funzioni di base. Sempre attivi.',sta:'Analitica e misurazione',staD:'Ci aiuta a capire quali pagine sono utili (dati aggregati).'},
  de:{title:'Wir schützen Ihre Privatsphäre',desc:'Wir nutzen notwendige Cookies für den Betrieb der Website. Mit Ihrer Zustimmung auch Analyse-Cookies (z. B. für Reichweitenmessung).',accept:'Alle akzeptieren',reject:'Ohne Zustimmung fortfahren',manage:'Cookie-Einstellungen',save:'Speichern',nec:'Notwendige Cookies',necD:'Erforderlich für Sicherheit, Formulare und Grundfunktionen. Immer aktiv.',sta:'Analyse & Messung',staD:'Hilft uns zu verstehen, welche Seiten genutzt werden (aggregiert).'},
  nl:{title:'Wij respecteren uw privacy',desc:'We gebruiken essentiële cookies zodat de site werkt. Met jouw toestemming ook analytics om bezoek te begrijpen.',accept:'Alles accepteren',reject:'Doorgaan zonder te accepteren',manage:'Cookie-instellingen',save:'Opslaan',nec:'Essentiële cookies',necD:'Nodig voor beveiliging, formulieren en basiswerking. Altijd aan.',sta:'Analyse & meting',staD:'Helpt ons zien welke pagina’s nuttig zijn (geaggregeerd).'},
  ar:{title:'نحن نحترم خصوصيتك',desc:'نستخدم ملفات ضرورية لعمل الموقع. بموافقتك قد نستخدم ملفات قياس لزيارات الموقع.',accept:'قبول الكل',reject:'المتابعة بدون قبول',manage:'إعدادات الكوكيز',save:'حفظ',nec:'ملفات ضرورية',necD:'مطلوبة للأمان والنماذج والوظائف الأساسية. مفعَّلة دائمًا.',sta:'التحليلات والقياس',staD:'تساعدنا على فهم الصفحات المفيدة (بيانات مجمَّعة).'},
};
var t=T[lang]||T.en;
function applyGCM(){
  if(typeof gtag!=='function')return;
  var ok=acceptedCategory('analytics');
  var s=ok?'granted':'denied';
  gtag('consent','update',{
    analytics_storage:s,ad_storage:s,ad_user_data:s,ad_personalization:s,personalization_storage:s
  });
}
run({
  hideFromBots:false,
  autoShow:true,
  revision:2,
  cookie:{name:'cc_cookie',expiresAfterDays:182,path:'/',domain:'',secure:typeof location!=='undefined'&&location.protocol==='https:',sameSite:'Lax'},
  guiOptions:{consentModal:{layout:'box',position:'bottom left',equalWeightButtons:false,flipButtons:false},preferencesModal:{layout:'box'}},
  categories:{
    necessary:{enabled:true,readOnly:true},
    analytics:{enabled:false,autoClear:{cookies:[{name:/^_ga/},{name:/^_gid/},{name:/^_gat/}]}}
  },
  language:{default:lang,translations:{[lang]:{
    consentModal:{title:t.title,description:t.desc,acceptAllBtn:t.accept,acceptNecessaryBtn:t.reject},
    preferencesModal:{title:t.manage,acceptAllBtn:t.accept,acceptNecessaryBtn:t.reject,savePreferencesBtn:t.save,closeIconLabel:t.save,
      sections:[
        {title:t.nec,description:t.necD,linkedCategory:'necessary'},
        {title:t.sta,description:t.staD,linkedCategory:'analytics'}
      ]}
  }}},
  onFirstConsent: applyGCM,
  onConsent: applyGCM
});
/* ── Persistent cookie-preferences trigger ── */
(function(){
  var btn=document.createElement('button');
  btn.id='cc-trigger';
  btn.setAttribute('aria-label','Cookie preferences');
  btn.title='Cookie preferences';
  btn.innerHTML='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" width="17" height="17" aria-hidden="true"><circle cx="12" cy="12" r="10"/><circle cx="8.5" cy="9" r="1.3" fill="currentColor" stroke="none"/><circle cx="15" cy="9.5" r="1.1" fill="currentColor" stroke="none"/><circle cx="11.5" cy="14.5" r="1.2" fill="currentColor" stroke="none"/><path d="M9 6c.8-1.2 3.2-1.5 5 0M6.5 12.5c-1.5.3-1.8 2.5 0 3M16 14c1.5.5 2 2.5.5 3.5"/></svg>';
  btn.addEventListener('click',function(){
    if(window.CookieConsent&&window.CookieConsent.showPreferences)
      window.CookieConsent.showPreferences();
  });
  document.body.appendChild(btn);
})();
} catch (e) { console.error('[CMP] CookieConsent failed:', e); }
})();
</script>"""
    n = 0
    import re as _cmp_re
    from pathlib import Path as _Path
    for html_path in _Path(DEMO_DIR).rglob("*.html"):
        try:
            _rel_cmp = str(html_path.relative_to(_Path(DEMO_DIR))).replace("\\", "/")
            if _rel_cmp.startswith("admin/"):
                continue
            with open(html_path, encoding="utf-8", errors="replace") as f:
                h = f.read()
            h = _cmp_re.sub(
                r'<script[^>]*id=["\']gcm-consent-default["\'][^>]*>[\s\S]*?</script>', "", h, flags=_cmp_re.I
            )
            h = _cmp_re.sub(r"<link[^>]*cookieconsent\.css[^>]*>", "", h, flags=_cmp_re.I)
            h = _cmp_re.sub(
                r"<link[^>]*\/assets\/css\/(?:cmp-brand|ngor-surfcamp-consent)\.css[^>]*>",
                "",
                h,
                flags=_cmp_re.I,
            )
            h = _cmp_re.sub(
                r'<script[^>]*type=["\']module["\'][^>]*>[\s\S]*?vanilla-cookieconsent[\s\S]*?</script>',
                "",
                h,
                flags=_cmp_re.DOTALL,
            )
            if "</head>" not in h:
                continue
            h = h.replace("</head>", CMP_HEAD_BLOCK + "\n</head>", 1)
            if "</body>" in h:
                h = h.replace("</body>", CMP_JS + "\n</body>", 1)
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(h)
            n += 1
        except Exception as e:
            print(f"  CMP patch error {html_path}: {e}")
    print(f"  CMP injected into {n} HTML pages")

print("Patching <head> sitewide (asset version, async fonts, preconnects)…")
patch_head_all_pages()

print("Patching surfing pages (icons, grid, HTML structure)…")
patch_surfing_pages_visuals_all()

print("Building surfing pages…")
for lang in LANGS:
    pfx = LANG_PFX[lang]
    spfx = f"/{lang}" if lang != "en" else ""
    slug = SLUG[lang]["surfing"]
    wp(f"{spfx}/{slug}/", build_surfing(lang))
    # Create redirect from /xx/surfing/ → /xx/{slug}/ for langs with different slug
    _old_surfing_slug = "surfing"
    if slug != _old_surfing_slug and lang != "en":
        wp(f"{spfx}/{_old_surfing_slug}/", make_redirect(f"{pfx}/{slug}/"))
    print(f"  ✅ {lang}: /{spfx}/{slug}/")

print("Building gallery pages…")
for lang in LANGS:
    pfx = LANG_PFX[lang]
    spfx = f"/{lang}" if lang != "en" else ""
    slug = SLUG[lang]["gallery"]
    wp(f"{spfx}/{slug}/", build_gallery(lang))
    gal_path = f"/{slug}/" if lang == "en" else f"/{lang}/{slug}/"
    print(f"  ✅ {lang}: {gal_path}")

print("Building surf-house pages…")
for lang in LANGS:
    spfx = f"/{lang}" if lang != "en" else ""
    wp(f"{spfx}/surf-house/", build_surf_house(lang))
    sh_path = "/surf-house/" if lang == "en" else f"/{lang}/surf-house/"
    print(f"  ✅ {lang}: {sh_path}")

print("Building booking pages...")
for lang in LANGS:
    pfx  = LANG_PFX[lang]
    spfx = f"/{lang}" if lang != "en" else ""
    slug = SLUG[lang]["booking"]
    wp(f"{spfx}/{slug}/", build_booking(lang))
    # Create redirect from old slug if different
    old_slug = "booking"
    if slug != old_slug:
        wp(f"{spfx}/{old_slug}/", make_redirect(f"{pfx}/{slug}/"))
    print(f"  ✅ {lang}: /{spfx}/{slug}/")

print(f"\n✅ Built {total} pages (surfing + booking + redirects)")

print("Building privacy policy pages…")
for lang in LANGS:
    spfx = f"/{lang}" if lang != "en" else ""
    slug = SLUG[lang]["privacy-policy"]
    wp(f"{spfx}/{slug}/", build_privacy_policy(lang))

print("Building surf conditions pages...")
for lang in LANGS:
    pfx  = LANG_PFX[lang]
    spfx = f"/{lang}" if lang != "en" else ""
    slug = SLUG[lang].get("surf-conditions", "surf-conditions")
    wp(f"{spfx}/{slug}/", build_surf_conditions_page(lang))
    print(f"  ✅ {lang}: surf-conditions")

    print(f"  ✅ {lang}: {spfx}/{slug}/")

print("Building island guide articles…")
_island_guides = load_island_guides()
for _igi, _g in enumerate(_island_guides):
    for _lg in LANGS:
        _rp = island_guide_href_path(_lg, _g).lstrip("/")
        wp("/" + _rp, build_island_guide_page(_g, _lg, _island_guides, _igi))
if _island_guides:
    print(f"  ✅ island guides: {len(_island_guides)} × {len(LANGS)} languages")
    patch_island_hub_guides_section(_island_guides)
    print("  ✅ island hub pages: guides section patched")
else:
    print("  (no island_guides manifest — skip)")

# Keep legacy NL/AR island links valid when localized hub pages are not generated.
wp("/nl/eiland/", make_redirect("/nl/island/"))
wp("/ar/ngor-island/", make_redirect("/ar/island/"))

print("Rebuilding Super FAQ (full nl/ar copy) + blog HTML from articles_v2…")
_scripts_dir = os.path.join(_BASE_DIR, "scripts")
_rc_faq = subprocess.run(
    [sys.executable, os.path.join(_scripts_dir, "build_faq.py"), "--faq-only"],
    cwd=_BASE_DIR,
)
_rc_blog = subprocess.run(
    [sys.executable, os.path.join(_scripts_dir, "build_blog.py")],
    cwd=_BASE_DIR,
)
if _rc_faq.returncode != 0:
    print("WARNING: FAQ legacy build failed (exit %s)" % _rc_faq.returncode)
if _rc_blog.returncode != 0:
    print("WARNING: blog legacy rebuild failed (exit %s)" % _rc_blog.returncode)
print("Patching <head> on FAQ/blog output (fonts, asset version)…")
patch_head_all_pages()

print("Refreshing footer on all HTML pages (GMB badge + translations)…")
patch_all_footers()

print("Injecting structured data (JSON-LD) on homepages…")
inject_homepage_jsonld()

print("Injecting Organization+AggregateRating schema on non-blog pages…")
inject_nonblog_org_schema()

print("Removing legacy floating WhatsApp button (#float-wa) from all HTML…")
patch_remove_float_wa_all()

print("Patching Arabic WhatsApp wording (all /ar/ HTML)…")
patch_ar_whatsapp_word_in_html_all()

# Verify
with open(f'{DEMO_DIR}/booking/index.html') as f: h = f.read()
scripts   = len([m for m in re.finditer(r'<script(?!\s+src)', h)])
form_cards = h.count('form-card')
divs_open  = h.count('<div')
divs_close = h.count('</div>')
print(f"\nEN booking verification: scripts={scripts} form-card={form_cards} divs={divs_open}/{divs_close}")

print("Injecting CMP (Google Consent Mode V2) site-wide…")
patch_cmp_all_pages()

print("Refreshing home nav+footer (latest localized chrome)…")
patch_home_nav_footer_all()

print("Patching canonical + hreflang clusters (all index pages)…")
patch_hreflang_canonical_all_pages()
verify_hreflang_alternate_count()
patch_target_blank_rel_all()

def patch_heading_hierarchy_all():
    """Fix H2→H4 jumps across all generated HTML:
    - <h4 style="margin:20px 0 8px;color:var(--navy)"> → <h3 …> (inline-styled article sub-headings)
    - <h4 class="faq-inline-q"> → <h3 class="faq-inline-q"> (FAQ bold-line headings)
    - plain <h4> inside prose sections → <h3>
    - footer h4 → p.footer-col-title (navigation labels, not content headings)
    Only touches files that actually need changes.
    """
    import re as _re
    from pathlib import Path as _Path
    touched = 0

    # Pattern 1: inline-styled h4 (article sub-headings with margin/color)
    _INLINE_H4 = _re.compile(
        r'<h4(\s+style="[^"]*margin:20px[^"]*"[^>]*)>',
        _re.I
    )
    # Pattern 2: faq-inline-q h4
    _FAQ_H4 = _re.compile(r'<h4(\s+class="faq-inline-q"[^>]*)>', _re.I)
    _FAQ_H4_CLOSE = '</h4>'

    # Pattern 3: footer h4 → p.footer-col-title (inside <footer>)
    _FOOTER_H4_OPEN = _re.compile(r'<h4>(?=(?:Explore|Explorer|Explorar|Esplora|Erkunden|Verkennen|استكشاف|Contact|Contatti|Kontakt|Follow|Suivez-nous|Síguenos|Seguici|Folgen|Accréditation|Akkreditierung|Accreditamento|Accreditatie|الاعتماد|Acreditación))', _re.I)

    for html_path in _Path(DEMO_DIR).rglob("*.html"):
        try:
            h = html_path.read_text(encoding='utf-8', errors='replace')
        except Exception:
            continue
        orig = h

        # Fix inline-styled h4 → h3
        h = _INLINE_H4.sub(r'<h3\1>', h)
        h = h.replace('<h4 style="margin:20px 0 8px;color:var(--navy)">', '<h3 style="margin:20px 0 8px;color:var(--navy)">')
        # Fix corresponding closing tags (only safe when h4 was inline-styled or faq)
        # We use a paired approach: count replacements to match open/close
        if '<h3 style="margin:20px 0 8px;color:var(--navy)">' in h:
            # Replace </h4> that follow these specific opens
            # Since inline styles are unique, replace all occurrences in sequence
            pass  # closing tag handled below

        # Fix faq-inline-q h4 → h3
        h = _FAQ_H4.sub(r'<h3\1>', h)

        # Fix footer navigation h4 → p.footer-col-title
        h = _FOOTER_H4_OPEN.sub('<p class="footer-col-title">', h)

        # Now fix orphan </h4> where a corresponding <h4> no longer exists
        # Strategy: count <h4> vs </h4> and fix imbalance
        opens = len(_re.findall(r'<h4\b', h))
        closes = h.count('</h4>')
        while closes > opens:
            # Replace last </h4> that doesn't have a matching <h4> open
            # Heuristic: replace </h4> that follow a <h3 (i.e. we just changed the open)
            h = h.replace('</h4>', '</h3>', 1)
            closes -= 1

        if h != orig:
            html_path.write_text(h, encoding='utf-8')
            touched += 1

    print(f"  heading hierarchy: fixed h4→h3 in {touched} HTML files")

patch_heading_hierarchy_all()

write_sitemaps_and_robots()
patch_legacy_public_host_all()

# Copy FSS federation logos from content/images to assets
_fss_logo_src = os.path.join(_BASE_DIR, "content", "images", "logo-federation.png")
_fss_logo_dst = os.path.join(DEMO_DIR, "assets", "images", "logo-federation.png")
if os.path.isfile(_fss_logo_src):
    shutil.copy2(_fss_logo_src, _fss_logo_dst)
    print("✓ logo-federation.png copied to assets/images/")
_fss_tp_src = os.path.join(_BASE_DIR, "content", "images", "logo-fede-transparant.png")
_fss_tp_dst = os.path.join(DEMO_DIR, "assets", "images", "logo-fede-transparant.png")
if os.path.isfile(_fss_tp_src):
    shutil.copy2(_fss_tp_src, _fss_tp_dst)
    print("✓ logo-fede-transparant.png copied to assets/images/")

# Copy static/ folder (CMS admin, etc.) into the output
_static_src = os.path.join(_BASE_DIR, "static")
if os.path.isdir(_static_src):
    for _root, _dirs, _files in os.walk(_static_src):
        for _fname in _files:
            _src_path = os.path.join(_root, _fname)
            _rel = os.path.relpath(_src_path, _static_src)
            _dst_path = os.path.join(DEMO_DIR, _rel)
            os.makedirs(os.path.dirname(_dst_path), exist_ok=True)
            shutil.copy2(_src_path, _dst_path)
    print(f"✓ static/ copied to {DEMO_DIR}")

def patch_webp_images_all():
    """Replace large PNG image references with pre-generated WebP equivalents."""
    REPLACEMENTS = [
        ("logo-federation.png",  "logo-federation.webp"),
        ("icon-location.png",    "icon-location.webp"),
        ("icon-summary.png",     "icon-summary.webp"),
        ("icon-coaching.png",    "icon-coaching.webp"),
        ("icon-federation.png",  "icon-federation.webp"),
        ("icon-checklist.png",   "icon-checklist.webp"),
        ("icon-calendar.png",    "icon-calendar.webp"),
    ]
    from pathlib import Path as _Path
    changed = 0
    for html_path in _Path(DEMO_DIR).rglob("*.html"):
        try:
            content = html_path.read_text(errors="replace")
            new_content = content
            for old, new in REPLACEMENTS:
                new_content = new_content.replace(old, new)
            if new_content != content:
                html_path.write_text(new_content, encoding="utf-8")
                changed += 1
        except Exception:
            pass
    print(f"  images: replaced PNG→WebP in {changed} HTML files")

def patch_chart_defer_all():
    """Wrap Chart.js initialisation in an IntersectionObserver on surf-conditions pages."""
    surf_pages = [
        "surf-conditions/index.html",
        "fr/conditions-surf/index.html",
        "es/condiciones-surf/index.html",
        "it/condizioni-surf/index.html",
        "de/surf-bedingungen/index.html",
        "nl/surf-condities/index.html",
        "ar/surf-conditions/index.html",
    ]
    OBSERVER = (
        "(function(){"
        "var _s=document.querySelector('.sc-chart-wrap');"
        "if(!_s||_s.getBoundingClientRect().top<window.innerHeight+400){"
        "_runCharts();"
        "}else{"
        "var _o=new IntersectionObserver(function(e){"
        "if(e[0].isIntersecting){_o.disconnect();_runCharts();}"
        "},{rootMargin:'400px',threshold:0});"
        "_o.observe(_s);"
        "}"
        "})();"
    )
    # Pattern 1: virgin unpatched pages
    OLD_CALL = "  loadCJS(function(){"
    OLD_TAIL = "    });\n  });\n})();\n</script>"
    NEW_CALL = "  function _runCharts(){loadCJS(function(){"
    NEW_TAIL = "    });\n  });\n}\n" + OBSERVER + "\n})();\n</script>"
    # Pattern 2: wrongly patched pages (missing loadCJS close `});`)
    WRONG_TAIL = "    });\n  }\n  " + OBSERVER + "\n})();\n</script>"
    FIXED_TAIL = NEW_TAIL  # same target

    changed = 0
    for rel in surf_pages:
        p = os.path.join(DEMO_DIR, rel)
        if not os.path.isfile(p):
            continue
        with open(p, encoding="utf-8", errors="replace") as f:
            html = f.read()
        # Already correctly patched
        if NEW_TAIL in html:
            continue
        patched = False
        if OLD_CALL in html and OLD_TAIL in html:
            html = html.replace(OLD_CALL, NEW_CALL).replace(OLD_TAIL, NEW_TAIL)
            patched = True
        elif WRONG_TAIL in html:
            html = html.replace(WRONG_TAIL, FIXED_TAIL)
            patched = True
        if patched:
            with open(p, "w", encoding="utf-8") as f:
                f.write(html)
            changed += 1
    print(f"  chart.js: deferred with IntersectionObserver on {changed} surf-conditions pages")

patch_webp_images_all()
patch_chart_defer_all()

# Build enhanced gallery pages with tag filter system
import subprocess as _subprocess
_gallery_script = os.path.join(_BASE_DIR, "scripts", "build_gallery_enhanced.py")
if os.path.isfile(_gallery_script):
    result = _subprocess.run([sys.executable, _gallery_script], capture_output=True, text=True)
    if result.returncode == 0:
        print("  gallery: enhanced gallery with filters built ✅")
    else:
        print(f"  gallery: build_gallery_enhanced.py error: {result.stderr[:300]}")

# ── Mobile performance: preload LCP, defer cookie CSS, content-visibility ──────
def _mobile_perf_patch():
    import re as _re
    _MOBILE_CSS = """
/* === MOBILE PERFORMANCE & UX === */
/* Touch targets */
.btn,.nav-link,.lang-dd-btn,.lang-dd-item,.nav-wa,.faq-q,.nav-toggle,
.gallery-item,.footer-flag-link,.footer-col a,.footer-pp-link{min-height:44px}
.nav-link{display:flex;align-items:center}
@media(hover:none){.btn:hover{transform:none}.card:hover{box-shadow:var(--s-sm)}.gallery-item:hover{transform:none}.feat:hover{transform:none}}
@media(max-width:768px){
  .hero-badge-corner{display:none}
  .scroll-indicator{display:none}
  .stats-bar .stats-inner{gap:32px}
  .section,.section-sm{padding:56px 0}
  .split{grid-template-columns:1fr;gap:32px}
  .split-img img{height:260px}
  .main-hero-h1{font-size:clamp(28px,9vw,44px)}
  .main-hero-tagline{font-size:14px}
  .main-hero-actions{gap:10px}
  .cta-band{padding:56px 0}
  .container{padding:0 18px}
  .s-title{font-size:clamp(24px,6vw,38px)}
}
@media(max-width:400px){
  .main-hero-h1{font-size:28px}
  .btn-lg{padding:13px 24px;font-size:13px}
  .nav-inner{padding:0 16px;height:60px}
  .nav-logo img{height:36px}
}
body{max-width:100vw;overflow-x:hidden}
"""
    _css_path = os.path.join(DEMO_DIR, "assets", "css", "ngor-surfcamp.css")
    if os.path.isfile(_css_path):
        _css = open(_css_path, encoding="utf-8").read()
        if "MOBILE PERFORMANCE" not in _css:
            _css += _MOBILE_CSS
            open(_css_path, "w", encoding="utf-8").write(_css)

    _FONT_PRELOADS = (
        '<link rel="preload" href="/assets/fonts/UcC73FwrK3iLTeHuS_nVMrMxCp50SjIa1ZL7W0Q5nw.woff2" as="font" type="font/woff2" crossorigin>\n'
        '<link rel="preload" href="/assets/fonts/1Ptug8zYS_SKggPNyC0IT4ttDfA.woff2" as="font" type="font/woff2" crossorigin>\n'
    )
    _CC_OLD = '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/vanilla-cookieconsent@3/dist/cookieconsent.css">'
    _CC_NEW = '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/vanilla-cookieconsent@3/dist/cookieconsent.css" media="print" onload="this.media=\'all\'">'

    _patched = 0
    for _root, _dirs, _files in os.walk(DEMO_DIR):
        for _fname in _files:
            if not _fname.endswith(".html"):
                continue
            _p = os.path.join(_root, _fname)
            _html = open(_p, encoding="utf-8", errors="replace").read()
            _mod = False

            # Fix duplicate fetchpriority="high" attrs on img tags (defensive cleanup)
            if _html.count('fetchpriority="high"') > 1:
                def _dedup_fp(m):
                    t = m.group(0)
                    fi = t.find('fetchpriority="high"')
                    if fi < 0 or t.count('fetchpriority') <= 1:
                        return t
                    after = t[fi + len('fetchpriority="high"'):]
                    cleaned = t[:fi + len('fetchpriority="high"')] + \
                              after.replace(' fetchpriority="high"', '').replace('fetchpriority="high" ', '')
                    return cleaned
                new_html = _re.sub(r'<img[^>]+>', _dedup_fp, _html)
                if new_html != _html:
                    _html = new_html
                    _mod = True

            # Hero LCP preload — main-hero / blog-hub-header background images
            _m = _re.search(r'class="(?:main-hero|blog-hub-header)[^"]*"\s+style="background-image:url\([\'"]?([^\'")\s]+)[\'"]?\)"', _html)
            if not _m:
                _m = _re.search(r'style="background-image:url\([\'"]?([^\'")\s]+)[\'"]?\)"\s[^>]*class="(?:main-hero|blog-hub-header)', _html)
            if _m and 'rel="preload"' not in _html:
                _tag = f'<link rel="preload" as="image" href="{_m.group(1)}" fetchpriority="high">\n'
                _html = _html.replace("</head>", _tag + "</head>", 1)
                _mod = True

            # Home page LCP: preload first hg-img (gallery strip)
            _hg = _re.search(r'<img class="hg-img hg-active"\s+src="([^"]+)"', _html)
            if _hg and 'rel="preload"' not in _html:
                _tag = f'<link rel="preload" as="image" href="{_hg.group(1)}" fetchpriority="high">\n'
                _html = _html.replace("</head>", _tag + "</head>", 1)
                _mod = True
            # Font preloads
            if 'preload" href="/assets/fonts/' not in _html:
                _html = _html.replace("</head>", _FONT_PRELOADS + "</head>", 1)
                _mod = True
            # Cookie consent defer
            if _CC_OLD in _html:
                _html = _html.replace(_CC_OLD, _CC_NEW)
                _mod = True
            if _mod:
                open(_p, "w", encoding="utf-8").write(_html)
                _patched += 1
    print(f"  perf: mobile optimizations applied to {_patched} HTML files ✅")

_mobile_perf_patch()

# ── Ensure FAQ link is in the nav of static pages not fully regenerated ──
def _patch_faq_in_nav():
    import re as _re
    _PAGES = [
        ("island/index.html",           "",     "FAQ"),
        ("getting-here/index.html",     "",     "FAQ"),
        ("fr/ile/index.html",           "/fr",  "FAQ"),
        ("fr/comment-venir/index.html", "/fr",  "FAQ"),
        ("es/isla/index.html",          "/es",  "FAQ"),
        ("es/como-llegar/index.html",   "/es",  "FAQ"),
        ("it/isola/index.html",         "/it",  "FAQ"),
        ("it/come-arrivare/index.html", "/it",  "FAQ"),
        ("de/insel/index.html",         "/de",  "FAQ"),
        ("de/anreise/index.html",       "/de",  "FAQ"),
        ("nl/bereikbaarheid/index.html","/nl",  "FAQ"),
        ("ar/getting-here/index.html",  "/ar",  "الأسئلة الشائعة"),
        ("da/oe/index.html",            "/da",  "FAQ"),
        ("da/getting-here/index.html",  "/da",  "FAQ"),
        ("pt/ilha/index.html",          "/pt",  "FAQ"),
        ("pt/como-chegar/index.html",   "/pt",  "FAQ"),
    ]
    _patched = 0
    for _rel, _pfx, _label in _PAGES:
        _fp = os.path.join(DEMO_DIR, _rel)
        if not os.path.isfile(_fp):
            continue
        _html = open(_fp, errors="replace").read()
        if "faq" in _html[:_html.find("</nav>")].lower():
            continue
        _faq_link = f'<a href="{_pfx}/faq/" class="nav-link">{_label}</a>'
        _new = _re.sub(
            r'(<a\s[^>]*class="nav-link[^"]*nav-cta[^"]*"[^>]*>)',
            _faq_link + r"\1", _html, count=1
        )
        if _new != _html:
            open(_fp, "w", encoding="utf-8").write(_new)
            _patched += 1
    if _patched:
        print(f"  nav: FAQ added to {_patched} static pages ✅")

_patch_faq_in_nav()

# ── Fix PT/DA untranslated content (footer + UI strings) ─────────────────────
def _patch_pt_da_translations():
    import re as _re
    _BASE = DEMO_DIR
    _PT = [
        ('Surf Camp en Senegal en Ngor Surfcamp', 'Surf Camp no Senegal no Ngor Surfcamp'),
        ('Vive la relajada vida isleña, la cálida hospitalidad senegalesa y el acceso fácil a algunos de los mejores surf spots de Dakar.',
         'Vive a vida relaxada da ilha, a calorosa hospitalidade senegalesa e o acesso fácil a alguns dos melhores spots de surf de Dakar.'),
        ('Isla de Ngor · Dakar · Senegal', 'Ilha de Ngor · Dakar · Senegal'),
        ('Licenciado por la Federación Senegalesa', 'Licenciado pela Federação Senegalesa'),
        ('Todos los niveles bienvenidos', 'Todos os níveis bem-vindos'),
        ('Abierto todo el año', 'Aberto todo o ano'),
        ('The essentials', 'O essencial'),
        ('Cómo llegar', 'Como chegar'),
        ('Llegar a Ngor Island', 'Chegar à Ilha de Ngor'),
        ('Todo en Ngor Surfcamp', 'Tudo no Ngor Surfcamp'),
        ('Descubrir', 'Descobrir'),
        ('Habitaciones, piscina, vista al mar, comidas senegalesas. Tu hogar junto al océano.',
         'Quartos, piscina, vista para o mar, refeições senegalesas. A tua casa junto ao oceano.'),
        ('Sin coches, olas de clase mundial, el legado de The Endless Summer.',
         'Sem carros, ondas de classe mundial, o legado de The Endless Summer.'),
        ('Análisis de vídeo profesional, sesiones personalizadas, todos los niveles.',
         'Análise de vídeo profissional, sessões personalizadas, todos os níveis.'),
        ('Lo que dicen los surfistas', 'O que dizem os surfistas'),
        ('54 reseñas', '54 avaliações'),
        ('Ver todos en Google', 'Ver todos no Google'),
        ('Dejar una reseña', 'Deixar uma avaliação'),
        ('Listo para surfear? Reserva tu estancia.', 'Pronto para surfar? Reserva a tua estadia.'),
        ('Planifica tu Viaje', 'Planeia a tua Viagem'),
        ('>Explore<', '>Explorar<'), ('>Contact<', '>Contacto<'),
        ('>Follow Us<', '>Siga-nos<'), ('>Surf Forecast<', '>Previsão Surf<'),
        ('>Getting here<', '>Como chegar<'), ('All rights reserved', 'Todos os direitos reservados'),
        (_re.compile(r'Premium surf camp on Ngor Island, Dakar, Senegal\. All levels welcome\.'),
         'Surf camp premium na Ilha de Ngor, Dakar, Senegal. Todos os níveis bem-vindos.'),
    ]
    _DA = [
        ('The essentials', 'Det vigtigste'),
        ('All levels welcome', 'Alle niveauer velkomne'),
        ('>Explore<', '>Udforsk<'), ('>Contact<', '>Kontakt<'),
        ('>Follow Us<', '>Følg os<'), ('>Surf Forecast<', '>Surfudsigt<'),
        ('>Getting here<', '>Kom hertil<'), ('All rights reserved', 'Alle rettigheder forbeholdes'),
        (_re.compile(r'Premium surf camp on Ngor Island, Dakar, Senegal\. All levels welcome\.'),
         'Premium surfcamp på Ngor Island, Dakar, Senegal. Alle niveauer velkomne.'),
    ]
    _count = 0
    for _lang, _repls, _folder in [('pt', _PT, 'pt'), ('da', _DA, 'da')]:
        _dir = os.path.join(_BASE, _folder)
        if not os.path.isdir(_dir): continue
        for _root, _dirs, _files in os.walk(_dir):
            for _f in _files:
                if not _f.endswith('.html'): continue
                _fp = os.path.join(_root, _f)
                _html = open(_fp, errors='replace').read()
                _orig = _html
                for _old, _new in _repls:
                    if isinstance(_old, _re.Pattern):
                        _html = _old.sub(_new, _html)
                    elif _old in _html:
                        _html = _html.replace(_old, _new)
                if _html != _orig:
                    open(_fp, 'w', encoding='utf-8').write(_html)
                    _count += 1
    if _count:
        print(f"  i18n: PT/DA translations fixed on {_count} pages ✅")

_patch_pt_da_translations()

