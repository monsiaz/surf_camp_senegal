"""
Site v3 — Full rebuild with:
- Homepage background video (Wix CDN)
- Real SVG country flags (not emoji)
- Author personas with photos + tooltip
- Article visual blocks (pull quotes, tip boxes, stat cards, highlights)
- Zero em dashes
- Responsive, polished DA
"""
import json, os, re, shutil

CONTENT  = "/Users/simonazoulay/SurfCampSenegal/content"
ARTICLES = f"{CONTENT}/articles"
PAGES_D  = f"{CONTENT}/pages"
AUTHORS_F= f"{CONTENT}/authors/authors.json"
DEMO_DIR = "/Users/simonazoulay/SurfCampSenegal/cloudflare-demo"
SITE_URL = "https://ngor-surfcamp-demo.pages.dev"

WIX = "https://static.wixstatic.com/media"
VIDEO_BASE = "https://video.wixstatic.com/video/df99f9_da0cf7c72b1a4606bcfa1f7c8e089dc4"
VIDEO_POSTER = f"{WIX}/df99f9_da0cf7c72b1a4606bcfa1f7c8e089dc4f000.jpg"

LANGS       = ["en","fr","es","it","de"]
LANG_NAMES  = {"en":"English","fr":"Français","es":"Español","it":"Italiano","de":"Deutsch"}
LANG_LOCALE = {"en":"en","fr":"fr-FR","es":"es-ES","it":"it-IT","de":"de-DE"}
LANG_PREFIX = {"en":"","fr":"/fr","es":"/es","it":"/it","de":"/de"}

