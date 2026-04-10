"""
Parallel article generator + translator — Ngor Surfcamp Teranga
Phase 1  : Regenerate 14 EN articles via GPT-5.4 (skip already-validated one)
Phase 1b : Generate missing B&W hero images via DALL-E 3
Phase 2  : Translate all 15 articles × 8 languages (120 parallel calls)
Phase 3  : Rebuild blog + full site

Usage:
    python3 scripts/gen_all_articles.py              # full pipeline
    python3 scripts/gen_all_articles.py --phase 1    # EN content only
    python3 scripts/gen_all_articles.py --phase 1b   # images only
    python3 scripts/gen_all_articles.py --phase 2    # translations only
    python3 scripts/gen_all_articles.py --phase 3    # rebuild only
"""

import os, json, sys, re, base64, time, threading, argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT       = Path(__file__).parent.parent
CONTENT_V2 = ROOT / "content" / "articles_v2"
IMG_DIR    = ROOT / "cloudflare-demo" / "assets" / "images" / "blog"

MAX_WORKERS = 30
LANGUAGES   = ["fr", "es", "it", "de", "nl", "ar", "pt", "da"]
LANG_NAMES  = {
    "fr": "French", "es": "Spanish", "it": "Italian", "de": "German",
    "nl": "Dutch",  "ar": "Arabic",  "pt": "Portuguese", "da": "Danish",
}

# Already validated — skip EN regeneration
SKIP_EN = {"senegal-surf-season-by-month"}

# ── Env & client ──────────────────────────────────────────────────────────────
def _load_env():
    p = ROOT / ".env"
    if p.exists():
        for line in p.read_text().splitlines():
            if line.startswith("#") or "=" not in line: continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

_load_env()

try:
    from openai import OpenAI
except ImportError:
    print("ERROR: pip install openai"); sys.exit(1)

API_KEY = os.environ.get("OPENAI_API_KEY", "")
if not API_KEY: print("ERROR: OPENAI_API_KEY not set"); sys.exit(1)

MODEL  = "gpt-5.4-2026-03-05"
client = OpenAI(api_key=API_KEY)

# Thread-safe print
_lock = threading.Lock()
def tp(*args):
    with _lock: print(*args, flush=True)

