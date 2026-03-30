"""
Fix 1: Parser - collect multi-line block content (SUMMARY + CHECKLIST on their own line)
Fix 2: Redesign visual blocks to match the navy/sand/fire DA
Fix 3: Rebuild all article pages with fixed parser
"""
import importlib.util
import json, os, re

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_site_assets_spec = importlib.util.spec_from_file_location(
    "site_assets", os.path.join(_BASE_DIR, "scripts", "site_assets.py")
)
_site_assets_mod = importlib.util.module_from_spec(_site_assets_spec)
_site_assets_spec.loader.exec_module(_site_assets_mod)
ASSET_VERSION = _site_assets_mod.ASSET_VERSION
ASSET_CSS_MAIN = _site_assets_mod.ASSET_CSS_MAIN
ASSET_JS_MAIN = _site_assets_mod.ASSET_JS_MAIN
CONTENT  = os.path.join(_BASE_DIR, "content")
V2_DIR   = f"{CONTENT}/articles_v2/en"
V2_LANGS  = ["en","fr","es","it","de","nl","ar"]
V1_DIR   = f"{CONTENT}/articles"
PAGES_D  = f"{CONTENT}/pages"
DEMO_DIR = os.path.join(_BASE_DIR, "cloudflare-demo")
SITE_URL = (os.environ.get("PUBLIC_SITE_URL") or "https://surf-camp-senegal.vercel.app").strip().rstrip("/")

LANGS       = ["en","fr","es","it","de","nl","ar"]
LANG_NAMES  = {"en":"English","fr":"Français","es":"Español","it":"Italiano","de":"Deutsch","nl":"Nederlands","ar":"العربية"}
LANG_LOCALE = {"en":"en","fr":"fr-FR","es":"es-ES","it":"it-IT","de":"de-DE","nl":"nl-NL","ar":"ar-MA"}
LANG_PREFIX = {"en":"","fr":"/fr","es":"/es","it":"/it","de":"/de","nl":"/nl","ar":"/ar"}
_WIX = "/assets/images/wix"
LOGO = f"{_WIX}/c2467f_a31779010ce34c4c8c61cc5868d81f31.webp"

# ════════════════════════════════════════════════════════════════════════════════
# NEW BLOCK CSS — Premium DA-matched designs
# ════════════════════════════════════════════════════════════════════════════════
NEW_BLOCK_CSS = """
/* ══════════════════════════════════════════════════════
   VISUAL BLOCKS v2 — Premium DA
══════════════════════════════════════════════════════ */

/* ── TIP block ────────────────────────────────────────── */
.vb-tip {
  background: linear-gradient(135deg, #fff8f5, #fff3ee);
  border: none;
  border-left: none;
  border-radius: 16px;
  padding: 28px 32px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 2px 20px rgba(255,90,31,0.08), inset 0 0 0 1.5px rgba(255,90,31,0.18);
}
.vb-tip::before {
  content: '';
  position: absolute; top: 0; left: 0; width: 5px; height: 100%;
  background: linear-gradient(to bottom, var(--fire), #ff8c5a);
  border-radius: 16px 0 0 16px;
}
.vb-tip .vb-header {
  display: flex; align-items: center; gap: 10px; margin-bottom: 12px;
}
.vb-tip .vb-label {
  font-size: 11px; font-weight: 800; letter-spacing: 0.16em;
  text-transform: uppercase; color: var(--fire);
  margin-bottom: 0;
}
.vb-tip .vb-ico {
  width: 36px; height: 36px; border-radius: 10px;
  background: rgba(255,90,31,0.12); flex-shrink: 0;
}
.vb-tip p, .vb-tip li { font-size: 15.5px; color: #2d1a0e; line-height: 1.72; }
.vb-tip strong { color: var(--fire); }

/* ── FACT block ───────────────────────────────────────── */
.vb-fact {
  background: linear-gradient(135deg, #f0f8ff, #e8f4ff);
  border: none;
  border-radius: 16px;
  padding: 28px 32px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 2px 20px rgba(14,165,233,0.08), inset 0 0 0 1.5px rgba(14,165,233,0.18);
}
.vb-fact::before {
  content: '';
  position: absolute; top: 0; left: 0; width: 5px; height: 100%;
  background: linear-gradient(to bottom, #0ea5e9, #38bdf8);
  border-radius: 16px 0 0 16px;
}
.vb-fact .vb-header { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
.vb-fact .vb-label { font-size: 11px; font-weight: 800; letter-spacing: 0.16em; text-transform: uppercase; color: #0284c7; margin-bottom: 0; }
.vb-fact .vb-ico { width: 36px; height: 36px; border-radius: 10px; background: rgba(14,165,233,0.12); flex-shrink: 0; }
.vb-fact p, .vb-fact li { font-size: 15.5px; color: #0c2a3a; line-height: 1.72; }

/* ── EXPERT / COACH quote ─────────────────────────────── */
.vb-expert {
  background: linear-gradient(135deg, #fffbf0, #fff8e6);
  border: none;
  border-radius: 16px;
  padding: 32px 36px 28px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 2px 20px rgba(240,192,96,0.12), inset 0 0 0 1.5px rgba(240,192,96,0.30);
}
.vb-expert::before {
  content: '"';
  position: absolute; top: -12px; left: 22px;
  font-size: 100px; line-height: 1; font-family: Georgia, serif;
  color: rgba(240,192,96,0.25); pointer-events: none;
  font-weight: 900;
}
.vb-expert::after {
  content: '';
  position: absolute; top: 0; left: 0; width: 5px; height: 100%;
  background: linear-gradient(to bottom, var(--sand), #e8b840);
  border-radius: 16px 0 0 16px;
}
.vb-expert .vb-header { display: flex; align-items: center; gap: 10px; margin-bottom: 16px; }
.vb-expert .vb-label { font-size: 11px; font-weight: 800; letter-spacing: 0.16em; text-transform: uppercase; color: #92680a; margin-bottom: 0; }
.vb-expert .vb-ico { width: 36px; height: 36px; border-radius: 10px; background: rgba(240,192,96,0.20); flex-shrink: 0; }
.vb-expert blockquote { font-size: 17px; font-style: italic; color: #2a1d06; line-height: 1.78; font-family: var(--fh); font-weight: 500; margin: 0; border: none; padding: 0; }

/* ── SUMMARY / KEY TAKEAWAYS ──────────────────────────── */
.vb-summary {
  background: linear-gradient(135deg, #0a2540 0%, #0d3060 60%, #0a2540 100%);
  border: none;
  border-radius: 20px;
  padding: 32px 36px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(10,37,64,0.25);
}
.vb-summary::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 3px;
  background: linear-gradient(90deg, var(--fire), var(--sand), var(--fire));
  background-size: 200% 100%;
  animation: shimmer 3s linear infinite;
}
.vb-summary::after {
  content: '';
  position: absolute; bottom: -30px; right: -20px;
  width: 140px; height: 140px; border-radius: 50%;
  background: rgba(255,255,255,0.03);
  pointer-events: none;
}
.vb-summary .vb-header { display: flex; align-items: center; gap: 10px; margin-bottom: 20px; }
.vb-summary .vb-label { font-size: 11px; font-weight: 800; letter-spacing: 0.18em; text-transform: uppercase; color: var(--sand); margin-bottom: 0; }
.vb-summary .vb-ico { width: 36px; height: 36px; border-radius: 10px; background: rgba(255,255,255,0.10); flex-shrink: 0; }
.vb-summary p { color: rgba(255,255,255,0.88); font-size: 15.5px; line-height: 1.72; margin: 0; }
.vb-summary ul { margin: 0; padding: 0; list-style: none; }
.vb-summary li {
  color: rgba(255,255,255,0.88); font-size: 15px; line-height: 1.68;
  margin-bottom: 10px; padding-left: 22px; position: relative;
}
.vb-summary li::before {
  content: '→'; position: absolute; left: 0;
  color: var(--sand); font-size: 13px; top: 2px;
}
.vb-summary li strong { color: #fff; }

/* ── CHECKLIST ────────────────────────────────────────── */
.vb-checklist {
  background: linear-gradient(135deg, #f0fff5, #e8fef0);
  border: none;
  border-radius: 16px;
  padding: 28px 32px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 2px 20px rgba(34,197,94,0.08), inset 0 0 0 1.5px rgba(34,197,94,0.20);
}
.vb-checklist::before {
  content: '';
  position: absolute; top: 0; left: 0; width: 5px; height: 100%;
  background: linear-gradient(to bottom, #22c55e, #4ade80);
  border-radius: 16px 0 0 16px;
}
.vb-checklist .vb-header { display: flex; align-items: center; gap: 10px; margin-bottom: 18px; }
.vb-checklist .vb-label { font-size: 11px; font-weight: 800; letter-spacing: 0.16em; text-transform: uppercase; color: #15803d; margin-bottom: 0; }
.vb-checklist .vb-ico { width: 36px; height: 36px; border-radius: 10px; background: rgba(34,197,94,0.12); flex-shrink: 0; }
.vb-checklist ul { list-style: none; margin: 0; padding: 0; }
.vb-checklist li {
  display: flex; align-items: flex-start; gap: 10px;
  font-size: 15px; line-height: 1.68; color: #0f2e1a;
  margin-bottom: 10px; padding: 0;
}
.vb-checklist li::before {
  content: '✓';
  width: 22px; height: 22px; border-radius: 50%;
  background: #22c55e; color: #fff;
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 800; flex-shrink: 0; margin-top: 1px;
}

/* ── NOTE block ───────────────────────────────────────── */
.vb-note {
  background: #f8fafc;
  border: none;
  border-radius: 16px;
  padding: 24px 28px;
  position: relative;
  overflow: hidden;
  box-shadow: inset 0 0 0 1.5px rgba(10,37,64,0.12);
}
.vb-note::before {
  content: '';
  position: absolute; top: 0; left: 0; width: 5px; height: 100%;
  background: linear-gradient(to bottom, var(--navy), #1a4a7a);
  border-radius: 16px 0 0 16px;
}
.vb-note .vb-header { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
.vb-note .vb-label { font-size: 11px; font-weight: 800; letter-spacing: 0.16em; text-transform: uppercase; color: var(--navy); margin-bottom: 0; }
.vb-note .vb-ico { width: 36px; height: 36px; border-radius: 10px; background: rgba(10,37,64,0.08); flex-shrink: 0; }
.vb-note p, .vb-note li { font-size: 15px; color: #1a2b3c; line-height: 1.70; }

/* Shared block structural reset — only for standalone vblock, not combined with vb-* */
.vblock:not(.vb-tip):not(.vb-fact):not(.vb-expert):not(.vb-summary):not(.vb-checklist):not(.vb-note) { display: block; padding: 0; background: none; border: none; margin: 32px 0; }
.vb-ico { display: flex; align-items: center; justify-content: center; }
.vb-ico img { border-radius: 6px; }
.vb-header { position: relative; z-index: 1; }
.vb-content { position: relative; z-index: 1; }

/* List inside blocks */
.vblock ul.block-list { list-style: none; margin: 0; padding: 0; }
.vb-tip ul.block-list li, .vb-fact ul.block-list li, .vb-note ul.block-list li {
  padding-left: 18px; position: relative; margin-bottom: 8px;
}
.vb-tip ul.block-list li::before { content: '•'; position: absolute; left: 0; color: var(--fire); font-size: 16px; line-height: 1.5; }
.vb-fact ul.block-list li::before { content: '•'; position: absolute; left: 0; color: #0ea5e9; font-size: 16px; line-height: 1.5; }
"""

