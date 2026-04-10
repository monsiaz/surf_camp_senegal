#!/usr/bin/env python3
"""
Build enhanced gallery pages with:
- 161 new AI-labeled WebP images
- Tag filter buttons (surfcamp, surf, coaching, people, island, food, sunset, aerial, water)
- Masonry grid with lightbox
- Progressive loading
"""
import json, os, re
from pathlib import Path

ROOT     = Path(__file__).parent.parent
DEMO_DIR = ROOT / "cloudflare-demo"
MANIFEST = DEMO_DIR / "assets" / "images" / "gallery" / "manifest.json"

# Per-language tag labels — updated for new AI Vision taxonomy
TAG_LABELS = {
    "en": {
        "all": "All", "surf_action": "Surf & Waves", "surf_house": "Surf House",
        "surf_coaching": "Coaching", "people_vibe": "Community", "island_life": "Island Life",
        "food": "Food & Dining", "sunset": "Sunset", "pool": "Pool", "surf_gear": "Boards & Gear",
        "gallery_title": "Photo Gallery",
        "filter_label": "Filter by",
        "photos_count": "photos",
    },
    "fr": {
        "all": "Tout", "surf_action": "Surf & Vagues", "surf_house": "Surf House",
        "surf_coaching": "Coaching", "people_vibe": "Convivialité", "island_life": "Vie sur l'île",
        "food": "Cuisine", "sunset": "Coucher de soleil", "pool": "Piscine", "surf_gear": "Planches & Équipement",
        "gallery_title": "Galerie Photos",
        "filter_label": "Filtrer par",
        "photos_count": "photos",
    },
    "es": {
        "all": "Todo", "surf_action": "Surf & Olas", "surf_house": "Surf House",
        "surf_coaching": "Coaching", "people_vibe": "Comunidad", "island_life": "Vida en la isla",
        "food": "Gastronomía", "sunset": "Puesta de sol", "pool": "Piscina", "surf_gear": "Tablas y equipo",
        "gallery_title": "Galería de Fotos",
        "filter_label": "Filtrar por",
        "photos_count": "fotos",
    },
    "it": {
        "all": "Tutto", "surf_action": "Surf & Onde", "surf_house": "Surf House",
        "surf_coaching": "Coaching", "people_vibe": "Comunità", "island_life": "Vita sull'isola",
        "food": "Cucina", "sunset": "Tramonto", "pool": "Piscina", "surf_gear": "Tavole e attrezzatura",
        "gallery_title": "Galleria Fotografica",
        "filter_label": "Filtra per",
        "photos_count": "foto",
    },
    "de": {
        "all": "Alle", "surf_action": "Surf & Wellen", "surf_house": "Surf House",
        "surf_coaching": "Coaching", "people_vibe": "Gemeinschaft", "island_life": "Inselleben",
        "food": "Essen & Genuss", "sunset": "Sonnenuntergang", "pool": "Pool", "surf_gear": "Boards & Equipment",
        "gallery_title": "Fotogalerie",
        "filter_label": "Filtern nach",
        "photos_count": "Fotos",
    },
    "nl": {
        "all": "Alles", "surf_action": "Surf & Golven", "surf_house": "Surf House",
        "surf_coaching": "Coaching", "people_vibe": "Gemeenschap", "island_life": "Eilandleven",
        "food": "Eten & Drinken", "sunset": "Zonsondergang", "pool": "Zwembad", "surf_gear": "Boards & uitrusting",
        "gallery_title": "Fotogalerij",
        "filter_label": "Filteren op",
        "photos_count": "foto's",
    },
    "ar": {
        "all": "الكل", "surf_action": "ركوب الأمواج", "surf_house": "بيت السيرف",
        "surf_coaching": "التدريب", "people_vibe": "المجتمع", "island_life": "حياة الجزيرة",
        "food": "الطعام والشراب", "sunset": "غروب الشمس", "pool": "المسبح", "surf_gear": "اللوح والمعدات",
        "gallery_title": "معرض الصور",
        "filter_label": "تصفية حسب",
        "photos_count": "صور",
    },
    "pt": {
        "all": "Todos", "surf_action": "Surf & Ondas", "surf_house": "Surf House",
        "surf_coaching": "Coaching", "people_vibe": "Comunidade", "island_life": "Vida na ilha",
        "food": "Gastronomia", "sunset": "Pôr do sol", "pool": "Piscina", "surf_gear": "Pranchas e equipamento",
        "gallery_title": "Galeria de Fotos",
        "filter_label": "Filtrar por",
        "photos_count": "fotos",
    },
    "da": {
        "all": "Alle", "surf_action": "Surf & Bølger", "surf_house": "Surf House",
        "surf_coaching": "Coaching", "people_vibe": "Fællesskab", "island_life": "Ølivet",
        "food": "Mad og drikke", "sunset": "Solnedgang", "pool": "Swimmingpool", "surf_gear": "Brætter og udstyr",
        "gallery_title": "Fotogalleri",
        "filter_label": "Filtrer efter",
        "photos_count": "fotos",
    },
}