LOGO = f"{WIX}/c2467f_a31779010ce34c4c8c61cc5868d81f31~mv2.png"
IMGS = {
    "home":   VIDEO_POSTER,
    "house":  f"{WIX}/df99f9_2ec6248367cd4e21a5e6c26c2b0a1c35~mv2.jpg",
    "island": f"{WIX}/df99f9_56b9af6efe2841eea44109b3b08b7da1~mv2.jpg",
    "surf":   f"{WIX}/11062b_89a070321f814742a620b190592d51ad~mv2.jpg",
    "surf2":  f"{WIX}/df99f9_dd89cc4d86d4402189d7e9516ce672a3~mv2.jpg",
    "surf3":  f"{WIX}/df99f9_961b0768e713457f93025f4ce6fb1419~mv2.jpg",
    "house2": f"{WIX}/df99f9_eba4c24ec6a746b58d60a975b8d20946~mv2.jpg",
    "house3": f"{WIX}/df99f9_d8e77cf4807249f6953119f18be64166~mv2.jpg",
    "food":   f"{WIX}/df99f9_753890483d8e4cca8e2051a13f9c558e~mv2.jpg",
    "pool":   f"{WIX}/df99f9_a18d512828d9487e9a4987b9903960e0~mv2.jpg",
    "sunset": f"{WIX}/df99f9_d6e404dd3cf74396b6ea874cb7021a27~mv2.jpg",
    "art":    f"{WIX}/df99f9_d81668a18a9d49d1b5ebb0ea3a0abbc7~mv2.jpg",
    "island2":f"{WIX}/b28af82dbec544138f16e2bc5a85f2cb.jpg",
    "ngor_r": f"{WIX}/11062b_7f89d2db0ace4027ac4a00928a6aca08~mv2.jpg",
    "review": f"{WIX}/11062b_772a661c20f742c7baca38ad28c5f7fc~mv2.jpeg",
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

def load(p):
    if os.path.exists(p):
        try:
            with open(p) as f: return json.load(f)
        except: return None
    return None

# ── Load data ─────────────────────────────────────────────────────────────────
strategy = load(f"{CONTENT}/blog_strategy.json")
cats      = strategy["categories"]
authors   = load(AUTHORS_F) or {}

# Map categories to authors
CAT_AUTHOR = {}
for aid, a in authors.items():
    for cat in a.get("categories", []):
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

print(f"Articles: { {l: len(arts_by_lang[l]) for l in LANGS} }")
print(f"Authors: {list(authors.keys())}")

# ════════════════════════════════════════════════════════════════════════════════
# FLAG SVGs (clean minimal, matches DA)
# ════════════════════════════════════════════════════════════════════════════════
FLAG_SVGS = {
    "en": """<svg viewBox="0 0 60 40" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="English">
  <rect width="60" height="40" fill="#012169"/>
  <path d="M0,0 L60,40 M60,0 L0,40" stroke="#fff" stroke-width="8"/>
  <path d="M0,0 L60,40 M60,0 L0,40" stroke="#C8102E" stroke-width="5"/>
  <path d="M30,0 V40 M0,20 H60" stroke="#fff" stroke-width="12"/>
  <path d="M30,0 V40 M0,20 H60" stroke="#C8102E" stroke-width="8"/>
</svg>""",
    "fr": """<svg viewBox="0 0 60 40" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Français">
  <rect width="20" height="40" fill="#002395"/>
  <rect x="20" width="20" height="40" fill="#fff"/>
  <rect x="40" width="20" height="40" fill="#ED2939"/>
</svg>""",
    "es": """<svg viewBox="0 0 60 40" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Español">
  <rect width="60" height="40" fill="#c60b1e"/>
  <rect y="10" width="60" height="20" fill="#ffc400"/>
  <rect y="0" width="60" height="7" fill="#c60b1e"/>
  <rect y="33" width="60" height="7" fill="#c60b1e"/>
</svg>""",
    "it": """<svg viewBox="0 0 60 40" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Italiano">
  <rect width="20" height="40" fill="#009246"/>
  <rect x="20" width="20" height="40" fill="#fff"/>
  <rect x="40" width="20" height="40" fill="#CE2B37"/>
</svg>""",
    "de": """<svg viewBox="0 0 60 40" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Deutsch">
  <rect width="60" height="14" fill="#000"/>
  <rect y="13" width="60" height="14" fill="#DD0000"/>
  <rect y="26" width="60" height="14" fill="#FFCE00"/>
</svg>""",
}

def flag_icon(lang, size=24):
    svg = FLAG_SVGS.get(lang, "")
    return f'<span class="flag-icon" style="width:{size}px;height:{round(size*0.667)}px;display:inline-flex;border-radius:3px;overflow:hidden;flex-shrink:0;box-shadow:0 1px 3px rgba(0,0,0,0.2)">{svg}</span>'

# ════════════════════════════════════════════════════════════════════════════════
# SVG ICONS
# ════════════════════════════════════════════════════════════════════════════════
ICONS = {
    "wa": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>',
    "ig": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>',
    "tt": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M19.59 6.69a4.83 4.83 0 01-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 01-2.88 2.5 2.89 2.89 0 01-2.89-2.89 2.89 2.89 0 012.89-2.89c.28 0 .54.04.79.1V9.01a6.28 6.28 0 00-.79-.05 6.34 6.34 0 00-6.34 6.34 6.34 6.34 0 006.34 6.34 6.34 6.34 0 006.33-6.34V8.69a8.22 8.22 0 004.84 1.56V6.79a4.85 4.85 0 01-1.07-.1z"/></svg>',
    "menu": '<svg viewBox="0 0 24 24" fill="none"><path d="M3 7h18M3 12h18M3 17h12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
    "arrow": '<svg viewBox="0 0 24 24" fill="none"><path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "check": '<svg viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>',
    "quote": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M11.3 7H7c-.6 0-1 .4-1 1v4c0 .6.4 1 1 1h2.3l-1.7 3.4c-.2.4.1.6.4.6H9c.2 0 .4-.1.5-.3L11.8 13c.1-.2.2-.5.2-.7V8c0-.6-.3-1-.7-1zm8 0H15c-.6 0-1 .4-1 1v4c0 .6.4 1 1 1h2.3l-1.7 3.4c-.2.4.1.6.4.6H17c.2 0 .4-.1.5-.3L19.8 13c.1-.2.2-.5.2-.7V8c0-.6-.3-1-.7-1z"/></svg>',
    "lightbulb": '<svg viewBox="0 0 24 24" fill="none"><path d="M9 21h6M12 3a6 6 0 00-3 11.2V17a1 1 0 001 1h4a1 1 0 001-1v-2.8A6 6 0 0012 3z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "info": '<svg viewBox="0 0 24 24" fill="currentColor"><path fill-rule="evenodd" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z" clip-rule="evenodd"/></svg>',
    "wave": '<svg viewBox="0 0 40 16" fill="none"><path d="M0 10 C5 6,10 3,15 6 C20 9,25 12,30 7 C35 3,38 6,40 4 L40 16 L0 16Z" fill="currentColor" opacity="0.7"/><path d="M0 13 C8 9,15 12,20 11 C25 10,32 7,40 10 L40 16 L0 16Z" fill="currentColor"/></svg>',
}

def ico(name, size=20, cls=""):
    svg = ICONS.get(name,"")
    return f'<span class="svg-icon {cls}" style="width:{size}px;height:{size}px;display:inline-flex;align-items:center;justify-content:center;flex-shrink:0">{svg}</span>'

# ════════════════════════════════════════════════════════════════════════════════
# ARTICLE MARKDOWN → HTML with Visual Blocks
# ════════════════════════════════════════════════════════════════════════════════
BLOCK_COUNTER = [0]  # track section count for alternating

def md2html_rich(md):
    """Convert markdown to rich HTML with visual blocks."""
    if not md: return ""

    # Pre-process: remove em dashes
    md = md.replace(" — ", ", ").replace("—", ",").replace(" – ", ", ").replace("–", ",")

    lines  = md.split("\n")
    html   = []
    in_ul  = in_ol = False
    section_count = [0]

    def close_lists():
        nonlocal in_ul, in_ol
        if in_ul: html.append("</ul>"); in_ul = False
        if in_ol: html.append("</ol>"); in_ol = False

    def inline(text):
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'__(.*?)__', r'<strong>\1</strong>', text)
        text = re.sub(r'(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)', r'<em>\1</em>', text)
        # Internal links [LINK: text → /slug]
        def ilink(m):
            parts = m.group(0)[6:-1].split("→")
            anchor = parts[0].strip()
            target = parts[1].strip() if len(parts) > 1 else "#"
            return f'<a href="{target}/" class="ilink">{ico("arrow",14)} {anchor}</a>'
        text = re.sub(r'\[LINK:[^\]]+\]', ilink, text)
        return text

    i = 0
    while i < len(lines):
        line     = lines[i]
        stripped = line.strip()

        if not stripped:
            close_lists()
            i += 1; continue

        # Headings
        if stripped.startswith("### "):
            close_lists(); html.append(f"<h3>{inline(stripped[4:])}</h3>")
        elif stripped.startswith("## "):
            close_lists()
            section_count[0] += 1
            heading_text = inline(stripped[3:])
            html.append(f'<h2>{heading_text}</h2>')
        elif stripped.startswith("# "):
            close_lists(); html.append(f"<h1>{inline(stripped[2:])}</h1>")
        elif stripped.startswith("#### "):
            close_lists(); html.append(f"<h4>{inline(stripped[5:])}</h4>")

        # Lists
        elif re.match(r'^[-*]\s', stripped):
            if not in_ul: html.append('<ul class="prose-list">'); in_ul = True
            if in_ol: html.append("</ol>"); in_ol = False
            html.append(f"<li>{inline(stripped[2:])}</li>")
        elif re.match(r'^\d+\.\s', stripped):
            if not in_ol: html.append('<ol class="prose-list">'); in_ol = True
            if in_ul: html.append("</ul>"); in_ul = False
            item_text = re.sub(r'^\d+\.\s', '', stripped)
            html.append(f"<li>{inline(item_text)}</li>")

        # Blockquote / pull quote
        elif stripped.startswith(">"):
            close_lists()
            qt = stripped[1:].strip()
            html.append(f'''<div class="pull-quote">
  <div class="pq-mark">{ico("quote",28)}</div>
  <blockquote class="pq-text">{inline(qt)}</blockquote>
</div>''')

        # Special blocks via **TIP:**, **NOTE:**, **DID YOU KNOW**
        elif stripped.upper().startswith("**TIP:") or stripped.upper().startswith("**CONSEIL:") or stripped.upper().startswith("**TIPP:") or stripped.upper().startswith("**CONSEJO:") or stripped.upper().startswith("**CONSIGLIO:"):
            close_lists()
            content_text = re.sub(r'^\*\*[^:]+:\*?\*?\s*', '', stripped)
            tip_label = "Tip" if stripped[:4].upper() == "**TI" else "Conseil" if stripped[:5].upper() == "**CON" else "Tipp" if stripped[:5].upper() == "**TIP" else "Consejo"
            html.append(f'''<div class="visual-block tip-block">
  <div class="vb-icon">{ico("lightbulb",20)}</div>
  <div><span class="vb-label">{tip_label}</span><p>{inline(content_text)}</p></div>
</div>''')

        elif stripped.upper().startswith("**NOTE:") or stripped.upper().startswith("**REMARQUE:") or stripped.upper().startswith("**HINWEIS:") or stripped.upper().startswith("**NOTA:"):
            close_lists()
            content_text = re.sub(r'^\*\*[^:]+:\*?\*?\s*', '', stripped)
            html.append(f'''<div class="visual-block note-block">
  <div class="vb-icon">{ico("info",20)}</div>
  <div><span class="vb-label">Note</span><p>{inline(content_text)}</p></div>
</div>''')

        # **Bold heading** standalone lines (FAQ style)
        elif stripped.startswith("**") and stripped.endswith("**") and stripped.count("**") == 2:
            close_lists()
            heading_text = stripped.strip("*")
            if heading_text.endswith("?"):
                html.append(f'<h4 class="faq-q-inline">{heading_text}</h4>')
            else:
                html.append(f'<h4 class="prose-h4">{heading_text}</h4>')

        # Regular paragraphs
        else:
            close_lists()
            p_text = inline(stripped)
            if p_text:
                # Detect stat callout: short line with big number
                if re.match(r'^[\d,+%\s]{1,8}$', stripped.strip()):
                    html.append(f'<div class="stat-inline">{stripped}</div>')
                # Detect pull quote (starts with opening quote character)
                elif stripped.startswith('"') and stripped.endswith('"') and len(stripped) > 40:
                    html.append(f'''<div class="pull-quote mini">
  <blockquote class="pq-text">{p_text}</blockquote>
</div>''')
                else:
                    html.append(f"<p>{p_text}</p>")
        i += 1

    close_lists()
    return "\n".join(html)