# Update block CSS — replace existing section, never append duplicates
css_path = f"{DEMO_DIR}/assets/css/{ASSET_CSS_MAIN}"
with open(css_path) as f: css = f.read()

# Find and remove ALL existing block CSS sections (both old and new versions)
NEW_MARKER = ".vb-tip{background:linear-gradient"  # start of new block section
OLD_MARKER1 = "/* ── TIP block ──"
OLD_MARKER2 = "/* == v2 block overrides == */"

# Remove all copies of the new block section
import re as _re2
while True:
    p = css.find(NEW_MARKER)
    if p == -1: break
    # Find the next occurrence to determine section end
    p2 = css.find(NEW_MARKER, p + 1)
    if p2 == -1:
        # Last or only copy — remove from p to end
        css = css[:p].rstrip()
        break
    else:
        css = css[:p].rstrip() + css[p2:]

# Remove old marker lines
for marker in [OLD_MARKER1, OLD_MARKER2]:
    idx = css.find(marker)
    while idx != -1:
        end = css.find('\n', idx + 1)
        if end == -1: end = len(css)
        css = css[:idx] + css[end:]
        idx = css.find(marker)

# Append the block CSS exactly once
css = css.rstrip() + "\n" + NEW_BLOCK_CSS.strip() + "\n"
with open(css_path, "w") as f:
    f.write(css)
print("✅ Block CSS updated")

# ════════════════════════════════════════════════════════════════════════════════
# FIXED PARSER — multi-line block support
# ════════════════════════════════════════════════════════════════════════════════
ICO_BASE  = "/assets/images/icons"
ICONS_DIR = f"{DEMO_DIR}/assets/images/icons"
authors   = {}
auth_file = f"{CONTENT}/authors/authors.json"
if os.path.exists(auth_file):
    authors = json.load(open(auth_file))
personas = {}
pers_file = f"{CONTENT}/personas.json"
if os.path.exists(pers_file):
    personas = json.load(open(pers_file))
CAT_AUTHOR = {}
for aid, a in authors.items():
    for cat in a.get("categories",[]): CAT_AUTHOR[cat] = aid

def ico(name, size=32):
    local = f"{ICONS_DIR}/{name}.webp"
    if os.path.exists(local):
        return f'<img src="{ICO_BASE}/{name}.webp" alt="" width="{size}" height="{size}" style="object-fit:contain">'
    return ""

def fix_em(t):
    if not t: return ""
    s = str(t).replace(" — ",", ").replace("—",",").replace("\u2014",",").replace(" – ",", ").replace("–",",")
    # Strip markdown italic/bold markers (*...*  **...**) from plain-text contexts (titles, nav, alt)
    s = re.sub(r'\*\*(.*?)\*\*', r'\1', s)   # bold **text** → text
    s = re.sub(r'\*(.*?)\*', r'\1', s)         # italic *text* → text
    s = re.sub(r'\*+$', '', s.rstrip())        # trailing ** artefacts
    return re.sub(r',\s*,',',', s)

TIP_KW   = ("**TIP:","TIP:","**CONSEIL:","CONSEIL:","**TIPP:","TIPP:","**CONSEJO:","CONSEJO:","**CONSIGLIO:","CONSIGLIO:","**TIP ","TIP ")
NOTE_KW  = ("**NOTE:","NOTE:","**REMARQUE:","REMARQUE:","**HINWEIS:","HINWEIS:","**NOTA:","NOTA:","**OPMERKING:","OPMERKING:","**ملاحظة:","ملاحظة:")
FACT_KW  = ("**FACT:","FACT:","**FAIT:","FAIT:","**HECHO:","HECHO:","**FATTO:","FATTO:","**FAKT:","FAKT:","**FEIT:","FEIT:","**حقيقة:","حقيقة:")
EXP_KW   = ("**EXPERT:","EXPERT:","**EXPERT **","**QUOTE:","QUOTE:","**CITATION:","CITATION:","**COACH:","COACH:")
CHKL_KW  = ("**CHECKLIST:","CHECKLIST:","**CHECK:","CHECK:","**CONTROLELIJST:","CONTROLELIJST:","**قائمة التحقق:","قائمة التحقق:")
SUM_KW   = ("**SUMMARY:","SUMMARY:","**SYNTHÈSE:","SYNTHÈSE:","**RÉSUMÉ:","RÉSUMÉ:","**RESUMEN:","RESUMEN:",
            "**SINTESI:","SINTESI:","**FAZIT:","FAZIT:","**ZUSAMMENFASSUNG:","ZUSAMMENFASSUNG:",
            "**KEY TAKEAWAYS:","KEY TAKEAWAYS:","**POINTS CLÉS:","POINTS CLÉS:",
            "**PUNTI CHIAVE:","PUNTI CHIAVE:","**WICHTIGE PUNKTE:","WICHTIGE PUNKTE:",
            "**SAMENVATTING:","SAMENVATTING:","**BELANGRIJKSTE PUNTEN:","BELANGRIJKSTE PUNTEN:",
            "**الخلاصة:","الخلاصة:","**النقاط الرئيسية:","النقاط الرئيسية:")

BLOCK_LABELS = {
    "tip":      {"en":"Pro Tip","fr":"Conseil Pro","es":"Consejo Pro","it":"Consiglio Pro","de":"Profi-Tipp","nl":"Pro Tip","ar":"نصيحة احترافية"},
    "fact":     {"en":"Did You Know?","fr":"Le Saviez-Vous ?","es":"¿Sabías Que?","it":"Lo Sapevi?","de":"Wusstest Du?","nl":"Wist je dat?","ar":"هل تعلم؟"},
    "expert":   {"en":"From the Coaches","fr":"De nos Coachs","es":"De los Coaches","it":"Dai Coach","de":"Von den Coaches","nl":"Van de coaches","ar":"من المدربين"},
    "checklist":{"en":"Action Checklist","fr":"Liste d'Actions","es":"Lista de Acciones","it":"Lista d'Azioni","de":"Aktionsliste","nl":"Actiechecklist","ar":"قائمة التحقق"},
    "summary":  {"en":"Key Takeaways","fr":"Points Clés","es":"Puntos Clave","it":"Punti Chiave","de":"Fazit","nl":"Kernpunten","ar":"النقاط الرئيسية"},
    "note":     {"en":"Note","fr":"Note","es":"Nota","it":"Nota","de":"Hinweis","nl":"Noot","ar":"ملاحظة"},
}

PAGE_URL_MAP = {
    "surf":"pfx/surfing/","surfing":"pfx/surfing/","coaching":"pfx/surfing/",
    "ngor-right":"pfx/surfing/","ngor-left":"pfx/surfing/","waves":"pfx/surfing/",
    "island":"pfx/island/","ngor-island":"pfx/island/","ile-de-ngor":"pfx/island/",
    "surf-house":"pfx/surf-house/","accommodation":"pfx/surf-house/","rooms":"pfx/surf-house/",
    "book":"pfx/booking/","booking":"pfx/booking/","reserve":"pfx/booking/",
    "gallery":"pfx/gallery/","photos":"pfx/gallery/",
    "faq":"pfx/faq/","blog":"pfx/blog/",
}

def normalize_url(raw_tgt, pfx=""):
    tgt = raw_tgt.strip().strip("/").lower().replace(" ","-")
    for key, val in PAGE_URL_MAP.items():
        if key in tgt:
            return val.replace("pfx", pfx)
    if tgt: return f"{pfx}/blog/"
    return f"{pfx}/blog/"

