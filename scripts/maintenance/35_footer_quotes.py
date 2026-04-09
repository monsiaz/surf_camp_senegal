"""
Add animated quote slider above footer — 15 phrases per language, 3s rotation.
Visually premium: dark section, large quote marks, fade animation.
"""
import os, re, json

DEMO  = "/Users/simonazoulay/SurfCampSenegal/cloudflare-demo"
LANGS = ["en","fr","es","it","de"]

# ── 15 phrases per language ───────────────────────────────────────────────────
PHRASES = {
    "en": [
        "The ocean doesn't care about your level. It only cares about your presence.",
        "No cars. No noise. Just the sound of waves on Ngor.",
        "Progress in surfing is measured in smiles, not just turns.",
        "Ngor Right has been calling surfers since 1964. Your turn.",
        "The best surf trip is the one where you forget to check your phone.",
        "West Africa's best-kept surf secret? Not anymore.",
        "A pirogue ride separates Dakar from paradise.",
        "Surf better. Live slower. Feel the difference.",
        "Teranga: the Senegalese art of making every guest feel at home.",
        "Ngor Left teaches patience. Ngor Right rewards it.",
        "The Atlantic is warm here. The welcome even warmer.",
        "Six days, six sessions, one surf camp that changes everything.",
        "Real coaching starts where comfort zones end.",
        "Some people come to Ngor for a week. Many come back every year.",
        "The Endless Summer started here. Where will yours begin?",
    ],
    "fr": [
        "L'océan ne juge pas votre niveau. Il récompense votre présence.",
        "Pas de voitures. Pas de bruit. Juste le son des vagues sur Ngor.",
        "La progression en surf se mesure en sourires, pas seulement en virages.",
        "Ngor Right appelle les surfeurs depuis 1964. C'est votre tour.",
        "Le meilleur voyage surf, c'est celui où on oublie de regarder son téléphone.",
        "Le secret surf le mieux gardé d'Afrique de l'Ouest ? Plus pour longtemps.",
        "Une traversée en pirogue sépare Dakar du paradis.",
        "Surfez mieux. Vivez plus lentement. Ressentez la différence.",
        "Teranga : l'art sénégalais de faire de chaque invité un ami.",
        "Ngor Left enseigne la patience. Ngor Right la récompense.",
        "L'Atlantique est chaud ici. L'accueil encore plus.",
        "Six jours, six sessions, un surf camp qui change tout.",
        "Le vrai coaching commence là où finit la zone de confort.",
        "Certains viennent une semaine à Ngor. La plupart reviennent chaque année.",
        "L'Endless Summer a commencé ici. Où commencera le vôtre ?",
    ],
    "es": [
        "El océano no juzga tu nivel. Solo premia tu presencia.",
        "Sin coches. Sin ruido. Solo el sonido de las olas en Ngor.",
        "El progreso en el surf se mide en sonrisas, no solo en giros.",
        "Ngor Right lleva llamando a los surfistas desde 1964. Es tu turno.",
        "El mejor viaje surf es aquel en el que olvidas mirar el móvil.",
        "¿El secreto surf mejor guardado de África Occidental? Ya no más.",
        "Un trayecto en piragua separa Dakar del paraíso.",
        "Surfa mejor. Vive más despacio. Siente la diferencia.",
        "Teranga: el arte senegalés de hacer que cada huésped se sienta en casa.",
        "Ngor Left enseña paciencia. Ngor Right la recompensa.",
        "El Atlántico es cálido aquí. La bienvenida, aún más.",
        "Seis días, seis sesiones, un surf camp que lo cambia todo.",
        "El coaching real empieza donde termina la zona de confort.",
        "Algunos vienen a Ngor una semana. Muchos vuelven cada año.",
        "El Endless Summer empezó aquí. ¿Dónde empezará el tuyo?",
    ],
    "it": [
        "L'oceano non giudica il tuo livello. Premia solo la tua presenza.",
        "Niente auto. Niente rumore. Solo il suono delle onde a Ngor.",
        "Il progresso nel surf si misura in sorrisi, non solo in virate.",
        "Ngor Right chiama i surfisti dal 1964. È il tuo turno.",
        "Il miglior viaggio surf è quello in cui dimentichi di guardare il telefono.",
        "Il segreto surf meglio custodito dell'Africa Occidentale? Non più.",
        "Una traversata in piroga separa Dakar dal paradiso.",
        "Surfa meglio. Vivi più lentamente. Senti la differenza.",
        "Teranga: l'arte senegalese di far sentire ogni ospite a casa.",
        "Ngor Left insegna la pazienza. Ngor Right la premia.",
        "L'Atlantico è caldo qui. L'accoglienza ancora di più.",
        "Sei giorni, sei sessioni, un surf camp che cambia tutto.",
        "Il coaching vero inizia dove finisce la zona di comfort.",
        "Alcuni vengono a Ngor per una settimana. Molti tornano ogni anno.",
        "L'Endless Summer è iniziato qui. Dove inizierà il tuo?",
    ],
    "de": [
        "Der Ozean beurteilt dein Level nicht. Er belohnt nur deine Präsenz.",
        "Keine Autos. Kein Lärm. Nur das Rauschen der Wellen auf Ngor.",
        "Fortschritt im Surfen misst man in Lächeln, nicht nur in Kurven.",
        "Ngor Right ruft Surfer seit 1964. Du bist dran.",
        "Die beste Surfreise ist die, bei der du vergisst, aufs Handy zu schauen.",
        "Westafrikas bestgehütetes Surfgeheimnis? Nicht mehr lange.",
        "Eine Pirogenfahrt trennt Dakar vom Paradies.",
        "Besser surfen. Langsamer leben. Den Unterschied spüren.",
        "Teranga: die senegalesische Kunst, jeden Gast wie zu Hause zu empfangen.",
        "Ngor Left lehrt Geduld. Ngor Right belohnt sie.",
        "Der Atlantik ist hier warm. Das Willkommen noch wärmer.",
        "Sechs Tage, sechs Sessions, ein Surf Camp, das alles verändert.",
        "Echtes Coaching beginnt dort, wo die Komfortzone endet.",
        "Manche kommen für eine Woche nach Ngor. Viele kommen jedes Jahr wieder.",
        "Der Endless Summer begann hier. Wo beginnt deiner?",
    ],
}