# ════════════════════════════════════════════════════════════════════════════════
# CSS ADDITIONS for Visual Blocks + Author + Video + Flags
# ════════════════════════════════════════════════════════════════════════════════
CSS_ADDITIONS = """
/* ── Video Hero ─────────────────────────────────────────────────────────── */
.hero-video-wrap {
  position: absolute; inset: 0; z-index: 0; overflow: hidden;
}
.hero-video-wrap video {
  width: 100%; height: 100%; object-fit: cover;
  opacity: 0.7;
}
.hero-video-wrap::after {
  content: '';
  position: absolute; inset: 0;
  background: linear-gradient(170deg, rgba(10,37,64,0.6) 0%, rgba(10,37,64,0.3) 50%, rgba(0,0,0,0.65) 100%);
}

/* ── Flag Icons ──────────────────────────────────────────────────────────── */
.flag-icon { display: inline-flex; border-radius: 3px; overflow: hidden; flex-shrink: 0; box-shadow: 0 1px 4px rgba(0,0,0,0.25); }
.lang-option { display: flex; align-items: center; gap: 8px; }
.lang-select-styled {
  appearance: none;
  background: rgba(255,255,255,0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.2);
  color: #fff;
  padding: 7px 32px 7px 12px;
  border-radius: 10px;
  font-size: 13px;
  cursor: pointer;
  outline: none;
  font-family: inherit;
}
.lang-select-styled option { background: #0a2540; }

/* ── Author Card ─────────────────────────────────────────────────────────── */
.author-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 20px 24px;
  background: #f9fafb;
  border-radius: 14px;
  border: 1px solid #e5e7eb;
  margin: 40px 0;
  position: relative;
}
.author-avatar {
  width: 64px; height: 64px; border-radius: 50%;
  object-fit: cover; flex-shrink: 0;
  border: 3px solid #fff;
  box-shadow: 0 2px 12px rgba(10,37,64,0.15);
}
.author-avatar-placeholder {
  width: 64px; height: 64px; border-radius: 50%;
  background: linear-gradient(135deg, #0a2540, #1a4a7a);
  display: flex; align-items: center; justify-content: center;
  color: #f0d6a4; font-size: 24px; font-weight: 700;
  flex-shrink: 0;
}
.author-name { font-weight: 700; font-size: 16px; color: #0a2540; }
.author-role { font-size: 13px; color: #ff6b35; font-weight: 600; margin-top: 2px; }
.author-bio { font-size: 13px; color: #6b7280; margin-top: 4px; line-height: 1.6; }

/* Author tooltip */
.author-tooltip-wrap { position: relative; cursor: pointer; }
.author-tooltip {
  position: absolute; bottom: calc(100% + 12px); left: 0;
  background: #0a2540; color: #fff;
  padding: 16px 18px; border-radius: 12px;
  font-size: 13px; line-height: 1.6;
  width: 280px; z-index: 50;
  box-shadow: 0 8px 32px rgba(10,37,64,0.3);
  opacity: 0; pointer-events: none;
  transform: translateY(6px);
  transition: opacity 0.2s, transform 0.2s;
}
.author-tooltip::after {
  content: '';
  position: absolute; top: 100%; left: 24px;
  border: 8px solid transparent;
  border-top-color: #0a2540;
}
.author-tooltip-wrap:hover .author-tooltip,
.author-tooltip-wrap:focus-within .author-tooltip {
  opacity: 1; pointer-events: auto; transform: translateY(0);
}

/* ── Article Visual Blocks ───────────────────────────────────────────────── */
.visual-block {
  display: flex; gap: 14px; align-items: flex-start;
  padding: 20px 24px;
  border-radius: 12px;
  margin: 28px 0;
}
.visual-block p { margin: 0; font-size: 15.5px; }
.vb-icon {
  width: 40px; height: 40px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.vb-label {
  font-size: 11px; font-weight: 800; letter-spacing: 0.1em;
  text-transform: uppercase; display: block; margin-bottom: 6px;
}

.tip-block {
  background: linear-gradient(135deg, rgba(255,107,53,0.08), rgba(255,107,53,0.04));
  border: 1px solid rgba(255,107,53,0.2);
  border-left: 4px solid #ff6b35;
}
.tip-block .vb-icon { background: rgba(255,107,53,0.1); color: #ff6b35; }
.tip-block .vb-label { color: #ff6b35; }

.note-block {
  background: linear-gradient(135deg, rgba(10,37,64,0.04), rgba(10,37,64,0.02));
  border: 1px solid rgba(10,37,64,0.12);
  border-left: 4px solid #0a2540;
}
.note-block .vb-icon { background: rgba(10,37,64,0.08); color: #0a2540; }
.note-block .vb-label { color: #0a2540; }

/* Pull quote */
.pull-quote {
  position: relative;
  padding: 28px 32px;
  margin: 36px 0;
  background: linear-gradient(135deg, rgba(240,214,164,0.2), rgba(240,214,164,0.08));
  border-radius: 16px;
  border-left: 5px solid #f0d6a4;
}
.pull-quote .pq-mark {
  position: absolute; top: 16px; right: 20px;
  opacity: 0.15; color: #0a2540;
}
.pull-quote.mini { padding: 20px 24px; }
.pq-text {
  font-size: 19px; font-style: italic; line-height: 1.7;
  color: #0a2540; font-family: 'Raleway', sans-serif;
  font-weight: 600;
  margin: 0; border: none; padding: 0; background: none;
}

/* Stat inline */
.stat-inline {
  font-size: 48px; font-weight: 900;
  color: #ff6b35;
  font-family: 'Raleway', sans-serif;
  text-align: center; margin: 24px 0;
  line-height: 1;
}

/* FAQ inline */
.faq-q-inline {
  font-size: 17px; font-weight: 700; color: #0a2540;
  margin: 28px 0 10px; padding-left: 12px;
  border-left: 3px solid #ff6b35;
}

/* Prose lists */
.prose-list { margin: 16px 0 24px 20px; }
.prose-list li {
  font-size: 16.5px; line-height: 1.7; color: #374151; margin-bottom: 10px;
}
.prose-list li::marker { color: #ff6b35; }

/* Internal link styling */
.ilink {
  color: #ff6b35 !important; font-weight: 600;
  border-bottom: 1px solid rgba(255,107,53,0.3);
  display: inline-flex; align-items: center; gap: 4px;
  transition: border-color 0.2s;
}
.ilink:hover { border-bottom-color: #ff6b35; }

/* ── Language bar on articles ────────────────────────────────────────────── */
.article-lang-bar {
  display: flex; gap: 8px; flex-wrap: wrap;
  align-items: center; margin-bottom: 36px;
  padding: 14px 18px;
  background: #f9fafb;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
}
.article-lang-bar span {
  font-size: 11.5px; color: #9ca3af; text-transform: uppercase;
  letter-spacing: 0.08em; margin-right: 6px;
}
.lang-btn {
  display: inline-flex; align-items: center; gap: 7px;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 12.5px; font-weight: 600;
  background: #fff; border: 1px solid #e5e7eb;
  color: #374151; cursor: pointer; transition: all 0.2s;
  text-decoration: none;
}
.lang-btn:hover { background: #0a2540; color: #fff; border-color: #0a2540; }
.lang-btn.active { background: #0a2540; color: #fff; border-color: #0a2540; }

/* ── Related articles ────────────────────────────────────────────────────── */
.related-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 20px;
  margin-top: 16px;
}

/* Nav flag pill */
.nav-lang-btn {
  display: inline-flex; align-items: center; gap: 7px;
  padding: 6px 12px; border-radius: var(--radius-pill);
  background: var(--glass-bg-mid);
  backdrop-filter: blur(12px);
  border: 1px solid var(--glass-border);
  color: #fff; font-size: 13px; font-weight: 500;
  cursor: pointer; transition: var(--t);
}
.nav-lang-btn:hover { background: var(--glass-bg-high); }

/* ── Section image callout ───────────────────────────────────────────────── */
.img-callout {
  border-radius: 16px; overflow: hidden;
  position: relative; margin: 36px 0;
}
.img-callout img { width: 100%; height: 280px; object-fit: cover; }
.img-callout-cap {
  position: absolute; bottom: 0; left: 0; right: 0;
  padding: 16px 20px;
  background: linear-gradient(transparent, rgba(10,37,64,0.8));
  color: rgba(255,255,255,0.85); font-size: 13px; font-style: italic;
}

@media (max-width: 640px) {
  .related-grid { grid-template-columns: 1fr; }
  .pull-quote { padding: 20px; }
  .author-card { flex-direction: column; text-align: center; }
  .author-tooltip { left: 50%; transform: translateX(-50%) translateY(6px); }
  .author-tooltip-wrap:hover .author-tooltip { transform: translateX(-50%) translateY(0); }
}
"""

# Append to existing CSS
with open(f"{DEMO_DIR}/assets/css/style.css", "a") as f:
    f.write(CSS_ADDITIONS)
print("✅ CSS v3 additions written")

