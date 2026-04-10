import re

css_path = "/Users/simonazoulay/SurfCampSenegal/cloudflare-demo/assets/css/ngor-surfcamp.css"
with open(css_path, "r") as f:
    css = f.read()

# Remove the previously appended block
css = css.replace("""
.footer-col-follow {
  display: flex;
  flex-direction: column;
  height: 100%;
}
.footer-col-follow .footer-fss-in-col {
  margin-top: auto;
  margin-bottom: 0;
}
""", "")

# Add it with media query
css += """
@media (min-width: 661px) {
  .footer-col-follow {
    display: flex;
    flex-direction: column;
    height: 100%;
  }
  .footer-col-follow .footer-fss-in-col {
    margin-top: auto;
    margin-bottom: 0;
  }
}
"""

with open(css_path, "w") as f:
    f.write(css)

print("Footer CSS patched 4.")
