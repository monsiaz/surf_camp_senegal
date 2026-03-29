"""
Step 5 – Generate all content via gpt-5.4-2026-03-05
  • Improved English page content (meta, H1, body, OG)
  • 30 blog articles (2000 words each)
  • Translations: fr-fr, es-es, it-it, de-de
  • hreflang strategy per page
"""
import json, os, time
from openai import OpenAI

OPENAI_KEY = "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"
MODEL      = "gpt-5.4-2026-03-05"
OUT_DIR    = "/Users/simonazoulay/SurfCampSenegal/content"
ARTICLES_DIR = f"{OUT_DIR}/articles"
os.makedirs(ARTICLES_DIR, exist_ok=True)

client = OpenAI(api_key=OPENAI_KEY)

def gpt(messages, temperature=0.7, max_tokens=4096):
    resp = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=temperature,
        max_completion_tokens=max_tokens,
    )
    return resp.choices[0].message.content

def save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  ✅ Saved: {path}")

def load(path):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None

# ════════════════════════════════════════════════════════════════════════════════
# SITE CONTEXT (from SC + public site content)
# ════════════════════════════════════════════════════════════════════════════════
SITE_CONTEXT = """
Site: Ngor Surfcamp Teranga
URL: https://www.surfcampsenegal.com/
Location: Ngor Island, 800m west of Cap-Vert peninsula, Dakar, Senegal
Type: Premium surf camp and surf house

Key info:
- Licensed by the Senegalese Federation of Surfing
- All levels: beginner, intermediate, advanced
- Professional surf coaching with video analysis
- Cozy rooms, swimming pool, sea views
- No cars on the island – pure surf vibe
- World-class waves: Ngor Right, Ngor Left
- Featured in "The Endless Summer" (1964)
- WhatsApp: +221 78 925 70 25
- Email: info@surfcampsenegal.com

Pages: Home, Surf House, Island, Book Online, Surfing, Gallery, FAQ

Top SC queries (by impressions): surf camp senegal (1056), surf camp dakar (642),
senegal surf camp (768), ngor surf (672), ngor surf camp (553), dakar surf camp (629),
senegal surf (477), cours de surf dakar (7), surf ngor (67)

Top traffic countries: France, Senegal, Germany, Spain, UK, Belgium, Italy
Languages to target: EN (default/.com), /fr-fr/, /es-es/, /it-it/, /de-de/
"""

PAGES = [
    {
        "slug": "/",
        "name": "Homepage",
        "current_title": "Ngor Surfcamp Teranga – Surf Senegal from Ngor Island",
        "current_h1": "Ngor Surfcamp Teranga – Premium Surfcamp in Senegal",
        "current_desc": "Live the surfing spirit to the rhythm of West Africa. Ngor Surfcamp Teranga is much more than a surfcamp, it's an experience!",
    },
    {
        "slug": "/ngor-surf-house",
        "name": "Surf House",
        "current_title": "Surf House | Ngor Surfcamp Teranga",
        "current_h1": "The Surfhouse – Your home by the ocean",
        "current_desc": "Cozy rooms, swimming pool, sea views, chill community vibe steps away from the waves on Ngor Island, Dakar.",
    },
    {
        "slug": "/ngor-island",
        "name": "Island",
        "current_title": "Ngor Island | Ngor Surfcamp Teranga",
        "current_h1": "The Island – A tropical escape",
        "current_desc": "Ngor Island is a peaceful gem off Dakar, with no cars, stunning views, and a unique surf-meets-art atmosphere.",
    },
    {
        "slug": "/book-surf-trip",
        "name": "Book Online",
        "current_title": "Book Online | Ngor Surfcamp Teranga",
        "current_h1": "Book Your Surf Stay",
        "current_desc": "Check availability and book your surf camp stay at Ngor Island, Dakar, Senegal.",
    },
    {
        "slug": "/surfing",
        "name": "Surfing",
        "current_title": "Surfing | Ngor Surfcamp Teranga",
        "current_h1": "Surfing – Ride world-class waves",
        "current_desc": "Professional surf coaching, video analysis, tailored sessions at Ngor's world-class breaks for all levels.",
    },
    {
        "slug": "/gallery",
        "name": "Gallery",
        "current_title": "Gallery | Ngor Surfcamp Teranga",
        "current_h1": "Gallery",
        "current_desc": "Browse photos and videos from Ngor Surfcamp Teranga – waves, coaching, island life.",
    },
    {
        "slug": "/faq",
        "name": "FAQ",
        "current_title": "FAQ | Ngor Surfcamp Teranga",
        "current_h1": "Frequently Asked Questions",
        "current_desc": "Everything you need to know before booking your surf camp stay at Ngor Island, Senegal.",
    },
]

