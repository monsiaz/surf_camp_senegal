#!/usr/bin/env python3
"""
Performance optimization script:
1. Convert PNG/JPG images to WebP (massive size reduction)
2. Resize oversized images to appropriate dimensions
3. Update all HTML references to use .webp
4. Minify CSS and JS
"""
import os, re, shutil, subprocess
from pathlib import Path
from PIL import Image

DEMO = "/Users/simonazoulay/SurfCampSenegal/cloudflare-demo"
IMGS = f"{DEMO}/assets/images"
CSS_PATH = f"{DEMO}/assets/css/style.css"
JS_PATH  = f"{DEMO}/assets/js/animations.js"

# ═══════════════════════════════════════════════════════════════
# 1. IMAGE CONVERSION TO WebP
# ═══════════════════════════════════════════════════════════════

# Target dimensions per image category
IMG_CONFIGS = {
    "card":   {"max_w": 900,  "max_h": 600,  "quality": 82},   # blog card images
    "author": {"max_w": 300,  "max_h": 300,  "quality": 85},   # author avatars
    "icon":   {"max_w": 120,  "max_h": 120,  "quality": 80},   # small icons
    "persona":{"max_w": 160,  "max_h": 160,  "quality": 80},   # persona icons
    "brand":  {"max_w": 800,  "max_h": 600,  "quality": 85},   # brand assets
}

def get_config(path):
    name = os.path.basename(path).lower()
    parent = os.path.basename(os.path.dirname(path)).lower()
    if "author-" in name:
        return IMG_CONFIGS["author"]
    if parent == "icons" or "icons/" in path:
        # Persona icons (people faces) are a bit larger
        if any(x in name for x in ["amara","carlos","jake","fatou","marina"]):
            return IMG_CONFIGS["persona"]
        return IMG_CONFIGS["icon"]
    if parent == "brand":
        return IMG_CONFIGS["brand"]
    return IMG_CONFIGS["card"]

def convert_to_webp(src_path, dst_path, config):
    try:
        img = Image.open(src_path)
        # Convert to RGB if needed (RGBA → RGB with white bg for JPG compat)
        if img.mode in ("RGBA", "LA", "P"):
            bg = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            bg.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
            img = bg
        elif img.mode != "RGB":
            img = img.convert("RGB")

        # Resize if larger than target
        w, h = img.size
        max_w, max_h = config["max_w"], config["max_h"]
        if w > max_w or h > max_h:
            ratio = min(max_w/w, max_h/h)
            new_w, new_h = int(w*ratio), int(h*ratio)
            img = img.resize((new_w, new_h), Image.LANCZOS)

        img.save(dst_path, "WEBP", quality=config["quality"], method=4)
        return True
    except Exception as e:
        print(f"  ERROR converting {src_path}: {e}")
        return False

total_saved = 0
converted = 0
skipped = 0

print("=== Converting images to WebP ===")
# Process all PNG and JPG images
for ext in ["*.png", "*.jpg", "*.jpeg"]:
    for src in sorted(Path(IMGS).rglob(ext)):
        src_str = str(src)
        # Skip already-generated webp sources
        dst = src.with_suffix(".webp")
        dst_str = str(dst)

        src_size = src.stat().st_size
        # Skip if WebP already exists and is newer
        if dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
            skipped += 1
            continue

        config = get_config(src_str)
        ok = convert_to_webp(src_str, dst_str, config)
        if ok:
            dst_size = dst.stat().st_size
            saved = src_size - dst_size
            total_saved += saved
            converted += 1
            ratio = dst_size/src_size*100
            print(f"  {src.name}: {src_size//1024}KB → {dst_size//1024}KB ({ratio:.0f}%)")

print(f"\n✅ Converted {converted} images, skipped {skipped}")
print(f"   Total saved: {total_saved//1024//1024:.1f}MB")

# ═══════════════════════════════════════════════════════════════
# 2. UPDATE HTML REFERENCES TO WebP
# ═══════════════════════════════════════════════════════════════
print("\n=== Updating HTML to use WebP ===")

html_files = list(Path(DEMO).rglob("*.html"))
updated_files = 0
updated_refs = 0

