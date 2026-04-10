"""
Migration: Localize blog article slugs for all non-EN languages.
- Renames article directories to localized slugs
- Updates canonical, og:url, hreflang, lang-dd, lang-pills, breadcrumbs in all HTML files
- Updates blog index and category pages
- Creates 301-redirect pages at old English-slug URLs
- Updates sitemaps
- Updates JSON article files with local_slug field
- Updates build_blog.py SLUG_MAP reference
"""
import os, re, shutil, json

DEMO    = "/Users/simonazoulay/SurfCampSenegal/cloudflare-demo"
CONTENT = "/Users/simonazoulay/SurfCampSenegal/content/articles_v2"
SITE    = "https://surf-camp-senegal.vercel.app"

LANGS       = ["en","fr","es","it","de","nl","ar","pt","da"]
LANG_PREFIX = {"en":"","fr":"/fr","es":"/es","it":"/it","de":"/de","nl":"/nl","ar":"/ar","pt":"/pt","da":"/da"}
LANG_LOCALE = {"en":"en","fr":"fr-FR","es":"es-ES","it":"it-IT","de":"de-DE","nl":"nl-NL","ar":"ar-MA","pt":"pt-PT","da":"da-DK"}

# ─── SLUG MAP: en_slug → {lang: localized_slug} ───────────────────────────────
SLUG_MAP = {
  "dakar-surf-spots-for-every-level": {
    "en": "dakar-surf-spots-for-every-level",
    "fr": "spots-surf-dakar-tous-niveaux",
    "es": "spots-surf-dakar-todos-niveles",
    "it": "spot-surf-dakar-tutti-livelli",
    "de": "surfspots-dakar-alle-levels",
    "nl": "surfspots-dakar-elk-niveau",
    "ar": "spots-surf-dakar-kull-mustawayat",
    "pt": "spots-surf-dakar-todos-niveis",
    "da": "dakar-surfspots-alle-niveauer",
  },
  "endless-summer-senegal-ngor": {
    "en": "endless-summer-senegal-ngor",
    "fr": "ete-sans-fin-ngor-heritage-surf-senegal",
    "es": "verano-sin-fin-ngor-senegal",
    "it": "estate-senza-fine-ngor-senegal",
    "de": "endloser-sommer-ngor-senegal",
    "nl": "endless-summer-ngor-senegals-surferfgoed",
    "ar": "sayf-bila-nihaya-ngor-senegal",
    "pt": "verao-sem-fim-ngor-senegal",
    "da": "den-endloese-sommer-ngor-senegal",
  },
  "licensed-surf-camp-senegal": {
    "en": "licensed-surf-camp-senegal",
    "fr": "surf-camp-agree-senegal",
    "es": "campamento-surf-licenciado-senegal",
    "it": "surf-camp-autorizzato-senegal",
    "de": "lizenziertes-surf-camp-senegal",
    "nl": "surfkamp-licentie-senegal",
    "ar": "mukhayyam-surf-murajjas-senegal",
    "pt": "surf-camp-licenciado-senegal",
    "da": "licenseret-surfcamp-senegal",
  },
  "ngor-island-waves-explained": {
    "en": "ngor-island-waves-explained",
    "fr": "vagues-ile-ngor-expliquees",
    "es": "olas-ngor-island-explicadas",
    "it": "onde-ngor-island-spiegate",
    "de": "wellen-ngor-island-erklaert",
    "nl": "golven-ngor-island-uitgelegd",
    "ar": "amwaj-jazirat-ngor-sharh",
    "pt": "ondas-ngor-island-explicadas",
    "da": "boelger-ngor-island-forklaret",
  },
  "senegal-surf-camp-for-beginners": {
    "en": "senegal-surf-camp-for-beginners",
    "fr": "surf-camp-senegal-debutants",
    "es": "campamento-surf-senegal-principiantes",
    "it": "surf-camp-senegal-principianti",
    "de": "surfcamp-senegal-anfaenger",
    "nl": "surfcamp-senegal-beginners",
    "ar": "mukhayyam-surf-senegal-mubtadin",
    "pt": "surfcamp-senegal-iniciantes",
    "da": "surf-camp-senegal-begyndere",
  },
  "senegal-surf-season-by-month": {
    "en": "senegal-surf-season-by-month",
    "fr": "saison-surf-senegal-mois-par-mois",
    "es": "temporada-surf-senegal-mes-a-mes",
    "it": "stagione-surf-senegal-mese-per-mese",
    "de": "surfsaison-senegal-monat-fuer-monat",
    "nl": "surfseizoen-senegal-per-maand",
    "ar": "mawsim-surf-senegal-shahr-bishahr",
    "pt": "temporada-surf-senegal-mes-a-mes",
    "da": "senegals-surfsaeson-maaned-for-maaned",
  },
  "surf-camp-senegal-what-to-expect": {
    "en": "surf-camp-senegal-what-to-expect",
    "fr": "surf-camp-senegal-quoi-attendre",
    "es": "campamento-surf-senegal-que-esperar",
    "it": "surf-camp-senegal-cosa-aspettarsi",
    "de": "surfcamp-senegal-was-erwartet",
    "nl": "surfcamp-senegal-wat-verwachten",
    "ar": "mukhayyam-surf-senegal-matha-tatawaqqa",
    "pt": "surf-camp-senegal-o-que-esperar",
    "da": "surf-camp-senegal-hvad-forvente",
  },
  "surf-coaching-structured-ngor-surfcamp": {
    "en": "surf-coaching-structured-ngor-surfcamp",
    "fr": "coaching-surf-ngor-surfcamp",
    "es": "coaching-surf-ngor-surfcamp",
    "it": "surf-coaching-ngor-surfcamp",
    "de": "surf-coaching-ngor-surfcamp",
    "nl": "surfcoaching-ngor-surfcamp",
    "ar": "tadrib-surf-ngor-surfcamp",
    "pt": "coaching-surf-ngor-surfcamp",
    "da": "surfcoaching-ngor-surfcamp",
  },
  "surf-trip-to-senegal-what-to-pack": {
    "en": "surf-trip-to-senegal-what-to-pack",
    "fr": "voyage-surf-senegal-liste-valise",
    "es": "viaje-surf-senegal-equipaje",
    "it": "surf-trip-senegal-lista-valigia",
    "de": "surftrip-senegal-packliste",
    "nl": "surftrip-senegal-paklijst",
    "ar": "rihlat-surf-senegal-ma-tahmal",
    "pt": "viagem-surf-senegal-lista",
    "da": "surftrip-senegal-pakkelist",
  },
  "surfing-ngor-left-guide": {
    "en": "surfing-ngor-left-guide",
    "fr": "surfer-ngor-left-guide",
    "es": "surfear-ngor-left-guia",
    "it": "surf-ngor-left-guida",
    "de": "ngor-left-surfen-guide",
    "nl": "surfen-ngor-left-gids",
    "ar": "surf-ngor-left-dalil",
    "pt": "surfar-ngor-left-guia",
    "da": "surfe-ngor-left-guide",
  },
  "surfing-ngor-right-guide": {
    "en": "surfing-ngor-right-guide",
    "fr": "surf-ngor-right-guide",
    "es": "surfear-ngor-right-guia",
    "it": "surf-ngor-right-guida",
    "de": "ngor-right-surfen-guide",
    "nl": "surfen-ngor-right-spotgids",
    "ar": "surf-ngor-right-dalil",
    "pt": "surfar-ngor-right-guia",
    "da": "surfe-ngor-right-spotguide",
  },
  "video-analysis-surf-camp-senegal": {
    "en": "video-analysis-surf-camp-senegal",
    "fr": "analyse-video-surf-camp-senegal",
    "es": "analisis-video-surf-camp-senegal",
    "it": "analisi-video-surf-camp-senegal",
    "de": "videoanalyse-surfcamp-senegal",
    "nl": "videoanalyse-surfkamp-senegal",
    "ar": "tahlil-video-mukhayyam-surf-senegal",
    "pt": "analise-video-surf-camp-senegal",
    "da": "videoanalyse-surf-camp-senegal",
  },
  "where-to-stay-for-surfing-in-dakar": {
    "en": "where-to-stay-for-surfing-in-dakar",
    "fr": "ou-sejourner-surf-dakar",
    "es": "donde-alojarse-surf-dakar",
    "it": "dove-soggiornare-surf-dakar",
    "de": "surfen-dakar-insel-oder-festland",
    "nl": "verblijven-surf-dakar-eiland",
    "ar": "ayna-tiqam-surf-dakar",
    "pt": "onde-ficar-surf-dakar",
    "da": "bolig-surf-dakar-oe-fastland",
  },
  "why-choose-surf-camp-senegal": {
    "en": "why-choose-surf-camp-senegal",
    "fr": "pourquoi-choisir-surfcamp-senegal",
    "es": "por-que-elegir-surf-camp-senegal",
    "it": "perche-scegliere-surf-camp-senegal",
    "de": "warum-surfcamp-senegal",
    "nl": "waarom-surfkamp-senegal",
    "ar": "limatha-mukhayyam-surf-senegal",
    "pt": "por-que-escolher-surf-camp-senegal",
    "da": "hvorfor-vaelge-surfcamp-senegal",
  },
  "why-senegal-is-an-underrated-surf-destination": {
    "en": "why-senegal-is-an-underrated-surf-destination",
    "fr": "senegal-destination-surf-sous-estimee",
    "es": "senegal-destino-surf-infravalorado",
    "it": "senegal-destinazione-surf-sottovalutata",
    "de": "senegal-unterschaetztes-surfziel",
    "nl": "senegal-onderschatte-surfbestemming",
    "ar": "senegal-wajihat-surf-maghmura",
    "pt": "senegal-destino-surf-subestimado",
    "da": "senegal-undervurderet-surfdestination",
  },
}

