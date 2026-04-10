import re

css_path = "/Users/simonazoulay/SurfCampSenegal/cloudflare-demo/assets/css/ngor-surfcamp.css"
with open(css_path, "r") as f:
    css = f.read()

# Make FSS badge fit-content instead of 100%
css = re.sub(
    r"\.footer-fss-badge\{display:inline-flex;align-items:center;gap:12px;padding:10px 14px 10px 10px;background:rgba\(255,255,255,0\.06\);border:1px solid rgba\(240,192,96,0\.28\);border-radius:12px;box-sizing:border-box;width:100%;max-width:100%\}",
    r".footer-fss-badge{display:inline-flex;align-items:center;gap:12px;padding:10px 18px 10px 10px;background:rgba(255,255,255,0.06);border:1px solid rgba(240,192,96,0.28);border-radius:12px;box-sizing:border-box;width:fit-content;max-width:100%}",
    css
)

# Also, the WhatsApp link in Contact column wrapping:
# Let's change the text in build.py to not have "WhatsApp: " prefix, or just use a non-breaking space, or let the wider column handle it.
# The wider column (1.4fr instead of 1.1fr) should be enough. Let's make it 1.5fr to be safe.
css = re.sub(
    r"\.footer-grid\{display:grid;grid-template-columns:[^;]+;",
    r".footer-grid{display:grid;grid-template-columns: 1.8fr 1fr 1.5fr 1.1fr;",
    css
)

# Align the tops:
# Remove the padding-top: 12px from .footer-col if it was added
css = css.replace("\n.footer-col { padding-top: 12px; }\n", "")

# Add a specific padding to align the titles with the visual center of the logo
# The logo is 52px high. The title is 11px high.
# (52 - 11) / 2 = 20.5px.
# Let's add padding-top: 12px to .footer-col-title so it sits nicely aligned with the logo.
css = re.sub(
    r"\.footer-col-title\{font-size:11px;font-weight:800;letter-spacing:\.15em;text-transform:uppercase;color:var\(--sand,#e8c87a\);margin:0 0 18px;opacity:\.85;display:block\}",
    r".footer-col-title{font-size:11px;font-weight:800;letter-spacing:.15em;text-transform:uppercase;color:var(--sand,#e8c87a);margin:0 0 18px;padding-top:12px;opacity:.85;display:block}",
    css
)

with open(css_path, "w") as f:
    f.write(css)

print("Footer CSS patched 2.")
