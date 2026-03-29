"""
Comprehensive v4 patch:
- Creative DA: animated waves, hero parallax text reveal, floating elements
- Smart lang selector: custom dropdown, URL redirect, hide current lang
- Footer logo fix
- Stats counter animation
- Sticky floating WhatsApp CTA
- Scroll progress bar
- Wave SVG section dividers
- Breadcrumbs on articles
- SEO/marketing expert improvements
- Full responsive audit & fixes
"""
import json, os, re, shutil

CONTENT  = "/Users/simonazoulay/SurfCampSenegal/content"
ARTICLES = f"{CONTENT}/articles"
PAGES_D  = f"{CONTENT}/pages"
AUTHORS_F= f"{CONTENT}/authors/authors.json"
DEMO_DIR = "/Users/simonazoulay/SurfCampSenegal/cloudflare-demo"
SITE_URL = "https://ngor-surfcamp-demo.pages.dev"

WIX = "https://static.wixstatic.com/media"
VIDEO_BASE   = "https://video.wixstatic.com/video/df99f9_da0cf7c72b1a4606bcfa1f7c8e089dc4"
VIDEO_POSTER = f"{WIX}/df99f9_da0cf7c72b1a4606bcfa1f7c8e089dc4f000.jpg"
LOGO  = f"{WIX}/c2467f_a31779010ce34c4c8c61cc5868d81f31~mv2.png"

LANGS       = ["en","fr","es","it","de"]
LANG_NAMES  = {"en":"English","fr":"Français","es":"Español","it":"Italiano","de":"Deutsch"}
LANG_LOCALE = {"en":"en","fr":"fr-FR","es":"es-ES","it":"it-IT","de":"de-DE"}
LANG_PREFIX = {"en":"","fr":"/fr","es":"/es","it":"/it","de":"/de"}

IMGS = {
    "home":   VIDEO_POSTER,
    "surf2":  f"{WIX}/df99f9_dd89cc4d86d4402189d7e9516ce672a3~mv2.jpg",
    "surf3":  f"{WIX}/df99f9_961b0768e713457f93025f4ce6fb1419~mv2.jpg",
    "surf":   f"{WIX}/11062b_89a070321f814742a620b190592d51ad~mv2.jpg",
    "house2": f"{WIX}/df99f9_eba4c24ec6a746b58d60a975b8d20946~mv2.jpg",
    "island2":f"{WIX}/b28af82dbec544138f16e2bc5a85f2cb.jpg",
    "ngor_r": f"{WIX}/11062b_7f89d2db0ace4027ac4a00928a6aca08~mv2.jpg",
    "review": f"{WIX}/11062b_772a661c20f742c7baca38ad28c5f7fc~mv2.jpeg",
    "food":   f"{WIX}/df99f9_753890483d8e4cca8e2051a13f9c558e~mv2.jpg",
    "pool":   f"{WIX}/df99f9_a18d512828d9487e9a4987b9903960e0~mv2.jpg",
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
        f"{WIX}/df99f9_81e322c4e48d4bcbb444c6535daed131~mv2.jpg",
    ],
}

def load(p):
    if os.path.exists(p):
        try:
            with open(p) as f: return json.load(f)
        except: return None
    return None

def fix_em(text):
    if not text: return text or ""
    return re.sub(r',\s*,',',', str(text).replace(" — ",", ").replace("—",",").replace("\u2014",",").replace(" – ",", ").replace("–",","))

strategy = load(f"{CONTENT}/blog_strategy.json")
cats     = strategy["categories"]
authors  = load(AUTHORS_F) or {}
CAT_AUTHOR = {}
for aid, a in authors.items():
    for cat in a.get("categories",[]):
        CAT_AUTHOR[cat] = aid

arts_en = []
for fname in sorted(os.listdir(f"{ARTICLES}/en")):
    if fname.endswith(".json"):
        a = load(f"{ARTICLES}/en/{fname}")
        if a and a.get("slug"): arts_en.append(a)

arts_by_lang = {}
for lang in LANGS:
    arts_by_lang[lang] = {}
    d = f"{ARTICLES}/{lang}"
    if os.path.exists(d):
        for fname in os.listdir(d):
            if fname.endswith(".json") and not fname.startswith("_"):
                a = load(f"{d}/{fname}")
                if a:
                    key = a.get("original_en_slug", a.get("slug",""))
                    arts_by_lang[lang][key] = a
    if lang == "en":
        for a in arts_en: arts_by_lang["en"][a["slug"]] = a

# ════════════════════════════════════════════════════════════════════════════════
# SVG FLAGS (clean geometric)
# ════════════════════════════════════════════════════════════════════════════════
FLAG_SVG = {
    "en": '<svg viewBox="0 0 60 40" xmlns="http://www.w3.org/2000/svg"><rect width="60" height="40" fill="#012169"/><path d="M0,0 L60,40 M60,0 L0,40" stroke="#fff" stroke-width="8"/><path d="M0,0 L60,40 M60,0 L0,40" stroke="#C8102E" stroke-width="5"/><path d="M30,0 V40 M0,20 H60" stroke="#fff" stroke-width="12"/><path d="M30,0 V40 M0,20 H60" stroke="#C8102E" stroke-width="8"/></svg>',
    "fr": '<svg viewBox="0 0 60 40" xmlns="http://www.w3.org/2000/svg"><rect width="20" height="40" fill="#002395"/><rect x="20" width="20" height="40" fill="#fff"/><rect x="40" width="20" height="40" fill="#ED2939"/></svg>',
    "es": '<svg viewBox="0 0 60 40" xmlns="http://www.w3.org/2000/svg"><rect width="60" height="40" fill="#c60b1e"/><rect y="10" width="60" height="20" fill="#ffc400"/></svg>',
    "it": '<svg viewBox="0 0 60 40" xmlns="http://www.w3.org/2000/svg"><rect width="20" height="40" fill="#009246"/><rect x="20" width="20" height="40" fill="#fff"/><rect x="40" width="20" height="40" fill="#CE2B37"/></svg>',
    "de": '<svg viewBox="0 0 60 40" xmlns="http://www.w3.org/2000/svg"><rect width="60" height="13" fill="#000"/><rect y="13" width="60" height="14" fill="#DD0000"/><rect y="27" width="60" height="13" fill="#FFCE00"/></svg>',
}

def flag(lang, size=22):
    svg = FLAG_SVG.get(lang,"")
    h = round(size * 0.667)
    return f'<span class="flag" style="width:{size}px;height:{h}px;display:inline-flex;border-radius:3px;overflow:hidden;flex-shrink:0;box-shadow:0 1px 3px rgba(0,0,0,0.25)">{svg}</span>'

# ════════════════════════════════════════════════════════════════════════════════
# ICONS
# ════════════════════════════════════════════════════════════════════════════════
ICO = {
    "wa"    : '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>',
    "ig"    : '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>',
    "tt"    : '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M19.59 6.69a4.83 4.83 0 01-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 01-2.88 2.5 2.89 2.89 0 01-2.89-2.89 2.89 2.89 0 012.89-2.89c.28 0 .54.04.79.1V9.01a6.28 6.28 0 00-.79-.05 6.34 6.34 0 00-6.34 6.34 6.34 6.34 0 006.34 6.34 6.34 6.34 0 006.33-6.34V8.69a8.22 8.22 0 004.84 1.56V6.79a4.85 4.85 0 01-1.07-.1z"/></svg>',
    "menu"  : '<svg viewBox="0 0 24 24" fill="none"><path d="M3 7h18M3 12h18M3 17h12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
    "close" : '<svg viewBox="0 0 24 24" fill="none"><path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
    "arrow" : '<svg viewBox="0 0 24 24" fill="none"><path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "chev"  : '<svg viewBox="0 0 16 16" fill="none"><path d="M4 6l4 4 4-4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "star"  : '<svg viewBox="0 0 20 20" fill="currentColor"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/></svg>',
    "wave"  : '<svg viewBox="0 0 80 24" fill="none"><path d="M0 16C10 8,20 4,30 10C40 16,50 20,60 12C70 4,76 10,80 8" stroke="currentColor" stroke-width="3" stroke-linecap="round" fill="none"/></svg>',
    "shield": '<svg viewBox="0 0 24 24" fill="none"><path d="M12 2l7 4v6c0 4-3 7.5-7 9-4-1.5-7-5-7-9V6l7-4z" stroke="currentColor" stroke-width="2" stroke-linejoin="round" fill="none"/><path d="M9 12l2 2 4-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "surf"  : '<svg viewBox="0 0 24 48" fill="currentColor"><ellipse cx="12" cy="20" rx="5.5" ry="17" fill="currentColor" opacity="0.9"/><rect x="10.5" y="35" width="3" height="6" rx="1.5" fill="currentColor" opacity="0.6"/></svg>',
    "check" : '<svg viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>',
    "tip"   : '<svg viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/><path d="M12 7v5M12 16v.5" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/></svg>',
    "quote" : '<svg viewBox="0 0 32 24" fill="currentColor"><path d="M0 16.5C0 10.5 3.8 5.2 8 2l1.5 2.4C6.3 6.6 4 10 4 13H8v8H0v-4.5zm16 0C16 10.5 19.8 5.2 24 2l1.5 2.4C22.3 6.6 20 10 20 13h4v8h-8v-4.5z" opacity="0.25"/></svg>',
    "loc"   : '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/><circle cx="12" cy="9" r="2.5" fill="white"/></svg>',
}

def ico(name, size=20):
    svg = ICO.get(name,"")
    return f'<span style="width:{size}px;height:{size}px;display:inline-flex;align-items:center;justify-content:center;flex-shrink:0">{svg}</span>'

