#!/usr/bin/env python3
"""
Regenerate all 5 island guide JSONs at 2000-3000 words per locale (5 languages).
Uses gpt-5.4-2026-03-05, 25 parallel tasks.
"""
import json, os, re
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

OPENAI_KEY = (os.environ.get("OPENAI_API_KEY") or "").strip()
MODEL = (os.environ.get("OPENAI_MODEL") or "gpt-4o").strip()
GUIDES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "content", "island_guides")

if not OPENAI_KEY:
    raise SystemExit("Set OPENAI_API_KEY in the environment.")

client = OpenAI(api_key=OPENAI_KEY)
lock   = threading.Lock()

SITE_CTX = """
Ngor Surfcamp Teranga | Premium surf camp on Ngor Island (Île de Ngor), Dakar, Senegal.
Licensed by Senegalese Federation of Surfing. All levels. Video coaching.
Waves: Ngor Right (powerful point break, intermediate+) + Ngor Left (forgiving, all levels).
Featured in The Endless Summer (1966 release). No cars on island. Atlantic Ocean.
Pool, sea views, daily Senegalese meals (breakfast + dinner), boat transfers, daily surf guiding.
WhatsApp: +221 78 925 70 25
"""

def log(msg):
    with lock: print(msg, flush=True)

def gpt(prompt, temp=0.72, tokens=6000):
    r = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=temp,
        max_completion_tokens=tokens,
    )
    return r.choices[0].message.content.strip()

def fix_em(t):
    return re.sub(r',\s*,', ',', str(t)
        .replace(" — ", ", ").replace("—", ",").replace("\u2014", ",")
        .replace(" – ", ", ").replace("–", ","))

# ── Existing guide structure (to keep slugs, ids, heroes) ──────────
def load_guide(filename):
    with open(os.path.join(GUIDES_DIR, filename), encoding="utf-8") as f:
        return json.load(f)

