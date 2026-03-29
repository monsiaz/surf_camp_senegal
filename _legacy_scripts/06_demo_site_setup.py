"""
Step 6 – Setup DEMO site fully:
  - Install Blog app
  - Update site properties (EN, correct info)
  - Set up multilingual (FR, ES, IT, DE)
  - Inject custom CSS for DA improvements
  - Create header navigation (with Blog link)
  - Create blog categories
"""
import json, requests, os

WIX_KEY    = open("/Users/simonazoulay/SurfCampSenegal/clesapi.txt").read().strip()
ACCOUNT_ID = "c2467ffa-759d-4bb8-bd93-1544d1f6f10d"
SITE_DEMO  = "e8cc06ab-3597-48e0-b1fb-f80eb45d6746"
SITE_MAIN  = "4dd6806d-ff9c-4e35-bd98-1dc27ac71a7a"
BASE       = "https://www.wixapis.com"

def H(site_id):
    return {
        "Authorization": WIX_KEY,
        "Content-Type":  "application/json",
        "wix-site-id":   site_id,
    }

def call(method, path, site_id, body=None, params=None):
    r = requests.request(method, BASE+path, headers=H(site_id), json=body, params=params, timeout=20)
    try:    return r.status_code, r.json()
    except: return r.status_code, {"raw": r.text[:600]}

results = {}

# ═══════════════════════════════════════════════════════════════════════════════
# 1. Update site properties on DEMO
# ═══════════════════════════════════════════════════════════════════════════════
print("=== 1. Update DEMO site properties ===")

# First get current properties to know the exact fields
sc, d = call("GET", "/site-properties/v4/properties", SITE_DEMO)
print(f"  GET properties: {sc}")
print(f"  Current: lang={d.get('properties',d).get('language')} name={d.get('properties',d).get('siteDisplayName')}")

# Update: language → en, fix display name & info
# fieldMask is required to specify which fields to update
update_attempts = [
    # Try v4 with fieldMask
    {"path": "/site-properties/v4/properties", "body": {
        "properties": {
            "language": "en",
            "locale": {"languageCode": "en", "country": "SN"},
            "siteDisplayName": "Ngor Surfcamp Teranga",
            "email": "info@surfcampsenegal.com",
            "phone": "+221 78 925 70 25",
        },
        "fieldMask": {"paths": ["language", "locale", "siteDisplayName", "email", "phone"]}
    }},
    # Try with field_set_mask
    {"path": "/site-properties/v4/properties", "body": {
        "properties": {"language": "en", "siteDisplayName": "Ngor Surfcamp Teranga"},
        "field_set_mask": "language,siteDisplayName"
    }},
    # Try simple PUT
    {"path": "/site-properties/v4/properties", "body": {
        "language": "en",
        "siteDisplayName": "Ngor Surfcamp Teranga",
    }},
]

for attempt in update_attempts:
    sc, d = call("PATCH", attempt["path"], SITE_DEMO, attempt["body"])
    print(f"  PATCH {attempt['path']}: {sc} | {json.dumps(d)[:200]}")
    if sc == 200:
        results["site_properties_updated"] = True
        print("  ✅ Site properties updated!")
        break

# ═══════════════════════════════════════════════════════════════════════════════
# 2. Try to install Blog app on DEMO
# ═══════════════════════════════════════════════════════════════════════════════
print("\n=== 2. Install Blog app on DEMO ===")
BLOG_APP_ID = "14bcded7-0066-7c35-14d7-466cb3f09103"

app_install_attempts = [
    ("POST", f"/apps/v1/apps/{BLOG_APP_ID}/provision",  {}),
    ("POST", f"/apps/v2/apps/{BLOG_APP_ID}/install",    {}),
    ("POST", "/apps/v1/installed-apps",                  {"appId": BLOG_APP_ID}),
    ("POST", "/app-market/v1/apps/install",              {"appId": BLOG_APP_ID}),
    ("POST", "/app-management/v2/installed-apps",        {"appId": BLOG_APP_ID}),
    ("PUT",  f"/apps/v1/apps/{BLOG_APP_ID}",            {"installed": True}),
]

