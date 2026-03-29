#!/usr/bin/env python3
"""
Patch build.py, surf_house_page.py, 28_fix_blocks.py, 22_build_surfing_faq.py
to add nl (Dutch) and ar (Arabic/Morocco) language support.
"""
import json, os, re, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load translations
T_UI    = json.load(open(os.path.join(BASE, "scripts", "translations_nl_ar.json"), encoding="utf-8"))
T_PAGES = json.load(open(os.path.join(BASE, "scripts", "translations_pages_nl_ar.json"), encoding="utf-8"))
T_BLOG  = json.load(open(os.path.join(BASE, "scripts", "translations_blog_nl_ar.json"), encoding="utf-8"))

def t_ui(section, key, lang):
    return T_UI.get(section, {}).get(key, {}).get(lang, f"[{lang}:{key}]")

def t_pages(section, key, lang):
    return T_PAGES.get(section, {}).get(lang, {}).get(key, f"[{lang}:{key}]")

def t_blog(section, key, lang):
    return T_BLOG.get(section, {}).get(lang, {}).get(key, f"[{lang}:{key}]")

# ─────────────────────────────────────────────────────────────────────────────
# 1. PATCH build.py
# ─────────────────────────────────────────────────────────────────────────────
build_path = os.path.join(BASE, "build.py")
with open(build_path, encoding="utf-8") as f:
    bp = f.read()

# 1a. LANGS
bp = bp.replace(
    'LANGS    = ["en","fr","es","it","de"]',
    'LANGS    = ["en","fr","es","it","de","nl","ar"]'
)

# 1b. LANG_PFX
bp = bp.replace(
    'LANG_PFX = {"en":"","fr":"/fr","es":"/es","it":"/it","de":"/de"}',
    'LANG_PFX = {"en":"","fr":"/fr","es":"/es","it":"/it","de":"/de","nl":"/nl","ar":"/ar"}'
)

# 1c. LANG_LOCALE
bp = bp.replace(
    'LANG_LOCALE = {"en":"en","fr":"fr-FR","es":"es-ES","it":"it-IT","de":"de-DE"}',
    'LANG_LOCALE = {"en":"en","fr":"fr-FR","es":"es-ES","it":"it-IT","de":"de-DE","nl":"nl-NL","ar":"ar-MA"}'
)

# 1d. LANG_NAMES
bp = bp.replace(
    'LANG_NAMES  = {"en":"English","fr":"Français","es":"Español","it":"Italiano","de":"Deutsch"}',
    'LANG_NAMES  = {"en":"English","fr":"Français","es":"Español","it":"Italiano","de":"Deutsch","nl":"Nederlands","ar":"العربية"}'
)

# 1e. SLUG – add nl and ar entries after de
slug_de = '''    "de": {"surf-house":"surf-house","island":"insel","surfing":"surfen",
           "booking":"buchen","gallery":"galerie","faq":"faq","blog":"blog",
           "privacy-policy":"datenschutzrichtlinie","category":"kategorie"},
}'''

slug_nl_slug = t_ui("SLUG", "surf-house", "nl")  # surfhuis or keep surf-house for SEO
# For NL, use Dutch slugs. For AR, keep ASCII slugs for clean URLs
slug_new = f'''    "de": {{"surf-house":"surf-house","island":"insel","surfing":"surfen",
           "booking":"buchen","gallery":"galerie","faq":"faq","blog":"blog",
           "privacy-policy":"datenschutzrichtlinie","category":"kategorie"}},
    "nl": {{"surf-house":"surf-house","island":"eiland","surfing":"surfen",
           "booking":"boeken","gallery":"galerij","faq":"faq","blog":"blog",
           "privacy-policy":"privacybeleid","category":"categorie"}},
    "ar": {{"surf-house":"surf-house","island":"ngor-island","surfing":"surf",
           "booking":"reservation","gallery":"galerie","faq":"faq","blog":"blog",
           "privacy-policy":"privacy-policy","category":"categorie"}},
}}'''
bp = bp.replace(slug_de, slug_new)

# 1f. FLAG_SVG – add NL (Netherlands) and MA (Morocco) flags
flag_de_end = '''    "de": \'<svg viewBox="0 0 60 40"><rect width="60" height="13" fill="#000"/><rect y="13" width="60" height="14" fill="#DD0000"/><rect y="27" width="60" height="13" fill="#FFCE00"/></svg>\',
}'''

flag_new_end = '''    "de": \'<svg viewBox="0 0 60 40"><rect width="60" height="13" fill="#000"/><rect y="13" width="60" height="14" fill="#DD0000"/><rect y="27" width="60" height="13" fill="#FFCE00"/></svg>\',
    "nl": \'<svg viewBox="0 0 60 40"><rect width="60" height="13" fill="#AE1C28"/><rect y="13" width="60" height="14" fill="#fff"/><rect y="27" width="60" height="13" fill="#21468B"/></svg>\',
    "ar": \'<svg viewBox="0 0 60 40"><rect width="60" height="14" fill="#006233"/><rect y="14" width="60" height="12" fill="#fff"/><rect y="26" width="60" height="14" fill="#C1272D"/><path d="M30,8 L32.1,14.3 L38.7,14.3 L33.3,18.2 L35.4,24.4 L30,20.5 L24.6,24.4 L26.7,18.2 L21.3,14.3 L27.9,14.3 Z" fill="#006233" transform="scale(0.55) translate(27,0)"/></svg>\',
}}'''
bp = bp.replace(flag_de_end, flag_new_end)