# ════════════════════════════════════════════════════════════════════════════════
# COMPLETE CSS v4
# ════════════════════════════════════════════════════════════════════════════════
CSS_V4 = """
@import url('https://fonts.googleapis.com/css2?family=Raleway:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,400&family=Inter:wght@300;400;500;600&display=swap');

/* ══════════════════════════════════════════════════════
   TOKENS
══════════════════════════════════════════════════════ */
:root {
  --navy:   #0a2540;
  --navy2:  #0d3060;
  --sand:   #f0d6a4;
  --sand2:  #fdf4e3;
  --fire:   #ff6b35;
  --fired:  #e05a28;
  --ocean:  #0ea5e9;
  --foam:   rgba(255,255,255,0.06);
  --glass:  rgba(255,255,255,0.10);
  --glassd: rgba(255,255,255,0.16);
  --border: rgba(255,255,255,0.12);
  --bs:     0 8px 32px rgba(10,37,64,0.18), inset 0 1px 0 rgba(255,255,255,0.08);
  --ease:   cubic-bezier(0.4,0,0.2,1);
  --t:      0.28s var(--ease);
  --r:      14px;
  --rp:     50px;
  --max:    1240px;
  --fh:     'Raleway', sans-serif;
  --fb:     'Inter', -apple-system, sans-serif;
}

/* ══════════════════════════════════════════════════════
   RESET + BASE
══════════════════════════════════════════════════════ */
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth;-webkit-text-size-adjust:100%}
body{font-family:var(--fb);color:var(--navy);line-height:1.7;background:#fff;overflow-x:hidden}
h1,h2,h3,h4,h5,h6{font-family:var(--fh);font-weight:700;line-height:1.2;letter-spacing:-0.025em}
a{color:inherit;text-decoration:none}
img{max-width:100%;height:auto;display:block}
button{cursor:pointer;border:none;background:none;font-family:inherit}
::selection{background:var(--fire);color:#fff}

/* ══════════════════════════════════════════════════════
   ANIMATIONS
══════════════════════════════════════════════════════ */
@keyframes waveFloat{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}
@keyframes fadeUp{from{opacity:0;transform:translateY(24px)}to{opacity:1;transform:translateY(0)}}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
@keyframes shimmer{0%{background-position:-200% 0}100%{background-position:200% 0}}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:0.85;transform:scale(1.04)}}
@keyframes waveAnim{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}
@keyframes heroText{0%{opacity:0;transform:translateY(30px) skewX(-2deg)}100%{opacity:1;transform:translateY(0) skewX(0)}}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes floatUp{0%,100%{transform:translateY(0) rotate(-2deg)}50%{transform:translateY(-14px) rotate(2deg)}}

/* ══════════════════════════════════════════════════════
   SCROLL PROGRESS
══════════════════════════════════════════════════════ */
#scroll-progress{
  position:fixed;top:0;left:0;width:0;height:3px;
  background:linear-gradient(90deg,var(--fire),var(--sand));
  z-index:1000;transition:width 0.1s linear;
}

/* ══════════════════════════════════════════════════════
   NAVIGATION
══════════════════════════════════════════════════════ */
#nav{
  position:fixed;top:0;left:0;right:0;z-index:200;
  background:rgba(10,37,64,0.80);
  backdrop-filter:blur(32px) saturate(200%);
  -webkit-backdrop-filter:blur(32px) saturate(200%);
  border-bottom:1px solid rgba(255,255,255,0.07);
  transition:background var(--t),box-shadow var(--t);
}
#nav.scrolled{background:rgba(10,37,64,0.96);box-shadow:0 4px 24px rgba(0,0,0,0.2);}
.nav-inner{
  max-width:var(--max);margin:0 auto;padding:0 24px;
  height:68px;display:flex;align-items:center;gap:12px;
}
.nav-logo img{height:42px;width:auto}
.nav-links{
  display:flex;align-items:center;gap:2px;flex:1;justify-content:center;
}
.nav-link{
  color:rgba(255,255,255,0.8);padding:7px 13px;border-radius:10px;
  font-size:13.5px;font-weight:500;transition:var(--t);white-space:nowrap;
}
.nav-link:hover,.nav-link.active{color:#fff;background:rgba(255,255,255,0.10);}
.nav-link.active{font-weight:600;}
.nav-cta{background:var(--fire) !important;color:#fff !important;border-radius:var(--rp) !important;font-weight:700 !important;font-size:13px !important;padding:8px 18px !important;}
.nav-cta:hover{background:var(--fired) !important;transform:translateY(-1px);}
.nav-right{display:flex;align-items:center;gap:8px;}
.nav-wa{
  display:flex;align-items:center;gap:7px;padding:8px 14px;
  border-radius:var(--rp);background:#25D366;color:#fff;
  font-size:13px;font-weight:700;transition:var(--t);
}
.nav-wa:hover{background:#1da851;transform:translateY(-1px);}
.nav-wa-label{display:none;}
@media(min-width:1100px){.nav-wa-label{display:inline;}}
.nav-toggle{
  width:38px;height:38px;border-radius:10px;
  background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.15);
  display:none;align-items:center;justify-content:center;color:#fff;
}

/* Smart language dropdown */
.lang-dd{position:relative;}
.lang-dd-btn{
  display:flex;align-items:center;gap:7px;padding:7px 11px;
  border-radius:10px;background:rgba(255,255,255,0.10);
  border:1px solid rgba(255,255,255,0.14);color:#fff;
  font-size:13px;font-weight:500;transition:var(--t);cursor:pointer;
  white-space:nowrap;
}
.lang-dd-btn:hover{background:rgba(255,255,255,0.16);}
.lang-dd-btn .chev{width:14px;height:14px;transition:transform var(--t);}
.lang-dd.open .chev{transform:rotate(180deg);}
.lang-dd-menu{
  position:absolute;top:calc(100% + 8px);right:0;
  background:rgba(10,37,64,0.97);
  backdrop-filter:blur(20px);
  -webkit-backdrop-filter:blur(20px);
  border:1px solid rgba(255,255,255,0.12);
  border-radius:12px;padding:6px;min-width:160px;
  opacity:0;pointer-events:none;transform:translateY(8px);
  transition:opacity 0.2s var(--ease),transform 0.2s var(--ease);
  box-shadow:0 16px 40px rgba(0,0,0,0.3);
  z-index:300;
}
.lang-dd.open .lang-dd-menu{opacity:1;pointer-events:auto;transform:translateY(0);}
.lang-dd-item{
  display:flex;align-items:center;gap:9px;padding:10px 12px;
  border-radius:8px;color:rgba(255,255,255,0.82);font-size:13.5px;
  font-weight:500;transition:background var(--t);cursor:pointer;
}
.lang-dd-item:hover{background:rgba(255,255,255,0.10);color:#fff;}
.flag{display:inline-flex;border-radius:3px;overflow:hidden;flex-shrink:0;box-shadow:0 1px 3px rgba(0,0,0,0.22);}

/* ══════════════════════════════════════════════════════
   HERO (video + animated text)
══════════════════════════════════════════════════════ */
.hero{
  position:relative;min-height:100vh;
  display:flex;align-items:center;justify-content:center;
  overflow:hidden;
}
.hero-video-wrap{
  position:absolute;inset:0;z-index:0;
}
.hero-video-wrap video{
  width:100%;height:100%;object-fit:cover;
  transition:opacity 1s;
}
.hero-video-wrap::after{
  content:'';position:absolute;inset:0;
  background:linear-gradient(160deg,rgba(10,37,64,0.72) 0%,rgba(10,37,64,0.40) 40%,rgba(0,0,0,0.60) 100%);
}
/* Animated wave pattern overlay */
.hero-waves{
  position:absolute;bottom:0;left:0;right:0;z-index:2;
  height:120px;overflow:hidden;
}
.hero-waves svg{
  width:200%;height:100%;
  animation:waveAnim 14s linear infinite;
}
.hero-content{
  position:relative;z-index:3;
  text-align:center;max-width:860px;
  padding:0 24px;
}
.hero-eyebrow{
  display:inline-flex;align-items:center;gap:9px;
  padding:7px 18px;border-radius:var(--rp);
  background:rgba(255,107,53,0.18);
  border:1px solid rgba(255,107,53,0.32);
  color:var(--sand);font-size:12px;font-weight:700;
  letter-spacing:0.14em;text-transform:uppercase;
  margin-bottom:22px;
  backdrop-filter:blur(8px);
  animation:fadeUp 0.6s var(--ease) 0.1s both;
}
.hero-h1{
  font-size:clamp(40px,7vw,84px);
  color:#fff;font-weight:900;letter-spacing:-0.04em;
  margin-bottom:18px;
  text-shadow:0 2px 40px rgba(0,0,0,0.22);
  animation:heroText 0.9s var(--ease) 0.3s both;
  line-height:1.05;
}
.hero-h1 em{
  font-style:normal;
  background:linear-gradient(90deg,var(--sand),var(--fire));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  background-clip:text;
}
.hero-sub{
  font-size:clamp(16px,2.3vw,21px);
  color:rgba(255,255,255,0.85);font-weight:300;
  line-height:1.65;margin-bottom:36px;
  animation:fadeUp 0.8s var(--ease) 0.55s both;
}
.hero-cta{
  display:flex;gap:14px;justify-content:center;flex-wrap:wrap;
  animation:fadeUp 0.8s var(--ease) 0.75s both;
}
/* Hero trust badges */
.hero-trust{
  display:flex;gap:20px;justify-content:center;flex-wrap:wrap;
  margin-top:44px;
  animation:fadeUp 0.8s var(--ease) 0.95s both;
}
.trust-badge{
  display:flex;align-items:center;gap:8px;
  padding:8px 16px;border-radius:var(--rp);
  background:rgba(255,255,255,0.10);
  border:1px solid rgba(255,255,255,0.14);
  backdrop-filter:blur(10px);
  color:rgba(255,255,255,0.88);font-size:12.5px;font-weight:500;
}
.trust-badge svg,.trust-badge span{flex-shrink:0;}
/* Bottom wave */
.hero-bottom-wave{
  position:absolute;bottom:-2px;left:0;right:0;z-index:4;line-height:0;
}
.hero-bottom-wave svg{width:100%;height:72px;}

/* ══════════════════════════════════════════════════════
   BUTTONS
══════════════════════════════════════════════════════ */
.btn{
  display:inline-flex;align-items:center;gap:8px;
  padding:13px 28px;border-radius:var(--rp);
  font-family:var(--fh);font-weight:700;font-size:14px;
  letter-spacing:0.04em;text-transform:uppercase;
  transition:var(--t);position:relative;overflow:hidden;border:none;
}
.btn::after{
  content:'';position:absolute;inset:0;
  background:radial-gradient(circle at 50% -10%,rgba(255,255,255,0.25) 0%,transparent 55%);
  opacity:0;transition:opacity var(--t);
}
.btn:hover::after{opacity:1;}
.btn-fire{background:var(--fire);color:#fff;}
.btn-fire:hover{background:var(--fired);transform:translateY(-2px);box-shadow:0 10px 28px rgba(255,107,53,0.42);}
.btn-deep{background:var(--navy);color:#fff;}
.btn-deep:hover{background:var(--navy2);transform:translateY(-2px);box-shadow:0 10px 24px rgba(10,37,64,0.28);}
.btn-glass{background:rgba(255,255,255,0.12);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);color:#fff;border:1px solid rgba(255,255,255,0.2);}
.btn-glass:hover{background:rgba(255,255,255,0.20);transform:translateY(-2px);}
.btn-sand{background:var(--sand);color:var(--navy);}
.btn-sand:hover{background:#e8c880;transform:translateY(-2px);}
.btn-outline{background:transparent;color:var(--fire);border:2px solid var(--fire);}
.btn-outline:hover{background:var(--fire);color:#fff;}
.btn-wa{background:#25D366;color:#fff;}
.btn-wa:hover{background:#1da851;transform:translateY(-2px);box-shadow:0 10px 24px rgba(37,211,102,0.35);}
.btn-sm{padding:9px 18px;font-size:12px;}
.btn-lg{padding:16px 36px;font-size:15px;}

/* ══════════════════════════════════════════════════════
   LAYOUT
══════════════════════════════════════════════════════ */
.container{max-width:var(--max);margin:0 auto;padding:0 24px;}
.container-sm{max-width:800px;margin:0 auto;padding:0 24px;}
.section{padding:100px 0;}
.section-sm{padding:64px 0;}
.sec-dark{background:var(--navy);color:#fff;}
.sec-light{background:#f8fafc;}
.sec-sand{background:linear-gradient(135deg,#fdf4e3,#fef9f0);}

/* Section labels */
.s-label{
  display:inline-flex;align-items:center;gap:9px;
  font-size:11px;font-weight:800;letter-spacing:0.18em;
  text-transform:uppercase;color:var(--fire);margin-bottom:14px;
}
.s-label::before{content:'';width:20px;height:2px;background:var(--fire);border-radius:2px;display:inline-block;}
.s-title{font-size:clamp(26px,4vw,48px);margin-bottom:16px;line-height:1.15;}
.s-sub{font-size:17px;color:#5b6b7c;max-width:580px;line-height:1.75;}
.sec-dark .s-sub{color:rgba(255,255,255,0.70);}
.sec-dark .s-label{color:var(--sand);}
.sec-dark .s-label::before{background:var(--sand);}

/* Wave section dividers */
.wave-top{position:relative;margin-top:-1px;}
.wave-top svg{width:100%;display:block;}
.wave-bottom{position:relative;margin-bottom:-1px;}
.wave-bottom svg{width:100%;display:block;}

/* Decorative surf element */
.surf-deco{
  position:absolute;opacity:0.04;
  animation:floatUp 6s ease-in-out infinite;
  pointer-events:none;
}

/* ══════════════════════════════════════════════════════
   STATS (with counter animation)
══════════════════════════════════════════════════════ */
.stats-bar{padding:60px 0;background:var(--navy);position:relative;overflow:hidden;}
.stats-bar::before{
  content:'';position:absolute;inset:0;
  background:radial-gradient(ellipse at 50% 120%,rgba(255,107,53,0.12) 0%,transparent 60%);
}
.stats-inner{
  max-width:var(--max);margin:0 auto;padding:0 24px;
  display:flex;justify-content:center;flex-wrap:wrap;gap:60px;
  position:relative;z-index:1;
}
.stat{text-align:center;}
.stat-n{
  font-size:clamp(44px,6vw,68px);font-weight:900;
  font-family:var(--fh);
  background:linear-gradient(135deg,var(--sand),#fff8e6);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  background-clip:text;display:block;line-height:1;
}
.stat-l{font-size:12px;letter-spacing:0.12em;text-transform:uppercase;color:rgba(255,255,255,0.55);margin-top:6px;display:block;}

/* ══════════════════════════════════════════════════════
   CARDS
══════════════════════════════════════════════════════ */
.card{
  border-radius:var(--r);overflow:hidden;background:#fff;
  box-shadow:0 2px 20px rgba(10,37,64,0.08);
  transition:transform var(--t),box-shadow var(--t);
}
.card:hover{transform:translateY(-7px);box-shadow:0 20px 50px rgba(10,37,64,0.18);}
.card-img{width:100%;aspect-ratio:16/10;object-fit:cover;transition:transform 0.6s var(--ease);}
.card:hover .card-img{transform:scale(1.04);}
.card-body{padding:24px;}
.card-tag{font-size:11px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:var(--fire);margin-bottom:10px;}
.card-h3{font-size:18px;margin-bottom:10px;line-height:1.35;}
.card-text{font-size:14px;color:#6b7280;line-height:1.65;}

/* Blog cat badge */
.cat-badge{
  display:inline-flex;align-items:center;gap:5px;
  padding:4px 12px;border-radius:var(--rp);
  background:rgba(255,107,53,0.1);color:var(--fired);
  font-size:11px;font-weight:700;letter-spacing:0.04em;
}

/* ══════════════════════════════════════════════════════
   SPLIT LAYOUT
══════════════════════════════════════════════════════ */
.split{display:grid;grid-template-columns:1fr 1fr;gap:72px;align-items:center;}
.split-img{border-radius:var(--r);overflow:hidden;position:relative;}
.split-img img{width:100%;height:460px;object-fit:cover;}
.split-img::before{
  content:'';position:absolute;inset:0;z-index:1;
  background:linear-gradient(135deg,transparent 60%,rgba(255,107,53,0.15));
  pointer-events:none;
}
/* Decorative corner badge */
.split-img::after{
  content:'NGOR';position:absolute;bottom:16px;right:16px;z-index:2;
  padding:6px 14px;border-radius:var(--rp);
  background:rgba(10,37,64,0.85);
  backdrop-filter:blur(10px);
  color:var(--sand);font-size:11px;font-weight:800;letter-spacing:0.14em;
  border:1px solid rgba(240,214,164,0.25);
}

/* Grid */
.grid-2{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:28px;}
.grid-3{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:24px;}
.grid-4{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:20px;}

/* ══════════════════════════════════════════════════════
   FEATURES LIST
══════════════════════════════════════════════════════ */
.feat{
  display:flex;gap:16px;align-items:flex-start;
  padding:20px;border-radius:12px;
  transition:background var(--t);
}
.feat:hover{background:rgba(10,37,64,0.04);}
.feat-icon{
  width:48px;height:48px;border-radius:14px;
  background:linear-gradient(135deg,var(--navy),var(--navy2));
  display:flex;align-items:center;justify-content:center;
  color:var(--sand);flex-shrink:0;
}
.feat-title{font-size:16px;font-weight:700;margin-bottom:5px;}
.feat-text{font-size:13.5px;color:#6b7280;line-height:1.6;}

/* ══════════════════════════════════════════════════════
   TESTIMONIAL
══════════════════════════════════════════════════════ */
.testimonial{
  padding:36px;border-radius:var(--r);background:#fff;
  box-shadow:0 4px 24px rgba(10,37,64,0.08);
  border-left:4px solid var(--fire);
  position:relative;overflow:hidden;
}
.testimonial::before{
  content:'"';
  position:absolute;top:8px;left:24px;
  font-size:100px;line-height:1;font-family:Georgia,serif;
  color:var(--fire);opacity:0.10;
}
.testimonial-text{font-size:18px;font-style:italic;line-height:1.75;margin-bottom:20px;position:relative;}
.testimonial-author{font-weight:700;font-size:15px;}
.testimonial-role{font-size:13px;color:#9ca3af;}
.stars{color:var(--sand);font-size:18px;letter-spacing:2px;}

/* ══════════════════════════════════════════════════════
   GALLERY
══════════════════════════════════════════════════════ */
.gallery-masonry{columns:3 280px;column-gap:14px;}
.gallery-item{break-inside:avoid;margin-bottom:14px;border-radius:10px;overflow:hidden;cursor:pointer;position:relative;}
.gallery-item img{width:100%;display:block;transition:transform 0.5s var(--ease);}
.gallery-item::after{content:'';position:absolute;inset:0;background:linear-gradient(transparent 55%,rgba(10,37,64,0.5));opacity:0;transition:opacity 0.3s;}
.gallery-item:hover img{transform:scale(1.05);}
.gallery-item:hover::after{opacity:1;}
#lb{display:none;position:fixed;inset:0;z-index:1000;background:rgba(0,0,0,0.93);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);align-items:center;justify-content:center;}
#lb.open{display:flex;}
#lb img{max-width:90vw;max-height:88vh;border-radius:var(--r);object-fit:contain;box-shadow:0 32px 80px rgba(0,0,0,0.5);}
#lb-close{position:absolute;top:20px;right:20px;width:44px;height:44px;border-radius:50%;background:rgba(255,255,255,0.12);border:1px solid rgba(255,255,255,0.2);color:#fff;font-size:20px;display:flex;align-items:center;justify-content:center;cursor:pointer;transition:background var(--t);}
#lb-close:hover{background:rgba(255,255,255,0.22);}

/* ══════════════════════════════════════════════════════
   FAQ
══════════════════════════════════════════════════════ */
.faq-item{border:1px solid rgba(10,37,64,0.10);border-radius:12px;overflow:hidden;margin-bottom:10px;transition:box-shadow var(--t);}
.faq-item:hover{box-shadow:0 4px 20px rgba(10,37,64,0.10);}
.faq-q{width:100%;text-align:left;padding:20px 24px;display:flex;align-items:center;justify-content:space-between;gap:16px;font-weight:600;font-size:16px;color:var(--navy);background:#fff;transition:background var(--t);}
.faq-q:hover{background:#fafafa;}
.faq-arrow{color:var(--fire);flex-shrink:0;transition:transform 0.25s var(--ease);}
.faq-a{padding:0 24px 20px;color:#4b5563;line-height:1.75;font-size:15px;display:none;}
.faq-item.open .faq-arrow{transform:rotate(180deg);}
.faq-item.open .faq-a{display:block;}

/* ══════════════════════════════════════════════════════
   BLOG
══════════════════════════════════════════════════════ */
.blog-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:28px;}

/* ══════════════════════════════════════════════════════
   ARTICLE PAGE
══════════════════════════════════════════════════════ */
.article-hero{
  position:relative;min-height:72vh;
  background-size:cover;background-position:center;
  display:flex;align-items:flex-end;overflow:hidden;
}
.article-hero::before{content:'';position:absolute;inset:0;background:linear-gradient(transparent 10%,rgba(10,37,64,0.88) 100%);}
.art-hero-inner{position:relative;z-index:1;padding:48px 24px;width:100%;max-width:900px;margin:0 auto;color:#fff;}
/* Prose */
.prose{max-width:720px;margin:0 auto;}
.prose h1{font-size:clamp(26px,4vw,44px);margin-bottom:28px;color:var(--navy);}
.prose h2{font-size:clamp(20px,3vw,29px);margin:52px 0 18px;color:var(--navy);padding-bottom:10px;border-bottom:2px solid var(--sand);}
.prose h3{font-size:clamp(17px,2.5vw,22px);margin:32px 0 12px;color:var(--navy);}
.prose h4{font-size:16.5px;margin:24px 0 8px;color:var(--navy);font-weight:700;}
.prose p{font-size:17px;line-height:1.84;color:#374151;margin-bottom:22px;}
.prose ul,.prose ol{margin:14px 0 22px 22px;}
.prose li{font-size:16.5px;line-height:1.72;color:#374151;margin-bottom:9px;}
.prose li::marker{color:var(--fire);}
.prose strong{color:var(--navy);font-weight:700;}
.prose a{color:var(--fire);border-bottom:1px solid rgba(255,107,53,0.25);transition:border-color var(--t);}
.prose a:hover{border-color:var(--fire);}
.prose blockquote{border-left:4px solid var(--fire);padding:16px 24px;margin:30px 0;background:linear-gradient(135deg,rgba(240,214,164,0.15),rgba(240,214,164,0.06));border-radius:0 10px 10px 0;font-style:italic;}

/* Visual blocks */
.vblock{display:flex;gap:14px;align-items:flex-start;padding:20px 22px;border-radius:12px;margin:26px 0;}
.vblock p{margin:0;font-size:15.5px;}
.vblock-ico{width:38px;height:38px;border-radius:10px;display:flex;align-items:center;justify-content:center;flex-shrink:0;}
.vblock-label{font-size:10.5px;font-weight:800;letter-spacing:0.12em;text-transform:uppercase;display:block;margin-bottom:5px;}
.vb-tip{background:rgba(255,107,53,0.08);border:1px solid rgba(255,107,53,0.2);border-left:4px solid var(--fire);}
.vb-tip .vblock-ico{background:rgba(255,107,53,0.12);color:var(--fire);}
.vb-tip .vblock-label{color:var(--fire);}
.vb-note{background:rgba(10,37,64,0.04);border:1px solid rgba(10,37,64,0.10);border-left:4px solid var(--navy);}
.vb-note .vblock-ico{background:rgba(10,37,64,0.08);color:var(--navy);}
.vb-note .vblock-label{color:var(--navy);}
.pull-quote{position:relative;padding:28px 32px 24px;margin:36px 0;background:linear-gradient(135deg,rgba(240,214,164,0.22),rgba(240,214,164,0.08));border-radius:16px;border-left:5px solid var(--sand);}
.pull-quote::before{content:'';position:absolute;top:12px;right:16px;width:44px;height:36px;opacity:0.12;background:currentColor;}
.pq-txt{font-size:19px;font-style:italic;line-height:1.7;color:var(--navy);font-family:var(--fh);font-weight:600;margin:0;}
.ilink{color:var(--fire) !important;font-weight:600;display:inline-flex;align-items:center;gap:4px;}
/* Lang bar */
.art-lang-bar{display:flex;gap:8px;flex-wrap:wrap;align-items:center;padding:14px 18px;background:#f9fafb;border-radius:12px;border:1px solid #e5e7eb;margin-bottom:36px;}
.art-lang-bar .lbl{font-size:11px;color:#9ca3af;text-transform:uppercase;letter-spacing:0.1em;margin-right:4px;}
.lang-pill{display:inline-flex;align-items:center;gap:7px;padding:6px 12px;border-radius:8px;font-size:12.5px;font-weight:600;background:#fff;border:1px solid #e5e7eb;color:#374151;transition:var(--t);}
.lang-pill:hover,.lang-pill.active{background:var(--navy);color:#fff;border-color:var(--navy);}
/* Article CTA */
.art-cta{
  margin:56px 0;padding:40px;border-radius:var(--r);text-align:center;color:#fff;
  background:linear-gradient(135deg,var(--navy) 0%,var(--navy2) 100%);
  position:relative;overflow:hidden;
}
.art-cta::before{
  content:'';position:absolute;inset:0;
  background:url("data:image/svg+xml,%3Csvg viewBox='0 0 400 80' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0 50 C80 30,160 55,240 40 C320 25,380 50,400 40 L400 80 L0 80Z' fill='rgba(255,255,255,0.03)'/%3E%3C/svg%3E") bottom;
  background-size:100%;background-repeat:no-repeat;
}
/* Author card */
.author-card{display:flex;align-items:center;gap:14px;padding:20px 24px;background:#f9fafb;border-radius:14px;border:1px solid #e5e7eb;margin:40px 0;position:relative;}
.author-avatar{width:60px;height:60px;border-radius:50%;object-fit:cover;flex-shrink:0;border:3px solid #fff;box-shadow:0 2px 12px rgba(10,37,64,0.15);}
.author-av-ph{width:60px;height:60px;border-radius:50%;background:linear-gradient(135deg,var(--navy),var(--navy2));display:flex;align-items:center;justify-content:center;color:var(--sand);font-size:22px;font-weight:700;flex-shrink:0;}
.author-name{font-weight:700;font-size:15px;color:var(--navy);}
.author-role{font-size:12.5px;color:var(--fire);font-weight:600;}
.author-bio-text{font-size:13px;color:#6b7280;margin-top:4px;line-height:1.55;}
/* Breadcrumb */
.breadcrumb{display:flex;align-items:center;gap:6px;font-size:12.5px;color:#9ca3af;margin-bottom:28px;flex-wrap:wrap;}
.breadcrumb a{color:#6b7280;transition:color var(--t);}
.breadcrumb a:hover{color:var(--fire);}
.breadcrumb span{color:#d1d5db;}
/* Related */
.related-grid{display:grid;grid-template-columns:1fr 1fr;gap:20px;}

/* ══════════════════════════════════════════════════════
   PAGE HEADER (non-hero pages)
══════════════════════════════════════════════════════ */
.page-header{
  padding:140px 24px 80px;color:#fff;text-align:center;
  background-size:cover;background-position:center;position:relative;overflow:hidden;
}
.page-header::before{content:'';position:absolute;inset:0;background:linear-gradient(rgba(10,37,64,0.6),rgba(10,37,64,0.88));}
.page-header>*{position:relative;z-index:1;}
.page-header h1{font-size:clamp(30px,5vw,60px);margin-bottom:14px;}
.page-header p{font-size:18px;opacity:0.85;max-width:560px;margin:0 auto;}

/* ══════════════════════════════════════════════════════
   BOOKING FORM
══════════════════════════════════════════════════════ */
.form-card{background:#fff;border-radius:var(--r);padding:40px;box-shadow:0 4px 32px rgba(10,37,64,0.08);}
.form-group{margin-bottom:20px;}
.form-label{display:block;font-weight:600;font-size:13px;margin-bottom:7px;color:var(--navy);}
.form-input,.form-select,.form-textarea{width:100%;padding:12px 16px;border:2px solid #e5e7eb;border-radius:10px;font-family:var(--fb);font-size:15px;color:var(--navy);transition:var(--t);outline:none;background:#fff;}
.form-input:focus,.form-select:focus,.form-textarea:focus{border-color:var(--fire);box-shadow:0 0 0 3px rgba(255,107,53,0.12);}
.form-textarea{resize:vertical;min-height:88px;}
.form-row{display:grid;grid-template-columns:1fr 1fr;gap:18px;}
.form-check{display:flex;align-items:center;gap:10px;cursor:pointer;font-size:14px;color:#374151;}
.form-check input{accent-color:var(--fire);width:17px;height:17px;}

/* ══════════════════════════════════════════════════════
   CTA BAND
══════════════════════════════════════════════════════ */
.cta-band{
  padding:100px 0;color:#fff;text-align:center;
  background:linear-gradient(150deg,var(--navy) 0%,var(--navy2) 50%,#0a1f35 100%);
  position:relative;overflow:hidden;
}
.cta-band::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse at 50% 110%,rgba(255,107,53,0.20) 0%,transparent 55%);}
.cta-band h2{font-size:clamp(26px,4vw,48px);margin-bottom:14px;position:relative;z-index:1;}
.cta-band p{font-size:17px;opacity:0.80;max-width:520px;margin:0 auto 40px;position:relative;z-index:1;line-height:1.7;}
.cta-btns{display:flex;gap:14px;justify-content:center;flex-wrap:wrap;position:relative;z-index:1;}

/* ══════════════════════════════════════════════════════
   FOOTER
══════════════════════════════════════════════════════ */
footer{background:var(--navy);color:#fff;padding:72px 0 32px;border-top:1px solid rgba(255,255,255,0.06);}
.footer-grid{display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:48px;margin-bottom:52px;}
.footer-brand-logo{height:auto;max-height:56px;width:auto;max-width:180px;display:block;margin-bottom:18px;object-fit:contain;}
.footer-brand p{font-size:13.5px;opacity:0.60;line-height:1.75;max-width:260px;}
.footer-col h4{font-size:11px;font-weight:800;letter-spacing:0.14em;text-transform:uppercase;color:var(--sand);margin-bottom:18px;}
.footer-col a{display:block;font-size:14px;color:rgba(255,255,255,0.60);margin-bottom:10px;transition:color var(--t);}
.footer-col a:hover{color:#fff;}
.footer-social{display:flex;gap:10px;margin-top:20px;}
.soc-btn{width:40px;height:40px;border-radius:10px;background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.10);display:flex;align-items:center;justify-content:center;color:rgba(255,255,255,0.70);transition:var(--t);}
.soc-btn:hover{background:rgba(255,255,255,0.16);color:#fff;transform:translateY(-2px);}
.soc-btn.wa:hover{background:#25D366;border-color:transparent;}
.soc-btn.ig:hover{background:linear-gradient(135deg,#f09433,#e6683c,#dc2743,#bc1888);border-color:transparent;}
.soc-btn.tt:hover{background:#010101;border-color:transparent;}
.footer-bottom{border-top:1px solid rgba(255,255,255,0.07);padding-top:28px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:14px;}
.footer-bottom p{font-size:13px;color:rgba(255,255,255,0.40);}
.footer-flags{display:flex;gap:10px;align-items:center;}
.footer-flag-link{opacity:0.55;transition:opacity var(--t);display:inline-flex;}
.footer-flag-link:hover{opacity:1;}

/* ══════════════════════════════════════════════════════
   FLOATING WhatsApp
══════════════════════════════════════════════════════ */
#float-wa{
  position:fixed;bottom:28px;right:28px;z-index:150;
  width:56px;height:56px;border-radius:50%;
  background:#25D366;color:#fff;
  display:flex;align-items:center;justify-content:center;
  box-shadow:0 8px 24px rgba(37,211,102,0.42);
  transition:transform var(--t),box-shadow var(--t);
  animation:pulse 2.5s ease-in-out 3s infinite;
}
#float-wa:hover{transform:scale(1.12);box-shadow:0 12px 32px rgba(37,211,102,0.55);animation:none;}
#float-wa::before{
  content:'';position:absolute;inset:-4px;border-radius:50%;
  border:2px solid rgba(37,211,102,0.4);
  animation:pulse 2.5s ease-in-out 3.25s infinite;
}

/* ══════════════════════════════════════════════════════
   SCROLL REVEAL
══════════════════════════════════════════════════════ */
.reveal{opacity:0;transform:translateY(28px);transition:opacity 0.65s var(--ease),transform 0.65s var(--ease);}
.reveal.up{opacity:1;transform:none;}

/* ══════════════════════════════════════════════════════
   RESPONSIVE
══════════════════════════════════════════════════════ */
@media(max-width:1024px){
  .footer-grid{grid-template-columns:1fr 1fr;}
  .split{grid-template-columns:1fr;gap:40px;}
  .split-img img{height:320px;}
}
@media(max-width:768px){
  .nav-links{
    display:none;flex-direction:column;position:fixed;
    top:68px;left:0;right:0;padding:16px;
    background:rgba(10,37,64,0.98);
    border-bottom:1px solid rgba(255,255,255,0.08);
    box-shadow:0 10px 30px rgba(0,0,0,0.2);
    z-index:199;
  }
  .nav-links.open{display:flex;}
  .nav-toggle{display:flex;}
  .hero{background-attachment:scroll;}
  .hero-h1{font-size:clamp(34px,9vw,60px);}
  .hero-trust{gap:10px;}
  .trust-badge{font-size:11px;padding:6px 12px;}
  .stats-inner{gap:32px;}
  .gallery-masonry{columns:2 180px;}
  .related-grid{grid-template-columns:1fr;}
  .form-row{grid-template-columns:1fr;}
  .footer-grid{grid-template-columns:1fr;gap:28px;}
  .section{padding:72px 0;}
  .form-card{padding:24px;}
  #float-wa{bottom:20px;right:20px;width:50px;height:50px;}
  .art-hero-inner{padding:28px 20px;}
}
@media(max-width:480px){
  .hero-cta{flex-direction:column;align-items:stretch;}
  .btn{justify-content:center;}
  .cta-btns{flex-direction:column;align-items:center;}
  .gallery-masonry{columns:1;}
  .testimonial{padding:22px;}
  .hero-trust{flex-direction:column;align-items:center;}
  .pull-quote{padding:18px 20px;}
}
"""

