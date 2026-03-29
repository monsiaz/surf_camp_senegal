"""
Build improved article pages with:
- Table of contents (auto-generated from H2s)
- Persona badges ("This article is for...")
- Visual blocks: TIP, SUMMARY, EXPERT, FACT, CHECKLIST, pull-quote
- Reading time + progress bar
- TOC sticky sidebar on desktop
- Better CTA (contextual)
- Next/prev article navigation
- Share buttons (WhatsApp)
- Uses new v2 articles (3000-3500 words) when available
- Falls back to v1 if v2 not ready
"""
import json, os, re

CONTENT   = "/Users/simonazoulay/SurfCampSenegal/content"
V2_DIR    = f"{CONTENT}/articles_v2"
V1_DIR    = f"{CONTENT}/articles"
PAGES_D   = f"{CONTENT}/pages"
ICONS_DIR = "/Users/simonazoulay/SurfCampSenegal/cloudflare-demo/assets/images/icons"
DEMO_DIR  = "/Users/simonazoulay/SurfCampSenegal/cloudflare-demo"
SITE_URL  = "https://ngor-surfcamp-demo.pages.dev"

WIX  = "https://static.wixstatic.com/media"
LOGO = f"{WIX}/c2467f_a31779010ce34c4c8c61cc5868d81f31~mv2.png"

LANGS       = ["en","fr","es","it","de"]
LANG_NAMES  = {"en":"English","fr":"Français","es":"Español","it":"Italiano","de":"Deutsch"}
LANG_LOCALE = {"en":"en","fr":"fr-FR","es":"es-ES","it":"it-IT","de":"de-DE"}
LANG_PREFIX = {"en":"","fr":"/fr","es":"/es","it":"/it","de":"/de"}

ICO_BASE = "/assets/images/icons"

def load(p):
    if os.path.exists(p):
        try:
            with open(p) as f: return json.load(f)
        except: return None
    return None

def fix_em(t):
    if not t: return ""
    return re.sub(r',\s*,',',', str(t).replace(" — ",", ").replace("—",",").replace("\u2014",",").replace(" – ",", ").replace("–",","))

# Load data
strategy = load(f"{CONTENT}/blog_strategy.json")
cats     = strategy["categories"]
personas_data = load(f"{CONTENT}/personas.json") or {}

arts_en = []
for fname in sorted(os.listdir(f"{V1_DIR}/en")):
    if fname.endswith(".json"):
        a = load(f"{V1_DIR}/en/{fname}")
        if a and a.get("slug"):
            # Try v2 first
            v2 = load(f"{V2_DIR}/en/{fname}")
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
                a = load(f"{d}/{fname}")
                if a:
                    key = a.get("original_en_slug", a.get("slug",""))
                    arts_by_lang[lang][key] = a
    if lang == "en":
        for a in arts_en: arts_by_lang["en"][a["slug"]] = a

print(f"Articles loaded: { {l: len(arts_by_lang[l]) for l in LANGS} }")

# ════════════════════════════════════════════════════════════════════════════════
# MARKDOWN → RICH HTML v2
# ════════════════════════════════════════════════════════════════════════════════
def icon_img(name, size=24, alt=""):
    local = f"{ICONS_DIR}/{name}.png"
    if os.path.exists(local):
        return f'<img src="{ICO_BASE}/{name}.png" alt="{alt}" width="{size}" height="{size}" style="display:inline-block;vertical-align:middle;object-fit:contain">'
    # SVG fallback
    FALLBACKS = {
        "icon-tip":       '<svg viewBox="0 0 24 24" fill="none" style="width:{s}px;height:{s}px"><circle cx="12" cy="12" r="10" stroke="#ff6b35" stroke-width="2"/><path d="M12 7v5M12 16v.5" stroke="#ff6b35" stroke-width="2.5" stroke-linecap="round"/></svg>',
        "icon-summary":   '<svg viewBox="0 0 24 24" fill="none" style="width:{s}px;height:{s}px"><rect x="3" y="3" width="18" height="18" rx="3" stroke="#0a2540" stroke-width="2"/><path d="M7 8h10M7 12h10M7 16h6" stroke="#0a2540" stroke-width="2" stroke-linecap="round"/></svg>',
        "icon-checklist": '<svg viewBox="0 0 24 24" fill="none" style="width:{s}px;height:{s}px"><path d="M9 12l2 2 4-4" stroke="#22c55e" stroke-width="2.5" stroke-linecap="round"/><rect x="3" y="3" width="18" height="18" rx="3" stroke="#22c55e" stroke-width="2"/></svg>',
        "icon-quote":     '<svg viewBox="0 0 24 24" fill="#f0d6a4" style="width:{s}px;height:{s}px"><path d="M3 12C3 7.5 6 4 9 3l1 2C7 6.5 5.5 9 6 11h3v6H3v-5zm11 0c0-4.5 3-7.5 6-8.5l1 2C18 7 16.5 9.5 17 12h3v6h-6v-6z"/></svg>',
        "icon-federation":'<svg viewBox="0 0 24 24" fill="none" style="width:{s}px;height:{s}px"><path d="M12 2l7 4v6c0 4-3 7.5-7 9-4-1.5-7-5-7-9V6l7-4z" stroke="#ff6b35" stroke-width="2"/><path d="M9 12l2 2 4-4" stroke="#ff6b35" stroke-width="2" stroke-linecap="round"/></svg>',
    }
    fb = FALLBACKS.get(name, FALLBACKS.get("icon-tip","")).replace("{s}",str(size))
    return fb if fb else ""

