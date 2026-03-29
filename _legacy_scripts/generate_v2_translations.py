#!/usr/bin/env python3
"""
Generate translated v2 articles (with visual blocks) for fr, es, it, de.
Strategy:
  1. Read each English v2 article (which has TIP/FACT/EXPERT/SUMMARY/CHECKLIST blocks)
  2. Read the existing translated article (v1 - full body in target language)
  3. Call OpenAI to inject translated blocks at appropriate positions in the translated content
  4. Save as articles_v2/{lang}/{slug}.json
"""
import json, os, re, sys, time

try:
    from openai import OpenAI
except ImportError:
    sys.exit("pip install openai first")

OPENAI_KEY = "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"
client = OpenAI(api_key=OPENAI_KEY)

CONTENT = "/Users/simonazoulay/SurfCampSenegal/content"
V2_EN   = f"{CONTENT}/articles_v2/en"
V1_DIR  = f"{CONTENT}/articles"
V2_OUT  = f"{CONTENT}/articles_v2"

LANGS = ["fr", "es", "it", "de"]
LANG_NAMES = {"fr": "French", "es": "Spanish", "it": "Italian", "de": "German"}

BLOCK_KW_MAP = {
    "fr": {"tip": "**CONSEIL:", "fact": "**FAIT:", "expert": "**EXPERT:", "summary": "**RÉSUMÉ:", "checklist": "**CHECKLIST:"},
    "es": {"tip": "**CONSEJO:", "fact": "**HECHO:", "expert": "**EXPERT:", "summary": "**RESUMEN:", "checklist": "**CHECKLIST:"},
    "it": {"tip": "**CONSIGLIO:", "fact": "**FATTO:", "expert": "**EXPERT:", "summary": "**SINTESI:", "checklist": "**CHECKLIST:"},
    "de": {"tip": "**TIPP:", "fact": "**FAKT:", "expert": "**EXPERT:", "summary": "**FAZIT:", "checklist": "**CHECKLIST:"},
}

ALL_BLOCK_KWS = [
    "**TIP:", "**CONSEIL:", "**TIPP:", "**CONSEJO:", "**CONSIGLIO:",
    "**NOTE:", "**REMARQUE:", "**HINWEIS:", "**NOTA:",
    "**FACT:", "**FAIT:", "**HECHO:", "**FATTO:", "**FAKT:",
    "**EXPERT:", "**QUOTE:", "**CITATION:", "**COACH:",
    "**CHECKLIST:", "**CHECK:",
    "**SUMMARY:", "**SYNTHÈSE:", "**RÉSUMÉ:", "**RESUMEN:", "**SINTESI:",
    "**FAZIT:", "**ZUSAMMENFASSUNG:", "**KEY TAKEAWAYS:",
    "**POINTS CLÉS:", "**PUNTI CHIAVE:", "**WICHTIGE PUNKTE:",
]

def detect_block_type(line):
    s = line.strip().upper()
    if any(s.startswith(k.upper()) for k in ["**TIP:", "**CONSEIL:", "**TIPP:", "**CONSEJO:", "**CONSIGLIO:"]):
        return "tip"
    if any(s.startswith(k.upper()) for k in ["**FACT:", "**FAIT:", "**HECHO:", "**FATTO:", "**FAKT:"]):
        return "fact"
    if any(s.startswith(k.upper()) for k in ["**EXPERT:", "**QUOTE:", "**CITATION:", "**COACH:"]):
        return "expert"
    if any(s.startswith(k.upper()) for k in ["**CHECKLIST:", "**CHECK:"]):
        return "checklist"
    if any(s.startswith(k.upper()) for k in ["**SUMMARY:", "**SYNTHÈSE:", "**RÉSUMÉ:", "**RESUMEN:", "**SINTESI:",
                                               "**FAZIT:", "**ZUSAMMENFASSUNG:", "**KEY TAKEAWAYS:",
                                               "**POINTS CLÉS:", "**PUNTI CHIAVE:", "**WICHTIGE PUNKTE:"]):
        return "summary"
    return None

def extract_blocks(md):
    """Extract all blocks from markdown with their type and content."""
    lines = md.split("\n")
    blocks = []
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        btype = detect_block_type(s)
        if btype:
            # Get content after keyword
            content_after = re.sub(r'^\*\*[^:]+:\*?\*?\s*', '', s).strip()
            block_lines = []
            if content_after:
                block_lines.append(content_after)
            j = i + 1
            while j < len(lines):
                ls = lines[j].strip()
                if not ls:
                    if block_lines:
                        break
                    j += 1
                    continue
                if ls.startswith('#') or any(ls.upper().startswith(k.upper()) for k in ALL_BLOCK_KWS):
                    break
                block_lines.append(ls)
                j += 1
            blocks.append({"type": btype, "content": "\n".join(block_lines)})
            i = j
        else:
            i += 1
    return blocks

