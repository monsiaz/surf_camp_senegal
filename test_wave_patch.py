import re
import os

WAVE_RE = re.compile(r'\s*<div class="wave-(?:top|bottom)"[^>]*>.*?</div>', re.DOTALL)
WAVE_DIV_RE = re.compile(r'\s*<div[^>]*class="[^"]*wave-divider[^"]*"[^>]*>.*?</div>', re.DOTALL)

def _strip_waves(h):
    h = WAVE_RE.sub('', h)
    h = WAVE_DIV_RE.sub('', h)
    return h

def wave_bottom(bg, fill):
    return f'<div class="wave-bottom" aria-hidden="true" style="background:{bg}"><svg viewBox="0 0 1440 52" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none"><path d="M0 26 C240 2,480 50,720 24 C960 -2,1200 48,1440 26 L1440 52 L0 52Z" fill="{fill}"/></svg></div>'

path = "/Users/simonazoulay/SurfCampSenegal/cloudflare-demo/getting-here/index.html"
with open(path, "r", encoding="utf-8") as f:
    h = f.read()

h = _strip_waves(h)

FQ_MARKER = '<div class="footer-quotes"'
if FQ_MARKER in h:
    idx = h.find(FQ_MARKER)
    preceding = h[max(0, idx-2500):idx]
    if 'cta-band' not in preceding:
        if 'sec-light' in preceding or 'sec-sand' in preceding:
            prev_bg = "#fdf4e3" # _BG_LIGHT
        else:
            prev_bg = "#ffffff" # _BG_WHITE
        wave_html = '\n' + wave_bottom(prev_bg, "#000") + '\n'
        h = h.replace(FQ_MARKER, wave_html + FQ_MARKER, 1)
        print("Wave added!")
else:
    print("FQ_MARKER not found")

with open("/tmp/test_getting_here.html", "w") as f:
    f.write(h)
