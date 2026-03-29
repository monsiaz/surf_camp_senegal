"""
Regenerate article images + author photos with:
- Consistent illustration DA (NOT stock photo / NOT cliché AI)
- Style: editorial surf magazine illustration, West African aesthetic
- Color palette: deep navy, golden sand, burnt orange, turquoise ocean
- Author personas: realistic documentary portrait style
"""
import json, os, requests
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

OPENAI_KEY  = "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"
IMAGES_DIR  = "/Users/simonazoulay/SurfCampSenegal/cloudflare-demo/assets/images"
AUTHORS_DIR = "/Users/simonazoulay/SurfCampSenegal/content/authors"
DEMO_DIR    = "/Users/simonazoulay/SurfCampSenegal/cloudflare-demo"

client = OpenAI(api_key=OPENAI_KEY)
lock   = threading.Lock()

def log(m):
    with lock: print(m, flush=True)

# ════════════════════════════════════════════════════════════════════════════════
# DA SYSTEM PROMPT — Consistent illustration style
# ════════════════════════════════════════════════════════════════════════════════
DA_SYSTEM = """
Illustration style: editorial surf and travel magazine, graphic and painterly, NOT photorealistic.
Color palette: deep ocean navy (#0a2540), warm golden sand (#f0c060), burnt sunset orange (#ff5a1f), turquoise Atlantic ocean.
Aesthetic: West African coastal culture meets surf lifestyle. Ngor Island, Dakar, Senegal.
Atmosphere: warm, adventurous, authentic — not touristy or corporate.
Composition: cinematic, dynamic, strong focal point.
No text, no logos, no watermarks.
Style references: vintage surf travel poster illustration, editorial magazine spread, bold graphic art.
Light: warm golden hour or dramatic Atlantic light.
"""

