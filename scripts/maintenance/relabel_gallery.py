"""
Re-label gallery images with OpenAI Vision using a richer, more precise taxonomy.
Updates manifest.json in-place with better tags, refined quality scores, and detailed descriptions.
"""
import json, base64, os, sys, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# ─── Setup ──────────────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent.parent))
from env_utils import load_dotenv_if_needed
load_dotenv_if_needed()

from openai import OpenAI
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

DEMO      = Path(__file__).parent.parent / "cloudflare-demo"
MANIFEST  = DEMO / "assets" / "images" / "gallery" / "manifest.json"
MAX_WORKERS = 30

# ─── Rich taxonomy ───────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert image curator for a surf camp website (Ngor Surfcamp Teranga, Ngor Island, Dakar, Senegal).
Analyze the image and return STRICT JSON with these fields:

{
  "tags": [list of 1-4 tags from the taxonomy below],
  "quality": <integer 1-10>,
  "caption": "<short English caption, max 12 words>",
  "suitability": {
    "home_hero": <0-10>,
    "coaching_section": <0-10>,
    "surf_house_header": <0-10>,
    "island_section": <0-10>,
    "surfing_story": <0-10>,
    "gallery_feature": <0-10>,
    "blog_preview": <0-10>,
    "food_section": <0-10>
  }
}

TAXONOMY (pick the most accurate tags):
- "surf_action"   : surfer actively riding a wave (high energy, good form)
- "surf_coaching" : instructor teaching, coaching session, lesson on beach or water
- "surf_house"    : interior rooms, beds, corridors, common areas of the surf camp
- "pool"          : swimming pool, mosaic pool area
- "food"          : meals, plates, cooking, dining
- "island_life"   : island scenery, pirogue/boat, beach village, local life on Ngor Island
- "sunset"        : golden hour, sunset or sunrise light
- "people_vibe"   : group energy, smiles, social moments (not coaching)
- "surf_gear"     : surfboards stacked, wetsuits, equipment
- "landscape"     : ocean, seascape, wide shots without main subject
- "aerial"        : drone or high-angle overhead shot

QUALITY GUIDE:
10 = magazine cover quality, perfect composition+lighting+subject
9  = excellent, hero-worthy  
8  = very good, feature-worthy
7  = good, usable in sections
6  = acceptable, minor issues
5  = mediocre, use only if nothing better exists
1-4= poor quality, avoid

SUITABILITY: rate 0-10 for how well this image fits each specific use case. Be strict."""

def encode_image_b64(img_path: Path, max_px: int = 1024) -> str:
    from PIL import Image
    img = Image.open(img_path).convert("RGB")
    # Resize for API efficiency
    ratio = min(max_px / img.width, max_px / img.height, 1.0)
    if ratio < 1:
        img = img.resize((int(img.width * ratio), int(img.height * ratio)), Image.LANCZOS)
    import io
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode()

def label_image(img_entry: dict) -> dict:
    src = img_entry["src"]
    img_path = DEMO / src.lstrip("/")
    
    if not img_path.exists():
        return img_entry
    
    try:
        b64 = encode_image_b64(img_path)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}", "detail": "low"}},
                    {"type": "text", "text": "Analyze this image from Ngor Surfcamp Teranga."}
                ]}
            ],
            response_format={"type": "json_object"},
            max_tokens=400,
            temperature=0,
        )
        result = json.loads(response.choices[0].message.content)
        
        img_entry["tags"]         = result.get("tags", img_entry.get("tags", []))
        img_entry["quality"]      = result.get("quality", img_entry.get("quality", 7))
        img_entry["caption"]      = result.get("caption", img_entry.get("caption", ""))
        img_entry["suitability"]  = result.get("suitability", {})
        return img_entry
    except Exception as e:
        print(f"  ⚠️ Error on {src}: {e}")
        return img_entry

def main():
    manifest = json.loads(MANIFEST.read_text())
    images = manifest["images"]
    print(f"Re-labeling {len(images)} images with OpenAI Vision ({MAX_WORKERS} workers)...")
    
    updated = []
    errors = 0
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(label_image, img): img for img in images}
        for i, fut in enumerate(as_completed(futures)):
            try:
                result = fut.result()
                updated.append(result)
                tags = ", ".join(result.get("tags", []))
                q = result.get("quality", "?")
                src = result["src"].split("/")[-1][:40]
                print(f"  [{i+1:3d}/{len(images)}] Q={q} [{tags}] {src}")
            except Exception as e:
                updated.append(futures[fut])
                errors += 1
                print(f"  ❌ Error: {e}")
    
    # Sort by quality descending
    updated.sort(key=lambda x: -x.get("quality", 0))
    
    manifest["images"] = updated
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    print(f"\n✅ Done! {len(updated)} images re-labeled, {errors} errors.")
    print(f"Manifest saved: {MANIFEST}")

if __name__ == "__main__":
    main()
