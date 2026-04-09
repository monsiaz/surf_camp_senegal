#!/usr/bin/env python3
"""
pre_deploy_check.py
===================
Quality-gate that runs before every Vercel deployment.
Exit 0 = all checks passed (or only warnings).
Exit 1 = at least one CRITICAL check failed → deploy blocked.

Usage:
    python3 scripts/pre_deploy_check.py            # full check
    python3 scripts/pre_deploy_check.py --fix      # also bump build version
"""

import os, sys, re, json, glob, hashlib, datetime, argparse
from pathlib import Path
from collections import defaultdict

# ── Config ────────────────────────────────────────────────────────────────────
ROOT      = Path(__file__).parent.parent
DEMO      = ROOT / "cloudflare-demo"
VERSION_F = ROOT / "version.json"
CHANGELOG = ROOT / "CHANGELOG.md"

LANGS = ["en","fr","es","it","de","nl","ar","pt","da"]

# Main build pipeline langs (pt/da are patched separately)
MAIN_LANGS = ["en","fr","es","it","de","nl","ar"]

# Key pages per lang (slug relative to lang prefix)
SLUG = {
    "en": {"surf-house":"surf-house","island":"island","surfing":"surfing",
           "gallery":"gallery","faq":"faq","booking":"booking","blog":"blog","home":""},
    "fr": {"surf-house":"surf-house","island":"ile","surfing":"surf",
           "gallery":"galerie","faq":"faq","booking":"reservation","blog":"blog","home":""},
    "es": {"surf-house":"surf-house","island":"isla","surfing":"surf",
           "gallery":"galeria","faq":"faq","booking":"reservar","blog":"blog","home":""},
    "it": {"surf-house":"surf-house","island":"isola","surfing":"surf",
           "gallery":"galleria","faq":"faq","booking":"prenota","blog":"blog","home":""},
    "de": {"surf-house":"surf-house","island":"insel","surfing":"surfen",
           "gallery":"galerie","faq":"faq","booking":"buchen","blog":"blog","home":""},
    "nl": {"surf-house":"surf-house","island":"eiland","surfing":"surfen",
           "gallery":"galerij","faq":"faq","booking":"boeken","blog":"blog","home":""},
    "ar": {"surf-house":"surf-house","island":"ngor-island","surfing":"surf",
           "gallery":"galerie","faq":"faq","booking":"reservation","blog":"blog","home":""},
    "pt": {"surf-house":"surf-house","island":"ilha","surfing":"surf",
           "gallery":"galeria","faq":"faq","booking":"reservar","blog":"blog","home":""},
    "da": {"surf-house":"surf-house","island":"oe","surfing":"surf",
           "gallery":"galleri","faq":"faq","booking":"book","blog":"blog","home":""},
}

CRITICAL_STRINGS = {
    # page_key → list of HTML strings that MUST appear
    # NOTE: class names verified against actual generated output
    "surf-house": ["main-hero", "gallery-masonry", "footer"],
    "island":     ["main-hero", "island-discover", "footer"],
    "surfing":    ["surf-feat-grid", "footer"],          # main-hero only on MAIN_LANGS
    "gallery":    ["gallery-masonry", "gal-tag", "ngor_gallery_filter", "footer"],
    "faq":        ["faq-layout", "footer"],
    "home":       ["class=\"hero\"", "footer"],           # home uses video hero, not main-hero
    "blog":       ["blog-grid", "footer"],
}

# CSS classes/patterns that must exist in the main CSS file
REQUIRED_CSS = [
    "main-hero", "footer-fss-badge", "gallery-masonry", "faq-item",
    "surf-feat-grid", "cat-filter-btn", "blog-grid", "island-discover-card",
    "gal-tag", "faq-layout",
]

# JS patterns that must appear in generated pages
REQUIRED_JS = [
    "ngor_gallery_filter",  # gallery pre-filter via sessionStorage
    "filterTo",             # gallery filter function
]

MIN_PAGES     = 450   # total index.html count
MIN_ARTICLES  = 20    # EN blog articles
MIN_CSS_BYTES = 50_000

# ── Helpers ────────────────────────────────────────────────────────────────────
PASS  = "\033[92m✓\033[0m"
FAIL  = "\033[91m✗\033[0m"
WARN  = "\033[93m⚠\033[0m"
INFO  = "\033[94mℹ\033[0m"

errors   = []
warnings = []

def ok(msg):    print(f"  {PASS} {msg}")
def fail(msg):  print(f"  {FAIL} {msg}"); errors.append(msg)
def warn(msg):  print(f"  {WARN} {msg}"); warnings.append(msg)
def info(msg):  print(f"  {INFO} {msg}")

