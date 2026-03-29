"""
Build Google Reviews-style slider + review badge.
- 10 best reviews from real Google data
- Translated to EN/FR/ES/IT/DE via GPT
- Beautiful slider with avatars, stars, dates
- Injects into all homepages + booking pages
- Replaces ugly badge strip with elegant version
"""
import json, os, re, time
from openai import OpenAI

OPENAI_KEY = "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"
MODEL    = "gpt-5.4-2026-03-05"
DEMO_DIR = "/Users/simonazoulay/SurfCampSenegal/cloudflare-demo"
LANGS    = ["en","fr","es","it","de"]
LANG_PFX = {"en":"","fr":"/fr","es":"/es","it":"/it","de":"/de"}
client   = OpenAI(api_key=OPENAI_KEY)

def gpt(prompt, temp=0.4, tokens=3000):
    r = client.chat.completions.create(
        model=MODEL, temperature=temp, max_completion_tokens=tokens,
        messages=[{"role":"user","content":prompt}]
    )
    return r.choices[0].message.content

# ════════════════════════════════════════════════════════════════════════════════
# TOP 10 REVIEWS (curated from real Google data)
# ════════════════════════════════════════════════════════════════════════════════
RAW_REVIEWS = [
    {
        "id": "r01",
        "author": "Julie F.",
        "country": "France", "flag": "🇫🇷",
        "stars": 5,
        "date_fr": "aujourd'hui",
        "avatar_color": "#ff5a1f",
        "verified": True,
        "text_fr": "Le surf camp Teranga est un lieu au top pour tous les passionnés de surf ! Le camp, les spots, le coaching, l'île, l'ambiance, la nourriture et l'accueil... Bref, il porte bien son nom, c'est la teranga sénégalaise ! Aucune hésitation à y séjourner !",
    },
    {
        "id": "r02",
        "author": "Addie W.",
        "country": "USA", "flag": "🇺🇸",
        "stars": 5,
        "date_fr": "il y a 2 mois",
        "avatar_color": "#0ea5e9",
        "verified": True,
        "text_fr": "Je suis allée plusieurs fois à Dakar pour surfer et j'ai séjourné dans différents endroits. Abu est, à mon avis, le meilleur guide de surf de Dakar et je le suis partout. Il sait parfaitement vous placer sur la vague et assure la sécurité de tout le monde. Incontournable !",
    },
    {
        "id": "r03",
        "author": "F. F.",
        "country": "Europe", "flag": "🇪🇺",
        "stars": 5,
        "date_fr": "il y a 3 semaines",
        "avatar_color": "#9c27b0",
        "verified": True,
        "text_fr": "Je reviens tout juste d'une semaine incroyable au Ngor Surfcamp avec ma fille de 16 ans. Tout s'est déroulé à merveille, de l'entrée facile grâce à mon passeport européen à la prise en charge professionnelle. Organisation impeccable, coaching excellent, repas délicieux. Je recommande à 100% !",
    },
    {
        "id": "r04",
        "author": "John Fairs",
        "country": "Angleterre", "flag": "🇬🇧",
        "stars": 5,
        "date_fr": "il y a 3 semaines",
        "avatar_color": "#22c55e",
        "verified": True,
        "text_fr": "Première classe ! J'ai passé un super moment. Benoit est génial, le guide de surf Abu est incroyable et la cuisine d'Arame était fantastique. En plus les vagues étaient parfaites tous les jours. Que demander de plus !",
    },
    {
        "id": "r05",
        "author": "Niccolò P.",
        "country": "Italie", "flag": "🇮🇹",
        "stars": 5,
        "date_fr": "il y a 3 mois",
        "avatar_color": "#f0c060",
        "verified": True,
        "text_fr": "Expérience absolument fantastique. La surfhouse est chaleureuse et paisible. De mon balcon, j'avais une vue imprenable sur l'océan et le coucher de soleil sur Ngor Right, sans doute le meilleur spot de surf de la région. La cuisine était délicieuse, le service attentionné.",
    },
    {
        "id": "r06",
        "author": "Kirstine F.",
        "country": "Danemark", "flag": "🇩🇰",
        "stars": 5,
        "date_fr": "il y a 5 mois",
        "avatar_color": "#e91e63",
        "verified": True,
        "text_fr": "J'ai passé un séjour incroyable au Ngor Surfcamp ! L'ambiance était géniale avec des gens formidables, des guides et des coachs de surf compétents qui vous aident vraiment à progresser. La nourriture était délicieuse et variée. Je recommande vivement à tous les niveaux !",
    },
    {
        "id": "r07",
        "author": "Fritz L.",
        "country": "Allemagne", "flag": "🇩🇪",
        "stars": 5,
        "date_fr": "il y a 4 mois",
        "avatar_color": "#0a2540",
        "verified": True,
        "text_fr": "L'endroit idéal pour un séjour surf au Sénégal. Vue imprenable sur l'océan Atlantique, proximité de spots exceptionnels. Ben est un hôte très sympathique qui vous emmène chaque jour en bateau vers les meilleurs spots. Les repas sont inclus et absolument délicieux !",
    },
    {
        "id": "r08",
        "author": "Manuel G. M.",
        "country": "Espagne", "flag": "🇪🇸",
        "stars": 5,
        "date_fr": "il y a 2 mois",
        "avatar_color": "#ff6b35",
        "verified": True,
        "text_fr": "Le meilleur surfcamp de Ngor ! Ben et Abu ont été absolument exceptionnels. Organisation parfaite, coaching top niveau, ambiance incroyable. Je recommande à 100% sans la moindre hésitation !",
    },
    {
        "id": "r09",
        "author": "Garoe M. G.",
        "country": "Espagne", "flag": "🇪🇸",
        "stars": 5,
        "date_fr": "il y a 2 mois",
        "avatar_color": "#26a69a",
        "verified": True,
        "text_fr": "Superbe expérience au Ngor Surf Camp Teranga. L'ambiance y est chaleureuse et accueillante, on s'y sentait vraiment comme à la maison. Malgré un vol très tardif, nous avons pu profiter des espaces communs toute la journée. Accueil irréprochable, coaching de qualité.",
    },
    {
        "id": "r10",
        "author": "Arame D.",
        "country": "Sénégal", "flag": "🇸🇳",
        "stars": 5,
        "date_fr": "il y a 5 mois",
        "avatar_color": "#8bc34a",
        "verified": True,
        "text_fr": "Super séjour ! Une ambiance au top, une équipe souriante et un cadre de rêve. Le meilleur surfcamp que j'ai testé ! Je reviendrai sans hésiter pour profiter encore des vagues de Ngor et de l'accueil chaleureux.",
    },
]

