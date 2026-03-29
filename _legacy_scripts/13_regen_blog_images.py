"""
Regenerate all 30 blog featured images with precise DA direction.
- gpt-image-1.5-2025-12-16
- Minimal editorial style, surf lifestyle
- 3-color palette: deep navy, warm sand, fire orange
- Each image matches the article's exact subject
- Horizontal 1536x1024 format
- Force regenerate (overwrite existing)
"""
import json, os, requests
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

OPENAI_KEY   = "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"
ARTICLES_DIR = "/Users/simonazoulay/SurfCampSenegal/content/articles/en"
IMAGES_DIR   = "/Users/simonazoulay/SurfCampSenegal/content/images_v2"
DEMO_DIR     = "/Users/simonazoulay/SurfCampSenegal/cloudflare-demo/assets/images"

os.makedirs(IMAGES_DIR, exist_ok=True)

client     = OpenAI(api_key=OPENAI_KEY)
lock       = threading.Lock()

# Precise DA style guide for all images
DA_STYLE = """
Art direction: Minimal editorial surf photography. Cinematic composition.
Color palette: dominant deep ocean navy blues, accents of warm sand/amber, 
occasional fire orange/sunset tones. Clean, airy feel.
Mood: authentic West African coastal lifestyle, not touristy.
No text, no logos, no watermarks.
Ultra-realistic photography style, shot on film camera.
Golden hour or blue hour lighting preferred.
Location context: Ngor Island, Dakar, Senegal, West Africa.
"""

# Per-article specific prompts with subject context
ARTICLE_PROMPTS = {
    "why-choose-surf-camp-senegal": "Aerial view of surfer paddling out at Ngor Island Senegal, crystal turquoise water, sandy beach, small island visible in background, golden morning light",
    "complete-guide-surf-camp-dakar-ngor-isla": "View from pirogue boat approaching Ngor Island, colorful wooden boat bow, island with surf camp buildings visible, Atlantic Ocean, Dakar coast in background",
    "senegal-surf-camp-beginners-learn-faster": "Surf instructor guiding beginner on beach with surfboard, Ngor Island shoreline, gentle waves, warm sandy beach, encouraging moment",
    "advanced-surf-coaching-senegal-video-ana": "Surf coach showing video playback on tablet to surfer sitting on beach, both looking at screen, ocean in background, professional coaching session",
    "ngor-surf-guide-right-left": "Perfect A-frame wave breaking at Ngor Island point break, two surfers taking off on right and left simultaneously, turquoise water, rocks visible",
    "best-time-book-surf-camp-senegal": "Surfer silhouette against dramatic sunset at Ngor Island, orange and deep blue sky, calm ocean surface reflecting colors, peaceful atmosphere",
    "surf-culture-island-life-ngor": "Colorful street art mural on Ngor Island wall, surfer walking past with board under arm, local children playing nearby, authentic island life",
    "week-at-premium-surf-camp-ngor-island": "Terrace of surf camp overlooking ocean, hammocks, surfboards leaning against wall, palm trees, morning coffee cup in foreground, Ngor Island view",
    "endless-summer-legacy-surfing-ngor": "Vintage-inspired golden light scene at Ngor point break, longboarder in classic style, black and white treatment with amber tones, timeless feel",
    "senegal-surf-camp-for-beginners": "Group of happy beginner surfers on beach holding longboards, smiling, surf instructor in center, Ngor Island backdrop, celebratory moment after first waves",
    "best-time-to-surf-senegal": "Monthly calendar-style split scene showing Ngor waves in different seasons, dry season clean waves vs green season bigger swells, Senegal coast",
    "dakar-surf-spots-for-every-level": "Map-style overhead drone shot of Ngor Island and surrounding Dakar coastline showing multiple surf breaks, turquoise water, beach geography",
    "surf-camp-senegal-what-to-expect": "Ngor surf camp courtyard, pool with surfboards stacked, hammocks, communal area with surfers relaxing, warm tropical light filtering through",
    "how-to-improve-faster-at-surf-camp": "Sequential surfing progression photos on Ngor beach, same surfer in beginner stance then confident pop-up, coaching notes in foreground",
    "senegal-surf-season-by-month": "Dramatic wave at Ngor Right during peak swell, powerful green-blue lip throwing, lone experienced surfer on rail, raw ocean power",
    "licensed-surf-camp-senegal": "Official Federation of Senegalese Surfing certificate on wall, surf camp office corner, trophies, professional context, authenticity",
    "how-to-choose-best-surf-camp-in-senegal": "Surfer sitting on beach at sunset reviewing accommodation options on phone, surfboard beside them, Ngor Island in background, decision moment",
    "no-cars-ngor-island-surf-stay": "Sandy pedestrian path on Ngor Island, surfers walking with boards, no vehicles, palm trees, low colorful houses, authentic island calm",
    "surf-trip-senegal-what-to-pack": "Surf travel bag open on bed with organized gear: wetsuit, fins, wax, sunscreen, passport, Senegal travel guide, surf camp booking confirmation",
    "surfing-ngor-left-guide": "Clean left-hander at Ngor Island, turquoise glassy wave, lone surfer doing smooth carve, rocks and island visible, perfect conditions",
    "where-to-stay-surfing-dakar": "Split view: Ngor Island surf camp terrace vs Dakar mainland busy street, peaceful island life comparison, ocean view from surf house",
    "surfing-ngor-right-guide": "Ngor Right point break, long wall peeling perfectly, surfer in trim position, classic point break framing, early morning glassy conditions",
    "advanced-surf-senegal-ngor-right": "Advanced surfer doing aerial maneuver at Ngor Right, spray catching light, powerful movement, serious surfing action photography",
    "why-senegal-underrated-surf-destination": "Ngor Island seen from water level, beautiful unspoiled coastline, no crowds, couple of surfers paddling out, authentic African coast",
    "video-analysis-surf-camp-senegal": "Close-up of tablet screen showing slow-motion surf footage, coach's hand pointing at technique detail, ocean blurred in background",
    "beginner-to-advanced-surf-coaching": "Split-screen style beach scene: left side beginner on foam board, right side same surfer doing confident turn, progression visible",
    "surf-spots-near-dakar": "Drone aerial shot of Dakar Cape Verde peninsula with multiple surf breaks visible, Ngor Island prominent, ocean meeting coastline",
    "how-surf-camp-schedule-works": "Morning lineup at surf camp: surfers stretching, boards lined up, coach briefing group on beach, Ngor waves breaking in background, organized energy",
    "surf-coaching-techniques-senegal": "Surf coach on beach demonstrating pop-up technique to small group, visual demonstration with arms, surfboard in sand as teaching prop",
    "french-surfers-senegal": "French and Senegalese surfers sharing waves and laughing in water at Ngor, multicultural scene, post-session stoke, international surf community",
}

