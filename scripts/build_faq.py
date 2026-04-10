# -*- coding: utf-8 -*-
"""
Build improved Surfing page (using live site content) + Super FAQ page
All site languages (incl. nl, ar).
"""
import argparse
import importlib.util
import json, os, re

from faq_ar_nl_merge import merge_faq_sections

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_site_assets_spec = importlib.util.spec_from_file_location(
    "site_assets", os.path.join(_BASE_DIR, "scripts", "site_assets.py")
)
_site_assets_mod = importlib.util.module_from_spec(_site_assets_spec)
_site_assets_spec.loader.exec_module(_site_assets_mod)
ASSET_VERSION = _site_assets_mod.ASSET_VERSION
ASSET_CSS_MAIN = _site_assets_mod.ASSET_CSS_MAIN
CONTENT  = os.path.join(_BASE_DIR, "content")
PAGES_D  = f"{CONTENT}/pages"
DEMO_DIR = os.path.join(_BASE_DIR, "cloudflare-demo")
SITE_URL = (os.environ.get("PUBLIC_SITE_URL") or "https://surf-camp-senegal.vercel.app").strip().rstrip("/")

_WIX = "/assets/images/wix"
LOGO = f"{_WIX}/c2467f_a31779010ce34c4c8c61cc5868d81f31.webp"

LANGS       = ["en","fr","es","it","de","nl","ar"]
LANG_NAMES  = {"en":"English","fr":"Français","es":"Español","it":"Italiano","de":"Deutsch","nl":"Nederlands","ar":"العربية"}
LANG_LOCALE = {"en":"en","fr":"fr-FR","es":"es-ES","it":"it-IT","de":"de-DE","nl":"nl-NL","ar":"ar-MA"}
LANG_PREFIX = {"en":"","fr":"/fr","es":"/es","it":"/it","de":"/de","nl":"/nl","ar":"/ar"}

IMGS = {
    "surf":   f"{_WIX}/11062b_89a070321f814742a620b190592d51ad.webp",
    "surf2":  "/assets/images/gallery/79fd3518-a569-479b-9980-5af713fda22c_1c4694d0.webp",
    "surf3":  f"{_WIX}/df99f9_961b0768e713457f93025f4ce6fb1419.webp",
    "surf4":  f"{_WIX}/df99f9_0d4a03baee4f46b68bc1aa085ed28e35.webp",
    "surf5":  f"{_WIX}/df99f9_796b6115065145eabddfe3ae32b8f4d5.webp",
    "surf6":  f"{_WIX}/df99f9_04a8bba9fda34e22b7b5feae890d79cf.webp",
    "coach":  f"{_WIX}/df99f9_9e239b5550f949e998b00f8e16417fa8.webp",
    "island": f"{_GAL}/island_hero.webp",
    "ngor_r": f"{_WIX}/11062b_7f89d2db0ace4027ac4a00928a6aca08.webp",
    "airport":f"{_WIX}/df99f9_d6e404dd3cf74396b6ea874cb7021a27.webp",
    "boat":   f"{_WIX}/df99f9_4edccd3c01ca4f8ba06ed25c80e1eccb.webp",
    "ngor_island_map": f"{_WIX}/df99f9_d81668a18a9d49d1b5ebb0ea3a0abbc7.webp",
}

ICONS_DIR = f"{DEMO_DIR}/assets/images/icons"
ICO_BASE  = "/assets/images/icons"

def ico(name, size=28, alt=""):
    local = f"{ICONS_DIR}/{name}.png"
    if os.path.exists(local):
        return f'<img src="{ICO_BASE}/{name}.png" alt="{alt}" width="{size}" height="{size}" style="display:inline-block;object-fit:contain">'
    return f'<span style="width:{size}px;height:{size}px;display:inline-flex;align-items:center;justify-content:center;opacity:0.7">◈</span>'

def load(p):
    if os.path.exists(p):
        try:
            with open(p) as f: return json.load(f)
        except: return None
    return None

def fix_em(t):
    if not t: return ""
    s = str(t).replace(" — ",", ").replace("—",",").replace("\u2014",",").replace(" – ",", ").replace("–",",")
    s = re.sub(r'\*\*(.*?)\*\*', r'\1', s)
    s = re.sub(r'\*(.*?)\*', r'\1', s)
    s = re.sub(r'\*+', '', s)
    return re.sub(r',\s*,', ',', s)

FLAG_SVG = {
    "en":'<svg viewBox="0 0 60 40"><rect width="60" height="40" fill="#012169"/><path d="M0,0 L60,40 M60,0 L0,40" stroke="#fff" stroke-width="8"/><path d="M0,0 L60,40 M60,0 L0,40" stroke="#C8102E" stroke-width="5"/><path d="M30,0 V40 M0,20 H60" stroke="#fff" stroke-width="12"/><path d="M30,0 V40 M0,20 H60" stroke="#C8102E" stroke-width="8"/></svg>',
    "fr":'<svg viewBox="0 0 60 40"><rect width="20" height="40" fill="#002395"/><rect x="20" width="20" height="40" fill="#fff"/><rect x="40" width="20" height="40" fill="#ED2939"/></svg>',
    "es":'<svg viewBox="0 0 60 40"><rect width="60" height="40" fill="#c60b1e"/><rect y="10" width="60" height="20" fill="#ffc400"/></svg>',
    "it":'<svg viewBox="0 0 60 40"><rect width="20" height="40" fill="#009246"/><rect x="20" width="20" height="40" fill="#fff"/><rect x="40" width="20" height="40" fill="#CE2B37"/></svg>',
    "de":'<svg viewBox="0 0 60 40"><rect width="60" height="13" fill="#000"/><rect y="13" width="60" height="14" fill="#DD0000"/><rect y="27" width="60" height="13" fill="#FFCE00"/></svg>',
    "nl":'<svg viewBox="0 0 60 40"><rect width="60" height="13" fill="#AE1C28"/><rect y="13" width="60" height="14" fill="#fff"/><rect y="27" width="60" height="13" fill="#21468B"/></svg>',
    "ar":'<svg viewBox="0 0 60 40"><rect width="60" height="40" fill="#C1272D"/><path d="M30,10 L31.8,16.1 L38.5,16.1 L33,19.9 L35,26 L30,22.1 L25,26 L27,19.9 L21.5,16.1 L28.2,16.1 Z" fill="none" stroke="#006233" stroke-width="1.2"/></svg>',
}
WA_ICO = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>'
MENU_ICO = '<svg viewBox="0 0 24 24" fill="none"><path d="M3 7h18M3 12h18M3 17h12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>'
CHEV_ICO = '<svg viewBox="0 0 16 16" fill="none"><path d="M4 6l4 4 4-4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
CHECK_ICO= '<svg viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>'

def flag(lang, size=22):
    h = round(size*0.667)
    return f'<span style="width:{size}px;height:{h}px;display:inline-flex;border-radius:3px;overflow:hidden;flex-shrink:0;box-shadow:0 1px 3px rgba(0,0,0,0.22)">{FLAG_SVG.get(lang,"")}</span>'

def lang_dd(cur, page_slug):
    s = "/" + page_slug.strip("/") if page_slug.strip("/") else ""
    opts = "".join([f'<a class="lang-dd-item" href="{"/" + l + s + "/" if l!="en" else s+"/"}" hreflang="{LANG_LOCALE[l]}">{flag(l,18)} {LANG_NAMES[l]}</a>' for l in LANGS if l!=cur])
    return f'<div class="lang-dd" id="lang-dd"><button class="lang-dd-btn" onclick="toggleLangDD(event)">{flag(cur,20)} {cur.upper()} <span style="width:14px;height:14px;display:inline-flex">{CHEV_ICO}</span></button><div class="lang-dd-menu" role="menu">{opts}</div></div>'

GLOBAL_JS = """<script>
window.addEventListener('scroll',()=>{const el=document.getElementById('scroll-progress');if(el){const pct=(scrollY/(document.body.scrollHeight-innerHeight))*100;el.style.width=Math.min(pct,100)+'%';}},{passive:true});
window.addEventListener('scroll',()=>{const nav=document.getElementById('nav');if(nav)nav.classList.toggle('scrolled',scrollY>30);},{passive:true});
const obs=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting)e.target.classList.add('up');}),{threshold:0.09});
document.querySelectorAll('.reveal').forEach(el=>obs.observe(el));
function getBasePath(){const p=location.pathname;for(const l of['fr','es','it','de','nl','ar']){if(p===('/'+l)||p==='/'+l+'/')return'/';if(p.startsWith('/'+l+'/'))return p.slice(l.length+1)||'/';}return p;}
function toggleLangDD(e){e.stopPropagation();document.getElementById('lang-dd').classList.toggle('open');}
document.addEventListener('click',e=>{const d=document.getElementById('lang-dd');if(d&&!d.contains(e.target))d.classList.remove('open');});
function toggleMenu(){document.getElementById('nav-links').classList.toggle('open');}
document.addEventListener('click',e=>{const nl=document.getElementById('nav-links');const nt=document.getElementById('nav-toggle');if(nl&&nt&&!nl.contains(e.target)&&!nt.contains(e.target))nl.classList.remove('open');});
document.querySelectorAll('.faq-q').forEach(q=>q.addEventListener('click',()=>{const it=q.closest('.faq-item');it.classList.toggle('open');}));
const lb=document.getElementById('lb'),lbImg=document.getElementById('lb-img'),lbCls=document.getElementById('lb-close');
if(lb){document.querySelectorAll('.gallery-item').forEach(i=>i.addEventListener('click',()=>{lbImg.src=i.querySelector('img').src;lb.classList.add('open');}));lb.addEventListener('click',e=>{if(e.target===lb)lb.classList.remove('open');});lbCls&&lbCls.addEventListener('click',()=>lb.classList.remove('open'));document.addEventListener('keydown',e=>{if(e.key==='Escape')lb.classList.remove('open');});}
document.querySelectorAll('.gallery-item img').forEach(img=>{if(img.complete&&img.naturalWidth>0)img.classList.add('is-loaded');else img.addEventListener('load',()=>img.classList.add('is-loaded'));});
</script>"""