# ════════════════════════════════════════════════════════════════════════════════
# JAVASCRIPT ADDITIONS
# ════════════════════════════════════════════════════════════════════════════════
I18N_JS = """<script>
const LANGS = ['en','fr','es','it','de'];
const LANG_STORAGE = 'ngor_lang';

function getLang(){ return localStorage.getItem(LANG_STORAGE) || document.documentElement.lang || 'en'; }

function setLang(l){
  if(!LANGS.includes(l)) return;
  localStorage.setItem(LANG_STORAGE, l);
  document.documentElement.lang = l;
  document.querySelectorAll('[data-lang]').forEach(el => {
    el.style.display = el.getAttribute('data-lang') === l ? '' : 'none';
  });
  document.getElementById('lang-sel') && (document.getElementById('lang-sel').value = l);
}

document.addEventListener('DOMContentLoaded', () => {
  // Scroll reveal
  const obs = new IntersectionObserver(es => es.forEach(e => {
    if(e.isIntersecting){ e.target.classList.add('up'); }
  }), {threshold: 0.08});
  document.querySelectorAll('.reveal').forEach(el => obs.observe(el));

  // Nav scroll effect
  const nav = document.getElementById('nav');
  if(nav) window.addEventListener('scroll', () => nav.classList.toggle('scrolled', scrollY > 30), {passive:true});

  // FAQ
  document.querySelectorAll('.faq-q').forEach(q => {
    q.addEventListener('click', () => {
      const item = q.closest('.faq-item');
      item.classList.toggle('open');
      item.classList.toggle('closed');
    });
  });

  // Gallery lightbox
  const lb = document.getElementById('lb');
  const lbImg = document.getElementById('lb-img');
  const lbClose = document.getElementById('lb-close');
  if(lb){
    document.querySelectorAll('.gallery-item').forEach(item => {
      item.addEventListener('click', () => {
        lbImg.src = item.querySelector('img').src;
        lb.classList.add('open');
      });
    });
    lb.addEventListener('click', e => { if(e.target === lb) lb.classList.remove('open'); });
    lbClose && lbClose.addEventListener('click', () => lb.classList.remove('open'));
  }

  // Mobile nav
  document.getElementById('nav-toggle') && document.getElementById('nav-toggle').addEventListener('click', () => {
    document.getElementById('nav-links').classList.toggle('open');
  });

  // Booking form → WhatsApp
  const form = document.getElementById('booking-form');
  if(form){
    form.addEventListener('submit', function(e){
      e.preventDefault();
      const fname = (this.querySelector('.f-name') || {}).value || '';
      const level = (this.querySelector('.f-level') || {}).value || '';
      const msg = encodeURIComponent('Hello Ngor Surfcamp! I would like to book a stay. Name: ' + fname + (level ? '. Level: ' + level : '') + '. Please send me availability and prices.');
      window.open('https://wa.me/221789257025?text=' + msg, '_blank');
    });
  }

  // Video autoplay muted fallback
  const vid = document.getElementById('hero-video');
  if(vid){
    vid.play().catch(() => { vid.style.display = 'none'; });
  }

  // Lang select
  const sel = document.getElementById('lang-sel');
  if(sel){
    sel.value = getLang();
    sel.addEventListener('change', e => setLang(e.target.value));
  }
  setLang(getLang());
});

function toggleMenu(){
  document.getElementById('nav-links').classList.toggle('open');
}
</script>"""

# ════════════════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════════════════
def fix_em(text):
    if not text: return text
    text = text.replace(" — ", ", ").replace("—", ",").replace("\u2014",",")
    text = text.replace(" – ", ", ").replace("–",",").replace("\u2013",",")
    return re.sub(r',\s*,', ',', text)

def art_img(en_slug):
    local = f"/assets/images/{en_slug}.png"
    if os.path.exists(f"{DEMO_DIR}{local}"):
        return local
    return IMGS["surf3"]

def author_for(art):
    cat = art.get("category","")
    aid = CAT_AUTHOR.get(cat, "kofi-mensah")
    return authors.get(aid, {})

def author_card_html(art, lang):
    a     = author_for(art)
    if not a: return ""
    aid   = a.get("id","")
    name  = a.get("name","")
    role  = a.get("role",{}).get(lang, a.get("role",{}).get("en",""))
    bio   = a.get("bio",{}).get(lang, a.get("bio",{}).get("en",""))[:200]
    img_local = f"/assets/images/author-{aid}.jpg"
    img_exists = os.path.exists(f"{DEMO_DIR}{img_local}")
    img_tag = f'<img src="{img_local}" alt="{name}" class="author-avatar" loading="lazy">' if img_exists else f'<div class="author-avatar-placeholder">{name[0]}</div>'
    WRITTEN = {"en":"Written by","fr":"Écrit par","es":"Escrito por","it":"Scritto da","de":"Geschrieben von"}
    return f"""<div class="author-card reveal">
  <div class="author-tooltip-wrap">
    {img_tag}
    <div class="author-tooltip">{bio}</div>
  </div>
  <div>
    <div style="font-size:11px;color:#9ca3af;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:4px">{WRITTEN.get(lang,'Written by')}</div>
    <div class="author-name">{name}</div>
    <div class="author-role">{role}</div>
  </div>
</div>"""

def hreflang_tags(page_slug):
    slug = "/" + page_slug.strip("/") if page_slug.strip("/") else ""
    tags = [
        f'<link rel="alternate" hreflang="x-default" href="{SITE_URL}{slug}/">',
        f'<link rel="alternate" hreflang="en" href="{SITE_URL}{slug}/">',
    ]
    for l in ["fr","es","it","de"]:
        tags.append(f'<link rel="alternate" hreflang="{LANG_LOCALE[l]}" href="{SITE_URL}/{l}{slug}/">')
    return "\n  ".join(tags)

def canonical_tag(page_slug, lang):
    slug = "/" + page_slug.strip("/") if page_slug.strip("/") else ""
    pfx  = f"/{lang}" if lang != "en" else ""
    return f'<link rel="canonical" href="{SITE_URL}{pfx}{slug}/">'

def head(title, meta_desc, canonical="", hreflang="", lang="en", og_image=""):
    og = og_image or IMGS["home"]
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{fix_em(title)}</title>
<meta name="description" content="{fix_em(meta_desc)}">
<meta property="og:title" content="{fix_em(title)}">
<meta property="og:description" content="{fix_em(meta_desc)}">
<meta property="og:image" content="{og}">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<meta name="robots" content="index,follow">
{canonical}
{hreflang}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Raleway:wght@300;400;500;600;700;800;900&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/css/style.css">
</head>
<body>"""

def nav_html(active, lang, pfx):
    NAV = [
        ("", {"en":"Home","fr":"Accueil","es":"Inicio","it":"Home","de":"Start"}),
        ("/surf-house", {"en":"Surf House","fr":"Surf House","es":"Surf House","it":"Surf House","de":"Surf House"}),
        ("/island", {"en":"Island","fr":"Île","es":"Isla","it":"Isola","de":"Insel"}),
        ("/surfing", {"en":"Surfing","fr":"Surf","es":"Surf","it":"Surf","de":"Surfen"}),
        ("/blog", {"en":"Blog","fr":"Blog","es":"Blog","it":"Blog","de":"Blog"}),
        ("/gallery", {"en":"Gallery","fr":"Galerie","es":"Galería","it":"Galleria","de":"Galerie"}),
        ("/booking", {"en":"Book Now","fr":"Réserver","es":"Reservar","it":"Prenota","de":"Buchen"}),
    ]
    items = ""
    for slug, labels in NAV:
        label = labels.get(lang, labels["en"])
        href  = f"{pfx}{slug}/"
        cls   = "nav-link active" if (slug.strip("/")==active.strip("/") or (not slug and not active)) else "nav-link"
        if slug == "/booking": cls += " nav-cta"
        items += f'<a href="{href}" class="{cls}">{label}</a>\n'

    # Lang selector with flag
    opts = "\n".join([f'<option value="{l}" {"selected" if l==lang else ""}>{LANG_NAMES[l]}</option>' for l in LANGS])

    return f"""<nav id="nav">
  <div class="nav-inner">
    <a href="{pfx}/" class="nav-logo">
      <img src="{LOGO}" alt="Ngor Surfcamp Teranga" width="130" height="44" loading="eager">
    </a>
    <div class="nav-links" id="nav-links">
      {items}
    </div>
    <div class="nav-right">
      <div class="lang-picker" style="position:relative">
        <div style="display:flex;align-items:center;gap:6px">
          {flag_icon(lang, 22)}
          <select id="lang-sel" class="lang-select-styled" aria-label="Select language">
            {opts}
          </select>
        </div>
      </div>
      <a href="https://wa.me/221789257025" target="_blank" rel="noopener" class="nav-wa" aria-label="WhatsApp">
        <span class="svg-icon" style="width:18px;height:18px;display:inline-flex">{ICONS["wa"]}</span>
        <span class="wa-label">WhatsApp</span>
      </a>
      <button class="nav-toggle" id="nav-toggle" aria-label="Menu" onclick="toggleMenu()">
        <span class="svg-icon" style="width:22px;height:22px;display:inline-flex;color:#fff">{ICONS["menu"]}</span>
      </button>
    </div>
  </div>