with open(f"{DEMO_DIR}/assets/css/style.css","w") as f:
    f.write(CSS_V4)
print("✅ CSS v4 written")

# ════════════════════════════════════════════════════════════════════════════════
# JAVASCRIPT — Smart language redirect + all interactions
# ════════════════════════════════════════════════════════════════════════════════
GLOBAL_JS = """<script>
/* ── Scroll progress ─────────────────────────────────── */
window.addEventListener('scroll', () => {
  const el = document.getElementById('scroll-progress');
  if(el){
    const pct = (scrollY / (document.body.scrollHeight - innerHeight)) * 100;
    el.style.width = Math.min(pct, 100) + '%';
  }
}, {passive:true});

/* ── Nav scroll ──────────────────────────────────────── */
window.addEventListener('scroll', () => {
  const nav = document.getElementById('nav');
  if(nav) nav.classList.toggle('scrolled', scrollY > 30);
}, {passive:true});

/* ── Reveal on scroll ────────────────────────────────── */
const revealObs = new IntersectionObserver(es => {
  es.forEach(e => { if(e.isIntersecting) e.target.classList.add('up'); });
}, {threshold:0.09});
document.querySelectorAll('.reveal').forEach(el => revealObs.observe(el));

/* ── Counter animation ───────────────────────────────── */
function animateCounter(el) {
  const target = parseFloat(el.dataset.target || el.textContent.replace(/[^0-9.]/g,''));
  const suffix = el.dataset.suffix || el.textContent.replace(/[0-9.]/g,'').trim();
  const dur    = 1800;
  const start  = Date.now();
  const tick   = () => {
    const p = Math.min((Date.now() - start) / dur, 1);
    const ease = 1 - Math.pow(1 - p, 3);
    const val  = target < 10 ? (ease * target).toFixed(1) : Math.round(ease * target);
    el.textContent = val + suffix;
    if(p < 1) requestAnimationFrame(tick);
  };
  tick();
}
const ctrObs = new IntersectionObserver(es => {
  es.forEach(e => {
    if(e.isIntersecting){
      animateCounter(e.target);
      ctrObs.unobserve(e.target);
    }
  });
}, {threshold:0.5});
document.querySelectorAll('.stat-n[data-target]').forEach(el => ctrObs.observe(el));

/* ── Smart language selector ────────────────────────────
   Reads current URL path, strips lang prefix,
   redirects to the correct language version          */
function detectLangFromPath() {
  const path = location.pathname;
  const langs = ['fr','es','it','de'];
  for(const l of langs){
    if(path === '/' + l || path === '/' + l + '/' || path.startsWith('/' + l + '/'))
      return l;
  }
  return 'en';
}
function getBasePath() {
  const path = location.pathname;
  const langs = ['fr','es','it','de'];
  for(const l of langs){
    if(path === '/' + l || path === '/' + l + '/') return '/';
    if(path.startsWith('/' + l + '/')){
      const base = path.slice(l.length + 1);
      return base || '/';
    }
  }
  return path;
}
function switchLang(newLang) {
  const base   = getBasePath();
  const newPath = newLang === 'en' ? base : '/' + newLang + base;
  localStorage.setItem('ngor_lang', newLang);
  location.href = newPath;
}
function toggleLangDD(e) {
  e.stopPropagation();
  document.getElementById('lang-dd').classList.toggle('open');
}
document.addEventListener('click', e => {
  const dd = document.getElementById('lang-dd');
  if(dd && !dd.contains(e.target)) dd.classList.remove('open');
});

/* ── Mobile nav ──────────────────────────────────────── */
function toggleMenu(){
  const el = document.getElementById('nav-links');
  el && el.classList.toggle('open');
}
document.addEventListener('click', e => {
  const nl = document.getElementById('nav-links');
  const nt = document.getElementById('nav-toggle');
  if(nl && nt && !nl.contains(e.target) && !nt.contains(e.target))
    nl.classList.remove('open');
});

/* ── FAQ accordion ───────────────────────────────────── */
document.querySelectorAll('.faq-q').forEach(q => {
  q.addEventListener('click', () => q.closest('.faq-item').classList.toggle('open'));
});

/* ── Gallery lightbox ────────────────────────────────── */
const lb    = document.getElementById('lb');
const lbImg = document.getElementById('lb-img');
const lbCls = document.getElementById('lb-close');
if(lb){
  document.querySelectorAll('.gallery-item').forEach(item => {
    item.addEventListener('click', () => {
      lbImg.src = item.querySelector('img').src;
      lb.classList.add('open');
    });
  });
  lb.addEventListener('click', e => { if(e.target === lb) lb.classList.remove('open'); });
  lbCls && lbCls.addEventListener('click', () => lb.classList.remove('open'));
  document.addEventListener('keydown', e => { if(e.key==='Escape') lb.classList.remove('open'); });
}

/* ── Video hero ──────────────────────────────────────── */
const vid = document.getElementById('hero-video');
if(vid){
  vid.play().catch(() => {
    const wrap = document.querySelector('.hero-video-wrap');
    if(wrap) wrap.style.display = 'none';
  });
}

/* ── Booking form → WhatsApp ─────────────────────────── */
const form = document.getElementById('booking-form');
if(form){
  form.addEventListener('submit', function(e){
    e.preventDefault();
    const name  = (this.querySelector('.f-name')  || {}).value || '';
    const level = (this.querySelector('.f-level') || {}).value || '';
    const msg   = encodeURIComponent(
      'Hello Ngor Surfcamp! I would like to book a stay.' +
      (name  ? ' Name: ' + name + '.' : '') +
      (level ? ' Level: ' + level + '.' : '') +
      ' Please send me availability and prices.'
    );
    window.open('https://wa.me/221789257025?text=' + msg, '_blank');
  });
}
</script>"""