# ── Translate all reviews ─────────────────────────────────────────────────────
REVIEWS_FILE = f"{DEMO_DIR}/../output/reviews_translated.json"
os.makedirs(os.path.dirname(REVIEWS_FILE), exist_ok=True)

reviews_data = {}
if os.path.exists(REVIEWS_FILE):
    reviews_data = json.load(open(REVIEWS_FILE))

for rev in RAW_REVIEWS:
    rid = rev["id"]
    if rid in reviews_data and all(lang in reviews_data[rid] for lang in LANGS):
        print(f"  [skip] {rid}")
        continue

    print(f"  Translating {rid}: {rev['author']}")
    if rid not in reviews_data:
        reviews_data[rid] = {}

    # Translate from French to all other languages
    prompt = f"""Translate this genuine customer review of Ngor Surfcamp Teranga (surf camp on Ngor Island, Dakar, Senegal) to English, Spanish, Italian and German. Keep the authentic voice and enthusiasm. No em dashes.

French original:
"{rev['text_fr']}"

Return ONLY valid JSON:
{{
  "en": "English translation",
  "es": "Spanish translation",
  "it": "Italian translation",
  "de": "German translation"
}}"""

    try:
        raw = gpt(prompt, temp=0.3, tokens=1000)
        if "```json" in raw: raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:   raw = raw.split("```")[1].split("```")[0].strip()
        trans = json.loads(raw)
        reviews_data[rid] = {
            "fr": rev["text_fr"],
            "en": trans.get("en",""),
            "es": trans.get("es",""),
            "it": trans.get("it",""),
            "de": trans.get("de",""),
            "author": rev["author"],
            "country": rev["country"],
            "flag": rev["flag"],
            "stars": rev["stars"],
            "date_fr": rev["date_fr"],
            "avatar_color": rev["avatar_color"],
        }
        with open(REVIEWS_FILE,"w") as f:
            json.dump(reviews_data, f, indent=2, ensure_ascii=False)
        time.sleep(0.3)
    except Exception as e:
        print(f"    ERROR: {e}")

print(f"Reviews translated: {len(reviews_data)}/10")