# ── Article definitions ───────────────────────────────────────────────────────
ARTICLES = [
    {
        "slug": "senegal-surf-season-by-month",
        "title": "Senegal Surf Season by Month: When to Go for Perfect Waves",
        "category": "Surf Conditions & Spots",
        "focus_keyword": "senegal surf season",
        "angle": "month-by-month surf season breakdown for Ngor Island — swell windows, wind patterns, water temperature, crowd levels, and what to expect each month from November to April",
    },
    {
        "slug": "ngor-island-waves-explained",
        "title": "Ngor Island Waves Explained: Right, Left and Beyond",
        "category": "Surf Conditions & Spots",
        "focus_keyword": "ngor island waves",
        "angle": "technical guide to Ngor Island's surf breaks — Ngor Right mechanics, Ngor Left character, lesser-known spots, tide sensitivity, optimal conditions, and how to read the reef",
    },
    {
        "slug": "surfing-ngor-right-guide",
        "title": "Surfing Ngor Right: A Complete Spot Guide for Visitors",
        "category": "Surf Conditions & Spots",
        "focus_keyword": "surfing ngor right",
        "angle": "definitive spot guide to Ngor Right — paddle-out routes, take-off zone, wave sections, swell and wind requirements, who it suits, and how to get the most from the lineup",
    },
    {
        "slug": "surfing-ngor-left-guide",
        "title": "Surfing Ngor Left: The Quieter Wave Worth Knowing",
        "category": "Surf Conditions & Spots",
        "focus_keyword": "surfing ngor left",
        "angle": "guide to Ngor Left — its character, when it breaks, who it suits (intermediates, longboarders), how it differs from Ngor Right, and how to position correctly",
    },
    {
        "slug": "dakar-surf-spots-for-every-level",
        "title": "Dakar Surf Spots for Every Level: A Local's Guide",
        "category": "Surf Conditions & Spots",
        "focus_keyword": "dakar surf spots",
        "angle": "practical guide to all surf spots accessible from Ngor Island — Ngor Right, Ngor Left, Ouakam, Yoff, Virage, Almadies — with level requirements, conditions, and logistics",
    },
    {
        "slug": "endless-summer-senegal-ngor",
        "title": "The Endless Summer at Ngor: How Senegal Became Surf History",
        "category": "Island Life & Surf Camp",
        "focus_keyword": "endless summer senegal ngor",
        "angle": "story of Bruce Brown's 1966 film and how Ngor Island became iconic in surfing — the history, what changed, how the spirit of the Endless Summer still lives in the lineup today",
    },
    {
        "slug": "surf-camp-senegal-what-to-expect",
        "title": "Surf Camp Senegal: What to Expect on a Premium Ngor Island Stay",
        "category": "Island Life & Surf Camp",
        "focus_keyword": "surf camp senegal what to expect",
        "angle": "honest inside account of a week at Ngor Surfcamp Teranga — daily rhythm, meals, guiding, coaching, island life, typical guest profile, and what makes it different from a hotel",
    },
    {
        "slug": "surf-trip-to-senegal-what-to-pack",
        "title": "Surf Trip to Senegal: The Complete Packing List for Ngor",
        "category": "Island Life & Surf Camp",
        "focus_keyword": "surf trip senegal what to pack",
        "angle": "comprehensive packing guide for a surf trip to Ngor Island — boards, wetsuits, reef booties, wax, travel documents, health essentials, and what you can leave at home",
    },
    {
        "slug": "where-to-stay-for-surfing-in-dakar",
        "title": "Where to Stay for Surfing in Dakar: Ngor Island vs Mainland",
        "category": "Island Life & Surf Camp",
        "focus_keyword": "where to stay surfing dakar",
        "angle": "genuine comparison between staying on Ngor Island vs mainland Dakar for surfers — proximity to waves, logistics, atmosphere, cost, who should choose which option",
    },
    {
        "slug": "why-senegal-is-an-underrated-surf-destination",
        "title": "Why Senegal Is an Underrated Surf Destination for Europeans",
        "category": "Island Life & Surf Camp",
        "focus_keyword": "senegal surf destination",
        "angle": "case for Senegal as Europe's closest warm-water surf destination — geography, flight times from Paris/Madrid/Lisbon, uncrowded lineups, culture, cost comparison vs Canaries/Morocco",
    },
    {
        "slug": "senegal-surf-camp-for-beginners",
        "title": "Senegal Surf Camp for Beginners: Is Ngor Island Right for You?",
        "category": "Coaching & Progression",
        "focus_keyword": "senegal surf camp beginners",
        "angle": "honest guide for beginner surfers considering Ngor — which waves are suitable, what coaching looks like, how fast you can expect to progress, typical first-week experience",
    },
    {
        "slug": "surf-coaching-structured-ngor-surfcamp",
        "title": "How Surf Coaching Is Structured at Ngor Surfcamp Teranga",
        "category": "Coaching & Progression",
        "focus_keyword": "surf coaching ngor surfcamp",
        "angle": "deep dive into the coaching methodology — theory sessions, water time, feedback loop, skill progression from pop-up to turns to barrels, how coaches adapt to each level",
    },
    {
        "slug": "video-analysis-surf-camp-senegal",
        "title": "Video Analysis at Surf Camp: How It Accelerates Your Progress",
        "category": "Coaching & Progression",
        "focus_keyword": "video analysis surf camp senegal",
        "angle": "how video analysis works at Ngor Surfcamp — filming sessions, review process, what coaches look for, before/after comparisons, which faults get corrected fastest and why",
    },
    {
        "slug": "why-choose-surf-camp-senegal",
        "title": "Why Choose a Surf Camp in Senegal Over Other Destinations",
        "category": "Coaching & Progression",
        "focus_keyword": "why choose surf camp senegal",
        "angle": "reasoned argument for choosing Senegal over Indonesia, Morocco, or the Canaries for a surf camp — waves, weather, culture, cost, crowds, and the Ngor factor",
    },
    {
        "slug": "licensed-surf-camp-senegal",
        "title": "Licensed Surf Camp in Senegal: Why Accreditation Matters",
        "category": "Coaching & Progression",
        "focus_keyword": "licensed surf camp senegal",
        "angle": "why FSS (Fédération Sénégalaise de Surf) accreditation matters — coach qualifications, safety standards, what to ask before booking, how to spot unlicensed operators",
    },
]

