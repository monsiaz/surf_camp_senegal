"""
Generate via DALL-E:
  - 5 surfer persona profile icons
  - 15 UI icons (replacing emoji in the site)
All consistent DA: minimal flat illustration, navy/sand/fire palette
"""
import os, requests, base64
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

OPENAI_KEY = "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"
ICONS_DIR  = "/Users/simonazoulay/SurfCampSenegal/cloudflare-demo/assets/images/icons"
os.makedirs(ICONS_DIR, exist_ok=True)

client = OpenAI(api_key=OPENAI_KEY)
lock   = threading.Lock()

STYLE = """
Flat minimal illustration, icon style.
Color palette: deep navy blue (#0a2540), warm sand/amber, bright orange (#ff6b35).
Clean white background. Simple bold shapes, no gradients.
Professional, modern surf lifestyle aesthetic.
No text, no watermarks.
Square composition, centered subject, lots of breathing room.
"""

# ── 5 Surfer Personas ─────────────────────────────────────────────────────────
PERSONAS = [
    {
        "id": "maya-beginner",
        "name": "Maya",
        "type": "The Curious Beginner",
        "prompt": f"Flat minimal illustration of a young woman (25, French) in a surf lesson on the beach, holding a foam surfboard with excitement, bright smile, casual swimwear, tropical beach background. {STYLE}",
        "color": "#29b6f6",
        "description": {"en":"First surf trip, never surfed before, eager to learn","fr":"Premier voyage surf, jamais surfé, impatiente d'apprendre","es":"Primer viaje surf, nunca ha surfeado, deseosa de aprender","it":"Primo viaggio surf, non ha mai surfato, desiderosa di imparare","de":"Erste Surfreise, noch nie gesurft, lernbegierig"},
    },
    {
        "id": "jake-weekend",
        "name": "Jake",
        "type": "The Weekend Warrior",
        "prompt": f"Flat minimal illustration of a British man (34) paddling on a surfboard, focused determined expression, wetsuit, ocean waves in background, athletic build. {STYLE}",
        "color": "#ff6b35",
        "description": {"en":"Surfs 2-3x per year, wants to break through to the next level","fr":"Surfe 2-3x par an, veut passer au niveau supérieur","es":"Surfea 2-3x al año, quiere pasar al siguiente nivel","it":"Surfa 2-3 volte l'anno, vuole passare al livello successivo","de":"Surft 2-3x im Jahr, will auf das nächste Level"},
    },
    {
        "id": "lena-committed",
        "name": "Lena",
        "type": "The Committed Improver",
        "prompt": f"Flat minimal illustration of a German woman (28) analyzing surf video on a tablet with a coach on a beach, serious focused expression, performance surf gear. {STYLE}",
        "color": "#f0d6a4",
        "description": {"en":"Trains regularly, serious about video analysis & technique","fr":"S'entraîne régulièrement, sérieuse en analyse vidéo","es":"Entrena regularmente, seria con el análisis de vídeo","it":"Si allena regolarmente, seria nell'analisi video","de":"Trainiert regelmäßig, ernst bei Videoanalyse & Technik"},
    },
    {
        "id": "carlos-globetrotter",
        "name": "Carlos",
        "type": "The Globe-Trotter",
        "prompt": f"Flat minimal illustration of a Spanish man (42) standing on a surfboard riding a perfect wave at a tropical point break, confident relaxed stance, experienced surfer pose. {STYLE}",
        "color": "#0a2540",
        "description": {"en":"Experienced surfer, traveled extensively, seeks new quality breaks","fr":"Surfeur expérimenté, a beaucoup voyagé, cherche de nouveaux spots","es":"Surfista experimentado, viajero, busca nuevos y quality spots","it":"Surfista esperto, viaggiatore, cerca nuovi spot di qualità","de":"Erfahrener Surfer, viel gereist, sucht neue Qualitätswellen"},
    },
    {
        "id": "amara-soul",
        "name": "Amara",
        "type": "The Soul Surfer",
        "prompt": f"Flat minimal illustration of a young Senegalese woman (31) sitting on a surfboard watching a perfect sunset over the ocean, peaceful meditative pose, traditional fabric wrap. {STYLE}",
        "color": "#9c27b0",
        "description": {"en":"Lifestyle surfer, mindful, connects with West African ocean culture","fr":"Surfeuse lifestyle, pleine conscience, connectée à la culture océane","es":"Surfera lifestyle, mindful, conectada con la cultura oceánica","it":"Surfer lifestyle, mindful, connessa con la cultura oceanica","de":"Lifestyle-Surferin, achtsam, verbunden mit Westafrikas Ozeankultur"},
    },
]