def save_guide(filename, data):
    with open(os.path.join(GUIDES_DIR, filename), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ── Per-guide topic briefings ──────────────────────────────────────
GUIDE_BRIEFS = {
    "things-to-do": {
        "en_title": "What to Do on Ngor Island",
        "sections": [
            "Introduction: why Ngor is special — car-free island, 5-10 min boat from Dakar",
            "The boat crossing: where to board, fares in XOF, beach landings",
            "Beaches: North beach (calmer, family), South side, swimming safety tips",
            "Walking the island: complete circumference walk ~30 min, painted doors, murals, neighborhood life",
            "Surf watching: best spots to watch Ngor Right and Left from shore, safety distances",
            "Food scene: grilled fish, thiéboudienne, yassa, local cafes, small restaurants, what to order",
            "Evening and sunsets: best west-facing spots, timing tips, atmosphere",
            "Shopping and crafts: local artisans, souvenirs, what to bring and what not to buy",
            "Cultural etiquette: photography consent, dress near mosques, Teranga hospitality",
            "Activities for non-surfers: paddling, snorkeling on calm days, yoga retreats, relaxing",
            "Practical day planning: morning vs afternoon island, split days with Dakar",
            "What to bring: cash XOF, reef shoes, sunscreen, refillable water bottle",
        ],
        "word_target": 2500,
    },
    "day-trips": {
        "en_title": "Day Trips from Ngor Island",
        "sections": [
            "Introduction: using Ngor as a base for Dakar and surroundings",
            "Lac Rose (Lac Retba): what it is, salt flats, pink color conditions (salinity + algae + light), getting there (45-60 min from Dakar), best time of day, camel rides, salt harvesting cooperatives",
            "Bandia Wildlife Reserve: lions, rhinos, giraffes, zebras, antelopes; 65 km south-east; guided 4WD; 2-3 hours; booking tips",
            "Gorée Island (UNESCO): historical importance, Maison des Esclaves, ferry from Port de Dakar (~30 min), completely different vibe from Ngor",
            "Dakar city highlights: IFAN Museum, Marché HLM (fabric), Sandaga/Kermel markets, restaurant scene, art galleries, Corniche",
            "Île de la Madeleine: uninhabited nature reserve, kayaking or boat tour, birds, vegetation, 2 hours round trip",
            "Toubab Dialaw and Cap Skirring: further options for multi-day trips, surf further south",
            "Practical transport: taxis, Uber/Yango in Dakar, private drivers (best value for groups), typical costs in XOF",
            "Planning tips: always one main destination per long day, book drivers the night before, confirm last boat time",
        ],
        "word_target": 2500,
    },
    "history-culture": {
        "en_title": "Ngor Island History & Culture",
        "sections": [
            "Introduction: small island with outsized place in Senegalese and global surf culture",
            "Geographic and pre-colonial context: fishing village, Lebu people, traditional boat-building",
            "Colonial era and Dakar's growth: how urbanization shaped the island's identity",
            "Islam in Ngor: role of mosques, Mouride brotherhood influence, daily prayer, respectful visit tips",
            "Teranga — the Senegalese art of hospitality: etymology, how it manifests daily, reciprocity",
            "The Endless Summer (1966): Bruce Brown's journey, what the film actually showed about Ngor, how it influenced surf tourism",
            "Modern surf culture: ISA, Senegalese Surf Federation, local heroes, how surf camp economy integrated",
            "Art scene: murals, street painters, the 'Porte de Ngor' tradition of painted doors",
            "Music and food culture: mbalax rhythm, thiéboudienne national dish, tea ceremony (attaya)",
            "Balancing tourism and community: how to be a respectful visitor, dos and don'ts",
            "Ngor today: demographics, fishing fleet still operating, mix of traditional and modern",
        ],
        "word_target": 2500,
    },
    "surf-right-left": {
        "en_title": "Surfing Ngor: Right & Left Guide",
        "sections": [
            "Introduction: why Ngor's two breaks matter in global surf travel",
            "Ngor Right (Droite): reef point break, swell direction (NW to NNW), size range, best tide, character of the wave (long wall, barrels on bigger days), skill level (intermediate to advanced), crowd dynamics",
            "Ngor Left (Gauche): beach/reef mix, more forgiving entry, swell requirements (smaller works fine), best for beginners and intermediates with coaching, shore break danger on big days",
            "Swell windows: North Atlantic low pressure systems, October-April peak, but offshore season (May-September) still produces",
            "Wind: harmattan (December-March) creates offshore conditions (best), summer trades can be cross/onshore",
            "Water temperature: 18-28°C range year round, warmest in summer, no winter wetsuit needed for most",
            "Equipment: recommended board types per level per break, fins, booties for reef, leash importance",
            "Etiquette and safety: don't drop in, wave priority, communicating in the lineup, sea urchins, riptide awareness",
            "Coaching at Ngor Surfcamp: ISA-licensed instructors, video analysis, progression levels, what a week looks like",
            "Other Dakar breaks: Vivier, Yoff, Plage de Ouakam context — when to surf those instead",
            "Practical: board rental, foam boards for learners, wax, reef safety briefing",
        ],
        "word_target": 2500,
    },
    "practical-tips": {
        "en_title": "Ngor Island Practical Travel Tips",
        "sections": [
            "Introduction: everything you need for a smooth stay",
            "Getting to Dakar: flights (Air France, Air Senegal, Turkish, Royal Air Maroc, Brussels Airlines), airport (Blaise Diagne AIBD — 45 km from Dakar), visa on arrival for EU/US/UK (check latest requirements)",
            "Airport to Ngor: taxi (negotiate fixed price ~15,000-20,000 XOF), Yango/Uber app, private transfer through camp",
            "The boat to Ngor Island: departure points (Plage de Ngor), pirogue schedule (every ~15 min, earlier/later by arrangement), fare (~500-1000 XOF each way), beach landing advice",
            "Money: XOF (CFA franc), ATMs in Dakar (not on island), bring cash for island, rough costs (beer 1500, grilled fish 3000-5000, boat 500-1000), tipping culture",
            "Accommodation: Ngor Surfcamp Teranga (private/shared rooms, pool, meals, guiding) — other options on island are guesthouses",
            "What to pack: reef shoes, rashguard, sunscreen (reef-safe), light evening layer (Harmattan), plug adapter (European C), refillable water bottle (filtered water at camp)",
            "Health: no mandatory vaccines but yellow fever recommended, malaria prophylaxis for Dakar (consult doctor), drinking water (filtered only), sun protection, pharmacies in Dakar",
            "Language: Wolof is essential greetings (Nanga def? Mangi fi. Jërejëf.), French is official and widely spoken, English growing in tourism",
            "Internet and phone: local SIM cards (Orange, Free, Expresso) cheap with data, good 4G coverage",
            "Safety: Ngor is safe, Dakar normal city precautions (don't flash valuables, use Yango at night), ocean safety (always ask locals before swimming)",
            "Best time to visit: November-March (dry season, offshore winds, good swell) — but April-October has charm and fewer crowds",
            "Cultural notes: photography permission, modest dress near mosques, Friday is holy day",
        ],
        "word_target": 2500,
    },
}

LANG_INSTRUCTIONS = {
    "en": "Write in natural, fluent British/American English. No em dashes.",
    "fr": "Rédige en français naturel et fluide, ton de guide de voyage professionnel. Pas de tirets em (—).",
    "es": "Escribe en español neutro y fluido, tono de guía de viaje profesional. Sin rayas em (—).",
    "it": "Scrivi in italiano fluente e naturale, tono guida di viaggio professionale. Senza trattini em (—).",
    "de": "Schreibe auf natürlichem, flüssigem Deutsch, Ton eines professionellen Reiseführers. Keine Gedankenstriche (—).",
}

LANG_NAMES = {
    "en": "English", "fr": "French", "es": "Spanish", "it": "Italian", "de": "German"
}

MD_FORMAT = """
Use rich markdown with these conventions:
- ## H2 headings for each major section (6-8 sections)
- ### H3 for sub-sections where useful
- **bold** for important terms, place names, numbers
- Bullet lists for practical tips (3-6 bullets each)
- Numbered lists for step-by-step sequences
- At least 3 VISUAL BLOCKS in this exact format:
  **TIP:** (practical advice)
  **FACT:** (interesting verified information)
  **SUMMARY:** (at end)
  also use **EXPERT:** (surf or local knowledge), **CHECKLIST:** items on separate lines
- Start with a brief engaging intro (no heading)
- End with a SUMMARY block and a call to action mentioning Ngor Surfcamp Teranga
- NO em dashes (— or –) — use commas or rephrase
- NO bullet starting with "Here are" or "Below you'll find"
"""

def build_prompt(guide_id, lang, existing_locale):
    brief = GUIDE_BRIEFS[guide_id]
    sections_str = "\n".join(f"  - {s}" for s in brief["sections"])
    lang_instr = LANG_INSTRUCTIONS[lang]
    word_target = brief["word_target"]
    existing_title = existing_locale.get("title", "")
    existing_h1    = existing_locale.get("h1", "")

    return f"""You are a professional travel and surf writer producing a high-quality island guide article.

CONTEXT:
{SITE_CTX}

TASK:
Write a complete island guide article for Ngor Island in {LANG_NAMES[lang]}.
Title (keep or improve): {existing_title}
H1: {existing_h1}
Target word count: {word_target} words (strictly between {word_target-200} and {word_target+300} words)

LANGUAGE INSTRUCTIONS:
{lang_instr}

SECTIONS TO COVER (must cover all of them, expand each thoroughly):
{sections_str}

MARKDOWN FORMAT:
{MD_FORMAT}

IMPORTANT:
- This article is the LOCAL-LANGUAGE ({LANG_NAMES[lang]}) version
- Every section should have at least 2-3 substantial paragraphs
- Include practical details (times, prices in XOF, distances in km) where relevant
- Mention Ngor Surfcamp Teranga naturally 2-3 times as the ideal base
- Make every word count — no filler, no repetition
- The article MUST be between {word_target-200} and {word_target+300} words

Return ONLY the markdown content, no preamble or meta-commentary.
"""

def generate_locale(guide_id, lang, existing_locale, filename):
    try:
        prompt = build_prompt(guide_id, lang, existing_locale)
        md = gpt(prompt, temp=0.72, tokens=6000)
        md = fix_em(md)
        word_count = len(md.split())
        log(f"  ✅ {filename} [{lang}] — {word_count} words")
        return lang, md, word_count
    except Exception as e:
        log(f"  ❌ {filename} [{lang}] ERROR: {e}")
        return lang, None, 0

def process_guide(filename):
    guide = load_guide(filename)
    guide_id = guide["guide_id"]
    log(f"\n→ Processing {filename} (guide_id={guide_id})")

    tasks = []
    with ThreadPoolExecutor(max_workers=5) as ex:
        futures = {}
        for lang in ["en", "fr", "es", "it", "de"]:
            loc = guide["locales"].get(lang, {})
            fut = ex.submit(generate_locale, guide_id, lang, loc, filename)
            futures[fut] = lang

        for fut in as_completed(futures):
            lang_res, md, wc = fut.result()
            if md:
                # Update reading minutes
                rm = max(8, min(15, wc // 200))
                guide["locales"][lang_res]["content_markdown"] = md
                guide["locales"][lang_res]["reading_minutes"] = rm
                guide["locales"][lang_res]["word_count"] = wc

    save_guide(filename, guide)
    log(f"  💾 Saved {filename}")

GUIDE_FILES = [
    "ngor-island-things-to-do.json",
    "ngor-island-history-culture.json",
    "day-trips-from-ngor-island.json",
    "ngor-island-surf-right-left-guide.json",
    "ngor-island-practical-travel-tips.json",
]

if __name__ == "__main__":
    log(f"Generating {len(GUIDE_FILES)} island guides × 5 languages = {len(GUIDE_FILES)*5} articles...")
    log(f"Model: {MODEL}")

    # Process guides sequentially (5 langs in parallel per guide)
    with ThreadPoolExecutor(max_workers=3) as ex:
        futs = {ex.submit(process_guide, fn): fn for fn in GUIDE_FILES}
        for fut in as_completed(futs):
            fn = futs[fut]
            try:
                fut.result()
            except Exception as e:
                log(f"FATAL {fn}: {e}")

    log("\n✅ All island guides regenerated. Run: python3 build.py --deploy")
