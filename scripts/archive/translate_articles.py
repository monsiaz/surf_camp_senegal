#!/usr/bin/env python3
"""
Translate all articles_v2/en/*.json to nl and ar.
Creates articles_v2/nl/ and articles_v2/ar/ with translated JSON files.
"""
import json, os, sys, time, glob, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import openai

API_KEY = (os.environ.get("OPENAI_API_KEY") or "").strip()
MODEL = (os.environ.get("OPENAI_MODEL") or "gpt-4o").strip()
if not API_KEY:
    raise SystemExit("Set OPENAI_API_KEY.")
client = openai.OpenAI(api_key=API_KEY)

BASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "content", "articles_v2")

SYSTEM_META = """You are a surf travel SEO copywriter and translator.
Translate the given article title and meta_description from English to Dutch (nl) and Arabic (ar/Morocco).
Keep surf terms natural, preserve proper nouns (Ngor, Dakar, Senegal, Ngor Right/Left, Teranga).
Return ONLY JSON: {"nl": {"title": "...", "meta_description": "..."}, "ar": {"title": "...", "meta_description": "..."}}"""

SYSTEM_CONTENT = """You are a professional surf travel writer and translator.
Translate the given markdown article from English to the target language.
- Preserve ALL markdown formatting (# headings, **bold**, *italic*, lists, > blockquotes)
- Keep proper nouns: Ngor, Dakar, Senegal, Ngor Right, Ngor Left, Teranga, Ben, Abu, Aram, ISA
- Keep HTML entities and special characters intact
- For Dutch (nl): natural, modern, friendly surf tone
- For Arabic (ar): Modern Standard Arabic, right-to-left aware (the markdown will be rendered RTL)
Return ONLY the translated markdown text, no JSON wrapper, no explanations."""

def translate_meta(title: str, meta: str) -> dict:
    """Returns {"nl": {...}, "ar": {...}}"""
    for attempt in range(3):
        try:
            r = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_META},
                    {"role": "user", "content": f'title: "{title}"\nmeta_description: "{meta}"'},
                ],
                max_completion_tokens=500,
                response_format={"type": "json_object"},
            )
            return json.loads(r.choices[0].message.content)
        except Exception as e:
            print(f"    ⚠️  meta attempt {attempt+1}: {e}")
            time.sleep(2)
    return {"nl": {"title": title, "meta_description": meta},
            "ar": {"title": title, "meta_description": meta}}


def translate_markdown(text: str, lang: str) -> str:
    """Translate markdown to target lang."""
    lang_name = "Dutch" if lang == "nl" else "Arabic"
    for attempt in range(3):
        try:
            r = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_CONTENT},
                    {"role": "user", "content": f"Translate to {lang_name}:\n\n{text}"},
                ],
                max_completion_tokens=16000,
            )
            return r.choices[0].message.content.strip()
        except Exception as e:
            print(f"    ⚠️  markdown {lang} attempt {attempt+1}: {e}")
            time.sleep(3)
    return text  # fallback: keep English


def make_slug(en_slug: str, lang: str) -> str:
    """Generate language-appropriate slug."""
    # Keep slug the same for nl (mostly intelligible), use transliteration hint for ar
    if lang == "nl":
        return en_slug  # Dutch URLs usually keep English-like slugs for SEO
    # For Arabic, keep the English slug (best for SEO)
    return en_slug


def process_article(filepath: str):
    with open(filepath, encoding="utf-8") as f:
        en = json.load(f)

    filename = os.path.basename(filepath)
    title = en.get("title", "")
    meta  = en.get("meta_description", "")
    content_md = en.get("content_markdown", "")

    print(f"  📄 {filename}")

    # Translate meta (title + meta_description)
    meta_result = translate_meta(title, meta)

    for lang in ["nl", "ar"]:
        out_dir = os.path.join(BASE, lang)
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, filename)

        if os.path.exists(out_path):
            print(f"     ✓ {lang} exists, skipping")
            continue

        print(f"     ↳ translating content → {lang}...")
        translated_md = ""
        if content_md:
            translated_md = translate_markdown(content_md, lang)

        # Build translated article JSON
        article = dict(en)
        article["lang"] = lang
        article["title"] = meta_result.get(lang, {}).get("title", title)
        article["meta_description"] = meta_result.get(lang, {}).get("meta_description", meta)
        article["content_markdown"] = translated_md
        article["slug"] = make_slug(en.get("slug", ""), lang)
        # Add hreflang reference back to EN
        article["hreflang_en"] = en.get("slug", "")

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(article, f, ensure_ascii=False, indent=2)
        print(f"     ✓ saved {lang}/{filename}")


if __name__ == "__main__":
    articles = sorted(glob.glob(os.path.join(BASE, "en", "*.json")))
    print(f"Translating {len(articles)} articles to nl + ar via GPT-5.4...\n")
    for i, path in enumerate(articles, 1):
        print(f"[{i}/{len(articles)}]", end=" ")
        process_article(path)
        time.sleep(0.5)  # gentle rate limiting

    print("\n✅ All articles translated!")
