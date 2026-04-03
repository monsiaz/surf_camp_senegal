#!/usr/bin/env python3
"""
Fix article completeness across all languages:
1. Severely truncated articles (ratio < 0.55): detect last good section,
   translate all missing EN sections, append.
2. All other articles missing FAQ: translate EN FAQ section, append.

Run: python3 scripts/fix_article_completeness.py
"""
import json, os, re, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed

import openai

API_KEY = (os.environ.get("OPENAI_API_KEY") or "").strip()
MODEL   = (os.environ.get("OPENAI_MODEL")    or "gpt-5.4-2026-03-05").strip()
if not API_KEY:
    raise SystemExit("Set OPENAI_API_KEY first.")

client = openai.OpenAI(api_key=API_KEY)

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "content", "articles_v2")

LANG_NAMES = {
    "fr": "French (modern, surf-oriented tone)",
    "es": "Spanish (Castilian, surf-oriented tone)",
    "it": "Italian (modern, surf-oriented tone)",
    "de": "German (modern, surf-oriented tone)",
}

SYSTEM = (
    "You are a professional translator specialising in surf tourism content. "
    "Rules:\n"
    "- Preserve ALL markdown formatting (# ## ### **bold** *italic* - lists > blockquotes)\n"
    "- Keep proper nouns unchanged: Ngor, Dakar, Senegal, Ngor Right, Ngor Left, "
    "Teranga, Ngor Island, ISA, Abu Diallo, Cap-Vert\n"
    "- Preserve special block labels (translate the label itself if it has a translation): "
    "**TIP:** **FACT:** **EXPERT:** **SUMMARY:** **CHECKLIST:** **Q:** **A:**\n"
    "- Do NOT summarise, shorten or add content. Translate faithfully.\n"
    "- Output ONLY the translated markdown, no preamble, no explanation."
)


# ── helpers ────────────────────────────────────────────────────────────────

def _call(text: str, lang: str, max_tokens: int = 6000) -> str:
    lang_desc = LANG_NAMES.get(lang, lang)
    user_msg  = f"Translate to {lang_desc}:\n\n{text}"
    for attempt in range(4):
        try:
            r = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM},
                    {"role": "user",   "content": user_msg},
                ],
                max_completion_tokens=max_tokens,
                temperature=0.3,
            )
            return r.choices[0].message.content.strip()
        except Exception as exc:
            wait = 2 ** attempt
            print(f"    API error (attempt {attempt+1}): {exc} — retrying in {wait}s")
            time.sleep(wait)
    return text  # fallback: return original


def load_article(lang: str, slug: str) -> dict:
    p = os.path.join(BASE, lang, f"{slug}.json")
    if not os.path.exists(p):
        return {}
    with open(p) as f:
        return json.load(f)


