#!/usr/bin/env python3
"""Fix remaining article issues:
1. AR week/ngor-surf-guide: broken content + missing FAQ
2. IT week-at-premium: 3 missing content sections
3. FR/IT dakar-surf-spots: missing sections
"""

import json, re, os, sys
import openai

API_KEY = os.environ.get("OPENAI_API_KEY", "")
MODEL   = os.environ.get("OPENAI_MODEL", "gpt-5.4-2026-03-05")
BASE    = "content/articles_v2"

client = openai.OpenAI(api_key=API_KEY)

SYSTEM_TRANSLATE = """You are a professional surf travel copywriter. You translate and adapt surf camp blog content into the target language.
Keep the same tone, structure, and markdown formatting as the source.
Translate accurately but naturally — not word-for-word. Keep all markdown headings (##, ###, **bold**, etc.).
Do NOT add any preamble or explanation. Output ONLY the translated markdown content."""

SYSTEM_EXPAND = """You are a professional surf travel copywriter. You expand and complete blog articles about surf camps.
Keep the same tone, style, and markdown formatting as existing content.
Do NOT add any preamble or explanation. Output ONLY the new markdown section(s) to append."""


def call_api(prompt: str, system: str, max_tokens: int = 4000) -> str:
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": prompt}],
        max_completion_tokens=max_tokens,
        temperature=0.3,
    )
    return resp.choices[0].message.content.strip()


def load(lang: str, slug: str) -> dict:
    with open(f"{BASE}/{lang}/{slug}.json") as f:
        return json.load(f)


def save(lang: str, slug: str, d: dict):
    with open(f"{BASE}/{lang}/{slug}.json", "w") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)


# ─── ISSUE 1: AR articles missing FAQ ─────────────────────────────────────────

def fix_ar_ngor_surf_guide():
    """Add FAQ section to ar/ngor-surf-guide-right-left."""
    slug = "ngor-surf-guide-right-left"
    en = load("en", slug)
    ar = load("ar", slug)

    # Extract EN FAQ section
    cm_en = en["content_markdown"]
    faq_match = re.search(r'(## FAQ\s*\n[\s\S]+)', cm_en)
    if not faq_match:
        print(f"  No EN FAQ found for {slug}")
        return

    faq_en = faq_match.group(1).strip()

    prompt = f"""Translate this FAQ section from English to Arabic for a surf camp blog article about Ngor Island waves.

English FAQ:
{faq_en}

Translate to Arabic. Use ## FAQ as the heading (keep it in English as that's consistent with the article). 
Keep the markdown bold/question formatting. Output ONLY the translated FAQ section."""

    faq_ar = call_api(prompt, SYSTEM_TRANSLATE, max_tokens=2000)

    cm_ar = ar["content_markdown"].rstrip()
    cm_ar += f"\n\n{faq_ar}\n"
    ar["content_markdown"] = cm_ar
    save("ar", slug, ar)
    print(f"  FIXED FAQ: ar/{slug}")


def fix_ar_week():
    """Fix broken content end + add FAQ to ar/week-at-premium-surf-camp-ngor-island."""
    slug = "week-at-premium-surf-camp-ngor-island"
    en = load("en", slug)
    ar = load("ar", slug)

    cm_ar = ar["content_markdown"]

    # Fix broken end: remove the leftover "في \n.\n" pattern
    # The broken part is at the very end with "في \n.\n"
    cm_ar = re.sub(r'\s+في\s*\n\s*\.\s*\n?$', '.', cm_ar)
    cm_ar = cm_ar.rstrip()

    # Extract EN FAQ section
    cm_en = en["content_markdown"]
    faq_match = re.search(r'(## FAQ\s*\n[\s\S]+)', cm_en)
    if not faq_match:
        print(f"  No EN FAQ found for {slug}")
        return

    faq_en = faq_match.group(1).strip()

    prompt = f"""Translate this FAQ section from English to Arabic for a surf camp blog article about a week at Ngor Island surf camp.

English FAQ:
{faq_en}

Translate to Arabic. Use ## FAQ as the heading. Keep the markdown bold/question formatting. 
Output ONLY the translated FAQ section."""

    faq_ar = call_api(prompt, SYSTEM_TRANSLATE, max_tokens=2000)

    cm_ar += f"\n\n{faq_ar}\n"
    ar["content_markdown"] = cm_ar
    save("ar", slug, ar)
    print(f"  FIXED (broken end + FAQ): ar/{slug}")