# Build reverse map: (lang, local_slug) -> en_slug
REVERSE_MAP = {}
for en_s, lang_map in SLUG_MAP.items():
    for lang, local_s in lang_map.items():
        REVERSE_MAP[(lang, local_s)] = en_s

def local_slug(en_s, lang):
    return SLUG_MAP.get(en_s, {}).get(lang, en_s)

def art_url(en_s, lang):
    pfx = LANG_PREFIX[lang]
    ls  = local_slug(en_s, lang)
    if lang == "en":
        return f"{SITE}/blog/{ls}/"
    return f"{SITE}{pfx}/blog/{ls}/"

# ─── STEP 1: Move article directories ─────────────────────────────────────────
print("=== STEP 1: Renaming article directories ===")
for en_s, lang_map in SLUG_MAP.items():
    for lang, ls in lang_map.items():
        if lang == "en":
            continue  # EN stays as-is
        pfx = LANG_PREFIX[lang]
        old_dir = f"{DEMO}{pfx}/blog/{en_s}"
        new_dir = f"{DEMO}{pfx}/blog/{ls}"
        if os.path.isdir(old_dir):
            if os.path.isdir(new_dir):
                print(f"  SKIP (already exists): {new_dir}")
            else:
                shutil.move(old_dir, new_dir)
                print(f"  MOVED: {old_dir} → {new_dir}")
        else:
            print(f"  MISSING (old dir not found): {old_dir}")