# 1g. BLOG_CATS – add nl and ar to each category's slug, name, desc
blog_cats_de_coaching = '''        "de": "coaching-fortschritt",
        },
        "name": {
            "en": "Coaching & Progression",
            "fr": "Coaching & Progression",
            "es": "Coaching & Progresión",
            "it": "Coaching & Progressione",
            "de": "Coaching & Fortschritt",
        },
        "desc": {
            "en": "Surf coaching guides, how to improve faster at a surf camp, video analysis, beginner tips and how to choose the best surf camp for your level.",
            "fr": "Guides de coaching surf, progresser plus vite en surf camp, analyse vidéo, conseils pour débutants et comment choisir le meilleur surf camp.",
            "es": "Guías de coaching surf, cómo mejorar más rápido en un surf camp, análisis de vídeo, consejos para principiantes y cómo elegir el mejor surf camp.",
            "it": "Guide al coaching surf, come migliorare più velocemente in un surf camp, analisi video, consigli per principianti e come scegliere il surf camp migliore.",
            "de": "Surf-Coaching-Guides, wie man im Surfcamp schneller besser wird, Videoanalyse, Anfänger-Tipps und wie man das beste Surfcamp wählt.",
        },'''

blog_cats_new_coaching = '''        "de": "coaching-fortschritt",
            "nl": "coaching-progressie",
            "ar": "coaching-progression",
        },
        "name": {
            "en": "Coaching & Progression",
            "fr": "Coaching & Progression",
            "es": "Coaching & Progresión",
            "it": "Coaching & Progressione",
            "de": "Coaching & Fortschritt",
            "nl": "Coaching & Progressie",
            "ar": "التدريب والتطور",
        },
        "desc": {
            "en": "Surf coaching guides, how to improve faster at a surf camp, video analysis, beginner tips and how to choose the best surf camp for your level.",
            "fr": "Guides de coaching surf, progresser plus vite en surf camp, analyse vidéo, conseils pour débutants et comment choisir le meilleur surf camp.",
            "es": "Guías de coaching surf, cómo mejorar más rápido en un surf camp, análisis de vídeo, consejos para principiantes y cómo elegir el mejor surf camp.",
            "it": "Guide al coaching surf, come migliorare più velocemente in un surf camp, analisi video, consigli per principianti e come scegliere il surf camp migliore.",
            "de": "Surf-Coaching-Guides, wie man im Surfcamp schneller besser wird, Videoanalyse, Anfänger-Tipps und wie man das beste Surfcamp wählt.",
            "nl": "Surfcoaching-gidsen, sneller verbeteren in een surfkamp, videoanalyse, tips voor beginners en hoe je het beste surfkamp kiest.",
            "ar": "أدلة تدريب ركوب الأمواج، كيفية التحسن بشكل أسرع في مخيم الأمواج، تحليل الفيديو، نصائح للمبتدئين وكيفية اختيار أفضل مخيم ركوب أمواج.",
        },'''

bp = bp.replace(blog_cats_de_coaching, blog_cats_new_coaching)

# Also patch the first two categories (island-life and surf-conditions)
blog_cats_de_island = '''        "de": "insel-leben",
        },
        "name": {
            "en": "Island Life & Surf Camp",
            "fr": "Vie sur l'île & Surf Camp",
            "es": "Vida en la isla & Surf Camp",
            "it": "Vita sull'isola & Surf Camp",
            "de": "Inselleben & Surf Camp",
        },
        "desc": {
            "en": "Discover what life at Ngor Surf Camp is really like — island living, local culture, what to pack, and why Senegal is an underrated surf destination.",
            "fr": "Découvrez la vie au Ngor Surf Camp — île sans voitures, culture locale, quoi emporter et pourquoi le Sénégal est une destination surf sous-estimée.",
            "es": "Descubre cómo es la vida en el Ngor Surf Camp — isla sin coches, cultura local, qué llevar y por qué Senegal es un destino surf infravalorado.",
            "it": "Scopri com'è la vita al Ngor Surf Camp — isola senza auto, cultura locale, cosa portare e perché il Senegal è una destinazione surf sottovalutata.",
            "de": "Entdecke das Leben im Ngor Surf Camp — autofreie Insel, lokale Kultur, Packliste und warum Senegal ein unterschätztes Surf-Ziel ist.",
        },'''