TAGS_ORDER = ["surf_action", "surf_house", "surf_coaching", "people_vibe", "island_life", "food", "sunset", "pool", "surf_gear"]

GALLERY_PAGES = {
    "en": "gallery/index.html",
    "fr": "fr/galerie/index.html",
    "es": "es/galeria/index.html",
    "it": "it/galleria/index.html",
    "de": "de/galerie/index.html",
    "nl": "nl/galerij/index.html",
    "ar": "ar/galerie/index.html",
    "pt": "pt/galeria/index.html",
    "da": "da/galleri/index.html",
}


def build_filter_bar(lang: str, labels: dict) -> str:
    tags_html = f'<button class="gal-tag active" data-tag="all">{labels["all"]}</button>\n'
    for tag in TAGS_ORDER:
        if tag in labels:
            tags_html += f'    <button class="gal-tag" data-tag="{tag}">{labels[tag]}</button>\n'
    return f"""
  <div class="gallery-filter-bar reveal">
    <span class="gallery-filter-label">{labels["filter_label"]} :</span>
    <div class="gallery-tag-btns">
    {tags_html}    </div>
  </div>"""


def build_image_grid(images: list) -> str:
    items = []
    for img in images:
        tags = img.get("tags", [])
        tags_attr = " ".join(tags)
        caption = img.get("caption", "")
        src = img.get("src", "")
        w = img.get("w", 800)
        h = img.get("h", 600)
        q = img.get("quality", 5)
        # Only include quality >= 5
        if q < 5:
            continue
        loading = "eager" if items == [] else "lazy"
        items.append(
            f'<button type="button" class="gallery-item reveal" role="listitem" '
            f'data-full="{src}" data-tags="{tags_attr}" '
            f'aria-label="{caption or "Gallery photo"}">'
            f'<span class="gallery-item-inner">'
            f'<img src="{src}" alt="{caption}" width="{w}" height="{h}" loading="{loading}" decoding="async">'
            f'</span></button>'
        )
    return "\n".join(items)


FILTER_CSS = """
/* ── Gallery Filter Bar v2 ── */
.gallery-filter-bar{position:sticky;top:68px;z-index:30;display:flex;align-items:center;gap:12px;padding:13px 0;margin:0 -24px 28px;padding-left:24px;padding-right:24px;background:rgba(250,249,247,.92);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);border-bottom:1px solid rgba(7,25,46,.07);box-shadow:0 2px 18px rgba(7,25,46,.05)}
.gallery-filter-label{font-size:12px;font-weight:800;color:var(--clr-navy,#07192e);opacity:.4;white-space:nowrap;text-transform:uppercase;letter-spacing:.14em;flex-shrink:0;display:none}
.gallery-tag-btns{display:flex;gap:7px;overflow-x:auto;scrollbar-width:none;-ms-overflow-style:none;flex:1;padding-bottom:1px}
.gallery-tag-btns::-webkit-scrollbar{display:none}
.gal-tag{display:inline-flex;align-items:center;gap:5px;padding:7px 15px;border-radius:100px;border:1.5px solid rgba(7,25,46,.10);background:transparent;color:rgba(7,25,46,.58);font-size:13px;font-weight:500;cursor:pointer;transition:all .2s ease;white-space:nowrap;flex-shrink:0;line-height:1}
.gal-tag:hover{border-color:rgba(7,25,46,.32);color:var(--clr-navy,#07192e);background:rgba(7,25,46,.04);transform:translateY(-1px)}
.gal-tag.active{background:var(--clr-navy,#07192e);border-color:var(--clr-navy,#07192e);color:#fff;box-shadow:0 4px 14px rgba(7,25,46,.22)}
.gal-tag-count{font-size:12px;font-weight:700;padding:1px 6px;border-radius:8px;background:rgba(7,25,46,.07);color:rgba(7,25,46,.45);line-height:1.5;transition:all .2s ease}
.gal-tag.active .gal-tag-count{background:rgba(255,255,255,.18);color:rgba(255,255,255,.80)}
.gallery-count-bar{display:flex;align-items:center;justify-content:space-between;margin-bottom:22px}
.gallery-count{font-size:13px;font-weight:500;color:rgba(7,25,46,.40);transition:opacity .15s}
.gal-hidden{display:none!important}
@keyframes galIn{from{opacity:0;transform:scale(.96)}to{opacity:1;transform:none}}
.gal-visible{animation:galIn .22s ease both}
@media(max-width:600px){.gallery-filter-bar{top:58px;margin:0 -18px 20px;padding-left:18px;padding-right:18px}}
"""

