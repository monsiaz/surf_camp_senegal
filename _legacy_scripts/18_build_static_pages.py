"""
Build all static pages: booking, island, surfing, gallery, faq, surf-house
+ all 5 languages. Booking form UX-first with WhatsApp redirect.
"""
import json, os, re

CONTENT  = "/Users/simonazoulay/SurfCampSenegal/content"
PAGES_D  = f"{CONTENT}/pages"
DEMO_DIR = "/Users/simonazoulay/SurfCampSenegal/cloudflare-demo"
SITE_URL = "https://ngor-surfcamp-demo.pages.dev"

WIX = "https://static.wixstatic.com/media"
LOGO = f"{WIX}/c2467f_a31779010ce34c4c8c61cc5868d81f31~mv2.png"

LANGS       = ["en","fr","es","it","de"]
LANG_NAMES  = {"en":"English","fr":"Français","es":"Español","it":"Italiano","de":"Deutsch"}
LANG_LOCALE = {"en":"en","fr":"fr-FR","es":"es-ES","it":"it-IT","de":"de-DE"}
LANG_PREFIX = {"en":"","fr":"/fr","es":"/es","it":"/it","de":"/de"}

IMGS = {
    "house":  f"{WIX}/df99f9_2ec6248367cd4e21a5e6c26c2b0a1c35~mv2.jpg",
    "house2": f"{WIX}/df99f9_eba4c24ec6a746b58d60a975b8d20946~mv2.jpg",
    "house3": f"{WIX}/df99f9_d8e77cf4807249f6953119f18be64166~mv2.jpg",
    "house4": f"{WIX}/df99f9_81e322c4e48d4bcbb444c6535daed131~mv2.jpg",
    "food":   f"{WIX}/df99f9_753890483d8e4cca8e2051a13f9c558e~mv2.jpg",
    "pool":   f"{WIX}/df99f9_a18d512828d9487e9a4987b9903960e0~mv2.jpg",
    "island": f"{WIX}/df99f9_56b9af6efe2841eea44109b3b08b7da1~mv2.jpg",
    "island2":f"{WIX}/b28af82dbec544138f16e2bc5a85f2cb.jpg",
    "island3":f"{WIX}/df99f9_5e1d04de46d74d1ca722aeeb6a640dad~mv2.jpg",
    "island4":f"{WIX}/df99f9_8acd4c6277cd4c619e1b87d56e4c8047~mv2.jpg",
    "ngor_r": f"{WIX}/11062b_7f89d2db0ace4027ac4a00928a6aca08~mv2.jpg",
    "sunset": f"{WIX}/df99f9_d6e404dd3cf74396b6ea874cb7021a27~mv2.jpg",
    "art":    f"{WIX}/df99f9_d81668a18a9d49d1b5ebb0ea3a0abbc7~mv2.jpg",
    "surf":   f"{WIX}/11062b_89a070321f814742a620b190592d51ad~mv2.jpg",
    "surf2":  f"{WIX}/df99f9_dd89cc4d86d4402189d7e9516ce672a3~mv2.jpg",
    "surf3":  f"{WIX}/df99f9_961b0768e713457f93025f4ce6fb1419~mv2.jpg",
    "surf4":  f"{WIX}/df99f9_0d4a03baee4f46b68bc1aa085ed28e35~mv2.jpg",
    "surf5":  f"{WIX}/df99f9_796b6115065145eabddfe3ae32b8f4d5~mv2.jpg",
    "surf6":  f"{WIX}/df99f9_04a8bba9fda34e22b7b5feae890d79cf~mv2.jpg",
    "booking":f"{WIX}/df99f9_f1a26a92f0044c95bab016044d325706~mv2.png",
    "gallery":[
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
        f"{WIX}/df99f9_bde010e1296b478cbbe4f885c2714338~mv2.jpg",
        f"{WIX}/df99f9_81e322c4e48d4bcbb444c6535daed131~mv2.jpg",
    ],
}

ICO = {
    "wa":'<svg viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>',
    "ig":'<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>',
    "tt":'<svg viewBox="0 0 24 24" fill="currentColor"><path d="M19.59 6.69a4.83 4.83 0 01-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 01-2.88 2.5 2.89 2.89 0 01-2.89-2.89 2.89 2.89 0 012.89-2.89c.28 0 .54.04.79.1V9.01a6.28 6.28 0 00-.79-.05 6.34 6.34 0 00-6.34 6.34 6.34 6.34 0 006.34 6.34 6.34 6.34 0 006.33-6.34V8.69a8.22 8.22 0 004.84 1.56V6.79a4.85 4.85 0 01-1.07-.1z"/></svg>',
    "menu":'<svg viewBox="0 0 24 24" fill="none"><path d="M3 7h18M3 12h18M3 17h12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
    "chev":'<svg viewBox="0 0 16 16" fill="none"><path d="M4 6l4 4 4-4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "check":'<svg viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>',
    "shield":'<svg viewBox="0 0 24 24" fill="none"><path d="M12 2l7 4v6c0 4-3 7.5-7 9-4-1.5-7-5-7-9V6l7-4z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M9 12l2 2 4-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "wave":'<svg viewBox="0 0 80 24" fill="none"><path d="M0 16C10 8,20 4,30 10C40 16,50 20,60 12C70 4,76 10,80 8" stroke="currentColor" stroke-width="3" stroke-linecap="round"/></svg>',
}

FLAG_SVG = {
    "en":'<svg viewBox="0 0 60 40" xmlns="http://www.w3.org/2000/svg"><rect width="60" height="40" fill="#012169"/><path d="M0,0 L60,40 M60,0 L0,40" stroke="#fff" stroke-width="8"/><path d="M0,0 L60,40 M60,0 L0,40" stroke="#C8102E" stroke-width="5"/><path d="M30,0 V40 M0,20 H60" stroke="#fff" stroke-width="12"/><path d="M30,0 V40 M0,20 H60" stroke="#C8102E" stroke-width="8"/></svg>',
    "fr":'<svg viewBox="0 0 60 40" xmlns="http://www.w3.org/2000/svg"><rect width="20" height="40" fill="#002395"/><rect x="20" width="20" height="40" fill="#fff"/><rect x="40" width="20" height="40" fill="#ED2939"/></svg>',
    "es":'<svg viewBox="0 0 60 40" xmlns="http://www.w3.org/2000/svg"><rect width="60" height="40" fill="#c60b1e"/><rect y="10" width="60" height="20" fill="#ffc400"/></svg>',
    "it":'<svg viewBox="0 0 60 40" xmlns="http://www.w3.org/2000/svg"><rect width="20" height="40" fill="#009246"/><rect x="20" width="20" height="40" fill="#fff"/><rect x="40" width="20" height="40" fill="#CE2B37"/></svg>',
    "de":'<svg viewBox="0 0 60 40" xmlns="http://www.w3.org/2000/svg"><rect width="60" height="13" fill="#000"/><rect y="13" width="60" height="14" fill="#DD0000"/><rect y="27" width="60" height="13" fill="#FFCE00"/></svg>',
}

def flag(lang, size=22):
    h = round(size*0.667)
    return f'<span style="width:{size}px;height:{h}px;display:inline-flex;border-radius:3px;overflow:hidden;flex-shrink:0;box-shadow:0 1px 3px rgba(0,0,0,0.22)">{FLAG_SVG.get(lang,"")}</span>'

def load(p):
    if os.path.exists(p):
        try:
            with open(p) as f: return json.load(f)
        except: return None
    return None

def fix_em(t):
    if not t: return ""
    return re.sub(r',\s*,',',', str(t).replace(" — ",", ").replace("—",",").replace("\u2014",",").replace(" – ",", ").replace("–",","))

# ─── SHARED TEMPLATES ────────────────────────────────────────────────────────
GLOBAL_JS = """<script>
window.addEventListener('scroll',()=>{
  const el=document.getElementById('scroll-progress');
  if(el){const pct=(scrollY/(document.body.scrollHeight-innerHeight))*100;el.style.width=Math.min(pct,100)+'%';}
},{passive:true});
window.addEventListener('scroll',()=>{
  const nav=document.getElementById('nav');
  if(nav)nav.classList.toggle('scrolled',scrollY>30);
},{passive:true});
const obs=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting)e.target.classList.add('up');}),{threshold:0.09});
document.querySelectorAll('.reveal').forEach(el=>obs.observe(el));
function detectLangFromPath(){const p=location.pathname;for(const l of['fr','es','it','de']){if(p===('/'+l)||p.startsWith('/'+l+'/'))return l;}return'en';}
function getBasePath(){const p=location.pathname;for(const l of['fr','es','it','de']){if(p===('/'+l)||p==='/'+l+'/')return'/';if(p.startsWith('/'+l+'/')){return p.slice(l.length+1)||'/';}}return p;}
function switchLang(l){const base=getBasePath();const np=l==='en'?base:'/'+l+base;localStorage.setItem('ngor_lang',l);location.href=np;}
function toggleLangDD(e){e.stopPropagation();document.getElementById('lang-dd').classList.toggle('open');}
document.addEventListener('click',e=>{const d=document.getElementById('lang-dd');if(d&&!d.contains(e.target))d.classList.remove('open');});
function toggleMenu(){document.getElementById('nav-links').classList.toggle('open');}
document.addEventListener('click',e=>{const nl=document.getElementById('nav-links');const nt=document.getElementById('nav-toggle');if(nl&&nt&&!nl.contains(e.target)&&!nt.contains(e.target))nl.classList.remove('open');});
document.querySelectorAll('.faq-q').forEach(q=>q.addEventListener('click',()=>q.closest('.faq-item').classList.toggle('open')));
const lb=document.getElementById('lb'),lbImg=document.getElementById('lb-img'),lbCls=document.getElementById('lb-close');
if(lb){document.querySelectorAll('.gallery-item').forEach(i=>i.addEventListener('click',()=>{lbImg.src=i.querySelector('img').src;lb.classList.add('open');}));lb.addEventListener('click',e=>{if(e.target===lb)lb.classList.remove('open');});lbCls&&lbCls.addEventListener('click',()=>lb.classList.remove('open'));document.addEventListener('keydown',e=>{if(e.key==='Escape')lb.classList.remove('open');});}
</script>"""

