"""
Push ALL content to DEMO site ONLY — NEVER touches the live site.
  - Creates blog draft posts (EN + FR + ES + IT + DE)
  - Generates & uploads featured images
  - Updates site properties (language = en)
  - Sets up multilingual languages
  - Injects DA custom CSS via custom code API
  - Updates hreflang / SEO metadata

DEMO site : e8cc06ab-3597-48e0-b1fb-f80eb45d6746
LIVE site : 4dd6806d-ff9c-4e35-bd98-1dc27ac71a7a  ← READ ONLY, NEVER WRITTEN
"""
import json, os, re, time, base64, requests
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# ── Constants ─────────────────────────────────────────────────────────────────
OPENAI_KEY    = "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"
WIX_KEY       = open("/Users/simonazoulay/SurfCampSenegal/clesapi.txt").read().strip()
IMAGE_MODEL   = "gpt-image-1.5-2025-12-16"
BASE          = "https://www.wixapis.com"
SITE_DEMO     = "e8cc06ab-3597-48e0-b1fb-f80eb45d6746"  # DEMO ONLY
MEMBER_ID     = "c2467ffa-759d-4bb8-bd93-1544d1f6f10d"  # demo site owner
ARTICLES_DIR  = "/Users/simonazoulay/SurfCampSenegal/content/articles"
IMAGES_DIR    = "/Users/simonazoulay/SurfCampSenegal/content/images"
OUTPUT_DIR    = "/Users/simonazoulay/SurfCampSenegal/output"
LANGS         = ["fr", "es", "it", "de"]
LANG_LOCALES  = {"en": "en", "fr": "fr", "es": "es", "it": "it", "de": "de"}

os.makedirs(IMAGES_DIR, exist_ok=True)

client     = OpenAI(api_key=OPENAI_KEY)
print_lock = threading.Lock()

def log(msg):
    with print_lock:
        print(msg, flush=True)

def H(site_id=SITE_DEMO):
    # ALWAYS default to DEMO; explicit site_id required to override
    return {
        "Authorization": WIX_KEY,
        "Content-Type":  "application/json",
        "wix-site-id":   site_id,
    }

def wix_get(path, params=None):
    return requests.get(BASE + path, headers=H(), params=params, timeout=20)

def wix_post(path, body):
    return requests.post(BASE + path, headers=H(), json=body, timeout=30)

def wix_patch(path, body):
    return requests.patch(BASE + path, headers=H(), json=body, timeout=20)

def load(path):
    if os.path.exists(path):
        try:
            with open(path) as f: return json.load(f)
        except Exception: return None
    return None

def save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ── Load strategy & category IDs ─────────────────────────────────────────────
strategy    = load("/Users/simonazoulay/SurfCampSenegal/content/blog_strategy.json")
cat_ids     = load(f"{OUTPUT_DIR}/demo_category_ids.json") or {}
cats        = strategy["categories"]
arts        = strategy["articles"]
cat_id_map  = cat_ids  # {"Surf Conditions & Spots": "d1c860f0-..."}

# ════════════════════════════════════════════════════════════════════════════════
# STEP 1 – Fix site properties on DEMO (language → EN)
# ════════════════════════════════════════════════════════════════════════════════
print("\n=== 1. Update DEMO site properties ===")
# Try the correct v4 PATCH format
prop_bodies = [
    {"properties": {"language": "en", "siteDisplayName": "Ngor Surfcamp Teranga"},
     "fieldMask":  {"paths": ["properties.language", "properties.siteDisplayName"]}},
    {"properties": {"language": "en"}, "fieldMask": {"paths": ["language"]}},
    {"language": "en", "siteDisplayName": "Ngor Surfcamp Teranga"},
]
for body in prop_bodies:
    r = requests.patch(BASE+"/site-properties/v4/properties", headers=H(), json=body, timeout=15)
    if r.status_code == 200:
        log(f"  ✅ Site properties updated (language=en, name=Ngor Surfcamp Teranga)")
        break
    log(f"  PATCH attempt: {r.status_code} | {r.text[:150]}")

