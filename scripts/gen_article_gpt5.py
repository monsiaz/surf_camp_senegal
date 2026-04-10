"""
Article generator using GPT-5.4 — Ngor Surfcamp Teranga
Generates one article at a time with visual blocks, FAQ, hero image.
Usage: python3 scripts/gen_article_gpt5.py <slug>
"""
import os, json, sys, re, base64, datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
CONTENT_DIR = ROOT / "content" / "articles_v2" / "en"
IMG_DIR = ROOT / "cloudflare-demo" / "assets" / "images" / "blog"

try:
    from openai import OpenAI
except ImportError:
    print("ERROR: pip install openai first")
    sys.exit(1)

# ── Load env ─────────────────────────────────────────────────────────────────
def load_env():
    env_path = ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

load_env()
API_KEY = os.environ.get("OPENAI_API_KEY", "")
MODEL   = "gpt-5.4-2026-03-05"

if not API_KEY:
    print("ERROR: OPENAI_API_KEY not set"); sys.exit(1)

client = OpenAI(api_key=API_KEY)

# ── Article definitions (15 articles) ────────────────────────────────────────
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

# ── System prompt ─────────────────────────────────────────────────────────────
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

# ── User prompt for one article ───────────────────────────────────────────────
def make_user_prompt(art):
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

# ── Generate one article ──────────────────────────────────────────────────────
def generate_article(art_def):
    print(f"  Calling GPT-5.4 for: {art_def['slug']}...")
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": make_user_prompt(art_def)},
        ],
        max_completion_tokens=5000,
        response_format={"type": "json_object"},
    )
    raw = resp.choices[0].message.content.strip()
    data = json.loads(raw)
    # Merge with defaults
    data["slug"]             = art_def["slug"]
    data["category"]         = art_def["category"]
    data["focus_keyword"]    = art_def["focus_keyword"]
    data["lang"]             = "en"
    data["type"]             = "article"
    data["personas"]         = ["surfer_intermediate", "traveler_europe"]
    data["secondary_keywords"] = []
    return data

# ── Generate hero image (B&W) ─────────────────────────────────────────────────
def generate_hero_image(art_def, hero_prompt):
    slug = art_def["slug"]
    img_path = IMG_DIR / f"{slug}_hero.webp"
    if img_path.exists():
        print(f"  Hero image already exists, skipping: {img_path.name}")
        return f"/assets/images/blog/{slug}_hero.webp"

    print(f"  Generating hero image for: {slug}...")
    full_prompt = (
        f"{hero_prompt}. "
        "Style: dramatic black-and-white photography, high contrast, film grain texture. "
        "NO text, NO watermark, NO logo. Cinematic composition, 16:9 crop."
    )
    resp = client.images.generate(
        model="dall-e-3",
        prompt=full_prompt,
        size="1792x1024",
        quality="hd",
        response_format="b64_json",
        n=1,
    )
    img_b64 = resp.data[0].b64_json
    img_bytes = base64.b64decode(img_b64)

    # Save as PNG first, we store as webp filename (build handles conversion)
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    png_path = IMG_DIR / f"{slug}_hero.png"
    png_path.write_bytes(img_bytes)

    # Convert to WebP using PIL
    try:
        from PIL import Image
        import io
        img = Image.open(io.BytesIO(img_bytes))
        img.save(str(img_path), "WEBP", quality=88)
        png_path.unlink()
        print(f"  Hero saved as WebP: {img_path.name}")
    except Exception:
        # Fallback: keep as PNG
        png_path.rename(img_path.with_suffix(".png"))
        return f"/assets/images/blog/{slug}_hero.png"

    return f"/assets/images/blog/{slug}_hero.webp"

