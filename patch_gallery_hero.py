import os

py_file = "/Users/simonazoulay/SurfCampSenegal/build.py"
with open(py_file, "r") as f:
    content = f.read()

# Change the hero variable
content = content.replace('hero = IMGS["gallery"][0]', 'hero = "/assets/images/gallery/gallery_hero.webp"')

# Update the style to include background-position
content = content.replace(
    '<header class="main-hero" style="background-image:url(\'{hero}\')" role="banner">',
    '<header class="main-hero" style="background-image:url(\'{hero}\'); background-position: center 45%;" role="banner">'
)

with open(py_file, "w") as f:
    f.write(content)

print("build.py patched for gallery hero.")