def generate_image(art):
    slug      = art["slug"]
    title     = art["title"]
    out_path  = f"{IMAGES_DIR}/{slug}.png"

    # Get specific prompt or fall back to article's hero_image_prompt
    specific  = ARTICLE_PROMPTS.get(slug, art.get("hero_image_prompt", ""))
    if not specific:
        specific = f"Surf photography related to: {title}. Ngor Island, Senegal."

    full_prompt = f"{specific}\n\n{DA_STYLE}"

    with lock:
        print(f"  ▶ {slug[:50]}")

    for model, size in [
        ("gpt-image-1.5-2025-12-16", "1536x1024"),
        ("gpt-image-1.5-2025-12-16", "1024x1024"),
        ("dall-e-3",                  "1792x1024"),
        ("dall-e-3",                  "1024x1024"),
    ]:
        try:
            kwargs = {"model": model, "prompt": full_prompt[:1500], "n": 1, "size": size}
            if model.startswith("dall-e"): kwargs["quality"] = "hd"
            resp  = client.images.generate(**kwargs)
            img_url = resp.data[0].url
            if img_url:
                img_bytes = requests.get(img_url, timeout=30).content
            else:
                import base64
                img_bytes = base64.b64decode(resp.data[0].b64_json)
            with open(out_path, "wb") as f:
                f.write(img_bytes)
            with lock:
                print(f"  ✅ [{model[:20]}] {slug[:40]} ({len(img_bytes)//1024}KB)")
            return slug, out_path
        except Exception as e:
            with lock:
                print(f"  ⚠️  {model} {size}: {str(e)[:80]}")
            continue

    with lock:
        print(f"  ❌ All failed: {slug[:40]}")
    return slug, None

# Load articles
articles = []
for fname in sorted(os.listdir(ARTICLES_DIR)):
    if fname.endswith(".json"):
        a = json.load(open(f"{ARTICLES_DIR}/{fname}"))
        if a.get("slug"):
            articles.append(a)

print(f"Generating {len(articles)} blog images (10 parallel)...")
img_map = {}

with ThreadPoolExecutor(max_workers=10) as ex:
    futs = {ex.submit(generate_image, a): a for a in articles}
    for f in as_completed(futs):
        slug, path = f.result()
        if path: img_map[slug] = path

print(f"\n✅ Generated: {len(img_map)}/30")

# Copy successful images to demo dir
import shutil
ok = 0
for slug, src in img_map.items():
    dst = f"{DEMO_DIR}/{slug}.png"
    if os.path.exists(src):
        shutil.copy2(src, dst)
        ok += 1
print(f"Copied {ok} images to demo")
