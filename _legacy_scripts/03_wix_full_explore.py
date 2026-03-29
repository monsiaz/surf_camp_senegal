"""
Step 3 – Full exploration of both Wix sites (main + demo)
"""
import json, requests, os

WIX_KEY      = open("/Users/simonazoulay/SurfCampSenegal/clesapi.txt").read().strip()
ACCOUNT_ID   = "c2467ffa-759d-4bb8-bd93-1544d1f6f10d"
SITE_MAIN    = "4dd6806d-ff9c-4e35-bd98-1dc27ac71a7a"   # published – read only
SITE_DEMO    = "e8cc06ab-3597-48e0-b1fb-f80eb45d6746"   # unpublished – we write here
BASE         = "https://www.wixapis.com"
OUT          = "/Users/simonazoulay/SurfCampSenegal/output/wix_full.json"

def hdrs(site_id):
    return {
        "Authorization": WIX_KEY,
        "Content-Type":  "application/json",
        "wix-site-id":   site_id,
        "wix-account-id": ACCOUNT_ID,
    }

def get(path, site_id, params=None):
    r = requests.get(BASE + path, headers=hdrs(site_id), params=params, timeout=20)
    try:    return r.status_code, r.json()
    except: return r.status_code, {"raw": r.text[:1000]}

def post(path, site_id, body):
    r = requests.post(BASE + path, headers=hdrs(site_id), json=body, timeout=20)
    try:    return r.status_code, r.json()
    except: return r.status_code, {"raw": r.text[:1000]}

result = {"main": {}, "demo": {}}

for label, site_id in [("main", SITE_MAIN), ("demo", SITE_DEMO)]:
    print(f"\n{'='*60}")
    print(f"  SITE: {label.upper()} ({site_id})")
    print('='*60)

    # Site properties
    sc, d = get("/site-properties/v4/properties", site_id)
    print(f"\n[site-properties] {sc}")
    if sc == 200:
        props = d.get("properties", d)
        print(json.dumps(props, indent=2)[:600])
        result[label]["properties"] = props

    # Pages
    sc, d = post("/pages/v2/pages/query", site_id, {"query": {"paging": {"limit": 50}}})
    print(f"\n[pages] {sc}")
    if sc == 200:
        pages = d.get("pages", [])
        print(f"  {len(pages)} pages")
        for p in pages:
            title = p.get("title","")
            slug  = p.get("slug","")
            page_id = p.get("id","")
            print(f"    [{page_id[:8]}] /{slug}  → {title}")
        result[label]["pages"] = pages
    else:
        print(json.dumps(d)[:400])

    # Multilingual
    sc, d = get("/multilingual/v2/site-languages", site_id)
    print(f"\n[multilingual] {sc}")
    if sc == 200:
        print(json.dumps(d, indent=2)[:500])
        result[label]["multilingual"] = d
    else:
        print(json.dumps(d)[:300])

    # SEO - per page
    sc, d = post("/seo-schema/v1/schemas/query", site_id, {"query": {}})
    print(f"\n[seo-schemas] {sc}: {json.dumps(d)[:300]}")

    # Blog posts
    sc, d = get("/blog/v3/posts", site_id, {"paging.limit": 10})
    print(f"\n[blog posts] {sc}")
    if sc == 200:
        posts = d.get("posts", [])
        print(f"  {len(posts)} posts")
        for p in posts[:5]:
            print(f"    {p.get('title')} | slug={p.get('slug')}")
        result[label]["blog_posts"] = posts
    else:
        print(json.dumps(d)[:300])

    # Blog categories
    sc, d = get("/blog/v3/categories", site_id, {"paging.limit": 20})
    print(f"\n[blog categories] {sc}")
    if sc == 200:
        cats = d.get("categories", [])
        print(f"  {len(cats)} categories: {[c.get('label') for c in cats]}")
        result[label]["blog_categories"] = cats
    else:
        print(json.dumps(d)[:300])

    # Menus / Navigation
    sc, d = get("/menus/v1/menus", site_id)
    print(f"\n[menus] {sc}")
    if sc == 200:
        menus = d.get("menus", [])
        print(f"  {len(menus)} menus")
        for m in menus[:3]:
            print(f"    {m.get('name')} | items: {len(m.get('items',[]))}")
        result[label]["menus"] = menus
    else:
        print(json.dumps(d)[:300])

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w") as f:
    json.dump(result, f, indent=2, default=str)
print(f"\n\nSaved → {OUT}")