def lang_dropdown(current_lang, page_slug):
    slug_clean = "/" + page_slug.strip("/") if page_slug.strip("/") else ""
    opts = ""
    for l in LANGS:
        if l == current_lang: continue
        url = f"/{l}{slug_clean}/" if l != "en" else f"{slug_clean}/"
        opts += f'<a class="lang-dd-item" href="{url}" hreflang="{LANG_LOCALE[l]}">{flag(l,18)} {LANG_NAMES[l]}</a>\n'
    return f"""<div class="lang-dd" id="lang-dd">
  <button class="lang-dd-btn" onclick="toggleLangDD(event)" aria-label="Switch language">
    {flag(current_lang, 20)} {current_lang.upper()}
    <span style="width:14px;height:14px;display:inline-flex">{ICO["chev"]}</span>
  </button>
  <div class="lang-dd-menu" role="menu">{opts}</div>
</div>"""

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
    items = ""
    for slug, labels in NAV:
        label = labels.get(lang, labels["en"])
        href  = f"{pfx}{slug}/"
        cls   = "nav-link"
        if slug.strip("/")==active.strip("/") or (not slug and not active): cls += " active"
        if slug=="/booking": cls += " nav-cta"
        items += f'<a href="{href}" class="{cls}">{label}</a>\n'
    return f"""<nav id="nav">
  <div class="nav-inner">
    <a href="{pfx}/" class="nav-logo">
      <img src="{LOGO}" alt="Ngor Surfcamp Teranga" width="130" height="44" loading="eager">
    </a>
    <div class="nav-links" id="nav-links">{items}</div>
    <div class="nav-right">
      {lang_dropdown(lang, page_slug)}
      <a href="https://wa.me/221789257025" target="_blank" rel="noopener" class="nav-wa" aria-label="WhatsApp">
        <span style="width:18px;height:18px;display:inline-flex">{ICO['wa']}</span>
        <span class="nav-wa-label">WhatsApp</span>
      </a>
      <button class="nav-toggle" id="nav-toggle" aria-label="Menu" onclick="toggleMenu()">
        <span style="width:22px;height:22px;display:inline-flex;color:#fff">{ICO['menu']}</span>
      </button>
    </div>
  </div>
</nav>"""

def footer_html(lang, pfx):
    LINKS = [("/surf-house",{"en":"Surf House","fr":"Surf House","es":"Surf House","it":"Surf House","de":"Surf House"}),("/island",{"en":"Island","fr":"Île","es":"Isla","it":"Isola","de":"Insel"}),("/surfing",{"en":"Surfing","fr":"Surf","es":"Surf","it":"Surf","de":"Surfen"}),("/blog",{"en":"Blog","fr":"Blog","es":"Blog","it":"Blog","de":"Blog"}),("/gallery",{"en":"Gallery","fr":"Galerie","es":"Galería","it":"Galleria","de":"Galerie"}),("/faq",{"en":"FAQ","fr":"FAQ","es":"FAQ","it":"FAQ","de":"FAQ"}),("/booking",{"en":"Book Now","fr":"Réserver","es":"Reservar","it":"Prenota","de":"Buchen"})]
    lk = "\n".join([f'<a href="{pfx}{s}/">{l.get(lang,l["en"])}</a>' for s,l in LINKS])
    fl = " ".join([f'<a href="{"" if l=="en" else "/"+l}/" style="opacity:0.55;transition:opacity 0.2s;display:inline-flex" hreflang="{LANG_LOCALE[l]}" title="{LANG_NAMES[l]}" onmouseover="this.style.opacity=1" onmouseout="this.style.opacity=0.55">{flag(l,22)}</a>' for l in LANGS])
    ABOUT={"en":"Premium surf camp on Ngor Island, Dakar, Senegal. All levels. Licensed by the Senegalese Federation of Surfing.","fr":"Surf camp premium sur l'île de Ngor, Dakar, Sénégal. Tous niveaux. Agréé Fédération Sénégalaise de Surf.","es":"Surf camp premium en la isla de Ngor, Dakar, Senegal. Todos los niveles. Licenciado.","it":"Surf camp premium sull'isola di Ngor, Dakar, Senegal. Tutti i livelli. Autorizzato.","de":"Premium Surfcamp auf Ngor Island, Dakar, Senegal. Alle Level. Lizenziert."}
    COPY={"en":"© 2025 Ngor Surfcamp Teranga. All rights reserved.","fr":"© 2025 Ngor Surfcamp Teranga. Tous droits réservés.","es":"© 2025 Ngor Surfcamp Teranga. Todos los derechos reservados.","it":"© 2025 Ngor Surfcamp Teranga. Tutti i diritti riservati.","de":"© 2025 Ngor Surfcamp Teranga. Alle Rechte vorbehalten."}
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
          <a href="https://wa.me/221789257025" target="_blank" class="soc-btn wa" aria-label="WhatsApp"><span style="width:18px;height:18px;display:inline-flex">{ICO["wa"]}</span></a>
          <a href="https://www.instagram.com/ngorsurfcampteranga" target="_blank" class="soc-btn ig" aria-label="Instagram"><span style="width:18px;height:18px;display:inline-flex">{ICO["ig"]}</span></a>
          <a href="https://www.tiktok.com/@ngorsurfcampteranga" target="_blank" class="soc-btn tt" aria-label="TikTok"><span style="width:18px;height:18px;display:inline-flex">{ICO["tt"]}</span></a>
        </div>
      </div>
      <div class="footer-col"><h4>{EXP[lang]}</h4>{lk}</div>
      <div class="footer-col"><h4>{CON[lang]}</h4>
        <a href="https://wa.me/221789257025" target="_blank">WhatsApp: +221 78 925 70 25</a>
        <a href="mailto:info@surfcampsenegal.com">info@surfcampsenegal.com</a>
        <a href="{pfx}/booking/">{"Book your stay" if lang=="en" else "Réserver" if lang=="fr" else "Reservar" if lang=="es" else "Prenota" if lang=="it" else "Buchen"}</a>
      </div>
      <div class="footer-col"><h4>{FOL[lang]}</h4>
        <a href="https://www.instagram.com/ngorsurfcampteranga" target="_blank">Instagram</a>
        <a href="https://www.tiktok.com/@ngorsurfcampteranga" target="_blank">TikTok</a>
        <a href="https://wa.me/221789257025" target="_blank">WhatsApp</a>
      </div>
    </div>
    <div class="footer-bottom">
      <p>{COPY[lang]}</p>
      <div style="display:flex;gap:10px;align-items:center">{fl}</div>
    </div>
  </div>
</footer>
<a href="https://wa.me/221789257025" target="_blank" rel="noopener" id="float-wa" aria-label="Chat on WhatsApp">
  <span style="width:26px;height:26px;display:inline-flex">{ICO["wa"]}</span>
</a>"""

def head(title, meta, lang, can="", hrl="", og=""):
    og_img = og or IMGS["surf3"]
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{fix_em(title)}</title>
<meta name="description" content="{fix_em(meta)}">
<meta property="og:title" content="{fix_em(title)}">
<meta property="og:description" content="{fix_em(meta)}">
<meta property="og:image" content="{og_img}">
<meta property="og:type" content="website">
<meta name="robots" content="index,follow">
{can}{hrl}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Raleway:ital,wght@0,300;0,400;0,600;0,700;0,800;0,900;1,400&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/css/style.css">
</head><body>
<div id="scroll-progress"></div>"""

def close_page():
    return f"\n{GLOBAL_JS}\n</body>\n</html>"

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

