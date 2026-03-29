"""Push DE articles + final status check. DEMO ONLY."""
import json, os, re, requests, threading
from concurrent.futures import ThreadPoolExecutor, as_completed

WIX_KEY      = open("/Users/simonazoulay/SurfCampSenegal/clesapi.txt").read().strip()
BASE         = "https://www.wixapis.com"
SITE_DEMO    = "e8cc06ab-3597-48e0-b1fb-f80eb45d6746"
MEMBER_ID    = "c2467ffa-759d-4bb8-bd93-1544d1f6f10d"
ARTICLES_DIR = "/Users/simonazoulay/SurfCampSenegal/content/articles"
OUTPUT_DIR   = "/Users/simonazoulay/SurfCampSenegal/output"

H       = {"Authorization": WIX_KEY, "Content-Type": "application/json", "wix-site-id": SITE_DEMO}
cat_ids = json.load(open(f"{OUTPUT_DIR}/demo_category_ids.json"))
pushed_file = f"{OUTPUT_DIR}/demo_pushed_posts.json"
pushed  = json.load(open(pushed_file)) if os.path.exists(pushed_file) else {}
lock    = threading.Lock()

def push(art, lang):
    slug  = art.get("slug", "")
    title = art.get("title", "")
    key   = f"{lang}_{slug}"
    if key in pushed or not slug or not title:
        return "skip"
    cat_id  = cat_ids.get(art.get("category", ""), "")
    content = art.get("content_markdown", "")
    excerpt = re.sub(r"[#*\[\]`]", "", content[:400]).strip()[:270].rsplit(" ", 1)[0] + "..."
    body = {"draftPost": {
        "title": title, "excerpt": excerpt, "memberId": MEMBER_ID,
        "language": lang, "commentingEnabled": True,
        "featured": art.get("type") == "hero",
        "categoryIds": [cat_id] if cat_id else [],
        "seoData": {"tags": [
            {"type": "TITLE",       "custom": True, "disabled": False, "children": title},
            {"type": "DESCRIPTION", "custom": True, "disabled": False,
             "children": art.get("meta_description", excerpt[:155])},
        ]},
    }}
    r = requests.post(BASE + "/blog/v3/draft-posts", headers=H, json=body, timeout=20)
    if r.status_code in [200, 201]:
        post_id = r.json().get("draftPost", {}).get("id", "")
        print(f"  ✅ [{lang}] {title[:55]}")
        with lock:
            pushed[key] = post_id
            with open(pushed_file, "w") as f:
                json.dump(pushed, f, indent=2)
        return post_id
    else:
        print(f"  ❌ [{lang}] {title[:40]}: {r.status_code} | {r.text[:150]}")
        return None

# ── Push all languages (in case any are missing) ──────────────────────────────
for lang in ["en", "fr", "es", "it", "de"]:
    lang_dir = f"{ARTICLES_DIR}/{lang}"
    if not os.path.exists(lang_dir):
        continue
    arts = []
    for fname in sorted(os.listdir(lang_dir)):
        if fname.endswith(".json") and not fname.startswith("_"):
            a = json.load(open(f"{lang_dir}/{fname}"))
            if a.get("slug") and a.get("title"):
                arts.append(a)

    todo = [a for a in arts if f"{lang}_{a['slug']}" not in pushed]
    print(f"\n{lang.upper()}: {len(arts)} total | {len(arts)-len(todo)} already pushed | {len(todo)} to push")

    if not todo:
        continue

    with ThreadPoolExecutor(max_workers=10) as ex:
        futs = [ex.submit(push, a, lang) for a in todo]
        for f in as_completed(futs):
            pass

# ── Final status ──────────────────────────────────────────────────────────────
r = requests.post(BASE + "/blog/v3/draft-posts/query", headers=H,
    json={"query": {"paging": {"limit": 200}}}, timeout=20)
all_posts = r.json().get("draftPosts", [])

lang_counts = {}
for p in all_posts:
    l = p.get("language", "?")
    lang_counts[l] = lang_counts.get(l, 0) + 1

print("\n" + "="*60)
print("DEMO SITE — BLOG STATUS (all posts are DRAFT)")
print("="*60)
total = 0
for l in ["en", "fr", "es", "it", "de"]:
    c   = lang_counts.get(l, 0)
    bar = "✅" if c >= 30 else "⚠️ "
    print(f"  {bar} {l.upper()}: {c}/30 articles")
    total += c
print(f"\n  TOTAL draft posts: {total}/150")
print(f"  Categories: 3")
print(f"\n  → Demo dashboard: https://manage.wix.com/editor/{SITE_DEMO}")
print(f"  → Live site NOT touched: https://www.surfcampsenegal.com")