def md2html_v2(md, lang="en"):
    if not md: return ""
    md = fix_em(md)

    # Pre-process: extract TOC items from H2s
    h2s = re.findall(r'^## (.+)$', md, re.MULTILINE)

    lines = md.split("\n")
    out   = []
    in_ul = in_ol = in_toc = False

    def close_lists():
        nonlocal in_ul, in_ol
        if in_ul: out.append("</ul>"); in_ul = False
        if in_ol: out.append("</ol>"); in_ol = False

    def to_id(text):
        return re.sub(r'[^a-z0-9-]','-', text.lower().strip())[:50].rstrip('-')

    def inline(t):
        t = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', t)
        t = re.sub(r'(?<![*])\*(?![*])(.*?)(?<![*])\*(?![*])', r'<em>\1</em>', t)
        def mk_ilink(m):
            parts = m.group(0)[6:-1].split("->")
            a2 = parts[0].strip(); tgt = parts[1].strip() if len(parts)>1 else "#"
            return f'<a href="{tgt}/" class="ilink" style="color:var(--fire);font-weight:600;display:inline-flex;align-items:center;gap:4px">→ {a2}</a>'
        t = re.sub(r'\[LINK:[^\]]+\]', mk_ilink, t)
        return t

    TIP_KW  = ("**TIP:","**CONSEIL:","**TIPP:","**CONSEJO:","**CONSIGLIO:")
    NOTE_KW = ("**NOTE:","**REMARQUE:","**HINWEIS:","**NOTA:")
    FACT_KW = ("**FACT:","**FAIT:","**HECHO:","**FATTO:","**FAKT:")
    EXP_KW  = ("**EXPERT:","**EXPERT ","**QUOTE:","**CITATION:")
    CHKL_KW = ("**CHECKLIST:","**CHECK:")
    SUM_KW  = ("**SUMMARY:","**SYNTHÈSE:","**RESUMEN:","**SINTESI:","**FAZIT:","**ZUSAMMENFASSUNG:")

    BLOCK_LABELS = {
        "tip":  {"en":"Pro Tip","fr":"Conseil Pro","es":"Consejo Pro","it":"Consiglio Pro","de":"Profi-Tipp"},
        "fact": {"en":"Did You Know","fr":"Le Saviez-Vous","es":"Sabías Que","it":"Lo Sapevi","de":"Wusstest Du"},
        "expert":{"en":"From the Coaches","fr":"Depuis les Coachs","es":"De los Coaches","it":"Dai Coach","de":"Von den Coaches"},
        "checklist":{"en":"Action Checklist","fr":"Checklist d'Action","es":"Lista de Acciones","it":"Checklist","de":"Aktionsliste"},
        "summary":  {"en":"Key Takeaways","fr":"Points Clés","es":"Puntos Clave","it":"Punti Chiave","de":"Wichtige Punkte"},
    }

    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if not s:
            close_lists(); i += 1; continue

        # TOC (## Contents block)
        if s == "## Contents" or s == "## Sommaire" or s == "## Tabla de Contenidos" or s == "## Indice" or s == "## Inhaltsverzeichnis":
            close_lists()
            out.append('<nav class="toc-block" aria-label="Table of contents"><div class="toc-title">' + ("Contents" if lang=="en" else "Sommaire" if lang=="fr" else "Contenido" if lang=="es" else "Indice" if lang=="it" else "Inhalt") + '</div><ol class="toc-list">')
            i += 1
            while i < len(lines) and lines[i].strip().startswith("- "):
                item = lines[i].strip()[2:].strip()
                anchor = to_id(item)
                out.append(f'<li><a href="#{anchor}">{item}</a></li>')
                i += 1
            out.append("</ol></nav>")
            continue

        # H1/H2/H3/H4
        if s.startswith("#### "): close_lists(); out.append(f'<h4>{inline(s[5:])}</h4>')
        elif s.startswith("### "): close_lists(); out.append(f'<h3>{inline(s[4:])}</h3>')
        elif s.startswith("## "):
            close_lists()
            txt = inline(s[3:])
            anchor = to_id(s[3:])
            out.append(f'<h2 id="{anchor}">{txt}</h2>')
        elif s.startswith("# "): close_lists(); out.append(f'<h1>{inline(s[2:])}</h1>')

        # Pull quote
        elif s.startswith("> "):
            close_lists()
            out.append(f'<div class="pull-quote">{icon_img("icon-quote",36,"Quote")}<blockquote class="pq-txt">{inline(s[2:])}</blockquote></div>')

        # Visual blocks
        elif any(s.upper().startswith(k) for k in TIP_KW):
            close_lists()
            ct = re.sub(r'^\*\*[^:]+:\*?\*?\s*','',s)
            lbl = BLOCK_LABELS["tip"].get(lang,"Tip")
            out.append(f'<div class="vblock vb-tip"><div class="vb-ico">{icon_img("icon-tip",28,lbl)}</div><div><span class="vb-label">{lbl}</span><p>{inline(ct)}</p></div></div>')

        elif any(s.upper().startswith(k) for k in FACT_KW):
            close_lists()
            ct = re.sub(r'^\*\*[^:]+:\*?\*?\s*','',s)
            lbl = BLOCK_LABELS["fact"].get(lang,"Did You Know")
            out.append(f'<div class="vblock vb-fact"><div class="vb-ico">{icon_img("icon-federation",28,lbl)}</div><div><span class="vb-label">{lbl}</span><p>{inline(ct)}</p></div></div>')

        elif any(s.upper().startswith(k) for k in EXP_KW):
            close_lists()
            ct = re.sub(r'^\*\*[^:]*:\*?\*?\s*','',s)
            lbl = BLOCK_LABELS["expert"].get(lang,"From the Coaches")
            out.append(f'<div class="vblock vb-expert"><div class="vb-ico">{icon_img("icon-coaching",28,lbl)}</div><div><span class="vb-label">{lbl}</span><blockquote style="margin:0;font-style:italic">{inline(ct)}</blockquote></div></div>')

        elif any(s.upper().startswith(k) for k in NOTE_KW):
            close_lists()
            ct = re.sub(r'^\*\*[^:]+:\*?\*?\s*','',s)
            out.append(f'<div class="vblock vb-note"><div class="vb-ico">{icon_img("icon-tip",28,"Note")}</div><div><span class="vb-label">Note</span><p>{inline(ct)}</p></div></div>')

        elif any(s.upper().startswith(k) for k in SUM_KW):
            close_lists()
            ct = re.sub(r'^\*\*[^:]+:\*?\*?\s*','',s)
            lbl = BLOCK_LABELS["summary"].get(lang,"Key Takeaways")
            out.append(f'<div class="vblock vb-summary"><div class="vb-ico">{icon_img("icon-summary",28,lbl)}</div><div><span class="vb-label">{lbl}</span><p>{inline(ct)}</p></div></div>')

        elif any(s.upper().startswith(k) for k in CHKL_KW):
            close_lists()
            ct = re.sub(r'^\*\*[^:]+:\*?\*?\s*','',s)
            lbl = BLOCK_LABELS["checklist"].get(lang,"Action Checklist")
            # Split checklist items by - or bullet
            items = [x.strip().lstrip("-").strip() for x in ct.split(",") if x.strip()]
            if len(items) <= 1:
                # Try the next lines as checklist items
                items_html_parts = f"<p>{inline(ct)}</p>"
            else:
                items_html_parts = '<ul class="checklist-items">' + "".join([f'<li>{icon_img("icon-checklist",16,"check")} {inline(it)}</li>' for it in items]) + "</ul>"
            out.append(f'<div class="vblock vb-checklist"><div class="vb-ico">{icon_img("icon-checklist",28,lbl)}</div><div><span class="vb-label">{lbl}</span>{items_html_parts}</div></div>')

        # Lists
        elif re.match(r'^[-*]\s',s):
            if not in_ul: out.append('<ul class="prose-ul">'); in_ul=True
            if in_ol: out.append("</ol>"); in_ol=False
            out.append(f'<li>{inline(s[2:])}</li>')
        elif re.match(r'^\d+\.\s',s):
            if not in_ol: out.append('<ol class="prose-ol">'); in_ol=True
            if in_ul: out.append("</ul>"); in_ul=False
            item = re.sub(r'^\d+\.\s','',s)
            out.append(f'<li>{inline(item)}</li>')

        # Bold standalone lines
        elif s.startswith("**") and s.endswith("**") and s.count("**")==2:
            close_lists()
            t2 = s.strip("*")
            if "?" in t2: out.append(f'<h4 class="faq-inline-q">{t2}</h4>')
            else: out.append(f'<h4>{t2}</h4>')

        # Regular paragraphs
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

