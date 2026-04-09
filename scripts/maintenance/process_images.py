#!/usr/bin/env python3
"""
Image Processing Pipeline for Ngor Surfcamp Teranga
=====================================================
1. Scan extracted image directories
2. Resize & convert all images to optimised WebP (max 2000px, 85% quality)
3. Use OpenAI GPT-4o Vision (40 parallel workers) to label each image
4. Generate a JSON manifest with labels, dimensions, file sizes
5. Output to cloudflare-demo/assets/images/gallery/

Labels used:
  surfcamp   – hébergement, chambre, piscine, terrasse, bâtiments
  surf       – vagues, surfeurs en action, planche, océan
  coaching   – cours de surf, instructor, video analysis, apprentissage
  people     – convivialité, guests, team, sourires, groupe
  island     – île de Ngor, paysage, nature, vue panoramique
  food       – repas, table, cuisine sénégalaise
  sunset     – coucher de soleil, golden hour, ciel coloré
  aerial     – vue aérienne, drone
  water      – eau, baignade, piscine, mer
"""

import os, sys, json, re, base64, hashlib, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image
import io

sys.path.insert(0, str(Path(__file__).parent))
import env_utils
import openai

# ─── Config ───────────────────────────────────────────────────────────────────
API_KEY   = os.environ.get("OPENAI_API_KEY", "")
MODEL     = "gpt-4o"          # Vision capable
WORKERS   = 40
MAX_PX    = 2000              # Max dimension for final WebP
THUMB_PX  = 800               # Thumb dimension sent to API (saves tokens)
WEBP_Q    = 85                # WebP quality
THUMB_Q   = 75                # Thumbnail API quality

ROOT      = Path(__file__).parent.parent
EXTRACTED = ROOT / "content" / "images" / "extracted"
OUT_DIR   = ROOT / "cloudflare-demo" / "assets" / "images" / "gallery"
MANIFEST  = OUT_DIR / "manifest.json"

VALID_EXT = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif", ".tiff", ".tif"}

ALL_TAGS  = ["surfcamp", "surf", "coaching", "people", "island", "food", "sunset", "aerial", "water"]

SYSTEM_PROMPT = """You are a visual classifier for a premium surf camp (Ngor Surfcamp Teranga, Dakar, Senegal).
Classify the image with 1 to 4 tags from this exact list:
surfcamp, surf, coaching, people, island, food, sunset, aerial, water

Rules:
- surfcamp: accommodation, rooms, pool, terrace, buildings, camp facilities
- surf: waves, surfers in action, surfboards, ocean action shots
- coaching: surf lessons, instructor teaching, video analysis, learning
- people: guests, team members, smiling, social moments, groups
- island: Ngor island landscape, panoramic views, nature, village
- food: meals, table setting, Senegalese cuisine, breakfast
- sunset: sunset/golden hour, colourful sky
- aerial: drone shots, bird's eye view
- water: swimming, diving, sea, pool water close-ups

Respond with ONLY a JSON object like:
{"tags": ["surf", "people"], "quality": 8, "caption": "Two surfers riding a wave at Ngor Right"}

quality is 1-10 (10=stunning hero-worthy shot, 1=blurry/unusable)
caption is a short English description (max 15 words)
"""

client = openai.OpenAI(api_key=API_KEY)

# ─── Helpers ──────────────────────────────────────────────────────────────────

def collect_images():
    """Collect all valid image paths from extracted directories."""
    imgs = []
    for p in EXTRACTED.rglob("*"):
        if p.suffix.lower() in VALID_EXT and p.is_file():
            # Skip MacOS metadata files
            if p.name.startswith("._") or "__MACOSX" in str(p):
                continue
            imgs.append(p)
    return sorted(imgs)


def img_to_b64_thumb(path: Path) -> tuple[str, tuple[int,int]]:
    """Open image, resize to THUMB_PX, return base64 JPEG + original (w, h)."""
    try:
        img = Image.open(path)
    except Exception:
        # Try with rawpy for HEIC
        raise
    
    orig_size = img.size
    img = img.convert("RGB")
    
    # Resize for API
    img.thumbnail((THUMB_PX, THUMB_PX), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=THUMB_Q, optimize=True)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return b64, orig_size


def label_image(path: Path):
    """Call GPT-4o Vision to label one image. Returns label dict or None on error."""
    try:
        b64, orig_size = img_to_b64_thumb(path)
    except Exception as e:
        print(f"  [SKIP] {path.name}: {e}")
        return None
    
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": [
                    {"type": "image_url", "image_url": {
                        "url": f"data:image/jpeg;base64,{b64}",
                        "detail": "low"
                    }}
                ]}
            ],
            max_completion_tokens=150,
            temperature=0.1,
        )
        raw = resp.choices[0].message.content.strip()
        # Parse JSON from response
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        if not m:
            return None
        data = json.loads(m.group(0))
        tags = [t for t in data.get("tags", []) if t in ALL_TAGS]
        return {
            "tags": tags,
            "quality": int(data.get("quality", 5)),
            "caption": data.get("caption", "")[:100],
            "orig_w": orig_size[0],
            "orig_h": orig_size[1],
        }
    except Exception as e:
        print(f"  [API ERR] {path.name}: {e}")
        return None