def md2html(md, lang="en", pfx=""):
    if not md: return ""
    md = fix_em(md)
    lines = md.split("\n")
    out   = []
    in_ul = in_ol = False

    def close_lists():
        nonlocal in_ul, in_ol
        if in_ul: out.append("</ul>"); in_ul = False
        if in_ol: out.append("</ol>"); in_ol = False

    def to_id(t): return re.sub(r'[^a-z0-9-]','-', t.lower())[:50].rstrip('-')

    def inline(t):
        t = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', t)
        t = re.sub(r'(?<![*])\*(?![*])(.*?)(?<![*])\*(?![*])', r'<em>\1</em>', t)
        # Remove any leftover stray asterisks (markdown artefacts)
        t = re.sub(r'\*+', '', t)
        def mk_link(m):
            inner = m.group(0)[6:-1] if m.group(0).startswith("[LINK:") else m.group(0)[1:-1]
            if "\u2192" in inner: parts = inner.split("\u2192",1)
            elif "->" in inner: parts = inner.split("->",1)
            else: parts = [inner,""]
            anchor = parts[0].strip()
            real_url = normalize_url(parts[1].strip() if len(parts)>1 else "", pfx)
            return f'<a href="{real_url}" class="ilink">{anchor}</a>'
        t = re.sub(r'\[LINK:[^\]]+\]', mk_link, t)
        return t

    def render_block_items(items, block_type):
        """Render a list of items inside a block correctly."""
        if not items: return ""
        if block_type in ("summary","checklist"):
            lis = "".join([f'<li>{inline(it)}</li>' for it in items])
            return f'<ul class="block-list">{lis}</ul>'
        else:
            # For tip/fact/note: render as paragraphs or bullet list
            if len(items) > 1 and items[0].startswith("-"):
                lis = "".join([f'<li>{inline(it.lstrip("-").strip())}</li>' for it in items])
                return f'<ul class="block-list">{lis}</ul>'
            return "".join([f'<p>{inline(it.lstrip("-").strip())}</p>' for it in items])

    def collect_block_lines(start_idx, keyword_content):
        """
        Given the index of the keyword line, collect ALL block content:
        - If keyword line has content after it, that's the first piece
        - Then collect following non-empty lines until heading or double blank
        Returns (list_of_content_items, new_index)
        """
        items = []
        if keyword_content.strip():
            items.append(keyword_content.strip())

        idx = start_idx + 1
        while idx < len(lines):
            line = lines[idx].strip()
            if not line:
                # One blank line after content ends block
                if items:
                    break
                idx += 1
                continue
            # Stop at headings or new blocks
            if line.startswith("#"):
                break
            if any(line.upper().startswith(k.upper()) for k in TIP_KW+NOTE_KW+FACT_KW+EXP_KW+CHKL_KW+SUM_KW):
                break
            # Collect list items
            if line.startswith("-") or line.startswith("*") or line.startswith("•"):
                items.append(line.lstrip("-*•").strip())
            elif line.startswith("1.") or (len(line)>2 and line[0].isdigit() and line[1]=="."):
                items.append(re.sub(r'^\d+\.\s*','',line))
            else:
                items.append(line)
            idx += 1
        return items, idx - 1

    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if not s:
            close_lists(); i += 1; continue

        # TOC
        if s in ("## Contents","## Sommaire","## Tabla de Contenidos","## Indice","## Inhaltsverzeichnis","## Table of Contents","## Contenu"):
            close_lists()
            TOC_TITLES = {"en":"Contents","fr":"Sommaire","es":"Contenido","it":"Indice","de":"Inhalt","nl":"Inhoud","ar":"المحتويات"}
            out.append(f'<nav class="toc-block"><div class="toc-title">{TOC_TITLES.get(lang,"Contents")}</div><ol class="toc-list">')
            i += 1
            while i < len(lines) and (lines[i].strip().startswith("- ") or lines[i].strip().startswith("* ")):
                item = lines[i].strip()[2:].strip()
                out.append(f'<li><a href="#{to_id(item)}">{item}</a></li>')
                i += 1
            out.append("</ol></nav>")
            continue

        # Headings
        if s.startswith("#### "):   close_lists(); out.append(f'<h4>{inline(s[5:])}</h4>')
        elif s.startswith("### "): close_lists(); out.append(f'<h3>{inline(s[4:])}</h3>')
        elif s.startswith("## "):
            close_lists()
            txt = inline(s[3:]); anchor = to_id(s[3:])
            out.append(f'<h2 id="{anchor}">{txt}</h2>')
        elif s.startswith("# "): close_lists(); out.append(f'<h1>{inline(s[2:])}</h1>')

        # Pull quote
        elif s.startswith("> "):
            close_lists()
            out.append(f'<div class="pull-quote"><blockquote class="pq-txt">{inline(s[2:])}</blockquote></div>')

        # ── VISUAL BLOCKS with multi-line support ────────────────────────────
        elif any(s.upper().startswith(k.upper()) for k in TIP_KW):
            close_lists()
            ct = re.sub(r'^\*\*[^:]+:\s*\*?\*?\s*','',s)
            items, new_i = collect_block_lines(i, ct)
            i = new_i
            lbl = BLOCK_LABELS["tip"].get(lang,"Tip")
            content_html = render_block_items(items, "tip")
            out.append(f'''<div class="vb-tip">
  <div class="vb-header">
    <div class="vb-ico">{ico("icon-tip",28)}</div>
    <span class="vb-label">{lbl}</span>
  </div>
  <div class="vb-content">{content_html}</div>
</div>''')

        elif any(s.upper().startswith(k.upper()) for k in FACT_KW):
            close_lists()
            ct = re.sub(r'^\*\*[^:]+:\s*\*?\*?\s*','',s)
            items, new_i = collect_block_lines(i, ct)
            i = new_i
            lbl = BLOCK_LABELS["fact"].get(lang,"Did You Know?")
            content_html = render_block_items(items, "fact")
            out.append(f'''<div class="vb-fact">
  <div class="vb-header">
    <div class="vb-ico">{ico("icon-federation",28)}</div>
    <span class="vb-label">{lbl}</span>
  </div>
  <div class="vb-content">{content_html}</div>
</div>''')

        elif any(s.upper().startswith(k.upper()) for k in EXP_KW):
            close_lists()
            ct = re.sub(r'^\*\*[^:]*:\s*\*?\*?\s*','',s)
            items, new_i = collect_block_lines(i, ct)
            i = new_i
            lbl = BLOCK_LABELS["expert"].get(lang,"From the Coaches")
            all_text = " ".join(items).strip().strip('"').strip("\u00ab\u00bb\u201c\u201d")
            out.append(f'''<div class="vb-expert">
  <div class="vb-header">
    <div class="vb-ico">{ico("icon-coaching",28)}</div>
    <span class="vb-label">{lbl}</span>
  </div>
  <div class="vb-content">
    <blockquote>{inline(all_text)}</blockquote>
  </div>
</div>''')

        elif any(s.upper().startswith(k.upper()) for k in NOTE_KW):
            close_lists()
            ct = re.sub(r'^\*\*[^:]+:\s*\*?\*?\s*','',s)
            items, new_i = collect_block_lines(i, ct)
            i = new_i
            lbl = BLOCK_LABELS["note"].get(lang,"Note")
            content_html = render_block_items(items, "note")
            out.append(f'''<div class="vb-note">
  <div class="vb-header">
    <div class="vb-ico">{ico("icon-tip",28)}</div>
    <span class="vb-label">{lbl}</span>
  </div>
  <div class="vb-content">{content_html}</div>
</div>''')

        elif any(s.upper().startswith(k.upper()) for k in SUM_KW):
            close_lists()
            ct = re.sub(r'^\*\*[^:]+:\s*\*?\*?\s*','',s)
            items, new_i = collect_block_lines(i, ct)
            i = new_i
            lbl = BLOCK_LABELS["summary"].get(lang,"Key Takeaways")
            content_html = render_block_items(items, "summary")
            out.append(f'''<div class="vb-summary">
  <div class="vb-header">
    <div class="vb-ico">{ico("icon-summary",28)}</div>
    <span class="vb-label">{lbl}</span>
  </div>
  <div class="vb-content">{content_html}</div>
</div>''')

        elif any(s.upper().startswith(k.upper()) for k in CHKL_KW):
            close_lists()
            ct = re.sub(r'^\*\*[^:]+:\s*\*?\*?\s*','',s)
            items, new_i = collect_block_lines(i, ct)
            i = new_i
            lbl = BLOCK_LABELS["checklist"].get(lang,"Action Checklist")
            content_html = render_block_items(items, "checklist")
            out.append(f'''<div class="vb-checklist">
  <div class="vb-header">
    <div class="vb-ico">{ico("icon-checklist",28)}</div>
    <span class="vb-label">{lbl}</span>
  </div>
  <div class="vb-content">{content_html}</div>
</div>''')

        # Lists
        elif re.match(r'^[-*]\s',s):
            if not in_ul: out.append('<ul class="prose-ul">'); in_ul=True
            if in_ol: out.append("</ol>"); in_ol=False
            out.append(f'<li>{inline(s[2:])}</li>')
        elif re.match(r'^\d+\.\s',s):
            if not in_ol: out.append('<ol class="prose-ol">'); in_ol=True
            if in_ul: out.append("</ul>"); in_ul=False
            item_text = re.sub(r'^\d+\.\s','',s)
            out.append(f'<li>{inline(item_text)}</li>')

        elif s.startswith("**") and s.endswith("**") and s.count("**")==2:
            close_lists()
            t2 = s.strip("*")
            out.append(f'<h4 class="{"faq-inline-q" if "?" in t2 else ""}">{t2}</h4>')

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
# Load all data + rebuild articles
# ════════════════════════════════════════════════════════════════════════════════
FLAG_SVG = {"en":'<svg viewBox="0 0 60 40"><rect width="60" height="40" fill="#012169"/><path d="M0,0 L60,40 M60,0 L0,40" stroke="#fff" stroke-width="8"/><path d="M0,0 L60,40 M60,0 L0,40" stroke="#C8102E" stroke-width="5"/><path d="M30,0 V40 M0,20 H60" stroke="#fff" stroke-width="12"/><path d="M30,0 V40 M0,20 H60" stroke="#C8102E" stroke-width="8"/></svg>',"fr":'<svg viewBox="0 0 60 40"><rect width="20" height="40" fill="#002395"/><rect x="20" width="20" height="40" fill="#fff"/><rect x="40" width="20" height="40" fill="#ED2939"/></svg>',"es":'<svg viewBox="0 0 60 40"><rect width="60" height="40" fill="#c60b1e"/><rect y="10" width="60" height="20" fill="#ffc400"/></svg>',"it":'<svg viewBox="0 0 60 40"><rect width="20" height="40" fill="#009246"/><rect x="20" width="20" height="40" fill="#fff"/><rect x="40" width="20" height="40" fill="#CE2B37"/></svg>',"de":'<svg viewBox="0 0 60 40"><rect width="60" height="13" fill="#000"/><rect y="13" width="60" height="14" fill="#DD0000"/><rect y="27" width="60" height="13" fill="#FFCE00"/></svg>',"nl":'<svg viewBox="0 0 60 40"><rect width="60" height="13" fill="#AE1C28"/><rect y="13" width="60" height="14" fill="#fff"/><rect y="27" width="60" height="13" fill="#21468B"/></svg>',"ar":'<svg viewBox="0 0 60 40"><rect width="60" height="40" fill="#C1272D"/><path d="M30,10 L31.8,16.1 L38.5,16.1 L33,19.9 L35,26 L30,22.1 L25,26 L27,19.9 L21.5,16.1 L28.2,16.1 Z" fill="none" stroke="#006233" stroke-width="1.2"/></svg>'}
WA_ICO = '<svg viewBox="0 0 24 24" fill="currentColor" width="18" height="18"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>'
MENU_ICO = '<svg viewBox="0 0 24 24" fill="none" width="22" height="22"><path d="M3 7h18M3 12h18M3 17h12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>'
CHEV_ICO = '<svg viewBox="0 0 16 16" fill="none" width="14" height="14"><path d="M4 6l4 4 4-4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'

def flag(lang, size=22):
    h = round(size*0.667)
    return f'<span style="width:{size}px;height:{h}px;display:inline-flex;border-radius:3px;overflow:hidden;flex-shrink:0;box-shadow:0 1px 3px rgba(0,0,0,0.22)">{FLAG_SVG.get(lang,"")}</span>'

def hrl_tags(slug):
    s = "/" + slug.strip("/") if slug.strip("/") else ""
    return "\n".join([f'<link rel="alternate" hreflang="x-default" href="{SITE_URL}{s}/">',f'<link rel="alternate" hreflang="en" href="{SITE_URL}{s}/">']+[f'<link rel="alternate" hreflang="{LANG_LOCALE[l]}" href="{SITE_URL}/{l}{s}/">' for l in ["fr","es","it","de","nl","ar"]])

def can_tag(slug, lang):
    s = "/" + slug.strip("/") if slug.strip("/") else ""
    pfx = f"/{lang}" if lang!="en" else ""
    return f'<link rel="canonical" href="{SITE_URL}{pfx}{s}/">'

def head_html(title, meta, lang, can="", hrl="", og="", og_alt=""):
    _og_img = og or WIX+'/df99f9_961b0768e713457f93025f4ce6fb1419~mv2.jpg'
    _og_alt_tag = f'\n<meta property="og:image:alt" content="{fix_em(og_alt or title)}">' if (og_alt or title) else ""
    return f"""<!DOCTYPE html>
<html lang="{LANG_LOCALE.get(lang,lang)}" dir='{"rtl" if lang=="ar" else "ltr"}'><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{fix_em(title)}</title>
<meta name="description" content="{fix_em(meta)}">
<meta property="og:title" content="{fix_em(title)}">
<meta property="og:description" content="{fix_em(meta)}">
<meta property="og:image" content="{_og_img}">{_og_alt_tag}
<meta property="og:type" content="article">
<meta name="robots" content="index,follow">
{can}{hrl}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preload" href="https://fonts.googleapis.com/css2?family=Raleway:ital,wght@0,400;0,700;0,800;0,900;1,400&family=Inter:wght@400;500;600&display=swap" as="style" onload="this.onload=null;this.rel='stylesheet'">
<noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Raleway:ital,wght@0,400;0,700;0,800;0,900;1,400&family=Inter:wght@400;500;600&display=swap"></noscript>
<link rel="stylesheet" href="/assets/css/{ASSET_CSS_MAIN}?v={ASSET_VERSION}">
<script src="/assets/js/{ASSET_JS_MAIN}?v={ASSET_VERSION}" defer></script>
</head><body>
<div id="scroll-progress"></div>
<div id="art-progress"><div id="art-progress-fill"></div></div>"""