LANGS = ["fr", "es", "it", "de"]
LANG_NAMES = {"fr": "French", "es": "Spanish", "it": "Italian", "de": "German"}
LANG_LOCALES = {"fr": "fr-FR", "es": "es-ES", "it": "it-IT", "de": "de-DE"}

# ════════════════════════════════════════════════════════════════════════════════
# STEP A – Improve English pages SEO
# ════════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("STEP A: Improve English SEO for all pages")
print("="*70)

en_pages_file = f"{OUT_DIR}/pages_en_improved.json"
en_pages = load(en_pages_file) or {}

for page in PAGES:
    slug = page["slug"]
    if slug in en_pages:
        print(f"  [skip] {slug} already done")
        continue

    print(f"\n  Processing: {page['name']} ({slug})")
    prompt = f"""You are a professional SEO copywriter specializing in surf travel and boutique surf camps.

Site context:
{SITE_CONTEXT}

Page: {page['name']} (URL: https://www.surfcampsenegal.com{slug})
Current title: {page['current_title']}
Current H1: {page['current_h1']}
Current meta description: {page['current_desc']}

Task: Improve the English SEO for this page. Return ONLY valid JSON with these exact fields:
{{
  "title": "optimized title tag (max 60 chars, include primary keyword naturally)",
  "meta_description": "compelling meta description (max 155 chars, include call-to-action)",
  "h1": "page H1 heading (clear, keyword-rich but natural)",
  "og_title": "Open Graph title (can be slightly different from title tag)",
  "og_description": "OG description (slightly more engaging than meta desc)",
  "focus_keyword": "primary target keyword",
  "secondary_keywords": ["list", "of", "secondary", "keywords"],
  "schema_type": "schema.org type (e.g. TouristAttraction, LodgingBusiness)",
  "improvements_note": "brief note on what was improved and why"
}}

Guidelines:
- Primary target: English-speaking surfers from France, Germany, Spain, Italy, UK, USA
- Tone: premium, adventurous, authentic West African surf culture vibe
- Avoid keyword stuffing – write for humans first
- Include location signals (Senegal, Dakar, Ngor Island, West Africa)
- Title should be under 60 characters strictly"""

    try:
        result = gpt([{"role": "user", "content": prompt}], temperature=0.4, max_tokens=1000)
        # extract JSON
        if "```json" in result:
            result = result.split("```json")[1].split("```")[0].strip()
        elif "```" in result:
            result = result.split("```")[1].split("```")[0].strip()
        en_pages[slug] = json.loads(result)
        en_pages[slug]["page_name"] = page["name"]
        save(en_pages_file, en_pages)
        time.sleep(0.5)
    except Exception as e:
        print(f"    ERROR: {e}")
        print(f"    Raw: {result[:200] if 'result' in dir() else 'no result'}")

print(f"\nEnglish pages improved: {len(en_pages)}/{len(PAGES)}")

# ════════════════════════════════════════════════════════════════════════════════
# STEP B – Translate pages to FR, ES, IT, DE
# ════════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("STEP B: Translate pages SEO to FR/ES/IT/DE")
print("="*70)

for lang in LANGS:
    lang_file = f"{OUT_DIR}/pages_{lang}_translated.json"
    lang_pages = load(lang_file) or {}

    for page in PAGES:
        slug = page["slug"]
        if slug not in en_pages:
            continue
        if slug in lang_pages:
            print(f"  [skip] {lang} {slug}")
            continue

        en = en_pages[slug]
        print(f"  Translating {lang}: {page['name']}")
        prompt = f"""You are an expert SEO translator for surf travel content.

Site: Ngor Surfcamp Teranga – Premium surf camp on Ngor Island, Dakar, Senegal
Target language: {LANG_NAMES[lang]} ({LANG_LOCALES[lang]})
Target URL: https://www.surfcampsenegal.com/{LANG_LOCALES[lang].lower()}{slug}

English source (already SEO-optimized):
Title: {en['title']}
Meta description: {en['meta_description']}
H1: {en['h1']}
OG title: {en['og_title']}
OG description: {en['og_description']}
Focus keyword: {en['focus_keyword']}

Task: Translate and localize for {LANG_NAMES[lang]}-speaking surfers. Return ONLY valid JSON:
{{
  "title": "translated title (max 60 chars)",
  "meta_description": "translated meta description (max 155 chars)",
  "h1": "translated H1",
  "og_title": "translated OG title",
  "og_description": "translated OG description",
  "focus_keyword": "best {LANG_NAMES[lang]} keyword equivalent",
  "hreflang": "{LANG_LOCALES[lang].lower()}"
}}

Guidelines:
- Natural, idiomatic {LANG_NAMES[lang]} – not literal translation
- Keep surf terminology authentic (many surf terms stay in English)
- Adapt tone to {LANG_NAMES[lang]}-speaking surf culture
- Maintain SEO intent of the English version"""

        try:
            result = gpt([{"role": "user", "content": prompt}], temperature=0.4, max_tokens=600)
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                result = result.split("```")[1].split("```")[0].strip()
            lang_pages[slug] = json.loads(result)
            save(lang_file, lang_pages)
            time.sleep(0.5)
        except Exception as e:
            print(f"    ERROR: {e}")