# ── System prompt (EN generation) ─────────────────────────────────────────────
SYSTEM_PROMPT = """You are a senior surf travel journalist and SEO specialist writing for Ngor Surfcamp Teranga — a premium licensed surf camp on Ngor Island, Dakar, Senegal.

BRAND VOICE: Authoritative, warm, honest, immersive. Never generic. Write like someone who has surfed there many times. Concrete details over vague superlatives.

SURF CAMP FACTS (always accurate):
- Name: Ngor Surfcamp Teranga
- Location: Ngor Island, 400m off Dakar coast, Senegal
- Waves: Ngor Right (reef break, fast, hollow), Ngor Left (mellower, longer)
- Access: 5-min pirogue from Ngor beach on mainland
- Camp includes: rooms (private/shared/dorm), breakfast+dinner, surf guiding, theory sessions, pool
- Extras: airport transfer, surf coaching, video analysis, board rental (€15/day), wetsuit rental (€5/day), lunch
- FSS licensed (Fédération Sénégalaise de Surf)
- Season: November–April (prime); May–October flat/off-season
- Suited for all levels but especially intermediates to advanced
- Website: surf-camp-senegal.vercel.app
- Instagram: @ngorsurfcampteranga

OUTPUT FORMAT — Return a strict JSON object with these exact keys:
{
  "title": "string (max 65 chars, compelling, keyword-rich)",
  "meta_description": "string (max 160 chars, includes focus keyword, drives clicks)",
  "slug": "string (URL-safe, matches provided slug)",
  "category": "string",
  "focus_keyword": "string",
  "hero_image_prompt": "string (DALL-E prompt for black-and-white photography-style image — NO TEXT — contextual to article topic)",
  "reading_time": integer (in minutes),
  "word_count_estimate": integer,
  "content_markdown": "string (see CONTENT RULES below)",
  "faq": [{"q": "string", "a": "string"}, ...] (exactly 5 FAQ pairs)
}

CONTENT RULES for content_markdown:
1. DO NOT include an H1 (it is rendered separately in the hero)
2. Open with a strong lead paragraph (2-3 sentences, hooks the reader)
3. Use ## for section headings (they become H2 in the page)
4. Target 2200–2800 words
5. Include EXACTLY 5 visual blocks spread evenly through the article
6. VISUAL BLOCK SYNTAX — use exactly these formats (parser-sensitive):

   For a Pro Tip:
   TIP:** [your tip text on a single line — no line break after TIP:**]

   For a Did You Know fact:
   FACT:** [your fact on a single line]

   For a coach quote:
   EXPERT:** [quote attributed to "The Ngor coaching team"]

   For key takeaways:
   SUMMARY:**
   - Point one
   - Point two
   - Point three

   For an action checklist:
   CHECKLIST:**
   - Action one
   - Action two
   - Action three

7. Use pull quotes with > for memorable one-liners
8. Internal links: [anchor text->target] where target is one of: surfing, island, surf-house, booking, gallery, faq, blog
9. End with a call-to-action paragraph linking to booking
10. DO NOT include the FAQ section in content_markdown (it is rendered separately as an accordion)
11. Do not add horizontal rules (---)"""


