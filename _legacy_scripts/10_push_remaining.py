"""
Push remaining articles (IT/DE) to demo + generate all images with correct size.
DEMO ONLY — never touches the live site.
"""
import json, os, re, requests, time
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

OPENAI_KEY  = "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"
WIX_KEY     = open("/Users/simonazoulay/SurfCampSenegal/clesapi.txt").read().strip()
BASE        = "https://www.wixapis.com"
SITE_DEMO   = "e8cc06ab-3597-48e0-b1fb-f80eb45d6746"   # DEMO ONLY
MEMBER_ID   = "c2467ffa-759d-4bb8-bd93-1544d1f6f10d"
ARTICLES_DIR = "/Users/simonazoulay/SurfCampSenegal/content/articles"
IMAGES_DIR   = "/Users/simonazoulay/SurfCampSenegal/content/images"
OUTPUT_DIR   = "/Users/simonazoulay/SurfCampSenegal/output"
LANGS        = ["en", "fr", "es", "it", "de"]

os.makedirs(IMAGES_DIR, exist_ok=True)
client     = OpenAI(api_key=OPENAI_KEY)
print_lock = threading.Lock()
def log(msg): 
    with print_lock: print(msg, flush=True)

def load(path):
    if os.path.exists(path):
        try:
            with open(path) as f: return json.load(f)
        except: return None
    return None

def save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path,"w") as f: json.dump(data,f,indent=2,ensure_ascii=False)

def H():
    return {"Authorization": WIX_KEY, "Content-Type": "application/json",
            "wix-site-id": SITE_DEMO}

# Load pushed post IDs
pushed_ids_file = f"{OUTPUT_DIR}/demo_pushed_posts.json"
pushed_ids = load(pushed_ids_file) or {}
push_lock  = threading.Lock()

# Category IDs
cat_ids = load(f"{OUTPUT_DIR}/demo_category_ids.json") or {}

# ── Get existing draft posts on demo to avoid duplicates ─────────────────────
print("=== Getting existing demo posts ===")
existing = {}
offset = 0
while True:
    r = requests.post(BASE+"/blog/v3/draft-posts/query", headers=H(),
        json={"query":{"paging":{"limit":100,"offset":offset}}}, timeout=20)
    posts = r.json().get("draftPosts", [])
    for p in posts:
        existing[p["title"]] = p["id"]
    if len(posts) < 100:
        break
    offset += 100

print(f"Existing draft posts on demo: {len(existing)}")

# ── Push article function ─────────────────────────────────────────────────────
def push_article(art_data, lang):
    slug  = art_data["slug"]
    key   = f"{lang}_{slug}"
    title = art_data["title"]

    if key in pushed_ids or title in existing:
        log(f"  [skip] {lang} {title[:45]}")
        return key, "skipped"

    cat_name = art_data.get("category","")
    cat_id   = cat_ids.get(cat_name,"")

    content  = art_data.get("content_markdown","")
    excerpt  = re.sub(r'[#*\[\]`]','', content[:400]).strip()[:270].rsplit(" ",1)[0] + "..."

    body = {
        "draftPost": {
            "title":             title,
            "excerpt":           excerpt,
            "memberId":          MEMBER_ID,
            "language":          lang,
            "commentingEnabled": True,
            "featured":          art_data.get("type") == "hero",
            "categoryIds":       [cat_id] if cat_id else [],
            "seoData": {
                "tags": [
                    {"type":"TITLE","custom":True,"disabled":False,
                     "children": title},
                    {"type":"DESCRIPTION","custom":True,"disabled":False,
                     "children": art_data.get("meta_description", excerpt[:155])},
                ]
            },
        }
    }

    r = requests.post(BASE+"/blog/v3/draft-posts", headers=H(), json=body, timeout=20)
    if r.status_code in [200, 201]:
        post_id = r.json().get("draftPost",{}).get("id","")
        log(f"  ✅ [{lang}] {title[:50]}")
        with push_lock:
            pushed_ids[key] = post_id
            save(pushed_ids_file, pushed_ids)
        return key, post_id
    else:
        log(f"  ❌ [{lang}] {title[:40]}: {r.status_code} | {r.text[:150]}")
        return key, None

# ── Push each language ────────────────────────────────────────────────────────
for lang in LANGS:
    lang_dir = f"{ARTICLES_DIR}/{lang if lang != 'en' else 'en'}"
    if not os.path.exists(lang_dir):
        print(f"\n  {lang}: directory not found, skipping")
        continue

    arts = []
    for fname in sorted(os.listdir(lang_dir)):
        if fname.endswith(".json"):
            a = load(f"{lang_dir}/{fname}")
            if a:
                arts.append(a)

    already  = sum(1 for a in arts if f"{lang}_{a['slug']}" in pushed_ids
                                     or a['title'] in existing)
    todo     = [a for a in arts if f"{lang}_{a['slug']}" not in pushed_ids
                                  and a['title'] not in existing]

    print(f"\n  {lang.upper()}: {len(arts)} articles | {already} already pushed | {len(todo)} to push")
    if not todo:
        continue

    with ThreadPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(push_article, a, lang): a for a in todo}
        for f in as_completed(futs):
            f.result()