# ════════════════════════════════════════════════════════════════════════════════
# BOOKING PAGE — Beautiful, multilingual, WhatsApp form
# ════════════════════════════════════════════════════════════════════════════════
def build_booking(lang):
    pfx = LANG_PREFIX[lang]
    p   = load(f"{PAGES_D}/{lang}_book_online.json") or {}
    h1  = fix_em(p.get("h1","Book Your Stay"))
    sub = fix_em(p.get("hero_subtitle","Check availability and we'll take care of the rest!"))
    title= fix_em(p.get("title_tag","Book Your Surf Stay | Ngor Surfcamp Teranga"))
    meta = fix_em(p.get("meta_description","Book your surf camp stay at Ngor Island, Dakar, Senegal."))

    T = {
        "h2":       {"en":"Check Availability & Book Your Stay","fr":"Vérifiez les disponibilités & Réservez","es":"Consulta disponibilidad y Reserva","it":"Controlla disponibilità e Prenota","de":"Verfügbarkeit prüfen & Buchen"},
        "sub":      {"en":"Tell us your dates and we'll find the perfect room for your surf adventure.","fr":"Donnez-nous vos dates et nous trouverons la chambre parfaite pour votre aventure surf.","es":"Cuéntanos tus fechas y encontraremos la habitación perfecta para tu aventura surf.","it":"Dicci le tue date e troveremo la camera perfetta per la tua avventura surf.","de":"Teilen Sie uns Ihre Daten mit und wir finden das perfekte Zimmer für Ihr Surferlebnis."},
        "fname":    {"en":"First Name","fr":"Prénom","es":"Nombre","it":"Nome","de":"Vorname"},
        "lname":    {"en":"Last Name","fr":"Nom de famille","es":"Apellido","it":"Cognome","de":"Nachname"},
        "email":    {"en":"E-mail","fr":"E-mail","es":"E-mail","it":"E-mail","de":"E-Mail"},
        "email_ph": {"en":"yourname@email.com","fr":"votremail@email.com","es":"sunombre@email.com","it":"tuonome@email.com","de":"ihrname@email.com"},
        "spam":     {"en":"No spam, just waves and logistics.","fr":"Pas de spam, juste des vagues et de la logistique.","es":"Sin spam, solo olas y logística.","it":"Niente spam, solo onde e logistica.","de":"Kein Spam, nur Wellen und Logistik."},
        "phone":    {"en":"WhatsApp / Phone Number","fr":"WhatsApp / Numéro de téléphone","es":"WhatsApp / Número de teléfono","it":"WhatsApp / Numero di telefono","de":"WhatsApp / Telefonnummer"},
        "phone_ph": {"en":"+ (Country Code) 123 456 789","fr":"+ (Indicatif) 06 12 34 56 78","es":"+ (Código) 612 345 678","it":"+ (Prefisso) 123 456 789","de":"+ (Vorwahl) 123 456 789"},
        "level":    {"en":"What's your current surf level?","fr":"Quel est votre niveau de surf actuel ?","es":"¿Cuál es tu nivel de surf actual?","it":"Qual è il tuo livello di surf attuale?","de":"Was ist Ihr aktuelles Surflevel?"},
        "choose":   {"en":"Choose an option","fr":"Choisissez une option","es":"Elige una opción","it":"Scegli un'opzione","de":"Option wählen"},
        "beginner": {"en":"Beginner — never surfed or just starting","fr":"Débutant — jamais surfé ou tout début","es":"Principiante — nunca surfeado o empezando","it":"Principiante — mai surfato o appena iniziato","de":"Anfänger — noch nie gesurft oder Einstieg"},
        "basic":    {"en":"Basic — can stand up, learning turns","fr":"Basique — tient debout, apprend les virages","es":"Básico — puede levantarse, aprendiendo giros","it":"Base — riesce a stare in piedi, impara le virate","de":"Grundlagen — kann stehen, lernt Kurven"},
        "inter":    {"en":"Intermediate — comfortable, working on technique","fr":"Intermédiaire — à l'aise, travaille la technique","es":"Intermedio — cómodo, trabajando técnica","it":"Intermedio — a proprio agio, lavora sulla tecnica","de":"Fortgeschrittene — sicher, Technik verbessern"},
        "advanced": {"en":"Advanced — ripping, pushing limits","fr":"Avancé — surfe bien, repousse ses limites","es":"Avanzado — surfea muy bien, supera sus límites","it":"Avanzato — surfa bene, supera i limiti","de":"Fortgeschritten — surft gut, Grenzen ausreizen"},
        "guests":   {"en":"How many guests are coming?","fr":"Combien de personnes viennent ?","es":"¿Cuántas personas vienen?","it":"Quante persone vengono?","de":"Wie viele Personen kommen?"},
        "guests_ph":{"en":"e.g., 2 Surfers","fr":"ex. 2 surfeurs","es":"p.ej., 2 surfistas","it":"es. 2 surfisti","de":"z.B. 2 Surfer"},
        "arrive":   {"en":"When do you arrive?","fr":"Quand arrivez-vous ?","es":"¿Cuándo llegas?","it":"Quando arrivi?","de":"Wann reisen Sie an?"},
        "leave":    {"en":"When do you leave?","fr":"Quand partez-vous ?","es":"¿Cuándo te vas?","it":"Quando parti?","de":"Wann reisen Sie ab?"},
        "flexible": {"en":"I'm flexible — tell me when the swell is best!","fr":"Je suis flexible — dites-moi quand le swell est le meilleur !","es":"Soy flexible — ¡dime cuándo es mejor el swell!","it":"Sono flessibile — dimmi quando il swell è migliore!","de":"Ich bin flexibel — sagen Sie mir, wann der Swell am besten ist!"},
        "goal":     {"en":"What is your #1 goal for this trip?","fr":"Quel est votre objectif principal pour ce voyage ?","es":"¿Cuál es tu objetivo principal para este viaje?","it":"Qual è il tuo obiettivo principale per questo viaggio?","de":"Was ist Ihr Hauptziel für diese Reise?"},
        "goal_ph":  {"en":"e.g., Improving my cutback, exploring Dakar, or just relaxing by the pool.","fr":"ex. Améliorer mon cutback, explorer Dakar, ou juste me détendre au bord de la piscine.","es":"p.ej., Mejorar mi cutback, explorar Dakar, o simplemente relajarme junto a la piscina.","it":"es. Migliorare il mio cutback, esplorare Dakar, o semplicemente rilassarmi a bordo piscina.","de":"z.B. Cutback verbessern, Dakar erkunden oder einfach am Pool entspannen."},
        "cta":      {"en":"Check Availability & Prices","fr":"Vérifier disponibilités & Tarifs","es":"Consultar disponibilidad y Precios","it":"Controlla disponibilità e Prezzi","de":"Verfügbarkeit & Preise prüfen"},
        "or":       {"en":"Or contact us directly:","fr":"Ou contactez-nous directement :","es":"O contáctanos directamente:","it":"O contattaci direttamente:","de":"Oder kontaktieren Sie uns direkt:"},
        "reply":    {"en":"No spam. We reply within 24 hours.","fr":"Pas de spam. Réponse sous 24h.","es":"Sin spam. Respondemos en 24h.","it":"Nessuno spam. Rispondiamo entro 24h.","de":"Kein Spam. Antwort innerhalb von 24h."},
        "steps_h":  {"en":"Booking made easy","fr":"Réservation simplifiée","es":"Reserva fácil","it":"Prenotazione facile","de":"Einfache Buchung"},
        "step1":    {"en":"Choose your dates","fr":"Choisissez vos dates","es":"Elige tus fechas","it":"Scegli le tue date","de":"Daten wählen"},
        "step2":    {"en":"Fill the form or message us on WhatsApp","fr":"Remplissez le formulaire ou écrivez-nous sur WhatsApp","es":"Rellena el formulario o escríbenos por WhatsApp","it":"Compila il modulo o scrivici su WhatsApp","de":"Formular ausfüllen oder WhatsApp schreiben"},
        "step3":    {"en":"We confirm your room & package within 24h","fr":"Nous confirmons votre chambre & package sous 24h","es":"Confirmamos tu habitación y paquete en 24h","it":"Confermiamo camera e pacchetto entro 24h","de":"Wir bestätigen Zimmer & Paket innerhalb von 24h"},
        "incl_h":   {"en":"Everything included","fr":"Tout est inclus","es":"Todo incluido","it":"Tutto incluso","de":"Alles inklusive"},
        "i1":{"en":"Accommodation in private or shared room","fr":"Hébergement en chambre privée ou partagée","es":"Alojamiento en habitación privada o compartida","it":"Alloggio in camera privata o condivisa","de":"Unterkunft im Einzel- oder Mehrbettzimmer"},
        "i2":{"en":"Breakfast & dinner (authentic Senegalese cuisine)","fr":"Petit-déjeuner & dîner (cuisine sénégalaise authentique)","es":"Desayuno y cena (cocina senegalesa auténtica)","it":"Colazione e cena (cucina senegalese autentica)","de":"Frühstück & Abendessen (authentische senegalesische Küche)"},
        "i3":{"en":"Daily surf guiding to the best spots","fr":"Guide surf quotidien vers les meilleurs spots","es":"Guía surf diario a los mejores spots","it":"Guida surf giornaliera ai migliori spot","de":"Tägliche Surf-Führung zu den besten Spots"},
        "i4":{"en":"Boat transfers to Ngor Right & Left","fr":"Transferts en pirogue vers Ngor Right & Left","es":"Traslados en bote a Ngor Right & Left","it":"Trasferimenti in barca a Ngor Right & Left","de":"Bootüberfahrten zu Ngor Right & Left"},
        "i5":{"en":"Free surf theory classes","fr":"Cours de théorie surf gratuits","es":"Clases de teoría surf gratuitas","it":"Lezioni di teoria surf gratuite","de":"Kostenlose Surf-Theoriestunden"},
        "i6":{"en":"Pool access & shared spaces","fr":"Accès piscine & espaces communs","es":"Acceso piscina y áreas comunes","it":"Accesso piscina e aree comuni","de":"Poolzugang & Gemeinschaftsbereiche"},
        "i7":{"en":"Free Wi-Fi & daily room cleaning","fr":"Wi-Fi gratuit & ménage quotidien","es":"Wi-Fi gratis y limpieza diaria","it":"Wi-Fi gratuito e pulizia giornaliera","de":"Kostenloses WLAN & tägliche Reinigung"},
        "err_fname":{"en":"Please enter your first name.","fr":"Veuillez entrer votre prénom.","es":"Por favor, introduce tu nombre.","it":"Per favore, inserisci il tuo nome.","de":"Bitte Vornamen eingeben."},
        "err_email":{"en":"Please enter a valid email address.","fr":"Veuillez entrer une adresse email valide.","es":"Por favor, introduce un email válido.","it":"Per favore, inserisci un'email valida.","de":"Bitte gültige E-Mail-Adresse eingeben."},
        "err_date": {"en":"Departure must be after arrival.","fr":"Le départ doit être après l'arrivée.","es":"La salida debe ser después de la llegada.","it":"La partenza deve essere dopo l'arrivo.","de":"Abreise muss nach Anreise sein."},
    }

    # Country code list (common countries + Senegal first)
    COUNTRIES = [
        ("+221","🇸🇳 SN +221"),("+33","🇫🇷 FR +33"),("+34","🇪🇸 ES +34"),
        ("+39","🇮🇹 IT +39"),("+49","🇩🇪 DE +49"),("+44","🇬🇧 UK +44"),
        ("+1","🇺🇸 US +1"),("+32","🇧🇪 BE +32"),("+41","🇨🇭 CH +41"),
        ("+31","🇳🇱 NL +31"),("+351","🇵🇹 PT +351"),("+212","🇲🇦 MA +212"),
        ("+55","🇧🇷 BR +55"),("+61","🇦🇺 AU +61"),("other","🌍 Other"),
    ]
    cc_opts = "\n".join([f'<option value="{v}">{l}</option>' for v,l in COUNTRIES])

    html = head(title, meta, lang, can_tag("booking",lang), hrl_tags("booking"), IMGS["booking"])
    html += nav_html("booking", lang, pfx, "/booking")
    html += f"""
<main>
  <!-- PAGE HEADER -->
  <header class="page-header" style="background-image:url('{IMGS['surf4']}')" role="banner">
    <h1>{h1}</h1>
    <p>{sub}</p>
  </header>

  <section class="section" id="booking-section">
    <div class="container">
      <div class="split" style="gap:56px;align-items:flex-start">

        <!-- THE FORM -->
        <div>
          <span class="s-label">{"Book" if lang=="en" else "Réserver" if lang=="fr" else "Reservar" if lang=="es" else "Prenota" if lang=="it" else "Buchen"}</span>
          <h2 class="s-title" style="margin-bottom:8px">{T['h2'][lang]}</h2>
          <p style="color:#6b7280;font-size:15px;margin-bottom:32px">{T['sub'][lang]}</p>

          <form id="booking-form" class="form-card" novalidate>
            <!-- Name row -->
            <div class="form-row">
              <div class="form-group">
                <label class="form-label" for="f-fname">{T['fname'][lang]} <span style="color:var(--fire)">*</span></label>
                <input type="text" id="f-fname" class="form-input f-name" placeholder="e.g., Kelly" autocomplete="given-name" required>
                <div class="form-error" id="err-fname" style="display:none;color:var(--fire);font-size:12.5px;margin-top:5px">{T['err_fname'][lang]}</div>
              </div>
              <div class="form-group">
                <label class="form-label" for="f-lname">{T['lname'][lang]}</label>
                <input type="text" id="f-lname" class="form-input f-lname" placeholder="Slater" autocomplete="family-name">
              </div>
            </div>

            <!-- Email -->
            <div class="form-group">
              <label class="form-label" for="f-email">{T['email'][lang]} <span style="color:var(--fire)">*</span></label>
              <input type="email" id="f-email" class="form-input f-email" placeholder="{T['email_ph'][lang]}" autocomplete="email" required>
              <div class="form-error" id="err-email" style="display:none;color:var(--fire);font-size:12.5px;margin-top:5px">{T['err_email'][lang]}</div>
              <p style="font-size:12.5px;color:#9ca3af;margin-top:5px">{T['spam'][lang]}</p>
            </div>

            <!-- Phone with country code -->
            <div class="form-group">
              <label class="form-label" for="f-phone">{T['phone'][lang]}</label>
              <div style="display:flex;gap:8px">
                <select id="f-cc" class="form-select f-cc" style="width:auto;min-width:130px;flex-shrink:0">
                  {cc_opts}
                </select>
                <input type="tel" id="f-phone" class="form-input f-phone" placeholder="{T['phone_ph'][lang]}" autocomplete="tel" style="flex:1">
              </div>
            </div>

            <!-- Surf level -->
            <div class="form-group">
              <label class="form-label" for="f-level">{T['level'][lang]} <span style="color:var(--fire)">*</span></label>
              <select id="f-level" class="form-select f-level" required>
                <option value="">{T['choose'][lang]}</option>
                <option value="beginner">{T['beginner'][lang]}</option>
                <option value="basic">{T['basic'][lang]}</option>
                <option value="intermediate">{T['inter'][lang]}</option>
                <option value="advanced">{T['advanced'][lang]}</option>
              </select>
            </div>

            <!-- Guests + dates row -->
            <div class="form-row">
              <div class="form-group">
                <label class="form-label" for="f-guests">{T['guests'][lang]}</label>
                <select id="f-guests" class="form-select f-guests">
                  <option value="">—</option>
                  {"".join([f'<option value="{n}">{n}</option>' for n in range(1,13)])}
                </select>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label" for="f-arrive">{T['arrive'][lang]}</label>
                <input type="date" id="f-arrive" class="form-input f-arrive">
              </div>
              <div class="form-group">
                <label class="form-label" for="f-leave">{T['leave'][lang]}</label>
                <input type="date" id="f-leave" class="form-input f-leave">
                <div class="form-error" id="err-date" style="display:none;color:var(--fire);font-size:12.5px;margin-top:5px">{T['err_date'][lang]}</div>
              </div>
            </div>

            <!-- Flexible checkbox -->
            <div class="form-group">
              <label class="form-check" style="cursor:pointer">
                <input type="checkbox" id="f-flex" class="f-flex" style="accent-color:var(--fire);width:17px;height:17px">
                <span>{T['flexible'][lang]}</span>
              </label>
            </div>

            <!-- Goal -->
            <div class="form-group">
              <label class="form-label" for="f-goal">{T['goal'][lang]}</label>
              <textarea id="f-goal" class="form-textarea f-goal" rows="3" placeholder="{T['goal_ph'][lang]}"></textarea>
            </div>

            <!-- Submit -->
            <button type="submit" class="btn btn-fire" style="width:100%;font-size:15px;padding:15px;justify-content:center;margin-top:8px">
              <span style="width:20px;height:20px;display:inline-flex">{ICO["wa"]}</span>
              {T['cta'][lang]}
            </button>
            <p style="text-align:center;margin-top:12px;font-size:13px;color:#9ca3af">{T['reply'][lang]}</p>
          </form>

          <!-- Direct contact -->
          <div style="margin-top:28px;padding:20px 24px;border-radius:14px;border:1px solid #e5e7eb;background:#fafafa">
            <p style="font-weight:600;font-size:14px;margin-bottom:14px">{T['or'][lang]}</p>
            <div style="display:flex;flex-wrap:wrap;gap:12px">
              <a href="https://wa.me/221789257025" target="_blank" rel="noopener" class="btn btn-wa btn-sm">
                <span style="width:16px;height:16px;display:inline-flex">{ICO["wa"]}</span>
                +221 78 925 70 25
              </a>
              <a href="mailto:info@surfcampsenegal.com" class="btn btn-deep btn-sm">
                info@surfcampsenegal.com
              </a>
            </div>
          </div>
        </div>

        <!-- SIDEBAR: Steps + Inclusions -->
        <div>
          <!-- Steps -->
          <div class="form-card reveal" style="margin-bottom:28px">
            <h3 style="font-size:18px;margin-bottom:20px">{T['steps_h'][lang]}</h3>
            {"".join([f'<div style="display:flex;gap:14px;align-items:flex-start;margin-bottom:16px"><div style="width:32px;height:32px;border-radius:50%;background:var(--fire);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:15px;flex-shrink:0">{n}</div><div style="font-size:14.5px;color:#374151;padding-top:4px">{t}</div></div>' for n,t in [(1,T['step1'][lang]),(2,T['step2'][lang]),(3,T['step3'][lang])]])}
          </div>

          <!-- Inclusions -->
          <div class="form-card reveal">
            <h3 style="font-size:18px;margin-bottom:20px">{T['incl_h'][lang]}</h3>
            {"".join([f'<div style="display:flex;align-items:flex-start;gap:10px;margin-bottom:12px"><span style="width:18px;height:18px;display:inline-flex;color:#22c55e;flex-shrink:0;margin-top:1px">{ICO["check"]}</span><span style="font-size:14px;color:#374151">{t}</span></div>' for t in [T['i1'][lang],T['i2'][lang],T['i3'][lang],T['i4'][lang],T['i5'][lang],T['i6'][lang],T['i7'][lang]]])}
          </div>

          <!-- Trust -->
          <div style="margin-top:20px;padding:16px 20px;border-radius:12px;background:rgba(10,37,64,0.04);border:1px solid rgba(10,37,64,0.08);display:flex;align-items:center;gap:12px">
            <span style="width:24px;height:24px;display:inline-flex;color:var(--fire)">{ICO["shield"]}</span>
            <div>
              <div style="font-weight:700;font-size:13px;color:var(--navy)">{"Licensed by the Senegalese Federation of Surfing" if lang=="en" else "Agréé par la Fédération Sénégalaise de Surf" if lang=="fr" else "Licenciado por la Federación Senegalesa de Surf" if lang=="es" else "Autorizzato dalla Federazione Senegalese di Surf" if lang=="it" else "Lizenziert vom senegalesischen Surfverband"}</div>
              <div style="font-size:12px;color:#9ca3af">{"Professional, safe, certified coaches." if lang=="en" else "Coachs professionnels, sécurisés, certifiés." if lang=="fr" else "Coaches profesionales, seguros, certificados." if lang=="es" else "Coach professionali, sicuri, certificati." if lang=="it" else "Professionelle, sichere, zertifizierte Coaches."}</div>
            </div>
          </div>
        </div>

      </div>
    </div>
  </section>
</main>

<!-- FORM LOGIC -->
<script>
(function(){{
  const form    = document.getElementById('booking-form');
  const fFname  = document.getElementById('f-fname');
  const fEmail  = document.getElementById('f-email');
  const fArrive = document.getElementById('f-arrive');
  const fLeave  = document.getElementById('f-leave');
  const fLevel  = document.getElementById('f-level');
  const fGuests = document.getElementById('f-guests');
  const fPhone  = document.getElementById('f-phone');
  const fCC     = document.getElementById('f-cc');
  const fFlex   = document.getElementById('f-flex');
  const fGoal   = document.getElementById('f-goal');

  // Set min date to today
  const today = new Date().toISOString().split('T')[0];
  fArrive.setAttribute('min', today);
  fLeave.setAttribute('min', today);

  fArrive.addEventListener('change', function(){{
    if(this.value) fLeave.setAttribute('min', this.value);
  }});

  function showError(id, show){{
    const el = document.getElementById(id);
    if(el) el.style.display = show ? 'block' : 'none';
  }}
  function markField(el, valid){{
    el.style.borderColor = valid ? '#22c55e' : 'var(--fire)';
  }}

  form.addEventListener('submit', function(e){{
    e.preventDefault();
    let valid = true;

    // Validate name (trim, case-insensitive)
    const name = fFname.value.trim();
    if(!name){{ showError('err-fname', true); markField(fFname, false); valid = false; }}
    else {{ showError('err-fname', false); markField(fFname, true); }}

    // Validate email (very permissive)
    const email = fEmail.value.trim().toLowerCase();
    const emailOk = /^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$/.test(email);
    if(!emailOk){{ showError('err-email', true); markField(fEmail, false); valid = false; }}
    else {{ showError('err-email', false); markField(fEmail, true); }}

    // Validate dates
    if(fArrive.value && fLeave.value && fLeave.value <= fArrive.value){{
      showError('err-date', true); markField(fLeave, false); valid = false;
    }} else {{ showError('err-date', false); if(fLeave.value) markField(fLeave, true); }}

    if(!valid) return;

    // Build WhatsApp message
    const lname   = document.getElementById('f-lname').value.trim();
    const fullName= name + (lname ? ' ' + lname : '');
    const cc      = fCC.value !== 'other' ? fCC.value : '';
    const phone   = (cc + ' ' + fPhone.value.trim()).trim();
    const level   = fLevel.options[fLevel.selectedIndex]?.text || '';
    const guests  = fGuests.value;
    const arrive  = fArrive.value;
    const leave   = fLeave.value;
    const flex    = fFlex.checked;
    const goal    = fGoal.value.trim();

    let msg = 'Hello Ngor Surfcamp! ';
    msg += 'Name: ' + fullName + '. ';
    if(email)  msg += 'Email: ' + email + '. ';
    if(phone.length > 3) msg += 'Phone: ' + phone + '. ';
    if(level)  msg += 'Level: ' + level + '. ';
    if(guests) msg += 'Guests: ' + guests + '. ';
    if(flex)   msg += 'Flexible on dates. ';
    else {{
      if(arrive) msg += 'Arrival: ' + arrive + '. ';
      if(leave)  msg += 'Departure: ' + leave + '. ';
    }}
    if(goal) msg += 'Goal: ' + goal;

    window.open('https://wa.me/221789257025?text=' + encodeURIComponent(msg), '_blank');
  }});

  // Real-time validation on blur (not on every keystroke)
  fFname.addEventListener('blur', function(){{
    if(this.value.trim()) {{ showError('err-fname',false); markField(this,true); }}
  }});
  fEmail.addEventListener('blur', function(){{
    const ok = /^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$/.test(this.value.trim().toLowerCase());
    if(ok) {{ showError('err-email',false); markField(this,true); }}
  }});
}})();
</script>"""
    html += footer_html(lang, pfx)
    html += close_page()
    return html

