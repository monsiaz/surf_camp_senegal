#!/usr/bin/env python3
"""
Translate all page copy (SURF_PAGE_COPY, surf_house_page, booking, PP, surfing/FAQ)
and save to scripts/translations_pages_nl_ar.json
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import openai

API_KEY = "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"
MODEL  = "gpt-5.4-2026-03-05"
client = openai.OpenAI(api_key=API_KEY)
OUT    = os.path.join(os.path.dirname(__file__), "translations_pages_nl_ar.json")

SYSTEM = """You are a professional surf travel copywriter and translator.
Translate English surf camp website copy to Dutch (nl) and Arabic (ar/Morocco).
Dutch: natural, friendly, modern. Arabic: Modern Standard Arabic suitable for Moroccan tourists.
Return ONLY a JSON object: {"nl": {...}, "ar": {...}} with same keys as input. No markdown."""

def gpt(data: dict, label="") -> dict:
    print(f"  → {label} ({len(data)} keys)...")
    prompt = f'Translate all values from English:\n{json.dumps(data, ensure_ascii=False, indent=2)}'
    for attempt in range(3):
        try:
            r = client.chat.completions.create(
                model=MODEL,
                messages=[{"role":"system","content":SYSTEM},{"role":"user","content":prompt}],
                max_completion_tokens=8000,
                response_format={"type":"json_object"},
            )
            parsed = json.loads(r.choices[0].message.content)
            # Ensure both nl and ar present
            if "nl" in parsed and "ar" in parsed:
                return parsed
            print(f"  ⚠️  Missing nl or ar key, retrying...")
        except Exception as e:
            print(f"  ⚠️  Attempt {attempt+1}: {e}")
            time.sleep(2)
    return {"nl": {k: f"[TODO:{k}]" for k in data}, "ar": {k: f"[TODO:{k}]" for k in data}}

result = {}

# ── 1. SURF_PAGE_COPY (en) ──────────────────────────────────────────────────
surf_en = {
    "title": "Surfing in Ngor | Ngor Surfcamp Teranga",
    "meta": "Surf Ngor Island, Dakar: coaching, guiding, video analysis, theory classes, reef breaks and surf trips. Surf better, live slower.",
    "h1": "Surfing in Ngor",
    "tag": "Surf better, live slower, feel the difference",
    "lbl_intro": "Surf at Ngor",
    "p1": "At Ngor Surfcamp Teranga, we mix world-class waves with laid-back island vibes and expert surf coaching that actually moves the needle.",
    "p2": "Whether you are chasing your first green wave or refining your turns, we guide your progression at your rhythm in the heart of West Africa's surf culture.",
    "p3": "At Ngor Surfcamp, your surf journey goes beyond the waves. With expert coaching and a relaxed island lifestyle, we help you find your best surf and your flow.",
    "p4": "Surf better and feel connected: two sessions a day — morning and afternoon — taken to the best spot according to forecast and swell. Our surf guide Abu, rated the best surf guide in Dakar, knows exactly how to place you on the wave. Fast progression guaranteed.",
    "p5": "From sunrise surf to sunset chill, you will grow in and out of the water, surrounded by people who share the same passion.",
    "thumb_lbl": "What you get",
    "thumb_h2": "Professional surf experience",
    "thumbs_0": "Professional surf coaching — all levels",
    "thumbs_1": "Professional surf guiding",
    "thumbs_2": "Video analysis",
    "thumbs_3": "Surf theory classes — free: paddling, pop-up, bottom turn, cutback…",
    "thumbs_4": "Consistent reef and beach breaks",
    "thumbs_5": "Surf trips (swell dependent)",
    "thumbs_6": "Chill, safe island with local culture",
    "lvl_lbl": "Your level at Ngor",
    "lvl_h2": "Your level at Ngor",
    "beg_t": "Beginner",
    "beg_d": "Never surfed, or just tried once or twice. You will start on a foam board on Ngor Left, a forgiving wave perfect for learning. By the end of your stay, you will be standing and riding.",
    "int_t": "Intermediate",
    "int_d": "You can consistently pop up and ride down the line. Ready to work on turns, reading waves, and timing your take-off. Ngor Right on smaller days will become your playground.",
    "adv_t": "Advanced",
    "adv_d": "You surf turns and are pushing your performance. Ngor Right at full size is your wave: powerful, fast and demanding. Video analysis will fast-track your specific weaknesses.",
    "team_lbl": "Our team",
    "team_h2": "Why Ngor Surfcamp Teranga?",
    "team_intro": "Meet Ben (owner & coach), Abu (head surf guide — rated the best surf guide in Dakar by our guests) and Arame (chef). Together they create an experience guests describe as 'feeling like home': impeccable organisation, expert coaching and food that earns five stars on its own.",
    "team_isa": "The instructors are local surfers with industry-standard ISA qualifications and national diplomas.",
    "gal_h2": "Our surf trips in action",
    "cta_h2": "Meet like-minded surfers from around the world",
    "cta_sub": "Ngor Island, Dakar, Senegal. WhatsApp: +221 78 925 70 25",
    "book": "Book your surf package",
    "badge_isa": "ISA certified",
    "badge_fed": "Senegalese Federation",
    "badge_loc": "Local knowledge",
}
r = gpt(surf_en, "SURF_PAGE_COPY")
result["SURF_PAGE_COPY"] = {"nl": r["nl"], "ar": r["ar"]}

# ── 2. SURF_HOUSE_PAGE (en) ─────────────────────────────────────────────────
sh_en = {
    "title": "Surf House on Ngor Island, Senegal | Ngor Surfcamp Teranga",
    "meta": "Welcome to Ngor Surf House: private & shared rooms, pool, meals, surf transfers and daily guiding on Ngor Island, Dakar.",
    "hero_kicker": "Surf House on Ngor Island, Senegal",
    "h1": "Ngor Surf House",
    "tagline": "Surfing is our Way of Life",
    "welcome_lbl": "Welcome",
    "welcome_title": "Welcome to Ngor Surf House",
    "p1": "Welcome to Ngor Surf House — your home on the waves on Ngor Island, Senegal!",
    "p2": "Tucked between turquoise water and a laid-back vibe, our surf house is more than just a place to stay: it's a home base for surfers, travellers and ocean lovers from around the world.",
    "p3": "Our surf house on Ngor Island offers a cosy, community-focused atmosphere just steps from the ocean. Rooms are cleaned and beds made every day — guests regularly rate it the cleanest and best-kept surf house on the island. Many rooms have a panoramic view over the Atlantic and the Ngor Right sunset.",
    "p4": "Whether you're a beginner or an experienced surfer, travelling solo, as a couple or with friends, our surf house offers a friendly, community-focused atmosphere — with comfortable rooms, shared living spaces, a seaside terrace, a swimming pool and easy access to some of the best surf spots in Dakar, including the world-famous wave of Ngor Island.",
    "quote_h2": "Private & shared surf rooms on Ngor Island",
    "quote_line1": "Our surf house is more than a destination",
    "quote_line2": "It's a way of life!",
    "acc_h2": "Comfortable surf camp",
    "acc_sub": "Accommodations in Senegal",
    "meals_h2": "Enjoy local meals at our surf house in Senegal",
    "meals_p": "We're not just sharing waves — we're sharing moments! Enjoy generous, delicious national dishes prepared fresh every day — breakfast and dinner included. A taste of Senegalese hospitality with music, good food and great vibes.",
    "bento_h2": "Island life in pictures",
    "bento_c1": "Terrace & rooms",
    "bento_c2": "Surf spirit",
    "bento_c3": "Pool & chill",
    "bento_c4": "Senegalese table",
    "bento_c5": "Steps from the wave",
    "gal_h2": "Life at the surf house",
    "cta_h2": "Book your stay",
    "cta_p": "Rooms are cleaned and beds made every day — so you can focus on surfing. Message us on WhatsApp; we reply within 24h.",
    "book": "Book your stay",
    "copyright": "© NGOR SURFCAMP TERANGA. All rights reserved.",
    "privacy": "Privacy & information",
}
r = gpt(sh_en, "SURF_HOUSE_PAGE")
result["SURF_HOUSE_PAGE"] = {"nl": r["nl"], "ar": r["ar"]}

# ── 3. SURF_HOUSE_FEATS (en) ────────────────────────────────────────────────
feats_en = {
    "feat_0_title": "Private & shared rooms",
    "feat_0_desc": "Single or double rooms (with or without balcony) just steps from the ocean, plus a comfortable dorm with bathroom.",
    "feat_1_title": "Pool & chill zones",
    "feat_1_desc": "A terrace overlooking the Atlantic, a pool to cool off between sessions, and communal spaces to swap stories.",
    "feat_2_title": "Meals included",
    "feat_2_desc": "Breakfast and dinner prepared fresh every day: traditional Senegalese dishes, fish, rice and local flavours.",
    "feat_3_title": "Surf transfers & guiding",
    "feat_3_desc": "Daily boat or vehicle trips to the best spots: Ngor Right, Ngor Left, Ouakam, Yoff and beyond.",
    "feat_4_title": "Free surf theory",
    "feat_4_desc": "Daily theory sessions covering ocean reading, paddling technique, wave selection and safety.",
    "feat_5_title": "Free Wi-Fi & daily room cleaning",
    "feat_5_desc": "Stay connected and come back to a clean, fresh room every afternoon.",
}
r = gpt(feats_en, "SURF_HOUSE_FEATS")
result["SURF_HOUSE_FEATS"] = {"nl": r["nl"], "ar": r["ar"]}

# ── 4. BOOKING_PAGE (en) ────────────────────────────────────────────────────
booking_en = {
    "title": "Book Your Surf Camp Stay | Ngor Surfcamp Teranga",
    "meta": "Book your surf camp stay at Ngor Surfcamp Teranga on Ngor Island, Dakar, Senegal. Check availability and we'll take care of the rest.",
    "h1": "Book Your Stay",
    "sub": "Check availability and we'll take care of the rest!",
    "h2": "Check Availability & Book Your Stay",
    "sub2": "Tell us your dates and we'll find the perfect room for your surf adventure.",
    "fname": "First Name",
    "lname": "Last Name",
    "email": "E-mail",
    "phone": "WhatsApp / Phone Number",
    "level": "What's your current surf level?",
    "guests": "How many guests?",
    "arrive": "When do you arrive?",
    "depart": "When do you leave?",
    "flexible": "I'm flexible — tell me when the swell is best!",
    "goal": "What is your #1 goal for this trip?",
    "goal_ph": "e.g., improving my cutback, exploring Dakar, relaxing by the pool...",
    "submit": "CHECK AVAILABILITY & PRICES",
    "no_spam": "No spam. We reply within 24 hours.",
    "or": "Or contact us directly:",
    "steps_h": "Booking made easy",
    "step1": "Choose your dates",
    "step2": "Fill the form or WhatsApp us",
    "step3": "We confirm your room & package",
    "incl_h": "Everything included",
    "incl_0": "Accommodation (private or shared room)",
    "incl_1": "Breakfast & dinner (authentic Senegalese cuisine)",
    "incl_2": "Daily surf guiding to the best spots",
    "incl_3": "Boat transfers to Ngor Right & Left",
    "incl_4": "Free surf theory classes",
    "incl_5": "Pool access & shared spaces",
    "incl_6": "Free Wi-Fi & daily room cleaning",
    "trust": "Licensed by the Senegalese Federation of Surfing",
    "err_fn": "Please enter your first name",
    "err_em": "Please enter a valid email address",
    "err_dt": "Departure must be after arrival",
    "level_beg": "Beginner (never surfed or just started)",
    "level_int": "Intermediate (can ride waves)",
    "level_adv": "Advanced (working on turns & performance)",
}
r = gpt(booking_en, "BOOKING_PAGE")
result["BOOKING_PAGE"] = {"nl": r["nl"], "ar": r["ar"]}

# ── 5. FAQ key strings ──────────────────────────────────────────────────────
faq_en = {
    "title": "Surf Camp Senegal FAQ | Ngor Surfcamp Teranga",
    "h1": "Frequently Asked Questions",
    "meta": "All your questions about Ngor Surfcamp Teranga answered: accommodation, surf levels, packages, transfers and more.",
    "cta_h": "Ready to surf Ngor Island?",
    "cta_p": "Book your stay and we'll handle the rest. WhatsApp us anytime.",
    "cta_btn": "Book your stay",
    "cta_wa": "WhatsApp us",
}
r = gpt(faq_en, "FAQ_PAGE")
result["FAQ_PAGE"] = {"nl": r["nl"], "ar": r["ar"]}

# ── 6. Privacy Policy ───────────────────────────────────────────────────────
pp_en = {
    "title": "Privacy Policy | Ngor Surfcamp Teranga",
    "meta": "Privacy policy for Ngor Surfcamp Teranga surf camp in Senegal.",
    "h1": "Privacy Policy",
    "slug": "privacy-policy",
    "label": "Privacy Policy",
    "copyright": "© NGOR SURFCAMP TERANGA. All rights reserved.",
    "copyright_short": "© NGOR SURFCAMP TERANGA",
    "back": "← Back to home",
}
r = gpt(pp_en, "PP_PAGE")
result["PP_PAGE"] = {"nl": r["nl"], "ar": r["ar"]}

# ── 7. Island page ──────────────────────────────────────────────────────────
island_en = {
    "title": "Ngor Island Senegal | Surf Trip near Dakar",
    "meta": "Discover Ngor Island: surf, culture, local life and the world-famous Ngor Right wave, just 800m off the coast of Dakar.",
    "h1": "Ngor Island, Senegal",
    "tag": "A car-free surf haven just off Dakar",
    "lbl": "The Island",
    "p1": "Ngor Island sits 800 metres off the Almadies peninsula, the westernmost tip of mainland Africa. No cars, no traffic — just 900 metres of walkable paths, fishing boats, surf culture and Atlantic light.",
    "p2": "The island is home to two world-class waves: Ngor Right, a long mechanical right-hander that featured in the 1964 film The Endless Summer, and Ngor Left, a perfect wave for beginners and intermediate surfers.",
    "p3": "Life on Ngor is defined by the rhythm of the tides. In the morning, the Atlantic is glassy. By afternoon, the trade winds pick up. At sunset, the sky turns orange and the island glows.",
    "cta_book": "Book your island surf stay",
    "cta_guide": "Explore island guides",
}
r = gpt(island_en, "ISLAND_PAGE")
result["ISLAND_PAGE"] = {"nl": r["nl"], "ar": r["ar"]}

# ── 8. Footer & general UI ──────────────────────────────────────────────────
footer_en = {
    "explore": "Explore",
    "contact": "Contact",
    "follow": "Follow us",
    "premium": "Premium surf camp on Ngor Island, Dakar, Senegal. Licensed by the Senegalese Federation of Surfing.",
    "rights": "© NGOR SURFCAMP TERANGA. All rights reserved.",
    "rights_short": "© NGOR SURFCAMP TERANGA",
    "whatsapp_label": "WhatsApp",
    "email_label": "Email",
    "lang_select": "Language",
}
r = gpt(footer_en, "FOOTER")
result["FOOTER"] = {"nl": r["nl"], "ar": r["ar"]}

# Save
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print(f"\n✅ Page translations saved → {OUT}")