# CSS additions for v2 article features
ARTICLE_CSS = """
/* ══════════════════════════════════════════════════════
   ARTICLE V2 ENHANCEMENTS
══════════════════════════════════════════════════════ */

/* TOC block */
.toc-block {
  background: linear-gradient(135deg, rgba(10,37,64,0.04), rgba(10,37,64,0.02));
  border: 1px solid rgba(10,37,64,0.10);
  border-left: 4px solid var(--fire);
  border-radius: 14px;
  padding: 24px 28px;
  margin: 32px 0;
}
.toc-title {
  font-family: var(--fh);
  font-weight: 800; font-size: 13px;
  text-transform: uppercase; letter-spacing: 0.14em;
  color: var(--fire); margin-bottom: 14px;
}
.toc-list {
  list-style: none; padding: 0; margin: 0;
  display: grid; grid-template-columns: 1fr 1fr; gap: 6px 20px;
}
.toc-list li a {
  font-size: 14px; color: #374151; font-weight: 500;
  transition: color 0.2s;
  display: flex; align-items: center; gap: 6px;
  text-decoration: none;
}
.toc-list li a::before {
  content: '→'; color: var(--fire); font-size: 12px;
  flex-shrink: 0;
}
.toc-list li a:hover { color: var(--fire); }

/* Visual blocks v2 */
.vblock {
  display: flex; gap: 16px; align-items: flex-start;
  padding: 22px 26px; border-radius: 14px;
  margin: 32px 0;
}
.vb-ico {
  width: 44px; height: 44px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  border-radius: 12px;
}
.vblock p, .vblock blockquote { margin: 0; font-size: 15.5px; line-height: 1.7; }
.vb-label {
  font-size: 10px; font-weight: 800; letter-spacing: 0.16em;
  text-transform: uppercase; display: block; margin-bottom: 6px;
}

.vb-tip {
  background: linear-gradient(135deg, rgba(255,107,53,0.10), rgba(255,107,53,0.04));
  border: 1px solid rgba(255,107,53,0.22);
  border-left: 4px solid var(--fire);
}
.vb-tip .vb-ico { background: rgba(255,107,53,0.12); }
.vb-tip .vb-label { color: var(--fire); }

.vb-fact {
  background: linear-gradient(135deg, rgba(14,165,233,0.10), rgba(14,165,233,0.04));
  border: 1px solid rgba(14,165,233,0.22);
  border-left: 4px solid #0ea5e9;
}
.vb-fact .vb-ico { background: rgba(14,165,233,0.12); }
.vb-fact .vb-label { color: #0284c7; }

.vb-expert {
  background: linear-gradient(135deg, rgba(240,214,164,0.25), rgba(240,214,164,0.10));
  border: 1px solid rgba(200,160,80,0.30);
  border-left: 4px solid var(--sand);
}
.vb-expert .vb-ico { background: rgba(240,214,164,0.30); }
.vb-expert .vb-label { color: #b45309; }
.vb-expert blockquote { font-style: italic; color: #374151; font-size: 16px; line-height: 1.75; }

.vb-summary {
  background: var(--navy);
  color: #fff;
  border-radius: 16px;
  padding: 28px 32px;
}
.vb-summary .vb-ico { background: rgba(255,255,255,0.12); }
.vb-summary .vb-label { color: var(--sand); }
.vb-summary p { color: rgba(255,255,255,0.88); }

.vb-note {
  background: rgba(10,37,64,0.04);
  border: 1px solid rgba(10,37,64,0.12);
  border-left: 4px solid var(--navy);
}
.vb-note .vb-ico { background: rgba(10,37,64,0.08); }
.vb-note .vb-label { color: var(--navy); }

.vb-checklist {
  background: linear-gradient(135deg, rgba(34,197,94,0.08), rgba(34,197,94,0.03));
  border: 1px solid rgba(34,197,94,0.20);
  border-left: 4px solid #22c55e;
}
.vb-checklist .vb-ico { background: rgba(34,197,94,0.12); }
.vb-checklist .vb-label { color: #16a34a; }
.checklist-items { list-style: none; padding: 0; margin: 8px 0 0; }
.checklist-items li {
  display: flex; align-items: flex-start; gap: 8px;
  font-size: 15px; line-height: 1.65; margin-bottom: 8px;
  color: #374151;
}

/* Pull quotes v2 */
.pull-quote {
  position: relative;
  padding: 28px 36px;
  margin: 36px 0;
  background: linear-gradient(135deg, rgba(240,214,164,0.22), rgba(240,214,164,0.08));
  border-radius: 18px;
  border-left: 5px solid var(--sand);
  display: flex; gap: 14px; align-items: flex-start;
}
.pull-quote img { opacity: 0.3; flex-shrink: 0; }
.pull-quote.mini { padding: 20px 24px; }
.pq-txt {
  font-size: 20px; font-style: italic; line-height: 1.7;
  color: var(--navy); font-family: var(--fh); font-weight: 600;
  margin: 0; border: none; padding: 0; background: none;
}

/* FAQ inline */
.faq-inline-q {
  font-size: 17px; font-weight: 700; color: var(--navy);
  margin: 28px 0 10px; padding-left: 14px;
  border-left: 3px solid var(--fire);
}

/* Prose lists v2 */
.prose-ul,.prose-ol { margin: 14px 0 22px 22px; }
.prose-ul li,.prose-ol li {
  font-size: 16.5px; line-height: 1.72; color: #374151; margin-bottom: 9px;
}
.prose-ul li::marker,.prose-ol li::marker { color: var(--fire); }

/* Persona badges on article */
.persona-bar {
  display: flex; gap: 12px; flex-wrap: wrap;
  padding: 18px 22px;
  background: #f9fafb;
  border-radius: 14px;
  border: 1px solid #e5e7eb;
  margin-bottom: 32px;
  align-items: center;
}
.persona-bar-label {
  font-size: 11px; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.12em; color: #9ca3af;
}
.persona-chip {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 7px 14px; border-radius: 50px;
  font-size: 13px; font-weight: 600;
  border: 1.5px solid;
  position: relative; cursor: default;
}
.persona-chip img {
  width: 26px; height: 26px; border-radius: 50%;
  object-fit: cover; flex-shrink: 0;
}
.persona-chip-tooltip {
  position: absolute; bottom: calc(100% + 8px); left: 50%;
  transform: translateX(-50%);
  background: var(--navy); color: #fff;
  padding: 10px 14px; border-radius: 10px;
  font-size: 12.5px; line-height: 1.5; width: 230px;
  opacity: 0; pointer-events: none;
  transition: opacity 0.2s; z-index: 10;
  font-weight: 400; text-align: center;
}
.persona-chip-tooltip::after {
  content: ''; position: absolute; top: 100%; left: 50%;
  transform: translateX(-50%);
  border: 6px solid transparent;
  border-top-color: var(--navy);
}
.persona-chip:hover .persona-chip-tooltip { opacity: 1; }

/* Reading time bar */
.reading-meta {
  display: flex; align-items: center; gap: 20px;
  font-size: 13px; color: #9ca3af;
  margin-bottom: 28px; flex-wrap: wrap;
}
.reading-meta span { display: flex; align-items: center; gap: 5px; }

/* Article progress bar */
#art-progress {
  position: fixed; top: 68px; left: 0; right: 0;
  height: 2px; background: rgba(255,107,53,0.2);
  z-index: 100;
}
#art-progress-fill {
  height: 100%; width: 0;
  background: linear-gradient(90deg, var(--fire), var(--sand));
  transition: width 0.1s linear;
}

/* Share row */
.share-row {
  display: flex; align-items: center; gap: 12px;
  margin: 40px 0; flex-wrap: wrap;
}
.share-label {
  font-size: 13px; font-weight: 600; color: #9ca3af;
  text-transform: uppercase; letter-spacing: 0.1em;
}
.share-btn {
  display: inline-flex; align-items: center; gap: 7px;
  padding: 8px 16px; border-radius: 50px;
  font-size: 13px; font-weight: 600;
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer; border: none;
}
.share-btn:hover { transform: translateY(-1px); }
.share-wa { background: #25D366; color: #fff; }
.share-copy { background: #f3f4f6; color: #374151; }
.copy-success { display: none; color: #22c55e; font-size: 13px; font-weight: 600; }

/* Next/prev nav */
.art-nav {
  display: grid; grid-template-columns: 1fr 1fr; gap: 20px;
  margin: 56px 0 0;
  border-top: 1px solid #e5e7eb; padding-top: 40px;
}
.art-nav-item {
  display: flex; flex-direction: column; gap: 6px;
  padding: 20px; border-radius: 12px;
  border: 1px solid #e5e7eb; background: #fff;
  transition: all 0.25s; text-decoration: none; color: inherit;
}
.art-nav-item:hover { border-color: var(--fire); box-shadow: 0 4px 20px rgba(255,107,53,0.12); transform: translateY(-2px); }
.art-nav-dir { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: #9ca3af; }
.art-nav-title { font-size: 15px; font-weight: 700; color: var(--navy); line-height: 1.35; }
.art-nav-item.next { text-align: right; }

@media(max-width:768px){
  .toc-list { grid-template-columns: 1fr; }
  .pull-quote { padding: 18px; flex-direction: column; gap: 8px; }
  .pull-quote img { display: none; }
  .art-nav { grid-template-columns: 1fr; }
  .persona-bar { flex-direction: column; align-items: flex-start; }
}
"""

