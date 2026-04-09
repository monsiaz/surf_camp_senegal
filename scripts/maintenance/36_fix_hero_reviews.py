"""
Fix 1: Hero video — 720p source, less overlay, CSS sharpening, no grain
Fix 2: Reviews slider — better card distribution, clean navigation, CSS harmonized
"""
import os, re

DEMO  = "/Users/simonazoulay/SurfCampSenegal/cloudflare-demo"
LANGS = ["en","fr","es","it","de"]
LANG_PFX = {"en":"","fr":"/fr","es":"/es","it":"/it","de":"/de"}

# ════════════════════════════════════════════════════════════════
# CSS FIXES
# ════════════════════════════════════════════════════════════════
CSS_PATCH = """
/* ══ HERO VIDEO v2 — sharper, less overlay ══════════════════════ */
.hero-video-wrap video {
  width: 100%; height: 100%;
  object-fit: cover;
  filter: contrast(1.12) saturate(1.18) brightness(0.93);
  will-change: transform;
}
.hero-video-wrap::before {
  /* Reduced opacity overlay — let the video breathe */
  background:
    radial-gradient(ellipse at 65% 40%, rgba(255,90,31,0.08) 0%, transparent 45%),
    linear-gradient(168deg, rgba(6,16,30,0.58) 0%, rgba(6,16,30,0.28) 45%, rgba(0,0,0,0.62) 100%);
}
/* Remove grain overlay */
.hero-video-wrap::after { display: none; }

/* ══ REVIEWS SLIDER v2 — better card distribution ═══════════════ */
.reviews-section {
  padding: 80px 0 72px;
}
.reviews-header {
  margin-bottom: 44px;
}
.reviews-track {
  overflow: hidden;
  /* Remove negative margin so cards align to container */
  margin: 0;
  border-radius: 16px;
}
.reviews-inner {
  display: flex;
  gap: 16px;
  padding: 4px 2px 16px;
  transition: transform 0.55s cubic-bezier(0.4,0,0.2,1);
  will-change: transform;
}
/* Review card — better proportioned */
.review-card {
  flex: 0 0 calc(33.333% - 11px);
  min-width: 0;
  background: rgba(255,255,255,0.07);
  backdrop-filter: blur(16px) saturate(160%);
  -webkit-backdrop-filter: blur(16px) saturate(160%);
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: 18px;
  padding: 26px 24px 22px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15), inset 0 1px 0 rgba(255,255,255,0.07);
  transition: transform 0.3s, box-shadow 0.3s, background 0.3s;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.review-card::before {
  content: '"';
  position: absolute; top: 10px; right: 18px;
  font-size: 64px; line-height: 1;
  font-family: Georgia, serif;
  color: rgba(255,255,255,0.05);
  pointer-events: none;
}
.review-card:hover {
  transform: translateY(-4px);
  background: rgba(255,255,255,0.11);
  box-shadow: 0 14px 40px rgba(0,0,0,0.25), inset 0 1px 0 rgba(255,255,255,0.10);
}
.rc-head {
  display: flex; align-items: center; gap: 11px;
  flex-shrink: 0;
}
.rc-avatar {
  width: 42px; height: 42px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-family: var(--fh); font-weight: 800; font-size: 16px; color: #fff;
  flex-shrink: 0; border: 1.5px solid rgba(255,255,255,0.15);
}
.rc-info { flex: 1; min-width: 0; }
.rc-name { font-weight: 700; font-size: 14.5px; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.rc-meta { display: flex; align-items: center; gap: 5px; margin-top: 2px; }
.rc-flag { font-size: 13px; }
.rc-country { font-size: 11.5px; color: rgba(255,255,255,0.42); }
.rc-date { font-size: 11px; color: rgba(255,255,255,0.32); margin-left: auto; }
.rc-stars { display: flex; gap: 2px; flex-shrink: 0; }
.rc-stars span { color: var(--sand); font-size: 13px; }
.rc-text {
  font-size: 14px; line-height: 1.70; color: rgba(255,255,255,0.76);
  flex: 1;
  /* Clamp to 5 lines, click to expand */
  display: -webkit-box;
  -webkit-line-clamp: 5;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.rc-text.expanded { -webkit-line-clamp: unset; cursor: default; }
.rc-verified {
  display: inline-flex; align-items: center; gap: 4px;
  font-size: 11px; color: rgba(255,255,255,0.32);
  flex-shrink: 0;
}
.rc-verified svg { color: #4285f4; }

/* Navigation */
.reviews-nav {
  display: flex; align-items: center; justify-content: center;
  gap: 12px; margin-top: 28px;
}
.rev-arrow {
  width: 44px; height: 44px; border-radius: 50%;
  background: rgba(255,255,255,0.08);
  border: 1.5px solid rgba(255,255,255,0.14);
  color: rgba(255,255,255,0.7);
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
  transition: background 0.2s, color 0.2s, transform 0.2s, border-color 0.2s;
  flex-shrink: 0;
}
.rev-arrow:hover:not(:disabled) {
  background: var(--fire);
  border-color: var(--fire);
  color: #fff;
  transform: scale(1.06);
}
.rev-arrow:disabled { opacity: 0.28; cursor: not-allowed; pointer-events: none; }
.rev-arrow svg { width: 18px; height: 18px; }

/* Dots — compact pill style */
.rev-dots { display: flex; gap: 6px; align-items: center; }
.rev-dot {
  height: 6px; width: 6px; border-radius: 3px;
  background: rgba(255,255,255,0.22);
  cursor: pointer;
  transition: background 0.25s, width 0.3s cubic-bezier(0.4,0,0.2,1);
  border: none;
  padding: 0;
}
.rev-dot.active {
  background: var(--fire);
  width: 22px;
  border-radius: 3px;
}

/* Google CTA row */
.reviews-cta {
  display: flex; justify-content: center; gap: 14px;
  margin-top: 32px; flex-wrap: wrap;
}
.google-cta-btn {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 11px 20px; border-radius: var(--r-pill);
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.14);
  color: rgba(255,255,255,0.78);
  font-size: 13.5px; font-weight: 600;
  transition: background 0.2s, color 0.2s, transform 0.2s;
}
.google-cta-btn:hover { background: rgba(255,255,255,0.16); color: #fff; transform: translateY(-1px); }
.google-cta-btn svg { width: 16px; height: 16px; flex-shrink: 0; }

/* Rating badge */
.reviews-rating-badge {
  padding: 16px 20px; border-radius: 18px;
  background: rgba(255,255,255,0.07);
  backdrop-filter: blur(14px);
  border: 1px solid rgba(255,255,255,0.12);
  text-align: center; min-width: 110px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.2), inset 0 1px 0 rgba(255,255,255,0.07);
}
.reviews-score {
  font-family: var(--fh); font-size: 44px; font-weight: 900; line-height: 1;
  background: linear-gradient(135deg, var(--sand), #fff);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.reviews-stars-header { display: flex; gap: 3px; justify-content: center; margin: 4px 0 2px; }
.reviews-stars-header span { font-size: 16px; color: var(--sand); }
.reviews-count { font-size: 11.5px; opacity: 0.5; }
.google-badge { display: flex; align-items: center; justify-content: center; gap: 5px; font-size: 11px; color: rgba(255,255,255,0.45); margin-top: 5px; }
.google-badge svg { width: 14px; height: 14px; }

/* Responsive */
@media(max-width:960px){
  .review-card { flex: 0 0 calc(50% - 8px); }
}
@media(max-width:600px){
  .review-card { flex: 0 0 calc(100% - 0px); }
  .reviews-header { flex-direction: column; align-items: flex-start; }
}
"""