# ════════════════════════════════════════════════════════════════════════════════
# MARKDOWN → RICH HTML
# ════════════════════════════════════════════════════════════════════════════════
def md2html(md):
    if not md: return ""
    md = fix_em(md)
    lines  = md.split("\n")
    out    = []
    in_ul  = in_ol = False
    tip_kw = ("**TIP:","**CONSEIL:","**TIPP:","**CONSEJO:","**CONSIGLIO:")
    note_kw= ("**NOTE:","**REMARQUE:","**HINWEIS:","**NOTA:")

    def close_lists():
        nonlocal in_ul, in_ol
        if in_ul: out.append("</ul>"); in_ul = False
        if in_ol: out.append("</ol>"); in_ol = False

    def inline(t):
        t = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', t)
        t = re.sub(r'(?<![*])\*(?![*])(.*?)(?<![*])\*(?![*])', r'<em>\1</em>', t)
        def mk_ilink(m):
            parts = m.group(0)[6:-1].split("→")
            a = parts[0].strip(); tgt = parts[1].strip() if len(parts)>1 else "#"
            return f'<a href="{tgt}/" class="ilink">{ICO["arrow"].replace("currentColor","var(--fire)")} {a}</a>'
        t = re.sub(r'\[LINK:[^\]]+\]', mk_ilink, t)
        return t

    for line in lines:
        s = line.strip()
        if not s:
            close_lists(); continue
        if s.startswith("### "):
            close_lists(); out.append(f"<h3>{inline(s[4:])}</h3>")
        elif s.startswith("## "):
            close_lists(); out.append(f"<h2>{inline(s[3:])}</h2>")
        elif s.startswith("# "):
            close_lists(); out.append(f"<h1>{inline(s[2:])}</h1>")
        elif s.startswith("#### "):
            close_lists(); out.append(f"<h4>{inline(s[5:])}</h4>")
        elif s.startswith("> "):
            close_lists()
            out.append(f'<div class="pull-quote"><blockquote class="pq-txt">{inline(s[2:])}</blockquote></div>')
        elif any(s.upper().startswith(k) for k in tip_kw):
            close_lists()
            ct = re.sub(r'^\*\*[^:]+:\*?\*?\s*','',s)
            out.append(f'<div class="vblock vb-tip"><div class="vblock-ico">{ico("tip",18)}</div><div><span class="vblock-label">Tip</span><p>{inline(ct)}</p></div></div>')
        elif any(s.upper().startswith(k) for k in note_kw):
            close_lists()
            ct = re.sub(r'^\*\*[^:]+:\*?\*?\s*','',s)
            out.append(f'<div class="vblock vb-note"><div class="vblock-ico">{ico("tip",18)}</div><div><span class="vblock-label">Note</span><p>{inline(ct)}</p></div></div>')
        elif re.match(r'^[-*]\s',s):
            if not in_ul: out.append('<ul class="prose-ul">'); in_ul=True
            if in_ol: out.append("</ol>"); in_ol=False
            out.append(f"<li>{inline(s[2:])}</li>")
        elif re.match(r'^\d+\.\s',s):
            if not in_ol: out.append('<ol class="prose-ol">'); in_ol=True
            if in_ul: out.append("</ul>"); in_ul=False
            item = re.sub(r'^\d+\.\s','',s)
            out.append(f"<li>{inline(item)}</li>")
        elif s.startswith("**") and s.endswith("**") and s.count("**")==2:
            close_lists()
            t = s.strip("*")
            if t.endswith("?"): out.append(f'<h4 style="padding-left:12px;border-left:3px solid var(--fire);margin:24px 0 10px">{t}</h4>')
            else: out.append(f"<h4>{t}</h4>")
        else:
            close_lists()
            p = inline(s)
            if p:
                if s.startswith('"') and s.endswith('"') and len(s)>50:
                    out.append(f'<div class="pull-quote"><blockquote class="pq-txt">{p}</blockquote></div>')
                else:
                    out.append(f"<p>{p}</p>")
    close_lists()
    return "\n".join(out)