# Append CSS
with open(f"{DEMO_DIR}/assets/css/style.css","a") as f:
    f.write("\n" + ARTICLE_CSS)
print("✅ Article CSS v2 added")

# ════════════════════════════════════════════════════════════════════════════════
# ARTICLE PAGE BUILDER v2
# ════════════════════════════════════════════════════════════════════════════════
FLAG_SVG = {
    "en":'<svg viewBox="0 0 60 40"><rect width="60" height="40" fill="#012169"/><path d="M0,0 L60,40 M60,0 L0,40" stroke="#fff" stroke-width="8"/><path d="M0,0 L60,40 M60,0 L0,40" stroke="#C8102E" stroke-width="5"/><path d="M30,0 V40 M0,20 H60" stroke="#fff" stroke-width="12"/><path d="M30,0 V40 M0,20 H60" stroke="#C8102E" stroke-width="8"/></svg>',
    "fr":'<svg viewBox="0 0 60 40"><rect width="20" height="40" fill="#002395"/><rect x="20" width="20" height="40" fill="#fff"/><rect x="40" width="20" height="40" fill="#ED2939"/></svg>',
    "es":'<svg viewBox="0 0 60 40"><rect width="60" height="40" fill="#c60b1e"/><rect y="10" width="60" height="20" fill="#ffc400"/></svg>',
    "it":'<svg viewBox="0 0 60 40"><rect width="20" height="40" fill="#009246"/><rect x="20" width="20" height="40" fill="#fff"/><rect x="40" width="20" height="40" fill="#CE2B37"/></svg>',
    "de":'<svg viewBox="0 0 60 40"><rect width="60" height="13" fill="#000"/><rect y="13" width="60" height="14" fill="#DD0000"/><rect y="27" width="60" height="13" fill="#FFCE00"/></svg>',
}
WA_ICO = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>'
MENU_ICO = '<svg viewBox="0 0 24 24" fill="none"><path d="M3 7h18M3 12h18M3 17h12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>'
CHEV_ICO = '<svg viewBox="0 0 16 16" fill="none"><path d="M4 6l4 4 4-4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'

