"""
Generate brand assets: 16 circular vintage badge icons
Style: black bg, white line art, stamp/badge, surf meets West Africa
Uses: Nano Banana 2 (gemini-3.1-flash-image-preview) → Imagen 4 Ultra fallback → DALL-E 3
"""
import os, base64, requests, json, time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

GEMINI_KEY  = "AIzaSyBD5ccBWV5IZggOzbO2pYhU2mvnmAtJyyI"
OPENAI_KEY  = "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"
ASSETS_DIR  = "/Users/simonazoulay/SurfCampSenegal/cloudflare-demo/assets/images/brand"
os.makedirs(ASSETS_DIR, exist_ok=True)

lock = threading.Lock()

def log(msg):
    with lock: print(msg, flush=True)

# ── Art direction base style ───────────────────────────────────────────────────
STYLE = """
Vintage circular badge/stamp icon. Single color: pure white illustration on pure black (#000000) background.
Style: bold clean linework, woodcut/linocut aesthetic, retro surf brand stamp.
No gradients, no shadows, no colors — only stark white lines on black.
Perfectly circular badge frame with thin decorative border.
Organic hand-crafted feel, not digital-looking.
Square 1:1 format. The badge fills 90% of the canvas.
Ultra high detail linework.
"""

# ── 16 Badge icons ────────────────────────────────────────────────────────────
BADGES = [
    {
        "id": "badge-surfer-wave",
        "prompt": f"Circular vintage badge: lone surfer silhouette carving a large breaking wave, ocean spray, bold circular frame, 'NGOR' text arc at bottom. {STYLE}",
        "use": "hero_section",
    },
    {
        "id": "badge-surfboard-paddle",
        "prompt": f"Circular vintage badge: single surfboard held overhead from below by a hand reaching up, ocean horizon line, rays of sun behind, bold circular frame. {STYLE}",
        "use": "surf_house",
    },
    {
        "id": "badge-crossed-boards",
        "prompt": f"Circular vintage badge: two longboards crossed in X formation over wave lines, circle frame with rope/chain border decoration. {STYLE}",
        "use": "blog_header",
    },
    {
        "id": "badge-compass-surf",
        "prompt": f"Circular vintage badge: nautical compass rose with small wave motifs in each cardinal direction, 'DAKAR' text arc at top, 'SENEGAL' at bottom, ornate detailed compass design. {STYLE}",
        "use": "island_section",
    },
    {
        "id": "badge-ngor-palms",
        "prompt": f"Circular vintage badge: two palm trees on a tiny island surrounded by ocean waves, sun above horizon, 'NGOR ISLAND' text arc at bottom. {STYLE}",
        "use": "island_page",
    },
    {
        "id": "badge-ngor-lighthouse",
        "prompt": f"Circular vintage badge: tall lighthouse on rocky cliff over stormy waves, beams of light radiating, 'NGOR LIGHTHOUSE' text arc at bottom, dramatic composition. {STYLE}",
        "use": "surfing_section",
    },
    {
        "id": "badge-teranga-spirit",
        "prompt": f"Circular vintage badge: majestic African baobab tree with waves crashing at its roots, roots visible below waterline, 'TERANGA SPIRIT' text arc at bottom. {STYLE}",
        "use": "footer_deco",
    },
    {
        "id": "badge-ngor-pirogue",
        "prompt": f"Circular vintage badge: traditional Senegalese pirogue fishing boat floating on calm ocean waves, seen from side, 'NGOR' text arc at top, 'PIROGUE' at bottom. {STYLE}",
        "use": "booking_section",
    },
    {
        "id": "badge-anchor-waves",
        "prompt": f"Circular vintage badge: classic anchor partially submerged in rolling waves, rope coiled around anchor, 'EST.' arc at top, '2025' arc at bottom. {STYLE}",
        "use": "about_section",
    },
    {
        "id": "badge-shark-fin",
        "prompt": f"Circular vintage badge: shark fin breaking calm ocean surface, sun peeking above horizon behind it, minimalist composition, 'SURF' arc at top, 'SENEGAL' at bottom. {STYLE}",
        "use": "blog_category",
    },
    {
        "id": "badge-cowrie-shells",
        "prompt": f"Circular vintage badge: arrangement of 8 cowrie shells in circular pattern, traditional West African decorative motif, 'TERANGA' text arc below. {STYLE}",
        "use": "about_deco",
    },
    {
        "id": "badge-sere",
        "prompt": f"Circular vintage badge: bold 'SÈRÈ' text in center (Wolof for 'peace/harmony'), surrounded by small wave patterns, geometric tribal border. {STYLE}",
        "use": "testimonial",
    },
    {
        "id": "badge-ngor-right",
        "prompt": f"Circular vintage badge: overhead aerial view of a perfect point break wave curling to the right, surfer dots visible on wave face, 'NGOR RIGHT' text arc below. {STYLE}",
        "use": "wave_section",
    },
    {
        "id": "badge-endless-summer",
        "prompt": f"Circular vintage badge: retro sun with face in center, surfboard silhouette diagonal across sun, film strip border around circle, '1964' text arc below, vintage movie poster feel. {STYLE}",
        "use": "heritage_section",
    },
    {
        "id": "badge-federation",
        "prompt": f"Circular vintage badge: shield/crest with wave and surfboard inside, laurel leaves on sides, 'LICENSED' arc at top, 'FEDERATION' arc at bottom, official seal appearance. {STYLE}",
        "use": "trust_section",
    },
    {
        "id": "badge-atlantic-wave",
        "prompt": f"Circular vintage badge: powerful Atlantic ocean wave forming perfect barrel/tube, spray from lip, 'ATLANTIC OCEAN' text arc at top, 'WEST AFRICA' at bottom. {STYLE}",
        "use": "wave_bg",
    },
]

