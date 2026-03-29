"""
Step 4 – Try all available Wix APIs on the DEMO site + scrape main site content
"""
import json, requests, os

WIX_KEY    = open("/Users/simonazoulay/SurfCampSenegal/clesapi.txt").read().strip()
ACCOUNT_ID = "c2467ffa-759d-4bb8-bd93-1544d1f6f10d"
SITE_DEMO  = "e8cc06ab-3597-48e0-b1fb-f80eb45d6746"
BASE       = "https://www.wixapis.com"

H = {
    "Authorization": WIX_KEY,
    "Content-Type":  "application/json",
    "wix-site-id":   SITE_DEMO,
    "wix-account-id": ACCOUNT_ID,
}

def call(method, path, body=None, params=None):
    r = requests.request(method, BASE+path, headers=H, json=body, params=params, timeout=20)
    try:    return r.status_code, r.json()
    except: return r.status_code, {"raw": r.text[:600]}

result = {}

# ── 1. Update site language to EN (fix wrong 'fr' default) ───────────────────
print("=== 1. Update site language to EN ===")
sc, d = call("PATCH", "/site-properties/v4/properties", {
    "properties": {
        "language": "en",
        "locale": {"languageCode": "en", "country": "SN"},
        "siteDisplayName": "Ngor Surfcamp Teranga",
        "email": "info@surfcampsenegal.com",
    }
})
print(f"  PATCH site-properties: {sc}")
print(f"  {json.dumps(d)[:400]}")

# ── 2. Try various page-related endpoints ────────────────────────────────────
print("\n=== 2. Page endpoints ===")
for method, path, body in [
    ("GET",  "/pages/v1/pages",                None),
    ("POST", "/pages/v1/pages/query",          {"query": {}}),
    ("GET",  "/v2/pages",                      None),
    ("POST", "/pages/v2/pages/query",          {"query": {}}),
    ("GET",  "/dynamic-pages/v1/pages",        None),
    ("GET",  "/page-management/v1/pages",      None),
]:
    sc, d = call(method, path, body)
    if sc == 200:
        pages = d.get("pages", d.get("items", []))
        print(f"  ✅ {method} {path} → {sc} | {len(pages)} pages")
        for p in pages[:3]:
            print(f"       {p.get('title','')} | {p.get('slug','')}")
        result["pages"] = pages
    elif sc not in [404, 400]:
        print(f"  ⚠️  {method} {path} → {sc} | {json.dumps(d)[:150]}")

# ── 3. Multilingual endpoints ────────────────────────────────────────────────
print("\n=== 3. Multilingual endpoints ===")
for method, path, body in [
    ("GET",  "/multilingual/v1/site-languages",   None),
    ("GET",  "/multilingual/v2/site-languages",   None),
    ("POST", "/multilingual/v1/site-languages",   None),
]:
    sc, d = call(method, path, body)
    if sc not in [404]:
        print(f"  {method} {path} → {sc} | {json.dumps(d)[:300]}")

# ── 4. SEO endpoints ─────────────────────────────────────────────────────────
print("\n=== 4. SEO endpoints ===")
for method, path, body in [
    ("GET",  "/seo/v1/redirects",                 None),
    ("GET",  "/seo-schema/v1/schemas",             None),
    ("POST", "/seo-schema/v1/schemas/query",       {"query": {}}),
    ("GET",  "/seo/v2/settings",                   None),
]:
    sc, d = call(method, path, body)
    if sc not in [404, 400]:
        print(f"  {method} {path} → {sc} | {json.dumps(d)[:300]}")

# ── 5. Blog endpoints ────────────────────────────────────────────────────────
print("\n=== 5. Blog endpoints ===")
for method, path, body, params in [
    ("GET",  "/blog/v3/posts",            None, {"paging.limit": 3}),
    ("GET",  "/blog/v3/categories",       None, {"paging.limit": 10}),
    ("GET",  "/blog/v3/tags",             None, {"paging.limit": 10}),
    ("POST", "/blog/v3/posts/query",      {"query": {}}, None),
    ("POST", "/blog/v3/categories/query", {"query": {}}, None),
]:
    sc, d = call(method, path, body, params)
    if sc not in [404]:
        print(f"  {method} {path} → {sc} | {json.dumps(d)[:300]}")

# ── 6. Menus / navigation ────────────────────────────────────────────────────
print("\n=== 6. Menus ===")
for path in ["/menus/v1/menus", "/navigation/v1/menus", "/header-footer/v1/menus"]:
    sc, d = call("GET", path)
    if sc not in [404]:
        print(f"  GET {path} → {sc} | {json.dumps(d)[:300]}")

# ── 7. App instance / installed apps ─────────────────────────────────────────
print("\n=== 7. Installed apps ===")
sc, d = call("GET", "/apps/v1/installed-apps")
print(f"  GET /apps/v1/installed-apps → {sc} | {json.dumps(d)[:400]}")
sc, d = call("GET", "/apps/v2/apps")
print(f"  GET /apps/v2/apps → {sc} | {json.dumps(d)[:400]}")

os.makedirs("/Users/simonazoulay/SurfCampSenegal/output", exist_ok=True)
with open("/Users/simonazoulay/SurfCampSenegal/output/wix_demo_explore.json","w") as f:
    json.dump(result, f, indent=2, default=str)
print("\nDone.")
