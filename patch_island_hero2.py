import os

old_img = "df99f9_56b9af6efe2841eea44109b3b08b7da1.webp"
new_img = "island_hero.webp"

for py_file in ["build.py", "scripts/build_faq.py"]:
    path = os.path.join("/Users/simonazoulay/SurfCampSenegal", py_file)
    if os.path.exists(path):
        with open(path, "r") as f:
            content = f.read()
        # Change the folder from _WIX to _GAL if applicable
        content = content.replace(f"{{_WIX}}/{old_img}", f"{{_GAL}}/{new_img}")
        with open(path, "w") as f:
            f.write(content)

print("Python files patched.")