blog_cats_new_island = '''        "de": "insel-leben",
            "nl": "eiland-leven",
            "ar": "island-life",
        },
        "name": {
            "en": "Island Life & Surf Camp",
            "fr": "Vie sur l'île & Surf Camp",
            "es": "Vida en la isla & Surf Camp",
            "it": "Vita sull'isola & Surf Camp",
            "de": "Inselleben & Surf Camp",
            "nl": "Eilandleven & Surfcamp",
            "ar": "حياة الجزيرة ومخيم الأمواج",
        },
        "desc": {
            "en": "Discover what life at Ngor Surf Camp is really like — island living, local culture, what to pack, and why Senegal is an underrated surf destination.",
            "fr": "Découvrez la vie au Ngor Surf Camp — île sans voitures, culture locale, quoi emporter et pourquoi le Sénégal est une destination surf sous-estimée.",
            "es": "Descubre cómo es la vida en el Ngor Surf Camp — isla sin coches, cultura local, qué llevar y por qué Senegal es un destino surf infravalorado.",
            "it": "Scopri com'è la vita al Ngor Surf Camp — isola senza auto, cultura locale, cosa portare e perché il Senegal è una destinazione surf sottovalutata.",
            "de": "Entdecke das Leben im Ngor Surf Camp — autofreie Insel, lokale Kultur, Packliste und warum Senegal ein unterschätztes Surf-Ziel ist.",
            "nl": "Ontdek hoe het leven in het Ngor Surf Camp echt is — eilandleven, lokale cultuur, wat mee te nemen en waarom Senegal een onderschat surfbestemming is.",
            "ar": "اكتشف كيف هي الحياة في مخيم نغور للأمواج — العيش على الجزيرة، الثقافة المحلية، ما تحمله، ولماذا السنغال وجهة أمواج مهمَلة.",
        },'''
bp = bp.replace(blog_cats_de_island, blog_cats_new_island)

blog_cats_de_surf = '''        "de": "surf-bedingungen",
        },
        "name": {
            "en": "Surf Conditions & Spots",
            "fr": "Conditions & Spots de Surf",
            "es": "Condiciones & Spots de Surf",
            "it": "Condizioni & Spot di Surf",
            "de": "Surf-Bedingungen & Spots",
        },
        "desc": {
            "en": "Everything about Ngor Island's waves, the best time to surf Senegal, surf season guides and detailed breakdowns of Ngor Right and Left.",
            "fr": "Tout sur les vagues de l'île de Ngor, la meilleure saison pour surfer au Sénégal et les guides détaillés de Ngor Right et Left.",
            "es": "Todo sobre las olas de la isla de Ngor, la mejor temporada para surfear en Senegal y guías detalladas de Ngor Right y Left.",
            "it": "Tutto sulle onde dell'isola di Ngor, il periodo migliore per fare surf in Senegal e guide dettagliate su Ngor Right e Left.",
            "de": "Alles über die Wellen der Insel Ngor, die beste Surfsaison in Senegal und detaillierte Guides zu Ngor Right und Left.",
        },'''

blog_cats_new_surf = '''        "de": "surf-bedingungen",
            "nl": "surf-omstandigheden",
            "ar": "surf-conditions",
        },
        "name": {
            "en": "Surf Conditions & Spots",
            "fr": "Conditions & Spots de Surf",
            "es": "Condiciones & Spots de Surf",
            "it": "Condizioni & Spot di Surf",
            "de": "Surf-Bedingungen & Spots",
            "nl": "Surfomstandigheden & Spots",
            "ar": "ظروف الأمواج والمواقع",
        },
        "desc": {
            "en": "Everything about Ngor Island's waves, the best time to surf Senegal, surf season guides and detailed breakdowns of Ngor Right and Left.",
            "fr": "Tout sur les vagues de l'île de Ngor, la meilleure saison pour surfer au Sénégal et les guides détaillés de Ngor Right et Left.",
            "es": "Todo sobre las olas de la isla de Ngor, la mejor temporada para surfear en Senegal y guías detalladas de Ngor Right y Left.",
            "it": "Tutto sulle onde dell'isola di Ngor, il periodo migliore per fare surf in Senegal e guide dettagliate su Ngor Right e Left.",
            "de": "Alles über die Wellen der Insel Ngor, die beste Surfsaison in Senegal und detaillierte Guides zu Ngor Right und Left.",
            "nl": "Alles over de golven van Ngor Island, de beste tijd om te surfen in Senegal, gidsen per seizoen en gedetailleerde overzichten van Ngor Right en Left.",
            "ar": "كل شيء عن أمواج جزيرة نغور، أفضل وقت لركوب الأمواج في السنغال، أدلة موسم الأمواج والتحليل التفصيلي لـ Ngor Right وLeft.",
        },'''
bp = bp.replace(blog_cats_de_surf, blog_cats_new_surf)

# 1h. footer dicts – add nl and ar
# ABOUT dict
bp = bp.replace(
    '"de":"Premium Surfcamp auf Ngor Island, Dakar, Senegal. Alle Level. Lizenziert."}',
    '"de":"Premium Surfcamp auf Ngor Island, Dakar, Senegal. Alle Level. Lizenziert.","nl":"Premium surfkamp op Ngor Island, Dakar, Senegal. Alle niveaus. Erkend door de Senegalese Surfbond.","ar":"مخيم ركوب أمواج متميز في جزيرة نغور، داكار، السنغال. جميع المستويات. مرخص من الاتحاد السنغالي للأمواج."}'
)

