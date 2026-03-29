"""
Step 5b – Generate blog strategy + 30 articles + translations
Resumes from where 05_generate_content.py left off (pages already done)
"""
import json, os, time, re
from openai import OpenAI

OPENAI_KEY   = "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"
MODEL        = "gpt-5.4-2026-03-05"
OUT_DIR      = "/Users/simonazoulay/SurfCampSenegal/content"
ARTICLES_DIR = f"{OUT_DIR}/articles"
os.makedirs(ARTICLES_DIR, exist_ok=True)

client = OpenAI(api_key=OPENAI_KEY)

def gpt(messages, temperature=0.7, max_tokens=4000):
    resp = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=temperature,
        max_completion_tokens=max_tokens,
    )
    return resp.choices[0].message.content

def extract_json(text):
    """Extract and parse the first JSON object or array from text."""
    if not text:
        return None
    text = text.strip()
    # 1. Direct parse (clean response)
    try:
        return json.loads(text)
    except Exception:
        pass
    # 2. ```json fenced block
    m = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if m:
        try:
            return json.loads(m.group(1).strip())
        except Exception:
            pass
    # 3. Find first [ or { and extract to matching close
    for start, end in [("[", "]"), ("{", "}")]:
        idx = text.find(start)
        if idx == -1:
            continue
        # find matching close by counting depth (ignoring strings)
        depth = 0
        in_str = False
        esc = False
        for i, ch in enumerate(text[idx:], idx):
            if esc:
                esc = False
                continue
            if ch == "\\":
                esc = True
                continue
            if ch == '"':
                in_str = not in_str
            if not in_str:
                if ch == start:
                    depth += 1
                elif ch == end:
                    depth -= 1
                    if depth == 0:
                        try:
                            return json.loads(text[idx:i+1])
                        except Exception:
                            break
    raise ValueError(f"Could not extract JSON from: {text[:200]}")

def save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  ✅ Saved: {os.path.basename(path)}")

def load(path):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None

SITE_CONTEXT = """
Site: Ngor Surfcamp Teranga | Premium surf camp on Ngor Island, Dakar, Senegal
URL: https://www.surfcampsenegal.com/
Licensed by the Senegalese Federation of Surfing | All levels (beginner → advanced)
Professional coaching with video analysis | Pool, sea views, no cars on the island
Featured in The Endless Summer (1964) | World-class waves: Ngor Right + Ngor Left
WhatsApp: +221 78 925 70 25 | Email: info@surfcampsenegal.com
Top markets: France, Germany, Spain, Italy, UK, USA, Belgium
"""

LANGS = ["fr", "es", "it", "de"]
LANG_NAMES = {"fr": "French", "es": "Spanish", "it": "Italian", "de": "German"}

# ════════════════════════════════════════════════════════════════════════════════
# STEP C – Blog strategy: 3 categories + 30 article briefs
# ════════════════════════════════════════════════════════════════════════════════
print("="*70)
print("STEP C: Blog strategy")
print("="*70)

strategy_file = f"{OUT_DIR}/blog_strategy.json"
strategy = load(strategy_file)

if not strategy:
    print("  Generating categories...")
    cats_prompt = f"""You are a content strategist for a premium surf camp.

{SITE_CONTEXT}

Create exactly 3 blog categories for Ngor Surfcamp Teranga's blog. Return ONLY valid JSON array:
[
  {{"name": "category name", "slug": "category-slug", "description": "1-sentence description", "color": "#hexcolor"}},
  ...
]

The 3 categories should cover: surf conditions/spots, surf camp lifestyle, and learning/progression."""

    cats_raw = gpt([{"role":"user","content":cats_prompt}], temperature=0.5, max_tokens=500)
    cats = extract_json(cats_raw)
    # Ensure it's a list
    if isinstance(cats, str):
        cats = json.loads(cats)
    if isinstance(cats, dict) and "categories" in cats:
        cats = cats["categories"]
    print(f"  Categories: {[c['name'] for c in cats]}")

    print("  Generating 30 article briefs (2 batches of 15)...")
    cats_str = json.dumps([c['name'] for c in cats])
    ARTS_SCHEMA = '{"id":N,"title":"...","slug":"...","category":"cat name","type":"hero|seo","focus_keyword":"...","secondary_keywords":["kw1","kw2"],"target_audience":"...","intent":"informational","hero_image_prompt":"vivid 35-word DA brief","brief":"2-3 sentence content brief"}'

    def gen_batch(start_id, count, type_label, extra_kw_hint=""):
        prompt = f"""Content strategist for Ngor Surfcamp Teranga surf camp blog.
{SITE_CONTEXT}
SEO opportunities: "surf camp senegal" pos 25, "surf camp dakar" pos 24, "senegal surf camp" pos 42, "ngor surf" pos 56.
Categories: {cats_str}
{extra_kw_hint}
Generate exactly {count} article briefs (ids {start_id} to {start_id+count-1}), all type="{type_label}".
Return ONLY a valid JSON array of exactly {count} objects. Schema: {ARTS_SCHEMA}"""
        raw = gpt([{"role":"user","content":prompt}], temperature=0.6, max_tokens=5000)
        try:
            result = extract_json(raw)
        except Exception:
            m = re.search(r'\[[\s\S]*\]', raw)
            result = json.loads(m.group(0)) if m else []
        if isinstance(result, dict):
            result = result.get("articles", [])
        return result or []

    arts = gen_batch(1, 10, "hero")
    print(f"  Batch 1 (hero): {len(arts)} articles")
    seo_arts = gen_batch(11, 20, "seo",
        "Focus on long-tail keywords: best time to surf senegal, learn to surf dakar, ngor island waves, etc.")
    print(f"  Batch 2 (seo): {len(seo_arts)} articles")
    arts = arts + seo_arts
    print(f"  Total: {len(arts)} articles")

    strategy = {"categories": cats, "articles": arts}
    save(strategy_file, strategy)