</nav>"""

def footer_html(lang, pfx):
    PAGES_NAV = [
        ("/surf-house", {"en":"Surf House","fr":"Surf House","es":"Surf House","it":"Surf House","de":"Surf House"}),
        ("/island",     {"en":"Island","fr":"Île de Ngor","es":"Isla de Ngor","it":"Isola di Ngor","de":"Ngor Island"}),
        ("/surfing",    {"en":"Surfing","fr":"Surf","es":"Surf","it":"Surf","de":"Surfen"}),
        ("/blog",       {"en":"Blog","fr":"Blog","es":"Blog","it":"Blog","de":"Blog"}),
        ("/gallery",    {"en":"Gallery","fr":"Galerie","es":"Galería","it":"Galleria","de":"Galerie"}),
        ("/faq",        {"en":"FAQ","fr":"FAQ","es":"FAQ","it":"FAQ","de":"FAQ"}),
        ("/booking",    {"en":"Book Now","fr":"Réserver","es":"Reservar","it":"Prenota","de":"Buchen"}),
    ]
    page_links = "\n".join([f'<a href="{pfx}{s}/">{labels.get(lang,labels["en"])}</a>' for s,labels in PAGES_NAV])
    lang_links = " ".join([
        f'<a href="{"" if l=="en" else "/"+l}/" hreflang="{LANG_LOCALE[l]}" style="display:inline-flex;align-items:center;gap:5px">{flag_icon(l,18)}</a>'
        for l in LANGS
    ])
    ABOUT = {"en":"Premium surf camp on Ngor Island, Dakar, Senegal. All levels welcome. Licensed by the Senegalese Federation of Surfing.","fr":"Surf camp premium sur l'île de Ngor, Dakar, Sénégal. Tous niveaux. Agréé par la Fédération Sénégalaise de Surf.","es":"Surf camp premium en la isla de Ngor, Dakar, Senegal. Todos los niveles. Licenciado por la Federación Senegalesa de Surf.","it":"Surf camp premium sull'isola di Ngor, Dakar, Senegal. Tutti i livelli. Autorizzato dalla Federazione Senegalese di Surf.","de":"Premium Surfcamp auf Ngor Island, Dakar, Senegal. Alle Level willkommen. Lizenziert vom senegalesischen Surfverband."}
    COPY  = {"en":"© 2025 Ngor Surfcamp Teranga. All rights reserved.","fr":"© 2025 Ngor Surfcamp Teranga. Tous droits réservés.","es":"© 2025 Ngor Surfcamp Teranga. Todos los derechos reservados.","it":"© 2025 Ngor Surfcamp Teranga. Tutti i diritti riservati.","de":"© 2025 Ngor Surfcamp Teranga. Alle Rechte vorbehalten."}
    EXP   = {"en":"Explore","fr":"Explorer","es":"Explorar","it":"Esplora","de":"Erkunden"}
    CON   = {"en":"Contact","fr":"Contact","es":"Contacto","it":"Contatti","de":"Kontakt"}
    FOL   = {"en":"Follow Us","fr":"Nous suivre","es":"Síguenos","it":"Seguici","de":"Folgen"}
    BOOK  = {"en":"Book your stay","fr":"Réserver un séjour","es":"Reservar estancia","it":"Prenota soggiorno","de":"Aufenthalt buchen"}

    return f"""<footer>
  <div class="container">
    <div class="footer-grid">
      <div class="footer-brand">
        <img src="{LOGO}" alt="Ngor Surfcamp Teranga" width="120" height="40" loading="lazy">
        <p>{ABOUT[lang]}</p>
        <div class="footer-social" style="margin-top:16px">
          <a href="https://wa.me/221789257025" target="_blank" rel="noopener" class="social-btn wa-btn" aria-label="WhatsApp"><span class="svg-icon" style="width:18px;height:18px;display:inline-flex">{ICONS['wa']}</span></a>
          <a href="https://www.instagram.com/ngorsurfcampteranga" target="_blank" rel="noopener" class="social-btn ig-btn" aria-label="Instagram"><span class="svg-icon" style="width:18px;height:18px;display:inline-flex">{ICONS['ig']}</span></a>
          <a href="https://www.tiktok.com/@ngorsurfcampteranga" target="_blank" rel="noopener" class="social-btn tt-btn" aria-label="TikTok"><span class="svg-icon" style="width:18px;height:18px;display:inline-flex">{ICONS['tt']}</span></a>
        </div>
      </div>
      <div class="footer-col">
        <h4>{EXP[lang]}</h4>
        {page_links}
      </div>
      <div class="footer-col">
        <h4>{CON[lang]}</h4>
        <a href="https://wa.me/221789257025" target="_blank">WhatsApp: +221 78 925 70 25</a>
        <a href="mailto:info@surfcampsenegal.com">info@surfcampsenegal.com</a>
        <a href="{pfx}/booking/">{BOOK[lang]}</a>
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
      <div style="display:flex;gap:8px;align-items:center" aria-label="Language versions">
        {lang_links}
      </div>
    </div>
  </div>