# ── Gemini generation ─────────────────────────────────────────────────────────
def gen_gemini_imagen4(badge):
    """Try Imagen 4 Ultra via Google AI SDK"""
    from google import genai as gai
    from google.genai import types

    client = gai.Client(api_key=GEMINI_KEY)
    resp = client.models.generate_images(
        model="imagen-4.0-ultra-generate-001",
        prompt=badge["prompt"],
        config=types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio="1:1",
            safety_filter_level="BLOCK_NONE",
        )
    )
    if resp.generated_images:
        img_bytes = resp.generated_images[0].image.image_bytes
        return img_bytes
    return None

def gen_gemini_nano2(badge):
    """Try Nano Banana 2 (gemini-3.1-flash-image-preview)"""
    from google import genai as gai
    from google.genai import types

    client = gai.Client(api_key=GEMINI_KEY)
    resp = client.models.generate_content(
        model="gemini-3.1-flash-image-preview",
        contents=badge["prompt"],
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
        ),
    )
    for part in resp.candidates[0].content.parts:
        if part.inline_data and "image" in part.inline_data.mime_type:
            return part.inline_data.data
    return None

def gen_dalle(badge):
    """Fallback: DALL-E 3"""
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_KEY)
    resp = client.images.generate(
        model="dall-e-3",
        prompt=badge["prompt"][:1500],
        n=1, size="1024x1024", quality="hd"
    )
    url = resp.data[0].url
    return requests.get(url, timeout=30).content

def generate_badge(badge):
    bid  = badge["id"]
    out  = f"{ASSETS_DIR}/{bid}.png"

    if os.path.exists(out) and os.path.getsize(out) > 5000:
        log(f"  [skip] {bid}")
        return bid, out

    log(f"  ▶ {bid}")
    img_bytes = None

    # Try Gemini Imagen 4 Ultra first
    for attempt_fn, label in [
        (gen_gemini_imagen4, "Imagen 4 Ultra"),
        (gen_gemini_nano2,   "Nano Banana 2"),
        (gen_dalle,          "DALL-E 3"),
    ]:
        try:
            img_bytes = attempt_fn(badge)
            if img_bytes:
                log(f"  ✅ [{label}] {bid}")
                break
        except Exception as e:
            log(f"  ⚠️  [{label}] {bid}: {str(e)[:80]}")
            continue

    if img_bytes:
        with open(out, "wb") as f:
            f.write(img_bytes if isinstance(img_bytes, bytes) else base64.b64decode(img_bytes))
        return bid, out
    else:
        log(f"  ❌ All failed: {bid}")
        return bid, None

print(f"=== Generating {len(BADGES)} brand badge assets ===")
print(f"Output: {ASSETS_DIR}\n")

with ThreadPoolExecutor(max_workers=8) as ex:
    futs = {ex.submit(generate_badge, b): b for b in BADGES}
    results = {}
    for f in as_completed(futs):
        bid, path = f.result()
        if path: results[bid] = path

print(f"\n✅ Generated: {len(results)}/{len(BADGES)} badges")

# Save metadata
meta = {b["id"]: {"use": b["use"], "path": f"/assets/images/brand/{b['id']}.png"} for b in BADGES}
with open(f"{ASSETS_DIR}/badges.json", "w") as f:
    json.dump(meta, f, indent=2)
print(f"Saved metadata → {ASSETS_DIR}/badges.json")