def save_article(lang: str, slug: str, data: dict):
    p = os.path.join(BASE, lang, f"{slug}.json")
    with open(p, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def en_sections(slug: str) -> list[str]:
    """Return list of EN sections split at '## ' boundaries, preserving intro."""
    art = load_article("en", slug)
    cm  = art.get("content_markdown", "")
    # Split while keeping the separator
    parts = re.split(r'\n(?=## )', cm)
    return parts  # parts[0] = intro+H1, parts[1..] = ## sections


def get_en_faq(slug: str) -> str:
    art = load_article("en", slug)
    cm  = art.get("content_markdown", "")
    idx = cm.find("\n## FAQ")
    if idx == -1:
        return ""
    return cm[idx + 1:].strip()   # strip leading newline


# ── core fixers ────────────────────────────────────────────────────────────

def fix_truncated(lang: str, slug: str) -> str:
    """
    For severely truncated translations:
    1. Find the last ## section heading present in the translated article.
    2. Find that same section in EN (by position/index).
    3. Extract everything that follows it in EN (next sections + FAQ).
    4. Translate that block and append to the cleaned translated article
       (removing any garbled tail after the last good section).
    """
    art = load_article(lang, slug)
    if not art:
        return f"SKIP: {lang}/{slug} not found"

    lang_cm = art.get("content_markdown", "")
    en_parts = en_sections(slug)           # EN split by ## boundaries

    # --- find last ## heading in translated article ---
    lang_h2s = re.findall(r'^## .+', lang_cm, re.MULTILINE)

    if not lang_h2s:
        # No sections at all – translate everything after the EN intro
        missing_block = "\n\n".join(en_parts[1:])
    else:
        last_lang_h2 = lang_h2s[-1]

        # Find which EN section index corresponds to the last translated heading.
        # We match by order (the k-th ## in lang = k-th ## in EN).
        en_h2_parts = [p for p in en_parts if re.match(r'^## ', p)]
        k = len(lang_h2s)           # how many ## sections are in translated article
        # everything from index k onwards is missing
        if k >= len(en_h2_parts):
            return f"OK (already complete?): {lang}/{slug}"
        missing_parts = en_h2_parts[k:]
        missing_block = "\n\n".join(missing_parts)

    # --- clean the translated article: remove garbled tail after last good section ---
    if lang_h2s:
        last_h2 = lang_h2s[-1]
        idx = lang_cm.rfind(last_h2)
        # Keep everything up to the end of that section's last complete paragraph.
        # Simple heuristic: find the last complete sentence before any broken inline link.
        section_body = lang_cm[idx:]
        # Remove broken [LINK:...] if partially cut off
        section_body = re.sub(r'\[.*?→.*?(?:\]|$)', '', section_body)
        # Remove stray **CHECKLIST:** or **RÉSUMÉ:** etc. that belong to a later section
        # (they'll come back via the translation)
        section_body = re.sub(
            r'\n\*\*(?:CHECKLIST|RÉSUMÉ|ZUSAMMENFASSUNG|RESUMEN|RIEPILOGO'
            r'|CHECKLIJST|LISTE DE CONTRÔLE)[^*]*\*\*:?.*',
            '', section_body, flags=re.DOTALL
        )
        clean_tail = section_body.rstrip()
        lang_cm_clean = lang_cm[:idx] + clean_tail
    else:
        lang_cm_clean = lang_cm.rstrip()

    # --- translate missing EN block ---
    print(f"  [{lang}] translating {len(missing_block)} chars missing from {slug} ...")
    translated_missing = _call(missing_block, lang, max_tokens=8000)

    art["content_markdown"] = lang_cm_clean.rstrip() + "\n\n" + translated_missing + "\n"
    save_article(lang, slug, art)
    return f"FIXED (truncated): {lang}/{slug}"


def fix_faq_only(lang: str, slug: str) -> str:
    """Translate EN FAQ section and append to translated article."""
    en_faq = get_en_faq(slug)
    if not en_faq:
        return f"SKIP (no EN FAQ): {lang}/{slug}"

    art = load_article(lang, slug)
    if not art:
        return f"SKIP (lang file missing): {lang}/{slug}"

    # Don't add if FAQ already present
    if "## FAQ" in art.get("content_markdown", ""):
        return f"SKIP (FAQ already present): {lang}/{slug}"

    title = art.get("title", slug)
    print(f"  [{lang}] translating FAQ for {slug} ...")
    translated_faq = _call(en_faq, lang, max_tokens=3000)

    cm = art.get("content_markdown", "").rstrip()
    art["content_markdown"] = cm + "\n\n" + translated_faq + "\n"
    save_article(lang, slug, art)
    return f"FIXED (FAQ): {lang}/{slug}"


# ── main ───────────────────────────────────────────────────────────────────

def main():
    LANGS = ["fr", "es", "it", "de"]

    # Load EN article info
    en_dir = os.path.join(BASE, "en")
    en_info: dict[str, dict] = {}
    for fname in os.listdir(en_dir):
        if not fname.endswith(".json"):
            continue
        with open(os.path.join(en_dir, fname)) as f:
            d = json.load(f)
        slug = fname[:-5]
        cm   = d.get("content_markdown", "")
        en_info[slug] = {
            "len": len(cm),
            "has_faq": "## FAQ" in cm,
        }

    # Build work queue
    truncated_jobs: list[tuple[str, str]] = []  # (lang, slug) for severe truncation
    faq_jobs:       list[tuple[str, str]] = []  # (lang, slug) for missing FAQ only

    for lang in LANGS:
        lang_dir = os.path.join(BASE, lang)
        if not os.path.isdir(lang_dir):
            continue
        for fname in os.listdir(lang_dir):
            if not fname.endswith(".json"):
                continue
            with open(os.path.join(lang_dir, fname)) as f:
                art = json.load(f)
            slug    = art.get("original_en_slug") or art.get("hreflang_en") or fname[:-5]
            lang_cm = art.get("content_markdown", "")
            has_faq = "## FAQ" in lang_cm

            if slug not in en_info:
                continue
            ei = en_info[slug]
            ratio = len(lang_cm) / ei["len"] if ei["len"] else 1.0

            if ratio < 0.55:
                truncated_jobs.append((lang, fname[:-5]))
            elif ei["has_faq"] and not has_faq:
                faq_jobs.append((lang, fname[:-5]))

    print(f"Jobs: {len(truncated_jobs)} truncated, {len(faq_jobs)} missing FAQ")

    results = []

    # --- fix truncated first (sequential to avoid rate limits) ---
    for lang, slug in truncated_jobs:
        r = fix_truncated(lang, slug)
        print(" ", r)
        results.append(r)
        time.sleep(1)

    # --- fix missing FAQ in parallel (8 workers) ---
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(fix_faq_only, lang, slug): (lang, slug)
                   for lang, slug in faq_jobs}
        for fut in as_completed(futures):
            r = fut.result()
            print(" ", r)
            results.append(r)

    fixed   = sum(1 for r in results if r.startswith("FIXED"))
    skipped = sum(1 for r in results if r.startswith("SKIP"))
    print(f"\nDone. Fixed={fixed}, Skipped={skipped}")


if __name__ == "__main__":
    main()