# ── CSS for the slider ────────────────────────────────────────────────────────
REVIEWS_CSS = """
/* ══════════════════════════════════════════════════════
   GOOGLE REVIEWS SLIDER
══════════════════════════════════════════════════════ */

/* Section */
.reviews-section {
  padding: 100px 0;
  background: linear-gradient(160deg, #07192e 0%, var(--navy) 60%, #09203a 100%);
  color: #fff;
  position: relative;
  overflow: hidden;
}
.reviews-section::before {
  content: '';
  position: absolute; inset: 0;
  background: radial-gradient(ellipse at 20% 50%, rgba(255,90,31,0.10) 0%, transparent 50%),
              radial-gradient(ellipse at 80% 50%, rgba(14,165,233,0.08) 0%, transparent 50%);
}
.reviews-section::after {
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, transparent, rgba(240,192,96,0.4), transparent);
}

/* Header row */
.reviews-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-bottom: 52px;
  flex-wrap: wrap;
  gap: 20px;
  position: relative; z-index: 1;
}
.reviews-rating-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 18px 24px;
  background: rgba(255,255,255,0.07);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 20px;
  text-align: center;
  min-width: 120px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.2), inset 0 1px 0 rgba(255,255,255,0.08);
}
.reviews-score {
  font-family: var(--fh);
  font-size: 48px; font-weight: 900; line-height: 1;
  background: linear-gradient(135deg, var(--sand), #fff);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
}
.reviews-stars-header {
  display: flex; gap: 3px;
}
.reviews-stars-header span {
  font-size: 18px; color: var(--sand);
}
.reviews-count {
  font-size: 12px; opacity: 0.55; letter-spacing: 0.05em;
}
.google-badge {
  display: flex; align-items: center; gap: 8px;
  font-size: 12px; color: rgba(255,255,255,0.5);
  margin-top: 6px;
}
.google-badge svg { width: 16px; height: 16px; }

/* Slider container */
.reviews-slider-wrap {
  position: relative;
  z-index: 1;
}
.reviews-track {
  overflow: hidden;
  margin: 0 -8px;
}
.reviews-inner {
  display: flex;
  gap: 20px;
  padding: 8px 8px 20px;
  transition: transform 0.55s cubic-bezier(0.4,0,0.2,1);
  will-change: transform;
}

/* Review card */
.review-card {
  flex: 0 0 calc(33.33% - 14px);
  background: rgba(255,255,255,0.06);
  backdrop-filter: blur(18px) saturate(160%);
  -webkit-backdrop-filter: blur(18px) saturate(160%);
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: 20px;
  padding: 28px;
  transition: transform 0.3s var(--spring), box-shadow 0.3s, background 0.3s;
  cursor: default;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 24px rgba(0,0,0,0.15), inset 0 1px 0 rgba(255,255,255,0.08);
}
.review-card::before {
  content: '"';
  position: absolute; top: 12px; right: 20px;
  font-size: 80px; line-height: 1; font-family: Georgia,serif;
  color: rgba(255,255,255,0.06); pointer-events: none;
}
.review-card:hover {
  transform: translateY(-5px);
  background: rgba(255,255,255,0.10);
  box-shadow: 0 16px 48px rgba(0,0,0,0.25), inset 0 1px 0 rgba(255,255,255,0.12);
}

/* Card header */
.rc-head {
  display: flex; align-items: center; gap: 12px; margin-bottom: 16px;
}
.rc-avatar {
  width: 46px; height: 46px; border-radius: 50%; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  font-family: var(--fh); font-weight: 800; font-size: 18px; color: #fff;
  border: 2px solid rgba(255,255,255,0.15);
  background-size: cover; background-position: center;
}
.rc-info { flex: 1; min-width: 0; }
.rc-name {
  font-weight: 700; font-size: 15px; color: #fff;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.rc-meta {
  display: flex; align-items: center; gap: 6px; margin-top: 3px;
}
.rc-flag { font-size: 14px; }
.rc-country { font-size: 12px; color: rgba(255,255,255,0.45); }
.rc-date { font-size: 12px; color: rgba(255,255,255,0.35); margin-left: auto; }

/* Stars */
.rc-stars {
  display: flex; gap: 3px; margin-bottom: 14px;
}
.rc-stars span { color: var(--sand); font-size: 14px; }

/* Review text */
.rc-text {
  font-size: 14.5px; line-height: 1.72; color: rgba(255,255,255,0.78);
  display: -webkit-box;
  -webkit-line-clamp: 5;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.rc-text.expanded { -webkit-line-clamp: unset; }

/* Verified badge */
.rc-verified {
  display: inline-flex; align-items: center; gap: 5px;
  margin-top: 14px; font-size: 11px;
  color: rgba(255,255,255,0.35);
}
.rc-verified svg { width: 12px; height: 12px; color: #4285f4; }

/* Nav */
.reviews-nav {
  display: flex; align-items: center; justify-content: center;
  gap: 16px; margin-top: 36px;
  position: relative; z-index: 1;
}
.rev-arrow {
  width: 48px; height: 48px; border-radius: 50%;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.14);
  color: rgba(255,255,255,0.7);
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: background var(--t), color var(--t), transform 0.2s var(--spring);
  flex-shrink: 0;
}
.rev-arrow:hover { background: var(--fire); border-color: var(--fire); color: #fff; transform: scale(1.08); }
.rev-arrow:disabled { opacity: 0.3; cursor: not-allowed; pointer-events: none; }
.rev-arrow svg { width: 20px; height: 20px; }

.rev-dots { display: flex; gap: 8px; }
.rev-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: rgba(255,255,255,0.20);
  cursor: pointer; transition: background 0.3s, transform 0.3s, width 0.3s;
  border: none;
}
.rev-dot.active {
  background: var(--fire);
  width: 24px; border-radius: 4px;
}

/* Google CTA */
.reviews-cta {
  display: flex; align-items: center; justify-content: center;
  gap: 16px; margin-top: 40px; flex-wrap: wrap;
  position: relative; z-index: 1;
}
.google-cta-btn {
  display: inline-flex; align-items: center; gap: 9px;
  padding: 12px 22px; border-radius: var(--r-pill);
  background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.14);
  color: rgba(255,255,255,0.80); font-size: 13.5px; font-weight: 600;
  transition: background var(--t), color var(--t), transform 0.2s var(--spring);
  text-decoration: none;
}
.google-cta-btn:hover { background: rgba(255,255,255,0.16); color: #fff; transform: translateY(-2px); }
.google-cta-btn svg { width: 18px; height: 18px; flex-shrink: 0; }

/* ── MINI review badge (booking page) ─────────────────────────── */
.booking-review-badge {
  background: linear-gradient(135deg, rgba(10,37,64,0.96), rgba(8,22,40,0.98));
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: 20px;
  padding: 28px 32px;
  color: #fff;
  position: relative;
  overflow: hidden;
}
.booking-review-badge::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 3px;
  background: linear-gradient(90deg, var(--fire), var(--sand), var(--fire));
  background-size: 200% 100%;
  animation: shimmer 3s linear infinite;
}
.badge-score-row {
  display: flex; align-items: center; gap: 20px; margin-bottom: 24px;
}
.badge-big-score {
  font-family: var(--fh); font-size: 56px; font-weight: 900; line-height: 1;
  background: linear-gradient(135deg, var(--sand), #fff);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.badge-score-info {}
.badge-stars { display: flex; gap: 3px; margin-bottom: 4px; }
.badge-stars span { color: var(--sand); font-size: 20px; }
.badge-count { font-size: 13px; color: rgba(255,255,255,0.5); }
.badge-from { font-size: 11px; color: rgba(255,255,255,0.35); margin-top:2px; }

/* Mini slider */
.mini-review-slider {
  position: relative; overflow: hidden; border-radius: 14px;
}
.mini-reviews-inner {
  display: flex;
  transition: transform 0.5s cubic-bezier(0.4,0,0.2,1);
}
.mini-review-card {
  flex: 0 0 100%;
  padding: 20px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 14px;
}
.mini-rc-text {
  font-size: 14px; line-height: 1.68; color: rgba(255,255,255,0.80);
  font-style: italic; margin-bottom: 14px;
  display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden;
}
.mini-rc-author {
  display: flex; align-items: center; gap: 10px;
}
.mini-rc-avatar {
  width: 34px; height: 34px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; font-weight: 800; color: #fff; flex-shrink: 0;
}
.mini-rc-name { font-weight: 700; font-size: 13px; }
.mini-rc-stars { display: flex; gap: 2px; margin-top: 2px; }
.mini-rc-stars span { color: var(--sand); font-size: 12px; }
.mini-nav {
  display: flex; justify-content: center; gap: 6px; margin-top: 14px;
}
.mini-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: rgba(255,255,255,0.2); cursor: pointer;
  transition: background 0.3s, width 0.3s; border: none;
}
.mini-dot.active { background: var(--fire); width: 18px; border-radius: 3px; }

/* Responsive */
@media(max-width:1024px){
  .review-card { flex: 0 0 calc(50% - 10px); }
}
@media(max-width:640px){
  .review-card { flex: 0 0 calc(100% - 0px); }
  .reviews-header { flex-direction: column; align-items: flex-start; }
}
"""

