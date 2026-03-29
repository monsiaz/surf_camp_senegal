"""
Regenerate all 30 EN articles at 3000-3500 words with:
- Table of contents
- Visual blocks (TIP, SUMMARY, EXPERT, FACT, CHECKLIST)
- Persona sections (which surfer is this for)
- Internal links
- No em dashes
30 parallel workers
"""
import json, os, re, time
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

OPENAI_KEY   = "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"
MODEL        = "gpt-5.4-2026-03-05"
ARTICLES_DIR = "/Users/simonazoulay/SurfCampSenegal/content/articles_v2/en"
OLD_ARTICLES = "/Users/simonazoulay/SurfCampSenegal/content/articles/en"
os.makedirs(ARTICLES_DIR, exist_ok=True)

client     = OpenAI(api_key=OPENAI_KEY)
lock       = threading.Lock()
done_count = [0]

PERSONAS_FOR_ARTICLES = {
    "hero":  ["maya-beginner", "jake-weekend", "carlos-globetrotter"],
    "seo":   ["jake-weekend", "lena-committed", "carlos-globetrotter"],
    "surf-conditions-spots": ["carlos-globetrotter", "jake-weekend"],
    "island-life-surf-camp": ["amara-soul", "maya-beginner"],
    "coaching-progression":  ["lena-committed", "jake-weekend"],
}
ALL_PERSONAS = {
    "maya-beginner":   {"name":"Maya","type":"The Curious Beginner","en":"Perfect for complete beginners planning their first surf trip"},
    "jake-weekend":    {"name":"Jake","type":"The Weekend Warrior","en":"Great if you surf a few times a year and want real progression"},
    "lena-committed":  {"name":"Lena","type":"The Committed Improver","en":"Ideal for surfers serious about technique and video coaching"},
    "carlos-globetrotter":{"name":"Carlos","type":"The Globe-Trotter","en":"For experienced surfers seeking world-class destinations"},
    "amara-soul":      {"name":"Amara","type":"The Soul Surfer","en":"Perfect if you surf for lifestyle, culture and connection"},
}

SITE_CONTEXT = """
Ngor Surfcamp Teranga | Premium surf camp | Ngor Island (Ile de Ngor), Dakar, Senegal
Licensed by Senegalese Federation of Surfing | All levels | Video coaching
World-class waves: Ngor Right (powerful point break, intermediate+) + Ngor Left (all levels)
Featured in The Endless Summer (1964) | No cars on island | Atlantic Ocean
WhatsApp: +221 78 925 70 25 | surfcampsenegal.com | info@surfcampsenegal.com
Pool, sea views, daily Senegalese meals, boat transfers, daily surf guiding
Top markets: France, Germany, Spain, Italy, UK, Senegal
"""

def log(msg):
    with lock: print(msg, flush=True)

def gpt(prompt, temp=0.75, tokens=5000):
    r = client.chat.completions.create(
        model=MODEL,
        messages=[{"role":"user","content":prompt}],
        temperature=temp,
        max_completion_tokens=tokens,
    )
    return r.choices[0].message.content

def fix_em(text):
    return re.sub(r',\s*,',',', str(text).replace(" — ",", ").replace("—",",").replace("\u2014",",").replace(" – ",", ").replace("–",","))

def art_personas(art):
    cat = art.get("category","")
    tp  = art.get("type","seo")
    pids = PERSONAS_FOR_ARTICLES.get(cat, PERSONAS_FOR_ARTICLES.get(tp, ["jake-weekend","carlos-globetrotter"]))
    return [ALL_PERSONAS[pid] for pid in pids if pid in ALL_PERSONAS][:2]