# ════════════════════════════════════════════════════════════════════════════════
# SURF HOUSE PAGE
# ════════════════════════════════════════════════════════════════════════════════
def build_surf_house(lang):
    pfx = LANG_PREFIX[lang]
    p   = load(f"{PAGES_D}/{lang}_surf_house.json") or {}
    h1  = fix_em(p.get("h1","Surf House on Ngor Island"))
    sub = fix_em(p.get("hero_subtitle","Your home by the ocean"))
    title= fix_em(p.get("title_tag","Ngor Surf House | Surf Camp Stay in Senegal"))
    meta = fix_em(p.get("meta_description","Stay at our surf house on Ngor Island, Dakar. Pool, sea views, daily meals."))
    intro= fix_em(p.get("intro",""))

    FEAT = [
        ("🚤",{"en":"Surf Transfers","fr":"Transferts surf","es":"Traslados surf","it":"Trasferimenti surf","de":"Surf-Transfers"},{"en":"Daily boat to Ngor Right & Left. Minibus to Dakar's best breaks.","fr":"Pirogue quotidienne vers Ngor Right & Left. Minibus vers les meilleurs spots de Dakar.","es":"Piroga diaria a Ngor Right & Left. Minibús a los mejores spots de Dakar.","it":"Barca giornaliera a Ngor Right & Left. Minibus verso i migliori spot di Dakar.","de":"Tägliches Boot zu Ngor Right & Left. Minibus zu Dakars besten Spots."}),
        ("🍽️",{"en":"Breakfast & Dinner","fr":"Petit-déjeuner & Dîner","es":"Desayuno y Cena","it":"Colazione e Cena","de":"Frühstück & Abendessen"},{"en":"Authentic Senegalese meals daily. Filtered water, tea & coffee included.","fr":"Plats sénégalais authentiques. Eau filtrée, thé & café inclus.","es":"Comidas senegalesas auténticas diariamente. Agua filtrada, té y café incluidos.","it":"Pasti senegalesi autentici quotidianamente. Acqua filtrata, tè e caffè inclusi.","de":"Authentische senegalesische Mahlzeiten täglich. Gefiltertes Wasser, Tee & Kaffee inklusive."}),
        ("🏄",{"en":"Daily Surf Guiding","fr":"Guide surf quotidien","es":"Guía surf diario","it":"Guida surf giornaliera","de":"Tägliche Surf-Führung"},{"en":"We guide you to the best spot every day. All levels welcomed.","fr":"Nous vous guidons vers le meilleur spot chaque jour. Tous niveaux.","es":"Te llevamos al mejor spot cada día. Todos los niveles.","it":"Ti guidiamo verso il miglior spot ogni giorno. Tutti i livelli.","de":"Wir führen Sie täglich zum besten Spot. Alle Level willkommen."}),
        ("📚",{"en":"Surf Theory Classes","fr":"Cours de théorie surf","es":"Clases de teoría surf","it":"Lezioni di teoria surf","de":"Surf-Theoriestunden"},{"en":"Free theory sessions: paddling, pop-up, turns & ocean reading.","fr":"Sessions théorie gratuites : paddle, pop-up, virages & lecture de l'océan.","es":"Sesiones de teoría gratuitas: remo, pop-up, giros & lectura del océano.","it":"Sessioni di teoria gratuite: paddling, pop-up, virate & lettura dell'oceano.","de":"Kostenlose Theoriestunden: Paddeln, Pop-up, Kurven & Ozean lesen."}),
        ("🏊",{"en":"Pool & Common Areas","fr":"Piscine & espaces communs","es":"Piscina & áreas comunes","it":"Piscina & aree comuni","de":"Pool & Gemeinschaftsbereiche"},{"en":"Outdoor pool, sea terrace and chill zones. Ngor Island is your backyard.","fr":"Piscine extérieure, terrasse vue mer. L'île de Ngor est votre arrière-cour.","es":"Piscina exterior, terraza con vistas al mar. La isla de Ngor es tu patio trasero.","it":"Piscina esterna, terrazza vista mare. L'isola di Ngor è il tuo giardino.","de":"Außenpool, Meerterrasse. Ngor Island ist Ihr Garten."}),
        ("📶",{"en":"Free Wi-Fi & Daily Cleaning","fr":"Wi-Fi gratuit & ménage quotidien","es":"Wi-Fi gratis y limpieza diaria","it":"Wi-Fi gratuito e pulizia giornaliera","de":"Kostenloses WLAN & tägliche Reinigung"},{"en":"Stay connected. Rooms cleaned daily so you can focus on the waves.","fr":"Restez connecté. Chambres nettoyées quotidiennement.","es":"Mantente conectado. Habitaciones limpias diariamente.","it":"Rimani connesso. Camere pulite quotidianamente.","de":"Bleib verbunden. Zimmer täglich gereinigt."}),
    ]
    feats_html = "".join([f'<div class="feat reveal"><div class="feat-icon" style="font-size:20px">{ic}</div><div><div class="feat-title">{t.get(lang,t["en"])}</div><div class="feat-text">{d.get(lang,d["en"])}</div></div></div>' for ic,t,d in FEAT])
    gal_imgs = [IMGS["house2"],IMGS["house3"],IMGS["house4"],IMGS["food"],IMGS["pool"],IMGS["surf2"]]
    gal_html = "".join([f'<div class="gallery-item"><img src="{u}" alt="Ngor Surf House" loading="lazy"></div>' for u in gal_imgs])
    BOOK = {"en":"Book Your Room","fr":"Réserver votre chambre","es":"Reservar tu habitación","it":"Prenota la tua stanza","de":"Zimmer buchen"}
    INTRO_FB = {"en":"Tucked between turquoise ocean and the laid-back rhythm of Ngor Island, our surf house is your base camp for waves, community and authentic West African hospitality.","fr":"Niché entre l'océan turquoise et le rythme détendu de l'île de Ngor, notre surf house est votre camp de base pour les vagues, la communauté et l'hospitalité authentique d'Afrique de l'Ouest.","es":"Enclavada entre el océano turquesa y el ritmo relajado de Ngor Island, nuestra surf house es tu campo base para olas, comunidad y hospitalidad auténtica de África Occidental.","it":"Immersa tra l'oceano turchese e il ritmo rilassato di Ngor Island, la nostra surf house è il tuo campo base per onde, comunità e autentica ospitalità dell'Africa Occidentale.","de":"Zwischen dem türkisblauen Ozean und dem entspannten Rhythmus von Ngor Island ist unser Surf House Ihre Basislager für Wellen, Gemeinschaft und authentische westafrikanische Gastfreundschaft."}
    AMN = {"en":"What's Included","fr":"Ce qui est inclus","es":"Qué está incluido","it":"Cosa è incluso","de":"Inbegriffen"}
    LIFE = {"en":"Life at the Surf House","fr":"La vie à la Surf House","es":"Vida en la Surf House","it":"La vita alla Surf House","de":"Leben im Surf House"}
    CTA_H = {"en":"Ready to book your stay?","fr":"Prêt à réserver votre séjour ?","es":"Listo para reservar tu estancia?","it":"Pronto a prenotare il tuo soggiorno?","de":"Bereit, Ihren Aufenthalt zu buchen?"}
    CTA_P = {"en":"Contact us on WhatsApp for availability and prices. We reply within 24h.","fr":"Contactez-nous sur WhatsApp pour les disponibilités et les tarifs. Réponse sous 24h.","es":"Contáctanos por WhatsApp para disponibilidad y precios. Respondemos en 24h.","it":"Contattaci su WhatsApp per disponibilità e prezzi. Rispondiamo entro 24h.","de":"Kontaktieren Sie uns per WhatsApp für Verfügbarkeit und Preise. Antwort innerhalb von 24h."}
    ACCOM = {"en":"Accommodation","fr":"Hébergement","es":"Alojamiento","it":"Alloggio","de":"Unterkunft"}
    ROOM_H = {"en":"Private & Shared Rooms","fr":"Chambres privées et partagées","es":"Habitaciones privadas y compartidas","it":"Camere private e condivise","de":"Einzel- und Mehrbettzimmer"}

    html = head(title, meta, lang, can_tag("surf-house",lang), hrl_tags("surf-house"), IMGS["house"])
    html += nav_html("surf-house", lang, pfx, "/surf-house")
    html += f"""
<main>
  <header class="page-header" style="background-image:url('{IMGS['house']}')" role="banner">
    <h1>{h1}</h1><p>{sub}</p>
  </header>
  <section class="section">
    <div class="container">
      <div class="split reveal">
        <div>
          <span class="s-label">{ACCOM[lang]}</span>
          <h2 class="s-title">{ROOM_H[lang]}</h2>
          <p class="s-sub" style="margin-bottom:28px">{intro or INTRO_FB.get(lang,"")}</p>
          <a href="{pfx}/booking/" class="btn btn-fire btn-lg">{BOOK[lang]}</a>
        </div>
        <div class="split-img"><img src="{IMGS['house2']}" alt="Ngor Surf House room" loading="lazy" width="600" height="460"></div>
      </div>
    </div>
  </section>
  <section class="section sec-light">
    <div class="container">
      <h2 class="s-title reveal" style="text-align:center;margin-bottom:52px">{AMN[lang]}</h2>
      <div class="grid-3 reveal">{feats_html}</div>
    </div>
  </section>
  <section class="section">
    <div class="container">
      <h2 class="s-title reveal" style="text-align:center;margin-bottom:40px">{LIFE[lang]}</h2>
      <div class="gallery-masonry reveal">{gal_html}</div>
    </div>
    <div id="lb"><button id="lb-close" aria-label="Close">✕</button><img id="lb-img" src="" alt="Gallery"></div>
  </section>
  <div class="cta-band">
    <div class="container">
      <h2>{CTA_H[lang]}</h2><p>{CTA_P[lang]}</p>
      <div class="cta-btns">
        <a href="{pfx}/booking/" class="btn btn-fire btn-lg">{BOOK[lang]}</a>
        <a href="https://wa.me/221789257025" target="_blank" rel="noopener" class="btn btn-glass btn-lg">
          <span style="width:18px;height:18px;display:inline-flex">{ICO['wa']}</span> WhatsApp</a>
      </div>
    </div>
  </div>
</main>"""
    html += footer_html(lang, pfx)
    html += close_page()
    return html