# COPY dict
bp = bp.replace(
    '"de":"© 2025 Ngor Surfcamp Teranga. Alle Rechte vorbehalten."}',
    '"de":"© 2025 Ngor Surfcamp Teranga. Alle Rechte vorbehalten.","nl":"© 2025 Ngor Surfcamp Teranga. Alle rechten voorbehouden.","ar":"© 2025 Ngor Surfcamp Teranga. جميع الحقوق محفوظة."}'
)

# PP_LBL dict
bp = bp.replace(
    '"de":"Datenschutzrichtlinie"}',
    '"de":"Datenschutzrichtlinie","nl":"Privacybeleid","ar":"سياسة الخصوصية"}'
)

# EXP dict (Explore)
bp = bp.replace(
    '"de":"Erkunden"}',
    '"de":"Erkunden","nl":"Verkennen","ar":"استكشاف"}'
)

# CON dict (Contact)
bp = bp.replace(
    '"de":"Kontakt"}',
    '"de":"Kontakt","nl":"Contact","ar":"اتصل بنا"}'
)

# FOL dict (Follow us)
bp = bp.replace(
    '"de":"Folgen"}',
    '"de":"Folgen","nl":"Volgen","ar":"تابعنا"}'
)

# GH_L (Getting here) dict in footer
bp = bp.replace(
    '"de":"Anreise"}',
    '"de":"Anreise","nl":"Hoe kom je er","ar":"كيف تصل"}'
)

# 1i. Add RTL dir attribute to html tag generation
# Find where HTML page starts building and add dir="rtl" for ar
# Look for the html tag builder
bp = bp.replace(
    'def head_html(lang, title, meta_description, canonical, hreflangs, og_image=None, og_type="website"):',
    'def head_html(lang, title, meta_description, canonical, hreflangs, og_image=None, og_type="website", is_rtl=False):'
)

# Find the html opening tag with lang attribute
# Pattern: <html lang="...">
bp = re.sub(
    r'(<html lang="{?LANG_LOCALE\[lang\]}?">)',
    '<html lang="{LANG_LOCALE[lang]}" dir=\'{"rtl" if lang=="ar" else "ltr"}\'>',
    bp
)

# 1j. HOME_PROOF_L10N – add nl and ar
# Find the de entry and add nl + ar
home_proof_de = '''"de": {
        "aria": "Camp-Highlights",
        "eyebrow": "Das Wesentliche",
        "f1_n": "2×",
        "f1_t": "Surfsessions täglich",
        "f1_d": "Morgens und nachmittags — Spots je nach Vorhersage gewählt",
        "f2_n": "1964",
        "f2_t": "Endless Summer",
        "f2_d": "Der Film, der Ngor bekannt machte",
        "f3_n": "Alle",
        "f3_t": "Level",
        "f3_d": "Anfänger bis Fortgeschrittene — Abu, bester Surf-Guide in Dakar",
    },
}'''
home_proof_new = '''"de": {
        "aria": "Camp-Highlights",
        "eyebrow": "Das Wesentliche",
        "f1_n": "2×",
        "f1_t": "Surfsessions täglich",
        "f1_d": "Morgens und nachmittags — Spots je nach Vorhersage gewählt",
        "f2_n": "1964",
        "f2_t": "Endless Summer",
        "f2_d": "Der Film, der Ngor bekannt machte",
        "f3_n": "Alle",
        "f3_t": "Level",
        "f3_d": "Anfänger bis Fortgeschrittene — Abu, bester Surf-Guide in Dakar",
    },
    "nl": {
        "aria": "Camphoogtepunten",
        "eyebrow": "De essentie",
        "f1_n": "2×",
        "f1_t": "dagelijkse surfsessies",
        "f1_d": "Ochtend & middag — spots gekozen op basis van de voorspelling",
        "f2_n": "1964",
        "f2_t": "Endless Summer",
        "f2_d": "De film die Ngor op de kaart zette",
        "f3_n": "Alle",
        "f3_t": "niveaus",
        "f3_d": "Beginner tot gevorderd — Abu, beste surfgids van Dakar",
    },
    "ar": {
        "aria": "أبرز مزايا المخيم",
        "eyebrow": "الأساسيات",
        "f1_n": "2×",
        "f1_t": "حصص ركوب أمواج يومية",
        "f1_d": "صباحاً ومساءً — المواقع تُختار حسب التوقعات",
        "f2_n": "1964",
        "f2_t": "Endless Summer",
        "f2_d": "الفيلم الذي وضع نغور على الخريطة",
        "f3_n": "جميع",
        "f3_t": "المستويات",
        "f3_d": "من المبتدئين إلى المحترفين — أبو، أفضل مرشد أمواج في داكار",
    },
}'''
if home_proof_de in bp:
    bp = bp.replace(home_proof_de, home_proof_new)
else:
    print("⚠️  HOME_PROOF_L10N de block not found exactly — will need manual check")