def nav_html(active, lang, pfx, page_slug=""):
    NAV=[("",{"en":"Home","fr":"Accueil","es":"Inicio","it":"Home","de":"Start","nl":"Home","ar":"الرئيسية"}),("/surf-house",{"en":"Surf House","fr":"Surf House","es":"Surf House","it":"Surf House","de":"Surf House","nl":"Surf House","ar":"بيت الأمواج"}),("/island",{"en":"Island","fr":"Île","es":"Isla","it":"Isola","de":"Insel","nl":"Eiland","ar":"الجزيرة"}),("/surfing",{"en":"Surfing","fr":"Surf","es":"Surf","it":"Surf","de":"Surfen","nl":"Surfen","ar":"ركوب الأمواج"}),("/blog",{"en":"Blog","fr":"Blog","es":"Blog","it":"Blog","de":"Blog","nl":"Blog","ar":"المدونة"}),("/gallery",{"en":"Gallery","fr":"Galerie","es":"Galería","it":"Galleria","de":"Galerie","nl":"Galerij","ar":"معرض الصور"}),("/booking",{"en":"Book Now","fr":"Réserver","es":"Reservar","it":"Prenota","de":"Buchen","nl":"Boeken","ar":"احجز الآن"})]
    items="".join([f'<a href="{pfx}{s}/" class="nav-link{" active" if s.strip("/")==active.strip("/") or (not s and not active) else ""}{ " nav-cta" if s=="/booking" else ""}">{l.get(lang,l["en"])}</a>' for s,l in NAV])
    return f'<nav id="nav"><div class="nav-inner"><a href="{pfx}/" class="nav-logo"><img src="{LOGO}" alt="Ngor Surfcamp Teranga" width="130" height="44" loading="eager"></a><div class="nav-links" id="nav-links">{items}</div><div class="nav-right">{lang_dd(lang,page_slug)}<a href="https://wa.me/221789257025" target="_blank" class="nav-wa" aria-label="WhatsApp"><span style="width:18px;height:18px;display:inline-flex">{WA_ICO}</span><span class="nav-wa-label">WhatsApp</span></a><button class="nav-toggle" id="nav-toggle" aria-label="Menu" onclick="toggleMenu()"><span style="width:22px;height:22px;display:inline-flex;color:#fff">{MENU_ICO}</span></button></div></div></nav>'

def footer_html(lang, pfx):
    IG='<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>'
    TT='<svg viewBox="0 0 24 24" fill="currentColor"><path d="M19.59 6.69a4.83 4.83 0 01-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 01-2.88 2.5 2.89 2.89 0 01-2.89-2.89 2.89 2.89 0 012.89-2.89c.28 0 .54.04.79.1V9.01a6.28 6.28 0 00-.79-.05 6.34 6.34 0 00-6.34 6.34 6.34 6.34 0 006.34 6.34 6.34 6.34 0 006.33-6.34V8.69a8.22 8.22 0 004.84 1.56V6.79a4.85 4.85 0 01-1.07-.1z"/></svg>'
    LINKS=[("/surf-house",{"en":"Surf House","fr":"Surf House","es":"Surf House","it":"Surf House","de":"Surf House","nl":"Surf House","ar":"بيت الأمواج"}),("/island",{"en":"Island","fr":"Île","es":"Isla","it":"Isola","de":"Insel","nl":"Eiland","ar":"الجزيرة"}),("/surfing",{"en":"Surfing","fr":"Surf","es":"Surf","it":"Surf","de":"Surfen","nl":"Surfen","ar":"ركوب الأمواج"}),("/blog",{"en":"Blog","fr":"Blog","es":"Blog","it":"Blog","de":"Blog","nl":"Blog","ar":"المدونة"}),("/gallery",{"en":"Gallery","fr":"Galerie","es":"Galería","it":"Galleria","de":"Galerie","nl":"Galerij","ar":"معرض الصور"}),("/faq",{"en":"FAQ","fr":"FAQ","es":"FAQ","it":"FAQ","de":"FAQ","nl":"FAQ","ar":"الأسئلة الشائعة"}),("/booking",{"en":"Book Now","fr":"Réserver","es":"Reservar","it":"Prenota","de":"Buchen","nl":"Boeken","ar":"احجز الآن"})]
    lk="\n".join([f'<a href="{pfx}{s}/">{l.get(lang,l["en"])}</a>' for s,l in LINKS])
    fl=" ".join([f'<a href="{"" if l=="en" else "/"+l}/" style="opacity:0.55;display:inline-flex" hreflang="{LANG_LOCALE[l]}" title="{LANG_NAMES[l]}">{flag(l,22)}</a>' for l in LANGS])
    COPY={"en":"© 2025 Ngor Surfcamp Teranga. All rights reserved.","fr":"© 2025 Ngor Surfcamp Teranga. Tous droits réservés.","es":"© 2025 Ngor Surfcamp Teranga. Todos los derechos reservados.","it":"© 2025 Ngor Surfcamp Teranga. Tutti i diritti riservati.","de":"© 2025 Ngor Surfcamp Teranga. Alle Rechte vorbehalten.","nl":"© 2025 Ngor Surfcamp Teranga. Alle rechten voorbehouden.","ar":"© 2025 Ngor Surfcamp Teranga. جميع الحقوق محفوظة."}
    ABOUT={"en":"Premium surf camp on Ngor Island, Dakar, Senegal. All levels. Licensed by the Senegalese Federation of Surfing.","fr":"Surf camp premium sur l'île de Ngor, Dakar, Sénégal. Tous niveaux. Agréé Fédération Sénégalaise de Surf.","es":"Surf camp premium en la isla de Ngor, Dakar, Senegal. Todos los niveles.","it":"Surf camp premium sull'isola di Ngor, Dakar, Senegal. Tutti i livelli.","de":"Premium Surfcamp auf Ngor Island, Dakar, Senegal. Alle Level.","nl":"Premium surf camp op Ngor Island, Dakar, Senegal. Alle niveaus.","ar":"مخيم سيرف متميز في جزيرة Ngor، داكار، السنغال. جميع المستويات."}
    PP_SLUG={"en":"privacy-policy","fr":"politique-de-confidentialite","es":"politica-de-privacidad","it":"informativa-sulla-privacy","de":"datenschutzrichtlinie","nl":"privacybeleid","ar":"privacy-policy"}
    PP_LBL={"en":"Privacy Policy","fr":"Politique de confidentialité","es":"Política de privacidad","it":"Informativa sulla privacy","de":"Datenschutzrichtlinie","nl":"Privacybeleid","ar":"سياسة الخصوصية"}
    pp_href=f"{pfx}/{PP_SLUG[lang]}/"
    return f"""<footer><div class="container"><div class="footer-grid"><div><img src="{LOGO}" alt="Ngor Surfcamp Teranga" class="footer-brand-logo" loading="lazy"><p>{ABOUT[lang]}</p><div class="footer-social"><a href="https://wa.me/221789257025" target="_blank" class="soc-btn wa" aria-label="WhatsApp"><span style="width:18px;height:18px;display:inline-flex">{WA_ICO}</span></a><a href="https://www.instagram.com/ngorsurfcampteranga" target="_blank" class="soc-btn ig" aria-label="Instagram"><span style="width:18px;height:18px;display:inline-flex">{IG}</span></a><a href="https://www.tiktok.com/@ngorsurfcampteranga" target="_blank" class="soc-btn tt" aria-label="TikTok"><span style="width:18px;height:18px;display:inline-flex">{TT}</span></a></div></div><div class="footer-col"><h4>{"Explore" if lang=="en" else "Explorer" if lang=="fr" else "Explorar" if lang=="es" else "Esplora" if lang=="it" else "Erkunden" if lang=="de" else "Ontdekken" if lang=="nl" else "استكشاف"}</h4>{lk}</div><div class="footer-col"><h4>{"Contact" if lang in ["en","fr","nl"] else "Contacto" if lang=="es" else "Contatti" if lang=="it" else "Kontakt" if lang=="de" else "اتصل"}</h4><a href="https://wa.me/221789257025" target="_blank">WhatsApp: +221 78 925 70 25</a><a href="mailto:info@surfcampsenegal.com">info@surfcampsenegal.com</a></div><div class="footer-col"><h4>{"Follow Us" if lang=="en" else "Suivez-nous" if lang=="fr" else "Síguenos" if lang=="es" else "Seguici" if lang=="it" else "Folgen" if lang=="de" else "Volg ons" if lang=="nl" else "تابعنا"}</h4><a href="https://www.instagram.com/ngorsurfcampteranga" target="_blank">Instagram</a><a href="https://www.tiktok.com/@ngorsurfcampteranga" target="_blank">TikTok</a></div></div><div class="footer-bottom"><p>{COPY[lang]} &nbsp;·&nbsp; <a href="{pp_href}" class="footer-pp-link">{PP_LBL[lang]}</a></p><div style="display:flex;gap:10px;align-items:center">{fl}</div></div></div></footer>"""

def head(title, meta, lang, can="", hrl="", og=""):
    return f"""<!DOCTYPE html><html lang="{lang}"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{fix_em(title)}</title><meta name="description" content="{fix_em(meta)}">
<meta property="og:title" content="{fix_em(title)}"><meta property="og:description" content="{fix_em(meta)}">
<meta property="og:image" content="{og}"><meta name="robots" content="index,follow">
{can}{hrl}
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Raleway:ital,wght@0,300;0,400;0,600;0,700;0,800;0,900;1,400&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/css/{ASSET_CSS_MAIN}?v={ASSET_VERSION}">
</head><body><div id="scroll-progress"></div>"""

def hrl_tags(slug):
    s = "/" + slug.strip("/") if slug.strip("/") else ""
    return "\n".join([f'<link rel="alternate" hreflang="x-default" href="{SITE_URL}{s}/">',f'<link rel="alternate" hreflang="en" href="{SITE_URL}{s}/">']+[f'<link rel="alternate" hreflang="{LANG_LOCALE[l]}" href="{SITE_URL}/{l}{s}/">' for l in ["fr","es","it","de","nl","ar"]])

def can_tag(slug, lang):
    s = "/" + slug.strip("/") if slug.strip("/") else ""
    pfx = f"/{lang}" if lang!="en" else ""
    return f'<link rel="canonical" href="{SITE_URL}{pfx}{s}/">'

def close():
    return f"\n{GLOBAL_JS}\n</body>\n</html>"