# ════════════════════════════════════════════════════════════════════════════════
# TEMPLATE HELPERS
# ════════════════════════════════════════════════════════════════════════════════
def art_img(en_slug):
    local = f"/assets/images/{en_slug}.png"
    return local if os.path.exists(f"{DEMO_DIR}{local}") else IMGS["surf3"]

def author_for(art):
    cat = art.get("category","")
    aid = CAT_AUTHOR.get(cat,"kofi-mensah")
    return authors.get(aid,{}), aid

def hreflang(page_slug):
    slug = "/" + page_slug.strip("/") if page_slug.strip("/") else ""
    tags = [
        f'<link rel="alternate" hreflang="x-default" href="{SITE_URL}{slug}/">',
        f'<link rel="alternate" hreflang="en"          href="{SITE_URL}{slug}/">',
    ]
    for l in ["fr","es","it","de"]:
        tags.append(f'<link rel="alternate" hreflang="{LANG_LOCALE[l]}" href="{SITE_URL}/{l}{slug}/">')
    return "\n  ".join(tags)

def canonical(slug, lang):
    s = "/" + slug.strip("/") if slug.strip("/") else ""
    pfx = f"/{lang}" if lang!="en" else ""
    return f'<link rel="canonical" href="{SITE_URL}{pfx}{s}/">'

def head(title, meta_d, can, hrl, lang, og_img=""):
    og = og_img or IMGS["home"]
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{fix_em(title)}</title>
<meta name="description" content="{fix_em(meta_d)}">
<meta property="og:title" content="{fix_em(title)}">
<meta property="og:description" content="{fix_em(meta_d)}">
<meta property="og:image" content="{og}">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<meta name="robots" content="index,follow">
{can}
{hrl}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Raleway:ital,wght@0,300;0,400;0,600;0,700;0,800;0,900;1,400&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/css/style.css">
</head>
<body>
<div id="scroll-progress"></div>"""

# ── Smart language dropdown ───────────────────────────────────────────────────
def lang_dropdown(current_lang, page_slug, has_blog_slug=None):
    """
    Builds a custom dropdown that redirects to the correct URL.
    Does NOT show the current language.
    page_slug: e.g. '', '/blog', '/blog/some-slug'
    """
    slug_clean = "/" + page_slug.strip("/") if page_slug.strip("/") else ""

    opts = ""
    for l in LANGS:
        if l == current_lang:
            continue
        if l == "en":
            url = f"{slug_clean}/" if slug_clean else "/"
        else:
            url = f"/{l}{slug_clean}/"
        opts += f'<a class="lang-dd-item" href="{url}" hreflang="{LANG_LOCALE[l]}">{flag(l,18)} {LANG_NAMES[l]}</a>\n'

    cur_code = current_lang.upper()
    return f"""<div class="lang-dd" id="lang-dd">
  <button class="lang-dd-btn" onclick="toggleLangDD(event)" aria-label="Switch language" aria-expanded="false" aria-haspopup="true">
    {flag(current_lang, 20)} {cur_code}
    <span class="chev">{ICO["chev"]}</span>
  </button>
  <div class="lang-dd-menu" role="menu">
    {opts}
  </div>
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
    <div class="nav-links" id="nav-links">
      {items}
    </div>
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
    PAGES_LINKS = [
        ("/surf-house",{"en":"Surf House","fr":"Surf House","es":"Surf House","it":"Surf House","de":"Surf House"}),
        ("/island",    {"en":"Island","fr":"Île de Ngor","es":"Isla de Ngor","it":"Isola di Ngor","de":"Ngor Island"}),
        ("/surfing",   {"en":"Surfing","fr":"Surf","es":"Surf","it":"Surf","de":"Surfen"}),
        ("/blog",      {"en":"Blog","fr":"Blog","es":"Blog","it":"Blog","de":"Blog"}),
        ("/gallery",   {"en":"Gallery","fr":"Galerie","es":"Galería","it":"Galleria","de":"Galerie"}),
        ("/faq",       {"en":"FAQ","fr":"FAQ","es":"FAQ","it":"FAQ","de":"FAQ"}),
        ("/booking",   {"en":"Book Now","fr":"Réserver","es":"Reservar","it":"Prenota","de":"Buchen"}),
    ]
    links_html = "\n".join([f'<a href="{pfx}{s}/">{labels.get(lang,labels["en"])}</a>' for s,labels in PAGES_LINKS])
    flags_html = " ".join([
        f'<a href="{"" if l=="en" else "/"+l}/" class="footer-flag-link" hreflang="{LANG_LOCALE[l]}" title="{LANG_NAMES[l]}">{flag(l,22)}</a>'
        for l in LANGS
    ])
    ABOUT = {
        "en":"Premium surf camp on Ngor Island, Dakar, Senegal. All levels. Licensed by the Senegalese Federation of Surfing.",
        "fr":"Surf camp premium sur l'île de Ngor, Dakar, Sénégal. Tous niveaux. Agréé par la Fédération Sénégalaise de Surf.",
        "es":"Surf camp premium en la isla de Ngor, Dakar, Senegal. Todos los niveles. Licenciado por la Federación Senegalesa de Surf.",
        "it":"Surf camp premium sull'isola di Ngor, Dakar, Senegal. Tutti i livelli. Autorizzato dalla Federazione Senegalese di Surf.",
        "de":"Premium Surfcamp auf Ngor Island, Dakar, Senegal. Alle Level. Lizenziert vom senegalesischen Surfverband.",
    }
    COPY = {"en":"© 2025 Ngor Surfcamp Teranga. All rights reserved.","fr":"© 2025 Ngor Surfcamp Teranga. Tous droits réservés.","es":"© 2025 Ngor Surfcamp Teranga. Todos los derechos reservados.","it":"© 2025 Ngor Surfcamp Teranga. Tutti i diritti riservati.","de":"© 2025 Ngor Surfcamp Teranga. Alle Rechte vorbehalten."}
    EXP = {"en":"Explore","fr":"Explorer","es":"Explorar","it":"Esplora","de":"Erkunden"}
    CON = {"en":"Contact","fr":"Contact","es":"Contacto","it":"Contatti","de":"Kontakt"}
    FOL = {"en":"Follow Us","fr":"Suivez-nous","es":"Síguenos","it":"Seguici","de":"Folgen"}

    return f"""<footer>
  <div class="container">
    <div class="footer-grid">
      <div>
        <img src="{LOGO}" alt="Ngor Surfcamp Teranga" class="footer-brand-logo" loading="lazy">
        <p>{ABOUT[lang]}</p>
        <div class="footer-social">
          <a href="https://wa.me/221789257025" target="_blank" rel="noopener" class="soc-btn wa" aria-label="WhatsApp">
            <span style="width:18px;height:18px;display:inline-flex">{ICO['wa']}</span>
          </a>
          <a href="https://www.instagram.com/ngorsurfcampteranga" target="_blank" rel="noopener" class="soc-btn ig" aria-label="Instagram">
            <span style="width:18px;height:18px;display:inline-flex">{ICO['ig']}</span>
          </a>
          <a href="https://www.tiktok.com/@ngorsurfcampteranga" target="_blank" rel="noopener" class="soc-btn tt" aria-label="TikTok">
            <span style="width:18px;height:18px;display:inline-flex">{ICO['tt']}</span>
          </a>
        </div>
      </div>
      <div class="footer-col"><h4>{EXP[lang]}</h4>{links_html}</div>
      <div class="footer-col">
        <h4>{CON[lang]}</h4>
        <a href="https://wa.me/221789257025" target="_blank">WhatsApp: +221 78 925 70 25</a>
        <a href="mailto:info@surfcampsenegal.com">info@surfcampsenegal.com</a>
        <a href="{pfx}/booking/">{"Book your stay" if lang=="en" else "Réserver" if lang=="fr" else "Reservar" if lang=="es" else "Prenota" if lang=="it" else "Buchen"}</a>
      </div>
      <div class="footer-col">
        <h4>{FOL[lang]}</h4>
        <a href="https://www.instagram.com/ngorsurfcampteranga" target="_blank" rel="noopener">Instagram</a>
        <a href="https://www.tiktok.com/@ngorsurfcampteranga" target="_blank" rel="noopener">TikTok</a>
        <a href="https://wa.me/221789257025" target="_blank" rel="noopener">WhatsApp</a>
      </div>
    </div>
    <div class="footer-bottom">
      <p>{COPY[lang]}</p>
      <div class="footer-flags" aria-label="Language versions">{flags_html}</div>
    </div>
  </div>
</footer>
<!-- Floating WhatsApp -->
<a href="https://wa.me/221789257025" target="_blank" rel="noopener" id="float-wa" aria-label="Chat on WhatsApp">
  <span style="width:26px;height:26px;display:inline-flex">{ICO['wa']}</span>
</a>"""

