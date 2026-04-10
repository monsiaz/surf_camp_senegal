import os

path = "/Users/simonazoulay/SurfCampSenegal/scripts/pre_deploy_check.py"
with open(path, "r") as f:
    content = f.read()

# Update CRITICAL_STRINGS for booking
content = content.replace('"booking":    ["main-hero", "booking-form", "footer"],', '"booking":    ["booking-header", "booking-form", "footer"],')

with open(path, "w") as f:
    f.write(content)

print("pre_deploy_check.py updated for booking.")