def page_path(lang, page):
    slug = SLUG[lang][page]
    if lang == "en":
        return DEMO / slug / "index.html" if slug else DEMO / "index.html"
    return DEMO / lang / slug / "index.html" if slug else DEMO / lang / "index.html"

def read_html(path):
    try:
        return path.read_text(errors="replace")
    except Exception:
        return ""

# ── CHECK 1: Page existence ───────────────────────────────────────────────────
# Known structural gaps (redirect-only pages, not full content)
KNOWN_REDIRECT_GAPS = {"nl/island", "ar/island"}

# Known template gaps: PT/DA use older page template (generated via translation patch, not main builder)
KNOWN_TEMPLATE_GAPS = {"pt/surf-house", "da/surf-house", "pt/surfing", "da/surfing"}

def is_redirect_only(path):
    """Returns True if the page is just a <meta refresh> redirect stub (<5 KB)."""
    try:
        content = path.read_text(errors="replace")
        return 'http-equiv="refresh"' in content and len(content) < 10_000
    except Exception:
        return False

def check_page_coverage():
    print("\n📋 Page coverage (all languages)")
    missing = []
    redirect_gaps = []
    for page in SLUG["en"]:
        row = []
        for lang in LANGS:
            p = page_path(lang, page)
            if not p.exists():
                row.append("✗")
                missing.append(f"{lang}/{page}")
            elif is_redirect_only(p):
                key = f"{lang}/{page}"
                if key in KNOWN_REDIRECT_GAPS:
                    row.append("↷")  # known redirect gap
                    redirect_gaps.append(key)
                else:
                    row.append("↷")
                    missing.append(key)
            else:
                row.append("✓")
        status = PASS if all(c in ("✓","↷") for c in row) else FAIL
        print(f"  {status} {page:12s}  {'  '.join(row)}  ({' '.join(LANGS)})")
    for m in missing:
        if m not in KNOWN_REDIRECT_GAPS:
            fail(f"Missing/redirect-only page: {m}")
    for r in redirect_gaps:
        warn(f"Known redirect-only page (needs full content): {r}")
    if not [m for m in missing if m not in KNOWN_REDIRECT_GAPS]:
        ok(f"All key pages present in all {len(LANGS)} languages ({len(redirect_gaps)} known redirect gaps)")

# ── CHECK 2: Critical HTML content ────────────────────────────────────────────
def check_critical_content():
    print("\n🔍 Critical HTML content")
    for page, required in CRITICAL_STRINGS.items():
        bad_langs = []
        warn_langs = []
        for lang in LANGS:
            p = page_path(lang, page)
            if not p.exists() or is_redirect_only(p):
                continue  # already flagged in page coverage check
            html = read_html(p)
            gap_key = f"{lang}/{page}"
            for needle in required:
                if needle not in html:
                    if gap_key in KNOWN_TEMPLATE_GAPS:
                        warn_langs.append(f"{lang}:{needle}")
                    else:
                        bad_langs.append(f"{lang}:{needle}")
        if bad_langs:
            fail(f"{page} missing content: {bad_langs[:5]}")
        elif warn_langs:
            warn(f"{page} old template on known gap pages: {warn_langs[:3]}")
        else:
            ok(f"{page}: all critical elements present across all languages")

# ── CHECK 3: Translation quality ──────────────────────────────────────────────
def check_translations():
    print("\n🌍 Translation completeness")
    # Pick a few nav/footer strings that must NOT appear verbatim in other-lang pages
    en_only_strings = ["Book Now", "Surf House", "Back to Blog"]
    
    for lang in [l for l in LANGS if l != "en"]:
        home_p = page_path(lang, "home")
        if not home_p.exists():
            continue
        html = read_html(home_p)
        
        # Check hreflang tags present
        if 'hreflang' not in html:
            warn(f"{lang}/home: missing hreflang tags")
        
        # Check lang attribute on <html>
        if f'lang="{lang}"' not in html and f"lang='{lang}'" not in html:
            warn(f"{lang}/home: <html> tag missing lang=\"{lang}\"")
        
        # Check footer language switcher has links for all langs
        if '/en/' not in html and 'href="/"' not in html:
            warn(f"{lang}/home: no link back to English in footer/nav")
    
    # Check that blog articles exist in translated langs
    for lang in ["fr", "es", "de"]:  # key markets
        blog_dir = DEMO / lang / "blog"
        if not blog_dir.exists():
            fail(f"{lang}/blog directory missing")
            continue
        art_count = len(list(blog_dir.glob("*/index.html")))
        if art_count < 5:
            warn(f"{lang}/blog: only {art_count} articles (expected ≥5)")
        else:
            ok(f"{lang}/blog: {art_count} translated articles")
    
    ok("hreflang / lang attr checks complete")

