import re

# 1. Update build.py
py_file = "/Users/simonazoulay/SurfCampSenegal/build.py"
with open(py_file, "r") as f:
    content = f.read()

content = content.replace('wave_bottom(prev_bg, "#000")', 'wave_bottom(prev_bg, "#06111e")')

with open(py_file, "w") as f:
    f.write(content)

# 2. Update CSS
css_file = "/Users/simonazoulay/SurfCampSenegal/cloudflare-demo/assets/css/ngor-surfcamp.css"
with open(css_file, "r") as f:
    css = f.read()

# Update .footer-quotes
css = re.sub(
    r"\.footer-quotes\{background:#000;border-top:1px solid rgba\(255,255,255,0\.1\);border-bottom:1px solid rgba\(255,255,255,0\.07\);",
    r".footer-quotes{background:#06111e;border-top:none;border-bottom:none;",
    css
)

# Update footer border-top
css = re.sub(
    r"footer\{background:linear-gradient\(160deg,#06111e,#08192c\);color:#fff;padding:80px 0 36px;border-top:1px solid rgba\(255,255,255,0\.05\)\}",
    r"footer{background:linear-gradient(160deg,#06111e,#08192c);color:#fff;padding:80px 0 36px;border-top:none}",
    css
)

with open(css_file, "w") as f:
    f.write(css)

print("Footer quotes patched.")
