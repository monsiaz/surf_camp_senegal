"""
Step 2 – Explore Wix API: list sites, pages, SEO settings
"""
import json, requests

WIX_KEY = open("/Users/simonazoulay/SurfCampSenegal/clesapi.txt").read().strip()
HEADERS  = {"Authorization": WIX_KEY, "Content-Type": "application/json"}
BASE     = "https://www.wixapis.com"
OUT      = "/Users/simonazoulay/SurfCampSenegal/output/wix_structure.json"

def call(method, path, body=None):
    url = BASE + path
    r = requests.request(method, url, headers=HEADERS, json=body, timeout=30)
    try:
        return r.status_code, r.json()
    except Exception:
        return r.status_code, {"raw": r.text[:2000]}

result = {}

# ── List all sites on the account ─────────────────────────────────────────────
print("=== Site List ===")
sc, data = call("GET", "/site-list/v2/sites")
print(f"  Status: {sc}")
sites = data.get("sites", [])
print(f"  Sites found: {len(sites)}")
for s in sites:
    print(f"    id={s.get('id')}  name={s.get('displayName')}  url={s.get('viewUrl')}")
result["sites"] = sites

# ── Pick the surf camp site ────────────────────────────────────────────────────
surf_site = None
for s in sites:
    url = s.get("viewUrl","") + s.get("displayName","")
    if "surf" in url.lower() or "senegal" in url.lower() or "ngor" in url.lower() or "teranga" in url.lower():
        surf_site = s
        break
if not surf_site and sites:
    surf_site = sites[0]

if surf_site:
    site_id = surf_site.get("id","")
    print(f"\nUsing site: {surf_site.get('displayName')} (id={site_id})")
    SITE_HEADERS = {**HEADERS, "wix-site-id": site_id}

    # ── Pages ────────────────────────────────────────────────────────────────
    print("\n=== Pages ===")
    sc2, pages_data = call("GET", f"/pages/v2/pages")
    # pages API needs site header
    r2 = requests.get(BASE + "/pages/v2/pages", headers=SITE_HEADERS, timeout=30)
    pages_data = r2.json()
    print(f"  Status: {r2.status_code}")
    pages = pages_data.get("pages", [])
    print(f"  Pages found: {len(pages)}")
    for p in pages:
        print(f"    id={p.get('id')}  title={p.get('title')}  url={p.get('url')}  slug={p.get('slug')}")
    result["pages"] = pages

    # ── SEO / Meta ───────────────────────────────────────────────────────────
    print("\n=== Site SEO ===")
    r3 = requests.get(BASE + "/site-properties/v4/properties", headers=SITE_HEADERS, timeout=30)
    print(f"  Status: {r3.status_code}")
    try:
        seo = r3.json()
        result["site_properties"] = seo
        print(json.dumps(seo, indent=2)[:800])
    except Exception:
        print(r3.text[:500])

    # ── Languages / Multilingual ─────────────────────────────────────────────
    print("\n=== Multilingual ===")
    r4 = requests.get(BASE + "/multilingual/v1/site-languages", headers=SITE_HEADERS, timeout=30)
    print(f"  Status: {r4.status_code}")
    try:
        ml = r4.json()
        result["multilingual"] = ml
        print(json.dumps(ml, indent=2)[:600])
    except Exception:
        print(r4.text[:500])

    # ── Blog posts ───────────────────────────────────────────────────────────
    print("\n=== Blog Posts ===")
    r5 = requests.get(BASE + "/blog/v3/posts?paging.limit=5", headers=SITE_HEADERS, timeout=30)
    print(f"  Status: {r5.status_code}")
    try:
        blog = r5.json()
        result["blog"] = blog
        posts = blog.get("posts", [])
        print(f"  Posts: {len(posts)}")
        for p in posts[:5]:
            print(f"    {p.get('title')} | {p.get('slug')}")
    except Exception:
        print(r5.text[:500])

    # ── Blog categories ──────────────────────────────────────────────────────
    print("\n=== Blog Categories ===")
    r6 = requests.get(BASE + "/blog/v3/categories?paging.limit=20", headers=SITE_HEADERS, timeout=30)
    print(f"  Status: {r6.status_code}")
    try:
        cats = r6.json()
        result["blog_categories"] = cats
        print(json.dumps(cats, indent=2)[:600])
    except Exception:
        print(r6.text[:500])

    result["active_site_id"] = site_id

import os
os.makedirs("/Users/simonazoulay/SurfCampSenegal/output", exist_ok=True)
with open(OUT, "w") as f:
    json.dump(result, f, indent=2, default=str)
print(f"\nSaved → {OUT}")