# 1k. HOME_GALLERY_L10N – add nl and ar
home_gallery_de = '''"de": {"lbl":"Galerie","h2":"Inselleben in Bildern","cta":"Alle Fotos ansehen"},
}'''
home_gallery_new = '''"de": {"lbl":"Galerie","h2":"Inselleben in Bildern","cta":"Alle Fotos ansehen"},
    "nl": {"lbl":"Galerij","h2":"Eilandleven in foto's","cta":"Bekijk alle foto's"},
    "ar": {"lbl":"معرض الصور","h2":"حياة الجزيرة بالصور","cta":"عرض جميع الصور"},
}'''
if home_gallery_de in bp:
    bp = bp.replace(home_gallery_de, home_gallery_new)
else:
    print("⚠️  HOME_GALLERY_L10N de block not found exactly")

# 1l. BOOKING_SOCIAL_L10N – add nl and ar
booking_social_de = '''"de": {"score":"4.2","count":"64 Google-Bewertungen","maps":"Auf Google Maps ansehen",
           "leave":"Bewertung abgeben","rv_eyebrow":"Soziale Beweise",
           "rv_h":"Was Gäste sagen","rc_tip":"Zum Weiterlesen klicken"},
}'''
booking_social_new = '''"de": {"score":"4.2","count":"64 Google-Bewertungen","maps":"Auf Google Maps ansehen",
           "leave":"Bewertung abgeben","rv_eyebrow":"Soziale Beweise",
           "rv_h":"Was Gäste sagen","rc_tip":"Zum Weiterlesen klicken"},
    "nl": {"score":"4.2","count":"64 Google-recensies","maps":"Bekijk op Google Maps",
           "leave":"Schrijf een recensie","rv_eyebrow":"Beoordelingen",
           "rv_h":"Wat gasten zeggen","rc_tip":"Klik om meer te lezen"},
    "ar": {"score":"4.2","count":"64 تقييم على جوجل","maps":"عرض على خرائط جوجل",
           "leave":"اترك تقييماً","rv_eyebrow":"آراء الضيوف",
           "rv_h":"ماذا يقول الضيوف","rc_tip":"انقر لقراءة المزيد"},
}'''
if booking_social_de in bp:
    bp = bp.replace(booking_social_de, booking_social_new)
else:
    print("⚠️  BOOKING_SOCIAL_L10N de block not found exactly")

# 1m. GALLERY_PAGE_COPY – add nl and ar
gallery_de = '''"de": {
        "title":"Surf Camp Senegal Galerie | Ngor Island Fotos",
        "meta":"Entdecke Ngor Surfcamp Teranga durch Fotos: Surfsessions, Inselleben, Zimmer, Essen und Sonnenuntergänge auf Ngor Island, Dakar.",
        "h1":"Unsere Galerie",
        "intro":"Ein Einblick in das Leben im Ngor Surfcamp Teranga — Wellen, Lächeln, Sonnenuntergänge und Surfen.",
        "lb_close":"Galerie schließen",
        "lb_prev":"Vorheriges Foto",
        "lb_next":"Nächstes Foto",
        "lb_counter":"von",
    },
}'''
gallery_new = '''"de": {
        "title":"Surf Camp Senegal Galerie | Ngor Island Fotos",
        "meta":"Entdecke Ngor Surfcamp Teranga durch Fotos: Surfsessions, Inselleben, Zimmer, Essen und Sonnenuntergänge auf Ngor Island, Dakar.",
        "h1":"Unsere Galerie",
        "intro":"Ein Einblick in das Leben im Ngor Surfcamp Teranga — Wellen, Lächeln, Sonnenuntergänge und Surfen.",
        "lb_close":"Galerie schließen",
        "lb_prev":"Vorheriges Foto",
        "lb_next":"Nächstes Foto",
        "lb_counter":"von",
    },
    "nl": {
        "title":"Surf Camp Senegal Galerij | Foto's van Ngor Island",
        "meta":"Ontdek Ngor Surfcamp Teranga via foto's: surfsessies, eilandleven, kamers, eten en zonsondergangen op Ngor Island, Dakar.",
        "h1":"Onze Galerij",
        "intro":"Een kijkje in het leven bij Ngor Surfcamp Teranga — golven, lachende gezichten, zonsondergangen en surfen.",
        "lb_close":"Galerij sluiten",
        "lb_prev":"Vorige foto",
        "lb_next":"Volgende foto",
        "lb_counter":"van",
    },
    "ar": {
        "title":"معرض صور مخيم الأمواج في السنغال | صور جزيرة نغور",
        "meta":"اكتشف Ngor Surfcamp Teranga من خلال الصور: حصص ركوب الأمواج، الحياة على الجزيرة، الغرف، الطعام وغروب الشمس في جزيرة نغور، داكار.",
        "h1":"معرض صورنا",
        "intro":"لمحة عن الحياة في Ngor Surfcamp Teranga — أمواج، ابتسامات، غروب الشمس وركوب الأمواج.",
        "lb_close":"إغلاق المعرض",
        "lb_prev":"الصورة السابقة",
        "lb_next":"الصورة التالية",
        "lb_counter":"من",
    },
}'''
if gallery_de in bp:
    bp = bp.replace(gallery_de, gallery_new)
else:
    print("⚠️  GALLERY_PAGE_COPY de block not found exactly")