def flag(lang, size=22):
    h = round(size*0.667)
    return f'<span style="width:{size}px;height:{h}px;display:inline-flex;border-radius:3px;overflow:hidden;flex-shrink:0;box-shadow:0 1px 3px rgba(0,0,0,0.22)">{FLAG_SVG.get(lang,"")}</span>'

def lang_dd(cur, page_slug):
    s = "/" + page_slug.strip("/") if page_slug.strip("/") else ""
    opts = ""
    for l in LANGS:
        if l == cur: continue
        url = f"/{l}{s}/" if l != "en" else f"{s}/"
        opts += f'<a class="lang-dd-item" href="{url}" hreflang="{LANG_LOCALE[l]}">{flag(l,18)} {LANG_NAMES[l]}</a>\n'
    return f"""<div class="lang-dd" id="lang-dd">
  <button class="lang-dd-btn" onclick="toggleLangDD(event)">{flag(cur,20)} {cur.upper()} <span style="width:14px;height:14px;display:inline-flex">{CHEV_ICO}</span></button>
  <div class="lang-dd-menu" role="menu">{opts}</div>
</div>"""

GLOBAL_JS = """<script>
window.addEventListener('scroll',()=>{const el=document.getElementById('scroll-progress');if(el){const pct=(scrollY/(document.body.scrollHeight-innerHeight))*100;el.style.width=Math.min(pct,100)+'%';}},{passive:true});
window.addEventListener('scroll',()=>{const p=document.getElementById('art-progress-fill');if(p){const pct=(scrollY/(document.body.scrollHeight-innerHeight))*100;p.style.width=Math.min(pct,100)+'%';}},{passive:true});
window.addEventListener('scroll',()=>{const nav=document.getElementById('nav');if(nav)nav.classList.toggle('scrolled',scrollY>30);},{passive:true});
const obs=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting)e.target.classList.add('up');}),{threshold:0.09});
document.querySelectorAll('.reveal').forEach(el=>obs.observe(el));
function getBasePath(){const p=location.pathname;for(const l of['fr','es','it','de']){if(p===('/'+l)||p==='/'+l+'/')return'/';if(p.startsWith('/'+l+'/'))return p.slice(l.length+1)||'/';}return p;}
function switchLang(l){const base=getBasePath();const np=l==='en'?base:'/'+l+base;localStorage.setItem('ngor_lang',l);location.href=np;}
function toggleLangDD(e){e.stopPropagation();document.getElementById('lang-dd').classList.toggle('open');}
document.addEventListener('click',e=>{const d=document.getElementById('lang-dd');if(d&&!d.contains(e.target))d.classList.remove('open');});
function toggleMenu(){document.getElementById('nav-links').classList.toggle('open');}
document.addEventListener('click',e=>{const nl=document.getElementById('nav-links');const nt=document.getElementById('nav-toggle');if(nl&&nt&&!nl.contains(e.target)&&!nt.contains(e.target))nl.classList.remove('open');});
document.querySelectorAll('.faq-q').forEach(q=>q.addEventListener('click',()=>q.closest('.faq-item').classList.toggle('open')));
const lb=document.getElementById('lb'),lbImg=document.getElementById('lb-img'),lbCls=document.getElementById('lb-close');
if(lb){document.querySelectorAll('.gallery-item').forEach(i=>i.addEventListener('click',()=>{lbImg.src=i.querySelector('img').src;lb.classList.add('open');}));lb.addEventListener('click',e=>{if(e.target===lb)lb.classList.remove('open');});lbCls&&lbCls.addEventListener('click',()=>lb.classList.remove('open'));document.addEventListener('keydown',e=>{if(e.key==='Escape')lb.classList.remove('open');});}
function copyURL(){navigator.clipboard.writeText(location.href).then(()=>{const el=document.querySelector('.copy-success');if(el){el.style.display='inline';setTimeout(()=>el.style.display='none',2000);}});}
function shareWA(){const msg=encodeURIComponent('Check this out: '+document.title+' - '+location.href);window.open('https://wa.me/?text='+msg,'_blank');}
</script>"""

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
    <a href="{pfx}/" class="nav-logo"><img src="{LOGO}" alt="Ngor Surfcamp Teranga" width="130" height="44" loading="eager"></a>
    <div class="nav-links" id="nav-links">{items}</div>
    <div class="nav-right">
      {lang_dd(lang, page_slug)}
      <a href="https://wa.me/221789257025" target="_blank" rel="noopener" class="nav-wa" aria-label="WhatsApp">
        <span style="width:18px;height:18px;display:inline-flex">{WA_ICO}</span>
        <span class="nav-wa-label">WhatsApp</span>
      </a>
      <button class="nav-toggle" id="nav-toggle" aria-label="Menu" onclick="toggleMenu()">
        <span style="width:22px;height:22px;display:inline-flex;color:#fff">{MENU_ICO}</span>
      </button>
    </div>
  </div>