# ════════════════════════════════════════════════════════════════════════════════
# IMPROVED SURFING PAGE
# ════════════════════════════════════════════════════════════════════════════════
def build_surfing_v2(lang):
    pfx = LANG_PREFIX[lang]
    p   = load(f"{PAGES_D}/{lang}_surfing.json") or {}
    h1  = fix_em(p.get("h1","Surfing in Ngor"))
    meta= fix_em(p.get("meta_description","Professional surf coaching with video analysis at Ngor Island, Dakar, Senegal."))
    title= fix_em(p.get("title_tag","Surfing in Ngor | Coaching & Waves | Ngor Surfcamp Teranga"))

    MOTTO = {"en":"Surf better, live slower, feel the difference.","fr":"Surfez mieux, vivez plus lentement, ressentez la différence.","es":"Surfa mejor, vive más lento, siente la diferencia.","it":"Surfa meglio, vivi più lentamente, senti la differenza.","de":"Besser surfen, langsamer leben, den Unterschied spüren.","nl":"Surf beter, leef langzamer, voel het verschil.","ar":"تصفح بشكل أفضل، عش بشكل أبطأ، اشعر بالفرق."}
    INTRO = {"en":"At Ngor Surfcamp Teranga, we mix world-class West African waves with laid-back island vibes and expert surf coaching that actually moves the needle. Whether you are chasing your first green wave or refining your turns, we guide your progression at your rhythm in the heart of West Africa's surf culture.","fr":"Au Ngor Surfcamp Teranga, nous combinons des vagues de classe mondiale avec l'ambiance relax de l'île et un coaching surf expert qui fait vraiment la différence. Que vous visiez votre première vague verte ou que vous affiniez vos virages, nous guidons votre progression à votre rythme.","es":"En Ngor Surfcamp Teranga, combinamos olas de clase mundial con el ambiente relajado de la isla y un coaching surf experto que marca la diferencia. Tanto si buscas tu primera ola verde como si estás refinando tus giros, guiamos tu progresión a tu ritmo.","it":"Al Ngor Surfcamp Teranga, combiniamo onde di classe mondiale con la vita rilassata dell'isola e un coaching surf esperto che fa davvero la differenza. Che tu stia inseguendo la tua prima onda verde o perfezionando le virate, guidiamo la tua progressione al tuo ritmo.","de":"Im Ngor Surfcamp Teranga verbinden wir Weltklasse-Wellen mit der entspannten Inselatmosphäre und einem Surf-Coaching, das wirklich einen Unterschied macht. Ob du deine erste grüne Welle verfolgst oder deine Kurven verfeinerst, wir begleiten deine Progression in deinem Tempo.","nl":"Bij Ngor Surfcamp Teranga combineren we wereldklasse West-Afrikaanse golven met relaxed eilandleven en expert surfcoaching. Of je nu je eerste groene golf najaagt of je techniek verfijnt, wij begeleiden jouw progressie op jouw tempo.","ar":"في Ngor Surfcamp Teranga، نجمع بين الأمواج الرائعة في غرب أفريقيا والحياة الجزيرية المريحة والتدريب الاحترافي. سواء كنت تطارد موجتك الأولى أو تصقل تقنيتك، نوجه تقدمك بوتيرتك الخاصة."}
    WHY_H = {"en":"Why Ngor Surfcamp Teranga?","fr":"Pourquoi Ngor Surfcamp Teranga ?","es":"¿Por qué Ngor Surfcamp Teranga?","it":"Perché Ngor Surfcamp Teranga?","de":"Warum Ngor Surfcamp Teranga?","nl":"Waarom Ngor Surfcamp Teranga?","ar":"لماذا Ngor Surfcamp Teranga؟"}
    TEAM_H= {"en":"Our Team","fr":"Notre Équipe","es":"Nuestro Equipo","it":"Il Nostro Team","de":"Unser Team","nl":"Ons Team","ar":"فريقنا"}
    TEAM_T= {"en":"All our instructors are local surfers with ISA qualifications and national diplomas. They surf these waves every day and know every mood, tide and shift in the break. Combined with Ngor Surfcamp's structured coaching methodology, you will progress faster than anywhere else in West Africa.","fr":"Tous nos instructeurs sont des surfeurs locaux avec des qualifications ISA et des diplômes nationaux. Ils surfent ces vagues tous les jours et connaissent chaque humeur, marée et changement du break. Combiné avec la méthodologie de coaching structurée de Ngor Surfcamp, vous progresserez plus vite qu'ailleurs en Afrique de l'Ouest.","es":"Todos nuestros instructores son surfistas locales con calificaciones ISA y diplomas nacionales. Surfean estas olas todos los días y conocen cada estado, marea y cambio en el break. Combinado con la metodología de coaching estructurada de Ngor Surfcamp, progresarás más rápido que en cualquier otro lugar de África Occidental.","it":"Tutti i nostri istruttori sono surfisti locali con qualifiche ISA e diplomi nazionali. Surfano queste onde ogni giorno e conoscono ogni umore, marea e cambiamento del break. Combinato con la metodologia di coaching strutturata di Ngor Surfcamp, progredirai più velocemente che altrove in Africa Occidentale.","de":"Alle unsere Instruktoren sind lokale Surfer mit ISA-Qualifikationen und nationalen Diplomen. Sie surfen diese Wellen täglich und kennen jede Stimmung, Gezeiten und Veränderungen des Breaks. Kombiniert mit Ngor Surfcamps strukturierter Coaching-Methodik werden Sie schneller als irgendwo sonst in Westafrika Fortschritte machen.","nl":"Al onze instructeurs zijn lokale surfers met ISA-kwalificaties en nationale diploma's. Ze surfen deze golven elke dag. Met de gestructureerde coaching van Ngor Surfcamp zul je sneller vorderen dan waar ook in West-Afrika.","ar":"جميع مدربينا متصفحون محليون حاصلون على مؤهلات ISA. يركبون هذه الأمواج يومياً. مع منهج التدريب المنظم في Ngor Surfcamp، ستتقدم بشكل أسرع من أي مكان في غرب أفريقيا."}

    SERVICES = [
        ({"en":"Professional Surf Coaching All Levels","fr":"Coaching Surf Professionnel Tous Niveaux","es":"Coaching Surf Profesional Todos Los Niveles","it":"Coaching Surf Professionale Tutti i Livelli","de":"Professionelles Surf-Coaching Alle Level"},
         {"en":"Personalized one-on-one or small group sessions, adapted to your exact level and goals. From complete beginner to pushing advanced limits.","fr":"Séances personnalisées individuelles ou en petits groupes, adaptées à votre niveau exact et vos objectifs. Du débutant complet aux limites avancées.","es":"Sesiones personalizadas individuales o en grupos pequeños, adaptadas a tu nivel exacto y objetivos. Desde principiante completo hasta límites avanzados.","it":"Sessioni personalizzate individuali o in piccoli gruppi, adattate al tuo livello esatto e ai tuoi obiettivi. Dal principiante assoluto ai limiti avanzati.","de":"Personalisierte Einzel- oder Kleingruppeneinheiten, angepasst an Ihr genaues Level. Von komplett Anfänger bis zu fortgeschrittenen Grenzen."},
         "icon-coaching"),
        ({"en":"Professional Surf Guiding","fr":"Guide Surf Professionnel","es":"Guía Surf Profesional","it":"Guida Surf Professionale","de":"Professionelle Surf-Führung"},
         {"en":"Daily guided sessions to the best break of the day. Local knowledge means you are always at the right spot for your level, tide, and swell direction.","fr":"Sessions guidées quotidiennes vers le meilleur break du jour. La connaissance locale signifie que vous êtes toujours au bon endroit pour votre niveau.","es":"Sesiones guiadas diarias al mejor break del día. El conocimiento local significa que siempre estás en el lugar correcto para tu nivel.","it":"Sessioni guidate giornaliere verso il miglior break del giorno. La conoscenza locale significa che sei sempre nel posto giusto per il tuo livello.","de":"Tägliche geführte Sessions zum besten Break des Tages. Lokales Wissen bedeutet, dass Sie immer am richtigen Spot für Ihr Level sind."},
         "icon-surf-guide"),
        ({"en":"Video Analysis","fr":"Analyse Vidéo","es":"Análisis de Vídeo","it":"Analisi Video","de":"Videoanalyse"},
         {"en":"We film your sessions and review the footage with you on a tablet on the beach. Visual feedback accelerates learning by 3-4x compared to verbal coaching alone.","fr":"Nous filmons vos sessions et analysons les images avec vous sur une tablette sur la plage. Le feedback visuel accélère l'apprentissage de 3-4x par rapport au coaching verbal seul.","es":"Filmamos tus sesiones y analizamos las imágenes contigo en una tableta en la playa. El feedback visual acelera el aprendizaje 3-4x comparado con el coaching verbal solo.","it":"Filmiamo le tue sessioni e analizziamo le riprese con te su un tablet in spiaggia. Il feedback visivo accelera l'apprendimento di 3-4x rispetto al solo coaching verbale.","de":"Wir filmen Ihre Sessions und analysieren die Aufnahmen mit Ihnen auf einem Tablet am Strand. Visuelles Feedback beschleunigt das Lernen 3-4x im Vergleich zu rein verbalems Coaching."},
         "icon-video"),
        ({"en":"Surf Theory Classes — Free","fr":"Cours de Théorie Surf — Gratuits","es":"Clases de Teoría Surf — Gratuitas","it":"Lezioni di Teoria Surf — Gratuite","de":"Surf-Theoriestunden — Kostenlos"},
         {"en":"Daily theory sessions covering: paddling technique, pop-up mechanics, reading waves, bottom turn, cutback, tide and wind effects. Free for all guests.","fr":"Sessions théorie quotidiennes couvrant : technique de paddle, mécanique du pop-up, lecture des vagues, bottom turn, cutback, effets de marée et de vent. Gratuit pour tous les invités.","es":"Sesiones de teoría diarias que cubren: técnica de remo, mecánica del pop-up, lectura de olas, bottom turn, cutback, efectos de marea y viento. Gratuito para todos los huéspedes.","it":"Sessioni di teoria giornaliere che coprono: tecnica di paddling, meccanica del pop-up, lettura delle onde, bottom turn, cutback, effetti di marea e vento. Gratuito per tutti gli ospiti.","de":"Tägliche Theoriestunden zu: Paddeltechnik, Pop-up-Mechanik, Wellenlesung, Bottom Turn, Cutback, Gezeiten- und Windeffekte. Kostenlos für alle Gäste."},
         "icon-theory"),
        ({"en":"Consistent Reef & Beach Breaks","fr":"Breaks de Récif et de Plage Consistants","es":"Breaks de Arrecife y Playa Consistentes","it":"Break di Reef e Spiaggia Consistenti","de":"Konsistente Riff- und Strand-Breaks"},
         {"en":"Ngor Right is a world-class point break for intermediate to advanced surfers. Ngor Left works on smaller days and is perfect for beginners and improvers. Multiple other spots accessible by boat depending on swell.","fr":"Ngor Right est un point break de classe mondiale pour surfeurs intermédiaires à avancés. Ngor Left fonctionne lors de petits jours et est parfait pour débutants et intermédiaires.","es":"Ngor Right es un point break de clase mundial para surfistas de intermedio a avanzado. Ngor Left funciona en días más pequeños y es perfecto para principiantes e intermedios.","it":"Ngor Right è un point break di classe mondiale per surfisti da intermedio ad avanzato. Ngor Left funziona nei giorni più piccoli ed è perfetto per principianti e intermedi.","de":"Ngor Right ist ein Weltklasse-Point-Break für Fortgeschrittene. Ngor Left funktioniert an kleineren Tagen und ist perfekt für Anfänger und Fortgeschrittene."},
         "icon-location"),
        ({"en":"Surf Trips — Swell Dependent","fr":"Surf Trips — Selon le Swell","es":"Surf Trips — Según el Swell","it":"Surf Trip — In Base al Swell","de":"Surf Trips — Swell-Abhängig"},
         {"en":"When conditions align, we organize day trips to Dakar's best surf spots by minibus: Virage, Yoff, Ouakam and beyond. Local knowledge is your advantage.","fr":"Quand les conditions s'alignent, nous organisons des excursions journalières vers les meilleurs spots de surf de Dakar en minibus : Virage, Yoff, Ouakam et plus.","es":"Cuando las condiciones se alinean, organizamos excursiones de día a los mejores spots de surf de Dakar en minibús: Virage, Yoff, Ouakam y más.","it":"Quando le condizioni si allineano, organizziamo gite giornaliere nei migliori spot surf di Dakar in minibus: Virage, Yoff, Ouakam e altro.","de":"Wenn die Bedingungen stimmen, organisieren wir Tagesausflüge zu Dakars besten Surf-Spots per Minibus: Virage, Yoff, Ouakam und mehr."},
         "icon-transfer"),
    ]

    LEVELS = [
        ({"en":"Beginner","fr":"Débutant","es":"Principiante","it":"Principiante","de":"Anfänger"},
         {"en":"Never surfed, or just tried once or twice. You will start on a foam board on Ngor Left, a forgiving wave perfect for learning. By the end of your stay, you will be standing and riding.","fr":"Jamais surfé, ou essayé une ou deux fois. Vous commencerez sur une planche en mousse à Ngor Left, une vague indulgente parfaite pour apprendre. À la fin de votre séjour, vous serez debout et en train de rider.","es":"Nunca has surfeado, o lo has intentado una o dos veces. Empezarás en una tabla de foam en Ngor Left, una ola perfecta para aprender. Al final de tu estancia, estarás de pie y montando olas.","it":"Non hai mai surfato, o ci hai provato una o due volte. Inizierai su una tavola in schiuma a Ngor Left, un'onda perfetta per imparare. Alla fine del soggiorno, starai in piedi e cavalcherai le onde.","de":"Noch nie gesurft oder nur ein-, zweimal versucht. Sie beginnen auf einem Schaumstoffboard an Ngor Left, einer verzeihenden Welle. Am Ende Ihres Aufenthalts werden Sie stehen und reiten."},
         "#29b6f6"),
        ({"en":"Intermediate","fr":"Intermédiaire","es":"Intermedio","it":"Intermedio","de":"Fortgeschrittener"},
         {"en":"You can consistently pop up and ride down the line. Ready to work on turns, reading waves, and timing your take-off. Ngor Right on smaller days will become your playground.","fr":"Vous vous levez régulièrement et ridez dans la ligne. Prêt à travailler les virages, la lecture des vagues et le timing. Ngor Right les petits jours deviendra votre terrain de jeu.","es":"Puedes levantarte consistentemente y montar la ola en línea. Listo para trabajar giros, lectura de olas y timing del despegue. Ngor Right en días pequeños será tu patio de recreo.","it":"Riesci a fare il pop-up consistentemente e cavalcare l'onda. Pronto a lavorare sulle virate, lettura delle onde e timing del decollo. Ngor Right nelle giornate piccole sarà il tuo terreno di gioco.","de":"Sie können konsistent aufspringen und die Welle reiten. Bereit, an Kurven, Wellenlesen und Timing zu arbeiten. Ngor Right an kleineren Tagen wird Ihr Spielplatz."},
         "#ff6b35"),
        ({"en":"Advanced","fr":"Avancé","es":"Avanzado","it":"Avanzato","de":"Profi"},
         {"en":"You surf turns and are pushing your performance. Ngor Right at full size is your wave: powerful, fast and demanding. Video analysis with Kofi or Luca will fast-track your specific weaknesses.","fr":"Vous surfez les virages et poussez votre performance. Ngor Right en pleine taille est votre vague : puissante, rapide et exigeante. L'analyse vidéo avec Kofi ou Luca accélérera vos points faibles spécifiques.","es":"Surfeas giros y estás empujando tu rendimiento. Ngor Right en su tamaño completo es tu ola: poderosa, rápida y exigente. El análisis de vídeo con Kofi o Luca acelerará tus puntos débiles específicos.","it":"Surfai le virate e stai spingendo le tue performance. Ngor Right a piena dimensione è la tua onda: potente, veloce e impegnativa. L'analisi video con Kofi o Luca accelererà i tuoi punti deboli specifici.","de":"Sie surfen Kurven und pushen Ihre Performance. Ngor Right in voller Größe ist Ihre Welle: kraftvoll, schnell und fordernd. Videoanalyse mit Kofi oder Luca beschleunigt Ihre spezifischen Schwachpunkte."},
         "#0a2540"),
    ]

    BOOK  = {"en":"Book Your Surf Package","fr":"Réserver votre Package Surf","es":"Reservar tu Paquete Surf","it":"Prenota il tuo Pacchetto Surf","de":"Surf-Paket buchen","nl":"Surf-pakket boeken","ar":"احجز باقة السيرف"}
    MEET  = {"en":"Meet like-minded surfers from around the world","fr":"Rencontrez des surfeurs du monde entier","es":"Conoce surfistas de todo el mundo","it":"Incontra surfisti da tutto il mondo","de":"Treffe gleichgesinnte Surfer aus aller Welt","nl":"Ontmoet gelijkgestemde surfers van over de hele wereld","ar":"التقِ بالمتصفحين ذوي التفكير المماثل من جميع أنحاء العالم"}
    CTA_H = {"en":"Your best surf is waiting.","fr":"Votre meilleur surf vous attend.","es":"Tu mejor surf te está esperando.","it":"Il tuo miglior surf ti aspetta.","de":"Dein bestes Surfen wartet auf dich.","nl":"Jouw beste surfen wacht op je.","ar":"أفضل تصفح لك ينتظرك."}
    CTA_P = {"en":"Ngor Island, Dakar, Senegal. WhatsApp: +221 78 925 70 25","fr":"Île de Ngor, Dakar, Sénégal. WhatsApp : +221 78 925 70 25","es":"Isla de Ngor, Dakar, Senegal. WhatsApp: +221 78 925 70 25","it":"Isola di Ngor, Dakar, Senegal. WhatsApp: +221 78 925 70 25","de":"Ngor Island, Dakar, Senegal. WhatsApp: +221 78 925 70 25","nl":"Ngor Island, Dakar, Senegal. WhatsApp: +221 78 925 70 25","ar":"جزيرة Ngor، داكار، السنغال. WhatsApp: +221 78 925 70 25"}
    WHAT_S = {"en":"What's included with every stay","fr":"Ce qui est inclus dans chaque séjour","es":"Qué incluye cada estancia","it":"Cosa è incluso in ogni soggiorno","de":"Was bei jedem Aufenthalt inklusive ist","nl":"Wat bij elk verblijf is inbegrepen","ar":"ما هو مدرج في كل إقامة"}
    YOUR_L = {"en":"Your level at Ngor","fr":"Votre niveau à Ngor","es":"Tu nivel en Ngor","it":"Il tuo livello a Ngor","de":"Dein Level bei Ngor","nl":"Jouw niveau bij Ngor","ar":"مستواك في Ngor"}
    SERVICES_H = {"en":"Our Surfing Services","fr":"Nos Services Surf","es":"Nuestros Servicios Surf","it":"I Nostri Servizi Surf","de":"Unsere Surf-Services","nl":"Onze Surf-Services","ar":"خدمات السيرف لدينا"}
    GAL_H  = {"en":"Our surf trips in action","fr":"Nos sessions en action","es":"Nuestras sesiones en acción","it":"Le nostre sessioni in azione","de":"Unsere Sessions in Aktion","nl":"Onze sessies in actie","ar":"جلساتنا في العمل"}

    gal_imgs = [IMGS["surf"],IMGS["surf2"],IMGS["surf3"],IMGS["surf4"],IMGS["surf5"],IMGS["surf6"]]
    gal_html = "".join([f'<div class="gallery-item"><img src="{u}" alt="Surfing Ngor Island" loading="lazy"></div>' for u in gal_imgs])

    services_html = ""
    for titles, descs, ic in SERVICES:
        t = titles.get(lang,titles["en"]); d = descs.get(lang,descs["en"])
        services_html += f'<div class="feat reveal"><div class="feat-icon">{ico(ic,26)}</div><div><div class="feat-title">{t}</div><div class="feat-text">{d}</div></div></div>'

    levels_html = "".join([f'<div style="padding:24px;border-radius:14px;border-left:5px solid {c};background:{c}15;margin-bottom:16px"><div style="font-weight:700;font-size:17px;color:#0a2540;margin-bottom:8px">{t.get(lang,t["en"])}</div><p style="font-size:14.5px;color:#374151;margin:0">{d.get(lang,d["en"])}</p></div>' for t,d,c in LEVELS])

    html = head(title, meta, lang, can_tag("surfing",lang), hrl_tags("surfing"), IMGS["surf"])
    html += nav_html("surfing", lang, pfx, "/surfing")
    html += f"""
<main>
  <header class="main-hero" style="background-image:url('{IMGS['surf']}')" role="banner">
    <div class="main-hero-inner">
      <div class="main-hero-eyebrow">
        <span class="main-hero-dot"></span>
        <span>Ngor Surfcamp Teranga</span>
      </div>
      <h1 class="main-hero-h1">{h1}</h1>
      <p class="main-hero-tagline" style="font-style:italic">{MOTTO[lang]}</p>
      <div class="main-hero-actions">
        <a href="#main-intro" class="btn btn-outline-white btn-lg">&#8964;</a>
      </div>
    </div>
  </header>

  <!-- Main intro -->
  <section id="main-intro" class="section">
    <div class="container">
      <div class="split reveal">
        <div>
          <span class="s-label">{"Coaching & Waves" if lang=="en" else "Coaching & Vagues" if lang=="fr" else "Coaching y Olas" if lang=="es" else "Coaching e Onde" if lang=="it" else "Coaching & Wellen"}</span>
          <h2 class="s-title" style="margin-bottom:16px">{"Surf better. Progress faster." if lang=="en" else "Surfez mieux. Progressez plus vite." if lang=="fr" else "Surfa mejor. Progresa más rápido." if lang=="es" else "Surfa meglio. Progredisci più velocemente." if lang=="it" else "Besser surfen. Schneller Fortschritte."}</h2>
          <p style="font-size:17px;color:#374151;line-height:1.85;margin-bottom:28px">{INTRO[lang]}</p>
          <a href="{pfx}/booking/" class="btn btn-fire btn-lg">{BOOK[lang]}</a>
        </div>
        <div class="split-img"><img src="{IMGS['surf2']}" alt="Surf coaching Ngor Island" loading="lazy" width="600" height="460"></div>
      </div>
    </div>
  </section>

  <!-- Services grid -->
  <section class="section sec-light">
    <div class="container">
      <div style="text-align:center;margin-bottom:56px" class="reveal">
        <span class="s-label">{SERVICES_H[lang]}</span>
        <h2 class="s-title">{WHAT_S[lang]}</h2>
      </div>
      <div class="grid-2 reveal">{services_html}</div>
    </div>
  </section>

  <!-- Surf levels -->
  <section class="section">
    <div class="container">
      <div class="split reveal" style="align-items:flex-start">
        <div>
          <span class="s-label">{YOUR_L[lang]}</span>
          <h2 class="s-title" style="margin-bottom:28px">{YOUR_L[lang]}</h2>
          {levels_html}
        </div>
        <div class="split-img"><img src="{IMGS['coach']}" alt="Surf coaching at Ngor" loading="lazy" width="600" height="460"></div>
      </div>
    </div>
  </section>

  <!-- Team -->
  <section class="section sec-light">
    <div class="container reveal">
      <div style="text-align:center;max-width:760px;margin:0 auto">
        <span class="s-label">{TEAM_H[lang]}</span>
        <h2 class="s-title">{WHY_H[lang]}</h2>
        <p style="font-size:17px;color:#374151;line-height:1.85;margin-top:16px">{TEAM_T[lang]}</p>
        <div style="display:flex;gap:16px;justify-content:center;flex-wrap:wrap;margin-top:32px">
          <div style="display:flex;align-items:center;gap:10px;padding:12px 20px;border-radius:50px;background:#fff;box-shadow:0 2px 12px rgba(10,37,64,0.08)"><span style="color:var(--fire);font-size:20px">★</span><span style="font-weight:600;font-size:14px">ISA Certified</span></div>
          <div style="display:flex;align-items:center;gap:10px;padding:12px 20px;border-radius:50px;background:#fff;box-shadow:0 2px 12px rgba(10,37,64,0.08)"><span style="width:20px;height:20px;display:inline-flex">{ico("icon-federation",20)}</span><span style="font-weight:600;font-size:14px">Senegalese Federation</span></div>
          <div style="display:flex;align-items:center;gap:10px;padding:12px 20px;border-radius:50px;background:#fff;box-shadow:0 2px 12px rgba(10,37,64,0.08)"><span style="color:var(--ocean);font-size:20px">🌊</span><span style="font-weight:600;font-size:14px">{"Local Knowledge" if lang=="en" else "Connaissance Locale" if lang=="fr" else "Conocimiento Local" if lang=="es" else "Conoscenza Locale" if lang=="it" else "Lokales Wissen"}</span></div>
        </div>
      </div>
    </div>
  </section>

  <!-- Gallery -->
  <section class="section">
    <div class="container">
      <h2 class="s-title reveal" style="text-align:center;margin-bottom:40px">{GAL_H[lang]}</h2>
      <div class="gallery-masonry reveal">{gal_html}</div>
    </div>
    <div id="lb"><button id="lb-close" aria-label="Close">✕</button><img id="lb-img" src="" alt="Surfing"></div>
  </section>

  <!-- Meet surfers -->
  <div class="cta-band">
    <div class="container">
      <h2>{MEET[lang]}</h2>
      <h3 style="font-size:20px;font-weight:300;opacity:0.82;margin-bottom:36px">{CTA_P[lang]}</h3>
      <div class="cta-btns">
        <a href="{pfx}/booking/" class="btn btn-fire btn-lg">{BOOK[lang]}</a>
        <a href="https://wa.me/221789257025" target="_blank" class="btn btn-glass btn-lg">
          <span style="width:18px;height:18px;display:inline-flex">{WA_ICO}</span> WhatsApp</a>
      </div>
    </div>
  </div>
</main>"""
    html += footer_html(lang, pfx)
    html += close()
    return html