def _make_user_prompt(art):
    return f"""Write a complete article for Ngor Surfcamp Teranga's blog.

Slug: {art['slug']}
Title target: {art['title']}
Category: {art['category']}
Focus keyword: {art['focus_keyword']}
Angle: {art['angle']}

Requirements:
- 2200–2800 words in content_markdown
- 5 visual blocks (mix of TIP, FACT, EXPERT, SUMMARY, CHECKLIST)
- 5 FAQ pairs (search-intent questions readers actually Google)
- Hero image prompt: black-and-white photo style, NO text visible in image, atmospheric, contextual to the article topic. Reference real locations (Ngor Island, Dakar, Atlantic coast, volcanic reef, surfers, etc.)
- Meta description: exactly 150-160 chars, includes "{art['focus_keyword']}"
- Title: max 65 chars

Return ONLY the JSON object. No markdown fences, no explanation."""


# ── Retry wrapper ──────────────────────────────────────────────────────────────
def _with_retry(fn, retries=3, wait=10):
    for attempt in range(retries):
        try:
            return fn()
        except Exception as e:
            if attempt < retries - 1:
                tp(f"  ⚠ Retry {attempt+1}/{retries} after error: {e}")
                time.sleep(wait * (attempt + 1))
            else:
                raise


# ── Phase 1: Generate EN article ──────────────────────────────────────────────
def generate_en_article(art_def):
    slug = art_def["slug"]
    out_path = CONTENT_V2 / "en" / f"{slug}.json"

    # Check if already has new-format content (has faq key)
    if out_path.exists():
        try:
            existing = json.loads(out_path.read_text(encoding="utf-8"))
            if existing.get("faq") and len(existing["faq"]) >= 5:
                tp(f"  ⏭  {slug} — already has faq, skipping EN regen")
                return existing
        except Exception:
            pass

    tp(f"  🔄 [{slug}] Calling GPT-5.4...")

    def _call():
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": _make_user_prompt(art_def)},
            ],
            max_completion_tokens=5000,
            response_format={"type": "json_object"},
        )
        raw = resp.choices[0].message.content.strip()
        if not raw:
            raise ValueError("Empty API response")
        return json.loads(raw)

    data = _with_retry(_call)
    data["slug"]          = slug
    data["category"]      = art_def["category"]
    data["focus_keyword"] = art_def["focus_keyword"]
    data["lang"]          = "en"
    data["type"]          = "article"
    data["personas"]      = ["surfer_intermediate", "traveler_europe"]

    (CONTENT_V2 / "en").mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tp(f"  ✅ [{slug}] EN saved ({data.get('word_count_estimate',0)} words, {len(data.get('faq',[]))} FAQ)")
    return data


# ── Phase 1b: Generate hero image ─────────────────────────────────────────────
def generate_hero_image(slug, hero_prompt):
    img_path = IMG_DIR / f"{slug}_hero.webp"
    if img_path.exists():
        tp(f"  ⏭  [{slug}] hero image already exists")
        return f"/assets/images/blog/{slug}_hero.webp"

    tp(f"  🎨 [{slug}] Generating B&W hero image...")
    full_prompt = (
        f"{hero_prompt}. "
        "Style: PURE TRUE BLACK AND WHITE photography — absolutely no color, no sepia, no warm tones, no yellow tint, no brown tint. "
        "Pure monochrome grayscale only. High contrast, deep blacks, bright whites, silver halide film grain texture. "
        "NO text, NO watermark, NO logo. Cinematic composition, 16:9 crop."
    )

    def _call():
        return client.images.generate(
            model="dall-e-3",
            prompt=full_prompt,
            size="1792x1024",
            quality="hd",
            response_format="b64_json",
            n=1,
        )

    resp     = _with_retry(_call)
    img_b64  = resp.data[0].b64_json
    img_bytes = base64.b64decode(img_b64)

    IMG_DIR.mkdir(parents=True, exist_ok=True)
    try:
        from PIL import Image
        import io
        # Force true grayscale to strip any color/sepia/warm tint from DALL-E output
        img = Image.open(io.BytesIO(img_bytes)).convert("L").convert("RGB")
        img.save(str(img_path), "WEBP", quality=88)
        tp(f"  ✅ [{slug}] hero saved as true B&W WebP")
    except Exception:
        png_path = IMG_DIR / f"{slug}_hero.png"
        png_path.write_bytes(img_bytes)
        tp(f"  ✅ [{slug}] hero saved as PNG (PIL not available)")
        return f"/assets/images/blog/{slug}_hero.png"

    return f"/assets/images/blog/{slug}_hero.webp"