</footer>"""

def close_page():
    return f"\n{I18N_JS}\n</body>\n</html>"

# ════════════════════════════════════════════════════════════════════════════════
# BUILD HOMEPAGE (with video hero)
# ════════════════════════════════════════════════════════════════════════════════
def build_homepage(lang):
    pfx = LANG_PREFIX[lang]
    p   = load(f"{PAGES_D}/{lang}_homepage.json") or {}
    h1  = fix_em(p.get("h1","Ngor Surfcamp Teranga"))
    sub = fix_em(p.get("hero_subtitle","Premium Surfcamp in Senegal"))
    intro = fix_em(p.get("intro",""))
    sections = p.get("sections",[])
    title = fix_em(p.get("title_tag","Surf Camp Senegal | Ngor Surfcamp Teranga"))
    meta  = fix_em(p.get("meta_description","Premium surf camp on Ngor Island, Dakar, Senegal."))

    BOOK = {"en":"Book Your Stay","fr":"Réserver","es":"Reservar","it":"Prenota","de":"Jetzt buchen"}
    DISC = {"en":"Discover","fr":"Découvrir","es":"Descubrir","it":"Scoprire","de":"Entdecken"}
    MORE = {"en":"Learn More","fr":"En savoir plus","es":"Saber más","it":"Scopri di più","de":"Mehr erfahren"}
    ALL_ART = {"en":"All Articles","fr":"Tous les articles","es":"Todos los artículos","it":"Tutti gli articoli","de":"Alle Artikel"}
    LAT = {"en":"Latest from the Blog","fr":"Derniers articles du Blog","es":"Últimos artículos del Blog","it":"Ultimi articoli dal Blog","de":"Neuestes aus dem Blog"}
    REV_TEXT = {"en":"I had an amazing stay at Ngor Surfcamp Teranga. The coaching was top-notch and I felt my surfing progress significantly.","fr":"Un séjour incroyable au Ngor Surfcamp Teranga. Le coaching était excellent et mes progrès en surf ont été significatifs.","es":"Una estancia increíble en Ngor Surfcamp Teranga. El coaching fue excelente y progresé mucho con el surf.","it":"Un soggiorno incredibile al Ngor Surfcamp Teranga. Il coaching era ottimo e i miei progressi nel surf sono stati significativi.","de":"Ein unglaublicher Aufenthalt im Ngor Surfcamp Teranga. Das Coaching war erstklassig und ich habe erhebliche Fortschritte im Surfen gemacht."}
    ABOUT_H2 = {"en":"Serious about your surfing progression?","fr":"Sérieux dans votre progression surf ?","es":"¿En serio sobre tu progresión surf?","it":"Serio sulla tua progressione nel surf?","de":"Ernsthaft an Ihrer Surfprogression interessiert?"}
    INTRO_FB = {"en":"At Ngor Surfcamp Teranga, we offer professional surf coaching tailored to your exact level. Beginner, intermediate or advanced, our licensed coaches help you ride better waves faster in one of West Africa's most beautiful surf destinations.","fr":"Au Ngor Surfcamp Teranga, nous proposons un coaching surf professionnel adapté à votre niveau exact. Débutant, intermédiaire ou avancé, nos coachs agréés vous aident à progresser dans l'une des plus belles destinations surf d'Afrique de l'Ouest.","es":"En Ngor Surfcamp Teranga ofrecemos coaching surf profesional adaptado a tu nivel exacto. Principiante, intermedio o avanzado, nuestros coaches licenciados te ayudan a mejorar en una de las destinos surf más bellas de África Occidental.","it":"Al Ngor Surfcamp Teranga offriamo coaching surf professionale adattato al tuo livello esatto. Principiante, intermedio o avanzato, i nostri coach autorizzati ti aiutano a migliorare in una delle più belle destinazioni surf dell'Africa Occidentale.","de":"Im Ngor Surfcamp Teranga bieten wir professionelles Surfcoaching für Ihr genaues Level. Anfänger, Fortgeschrittene oder Profi, unsere lizenzierten Coaches helfen Ihnen, in einem der schönsten Surfreiseziele Westafrikas schneller besser zu surfen."}
    SURF_HOUSE = {"en":"The Surf House","fr":"La Surf House","es":"La Surf House","it":"La Surf House","de":"Das Surf House"}
    ISLAND_L = {"en":"Ngor Island","fr":"Île de Ngor","es":"Isla de Ngor","it":"Isola di Ngor","de":"Ngor Island"}
    COACHING_L = {"en":"Surf Coaching","fr":"Coaching Surf","es":"Coaching Surf","it":"Coaching Surf","de":"Surf-Coaching"}
    DESC_HOUSE = {"en":"Rooms, pool, sea views, daily meals. Your home by the ocean.","fr":"Chambres, piscine, vue mer, repas quotidiens. Votre maison sur l'océan.","es":"Habitaciones, piscina, vista al mar, comidas diarias. Tu hogar junto al océano.","it":"Camere, piscina, vista mare, pasti quotidiani. La tua casa sull'oceano.","de":"Zimmer, Pool, Meerblick, tägliche Mahlzeiten. Ihr Zuhause am Ozean."}
    DESC_ISLAND = {"en":"No cars, world-class waves, legendary surf history. A gem off Dakar.","fr":"Pas de voitures, vagues de classe mondiale, histoire légendaire du surf.","es":"Sin coches, olas de clase mundial, historia legendaria del surf.","it":"Niente auto, onde di classe mondiale, storia leggendaria del surf.","de":"Keine Autos, weltklasse Wellen, legendäre Surfgeschichte."}
    DESC_COACH = {"en":"Professional video analysis. All levels. Year-round. Licensed federation.","fr":"Analyse vidéo professionnelle. Tous niveaux. Toute l'année. Fédération agréée.","es":"Análisis de vídeo profesional. Todos los niveles. Todo el año.","it":"Analisi video professionale. Tutti i livelli. Tutto l'anno.","de":"Professionelle Videoanalyse. Alle Level. Das ganze Jahr."}
    STAT_W = {"en":"Waves","fr":"Vagues","es":"Olas","it":"Onde","de":"Wellen"}
    STAT_L = {"en":"All Levels","fr":"Tous Niveaux","es":"Todos Niveles","it":"Tutti i Livelli","de":"Alle Level"}
    STAT_C = {"en":"Coaching","fr":"Coaching","es":"Coaching","it":"Coaching","de":"Coaching"}
    STAT_Y = {"en":"Year-Round","fr":"Toute l'année","es":"Todo el año","it":"Tutto l'anno","de":"Ganzjährig"}

    # 3 featured blog cards
    blog_cards = ""
    for en_art in arts_en[:3]:
        en_slug = en_art["slug"]
        art = arts_by_lang[lang].get(en_slug, en_art) if lang != "en" else en_art
        title_art = fix_em(art.get("title", en_art["title"]))[:80]
        meta_art  = fix_em(art.get("meta_description",""))[:110]
        blog_cards += f"""<a href="{pfx}/blog/{en_slug}/" class="card" style="text-decoration:none">
      <img src="{art_img(en_slug)}" alt="{title_art}" class="card-img" loading="lazy" onerror="this.src='{IMGS['surf3']}'">
      <div class="card-body">
        <span class="blog-cat-badge">{en_art.get('category','')}</span>
        <h3 class="card-h3" style="margin-top:10px;font-size:17px">{title_art}</h3>
        <p class="card-text">{meta_art}</p>
      </div>
    </a>"""

    eyebrow = {"en":"Ngor Island · Dakar · Senegal","fr":"Île de Ngor · Dakar · Sénégal","es":"Isla de Ngor · Dakar · Senegal","it":"Isola di Ngor · Dakar · Senegal","de":"Ngor Island · Dakar · Senegal"}

    return (head(title, meta, canonical_tag("", lang), hreflang_tags(""), lang, IMGS["home"]) +
nav_html("", lang, pfx) + f"""
<main>
  <!-- VIDEO HERO with H1 -->
  <section class="hero" aria-label="Hero">
    <!-- Background video -->
    <div class="hero-video-wrap">
      <video id="hero-video" autoplay muted loop playsinline poster="{VIDEO_POSTER}" preload="none">
        <source src="{VIDEO_BASE}/480p/mp4/file.mp4" type="video/mp4">
        <source src="{VIDEO_BASE}/360p/mp4/file.mp4" type="video/mp4">
      </video>
    </div>
    <div class="hero-grain"></div>
    <div class="hero-content reveal">
      <div class="hero-eyebrow">{ico("wave",16)} {eyebrow[lang]}</div>
      <h1 class="hero-h1">{h1}</h1>
      <p class="hero-sub">{sub}</p>
      <div class="hero-cta">
        <a href="{pfx}/booking/" class="btn btn-fire btn-lg">{BOOK[lang]}</a>
        <a href="https://wa.me/221789257025" target="_blank" rel="noopener" class="btn btn-glass btn-lg">
          <span class="svg-icon" style="width:18px;height:18px;display:inline-flex">{ICONS['wa']}</span> WhatsApp
        </a>
      </div>
    </div>
    <div class="wave-divider">
      <svg viewBox="0 0 1440 60" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none" aria-hidden="true">
        <path d="M0 30 C300 55 600 5 900 35 C1100 55 1300 20 1440 30 L1440 60 L0 60Z" fill="#fff"/>
      </svg>
    </div>
  </section>

  <!-- Stats -->
  <div class="stats" role="region" aria-label="Key figures">
    <div class="stats-inner">
      <div class="stat"><span class="stat-n">3</span><span class="stat-l">{STAT_W[lang]}</span></div>
      <div class="stat"><span class="stat-n">All</span><span class="stat-l">{STAT_L[lang]}</span></div>
      <div class="stat"><span class="stat-n">5★</span><span class="stat-l">{STAT_C[lang]}</span></div>
      <div class="stat"><span class="stat-n">365</span><span class="stat-l">{STAT_Y[lang]}</span></div>
    </div>
  </div>

  <!-- About section -->
  <section class="section" aria-labelledby="about-heading">
    <div class="container">
      <div class="split reveal">
        <div>
          <span class="s-label">{"Premium Surf Camp" if lang=="en" else "Surf Camp Premium"}</span>
          <h2 id="about-heading" class="s-title">{sections[0]["h2"] if sections else ABOUT_H2.get(lang)}</h2>
          <p class="s-sub" style="margin-bottom:28px">{intro or INTRO_FB.get(lang,"")}</p>
          <div style="display:flex;gap:12px;flex-wrap:wrap">
            <a href="{pfx}/surf-house/" class="btn btn-deep">{SURF_HOUSE[lang]}</a>
            <a href="{pfx}/surfing/" class="btn btn-outline-fire">{MORE[lang]}</a>
          </div>
        </div>
        <div class="split-img"><img src="{IMGS['surf2']}" alt="Surf coaching at Ngor Island" loading="lazy" width="600" height="440"></div>
      </div>
    </div>
  </section>

  <!-- 3 pillars -->
  <section class="section sec-sand" aria-labelledby="discover-heading">
    <div class="container">
      <div class="reveal" style="text-align:center;margin-bottom:60px">
        <span class="s-label">{DISC[lang]}</span>
        <h2 id="discover-heading" class="s-title">{"Everything at Ngor Surfcamp" if lang=="en" else "Tout au Ngor Surfcamp" if lang=="fr" else "Todo en Ngor Surfcamp" if lang=="es" else "Tutto al Ngor Surfcamp" if lang=="it" else "Alles im Ngor Surfcamp"}</h2>
      </div>
      <div class="grid-3 reveal">
        <a href="{pfx}/surf-house/" class="card">
          <img src="{IMGS['house2']}" alt="Surf House Ngor Island" class="card-img" loading="lazy">
          <div class="card-body">
            <h3 class="card-h3">{SURF_HOUSE[lang]}</h3>
            <p class="card-text">{DESC_HOUSE[lang]}</p>
            <span class="btn btn-deep btn-sm" style="margin-top:14px">{DISC[lang]}</span>
          </div>
        </a>
        <a href="{pfx}/island/" class="card">
          <img src="{IMGS['island2']}" alt="Ngor Island Senegal" class="card-img" loading="lazy">
          <div class="card-body">
            <h3 class="card-h3">{ISLAND_L[lang]}</h3>
            <p class="card-text">{DESC_ISLAND[lang]}</p>
            <span class="btn btn-deep btn-sm" style="margin-top:14px">{DISC[lang]}</span>
          </div>
        </a>
        <a href="{pfx}/surfing/" class="card">
          <img src="{IMGS['surf']}" alt="Surf coaching Senegal" class="card-img" loading="lazy">
          <div class="card-body">
            <h3 class="card-h3">{COACHING_L[lang]}</h3>
            <p class="card-text">{DESC_COACH[lang]}</p>
            <span class="btn btn-deep btn-sm" style="margin-top:14px">{MORE[lang]}</span>
          </div>
        </a>
      </div>
    </div>
  </section>

  <!-- Testimonial -->
  <section class="section" aria-label="Customer reviews">
    <div class="container-sm">
      <div class="testimonial reveal">
        <p class="testimonial-text">{REV_TEXT[lang]}</p>
        <div style="display:flex;align-items:center;gap:14px;margin-top:20px">
          <img src="{IMGS['review']}" alt="Marc Lecarpentier" style="width:52px;height:52px;border-radius:50%;object-fit:cover" loading="lazy">
          <div>
            <div class="testimonial-author">Marc Lecarpentier</div>
            <div class="testimonial-role">{"Surfer, France" if lang in ["en","fr"] else "Surfista, Francia" if lang in ["es","it"] else "Surfer, Frankreich"}</div>
          </div>
          <div style="margin-left:auto;font-size:18px;color:#f0d6a4">★★★★★</div>
        </div>
      </div>
    </div>
  </section>

  <!-- Blog preview -->
  <section class="section sec-sand" aria-labelledby="blog-preview-heading">
    <div class="container">
      <div class="reveal" style="display:flex;align-items:flex-end;justify-content:space-between;margin-bottom:48px;flex-wrap:wrap;gap:16px">
        <div>
          <span class="s-label">Blog</span>
          <h2 id="blog-preview-heading" class="s-title">{LAT[lang]}</h2>
        </div>
        <a href="{pfx}/blog/" class="btn btn-fire">{ALL_ART[lang]}</a>
      </div>
      <div class="blog-card-grid reveal">{blog_cards}</div>
    </div>
  </section>

  <!-- CTA -->
  <div class="cta-band">
    <div class="container">
      <h2>{"Ready to ride? Book your stay." if lang=="en" else "Prêt à surfer ? Réservez votre séjour." if lang=="fr" else "Listo para surfear? Reserva tu estancia." if lang=="es" else "Pronto a surfare? Prenota il tuo soggiorno." if lang=="it" else "Bereit zum Surfen? Buche deinen Aufenthalt."}</h2>
      <p>{"Ngor Island, Dakar, Senegal. WhatsApp: +221 78 925 70 25" if lang=="en" else "Île de Ngor, Dakar, Sénégal. WhatsApp : +221 78 925 70 25" if lang=="fr" else "Isla de Ngor, Dakar, Senegal. WhatsApp: +221 78 925 70 25" if lang in ["es","it","de"] else ""}</p>
      <div class="cta-btns">
        <a href="{pfx}/booking/" class="btn btn-fire btn-lg">{BOOK[lang]}</a>
        <a href="https://wa.me/221789257025" target="_blank" rel="noopener" class="btn btn-glass btn-lg">
          <span class="svg-icon" style="width:18px;height:18px;display:inline-flex">{ICONS['wa']}</span> WhatsApp
        </a>
      </div>
    </div>
  </div>