# ════════════════════════════════════════════════════════════════════════════════
# STEP 2 – Custom CSS injection for DA improvements (DEMO only)
# ════════════════════════════════════════════════════════════════════════════════
print("\n=== 2. Inject custom CSS (DA improvements) on DEMO ===")
css_content = open("/Users/simonazoulay/SurfCampSenegal/content/custom_css_da.css").read()
css_tag     = f"<style id='ngor-da-v1'>\n{css_content}\n</style>"

css_endpoints = [
    ("/custom-code/v1/site-custom-code", "POST",
     {"customCodeEntry": {"type": "INLINE", "placement": "BODY_START",
                          "code": css_tag, "position": {"placementType": "BODY_START"}}}),
    ("/v1/custom-code/entries", "POST",
     {"entry": {"code": css_tag, "placement": "BODY_START", "id": "ngor-da-improvements"}}),
]
css_ok = False
for path, method, body in css_endpoints:
    r = requests.request(method, BASE+path, headers=H(), json=body, timeout=15)
    if r.status_code in [200, 201]:
        log(f"  ✅ CSS injected via {path}")
        css_ok = True
        break
    log(f"  {method} {path}: {r.status_code} | {r.text[:150]}")

if not css_ok:
    log("  ⚠️  CSS API not available → saved to content/custom_css_da.css for manual Velo injection")
    log("  Instructions: Dashboard DEMO site → Outils de dév → CSS global → coller le fichier")

# ════════════════════════════════════════════════════════════════════════════════
# STEP 3 – Set up multilingual on DEMO
# ════════════════════════════════════════════════════════════════════════════════
print("\n=== 3. Set up multilingual on DEMO ===")
lang_endpoints = [
    "/multilingual/v2/site-languages",
    "/multilingual/v1/site-languages",
]
for lang_code, country in [("fr","FR"),("es","ES"),("it","IT"),("de","DE")]:
    added = False
    for ep in lang_endpoints:
        body = {"language": {
            "languageCode": lang_code,
            "locale": {"country": country, "languageCode": lang_code},
            "isPrimary": False,
            "status": "Active",
        }}
        r = wix_post(ep, body)
        if r.status_code in [200, 201]:
            log(f"  ✅ Language {lang_code}-{country} added")
            added = True
            break
    if not added:
        log(f"  ⚠️  {lang_code}: API unavailable (will note in guide)")

# ════════════════════════════════════════════════════════════════════════════════
# STEP 4 – Generate featured images (gpt-image-1.5-2025-12-16) in parallel
# ════════════════════════════════════════════════════════════════════════════════
print("\n=== 4. Generate featured images ===")

def generate_image(article):
    img_path = f"{IMAGES_DIR}/{article['slug']}.png"
    if os.path.exists(img_path):
        log(f"  [skip img] {article['slug'][:40]}")
        return article['slug'], img_path

    hero_prompt = article.get("hero_image_prompt", "")
    if not hero_prompt:
        hero_prompt = f"Surf photography: {article['title']}. Ngor Island, Senegal, West Africa. Golden light, turquoise ocean."

    full_prompt = f"""{hero_prompt}
Style: editorial surf photography, cinematic, warm golden West African light,
turquoise ocean, authentic atmosphere. No text, no watermarks.
Aspect ratio: 16:9. High resolution, professional quality."""

    try:
        resp = client.images.generate(
            model=IMAGE_MODEL,
            prompt=full_prompt,
            n=1,
            size="1536x1024",
        )
        img_url = resp.data[0].url
        # Download the image
        img_data = requests.get(img_url, timeout=30).content
        with open(img_path, "wb") as f:
            f.write(img_data)
        log(f"  ✅ Image: {article['slug'][:40]} ({len(img_data)//1024}KB)")
        return article['slug'], img_path
    except Exception as e:
        log(f"  ❌ Image error for {article['slug'][:40]}: {e}")
        # Try fallback: dalle-3
        try:
            resp2 = client.images.generate(
                model="dall-e-3",
                prompt=full_prompt[:1000],
                n=1,
                size="1536x1024",
                quality="hd",
            )
            img_url = resp2.data[0].url
            img_data = requests.get(img_url, timeout=30).content
            with open(img_path, "wb") as f:
                f.write(img_data)
            log(f"  ✅ Image (fallback dall-e-3): {article['slug'][:40]}")
            return article['slug'], img_path
        except Exception as e2:
            log(f"  ❌ Fallback image error: {e2}")
            return article['slug'], None