def generate_article(art):
    en_slug  = art["slug"]
    out_file = f"{ARTICLES_DIR}/{en_slug}.json"
    if os.path.exists(out_file) and os.path.getsize(out_file) > 5000:
        existing = json.load(open(out_file))
        if existing.get("word_count_estimate",0) >= 2500:
            log(f"  [skip] #{art['id']}: {art['title'][:50]} ({existing.get('word_count_estimate',0)}w)")
            return en_slug, "skipped"

    personas = art_personas(art)
    persona_str = " | ".join([f"{p['name']} ({p['type']}): {p['en']}" for p in personas])
    cat_info = art.get("category","")

    prompt = f"""You are an expert surf travel journalist who has spent years at Ngor Island, Senegal.
Write with authentic passion, vivid imagery, and insider knowledge. NOT generic AI content.
NEVER use em dashes (—). Use commas, periods, or colons instead.

{SITE_CONTEXT}

ARTICLE TO WRITE:
Title: {art['title']}
Category: {cat_info}
Focus keyword: {art['focus_keyword']}
Secondary keywords: {', '.join(art.get('secondary_keywords',[]))}
Type: {art.get('type','seo')} | Audience: {art.get('target_audience','')}
Brief: {art.get('brief','')}

TARGET PERSONAS: {persona_str}

Write a COMPLETE 3000-3500 word article. Use this EXACT structure:

META: [compelling meta description, max 155 chars, focus keyword early]

PERSONAS: [slug1,slug2] (choose 2 from: maya-beginner, jake-weekend, lena-committed, carlos-globetrotter, amara-soul)

READING_TIME: [X min]

# [H1 - compelling, keyword-rich title]

[Hook: 250-word vivid opening scene or surprising fact. Grab attention immediately. Set in Ngor/Senegal.]

## Contents
- [Section 1 title]
- [Section 2 title]
- [Section 3 title]
- [Section 4 title]
- [Section 5 title]
- [Section 6 title]
- [FAQ]

## [H2 - Section 1, includes focus keyword]
[400-450 words of rich, specific content with local knowledge]

> [Pull quote or memorable insight from this section]

## [H2 - Section 2]
[400-450 words]

**TIP:** [Specific actionable tip related to this section, 50-80 words]

## [H2 - Section 3]
[400-450 words]

**SUMMARY:** [Key takeaways from sections 1-3, 3-4 bullet points, 80-100 words total]

## [H2 - Section 4]
[400-450 words]

**FACT:** [Interesting stat or verified fact about surfing/Senegal/Ngor, with context, 50-70 words]

## [H2 - Section 5]
[350-400 words]

**EXPERT:** [Quote-style insight from Kofi Mensah (local surf instructor) or Sophie Renard (surf travel writer) or Luca Ferretti (ISA coach), 60-80 words]

## [H2 - Section 6: Practical tips or "What to do"]
[350-400 words]

**CHECKLIST:** [5-7 actionable items as a checklist]

## Ready to Ride? Book at Ngor Surfcamp Teranga
[200-word authentic CTA — specific, not generic. Mention exact features, WhatsApp +221 78 925 70 25, location Ngor Island]

## FAQ

**[Specific question about the article topic]**
[Answer: 80-100 words]

**[Second specific question]**
[Answer: 80-100 words]

**[Third question]**
[Answer: 70-90 words]

Include 3-4 internal links using: [LINK: anchor text -> /page-slug]
Target internal pages: /surf-house, /island, /surfing, /booking, /gallery, /faq, /blog"""

    try:
        content = fix_em(gpt(prompt, temp=0.78, tokens=5000))

        # Extract structured fields
        meta = ""
        personas_str = ""
        reading_time = "8"
        body = content

        lines = content.split("\n")
        body_lines = []
        skip_toc = False
        for line in lines:
            if line.startswith("META: "):
                meta = line.replace("META: ","").strip()
            elif line.startswith("PERSONAS: "):
                personas_str = line.replace("PERSONAS: ","").strip()
            elif line.startswith("READING_TIME: "):
                reading_time = line.replace("READING_TIME: ","").strip().replace(" min","")
            else:
                body_lines.append(line)
        body = "\n".join(body_lines).strip()

        words = len(body.split())
        data = {
            "id":           art["id"],
            "title":        fix_em(art["title"]),
            "slug":         en_slug,
            "category":     art.get("category",""),
            "focus_keyword":art["focus_keyword"],
            "secondary_keywords": art.get("secondary_keywords",[]),
            "type":         art.get("type","seo"),
            "hero_image_prompt": art.get("hero_image_prompt",""),
            "target_audience": art.get("target_audience",""),
            "lang":         "en",
            "meta_description": meta,
            "personas":     [p.strip() for p in personas_str.split(",") if p.strip()],
            "reading_time": reading_time,
            "content_markdown": body,
            "word_count_estimate": words,
        }
        with open(out_file,"w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        done_count[0] += 1
        log(f"  ✅ #{art['id']} [{done_count[0]}/30] {art['title'][:50]} ({words}w)")
        return en_slug, "done"
    except Exception as e:
        log(f"  ❌ #{art['id']} {art['title'][:40]}: {e}")
        return en_slug, f"error: {e}"

# Load strategy
strategy = json.load(open("/Users/simonazoulay/SurfCampSenegal/content/blog_strategy.json"))
arts = strategy["articles"]

print(f"=== Regenerating {len(arts)} articles at 3000-3500 words (30 workers) ===")
print(f"Output: {ARTICLES_DIR}\n")

with ThreadPoolExecutor(max_workers=30) as ex:
    futs = {ex.submit(generate_article, art): art for art in arts}
    for f in as_completed(futs): f.result()

# Summary
files  = [f for f in os.listdir(ARTICLES_DIR) if f.endswith(".json")]
total_words = 0
for fname in files:
    a = json.load(open(f"{ARTICLES_DIR}/{fname}"))
    total_words += a.get("word_count_estimate",0)
avg = total_words // len(files) if files else 0

print(f"\n{'='*60}")
print(f"ARTICLES REGENERATED: {len(files)}/30")
print(f"Average word count: {avg}")
print(f"Total words: {total_words:,}")
print(f"Output: {ARTICLES_DIR}")