# ── Slider JS ─────────────────────────────────────────────────────────────────
SLIDER_JS = """
/* ── Google Reviews Slider ─────────────────────────────── */
(function initReviewsSlider(){
  const track  = document.getElementById('reviews-inner');
  const mini   = document.getElementById('mini-reviews-inner');
  if(!track && !mini) return;

  function makeSlider(inner, dotsEl, prevBtn, nextBtn, visCount){
    if(!inner) return;
    const cards = inner.querySelectorAll('[data-slide]');
    if(!cards.length) return;
    let cur = 0;
    const total = cards.length;
    const maxIdx = Math.max(0, total - visCount);

    function go(idx){
      cur = Math.max(0, Math.min(idx, maxIdx));
      const w = cards[0].getBoundingClientRect().width + 20;
      inner.style.transform = 'translateX(-' + (cur * w) + 'px)';
      if(dotsEl){
        [...dotsEl.querySelectorAll('[data-dot]')].forEach((d,i) => d.classList.toggle('active', i===cur));
      }
      if(prevBtn) prevBtn.disabled = cur === 0;
      if(nextBtn) nextBtn.disabled = cur >= maxIdx;
    }

    if(prevBtn) prevBtn.addEventListener('click', () => go(cur-1));
    if(nextBtn) nextBtn.addEventListener('click', () => go(cur+1));

    if(dotsEl){
      [...dotsEl.querySelectorAll('[data-dot]')].forEach((d,i) => d.addEventListener('click', () => go(i)));
    }

    // Touch/swipe
    let startX = 0;
    inner.parentElement.addEventListener('touchstart', e => startX = e.touches[0].clientX, {passive:true});
    inner.parentElement.addEventListener('touchend', e => {
      const diff = startX - e.changedTouches[0].clientX;
      if(Math.abs(diff) > 50) go(diff > 0 ? cur+1 : cur-1);
    }, {passive:true});

    // Auto-play for mini
    if(inner === mini){
      setInterval(() => go((cur+1) > maxIdx ? 0 : cur+1), 4000);
    }

    // Responsive: recalc on resize
    window.addEventListener('resize', () => go(cur));
    go(0);
    return {go};
  }

  function getVisCount(){
    if(window.innerWidth >= 1024) return 3;
    if(window.innerWidth >= 640) return 2;
    return 1;
  }

  // Main slider
  if(track){
    const vc = getVisCount();
    const dotsCtr  = document.getElementById('rev-dots');
    const prevBtn  = document.getElementById('rev-prev');
    const nextBtn  = document.getElementById('rev-next');
    // Create dots
    if(dotsCtr){
      const cards = track.querySelectorAll('[data-slide]');
      const maxIdx = Math.max(0, cards.length - vc);
      dotsCtr.innerHTML = '';
      for(let i=0; i<=maxIdx; i++){
        const d = document.createElement('button');
        d.className = 'rev-dot' + (i===0?' active':'');
        d.dataset.dot = i;
        d.setAttribute('aria-label', 'Review ' + (i+1));
        dotsCtr.appendChild(d);
      }
    }
    makeSlider(track, dotsCtr, prevBtn, nextBtn, vc);
  }

  // Mini slider
  if(mini){
    const miniDots = document.getElementById('mini-rev-dots');
    if(miniDots){
      const cards = mini.querySelectorAll('[data-slide]');
      miniDots.innerHTML = '';
      cards.forEach((_,i) => {
        const d = document.createElement('button');
        d.className = 'mini-dot' + (i===0?' active':'');
        d.dataset.dot = i;
        d.setAttribute('aria-label', 'Review ' + (i+1));
        miniDots.appendChild(d);
      });
    }
    makeSlider(mini, miniDots, null, null, 1);
  }

  // Expand review text on click
  document.querySelectorAll('.rc-text').forEach(el => {
    el.addEventListener('click', () => el.classList.toggle('expanded'));
  });
})();
"""