# ════════════════════════════════════════════════════════════════════════════════
# STEP C – Define blog strategy + 30 article briefs
# ════════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("STEP C: Define editorial strategy + 30 article briefs")
print("="*70)

strategy_file = f"{OUT_DIR}/blog_strategy.json"
if load(strategy_file):
    print("  [skip] strategy already defined")
    strategy = load(strategy_file)
else:
    prompt = f"""You are an expert content strategist for surf travel brands.

{SITE_CONTEXT}

Search Console data shows these high-impression queries with weak CTR (SEO opportunities):
- "surf camp senegal" → 1056 impressions, pos 25.8
- "surf camp dakar" → 642 impressions, pos 24.2
- "senegal surf camp" → 768 impressions, pos 42.5
- "ngor surf" → 672 impressions, pos 56.5
- "ngor surf camp" → 553 impressions, pos 51.9
- "dakar surf camp" → 629 impressions, pos 30.9

Top audience: France (FR), Senegal, Germany (DE), Spain (ES), UK, Belgium, Italy (IT)

Create a complete blog strategy with:
1. Exactly 3 blog categories (with names, slugs, descriptions)
2. Exactly 30 article briefs (10 "hero/flagship" articles + 20 SEO-targeted articles)

For each article provide:
- title (English, compelling)
- slug (SEO-friendly URL)
- category (one of the 3 categories)
- type: "hero" or "seo"
- focus_keyword (primary SEO target)
- secondary_keywords (list of 3-5)
- target_audience (who is this for)
- word_count: 2000 (all articles)
- intent: "informational" | "navigational" | "commercial"
- hero_image_prompt: (vivid DA brief for the featured image, 50 words max)
- brief: (200 words max – what the article should cover, tone, angle, key points)

Return ONLY valid JSON:
{{
  "categories": [
    {{"name": "...", "slug": "...", "description": "..."}}
  ],
  "articles": [
    {{
      "id": 1,
      "title": "...",
      "slug": "...",
      "category": "...",
      "type": "hero|seo",
      "focus_keyword": "...",
      "secondary_keywords": [],
      "target_audience": "...",
      "word_count": 2000,
      "intent": "...",
      "hero_image_prompt": "...",
      "brief": "..."
    }}
  ]
}}"""

    result = gpt([{"role": "user", "content": prompt}], temperature=0.6, max_tokens=6000)
    if "```json" in result:
        result = result.split("```json")[1].split("```")[0].strip()
    elif "```" in result:
        result = result.split("```")[1].split("```")[0].strip()
    strategy = json.loads(result)
    save(strategy_file, strategy)

cats = strategy.get("categories", [])
arts = strategy.get("articles", [])
print(f"  Categories: {len(cats)}")
for c in cats:
    print(f"    {c['name']} ({c['slug']})")
print(f"  Articles: {len(arts)} ({sum(1 for a in arts if a.get('type')=='hero')} hero + {sum(1 for a in arts if a.get('type')=='seo')} seo)")

# ════════════════════════════════════════════════════════════════════════════════
# STEP D – Generate full articles (2000 words each)
# ════════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("STEP D: Generate full articles (2000 words each)")
print("="*70)

