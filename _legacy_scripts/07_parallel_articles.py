"""
Génère 30 articles EN en parallèle (30 workers simultanés)
+ 4 × 30 traductions en parallèle
IMPORTANT: LECTURE SEULE sur le site live. Tout contenu va sur la démo.
"""
import json, os, re, time
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

OPENAI_KEY   = "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"
MODEL        = "gpt-5.4-2026-03-05"
OUT_DIR      = "/Users/simonazoulay/SurfCampSenegal/content"
ARTICLES_DIR = f"{OUT_DIR}/articles"
LANGS        = ["fr", "es", "it", "de"]
LANG_NAMES   = {"fr": "French", "es": "Spanish", "it": "Italian", "de": "German"}

for d in [f"{ARTICLES_DIR}/en"] + [f"{ARTICLES_DIR}/{l}" for l in LANGS]:
    os.makedirs(d, exist_ok=True)

client     = OpenAI(api_key=OPENAI_KEY)
print_lock = threading.Lock()

def log(msg):
    with print_lock:
        print(msg, flush=True)

def gpt(prompt, temperature=0.75, max_tokens=4000):
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_completion_tokens=max_tokens,
    )
    return resp.choices[0].message.content

def save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load(path):
    if os.path.exists(path):
        try:
            with open(path) as f:
                return json.load(f)
        except Exception:
            return None
    return None

# ── Load strategy ─────────────────────────────────────────────────────────────
strategy = load(f"{OUT_DIR}/blog_strategy.json")
if not strategy:
    raise SystemExit("blog_strategy.json not found – run 05b first")

cats = strategy["categories"]
arts = strategy["articles"]
cats_by_name = {c["name"]: c for c in cats}

SITE_CONTEXT = """Ngor Surfcamp Teranga | Premium surf camp | Ngor Island, Dakar, Senegal
Licensed by Senegalese Federation of Surfing | All levels | Video coaching
World-class waves: Ngor Right + Ngor Left | Featured in The Endless Summer (1964)
Pool, sea views, no cars on island | +221 78 925 70 25 | surfcampsenegal.com"""

# ════════════════════════════════════════════════════════════════════════════════
# STEP D – Generate EN articles (30 workers in parallel)
# ════════════════════════════════════════════════════════════════════════════════
def generate_en_article(article):
    art_slug = article["slug"]
    art_file = f"{ARTICLES_DIR}/en/{art_slug}.json"
    if load(art_file):
        log(f"  [skip EN] {article['title'][:55]}")
        return art_slug, "skipped"

    cat_info = cats_by_name.get(article.get("category", ""), {})
    log(f"  ▶ Generating EN #{article['id']}: {article['title'][:55]}")

    prompt = f"""You are a professional surf travel writer who knows Senegal intimately.
Write with authentic passion – real insider knowledge, vivid scenes, NO generic AI clichés.

{SITE_CONTEXT}

Article:
Title: {article['title']}
Category: {article.get('category')} – {cat_info.get('description', '')}
Focus keyword: {article['focus_keyword']}
Secondary keywords: {', '.join(article.get('secondary_keywords', []))}
Audience: {article['target_audience']}
Brief: {article['brief']}

Write a 2000-word article. Structure:
META: [compelling meta description, max 155 chars]

# [H1]

[150-word hook intro with vivid scene or surprising fact]

## [H2 with focus keyword]
[~350 words]

## [H2]
[~350 words]

## [H2]
[~350 words]

## [H2]
[~350 words]

## [H2 – practical tips]
[~350 words]

## Ready to Ride? Book at Ngor Surfcamp Teranga
[~150 words, authentic CTA, mention coaching, location, WhatsApp +221 78 925 70 25]

## FAQ
**[Question]**
[50-80 word answer]
**[Question 2]**
[50-80 word answer]

Add 2-3 internal links: [LINK: anchor text → /page-slug]"""

    try:
        content = gpt(prompt, temperature=0.75, max_tokens=4000)
        meta = ""
        body = content
        if content.startswith("META:"):
            lines = content.split("\n", 2)
            meta  = lines[0].replace("META:", "").strip()
            body  = "\n".join(lines[1:]).strip()

        data = {
            "id": article["id"],
            "title": article["title"],
            "slug": art_slug,
            "category": article.get("category"),
            "focus_keyword": article["focus_keyword"],
            "secondary_keywords": article.get("secondary_keywords", []),
            "type": article.get("type"),
            "hero_image_prompt": article.get("hero_image_prompt", ""),
            "target_audience": article.get("target_audience"),
            "lang": "en",
            "meta_description": meta,
            "content_markdown": body,
            "word_count_estimate": len(body.split()),
        }
        save(art_file, data)
        log(f"  ✅ EN #{article['id']} done (~{data['word_count_estimate']}w)")
        return art_slug, "done"
    except Exception as e:
        log(f"  ❌ EN #{article['id']} error: {e}")
        return art_slug, f"error: {e}"