# 1n. ISLAND_GUIDE_UI – add nl and ar
island_ui_de = '''"de": {
        "eyebrow": "Insel-Guide",
        "back": "← Zurück zur Insel",
        "related": "Mehr Insel-Guides",
        "hub_eyebrow": "Die Insel erkunden",
        "hub_h2": "Insel-Guides",
        "hub_sub": "Alles, was du über Ngor Island wissen musst",
    },
}'''
island_ui_new = '''"de": {
        "eyebrow": "Insel-Guide",
        "back": "← Zurück zur Insel",
        "related": "Mehr Insel-Guides",
        "hub_eyebrow": "Die Insel erkunden",
        "hub_h2": "Insel-Guides",
        "hub_sub": "Alles, was du über Ngor Island wissen musst",
    },
    "nl": {
        "eyebrow": "Eilandgids",
        "back": "← Terug naar het eiland",
        "related": "Meer eilandgidsen",
        "hub_eyebrow": "Verken het eiland",
        "hub_h2": "Eilandgidsen",
        "hub_sub": "Alles wat je moet weten over Ngor Island",
    },
    "ar": {
        "eyebrow": "دليل الجزيرة",
        "back": "← العودة إلى الجزيرة",
        "related": "المزيد من أدلة الجزيرة",
        "hub_eyebrow": "استكشاف الجزيرة",
        "hub_h2": "أدلة الجزيرة",
        "hub_sub": "كل ما تحتاج معرفته عن جزيرة نغور",
    },
}'''
if island_ui_de in bp:
    bp = bp.replace(island_ui_de, island_ui_new)
else:
    print("⚠️  ISLAND_GUIDE_UI de block not found exactly")

# 1o. ISLAND_HUB_GUIDES_SECTION – add nl and ar
island_hub_de = '''"de": {
        "eyebrow": "Alle Guides",
        "h2": "Ngor Island erkunden",
        "sub": "Praktische Guides und lokale Einblicke für deinen Surfaufenthalt",
    },
}'''
island_hub_new = '''"de": {
        "eyebrow": "Alle Guides",
        "h2": "Ngor Island erkunden",
        "sub": "Praktische Guides und lokale Einblicke für deinen Surfaufenthalt",
    },
    "nl": {
        "eyebrow": "Alle gidsen",
        "h2": "Ngor Island verkennen",
        "sub": "Praktische gidsen en lokale inzichten voor je surfverblijf",
    },
    "ar": {
        "eyebrow": "جميع الأدلة",
        "h2": "استكشاف جزيرة نغور",
        "sub": "أدلة عملية ومعرفة محلية لإقامتك في ركوب الأمواج",
    },
}'''
if island_hub_de in bp:
    bp = bp.replace(island_hub_de, island_hub_new)
else:
    print("⚠️  ISLAND_HUB_GUIDES_SECTION de block not found exactly")

# 1p. SURF_PAGE_COPY – add nl and ar
# This is complex; we'll add after the "de" block
# Find the de block ending pattern in SURF_PAGE_COPY
surf_de_end = '''"de": {
        "title": "Surfen auf Ngor | Ngor Surfcamp Teranga",'''

# We need to find the complete de block and add after it
# Instead of trying exact match, let's add nl and ar before the closing of the dict
# by finding a specific unique pattern at the end of the de entry in SURF_PAGE_COPY

# Find SURF_PAGE_COPY in the file  
idx = bp.find('"SURF_PAGE_COPY"') if '"SURF_PAGE_COPY"' in bp else bp.find('SURF_PAGE_COPY = {')
if idx == -1:
    print("⚠️  SURF_PAGE_COPY not found in build.py")
else:
    print(f"✓ SURF_PAGE_COPY found at index {idx}")

# 1q. BOOKING_REVIEWS – add nl and ar
# Find and add after de reviews
booking_rev_de_end = '''"de": ['''  # use a different pattern to find
# We'll skip this for now — nl/ar reviews will be added as English fallback

# 1r. Update GETTING_HERE_FLAG_HREF to include nl and ar
# This dict maps lang → URL for "getting here" links
gh_de = '"de":"https://ngor-surfcamp-demo.pages.dev/de/insel/"}'
gh_new = '"de":"https://ngor-surfcamp-demo.pages.dev/de/insel/","nl":"https://ngor-surfcamp-demo.pages.dev/nl/eiland/","ar":"https://ngor-surfcamp-demo.pages.dev/ar/ngor-island/"}'
if gh_de in bp:
    bp = bp.replace(gh_de, gh_new)
else:
    # Try to find and update the dict
    print("⚠️  GETTING_HERE_FLAG_HREF de entry not found exactly")

# 1s. NAV labels used in build_home_page / navigation
# Look for common patterns like nav labels dict
# Search for HOME_PAGE_COPY or similar
nav_de = '"de":"Startseite"'
if '"de":"Startseite"' in bp:
    # Find context
    pass  # will handle in build step

# Save patched build.py
with open(build_path, "w", encoding="utf-8") as f:
    f.write(bp)
print("✅ build.py patched successfully")

# ─────────────────────────────────────────────────────────────────────────────
# 2. PATCH surf_house_page.py
# ─────────────────────────────────────────────────────────────────────────────
sh_path = os.path.join(BASE, "surf_house_page.py")
with open(sh_path, encoding="utf-8") as f:
    shp = f.read()