for article in arts:
    art_id    = article.get("id", "?")
    art_slug  = article.get("slug", f"article-{art_id}")
    art_file  = f"{ARTICLES_DIR}/en/{art_slug}.json"

    if load(art_file):
        print(f"  [skip] #{art_id}: {article['title'][:50]}")
        continue

    print(f"\n  Generating #{art_id}: {article['title'][:60]}")
    cat_info = next((c for c in cats if c["name"] == article.get("category")), {})

    prompt = f"""You are a professional surf travel writer with deep knowledge of West Africa, Senegal, and surf culture. Write in an authentic, engaging style – not generic AI content.

{SITE_CONTEXT}

Article brief:
- Title: {article['title']}
- Category: {article.get('category')} – {cat_info.get('description','')}
- Focus keyword: {article['focus_keyword']}
- Secondary keywords: {', '.join(article.get('secondary_keywords',[]))}
- Target audience: {article['target_audience']}
- Intent: {article['intent']}
- Brief: {article['brief']}

Write a complete, 2000-word blog article. Requirements:
1. Natural keyword integration (focus keyword in: title, first paragraph, at least 2 H2s, conclusion)
2. Structure: intro hook → 4-6 H2 sections → conclusion with CTA to book at Ngor Surfcamp Teranga
3. Include: practical tips, local insider knowledge, vivid descriptions of Ngor/Senegal/the waves
4. Tone: authentic, adventurous, passionate about surfing + West African culture. Not corporate.
5. Add 2-3 naturally placed internal link suggestions (format: [LINK: anchor text → /page-slug])
6. Add 1-2 FAQ items at the end (for FAQ schema)
7. Include a compelling meta description (max 155 chars) at the very top, format: META: your description here

Write the full article now. Output format:
META: [meta description]

# [H1 title]

[full article body in markdown with H2/H3 subheadings]

## FAQ

**[Question]**
[Answer]"""

    try:
        content = gpt([{"role": "user", "content": prompt}], temperature=0.75, max_tokens=4000)
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
            "content_markdown": content,
            "word_count_estimate": len(content.split()),
        }
        # extract meta
        if content.startswith("META:"):
            lines = content.split("\n")
            art_data["meta_description"] = lines[0].replace("META:","").strip()
            art_data["content_markdown"] = "\n".join(lines[1:]).strip()
        os.makedirs(f"{ARTICLES_DIR}/en", exist_ok=True)
        save(art_file, art_data)
        time.sleep(0.5)
    except Exception as e:
        print(f"    ERROR: {e}")

print(f"\nArticle generation complete.")

# ════════════════════════════════════════════════════════════════════════════════
# STEP E – Translate articles (FR, ES, IT, DE) – summaries only for blog posts
# ════════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("STEP E: Translate article titles/meta/excerpts for multilingual blog")
print("="*70)

for lang in LANGS:
    lang_dir = f"{ARTICLES_DIR}/{lang}"
    os.makedirs(lang_dir, exist_ok=True)
    trans_index_file = f"{lang_dir}/index.json"
    trans_index = load(trans_index_file) or {}

    slugs_to_translate = [a["slug"] for a in arts if a["slug"] not in trans_index]
    if not slugs_to_translate:
        print(f"  [skip] {lang} all done")
        continue

    print(f"\n  Translating metadata to {lang} ({len(slugs_to_translate)} articles)")

    batch_titles = [(a["slug"], a["title"], a["focus_keyword"]) for a in arts if a["slug"] not in trans_index]
    # Batch all 30 in one call
    batch_str = "\n".join([f"{i+1}. slug={sl} | title={ti} | keyword={kw}" for i,(sl,ti,kw) in enumerate(batch_titles)])

    prompt = f"""Translate these {len(batch_titles)} blog article titles, meta descriptions and slugs to {LANG_NAMES[lang]}.

Context: These are articles for Ngor Surfcamp Teranga, a premium surf camp in Senegal, Ngor Island.
Audience: {LANG_NAMES[lang]}-speaking surfers and travel enthusiasts.

Articles (English):
{batch_str}

For each article return a JSON array entry. Return ONLY valid JSON array:
[
  {{
    "slug": "original-english-slug",
    "title_{lang}": "translated title",
    "meta_{lang}": "translated meta description (max 155 chars)",
    "excerpt_{lang}": "compelling 2-sentence excerpt in {LANG_NAMES[lang]}",
    "slug_{lang}": "seo-friendly-slug-in-{lang}"
  }}
]"""

    try:
        result = gpt([{"role": "user", "content": prompt}], temperature=0.4, max_tokens=4000)
        if "```json" in result:
            result = result.split("```json")[1].split("```")[0].strip()
        elif "```" in result:
            result = result.split("```")[1].split("```")[0].strip()
        translations = json.loads(result)
        for t in translations:
            trans_index[t["slug"]] = t
        save(trans_index_file, trans_index)
    except Exception as e:
        print(f"    ERROR: {e}")

print("\n✅ All content generation complete!")
print(f"Output directory: {OUT_DIR}")