# ── CSS ───────────────────────────────────────────────────────────────────────
QUOTE_CSS = """
/* ══ FOOTER QUOTE TICKER (DOZ-style « caps ») ══ */
.footer-quotes {
  background: #000;
  border-top: 1px solid rgba(255,255,255,0.1);
  border-bottom: 1px solid rgba(255,255,255,0.07);
  padding: 48px 0 52px;
  overflow: hidden;
  position: relative;
}
.footer-quotes::before { display: none; }
.footer-quotes-inner {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 1;
}
.fq-icon { display: none; }
.fq-text-wrap {
  flex: 1;
  min-width: 0;
  width: 100%;
  position: relative;
  min-height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.fq-phrase {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 100%;
  max-width: 1000px;
  margin: 0;
  padding: 0 20px;
  box-sizing: border-box;
  text-align: center;
  font-size: clamp(14px, 2.8vw, 28px);
  font-style: normal;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  line-height: 1.22;
  font-family: var(--fh, 'Raleway', system-ui), system-ui, sans-serif;
  color: #fff;
  opacity: 0;
  transform: translate(-50%, calc(-50% + 10px));
  transition: opacity 0.65s ease, transform 0.65s ease;
  pointer-events: none;
}
.fq-phrase::before { content: '«\\00a0'; font-weight: 800; letter-spacing: 0.02em; }
.fq-phrase::after { content: '\\00a0»'; font-weight: 800; letter-spacing: 0.02em; }
.fq-phrase.active {
  opacity: 1;
  transform: translate(-50%, -50%);
}
.fq-phrase strong {
  color: #fff;
  font-weight: 800;
  border-bottom: 2px solid var(--sand, #f0c060);
  padding-bottom: 2px;
}
.fq-dots, .fq-dot { display: none !important; }
@media(max-width:640px){
  .footer-quotes { padding: 36px 0 40px; }
  .footer-quotes-inner { padding: 0 18px; }
  .fq-text-wrap { min-height: 120px; }
  .fq-phrase {
    font-size: clamp(11px, 3.6vw, 17px);
    letter-spacing: 0.08em;
    line-height: 1.3;
    padding: 0 12px;
    font-weight: 800;
  }
}
"""