css_path = f"{DEMO}/assets/css/ngor-surfcamp.css"
with open(css_path,'a') as f: f.write('\n/* === hero+reviews v2 === */\n' + CSS_PATCH)
print("✅ CSS patch applied")

# ════════════════════════════════════════════════════════════════
# FIX HERO VIDEO — 720p source + no grain overlay
# ════════════════════════════════════════════════════════════════
VIDEO_POSTER = "/assets/images/wix/df99f9_da0cf7c72b1a4606bcfa1f7c8e089dc4f000.webp"

NEW_VIDEO_TAG = f"""<video id="hero-video" autoplay muted playsinline preload="none" poster="{VIDEO_POSTER}" style="width:100%;height:100%;object-fit:cover">
        <source src="/assets/video/hero-ngor-720p.mp4" type="video/mp4">
        <source src="/assets/video/hero-ngor-480p.mp4" type="video/mp4">
        <source src="/assets/video/hero-ngor-360p.mp4" type="video/mp4">
      </video>"""

# Regex to find and replace existing video tag
OLD_VIDEO_RE = re.compile(
    r'<video id="hero-video"[^>]*>.*?</video>',
    re.DOTALL
)

total_video = 0
for lang in LANGS:
    spfx = f"/{lang}" if lang != "en" else ""
    hp = f"{DEMO}{spfx}/index.html"
    if not os.path.exists(hp): continue
    with open(hp) as f: html = f.read()
    new_html, n = OLD_VIDEO_RE.subn(NEW_VIDEO_TAG, html, count=1)
    if n:
        with open(hp,'w') as f: f.write(new_html)
        total_video += 1
        print(f"  ✅ {lang}: hero video → 720p")

