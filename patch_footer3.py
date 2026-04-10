import re

css_path = "/Users/simonazoulay/SurfCampSenegal/cloudflare-demo/assets/css/ngor-surfcamp.css"
with open(css_path, "r") as f:
    css = f.read()

# Make footer-col-follow a flex container to push the FSS badge to the bottom
if ".footer-col-follow {" not in css:
    css += """
.footer-col-follow {
  display: flex;
  flex-direction: column;
  height: 100%;
}
.footer-col-follow .footer-fss-in-col {
  margin-top: auto;
  margin-bottom: 0;
}
"""

with open(css_path, "w") as f:
    f.write(css)

print("Footer CSS patched 3.")