# ── Per-article specific illustration briefs ──────────────────────────────────
# These describe the SCENE to illustrate, not a photo to take
ARTICLE_ILLUSTRATION = {
    "why-choose-surf-camp-senegal":
        "Wide aerial view illustration: tiny Ngor Island surrounded by turquoise Atlantic, a few surf camp buildings visible among palm trees, warm golden evening light, geometric graphic style",

    "complete-guide-surf-camp-dakar-ngor-isla":
        "Graphic illustration: view from a traditional wooden pirogue approaching Ngor Island at sunset, the island silhouette with palms and surf camp, bold warm colors",

    "senegal-surf-camp-beginners-learn-faster":
        "Illustration: friendly surf lesson scene on a golden beach, instructor and student in the shallows, foam surfboard, joyful energy, Ngor Island in background",

    "advanced-surf-coaching-senegal-video-ana":
        "Graphic editorial illustration: surf coach reviewing slow-motion wave footage on tablet with student, seated on the beach, waves visible behind, detailed and dynamic",

    "ngor-surf-guide-right-left":
        "Aerial illustration of Ngor Right point break: perfect peeling wave from above, bold graphic wave lines, turquoise and navy ocean, surfer silhouette on the wave",

    "best-time-book-surf-camp-senegal":
        "Illustration: circular calendar graphic overlaid on Senegalese coastline, seasons shown with wave sizes, warm editorial infographic-art style",

    "surf-culture-island-life-ngor":
        "Colorful street art illustration of Ngor Island life: narrow sandy paths, colorful houses, surfboards leaning on walls, baobab trees, bold graphic lines",

    "week-at-premium-surf-camp-ngor-island":
        "Horizontal illustration strip: sequence of a surf camp day — dawn paddle, coaching session, pool terrace at sunset, dinner on the terrace, atmospheric storytelling",

    "endless-summer-senegal-ngor":
        "Vintage movie poster style illustration: retro sun setting over Ngor Right, surfer silhouette on longboard, film grain texture, 1960s illustration aesthetic, 'The Endless Summer' vibe",

    "senegal-surf-camp-for-beginners":
        "Joyful illustration: group of learner surfers celebrating first waves on the beach, foam boards visible, Senegalese sunset backdrop, warm triumphant energy",

    "best-time-to-surf-senegal":
        "Graphic illustration: stylized Atlantic swell map of West Africa, wave arrows, seasonal sun icons, Dakar and Ngor Island marked, bold editorial map art",

    "dakar-surf-spots-for-every-level":
        "Illustrated map of Dakar's Cap-Vert peninsula surf breaks: Ngor Island prominent with waves, other spots marked, graphic map illustration style, warm colors",

    "surf-camp-senegal-what-to-expect":
        "Split illustration: left shows surf camp courtyard with pool and hammocks, right shows Ngor waves at sunset, joined by a graphic diagonal line, editorial style",

    "how-to-improve-faster-at-surf-camp":
        "Dynamic illustration: before/after of a surfer — awkward beginner stance on left, confident flowing turn on right, progression arrows, coaching notes overlay",

    "senegal-surf-season-by-month":
        "Bold graphic illustration: large Atlantic wave at peak season, surfer on the face, spray catching the golden light, powerful and atmospheric",

    "licensed-surf-camp-senegal":
        "Illustration: official federation certificate on a wooden board wall beside surf trophies and photos, warm indoor light, authentic surf camp office feel",

    "how-to-choose-best-surf-camp-in-senegal":
        "Illustration: traveler sitting on Ngor beach researching on laptop, surfboard beside them, island and waves in background, thoughtful decision moment",

    "no-cars-ngor-island-surf-stay":
        "Peaceful illustration: narrow sandy Ngor Island path at sunrise, no vehicles, local fishermen and surfers walking with boards, palm trees, authentic island morning",

    "surf-trip-senegal-what-to-pack":
        "Flat-lay editorial illustration: perfectly arranged surf trip essentials — boards, wetsuit, fins, wax, passport, sunscreen — artistic overhead composition",

    "surfing-ngor-left-guide":
        "Graphic illustration: clean left-hand wave at Ngor from water level, surfer mid-carve, spray graphic, island rocks visible, bold wave illustration",

    "where-to-stay-surfing-dakar":
        "Comparison illustration: peaceful Ngor Island surf camp terrace with ocean view on one side, busy Dakar street on other, graphic split composition",

    "surfing-ngor-right-guide":
        "Dramatic illustration: powerful Ngor Right point break, long wall peeling perfectly, experienced surfer in trim position, graphic and atmospheric",

    "advanced-surf-senegal-ngor-right":
        "Action illustration: advanced surfer doing aerial at Ngor Right, spray frozen in graphic lines, powerful wave face, bold athletic composition",

    "why-senegal-is-an-underrated-surf-destination":
        "Illustrated travel poster style: dramatic Ngor Island coastline with waves, 'Senegal' as part of the landscape, bold colors, inviting adventure energy",

    "video-analysis-surf-camp-senegal":
        "Graphic illustration: close-up of tablet screen showing wave footage breakdown with arrows and coaching annotations, beach setting, analytical mood",

    "beginner-to-advanced-surf-coaching":
        "Triptych illustration: beginner on foam board, intermediate carving, advanced on overhead wave — progression story, bold graphic sequential art",

    "surf-spots-near-dakar":
        "Illustrated overhead panorama: Dakar's Cape Verde peninsula at golden hour, multiple surf breaks visible as white water lines, artistic map-like view",

    "how-surf-camp-schedule-works":
        "Illustrated daily schedule: sunrise surf session, breakfast terrace, coaching analysis, afternoon free surf, sunset — time shown graphically, editorial style",

    "surf-coaching-techniques-senegal":
        "Technical illustration: surf coach demonstrating pop-up technique on beach with graphic overlay showing body position, instructional but artistic",

    "french-surfers-senegal":
        "Warm illustration: international group of surfers sharing a wave at Ngor, diverse faces laughing in the water, multicultural surf community energy, celebratory",
}

# ── Generate article illustrations ───────────────────────────────────────────
strategy = json.load(open("/Users/simonazoulay/SurfCampSenegal/content/blog_strategy.json"))
arts = strategy["articles"]

