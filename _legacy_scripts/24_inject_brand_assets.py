"""
Inject brand badge assets into the site:
- Background watermarks on key sections
- Decorative elements in headers
- Icon strip on homepage
- Pattern backgrounds
- Badge showcase section on homepage
"""
import os, json, re

DEMO_DIR  = "/Users/simonazoulay/SurfCampSenegal/cloudflare-demo"
BRAND_DIR = f"{DEMO_DIR}/assets/images/brand"
SITE_URL  = "https://ngor-surfcamp-demo.pages.dev"

# Load existing badge metadata
badges_meta = json.load(open(f"{BRAND_DIR}/badges.json"))
badge_files = [f for f in os.listdir(BRAND_DIR) if f.endswith(".png") and f != "badges.json"]

print(f"Badges available: {len(badge_files)}")

# ════════════════════════════════════════════════════════════════════════════════
# CSS FOR BRAND ASSETS
# ════════════════════════════════════════════════════════════════════════════════
BRAND_CSS = """
/* ══════════════════════════════════════════════════════
   BRAND ASSETS — Badge decorations
══════════════════════════════════════════════════════ */

/* Badge strip (horizontal scrolling row) */
.badge-strip {
  overflow: hidden;
  padding: 32px 0;
  background: var(--navy);
  position: relative;
}
.badge-strip::before,.badge-strip::after {
  content: '';
  position: absolute;
  top: 0; bottom: 0;
  width: 80px;
  z-index: 2;
}
.badge-strip::before {
  left: 0;
  background: linear-gradient(to right, var(--navy), transparent);
}
.badge-strip::after {
  right: 0;
  background: linear-gradient(to left, var(--navy), transparent);
}
.badge-strip-inner {
  display: flex;
  gap: 32px;
  width: max-content;
  animation: badgeScroll 40s linear infinite;
}
.badge-strip-inner:hover { animation-play-state: paused; }
@keyframes badgeScroll {
  from { transform: translateX(0); }
  to   { transform: translateX(-50%); }
}
.badge-item {
  width: 100px;
  height: 100px;
  flex-shrink: 0;
  opacity: 0.75;
  transition: opacity 0.3s, transform 0.3s;
  filter: brightness(0.9);
}
.badge-item:hover {
  opacity: 1;
  transform: scale(1.1) rotate(5deg);
}
.badge-item img {
  width: 100%; height: 100%;
  object-fit: contain;
  border-radius: 50%;
}

/* Watermark badges as section backgrounds */
.badge-watermark {
  position: absolute;
  opacity: 0.04;
  pointer-events: none;
  user-select: none;
  z-index: 0;
}
.badge-watermark img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: invert(1);
}

/* Section positions for watermarks */
.sec-with-badge { position: relative; overflow: hidden; }

/* Badge showcase grid */
.badge-showcase {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
  gap: 20px;
  padding: 40px 0;
}
.badge-showcase-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: transform 0.3s;
}
.badge-showcase-item:hover { transform: scale(1.08) rotate(3deg); }
.badge-showcase-item img {
  width: 90px; height: 90px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid rgba(255,255,255,0.1);
  box-shadow: 0 4px 16px rgba(0,0,0,0.3);
}
.badge-showcase-item span {
  font-size: 10px;
  color: rgba(255,255,255,0.5);
  text-align: center;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

/* Hero corner badge */
.hero-badge-corner {
  position: absolute;
  bottom: 100px;
  right: 5%;
  width: 120px;
  height: 120px;
  z-index: 4;
  opacity: 0.65;
  animation: floatUp 7s ease-in-out infinite;
  filter: drop-shadow(0 4px 12px rgba(0,0,0,0.4));
}
.hero-badge-corner img {
  width: 100%; height: 100%;
  object-fit: contain;
}
@keyframes floatUp {
  0%,100%{ transform: translateY(0) rotate(-3deg); }
  50%{ transform: translateY(-18px) rotate(3deg); }
}

/* Section divider badges */
.sec-badge-divider {
  display: flex;
  justify-content: center;
  padding: 24px 0;
  opacity: 0.3;
}
.sec-badge-divider img {
  width: 60px; height: 60px;
  object-fit: contain;
  filter: invert(1);
}

/* Floating mini badges on dark sections */
.float-badge {
  position: absolute;
  pointer-events: none;
  opacity: 0.08;
  animation: floatUp 8s ease-in-out infinite;
}
.float-badge img { width:100%; height:100%; object-fit:contain; filter:brightness(10); }

/* Responsive */
@media(max-width:768px){
  .hero-badge-corner{width:80px;height:80px;bottom:80px;right:16px;}
  .badge-item{width:70px;height:70px;}
  .badge-showcase-item img{width:65px;height:65px;}
}
"""

