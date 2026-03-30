#!/usr/bin/env python3
"""
Translate all site content for nl (Dutch/Netherlands) and ar (Arabic/Morocco)
using GPT-5.4-2026-03-05.

Run: python3 scripts/translate_new_langs.py
Output: scripts/translations_nl_ar.json
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import openai

API_KEY = (os.environ.get("OPENAI_API_KEY") or "").strip()
MODEL = (os.environ.get("OPENAI_MODEL") or "gpt-4o").strip()
if not API_KEY:
    raise SystemExit("Set OPENAI_API_KEY.")

client = openai.OpenAI(api_key=API_KEY)

OUT = os.path.join(os.path.dirname(__file__), "translations_nl_ar.json")

SYSTEM = """You are a professional multilingual translator for a surf camp website in Senegal.
Translate English marketing copy accurately, keeping the surf/travel tone.
For Dutch (nl): natural, friendly Dutch.
For Arabic (ar): Modern Standard Arabic (فصحى), right-to-left, suitable for Moroccan audience.
Return ONLY a JSON object with keys "nl" and "ar". No explanations. No markdown code blocks."""

def gpt(content_en: dict) -> dict:
    """Translate a dict of English strings to nl + ar."""
    prompt = f"""Translate each value in this JSON from English to Dutch (nl) and Arabic (ar).
Return JSON: {{"nl": {{...same keys, Dutch values...}}, "ar": {{...same keys, Arabic values...}}}}