# ════════════════════════════════════════════════════════════════════════════════
# ISLAND PAGE
# ════════════════════════════════════════════════════════════════════════════════
def build_island(lang):
    pfx = LANG_PREFIX[lang]
    p   = load(f"{PAGES_D}/{lang}_island.json") or {}
    h1  = fix_em(p.get("h1","Discover Ngor Island"))
    sub = fix_em(p.get("hero_subtitle","A hidden gem off the coast of Dakar"))
    title= fix_em(p.get("title_tag","Ngor Island Senegal | Surf, Stay & Relax"))
    meta = fix_em(p.get("meta_description","Discover Ngor Island — world-class waves, no cars, authentic West African atmosphere."))
    intro= fix_em(p.get("intro",""))
    INTRO_FB={"en":"Just a few hundred meters from Dakar, Ngor Island is a peaceful escape from the city. A short pirogue ride takes you to this charming island famous for its authentic vibe, no cars, natural beauty and world-class surf.","fr":"A quelques centaines de mètres de Dakar, l'île de Ngor est une escapade paisible loin de la ville. Une courte traversée en pirogue vous emmène sur cette île charmante connue pour son ambiance authentique.","es":"A pocos cientos de metros de Dakar, la isla de Ngor es un escape tranquilo de la ciudad. Un corto trayecto en piragua te lleva a esta encantadora isla famosa por su ambiente auténtico.","it":"A poche centinaia di metri da Dakar, l'isola di Ngor è una tranquilla fuga dalla città. Un breve tragitto in piroga ti porta a questa incantevole isola famosa per la sua atmosfera autentica.","de":"Nur wenige hundert Meter von Dakar entfernt ist Ngor Island eine ruhige Flucht aus der Stadt. Eine kurze Pirogenfahrt bringt Sie zu dieser charmanten Insel."}
    CARDS = [
        (IMGS["ngor_r"],{"en":"Legendary Surf: Ngor Right","fr":"Surf Légendaire : Ngor Right","es":"Surf Legendario: Ngor Right","it":"Surf Leggendario: Ngor Right","de":"Legendäres Surfen: Ngor Right"},{"en":"One of West Africa's most famous waves, made legendary by The Endless Summer (1964). Consistent, powerful point break for intermediate to advanced surfers.","fr":"L'une des vagues les plus célèbres d'Afrique de l'Ouest, rendue légendaire par The Endless Summer. Point break puissant et régulier.","es":"Una de las olas más famosas de África Occidental, hecha legendaria por The Endless Summer. Punto de rompimiento consistente y poderoso.","it":"Una delle onde più famose dell'Africa Occidentale, resa leggendaria da The Endless Summer. Break consistente e potente.","de":"Eine der bekanntesten Wellen Westafrikas, legendär durch The Endless Summer. Konsistenter, kraftvoller Point Break."}),
        (IMGS["art"],{"en":"Bohemian Spirit","fr":"Esprit bohème","es":"Espíritu bohemio","it":"Spirito bohémien","de":"Böhmischer Geist"},{"en":"Street art, colorful houses, art galleries and cozy cafes. Ngor has a unique soul far from mass tourism.","fr":"Street art, maisons colorées, galeries d'art et cafés cosy. Ngor a une âme unique loin du tourisme de masse.","es":"Arte callejero, casas coloridas, galerías de arte y cafés acogedores. Ngor tiene un alma única.","it":"Street art, case colorate, gallerie d'arte e caffè accoglienti. Ngor ha un'anima unica.","de":"Street Art, bunte Häuser, Kunstgalerien und gemütliche Cafés. Ngor hat eine einzigartige Seele."}),
        (IMGS["sunset"],{"en":"Magical Sunsets","fr":"Couchers de soleil magiques","es":"Atardeceres mágicos","it":"Tramonti magici","de":"Magische Sonnenuntergänge"},{"en":"The island's western shore offers breathtaking sunset views over the Atlantic. An unmissable daily ritual.","fr":"Le rivage ouest de l'île offre des couchers de soleil époustouflants sur l'Atlantique. Un rituel quotidien incontournable.","es":"La costa occidental de la isla ofrece impresionantes vistas al atardecer. Un ritual diario imperdible.","it":"La riva occidentale dell'isola offre viste al tramonto mozzafiato sull'Atlantico. Un rito quotidiano imperdibile.","de":"Die Westküste der Insel bietet atemberaubende Sonnenuntergangspanoramen. Ein unverzichtbares tägliches Ritual."}),
    ]
    cards_html = "".join([f'<a href="{pfx}/booking/" class="card" style="text-decoration:none"><img src="{img}" alt="{titles.get(lang,titles["en"])}" class="card-img" loading="lazy"><div class="card-body"><h3 class="card-h3">{titles.get(lang,titles["en"])}</h3><p class="card-text">{descs.get(lang,descs["en"])}</p></div></a>' for img,titles,descs in CARDS])
    STATS_L = {"en":"800m from Dakar","fr":"800m de Dakar","es":"800m de Dakar","it":"800m da Dakar","de":"800m von Dakar"}
    STATS_NC = {"en":"No Cars","fr":"Pas de Voitures","es":"Sin Coches","it":"Niente Auto","de":"Keine Autos"}
    STATS_WT = {"en":"World-Class Waves","fr":"Vagues Mondiale","es":"Olas Mundiales","it":"Onde Mondiali","de":"Weltklasse Wellen"}
    STATS_YR = {"en":"Year-Round Surf","fr":"Surf Toute l'Année","es":"Surf Todo el Año","it":"Surf Tutto l'Anno","de":"Ganzjähriges Surfen"}
    EXP_L = {"en":"Experience Ngor Island","fr":"Vivre l'Île de Ngor","es":"Vive la Isla de Ngor","it":"Vivi l'Isola di Ngor","de":"Erlebe Ngor Island"}
    EXP_P = {"en":"Stay at Ngor Surfcamp Teranga and make the island your home.","fr":"Séjournez au Ngor Surfcamp Teranga et faites de l'île votre maison.","es":"Alójate en Ngor Surfcamp Teranga y convierte la isla en tu hogar.","it":"Soggiorna al Ngor Surfcamp Teranga e fai dell'isola la tua casa.","de":"Übernachten Sie im Ngor Surfcamp Teranga und machen Sie die Insel zu Ihrem Zuhause."}
    BOOK_L = {"en":"Book Your Stay","fr":"Réserver votre séjour","es":"Reservar tu estancia","it":"Prenota il tuo soggiorno","de":"Jetzt buchen"}
    ABOUT_N = {"en":"Ngor Island","fr":"Île de Ngor","es":"Isla de Ngor","it":"Isola di Ngor","de":"Ngor Island"}
    TWO_SIDES = {"en":"Two sides, two moods","fr":"Deux côtés, deux ambiances","es":"Dos lados, dos ambientes","it":"Due lati, due atmosfere","de":"Zwei Seiten, zwei Stimmungen"}
    DISC = {"en":"Discover","fr":"Découvrir","es":"Descubrir","it":"Scoprire","de":"Entdecken"}

    html = head(title, meta, lang, can_tag("island",lang), hrl_tags("island"), IMGS["island"])
    html += nav_html("island", lang, pfx, "/island")
    html += f"""
<main>
  <header class="page-header" style="background-image:url('{IMGS['island']}')" role="banner">
    <h1>{h1}</h1><p>{sub}</p>
  </header>
  <section class="section">
    <div class="container">
      <div class="split reveal">
        <div>
          <span class="s-label">{ABOUT_N[lang]}</span>
          <h2 class="s-title">{TWO_SIDES[lang]}</h2>
          <p class="s-sub" style="margin-bottom:28px">{intro or INTRO_FB.get(lang,"")}</p>
          <a href="{pfx}/booking/" class="btn btn-fire btn-lg">{BOOK_L[lang]}</a>
        </div>
        <div class="split-img"><img src="{IMGS['island2']}" alt="Ngor Island Senegal" loading="lazy" width="600" height="460"></div>
      </div>
    </div>
  </section>
  <div style="background:var(--navy);padding:48px 0">
    <div class="container">
      <div style="display:flex;justify-content:center;flex-wrap:wrap;gap:48px">
        <div style="text-align:center;color:#fff"><div style="font-size:36px;font-weight:900;font-family:var(--fh);color:var(--sand)">800m</div><div style="font-size:12px;text-transform:uppercase;letter-spacing:0.12em;opacity:0.6">{STATS_L[lang]}</div></div>
        <div style="text-align:center;color:#fff"><div style="font-size:36px;font-weight:900;font-family:var(--fh);color:var(--sand)">0</div><div style="font-size:12px;text-transform:uppercase;letter-spacing:0.12em;opacity:0.6">{STATS_NC[lang]}</div></div>
        <div style="text-align:center;color:#fff"><div style="font-size:36px;font-weight:900;font-family:var(--fh);color:var(--sand)">#43</div><div style="font-size:12px;text-transform:uppercase;letter-spacing:0.12em;opacity:0.6">{"Most Beautiful Bay" if lang=="en" else "Plus Belle Baie" if lang=="fr" else "Bahía más Bella" if lang=="es" else "Baia più Bella" if lang=="it" else "Schönste Bucht"}</div></div>
        <div style="text-align:center;color:#fff"><div style="font-size:36px;font-weight:900;font-family:var(--fh);color:var(--sand)">1964</div><div style="font-size:12px;text-transform:uppercase;letter-spacing:0.12em;opacity:0.6">{STATS_YR[lang]}</div></div>
      </div>
    </div>
  </div>
  <section class="section sec-light">
    <div class="container">
      <div style="text-align:center;margin-bottom:52px" class="reveal">
        <span class="s-label">{DISC[lang]}</span>
        <h2 class="s-title">{STATS_WC if (STATS_WC := STATS_WT.get(lang,"")) else ""}</h2>
      </div>
      <div class="grid-3 reveal">{cards_html}</div>
    </div>
  </section>
  <div class="cta-band">
    <div class="container">
      <h2>{EXP_L[lang]}</h2><p>{EXP_P[lang]}</p>
      <div class="cta-btns">
        <a href="{pfx}/booking/" class="btn btn-fire btn-lg">{BOOK_L[lang]}</a>
        <a href="https://wa.me/221789257025" target="_blank" class="btn btn-glass btn-lg"><span style="width:18px;height:18px;display:inline-flex">{ICO['wa']}</span> WhatsApp</a>
      </div>
    </div>
  </div>
</main>"""
    html += footer_html(lang, pfx)
    html += close_page()
    return html