def convert_to_webp(src: Path, dst: Path, max_px: int = MAX_PX, quality: int = WEBP_Q):
    """Convert source image to WebP, resize if needed."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        return  # skip if already done
    try:
        img = Image.open(src).convert("RGB")
        img.thumbnail((max_px, max_px), Image.LANCZOS)
        img.save(dst, format="WEBP", quality=quality, method=4)
    except Exception as e:
        print(f"  [CONV ERR] {src.name}: {e}")


def safe_slug(path: Path) -> str:
    """Generate a unique, URL-safe filename (without extension)."""
    h = hashlib.md5(str(path).encode()).hexdigest()[:8]
    stem = re.sub(r'[^a-zA-Z0-9_-]', '_', path.stem)[:40]
    return f"{stem}_{h}"


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    if not API_KEY:
        sys.exit("ERROR: OPENAI_API_KEY not set")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load existing manifest to resume interrupted runs
    existing = {}
    if MANIFEST.exists():
        with open(MANIFEST) as f:
            existing = {item["src"]: item for item in json.load(f).get("images", [])}
    print(f"Existing manifest entries: {len(existing)}")

    images = collect_images()
    print(f"Found {len(images)} images to process")

    results = list(existing.values())
    to_process = [p for p in images if str(p) not in {r["_src_path"] for r in results}]
    print(f"To process: {len(to_process)} new images")
    print(f"Converting to WebP + labeling with {WORKERS} workers...")

    def process_one(path: Path):
        slug = safe_slug(path)
        dst = OUT_DIR / f"{slug}.webp"
        web_path = f"/assets/images/gallery/{slug}.webp"

        # Convert to WebP first
        convert_to_webp(path, dst)
        
        if not dst.exists():
            return None

        file_size = dst.stat().st_size

        # Label with AI
        label_data = label_image(path)
        if label_data is None:
            label_data = {"tags": [], "quality": 5, "caption": path.stem}

        # Get final dimensions
        try:
            with Image.open(dst) as img:
                w, h = img.size
        except Exception:
            w, h = label_data.get("orig_w", 0), label_data.get("orig_h", 0)

        entry = {
            "src": web_path,
            "slug": slug,
            "tags": label_data["tags"],
            "quality": label_data["quality"],
            "caption": label_data["caption"],
            "w": w,
            "h": h,
            "size_kb": round(file_size / 1024),
            "_src_path": str(path),
            "_source_zip": path.parts[-3] if len(path.parts) >= 3 else "",
        }
        print(f"  ✓ {slug}.webp | {label_data['tags']} | q={label_data['quality']} | {round(file_size/1024)}KB")
        return entry

    # Run with 40 workers
    done = 0
    total = len(to_process)
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futures = {ex.submit(process_one, p): p for p in to_process}
        for future in as_completed(futures):
            done += 1
            r = future.result()
            if r:
                results.append(r)
            # Save progress every 20 images
            if done % 20 == 0 or done == total:
                # Sort by quality desc
                results_sorted = sorted(results, key=lambda x: -x.get("quality", 0))
                manifest_data = {
                    "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "total": len(results_sorted),
                    "tags": ALL_TAGS,
                    "images": results_sorted
                }
                with open(MANIFEST, "w") as f:
                    json.dump(manifest_data, f, ensure_ascii=False, indent=2)
                print(f"  [Progress] {done}/{total} processed, manifest saved")

    # Final sort and save
    results_sorted = sorted(results, key=lambda x: -x.get("quality", 0))
    manifest_data = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total": len(results_sorted),
        "tags": ALL_TAGS,
        "images": results_sorted
    }
    with open(MANIFEST, "w") as f:
        json.dump(manifest_data, f, ensure_ascii=False, indent=2)

    # Print summary
    from collections import Counter
    tag_counts = Counter(t for r in results_sorted for t in r.get("tags", []))
    print("\n=== Summary ===")
    print(f"Total images processed: {len(results_sorted)}")
    print(f"Tag distribution: {dict(tag_counts.most_common())}")
    print(f"High quality (≥8): {sum(1 for r in results_sorted if r.get('quality', 0) >= 8)}")
    print(f"Manifest: {MANIFEST}")
    print(f"WebP gallery: {OUT_DIR}")


if __name__ == "__main__":
    main()