def close_page():
    return f"\n{GLOBAL_JS}\n</body>\n</html>"

# ════════════════════════════════════════════════════════════════════════════════
# HOMEPAGE — Video hero + animated reveals + creative layout
# ════════════════════════════════════════════════════════════════════════════════
def build_homepage(lang):
    pfx = LANG_PREFIX[lang]
    p   = load(f"{PAGES_D}/{lang}_homepage.json") or {}
    h1  = fix_em(p.get("h1","Ngor Surfcamp Teranga"))
    sub = fix_em(p.get("hero_subtitle","Premium Surfcamp in Senegal"))
    intro = fix_em(p.get("intro","") or "")
    sects = p.get("sections",[])
    title = fix_em(p.get("title_tag","Surf Camp Senegal | Ngor Surfcamp Teranga"))
    meta  = fix_em(p.get("meta_description","Premium surf camp on Ngor Island, Dakar, Senegal."))

    # Make H1 italic on the key noun for gradient effect
    if "Teranga" in h1:
        h1_html = h1.replace("Teranga","<em>Teranga</em>")
    elif "Ngor" in h1:
        h1_html = h1.replace("Ngor","<em>Ngor</em>",1)
    else:
        h1_html = h1

    BOOK = {"en":"Check Availability","fr":"Vérifier les disponibilités","es":"Consultar disponibilidad","it":"Controlla disponibilità","de":"Verfügbarkeit prüfen"}
    DISC = {"en":"Discover","fr":"Découvrir","es":"Descubrir","it":"Scoprire","de":"Entdecken"}
    LAT  = {"en":"Latest from the Blog","fr":"Derniers articles du Blog","es":"Últimos artículos del Blog","it":"Ultimi articoli dal Blog","de":"Neuestes aus dem Blog"}
    ALL  = {"en":"All Articles","fr":"Tous les articles","es":"Todos los artículos","it":"Tutti gli articoli","de":"Alle Artikel"}
    TRUST_FED = {"en":"Licensed by Senegal Surf Federation","fr":"Agréé par la Fédération Sénégalaise de Surf","es":"Licenciado por la Federación Senegalesa","it":"Autorizzato dalla Federazione Senegalese","de":"Lizenziert vom senegalesischen Surfverband"}
    TRUST_LVL = {"en":"All levels welcome","fr":"Tous niveaux bienvenus","es":"Todos los niveles bienvenidos","it":"Tutti i livelli benvenuti","de":"Alle Level willkommen"}
    TRUST_YR  = {"en":"Open year-round","fr":"Ouvert toute l'année","es":"Abierto todo el año","it":"Aperto tutto l'anno","de":"Ganzjährig geöffnet"}
    ABOUT_H2  = {"en":"Serious about improving your surfing?","fr":"Sérieux dans votre progression surf ?","es":"Serio en mejorar tu surf?","it":"Serio nel migliorare il tuo surf?","de":"Ernsthaft am Surfen verbessern?"}
    INTRO_FB  = {"en":"At Ngor Surfcamp Teranga, we pair world-class West African waves with professional coaching and authentic island life. Whether you are picking up a surfboard for the first time or pushing your limits on Ngor Right, our licensed team is here to help you progress.","fr":"Au Ngor Surfcamp Teranga, nous combinons des vagues de classe mondiale avec un coaching professionnel et la vie authentique de l'île. Que vous preniez une planche pour la première fois ou que vous poussiez vos limites sur Ngor Right, notre équipe agréée est là pour vous aider à progresser.","es":"En Ngor Surfcamp Teranga combinamos olas de clase mundial con coaching profesional y vida isleña auténtica. Ya sea que estés cogiendo una tabla por primera vez o llevando tus límites a Ngor Right, nuestro equipo licenciado está aquí para ayudarte a progresar.","it":"Al Ngor Surfcamp Teranga combiniamo onde di classe mondiale con coaching professionale e vita isolana autentica. Che tu stia prendendo una tavola per la prima volta o spingendo i tuoi limiti su Ngor Right, il nostro team autorizzato è qui per aiutarti a progredire.","de":"Im Ngor Surfcamp Teranga verbinden wir weltklasse Wellen mit professionellem Coaching und authentischem Inselleben. Egal ob du zum ersten Mal ein Surfbrett in die Hand nimmst oder deine Grenzen an Ngor Right auslotst, unser lizenziertes Team ist für Sie da."}
    SH_L = {"en":"The Surf House","fr":"La Surf House","es":"La Surf House","it":"La Surf House","de":"Das Surf House"}
    IS_L = {"en":"Ngor Island","fr":"Île de Ngor","es":"Isla de Ngor","it":"Isola di Ngor","de":"Ngor Island"}
    CO_L = {"en":"Surf Coaching","fr":"Coaching Surf","es":"Coaching Surf","it":"Coaching Surf","de":"Surf-Coaching"}
    SH_D = {"en":"Cozy rooms, pool, sea views, daily Senegalese meals. Your home by the ocean.","fr":"Chambres, piscine, vue mer, repas sénégalais. Votre maison au bord de l'océan.","es":"Habitaciones, piscina, vista al mar, comidas senegalesas. Tu hogar junto al océano.","it":"Camere, piscina, vista mare, pasti senegalesi. La tua casa sull'oceano.","de":"Zimmer, Pool, Meerblick, senegalesische Mahlzeiten. Ihr Zuhause am Ozean."}
    IS_D = {"en":"No cars, world-class waves, The Endless Summer legacy. A gem off Dakar.","fr":"Pas de voitures, vagues de classe mondiale, héritage de The Endless Summer.","es":"Sin coches, olas de clase mundial, el legado de The Endless Summer.","it":"Niente auto, onde di classe mondiale, il lascito di The Endless Summer.","de":"Keine Autos, weltklasse Wellen, das Erbe von The Endless Summer."}
    CO_D = {"en":"Professional video analysis, personalized sessions, all levels. Licensed coaches.","fr":"Analyse vidéo pro, séances personnalisées, tous niveaux. Coachs agréés.","es":"Análisis de vídeo profesional, sesiones personalizadas, todos los niveles.","it":"Analisi video professionale, sessioni personalizzate, tutti i livelli.","de":"Professionelle Videoanalyse, personalisierte Sessions, alle Level."}
    EV   = {"en":"Everything at Ngor Surfcamp","fr":"Tout au Ngor Surfcamp","es":"Todo en Ngor Surfcamp","it":"Tutto al Ngor Surfcamp","de":"Alles im Ngor Surfcamp"}
    REV_T = {"en":"I had an amazing stay at Ngor Surfcamp Teranga. The coaching was top-notch and my surfing improved significantly.","fr":"Un séjour incroyable au Ngor Surfcamp Teranga. Le coaching était excellent et mon surf a vraiment progressé.","es":"Una estancia increíble en Ngor Surfcamp Teranga. El coaching fue excelente y mi surf mejoró significativamente.","it":"Un soggiorno incredibile al Ngor Surfcamp Teranga. Il coaching era ottimo e il mio surf è migliorato significativamente.","de":"Ein unglaublicher Aufenthalt im Ngor Surfcamp Teranga. Das Coaching war erstklassig und mein Surfen hat sich deutlich verbessert."}
    WHAT = {"en":"What surfers say","fr":"Ce que disent les surfeurs","es":"Lo que dicen los surfistas","it":"Cosa dicono i surfisti","de":"Was Surfer sagen"}
    SURF_REV = {"en":"Surfer, France","fr":"Surfeur, France","es":"Surfista, Francia","it":"Surfista, Francia","de":"Surfer, Frankreich"}
    CTA_H = {"en":"Ready to surf? Book your stay.","fr":"Prêt à surfer ? Réservez votre séjour.","es":"Listo para surfear? Reserva tu estancia.","it":"Pronto a surfare? Prenota il tuo soggiorno.","de":"Bereit zum Surfen? Buche jetzt."}
    CTA_P = {"en":"Ngor Island, Dakar, Senegal. WhatsApp: +221 78 925 70 25","fr":"Île de Ngor, Dakar, Sénégal. WhatsApp : +221 78 925 70 25","es":"Isla de Ngor, Dakar, Senegal. WhatsApp: +221 78 925 70 25","it":"Isola di Ngor, Dakar, Senegal. WhatsApp: +221 78 925 70 25","de":"Ngor Island, Dakar, Senegal. WhatsApp: +221 78 925 70 25"}
    STAT_LB = {"waves":{"en":"Waves","fr":"Vagues","es":"Olas","it":"Onde","de":"Wellen"},"levels":{"en":"All Levels","fr":"Tous Niveaux","es":"Todos Niveles","it":"Tutti i Livelli","de":"Alle Level"},"years":{"en":"Year-Round","fr":"Toute l'année","es":"Todo el año","it":"Tutto l'anno","de":"Ganzjährig"},"legacy":{"en":"Endless Summer","fr":"Endless Summer","es":"Endless Summer","it":"Endless Summer","de":"Endless Summer"}}

    blog_cards = ""
    for en_art in arts_en[:3]:
        en_slug = en_art["slug"]
        art = arts_by_lang[lang].get(en_slug, en_art) if lang!="en" else en_art
        t   = fix_em(art.get("title",en_art["title"]))[:80]
        m   = fix_em(art.get("meta_description",""))[:110]
        blog_cards += f"""<a href="{pfx}/blog/{en_slug}/" class="card" style="text-decoration:none">
      <img src="{art_img(en_slug)}" alt="{t}" class="card-img" loading="lazy" onerror="this.src='{IMGS['surf3']}'">
      <div class="card-body">
        <span class="cat-badge">{en_art.get('category','')}</span>
        <h3 class="card-h3" style="margin-top:10px;font-size:17px">{t}</h3>
        <p class="card-text">{m}</p>
      </div>
    </a>"""

    eyebrow = {"en":"Ngor Island · Dakar · Senegal","fr":"Île de Ngor · Dakar · Sénégal","es":"Isla de Ngor · Dakar · Senegal","it":"Isola di Ngor · Dakar · Senegal","de":"Ngor Island · Dakar · Senegal"}

    html = head(title, meta, canonical("",lang), hreflang(""), lang, IMGS["home"])
    html += nav_html("", lang, pfx, "")
    html += f"""
<main>
  <!-- VIDEO HERO -->
  <section class="hero">
    <div class="hero-video-wrap">
      <video id="hero-video" autoplay muted loop playsinline preload="none" poster="{VIDEO_POSTER}">
        <source src="{VIDEO_BASE}/480p/mp4/file.mp4" type="video/mp4">
        <source src="{VIDEO_BASE}/360p/mp4/file.mp4" type="video/mp4">
      </video>
    </div>

    <div class="hero-content">
      <p class="hero-eyebrow">
        <span style="width:16px;height:12px;display:inline-flex;opacity:0.8">{ICO['wave']}</span>
        {eyebrow[lang]}
      </p>
      <h1 class="hero-h1">{h1_html}</h1>
      <p class="hero-sub">{sub}</p>

      <div class="hero-cta">
        <a href="{pfx}/booking/" class="btn btn-fire btn-lg">{BOOK[lang]}</a>
        <a href="https://wa.me/221789257025" target="_blank" rel="noopener" class="btn btn-glass btn-lg">
          <span style="width:18px;height:18px;display:inline-flex">{ICO['wa']}</span> WhatsApp
        </a>
      </div>

      <!-- Trust badges -->
      <div class="hero-trust">
        <div class="trust-badge">
          <span style="width:15px;height:15px;display:inline-flex;color:var(--sand)">{ICO['shield']}</span>
          {TRUST_FED[lang]}
        </div>
        <div class="trust-badge">
          <span style="width:15px;height:15px;display:inline-flex;color:var(--sand)">{ICO['wave']}</span>
          {TRUST_LVL[lang]}
        </div>
        <div class="trust-badge">
          <span style="width:15px;height:15px;display:inline-flex;color:var(--sand)">{ICO['star']}</span>
          {TRUST_YR[lang]}
        </div>
      </div>
    </div>

    <!-- Animated wave bottom -->
    <div class="hero-waves" aria-hidden="true">
      <svg viewBox="0 0 1440 120" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">
        <path d="M0 80 C180 40,360 90,540 70 C720 50,900 90,1080 60 C1260 30,1380 70,1440 60 L1440 120 L0 120 Z" fill="rgba(255,255,255,0.04)"/>
        <path d="M0 95 C200 60,400 100,600 85 C800 70,1000 100,1200 80 C1300 70,1380 90,1440 85 L1440 120 L0 120 Z" fill="rgba(255,255,255,0.07)"/>
        <path d="M0 108 C240 88,480 115,720 105 C960 95,1200 115,1440 108 L1440 120 L0 120 Z" fill="#fff"/>
      </svg>
    </div>
  </section>

  <!-- STATS with counter animation -->
  <div class="stats-bar">
    <div class="stats-inner">
      <div class="stat">
        <span class="stat-n" data-target="3" data-suffix="">3</span>
        <span class="stat-l">{STAT_LB["waves"][lang]}</span>
      </div>
      <div class="stat">
        <span class="stat-n">All</span>
        <span class="stat-l">{STAT_LB["levels"][lang]}</span>
      </div>
      <div class="stat">
        <span class="stat-n" data-target="5" data-suffix="★">5★</span>
        <span class="stat-l">{"Rating" if lang=="en" else "Note" if lang=="fr" else "Calificación" if lang=="es" else "Valutazione" if lang=="it" else "Bewertung"}</span>
      </div>
      <div class="stat">
        <span class="stat-n">1964</span>
        <span class="stat-l">{STAT_LB["legacy"][lang]}</span>
      </div>
    </div>
  </div>

  <!-- ABOUT SPLIT -->
  <section class="section">
    <div class="container">
      <div class="split reveal">
        <div>
          <span class="s-label">{"Premium Surf Camp" if lang=="en" else "Surf Camp Premium"}</span>
          <h2 class="s-title">{sects[0]["h2"] if sects else ABOUT_H2.get(lang,"")}</h2>
          <p class="s-sub" style="margin-bottom:32px">{intro or INTRO_FB.get(lang,"")}</p>
          <div style="display:flex;gap:12px;flex-wrap:wrap">
            <a href="{pfx}/surf-house/" class="btn btn-deep">{SH_L[lang]}</a>
            <a href="{pfx}/surfing/" class="btn btn-outline">{"Coaching" if lang=="en" else "Coaching"}</a>
          </div>
        </div>
        <div class="split-img">
          <img src="{IMGS['surf2']}" alt="Surf coaching Ngor Island Senegal" loading="lazy" width="600" height="460">
        </div>
      </div>
    </div>
  </section>

  <!-- 3 PILLARS with wave divider -->
  <div class="wave-top" style="background:#f8fafc">
    <svg viewBox="0 0 1440 40" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none"><path d="M0 20 C360 40,720 0,1080 25 C1260 35,1380 10,1440 20 L1440 0 L0 0Z" fill="#fff"/></svg>
  </div>
  <section class="section sec-light" style="padding-top:40px">
    <div class="container">
      <div class="reveal" style="text-align:center;margin-bottom:60px">
        <span class="s-label">{DISC[lang]}</span>
        <h2 class="s-title">{EV[lang]}</h2>
      </div>
      <div class="grid-3 reveal">
        <a href="{pfx}/surf-house/" class="card">
          <img src="{IMGS['house2']}" alt="{SH_L[lang]}" class="card-img" loading="lazy">
          <div class="card-body">
            <h3 class="card-h3">{SH_L[lang]}</h3>
            <p class="card-text">{SH_D[lang]}</p>
            <span class="btn btn-deep btn-sm" style="margin-top:14px">{DISC[lang]}</span>
          </div>
        </a>
        <a href="{pfx}/island/" class="card">
          <img src="{IMGS['island2']}" alt="{IS_L[lang]}" class="card-img" loading="lazy">
          <div class="card-body">
            <h3 class="card-h3">{IS_L[lang]}</h3>
            <p class="card-text">{IS_D[lang]}</p>
            <span class="btn btn-deep btn-sm" style="margin-top:14px">{DISC[lang]}</span>
          </div>
        </a>
        <a href="{pfx}/surfing/" class="card">
          <img src="{IMGS['surf']}" alt="{CO_L[lang]}" class="card-img" loading="lazy">
          <div class="card-body">
            <h3 class="card-h3">{CO_L[lang]}</h3>
            <p class="card-text">{CO_D[lang]}</p>
            <span class="btn btn-deep btn-sm" style="margin-top:14px">{DISC[lang]}</span>
          </div>
        </a>
      </div>
    </div>
  </section>
  <div class="wave-bottom" style="background:#f8fafc">
    <svg viewBox="0 0 1440 40" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none"><path d="M0 20 C360 0,720 40,1080 15 C1260 5,1380 30,1440 20 L1440 40 L0 40Z" fill="#fff"/></svg>
  </div>

  <!-- TESTIMONIAL -->
  <section class="section">
    <div class="container-sm">
      <div style="text-align:center;margin-bottom:40px" class="reveal">
        <span class="s-label">Reviews</span>
        <h2 class="s-title">{WHAT[lang]}</h2>
      </div>
      <div class="testimonial reveal">
        <p class="testimonial-text">{REV_T[lang]}</p>
        <div style="display:flex;align-items:center;gap:14px;margin-top:20px">
          <img src="{IMGS['review']}" alt="Marc Lecarpentier" style="width:52px;height:52px;border-radius:50%;object-fit:cover;flex-shrink:0" loading="lazy">
          <div>
            <div class="testimonial-author">Marc Lecarpentier</div>
            <div class="testimonial-role">{SURF_REV[lang]}</div>
          </div>
          <div style="margin-left:auto" class="stars">★★★★★</div>
        </div>
      </div>
    </div>
  </section>

  <!-- BLOG PREVIEW -->
  <div class="wave-top" style="background:var(--sand2)">
    <svg viewBox="0 0 1440 40" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none"><path d="M0 15 C480 35,960 5,1440 20 L1440 0 L0 0Z" fill="#fff"/></svg>
  </div>
  <section class="section sec-sand" style="padding-top:40px">
    <div class="container">
      <div class="reveal" style="display:flex;align-items:flex-end;justify-content:space-between;margin-bottom:48px;flex-wrap:wrap;gap:16px">
        <div>
          <span class="s-label">Blog</span>
          <h2 class="s-title">{LAT[lang]}</h2>
        </div>
        <a href="{pfx}/blog/" class="btn btn-fire">{ALL[lang]}</a>
      </div>
      <div class="blog-grid reveal">{blog_cards}</div>
    </div>
  </section>
  <div class="wave-bottom" style="background:var(--sand2)">
    <svg viewBox="0 0 1440 40" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none"><path d="M0 20 C360 5,720 38,1080 18 C1260 8,1380 32,1440 22 L1440 40 L0 40Z" fill="var(--navy)"/></svg>
  </div>

  <!-- CTA BAND -->
  <div class="cta-band">
    <div class="container">
      <h2>{CTA_H[lang]}</h2>
      <p>{CTA_P[lang]}</p>
      <div class="cta-btns">
        <a href="{pfx}/booking/" class="btn btn-fire btn-lg">{BOOK[lang]}</a>
        <a href="https://wa.me/221789257025" target="_blank" rel="noopener" class="btn btn-glass btn-lg">
          <span style="width:18px;height:18px;display:inline-flex">{ICO['wa']}</span> WhatsApp
        </a>
      </div>
    </div>
  </div>
</main>"""
    html += footer_html(lang, pfx)
    html += close_page()
    return html

