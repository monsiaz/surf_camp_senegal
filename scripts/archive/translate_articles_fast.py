#!/usr/bin/env python3
"""
Fast parallel article translation: nl + ar from en.
Translates title, meta, and full content. Uses 3 parallel workers.
Each article = 1 API call for meta (both langs) + 1 call for content (both langs simultaneously).
"""
import json, os, sys, time, glob
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import openai

API_KEY = "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"
MODEL  = "gpt-5.4-2026-03-05"
client = openai.OpenAI(api_key=API_KEY)

BASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "content", "articles_v2")


def gpt_meta(title: str, meta: str) -> dict:
    """Single call → {nl:{title,meta_description}, ar:{...}}"""
    prompt = f"""Translate these surf article metadata strings from English to Dutch (nl) AND Arabic (ar) simultaneously.
title: "{title}"
meta_description: "{meta}"

Return JSON: {{"nl":{{"title":"...","meta_description":"..."}},"ar":{{"title":"...","meta_description":"..."}}}}
Keep proper nouns: Ngor, Dakar, Senegal, Ngor Right, Ngor Left, Teranga."""
    for attempt in range(3):
        try:
            r = client.chat.completions.create(
                model=MODEL,
                messages=[{"role":"user","content":prompt}],
                max_completion_tokens=600,
                response_format={"type":"json_object"},
            )
            return json.loads(r.choices[0].message.content)
        except Exception as e:
            time.sleep(2)
    return {"nl":{"title":title,"meta_description":meta},"ar":{"title":title,"meta_description":meta}}


def gpt_content_both(text: str) -> dict:
    """Single call → {nl:"...", ar:"..."} translated markdown."""
    prompt = f"""Translate this surf camp article from English to BOTH Dutch (nl) AND Arabic (ar) simultaneously.
Rules:
- Preserve ALL markdown (# ## ### **bold** *italic* - lists > blockquotes)
- Keep proper nouns: Ngor, Dakar, Senegal, Ngor Right, Ngor Left, Teranga, Ben, Abu, Aram, ISA
- Dutch: friendly modern surf tone
- Arabic: Modern Standard Arabic

Return JSON: {{"nl": "<full markdown in Dutch>", "ar": "<full markdown in Arabic>"}}

Article to translate:
{text}"""
    for attempt in range(3):
        try:
            r = client.chat.completions.create(
                model=MODEL,
                messages=[{"role":"user","content":prompt}],
                max_completion_tokens=16000,
                response_format={"type":"json_object"},
            )
            parsed = json.loads(r.choices[0].message.content)
            return parsed
        except Exception as e:
            print(f"    ⚠️ content attempt {attempt+1}: {e}")
            time.sleep(3)
    return {"nl": text, "ar": text}


def process_article(filepath: str) -> str:
    filename = os.path.basename(filepath)
    with open(filepath, encoding="utf-8") as f:
        en = json.load(f)

    title = en.get("title", "")
    meta  = en.get("meta_description", "")
    content_md = en.get("content_markdown", "")

    # Check if both nl and ar already exist
    nl_path = os.path.join(BASE, "nl", filename)
    ar_path = os.path.join(BASE, "ar", filename)
    nl_exists = os.path.exists(nl_path)
    ar_exists = os.path.exists(ar_path)
    if nl_exists and ar_exists:
        return f"  ✓ {filename} — already translated"

    # Translate meta
    meta_result = gpt_meta(title, meta)

    # Translate content (both langs in one call)
    content_result = {"nl": content_md, "ar": content_md}
    if content_md:
        content_result = gpt_content_both(content_md)

    # Save nl
    if not nl_exists:
        os.makedirs(os.path.join(BASE, "nl"), exist_ok=True)
        article_nl = dict(en)
        article_nl["lang"] = "nl"
        article_nl["title"] = meta_result.get("nl", {}).get("title", title)
        article_nl["meta_description"] = meta_result.get("nl", {}).get("meta_description", meta)
        article_nl["content_markdown"] = content_result.get("nl", content_md)
        article_nl["slug"] = en.get("slug", "")  # keep EN slug for SEO
        article_nl["hreflang_en"] = en.get("slug", "")
        with open(nl_path, "w", encoding="utf-8") as f:
            json.dump(article_nl, f, ensure_ascii=False, indent=2)

    # Save ar
    if not ar_exists:
        os.makedirs(os.path.join(BASE, "ar"), exist_ok=True)
        article_ar = dict(en)
        article_ar["lang"] = "ar"
        article_ar["title"] = meta_result.get("ar", {}).get("title", title)
        article_ar["meta_description"] = meta_result.get("ar", {}).get("meta_description", meta)
        article_ar["content_markdown"] = content_result.get("ar", content_md)
        article_ar["slug"] = en.get("slug", "")  # keep EN slug for SEO
        article_ar["hreflang_en"] = en.get("slug", "")
        with open(ar_path, "w", encoding="utf-8") as f:
            json.dump(article_ar, f, ensure_ascii=False, indent=2)

    return f"  ✅ {filename}"


if __name__ == "__main__":
    articles = sorted(glob.glob(os.path.join(BASE, "en", "*.json")))
    total = len(articles)
    print(f"Translating {total} articles (nl + ar) with 3 parallel workers...\n")

    completed = 0
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(process_article, p): p for p in articles}
        for future in as_completed(futures):
            try:
                msg = future.result()
                completed += 1
                print(f"[{completed}/{total}] {msg}")
            except Exception as e:
                print(f"  ❌ Error: {e}")

    print(f"\n✅ Done! nl={len(glob.glob(os.path.join(BASE,'nl','*.json')))} ar={len(glob.glob(os.path.join(BASE,'ar','*.json')))}")
