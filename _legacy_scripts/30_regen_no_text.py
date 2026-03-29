"""
Regenerate ALL 30 article images with ABSOLUTE no-text constraint.
Removes vintage poster, certificate, label-prone prompts.
"""
import json, os, requests
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading, shutil

OPENAI_KEY  = "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"
IMAGES_DIR  = "/Users/simonazoulay/SurfCampSenegal/cloudflare-demo/assets/images"
client = OpenAI(api_key=OPENAI_KEY)
lock   = threading.Lock()

def log(m):
    with lock: print(m, flush=True)

# NO-TEXT system instruction added to EVERY prompt
NO_TEXT = "CRITICAL: ABSOLUTELY NO TEXT, NO LETTERS, NO WORDS, NO NUMBERS, NO LABELS, NO SIGNS, NO WRITING OF ANY KIND anywhere in the image. Pure visual illustration only."

# Base style
STYLE = f"""
Illustration style: editorial surf and travel magazine.
Color palette: deep ocean navy, warm golden sand, burnt sunset orange, turquoise Atlantic.
West African coastal culture, Ngor Island, Dakar, Senegal atmosphere.
Painterly, graphic, NOT photorealistic.
Warm golden hour or dramatic Atlantic light.
{NO_TEXT}
"""

# ALL 30 prompts — rewritten to avoid text-generating scenes
PROMPTS = {
    "why-choose-surf-camp-senegal":
        "Aerial illustration of tiny Ngor Island surrounded by turquoise ocean, palm trees and surf camp buildings visible, a perfect wave breaking on the reef, warm golden evening light, geometric graphic style",

    "complete-guide-surf-camp-dakar-ngor-isla":
        "Illustration of a traditional wooden pirogue approaching Ngor Island at sunset, the island silhouette with palms reflected in calm water, bold warm colors, no text anywhere",

    "senegal-surf-camp-beginners-learn-faster":
        "Illustration of a surf lesson on a golden beach, instructor gesturing to student holding foam surfboard, gentle waves, Ngor Island in background, joyful warm scene",

    "advanced-surf-coaching-senegal-video-ana":
        "Illustration of a coach and surfer reviewing footage on a tablet at the beach, ocean in background, detailed coaching session, dynamic composition, no screens showing text",

    "ngor-surf-guide-right-left":
        "Aerial illustration of a perfect point break wave seen from above, bold graphic wave lines, turquoise and navy ocean, tiny surfer silhouette on the wave, no labels or markers",

    "best-time-book-surf-camp-senegal":
        "Illustration of a dramatic Senegal sunset over the ocean, silhouette of a surfer walking on the beach at golden hour, warm amber sky, long shadows, atmospheric",

    "surf-culture-island-life-ngor":
        "Colorful illustration of narrow sandy Ngor Island paths, colorful houses, surfboards leaning on walls, baobab tree, local life, bold graphic lines, no signs or text on buildings",

    "week-at-premium-surf-camp-ngor-island":
        "Illustration of a surf camp terrace with ocean view, hammocks, surfboards, pool glinting in warm light, palm trees, peaceful island atmosphere, no text on boards",

    "endless-summer-senegal-ngor":
        "Dramatic surf illustration in retro graphic style, powerful wave breaking at Ngor point, surfer silhouette on longboard, golden sunset sky reflected in water, film grain texture, no text",

    "senegal-surf-camp-for-beginners":
        "Illustration of three happy surfer silhouettes walking into the ocean with foam boards at sunset, Senegal coastline, warm triumphant feeling, bold colors",

    "best-time-to-surf-senegal":
        "Graphic illustration of Atlantic ocean swells approaching the West African coast, wave patterns showing different sizes, tropical sun, Dakar skyline silhouette in distance, no text",

    "dakar-surf-spots-for-every-level":
        "Illustrated overhead view of Dakar's Cap-Vert peninsula coastline, multiple surf breaks visible as white water lines, Ngor Island prominent, artistic map-like style without any labels",

    "surf-camp-senegal-what-to-expect":
        "Split illustration: left side shows surf camp courtyard with pool and surfboards stacked neatly, right side shows ocean waves at sunset, warm colors, no text anywhere",

    "how-to-improve-faster-at-surf-camp":
        "Dynamic illustration of a surfer performing a perfect cutback on a wave, spray catching golden light, coaching arrows illustrated as light lines, energetic composition, no text",

    "senegal-surf-season-by-month":
        "Dramatic wave illustration, large Atlantic swell breaking at Ngor, powerful curling lip, golden spray, lone experienced surfer on the face, bold atmospheric art",

    "licensed-surf-camp-senegal":
        "Illustration of trophy shelf and surfboards mounted on a wall with medals and ribbons, warm indoor light, authentic surf culture, no text on any items, decorative only",

    "how-to-choose-best-surf-camp-in-senegal":
        "Illustration of a traveler sitting on Ngor beach looking at the ocean, surfboard beside them, island and waves in background, thoughtful peaceful scene, no devices showing text",

    "no-cars-ngor-island-surf-stay":
        "Peaceful illustration of sandy Ngor Island path at sunrise, local fishermen and surfers walking with boards, palm trees, no vehicles, birds in sky, quiet island morning",

    "surf-trip-senegal-what-to-pack":
        "Flat-lay editorial illustration of surf trip gear arranged artistically, surfboard fins, wax, sunscreen tube, sunglasses, passport (closed), arranged in circular pattern, no visible text",

    "surfing-ngor-left-guide":
        "Graphic illustration of a clean left-hand wave at Ngor, surfer mid-carve, spray frozen in graphic lines, island rocks visible, bold wave art, no markers",

    "where-to-stay-surfing-dakar":
        "Comparison illustration, left shows peaceful Ngor Island surf camp terrace with ocean view, right shows busy Dakar street life, graphic split composition, no signs",

    "surfing-ngor-right-guide":
        "Dramatic illustration of powerful Ngor Right point break, long wall of water peeling perfectly, experienced surfer in trim, graphic and atmospheric, no text",

    "advanced-surf-senegal-ngor-right":
        "Action illustration of advanced surfer doing aerial maneuver, spray frozen in bold lines, powerful wave face, energetic athletic composition, no text",

    "why-senegal-is-an-underrated-surf-destination":
        "Beautiful illustration of Ngor Island coastline with breaking waves, dramatic Atlantic sky, lush but tropical, inviting and adventurous, no text or labels",

    "video-analysis-surf-camp-senegal":
        "Illustration of coach gesturing at a blank glowing tablet screen showing wave shapes only as abstract curves, beach setting, analytical mood, no text on screen",

    "beginner-to-advanced-surf-coaching":
        "Triptych illustration: beginner on foam board on left, intermediate carving in middle, advanced on overhead wave on right, progression story, bold sequential art, no text",

    "surf-spots-near-dakar":
        "Illustrated panoramic view of Dakar coastline at golden hour, multiple surf breaks visible as wave lines, dramatic sky, no labels or text markers anywhere",

    "how-surf-camp-schedule-works":
        "Circular illustration showing surf camp daily rhythm, sunrise, surfing, breakfast, coaching, sunset, illustrated as scenes in a wheel or timeline, no clock text",

    "surf-coaching-techniques-senegal":
        "Illustration of surf coach demonstrating pop-up on beach with student watching, coaching gestures shown with abstract arrow shapes not text, visual teaching scene",

    "french-surfers-senegal":
        "Warm illustration of international group of surfers together in water after a session, laughing and high-fiving, diverse faces, multicultural surf joy, no text",
}