def nav_html(active, lang, pfx, page_slug="", lang_urls=None):
    """Build the site nav bar.

    lang_urls: optional dict {lang_code: absolute_path} that overrides the
    language-switcher links for the current page (used by category pages so
    each flag points to the correct per-lang category URL instead of a naive
    prefix swap).
    """
    _ps = PAGE_SLUG.get(lang, PAGE_SLUG["en"])
    NAV=[
        ("",       {"en":"Home","fr":"Accueil","es":"Inicio","it":"Home","de":"Start","nl":"Home","ar":"الرئيسية"}),
        ("surf-house",{"en":"Surf House","fr":"Surf House","es":"Surf House","it":"Surf House","de":"Surf House","nl":"Surf House","ar":"بيت الأمواج"}),
        ("island", {"en":"Island","fr":"Île","es":"Isla","it":"Isola","de":"Insel","nl":"Eiland","ar":"الجزيرة"}),
        ("surfing",{"en":"Surfing","fr":"Surf","es":"Surf","it":"Surf","de":"Surfen","nl":"Surfen","ar":"ركوب الأمواج"}),
        ("blog",   {"en":"Blog","fr":"Blog","es":"Blog","it":"Blog","de":"Blog","nl":"Blog","ar":"المدونة"}),
        ("gallery",{"en":"Gallery","fr":"Galerie","es":"Galería","it":"Galleria","de":"Galerie","nl":"Galerij","ar":"معرض الصور"}),
        ("booking",{"en":"Book Now","fr":"Réserver","es":"Reservar","it":"Prenota","de":"Buchen","nl":"Boeken","ar":"احجز الآن"}),
    ]
    def _item_href(key):
        """Return the localized path for a nav item key."""
        if not key:  # Home
            return f"{pfx}/"
        localized = _ps.get(key, key)
        return f"{pfx}/{localized}/"

    def _is_active(key):
        if not key and not active:
            return True
        return key == active.strip("/")

    items = "".join([
        f'<a href="{_item_href(k)}" class="nav-link{" active" if _is_active(k) else ""}{ " nav-cta" if k=="booking" else ""}">{lbl.get(lang, lbl["en"])}</a>'
        for k, lbl in NAV
    ])

    # Language switcher: use per-lang URLs if provided, else prefix-swap the current slug
    if lang_urls:
        opts = "".join([
            f'<a class="lang-dd-item" href="{lang_urls.get(l, ("/" if l=="en" else "/"+l+"/"))}" hreflang="{LANG_LOCALE[l]}">{flag(l,18)} {LANG_NAMES[l]}</a>'
            for l in LANGS if l != lang
        ])
    else:
        slug_clean = "/" + page_slug.strip("/") if page_slug.strip("/") else ""
        opts = "".join([
            f'<a class="lang-dd-item" href="{"/" + l + slug_clean + "/" if l!="en" else slug_clean+"/"}" hreflang="{LANG_LOCALE[l]}">{flag(l,18)} {LANG_NAMES[l]}</a>'
            for l in LANGS if l != lang
        ])
    return f'<nav id="nav"><div class="nav-inner"><a href="{pfx}/" class="nav-logo"><img src="{LOGO}" alt="Ngor Surfcamp Teranga" width="130" height="44" loading="eager"></a><div class="nav-links" id="nav-links">{items}</div><div class="nav-right"><div class="lang-dd" id="lang-dd"><button class="lang-dd-btn" onclick="toggleLangDD(event)">{flag(lang,20)} {lang.upper()} <span style="display:inline-flex">{CHEV_ICO}</span></button><div class="lang-dd-menu" role="menu">{opts}</div></div><a href="https://wa.me/221789257025" target="_blank" rel="noopener" class="nav-wa" aria-label="WhatsApp"><span style="display:inline-flex">{WA_ICO}</span><span class="nav-wa-label">WhatsApp</span></a><button class="nav-toggle" id="nav-toggle" aria-label="Menu" onclick="toggleMenu()"><span style="display:inline-flex;color:#fff">{MENU_ICO}</span></button></div></div></nav>'

WAVE_DARK_TO_WHITE = '<div class="wave-top" style="background:#fff;margin-top:-2px" aria-hidden="true"><svg viewBox="0 0 1440 52" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none"><path d="M0 26 C240 50,480 2,720 28 C960 54,1200 4,1440 26 L1440 0 L0 0Z" fill="#07192e"/></svg></div>'
WAVE_WHITE_TO_DARK = '<div class="wave-bottom" style="background:#07192e;margin-bottom:-2px" aria-hidden="true"><svg viewBox="0 0 1440 52" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none"><path d="M0 26 C240 2,480 50,720 24 C960 -2,1200 48,1440 26 L1440 52 L0 52Z" fill="#fff"/></svg></div>'

def get_footer_quotes(lang):
    """Extract footer-quotes block from the home page (built by build.py)."""
    home_rel = "index.html" if lang == "en" else f"{lang}/index.html"
    home_path = os.path.join(DEMO_DIR, home_rel)
    try:
        with open(home_path, encoding="utf-8", errors="replace") as f:
            h = f.read()
        i = h.find('<div class="footer-quotes"')
        if i < 0:
            return ""
        k = h.find("<footer", i)
        if k < 0:
            return ""
        return h[i:k].strip()
    except OSError:
        return ""

def footer_html(lang, pfx):
    IG='<svg viewBox="0 0 24 24" fill="currentColor" width="18" height="18"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>'
    TT='<svg viewBox="0 0 24 24" fill="currentColor" width="18" height="18"><path d="M19.59 6.69a4.83 4.83 0 01-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 01-2.88 2.5 2.89 2.89 0 01-2.89-2.89 2.89 2.89 0 012.89-2.89c.28 0 .54.04.79.1V9.01a6.28 6.28 0 00-.79-.05 6.34 6.34 0 00-6.34 6.34 6.34 6.34 0 006.34 6.34 6.34 6.34 0 006.33-6.34V8.69a8.22 8.22 0 004.84 1.56V6.79a4.85 4.85 0 01-1.07-.1z"/></svg>'
    LINKS=[("/surf-house",{"en":"Surf House","fr":"Surf House","es":"Surf House","it":"Surf House","de":"Surf House"}),("/island",{"en":"Island","fr":"Île","es":"Isla","it":"Isola","de":"Insel"}),("/surfing",{"en":"Surfing","fr":"Surf","es":"Surf","it":"Surf","de":"Surfen"}),("/blog",{"en":"Blog","fr":"Blog","es":"Blog","it":"Blog","de":"Blog"}),("/gallery",{"en":"Gallery","fr":"Galerie","es":"Galería","it":"Galleria","de":"Galerie"}),("/faq",{"en":"FAQ","fr":"FAQ","es":"FAQ","it":"FAQ","de":"FAQ","nl":"FAQ","ar":"الأسئلة الشائعة"}),("/booking",{"en":"Book Now","fr":"Réserver","es":"Reservar","it":"Prenota","de":"Buchen","nl":"Boeken","ar":"احجز الآن"})]
    lk="\n".join([f'<a href="{pfx}{s}/">{l.get(lang,l["en"])}</a>' for s,l in LINKS])
    fl=" ".join([f'<a href="{"" if l=="en" else "/"+l}/" style="opacity:0.45;display:inline-flex" hreflang="{LANG_LOCALE[l]}" title="{LANG_NAMES[l]}">{flag(l,22)}</a>' for l in LANGS])
    COPY={"en":"© 2025 Ngor Surfcamp Teranga.","fr":"© 2025 Ngor Surfcamp Teranga.","es":"© 2025 Ngor Surfcamp Teranga.","it":"© 2025 Ngor Surfcamp Teranga.","de":"© 2025 Ngor Surfcamp Teranga.","nl":"© 2025 Ngor Surfcamp Teranga.","ar":"© 2025 Ngor Surfcamp Teranga."}
    ABOUT={"en":"Premium surf camp on Ngor Island, Dakar, Senegal.","fr":"Surf camp premium sur l'île de Ngor, Dakar, Sénégal.","es":"Surf camp premium en la isla de Ngor, Dakar, Senegal.","it":"Surf camp premium sull'isola di Ngor, Dakar, Senegal.","de":"Premium Surfcamp auf Ngor Island, Dakar, Senegal.","nl":"Premium surfkamp op Ngor Island, Dakar, Senegal.","ar":"مخيم أمواج متميز في جزيرة نغور، داكار، السنغال."}
    EXP={"en":"Explore","fr":"Explorer","es":"Explorar","it":"Esplora","de":"Erkunden","nl":"Verkennen","ar":"استكشاف"}
    PP_SLUG={"en":"privacy-policy","fr":"politique-de-confidentialite","es":"politica-de-privacidad","it":"informativa-sulla-privacy","de":"datenschutzrichtlinie","nl":"privacybeleid","ar":"privacy-policy"}
    PP_LBL={"en":"Privacy Policy","fr":"Politique de confidentialité","es":"Política de privacidad","it":"Informativa sulla privacy","de":"Datenschutzrichtlinie","nl":"Privacybeleid","ar":"سياسة الخصوصية"}
    pp_href=f"{pfx}/{PP_SLUG[lang]}/"
    return f'<footer><div class="container"><div class="footer-grid"><div><img src="{LOGO}" alt="Ngor Surfcamp Teranga" class="footer-brand-logo" loading="lazy"><p>{ABOUT[lang]}</p><div class="footer-social"><a href="https://wa.me/221789257025" target="_blank" class="soc-btn wa" aria-label="WhatsApp"><span style="display:inline-flex">{WA_ICO}</span></a><a href="https://www.instagram.com/ngorsurfcampteranga" target="_blank" class="soc-btn ig" aria-label="Instagram"><span style="display:inline-flex">{IG}</span></a><a href="https://www.tiktok.com/@ngorsurfcampteranga" target="_blank" class="soc-btn tt" aria-label="TikTok"><span style="display:inline-flex">{TT}</span></a></div></div><div class="footer-col"><h4>{EXP[lang]}</h4>{lk}</div><div class="footer-col"><h4>{"Contact" if lang in ["en","fr","es"] else "Contatti" if lang=="it" else "Kontakt"}</h4><a href="https://wa.me/221789257025" target="_blank">WhatsApp: +221 78 925 70 25</a><a href="mailto:info@surfcampsenegal.com">info@surfcampsenegal.com</a></div><div class="footer-col"><h4>{"Follow" if lang=="en" else "Suivez-nous" if lang=="fr" else "Síguenos" if lang=="es" else "Seguici" if lang=="it" else "Folgen"}</h4><a href="https://www.instagram.com/ngorsurfcampteranga" target="_blank">Instagram</a><a href="https://www.tiktok.com/@ngorsurfcampteranga" target="_blank">TikTok</a></div></div><div class="footer-bottom"><p>{COPY[lang]} &nbsp;·&nbsp; <a href="{pp_href}" class="footer-pp-link">{PP_LBL[lang]}</a></p><div class="footer-flags">{fl}</div></div></div></footer>'

PERSONA_COLORS = {"maya-beginner":("#29b6f6","#e0f7fa"),"jake-weekend":("#ff6b35","#fff3ef"),"lena-committed":("#9c27b0","#f3e5f5"),"carlos-globetrotter":("#0a2540","#e8edf5"),"amara-soul":("#e91e63","#fce4ec")}

def persona_bar(art_data, lang):
    pids = art_data.get("personas",[]) or ["jake-weekend","carlos-globetrotter"]
    if not pids: return ""
    LABEL = {"en":"Who is this for?","fr":"Pour qui est cet article ?","es":"¿Para quién?","it":"Per chi è?","de":"Für wen?","nl":"Voor wie is dit?","ar":"لمن هذا المقال؟"}
    chips = ""
    for pid in pids[:3]:
        p = personas.get(pid,{})
        if not p: continue
        name = p.get("name",""); ptype = p.get("type","")
        desc = p.get("description",{}).get(lang, p.get("description",{}).get("en",""))
        color, bg = PERSONA_COLORS.get(pid,("#ff6b35","#fff3ef"))
        img_path = f"{DEMO_DIR}/assets/images/icons/{pid}.webp"
        if os.path.exists(img_path):
            img_tag = f'<img src="/assets/images/icons/{pid}.webp" alt="{name}" style="width:28px;height:28px;border-radius:50%;object-fit:cover">'
        else:
            img_tag = f'<span style="width:28px;height:28px;border-radius:50%;background:{color};color:#fff;display:inline-flex;align-items:center;justify-content:center;font-weight:700;font-size:13px">{name[0] if name else "?"}</span>'
        chips += f'<div class="persona-chip" style="border-color:{color};color:{color};background:{bg}">{img_tag}<span>{name} <span style="font-weight:400;opacity:0.7;font-size:11px">· {ptype}</span></span><div class="persona-chip-tooltip">{desc}</div></div>'
    return f'<div class="persona-bar"><span class="persona-bar-label">{LABEL.get(lang,"For:")}</span>{chips}</div>'

