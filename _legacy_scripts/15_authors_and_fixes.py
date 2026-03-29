"""
- Generate 3 fictional author profile images (DALL-E)
- Fix ALL em dashes (—) in article JSON files → replace with proper punctuation
- Save author metadata JSON
"""
import json, os, re, requests
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed

OPENAI_KEY   = "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"
ARTICLES_DIR = "/Users/simonazoulay/SurfCampSenegal/content/articles"
AUTHORS_DIR  = "/Users/simonazoulay/SurfCampSenegal/content/authors"
DEMO_ASSETS  = "/Users/simonazoulay/SurfCampSenegal/cloudflare-demo/assets/images"

os.makedirs(AUTHORS_DIR, exist_ok=True)
client = OpenAI(api_key=OPENAI_KEY)

# ════════════════════════════════════════════════════════════════════════════════
# STEP 1 – Define author personas
# ════════════════════════════════════════════════════════════════════════════════
AUTHORS = [
    {
        "id": "kofi-mensah",
        "name": "Kofi Mensah",
        "role": {"en":"Surf Instructor & Local Guide","fr":"Instructeur Surf & Guide Local","es":"Instructor Surf & Guía Local","it":"Istruttore Surf & Guida Locale","de":"Surf-Instruktor & Ortskundiger"},
        "bio": {
            "en":"Born and raised in Dakar, Kofi has been surfing Ngor's waves since age 10. Licensed by the Senegalese Federation of Surfing, he brings 15 years of coaching experience and intimate knowledge of every break around the island.",
            "fr":"Né et élevé à Dakar, Kofi surfe les vagues de Ngor depuis l'âge de 10 ans. Agréé par la Fédération Sénégalaise de Surf, il apporte 15 ans d'expérience en coaching.",
            "es":"Nacido y criado en Dakar, Kofi surfea las olas de Ngor desde los 10 años. Licenciado por la Federación Senegalesa de Surf.",
            "it":"Nato e cresciuto a Dakar, Kofi surfa le onde di Ngor dall'età di 10 anni. Autorizzato dalla Federazione Senegalese di Surf.",
            "de":"In Dakar geboren und aufgewachsen, surft Kofi seit seinem 10. Lebensjahr die Wellen von Ngor. Lizenziert vom senegalesischen Surfverband.",
        },
        "categories": ["Surf Conditions & Spots"],
        "image_prompt": "Professional headshot of a confident young Senegalese man in his early 30s, outdoor natural light, slight smile, wearing a casual surf brand t-shirt, ocean blurred in background, photorealistic portrait, warm golden African light, authentic non-posed expression",
    },
    {
        "id": "sophie-renard",
        "name": "Sophie Renard",
        "role": {"en":"Surf Travel Writer","fr":"Rédactrice Voyage Surf","es":"Escritora de Viajes Surf","it":"Scrittrice di Viaggi Surf","de":"Surf-Reiseredakteurin"},
        "bio": {
            "en":"A freelance surf journalist from Bordeaux, France, Sophie has spent eight years chasing waves across Africa, Europe and Indonesia. She first visited Ngor in 2019 and has been returning ever since.",
            "fr":"Journaliste surf freelance de Bordeaux, Sophie a passé huit ans à chasser les vagues en Afrique, Europe et Indonésie.",
            "es":"Periodista surf freelance de Burdeos, Sophie ha pasado ocho años persiguiendo olas por África, Europa e Indonesia.",
            "it":"Giornalista surf freelance di Bordeaux, Sophie ha trascorso otto anni a inseguire le onde in Africa, Europa e Indonesia.",
            "de":"Als freie Surf-Journalistin aus Bordeaux verbrachte Sophie acht Jahre damit, Wellen in Afrika, Europa und Indonesien zu jagen.",
        },
        "categories": ["Island Life & Surf Camp"],
        "image_prompt": "Professional headshot of an attractive French woman in her late 20s, warm natural light, relaxed genuine smile, long sun-lightened hair, casual bohemian style, beach/ocean setting subtly blurred in background, photorealistic portrait, editorial travel photography style",
    },
    {
        "id": "luca-ferretti",
        "name": "Luca Ferretti",
        "role": {"en":"ISA Surf Coach","fr":"Coach Surf ISA","es":"Coach Surf ISA","it":"Coach Surf ISA","de":"ISA Surf-Coach"},
        "bio": {
            "en":"An ISA-certified surf coach from Sardinia, Luca specializes in video analysis and progression methodology. With 12 years of professional coaching across Europe and West Africa, he joined Ngor Surfcamp's team in 2022.",
            "fr":"Coach surf certifié ISA de Sardaigne, Luca se spécialise dans l'analyse vidéo et la méthodologie de progression.",
            "es":"Coach surf certificado ISA de Cerdeña, Luca se especializa en análisis de vídeo y metodología de progresión.",
            "it":"Coach surf certificato ISA dalla Sardegna, Luca è specializzato in analisi video e metodologia di progressione.",
            "de":"Ein ISA-zertifizierter Surf-Coach aus Sardinien, Luca spezialisiert sich auf Videoanalyse und Progressionsmethodik.",
        },
        "categories": ["Coaching & Progression"],
        "image_prompt": "Professional headshot of an athletic Italian man in his late 30s, tanned skin from outdoor life, confident relaxed expression, wearing a technical surf/sports polo, outdoor coastal light, slight stubble, photorealistic portrait, clean professional editorial look",
    },
]