FILTER_JS = """
/* Gallery tag filter v2 */
(function(){
  var bar = document.querySelector('.gallery-filter-bar');
  if(!bar) return;
  var btns = Array.from(bar.querySelectorAll('.gal-tag'));
  var items = Array.from(document.querySelectorAll('.gallery-item[data-tags]'));
  var countEl = document.querySelector('.gallery-count');
  /* Build per-tag counts */
  var tagCounts = {all: items.length};
  items.forEach(function(el){
    (el.dataset.tags||'').split(' ').filter(Boolean).forEach(function(t){
      tagCounts[t] = (tagCounts[t]||0)+1;
    });
  });
  /* Inject count badges (guard against bfcache double-run) */
  if(!bar.dataset.filterInit){
    bar.dataset.filterInit='1';
    btns.forEach(function(btn){
      var t = btn.dataset.tag||'all';
      var badge = document.createElement('span');
      badge.className = 'gal-tag-count';
      badge.setAttribute('aria-hidden','true');
      badge.textContent = tagCounts[t]||0;
      btn.appendChild(badge);
    });
  }
  function setCount(n){
    if(countEl) countEl.textContent = n + ' ' + (countEl.dataset.unit||'photos');
  }
  function filterTo(tag){
    var visible = 0;
    items.forEach(function(el){
      var tags = (el.dataset.tags||'').split(' ');
      var show = tag==='all' || tags.indexOf(tag)>=0;
      if(show){
        el.classList.remove('gal-hidden');
        el.classList.remove('gal-visible');
        void el.offsetWidth;
        el.classList.add('gal-visible');
        visible++;
      } else {
        el.classList.add('gal-hidden');
        el.classList.remove('gal-visible');
      }
    });
    setCount(visible);
    /* Update "All" badge to show filtered count */
    btns.forEach(function(btn){
      var t = btn.dataset.tag||'all';
      var badge = btn.querySelector('.gal-tag-count');
      if(badge && t==='all') badge.textContent = visible;
    });
  }
  btns.forEach(function(btn){
    btn.addEventListener('click',function(){
      btns.forEach(function(b){b.classList.remove('active');});
      btn.classList.add('active');
      filterTo(btn.dataset.tag||'all');
    });
  });
  setCount(items.length);
  /* Auto-apply filter stored by other pages via sessionStorage */
  var _preFilter = sessionStorage.getItem('ngor_gallery_filter');
  if (_preFilter) {
    sessionStorage.removeItem('ngor_gallery_filter');
    var _preBtn = btns.filter(function(b){ return b.dataset.tag === _preFilter; })[0];
    if (_preBtn) {
      btns.forEach(function(b){b.classList.remove('active');});
      _preBtn.classList.add('active');
      filterTo(_preFilter);
      setTimeout(function(){ _preBtn.scrollIntoView({behavior:'smooth',block:'nearest',inline:'center'}); }, 200);
    }
  }
})();
"""