# ── CHECK 4: CSS integrity ────────────────────────────────────────────────────
def check_css():
    print("\n🎨 CSS integrity")
    css_files = list((DEMO / "assets" / "css").glob("*.css"))
    if not css_files:
        fail("No CSS files found in assets/css/")
        return
    
    main_css = None
    for f in css_files:
        if "ngor" in f.name or "main" in f.name:
            main_css = f
            break
    main_css = main_css or css_files[0]
    
    css_text = main_css.read_text(errors="replace")
    size = len(css_text)
    
    if size < MIN_CSS_BYTES:
        fail(f"Main CSS too small: {size:,} bytes (expected ≥{MIN_CSS_BYTES:,})")
    else:
        ok(f"Main CSS: {size:,} bytes ({main_css.name})")
    
    # Check required classes
    missing_cls = [c for c in REQUIRED_CSS if f".{c}" not in css_text]
    if missing_cls:
        fail(f"Missing CSS classes: {missing_cls}")
    else:
        ok(f"All {len(REQUIRED_CSS)} required CSS classes present")
    
    # Basic brace balance
    opens  = css_text.count("{")
    closes = css_text.count("}")
    if opens != closes:
        fail(f"CSS brace mismatch: {opens} open vs {closes} close")
    else:
        ok("CSS braces balanced")

# ── CHECK 5: JS integrity ─────────────────────────────────────────────────────
def check_js():
    print("\n⚙️  JavaScript integrity")
    
    # Check gallery page has sessionStorage filter logic
    gal_p = DEMO / "gallery" / "index.html"
    if gal_p.exists():
        gal_html = read_html(gal_p)
        for pat in REQUIRED_JS:
            if pat not in gal_html:
                fail(f"gallery/index.html missing JS: {pat}")
            else:
                ok(f"gallery: '{pat}' present")
    
    # Check all JS assets exist and are non-empty
    js_files = list((DEMO / "assets" / "js").glob("*.js"))
    for jf in js_files:
        sz = jf.stat().st_size
        if sz < 100:
            warn(f"JS file suspiciously small: {jf.name} ({sz} bytes)")
    ok(f"JS assets: {len(js_files)} files checked")
    
    # Check no inline JS syntax disaster: unclosed function or missing }
    # (just spot-check the home page)
    home_html = read_html(DEMO / "index.html")
    scripts = re.findall(r'<script[^>]*>(.*?)</script>', home_html, re.DOTALL)
    for s in scripts:
        opens  = s.count("{")
        closes = s.count("}")
        if abs(opens - closes) > 5:
            warn(f"Home inline script has brace imbalance: {opens} open vs {closes} close")

# ── CHECK 6: Asset references ─────────────────────────────────────────────────
def check_asset_refs():
    print("\n🖼️  Critical asset references")
    critical_assets = [
        "assets/css/ngor-surfcamp.css",
        "assets/images/logo-fss-badge.webp",
        "assets/images/wix/c2467f_a31779010ce34c4c8c61cc5868d81f31.webp",  # nav logo
    ]
    for asset in critical_assets:
        p = DEMO / asset
        if not p.exists():
            fail(f"Missing asset: {asset}")
        elif p.stat().st_size < 100:
            warn(f"Asset too small (possibly corrupt): {asset}")
        else:
            ok(f"Asset OK: {asset} ({p.stat().st_size:,} bytes)")

# ── CHECK 7: Page count ───────────────────────────────────────────────────────
def check_page_count():
    print("\n📊 Page count")
    all_pages = list(DEMO.glob("**/index.html"))
    total = len(all_pages)
    if total < MIN_PAGES:
        fail(f"Page count too low: {total} (expected ≥{MIN_PAGES})")
    else:
        ok(f"Total pages: {total}")
    
    # Blog articles
    en_articles = list((DEMO / "blog").glob("*/index.html"))
    if len(en_articles) < MIN_ARTICLES:
        warn(f"EN blog articles: {len(en_articles)} (expected ≥{MIN_ARTICLES})")
    else:
        ok(f"EN blog articles: {len(en_articles)}")

# ── CHECK 8: SEO basics ───────────────────────────────────────────────────────
def check_seo():
    print("\n🔎 SEO basics")
    sampled_pages = [
        DEMO / "index.html",
        DEMO / "surfing" / "index.html",
        DEMO / "blog" / "index.html",
        DEMO / "fr" / "index.html",
    ]
    for p in sampled_pages:
        if not p.exists():
            continue
        html = read_html(p)
        label = str(p.relative_to(DEMO))
        
        if "<title>" not in html:
            fail(f"{label}: missing <title>")
        if 'name="description"' not in html:
            warn(f"{label}: missing meta description")
        if 'rel="canonical"' not in html:
            warn(f"{label}: missing canonical tag")
        if 'application/ld+json' not in html:
            warn(f"{label}: missing JSON-LD structured data")
        
        # Check no empty <title>
        m = re.search(r'<title>(.*?)</title>', html, re.DOTALL)
        if m and len(m.group(1).strip()) < 10:
            fail(f"{label}: title too short: {repr(m.group(1))}")
    
    ok("SEO spot-checks complete")

