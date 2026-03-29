"""
Scrape ALL pages from live site (READ ONLY), improve EN content,
translate EVERYTHING to FR/ES/IT/DE for the demo.
NEVER writes to the live site.
"""
import json, os, re, time, requests
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser

OPENAI_KEY = "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"
MODEL    = "gpt-5.4-2026-03-05"
OUT_DIR  = "/Users/simonazoulay/SurfCampSenegal/content"
os.makedirs(f"{OUT_DIR}/pages", exist_ok=True)

client = OpenAI(api_key=OPENAI_KEY)

DOMAIN = "https://www.surfcampsenegal.com"
PAGES  = [
    {"slug": "/",                "name": "Homepage"},
    {"slug": "/ngor-surf-house", "name": "Surf House"},
    {"slug": "/ngor-island",     "name": "Island"},
    {"slug": "/surfing",         "name": "Surfing"},
    {"slug": "/book-surf-trip",  "name": "Book Online"},
    {"slug": "/gallery",         "name": "Gallery"},
    {"slug": "/faq",             "name": "FAQ"},
]
LANGS      = ["fr", "es", "it", "de"]
LANG_NAMES = {"fr": "French", "es": "Spanish", "it": "Italian", "de": "German"}
LANG_CODE  = {"fr": "fr-FR",  "es": "es-ES",   "it": "it-IT",   "de": "de-DE"}

# ── HTML text extractor ───────────────────────────────────────────────────────
class TextExtractor(HTMLParser):
    SKIP_TAGS = {"script","style","noscript","nav","footer","button","head","meta","link","img"}
    def __init__(self):
        super().__init__()
        self.texts   = []
        self._skip   = 0
        self._tag_stack = []
    def handle_starttag(self, tag, attrs):
        self._tag_stack.append(tag)
        if tag in self.SKIP_TAGS: self._skip += 1
    def handle_endtag(self, tag):
        if self._tag_stack and self._tag_stack[-1] == tag:
            self._tag_stack.pop()
        if tag in self.SKIP_TAGS and self._skip > 0: self._skip -= 1
    def handle_data(self, data):
        if self._skip == 0:
            t = data.strip()
            if t and len(t) > 2: self.texts.append(t)
    def get_text(self):
        return "\n".join(self.texts)

def scrape_page(url):
    """Scrape a live site page — READ ONLY."""
    try:
        r = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        parser = TextExtractor()
        parser.feed(r.text)
        raw = parser.get_text()
        # Clean: remove duplicates, navigation noise
        lines = []
        seen  = set()
        for line in raw.split("\n"):
            line = line.strip()
            if line and line not in seen and len(line) > 3:
                seen.add(line)
                lines.append(line)
        return "\n".join(lines)
    except Exception as e:
        print(f"  Scrape error {url}: {e}")
        return ""

def gpt(prompt, temperature=0.6, max_tokens=4000):
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
            with open(path) as f: return json.load(f)
        except: return None
    return None

# ════════════════════════════════════════════════════════════════════════════════
# STEP A – Scrape all pages
# ════════════════════════════════════════════════════════════════════════════════
print("="*70)
print("STEP A: Scrape all live pages (read only)")
print("="*70)

scraped = {}
for page in PAGES:
    url      = DOMAIN + page["slug"]
    cache_f  = f"{OUT_DIR}/pages/scraped_{page['name'].lower().replace(' ','_')}.txt"
    if os.path.exists(cache_f):
        with open(cache_f) as f: scraped[page["slug"]] = f.read()
        print(f"  [cache] {page['name']}")
        continue
    print(f"  Scraping: {url}")
    text = scrape_page(url)
    if text:
        with open(cache_f, "w") as f: f.write(text)
        scraped[page["slug"]] = text
        print(f"    → {len(text.split())} words extracted")
    time.sleep(0.5)

print(f"\nScraped {len(scraped)} pages")

# ════════════════════════════════════════════════════════════════════════════════
# STEP B – Improve English content for each page (full rewrite with all info)
# ════════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("STEP B: Improve & structure English content per page")
print("="*70)

