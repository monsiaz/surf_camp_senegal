"""
Add FAQ accordion + Schema.org FAQPage JSON-LD to all article pages.
Finds h4.faq-inline-q + following p elements, converts to accordion.
"""
import os, re, json

DEMO  = "/Users/simonazoulay/SurfCampSenegal/cloudflare-demo"
LANGS = ["en","fr","es","it","de"]
LANG_PFX = {"en":"","fr":"/fr","es":"/es","it":"/it","de":"/de"}

FAQ_LABELS = {
    "en": "Frequently Asked Questions",
    "fr": "Questions Fréquentes",
    "es": "Preguntas Frecuentes",
    "it": "Domande Frequenti",
    "de": "Häufig gestellte Fragen",
}

# ── FAQ accordion CSS ─────────────────────────────────────────────────────────
FAQ_CSS = """
/* ══ ARTICLE FAQ ACCORDION ════════════════════════════════════ */
.article-faq-section {
  margin: 56px 0 0;
  border-radius: 20px;
  overflow: hidden;
  border: 1.5px solid rgba(10,37,64,0.10);
  background: #fff;
  box-shadow: 0 2px 20px rgba(10,37,64,0.06);
}
.article-faq-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 24px 32px;
  background: linear-gradient(135deg, var(--navy), #1a4a7a);
  color: #fff;
}
.article-faq-header h2 {
  font-size: clamp(18px, 2.5vw, 22px);
  color: #fff;
  margin: 0;
  font-weight: 700;
}
.article-faq-header .faq-schema-icon {
  width: 36px; height: 36px;
  background: rgba(255,255,255,0.12);
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  font-size: 18px;
}
.article-faq-item {
  border-bottom: 1px solid rgba(10,37,64,0.07);
  position: relative;
}
.article-faq-item:last-child { border-bottom: none; }
.article-faq-q {
  width: 100%;
  text-align: left;
  padding: 20px 32px 20px 28px;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  font-weight: 600;
  font-size: 15.5px;
  color: var(--navy);
  background: #fff;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
  border: none;
  font-family: var(--fh);
  line-height: 1.45;
}
.article-faq-q:hover { background: var(--sand3); }
.article-faq-item.open .article-faq-q {
  color: var(--fire);
  background: #fff9f6;
}
/* Number badge */
.article-faq-q::before {
  content: attr(data-num);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 26px; height: 26px;
  background: var(--fire-light, rgba(255,90,31,0.10));
  color: var(--fire);
  border-radius: 8px;
  font-size: 12px;
  font-weight: 800;
  flex-shrink: 0;
  margin-right: 4px;
  margin-top: 1px;
  font-family: var(--fh);
}
.faq-a-chevron {
  width: 22px; height: 22px;
  flex-shrink: 0;
  border-radius: 50%;
  background: rgba(10,37,64,0.07);
  display: flex; align-items: center; justify-content: center;
  transition: background 0.2s, transform 0.3s var(--spring);
  margin-top: 2px;
}
.article-faq-item.open .faq-a-chevron {
  background: rgba(255,90,31,0.12);
  transform: rotate(180deg);
}
.faq-a-chevron svg { color: var(--muted); }
.article-faq-item.open .faq-a-chevron svg { color: var(--fire); }
.article-faq-answer {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.4s cubic-bezier(0.4,0,0.2,1);
  background: #fff9f6;
  border-top: 1px solid rgba(255,90,31,0.08);
}
.article-faq-answer .faq-answer-inner {
  padding: 18px 32px 22px 60px;
}
.article-faq-answer p {
  color: #4b5563;
  font-size: 15.5px;
  line-height: 1.78;
  margin: 0;
}
.article-faq-item.open .article-faq-answer {
  max-height: 600px;
}
/* First item auto-open indicator */
.article-faq-item:first-of-type .article-faq-q::after {
  content: '';
  position: absolute;
  left: 0; top: 0; bottom: 0;
  width: 3px;
  background: var(--fire);
  border-radius: 0 2px 2px 0;
  opacity: 0;
  transition: opacity 0.2s;
}
.article-faq-item.open .article-faq-q::after { opacity: 1; }

@media(max-width:640px){
  .article-faq-header { padding: 20px; }
  .article-faq-q { padding: 16px 20px 16px 16px; font-size: 14.5px; }
  .article-faq-answer .faq-answer-inner { padding: 14px 20px 18px 20px; }
}
"""