blog_installed = False
for method, path, body in app_install_attempts:
    sc, d = call(method, path, SITE_DEMO, body)
    if sc not in [404, 405]:
        print(f"  {method} {path}: {sc} | {json.dumps(d)[:300]}")
    if sc in [200, 201]:
        blog_installed = True
        print("  ✅ Blog app installed!")
        break

# ═══════════════════════════════════════════════════════════════════════════════
# 3. Set up Multilingual on DEMO
# ═══════════════════════════════════════════════════════════════════════════════
print("\n=== 3. Set up Multilingual on DEMO ===")

TARGET_LANGUAGES = [
    {"languageCode": "fr", "locale": "fr-FR", "isPrimary": False, "status": "Active"},
    {"languageCode": "es", "locale": "es-ES", "isPrimary": False, "status": "Active"},
    {"languageCode": "it", "locale": "it-IT", "isPrimary": False, "status": "Active"},
    {"languageCode": "de", "locale": "de-DE", "isPrimary": False, "status": "Active"},
]

multilingual_attempts = [
    ("POST", "/multilingual/v2/site-languages", {"language": {
        "languageCode": "fr", "locale": {"country": "FR", "languageCode": "fr"},
        "isPrimary": False, "status": "Active"
    }}),
    ("GET",  "/multilingual/v2/site-languages", None),
    ("POST", "/multilingual/v1/site-languages", {"siteLanguage": {
        "languageCode": "fr", "locale": "fr-FR", "isPrimary": False
    }}),
    ("GET",  "/multilingual/v1/site-languages", None),
]

for method, path, body in multilingual_attempts:
    sc, d = call(method, path, SITE_DEMO, body)
    if sc not in [404, 405]:
        print(f"  {method} {path}: {sc} | {json.dumps(d)[:300]}")
        if sc in [200, 201]:
            print("  ✅ Multilingual response received!")

# Try adding each language
for lang_data in TARGET_LANGUAGES:
    bodies_to_try = [
        {"language": {
            "languageCode": lang_data["languageCode"],
            "locale": {"country": lang_data["locale"].split("-")[1], "languageCode": lang_data["languageCode"]},
            "isPrimary": False, "status": "Active"
        }},
        {"siteLanguage": {"languageCode": lang_data["languageCode"], "isPrimary": False}},
    ]
    for body in bodies_to_try:
        for path in ["/multilingual/v2/site-languages", "/multilingual/v1/site-languages"]:
            sc, d = call("POST", path, SITE_DEMO, body)
            if sc not in [404, 405, 400]:
                print(f"  Add {lang_data['languageCode']}: {sc} | {json.dumps(d)[:200]}")
                if sc in [200, 201]:
                    print(f"  ✅ Language {lang_data['languageCode']} added!")

# ═══════════════════════════════════════════════════════════════════════════════
# 4. Custom CSS injection for DA improvements
# ═══════════════════════════════════════════════════════════════════════════════
print("\n=== 4. Custom CSS injection (DA improvements) ===")