</nav>"""

def footer_html(lang, pfx):
    # footer_html defined inline
    LINKS = [("/surf-house",{"en":"Surf House","fr":"Surf House","es":"Surf House","it":"Surf House","de":"Surf House"}),("/island",{"en":"Island","fr":"Île","es":"Isla","it":"Isola","de":"Insel"}),("/surfing",{"en":"Surfing","fr":"Surf","es":"Surf","it":"Surf","de":"Surfen"}),("/blog",{"en":"Blog","fr":"Blog","es":"Blog","it":"Blog","de":"Blog"}),("/gallery",{"en":"Gallery","fr":"Galerie","es":"Galería","it":"Galleria","de":"Galerie"}),("/faq",{"en":"FAQ","fr":"FAQ","es":"FAQ","it":"FAQ","de":"FAQ"}),("/booking",{"en":"Book Now","fr":"Réserver","es":"Reservar","it":"Prenota","de":"Buchen"})]
    lk = "\n".join([f'<a href="{pfx}{s}/">{l.get(lang,l["en"])}</a>' for s,l in LINKS])
    fl = " ".join([f'<a href="{"" if l=="en" else "/"+l}/" style="opacity:0.55;display:inline-flex" hreflang="{LANG_LOCALE[l]}" title="{LANG_NAMES[l]}">{flag(l,22)}</a>' for l in LANGS])
    IG = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>'
    TT = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M19.59 6.69a4.83 4.83 0 01-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 01-2.88 2.5 2.89 2.89 0 01-2.89-2.89 2.89 2.89 0 012.89-2.89c.28 0 .54.04.79.1V9.01a6.28 6.28 0 00-.79-.05 6.34 6.34 0 00-6.34 6.34 6.34 6.34 0 006.34 6.34 6.34 6.34 0 006.33-6.34V8.69a8.22 8.22 0 004.84 1.56V6.79a4.85 4.85 0 01-1.07-.1z"/></svg>'
    COPY={"en":"© 2025 Ngor Surfcamp Teranga.","fr":"© 2025 Ngor Surfcamp Teranga.","es":"© 2025 Ngor Surfcamp Teranga.","it":"© 2025 Ngor Surfcamp Teranga.","de":"© 2025 Ngor Surfcamp Teranga."}
    return f"""<footer>
  <div class="container">
    <div class="footer-grid">
      <div>
        <img src="{LOGO}" alt="Ngor Surfcamp Teranga" class="footer-brand-logo" loading="lazy">
        <p>{"Premium surf camp on Ngor Island, Dakar, Senegal." if lang=="en" else "Surf camp premium sur l'île de Ngor, Dakar, Sénégal." if lang=="fr" else "Surf camp premium en la isla de Ngor, Dakar, Senegal." if lang=="es" else "Surf camp premium sull'isola di Ngor, Dakar, Senegal." if lang=="it" else "Premium Surfcamp auf Ngor Island, Dakar, Senegal."}</p>
        <div class="footer-social">
          <a href="https://wa.me/221789257025" target="_blank" class="soc-btn wa" aria-label="WhatsApp"><span style="width:18px;height:18px;display:inline-flex">{WA_ICO}</span></a>
          <a href="https://www.instagram.com/ngorsurfcampteranga" target="_blank" class="soc-btn ig" aria-label="Instagram"><span style="width:18px;height:18px;display:inline-flex">{IG}</span></a>
          <a href="https://www.tiktok.com/@ngorsurfcampteranga" target="_blank" class="soc-btn tt" aria-label="TikTok"><span style="width:18px;height:18px;display:inline-flex">{TT}</span></a>
        </div>
      </div>
      <div class="footer-col"><h4>{"Explore" if lang=="en" else "Explorer" if lang=="fr" else "Explorar" if lang=="es" else "Esplora" if lang=="it" else "Erkunden"}</h4>{lk}</div>
      <div class="footer-col"><h4>{"Contact" if lang in ["en","fr","es"] else "Contatti" if lang=="it" else "Kontakt"}</h4>
        <a href="https://wa.me/221789257025" target="_blank">WhatsApp: +221 78 925 70 25</a>
        <a href="mailto:info@surfcampsenegal.com">info@surfcampsenegal.com</a>
      </div>
      <div class="footer-col"><h4>{"Follow Us" if lang=="en" else "Suivez-nous" if lang=="fr" else "Síguenos" if lang=="es" else "Seguici" if lang=="it" else "Folgen"}</h4>
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
<a href="https://wa.me/221789257025" target="_blank" rel="noopener" id="float-wa" aria-label="WhatsApp">
  <span style="width:26px;height:26px;display:inline-flex">{WA_ICO}</span>
</a>"""

def head(title, meta, lang, can="", hrl="", og=""):
    return f"""<!DOCTYPE html>