CHEV_SVG = '<svg viewBox="0 0 16 16" fill="none" width="14" height="14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 6l4 4 4-4"/></svg>'

# ── Extract Q&A pairs from article HTML ───────────────────────────────────────
def extract_faq_pairs(html):
    """Find FAQ section in article HTML, extract Q&A pairs."""
    # Locate FAQ heading
    faq_start = -1
    for pattern in ['id="faq">', '>FAQ</h2>', '>Frequently Asked', '>Questions Fréquentes', 
                    '>Preguntas Frecuentes', '>Domande Frequenti', '>Häufig gestellte']:
        idx = html.find(pattern)
        if idx > 0:
            faq_start = idx
            break
    
    if faq_start < 0:
        return [], faq_start
    
    # Get the FAQ section (from h2 to end of prose or next h2/section)
    faq_section = html[faq_start:]
    # Stop at next h2 that's NOT the FAQ itself, or at prose div end
    next_h2 = faq_section.find('<h2 ', 50)
    if next_h2 > 0:
        faq_section = faq_section[:next_h2]
    
    # Extract Q&A pairs using h4.faq-inline-q and following p
    pairs = []
    
    # Pattern: <h4 class="faq-inline-q">QUESTION</h4> followed by <p>ANSWER</p>
    pattern = re.compile(
        r'<h4[^>]*class="faq-inline-q"[^>]*>(.*?)</h4>\s*<p>(.*?)</p>',
        re.DOTALL
    )
    
    for m in pattern.finditer(faq_section):
        question = m.group(1).strip()
        answer   = m.group(2).strip()
        # Clean up HTML tags in question/answer for schema
        question_clean = re.sub(r'<[^>]+>', '', question)
        answer_clean   = re.sub(r'<[^>]+>', '', answer)
        pairs.append({
            "q": question_clean,
            "a": answer_clean,
            "q_html": question,
            "a_html": answer,
        })
    
    return pairs, faq_start

def build_faq_accordion(pairs, lang, article_title=""):
    """Build accordion HTML + JSON-LD for FAQ pairs."""
    if not pairs:
        return "", ""
    
    label = FAQ_LABELS.get(lang, "Frequently Asked Questions")
    
    # Build accordion items
    items_html = ""
    for i, pair in enumerate(pairs):
        num = str(i + 1)
        # First item open by default
        cls = "article-faq-item open" if i == 0 else "article-faq-item"
        ans_style = "" if i == 0 else ""
        items_html += f'''<div class="{cls}" itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
  <button class="article-faq-q" data-num="{num}" onclick="toggleArticleFaq(this)" aria-expanded="{"true" if i==0 else "false"}">
    <span itemprop="name">{pair["q_html"]}</span>
    <span class="faq-a-chevron">{CHEV_SVG}</span>
  </button>
  <div class="article-faq-answer" itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
    <div class="faq-answer-inner">
      <p itemprop="text">{pair["a_html"]}</p>
    </div>
  </div>
</div>'''
    
    accordion_html = f'''<div class="article-faq-section" itemscope itemtype="https://schema.org/FAQPage" aria-label="{label}">
  <div class="article-faq-header">
    <div class="faq-schema-icon">❓</div>
    <h2>{label}</h2>
  </div>
  {items_html}
</div>'''
    
    # Build JSON-LD
    schema_entities = []
    for pair in pairs:
        schema_entities.append({
            "@type": "Question",
            "name": pair["q"],
            "acceptedAnswer": {
                "@type": "Answer",
                "text": pair["a"]
            }
        })
    
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "name": article_title,
        "mainEntity": schema_entities
    }
    
    schema_tag = f'<script type="application/ld+json">\n{json.dumps(schema, ensure_ascii=False, indent=2)}\n</script>'
    
    return accordion_html, schema_tag