# ════════════════════════════════════════════════════════════════════════════════
# SUPER FAQ PAGE
# ════════════════════════════════════════════════════════════════════════════════
def build_super_faq(lang):
    pfx = LANG_PREFIX[lang]
    p   = load(f"{PAGES_D}/{lang}_faq.json") or {}
    h1  = fix_em(p.get("h1","Everything You Need to Know"))
    meta= fix_em(p.get("meta_description","Complete FAQ about Ngor Surfcamp Teranga: getting there, surf levels, booking, waves, accommodation and more."))
    title= fix_em(p.get("title_tag","FAQ | Ngor Surfcamp Teranga | Complete Guide"))

    SECTIONS = [
        {
            "id": "getting-there",
            "title": {"en":"Getting to Ngor Island","fr":"Se Rendre à l'Île de Ngor","es":"Cómo Llegar a la Isla de Ngor","it":"Come Arrivare all'Isola di Ngor","de":"Anreise zu Ngor Island","nl":"Naar Ngor Island","ar":"الوصول إلى جزيرة نغور"},
            "icon": "icon-location",
            "faqs": [
                ({"en":"Where is Ngor Island exactly?","fr":"Où se trouve exactement l'île de Ngor ?","es":"¿Dónde está exactamente la isla de Ngor?","it":"Dov'è esattamente l'isola di Ngor?","de":"Wo genau liegt Ngor Island?"},
                 {"en":"Ngor Island is located approximately 800 meters off the Cap-Vert peninsula in Dakar, Senegal, West Africa. It is a small, car-free island reachable by a short pirogue (traditional wooden boat) ride from Ngor beach. The island is about 20 minutes from Dakar-Yoff International Airport (DSS) by taxi or Uber.","fr":"L'île de Ngor est située à environ 800 mètres de la péninsule du Cap-Vert à Dakar, Sénégal, Afrique de l'Ouest. C'est une petite île sans voitures accessible par une courte traversée en pirogue (bateau traditionnel en bois) depuis la plage de Ngor. L'île est à environ 20 minutes de l'aéroport international de Dakar-Yoff (DSS) en taxi ou Uber.","es":"La isla de Ngor está ubicada aproximadamente a 800 metros de la península de Cap-Vert en Dakar, Senegal, África Occidental. Es una pequeña isla sin coches accesible por un corto trayecto en piragua (barco tradicional de madera) desde la playa de Ngor. La isla está a unos 20 minutos del aeropuerto internacional de Dakar-Yoff (DSS) en taxi o Uber.","it":"L'isola di Ngor è situata a circa 800 metri dalla penisola di Cap-Vert a Dakar, Senegal, Africa Occidentale. È una piccola isola senza auto raggiungibile con una breve traversata in piroga (barca di legno tradizionale) dalla spiaggia di Ngor. L'isola dista circa 20 minuti dall'aeroporto internazionale di Dakar-Yoff (DSS) in taxi o Uber.","de":"Ngor Island liegt etwa 800 Meter vor der Cap-Vert-Halbinsel in Dakar, Senegal, Westafrika. Es ist eine kleine, autofreie Insel, die mit einer kurzen Pirogenfahrt (traditionelles Holzboot) vom Ngor-Strand aus erreichbar ist. Die Insel ist etwa 20 Minuten vom internationalen Flughafen Dakar-Yoff (DSS) mit Taxi oder Uber entfernt."}),
                ({"en":"How do I get from Dakar airport to Ngor Island?","fr":"Comment aller de l'aéroport de Dakar à l'île de Ngor ?","es":"¿Cómo ir del aeropuerto de Dakar a la isla de Ngor?","it":"Come andare dall'aeroporto di Dakar all'isola di Ngor?","de":"Wie komme ich vom Flughafen Dakar nach Ngor Island?"},
                 {"en":"Step 1: Take a taxi or Uber from Blaise Diagne International Airport (DSS) to Ngor beach. The ride takes about 20-30 minutes and costs approximately 5,000-8,000 CFA (around €8-12). Step 2: Walk to the small pier at Ngor beach and take the pirogue to Ngor Island. The boat ride takes about 5 minutes and costs less than 500 CFA (under €1). Pirogues run continuously throughout the day until about 10pm. Our team can also arrange a pickup, just WhatsApp us in advance.","fr":"Étape 1 : Prenez un taxi ou Uber depuis l'aéroport international Blaise Diagne (DSS) jusqu'à la plage de Ngor. Le trajet dure environ 20-30 minutes et coûte environ 5 000-8 000 CFA (environ 8-12€). Étape 2 : Marchez jusqu'à la petite jetée à la plage de Ngor et prenez la pirogue vers l'île de Ngor. La traversée dure environ 5 minutes et coûte moins de 500 CFA (moins de 1€). Les pirogues fonctionnent en continu tout au long de la journée jusqu'à environ 22h.","es":"Paso 1: Toma un taxi o Uber desde el aeropuerto internacional Blaise Diagne (DSS) hasta la playa de Ngor. El trayecto dura unos 20-30 minutos y cuesta aproximadamente 5.000-8.000 CFA (unos 8-12€). Paso 2: Camina hasta el pequeño embarcadero de la playa de Ngor y toma la piragua hasta la isla de Ngor. El trayecto dura unos 5 minutos y cuesta menos de 500 CFA (menos de 1€). Las piraguas funcionan continuamente durante el día hasta las 22h aproximadamente.","it":"Fase 1: Prendi un taxi o Uber dall'aeroporto internazionale Blaise Diagne (DSS) alla spiaggia di Ngor. Il tragitto dura circa 20-30 minuti e costa circa 5.000-8.000 CFA (circa 8-12€). Fase 2: Cammina fino al piccolo molo della spiaggia di Ngor e prendi la piroga verso l'isola di Ngor. Il tragitto dura circa 5 minuti e costa meno di 500 CFA (meno di 1€). Le piroghe funzionano continuamente durante il giorno fino alle 22h circa.","de":"Schritt 1: Nehmen Sie ein Taxi oder Uber vom Internationalen Flughafen Blaise Diagne (DSS) zum Ngor-Strand. Die Fahrt dauert etwa 20-30 Minuten und kostet ca. 5.000-8.000 CFA (ca. 8-12€). Schritt 2: Gehen Sie zum kleinen Pier am Ngor-Strand und nehmen Sie die Piroge nach Ngor Island. Die Bootsfahrt dauert etwa 5 Minuten und kostet weniger als 500 CFA (unter 1€). Piroge fahren den ganzen Tag bis etwa 22 Uhr."}),
                ({"en":"Are there direct flights to Dakar?","fr":"Y a-t-il des vols directs vers Dakar ?","es":"¿Hay vuelos directos a Dakar?","it":"Ci sono voli diretti per Dakar?","de":"Gibt es Direktflüge nach Dakar?"},
                 {"en":"Yes. Blaise Diagne International Airport (DSS) receives direct flights from Paris (Air France, Transavia, Air Sénégal), Brussels, Casablanca, Madrid, London, Frankfurt, Amsterdam, and many African hubs. Flight times: Paris 6h, London 7h, Madrid 5h, Frankfurt 7h, Amsterdam 7h. Most European airlines have seasonal or year-round direct routes.","fr":"Oui. L'aéroport international Blaise Diagne (DSS) reçoit des vols directs depuis Paris (Air France, Transavia, Air Sénégal), Bruxelles, Casablanca, Madrid, Londres, Francfort, Amsterdam et de nombreuses plateformes africaines.","es":"Sí. El aeropuerto internacional Blaise Diagne (DSS) recibe vuelos directos desde París (Air France, Transavia, Air Sénégal), Bruselas, Casablanca, Madrid, Londres, Fráncfort, Ámsterdam y muchos hubs africanos.","it":"Sì. L'aeroporto internazionale Blaise Diagne (DSS) riceve voli diretti da Parigi (Air France, Transavia, Air Sénégal), Bruxelles, Casablanca, Madrid, Londra, Francoforte, Amsterdam e molti hub africani.","de":"Ja. Der Internationale Flughafen Blaise Diagne (DSS) empfängt Direktflüge aus Paris (Air France, Transavia, Air Sénégal), Brüssel, Casablanca, Madrid, London, Frankfurt, Amsterdam und vielen afrikanischen Hubs."}),
            ]
        },
        {
            "id": "surf-levels",
            "title": {"en":"Surf Levels & Coaching","fr":"Niveaux Surf & Coaching","es":"Niveles Surf y Coaching","it":"Livelli Surf e Coaching","de":"Surf-Level & Coaching","nl":"Surfniveaus & Coaching","ar":"مستويات ركوب الأمواج والتدريب"},
            "icon": "icon-coaching",
            "faqs": [
                ({"en":"What surf level do I need to join?","fr":"Quel niveau de surf faut-il pour rejoindre ?","es":"¿Qué nivel de surf necesito?","it":"Quale livello di surf è necessario?","de":"Welches Surflevel brauche ich?"},
                 {"en":"No experience needed at all. We welcome complete beginners to advanced surfers. Our coaches create individualized sessions for each guest regardless of level. Beginners start on large foam boards at Ngor Left, a forgiving and consistent wave. Intermediate surfers work at Ngor Left and smaller Ngor Right days. Advanced surfers tackle full-size Ngor Right with video analysis coaching.","fr":"Aucune expérience n'est requise. Nous accueillons des débutants complets comme des surfeurs avancés. Nos coachs créent des sessions individualisées pour chaque invité quel que soit le niveau. Les débutants commencent sur de grandes planches en mousse à Ngor Left. Les surfeurs intermédiaires travaillent à Ngor Left et lors des petits jours de Ngor Right. Les surfeurs avancés s'attaquent à Ngor Right à pleine taille.","es":"No se necesita ninguna experiencia. Damos la bienvenida desde principiantes completos hasta surfistas avanzados. Nuestros coaches crean sesiones individualizadas para cada huésped independientemente del nivel. Los principiantes comienzan en tablas de foam grandes en Ngor Left. Los surfistas intermedios trabajan en Ngor Left y días pequeños de Ngor Right. Los surfistas avanzados afrontan Ngor Right a pleno tamaño.","it":"Non è necessaria alcuna esperienza. Accogliamo principianti assoluti e surfisti avanzati. I nostri coach creano sessioni individualizzate per ogni ospite indipendentemente dal livello. I principianti iniziano su grandi tavole in schiuma a Ngor Left. I surfisti intermedi lavorano a Ngor Left e nelle giornate piccole di Ngor Right. I surfisti avanzati affrontano Ngor Right a piena dimensione.","de":"Keine Erfahrung nötig. Wir begrüßen komplette Anfänger bis zu fortgeschrittenen Surfern. Unsere Coaches erstellen individuelle Sessions für jeden Gast unabhängig vom Level. Anfänger beginnen auf großen Schaumstoffboards an Ngor Left. Fortgeschrittene surfen Ngor Left und kleinere Ngor Right-Tage. Profi-Surfer nehmen Ngor Right in voller Größe unter Video-Analyse."}),
                ({"en":"Is video analysis included in the coaching?","fr":"L'analyse vidéo est-elle incluse dans le coaching ?","es":"¿Está incluido el análisis de vídeo?","it":"L'analisi video è inclusa nel coaching?","de":"Ist die Videoanalyse im Coaching inklusive?"},
                 {"en":"Yes, video analysis is a core feature of our coaching program at no extra cost. We film your surf sessions from the beach or water, then review the footage with you on a tablet. You see exactly what your body is doing at each stage of the wave: paddle, pop-up, bottom turn, and trim position. This visual feedback accelerates learning significantly faster than verbal coaching alone. It is particularly useful for intermediate surfers stuck on a plateau.","fr":"Oui, l'analyse vidéo est une fonctionnalité essentielle de notre programme de coaching sans frais supplémentaires. Nous filmons vos sessions de surf depuis la plage ou l'eau, puis analysons les images avec vous sur une tablette. Vous voyez exactement ce que fait votre corps à chaque étape de la vague. Ce feedback visuel accélère considérablement l'apprentissage.","es":"Sí, el análisis de vídeo es una característica central de nuestro programa de coaching sin coste adicional. Filmamos tus sesiones de surf desde la playa o el agua, luego revisamos las grabaciones contigo en una tableta. Ves exactamente lo que hace tu cuerpo en cada etapa de la ola. Este feedback visual acelera el aprendizaje significativamente más rápido que el coaching verbal solo.","it":"Sì, l'analisi video è una caratteristica fondamentale del nostro programma di coaching senza costi aggiuntivi. Filmiamo le tue sessioni di surf dalla spiaggia o dall'acqua, poi analizziamo le riprese con te su un tablet. Vedi esattamente cosa fa il tuo corpo in ogni fase dell'onda. Questo feedback visivo accelera notevolmente l'apprendimento.","de":"Ja, die Videoanalyse ist ein Kernmerkmal unseres Coaching-Programms ohne Aufpreis. Wir filmen Ihre Surf-Sessions vom Strand oder Wasser, dann analysieren wir die Aufnahmen gemeinsam auf einem Tablet. Sie sehen genau, was Ihr Körper in jeder Phase der Welle macht. Dieses visuelle Feedback beschleunigt das Lernen erheblich schneller als rein verbales Coaching."}),
                ({"en":"What are Ngor Right and Ngor Left?","fr":"Que sont Ngor Right et Ngor Left ?","es":"¿Qué son Ngor Right y Ngor Left?","it":"Cosa sono Ngor Right e Ngor Left?","de":"Was sind Ngor Right und Ngor Left?"},
                 {"en":"Ngor Right is a famous right-hand point break that was featured in the 1964 surf film 'The Endless Summer.' It is a powerful, consistent wave that peels over a rocky reef, producing long rides of 50-100+ meters. It is best for intermediate to advanced surfers and works best at mid to full tide with a solid north or northwest swell. Ngor Left is a more forgiving left-hand wave that breaks closer to the beach on a sand and rock bottom. It is excellent for beginners and intermediates, and works well even on smaller days. Both breaks are accessible by a short 5-minute pirogue ride from Ngor Island.","fr":"Ngor Right est un célèbre point break à droite qui a été présenté dans le film de surf de 1964 'The Endless Summer.' C'est une vague puissante et consistante qui déferle sur un récif rocheux, produisant de longues rides de 50-100+ mètres. Ngor Left est une vague à gauche plus indulgente qui se brise plus près de la plage. Excellente pour débutants et intermédiaires, elle fonctionne bien même les petits jours.","es":"Ngor Right es un famoso point break de derecha que fue presentado en la película de surf de 1964 'The Endless Summer.' Es una ola potente y consistente que rompe sobre un arrecife rocoso, produciendo largas salidas de 50-100+ metros. Ngor Left es una ola izquierda más indulgente que rompe más cerca de la playa. Excelente para principiantes e intermedios.","it":"Ngor Right è un famoso point break destro che è stato presentato nel film surf del 1964 'The Endless Summer.' È un'onda potente e consistente che si rompe su una scogliera rocciosa, producendo lunghe cavalcate di 50-100+ metri. Ngor Left è un'onda sinistra più indulgente che si rompe più vicino alla spiaggia. Eccellente per principianti e intermedi.","de":"Ngor Right ist ein berühmter rechtshandiger Point Break, der im Surf-Film von 1964 'The Endless Summer' zu sehen war. Es ist eine kraftvolle, konsistente Welle, die über ein felsiges Riff bricht und lange Rides von 50-100+ Metern produziert. Ngor Left ist eine nachgebendere linkshändige Welle, die näher am Strand bricht. Hervorragend für Anfänger und Fortgeschrittene."}),
            ]
        },
        {
            "id": "accommodation",
            "title": {"en":"Accommodation & What's Included","fr":"Hébergement et Ce Qui Est Inclus","es":"Alojamiento y Qué Está Incluido","it":"Alloggio e Cosa è Incluso","de":"Unterkunft & Inbegriffene Leistungen"},
            "icon": "icon-checklist",
            "faqs": [
                ({"en":"What's included in the price?","fr":"Qu'est-ce qui est inclus dans le prix ?","es":"¿Qué incluye el precio?","it":"Cosa è incluso nel prezzo?","de":"Was ist im Preis inbegriffen?"},
                 {"en":"Your stay at Ngor Surfcamp Teranga includes: accommodation in a private or shared room, breakfast and dinner daily (authentic Senegalese cuisine), daily surf guiding to the best spot, daily free surf theory classes, boat transfers to Ngor Right and Left, pool access and shared spaces, free Wi-Fi throughout, and daily room cleaning. Video coaching sessions are also available as part of the coaching program. The only extras are optional surf trip transfers to other Dakar spots and equipment rental if you need it.","fr":"Votre séjour au Ngor Surfcamp Teranga comprend : hébergement en chambre privée ou partagée, petit-déjeuner et dîner quotidien (cuisine sénégalaise authentique), guide surf quotidien vers le meilleur spot, cours de théorie surf quotidiens gratuits, transferts en bateau vers Ngor Right et Left, accès piscine, Wi-Fi gratuit, et ménage quotidien.","es":"Tu estancia en Ngor Surfcamp Teranga incluye: alojamiento en habitación privada o compartida, desayuno y cena diarios (cocina senegalesa auténtica), guía surf diario al mejor spot, clases de teoría surf diarias gratuitas, traslados en barco a Ngor Right y Left, acceso a piscina, Wi-Fi gratuito, y limpieza diaria de habitación.","it":"Il tuo soggiorno al Ngor Surfcamp Teranga include: alloggio in camera privata o condivisa, colazione e cena quotidiana (cucina senegalese autentica), guida surf giornaliera verso il miglior spot, lezioni di teoria surf giornaliere gratuite, trasferimenti in barca verso Ngor Right e Left, accesso alla piscina, Wi-Fi gratuito, e pulizia giornaliera della camera.","de":"Ihr Aufenthalt im Ngor Surfcamp Teranga beinhaltet: Unterkunft im Einzel- oder Mehrbettzimmer, tägliches Frühstück und Abendessen (authentische senegalesische Küche), tägliche Surf-Führung zum besten Spot, tägliche kostenlose Surf-Theoriestunden, Bootüberfahrten zu Ngor Right und Left, Poolzugang, kostenloses WLAN und tägliche Zimmerreinigung."}),
                ({"en":"Can I book accommodation only without surf coaching?","fr":"Puis-je réserver l'hébergement seul sans coaching surf ?","es":"¿Puedo reservar solo el alojamiento sin coaching surf?","it":"Posso prenotare solo l'alloggio senza coaching surf?","de":"Kann ich nur die Unterkunft ohne Surf-Coaching buchen?"},
                 {"en":"Absolutely. We offer accommodation-only options for experienced surfers who want the island base and the food without the structured coaching sessions. You can still join daily surf guiding sessions, access the theory classes, and use the boat transfers. Just tell us your preference when you book via WhatsApp.","fr":"Absolument. Nous proposons des options d'hébergement seul pour les surfeurs expérimentés qui souhaitent la base insulaire et la nourriture sans les séances de coaching structurées. Contactez-nous sur WhatsApp avec vos préférences.","es":"Por supuesto. Ofrecemos opciones de solo alojamiento para surfistas experimentados que quieren la base en la isla y la comida sin las sesiones de coaching estructuradas. Cuéntanos tus preferencias al reservar por WhatsApp.","it":"Assolutamente sì. Offriamo opzioni di solo alloggio per surfisti esperti che vogliono la base sull'isola e il cibo senza le sessioni di coaching strutturate. Comunica le tue preferenze prenotando via WhatsApp.","de":"Absolut. Wir bieten Unterkunft-nur-Optionen für erfahrene Surfer an, die die Inselbasis und das Essen ohne die strukturierten Coaching-Sessions möchten. Teilen Sie uns Ihre Präferenzen bei der Buchung per WhatsApp mit."}),
            ]
        },
        {
            "id": "surf-conditions",
            "title": {"en":"Surf Conditions & Best Season","fr":"Conditions Surf & Meilleure Saison","es":"Condiciones Surf y Mejor Temporada","it":"Condizioni Surf e Stagione Migliore","de":"Surf-Bedingungen & Beste Reisezeit"},
            "icon": "icon-calendar",
            "faqs": [
                ({"en":"When is the best time to surf at Ngor Island?","fr":"Quelle est la meilleure période pour surfer à l'île de Ngor ?","es":"¿Cuándo es el mejor momento para surfear en la isla de Ngor?","it":"Quando è il periodo migliore per fare surf all'isola di Ngor?","de":"Wann ist die beste Zeit zum Surfen auf Ngor Island?"},
                 {"en":"Ngor is surfable year-round, which is one of its major advantages over European destinations. The peak surf season runs from October to April, when consistent north and northwest Atlantic swells produce the best waves at Ngor Right (2-4 meters face). The summer months (May-September) are warmer with lighter swells, perfect for beginners and intermediate surfers. Water temperature stays between 22-27°C all year. Air temperature ranges from 24-34°C.","fr":"Ngor est surfable toute l'année, ce qui est l'un de ses principaux avantages sur les destinations européennes. La saison de pointe va d'octobre à avril, avec des houles atlantiques consistantes du nord et du nord-ouest. Les mois d'été (mai-septembre) sont plus chauds avec des houles plus légères, parfaits pour débutants et intermédiaires.","es":"Ngor es surfeable durante todo el año, lo que es una de sus principales ventajas. La temporada pico va de octubre a abril, con swells atlánticos consistentes del norte y noroeste. Los meses de verano (mayo-septiembre) son más cálidos con swells más ligeros, perfectos para principiantes e intermedios.","it":"Ngor è surfabile tutto l'anno, il che è uno dei suoi principali vantaggi. La stagione di punta va da ottobre ad aprile, con swell atlantici consistenti da nord e nord-ovest. I mesi estivi (maggio-settembre) sono più caldi con swell più leggeri, perfetti per principianti e intermedi.","de":"Ngor ist das ganze Jahr über surfbar, was einer der Hauptvorteile gegenüber europäischen Zielen ist. Die Hauptsurfsaison läuft von Oktober bis April mit konsistenten Nord- und Nordwestswells. Die Sommermonate (Mai-September) sind wärmer mit leichterem Swell, perfekt für Anfänger und Fortgeschrittene."}),
                ({"en":"Do I need a wetsuit?","fr":"Ai-je besoin d'une combinaison ?","es":"¿Necesito un traje de surf?","it":"Ho bisogno di una muta?","de":"Brauche ich einen Neoprenanzug?"},
                 {"en":"Generally no. Senegal's water temperature stays between 22-27°C year-round. A standard swimsuit or boardshorts is fine for most surfers from April to November. Some people prefer a spring suit (short arms/legs, 2mm) or a long-sleeve rashguard for sun protection in winter months (December-March) when water temperatures can dip to 22-23°C. We have rashguards and basic wetsuits available for guests to borrow.","fr":"Généralement non. La température de l'eau au Sénégal reste entre 22-27°C toute l'année. Un maillot de bain standard convient pour la plupart des surfeurs d'avril à novembre. Certains préfèrent une combi shortie ou un rashguard à manches longues pour la protection solaire en hiver (décembre-mars) quand l'eau peut descendre à 22-23°C.","es":"Generalmente no. La temperatura del agua en Senegal se mantiene entre 22-27°C durante todo el año. Un bañador estándar está bien para la mayoría de surfistas de abril a noviembre. Algunos prefieren una combi shortie o un rashguard de manga larga para protección solar en los meses de invierno (diciembre-marzo).","it":"Generalmente no. La temperatura dell'acqua in Senegal rimane tra 22-27°C tutto l'anno. Un costume da bagno standard va bene per la maggior parte dei surfisti da aprile a novembre. Alcuni preferiscono una muta shortie o un rashguard a maniche lunghe per la protezione solare nei mesi invernali (dicembre-marzo).","de":"Im Allgemeinen nein. Die Wassertemperatur in Senegal bleibt das ganze Jahr über zwischen 22-27°C. Ein normaler Badeanzug oder Boardshorts ist für die meisten Surfer von April bis November ausreichend. Einige bevorzugen einen Shorty oder Langarm-Rashguard für Sonnenschutz in Wintermonaten (Dezember-März)."}),
            ]
        },
        {
            "id": "practical",
            "title": {"en":"Practical Information","fr":"Informations Pratiques","es":"Información Práctica","it":"Informazioni Pratiche","de":"Praktische Informationen"},
            "icon": "icon-federation",
            "faqs": [
                ({"en":"What visa do I need for Senegal?","fr":"Quel visa faut-il pour le Sénégal ?","es":"¿Qué visa necesito para Senegal?","it":"Di quale visto ho bisogno per il Senegal?","de":"Welches Visum brauche ich für Senegal?"},
                 {"en":"Citizens of EU countries (France, Germany, Spain, Italy, etc.), UK, USA, Canada and most other Western nations do not need a visa to enter Senegal. You receive a free 90-day stamp on arrival at Blaise Diagne Airport. Always verify current entry requirements with your country's consulate or official government travel advisory before booking flights.","fr":"Les citoyens des pays de l'UE (France, Allemagne, Espagne, Italie, etc.), du Royaume-Uni, des États-Unis, du Canada et de la plupart des autres nations occidentales n'ont pas besoin de visa pour entrer au Sénégal. Vous recevez un tampon gratuit de 90 jours à l'arrivée. Vérifiez toujours les conditions d'entrée actuelles avant de réserver des vols.","es":"Los ciudadanos de países de la UE (Francia, Alemania, España, Italia, etc.), UK, USA, Canadá y la mayoría de otras naciones occidentales no necesitan visa para entrar en Senegal. Recibes un sello gratuito de 90 días a la llegada. Verifica siempre los requisitos de entrada actuales antes de reservar vuelos.","it":"I cittadini dei paesi UE (Francia, Germania, Spagna, Italia, ecc.), UK, USA, Canada e la maggior parte delle altre nazioni occidentali non hanno bisogno di visto per entrare in Senegal. Si riceve un timbro gratuito di 90 giorni all'arrivo. Verifica sempre i requisiti di ingresso attuali prima di prenotare voli.","de":"Bürger der EU-Länder (Frankreich, Deutschland, Spanien, Italien, etc.), UK, USA, Kanada und die meisten anderen westlichen Nationen benötigen kein Visum für Senegal. Sie erhalten bei der Ankunft einen kostenlosen 90-Tage-Stempel. Überprüfen Sie immer die aktuellen Einreisebestimmungen vor der Flugbuchung."}),
                ({"en":"What currency is used? Can I pay by card?","fr":"Quelle monnaie est utilisée ? Puis-je payer par carte ?","es":"¿Qué moneda se usa? ¿Puedo pagar con tarjeta?","it":"Quale valuta si usa? Posso pagare con carta?","de":"Welche Währung wird verwendet? Kann ich mit Karte bezahlen?"},
                 {"en":"Senegal uses the West African CFA Franc (XOF). Most transactions on Ngor Island are in cash, as card payment infrastructure on the island itself is limited. We recommend withdrawing CFA francs from ATMs in Dakar before taking the pirogue. Major ATMs at the airport and in central Dakar accept Visa and Mastercard. 1 EUR is approximately 650-660 XOF. We accept payment by bank transfer or PayPal for accommodation booking deposits.","fr":"Le Sénégal utilise le Franc CFA d'Afrique de l'Ouest (XOF). La plupart des transactions sur l'île de Ngor se font en espèces. Nous recommandons de retirer des francs CFA aux distributeurs automatiques à Dakar avant de prendre la pirogue. Les principaux distributeurs à l'aéroport et dans le centre de Dakar acceptent Visa et Mastercard.","es":"Senegal usa el Franco CFA de África Occidental (XOF). La mayoría de transacciones en la isla de Ngor son en efectivo. Recomendamos retirar francos CFA de cajeros en Dakar antes de tomar la piragua. Los cajeros principales en el aeropuerto y en el centro de Dakar aceptan Visa y Mastercard. 1 EUR equivale aproximadamente a 650-660 XOF.","it":"Il Senegal usa il Franco CFA dell'Africa Occidentale (XOF). La maggior parte delle transazioni sull'isola di Ngor avvengono in contanti. Raccomandiamo di prelevare franchi CFA dai bancomat a Dakar prima di prendere la piroga. I principali bancomat all'aeroporto e nel centro di Dakar accettano Visa e Mastercard. 1 EUR equivale a circa 650-660 XOF.","de":"Senegal verwendet den westafrikanischen CFA-Franc (XOF). Die meisten Transaktionen auf Ngor Island erfolgen bar. Wir empfehlen, CFA-Francs von Geldautomaten in Dakar abzuheben, bevor Sie die Piroge nehmen. Hauptgeldautomaten am Flughafen und in der Innenstadt von Dakar akzeptieren Visa und Mastercard. 1 EUR entspricht ca. 650-660 XOF."}),
                ({"en":"How do I book? How fast do you reply?","fr":"Comment réserver ? Quelle est la vitesse de réponse ?","es":"¿Cómo reservo? ¿Qué tan rápido respondéis?","it":"Come prenoto? Quanto velocemente rispondete?","de":"Wie buche ich? Wie schnell antworten Sie?"},
                 {"en":"The simplest way is to send us a message on WhatsApp (+221 78 925 70 25) with your dates, number of guests, and surf level. You can also fill the booking form on this site, which will send a pre-filled message to our WhatsApp. We reply to all inquiries within 24 hours, usually much faster during Senegal waking hours (8am-8pm GMT). Once you confirm, we send a booking confirmation and a deposit payment link.","fr":"La façon la plus simple est de nous envoyer un message sur WhatsApp (+221 78 925 70 25) avec vos dates, le nombre d'invités et votre niveau de surf. Vous pouvez aussi remplir le formulaire de réservation sur ce site. Nous répondons à toutes les demandes dans les 24 heures, généralement beaucoup plus vite pendant les heures de réveil au Sénégal (8h-20h GMT).","es":"La forma más sencilla es enviarnos un mensaje por WhatsApp (+221 78 925 70 25) con tus fechas, número de huéspedes y nivel de surf. También puedes rellenar el formulario de reserva en este sitio. Respondemos a todas las consultas en 24 horas, generalmente mucho más rápido durante las horas de vigilia en Senegal (8h-20h GMT).","it":"Il modo più semplice è inviarci un messaggio su WhatsApp (+221 78 925 70 25) con le tue date, il numero di ospiti e il livello di surf. Puoi anche compilare il modulo di prenotazione su questo sito. Rispondiamo a tutte le richieste entro 24 ore, generalmente molto più velocemente durante le ore di veglia in Senegal (8h-20h GMT).","de":"Der einfachste Weg ist eine WhatsApp-Nachricht (+221 78 925 70 25) mit Ihren Daten, Gästezahl und Surf-Level. Sie können auch das Buchungsformular auf dieser Website ausfüllen. Wir antworten auf alle Anfragen innerhalb von 24 Stunden, in der Regel viel schneller während der senegalesischen Wachstunden (8-20 Uhr GMT)."}),
            ]
        },
    ]
    SECTIONS = merge_faq_sections(SECTIONS)

    HERO_DEFAULT = {
        "en": "Complete guide to Ngor Surfcamp Teranga: getting there, surf levels, accommodation, waves and booking.",
        "fr": "Guide complet sur le Ngor Surfcamp Teranga : comment s'y rendre, niveaux surf, hébergement, vagues et réservation.",
        "es": "Guía completa del Ngor Surfcamp Teranga: cómo llegar, niveles surf, alojamiento, olas y reserva.",
        "it": "Guida completa al Ngor Surfcamp Teranga: come arrivare, livelli surf, alloggio, onde e prenotazione.",
        "de": "Vollständiger Leitfaden zum Ngor Surfcamp Teranga: Anreise, Surf-Level, Unterkunft, Wellen und Buchung.",
        "nl": "Volledige gids voor Ngor Surfcamp Teranga: reis, surfniveaus, accommodatie, golven en boeken.",
        "ar": "دليل كامل عن Ngor Surfcamp Teranga: الوصول، مستويات ركوب الأمواج، الإقامة، الأمواج والحجز.",
    }
    hero_p = fix_em(p.get("hero_subtitle") or HERO_DEFAULT.get(lang, HERO_DEFAULT["en"]))

    # Build sections HTML
    sections_html = ""
    for sec in SECTIONS:
        sec_id    = sec["id"]
        sec_title = sec["title"].get(lang, sec["title"]["en"])
        sec_ico   = sec.get("icon","icon-tip")

        faq_items = "".join([
            f'<div class="faq-item closed" itemscope itemprop="mainEntity" itemtype="https://schema.org/Question"><button class="faq-q" type="button"><span itemprop="name">{q.get(lang,q["en"])}</span><span class="faq-arrow" aria-hidden="true">▼</span></button><div class="faq-a" itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer"><div itemprop="text">{a.get(lang,a["en"])}</div></div></div>'
            for q, a in sec["faqs"]
        ])

        sections_html += f'''
<div class="faq-section reveal" id="{sec_id}">
  <div style="display:flex;align-items:center;gap:14px;margin-bottom:24px">
    <div style="width:48px;height:48px;border-radius:14px;background:linear-gradient(135deg,var(--navy),#1a4a7a);display:flex;align-items:center;justify-content:center;flex-shrink:0">
      {ico(sec_ico,28)}
    </div>
    <h2 style="font-size:clamp(20px,3vw,28px);color:var(--navy);margin:0">{sec_title}</h2>
  </div>
  <div>{faq_items}</div>
</div>'''

    # TOC
    toc_html = "".join([
        f'<a href="#{s["id"]}" style="display:flex;align-items:center;gap:10px;padding:10px 14px;border-radius:10px;color:#374151;font-size:14px;font-weight:500;transition:all 0.2s;text-decoration:none" onmouseover="this.style.background=\'#f3f4f6\'" onmouseout="this.style.background=\'none\'">{ico(s.get("icon","icon-tip"),20)} {s["title"].get(lang,s["title"]["en"])}</a>'
        for s in SECTIONS
    ])

    STILL_Q = {"en":"Still have a question?","fr":"Vous avez encore une question ?","es":"¿Todavía tienes una pregunta?","it":"Hai ancora una domanda?","de":"Noch eine Frage?","nl":"Nog een vraag?","ar":"هل لا تزال لديك سؤال؟"}
    CHAT    = {"en":"Chat on WhatsApp","fr":"Discuter sur WhatsApp","es":"Chatear en WhatsApp","it":"Chatta su WhatsApp","de":"WhatsApp-Chat","nl":"Chatten op WhatsApp","ar":"الدردشة على WhatsApp"}
    ANSWERS = {"en":"We answer in 24h or less.","fr":"Nous répondons en 24h ou moins.","es":"Respondemos en 24h o menos.","it":"Rispondiamo in 24h o meno.","de":"Wir antworten in 24h oder weniger.","nl":"We antwoorden binnen 24 uur of minder.","ar":"نرد في غضون 24 ساعة أو أقل."}
    QUICK_ANS = {"en":"Quick answers","fr":"Réponses rapides","es":"Respuestas rápidas","it":"Risposte veloci","de":"Schnelle Antworten","nl":"Snelle antwoorden","ar":"إجابات سريعة"}

    html = head(title, meta, lang, can_tag("faq",lang), hrl_tags("faq"), IMGS["island"])
    html += nav_html("faq", lang, pfx, "/faq")
    html += f"""
<main>
  <header class="main-hero" style="background-image:url('{IMGS['island']}')" role="banner">
    <div class="main-hero-inner">
      <div class="main-hero-eyebrow">
        <span class="main-hero-dot"></span>
        <span>Ngor Surfcamp Teranga</span>
      </div>
      <h1 class="main-hero-h1">{h1}</h1>
      <p class="main-hero-tagline">{hero_p}</p>
      <div class="main-hero-actions">
        <a href="#faq-content" class="btn btn-outline-white btn-lg">&#8964;</a>
      </div>
    </div>
  </header>

  <section id="faq-content" class="section">
    <div class="container">
      <div class="faq-layout">

        <!-- TOC Sidebar -->
        <aside class="faq-sidebar">
          <div class="s-label" style="margin-bottom:14px">{QUICK_ANS[lang]}</div>
          <nav style="display:flex;flex-direction:column;gap:2px">{toc_html}</nav>
        </aside>

        <!-- FAQ content -->
        <div itemscope itemtype="https://schema.org/FAQPage">
          {sections_html}

          <!-- Still have questions -->
          <div style="margin-top:60px;padding:36px;border-radius:var(--r);background:var(--navy);color:#fff;text-align:center">
            <h3 style="font-size:22px;margin-bottom:10px">{STILL_Q[lang]}</h3>
            <p style="opacity:0.8;margin-bottom:24px">{ANSWERS[lang]}</p>
            <div style="display:flex;justify-content:center">
              <a href="https://wa.me/221789257025" target="_blank" class="btn btn-wa btn-lg">
                <span style="width:18px;height:18px;display:inline-flex">{WA_ICO}</span> {CHAT[lang]}
              </a>
            </div>
          </div>
        </div>

      </div>
    </div>
  </section>
</main>
<style>
@media(max-width:1024px){{.faq-layout{{grid-template-columns:1fr!important;gap:32px!important;}}.faq-sidebar{{position:relative!important;top:auto!important;}}}}
/* FAQ accordion: grid 0fr→1fr so full answers show even if main.css is cached old */
.faq-a{{display:grid!important;grid-template-rows:0fr!important;overflow:hidden!important;transition:grid-template-rows 0.45s ease!important;box-sizing:border-box!important}}
.faq-item.open .faq-a{{grid-template-rows:1fr!important}}
.faq-a>div{{min-height:0!important;overflow:hidden!important}}
.faq-item.open .faq-a>div{{overflow:visible!important}}
</style>"""
    html += footer_html(lang, pfx)
    html += close()
    return html