<html lang="{lang}"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{fix_em(title)}</title>
<meta name="description" content="{fix_em(meta)}">
<meta property="og:title" content="{fix_em(title)}">
<meta property="og:description" content="{fix_em(meta)}">
<meta property="og:image" content="{og or ''}">
<meta property="og:type" content="article">
<meta name="robots" content="index,follow">
{can}{hrl}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Raleway:ital,wght@0,300;0,400;0,600;0,700;0,800;0,900;1,400&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/css/style.css">
</head><body>
<div id="scroll-progress"></div>
<div id="art-progress"><div id="art-progress-fill"></div></div>"""

def hrl_tags(slug):
    s = "/" + slug.strip("/") if slug.strip("/") else ""
    return "\n".join([f'<link rel="alternate" hreflang="x-default" href="{SITE_URL}{s}/">',f'<link rel="alternate" hreflang="en" href="{SITE_URL}{s}/">']+[f'<link rel="alternate" hreflang="{LANG_LOCALE[l]}" href="{SITE_URL}/{l}{s}/">' for l in ["fr","es","it","de"]])

def can_tag(slug, lang):
    s = "/" + slug.strip("/") if slug.strip("/") else ""
    pfx = f"/{lang}" if lang!="en" else ""
    return f'<link rel="canonical" href="{SITE_URL}{pfx}{s}/">'

def art_img(en_slug):
    local = f"/assets/images/{en_slug}.png"
    return local if os.path.exists(f"{DEMO_DIR}{local}") else f"{WIX}/df99f9_961b0768e713457f93025f4ce6fb1419~mv2.jpg"

PERSONA_COLORS = {
    "maya-beginner":     ("#29b6f6","#e0f7fa"),
    "jake-weekend":      ("#ff6b35","#fff3ef"),
    "lena-committed":    ("#9c27b0","#f3e5f5"),
    "carlos-globetrotter":("#0a2540","#e8edf5"),
    "amara-soul":        ("#e91e63","#fce4ec"),
}

def persona_bar_html(art_data, lang):
    pids = art_data.get("personas",[]) or ["jake-weekend","carlos-globetrotter"]
    if not pids: return ""

    LABEL = {"en":"Who is this for?","fr":"À qui s'adresse cet article ?","es":"¿Para quién es?","it":"Per chi è?","de":"Für wen?"}
    chips = ""
    for pid in pids[:3]:
        p = personas_data.get(pid,{})
        if not p: continue
        name  = p.get("name","")
        ptype = p.get("type","")
        desc  = p.get("description",{}).get(lang, p.get("description",{}).get("en",""))
        color, bg = PERSONA_COLORS.get(pid,("#ff6b35","#fff3ef"))
        img_path = f"{ICONS_DIR}/{pid}.png"
        img_tag = f'<img src="{ICO_BASE}/{pid}.png" alt="{name}" style="width:28px;height:28px;border-radius:50%;object-fit:cover">' if os.path.exists(img_path) else f'<span style="width:28px;height:28px;border-radius:50%;background:{color};color:#fff;display:inline-flex;align-items:center;justify-content:center;font-weight:700;font-size:13px">{name[0]}</span>'
        chips += f'''<div class="persona-chip" style="border-color:{color};color:{color};background:{bg}">
  {img_tag}
  <span>{name} <span style="font-weight:400;opacity:0.7;font-size:11px">· {ptype}</span></span>
  <div class="persona-chip-tooltip">{desc}</div>
</div>'''

    return f'<div class="persona-bar" role="note"><span class="persona-bar-label">{LABEL.get(lang,"For:")}</span>{chips}</div>'

def author_card_html(en_art, lang):
    authors_data_local = load(f"{CONTENT}/authors/authors.json") or {}
    CAT_AUTHOR = {}
    for aid, a in authors_data_local.items():
        for cat in a.get("categories",[]): CAT_AUTHOR[cat] = aid
    cat = en_art.get("category","")
    aid = CAT_AUTHOR.get(cat,"kofi-mensah")
    a   = authors_data_local.get(aid,{})
    if not a: return ""
    name = a.get("name","")
    role = a.get("role",{}).get(lang, a.get("role",{}).get("en",""))
    bio  = a.get("bio",{}).get(lang, a.get("bio",{}).get("en",""))[:180]
    img_local = f"/assets/images/author-{aid}.jpg"
    img_ok = os.path.exists(f"{DEMO_DIR}{img_local}")
    img_tag = f'<img src="{img_local}" alt="{name}" class="author-avatar" loading="lazy">' if img_ok else f'<div class="author-av-ph">{name[0]}</div>'
    BY = {"en":"Written by","fr":"Écrit par","es":"Escrito por","it":"Scritto da","de":"Geschrieben von"}
    return f'<div class="author-card reveal">{img_tag}<div><div style="font-size:11px;color:#9ca3af;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:4px">{BY.get(lang)}</div><div class="author-name">{name}</div><div class="author-role">{role}</div><div class="author-bio-text">{bio}</div></div></div>'

def build_article_v2(en_art, lang):
    pfx     = LANG_PREFIX[lang]
    en_slug = en_art["slug"]
    art     = arts_by_lang[lang].get(en_slug, en_art) if lang!="en" else en_art
    title   = fix_em(art.get("title", en_art["title"]))
    meta_d  = fix_em(art.get("meta_description",""))[:155]
    reading = art.get("reading_time", en_art.get("reading_time","7"))
    content = md2html_v2(art.get("content_markdown",""), lang)
    cat     = en_art.get("category","")
    img     = art_img(en_slug)
    idx     = next((i for i,a in enumerate(arts_en) if a["slug"]==en_slug), 0)
    prev_art = arts_en[idx-1] if idx > 0 else None
    next_art = arts_en[idx+1] if idx < len(arts_en)-1 else None

    BACK  = {"en":"Back to Blog","fr":"Retour au Blog","es":"Volver al Blog","it":"Torna al Blog","de":"Zurück zum Blog"}
    BOOK  = {"en":"Book Your Stay","fr":"Réserver","es":"Reservar","it":"Prenota","de":"Buchen"}
    REL   = {"en":"Related Articles","fr":"Articles connexes","es":"Artículos relacionados","it":"Articoli correlati","de":"Verwandte Artikel"}
    LANG_L= {"en":"Read in:","fr":"Lire en :","es":"Leer en:","it":"Leggi in:","de":"Lesen auf:"}
    SHARE_L={"en":"Share:","fr":"Partager :","es":"Compartir:","it":"Condividi:","de":"Teilen:"}
    SHARE_COPY={"en":"Copy link","fr":"Copier le lien","es":"Copiar enlace","it":"Copia link","de":"Link kopieren"}
    COPY_OK={"en":"Copied!","fr":"Copié !","es":"Copiado!","it":"Copiato!","de":"Kopiert!"}
    READ_T = {"en":"min read","fr":"min de lecture","es":"min de lectura","it":"min di lettura","de":"Min Lesezeit"}
    PREV_L = {"en":"Previous","fr":"Précédent","es":"Anterior","it":"Precedente","de":"Vorheriger"}
    NEXT_L = {"en":"Next","fr":"Suivant","es":"Siguiente","it":"Successivo","de":"Nächster"}
    CTA_H  = {"en":"Ready to experience Ngor for yourself?","fr":"Prêt à vivre Ngor par vous-même ?","es":"Listo para vivir Ngor por ti mismo?","it":"Pronto a vivere Ngor di persona?","de":"Bereit, Ngor selbst zu erleben?"}

    # Language pills
    lang_pills = " ".join([
        f'<a href="{LANG_PREFIX[l]}/blog/{en_slug}/" class="lang-pill {"active" if l==lang else ""}" hreflang="{LANG_LOCALE[l]}">{flag(l,16)} {LANG_NAMES[l]}</a>'
        for l in LANGS
    ])

    # Related articles
    related = [a for a in arts_en if a.get("category")==cat and a["slug"]!=en_slug][:2]
    rel_html = "".join([
        f'<a href="{pfx}/blog/{r["slug"]}/" class="card" style="text-decoration:none"><img src="{art_img(r["slug"])}" alt="{fix_em(r["title"])}" class="card-img" loading="lazy"><div class="card-body"><span class="cat-badge">{r.get("category","")}</span><h3 class="card-h3" style="font-size:15px;margin-top:8px">{fix_em(arts_by_lang[lang].get(r["slug"],r).get("title",r["title"]))[:65]}</h3></div></a>'
        for r in related
    ])

    # Prev/next nav
    def pn_art(a, direction):
        if not a: return ""
        a2 = arts_by_lang[lang].get(a["slug"],a) if lang!="en" else a
        dir_cls = "next" if direction=="next" else ""
        dir_lbl = NEXT_L[lang] if direction=="next" else PREV_L[lang]
        arrow   = "→" if direction=="next" else "←"
        return f'<a href="{pfx}/blog/{a["slug"]}/" class="art-nav-item {dir_cls}"><span class="art-nav-dir">{arrow} {dir_lbl}</span><span class="art-nav-title">{fix_em(a2.get("title",a["title"]))[:60]}</span></a>'

    nav_prev = pn_art(prev_art, "prev")
    nav_next = pn_art(next_art, "next")
    art_nav_html = f'<div class="art-nav">{nav_prev}{nav_next}</div>' if (nav_prev or nav_next) else ""

    # Breadcrumb
    bc_blog = {"en":"Blog","fr":"Blog","es":"Blog","it":"Blog","de":"Blog"}
    breadcrumb = f'<nav class="breadcrumb" aria-label="breadcrumb"><a href="{pfx}/">{"Home" if lang=="en" else "Accueil" if lang=="fr" else "Inicio" if lang=="es" else "Home" if lang=="it" else "Start"}</a><span>›</span><a href="{pfx}/blog/">{bc_blog[lang]}</a><span>›</span><span>{title[:45]}</span></nav>'

    html = head(title[:60], meta_d, lang, can_tag(f"/blog/{en_slug}",lang), hrl_tags(f"/blog/{en_slug}"), img)
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

      <div class="art-lang-bar">
        <span class="lbl">{LANG_L[lang]}</span>
        {lang_pills}
      </div>

      {persona_bar_html(art, lang)}
      {author_card_html(en_art, lang)}

      <div class="prose" itemprop="articleBody">{content}</div>

      <!-- Share row -->
      <div class="share-row">
        <span class="share-label">{SHARE_L[lang]}</span>
        <button class="share-btn share-wa" onclick="shareWA()">
          <span style="width:16px;height:16px;display:inline-flex">{WA_ICO}</span> WhatsApp
        </button>
        <button class="share-btn share-copy" onclick="copyURL()">
          🔗 {SHARE_COPY[lang]}
        </button>
        <span class="copy-success">{COPY_OK[lang]}</span>
      </div>

      <!-- CTA -->
      <div class="art-cta">
        <div style="position:relative;z-index:1">
          <h2 style="font-size:24px;margin-bottom:10px">{CTA_H[lang]}</h2>
          <p style="opacity:0.82;margin-bottom:28px;font-size:15px;max-width:480px;margin-left:auto;margin-right:auto">Ngor Island, Dakar, Senegal. WhatsApp: +221 78 925 70 25</p>
          <div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap">
            <a href="{pfx}/booking/" class="btn btn-fire btn-lg">{BOOK[lang]}</a>
            <a href="https://wa.me/221789257025" target="_blank" class="btn btn-glass btn-lg">
              <span style="width:18px;height:18px;display:inline-flex">{WA_ICO}</span> WhatsApp
            </a>
          </div>
        </div>
      </div>

      {f'<div style="margin-top:64px"><h2 style="font-size:20px;margin-bottom:22px">{REL[lang]}</h2><div class="related-grid">{rel_html}</div></div>' if rel_html else ""}

      {art_nav_html}

      <div style="margin-top:40px">
        <a href="{pfx}/blog/" class="btn btn-deep" style="display:inline-flex;align-items:center;gap:8px">← {BACK[lang]}</a>
      </div>
    </div>
  </article>
</main>"""
    html += footer_html(lang, pfx)
    html += f"\n{GLOBAL_JS}\n</body>\n</html>"
    return html

# ════════════════════════════════════════════════════════════════════════════════
# WRITE ALL ARTICLE PAGES
# ════════════════════════════════════════════════════════════════════════════════
total = 0
def write(path, html):
    global total
    full = DEMO_DIR + path
    if full.endswith("/"): full += "index.html"
    elif not full.endswith(".html"):
        os.makedirs(full, exist_ok=True); full += "/index.html"
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full,"w") as f: f.write(html)
    total += 1

print("\nBuilding article pages v2...")
for lang in LANGS:
    pfx  = LANG_PREFIX[lang]
    spfx = f"/{lang}" if lang!="en" else ""
    for en_art in arts_en:
        write(f"{spfx}/blog/{en_art['slug']}/", build_article_v2(en_art, lang))
    print(f"  ✅ {lang}: {len(arts_en)} articles")

print(f"\nTotal article pages: {total}")
print("✅ Article template v2 complete")