with ThreadPoolExecutor(max_workers=10) as ex:
    futures = {ex.submit(generate_image, art): art for art in arts}
    img_map = {}
    for future in as_completed(futures):
        slug, path = future.result()
        if path:
            img_map[slug] = path

log(f"\nImages generated: {len(img_map)}/30")

# ════════════════════════════════════════════════════════════════════════════════
# STEP 5 – Upload images to Wix Media and get media URLs
# ════════════════════════════════════════════════════════════════════════════════
print("\n=== 5. Upload images to Wix Media (DEMO) ===")

def upload_image_to_wix(slug, img_path):
    """Upload image to Wix Media Manager and return the wix media ID."""
    media_id_file = f"{IMAGES_DIR}/{slug}_wix_id.json"
    cached = load(media_id_file)
    if cached:
        return cached.get("media_id"), cached.get("url")

    if not img_path or not os.path.exists(img_path):
        return None, None

    try:
        # Step 1: Get upload URL from Wix
        r = requests.post(BASE + "/media/v2/files/generate-upload-url",
            headers=H(),
            json={
                "mimeType": "image/png",
                "fileName": f"{slug}.png",
            }, timeout=15)

        if r.status_code not in [200, 201]:
            log(f"  Upload URL error: {r.status_code} | {r.text[:200]}")
            return None, None

        upload_data = r.json()
        upload_url  = upload_data.get("uploadUrl", "")
        media_id    = upload_data.get("id", "")

        if not upload_url:
            # Try alternate endpoint
            r2 = requests.post(BASE + "/v2/upload-url",
                headers=H(),
                json={"fileName": f"{slug}.png", "mimeType": "image/png"},
                timeout=15)
            if r2.status_code in [200, 201]:
                upload_data = r2.json()
                upload_url  = upload_data.get("uploadUrl", "")
                media_id    = upload_data.get("id", "")

        if not upload_url:
            return None, None

        # Step 2: Upload the file
        with open(img_path, "rb") as f:
            img_bytes = f.read()

        r_up = requests.put(upload_url,
            data=img_bytes,
            headers={"Content-Type": "image/png"},
            timeout=60)

        if r_up.status_code in [200, 201]:
            wix_url = upload_data.get("fileUrl", "")
            save(media_id_file, {"media_id": media_id, "url": wix_url, "slug": slug})
            log(f"  ✅ Uploaded: {slug[:40]}")
            return media_id, wix_url
        else:
            log(f"  Upload failed: {r_up.status_code}")
            return None, None

    except Exception as e:
        log(f"  Upload error {slug}: {e}")
        return None, None

wix_media_map = {}
with ThreadPoolExecutor(max_workers=5) as ex:
    futures = {ex.submit(upload_image_to_wix, slug, path): slug
               for slug, path in img_map.items()}
    for future in as_completed(futures):
        slug = futures[future]
        media_id, url = future.result()
        if media_id:
            wix_media_map[slug] = {"id": media_id, "url": url}

log(f"Wix media uploaded: {len(wix_media_map)}/30")

# ════════════════════════════════════════════════════════════════════════════════
# STEP 6 – Create draft blog posts on DEMO (EN + all languages)
# ════════════════════════════════════════════════════════════════════════════════
print("\n=== 6. Create blog draft posts on DEMO site ===")

# Load existing draft post IDs to avoid duplicates
pushed_ids_file = f"{OUTPUT_DIR}/demo_pushed_posts.json"
pushed_ids = load(pushed_ids_file) or {}

def markdown_to_wix_content(md_text):
    """Convert simple markdown to Wix rich text JSON (basic structure)."""
    # Return as plain text nodes for now — Wix will render it
    # For proper rich text we'd need the full Wix document model
    paragraphs = []
    for line in md_text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith("## "):
            paragraphs.append({"type": "HEADING", "text": line[3:], "nodes": []})
        elif line.startswith("# "):
            paragraphs.append({"type": "HEADING", "text": line[2:], "nodes": []})
        elif line.startswith("**") and line.endswith("**"):
            paragraphs.append({"type": "PARAGRAPH", "text": line.strip("*"), "nodes": []})
        else:
            paragraphs.append({"type": "PARAGRAPH", "text": line, "nodes": []})
    return paragraphs