# Add nl and ar to SURF_HOUSE_PAGE
# Find the de entry and insert nl + ar after it

sh_en = T_PAGES.get("SURF_HOUSE_PAGE", {})
sh_nl = sh_en.get("nl", {})
sh_ar = sh_en.get("ar", {})

def q(s):
    """Escape string for Python."""
    return s.replace("\\", "\\\\").replace('"', '\\"')

def nl_block():
    return f'''    "nl": {{
        "title": "{q(sh_nl.get('title',''))}",
        "meta": "{q(sh_nl.get('meta',''))}",
        "hero_kicker": "{q(sh_nl.get('hero_kicker',''))}",
        "h1": "{q(sh_nl.get('h1',''))}",
        "tagline": "{q(sh_nl.get('tagline',''))}",
        "welcome_lbl": "{q(sh_nl.get('welcome_lbl',''))}",
        "welcome_title": "{q(sh_nl.get('welcome_title',''))}",
        "p1": "{q(sh_nl.get('p1',''))}",
        "p2": "{q(sh_nl.get('p2',''))}",
        "p3": "{q(sh_nl.get('p3',''))}",
        "p4": "{q(sh_nl.get('p4',''))}",
        "quote_h2": "{q(sh_nl.get('quote_h2',''))}",
        "quote_line1": "{q(sh_nl.get('quote_line1',''))}",
        "quote_line2": "{q(sh_nl.get('quote_line2',''))}",
        "acc_h2": "{q(sh_nl.get('acc_h2',''))}",
        "acc_sub": "{q(sh_nl.get('acc_sub',''))}",
        "meals_h2": "{q(sh_nl.get('meals_h2',''))}",
        "meals_p": "{q(sh_nl.get('meals_p',''))}",
        "bento_h2": "{q(sh_nl.get('bento_h2',''))}",
        "bento_c1": "{q(sh_nl.get('bento_c1',''))}",
        "bento_c2": "{q(sh_nl.get('bento_c2',''))}",
        "bento_c3": "{q(sh_nl.get('bento_c3',''))}",
        "bento_c4": "{q(sh_nl.get('bento_c4',''))}",
        "bento_c5": "{q(sh_nl.get('bento_c5',''))}",
        "gal_h2": "{q(sh_nl.get('gal_h2',''))}",
        "cta_h2": "{q(sh_nl.get('cta_h2',''))}",
        "cta_p": "{q(sh_nl.get('cta_p',''))}",
        "book": "{q(sh_nl.get('book',''))}",
        "copyright": "{q(sh_nl.get('copyright',''))}",
        "privacy": "{q(sh_nl.get('privacy',''))}",
    }},'''

def ar_block():
    return f'''    "ar": {{
        "title": "{q(sh_ar.get('title',''))}",
        "meta": "{q(sh_ar.get('meta',''))}",
        "hero_kicker": "{q(sh_ar.get('hero_kicker',''))}",
        "h1": "{q(sh_ar.get('h1',''))}",
        "tagline": "{q(sh_ar.get('tagline',''))}",
        "welcome_lbl": "{q(sh_ar.get('welcome_lbl',''))}",
        "welcome_title": "{q(sh_ar.get('welcome_title',''))}",
        "p1": "{q(sh_ar.get('p1',''))}",
        "p2": "{q(sh_ar.get('p2',''))}",
        "p3": "{q(sh_ar.get('p3',''))}",
        "p4": "{q(sh_ar.get('p4',''))}",
        "quote_h2": "{q(sh_ar.get('quote_h2',''))}",
        "quote_line1": "{q(sh_ar.get('quote_line1',''))}",
        "quote_line2": "{q(sh_ar.get('quote_line2',''))}",
        "acc_h2": "{q(sh_ar.get('acc_h2',''))}",
        "acc_sub": "{q(sh_ar.get('acc_sub',''))}",
        "meals_h2": "{q(sh_ar.get('meals_h2',''))}",
        "meals_p": "{q(sh_ar.get('meals_p',''))}",
        "bento_h2": "{q(sh_ar.get('bento_h2',''))}",
        "bento_c1": "{q(sh_ar.get('bento_c1',''))}",
        "bento_c2": "{q(sh_ar.get('bento_c2',''))}",
        "bento_c3": "{q(sh_ar.get('bento_c3',''))}",
        "bento_c4": "{q(sh_ar.get('bento_c4',''))}",
        "bento_c5": "{q(sh_ar.get('bento_c5',''))}",
        "gal_h2": "{q(sh_ar.get('gal_h2',''))}",
        "cta_h2": "{q(sh_ar.get('cta_h2',''))}",
        "cta_p": "{q(sh_ar.get('cta_p',''))}",
        "book": "{q(sh_ar.get('book',''))}",
        "copyright": "{q(sh_ar.get('copyright',''))}",
        "privacy": "{q(sh_ar.get('privacy',''))}",
    }},
}}'''

# Find the last "de" closing in SURF_HOUSE_PAGE and add nl + ar
# Look for the pattern at end of de entry
de_end_pattern = '''    "de": {
        "title": "Ngor Surf House | Surfen auf Ngor Island, Senegal",'''