# ── UI Icons (replacing emoji in the site) ────────────────────────────────────
UI_ICONS = [
    {"id": "icon-transfer",  "prompt": f"Flat minimal icon of a traditional wooden pirogue boat on calm water with surfboards visible, aerial angle, tropical blue ocean. {STYLE}"},
    {"id": "icon-food",      "prompt": f"Flat minimal icon of a steaming bowl of thieboudienne (Senegalese fish rice dish) with colorful vegetables, warm appetizing styling. {STYLE}"},
    {"id": "icon-surf-guide","prompt": f"Flat minimal icon of a surf instructor pointing at ocean waves, student beside them with surfboard, beach setting. {STYLE}"},
    {"id": "icon-theory",    "prompt": f"Flat minimal icon of a whiteboard with surf technique diagrams (pop-up position, turn arrows), open book and pen beside it. {STYLE}"},
    {"id": "icon-pool",      "prompt": f"Flat minimal icon of a small infinity pool overlooking the ocean, lounge chairs, palm tree, Ngor Island tropical vibe. {STYLE}"},
    {"id": "icon-wifi",      "prompt": f"Flat minimal icon of wifi signal arching over a tropical beach scene with ocean, modern minimalist design. {STYLE}"},
    {"id": "icon-video",     "prompt": f"Flat minimal icon of a camera filming a surfer on a wave, playback on a tablet beside it, analysis diagram. {STYLE}"},
    {"id": "icon-coaching",  "prompt": f"Flat minimal icon of a surf coach on the beach with a clipboard, gesturing to a student about to paddle out, professional teaching moment. {STYLE}"},
    {"id": "icon-federation","prompt": f"Flat minimal icon of an official certificate with a surf federation seal, laurel wreath, professional award styling. {STYLE}"},
    {"id": "icon-location",  "prompt": f"Flat minimal icon of Ngor Island viewed from above, tiny island with a few buildings and palm trees, turquoise water, simple map pin above. {STYLE}"},
    {"id": "icon-calendar",  "prompt": f"Flat minimal icon of a calendar showing sunny tropical days, surf forecast chart, seasonal waves graphic. {STYLE}"},
    {"id": "icon-tip",       "prompt": f"Flat minimal icon of a lightbulb with a wave shape inside it, surf tip concept, bright and clear. {STYLE}"},
    {"id": "icon-checklist", "prompt": f"Flat minimal icon of a surf packing list clipboard with checkboxes, wetsuit, fins, wax and passport items. {STYLE}"},
    {"id": "icon-quote",     "prompt": f"Flat minimal icon of large quotation marks over an ocean wave, inspiring journalistic style, editorial feel. {STYLE}"},
    {"id": "icon-summary",   "prompt": f"Flat minimal icon of a summary card with key bullet points and a wave motif, organized clean layout. {STYLE}"},
]

def generate_icon(item, is_persona=False):
    name = item["id"]
    out  = f"{ICONS_DIR}/{name}.png"
    if os.path.exists(out) and os.path.getsize(out) > 5000:
        with lock: print(f"  [skip] {name}")
        return name, out

    with lock: print(f"  Generating: {name}")
    prompt = item.get("prompt","")

    for model, size in [("dall-e-3","1024x1024")]:
        try:
            resp = client.images.generate(
                model=model, prompt=prompt[:1500], n=1, size=size,
                quality="standard" if not is_persona else "hd"
            )
            url = resp.data[0].url
            img = requests.get(url, timeout=30).content
            with open(out,"wb") as f: f.write(img)
            with lock: print(f"  ✅ {name} ({len(img)//1024}KB)")
            return name, out
        except Exception as e:
            with lock: print(f"  ❌ {name}: {e}")
    return name, None

print("=== Generating Persona Icons ===")
with ThreadPoolExecutor(max_workers=5) as ex:
    futs = {ex.submit(generate_icon, p, True): p for p in PERSONAS}
    for f in as_completed(futs): f.result()

print("\n=== Generating UI Icons ===")
with ThreadPoolExecutor(max_workers=8) as ex:
    futs = {ex.submit(generate_icon, i, False): i for i in UI_ICONS}
    for f in as_completed(futs): f.result()

# Save personas metadata
import json
personas_data = {p["id"]: {k:v for k,v in p.items() if k!="prompt"} for p in PERSONAS}
with open(f"{ICONS_DIR}/../../../content/personas.json","w") as f:
    json.dump(personas_data, f, indent=2, ensure_ascii=False)
print("\n✅ All icons generated")
print(f"Icons dir: {ICONS_DIR}")