# ════════════════════════════════════════════════════════════════════════════════
# STEP 2 – Generate author profile images
# ════════════════════════════════════════════════════════════════════════════════
print("=== Generating author profile images ===")

def gen_author_img(author):
    out_path = f"{AUTHORS_DIR}/{author['id']}.jpg"
    if os.path.exists(out_path) and os.path.getsize(out_path) > 20000:
        print(f"  [skip] {author['name']}")
        return author["id"], out_path

    print(f"  Generating: {author['name']}")
    prompt = author["image_prompt"] + "\n\nStyle: Clean editorial headshot, square crop 1:1, neutral background with slight bokeh, high resolution, no text, no watermarks, authentic human expression."

    for model, size in [("dall-e-3", "1024x1024")]:
        try:
            resp = client.images.generate(
                model=model, prompt=prompt, n=1, size=size, quality="hd"
            )
            url = resp.data[0].url
            img_bytes = requests.get(url, timeout=30).content
            with open(out_path, "wb") as f:
                f.write(img_bytes)
            # Also copy to demo assets
            demo_path = f"{DEMO_ASSETS}/author-{author['id']}.jpg"
            with open(demo_path, "wb") as f:
                f.write(img_bytes)
            print(f"  ✅ {author['name']} ({len(img_bytes)//1024}KB)")
            return author["id"], out_path
        except Exception as e:
            print(f"  ❌ {author['name']}: {e}")
    return author["id"], None

with ThreadPoolExecutor(max_workers=3) as ex:
    futs = {ex.submit(gen_author_img, a): a for a in AUTHORS}
    for f in as_completed(futs):
        f.result()

# Save authors JSON
authors_data = {a["id"]: {k: v for k, v in a.items() if k != "image_prompt"} for a in AUTHORS}
with open(f"{AUTHORS_DIR}/authors.json","w") as f:
    json.dump(authors_data, f, indent=2, ensure_ascii=False)
print("✅ Authors JSON saved")

# ════════════════════════════════════════════════════════════════════════════════
# STEP 3 – Remove ALL em dashes from article content
# ════════════════════════════════════════════════════════════════════════════════
print("\n=== Fixing em dashes in all articles ===")

def fix_emdash(text):
    if not text:
        return text
    # Replace em dash patterns
    # " — " → ", "
    text = text.replace(" — ", ", ")
    text = text.replace(" \u2014 ", ", ")
    # "—" alone → ","
    text = text.replace("—", ",")
    text = text.replace("\u2014", ",")
    # Also fix en dashes with spaces " – " → ", "
    text = text.replace(" – ", ", ")
    text = text.replace(" \u2013 ", ", ")
    # Clean up double commas
    text = re.sub(r',\s*,', ',', text)
    # Clean up comma+period
    text = re.sub(r',\.', '.', text)
    return text

total_fixed = 0
for lang in ["en","fr","es","it","de"]:
    lang_dir = f"{ARTICLES_DIR}/{lang}"
    if not os.path.exists(lang_dir):
        continue
    for fname in os.listdir(lang_dir):
        if not fname.endswith(".json") or fname.startswith("_"):
            continue
        fpath = f"{lang_dir}/{fname}"
        with open(fpath) as f:
            art = json.load(f)

        changed = False
        for field in ["title","meta_description","content_markdown","excerpt"]:
            if field in art and art[field]:
                fixed = fix_emdash(str(art[field]))
                if fixed != art[field]:
                    art[field] = fixed
                    changed = True

        if changed:
            with open(fpath,"w") as f:
                json.dump(art, f, indent=2, ensure_ascii=False)
            total_fixed += 1

print(f"  Fixed {total_fixed} article files")

# Also fix pages content
pages_dir = "/Users/simonazoulay/SurfCampSenegal/content/pages"
for fname in os.listdir(pages_dir):
    if fname.endswith(".json"):
        fpath = f"{pages_dir}/{fname}"
        with open(fpath) as f:
            p = json.load(f)
        changed = False
        for field in ["title_tag","meta_description","h1","hero_subtitle","intro","cta_text"]:
            if field in p and p[field]:
                fixed = fix_emdash(str(p[field]))
                if fixed != p[field]:
                    p[field] = fixed; changed = True
        if p.get("sections"):
            for s in p["sections"]:
                for sf in ["h2","content"]:
                    if s.get(sf):
                        fixed = fix_emdash(s[sf])
                        if fixed != s[sf]:
                            s[sf] = fixed; changed = True
                if s.get("bullets"):
                    new_bullets = [fix_emdash(b) for b in s["bullets"]]
                    if new_bullets != s["bullets"]:
                        s["bullets"] = new_bullets; changed = True
        if changed:
            with open(fpath,"w") as f:
                json.dump(p, f, indent=2, ensure_ascii=False)

print("  Pages content fixed too")
print("\n✅ All em dashes removed")