def gen_article_img(art):
    slug = art["slug"]
    out  = f"{IMAGES_DIR}/{slug}.png"
    # Force regenerate ALL (new style)
    
    specific = ARTICLE_ILLUSTRATION.get(slug, f"Editorial surf illustration: {art['title']}. Ngor Island, Senegal, West Africa.")
    
    full_prompt = f"""{specific}

{DA_SYSTEM}

The illustration should feel like a high-end surf travel magazine double-page spread. Atmospheric and evocative, not a stock photo. Warm, vivid, memorable."""

    log(f"  ▶ Generating: {slug[:45]}")
    for model, size, quality in [
        ("dall-e-3", "1792x1024", "hd"),
        ("dall-e-3", "1024x1024", "hd"),
    ]:
        try:
            resp = client.images.generate(
                model=model, prompt=full_prompt[:1500],
                n=1, size=size, quality=quality
            )
            url = resp.data[0].url
            img = requests.get(url, timeout=30).content
            with open(out,"wb") as f: f.write(img)
            log(f"  ✅ {slug[:45]} ({len(img)//1024}KB)")
            return slug, out
        except Exception as e:
            log(f"  ⚠️  {model} {size}: {str(e)[:80]}")
    
    log(f"  ❌ Failed: {slug[:45]}")
    return slug, None

print(f"=== Regenerating {len(arts)} article illustrations ===")
print(f"Style: Editorial surf illustration, West African aesthetic\n")

with ThreadPoolExecutor(max_workers=10) as ex:
    futs = {ex.submit(gen_article_img, a): a for a in arts}
    done_count = [0]
    results = {}
    for f in as_completed(futs):
        slug, path = f.result()
        done_count[0] += 1
        if path:
            results[slug] = path
            log(f"  Progress: {done_count[0]}/{len(arts)}")

log(f"\n✅ Generated: {len(results)}/{len(arts)} article illustrations")

# Copy to demo
import shutil
for slug, src in results.items():
    if os.path.exists(src):
        shutil.copy2(src, f"{IMAGES_DIR}/{slug}.png")

# ════════════════════════════════════════════════════════════════════════════════
# Regenerate author persona photos — more realistic, less AI
# ════════════════════════════════════════════════════════════════════════════════
print("\n=== Regenerating author persona photos ===")

AUTHORS = [
    {
        "id": "kofi-mensah",
        "prompt": """Authentic portrait photography of a young Senegalese man in his early 30s, Dakar beach environment. 
Natural documentary-style photo, NOT AI-generated looking. 
Natural skin tones, genuine relaxed expression, slightly squinting in bright West African sun. 
Wearing a simple dark surf brand t-shirt. Ocean blurred in background. 
Shot on film camera, grain texture, warm afternoon light. 
Like a real surf instructor, not a model. Honest and likeable face.
NOT stock photography. Real documentary portrait."""
    },
    {
        "id": "sophie-renard", 
        "prompt": """Authentic portrait photography of a French woman in her late 20s, casual outdoor travel photo.
Natural documentary style, NOT AI-generated looking.
Sun-lightened hair, genuine warm smile, slightly tanned skin from outdoor travel.
Wearing casual bohemian travel clothes. Coastal environment in background.
Shot on film camera with natural light, slightly overexposed feel of a sunny day.
Like a real travel journalist, not a model. Genuine and relatable.
NOT stock photography. Real environmental portrait."""
    },
    {
        "id": "luca-ferretti",
        "prompt": """Authentic portrait photography of an Italian man in his late 30s, surf coaching environment.
Natural documentary style, NOT AI-generated looking.
Athletic build, tanned from outdoor coastal work, focused competent expression.
Wearing a technical surf/sports polo. Beach coaching environment.
Shot on film camera, warm coastal light.
Like a real ISA-certified surf coach, not a fitness model. Professional but approachable.
NOT stock photography. Real professional portrait."""
    },
]

def gen_author_photo(author):
    out = f"{AUTHORS_DIR}/{author['id']}.jpg"
    log(f"  ▶ Author: {author['id']}")
    try:
        resp = client.images.generate(
            model="dall-e-3",
            prompt=author["prompt"][:1500],
            n=1, size="1024x1024", quality="hd"
        )
        url = resp.data[0].url
        img = requests.get(url, timeout=30).content
        with open(out,"wb") as f: f.write(img)
        # Copy to demo
        shutil.copy2(out, f"{DEMO_DIR}/assets/images/author-{author['id']}.jpg")
        log(f"  ✅ {author['id']} ({len(img)//1024}KB)")
        return author["id"], out
    except Exception as e:
        log(f"  ❌ {author['id']}: {e}")
        return author["id"], None

with ThreadPoolExecutor(max_workers=3) as ex:
    futs = {ex.submit(gen_author_photo, a): a for a in AUTHORS}
    for f in as_completed(futs): f.result()

print("\n✅ All regeneration complete!")
