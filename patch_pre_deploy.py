import os

path = "/Users/simonazoulay/SurfCampSenegal/scripts/pre_deploy_check.py"
with open(path, "r") as f:
    content = f.read()

# Update CRITICAL_STRINGS for surf-house
content = content.replace('"surf-house": ["main-hero", "gallery-masonry", "footer"],', '"surf-house": ["sh2-hero", "gallery-masonry", "footer"],')

with open(path, "w") as f:
    f.write(content)

print("pre_deploy_check.py updated.")