# ── Build the quote slider HTML block ─────────────────────────────────────────
def build_quotes_html(lang):
    phrases = PHRASES.get(lang, PHRASES["en"])
    phrases_json = json.dumps(phrases, ensure_ascii=False)

    # Build phrase spans (only first is active initially)
    spans = ""
    for i, phrase in enumerate(phrases):
        # Highlight the last part after a period as strong
        parts = phrase.rsplit(".", 1)
        if len(parts) == 2 and len(parts[1]) > 3:
            display = f'{parts[0]}.<strong>{parts[1]}</strong>'
        else:
            display = phrase
        cls = "fq-phrase active" if i == 0 else "fq-phrase"
        spans += f'<span class="{cls}" data-idx="{i}">{display}</span>'

    return f"""<div class="footer-quotes" aria-label="Surf quotes" aria-live="polite">
  <div class="footer-quotes-inner">
    <div class="fq-text-wrap" id="fq-wrap-{lang}">{spans}</div>
  </div>
</div>"""

# ── JS (injected into animations.js once) ────────────────────────────────────
QUOTE_JS = """
/* ── Footer Quote Ticker ───────────────────────────────────── */
(function initFooterQuotes(){
  const wrap = document.querySelector('[id^="fq-wrap-"]');
  if(!wrap) return;

  const phrases = wrap.querySelectorAll('.fq-phrase');
  const total   = phrases.length;
  if(!total) return;

  let cur = 0;

  function show(idx){
    phrases[cur].classList.remove('active');
    cur = (idx + total) % total;
    phrases[cur].classList.add('active');
  }

  setInterval(() => show(cur + 1), 3000);
})();
"""

# ── Apply to all HTML pages ───────────────────────────────────────────────────
def detect_lang(fpath):
    path = fpath.replace(DEMO, "")
    for l in ["fr","es","it","de"]:
        if path.startswith(f"/{l}/"): return l
    return "en"

print("=== Adding footer quotes to all pages ===")

# Add CSS once
css_path = f"{DEMO}/assets/css/ngor-surfcamp.css"
with open(css_path,'a') as f: f.write('\n' + QUOTE_CSS)
print("✅ Quote CSS added")

# Add JS once to animations.js
anim_path = f"{DEMO}/assets/js/ngor-surfcamp.js"
with open(anim_path,'a') as f: f.write('\n' + QUOTE_JS)
print("✅ Quote JS added")

# Inject HTML into all pages
total = 0
skipped = 0

for root, dirs, files in os.walk(DEMO):
    dirs[:] = [d for d in dirs if not d.startswith('.')]
    for fname in files:
        if not fname.endswith('.html'): continue
        fpath = os.path.join(root, fname)
        with open(fpath) as f: html = f.read()

        if 'http-equiv="refresh"' in html: skipped += 1; continue
        if 'fq-wrap-' in html: continue  # already added

        lang = detect_lang(fpath)
        quotes_html = build_quotes_html(lang)

        # Insert before <footer>
        if '<footer>' in html:
            html = html.replace('<footer>', quotes_html + '\n<footer>', 1)
            with open(fpath,'w') as f: f.write(html)
            total += 1

print(f"✅ Added to {total} pages (skipped {skipped} redirects)")

# Verify
with open(f'{DEMO}/index.html') as f: h = f.read()
has_fq  = 'fq-wrap-' in h
has_css = 'fq-text-wrap' in open(css_path).read()
print(f"\nVerification: HTML={has_fq} | CSS={has_css}")