# ─── ISSUE 2: IT week-at-premium missing 3 sections ──────────────────────────

def fix_it_week():
    """Translate and add 3 missing sections to it/week-at-premium-surf-camp-ngor-island."""
    slug = "week-at-premium-surf-camp-ngor-island"
    en = load("en", slug)
    it = load("it", slug)

    cm_en = en["content_markdown"]
    cm_it = it["content_markdown"]

    # IT has: Contents, Day-by-day, Afternoons, More than just surf, FAQ
    # EN has: Contents, Why reset, Day-by-day, Afternoons, Midweek confidence, Evenings, How to plan, FAQ
    # Missing in IT: Midweek is when confidence clicks, Evenings on Ngor, How to plan your stay

    # Extract missing EN sections
    missing_sections = []
    for heading in [
        "## Midweek is when confidence clicks",
        "## Evenings on Ngor are pure Atlantic magic",
        "## How to plan your Ngor Island stay",
    ]:
        m = re.search(rf'({re.escape(heading)}[\s\S]+?)(?=\n## |\Z)', cm_en)
        if m:
            missing_sections.append(m.group(1).strip())

    if not missing_sections:
        print(f"  Could not extract EN missing sections for {slug}")
        return

    sections_en = "\n\n".join(missing_sections)

    prompt = f"""Translate these blog sections from English to Italian for an article about a week at a premium surf camp on Ngor Island, Dakar, Senegal.

Sections to translate:
{sections_en}

Keep markdown formatting. Translate naturally and vividly. Output ONLY the translated sections."""

    new_sections_it = call_api(prompt, SYSTEM_TRANSLATE, max_tokens=3000)

    # Insert before FAQ section
    faq_match = re.search(r'\n## FAQ', cm_it)
    if faq_match:
        insert_pos = faq_match.start()
        cm_it = cm_it[:insert_pos] + f"\n\n{new_sections_it}\n" + cm_it[insert_pos:]
    else:
        cm_it = cm_it.rstrip() + f"\n\n{new_sections_it}\n"

    it["content_markdown"] = cm_it
    save("it", slug, it)
    print(f"  FIXED (3 missing sections): it/{slug}")


# ─── ISSUE 3: FR/IT dakar-surf-spots missing sections ────────────────────────

def fix_dakar_surf_spots(lang: str):
    """Add missing sections to fr/it dakar-surf-spots-for-every-level."""
    slug = "dakar-surf-spots-for-every-level"
    en = load("en", slug)
    art = load(lang, slug)

    cm_en = en["content_markdown"]
    cm_art = art["content_markdown"]

    # Check which EN sections are represented
    en_sections = re.findall(r'^## .+', cm_en, re.MULTILINE)
    art_sections = len(re.findall(r'^## ', cm_art, re.MULTILINE))

    # Skip "Contents" - it's a TOC not real content
    real_en_sections = [s for s in en_sections if s != '## Contents']
    print(f"  {lang}/dakar: has {art_sections} sections (EN real: {len(real_en_sections)})")

    # Extract sections present in EN but likely missing in translation
    # EN: Ngor Island (versatile base) + Practical Tips sections seem to be commonly merged/missing
    # Find sections that are missing
    missing = []
    for heading in ["## Practical Tips for Choosing the Right Dakar Surf Spot Each Day",
                    "## Ngor Island: The Most Versatile Base in Dakar"]:
        m = re.search(rf'({re.escape(heading)}[\s\S]+?)(?=\n## |\Z)', cm_en)
        if m:
            section_text = m.group(1).strip()
            # Check if a similar section exists in translated content
            # Simple heuristic: if translation is already ~95% of EN, likely OK
            ratio = len(cm_art) / len(cm_en)
            if ratio < 0.90:
                missing.append(section_text)

    if not missing:
        print(f"  {lang}/dakar: content ratio OK, skipping")
        return

    lang_names = {"fr": "French", "it": "Italian"}
    lang_name = lang_names.get(lang, lang)

    sections_en = "\n\n".join(missing)
    prompt = f"""Translate these blog sections from English to {lang_name} for an article about surf spots in Dakar, Senegal.

Sections to translate:
{sections_en}

Keep markdown formatting. Translate naturally. Output ONLY the translated sections."""

    new_sections = call_api(prompt, SYSTEM_TRANSLATE, max_tokens=2500)

    # Insert before FAQ
    faq_markers = ['## FAQ', '## Preguntas frecuentes', '## الأسئلة الشائعة']
    for marker in faq_markers:
        if marker in cm_art:
            idx = cm_art.index(marker)
            cm_art = cm_art[:idx] + f"{new_sections}\n\n" + cm_art[idx:]
            break
    else:
        cm_art = cm_art.rstrip() + f"\n\n{new_sections}\n"

    art["content_markdown"] = cm_art
    save(lang, slug, art)
    print(f"  FIXED (missing sections): {lang}/{slug}")