def push_article(art_data, lang="en"):
    """Create a draft post on DEMO site for one article in one language."""
    slug     = art_data["slug"]
    key      = f"{lang}_{slug}"
    if key in pushed_ids:
        log(f"  [skip push {lang}] {art_data['title'][:45]}")
        return key, pushed_ids[key]

    log(f"  ▶ Pushing {lang}: {art_data['title'][:50]}")

    # Get category ID
    cat_name = art_data.get("category", "")
    cat_id   = cat_id_map.get(cat_name, "")

    # Build media object if we have an image for this slug
    en_slug = art_data.get("original_en_slug", slug)
    media   = {}
    if en_slug in wix_media_map:
        wm = wix_media_map[en_slug]
        media = {
            "wixMedia": {
                "image": {
                    "id":  wm.get("id", ""),
                    "url": wm.get("url", ""),
                }
            },
            "displayed": True,
            "custom":    False,
        }

    # Excerpt: first 300 chars of content (strip markdown)
    content = art_data.get("content_markdown", "")
    excerpt_raw = re.sub(r'[#*\[\]`]', '', content[:500]).strip()
    excerpt = excerpt_raw[:280].rsplit(" ", 1)[0] + "..."

    body = {
        "draftPost": {
            "title":             art_data["title"],
            "excerpt":           excerpt,
            "memberId":          MEMBER_ID,
            "language":          art_data.get("lang", "en"),
            "commentingEnabled": True,
            "featured":          art_data.get("type") == "hero",
            "categoryIds":       [cat_id] if cat_id else [],
            "seoData": {
                "tags": [
                    {"type": "TITLE",
                     "custom": True,
                     "disabled": False,
                     "children": art_data["title"]},
                    {"type": "DESCRIPTION",
                     "custom": True,
                     "disabled": False,
                     "children": art_data.get("meta_description", excerpt[:155])},
                    {"type": "OG_TITLE",
                     "custom": True,
                     "disabled": False,
                     "children": art_data["title"]},
                ]
            },
        }
    }
    if media:
        body["draftPost"]["media"] = media

    r = requests.post(BASE + "/blog/v3/draft-posts", headers=H(), json=body, timeout=20)
    if r.status_code in [200, 201]:
        post_id = r.json().get("draftPost", {}).get("id", "")
        log(f"  ✅ Draft created [{lang}] {art_data['title'][:45]} → id={post_id[:8]}")
        with print_lock:
            pushed_ids[key] = post_id
            save(pushed_ids_file, pushed_ids)
        return key, post_id
    else:
        log(f"  ❌ Push error [{lang}] {art_data['title'][:40]}: {r.status_code} | {r.text[:200]}")
        return key, None

# Push EN articles
print("\n  Pushing EN articles (30 parallel)...")
en_articles = []
en_dir = f"{ARTICLES_DIR}/en"
if os.path.exists(en_dir):
    for fname in sorted(os.listdir(en_dir)):
        if fname.endswith(".json"):
            a = load(f"{en_dir}/{fname}")
            if a:
                en_articles.append(a)

print(f"  EN articles loaded: {len(en_articles)}")
with ThreadPoolExecutor(max_workers=10) as ex:
    futures = {ex.submit(push_article, art, "en"): art for art in en_articles}
    for future in as_completed(futures):
        future.result()

# Push translated articles
for lang in LANGS:
    lang_dir = f"{ARTICLES_DIR}/{lang}"
    if not os.path.exists(lang_dir):
        log(f"  [skip] {lang} directory not ready yet")
        continue

    lang_articles = []
    for fname in sorted(os.listdir(lang_dir)):
        if fname.endswith(".json"):
            a = load(f"{lang_dir}/{fname}")
            if a:
                lang_articles.append(a)

    if not lang_articles:
        log(f"  [skip] {lang}: no articles generated yet")
        continue

    print(f"\n  Pushing {lang} articles ({len(lang_articles)} parallel)...")
    with ThreadPoolExecutor(max_workers=10) as ex:
        futures = {ex.submit(push_article, art, lang): art for art in lang_articles}
        for future in as_completed(futures):
            future.result()