def process_article_faq(html, lang):
    """Find FAQ section in HTML, replace with accordion + add JSON-LD."""
    pairs, faq_start = extract_faq_pairs(html)
    if not pairs or faq_start < 0:
        return html, 0
    
    # Get article title for schema
    title_m = re.search(r'<title>([^<]+)</title>', html)
    article_title = title_m.group(1) if title_m else ""
    
    # Build the new FAQ section
    accordion_html, schema_tag = build_faq_accordion(pairs, lang, article_title)
    
    # Find the exact h2 FAQ heading in the original HTML (just before the Q&As)
    # Pattern: find <h2 ...>FAQ</h2> with optional anchor id
    faq_h2_pattern = re.compile(r'<h2[^>]*>(?:FAQ|Frequently Asked Questions|Questions Fréquentes|Preguntas Frecuentes|Domande Frequenti|Häufig gestellte Fragen)<\/h2>')
    faq_h2_match = faq_h2_pattern.search(html)
    
    if faq_h2_match:
        # Find the end of the FAQ section (all h4+p pairs)
        faq_end_search = html[faq_h2_match.start():]
        
        # Find where FAQ Q&As end (next h2 or major section)
        next_major = re.search(r'<(?:h2|div class="share-row|div class="art-cta|div class="related|div style="margin-top:48)', faq_end_search[50:])
        if next_major:
            faq_block = faq_end_search[:50 + next_major.start()]
        else:
            # Take a reasonable chunk
            faq_block = faq_end_search[:2000]
        
        # Replace the old FAQ block with new accordion
        new_html = html[:faq_h2_match.start()] + accordion_html + html[faq_h2_match.start() + len(faq_block):]
        
        # Add JSON-LD schema before </head>
        new_html = new_html.replace('</head>', schema_tag + '\n</head>', 1)
        
        return new_html, len(pairs)
    
    return html, 0

# ── Apply to all article pages ────────────────────────────────────────────────
print("=== Adding FAQ accordion + Schema.org to all articles ===")

# Add CSS once
css_path = f"{DEMO}/assets/css/style.css"
with open(css_path,'a') as f: f.write('\n' + FAQ_CSS)
print("✅ FAQ CSS added")

# Add FAQ JS to animations.js
faq_js = """
/* ── Article FAQ Accordion ─────────────────────────────────── */
function toggleArticleFaq(btn) {
  const item = btn.closest('.article-faq-item');
  const isOpen = item.classList.contains('open');
  const answer = item.querySelector('.article-faq-answer');
  
  // Close all others in same FAQ section
  const section = item.closest('.article-faq-section');
  if (section) {
    section.querySelectorAll('.article-faq-item.open').forEach(other => {
      if (other !== item) {
        other.classList.remove('open');
        other.querySelector('button').setAttribute('aria-expanded', 'false');
      }
    });
  }
  
  item.classList.toggle('open', !isOpen);
  btn.setAttribute('aria-expanded', String(!isOpen));
}

// Auto-open first FAQ item
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.article-faq-section').forEach(section => {
    const first = section.querySelector('.article-faq-item');
    if (first && !first.classList.contains('open')) {
      first.classList.add('open');
      const btn = first.querySelector('button');
      if (btn) btn.setAttribute('aria-expanded', 'true');
    }
  });
});
"""

anim_path = f"{DEMO}/assets/js/animations.js"
with open(anim_path,'a') as f: f.write('\n' + faq_js)
print("✅ FAQ JS added")

# Process all articles
total_faq    = 0
total_pages  = 0
lang_counter = {}

for root, dirs, files in os.walk(DEMO):
    dirs[:] = [d for d in dirs if not d.startswith('.')]
    for fname in files:
        if not fname.endswith('.html'): continue
        fpath = os.path.join(root, fname)
        if '/blog/' not in fpath: continue
        
        with open(fpath) as f: html = f.read()
        if 'http-equiv="refresh"' in html: continue
        if len(html) < 5000: continue  # Skip small pages (blog listing etc.)
        
        # Detect language
        lang = "en"
        path = fpath.replace(DEMO,"")
        for l in ["fr","es","it","de"]:
            if path.startswith(f'/{l}/'): lang = l; break
        
        new_html, n_pairs = process_article_faq(html, lang)
        if n_pairs > 0:
            with open(fpath,'w') as f: f.write(new_html)
            total_faq   += n_pairs
            total_pages += 1
            lang_counter[lang] = lang_counter.get(lang,0) + 1

print(f"\n✅ Processed {total_pages} article pages")
print(f"✅ Total FAQ pairs: {total_faq}")
print(f"By language: {lang_counter}")

# Verify
with open(f'{DEMO}/blog/why-choose-surf-camp-senegal/index.html') as f: h = f.read()
has_accordion = 'article-faq-section' in h
has_schema    = 'FAQPage' in h
has_jsonld    = 'application/ld+json' in h
print(f"\nVerification EN article: accordion={has_accordion} schema={has_schema} jsonld={has_jsonld}")