# ── Build review HTML for each lang ──────────────────────────────────────────
def star_html(n=5, size=14):
    return "".join([f'<span style="font-size:{size}px;color:var(--sand)">★</span>']*n)

def avatar_letter(name, color):
    initial = name[0].upper()
    return f'<div class="rc-avatar" style="background:{color}">{initial}</div>'

def mini_avatar(name, color):
    initial = name[0].upper()
    return f'<div class="mini-rc-avatar" style="background:{color}">{initial}</div>'

def build_reviews_slider(lang):
    """Build the full reviews section HTML for a given language."""
    DATE_LABELS = {
        "fr": {"aujourd'hui":"aujourd'hui","il y a un mois":"il y a un mois","il y a 2 mois":"il y a 2 mois",
               "il y a 3 mois":"il y a 3 mois","il y a 3 semaines":"il y a 3 semaines",
               "il y a 4 mois":"il y a 4 mois","il y a 5 mois":"il y a 5 mois"},
        "en": {"aujourd'hui":"today","il y a un mois":"1 month ago","il y a 2 mois":"2 months ago",
               "il y a 3 mois":"3 months ago","il y a 3 semaines":"3 weeks ago",
               "il y a 4 mois":"4 months ago","il y a 5 mois":"5 months ago"},
        "es": {"aujourd'hui":"hoy","il y a un mois":"hace 1 mes","il y a 2 mois":"hace 2 meses",
               "il y a 3 mois":"hace 3 meses","il y a 3 semaines":"hace 3 semanas",
               "il y a 4 mois":"hace 4 meses","il y a 5 mois":"hace 5 meses"},
        "it": {"aujourd'hui":"oggi","il y a un mois":"1 mese fa","il y a 2 mois":"2 mesi fa",
               "il y a 3 mois":"3 mesi fa","il y a 3 semaines":"3 settimane fa",
               "il y a 4 mois":"4 mesi fa","il y a 5 mois":"5 mesi fa"},
        "de": {"aujourd'hui":"heute","il y a un mois":"vor 1 Monat","il y a 2 mois":"vor 2 Monaten",
               "il y a 3 mois":"vor 3 Monaten","il y a 3 semaines":"vor 3 Wochen",
               "il y a 4 mois":"vor 4 Monaten","il y a 5 mois":"vor 5 Monaten"},
    }
    TITLES = {
        "en":"What surfers say","fr":"Ce que disent les surfeurs",
        "es":"Lo que dicen los surfistas","it":"Cosa dicono i surfisti","de":"Was Surfer sagen"
    }
    LABELS = {
        "en":"reviews","fr":"avis","es":"reseñas","it":"recensioni","de":"Bewertungen"
    }
    GOOGLE_L = {
        "en":"View all on Google","fr":"Voir tous sur Google",
        "es":"Ver todos en Google","it":"Vedi tutti su Google","de":"Alle auf Google sehen"
    }
    LEAVE_L = {
        "en":"Leave a review","fr":"Laisser un avis",
        "es":"Dejar una reseña","it":"Lascia una recensione","de":"Bewertung schreiben"
    }
    VERIFIED_L = {
        "en":"Verified review","fr":"Avis vérifié",
        "es":"Reseña verificada","it":"Recensione verificata","de":"Verifizierte Bewertung"
    }
    CLICK_L = {
        "en":"Click to read more","fr":"Cliquer pour lire plus",
        "es":"Clic para leer más","it":"Clicca per leggere di più","de":"Klicken zum Weiterlesen"
    }

    dates = DATE_LABELS.get(lang, DATE_LABELS["en"])

    # Build cards
    cards_html = ""
    for rev in RAW_REVIEWS:
        rid  = rev["id"]
        data = reviews_data.get(rid, {})
        text = data.get(lang, data.get("fr", rev["text_fr"]))
        text = text.replace(" — ",", ").replace("—",",")
        date = dates.get(rev["date_fr"], rev["date_fr"])
        av   = avatar_letter(rev["author"], rev["avatar_color"])

        cards_html += f"""<div class="review-card" data-slide aria-label="Review by {rev['author']}">
  <div class="rc-head">
    {av}
    <div class="rc-info">
      <div class="rc-name">{rev['author']}</div>
      <div class="rc-meta">
        <span class="rc-flag">{rev['flag']}</span>
        <span class="rc-country">{rev['country']}</span>
        <span class="rc-date">{date}</span>
      </div>
    </div>
  </div>
  <div class="rc-stars">{star_html(rev['stars'])}</div>
  <p class="rc-text" title="{CLICK_L[lang]}">{text}</p>
  <div class="rc-verified">
    <svg viewBox="0 0 16 16" fill="none"><path d="M8 1L9.8 4.7L14 5.3L11 8.2L11.7 12.4L8 10.4L4.3 12.4L5 8.2L2 5.3L6.2 4.7L8 1Z" fill="#4285f4" stroke="#4285f4" stroke-width="0.5"/></svg>
    {VERIFIED_L[lang]}
  </div>
</div>\n"""

    # Google SVG
    GOOGLE_SVG = '<svg viewBox="0 0 24 24"><path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/><path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/><path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/><path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/></svg>'

    return f"""<section class="reviews-section" id="reviews" aria-label="Reviews">
  <div class="container">
    <div class="reviews-header">
      <div>
        <span class="s-label" style="color:var(--sand)">{TITLES[lang]}</span>
        <h2 class="s-title" style="color:#fff;margin-bottom:0">{TITLES[lang]}</h2>
      </div>
      <div class="reviews-rating-badge">
        <div class="reviews-score">4,1</div>
        <div class="reviews-stars-header">{star_html(4, 16)}<span style="font-size:16px;color:rgba(240,192,96,0.4)">★</span></div>
        <div class="reviews-count">56 {LABELS[lang]}</div>
        <div class="google-badge">{GOOGLE_SVG} Google</div>
      </div>
    </div>

    <div class="reviews-slider-wrap">
      <div class="reviews-track">
        <div class="reviews-inner" id="reviews-inner">
          {cards_html}
        </div>
      </div>
      <div class="reviews-nav">
        <button class="rev-arrow" id="rev-prev" aria-label="Previous reviews">
          <svg viewBox="0 0 24 24" fill="none"><path d="M15 18l-6-6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
        </button>
        <div class="rev-dots" id="rev-dots" role="tablist"></div>
        <button class="rev-arrow" id="rev-next" aria-label="Next reviews">
          <svg viewBox="0 0 24 24" fill="none"><path d="M9 6l6 6-6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
        </button>
      </div>
    </div>

    <div class="reviews-cta">
      <a href="https://www.google.com/maps/place/Ngor+Surfcamp+Teranga" target="_blank" rel="noopener" class="google-cta-btn">
        {GOOGLE_SVG}
        {GOOGLE_L[lang]}
      </a>
      <a href="https://www.google.com/maps/place/Ngor+Surfcamp+Teranga/@14.7504,-17.5169,17z/data=!4m8!3m7!1s0x0:0x0!8m2!3d14.7504!4d-17.5169!9m1!1b1" target="_blank" rel="noopener" class="google-cta-btn">
        {GOOGLE_SVG}
        {LEAVE_L[lang]}
      </a>
    </div>
  </div>
</section>"""