def inject_filter_css(html: str) -> str:
    """Inject/replace filter CSS."""
    import re as _re
    # Replace existing block if present (v1 or v2)
    old_marker_v1 = "/* ── Gallery Filter Bar ── */"
    old_marker_v2 = "/* ── Gallery Filter Bar v2 ── */"
    new_block = FILTER_CSS.strip()
    for marker in (old_marker_v1, old_marker_v2):
        if marker in html:
            # Replace from marker to next standalone CSS block separator or end of style
            html = _re.sub(
                r'/\* ── Gallery Filter Bar[^─]*──[^*]*\*/' + r'[\s\S]*?(?=\n/\*|\n\.(?!gal|gallery)|</style>)',
                new_block + "\n",
                html, count=1
            )
            return html
    # Not found — inject before </style>
    marker = "</style>"
    if marker in html:
        return html.replace(marker, new_block + "\n" + marker, 1)
    return html.replace("</head>", f"<style>{new_block}</style></head>", 1)


def inject_filter_js(html: str) -> str:
    """Inject/replace filter JS."""
    import re as _re
    new_block = FILTER_JS.strip()
    # Case-insensitive check for any existing gallery filter script block
    if _re.search(r'/\*\s*gallery tag filter', html, _re.IGNORECASE):
        html = _re.sub(
            r'/\*\s*[Gg]allery tag filter[^*]*\*/[\s\S]*?\}\)\(\);',
            new_block,
            html, count=1
        )
        return html
    return html.replace("</body>", f"<script>{new_block}</script></body>", 1)


def patch_gallery_page(lang: str, images: list) -> bool:
    """Patch a single gallery page with filter bar and new images."""
    rel = GALLERY_PAGES.get(lang)
    if not rel:
        return False
    path = DEMO_DIR / rel
    if not path.exists():
        print(f"  [SKIP] {rel} — file not found")
        return False

    labels = TAG_LABELS.get(lang, TAG_LABELS["en"])

    with open(path, encoding="utf-8", errors="replace") as f:
        html = f.read()

    # Inject CSS + JS
    html = inject_filter_css(html)
    html = inject_filter_js(html)

    # Build the new gallery section content
    filter_bar = build_filter_bar(lang, labels)
    img_grid = build_image_grid(images)
    count = sum(1 for img in images if img.get("quality", 0) >= 5)

    # Build count badge with wrapper
    unit = labels["photos_count"]
    count_badge = f'<div class="gallery-count-bar"><span class="gallery-count" data-unit="{unit}">{count} {unit}</span></div>'

    # Replace the existing gallery-masonry--page div with new content
    new_section = (
        f'{filter_bar}\n'
        f'      {count_badge}\n'
        f'      <div class="gallery-masonry gallery-masonry--page" role="list">\n'
        f'        {img_grid}\n'
        f'      </div>'
    )

    # Replace existing gallery-masonry--page block
    pattern = re.compile(
        r'<div class="gallery-masonry gallery-masonry--page"[^>]*>.*?</div>',
        re.DOTALL
    )
    new_html, n = pattern.subn(
        f'<div class="gallery-masonry gallery-masonry--page" role="list">\n        {img_grid}\n      </div>',
        html,
        count=1
    )

    # Also inject filter bar before the masonry if not already there
    # Use the HTML element check (not CSS class name) to avoid false positives
    if n and 'class="gallery-filter-bar' not in new_html:
        new_html = new_html.replace(
            '<div class="gallery-masonry gallery-masonry--page"',
            filter_bar + '\n      ' + count_badge + '\n      <div class="gallery-masonry gallery-masonry--page"',
            1
        )

    if new_html != html:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_html)
        print(f"  ✓ Patched gallery: {rel} ({count} photos)")
        return True
    else:
        print(f"  [WARN] No change for: {rel}")
        return False


def main():
    if not MANIFEST.exists():
        print(f"ERROR: manifest not found at {MANIFEST}")
        return

    with open(MANIFEST) as f:
        manifest = json.load(f)

    images = manifest.get("images", [])
    # Sort by quality desc, filter out very low quality
    images = sorted([img for img in images if img.get("quality", 0) >= 5], key=lambda x: -x.get("quality", 0))
    print(f"Loaded {len(images)} gallery images from manifest (quality >= 5)")

    print("\nPatching gallery pages across all languages...")
    for lang in ["en", "fr", "es", "it", "de", "nl", "ar", "pt", "da"]:
        patch_gallery_page(lang, images)

    print("\n✅ Gallery pages updated with filter system and new photos!")
    print(f"Tag distribution:")
    from collections import Counter
    tag_counts = Counter(t for img in images for t in img.get("tags", []))
    for tag, count in tag_counts.most_common():
        print(f"  {tag}: {count}")


if __name__ == "__main__":
    main()