else:
    print(f"  [skip] Strategy already exists: {len(strategy['categories'])} cats, {len(strategy['articles'])} articles")

cats = strategy["categories"]
arts = strategy["articles"]

print(f"\n  Categories:")
for c in cats:
    print(f"    {c['name']} ({c['slug']})")
print(f"  Articles: {len(arts)} ({sum(1 for a in arts if a.get('type')=='hero')} hero + {sum(1 for a in arts if a.get('type')=='seo')} seo)")

# ════════════════════════════════════════════════════════════════════════════════
# STEP D – Generate full articles
# ════════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("STEP D: Generate full articles (2000 words each)")
print("="*70)

for i, article in enumerate(arts):
    art_id   = article.get("id", i+1)
    art_slug = article.get("slug", f"article-{art_id}")
    art_file = f"{ARTICLES_DIR}/en/{art_slug}.json"

    if load(art_file):
        words = load(art_file).get("word_count_estimate", 0)
        print(f"  [skip] #{art_id}: {article['title'][:55]} ({words}w)")
        continue

    print(f"\n  [{i+1}/30] Generating: {article['title'][:60]}")
    cat_info = next((c for c in cats if c["name"] == article.get("category")), {})

    prompt = f"""You are a professional surf travel writer who knows Senegal intimately.
Write in an authentic, passionate voice – real insider knowledge, vivid imagery, NO generic AI clichés.

{SITE_CONTEXT}

Article:
Title: {article['title']}
Category: {article.get('category')} – {cat_info.get('description','')}
Focus keyword: {article['focus_keyword']}
Secondary keywords: {', '.join(article.get('secondary_keywords',[]))}
Audience: {article['target_audience']}
Brief: {article['brief']}

Write a full 2000-word article. Structure:
META: [compelling meta description, max 155 chars]

# [H1 – exact or improved title]

[Hook intro paragraph – 150 words, grab attention with a vivid scene or surprising fact]

## [H2 – includes focus keyword]
[~350 words]

## [H2]
[~350 words]

## [H2]
[~350 words]

## [H2]
[~350 words]

## [H2 – practical info or tips]
[~350 words]

## Ready to Ride? Book Your Spot at Ngor Surfcamp Teranga
[~150 word CTA – authentic, not pushy. Mention: coaching, Ngor Island location, +221 78 925 70 25]

## FAQ

**[Question naturally asked about this topic]**
[Concise answer, 50-80 words]

**[Second question]**
[Concise answer, 50-80 words]

Also naturally include: [LINK: anchor text → /page-slug] for 2-3 internal links."""

    try:
        content = gpt([{"role":"user","content":prompt}], temperature=0.75, max_tokens=4000)

        meta = ""
        body = content
        if content.startswith("META:"):
            lines = content.split("\n", 2)
            meta = lines[0].replace("META:","").strip()
            body = "\n".join(lines[1:]).strip()

        art_data = {
            "id": art_id,
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
        os.makedirs(f"{ARTICLES_DIR}/en", exist_ok=True)
        save(art_file, art_data)
        print(f"     Words: ~{art_data['word_count_estimate']}")
        time.sleep(0.3)
    except Exception as e:
        print(f"    ERROR #{art_id}: {e}")

# Check how many generated
en_files = os.listdir(f"{ARTICLES_DIR}/en") if os.path.exists(f"{ARTICLES_DIR}/en") else []
print(f"\nTotal EN articles generated: {len(en_files)}/30")

# ════════════════════════════════════════════════════════════════════════════════
# STEP E – Translate article titles/excerpts/slugs (batch per language)
# ════════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("STEP E: Translate article metadata (FR/ES/IT/DE)")
print("="*70)

for lang in LANGS:
    lang_dir = f"{ARTICLES_DIR}/{lang}"
    os.makedirs(lang_dir, exist_ok=True)
    trans_file = f"{lang_dir}/_index.json"
    trans_index = load(trans_file) or {}

    todo = [a for a in arts if a["slug"] not in trans_index]
    if not todo:
        print(f"  [skip] {lang} – all {len(trans_index)} articles translated")
        continue

    print(f"\n  Translating {lang}: {len(todo)} articles...")
    # Batch all in one call
    batch = "\n".join([f"{i+1}. id={a['id']} slug={a['slug']} title={a['title']} keyword={a['focus_keyword']}" for i,a in enumerate(todo)])

    prompt = f"""Translate these {len(todo)} surf camp blog article titles and metadata to {LANG_NAMES[lang]}.
Context: Articles for Ngor Surfcamp Teranga, premium surf camp in Senegal (Ngor Island, Dakar).
Audience: {LANG_NAMES[lang]}-speaking surfers and surf travelers.

English articles:
{batch}

Return ONLY a valid JSON array with one entry per article:
[
  {{
    "slug": "original-english-slug",
    "title": "translated title in {LANG_NAMES[lang]}",
    "meta_description": "translated meta description (max 155 chars)",
    "excerpt": "2-sentence excerpt in {LANG_NAMES[lang]}",
    "slug_{lang}": "seo-friendly slug in {lang}"
  }}
]"""

    try:
        raw = gpt([{"role":"user","content":prompt}], temperature=0.4, max_tokens=4000)
        translations = extract_json(raw)
        for t in translations:
            trans_index[t["slug"]] = t
        save(trans_file, trans_index)
        print(f"  ✅ {lang}: {len(translations)} articles translated")
    except Exception as e:
        print(f"  ERROR {lang}: {e}")
        if 'raw' in dir():
            print(f"  Raw (first 300): {raw[:300]}")

# ════════════════════════════════════════════════════════════════════════════════
# STEP F – Generate full article translations (FR only first as proof of concept,
#          then ES/IT/DE – each article rewritten, not just translated)
# ════════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("STEP F: Full article translation (all languages)")
print("="*70)

en_articles = []
if os.path.exists(f"{ARTICLES_DIR}/en"):
    for fname in sorted(os.listdir(f"{ARTICLES_DIR}/en")):
        if fname.endswith(".json"):
            a = load(f"{ARTICLES_DIR}/en/{fname}")
            if a:
                en_articles.append(a)

print(f"  EN articles available: {len(en_articles)}")

for lang in LANGS:
    lang_dir = f"{ARTICLES_DIR}/{lang}"
    os.makedirs(lang_dir, exist_ok=True)
    done = [f for f in os.listdir(lang_dir) if f.endswith(".json") and not f.startswith("_")]
    print(f"\n  {lang.upper()}: {len(done)}/{len(en_articles)} articles done")

    for art in en_articles:
        art_slug = art["slug"]
        out_file = f"{lang_dir}/{art_slug}.json"
        if os.path.exists(out_file):
            continue

        print(f"    Translating {lang}: {art['title'][:55]}")

        # Get translation metadata if available
        trans_index = load(f"{lang_dir}/_index.json") or {}
        meta_trans = trans_index.get(art_slug, {})
        title_trans = meta_trans.get("title", art["title"])

        prompt = f"""You are a professional surf travel writer writing in {LANG_NAMES[lang]}.
Rewrite/translate this article for a {LANG_NAMES[lang]}-speaking audience. Keep the same structure,
depth and insider knowledge – adapt cultural references and tone to {LANG_NAMES[lang]} speakers.

{SITE_CONTEXT}

Original English article (translate to {LANG_NAMES[lang]}):
Focus keyword: {art['focus_keyword']}
Translated title: {title_trans}

Content:
{art['content_markdown'][:3000]}

Write the full {LANG_NAMES[lang]} version (same ~2000 words, same structure). Start with:
META: [meta description in {LANG_NAMES[lang]}, max 155 chars]

# [H1 in {LANG_NAMES[lang]}]

[full article body]"""

        try:
            content = gpt([{"role":"user","content":prompt}], temperature=0.7, max_tokens=4000)
            meta = ""
            body = content
            if content.startswith("META:"):
                lines = content.split("\n", 2)
                meta = lines[0].replace("META:","").strip()
                body = "\n".join(lines[1:]).strip()

            save(out_file, {
                **art,
                "lang": lang,
                "title": title_trans,
                "meta_description": meta,
                "content_markdown": body,
                "word_count_estimate": len(body.split()),
                "original_en_slug": art_slug,
            })
            time.sleep(0.3)
        except Exception as e:
            print(f"    ERROR: {e}")

print("\n✅ All article generation complete!")