strategy = json.load(open("/Users/simonazoulay/SurfCampSenegal/content/blog_strategy.json"))
arts = strategy["articles"]

def gen(art):
    slug = art["slug"]
    out  = f"{IMAGES_DIR}/{slug}.png"

    specific = PROMPTS.get(slug, f"Editorial surf illustration about {art['title'].lower()}, Ngor Island, Senegal, no text")
    prompt   = f"{specific}\n\n{STYLE}"

    log(f"  ▶ {slug[:48]}")
    for model, size, quality in [("dall-e-3","1792x1024","hd"),("dall-e-3","1024x1024","hd")]:
        try:
            resp = client.images.generate(model=model, prompt=prompt[:1500], n=1, size=size, quality=quality)
            img  = requests.get(resp.data[0].url, timeout=30).content
            with open(out,"wb") as f: f.write(img)
            log(f"  ✅ {slug[:48]} ({len(img)//1024}KB)")
            return slug, out
        except Exception as e:
            log(f"  ⚠️  {model}: {str(e)[:80]}")
    log(f"  ❌ {slug[:48]}")
    return slug, None

print(f"Regenerating {len(arts)} images — ZERO TEXT guaranteed\n")
with ThreadPoolExecutor(max_workers=10) as ex:
    futs = {ex.submit(gen, a): a for a in arts}
    done = [0]
    for f in as_completed(futs):
        _, path = f.result()
        done[0] += 1
        log(f"  [{done[0]}/30]")

ok = sum(1 for a in arts if os.path.exists(f"{IMAGES_DIR}/{a['slug']}.png"))
print(f"\n✅ Done: {ok}/30 images")