# ════════════════════════════════════════════════════════════════════════════════
# ARTICLE PAGE
# ════════════════════════════════════════════════════════════════════════════════
def build_article(en_art, lang):
    pfx     = LANG_PREFIX[lang]
    en_slug = en_art["slug"]
    art     = arts_by_lang[lang].get(en_slug, en_art) if lang!="en" else en_art
    title   = fix_em(art.get("title", en_art["title"]))
    meta_d  = fix_em(art.get("meta_description",""))[:155]
    content = md2html(art.get("content_markdown",""))
    cat     = en_art.get("category","")
    img     = art_img(en_slug)
    a_obj, aid = author_for(en_art)

    BACK  = {"en":"Back to Blog","fr":"Retour au Blog","es":"Volver al Blog","it":"Torna al Blog","de":"Zurück zum Blog"}
    BOOK  = {"en":"Book Your Stay","fr":"Réserver","es":"Reservar","it":"Prenota","de":"Buchen"}
    REL   = {"en":"Related Articles","fr":"Articles connexes","es":"Artículos relacionados","it":"Articoli correlati","de":"Verwandte Artikel"}
    BY    = {"en":"Written by","fr":"Écrit par","es":"Escrito por","it":"Scritto da","de":"Geschrieben von"}
    LANG_L = {"en":"Read in:","fr":"Lire en :","es":"Leer en:","it":"Leggi in:","de":"Lesen auf:"}

    # Breadcrumb
    bc_blog = {"en":"Blog","fr":"Blog","es":"Blog","it":"Blog","de":"Blog"}
    breadcrumb = f'<nav class="breadcrumb" aria-label="breadcrumb"><a href="{pfx}/">{"Home" if lang=="en" else "Accueil" if lang=="fr" else "Inicio" if lang=="es" else "Home" if lang=="it" else "Start"}</a><span>›</span><a href="{pfx}/blog/">{bc_blog[lang]}</a><span>›</span><span>{title[:50]}</span></nav>'

    # Lang pills
    lang_pills = " ".join([
        f'<a href="{LANG_PREFIX[l]}/blog/{en_slug}/" class="lang-pill {"active" if l==lang else ""}" hreflang="{LANG_LOCALE[l]}">{flag(l,16)} {LANG_NAMES[l]}</a>'
        for l in LANGS
    ])

    # Author card
    a_name = a_obj.get("name","")
    a_role = a_obj.get("role",{}).get(lang, a_obj.get("role",{}).get("en",""))
    a_bio  = a_obj.get("bio",{}).get(lang, a_obj.get("bio",{}).get("en",""))[:180]
    img_local = f"/assets/images/author-{aid}.jpg"
    img_exists = os.path.exists(f"{DEMO_DIR}{img_local}")
    a_img_tag = f'<img src="{img_local}" alt="{a_name}" class="author-avatar" loading="lazy">' if img_exists else f'<div class="author-av-ph">{a_name[0] if a_name else "N"}</div>'
    author_card = f"""<div class="author-card reveal">
  {a_img_tag}
  <div>
    <div style="font-size:11px;color:#9ca3af;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:4px">{BY[lang]}</div>
    <div class="author-name">{a_name}</div>
    <div class="author-role">{a_role}</div>
    <div class="author-bio-text">{a_bio}</div>
  </div>
</div>""" if a_name else ""

    # Related
    related = [a for a in arts_en if a.get("category")==cat and a["slug"]!=en_slug][:2]
    rel_html = ""
    for rel in related:
        rel_a = arts_by_lang[lang].get(rel["slug"],rel) if lang!="en" else rel
        rt = fix_em(rel_a.get("title",rel["title"]))[:65]
        rel_html += f'<a href="{pfx}/blog/{rel["slug"]}/" class="card" style="text-decoration:none"><img src="{art_img(rel["slug"])}" alt="{rt}" class="card-img" loading="lazy" onerror="this.src=' + chr(39) + IMGS["surf3"] + chr(39) + f'"><div class="card-body"><span class="cat-badge">{rel.get("category","")}</span><h3 class="card-h3" style="font-size:15px;margin-top:8px">{rt}</h3></div></a>'

    CTA_RDY = {"en":"Ready to Ride? Book at Ngor Surfcamp.","fr":"Prêt à Surfer ? Réservez au Ngor Surfcamp.","es":"Listo para Surfear? Reserva en Ngor Surfcamp.","it":"Pronto a Surfare? Prenota al Ngor Surfcamp.","de":"Bereit? Buche im Ngor Surfcamp."}
    CTA_LOC = {"en":"Ngor Island, Dakar, Senegal. WhatsApp: +221 78 925 70 25","fr":"Île de Ngor, Dakar, Sénégal. WhatsApp : +221 78 925 70 25","es":"Isla de Ngor, Dakar, Senegal. WhatsApp: +221 78 925 70 25","it":"Isola di Ngor, Dakar, Senegal. WhatsApp: +221 78 925 70 25","de":"Ngor Island, Dakar, Senegal. WhatsApp: +221 78 925 70 25"}

    html = head(title[:60], meta_d, canonical(f"/blog/{en_slug}",lang), hreflang(f"/blog/{en_slug}"), lang, img)
    html += nav_html("blog", lang, pfx, f"/blog/{en_slug}")
    html += f"""
<main>
  <article itemscope itemtype="https://schema.org/BlogPosting">
    <header class="article-hero" style="background-image:url('{img}')" aria-label="{title}">
      <div class="art-hero-inner">
        <p style="margin-bottom:12px"><span class="cat-badge">{cat}</span></p>
        <h1 style="font-size:clamp(22px,4vw,52px);margin-bottom:0;text-shadow:0 2px 16px rgba(0,0,0,0.3)" itemprop="headline">{title}</h1>
        <meta itemprop="publisher" content="Ngor Surfcamp Teranga">
      </div>
    </header>

    <div class="container" style="padding:48px 24px 80px">
      {breadcrumb}

      <div class="art-lang-bar">
        <span class="lbl">{LANG_L[lang]}</span>
        {lang_pills}
      </div>

      {author_card}

      <div class="prose" itemprop="articleBody">
        {content}
      </div>

      <div class="art-cta">
        <div style="position:relative;z-index:1">
          <h2 style="font-size:24px;margin-bottom:10px">{CTA_RDY[lang]}</h2>
          <p style="opacity:0.82;margin-bottom:28px;max-width:480px;margin-left:auto;margin-right:auto;font-size:15px">{CTA_LOC[lang]}</p>
          <div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap">
            <a href="{pfx}/booking/" class="btn btn-fire btn-lg">{BOOK[lang]}</a>
            <a href="https://wa.me/221789257025" target="_blank" rel="noopener" class="btn btn-glass btn-lg">
              <span style="width:18px;height:18px;display:inline-flex">{ICO['wa']}</span> WhatsApp
            </a>
          </div>
        </div>
      </div>

      {f'<div style="margin-top:60px"><h2 style="font-size:21px;margin-bottom:22px">{REL[lang]}</h2><div class="related-grid">{rel_html}</div></div>' if rel_html else ""}

      <div style="margin-top:48px">
        <a href="{pfx}/blog/" class="btn btn-deep" style="display:inline-flex;align-items:center;gap:8px">
          <span style="width:16px;height:16px;display:inline-flex;transform:scaleX(-1)">{ICO['arrow']}</span>
          {BACK[lang]}
        </a>
      </div>
    </div>
  </article>
</main>"""
    html += footer_html(lang, pfx)
    html += close_page()
    return html

