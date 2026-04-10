import re

css_path = "/Users/simonazoulay/SurfCampSenegal/cloudflare-demo/assets/css/ngor-surfcamp.css"
with open(css_path, "r") as f:
    css = f.read()

# 1. Update footer-grid columns
css = re.sub(
    r"\.footer-grid\{display:grid;grid-template-columns:[^;]+;",
    r".footer-grid{display:grid;grid-template-columns: 1.8fr 1fr 1.4fr 1.2fr;",
    css
)

# 2. Add padding-top to footer-col to align with logo
if ".footer-col{" not in css:
    css += "\n.footer-col { padding-top: 12px; }\n"

# 3. Prevent WhatsApp link from wrapping awkwardly if possible, or just let the new grid handle it.
# The new grid 1.8fr 1fr 1.4fr 1.2fr gives more space to the 3rd column (1.4fr instead of 1.1fr)

with open(css_path, "w") as f:
    f.write(css)

print("Footer CSS patched.")