# ── Phase 2: Translate one article ────────────────────────────────────────────
TRANSLATE_SYSTEM = """You are a professional surf travel translator.
Translate the provided English article JSON into the target language.

Rules:
- Translate: title, meta_description, category, focus_keyword, content_markdown, and all faq q/a pairs
- Preserve ALL markdown formatting exactly: ##, **, >, TIP:**, FACT:**, CHECKLIST:**, SUMMARY:**, EXPERT:**
- For internal links [anchor->target] — translate the anchor text but keep ->target unchanged
- Keep slug and original_en_slug values unchanged (English slug)
- Set "lang" to the target language code
- Preserve hero_image_url unchanged
- For Arabic: ensure right-to-left phrasing is natural; do NOT add dir attributes
- Return ONLY the complete JSON object, no markdown fences"""


def translate_article(en_data, lang):
    slug      = en_data["slug"]
    lang_name = LANG_NAMES[lang]
    out_path  = CONTENT_V2 / lang / f"{slug}.json"

    # Check if already translated with new format
    if out_path.exists():
        try:
            existing = json.loads(out_path.read_text(encoding="utf-8"))
            if existing.get("faq") and len(existing["faq"]) >= 5:
                tp(f"  ⏭  [{lang}] {slug} — already translated, skipping")
                return existing
        except Exception:
            pass

    tp(f"  🌍 [{lang}] Translating {slug}...")

    # Build a minimal payload to reduce tokens
    payload = {
        "title":            en_data.get("title", ""),
        "meta_description": en_data.get("meta_description", ""),
        "slug":             slug,
        "original_en_slug": slug,
        "category":         en_data.get("category", ""),
        "focus_keyword":    en_data.get("focus_keyword", ""),
        "lang":             lang,
        "reading_time":     en_data.get("reading_time", 8),
        "word_count_estimate": en_data.get("word_count_estimate", 0),
        "hero_image_url":   en_data.get("hero_image_url", f"/assets/images/blog/{slug}_hero.webp"),
        "content_markdown": en_data.get("content_markdown", ""),
        "faq":              en_data.get("faq", []),
    }

    user_msg = f"Target language: {lang_name} (code: {lang})\n\nTranslate this JSON:\n{json.dumps(payload, ensure_ascii=False)}"

    def _call():
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": TRANSLATE_SYSTEM},
                {"role": "user",   "content": user_msg},
            ],
            response_format={"type": "json_object"},
        )
        raw = resp.choices[0].message.content.strip()
        if not raw:
            raise ValueError("Empty API response")
        return json.loads(raw)

    data = _with_retry(_call, retries=4, wait=20)

    # Ensure required fields
    data["slug"]             = slug
    data["original_en_slug"] = slug
    data["lang"]             = lang
    data["type"]             = "article"
    data["hero_image_url"]   = payload["hero_image_url"]

    (CONTENT_V2 / lang).mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tp(f"  ✅ [{lang}] {slug} translated")
    return data


# ── Progress tracker ───────────────────────────────────────────────────────────
class Progress:
    def __init__(self, total, label):
        self.total = total
        self.done  = 0
        self.label = label
        self._lock = threading.Lock()

    def tick(self):
        with self._lock:
            self.done += 1
            pct = self.done * 100 // self.total
            bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
            print(f"\r  {self.label}: [{bar}] {self.done}/{self.total} ({pct}%)", end="", flush=True)
            if self.done == self.total:
                print()