# ════════════════════════════════════════════════════════════════════════════════
# BLOG LISTING
# ════════════════════════════════════════════════════════════════════════════════
def build_blog(lang):
    pfx   = LANG_PREFIX[lang]
    TITLE = {"en":"Surf Blog","fr":"Blog Surf","es":"Blog Surf","it":"Blog Surf","de":"Surf-Blog"}
    SUB   = {"en":"Guides, tips and stories from Ngor Island, Dakar","fr":"Guides, conseils et histoires de l'Île de Ngor, Dakar","es":"Guías, consejos e historias de la Isla de Ngor, Dakar","it":"Guide, consigli e storie dall'Isola di Ngor, Dakar","de":"Guides, Tipps und Geschichten von Ngor Island, Dakar"}
    META  = {"en":"Ngor Surfcamp Teranga surf blog. Expert guides, surf tips and stories from Ngor Island, Dakar, Senegal.","fr":"Blog surf du Ngor Surfcamp Teranga. Guides experts, conseils surf et histoires de l'île de Ngor, Dakar, Sénégal.","es":"Blog surf de Ngor Surfcamp Teranga. Guías de expertos, consejos surf e historias de la isla de Ngor, Dakar, Senegal.","it":"Blog surf di Ngor Surfcamp Teranga. Guide di esperti, consigli surf e storie dall'isola di Ngor, Dakar, Senegal.","de":"Surf-Blog von Ngor Surfcamp Teranga. Expertenguides, Surf-Tipps und Geschichten von Ngor Island, Dakar, Senegal."}
    ALL   = {"en":"All","fr":"Tous","es":"Todos","it":"Tutti","de":"Alle"}

    cat_btns = f'<button class="btn btn-fire btn-sm" onclick="filterCat(' + chr(39) + 'all' + chr(39) + ')" id="cat-all">{ALL[lang]}</button>\n'
    for c in cats:
        s = c["slug"]; n = c["name"]
        cat_btns += f'<button class="btn btn-deep btn-sm" onclick="filterCat(' + chr(39) + s + chr(39) + ')" id="cat-' + s + '">' + n + '</button>\n'

    cards = ""
    for en_art in arts_en:
        en_slug  = en_art["slug"]
        art      = arts_by_lang[lang].get(en_slug, en_art) if lang!="en" else en_art
        t        = fix_em(art.get("title", en_art["title"]))[:80]
        m        = fix_em(art.get("meta_description",""))[:120]
        cat_name = en_art.get("category","")
        cat_slug = next((c["slug"] for c in cats if c["name"]==cat_name), "misc")
        feat     = "★ " if en_art.get("type")=="hero" else ""
        cards += f"""<a href="{pfx}/blog/{en_slug}/" class="card" data-cat="{cat_slug}" style="text-decoration:none" aria-label="{t}">
      <img src="{art_img(en_slug)}" alt="{t}" class="card-img" loading="lazy" onerror="this.src='{IMGS['surf3']}'">
      <div class="card-body">
        <span class="cat-badge">{cat_name}</span>
        <h2 class="card-h3" style="font-size:16px;margin:10px 0">{feat}{t}</h2>
        <p class="card-text">{m}</p>
      </div>
    </a>\n"""

    html = head(f"Blog | {TITLE[lang]} | Ngor Surfcamp Teranga", META[lang], canonical("/blog",lang), hreflang("/blog"), lang)
    html += nav_html("blog", lang, pfx, "/blog")
    html += f"""
<main>
  <header class="page-header" style="background-image:url('{IMGS['surf3']}')" role="banner">
    <h1>{TITLE[lang]}</h1>
    <p>{SUB[lang]}</p>
  </header>
  <div style="background:#f9fafb;padding:18px 0;border-bottom:1px solid #e5e7eb">
    <div class="container" style="display:flex;gap:10px;flex-wrap:wrap;align-items:center">
      {cat_btns}
    </div>
  </div>
  <section class="section" aria-label="Articles">
    <div class="container">
      <div class="blog-grid" id="blog-grid">{cards}</div>
    </div>
  </section>
</main>
<script>
function filterCat(cat){{
  document.querySelectorAll('[id^="cat-"]').forEach(b=>b.className='btn btn-deep btn-sm');
  document.getElementById('cat-'+cat).className='btn btn-fire btn-sm';
  document.querySelectorAll('#blog-grid .card').forEach(c=>{{
    c.style.display=(cat==='all'||c.dataset.cat===cat)?'':'none';
  }});
}}
</script>"""
    html += footer_html(lang, pfx)
    html += close_page()
    return html

# ════════════════════════════════════════════════════════════════════════════════
# WRITE ALL FILES + DEPLOY
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

print("\nBuilding all pages...")
for lang in LANGS:
    pfx  = LANG_PREFIX[lang]
    spfx = f"/{lang}" if lang!="en" else ""
    write(f"{spfx}/", build_homepage(lang))
    write(f"{spfx}/blog/", build_blog(lang))
    for en_art in arts_en:
        write(f"{spfx}/blog/{en_art['slug']}/", build_article(en_art, lang))
    print(f"  ✅ {lang}: home + blog + {len(arts_en)} articles")

print(f"\nTotal HTML: {total} files")
print("✅ v4 build complete")