# ════════════════════════════════════════════════════════════════════════════════
# SURFING PAGE
# ════════════════════════════════════════════════════════════════════════════════
def build_surfing(lang):
    pfx = LANG_PREFIX[lang]
    p   = load(f"{PAGES_D}/{lang}_surfing.json") or {}
    h1  = fix_em(p.get("h1","Ride World-Class Waves"))
    sub = fix_em(p.get("hero_subtitle","Professional coaching on Ngor's legendary breaks"))
    title= fix_em(p.get("title_tag","Surfing in Senegal | Coaching at Ngor Surfcamp"))
    meta = fix_em(p.get("meta_description","Professional surf coaching with video analysis. All levels, world-class waves at Ngor Island."))
    intro= fix_em(p.get("intro",""))
    INTRO_FB={"en":"At Ngor Surfcamp Teranga, professional coaching meets world-class waves. Whether you are learning to surf or pushing your performance, our licensed coaches use video analysis and personalized sessions to help you progress faster.","fr":"Au Ngor Surfcamp Teranga, coaching professionnel et vagues de classe mondiale se rencontrent. Que vous appreniez à surfer ou que vous poussiez vos performances, nos coachs agréés utilisent l'analyse vidéo pour vous aider à progresser plus vite.","es":"En Ngor Surfcamp Teranga, coaching profesional y olas de clase mundial se encuentran. Tanto si estás aprendiendo como si estás empujando tu rendimiento, nuestros coaches licenciados usan análisis de vídeo para ayudarte a progresar.","it":"Al Ngor Surfcamp Teranga, coaching professionale e onde di classe mondiale si incontrano. Che tu stia imparando o spingendo le tue prestazioni, i nostri coach autorizzati usano l'analisi video per aiutarti a progredire.","de":"Im Ngor Surfcamp Teranga treffen professionelles Coaching und weltklasse Wellen aufeinander. Ob Sie Surfen lernen oder Ihre Leistung verbessern, unsere lizenzierten Coaches nutzen Videoanalyse."}
    FEATS = [
        ("🎥",{"en":"Video Analysis","fr":"Analyse vidéo","es":"Análisis de vídeo","it":"Analisi video","de":"Videoanalyse"},{"en":"We film your sessions and review the footage with you to pinpoint exactly what to improve.","fr":"Nous filmons vos sessions et analysons les images avec vous pour identifier précisément ce qui doit être amélioré.","es":"Filmamos tus sesiones y revisamos las grabaciones contigo para identificar exactamente qué mejorar.","it":"Filmiamo le tue sessioni e analizziamo le riprese con te per identificare esattamente cosa migliorare.","de":"Wir filmen Ihre Sessions und analysieren die Aufnahmen mit Ihnen, um genau zu bestimmen, was verbessert werden muss."}),
        ("🏄",{"en":"All Levels Welcome","fr":"Tous niveaux bienvenus","es":"Todos los niveles bienvenidos","it":"Tutti i livelli benvenuti","de":"Alle Level willkommen"},{"en":"Beginner to advanced: we tailor every session to your exact level and goals.","fr":"Débutant à avancé : nous adaptons chaque session à votre niveau exact et à vos objectifs.","es":"De principiante a avanzado: adaptamos cada sesión a tu nivel exacto y objetivos.","it":"Da principiante ad avanzato: adattiamo ogni sessione al tuo livello esatto e obiettivi.","de":"Von Anfänger bis Fortgeschrittener: Wir passen jede Session genau an Ihr Level an."}),
        ("📋",{"en":"Licensed Federation","fr":"Fédération agréée","es":"Federación licenciada","it":"Federazione autorizzata","de":"Lizenzierte Federation"},{"en":"Officially licensed by the Senegalese Federation of Surfing. Qualified, safety-first coaches.","fr":"Officiellement agréé par la Fédération Sénégalaise de Surf. Moniteurs qualifiés, sécurité en premier.","es":"Oficialmente licenciado por la Federación Senegalesa de Surf. Instructores cualificados.","it":"Ufficialmente autorizzato dalla Federazione Senegalese di Surf. Coach qualificati.","de":"Offiziell lizenziert vom senegalesischen Surfverband. Qualifizierte, sicherheitsbewusste Coaches."}),
        ("🌊",{"en":"Ngor Right & Left","fr":"Ngor Right & Left","es":"Ngor Right & Left","it":"Ngor Right & Left","de":"Ngor Right & Left"},{"en":"Two world-class breaks: Ngor Right for intermediate/advanced, Ngor Left a great all-level option.","fr":"Deux breaks de classe mondiale : Ngor Right (intermédiaire/avancé), Ngor Left (tous niveaux).","es":"Dos breaks de clase mundial: Ngor Right (intermedio/avanzado), Ngor Left (todos los niveles).","it":"Due break di classe mondiale: Ngor Right (intermedio/avanzato), Ngor Left (tutti i livelli).","de":"Zwei Weltklasse-Breaks: Ngor Right (Fortgeschrittene), Ngor Left (alle Level)."}),
    ]
    feats_html = "".join([f'<div class="feat reveal"><div class="feat-icon" style="font-size:20px">{ic}</div><div><div class="feat-title">{t.get(lang,t["en"])}</div><div class="feat-text">{d.get(lang,d["en"])}</div></div></div>' for ic,t,d in FEATS])
    gal_imgs = [IMGS["surf"],IMGS["surf2"],IMGS["surf3"],IMGS["surf4"],IMGS["surf5"],IMGS["surf6"]]
    gal_html = "".join([f'<div class="gallery-item"><img src="{u}" alt="Surfing Ngor Island" loading="lazy"></div>' for u in gal_imgs])
    BOOK = {"en":"Book Coaching","fr":"Réserver le coaching","es":"Reservar coaching","it":"Prenota coaching","de":"Coaching buchen"}
    PERF = {"en":"Waves, Coaching, Real Results.","fr":"Vagues, Coaching, Vrais Résultats.","es":"Olas, Coaching, Resultados Reales.","it":"Onde, Coaching, Risultati Reali.","de":"Wellen, Coaching, Echte Ergebnisse."}
    IN_ACT = {"en":"Our surf trips in action","fr":"Nos sessions en action","es":"Nuestras sesiones en acción","it":"Le nostre sessioni in azione","de":"Unsere Surf-Sessions"}
    START = {"en":"Start Your Surf Journey","fr":"Commencez votre aventure surf","es":"Comienza tu aventura surf","it":"Inizia il tuo viaggio surf","de":"Beginne deine Surfreise"}
    START_P = {"en":"Book a coaching package and progress faster.","fr":"Réservez un package coaching et progressez plus vite.","es":"Reserva un paquete coaching y progresa más rápido.","it":"Prenota un pacchetto coaching e progredisci più velocemente.","de":"Buche ein Coaching-Paket und mache schnellere Fortschritte."}
    COACH_L = {"en":"Surf Coaching","fr":"Coaching Surf","es":"Coaching Surf","it":"Coaching Surf","de":"Surf-Coaching"}

    html = head(title, meta, lang, can_tag("surfing",lang), hrl_tags("surfing"), IMGS["surf"])
    html += nav_html("surfing", lang, pfx, "/surfing")
    html += f"""
<main>
  <header class="page-header" style="background-image:url('{IMGS['surf']}')" role="banner">
    <h1>{h1}</h1><p>{sub}</p>
  </header>
  <section class="section">
    <div class="container">
      <div style="text-align:center;margin-bottom:56px" class="reveal">
        <span class="s-label">{COACH_L[lang]}</span>
        <h2 class="s-title">{PERF[lang]}</h2>
        <p class="s-sub">{intro or INTRO_FB.get(lang,"")}</p>
      </div>
      <div class="grid-2 reveal">{feats_html}</div>
    </div>
  </section>
  <section class="section sec-light">
    <div class="container">
      <h2 class="s-title reveal" style="text-align:center;margin-bottom:40px">{IN_ACT[lang]}</h2>
      <div class="gallery-masonry reveal">{gal_html}</div>
    </div>
    <div id="lb"><button id="lb-close" aria-label="Close">✕</button><img id="lb-img" src="" alt="Surfing"></div>
  </section>
  <div class="cta-band">
    <div class="container">
      <h2>{START[lang]}</h2><p>{START_P[lang]}</p>
      <div class="cta-btns">
        <a href="{pfx}/booking/" class="btn btn-fire btn-lg">{BOOK[lang]}</a>
        <a href="https://wa.me/221789257025" target="_blank" class="btn btn-glass btn-lg"><span style="width:18px;height:18px;display:inline-flex">{ICO['wa']}</span> WhatsApp</a>
      </div>
    </div>
  </div>
</main>"""
    html += footer_html(lang, pfx)
    html += close_page()
    return html