# ─── DE week-at-premium: check if needs fixing ───────────────────────────────

def fix_de_week():
    """DE week has 5 sections at 93% length - check if truly needs sections added."""
    slug = "week-at-premium-surf-camp-ngor-island"
    en = load("en", slug)
    de = load("de", slug)

    cm_en = en["content_markdown"]
    cm_de = de["content_markdown"]

    ratio = len(cm_de) / len(cm_en)
    de_secs = re.findall(r'^## .+', cm_de, re.MULTILINE)
    print(f"  de/week: ratio={ratio:.2f}, sections={de_secs}")

    # At 93% with 5 real sections (German-specific added), it's OK
    # EN has "Afternoons", "Midweek", "Evenings" as separate sections
    # DE merged some but has equivalent content at 93%
    # Only fix if ratio < 0.85
    if ratio >= 0.85:
        print(f"  de/week: ratio {ratio:.2f} >= 0.85, skipping")
        return

    # Else translate missing sections
    missing_en_headings = [
        "## Afternoons on Ngor Island are where the trip becomes more than surfing",
        "## Midweek is when confidence clicks, and the island starts to feel like home",
        "## Evenings on Ngor are pure Atlantic magic",
    ]
    missing = []
    for heading in missing_en_headings:
        m = re.search(rf'({re.escape(heading)}[\s\S]+?)(?=\n## |\Z)', cm_en)
        if m:
            missing.append(m.group(1).strip())

    if not missing:
        print("  de/week: could not extract missing sections")
        return

    sections_en = "\n\n".join(missing)
    prompt = f"""Translate these blog sections from English to German for an article about a week at a premium surf camp on Ngor Island, Dakar, Senegal.

{sections_en}

Keep markdown formatting. Translate naturally and vividly. Output ONLY the translated sections."""

    new_sections = call_api(prompt, SYSTEM_TRANSLATE, max_tokens=2500)

    faq_match = re.search(r'\n## FAQ', cm_de)
    if faq_match:
        insert_pos = faq_match.start()
        cm_de = cm_de[:insert_pos] + f"\n\n{new_sections}\n" + cm_de[insert_pos:]
    else:
        cm_de = cm_de.rstrip() + f"\n\n{new_sections}\n"

    de["content_markdown"] = cm_de
    save("de", slug, de)
    print(f"  FIXED: de/{slug}")


if __name__ == "__main__":
    if not API_KEY:
        sys.exit("ERROR: OPENAI_API_KEY not set")

    print("=== Fixing remaining article issues ===")
    print()

    print("1. AR ngor-surf-guide-right-left → add FAQ")
    fix_ar_ngor_surf_guide()

    print("2. AR week-at-premium → fix broken end + add FAQ")
    fix_ar_week()

    print("3. IT week-at-premium → add 3 missing sections")
    fix_it_week()

    print("4. FR dakar-surf-spots → check + fix missing sections")
    fix_dakar_surf_spots("fr")

    print("5. IT dakar-surf-spots → check + fix missing sections")
    fix_dakar_surf_spots("it")

    print("6. DE week-at-premium → check if needs fixing")
    fix_de_week()

    print()
    print("=== Done ===")