# ── Phase runners ──────────────────────────────────────────────────────────────
def run_phase1():
    """Generate EN content for all articles lacking the faq key."""
    to_generate = [a for a in ARTICLES if a["slug"] not in SKIP_EN]
    print(f"\n{'='*60}")
    print(f"Phase 1 — EN content generation ({len(to_generate)} articles, up to {MAX_WORKERS} workers)")
    print(f"{'='*60}")

    prog    = Progress(len(to_generate), "EN articles")
    results = {}

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(generate_en_article, art): art["slug"] for art in to_generate}
        for fut in as_completed(futures):
            slug = futures[fut]
            try:
                results[slug] = fut.result()
            except Exception as e:
                tp(f"  ❌ [{slug}] EN generation failed: {e}")
                results[slug] = None
            prog.tick()

    ok  = sum(1 for v in results.values() if v)
    err = len(results) - ok
    print(f"\n  Phase 1 done: {ok} succeeded, {err} failed")
    return results


def run_phase1b():
    """Generate missing hero images for all articles."""
    print(f"\n{'='*60}")
    print(f"Phase 1b — Hero image generation (DALL-E 3, up to {MAX_WORKERS} workers)")
    print(f"{'='*60}")

    # Collect slugs + prompts (load from saved EN JSON)
    jobs = []
    for art in ARTICLES:
        slug     = art["slug"]
        img_path = IMG_DIR / f"{slug}_hero.webp"
        if img_path.exists():
            continue
        # Load prompt from saved JSON
        json_path = CONTENT_V2 / "en" / f"{slug}.json"
        if json_path.exists():
            try:
                d      = json.loads(json_path.read_text(encoding="utf-8"))
                prompt = d.get("hero_image_prompt", f"Atmospheric surf photography, {slug.replace('-',' ')}, Ngor Island Senegal")
            except Exception:
                prompt = f"Atmospheric surf photography, {slug.replace('-',' ')}, Ngor Island Senegal"
        else:
            prompt = f"Atmospheric surf photography, {slug.replace('-',' ')}, Ngor Island Senegal"
        jobs.append((slug, prompt))

    if not jobs:
        print("  All hero images already exist.")
        return

    print(f"  {len(jobs)} images to generate...")
    prog = Progress(len(jobs), "Hero images")

    # DALL-E rate limit: 5 parallel max to avoid 429s
    dall_e_workers = min(5, len(jobs))
    with ThreadPoolExecutor(max_workers=dall_e_workers) as ex:
        futures = {ex.submit(generate_hero_image, slug, prompt): slug for slug, prompt in jobs}
        for fut in as_completed(futures):
            slug = futures[fut]
            try:
                fut.result()
            except Exception as e:
                tp(f"  ❌ [{slug}] image failed: {e}")
            prog.tick()

    print(f"  Phase 1b done")


def run_phase2():
    """Translate all 15 EN articles into 8 languages."""
    print(f"\n{'='*60}")
    total = len(ARTICLES) * len(LANGUAGES)
    print(f"Phase 2 — Translations ({len(ARTICLES)} articles × {len(LANGUAGES)} languages = {total} calls, {MAX_WORKERS} workers)")
    print(f"{'='*60}")

    # Load all EN articles
    en_articles = {}
    for art in ARTICLES:
        slug = art["slug"]
        p    = CONTENT_V2 / "en" / f"{slug}.json"
        if p.exists():
            try:
                en_articles[slug] = json.loads(p.read_text(encoding="utf-8"))
                # Ensure hero_image_url is set
                if not en_articles[slug].get("hero_image_url"):
                    en_articles[slug]["hero_image_url"] = f"/assets/images/blog/{slug}_hero.webp"
            except Exception as e:
                tp(f"  ⚠ Could not load EN {slug}: {e}")
        else:
            tp(f"  ⚠ Missing EN JSON for {slug} — skipping translations")

    # Build job list
    jobs = [
        (en_articles[art["slug"]], lang)
        for art in ARTICLES
        for lang in LANGUAGES
        if art["slug"] in en_articles
    ]

    prog = Progress(len(jobs), "Translations")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {
            ex.submit(translate_article, en_data, lang): (en_data["slug"], lang)
            for en_data, lang in jobs
        }
        for fut in as_completed(futures):
            slug, lang = futures[fut]
            try:
                fut.result()
            except Exception as e:
                tp(f"  ❌ [{lang}] {slug} translation failed: {e}")
            prog.tick()

    print(f"\n  Phase 2 done")