with open(f"{DEMO_DIR}/assets/css/style.css","a") as f:
    f.write("\n" + BRAND_CSS)
print("✅ Brand CSS added")

# ════════════════════════════════════════════════════════════════════════════════
# HTML SNIPPETS to inject
# ════════════════════════════════════════════════════════════════════════════════

# Infinite scroll badge strip
def badge_strip_html():
    """Scrolling strip of all 16 badges"""
    items = ""
    for b in ["badge-surfer-wave","badge-surfboard-paddle","badge-crossed-boards","badge-compass-surf",
              "badge-ngor-palms","badge-ngor-lighthouse","badge-teranga-spirit","badge-ngor-pirogue",
              "badge-anchor-waves","badge-shark-fin","badge-cowrie-shells","badge-sere",
              "badge-ngor-right","badge-endless-summer","badge-federation","badge-atlantic-wave"]:
        items += f'<div class="badge-item"><img src="/assets/images/brand/{b}.png" alt="{b}" loading="lazy"></div>\n'
    # Duplicate for seamless loop
    all_items = items + items
    return f"""<div class="badge-strip" aria-hidden="true">
  <div class="badge-strip-inner">{all_items}</div>
</div>"""

# Corner hero badge
def hero_corner_badge(badge_id="badge-ngor-pirogue"):
    return f'<div class="hero-badge-corner" aria-hidden="true"><img src="/assets/images/brand/{badge_id}.png" alt="" loading="lazy"></div>'

# Section watermark
def section_watermark(badge_id, size=300, top="50%", right="-5%"):
    return f'<div class="badge-watermark" style="width:{size}px;height:{size}px;top:{top};right:{right};transform:translateY(-50%)" aria-hidden="true"><img src="/assets/images/brand/{badge_id}.png" alt="" loading="lazy"></div>'

# Two floating badges on dark sections
def floating_badges(b1, b2, size1=200, size2=150):
    return f'''<div class="float-badge" style="width:{size1}px;height:{size1}px;bottom:-30px;left:-20px;animation-delay:0s" aria-hidden="true"><img src="/assets/images/brand/{b1}.png" alt="" loading="lazy"></div>
<div class="float-badge" style="width:{size2}px;height:{size2}px;top:-20px;right:-10px;animation-delay:3s" aria-hidden="true"><img src="/assets/images/brand/{b2}.png" alt="" loading="lazy"></div>'''

# Badge showcase (for about / brand section)
def badge_showcase_html(bg_dark=True):
    text_color = "rgba(255,255,255,0.5)" if bg_dark else "rgba(10,37,64,0.5)"
    items = ""
    BADGE_LABELS = {
        "badge-surfer-wave": "Surfing",
        "badge-surfboard-paddle": "Boards",
        "badge-crossed-boards": "Gear",
        "badge-compass-surf": "Navigate",
        "badge-ngor-palms": "Ngor Island",
        "badge-ngor-lighthouse": "Lighthouse",
        "badge-teranga-spirit": "Teranga",
        "badge-ngor-pirogue": "Pirogue",
        "badge-anchor-waves": "Est. 2025",
        "badge-shark-fin": "Senegal",
        "badge-cowrie-shells": "Culture",
        "badge-sere": "Sèrè",
        "badge-ngor-right": "Ngor Right",
        "badge-endless-summer": "1964",
        "badge-federation": "Licensed",
        "badge-atlantic-wave": "Atlantic",
    }
    for bid, label in BADGE_LABELS.items():
        items += f'''<div class="badge-showcase-item" title="{label}">
  <img src="/assets/images/brand/{bid}.png" alt="{label}" loading="lazy">
  <span style="color:{text_color}">{label}</span>
</div>\n'''
    return f'<div class="badge-showcase">{items}</div>'