IMPROVED_CSS = """
/* ── Ngor Surfcamp Teranga – Improved DA ──────────────────────────────────
   Typography: Sharper, premium feel
   Colors: Deeper ocean blues + warm sand tones
   Spacing: More breathing room
   Mobile: Better responsive behavior
────────────────────────────────────────────────────────────────────────── */

/* Google Fonts: Raleway (headings) + Inter (body) */
@import url('https://fonts.googleapis.com/css2?family=Raleway:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600&display=swap');

/* ── Global typography ── */
body, p, span, div {
  font-family: 'Inter', sans-serif !important;
  letter-spacing: 0.01em;
  line-height: 1.7;
}

h1, h2, h3, h4, h5, h6,
[data-hook="header"],
[class*="heading"],
[class*="title"] {
  font-family: 'Raleway', sans-serif !important;
  letter-spacing: -0.02em;
  line-height: 1.2;
}

/* ── Color palette ── */
:root {
  --color-ocean:    #0a2540;
  --color-wave:     #1565c0;
  --color-surf:     #29b6f6;
  --color-sand:     #f5e6c8;
  --color-sunset:   #ff6b35;
  --color-white:    #ffffff;
  --color-text:     #1a1a2e;
  --color-muted:    #6b7280;
  --radius-card:    12px;
  --shadow-card:    0 4px 24px rgba(10,37,64,0.10);
  --transition:     all 0.3s cubic-bezier(0.4,0,0.2,1);
}

/* ── Buttons – more premium ── */
button, [role="button"], a[class*="btn"], [class*="button"],
[class*="StylableButton"] {
  border-radius: 50px !important;
  font-family: 'Raleway', sans-serif !important;
  font-weight: 600 !important;
  letter-spacing: 0.05em !important;
  text-transform: uppercase !important;
  font-size: 13px !important;
  transition: var(--transition) !important;
  padding: 14px 32px !important;
}

/* ── Cards / sections ── */
[class*="card"], [class*="Card"],
[class*="container"], [class*="section"] {
  border-radius: var(--radius-card) !important;
}

/* ── Hero section ── */
[data-mesh-id*="SITE_HEADER"],
[class*="header"], [class*="Header"] {
  backdrop-filter: blur(8px) !important;
}

/* ── Better image aspect ratios ── */
[class*="media"], [class*="Media"],
img[class*="image"], img[class*="Image"] {
  object-fit: cover !important;
  border-radius: 8px;
}

/* ── Smooth scroll ── */
html { scroll-behavior: smooth; }

/* ── Better mobile header ── */
@media (max-width: 768px) {
  h1, [class*="heading1"] { font-size: clamp(28px, 7vw, 48px) !important; }
  h2, [class*="heading2"] { font-size: clamp(22px, 5vw, 36px) !important; }
}

/* ── Blog improvements ── */
[class*="blog"], [class*="Blog"],
[class*="post"], [class*="Post"] {
  font-family: 'Inter', sans-serif !important;
}
[class*="blog"] h1, [class*="blog"] h2,
[class*="post"] h1, [class*="post"] h2 {
  font-family: 'Raleway', sans-serif !important;
}
"""

custom_code_attempts = [
    ("POST", "/custom-code/v1/site-custom-code", {
        "customCodeEntry": {
            "type": "INLINE",
            "placement": "BODY_START",
            "code": f"<style>{IMPROVED_CSS}</style>",
            "position": {"placementType": "BODY_START"}
        }
    }),
    ("POST", "/site-plugins/v1/custom-code", {
        "code": f"<style>{IMPROVED_CSS}</style>",
        "placement": "HEAD",
        "position": 1
    }),
    ("POST", "/v1/site-custom-code", {
        "customCode": f"<style>{IMPROVED_CSS}</style>",
        "placement": "HEAD"
    }),
    ("POST", "/custom-code/v1/custom-code", {
        "code": f"<style>{IMPROVED_CSS}</style>",
        "placement": "BODY_START"
    }),
    ("PUT", "/custom-code/v1/site-custom-code/demo-da", {
        "customCodeEntry": {
            "id": "ngor-da-improvements",
            "code": f"<style>{IMPROVED_CSS}</style>",
            "placement": "BODY_START",
            "type": "INLINE"
        }
    }),
]

css_injected = False
for method, path, body in custom_code_attempts:
    sc, d = call(method, path, SITE_DEMO, body)
    if sc not in [404, 405]:
        print(f"  {method} {path}: {sc} | {json.dumps(d)[:300]}")
        if sc in [200, 201]:
            css_injected = True
            print("  ✅ Custom CSS injected!")
            break

if not css_injected:
    print("  ⚠️  Custom CSS injection via API not available")
    print("  → Saving CSS to file for manual Wix Velo injection")
    with open("/Users/simonazoulay/SurfCampSenegal/content/custom_css_da.css", "w") as f:
        f.write(IMPROVED_CSS)
    print("  → Saved: content/custom_css_da.css")

# ═══════════════════════════════════════════════════════════════════════════════
# 5. Header / Navigation on DEMO
# ═══════════════════════════════════════════════════════════════════════════════
print("\n=== 5. Header navigation ===")

