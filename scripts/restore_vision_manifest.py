#!/usr/bin/env python3
"""
Restore the OpenAI Vision-analyzed manifest.json, clean up non-gallery tags,
and merge the 14 new images that were added after the vision analysis.
"""
import json
from pathlib import Path

ROOT   = Path(__file__).parent.parent
DEMO   = ROOT / "cloudflare-demo"
GALLERY = DEMO / "assets" / "images" / "gallery"
MANIFEST = GALLERY / "manifest.json"

VALID_TAGS = {"surf_action", "surf_house", "surf_coaching", "people_vibe",
              "island_life", "food", "sunset", "pool", "surf_gear"}

# Tag remapping for unsupported tags
TAG_REMAP = {
    "landscape": "island_life",  # aerial/ocean landscapes → island_life
}

# Manual tags for the 14 new images not covered by vision analysis
# Excludes pure hero/decorative images
MANUAL_TAGS = {
    "2_acb35348-fcf6-4a9d-8a8e-d618754f3d70.webp": {
        "tags": ["surf_house", "people_vibe"], "quality": 6,
        "caption": "Ngor Surfcamp Teranga social space",
    },
    "4Y4A1359.webp": {
        "tags": ["surf_action", "island_life"], "quality": 8,
        "caption": "Surfer riding a powerful wave at Ngor Island",
    },
    "CAML1091.webp": {
        "tags": ["surf_action", "people_vibe"], "quality": 7,
        "caption": "Surfing at Ngor Island Senegal",
    },
    "CAML1095.webp": {
        "tags": ["surf_action", "people_vibe"], "quality": 7,
        "caption": "Surfing at Ngor Island Senegal",
    },
    "CAML1098.webp": {
        "tags": ["surf_action", "surf_coaching"], "quality": 7,
        "caption": "Surf coaching session at Ngor",
    },
    "CAML1103.webp": {
        "tags": ["surf_action", "people_vibe"], "quality": 7,
        "caption": "Surfing at Ngor Island Senegal",
    },
    "CAML1109.webp": {
        "tags": ["surf_action", "island_life"], "quality": 7,
        "caption": "Surfing at Ngor Island Senegal",
    },
    "CAML1121.webp": {
        "tags": ["surf_action", "surf_coaching"], "quality": 7,
        "caption": "Surf coaching at Ngor Surfcamp Teranga",
    },
    "IMG_2832_meal.webp": {
        "tags": ["food"], "quality": 7,
        "caption": "Senegalese meal at Ngor Surfcamp Teranga",
    },
    "salon_ig.webp": {
        "tags": ["surf_house", "people_vibe"], "quality": 7,
        "caption": "Lounge area at Ngor Surfcamp Teranga",
    },
    "school_ig.webp": {
        "tags": ["surf_coaching", "people_vibe"], "quality": 7,
        "caption": "Surf school session at Ngor Island",
    },
    "sunset_ig.webp": {
        "tags": ["sunset", "island_life"], "quality": 8,
        "caption": "Sunset over the Atlantic from Ngor Island",
    },
}

# Hero/decorative images to exclude from gallery
EXCLUDE = {"gallery_hero.webp", "island_hero.webp", "0a_hero.webp"}


def clean_tags(tags: list) -> list:
    """Remap non-gallery tags to valid ones and deduplicate."""
    cleaned = []
    for t in tags:
        mapped = TAG_REMAP.get(t, t)
        if mapped in VALID_TAGS and mapped not in cleaned:
            cleaned.append(mapped)
    # Fallback: if all tags were unmapped, use island_life
    if not cleaned:
        cleaned = ["island_life"]
    return cleaned


def main():
    # Load the vision manifest
    vision_data = json.loads(open("/tmp/manifest_vision.json").read())
    vision_images = vision_data["images"]

    # Set of filenames already covered by vision
    vision_filenames = {Path(i["src"]).name for i in vision_images}

    # Process vision images: clean tags, keep only valid ones
    cleaned = []
    for img in vision_images:
        filename = Path(img["src"]).name
        if filename in EXCLUDE:
            continue
        # Check file actually exists
        if not (GALLERY / filename).exists():
            print(f"  SKIP (missing file): {filename}")
            continue

        new_tags = clean_tags(img["tags"])
        cleaned.append({
            "src":     img["src"],
            "tags":    new_tags,
            "quality": img.get("quality", 7),
            "caption": img.get("caption", "Ngor Surfcamp Teranga"),
            "w":       img.get("w", 800),
            "h":       img.get("h", 600),
        })

    # Add new images not in vision manifest
    added = 0
    for filename, meta in MANUAL_TAGS.items():
        if filename in EXCLUDE or filename in vision_filenames:
            continue
        if not (GALLERY / filename).exists():
            print(f"  SKIP (missing file): {filename}")
            continue
        cleaned.append({
            "src":     f"/assets/images/gallery/{filename}",
            "tags":    meta["tags"],
            "quality": meta["quality"],
            "caption": meta["caption"],
            "w":       800,
            "h":       600,
        })
        added += 1
        print(f"  Added new: {filename} → {meta['tags']}")

    manifest = {"images": cleaned}
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    # Stats
    all_tags = {}
    for img in cleaned:
        for t in img["tags"]:
            all_tags[t] = all_tags.get(t, 0) + 1

    print(f"\n✅ Restored manifest.json with {len(cleaned)} images ({added} new added)")
    print("   Tag distribution:")
    for tag, count in sorted(all_tags.items(), key=lambda x: -x[1]):
        print(f"     {tag}: {count}")


if __name__ == "__main__":
    main()