def improve_page_en(page):
    slug      = page["slug"]
    name      = page["name"]
    out_file  = f"{OUT_DIR}/pages/en_{name.lower().replace(' ','_')}.json"
    cached    = load(out_file)
    if cached:
        print(f"  [skip EN] {name}")
        return slug, cached

    raw_text = scraped.get(slug, "")
    print(f"  Improving EN: {name}")

    prompt = f"""You are an expert SEO copywriter and web content specialist for surf travel.

You are working on the DEMO version of Ngor Surfcamp Teranga's website.
The demo is an improved copy of the live site at surfcampsenegal.com — same content, better SEO.

LIVE SITE PAGE CONTENT (read from {DOMAIN}{slug}):
\"\"\"
{raw_text[:3000]}
\"\"\"

Task: Rewrite this page's content for the demo, keeping ALL the original information, 
features, amenities and facts — but with:
1. Better SEO structure (improved title, meta, H1, H2s)
2. Richer body copy (more vivid, more useful, same info but better written)
3. All original bullet points / features preserved and enhanced
4. Strong call-to-action

Return valid JSON:
{{
  "slug": "{slug}",
  "lang": "en",
  "page_name": "{name}",
  "title_tag": "optimized title (max 60 chars)",
  "meta_description": "compelling meta (max 155 chars)",
  "h1": "main heading",
  "hero_subtitle": "short hero subtitle (1 sentence)",
  "intro": "improved intro paragraph (2-3 sentences, vivid and SEO-friendly)",
  "sections": [
    {{
      "h2": "section heading",
      "content": "section body text (2-4 sentences)",
      "bullets": ["bullet 1", "bullet 2"]
    }}
  ],
  "cta_heading": "CTA section heading",
  "cta_text": "CTA body (1-2 sentences)",
  "cta_button": "CTA button label",
  "og_title": "Open Graph title",
  "og_description": "OG description",
  "focus_keyword": "primary SEO keyword",
  "schema_type": "LocalBusiness|TouristAttraction|LodgingBusiness",
  "hreflang_urls": {{
    "en": "{DOMAIN}{slug}",
    "fr": "{DOMAIN}/fr-fr{slug}",
    "es": "{DOMAIN}/es-es{slug}",
    "it": "{DOMAIN}/it-it{slug}",
    "de": "{DOMAIN}/de-de{slug}"
  }}
}}"""

    try:
        raw = gpt(prompt, temperature=0.5, max_tokens=3000)
        # extract JSON
        raw = raw.strip()
        if "```json" in raw: raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:   raw = raw.split("```")[1].split("```")[0].strip()
        data = json.loads(raw)
        save(out_file, data)
        print(f"    ✅ {name} EN improved")
        return slug, data
    except Exception as e:
        print(f"    ❌ {name} error: {e}")
        return slug, None

# Parallel EN improvement
print("\n  Processing all pages in parallel...")
en_pages = {}
with ThreadPoolExecutor(max_workers=7) as ex:
    futs = {ex.submit(improve_page_en, p): p for p in PAGES}
    for f in as_completed(futs):
        slug, data = f.result()
        if data: en_pages[slug] = data

print(f"\nEN pages improved: {len(en_pages)}/7")

# ════════════════════════════════════════════════════════════════════════════════
# STEP C – Translate full page content to FR / ES / IT / DE
# ════════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("STEP C: Translate ALL page content (FR/ES/IT/DE) in parallel")
print("="*70)

def translate_page(page, lang):
    slug     = page["slug"]
    name     = page["name"]
    out_file = f"{OUT_DIR}/pages/{lang}_{name.lower().replace(' ','_')}.json"
    if load(out_file):
        print(f"  [skip {lang}] {name}")
        return lang, slug, load(out_file)

    en_data = en_pages.get(slug)
    if not en_data:
        return lang, slug, None

    lang_name = LANG_NAMES[lang]
    lang_code = LANG_CODE[lang]
    print(f"  Translating {lang}: {name}")

    # Build a string of all content to translate
    sections_str = json.dumps(en_data.get("sections", []), ensure_ascii=False)

    prompt = f"""Translate and localize this Wix page content to {lang_name} for Ngor Surfcamp Teranga.
Audience: {lang_name}-speaking surfers. Tone: authentic, adventurous, premium surf travel.
Surf terms can stay in English if natural. All information must be preserved exactly.

English content to translate:
- title_tag: {en_data.get('title_tag','')}
- meta_description: {en_data.get('meta_description','')}
- h1: {en_data.get('h1','')}
- hero_subtitle: {en_data.get('hero_subtitle','')}
- intro: {en_data.get('intro','')}
- sections: {sections_str[:2000]}
- cta_heading: {en_data.get('cta_heading','')}
- cta_text: {en_data.get('cta_text','')}
- cta_button: {en_data.get('cta_button','')}

Return ONLY valid JSON with these exact fields (same structure as input):
{{
  "slug": "{slug}",
  "lang": "{lang}",
  "page_name": "{name}",
  "title_tag": "translated title (max 60 chars)",
  "meta_description": "translated meta (max 155 chars)",
  "h1": "translated H1",
  "hero_subtitle": "translated subtitle",
  "intro": "translated intro",
  "sections": [
    {{ "h2": "...", "content": "...", "bullets": ["..."] }}
  ],
  "cta_heading": "translated CTA heading",
  "cta_text": "translated CTA text",
  "cta_button": "translated button label",
  "og_title": "translated OG title",
  "og_description": "translated OG description",
  "focus_keyword": "best {lang_name} keyword",
  "hreflang": "{lang_code}",
  "canonical_url": "{DOMAIN}/{lang}-{lang[0].upper()+lang[1:]}{slug}"
}}"""

    try:
        raw = gpt(prompt, temperature=0.4, max_tokens=3000)
        raw = raw.strip()
        if "```json" in raw: raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:   raw = raw.split("```")[1].split("```")[0].strip()
        data = json.loads(raw)
        save(out_file, data)
        print(f"    ✅ {lang} {name} done")
        return lang, slug, data
    except Exception as e:
        print(f"    ❌ {lang} {name}: {e}")
        return lang, slug, None