Input:
{json.dumps(content_en, ensure_ascii=False, indent=2)}"""
    
    for attempt in range(3):
        try:
            r = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM},
                    {"role": "user",   "content": prompt},
                ],
                max_completion_tokens=4000,
                response_format={"type": "json_object"},
            )
            return json.loads(r.choices[0].message.content)
        except Exception as e:
            print(f"  ⚠️  Attempt {attempt+1} failed: {e}")
            time.sleep(2)
    raise RuntimeError("Translation failed after 3 attempts")


def translate_batch(label: str, data: dict) -> dict:
    """data = {key: english_string}. Returns {key: {nl:..., ar:...}}"""
    print(f"  Translating: {label} ({len(data)} keys)...")
    result = gpt(data)
    out = {}
    for k, v_en in data.items():
        out[k] = {"en": v_en, "nl": result.get("nl", {}).get(k, ""), "ar": result.get("ar", {}).get(k, "")}
    return out


# ── Collect all English content ──────────────────────────────────────────────

translations = {}

# 1. SLUG
translations["SLUG"] = translate_batch("SLUG", {
    "surf-house": "surf-house",
    "island": "island",
    "surfing": "surfing",
    "booking": "booking",
    "gallery": "gallery",
    "faq": "faq",
    "blog": "blog",
    "privacy-policy": "privacy-policy",
    "category": "category",
})
print("  SLUG done")

# 2. Navigation labels
translations["NAV"] = translate_batch("NAV", {
    "home": "Home",
    "surf_house": "Surf House",
    "island": "Island",
    "surfing": "Surfing",
    "blog": "Blog",
    "gallery": "Gallery",
    "faq": "FAQ",
    "book_now": "Book Now",
    "getting_here": "Getting here",
})

# 3. BOOKING_SOCIAL_L10N
translations["BOOKING_SOCIAL"] = translate_batch("BOOKING_SOCIAL", {
    "google_lbl": "Google rating",
    "count": "64 Google reviews",
    "maps": "View on Google Maps",
    "leave": "Leave a review",
    "rv_eyebrow": "Social proof",
    "rv_h": "What guests say",
    "rc_tip": "Click to read more",
})

# 4. HOME_PROOF_L10N
translations["HOME_PROOF"] = translate_batch("HOME_PROOF", {
    "aria": "Camp highlights",
    "eyebrow": "The essentials",
    "f1_n": "2×",
    "f1_t": "daily surf sessions",
    "f1_d": "Morning & afternoon — spots chosen by forecast",
    "f2_n": "1964",
    "f2_t": "Endless Summer",
    "f2_d": "The film that put Ngor on the map",
    "f3_n": "All",
    "f3_t": "levels",
    "f3_d": "Beginner to advanced — Abu, best surf guide in Dakar",
})

# 5. HOME_GALLERY_L10N
translations["HOME_GALLERY"] = translate_batch("HOME_GALLERY", {
    "lbl": "Gallery",
    "h2": "Island Life in Pictures",
    "cta": "View all photos",
})

# 6. GALLERY_PAGE_COPY
translations["GALLERY_PAGE"] = translate_batch("GALLERY_PAGE", {
    "title": "Surf Camp Senegal Gallery | Ngor Island Photos",
    "meta": "Discover Ngor Surfcamp Teranga through photos: surf sessions, island life, rooms, food and sunsets on Ngor Island, Dakar.",
    "h1": "Our Gallery",
    "intro": "A glimpse of life at Ngor Surfcamp Teranga — waves, smiles, sunsets and surf.",
    "lb_close": "Close gallery",
    "lb_prev": "Previous photo",
    "lb_next": "Next photo",
    "lb_counter": "of",
})

# 7. ISLAND_GUIDE_UI (key navigation elements)
translations["ISLAND_GUIDE_UI"] = translate_batch("ISLAND_GUIDE_UI", {
    "eyebrow": "Island Guide",
    "back": "← Back to Island",
    "related": "More island guides",
    "hub_eyebrow": "Explore the island",
    "hub_h2": "Island Guides",
    "hub_sub": "Everything you need to know about Ngor Island",
})

# 8. ISLAND_HUB_GUIDES_SECTION
translations["ISLAND_HUB"] = translate_batch("ISLAND_HUB", {
    "eyebrow": "All guides",
    "h2": "Explore Ngor Island",
    "sub": "Practical guides and local insight for your surf stay",
})

# 9. BOOK_FOOTER_LABEL  
translations["BOOK_FOOTER"] = translate_batch("BOOK_FOOTER", {
    "label": "Book your stay",
    "sub": "Message us on WhatsApp or fill in the form — we reply within 24h.",
})

# 10. GETTING_HERE
translations["GETTING_HERE"] = translate_batch("GETTING_HERE", {
    "label": "Getting here",
    "title": "How to get to Ngor Island",
    "desc": "From Dakar airport, take a taxi to the Almadies jetty, then a short pirogue crossing to the island.",
})

# 11. PP (Privacy Policy) labels
translations["PP"] = translate_batch("PP", {
    "title": "Privacy Policy",
    "meta": "Privacy policy for Ngor Surfcamp Teranga surf camp in Senegal.",
    "slug": "privacy-policy",
    "label": "Privacy Policy",
    "copyright": "© NGOR SURFCAMP TERANGA. All rights reserved.",
    "copyright_short": "© NGOR SURFCAMP TERANGA",
})

# 12. BLOG_CATS  
translations["BLOG_CATS"] = translate_batch("BLOG_CATS", {
    "Island Life & Surf Camp": "Island Life & Surf Camp",
    "Surf Conditions & Spots": "Surf Conditions & Spots",
    "Coaching & Progression": "Coaching & Progression",
})

# 13. BLOG UI strings
translations["BLOG_UI"] = translate_batch("BLOG_UI", {
    "eyebrow": "Blog",
    "h1": "Surf Journal",
    "intro": "Stories, guides and expert tips from Ngor Island, Senegal.",
    "filter_all": "All articles",
    "browse_cats": "Browse by category",
    "read_more": "Read more",
    "back_blog": "← Back to Blog",
    "prev": "Previous",
    "next": "Next",
    "related": "Related articles",
    "min_read": "min read",
})

# 14. FAQ UI
translations["FAQ_UI"] = translate_batch("FAQ_UI", {
    "title": "Surf Camp Senegal FAQ | Ngor Surfcamp Teranga",
    "h1": "Frequently Asked Questions",
    "meta": "All your questions about Ngor Surfcamp Teranga answered: accommodation, surf levels, packages, transfers and more.",
})

# 15. Breadcrumb & misc
translations["MISC"] = translate_batch("MISC", {
    "home": "Home",
    "article_eyebrow": "Article",
    "share": "Share",
    "or_contact": "Or contact us directly:",
    "no_spam": "No spam",
    "reply_24h": "Reply in 24h",
    "free_cancel": "Free cancellation",
    "verified_review": "Verified review",
    "isa_cert": "ISA certified",
    "fed_senegal": "Senegalese Federation",
    "local_knowledge": "Local knowledge",
})

# Save
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(translations, f, ensure_ascii=False, indent=2)

print(f"\n✅ UI translations saved to {OUT}")