# ── Lightweight preview markdown renderer (no build_blog.py import side-effects) ──
def _preview_md2html(md):
    if not md: return ""
    BLOCK_MAP = {
        "TIP": ("vb-tip", "Pro Tip"),
        "FACT": ("vb-fact", "Did You Know?"),
        "NOTE": ("vb-note", "Note"),
        "EXPERT": ("vb-expert", "From the Coaches"),
        "SUMMARY": ("vb-summary", "Key Takeaways"),
        "CHECKLIST": ("vb-checklist", "Action Checklist"),
    }
    def inline(t):
        t = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', t)
        t = re.sub(r'(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)', r'<em>\1</em>', t)
        return re.sub(r'\*+', '', t)

    lines = md.split("\n")
    out = []
    in_ul = in_ol = False
    def close_lists():
        nonlocal in_ul, in_ol
        if in_ul: out.append("</ul>"); in_ul = False
        if in_ol: out.append("</ol>"); in_ol = False

    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if not s: close_lists(); i += 1; continue
        if re.match(r'^[-*_]{3,}$', s): close_lists(); i += 1; continue
        if s.startswith("#### "): close_lists(); out.append(f'<h3>{inline(s[5:])}</h3>')
        elif s.startswith("### "): close_lists(); out.append(f'<h3>{inline(s[4:])}</h3>')
        elif s.startswith("## "): close_lists(); out.append(f'<h2>{inline(s[3:])}</h2>')
        elif s.startswith("# "): close_lists(); out.append(f'<h2>{inline(s[2:])}</h2>')
        elif s.startswith("> "):
            close_lists()
            out.append(f'<div class="pull-quote"><blockquote class="pq-txt">{inline(s[2:])}</blockquote></div>')
        elif any(s.upper().startswith(kw + ":") for kw in BLOCK_MAP):
            close_lists()
            kw = next(k for k in BLOCK_MAP if s.upper().startswith(k + ":"))
            cls, lbl = BLOCK_MAP[kw]
            first = re.sub(r'^\*\*[^:]+:\*?\*?\s*', '', s, flags=re.IGNORECASE).strip()
            items = [first] if first else []
            i += 1
            while i < len(lines):
                ls = lines[i].strip()
                if not ls or ls.startswith("#") or any(ls.upper().startswith(k + ":") for k in BLOCK_MAP): break
                items.append(ls.lstrip("-•* "))
                i += 1
            if cls == "vb-expert":
                body = f'<blockquote>{inline(" ".join(items))}</blockquote>'
            elif len(items) > 1:
                body = "<ul>" + "".join(f"<li>{inline(it)}</li>" for it in items if it) + "</ul>"
            else:
                body = f"<p>{inline(' '.join(items))}</p>"
            out.append(f'<div class="{cls}"><div class="vb-header"><span class="vb-label">{lbl}</span></div><div class="vb-content">{body}</div></div>')
            continue
        elif re.match(r'^[-*]\s', s):
            if not in_ul: out.append('<ul class="prose-ul">'); in_ul = True
            if in_ol: out.append("</ol>"); in_ol = False
            out.append(f'<li>{inline(s[2:])}</li>')
        elif re.match(r'^\d+\.\s', s):
            if not in_ol: out.append('<ol class="prose-ol">'); in_ol = True
            if in_ul: out.append("</ul>"); in_ul = False
            out.append(f'<li>{inline(re.sub(r"^\d+\.\s","",s))}</li>')
        else:
            close_lists(); out.append(f'<p>{inline(s)}</p>')
        i += 1
    close_lists()
    return "\n".join(out)


def _preview_faq(pairs):
    if not pairs: return ""
    items = ""
    for pair in pairs:
        items += f'<div class="faq-item"><button class="faq-q">{pair["q"]}</button><div class="faq-a"><p>{pair["a"]}</p></div></div>\n'
    return items


# ── Build standalone HTML preview ─────────────────────────────────────────────
def build_preview_html(data, hero_url):
    """Build a self-contained HTML preview using the project CSS."""
    md = data["content_markdown"]
    md = re.sub(r'^\s*#\s+[^\n]+\n?', '', md, count=1).strip()

    content_html = _preview_md2html(md)
    faq_html     = _preview_faq(data.get("faq", []))

    title      = data["title"]
    meta_desc  = data["meta_description"]
    read_time  = data.get("reading_time", 8)
    category   = data.get("category", "")
    word_count = data.get("word_count_estimate", 0)

    css_path = ROOT / "cloudflare-demo" / "assets" / "css" / "ngor-surfcamp.css"
    css = css_path.read_text(errors="ignore") if css_path.exists() else ""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{meta_desc}">