print("\n" + "="*70)
print("STEP D: Generate 30 EN articles (30 parallel workers)")
print("="*70)

with ThreadPoolExecutor(max_workers=30) as ex:
    futures = {ex.submit(generate_en_article, art): art for art in arts}
    done_count = 0
    for future in as_completed(futures):
        slug, status = future.result()
        done_count += 1
        log(f"  Progress: {done_count}/30")

en_files = [f for f in os.listdir(f"{ARTICLES_DIR}/en") if f.endswith(".json")]
print(f"\nEN articles ready: {len(en_files)}/30")

# ════════════════════════════════════════════════════════════════════════════════
# STEP E – Translate all articles × 4 languages (120 parallel workers)
# ════════════════════════════════════════════════════════════════════════════════
def translate_article(art_data, lang):
    art_slug = art_data["slug"]
    out_file = f"{ARTICLES_DIR}/{lang}/{art_slug}.json"
    if load(out_file):
        log(f"  [skip {lang}] {art_data['title'][:45]}")
        return lang, art_slug, "skipped"

    log(f"  ▶ Translating {lang} #{art_data['id']}: {art_data['title'][:45]}")
    lang_name = LANG_NAMES[lang]

    prompt = f"""You are a professional surf travel writer writing in {lang_name}.
Rewrite this article for {lang_name}-speaking surfers. Same structure, same depth.
Adapt tone and cultural references. Surf terms can stay in English if natural.

{SITE_CONTEXT}

Original article (translate/adapt to {lang_name}):
{art_data['content_markdown'][:3500]}

Output format:
META: [meta description in {lang_name}, max 155 chars]
# [H1 in {lang_name}]
[full article ~2000 words in {lang_name}]"""

    try:
        content = gpt(prompt, temperature=0.7, max_tokens=4000)
        meta = ""
        body = content
        if content.startswith("META:"):
            lines = content.split("\n", 2)
            meta  = lines[0].replace("META:", "").strip()
            body  = "\n".join(lines[1:]).strip()

        # Extract translated title from H1
        title_trans = art_data["title"]
        m = re.search(r'^#\s+(.+)$', body, re.MULTILINE)
        if m:
            title_trans = m.group(1).strip()

        save(out_file, {
            **art_data,
            "lang": lang,
            "title": title_trans,
            "meta_description": meta,
            "content_markdown": body,
            "word_count_estimate": len(body.split()),
            "original_en_slug": art_slug,
        })
        log(f"  ✅ {lang} #{art_data['id']} done (~{len(body.split())}w)")
        return lang, art_slug, "done"
    except Exception as e:
        log(f"  ❌ {lang} #{art_data['id']} error: {e}")
        return lang, art_slug, f"error: {e}"

print("\n" + "="*70)
print("STEP E: Translate 30 articles × 4 languages (up to 120 parallel workers)")
print("="*70)

# Load all EN articles
en_articles = []
en_dir = f"{ARTICLES_DIR}/en"
for fname in sorted(os.listdir(en_dir)):
    if fname.endswith(".json"):
        a = load(f"{en_dir}/{fname}")
        if a:
            en_articles.append(a)

print(f"EN articles loaded: {len(en_articles)}")

# Build all translation tasks
tasks = [(art, lang) for lang in LANGS for art in en_articles]
print(f"Translation tasks: {len(tasks)} ({len(en_articles)} articles × {len(LANGS)} langs)")

with ThreadPoolExecutor(max_workers=30) as ex:
    futures = {ex.submit(translate_article, art, lang): (lang, art["slug"]) for art, lang in tasks}
    done_count = 0
    for future in as_completed(futures):
        lang, slug = futures[future]
        result = future.result()
        done_count += 1
        if done_count % 10 == 0:
            log(f"  Translation progress: {done_count}/{len(tasks)}")

# Final count
for lang in LANGS:
    files = [f for f in os.listdir(f"{ARTICLES_DIR}/{lang}") if f.endswith(".json")]
    print(f"  {lang}: {len(files)}/30 articles")

print("\n✅ All articles generated and translated!")
print(f"Output: {ARTICLES_DIR}")
