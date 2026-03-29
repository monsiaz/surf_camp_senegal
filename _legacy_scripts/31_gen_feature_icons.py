"""
Generate 12 feature icons via DALL-E then patch all feature sections.
Icons: surf transfer, food, surf guide, theory, pool, wifi,
       coaching, video analysis, waves, federation, calendar, location
Style: clean minimal flat icon, white stroke on transparent bg
"""
import os, requests
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

OPENAI_KEY  = "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"
ICONS_DIR   = "/Users/simonazoulay/SurfCampSenegal/cloudflare-demo/assets/images/icons"
os.makedirs(ICONS_DIR, exist_ok=True)

client = OpenAI(api_key=OPENAI_KEY)
lock   = threading.Lock()

STYLE = """
Minimal flat icon design. Clean bold strokes, pure white on solid deep navy blue (#0a2540) background.
Icon fills 65% of canvas, centered, with breathing room.
No gradients, no shadows, no text, no decorative elements.
Single color: white icon on dark navy square.
Modern app icon style, crisp and professional.
Square 1:1 format.
"""

ICONS = [
    ("feat-transfer",  "Minimal flat white icon: traditional narrow wooden boat (pirogue) seen from the side, simple clean silhouette, waves beneath, white on navy"),
    ("feat-food",      "Minimal flat white icon: bowl of rice and fish (Senegalese thieboudienne), steam rising, fork beside bowl, clean silhouette, white on navy"),
    ("feat-guide",     "Minimal flat white icon: surfboard pointing diagonally up-right with a wave curl behind it, clean bold lines, white on navy"),
    ("feat-theory",    "Minimal flat white icon: open book with a surfboard silhouette as a bookmark, clean minimal design, white on navy"),
    ("feat-pool",      "Minimal flat white icon: swimming pool viewed from side, two wavy lines representing water, sun above, simple clean, white on navy"),
    ("feat-wifi",      "Minimal flat white icon: wifi signal arcs with a tiny wave/ocean beneath them, clean minimal, white on navy"),
    ("feat-coaching",  "Minimal flat white icon: figure standing on surfboard with arms extended for balance, coaching pose, bold clean silhouette, white on navy"),
    ("feat-video",     "Minimal flat white icon: camera lens as a circle with a surfboard silhouette reflected in it, clean design, white on navy"),
    ("feat-calendar",  "Minimal flat white icon: calendar page with a sun and wave motif, clean simple design, white on navy"),
    ("feat-check",     "Minimal flat white icon: large bold checkmark inside a rounded square, clean and strong, white on navy"),
    ("feat-location",  "Minimal flat white icon: location pin with a tiny island (Ngor) and palm tree inside the pin drop, white on navy"),
    ("feat-star",      "Minimal flat white icon: five-pointed star with clean bold lines, small wave motif beneath it, white on navy"),
]

def gen_icon(name, prompt):
    out = f"{ICONS_DIR}/{name}.png"
    # Force regenerate
    full = f"{prompt}\n\n{STYLE}"
    with lock: print(f"  ▶ {name}")
    try:
        resp = client.images.generate(
            model="dall-e-3", prompt=full[:1200],
            n=1, size="1024x1024", quality="standard"
        )
        img = requests.get(resp.data[0].url, timeout=30).content
        with open(out,"wb") as f: f.write(img)
        with lock: print(f"  ✅ {name} ({len(img)//1024}KB)")
        return name, out
    except Exception as e:
        with lock: print(f"  ❌ {name}: {e}")
        return name, None

print(f"=== Generating {len(ICONS)} feature icons ===\n")
with ThreadPoolExecutor(max_workers=6) as ex:
    futs = {ex.submit(gen_icon, n, p): n for n,p in ICONS}
    done = {}
    for f in as_completed(futs): n,p = f.result(); done[n]=p

print(f"\n✅ Generated: {sum(1 for v in done.values() if v)}/{len(ICONS)}")