# ════════════════════════════════════════════════════════════════════════════════
# GALLERY PAGE
# ════════════════════════════════════════════════════════════════════════════════
def build_gallery(lang):
    pfx = LANG_PREFIX[lang]
    p   = load(f"{PAGES_D}/{lang}_gallery.json") or {}
    h1  = fix_em(p.get("h1","Gallery"))
    sub = fix_em(p.get("hero_subtitle","Waves, coaching, island life in pictures"))
    title= fix_em(p.get("title_tag","Gallery | Ngor Surfcamp Teranga"))
    meta = fix_em(p.get("meta_description","Browse photos from Ngor Surfcamp Teranga: waves, surf coaching and island life."))
    gal_html = "".join([f'<div class="gallery-item"><img src="{u}" alt="Ngor Surfcamp Teranga" loading="lazy"></div>' for u in IMGS["gallery"]])
    BOOK = {"en":"Book Your Surf Stay","fr":"Réserver votre séjour","es":"Reservar tu estancia","it":"Prenota il tuo soggiorno","de":"Jetzt buchen"}
    CTA_H = {"en":"Your next chapter starts here.","fr":"Votre prochain chapitre commence ici.","es":"Tu próximo capítulo empieza aquí.","it":"Il tuo prossimo capitolo inizia qui.","de":"Ihr nächstes Kapitel beginnt hier."}

    html = head(title, meta, lang, can_tag("gallery",lang), hrl_tags("gallery"), IMGS["gallery"][0])
    html += nav_html("gallery", lang, pfx, "/gallery")
    html += f"""
<main>
  <header class="page-header" style="background-image:url('{IMGS['gallery'][0]}')" role="banner">
    <h1>{h1}</h1><p>{sub}</p>
  </header>
  <section class="section">
    <div class="container">
      <div class="gallery-masonry">{gal_html}</div>
    </div>
  </section>
  <div id="lb"><button id="lb-close" aria-label="Close">✕</button><img id="lb-img" src="" alt="Gallery"></div>
  <div class="cta-band">
    <div class="container">
      <h2>{CTA_H[lang]}</h2>
      <div class="cta-btns"><a href="{pfx}/booking/" class="btn btn-fire btn-lg">{BOOK[lang]}</a></div>
    </div>
  </div>
</main>"""
    html += footer_html(lang, pfx)
    html += close_page()
    return html