# Try to get/create menus
menu_attempts = [
    ("GET",  "/menus/v1/menus",        None),
    ("GET",  "/menus/v2/menus",        None),
    ("POST", "/menus/v1/menus",        {
        "menu": {
            "name": "Main Navigation",
            "items": [
                {"label": "Home",           "link": {"url": "/",                "target": "_self"}},
                {"label": "Surf House",     "link": {"url": "/ngor-surf-house", "target": "_self"}},
                {"label": "Island",         "link": {"url": "/ngor-island",     "target": "_self"}},
                {"label": "Surfing",        "link": {"url": "/surfing",         "target": "_self"}},
                {"label": "Blog",           "link": {"url": "/blog",            "target": "_self"}},
                {"label": "Gallery",        "link": {"url": "/gallery",         "target": "_self"}},
                {"label": "Book Now",       "link": {"url": "/book-surf-trip",  "target": "_self"}},
            ]
        }
    }),
    ("POST", "/menus/v2/menus",        {
        "menu": {"name": "Main Menu", "items": [{"label": "Blog", "link": {"url": "/blog"}}]}
    }),
]

for method, path, body in menu_attempts:
    sc, d = call(method, path, SITE_DEMO, body)
    if sc not in [404, 405]:
        print(f"  {method} {path}: {sc} | {json.dumps(d)[:300]}")
        if sc in [200, 201]:
            print("  ✅ Menu created/fetched!")
            results["menu"] = d

# ═══════════════════════════════════════════════════════════════════════════════
# 6. Blog categories on DEMO (if blog gets installed)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n=== 6. Test blog write on DEMO (without account-id) ===")

# Test blog on DEMO without account-id (same as main site pattern)
H_DEMO_NO_ACC = {"Authorization": WIX_KEY, "Content-Type": "application/json", "wix-site-id": SITE_DEMO}

sc_b, d_b = requests.get(BASE+"/blog/v3/posts", headers=H_DEMO_NO_ACC, timeout=15).json() if False else (None, None)
r = requests.get(BASE+"/blog/v3/categories", headers=H_DEMO_NO_ACC, timeout=15)
print(f"  Blog categories (no account-id): {r.status_code} | {r.text[:200]}")

r = requests.get(BASE+"/blog/v3/posts", headers=H_DEMO_NO_ACC, timeout=15)
print(f"  Blog posts (no account-id): {r.status_code} | {r.text[:200]}")

# Try the MAIN site to see if we can write (create categories) there
print("\n=== 7. Test blog WRITE on MAIN site ===")
H_MAIN = {"Authorization": WIX_KEY, "Content-Type": "application/json", "wix-site-id": SITE_MAIN}

# Can we create a draft post on main?
test_post = {
    "post": {
        "title": "[DEMO] Test draft post – please ignore",
        "status": "DRAFT",
        "membersOnly": False,
        "language": "en",
        "excerpt": "This is a test draft post created by the demo setup script.",
        "seoData": {"tags": [{"type": "TITLE", "custom": False, "disabled": False}]}
    }
}
r = requests.post(BASE+"/blog/v3/posts", headers=H_MAIN, json=test_post, timeout=15)
print(f"  Create DRAFT post on MAIN: {r.status_code} | {r.text[:300]}")
if r.status_code in [200, 201]:
    try:
        post_id = r.json().get("post",{}).get("id","")
        print(f"  ✅ Draft post created! id={post_id}")
        results["can_write_blog_main"] = True
        results["test_post_id"] = post_id
        # Delete the test post immediately
        r_del = requests.delete(BASE+f"/blog/v3/posts/{post_id}", headers=H_MAIN, timeout=15)
        print(f"  Test post deleted: {r_del.status_code}")
    except Exception as e:
        print(f"  Parse error: {e}")

# Save results
os.makedirs("/Users/simonazoulay/SurfCampSenegal/output", exist_ok=True)
with open("/Users/simonazoulay/SurfCampSenegal/output/demo_setup_results.json","w") as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved → output/demo_setup_results.json")