</main>""" + footer_html(lang, pfx) + close_page())

# ════════════════════════════════════════════════════════════════════════════════
# BUILD ARTICLE PAGE
# ════════════════════════════════════════════════════════════════════════════════
def build_article(en_art, lang):
    pfx     = LANG_PREFIX[lang]
    en_slug = en_art["slug"]
    art     = arts_by_lang[lang].get(en_slug, en_art) if lang != "en" else en_art
    title   = fix_em(art.get("title", en_art["title"]))
    meta_d  = fix_em(art.get("meta_description",""))[:155]
    content = md2html_rich(art.get("content_markdown",""))
    cat     = en_art.get("category","")
    img     = art_img(en_slug)

    BACK  = {"en":"Back to Blog","fr":"Retour au Blog","es":"Volver al Blog","it":"Torna al Blog","de":"Zurück zum Blog"}
    BOOK  = {"en":"Book Your Stay","fr":"Réserver","es":"Reservar","it":"Prenota","de":"Buchen"}
    REL   = {"en":"Related Articles","fr":"Articles connexes","es":"Artículos relacionados","it":"Articoli correlati","de":"Verwandte Artikel"}
    LANG_L = {"en":"Read in","fr":"Lire en","es":"Leer en","it":"Leggi in","de":"Lesen auf"}

    # Language links
    lang_links = " ".join([
        f'<a href="{LANG_PREFIX[l]}/blog/{en_slug}/" class="lang-btn {"active" if l==lang else ""}" hreflang="{LANG_LOCALE[l]}">{flag_icon(l,18)} {LANG_NAMES[l]}</a>'
        for l in LANGS
    ])

    # Related articles
    related = [a for a in arts_en if a.get("category")==cat and a["slug"] != en_slug][:2]
    rel_html = ""
    for rel in related:
        rel_art   = arts_by_lang[lang].get(rel["slug"], rel) if lang != "en" else rel
        rel_title = fix_em(rel_art.get("title", rel["title"]))[:70]
        rel_html += f"""<a href="{pfx}/blog/{rel['slug']}/" class="card" style="text-decoration:none">
      <img src="{art_img(rel['slug'])}" alt="{rel_title}" class="card-img" loading="lazy" onerror="this.src='{IMGS['surf3']}'">
      <div class="card-body">
        <span class="blog-cat-badge">{rel.get('category','')}</span>
        <h3 class="card-h3" style="font-size:16px;margin-top:8px">{rel_title}</h3>
      </div>
    </a>"""

    return (head(title[:60], meta_d,
                 canonical_tag(f"/blog/{en_slug}", lang),
                 hreflang_tags(f"/blog/{en_slug}"), lang, img) +
nav_html("blog", lang, pfx) + f"""
<main>
  <article itemscope itemtype="https://schema.org/BlogPosting">
    <!-- Hero image with H1 -->
    <header class="article-hero" style="background-image:url('{img}')" aria-label="{title}">
      <div class="article-hero-content">
        <p class="article-meta"><span class="blog-cat-badge" itemprop="articleSection">{cat}</span></p>
        <h1 style="font-size:clamp(22px,4vw,50px);margin:14px 0 0" itemprop="headline">{title}</h1>
        <meta itemprop="publisher" content="Ngor Surfcamp Teranga">
      </div>
    </header>

    <div class="container" style="padding-top:48px;padding-bottom:80px">
      <!-- Language selector -->
      <div class="article-lang-bar">
        <span>{LANG_L[lang]}</span>
        {lang_links}
      </div>

      <!-- Author card -->
      {author_card_html(en_art, lang)}

      <!-- Article body -->
      <div class="prose" itemprop="articleBody">
        {content}
      </div>

      <!-- CTA -->
      <div class="article-cta" style="position:relative">
        <div style="position:relative;z-index:1">
          <h2 style="font-size:26px;margin-bottom:10px">{"Ready to Ride? Book at Ngor Surfcamp" if lang=="en" else "Prêt à Surfer ? Réservez au Ngor Surfcamp" if lang=="fr" else "Listo para Surfear? Reserva en Ngor Surfcamp" if lang=="es" else "Pronto a Surfare? Prenota al Ngor Surfcamp" if lang=="it" else "Bereit? Buche im Ngor Surfcamp"}</h2>
          <p style="opacity:0.82;margin-bottom:28px;max-width:480px;margin-left:auto;margin-right:auto">Ngor Island, Dakar, Senegal. WhatsApp: +221 78 925 70 25</p>
          <div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap">
            <a href="{pfx}/booking/" class="btn btn-fire btn-lg">{BOOK[lang]}</a>
            <a href="https://wa.me/221789257025" target="_blank" rel="noopener" class="btn btn-glass btn-lg">
              <span class="svg-icon" style="width:18px;height:18px;display:inline-flex">{ICONS['wa']}</span> WhatsApp
            </a>
          </div>
        </div>
      </div>

      {f'<div style="margin-top:64px"><h2 style="font-size:22px;margin-bottom:24px">{REL[lang]}</h2><div class="related-grid">{rel_html}</div></div>' if rel_html else ''}

      <div style="margin-top:48px">
        <a href="{pfx}/blog/" class="btn btn-deep">
          <span class="svg-icon" style="width:16px;height:16px;display:inline-flex;transform:scaleX(-1)">{ICONS['arrow']}</span>
          {BACK[lang]}
        </a>
      </div>
    </div>
  </article>