# ════════════════════════════════════════════════════════════════════════════════
# FAQ PAGE
# ════════════════════════════════════════════════════════════════════════════════
def build_faq(lang):
    pfx = LANG_PREFIX[lang]
    p   = load(f"{PAGES_D}/{lang}_faq.json") or {}
    h1  = fix_em(p.get("h1","Frequently Asked Questions"))
    sub = fix_em(p.get("hero_subtitle","Everything you need to know before your surf trip"))
    title= fix_em(p.get("title_tag","FAQ | Ngor Surfcamp Teranga"))
    meta = fix_em(p.get("meta_description","Frequently asked questions about Ngor Surfcamp Teranga, Ngor Island, Dakar, Senegal."))

    FAQS = [
        ({"en":"What surf level do I need?","fr":"Quel niveau de surf faut-il ?","es":"¿Qué nivel de surf necesito?","it":"Quale livello di surf è necessario?","de":"Welches Surflevel brauche ich?"},
         {"en":"We welcome all levels from complete beginners to experienced surfers. Our coaches adapt sessions to your exact level and goals.","fr":"Nous accueillons tous les niveaux, des débutants complets aux surfeurs expérimentés. Nos coachs adaptent les sessions à votre niveau exact.","es":"Damos la bienvenida a todos los niveles. Nuestros coaches adaptan las sesiones a tu nivel exacto.","it":"Accogliamo tutti i livelli. I nostri coach adattano le sessioni al tuo livello esatto.","de":"Wir begrüßen alle Level. Unsere Coaches passen die Sessions genau an Ihr Level an."}),
        ({"en":"What's the best time to visit?","fr":"Quelle est la meilleure période ?","es":"¿Cuál es la mejor época?","it":"Qual è il periodo migliore?","de":"Wann ist die beste Reisezeit?"},
         {"en":"The surf season runs year-round in Senegal. The most consistent swells hit from October to April. Water temperature stays at 22-27°C.","fr":"La saison surf se déroule toute l'année au Sénégal. Les houles les plus régulières arrivent d'octobre à avril. Eau à 22-27°C.","es":"La temporada surf es todo el año. Los swells más consistentes llegan de octubre a abril. Agua a 22-27°C.","it":"La stagione surf è tutto l'anno. Le onde più consistenti arrivano da ottobre ad aprile. Acqua a 22-27°C.","de":"Die Surfsaison ist ganzjährig. Die konstantesten Swells kommen von Oktober bis April. Wassertemperatur 22-27°C."}),
        ({"en":"How do I get to Ngor Island?","fr":"Comment rejoindre l'Île de Ngor ?","es":"¿Cómo llego a la Isla de Ngor?","it":"Come raggiungo Ngor Island?","de":"Wie komme ich nach Ngor Island?"},
         {"en":"Take a taxi or Uber to Ngor beach (about 20min from the airport). Then a short pirogue ride takes you to the island for less than 1 euro.","fr":"Prenez un taxi ou Uber jusqu'à la plage de Ngor (environ 20min de l'aéroport). Une courte traversée en pirogue vous emmène sur l'île pour moins de 1€.","es":"Toma un taxi o Uber hasta la playa de Ngor (unos 20min del aeropuerto). Luego una corta travesía en piragua por menos de 1€.","it":"Prendi un taxi o Uber fino alla spiaggia di Ngor (circa 20min dall'aeroporto). Poi una breve traversata in piroga per meno di 1€.","de":"Nehmen Sie ein Taxi oder Uber zum Ngor-Strand (ca. 20min vom Flughafen). Dann eine kurze Pirogenfahrt für weniger als 1€."}),
        ({"en":"Is video analysis included in coaching?","fr":"L'analyse vidéo est-elle incluse ?","es":"¿Está incluido el análisis de vídeo?","it":"L'analisi video è inclusa?","de":"Ist die Videoanalyse inbegriffen?"},
         {"en":"Yes! Video analysis is a core part of our coaching. We film your sessions and review footage together to fast-track your progression.","fr":"Oui ! L'analyse vidéo est au coeur de notre coaching. Nous filmons vos sessions et analysons les images ensemble pour accélérer votre progression.","es":"Sí! El análisis de vídeo es parte fundamental de nuestro coaching. Filmamos tus sesiones y analizamos juntos para acelerar tu progresión.","it":"Sì! L'analisi video è fondamentale nel nostro coaching. Filmiamo le tue sessioni e analizziamo insieme.","de":"Ja! Die Videoanalyse ist ein Kernbestandteil unseres Coachings. Wir filmen Ihre Sessions und analysieren gemeinsam."}),
        ({"en":"What's included in the price?","fr":"Qu'est-ce qui est inclus ?","es":"¿Qué está incluido en el precio?","it":"Cosa è incluso nel prezzo?","de":"Was ist im Preis inbegriffen?"},
         {"en":"Accommodation, breakfast & dinner, daily surf guiding, theory classes, boat transfers, pool access, Wi-Fi and daily room cleaning.","fr":"Hébergement, petit-déjeuner & dîner, guide surf quotidien, cours de théorie, transferts bateau, piscine, Wi-Fi et ménage quotidien.","es":"Alojamiento, desayuno y cena, guía surf diario, clases de teoría, traslados en barco, piscina, Wi-Fi y limpieza diaria.","it":"Alloggio, colazione e cena, guida surf giornaliera, lezioni di teoria, trasferimenti in barca, piscina, Wi-Fi e pulizia giornaliera.","de":"Unterkunft, Frühstück & Abendessen, tägliche Surf-Führung, Theoriestunden, Bootüberfahrten, Pool, WLAN und tägliche Reinigung."}),
        ({"en":"Can I book accommodation without coaching?","fr":"Puis-je réserver sans coaching ?","es":"¿Puedo reservar sin coaching?","it":"Posso prenotare senza coaching?","de":"Kann ich ohne Coaching buchen?"},
         {"en":"Yes! We offer accommodation-only options as well as full coaching packages. Contact us on WhatsApp to find the best option for you.","fr":"Oui ! Nous proposons des options hébergement seul ainsi que des packages coaching complets. Contactez-nous sur WhatsApp.","es":"Sí! Ofrecemos opciones de solo alojamiento así como paquetes de coaching completos. Contáctanos por WhatsApp.","it":"Sì! Offriamo opzioni di solo alloggio e pacchetti coaching completi. Contattaci su WhatsApp.","de":"Ja! Wir bieten Unterkunft-nur-Optionen sowie vollständige Coaching-Pakete. Kontaktieren Sie uns per WhatsApp."}),
    ]
    faq_html = "".join([f'<div class="faq-item closed"><button class="faq-q" type="button">{q.get(lang,q["en"])} <span class="faq-arrow">▼</span></button><div class="faq-a">{a.get(lang,a["en"])}</div></div>' for q,a in FAQS])
    STILL_Q = {"en":"Still have questions?","fr":"Encore des questions ?","es":"¿Todavía tienes preguntas?","it":"Hai ancora domande?","de":"Noch Fragen?"}
    CHAT = {"en":"Chat on WhatsApp","fr":"Discuter sur WhatsApp","es":"Chatear en WhatsApp","it":"Chatta su WhatsApp","de":"WhatsApp-Chat"}

    html = head(title, meta, lang, can_tag("faq",lang), hrl_tags("faq"), IMGS["surf3"])
    html += nav_html("faq", lang, pfx, "/faq")
    html += f"""
<main>
  <header class="page-header" style="background-image:url('{IMGS['surf3']}')" role="banner">
    <h1>{h1}</h1><p>{sub}</p>
  </header>
  <section class="section">
    <div class="container-sm">
      <div id="faq-list" itemscope itemtype="https://schema.org/FAQPage">{faq_html}</div>
      <div style="text-align:center;margin-top:48px">
        <p style="font-size:16px;color:#6b7280;margin-bottom:20px">{STILL_Q[lang]}</p>
        <a href="https://wa.me/221789257025" target="_blank" class="btn btn-wa btn-lg">
          <span style="width:18px;height:18px;display:inline-flex">{ICO['wa']}</span> {CHAT[lang]}
        </a>
      </div>
    </div>
  </section>
</main>"""
    html += footer_html(lang, pfx)
    html += close_page()
    return html

# ════════════════════════════════════════════════════════════════════════════════
# WRITE ALL FILES
# ════════════════════════════════════════════════════════════════════════════════
total = 0
def write(path, html):
    global total
    full = DEMO_DIR + path
    if full.endswith("/"): full += "index.html"
    elif not full.endswith(".html"):
        os.makedirs(full, exist_ok=True); full += "/index.html"
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f: f.write(html)
    total += 1

builders = [
    ("booking",   build_booking),
    ("surf-house", build_surf_house),
    ("island",    build_island),
    ("surfing",   build_surfing),
    ("gallery",   build_gallery),
    ("faq",       build_faq),
]

for lang in LANGS:
    pfx  = LANG_PREFIX[lang]
    spfx = f"/{lang}" if lang!="en" else ""
    for page_slug, builder in builders:
        write(f"{spfx}/{page_slug}/", builder(lang))
    print(f"  ✅ {lang}: all 6 static pages")

print(f"\nTotal pages written: {total}")
print("✅ All static pages built!")