# Build all translation tasks
tasks = [(page, lang) for lang in LANGS for page in PAGES]
print(f"\n  {len(tasks)} translation tasks ({len(PAGES)} pages × {len(LANGS)} langs)")

translated_pages = {}
with ThreadPoolExecutor(max_workers=28) as ex:
    futs = {ex.submit(translate_page, page, lang): (lang, page["slug"]) for page, lang in tasks}
    done = 0
    for f in as_completed(futs):
        lang, slug = futs[f]
        result_lang, result_slug, data = f.result()
        done += 1
        if done % 5 == 0:
            print(f"  Progress: {done}/{len(tasks)}")

# ════════════════════════════════════════════════════════════════════════════════
# STEP D – Build hreflang tags for all pages
# ════════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("STEP D: Generate hreflang HTML for all pages")
print("="*70)

hreflang_output = """<!-- ============================================================
  Ngor Surfcamp Teranga – hreflang tags
  Copy these into the <head> of each corresponding page.
  In Wix: Page Settings > Advanced > Head code
============================================================ -->

"""

for page in PAGES:
    slug = page["slug"]
    hreflang_output += f"<!-- PAGE: {page['name']} ({slug}) -->\n"
    hreflang_output += f'<link rel="alternate" hreflang="x-default" href="{DOMAIN}{slug}" />\n'
    hreflang_output += f'<link rel="alternate" hreflang="en" href="{DOMAIN}{slug}" />\n'
    for lang in LANGS:
        code = LANG_CODE[lang]
        hreflang_output += f'<link rel="alternate" hreflang="{code}" href="{DOMAIN}/{lang}-{lang.upper()}{slug}" />\n'
    hreflang_output += "\n"

with open(f"{OUT_DIR}/pages/hreflang_all_pages.html", "w") as f:
    f.write(hreflang_output)
print(f"  ✅ hreflang tags → content/pages/hreflang_all_pages.html")

# ════════════════════════════════════════════════════════════════════════════════
# STEP E – Build complete page content summary JSON
# ════════════════════════════════════════════════════════════════════════════════
all_pages_data = {"en": {}, "fr": {}, "es": {}, "it": {}, "de": {}}

for page in PAGES:
    slug = page["slug"]
    name = page["name"].lower().replace(" ","_")
    en_f = f"{OUT_DIR}/pages/en_{name}.json"
    if os.path.exists(en_f):
        all_pages_data["en"][slug] = load(en_f)
    for lang in LANGS:
        lang_f = f"{OUT_DIR}/pages/{lang}_{name}.json"
        if os.path.exists(lang_f):
            all_pages_data[lang][slug] = load(lang_f)

save(f"{OUT_DIR}/pages/all_pages_all_langs.json", all_pages_data)

# Print summary
print("\n" + "="*70)
print("PAGE CONTENT SUMMARY")
print("="*70)
for lang in ["en"] + LANGS:
    count = len(all_pages_data[lang])
    print(f"  {lang.upper()}: {count}/7 pages")
    for slug, data in all_pages_data[lang].items():
        if data:
            print(f"    {slug}: \"{data.get('title_tag','?')[:50]}\"")

print(f"\n✅ All page content scraped, improved and translated!")
print(f"Output: {OUT_DIR}/pages/")
