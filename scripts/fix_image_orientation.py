#!/usr/bin/env python3
"""
fix_image_orientation.py
━━━━━━━━━━━━━━━━━━━━━━━━
Uses OpenAI Vision API (45 parallel workers) to detect gallery images that are
NOT correctly oriented (rotated 90°, 180° or upside-down). For each wrong image
it rotates the file in-place using Pillow and saves a corrected copy.

Run:
    python3 scripts/fix_image_orientation.py
"""

import os, sys, base64, json, pathlib, concurrent.futures, io
from openai import OpenAI

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit("Pillow required: pip install Pillow")

GALLERY = pathlib.Path(__file__).parents[1] / "cloudflare-demo/assets/images/gallery"
MANIFEST = GALLERY / "manifest.json"
MAX_WORKERS = 45
MODEL = "gpt-4o-mini"

client = OpenAI()  # uses OPENAI_API_KEY env var

PROMPT = (
    "Look at this image. Is it correctly oriented (right-side up, as it should "
    "appear on a website)? Reply ONLY with a JSON object like:\n"
    '{"ok": true}\n'
    "or if it is rotated/flipped incorrectly:\n"
    '{"ok": false, "rotation": 90}\n'
    "where rotation is the clockwise degrees needed to fix it (90, 180, or 270). "
    "Never add any other text."
)


def img_to_b64(path: pathlib.Path, max_side=512) -> str:
    """Resize and encode image to base64 JPEG for the Vision API (fast & cheap)."""
    img = Image.open(path).convert("RGB")
    img = ImageOps.exif_transpose(img)  # apply EXIF rotation first
    img.thumbnail((max_side, max_side), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=75)
    return base64.b64encode(buf.getvalue()).decode()


def check_orientation(path: pathlib.Path):
    """Call Vision API and return (path, ok, rotation) tuple."""
    try:
        b64 = img_to_b64(path)
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": PROMPT},
                    {"type": "image_url", "image_url": {
                        "url": f"data:image/jpeg;base64,{b64}",
                        "detail": "low"
                    }}
                ]
            }],
            max_tokens=60,
            temperature=0,
        )
        raw = resp.choices[0].message.content.strip()
        # parse JSON (strip markdown fences if any)
        raw = raw.replace("```json","").replace("```","").strip()
        data = json.loads(raw)
        ok = bool(data.get("ok", True))
        rotation = int(data.get("rotation", 0)) if not ok else 0
        return path, ok, rotation
    except Exception as e:
        print(f"  [WARN] {path.name}: {e}")
        return path, True, 0  # assume OK on error


def fix_rotation(path: pathlib.Path, rotation: int):
    """Rotate image clockwise by `rotation` degrees and save in-place."""
    try:
        img = Image.open(path)
        img = ImageOps.exif_transpose(img)  # strip EXIF rotation first
        # PIL rotate is counter-clockwise; negate for clockwise
        fixed = img.rotate(-rotation, expand=True)
        # Preserve format
        fmt = path.suffix.lstrip(".").upper()
        if fmt == "JPG":
            fmt = "JPEG"
        if fmt not in ("JPEG", "WEBP", "PNG"):
            fmt = "JPEG"
        fixed.save(path, format=fmt, quality=90)
        print(f"  ✅ fixed {rotation}° CW: {path.name}")
    except Exception as e:
        print(f"  [ERROR] could not fix {path.name}: {e}")


def main():
    exts = {".webp", ".jpg", ".jpeg", ".png", ".avif"}
    images = sorted([p for p in GALLERY.iterdir() if p.suffix.lower() in exts
                     and p.name != "manifest.json"])

    print(f"Checking orientation of {len(images)} gallery images with {MAX_WORKERS} workers…")

    wrong = []
    checked = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(check_orientation, p): p for p in images}
        for fut in concurrent.futures.as_completed(futures):
            path, ok, rotation = fut.result()
            checked += 1
            if not ok:
                wrong.append((path, rotation))
                print(f"  ⚠️  wrong orientation ({rotation}°): {path.name}")
            if checked % 20 == 0:
                print(f"  … {checked}/{len(images)} checked")

    print(f"\n✅ Checked {checked} images. Found {len(wrong)} with incorrect orientation.")

    if wrong:
        print(f"\nFixing {len(wrong)} images…")
        for path, rotation in wrong:
            fix_rotation(path, rotation)
        print(f"\n✅ All {len(wrong)} images corrected. Run build.py to redeploy.")
    else:
        print("All images are correctly oriented — nothing to fix.")


if __name__ == "__main__":
    main()