# ─── STEP 2: No redirects needed (site not live) ─────────────────────────────
# Old English-slug directories for non-EN languages do NOT exist — all internal
# links already point directly to the localized slugs (200, no chains).
print("\n=== STEP 2: No redirect pages (site not live) — skipped ===")

# ─── STEP 3: Update URLs inside moved article HTML files ──────────────────────
print("\n=== STEP 3: Updating URLs in article HTML files ===")

def update_article_html(filepath, en_s, lang):
    """Update canonical, og:url, hreflang, lang-dd, lang-pills in an article page."""
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    # Fix canonical
    old_can = f'{SITE}{LANG_PREFIX[lang]}/blog/{en_s}/'
    new_can = art_url(en_s, lang)
    html = html.replace(
        f'<link rel="canonical" href="{old_can}">',
        f'<link rel="canonical" href="{new_can}">'
    )

    # Fix og:url
    html = html.replace(
        f'<meta property="og:url" content="{old_can}">',
        f'<meta property="og:url" content="{new_can}">'
    )

    # Fix JSON-LD breadcrumb item for this article
    html = html.replace(
        f'"item":"{old_can}"',
        f'"item":"{new_can}"'
    )

    # Fix ALL hreflang / lang-dd / lang-pill links for every language (full + relative URLs)
    for tgt_lang, tgt_ls in SLUG_MAP[en_s].items():
        tgt_pfx  = LANG_PREFIX[tgt_lang]
        # Full URLs (used in <head> hreflang)
        old_url  = f"{SITE}{tgt_pfx}/blog/{en_s}/"
        new_url  = art_url(en_s, tgt_lang)
        if old_url != new_url:
            html = html.replace(f'href="{old_url}"', f'href="{new_url}"')
        # Relative URLs (used in nav lang-dd, lang-pills)
        old_rel = f'{tgt_pfx}/blog/{en_s}/'
        new_rel = f'{tgt_pfx}/blog/{tgt_ls}/'
        if old_rel != new_rel:
            html = html.replace(f'href="{old_rel}"', f'href="{new_rel}"')

    # Fix intra-language related-article / nav links (same lang, other articles)
    for other_en_s, lang_map in SLUG_MAP.items():
        if other_en_s == en_s:
            continue
        other_old = f'{LANG_PREFIX[lang]}/blog/{other_en_s}/'
        other_new = f'{LANG_PREFIX[lang]}/blog/{lang_map.get(lang, other_en_s)}/'
        if other_old != other_new:
            html = html.replace(f'href="{other_old}"', f'href="{other_new}"')

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

