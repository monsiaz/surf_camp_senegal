#!/usr/bin/env python3
"""
Generate gallery/manifest.json from existing WebP images in the gallery folder.
Assigns tags based on filename patterns.
"""
import json
from pathlib import Path

ROOT      = Path(__file__).parent.parent
GALLERY   = ROOT / "cloudflare-demo" / "assets" / "images" / "gallery"
MANIFEST  = GALLERY / "manifest.json"

TAGS = ["surf_action","surf_house","surf_coaching","people_vibe","island_life","food","sunset","pool","surf_gear"]

def assign_tags(stem: str) -> list:
    s = stem.lower()
    # Explicit names
    if "sunset" in s:
        return ["sunset", "island_life"]
    if "school" in s:
        return ["surf_coaching", "people_vibe"]
    if "video_analysis" in s or "video" in s:
        return ["surf_coaching"]
    if "surf_instructor" in s or "instructor" in s:
        return ["surf_coaching", "people_vibe"]
    if "pool" in s:
        return ["pool", "surf_house"]
    if "food" in s or "meal" in s or "breakfast" in s or "lunch" in s or "dinner" in s:
        return ["food"]
    if "wave" in s or "surf_action" in s:
        return ["surf_action"]
    if "gear" in s or "board" in s or "wetsuit" in s:
        return ["surf_gear"]
    if "island" in s or "ngor" in s:
        return ["island_life"]

    # Professional photo series
    if stem.startswith("CAML"):
        n = 0
        try:
            n = int(stem[4:8])
        except:
            pass
        # Spread CAML across categories cyclically
        if n % 5 == 0:
            return ["surf_action", "island_life"]
        elif n % 5 == 1:
            return ["people_vibe", "surf_house"]
        elif n % 5 == 2:
            return ["surf_house", "surf_action"]
        elif n % 5 == 3:
            return ["people_vibe", "island_life"]
        else:
            return ["surf_house", "people_vibe"]

    if stem.startswith("4Y4A"):
        n = 0
        try:
            n = int(stem[4:8])
        except:
            pass
        if n % 4 == 0:
            return ["surf_action"]
        elif n % 4 == 1:
            return ["surf_action", "island_life"]
        elif n % 4 == 2:
            return ["island_life", "surf_house"]
        else:
            return ["people_vibe", "surf_action"]

    if stem.startswith("IMG_"):
        n = 0
        try:
            n = int(stem[4:8])
        except:
            pass
        if n % 5 == 0:
            return ["pool", "surf_house"]
        elif n % 5 == 1:
            return ["food"]
        elif n % 5 == 2:
            return ["surf_house", "people_vibe"]
        elif n % 5 == 3:
            return ["pool"]
        else:
            return ["food", "people_vibe"]

    if stem.startswith("DSC"):
        n = 0
        try:
            n = int(stem[3:8])
        except:
            pass
        if n % 3 == 0:
            return ["surf_action"]
        elif n % 3 == 1:
            return ["island_life", "people_vibe"]
        else:
            return ["surf_house"]

    # UUID-style images — spread evenly by hash of first char
    first = ord(stem[0]) if stem else 0
    cat_idx = first % len(TAGS)
    t1 = TAGS[cat_idx]
    t2 = TAGS[(cat_idx + 3) % len(TAGS)]
    return [t1, t2]


def make_alt(stem: str, tags: list) -> str:
    tag_map = {
        "surf_action": "Surfing at Ngor Island",
        "surf_house":  "Ngor Surfcamp Teranga",
        "surf_coaching": "Surf coaching session",
        "people_vibe": "Surf camp community",
        "island_life": "Ngor Island life",
        "food":        "Senegalese cuisine at the camp",
        "sunset":      "Sunset over the Atlantic",
        "pool":        "Pool at Ngor Surfcamp Teranga",
        "surf_gear":   "Surf equipment at the camp",
    }
    primary = tags[0] if tags else "surf_house"
    return tag_map.get(primary, "Ngor Surfcamp Teranga")


def main():
    webps = sorted(GALLERY.glob("*.webp"))
    # Exclude hero/bw images that aren't gallery photos
    exclude = {"0a_hero.webp"}
    images = []
    for p in webps:
        if p.name in exclude:
            continue
        stem = p.stem
        # Remove hash suffix (_xxxxxxxx) for tag logic
        base = stem.rsplit("_", 1)[0] if "_" in stem and len(stem.rsplit("_",1)[-1]) == 8 else stem
        tags = assign_tags(base)
        alt  = make_alt(base, tags)
        images.append({
            "src":     f"/assets/images/gallery/{p.name}",
            "tags":    tags,
            "quality": 7,
            "caption": alt,
            "w":       800,
            "h":       600,
        })

    manifest = {"images": images}
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    print(f"✅ manifest.json written with {len(images)} images")

    # Print tag distribution
    from collections import Counter
    tag_count = Counter(t for img in images for t in img["tags"])
    print("\nTag distribution:")
    for tag, count in sorted(tag_count.items(), key=lambda x: -x[1]):
        print(f"  {tag}: {count}")


if __name__ == "__main__":
    main()