if de_end_pattern not in shp:
    # Try alternative search
    print("⚠️  surf_house_page.py de entry start not found — checking...")
    idx = shp.find('"de": {')
    if idx != -1:
        print(f"  Found de at index {idx}")
        print(shp[idx:idx+100])
else:
    # Find the end of the de block (last entry before closing })
    de_idx = shp.find(de_end_pattern)
    # Find the closing of the entire dict (the last "}" before SURF_HOUSE_FEATS)
    # Strategy: find "}" + "\n}" pattern after de_idx
    feats_idx = shp.find("SURF_HOUSE_FEATS", de_idx)
    if feats_idx != -1:
        # Find the last "}" before SURF_HOUSE_FEATS
        last_close = shp.rfind("\n}", de_idx, feats_idx)
        if last_close != -1:
            # Insert nl and ar before the closing brace of SURF_HOUSE_PAGE
            new_shp = shp[:last_close] + "\n" + nl_block() + "\n" + ar_block() + shp[last_close+2:]
            with open(sh_path, "w", encoding="utf-8") as f:
                f.write(new_shp)
            print("✅ surf_house_page.py SURF_HOUSE_PAGE patched")
        else:
            print("⚠️  Could not find closing brace for SURF_HOUSE_PAGE")
    else:
        print("⚠️  SURF_HOUSE_FEATS not found after de block")

# Also patch SURF_HOUSE_FEATS
feats_nl = T_PAGES.get("SURF_HOUSE_FEATS", {}).get("nl", {})
feats_ar = T_PAGES.get("SURF_HOUSE_FEATS", {}).get("ar", {})

with open(sh_path, encoding="utf-8") as f:
    shp = f.read()

# Find end of feats de block
feats_de_end = '''    "de": {
        "feat_0_title": "Private & geteilte Zimmer",'''

if feats_de_end not in shp:
    print("⚠️  SURF_HOUSE_FEATS de block start not found")
else:
    de_idx = shp.rfind('"de": {', 0, len(shp))
    # Find closing "}" of entire SURF_HOUSE_FEATS dict
    end_dict = shp.rfind("}")
    # We need to insert before the very last "}"
    if end_dict > de_idx:
        feats_nl_block = f'''    "nl": {{
        "feat_0_title": "{q(feats_nl.get('feat_0_title','Private & gedeelde kamers'))}",
        "feat_0_desc": "{q(feats_nl.get('feat_0_desc',''))}",
        "feat_1_title": "{q(feats_nl.get('feat_1_title','Pool & ontspanningszones'))}",
        "feat_1_desc": "{q(feats_nl.get('feat_1_desc',''))}",
        "feat_2_title": "{q(feats_nl.get('feat_2_title','Maaltijden inbegrepen'))}",
        "feat_2_desc": "{q(feats_nl.get('feat_2_desc',''))}",
        "feat_3_title": "{q(feats_nl.get('feat_3_title','Surftransfers & begeleiding'))}",
        "feat_3_desc": "{q(feats_nl.get('feat_3_desc',''))}",
        "feat_4_title": "{q(feats_nl.get('feat_4_title','Gratis surftheorie'))}",
        "feat_4_desc": "{q(feats_nl.get('feat_4_desc',''))}",
        "feat_5_title": "{q(feats_nl.get('feat_5_title','Gratis wifi & dagelijkse kamerreiniging'))}",
        "feat_5_desc": "{q(feats_nl.get('feat_5_desc',''))}",
    }},'''
        feats_ar_block = f'''    "ar": {{
        "feat_0_title": "{q(feats_ar.get('feat_0_title','غرف خاصة ومشتركة'))}",
        "feat_0_desc": "{q(feats_ar.get('feat_0_desc',''))}",
        "feat_1_title": "{q(feats_ar.get('feat_1_title','منطقة المسبح والاسترخاء'))}",
        "feat_1_desc": "{q(feats_ar.get('feat_1_desc',''))}",
        "feat_2_title": "{q(feats_ar.get('feat_2_title','الوجبات مشمولة'))}",
        "feat_2_desc": "{q(feats_ar.get('feat_2_desc',''))}",
        "feat_3_title": "{q(feats_ar.get('feat_3_title','نقل الأمواج والتوجيه'))}",
        "feat_3_desc": "{q(feats_ar.get('feat_3_desc',''))}",
        "feat_4_title": "{q(feats_ar.get('feat_4_title','نظرية ركوب الأمواج مجانية'))}",
        "feat_4_desc": "{q(feats_ar.get('feat_4_desc',''))}",
        "feat_5_title": "{q(feats_ar.get('feat_5_title','واي فاي مجاني وتنظيف يومي'))}",
        "feat_5_desc": "{q(feats_ar.get('feat_5_desc',''))}",
    }},
}}'''
        new_shp = shp[:end_dict] + feats_nl_block + "\n" + feats_ar_block + shp[end_dict+1:]
        with open(sh_path, "w", encoding="utf-8") as f:
            f.write(new_shp)
        print("✅ surf_house_page.py SURF_HOUSE_FEATS patched")

print("\n✅ All patches applied!")