# Update all language article HTML files
for en_s, lang_map in SLUG_MAP.items():
    for lang, ls in lang_map.items():
        pfx = LANG_PREFIX[lang]
        if lang == "en":
            filepath = f"{DEMO}/blog/{en_s}/index.html"
        else:
            filepath = f"{DEMO}{pfx}/blog/{ls}/index.html"
        if os.path.isfile(filepath):
            update_article_html(filepath, en_s, lang)
            print(f"  UPDATED HTML: {filepath}")
        else:
            print(f"  MISSING HTML: {filepath}")

# ─── STEP 4: Update blog index and category pages ─────────────────────────────
print("\n=== STEP 4: Updating blog index and category pages ===")

def update_index_page(filepath, lang):
    """Replace all en_slug article links with localized slugs in an index/category page."""
    if not os.path.isfile(filepath):
        return
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()
    changed = False
    for en_s, lang_map in SLUG_MAP.items():
        ls = lang_map.get(lang, en_s)
        if ls == en_s:
            continue
        pfx = LANG_PREFIX[lang]
        # Relative href
        old_href = f'{pfx}/blog/{en_s}/'
        new_href = f'{pfx}/blog/{ls}/'
        if old_href in html:
            html = html.replace(old_href, new_href)
            changed = True
        # Full URL
        old_full = f'{SITE}{pfx}/blog/{en_s}/'
        new_full = art_url(en_s, lang)
        if old_full in html:
            html = html.replace(old_full, new_full)
            changed = True
    if changed:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  UPDATED INDEX: {filepath}")