# ── CHECK 9: No broken fragments in article content ───────────────────────────
def check_article_content():
    print("\n📝 Article content quality")
    broken_pattern = re.compile(
        r'<p>\s*[.,;]\s*</p>|'           # paragraph with just punctuation
        r'go straight to\s*</p>|'        # empty link remnant
        r'<p>\s*can help clarify\s*</p>' # orphaned fragment
    )
    bad_files = []
    for html_path in (DEMO / "blog").glob("*/index.html"):
        html = read_html(html_path)
        if broken_pattern.search(html):
            bad_files.append(str(html_path.relative_to(DEMO)))
    
    if bad_files:
        fail(f"Broken content fragments in: {bad_files[:5]}")
    else:
        ok(f"No broken article content fragments found")

# ── CHECK 10: Footer consistency ─────────────────────────────────────────────
def check_footer():
    print("\n🦶 Footer consistency")
    must_have = ["footer-fss-badge", "WhatsApp", "Instagram", "Privacy Policy"]
    bad = []
    sampled = list((DEMO).glob("*/index.html"))[:5] + [DEMO / "index.html"]
    for p in sampled:
        if not p.exists():
            continue
        html = read_html(p)
        for needle in must_have:
            if needle not in html:
                bad.append(f"{p.relative_to(DEMO)}:{needle}")
    if bad:
        warn(f"Footer missing elements in some pages: {bad[:4]}")
    else:
        ok("Footer elements consistent across sampled pages")

# ── Version management ────────────────────────────────────────────────────────
def load_version():
    if VERSION_F.exists():
        return json.loads(VERSION_F.read_text())
    return {"major": 1, "minor": 0, "patch": 0, "build": 0, "history": []}

def bump_version(fix_mode=False):
    v = load_version()
    v["build"] += 1
    now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    v["last_deploy"] = now
    
    # Compute a fingerprint of the output to detect content changes
    sample_files = list(DEMO.glob("**/index.html"))[:20]
    h = hashlib.md5()
    for f in sorted(sample_files):
        h.update(f.read_bytes()[:4096])
    v["build_hash"] = h.hexdigest()[:8]
    
    VERSION_F.write_text(json.dumps(v, indent=2))
    print(f"\n📦 Version: {v['major']}.{v['minor']}.{v['patch']} build {v['build']} ({now})")
    return v

def write_changelog_entry(v, passed, warned):
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    status = "✅ PASSED" if not errors else "❌ FAILED"
    entry = (
        f"\n## [{v['major']}.{v['minor']}.{v['patch']} build {v['build']}] — {now}\n"
        f"Status: {status}  |  Errors: {len(errors)}  |  Warnings: {len(warned)}\n"
        f"Hash: `{v.get('build_hash','?')}`\n"
    )
    if errors:
        entry += "### Errors\n" + "\n".join(f"- {e}" for e in errors) + "\n"
    if warned:
        entry += "### Warnings\n" + "\n".join(f"- {w}" for w in warned[:10]) + "\n"
    
    existing = CHANGELOG.read_text() if CHANGELOG.exists() else "# Changelog\n"
    # Insert after first heading
    first_nl = existing.find("\n")
    CHANGELOG.write_text(existing[:first_nl+1] + entry + existing[first_nl+1:])

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fix", action="store_true", help="Bump build version and write changelog")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    args = parser.parse_args()

    print("=" * 60)
    print("  🏄 NGOR SURFCAMP — Pre-deploy Quality Gate")
    print("=" * 60)

    check_page_coverage()
    check_critical_content()
    check_translations()
    check_css()
    check_js()
    check_asset_refs()
    check_page_count()
    check_seo()
    check_article_content()
    check_footer()

    print("\n" + "=" * 60)
    if errors:
        print(f"  {FAIL} {len(errors)} CRITICAL error(s) — deploy blocked")
        for e in errors:
            print(f"     • {e}")
    else:
        print(f"  {PASS} All critical checks passed")

    if warnings:
        print(f"  {WARN} {len(warnings)} warning(s)")
        for w in warnings[:8]:
            print(f"     • {w}")

    if args.fix or not errors:
        v = bump_version(args.fix)
        write_changelog_entry(v, not errors, warnings)
        print(f"  {INFO} Changelog updated → CHANGELOG.md")

    print("=" * 60)

    if errors:
        sys.exit(1)
    if args.strict and warnings:
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
