"""
Redesign stats section + fix hero/stats transition on homepage.
"""
import os, re, json

DEMO_DIR = "/Users/simonazoulay/SurfCampSenegal/cloudflare-demo"
LANGS    = ["en","fr","es","it","de"]
LANG_PREFIX = {"en":"","fr":"/fr","es":"/es","it":"/it","de":"/de"}

# ── New stats CSS ─────────────────────────────────────────────────────────────
STATS_CSS = """
/* ══ STATS BAR — v2 ════════════════════════════════════ */
.stats-bar {
  padding: 0;
  background: transparent;
  position: relative;
  z-index: 2;
  margin-top: -2px;
}
.stats-inner-wrap {
  background: linear-gradient(to right, #0a2540, #0c2e50, #0a2540);
  border-top: 1px solid rgba(255,255,255,0.07);
  border-bottom: 1px solid rgba(255,255,255,0.07);
  padding: 0;
}
.stats-inner {
  max-width: 1240px;
  margin: 0 auto;
  padding: 0 28px;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0;
}
.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 44px 20px;
  position: relative;
  text-align: center;
  border-right: 1px solid rgba(255,255,255,0.06);
}
.stat:last-child { border-right: none; }
.stat::before {
  content: '';
  position: absolute;
  bottom: 0; left: 20%; right: 20%; height: 2px;
  background: linear-gradient(90deg, transparent, var(--fire), transparent);
  opacity: 0;
  transition: opacity 0.4s;
}
.stat:hover::before { opacity: 1; }
.stat-icon {
  width: 40px; height: 40px;
  border-radius: 12px;
  background: rgba(255,107,53,0.12);
  border: 1px solid rgba(255,107,53,0.20);
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 14px;
  font-size: 18px;
  transition: transform 0.3s, background 0.3s;
}
.stat:hover .stat-icon {
  transform: scale(1.1) rotate(5deg);
  background: rgba(255,107,53,0.20);
}
.stat-n {
  font-family: var(--fh);
  font-size: clamp(36px, 4.5vw, 56px);
  font-weight: 900;
  line-height: 1;
  letter-spacing: -0.03em;
  background: linear-gradient(135deg, #fff 0%, var(--sand) 60%, #fff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  display: block;
  margin-bottom: 8px;
  transition: transform 0.3s;
}
.stat:hover .stat-n { transform: scale(1.05); }
.stat-l {
  font-size: 10.5px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: rgba(255,255,255,0.40);
  display: block;
  font-weight: 600;
}
@media(max-width: 768px) {
  .stats-inner {
    grid-template-columns: 1fr 1fr;
  }
  .stat {
    padding: 32px 16px;
    border-right: 1px solid rgba(255,255,255,0.06);
    border-bottom: 1px solid rgba(255,255,255,0.06);
  }
  .stat:nth-child(2n) { border-right: none; }
  .stat:nth-child(3), .stat:nth-child(4) { border-bottom: none; }
  .stat-n { font-size: 36px; }
}
@media(max-width: 480px) {
  .stats-inner { grid-template-columns: repeat(2, 1fr); }
}
"""

css_path = f"{DEMO_DIR}/assets/css/style.css"
with open(css_path) as f: css = f.read()
with open(css_path,"a") as f:
    f.write("\n/* stats v2 override */\n" + STATS_CSS)
print("✅ Stats CSS added")

# ── Build new stats HTML per lang ─────────────────────────────────────────────
STAT_ITEMS = {
    "en": [
        ("🌊", "3",   "Waves"),
        ("🏄", "All", "All Levels"),
        ("⭐", "5★",  "Rating"),
        ("📽", "1964","Endless Summer"),
    ],
    "fr": [
        ("🌊", "3",   "Vagues"),
        ("🏄", "All", "Tous Niveaux"),
        ("⭐", "5★",  "Note"),
        ("📽", "1964","Endless Summer"),
    ],
    "es": [
        ("🌊", "3",   "Olas"),
        ("🏄", "All", "Todos Niveles"),
        ("⭐", "5★",  "Valoración"),
        ("📽", "1964","Endless Summer"),
    ],
    "it": [
        ("🌊", "3",   "Onde"),
        ("🏄", "All", "Tutti i Livelli"),
        ("⭐", "5★",  "Valutazione"),
        ("📽", "1964","Endless Summer"),
    ],
    "de": [
        ("🌊", "3",   "Wellen"),
        ("🏄", "All", "Alle Level"),
        ("⭐", "5★",  "Bewertung"),
        ("📽", "1964","Endless Summer"),
    ],
}

def build_stats(lang):
    items = STAT_ITEMS.get(lang, STAT_ITEMS["en"])
    cells = ""
    for icon, val, label in items:
        # data-target only for numeric values
        target_attr = ""
        if val.replace("★","").replace(".","").isdigit():
            num = val.replace("★","")
            suffix = "★" if "★" in val else ""
            target_attr = f' data-target="{num}" data-suffix="{suffix}"'
        cells += f"""<div class="stat">
  <div class="stat-icon">{icon}</div>
  <span class="stat-n"{target_attr}>{val}</span>
  <span class="stat-l">{label}</span>
</div>"""
    return f"""<div class="stats-bar" role="region" aria-label="Key figures">
  <div class="stats-inner-wrap">
    <div class="stats-inner">{cells}</div>
  </div>
</div>"""

# ── Patch all homepage HTML files ─────────────────────────────────────────────
print("\n=== Patching stats section in all homepages ===")

OLD_STATS_PATTERN = re.compile(
    r'<!-- Stats.*?</div>\s*</div>\s*</div>',
    re.DOTALL
)
OLD_STATS_SIMPLE = re.compile(
    r'<div class="stats-bar"[^>]*>.*?</div>\s*\n\s*\n',
    re.DOTALL
)

for lang in LANGS:
    pfx  = LANG_PREFIX[lang]
    hp   = f"{DEMO_DIR}{pfx}/index.html"
    if not os.path.exists(hp): continue

    with open(hp) as f: html = f.read()
    new_stats = build_stats(lang)

    # Try to find and replace the existing stats section
    # Pattern: starts with <!-- Stats --> or <div class="stats-bar"
    replaced = False

    # Method 1: replace the old stats-inner div structure
    old_start = html.find('<div class="stats-bar"')
    if old_start > 0:
        # Find the closing of the outer div
        # Stats bar wraps: stats-bar > stats-inner > stat items
        depth = 0
        idx = old_start
        while idx < len(html):
            if html[idx:idx+4] == '<div': depth += 1
            elif html[idx:idx+6] == '</div': depth -= 1
            if depth == 0:
                old_end = idx + 6  # past </div>
                # Also consume trailing newlines
                while old_end < len(html) and html[old_end] in '\n\r ':
                    old_end += 1
                html = html[:old_start] + new_stats + "\n\n  " + html[old_end:]
                replaced = True
                break
            idx += 1

    if not replaced:
        print(f"  ⚠️  Could not find stats in {lang}")
    else:
        with open(hp,"w") as f: f.write(html)
        print(f"  ✅ {lang}: stats updated")

# ── Verify ─────────────────────────────────────────────────────────────────────
with open(f"{DEMO_DIR}/index.html") as f: test = f.read()
has_new = "stats-inner-wrap" in test
has_old_float = "3.0" in test or "5.0" in test
print(f"\nVerification: new stats={'✅' if has_new else '❌'} | old float='{'❌ none' if not has_old_float else '⚠️ still present'}'")
print("✅ Done!")