def run_phase3():
    """Rebuild blog + full site."""
    import subprocess
    print(f"\n{'='*60}")
    print("Phase 3 — Rebuilding blog + full site")
    print(f"{'='*60}")

    scripts_dir = ROOT / "scripts"
    build_blog  = scripts_dir / "build_blog.py"
    build_main  = ROOT / "build.py"

    # Build blog
    print("  Running scripts/build_blog.py...")
    r = subprocess.run([sys.executable, str(build_blog)], capture_output=True, text=True, cwd=ROOT)
    if r.returncode != 0:
        print(f"  ❌ build_blog.py failed:\n{r.stderr[-2000:]}")
    else:
        lines = [l for l in r.stdout.splitlines() if "article" in l.lower() or "blog" in l.lower() or "✅" in l]
        for l in lines[-10:]: print(f"  {l}")
        print("  ✅ build_blog.py done")

    # Build full site
    print("  Running build.py...")
    r = subprocess.run([sys.executable, str(build_main)], capture_output=True, text=True, cwd=ROOT)
    if r.returncode != 0:
        print(f"  ❌ build.py failed:\n{r.stderr[-2000:]}")
    else:
        lines = [l for l in r.stdout.splitlines() if "✅" in l or "cache-bust" in l or "hreflang" in l]
        for l in lines[-8:]: print(f"  {l}")
        print("  ✅ build.py done")

    # Sync to .vercel/output
    print("  Syncing to .vercel/output/static/...")
    r = subprocess.run(
        ["rsync", "-a", "--delete", "cloudflare-demo/", ".vercel/output/static/", "--exclude=.git"],
        capture_output=True, text=True, cwd=ROOT
    )
    if r.returncode == 0:
        print("  ✅ rsync done")
    else:
        print(f"  ⚠ rsync: {r.stderr[:500]}")

    # Deploy
    print("  Deploying to Vercel (production)...")
    r = subprocess.run(["vercel", "deploy", "--prebuilt", "--prod"], capture_output=True, text=True, cwd=ROOT)
    url_line = next((l for l in r.stdout.splitlines() if "surf-camp-senegal" in l and "vercel.app" in l), "")
    if r.returncode == 0 or url_line:
        print(f"  ✅ Deployed: {url_line}")
    else:
        print(f"  ⚠ Deploy output: {r.stdout[-500:]}")

    print("\n🏄 All done! Check the live site.")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Parallel article generator for Ngor Surfcamp")
    parser.add_argument("--phase", choices=["1", "1b", "2", "3", "all"], default="all",
                        help="Which phase to run (default: all)")
    args = parser.parse_args()

    phase = args.phase
    t0    = time.time()

    print(f"\n🏄 Ngor Surfcamp — Article Pipeline ({MAX_WORKERS} workers)")
    print(f"   Articles: {len(ARTICLES)} | Languages: {len(LANGUAGES)}")

    if phase in ("1", "all"):
        run_phase1()
    if phase in ("1b", "all"):
        run_phase1b()
    if phase in ("2", "all"):
        run_phase2()
    if phase in ("3", "all"):
        run_phase3()

    elapsed = time.time() - t0
    print(f"\n⏱  Total time: {elapsed/60:.1f} min")


if __name__ == "__main__":
    main()