for lang in LANGS:
    pfx = LANG_PREFIX[lang]
    # Blog main index
    update_index_page(f"{DEMO}{pfx}/blog/index.html", lang)
    # Category pages
    for root, dirs, files in os.walk(f"{DEMO}{pfx}/blog/"):
        for fn in files:
            if fn == "index.html":
                full = os.path.join(root, fn)
                # Skip article pages (they were already handled) and redirect pages
                rel = full[len(f"{DEMO}{pfx}/blog/"):]
                parts = rel.strip("/").split("/")
                is_article = len(parts) == 2 and parts[1] == "index.html" and parts[0] in [SLUG_MAP[s].get(lang, s) for s in SLUG_MAP]
                if not is_article:
                    update_index_page(full, lang)

# ─── STEP 5: Update sitemaps ──────────────────────────────────────────────────
print("\n=== STEP 5: Updating sitemaps ===")

sitemap_files = [
    f"{DEMO}/sitemap.xml",
    f"{DEMO}/sitemap-index.xml",
] + [f"{DEMO}/sitemap-{lang}.xml" for lang in LANGS]

for sitemap_path in sitemap_files:
    if not os.path.isfile(sitemap_path):
        continue
    with open(sitemap_path, "r", encoding="utf-8") as f:
        content = f.read()
    changed = False
    for en_s, lang_map in SLUG_MAP.items():
        for lang, ls in lang_map.items():
            if ls == en_s:
                continue
            pfx = LANG_PREFIX[lang]
            old_url = f"{SITE}{pfx}/blog/{en_s}/"
            new_url = art_url(en_s, lang)
            if old_url in content:
                content = content.replace(old_url, new_url)
                changed = True
    if changed:
        with open(sitemap_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  UPDATED SITEMAP: {sitemap_path}")

# ─── STEP 6: Update JSON article files ────────────────────────────────────────
print("\n=== STEP 6: Updating JSON article files ===")

for en_s, lang_map in SLUG_MAP.items():
    for lang, ls in lang_map.items():
        if lang == "en":
            continue
        json_path = f"{CONTENT}/{lang}/{en_s}.json"
        if os.path.isfile(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            data["slug"] = ls
            data["original_en_slug"] = en_s
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"  UPDATED JSON: {json_path} slug={ls}")

# ─── STEP 7: Update other pages referencing blog articles ────────────────────
print("\n=== STEP 7: Updating other site pages (home, surf, island...) ===")

# Walk all HTML in DEMO, update any blog article links for non-EN langs
for root, dirs, files in os.walk(DEMO):
    # Skip blog directories (already handled) and asset dirs
    skip_dirs = {"assets", ".git"}
    dirs[:] = [d for d in dirs if d not in skip_dirs]
    for fn in files:
        if fn != "index.html":
            continue
        full = os.path.join(root, fn)
        rel  = full[len(DEMO):]
        # Skip article pages already updated
        already_updated = False
        for en_s, lang_map in SLUG_MAP.items():
            for lang, ls in lang_map.items():
                pfx = LANG_PREFIX[lang]
                if rel == f"{pfx}/blog/{ls}/index.html":
                    already_updated = True
                    break
            if already_updated:
                break
        if already_updated:
            continue

        with open(full, "r", encoding="utf-8") as f:
            html = f.read()
        changed = False
        for en_s, lang_map in SLUG_MAP.items():
            for lang, ls in lang_map.items():
                if ls == en_s:
                    continue
                pfx = LANG_PREFIX[lang]
                old_href = f'{pfx}/blog/{en_s}/'
                new_href = f'{pfx}/blog/{ls}/'
                # only replace if this exact href pattern appears
                if f'href="{old_href}"' in html:
                    html = html.replace(f'href="{old_href}"', f'href="{new_href}"')
                    changed = True
                full_old = f'{SITE}{pfx}/blog/{en_s}/'
                full_new = art_url(en_s, lang)
                if full_old in html:
                    html = html.replace(full_old, full_new)
                    changed = True
        if changed:
            with open(full, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"  UPDATED PAGE: {rel}")

print("\n✅ Migration complete!")
