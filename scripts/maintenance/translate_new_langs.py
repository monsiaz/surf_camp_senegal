#!/usr/bin/env python3
"""
Translate all 30 EN articles to Portuguese (pt) and Danish (da).
Uses GPT-4o with 20 parallel workers.
"""
import json, os, re, sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, str(Path(__file__).parent))
import env_utils
import openai

API_KEY = os.environ.get("OPENAI_API_KEY", "")
MODEL   = "gpt-4o"   # Faster + cheaper for translation
WORKERS = 20

ROOT    = Path(__file__).parent.parent
EN_DIR  = ROOT / "content" / "articles_v2" / "en"
BASE    = ROOT / "content" / "articles_v2"

client = openai.OpenAI(api_key=API_KEY)

LANG_INFO = {
    "pt": {
        "name": "Portuguese (European, pt-PT)",
        "faq_heading": "## FAQ",
        "direction": "ltr",
    },
    "da": {
        "name": "Danish",
        "faq_heading": "## FAQ",
        "direction": "ltr",
    },
}

SYSTEM = """You are a professional surf travel copywriter and translator.
Translate the provided JSON fields from English to {lang_name} for a surf camp blog.

Rules:
- Translate: title, meta_description, content_markdown
- Do NOT translate: slug, original_en_slug, hreflang_en, tags
- Keep all markdown formatting (##, ###, **bold**, bullet points)
- Keep English brand names: Ngor Surfcamp Teranga, Ngor Island, Ngor Right, Ngor Left, Senegal, Dakar, FSS, WhatsApp
- Keep URLs and contact info unchanged
- Remove any [LINK: ...] patterns
- Translate naturally and fluently — not word-for-word
- The ## FAQ heading should remain "## FAQ" in English
- Output ONLY valid JSON with the same structure as input"""


def translate_article(lang: str, slug: str, en_data: dict):
    """Translate one EN article to target language."""
    out_path = BASE / lang / f"{slug}.json"
    if out_path.exists():
        # Already translated — verify it has content
        with open(out_path) as f:
            existing = json.load(f)
        if len(existing.get("content_markdown", "")) > 1000:
            return existing  # Skip
    
    lang_info = LANG_INFO[lang]
    
    # Build the payload to translate (only translatable fields)
    # Non-translatable fields to copy as-is
    static_fields = {
        "slug": slug,
        "original_en_slug": slug,
        "hreflang_en": f"/{slug}/",
        "tags": en_data.get("tags", []),
        "language": lang,
    }
    
    sys_prompt = SYSTEM.format(lang_name=lang_info["name"])
    
    def _call(user_text, max_tok=500):
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_text},
            ],
            max_completion_tokens=max_tok,
            temperature=0.2,
        )
        return resp.choices[0].message.content.strip()
    
    try:
        # 1. Translate title + meta (short call)
        short_payload = json.dumps({
            "title": en_data.get("title", ""),
            "meta_description": en_data.get("meta_description", ""),
        }, ensure_ascii=False)
        short_resp = _call(
            f"Translate this JSON from English to {lang_info['name']}. Output ONLY valid JSON:\n{short_payload}",
            max_tok=400
        )
        m = re.search(r'\{[\s\S]*\}', short_resp)
        if m:
            short_translated = json.loads(m.group(0))
        else:
            short_translated = {"title": en_data.get("title",""), "meta_description": en_data.get("meta_description","")}
        
        # 2. Translate content_markdown (large call)
        cm_en = en_data.get("content_markdown", "")
        cm_prompt = (
            f"Translate the following surf camp blog article from English to {lang_info['name']}.\n"
            f"Keep ALL markdown formatting (##, ###, **bold**, bullets, etc.).\n"
            f"Keep brand names: Ngor, Ngor Island, Ngor Right, Ngor Left, Senegal, Dakar, FSS unchanged.\n"
            f"Keep ## FAQ as '## FAQ' (don't translate the heading).\n"
            f"Remove any [LINK: ...] patterns.\n"
            f"Output ONLY the translated markdown text (no JSON, no explanation):\n\n"
            f"{cm_en}"
        )
        # Estimate tokens needed: ~1.5× input chars / 4 chars per token
        est_tokens = min(16000, max(4000, int(len(cm_en) * 1.5 / 4)))
        cm_translated = _call(cm_prompt, max_tok=est_tokens)
        
        # Clean up
        cm_translated = re.sub(r'\[LINK:[^\]]*\]', '', cm_translated)
        cm_translated = re.sub(r'\n{3,}', '\n\n', cm_translated)
        cm_translated = cm_translated.strip()
        
        result = {
            **static_fields,
            "title": short_translated.get("title", en_data.get("title", "")),
            "meta_description": short_translated.get("meta_description", en_data.get("meta_description", "")),
            "content_markdown": cm_translated,
        }
        
        # Save
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        return result
    
    except Exception as e:
        print(f"  [ERR] {lang}/{slug}: {e}")
        return None


def main():
    if not API_KEY:
        sys.exit("ERROR: OPENAI_API_KEY not set")
    
    # Collect EN articles
    en_articles = []
    for fp in sorted(EN_DIR.glob("*.json")):
        with open(fp) as f:
            data = json.load(f)
        en_articles.append((fp.stem, data))
    
    print(f"Found {len(en_articles)} EN articles to translate")
    
    for lang in ["pt", "da"]:
        (BASE / lang).mkdir(parents=True, exist_ok=True)
        print(f"\n=== Translating to {lang.upper()} ({LANG_INFO[lang]['name']}) ===")
        
        done = 0
        total = len(en_articles)
        
        with ThreadPoolExecutor(max_workers=WORKERS) as ex:
            futures = {
                ex.submit(translate_article, lang, slug, data): slug
                for slug, data in en_articles
            }
            for future in as_completed(futures):
                slug = futures[future]
                done += 1
                result = future.result()
                if result:
                    cm_len = len(result.get("content_markdown", ""))
                    print(f"  [{done}/{total}] ✓ {lang}/{slug} ({cm_len} chars)")
                else:
                    print(f"  [{done}/{total}] ✗ FAILED: {lang}/{slug}")
    
    print("\n✅ Translation complete!")


if __name__ == "__main__":
    main()