def author_card(en_art, lang):
    cat = en_art.get("category",""); aid = CAT_AUTHOR.get(cat,"kofi-mensah")
    a = authors.get(aid,{})
    if not a: return ""
    name = a.get("name",""); role = a.get("role",{}).get(lang, a.get("role",{}).get("en",""))
    bio = a.get("bio",{}).get(lang, a.get("bio",{}).get("en",""))
    img_ok = os.path.exists(f"{DEMO_DIR}/assets/images/author-{aid}.webp")
    img_tag = f'<img src="/assets/images/author-{aid}.webp" alt="{name}" class="author-avatar" loading="lazy" width="64" height="64">' if img_ok else f'<div class="author-av-ph">{name[0]}</div>'
    BY = {"en":"Written by","fr":"Écrit par","es":"Escrito por","it":"Scritto da","de":"Geschrieben von","nl":"Geschreven door","ar":"كتبه"}
    return f'<div class="author-card reveal">{img_tag}<div><div style="font-size:11px;color:#9ca3af;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:4px">{BY.get(lang)}</div><div class="author-name">{name}</div><div class="author-role">{role}</div><div class="author-bio-text">{bio}</div></div></div>'

# Load articles
strategy = json.load(open(f"{CONTENT}/blog_strategy.json"))
cats     = strategy["categories"]
arts_en  = []
for fname in sorted(os.listdir(f"{V1_DIR}/en")):
    if fname.endswith(".json"):
        a = json.load(open(f"{V1_DIR}/en/{fname}"))
        if a and a.get("slug"):
            v2 = None
            v2p = f"{V2_DIR}/{fname}"
            if os.path.exists(v2p):
                v2 = json.load(open(v2p))
                if v2 and v2.get("word_count_estimate",0) >= 2500: a = v2
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
                    # Prefer v2 translated article (has blocks) if available
                    if lang != "en":
                        v2p = f"{CONTENT}/articles_v2/{lang}/{fname}"
                        if os.path.exists(v2p):
                            v2_art = json.load(open(v2p))
                            if v2_art and v2_art.get("content_markdown","").strip():
                                art = v2_art
                    arts_by_lang[lang][key] = art
    if lang == "en":
        for a in arts_en: arts_by_lang["en"][a["slug"]] = a

