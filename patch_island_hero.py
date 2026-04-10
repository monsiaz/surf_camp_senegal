import os
import glob

old_img = "wix/df99f9_56b9af6efe2841eea44109b3b08b7da1.webp"
new_img = "gallery/island_hero.webp"

# 1. Update python files
for py_file in ["build.py", "scripts/build_faq.py"]:
    path = os.path.join("/Users/simonazoulay/SurfCampSenegal", py_file)
    if os.path.exists(path):
        with open(path, "r") as f:
            content = f.read()
        content = content.replace(old_img, new_img)
        with open(path, "w") as f:
            f.write(content)

# 2. Update HTML files in cloudflare-demo
html_files = glob.glob("/Users/simonazoulay/SurfCampSenegal/cloudflare-demo/**/*.html", recursive=True)
html_files.append("/Users/simonazoulay/SurfCampSenegal/cloudflare-demo/island.html")

for path in set(html_files):
    if not os.path.isfile(path): continue
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    if old_img in content:
        # Replace the image path
        content = content.replace(old_img, new_img)
        
        # Add background-position to inline styles if it's a background-image
        # style="background-image:url('/assets/images/gallery/island_hero.webp')"
        # -> style="background-image:url('/assets/images/gallery/island_hero.webp'); background-position: center 65%;"
        content = content.replace(
            f"style=\"background-image:url('/assets/images/{new_img}')\"",
            f"style=\"background-image:url('/assets/images/{new_img}'); background-position: center 65%;\""
        )
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

print("Hero image replaced and framed.")