print(f"Video updated: {total_video}/5")

# ════════════════════════════════════════════════════════════════
# FIX REVIEWS SLIDER JS — ensure correct dots generation
# ════════════════════════════════════════════════════════════════
# Replace the review slider JS to show max 5 dots and fix mobile behavior
NEW_SLIDER_JS = """
/* ── Reviews Slider v2 ─────────────────────────────────────── */
(function initReviewsSlider(){
  const track = document.getElementById('reviews-inner');
  if(!track) return;

  const cards    = track.querySelectorAll('.review-card');
  const dotsCtr  = document.getElementById('rev-dots');
  const prevBtn  = document.getElementById('rev-prev');
  const nextBtn  = document.getElementById('rev-next');
  const total    = cards.length;
  let cur = 0;

  function visCount(){
    if(window.innerWidth >= 960) return 3;
    if(window.innerWidth >= 600) return 2;
    return 1;
  }

  function maxIdx(){ return Math.max(0, total - visCount()); }

  // Build dots
  function buildDots(){
    if(!dotsCtr) return;
    const max = maxIdx();
    const numDots = Math.min(max + 1, 7);
    dotsCtr.innerHTML = '';
    for(let i = 0; i <= Math.min(max, numDots - 1); i++){
      const d = document.createElement('button');
      d.className = 'rev-dot' + (i === 0 ? ' active' : '');
      d.setAttribute('aria-label', 'Review group ' + (i + 1));
      d.dataset.idx = i;
      d.addEventListener('click', () => go(parseInt(d.dataset.idx)));
      dotsCtr.appendChild(d);
    }
  }

  function updateDots(){
    if(!dotsCtr) return;
    [...dotsCtr.querySelectorAll('.rev-dot')].forEach((d, i) => {
      d.classList.toggle('active', parseInt(d.dataset.idx) === cur);
    });
  }

  function go(idx){
    const max = maxIdx();
    cur = Math.max(0, Math.min(idx, max));
    const card = cards[0];
    const cardW = card ? card.getBoundingClientRect().width : 0;
    const gap   = 16;
    track.style.transform = 'translateX(-' + (cur * (cardW + gap)) + 'px)';
    updateDots();
    if(prevBtn) prevBtn.disabled = cur === 0;
    if(nextBtn) nextBtn.disabled = cur >= max;
  }

  // Build initial dots
  buildDots();
  go(0);

  // Buttons
  if(prevBtn) prevBtn.addEventListener('click', () => go(cur - 1));
  if(nextBtn) nextBtn.addEventListener('click', () => go(cur + 1));

  // Touch swipe
  let startX = 0;
  track.parentElement.addEventListener('touchstart', e => { startX = e.touches[0].clientX; }, {passive:true});
  track.parentElement.addEventListener('touchend', e => {
    const diff = startX - e.changedTouches[0].clientX;
    if(Math.abs(diff) > 50) go(diff > 0 ? cur + 1 : cur - 1);
  }, {passive:true});

  // Recalc on resize
  let resizeTimer;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => { buildDots(); go(Math.min(cur, maxIdx())); }, 200);
  }, {passive:true});

  // Expand review text on click
  document.querySelectorAll('.rc-text').forEach(el => {
    el.addEventListener('click', () => el.classList.toggle('expanded'));
    el.style.cursor = 'pointer';
    el.title = 'Click to expand';
  });

  // Auto-play
  let autoTimer = setInterval(() => {
    if(cur < maxIdx()) go(cur + 1);
    else go(0);
  }, 5000);
  track.parentElement.addEventListener('mouseenter', () => clearInterval(autoTimer));
  track.parentElement.addEventListener('mouseleave', () => {
    autoTimer = setInterval(() => {
      if(cur < maxIdx()) go(cur + 1); else go(0);
    }, 5000);
  });
})();
"""

# Replace existing slider JS in animations.js
anim_path = f"{DEMO}/assets/js/ngor-surfcamp.js"
with open(anim_path) as f: js = f.read()

# Remove old slider function (if any)
OLD_SLIDER_RE = re.compile(
    r'/\* ── Google Reviews Slider.*?(?=/\* ──|\Z)',
    re.DOTALL
)
# Remove old initReviewsSlider calls/functions
OLD_INIT_RE = re.compile(
    r'\(function initReviewsSlider\(\).*?\}\)\(\);',
    re.DOTALL
)

new_js = OLD_INIT_RE.sub('', js)
new_js = OLD_SLIDER_RE.sub('', new_js)

# Append new slider JS
new_js += "\n" + NEW_SLIDER_JS

with open(anim_path,'w') as f: f.write(new_js)
print("✅ Reviews slider JS updated")

print("\n✅ All fixes applied!")