# Locales without content/articles/{lang}/ (e.g. nl, ar): index articles_v2 only
for lang in LANGS:
    if lang == "en":
        continue
    v2_lang_dir = os.path.join(CONTENT, "articles_v2", lang)
    if not os.path.isdir(v2_lang_dir):
        continue
    for fname in sorted(os.listdir(v2_lang_dir)):
        if not fname.endswith(".json") or fname.startswith("_"):
            continue
        v2p = os.path.join(v2_lang_dir, fname)
        try:
            v2_art = json.load(open(v2p, encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not v2_art or not str(v2_art.get("content_markdown", "")).strip():
            continue
        key = (
            v2_art.get("original_en_slug")
            or v2_art.get("hreflang_en")
            or v2_art.get("slug")
            or fname[:-5]
        )
        arts_by_lang[lang][key] = v2_art

# ════════════════════════════════════════════════════════════════════════════════
# CATEGORY DATA — per-language slugs, names, descriptions
# ════════════════════════════════════════════════════════════════════════════════
BLOG_CATS_DATA = {
    "Island Life & Surf Camp": {
        "slug":  {"en":"island-life","fr":"vie-ile","es":"vida-isla","it":"vita-isola","de":"insel-leben","nl":"eiland-leven","ar":"island-life"},
        "name":  {"en":"Island Life & Surf Camp","fr":"Vie sur l'île & Surf Camp",
                  "es":"Vida en la isla & Surf Camp","it":"Vita sull'isola & Surf Camp","de":"Inselleben & Surf Camp","nl":"Eilandleven & Surf Camp","ar":"حياة الجزيرة ومخيم السيرف"},
        "desc":  {"en":"Discover what life at Ngor Surf Camp is really like — island living, local culture, what to pack, and why Senegal is an underrated surf destination.",
                  "fr":"Découvrez la vie au Ngor Surf Camp — île sans voitures, culture locale, quoi emporter et pourquoi le Sénégal est une destination surf sous-estimée.",
                  "es":"Descubre cómo es la vida en el Ngor Surf Camp — isla sin coches, cultura local, qué llevar y por qué Senegal es un destino surf infravalorado.",
                  "it":"Scopri com'è la vita al Ngor Surf Camp — isola senza auto, cultura locale, cosa portare e perché il Senegal è una destinazione surf sottovalutata.",
                  "de":"Entdecke das Leben im Ngor Surf Camp — autofreie Insel, lokale Kultur, Packliste und warum Senegal ein unterschätztes Surf-Ziel ist.",
                  "nl":"Ontdek hoe het leven in het Ngor Surf Camp echt is — eilandleven, lokale cultuur, wat te pakken en waarom Senegal een onderschatte surfbestemming is.",
                  "ar":"اكتشف كيف تبدو الحياة في Ngor Surf Camp — حياة جزيرة وثقافة محلية وما تحزمه ولماذا السنغال وجهة تصفح مقللة من شأنها."},
        "icon": "🏄", "ico_name": "feat-location", "color": "#F59E0B",
    },
    "Surf Conditions & Spots": {
        "slug":  {"en":"surf-conditions","fr":"conditions-surf","es":"condiciones-surf","it":"condizioni-surf","de":"surf-bedingungen","nl":"surf-omstandigheden","ar":"surf-conditions"},
        "name":  {"en":"Surf Conditions & Spots","fr":"Conditions & Spots de Surf",
                  "es":"Condiciones & Spots de Surf","it":"Condizioni & Spot di Surf","de":"Surf-Bedingungen & Spots","nl":"Surfomstandigheden & Spots","ar":"ظروف وأماكن التصفح"},
        "desc":  {"en":"Everything about Ngor Island's waves, the best time to surf Senegal, surf season guides and detailed breakdowns of Ngor Right and Left.",
                  "fr":"Tout sur les vagues de l'île de Ngor, la meilleure saison pour surfer au Sénégal et les guides détaillés de Ngor Right et Left.",
                  "es":"Todo sobre las olas de la isla de Ngor, la mejor temporada para surfear en Senegal y guías detalladas de Ngor Right y Left.",
                  "it":"Tutto sulle onde dell'isola di Ngor, il periodo migliore per fare surf in Senegal e guide dettagliate su Ngor Right e Left.",
                  "de":"Alles über die Wellen der Insel Ngor, die beste Surfsaison in Senegal und detaillierte Guides zu Ngor Right und Left.",
                  "nl":"Alles over de golven van Ngor Island, de beste tijd om te surfen in Senegal en gedetailleerde gidsen voor Ngor Right en Left.",
                  "ar":"كل شيء عن أمواج جزيرة Ngor وأفضل موسم للتصفح في السنغال وأدلة تفصيلية لـ Ngor Right و Left."},
        "icon": "🌊", "ico_name": "icon-surf-guide", "color": "#0E7490",
    },
    "Coaching & Progression": {
        "slug":  {"en":"coaching-progression","fr":"coaching-progression","es":"coaching-progresion","it":"coaching-progressione","de":"coaching-fortschritt","nl":"coaching-progressie","ar":"coaching-progression"},
        "name":  {"en":"Coaching & Progression","fr":"Coaching & Progression",
                  "es":"Coaching & Progresión","it":"Coaching & Progressione","de":"Coaching & Fortschritt","nl":"Coaching & Progressie","ar":"التدريب والتقدم"},
        "desc":  {"en":"Surf coaching guides, how to improve faster at a surf camp, video analysis, beginner tips and how to choose the best surf camp for your level.",
                  "fr":"Guides de coaching surf, progresser plus vite en surf camp, analyse vidéo, conseils pour débutants et comment choisir le meilleur surf camp.",
                  "es":"Guías de coaching surf, cómo mejorar más rápido en un surf camp, análisis de vídeo, consejos para principiantes y cómo elegir el mejor surf camp.",
                  "it":"Guide al coaching surf, come migliorare più velocemente in un surf camp, analisi video, consigli per principianti e come scegliere il surf camp migliore.",
                  "de":"Surf-Coaching-Guides, wie man im Surfcamp schneller besser wird, Videoanalyse, Anfänger-Tipps und wie man das beste Surfcamp wählt.",
                  "nl":"Surfcoaching-gidsen, sneller verbeteren in een surf camp, videoanalyse, tips voor beginners en het beste surf camp kiezen voor jouw niveau.",
                  "ar":"أدلة تدريب التصفح وكيفية التحسن بسرعة في مخيم السيرف وتحليل الفيديو ونصائح للمبتدئين وكيفية اختيار أفضل مخيم سيرف لمستواك."},
        "icon": "🎯", "ico_name": "icon-coaching", "color": "#22C55E",
    },
}

CAT_SLUG_WORD = {"en":"category","fr":"categorie","es":"categoria","it":"categoria","de":"kategorie","nl":"categorie","ar":"categorie"}
BLOG_SLUG_LG  = {"en":"blog","fr":"blog","es":"blog","it":"blog","de":"blog","nl":"blog","ar":"blog"}

# Localized page slugs — mirrors build.py SLUG dict so the blog nav generates correct per-lang URLs
PAGE_SLUG = {
    "en": {"surf-house":"surf-house","island":"island","surfing":"surfing","booking":"booking","gallery":"gallery","faq":"faq","blog":"blog"},
    "fr": {"surf-house":"surf-house","island":"ile","surfing":"surf","booking":"reservation","gallery":"galerie","faq":"faq","blog":"blog"},
    "es": {"surf-house":"surf-house","island":"isla","surfing":"surf","booking":"reservar","gallery":"galeria","faq":"faq","blog":"blog"},
    "it": {"surf-house":"surf-house","island":"isola","surfing":"surf","booking":"prenota","gallery":"galleria","faq":"faq","blog":"blog"},
    "de": {"surf-house":"surf-house","island":"insel","surfing":"surfen","booking":"buchen","gallery":"galerie","faq":"faq","blog":"blog"},
    "nl": {"surf-house":"surf-house","island":"eiland","surfing":"surfen","booking":"boeken","gallery":"galerij","faq":"faq","blog":"blog"},
    "ar": {"surf-house":"surf-house","island":"ngor-island","surfing":"surf","booking":"reservation","gallery":"galerie","faq":"faq","blog":"blog"},
}

def cat_href(cat_en, lang):
    """Full href to a category page for a given language."""
    pfx = LANG_PREFIX[lang]
    cdata = BLOG_CATS_DATA.get(cat_en, {})
    if not cdata: return f"{pfx}/blog/"
    cat_slug = cdata["slug"].get(lang, cdata["slug"]["en"])
    return f"{pfx}/blog/{CAT_SLUG_WORD[lang]}/{cat_slug}/"

def cat_name_for(cat_en, lang):
    """Localized display name for a category."""
    cdata = BLOG_CATS_DATA.get(cat_en, {})
    if not cdata: return cat_en
    return cdata["name"].get(lang, cat_en)

def build_article(en_art, lang):
    pfx  = LANG_PREFIX[lang]
    en_slug = en_art["slug"]
    art     = arts_by_lang[lang].get(en_slug, en_art) if lang!="en" else en_art
    title   = fix_em(art.get("title", en_art["title"]))
    meta_d  = fix_em(art.get("meta_description") or en_art.get("meta_description") or "")[:155]
    cat     = en_art.get("category","")

    # Reading time: estimate from word count if missing or is a placeholder like "[16]"
    _rt_raw = art.get("reading_time") or en_art.get("reading_time","")
    _wc = art.get("word_count_estimate") or en_art.get("word_count_estimate") or 0
    if _rt_raw and str(_rt_raw).strip().lstrip("[").rstrip("]").isdigit() and not str(_rt_raw).startswith("["):
        reading = str(_rt_raw)
    elif _wc:
        reading = str(max(5, round(int(_wc) / 200)))
    else:
        reading = "8"

    # Content: always use translated content if available; only fall back to EN if empty
    translated_content = art.get("content_markdown","").strip()
    content_raw = translated_content if translated_content else en_art.get("content_markdown","")
    content = md2html(content_raw, lang, pfx)

    img = f"/assets/images/{en_slug}.webp" if os.path.exists(f"{DEMO_DIR}/assets/images/{en_slug}.webp") else f"{_WIX}/df99f9_961b0768e713457f93025f4ce6fb1419.webp"
    idx = next((i for i,a in enumerate(arts_en) if a["slug"]==en_slug), 0)
    prev_art = arts_en[idx-1] if idx>0 else None
    next_art = arts_en[idx+1] if idx<len(arts_en)-1 else None

    BACK={"en":"Back to Blog","fr":"Retour au Blog","es":"Volver al Blog","it":"Torna al Blog","de":"Zurück zum Blog","nl":"Terug naar Blog","ar":"العودة إلى المدونة"}
    BOOK={"en":"Book Your Stay","fr":"Réserver","es":"Reservar","it":"Prenota","de":"Buchen","nl":"Boek je verblijf","ar":"احجز إقامتك"}
    REL={"en":"More in this category","fr":"Plus dans cette catégorie","es":"Más de esta categoría",
         "it":"Altro in questa categoria","de":"Mehr aus dieser Kategorie","nl":"Meer in deze categorie","ar":"المزيد في هذه الفئة"}
    LANG_L={"en":"Read in:","fr":"Lire en :","es":"Leer en:","it":"Leggi in:","de":"Lesen auf:","nl":"Lees in:","ar":"اقرأ بـ:"}
    CTA_H={"en":"Ready to surf at Ngor?","fr":"Prêt à surfer à Ngor ?","es":"Listo para surfear en Ngor?","it":"Pronto a surfare a Ngor?","de":"Bereit für Ngor?","nl":"Klaar om te surfen in Ngor?","ar":"هل أنت مستعد للتصفح في Ngor؟"}
    READ_T={"en":"min read","fr":"min de lecture","es":"min de lectura","it":"min di lettura","de":"Min Lesezeit","nl":"min lezen","ar":"دقيقة قراءة"}
    PREV_L={"en":"Previous","fr":"Précédent","es":"Anterior","it":"Precedente","de":"Vorheriger","nl":"Vorige","ar":"السابق"}
    NEXT_L={"en":"Next","fr":"Suivant","es":"Siguiente","it":"Successivo","de":"Nächster","nl":"Volgende","ar":"التالي"}
    BC={"en":"Home","fr":"Accueil","es":"Inicio","it":"Home","de":"Start","nl":"Home","ar":"الرئيسية"}
    BL={"en":"Blog","fr":"Blog","es":"Blog","it":"Blog","de":"Blog","nl":"Blog","ar":"المدونة"}
    SH={"en":"Share:","fr":"Partager :","es":"Compartir:","it":"Condividi:","de":"Teilen:","nl":"Delen:","ar":"شارك:"}
    CL={"en":"Copy link","fr":"Copier le lien","es":"Copiar enlace","it":"Copia link","de":"Link kopieren","nl":"Kopieer link","ar":"نسخ الرابط"}
    CD={"en":"Copied!","fr":"Copié !","es":"Copiado!","it":"Copiato!","de":"Kopiert!","nl":"Gekopieerd!","ar":"تم النسخ!"}
    SEE_ALL={"en":"See all articles","fr":"Voir tous les articles","es":"Ver todos los artículos",
             "it":"Vedi tutti gli articoli","de":"Alle Artikel anzeigen","nl":"Alle artikelen","ar":"كل المقالات"}

    # Category info for this article
    cat_display  = cat_name_for(cat, lang)
    cat_page_url = cat_href(cat, lang)

    lang_pills = " ".join([f'<a href="{LANG_PREFIX[l]}/blog/{en_slug}/" class="lang-pill {"active" if l==lang else ""}" hreflang="{LANG_LOCALE[l]}">{flag(l,16)} {LANG_NAMES[l]}</a>' for l in LANGS])

    # Same-category articles (up to 3, excluding self)
    same_cat = [a for a in arts_en if a.get("category")==cat and a["slug"]!=en_slug][:3]
    def rel_card(r):
        r_slug = r["slug"]
        r_art  = arts_by_lang[lang].get(r_slug, r)
        r_title = fix_em(r_art.get("title", r["title"]))
        r_img_path = f"{DEMO_DIR}/assets/images/{r_slug}.webp"
        r_img_src  = f"/assets/images/{r_slug}.webp" if os.path.exists(r_img_path) else f"{_WIX}/df99f9_961b0768e713457f93025f4ce6fb1419.webp"
        return (
            f'<a href="{pfx}/blog/{r_slug}/" class="card" style="text-decoration:none">'
            f'<img src="{r_img_src}" alt="{r_title}" class="card-img" loading="lazy" width="800" height="530" decoding="async">'
            f'<div class="card-body">'
            f'<span class="cat-badge" style="cursor:default">{cat_display}</span>'
            f'<h3 class="card-h3" style="font-size:15px;margin-top:8px">{r_title[:65]}</h3>'
            f'</div></a>'
        )
    rel_html = "".join([rel_card(r) for r in same_cat])

    def pn(a, d):
        if not a: return ""
        a2 = arts_by_lang[lang].get(a["slug"],a) if lang!="en" else a
        arrow = "→" if d=="next" else "←"; lbl = NEXT_L[lang] if d=="next" else PREV_L[lang]
        return f'<a href="{pfx}/blog/{a["slug"]}/" class="art-nav-item {"next" if d=="next" else ""}"><span class="art-nav-dir">{arrow} {lbl}</span><span class="art-nav-title">{fix_em(a2.get("title",a["title"]))[:60]}</span></a>'

    art_nav = f'<div class="art-nav">{pn(prev_art,"prev")}{pn(next_art,"next")}</div>' if (prev_art or next_art) else ""

    # Enriched breadcrumb: Home > Blog > Category > Article
    breadcrumb = (
        f'<nav class="breadcrumb" aria-label="breadcrumb">'
        f'<a href="{pfx}/">{BC[lang]}</a>'
        f'<span aria-hidden="true">›</span>'
        f'<a href="{pfx}/blog/">{BL[lang]}</a>'
        f'<span aria-hidden="true">›</span>'
        f'<a href="{cat_page_url}">{cat_display}</a>'
        f'<span aria-hidden="true">›</span>'
        f'<span aria-current="page">{title[:45]}</span>'
        f'</nav>'
    )

    # JSON-LD BreadcrumbList with category
    crumb_ld = f'''<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
  {{"@type":"ListItem","position":1,"name":"{BC[lang]}","item":"{SITE_URL}{pfx}/"}},
  {{"@type":"ListItem","position":2,"name":"{BL[lang]}","item":"{SITE_URL}{pfx}/blog/"}},
  {{"@type":"ListItem","position":3,"name":"{cat_display}","item":"{SITE_URL}{cat_page_url}"}},
  {{"@type":"ListItem","position":4,"name":"{title[:60].replace(chr(34), chr(39))}","item":"{SITE_URL}{pfx}/blog/{en_slug}/"}}
]}}
</script>'''

    # Category badge (clickable link in hero)
    cat_badge_hero = f'<a href="{cat_page_url}" class="cat-badge" style="text-decoration:none">{cat_display}</a>'

    # "More in category" section
    more_in_cat_html = ""
    if rel_html:
        more_in_cat_html = f'''
      <div class="more-in-cat" style="margin-top:64px">
        <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;margin-bottom:24px">
          <h2 style="font-size:20px;margin:0">{REL[lang]}: <span style="color:var(--fire)">{cat_display}</span></h2>
          <a href="{cat_page_url}" class="btn btn-deep btn-sm">{SEE_ALL[lang]} →</a>
        </div>
        <div class="related-grid">{rel_html}</div>
      </div>'''

    html = head_html(title[:60], meta_d, lang, can_tag(f"/blog/{en_slug}",lang), hrl_tags(f"/blog/{en_slug}"), img, og_alt=title)
    # Inject BreadcrumbList JSON-LD right after opening <head> (after <html>)
    html = html.replace("</head>", crumb_ld + "\n</head>", 1)
    fq_block = get_footer_quotes(lang)
    html += nav_html("blog", lang, pfx, f"/blog/{en_slug}")
    html += f"""
<main>
  <article itemscope itemtype="https://schema.org/BlogPosting">
    <header class="article-hero" style="background-image:url('{img}')" aria-label="{title}">
      <div class="art-hero-inner">
        <p style="margin-bottom:12px">{cat_badge_hero}</p>
        <h1 style="font-size:clamp(22px,4vw,52px);margin-bottom:12px;text-shadow:0 2px 20px rgba(0,0,0,0.7),0 0 48px rgba(0,0,0,0.45)" itemprop="headline">{title}</h1>
        <div class="reading-meta"><span>⏱ {reading} {READ_T[lang]}</span><span>📍 Ngor Island, Senegal</span></div>
      </div>
    </header>
    {WAVE_DARK_TO_WHITE}
    <div class="container" style="padding:20px 24px 80px">
      {breadcrumb}
      <div class="art-lang-bar"><span class="lbl">{LANG_L[lang]}</span>{lang_pills}</div>
      {persona_bar(art, lang)}
      {author_card(en_art, lang)}
      <div class="prose" itemprop="articleBody">{content}</div>
      <div class="share-row">
        <span class="share-label">{SH[lang]}</span>
        <button class="share-btn share-wa" onclick="shareWA()" style="display:inline-flex;align-items:center;gap:7px"><span style="display:inline-flex">{WA_ICO}</span> WhatsApp</button>
        <button class="share-btn share-copy" onclick="copyURL()">{CL[lang]}</button>
        <span class="copy-success">{CD[lang]}</span>
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
      {more_in_cat_html}
      {art_nav}
      <div style="margin-top:48px"><a href="{pfx}/blog/" class="btn btn-deep" style="display:inline-flex;align-items:center;gap:8px">← {BACK[lang]}</a></div>
    </div>
    {WAVE_WHITE_TO_DARK}
  </article>
</main>
{fq_block}"""
    html += footer_html(lang, pfx)
    html += "\n</body>\n</html>"
    return html

FALLBACK_IMG = "/assets/images/wix/df99f9_961b0768e713457f93025f4ce6fb1419.webp"

def art_img(slug):
    """Return best available image src for an article."""
    if os.path.exists(f"{DEMO_DIR}/assets/images/{slug}.webp"):
        return f"/assets/images/{slug}.webp"
    return FALLBACK_IMG


def build_blog_index(lang):
    """Regenerate blog index with category cards + filter buttons linking to category pages."""
    pfx   = LANG_PREFIX[lang]
    TITLE = {"en":"Surf Blog","fr":"Blog Surf","es":"Blog Surf","it":"Blog Surf","de":"Surf-Blog","nl":"Surf Blog","ar":"مدونة السيرف"}
    SUB   = {"en":"Guides, tips and stories from Ngor Island, Dakar",
             "fr":"Guides, conseils et histoires de l'Île de Ngor, Dakar",
             "es":"Guías, consejos e historias de la Isla de Ngor, Dakar",
             "it":"Guide, consigli e storie dall'Isola di Ngor, Dakar",
             "de":"Guides, Tipps und Geschichten von Ngor Island, Dakar",
             "nl":"Gidsen, tips en verhalen van Ngor Island, Dakar",
             "ar":"أدلة ونصائح وقصص من جزيرة Ngor، داكار"}
    META  = {"en":"Ngor Surfcamp Teranga surf blog. Expert guides, surf tips and stories from Ngor Island, Dakar, Senegal.",
             "fr":"Blog surf du Ngor Surfcamp Teranga. Guides experts, conseils surf et histoires de l'île de Ngor, Dakar, Sénégal.",
             "es":"Blog surf de Ngor Surfcamp Teranga. Guías de expertos, consejos surf e historias de la isla de Ngor, Dakar, Senegal.",
             "it":"Blog surf di Ngor Surfcamp Teranga. Guide di esperti, consigli surf e storie dall'isola di Ngor, Dakar, Senegal.",
             "de":"Surf-Blog von Ngor Surfcamp Teranga. Expertenguides, Surf-Tipps und Geschichten von Ngor Island, Dakar, Senegal.",
             "nl":"Surf blog van Ngor Surfcamp Teranga. Expertgidsen, surftips en verhalen van Ngor Island, Dakar, Senegal.",
             "ar":"مدونة سيرف Ngor Surfcamp Teranga. أدلة الخبراء ونصائح التصفح وقصص من جزيرة Ngor، داكار، السنغال."}
    ALL_LBL = {"en":"All","fr":"Tous","es":"Todos","it":"Tutti","de":"Alle","nl":"Alles","ar":"الكل"}
    BROWSE  = {"en":"Browse by Category","fr":"Parcourir par catégorie","es":"Explorar por categoría",
               "it":"Sfoglia per categoria","de":"Nach Kategorie durchsuchen","nl":"Bladeren per categorie","ar":"تصفح حسب الفئة"}
    ART_LBL = {"en":"articles","fr":"articles","es":"artículos","it":"articoli","de":"Artikel","nl":"artikelen","ar":"مقالات"}

    # Category cards (above-fold browse section)
    cat_cards = ""
    for cat_en, cdata in BLOG_CATS_DATA.items():
        c_slug    = cdata["slug"][lang]
        c_name    = cdata["name"][lang]
        c_desc    = cdata["desc"][lang][:120]
        c_ico_name = cdata.get("ico_name", "icon-surf-guide")
        c_color   = cdata["color"]
        c_href    = cat_href(cat_en, lang)
        c_count   = sum(1 for a in arts_en if a.get("category") == cat_en)
        c_ico_html = ico(c_ico_name, 40)
        cat_cards += f'''
      <a href="{c_href}" class="cat-card" style="text-decoration:none;border-top:3px solid {c_color}">
        <div class="cat-card-icon-wrap" style="width:56px;height:56px;border-radius:14px;background:{c_color}18;display:flex;align-items:center;justify-content:center;margin-bottom:14px;flex-shrink:0">{c_ico_html}</div>
        <h3 class="cat-card-name">{c_name}</h3>
        <p class="cat-card-desc">{c_desc}</p>
        <span class="cat-card-count" style="color:{c_color};font-weight:700;font-size:13px">{c_count} {ART_LBL[lang]}</span>
      </a>'''

    # Filter buttons (slug-based, JS filterCat)
    cat_btns = f'<button class="btn btn-fire btn-sm" onclick="filterCat(\'all\')" id="cat-all">{ALL_LBL[lang]}</button>\n'
    for cat_en, cdata in BLOG_CATS_DATA.items():
        # Use the EN slug from blog_strategy for data-cat consistency
        en_slug_cat = [c["slug"] for c in cats if c["name"] == cat_en]
        en_slug_cat = en_slug_cat[0] if en_slug_cat else cat_en.lower().replace(" & ", "-").replace(" ", "-")
        c_name = cdata["name"][lang]
        c_href = cat_href(cat_en, lang)
        cat_btns += (
            f'<button class="btn btn-deep btn-sm cat-filter-btn" '
            f'onclick="filterCat(\'{en_slug_cat}\')" '
            f'data-href="{c_href}" '
            f'id="cat-{en_slug_cat}">{c_name}</button>\n'
        )

    # Article cards
    cards = ""
    for en_art in arts_en:
        en_s     = en_art["slug"]
        a        = arts_by_lang[lang].get(en_s, en_art) if lang!="en" else en_art
        t        = fix_em(a.get("title", en_art["title"]))[:80]
        m        = fix_em(a.get("meta_description",""))[:120]
        cat_en   = en_art.get("category","")
        cat_disp = cat_name_for(cat_en, lang)
        cat_href_url = cat_href(cat_en, lang)
        en_slug_cat  = [c["slug"] for c in cats if c["name"] == cat_en]
        en_slug_cat  = en_slug_cat[0] if en_slug_cat else cat_en.lower().replace(" & ", "-").replace(" ", "-")
        feat     = "★ " if en_art.get("type") == "hero" else ""
        cards += f'''<a href="{pfx}/blog/{en_s}/" class="card blog-card" data-cat="{en_slug_cat}" style="text-decoration:none" aria-label="{t}">
      <div class="blog-card-img-wrap">
        <img src="{art_img(en_s)}" alt="{t}" class="card-img" loading="lazy" width="800" height="530" decoding="async" onerror="this.src='{FALLBACK_IMG}'">
      </div>
      <div class="card-body">
        <span class="cat-badge">{cat_disp}</span>
        <h2 class="card-h3" style="font-size:15px;margin:8px 0 6px;line-height:1.35">{feat}{t}</h2>
        <p class="card-text" style="font-size:13px;color:#6b7280;margin:0">{m}</p>
      </div>
    </a>\n'''

    # hreflang tags for blog index
    hrl = "\n".join([
        f'  <link rel="alternate" hreflang="{"x-default" if l=="en" else LANG_LOCALE[l]}" href="{SITE_URL}{LANG_PREFIX[l]}/blog/">'
        for l in ["en"] + [l for l in LANGS if l!="en"]
    ])
    hrl = f'<link rel="alternate" hreflang="x-default" href="{SITE_URL}/blog/">\n' + "\n".join([
        f'  <link rel="alternate" hreflang="{LANG_LOCALE[l]}" href="{SITE_URL}{LANG_PREFIX[l]}/blog/">'
        for l in LANGS
    ])
    can = f'<link rel="canonical" href="{SITE_URL}{pfx}/blog/">'

    html = head_html(f"Blog | {TITLE[lang]} | Ngor Surfcamp Teranga", META[lang], lang, can, hrl,
                     FALLBACK_IMG, og_alt=TITLE[lang])
    fq_block = get_footer_quotes(lang)
    html += nav_html("blog", lang, pfx, "/blog")
    EYEBROW = {"en":"Ngor Island · Dakar · Senegal","fr":"Île de Ngor · Dakar · Sénégal",
               "es":"Isla de Ngor · Dakar · Senegal","it":"Isola di Ngor · Dakar · Senegal",
               "de":"Ngor Island · Dakar · Senegal","nl":"Ngor Island · Dakar · Senegal",
               "ar":"جزيرة نغور · داكار · السنغال"}
    html += f"""
<main>
  <header class="blog-hub-header" role="banner">
    <div class="container" style="text-align:center;padding:56px 24px 68px">
      <span class="s-label" style="color:rgba(255,255,255,0.65);letter-spacing:.12em;display:block;margin-bottom:16px">{EYEBROW[lang]}</span>
      <h1 style="font-size:clamp(26px,4.5vw,50px);margin:0 0 14px;line-height:1.1;color:#fff;font-weight:900">{TITLE[lang]}</h1>
      <p style="font-size:16px;color:rgba(255,255,255,0.76);max-width:500px;margin:0 auto;line-height:1.6">{SUB[lang]}</p>
    </div>
    <div class="wave-bottom" aria-hidden="true"><svg viewBox="0 0 1440 52" fill="none" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none"><path d="M0 0 C360 52,1080 52,1440 0 L1440 52 L0 52Z" fill="#fff8ec"/></svg></div>
  </header>

  <!-- Category Browse Cards -->
  <section class="section sec-sand" style="padding:48px 0 32px" aria-label="Categories">
    <div class="container">
      <h2 class="s-title" style="margin-bottom:32px;font-size:clamp(20px,3vw,28px)">{BROWSE[lang]}</h2>
      <div class="cat-cards-grid">
        {cat_cards}
      </div>
    </div>
  </section>

  <!-- All Articles with filter -->
  <div class="blog-filter-bar">
    <div class="container">
      {cat_btns}
    </div>
  </div>
  <section class="section" aria-label="Articles" style="padding-top:40px;padding-bottom:64px">
    <div class="container">
      <div class="blog-grid" id="blog-grid">{cards}</div>
    </div>
  </section>
</main>
<script>
function filterCat(cat){{
  document.querySelectorAll('.cat-filter-btn').forEach(b=>{{b.className='btn btn-deep btn-sm cat-filter-btn';}});
  var btn=document.getElementById('cat-all');
  if(cat==='all'){{if(btn)btn.className='btn btn-fire btn-sm cat-filter-btn';}}
  else{{var cb=document.getElementById('cat-'+cat);if(cb)cb.className='btn btn-fire btn-sm cat-filter-btn';}}
  var shown=0;
  document.querySelectorAll('#blog-grid .blog-card').forEach(c=>{{
    var vis=(cat==='all'||c.dataset.cat===cat);
    c.style.display=vis?'':'none';
    if(vis)shown++;
  }});
}}
window.addEventListener('DOMContentLoaded',function(){{filterCat('all');}});
</script>
{fq_block}"""
    html += footer_html(lang, pfx)
    html += "\n</body>\n</html>"
    return html


def build_category_page(cat_en, lang):
    """Build a category landing page (one per category × language)."""
    pfx    = LANG_PREFIX[lang]
    cdata  = BLOG_CATS_DATA[cat_en]
    c_name = cdata["name"][lang]
    c_desc = cdata["desc"][lang]
    c_icon = cdata["icon"]
    c_color = cdata["color"]
    c_href = cat_href(cat_en, lang)
    c_slug = cdata["slug"][lang]

    BROWSE_CAT  = {"en":"Browse Category","fr":"Catégorie","es":"Categoría","it":"Categoria","de":"Kategorie","nl":"Categorie","ar":"تصفح الفئة"}
    ART_IN_CAT  = {"en":"Articles in this category","fr":"Articles de cette catégorie",
                   "es":"Artículos de esta categoría","it":"Articoli in questa categoria",
                   "de":"Artikel in dieser Kategorie","nl":"Artikelen in deze categorie","ar":"مقالات في هذه الفئة"}
    OTHER_CATS  = {"en":"Other Categories","fr":"Autres catégories","es":"Otras categorías",
                   "it":"Altre categorie","de":"Andere Kategorien","nl":"Andere categorieën","ar":"فئات أخرى"}
    BC          = {"en":"Home","fr":"Accueil","es":"Inicio","it":"Home","de":"Start","nl":"Home","ar":"الرئيسية"}
    BL          = {"en":"Blog","fr":"Blog","es":"Blog","it":"Blog","de":"Blog","nl":"Blog","ar":"المدونة"}
    ART_LBL     = {"en":"articles","fr":"articles","es":"artículos","it":"articoli","de":"Artikel","nl":"artikelen","ar":"مقالات"}
    BOOK        = {"en":"Book Your Stay","fr":"Réserver","es":"Reservar","it":"Prenota","de":"Buchen","nl":"Boek nu","ar":"احجز الآن"}
    CTA_H       = {"en":"Ready to Surf Ngor?","fr":"Prêt à surfer à Ngor ?","es":"¿Listo para surfear en Ngor?",
                   "it":"Pronto a surfare a Ngor?","de":"Bereit für Ngor?","nl":"Klaar voor Ngor?","ar":"هل أنت مستعد لـ Ngor؟"}
    CTA_SUB     = {"en":"Join us on Ngor Island — surf lessons, coaching, and an unforgettable Senegal experience.",
                   "fr":"Rejoignez-nous sur l'île de Ngor — cours de surf, coaching et une expérience Sénégal inoubliable.",
                   "es":"Únete a nosotros en la isla de Ngor — clases de surf, coaching y una experiencia inolvidable en Senegal.",
                   "it":"Unisciti a noi sull'isola di Ngor — lezioni di surf, coaching e un'esperienza indimenticabile in Senegal.",
                   "de":"Besuche uns auf Ngor Island — Surfunterricht, Coaching und ein unvergessliches Senegal-Erlebnis.",
                   "nl":"Word lid op Ngor Island — surflessen, coaching en een onvergetelijke Senegal-ervaring.",
                   "ar":"انضم إلينا في جزيرة Ngor — دروس تصفح وتدريب وتجربة سنغالية لا تُنسى."}

    # Articles in this category
    cat_arts = [a for a in arts_en if a.get("category") == cat_en]
    count = len(cat_arts)

    # Article cards
    cards = ""
    for en_art in cat_arts:
        en_s     = en_art["slug"]
        a        = arts_by_lang[lang].get(en_s, en_art) if lang!="en" else en_art
        t        = fix_em(a.get("title", en_art["title"]))[:80]
        m        = fix_em(a.get("meta_description",""))[:130]
        feat     = "★ " if en_art.get("type") == "hero" else ""
        cards += f'''<a href="{pfx}/blog/{en_s}/" class="card blog-card" style="text-decoration:none" aria-label="{t}">
      <div class="blog-card-img-wrap">
        <img src="{art_img(en_s)}" alt="{t}" class="card-img" loading="lazy" width="800" height="530" decoding="async" onerror="this.src='{FALLBACK_IMG}'">
      </div>
      <div class="card-body">
        <h3 class="card-h3" style="font-size:15px;margin:8px 0 6px;line-height:1.35">{feat}{t}</h3>
        <p class="card-text" style="font-size:13px;color:#6b7280;margin:0">{m}</p>
      </div>
    </a>\n'''

    # Other categories
    other_cats_html = ""
    for other_en, other_data in BLOG_CATS_DATA.items():
        if other_en == cat_en: continue
        o_href     = cat_href(other_en, lang)
        o_name     = other_data["name"][lang]
        o_ico_name = other_data.get("ico_name", "icon-surf-guide")
        o_ico_html = ico(o_ico_name, 40)
        o_color    = other_data["color"]
        o_count    = sum(1 for a in arts_en if a.get("category") == other_en)
        other_cats_html += f'''
        <a href="{o_href}" class="cat-card" style="text-decoration:none;border-top:3px solid {o_color}">
          <div class="cat-card-icon-wrap" style="width:56px;height:56px;border-radius:14px;background:{o_color}18;display:flex;align-items:center;justify-content:center;margin-bottom:14px;flex-shrink:0">{o_ico_html}</div>
          <h3 class="cat-card-name">{o_name}</h3>
          <span class="cat-card-count" style="color:{o_color};font-weight:700;font-size:13px">{o_count} {ART_LBL[lang]}</span>
        </a>'''

    # hreflang for this category page
    hrl_parts = [f'<link rel="alternate" hreflang="x-default" href="{SITE_URL}{cat_href(cat_en, "en")}">']
    for l in LANGS:
        hrl_parts.append(f'<link rel="alternate" hreflang="{LANG_LOCALE[l]}" href="{SITE_URL}{cat_href(cat_en, l)}">')
    hrl = "\n".join(hrl_parts)
    can = f'<link rel="canonical" href="{SITE_URL}{c_href}">'

    page_title = f"{c_name} | Blog | Ngor Surfcamp Teranga"
    meta_desc  = c_desc[:155]

    # JSON-LD breadcrumb
    crumb_ld = f'''<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
  {{"@type":"ListItem","position":1,"name":"{BC[lang]}","item":"{SITE_URL}{pfx}/"}},
  {{"@type":"ListItem","position":2,"name":"{BL[lang]}","item":"{SITE_URL}{pfx}/blog/"}},
  {{"@type":"ListItem","position":3,"name":"{c_name}","item":"{SITE_URL}{c_href}"}}
]}}
</script>'''

    breadcrumb = (
        f'<nav class="breadcrumb" aria-label="breadcrumb">'
        f'<a href="{pfx}/">{BC[lang]}</a>'
        f'<span aria-hidden="true">›</span>'
        f'<a href="{pfx}/blog/">{BL[lang]}</a>'
        f'<span aria-hidden="true">›</span>'
        f'<span aria-current="page">{c_name}</span>'
        f'</nav>'
    )

    html = head_html(page_title, meta_desc, lang, can, hrl, FALLBACK_IMG, og_alt=c_name)
    html = html.replace("</head>", crumb_ld + "\n</head>", 1)
    fq_block = get_footer_quotes(lang)
    # Build per-language URLs for the lang switcher so each flag points to the
    # correct category page in that language (not a naive slug swap)
    _cat_lang_urls = {l: cat_href(cat_en, l) for l in LANGS}
    html += nav_html("blog", lang, pfx, f"/blog/{CAT_SLUG_WORD[lang]}/{c_slug}", lang_urls=_cat_lang_urls)
    c_ico_name  = cdata.get("ico_name", "icon-surf-guide")
    c_ico_html  = ico(c_ico_name, 48)
    html += f"""
<main>
  <header class="blog-hub-header" role="banner">
    <div class="container" style="text-align:center;padding:52px 24px 64px">
      <div style="margin-bottom:12px">
        <span style="display:inline-block;font-size:11px;font-weight:800;letter-spacing:0.16em;text-transform:uppercase;color:rgba(240,192,96,0.9)">{BROWSE_CAT[lang]}</span>
      </div>
      <div style="margin-bottom:16px;display:inline-flex;align-items:center;justify-content:center;width:68px;height:68px;border-radius:16px;background:{c_color}28;border:1px solid {c_color}40">{c_ico_html}</div>
      <h1 style="font-size:clamp(24px,4vw,44px);margin:8px 0 12px;color:#fff;line-height:1.1;font-weight:900">{c_name}</h1>
      <p style="font-size:15px;color:rgba(255,255,255,0.76);max-width:520px;margin:0 auto;line-height:1.6">{c_desc[:160]}</p>
    </div>
    <div class="wave-bottom" aria-hidden="true"><svg viewBox="0 0 1440 52" fill="none" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none"><path d="M0 0 C360 52,1080 52,1440 0 L1440 52 L0 52Z" fill="#f9fafb"/></svg></div>
  </header>

  <!-- Breadcrumb + article count -->
  <div style="background:#f9fafb;border-bottom:1px solid #e5e7eb;padding:14px 0">
    <div class="container" style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px">
      {breadcrumb}
      <span style="font-size:14px;color:#6b7280"><strong style="color:var(--navy)">{count}</strong> {ART_LBL[lang]}</span>
    </div>
  </div>

  <!-- Articles grid -->
  <section class="section" aria-label="{ART_IN_CAT[lang]}" style="padding-top:48px">
    <div class="container">
      <h2 class="s-title reveal" style="margin-bottom:40px">{ART_IN_CAT[lang]}</h2>
      <div class="blog-grid reveal">{cards}</div>
    </div>
  </section>

  <!-- CTA -->
  <section class="section sec-dark" style="padding:64px 0" aria-label="CTA">
    <div class="container" style="text-align:center">
      <h2 style="font-size:clamp(22px,3.5vw,38px);margin-bottom:12px;color:#fff">{CTA_H[lang]}</h2>
      <p style="color:rgba(255,255,255,0.8);margin-bottom:32px;font-size:16px;max-width:560px;margin-left:auto;margin-right:auto">{CTA_SUB[lang]}</p>
      <div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap">
        <a href="{pfx}/booking/" class="btn btn-fire btn-lg">{BOOK[lang]}</a>
        <a href="https://wa.me/221789257025" target="_blank" class="btn btn-glass btn-lg"><span style="display:inline-flex">{WA_ICO}</span> WhatsApp</a>
      </div>
    </div>
  </section>

  <!-- Other categories -->
  <section class="section sec-sand" style="padding:48px 0" aria-label="{OTHER_CATS[lang]}">
    <div class="container">
      <h2 class="s-title reveal" style="margin-bottom:32px">{OTHER_CATS[lang]}</h2>
      <div class="cat-cards-grid">
        {other_cats_html}
      </div>
    </div>
  </section>
</main>
{fq_block}"""
    html += footer_html(lang, pfx)
    html += "\n</body>\n</html>"
    return html


def write_page(path, html):
    """Write an HTML page, creating directories as needed."""
    full = DEMO_DIR + path
    if full.endswith("/"): full += "index.html"
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(html)


print("\n=== Rebuilding all article pages with fixed blocks ===")
total = 0
for lang in LANGS:
    pfx  = LANG_PREFIX[lang]
    spfx = f"/{lang}" if lang!="en" else ""
    for en_art in arts_en:
        out_dir = f"{DEMO_DIR}{spfx}/blog/{en_art['slug']}"
        os.makedirs(out_dir, exist_ok=True)
        html = build_article(en_art, lang)
        with open(f"{out_dir}/index.html","w") as f: f.write(html)
        total += 1
    print(f"  ✅ {lang}: {len(arts_en)} articles")

print(f"\nTotal: {total} article pages rebuilt")

print("\n=== Rebuilding blog index pages ===")
for lang in LANGS:
    spfx = f"/{lang}" if lang!="en" else ""
    write_page(f"{spfx}/blog/", build_blog_index(lang))
    print(f"  ✅ {lang}: /blog/ index")

print("\n=== Building category pages ===")
cat_total = 0
for cat_en in BLOG_CATS_DATA:
    for lang in LANGS:
        spfx     = f"/{lang}" if lang!="en" else ""
        cdata    = BLOG_CATS_DATA[cat_en]
        c_slug   = cdata["slug"][lang]
        cat_word = CAT_SLUG_WORD[lang]
        out_path = f"{spfx}/blog/{cat_word}/{c_slug}/"
        write_page(out_path, build_category_page(cat_en, lang))
        cat_total += 1
    print(f"  ✅ '{cat_en}': {len(LANGS)} language pages")
print(f"  Total: {cat_total} category pages")

print("\n✅ Block fix + category pages complete!")