def build_mini_badge(lang):
    """Mini reviews widget for booking page."""
    TITLES = {
        "en":"Trusted by surfers worldwide","fr":"La confiance des surfeurs du monde entier",
        "es":"La confianza de surfistas de todo el mundo","it":"La fiducia dei surfisti di tutto il mondo",
        "de":"Das Vertrauen von Surfern weltweit"
    }
    FROM_L = {"en":"on Google","fr":"sur Google","es":"en Google","it":"su Google","de":"auf Google"}
    COUNT_L = {"en":"verified reviews","fr":"avis vérifiés","es":"reseñas verificadas","it":"recensioni verificate","de":"verifizierte Bewertungen"}

    # Pick 4 short reviews for mini slider
    mini_revs = [RAW_REVIEWS[0], RAW_REVIEWS[3], RAW_REVIEWS[4], RAW_REVIEWS[9]]
    mini_cards = ""
    for rev in mini_revs:
        rid = rev["id"]
        data = reviews_data.get(rid, {})
        text = data.get(lang, data.get("fr", rev["text_fr"]))
        text = text.replace(" — ",", ").replace("—",",")
        short = text[:200] + ("..." if len(text)>200 else "")
        av = mini_avatar(rev["author"], rev["avatar_color"])
        mini_cards += f"""<div class="mini-review-card" data-slide>
  <p class="mini-rc-text">"{short}"</p>
  <div class="mini-rc-author">
    {av}
    <div>
      <div class="mini-rc-name">{rev['author']} {rev['flag']}</div>
      <div class="mini-rc-stars">{star_html(5,12)}</div>
    </div>
  </div>
</div>\n"""

    GOOGLE_SVG = '<svg viewBox="0 0 24 24" width="16" height="16"><path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/><path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/><path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/><path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/></svg>'

    return f"""<div class="booking-review-badge" style="margin-top:28px">
  <div class="badge-score-row">
    <div class="badge-big-score">4,1</div>
    <div class="badge-score-info">
      <div class="badge-stars">{star_html(4,20)}<span style="font-size:20px;color:rgba(240,192,96,0.35)">★</span></div>
      <div class="badge-count">56 {COUNT_L[lang]}</div>
      <div class="badge-from" style="display:flex;align-items:center;gap:5px">{GOOGLE_SVG} {FROM_L[lang]}</div>
    </div>
  </div>
  <div style="font-size:13px;font-weight:700;color:rgba(255,255,255,0.6);margin-bottom:14px;text-transform:uppercase;letter-spacing:0.1em">{TITLES[lang]}</div>
  <div class="mini-review-slider">
    <div class="mini-reviews-inner" id="mini-reviews-inner">
      {mini_cards}
    </div>
  </div>
  <div class="mini-nav" id="mini-rev-dots"></div>
</div>"""