for html_path in html_files:
    try:
        with open(html_path, encoding="utf-8", errors="replace") as f:
            content = f.read()

        original = content

        # Replace .png/.jpg/.jpeg references that have corresponding WebP files
        def replace_img_ext(m):
            full_match = m.group(0)
            filepath = m.group(1)
            ext = m.group(2)
            quote = m.group(3)

            # Only replace if WebP version exists
            # Map URL path to filesystem path
            rel_path = filepath.lstrip("/")
            webp_fs = os.path.join(DEMO, rel_path.replace(ext, ".webp"))
            if os.path.exists(webp_fs):
                return full_match.replace(filepath + ext + quote,
                                         filepath + ".webp" + quote)
            return full_match

        # Match src="...(path).(png|jpg)" and url('...(path).(png|jpg)')
        pattern = r'(/assets/[^"\')\s]+?)(\.png|\.jpg|\.jpeg)(["\'\s)])'
        new_content = re.sub(pattern, replace_img_ext, content)

        if new_content != original:
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            refs = len(re.findall(pattern, original)) - len(re.findall(pattern, new_content))
            updated_refs += len(re.findall(r'\.webp', new_content)) - len(re.findall(r'\.webp', original))
            updated_files += 1

    except Exception as e:
        print(f"  Error updating {html_path}: {e}")

print(f"✅ Updated {updated_files} HTML files")

# ═══════════════════════════════════════════════════════════════
# 3. ADD WEBP REFERENCES IN PYTHON BUILD SCRIPTS
# ═══════════════════════════════════════════════════════════════
# The build scripts use .png extensions — update for future builds
build_scripts = [
    "/Users/simonazoulay/SurfCampSenegal/build.py",
    "/Users/simonazoulay/SurfCampSenegal/_legacy_scripts/28_fix_blocks.py",
]

print("\n=== Updating build scripts for WebP ===")
for script in build_scripts:
    with open(script, encoding="utf-8") as f:
        content = f.read()
    original = content
    # Replace .png references in image URLs (not in conditional checks)
    # Only replace in f-strings that generate HTML image paths
    content = re.sub(
        r'(f"/assets/images/\{[^}]+\})\.png"',
        r'\1.webp"',
        content
    )
    content = re.sub(
        r'(/assets/images/\{[^}]+\})\.png"',
        r'\1.webp"',
        content
    )
    # Replace literal .png in img src patterns
    content = re.sub(
        r'(/assets/images/[a-z0-9_-]+)\.png"',
        r'\1.webp"',
        content
    )
    if content != original:
        with open(script, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  Updated {os.path.basename(script)}")
    else:
        print(f"  No changes needed: {os.path.basename(script)}")

# ═══════════════════════════════════════════════════════════════
# 4. MINIFY CSS
# ═══════════════════════════════════════════════════════════════
print("\n=== Minifying CSS ===")
try:
    import rcssmin
    with open(CSS_PATH, encoding="utf-8") as f:
        css = f.read()
    orig_size = len(css.encode())
    minified = rcssmin.cssmin(css)
    min_size = len(minified.encode())
    with open(CSS_PATH, "w", encoding="utf-8") as f:
        f.write(minified)
    print(f"✅ CSS: {orig_size//1024}KB → {min_size//1024}KB (saved {(orig_size-min_size)//1024}KB)")
except Exception as e:
    print(f"  CSS minify error: {e}")

# ═══════════════════════════════════════════════════════════════
# 5. MINIFY JS
# ═══════════════════════════════════════════════════════════════
print("\n=== Minifying JS ===")
try:
    import jsmin
    with open(JS_PATH, encoding="utf-8") as f:
        js = f.read()
    orig_size = len(js.encode())
    minified = jsmin.jsmin(js)
    min_size = len(minified.encode())
    with open(JS_PATH, "w", encoding="utf-8") as f:
        f.write(minified)
    print(f"✅ JS: {orig_size//1024}KB → {min_size//1024}KB (saved {(orig_size-min_size)//1024}KB)")
except Exception as e:
    print(f"  JS minify error: {e}")

print("\n✅ Asset optimization complete!")