# ════════════════════════════════════════════════════════════════════════════════
# PATCH HOMEPAGE — inject badge strip + corner badge + watermarks
# ════════════════════════════════════════════════════════════════════════════════
def patch_homepage(filepath, lang="en"):
    if not os.path.exists(filepath):
        print(f"  skip (not found): {filepath}")
        return

    with open(filepath) as f:
        html = f.read()

    # 1. Add corner badge to hero
    hero_close = '<div class="hero-waves"'
    corner = hero_corner_badge("badge-ngor-pirogue") + "\n"
    if "hero-badge-corner" not in html and hero_close in html:
        html = html.replace(hero_close, corner + "  " + hero_close)

    # 2. Add badge strip after stats bar
    stats_end = "</div>\n\n  <!-- ABOUT SPLIT -->"
    strip = "\n\n" + badge_strip_html() + "\n"
    if "badge-strip" not in html and stats_end in html:
        html = html.replace(stats_end, "</div>" + strip + "\n  <!-- ABOUT SPLIT -->")

    # 3. Add watermark on about section
    about_split = '<div class="split reveal">'
    watermark = section_watermark("badge-teranga-spirit", 280, "50%", "-4%") + "\n"
    if "badge-watermark" not in html and about_split in html:
        html = html.replace(about_split, watermark + "      " + about_split, 1)

    # 4. Add floating badges on CTA band
    cta_band_inner = '<div class="container">\n      <h2>' + ({"en":"Ready","fr":"Prêt","es":"Listo","it":"Pronto","de":"Bereit"}[lang])
    floats = floating_badges("badge-anchor-waves","badge-compass-surf") + "\n"
    if "float-badge" not in html and cta_band_inner in html:
        html = html.replace('<div class="cta-band">', '<div class="cta-band" style="position:relative;overflow:hidden">\n  ' + floats)

    # 5. Before footer: add brand showcase section (EN only)
    if lang == "en" and "badge-showcase" not in html:
        showcase_section = f"""
<!-- Brand Universe -->
<section style="background:var(--navy);padding:60px 0 48px;position:relative;overflow:hidden">
  {floating_badges('badge-teranga-spirit','badge-ngor-right',250,180)}
  <div class="container" style="position:relative;z-index:1;text-align:center">
    <span class="s-label" style="color:var(--sand)">Our Universe</span>
    <h2 style="color:#fff;font-size:clamp(22px,3vw,36px);margin-bottom:8px">The Ngor World</h2>
    <p style="color:rgba(255,255,255,0.6);font-size:15px;margin-bottom:0">Waves, culture, community — West Africa's finest surf experience</p>
    {badge_showcase_html(True)}
  </div>
</section>\n"""
        html = html.replace("<footer>", showcase_section + "<footer>", 1)

    with open(filepath, "w") as f:
        f.write(html)
    print(f"  ✅ Patched: {filepath[-60:]}")

# ════════════════════════════════════════════════════════════════════════════════
# PATCH ALL PAGES
# ════════════════════════════════════════════════════════════════════════════════
print("\n=== Patching all homepages ===")
for lang in ["en","fr","es","it","de"]:
    pfx = {"en":"","fr":"/fr","es":"/es","it":"/it","de":"/de"}[lang]
    path = f"{DEMO_DIR}{pfx}/index.html"
    patch_homepage(path, lang)

# Patch static pages with subtle watermarks
def add_watermark_to_page(filepath, badge_id, size=300):
    if not os.path.exists(filepath): return
    with open(filepath) as f:
        html = f.read()
    if "badge-watermark" in html: return
    wm = section_watermark(badge_id, size, "30%", "-3%")
    # Insert after page-header or first section
    for marker in ['<section class="section">', '<section class="section sec-light">']:
        if marker in html:
            html = html.replace(marker, f'<section class="section sec-with-badge" style="position:relative">\n{wm}', 1)
            break
    with open(filepath, "w") as f:
        f.write(html)

print("\n=== Adding watermarks to static pages ===")
PAGE_BADGES = {
    "surf-house": "badge-ngor-palms",
    "island":     "badge-teranga-spirit",
    "surfing":    "badge-ngor-right",
    "booking":    "badge-anchor-waves",
    "gallery":    "badge-surfer-wave",
    "faq":        "badge-compass-surf",
}
for lang in ["en","fr","es","it","de"]:
    pfx = {"en":"","fr":"/fr","es":"/es","it":"/it","de":"/de"}[lang]
    for page, badge in PAGE_BADGES.items():
        path = f"{DEMO_DIR}{pfx}/{page}/index.html"
        add_watermark_to_page(path, badge)
print(f"  ✅ Watermarks added to all static pages")

# ════════════════════════════════════════════════════════════════════════════════
# ALSO COPY REFERENCE IMAGE to assets
# ════════════════════════════════════════════════════════════════════════════════
import shutil
ref_img = "/Users/simonazoulay/.cursor/projects/Users-simonazoulay-SurfCampSenegal/assets/Gemini_Generated_Image_m12a5nm12a5nm12a-b67200b9-6e56-4d6f-9e21-091d6f948991.png"
if os.path.exists(ref_img):
    shutil.copy2(ref_img, f"{BRAND_DIR}/reference-style.png")
    print("✅ Reference image copied")

print(f"\n✅ Brand assets injection complete!")
print(f"Badges: {BRAND_DIR}")