# ── Inject into HTML files ────────────────────────────────────────────────────
print("\n=== Injecting reviews slider into homepages ===")

# Add CSS once (to style.css)
current_css = open(f"{DEMO_DIR}/assets/css/style.css").read()
if "reviews-section" not in current_css:
    with open(f"{DEMO_DIR}/assets/css/style.css","a") as f:
        f.write("\n" + REVIEWS_CSS)
    print("  ✅ Reviews CSS added")
else:
    # Update existing
    css_content = current_css
    if "reviews-section" in css_content:
        start = css_content.find("/* ══════════════════════════════════════════════════════\n   GOOGLE REVIEWS SLIDER")
        if start > 0:
            # Replace old with new
            pass
    with open(f"{DEMO_DIR}/assets/css/style.css","a") as f:
        pass
    print("  ✅ Reviews CSS already present")

# Add slider JS to animations.js
anim_js = open(f"{DEMO_DIR}/assets/js/animations.js").read()
if "initReviewsSlider" not in anim_js:
    with open(f"{DEMO_DIR}/assets/js/animations.js","a") as f:
        f.write("\n" + SLIDER_JS)
    print("  ✅ Slider JS added to animations.js")

for lang in LANGS:
    pfx   = LANG_PFX[lang]
    hp    = f"{DEMO_DIR}{pfx}/index.html"
    if not os.path.exists(hp):
        print(f"  skip {lang}")
        continue

    with open(hp) as f: html = f.read()

    # 1. Replace testimonial section with review slider
    slider_html = build_reviews_slider(lang)

    # Remove old testimonial section entirely
    html = re.sub(
        r'<!-- TESTIMONIAL -->.*?</section>',
        slider_html,
        html, flags=re.DOTALL, count=1
    )
    # Also try the section pattern
    if "reviews-section" not in html:
        html = re.sub(
            r'<section class="section" aria-label="[Rr]eviews">.*?</section>',
            slider_html,
            html, flags=re.DOTALL, count=1
        )
    if "reviews-section" not in html:
        # Fallback: insert before blog preview section
        html = html.replace(
            '<!-- BLOG PREVIEW -->',
            slider_html + '\n\n  <!-- BLOG PREVIEW -->'
        )
        if "reviews-section" not in html:
            html = html.replace(
                '</section>\n\n  <!-- BLOG PREVIEW',
                f'</section>\n\n{slider_html}\n\n  <!-- BLOG PREVIEW'
            )

    # 2. Remove/improve the ugly badge strip
    # Replace the existing badge strip with a minimal one or remove it
    html = re.sub(
        r'<div class="badge-strip"[^>]*>.*?</div>\s*\n',
        '',
        html, flags=re.DOTALL
    )

    with open(hp,"w") as f: f.write(html)
    has_slider = "reviews-section" in html or "reviews-inner" in html
    print(f"  ✅ {lang}: homepage {'(slider added)' if has_slider else '(check manually)'}")

# ── Add review badge to booking pages ────────────────────────────────────────
print("\n=== Adding review badge to booking pages ===")
for lang in LANGS:
    pfx  = LANG_PFX[lang]
    bp   = f"{DEMO_DIR}{pfx}/booking/index.html"
    if not os.path.exists(bp): continue

    with open(bp) as f: html = f.read()
    if "booking-review-badge" in html:
        print(f"  [skip] {lang} booking"); continue

    badge = build_mini_badge(lang)
    # Insert after the direct contact section or before footer
    html = html.replace(
        '<!-- Direct contact -->',
        badge + '\n\n          <!-- Direct contact -->'
    )
    if "booking-review-badge" not in html:
        # Fallback: insert after sidebar trust badge
        html = html.replace(
            '</div>\n\n        </div>\n\n      </div>\n    </div>\n  </section>',
            f'{badge}\n</div>\n\n        </div>\n\n      </div>\n    </div>\n  </section>'
        )

    with open(bp,"w") as f: f.write(html)
    has_badge = "booking-review-badge" in open(bp).read()
    print(f"  ✅ {lang}: booking page {'(badge added)' if has_badge else '(check)'}")

print("\n✅ Reviews system complete!")