</main>""" + footer_html(lang, pfx) + close_page())

# ════════════════════════════════════════════════════════════════════════════════
# BUILD BLOG LISTING
# ════════════════════════════════════════════════════════════════════════════════
def build_blog(lang):
    pfx   = LANG_PREFIX[lang]
    TITLE = {"en":"Surf Blog","fr":"Blog Surf","es":"Blog Surf","it":"Blog Surf","de":"Surf-Blog"}
    SUB   = {"en":"Guides, tips and stories from Ngor Island","fr":"Guides, conseils et histoires de l'Île de Ngor","es":"Guías, consejos e historias de la Isla de Ngor","it":"Guide, consigli e storie dall'Isola di Ngor","de":"Guides, Tipps und Geschichten von Ngor Island"}
    META  = {"en":"Surf blog from Ngor Surfcamp Teranga. Guides, tips and stories about surfing in Senegal.","fr":"Blog surf de Ngor Surfcamp Teranga. Guides, conseils et histoires sur le surf au Sénégal.","es":"Blog surf de Ngor Surfcamp Teranga. Guías, consejos e historias sobre el surf en Senegal.","it":"Blog surf di Ngor Surfcamp Teranga. Guide, consigli e storie sul surf in Senegal.","de":"Surf-Blog von Ngor Surfcamp Teranga. Guides, Tipps und Geschichten über Surfen in Senegal."}
    ALL   = {"en":"All","fr":"Tous","es":"Todos","it":"Tutti","de":"Alle"}

    cat_btns = f'<button class="btn btn-fire btn-sm" onclick="filterCat(' + chr(39) + 'all' + chr(39) + ')" id="cat-all" style="display:flex;align-items:center;gap:6px">{ico("wave",14)} {ALL[lang]}</button>\n'
    for c in cats:
        s = c["slug"]
        n = c["name"]
        cat_btns += f'<button class="btn btn-deep btn-sm" onclick="filterCat(' + chr(39) + s + chr(39) + ')" id="cat-' + s + '">' + n + '</button>\n'

    cards = ""
    for en_art in arts_en:
        en_slug  = en_art["slug"]
        art      = arts_by_lang[lang].get(en_slug, en_art) if lang != "en" else en_art
        t        = fix_em(art.get("title", en_art["title"]))[:80]
        m        = fix_em(art.get("meta_description",""))[:120]
        cat_name = en_art.get("category","")
        cat_slug = next((c["slug"] for c in cats if c["name"] == cat_name), "misc")
        feat     = "★ " if en_art.get("type")=="hero" else ""
        cards += f"""<a href="{pfx}/blog/{en_slug}/" class="card" data-cat="{cat_slug}" style="text-decoration:none" aria-label="{t}">
      <img src="{art_img(en_slug)}" alt="{t}" class="card-img" loading="lazy" onerror="this.src='{IMGS['surf3']}'">
      <div class="card-body">
        <span class="blog-cat-badge">{cat_name}</span>
        <h2 class="card-h3" style="font-size:16px;margin:10px 0">{feat}{t}</h2>
        <p class="card-text">{m}</p>
      </div>
    </a>\n"""

    return (head(f"Blog | {TITLE[lang]} | Ngor Surfcamp Teranga", META[lang],
                 canonical_tag("/blog", lang), hreflang_tags("/blog"), lang) +
nav_html("blog", lang, pfx) + f"""
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
  <section class="section" aria-label="Blog articles">
    <div class="container">
      <div class="blog-card-grid" id="blog-grid">{cards}</div>
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
</script>""" + footer_html(lang, pfx) + close_page())

# ════════════════════════════════════════════════════════════════════════════════
# WRITE ALL FILES
# ════════════════════════════════════════════════════════════════════════════════
total = 0
def write(path, html):
    global total
    full = DEMO_DIR + path
    if full.endswith("/"):
        full += "index.html"
    elif not full.endswith(".html"):
        os.makedirs(full, exist_ok=True)
        full += "/index.html"
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(html)
    total += 1

print("\nBuilding all pages...")
for lang in LANGS:
    pfx  = LANG_PREFIX[lang]
    spfx = f"/{lang}" if lang != "en" else ""

    write(f"{spfx}/", build_homepage(lang))
    write(f"{spfx}/blog/", build_blog(lang))
    for en_art in arts_en:
        write(f"{spfx}/blog/{en_art['slug']}/", build_article(en_art, lang))

    print(f"  ✅ {lang}: home + blog + {len(arts_en)} articles")

print(f"\nTotal HTML files: {total}")
print("✅ Site v3 build complete!")