def translate_blocks_to_lang(blocks, target_lang, article_title, existing_translated_md):
    """
    Call OpenAI once to inject translated blocks into the existing translated article.
    Returns enhanced markdown with blocks injected at appropriate positions.
    """
    lang_name = LANG_NAMES[target_lang]
    kws = BLOCK_KW_MAP[target_lang]
    
    # Format blocks for the prompt
    blocks_text = ""
    for b in blocks:
        kw = kws.get(b["type"], f"**{b['type'].upper()}:")
        blocks_text += f"\n[{b['type'].upper()}]\n{b['content']}\n"
    
    prompt = f"""You are a surf content editor. Your task is to enhance a {lang_name} surf article by inserting translated visual information blocks at appropriate positions.

ARTICLE TITLE: {article_title}

ENGLISH BLOCKS TO TRANSLATE AND INSERT:
{blocks_text}

EXISTING {lang_name.upper()} ARTICLE (markdown):
{existing_translated_md}

INSTRUCTIONS:
1. Translate each block content to {lang_name}. Keep the meaning faithful to the English.
2. Insert each block at a LOGICAL position within the existing {lang_name} article:
   - TIP block: after a practical advice section or near the middle
   - FACT block: after a historical or factual mention
   - EXPERT block: near an experience/coaching section
   - SUMMARY/RÉSUMÉ block: near the end of the main content (before FAQ if any)
   - CHECKLIST block: near practical tips or at the end
3. Use these EXACT keyword prefixes for each block type in {lang_name}:
   - tip: {kws['tip']}
   - fact: {kws['fact']}
   - expert: {kws['expert']}
   - summary: {kws['summary']}
   - checklist: {kws['checklist']}
4. For SUMMARY and CHECKLIST, list items with "- " bullet format on separate lines.
5. Keep the rest of the article EXACTLY as is.
6. Return ONLY the complete enhanced markdown, no extra commentary.

Format each block like this (example for TIP):
{kws['tip']} [translated tip text here]

For multi-line blocks (SUMMARY, CHECKLIST):
{kws['summary']}
- [point 1]
- [point 2]
- [point 3]
"""

    resp = client.chat.completions.create(
        model="gpt-4.1-mini-2025-04-14",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4000,
        temperature=0.3,
    )
    return resp.choices[0].message.content.strip()

def main():
    # Create output directories
    for lang in LANGS:
        os.makedirs(f"{V2_OUT}/{lang}", exist_ok=True)
    
    v2_files = sorted(f for f in os.listdir(V2_EN) if f.endswith(".json"))
    print(f"Processing {len(v2_files)} articles × {len(LANGS)} languages...")
    
    total = 0
    errors = 0
    
    for fname in v2_files:
        slug = fname.replace(".json", "")
        
        # Load English v2 article
        with open(f"{V2_EN}/{fname}") as f:
            en_art = json.load(f)
        
        en_md = en_art.get("content_markdown", "")
        en_blocks = extract_blocks(en_md)
        
        if not en_blocks:
            print(f"  ⚠️  {slug}: no blocks in EN v2, skipping")
            continue
        
        print(f"\n📄 {slug} ({len(en_blocks)} blocks)")
        
        for lang in LANGS:
            out_path = f"{V2_OUT}/{lang}/{fname}"
            
            # Skip if already exists
            if os.path.exists(out_path):
                print(f"  ✓ {lang}: already exists, skipping")
                continue
            
            # Load existing translated v1 article
            v1_path = f"{V1_DIR}/{lang}/{fname}"
            if not os.path.exists(v1_path):
                print(f"  ⚠️  {lang}: no v1 article found at {v1_path}")
                continue
            
            with open(v1_path) as f:
                trans_art = json.load(f)
            
            trans_md = trans_art.get("content_markdown", "").strip()
            if not trans_md:
                print(f"  ⚠️  {lang}: empty translated content")
                continue
            
            print(f"  → {lang}: translating blocks...", end=" ", flush=True)
            
            try:
                enhanced_md = translate_blocks_to_lang(
                    en_blocks, lang,
                    trans_art.get("title", en_art.get("title", "")),
                    trans_md
                )
                
                # Build v2 translated article
                out_art = dict(trans_art)
                out_art["content_markdown"] = enhanced_md
                # Update word count
                out_art["word_count_estimate"] = len(enhanced_md.split())
                
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(out_art, f, ensure_ascii=False, indent=2)
                
                # Count blocks in result
                result_blocks = extract_blocks(enhanced_md)
                print(f"✅ {len(result_blocks)} blocks inserted")
                total += 1
                
            except Exception as e:
                print(f"❌ ERROR: {e}")
                errors += 1
            
            time.sleep(0.5)  # Be nice to API
    
    print(f"\n✅ Done! {total} articles created, {errors} errors")

if __name__ == "__main__":
    main()