# ════════════════════════════════════════════════════════════════════════════════
# STEP 2 – Generate featured images (correct sizes for gpt-image-1.5-2025-12-16)
# ════════════════════════════════════════════════════════════════════════════════
print("\n=== Generate featured images (gpt-image-1.5-2025-12-16) ===")

strategy = load("/Users/simonazoulay/SurfCampSenegal/content/blog_strategy.json")
arts_list = strategy["articles"]

def generate_image(article):
    slug     = article["slug"]
    img_path = f"{IMAGES_DIR}/{slug}.png"
    if os.path.exists(img_path) and os.path.getsize(img_path) > 10000:
        log(f"  [skip img] {slug[:40]}")
        return slug, img_path

    hero_prompt = article.get("hero_image_prompt","")
    if not hero_prompt:
        hero_prompt = f"Surf photography: {article['title']}, Ngor Island, Senegal, warm golden light."

    full_prompt = (
        f"{hero_prompt} "
        "Editorial surf photography style, cinematic composition, "
        "warm golden West African light, turquoise ocean waves, "
        "authentic atmosphere, no text, no watermarks, ultra-realistic."
    )

    for model, size in [
        ("gpt-image-1.5-2025-12-16", "1536x1024"),
        ("gpt-image-1.5-2025-12-16", "1024x1024"),
        ("dall-e-3",                  "1792x1024"),
        ("dall-e-3",                  "1024x1024"),
    ]:
        try:
            kwargs = dict(model=model, prompt=full_prompt[:1500], n=1, size=size)
            if model.startswith("dall-e"): kwargs["quality"] = "hd"
            resp = client.images.generate(**kwargs)
            url  = resp.data[0].url
            if not url and hasattr(resp.data[0], 'b64_json'):
                import base64
                img_bytes = base64.b64decode(resp.data[0].b64_json)
            else:
                img_bytes = requests.get(url, timeout=30).content
            with open(img_path, "wb") as f: f.write(img_bytes)
            log(f"  ✅ Image [{model[:20]}]: {slug[:40]} ({len(img_bytes)//1024}KB)")
            return slug, img_path
        except Exception as e:
            log(f"  ⚠️  {model} {size}: {e}")
            continue

    log(f"  ❌ All image attempts failed: {slug[:40]}")
    return slug, None

print(f"  Generating {len(arts_list)} images (10 parallel workers)...")
img_map = {}
with ThreadPoolExecutor(max_workers=10) as ex:
    futs = {ex.submit(generate_image, a): a for a in arts_list}
    for f in as_completed(futs):
        slug, path = f.result()
        if path: img_map[slug] = path

print(f"\nImages generated: {len(img_map)}/{len(arts_list)}")

# ════════════════════════════════════════════════════════════════════════════════
# FINAL STATUS
# ════════════════════════════════════════════════════════════════════════════════
r = requests.post(BASE+"/blog/v3/draft-posts/query", headers=H(),
    json={"query":{"paging":{"limit":200}}}, timeout=20)
all_posts = r.json().get("draftPosts",[])
lang_counts = {}
for p in all_posts:
    l = p.get("language","?")
    lang_counts[l] = lang_counts.get(l,0)+1

print("\n" + "="*70)
print("DEMO SITE — FINAL STATUS")
print("="*70)
print(f"\n  Blog posts (all DRAFT — invisible on live site):")
for l in ["en","fr","es","it","de"]:
    count = lang_counts.get(l,0)
    bar   = "✅" if count >= 30 else "⚠️ "
    print(f"    {bar} {l.upper()}: {count}/30")

print(f"\n  Featured images: {len(img_map)}/30")
print(f"  Categories: Surf Conditions & Spots | Island Life & Surf Camp | Coaching & Progression")
print(f"""
  Remaining manual steps in Wix Editor (DEMO site only):
  ──────────────────────────────────────────────────────
  1. CSS DA improvements:
     Dashboard → Outils de développement → CSS global
     → Coller le contenu de: content/custom_css_da.css

  2. Header navigation — ajouter "Blog":
     Éditeur → Menu principal → Ajouter lien → /blog

  3. Multilingual:
     Dashboard → Multilingue → Activer FR/ES/IT/DE
     → Utiliser les traductions dans content/pages/

  4. hreflang tags:
     Pour chaque page → Paramètres → SEO → Code head
     → Coller les tags de: content/pages/hreflang_all_pages.html

  5. Upload featured images:
     Blog → chaque article → Modifier → Image à la une
     → Fichiers: content/images/*.png
""")
