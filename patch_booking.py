import re

py_file = "/Users/simonazoulay/SurfCampSenegal/build.py"
with open(py_file, "r") as f:
    content = f.read()

# Replace the main-hero section in build_booking
old_hero = """<main>
  <header class="main-hero" style="background-image:url('/assets/images/gallery/CAML6902_d756823d.webp')" role="banner">
    <div class="main-hero-inner">
      <div class="main-hero-eyebrow">
        <span class="main-hero-dot"></span>
        <span>Ngor Surfcamp Teranga</span>
      </div>
      <h1 class="main-hero-h1">{g("h1")}</h1>
      <p class="main-hero-tagline">{g("sub")}</p>
      <div class="main-hero-actions" style="flex-direction:column;gap:24px;align-items:center">
        <div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap">{trust_badges}</div>
        <a href="#booking-section" class="btn btn-outline-white btn-lg">&#8964;</a>
      </div>
    </div>
  </header>"""

new_hero = """<main>
  <header class="booking-header" role="banner">
    <div class="container">
      <div class="booking-header-inner">
        <div class="booking-header-eyebrow">
          <span class="booking-header-dot"></span>
          <span>Ngor Surfcamp Teranga</span>
        </div>
        <h1 class="booking-header-h1">{g("h1")}</h1>
        <p class="booking-header-tagline">{g("sub")}</p>
        <div class="booking-header-trust">
          {trust_badges}
        </div>
      </div>
    </div>
  </header>"""

content = content.replace(old_hero, new_hero)

with open(py_file, "w") as f:
    f.write(content)

print("build.py patched for booking header.")