<style>
{css}
/* Preview extras */
body{{background:#f8f9fa;font-family:system-ui,sans-serif}}
.preview-wrap{{max-width:820px;margin:0 auto;background:#fff;box-shadow:0 2px 40px rgba(0,0,0,.10)}}
.preview-meta-bar{{background:#1a2640;color:#fff;padding:10px 24px;font-size:12px;display:flex;gap:16px;align-items:center}}
.preview-meta-bar strong{{color:var(--sand,#c9a96e)}}
</style>
</head>
<body>
<div class="preview-meta-bar">
  <strong>PREVIEW</strong>
  <span>Title ({len(data['title'])} chars): {data['title']}</span>
  <span>·</span>
  <span>Meta ({len(data['meta_description'])} chars)</span>
  <span>·</span>
  <span>{word_count} words · {read_time} min read</span>
</div>
<div class="preview-wrap">

<!-- HERO -->
<header class="article-hero" style="position:relative;min-height:420px;background:#1a2640;display:flex;align-items:flex-end;overflow:hidden;">
  <img src="{hero_url}" alt="{title}" loading="eager"
       style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:.6">
  <div style="position:relative;z-index:2;padding:40px 48px;width:100%">
    <span style="display:inline-block;background:var(--fire,#ff5a1f);color:#fff;font-size:11px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;padding:4px 12px;border-radius:4px;margin-bottom:14px">{category}</span>
    <h1 style="font-size:clamp(26px,4.5vw,48px);font-weight:900;color:#fff;line-height:1.1;margin:0 0 16px;max-width:760px;text-shadow:0 2px 8px rgba(0,0,0,.6)">{data['title']}</h1>
    <p style="color:rgba(255,255,255,.75);font-size:15px;margin:0">{read_time} min read · {word_count:,} words</p>
  </div>
</header>

<!-- ARTICLE BODY -->
<article class="article-body" style="padding:48px 64px;max-width:100%;box-sizing:border-box">
<div class="article-content prose">
{content_html}
</div>

<!-- FAQ ACCORDION -->
<div style="margin-top:56px">
<h2 style="font-size:28px;font-weight:900;color:var(--navy,#1a2640);margin-bottom:24px">Frequently Asked Questions</h2>
{faq_html}
</div>

</article>

<!-- SEO PREVIEW BOX -->
<div style="background:#f1f5f9;border:1px solid #e2e8f0;border-radius:12px;padding:24px 32px;margin:0 64px 48px;font-family:Arial,sans-serif">
  <div style="font-size:11px;text-transform:uppercase;letter-spacing:.1em;color:#64748b;margin-bottom:8px">Google SERP Preview</div>
  <div style="font-size:18px;color:#1a0dab;font-weight:500;margin-bottom:4px">{title}</div>
  <div style="font-size:13px;color:#006621;margin-bottom:6px">surf-camp-senegal.vercel.app › blog › {data['slug']}</div>
  <div style="font-size:14px;color:#545454;line-height:1.5">{meta_desc}</div>
</div>
</div>
<script>
// FAQ accordion
document.querySelectorAll('.faq-q').forEach(btn=>{{
  btn.addEventListener('click',()=>{{
    const item=btn.closest('.faq-item');
    const isOpen=item.classList.contains('open');
    document.querySelectorAll('.faq-item.open').forEach(i=>i.classList.remove('open'));
    if(!isOpen) item.classList.add('open');
  }});
}});
</script>
</body>
</html>"""
    return html

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    slug = sys.argv[1] if len(sys.argv) > 1 else "senegal-surf-season-by-month"
    art_def = next((a for a in ARTICLES if a["slug"] == slug), None)
    if not art_def:
        print(f"Unknown slug: {slug}. Available:")
        for a in ARTICLES: print(f"  {a['slug']}")
        sys.exit(1)

    print(f"\n🏄 Generating: {art_def['slug']}")
    print("=" * 60)

    # 1. Generate article content
    data = generate_article(art_def)

    # 2. Save JSON to content dir
    out_path = CONTENT_DIR / f"{slug}.json"
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  JSON saved: {out_path.name}")

    # 3. Generate hero image
    hero_url = generate_hero_image(art_def, data.get("hero_image_prompt", f"Black and white surf photography, {art_def['slug'].replace('-',' ')}, Ngor Island Senegal"))

    # 4. Build HTML preview
    preview_html = build_preview_html(data, hero_url)
    preview_path = ROOT / f"preview_{slug}.html"
    preview_path.write_text(preview_html, encoding="utf-8")
    print(f"\n✅ Preview ready: {preview_path}")
    print(f"   Open: file://{preview_path}")
    print(f"\n   Title ({len(data['title'])} chars): {data['title']}")
    print(f"   Meta  ({len(data['meta_description'])} chars): {data['meta_description']}")
    print(f"   Words: {data.get('word_count_estimate',0)}")
    print(f"   FAQ pairs: {len(data.get('faq',[]))}")

if __name__ == "__main__":
    main()