# ════════════════════════════════════════════════════════════════════════════════
# WRITE ALL FILES
# ════════════════════════════════════════════════════════════════════════════════
def _write_page(path, html):
    full = DEMO_DIR + path
    if full.endswith("/"):
        full += "index.html"
    elif not full.endswith(".html"):
        os.makedirs(full, exist_ok=True)
        full += "/index.html"
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(html)


def main():
    ap = argparse.ArgumentParser(description="Build surfing v2 and/or Super FAQ pages.")
    ap.add_argument(
        "--faq-only",
        action="store_true",
        help="Only write {lang}/faq/ (do not overwrite surfing pages).",
    )
    args = ap.parse_args()
    total = 0
    if args.faq_only:
        print("Building Super FAQ (all langs)…")
        for lang in LANGS:
            spfx = f"/{lang}" if lang != "en" else ""
            _write_page(f"{spfx}/faq/", build_super_faq(lang))
            total += 1
            print(f"  ✅ {lang}: faq")
    else:
        print("Building Surfing v2 + Super FAQ (all langs)…")
        for lang in LANGS:
            spfx = f"/{lang}" if lang != "en" else ""
            _write_page(f"{spfx}/surfing/", build_surfing_v2(lang))
            _write_page(f"{spfx}/faq/", build_super_faq(lang))
            total += 2
            print(f"  ✅ {lang}: surfing + faq")
    print(f"\nTotal pages: {total}")
    print("✅ Done.")


if __name__ == "__main__":
    main()