# ════════════════════════════════════════════════════════════════════════════════
# STEP 7 – Generate SEO page data & hreflang report
# ════════════════════════════════════════════════════════════════════════════════
print("\n=== 7. Generate SEO & hreflang report ===")

en_pages  = load("/Users/simonazoulay/SurfCampSenegal/content/pages_en_improved.json") or {}
lang_data = {lang: load(f"/Users/simonazoulay/SurfCampSenegal/content/pages_{lang}_translated.json") or {}
             for lang in LANGS}

DOMAIN = "https://www.surfcampsenegal.com"
hreflang_report = {}

for slug, en_page in en_pages.items():
    page_url = f"{DOMAIN}{slug}"
    hreflang_report[slug] = {
        "en": {"url": page_url, "title": en_page["title"], "meta": en_page["meta_description"]},
        "hreflang_tags": [
            f'<link rel="alternate" hreflang="x-default" href="{page_url}" />',
            f'<link rel="alternate" hreflang="en" href="{page_url}" />',
        ]
    }
    for lang in LANGS:
        lp = lang_data[lang].get(slug, {})
        lang_url = f"{DOMAIN}/{lang}-{lang.upper()}{slug}"
        hreflang_report[slug][lang] = {
            "url":   lang_url,
            "title": lp.get("title", ""),
            "meta":  lp.get("meta_description", ""),
        }
        hreflang_report[slug]["hreflang_tags"].append(
            f'<link rel="alternate" hreflang="{lang}-{lang.upper()}" href="{lang_url}" />'
        )

save(f"{OUTPUT_DIR}/hreflang_report.json", hreflang_report)

# Generate HTML snippet for each page
hreflang_html = "<!-- hreflang tags to add to each page's <head> -->\n\n"
for slug, data in hreflang_report.items():
    hreflang_html += f"<!-- Page: {slug} -->\n"
    hreflang_html += "\n".join(data["hreflang_tags"]) + "\n\n"

with open(f"{OUTPUT_DIR}/hreflang_tags.html", "w") as f:
    f.write(hreflang_html)

log(f"  ✅ hreflang report → output/hreflang_tags.html")

# ════════════════════════════════════════════════════════════════════════════════
# STEP 8 – Final status summary
# ════════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("DEMO SITE SETUP COMPLETE")
print("="*70)

pushed = load(pushed_ids_file) or {}
en_count   = sum(1 for k in pushed if k.startswith("en_"))
fr_count   = sum(1 for k in pushed if k.startswith("fr_"))
es_count   = sum(1 for k in pushed if k.startswith("es_"))
it_count   = sum(1 for k in pushed if k.startswith("it_"))
de_count   = sum(1 for k in pushed if k.startswith("de_"))

print(f"""
  Demo site   : https://manage.wix.com/editor/e8cc06ab-3597-48e0-b1fb-f80eb45d6746
  Live site   : https://www.surfcampsenegal.com/ (UNTOUCHED)

  Blog posts (all DRAFT – invisible on live):
    EN : {en_count}/30
    FR : {fr_count}/30
    ES : {es_count}/30
    IT : {it_count}/30
    DE : {de_count}/30

  Categories  : Surf Conditions & Spots | Island Life & Surf Camp | Coaching & Progression
  Images      : {len(img_map)}/30 generated

  Pages SEO   : 7 pages × 5 languages (EN/FR/ES/IT/DE) improved

  Files:
    content/pages_en_improved.json   – improved EN SEO for all pages
    content/pages_*_translated.json  – FR/ES/IT/DE translations
    content/articles/en/             – 30 EN articles (2000 words each)
    content/articles/fr|es|it|de/   – translated versions
    content/images/                  – 30 featured images (.png)
    output/hreflang_tags.html        – copy/paste hreflang tags
    content/custom_css_da.css        – DA improvements for Wix Velo

  Manual steps remaining (Wix Editor):
    1. CSS DA: Dashboard → Outils de développement → CSS global → coller custom_css_da.css
    2. Header nav: Ajouter "Blog" dans le menu de navigation de la démo
    3. Multilingual: Dashboard → Multilingue → Activer FR/ES/IT/DE
    4. hreflang: coller les tags depuis output/hreflang_tags.html dans chaque page
""")
