#!/usr/bin/env python3
"""Patch 28_fix_blocks.py to add nl and ar language support."""
import re, os

PATH = "/Users/simonazoulay/SurfCampSenegal/_legacy_scripts/28_fix_blocks.py"
with open(PATH, encoding="utf-8") as f:
    bp = f.read()

orig = bp

# 1. LANGS
bp = bp.replace(
    'LANGS       = ["en","fr","es","it","de"]',
    'LANGS       = ["en","fr","es","it","de","nl","ar"]'
)

# 2. LANG_NAMES
bp = bp.replace(
    'LANG_NAMES  = {"en":"English","fr":"Français","es":"Español","it":"Italiano","de":"Deutsch"}',
    'LANG_NAMES  = {"en":"English","fr":"Français","es":"Español","it":"Italiano","de":"Deutsch","nl":"Nederlands","ar":"العربية"}'
)

# 3. LANG_LOCALE
bp = bp.replace(
    'LANG_LOCALE = {"en":"en","fr":"fr-FR","es":"es-ES","it":"it-IT","de":"de-DE"}',
    'LANG_LOCALE = {"en":"en","fr":"fr-FR","es":"es-ES","it":"it-IT","de":"de-DE","nl":"nl-NL","ar":"ar-MA"}'
)

# 4. LANG_PREFIX
bp = bp.replace(
    'LANG_PREFIX = {"en":"","fr":"/fr","es":"/es","it":"/it","de":"/de"}',
    'LANG_PREFIX = {"en":"","fr":"/fr","es":"/es","it":"/it","de":"/de","nl":"/nl","ar":"/ar"}'
)

# 5. Visual block labels
bp = bp.replace(
    '"tip":      {"en":"Pro Tip","fr":"Conseil Pro","es":"Consejo Pro","it":"Consiglio Pro","de":"Profi-Tipp"}',
    '"tip":      {"en":"Pro Tip","fr":"Conseil Pro","es":"Consejo Pro","it":"Consiglio Pro","de":"Profi-Tipp","nl":"Pro Tip","ar":"نصيحة احترافية"}'
)
bp = bp.replace(
    '"fact":     {"en":"Did You Know?","fr":"Le Saviez-Vous ?","es":"¿Sabías Que?","it":"Lo Sapevi?","de":"Wusstest Du?"}',
    '"fact":     {"en":"Did You Know?","fr":"Le Saviez-Vous ?","es":"¿Sabías Que?","it":"Lo Sapevi?","de":"Wusstest Du?","nl":"Wist je dat?","ar":"هل تعلم؟"}'
)
bp = bp.replace(
    '"expert":   {"en":"From the Coaches","fr":"De nos Coachs","es":"De los Coaches","it":"Dai Coach","de":"Von den Coaches"}',
    '"expert":   {"en":"From the Coaches","fr":"De nos Coachs","es":"De los Coaches","it":"Dai Coach","de":"Von den Coaches","nl":"Van de coaches","ar":"من المدربين"}'
)
bp = bp.replace(
    '"checklist":{"en":"Action Checklist","fr":"Liste d\'Actions","es":"Lista de Acciones","it":"Lista d\'Azioni","de":"Aktionsliste"}',
    '"checklist":{"en":"Action Checklist","fr":"Liste d\'Actions","es":"Lista de Acciones","it":"Lista d\'Azioni","de":"Aktionsliste","nl":"Actiechecklist","ar":"قائمة التحقق"}'
)
bp = bp.replace(
    '"summary":  {"en":"Key Takeaways","fr":"Points Clés","es":"Puntos Clave","it":"Punti Chiave","de":"Fazit"}',
    '"summary":  {"en":"Key Takeaways","fr":"Points Clés","es":"Puntos Clave","it":"Punti Chiave","de":"Fazit","nl":"Kernpunten","ar":"النقاط الرئيسية"}'
)
bp = bp.replace(
    '"note":     {"en":"Note","fr":"Note","es":"Nota","it":"Nota","de":"Hinweis"}',
    '"note":     {"en":"Note","fr":"Note","es":"Nota","it":"Nota","de":"Hinweis","nl":"Noot","ar":"ملاحظة"}'
)

# 6. TOC_TITLES
bp = bp.replace(
    'TOC_TITLES = {"en":"Contents","fr":"Sommaire","es":"Contenido","it":"Indice","de":"Inhalt"}',
    'TOC_TITLES = {"en":"Contents","fr":"Sommaire","es":"Contenido","it":"Indice","de":"Inhalt","nl":"Inhoud","ar":"المحتويات"}'
)

# 7. FLAG_SVG - add nl and ar
bp = bp.replace(
    '"de":\'<svg viewBox="0 0 60 40"><rect width="60" height="13" fill="#000"/><rect y="13" width="60" height="14" fill="#DD0000"/><rect y="27" width="60" height="13" fill="#FFCE00"/></svg>\'}',
    '"de":\'<svg viewBox="0 0 60 40"><rect width="60" height="13" fill="#000"/><rect y="13" width="60" height="14" fill="#DD0000"/><rect y="27" width="60" height="13" fill="#FFCE00"/></svg>\',"nl":\'<svg viewBox="0 0 60 40"><rect width="60" height="13" fill="#AE1C28"/><rect y="13" width="60" height="14" fill="#fff"/><rect y="27" width="60" height="13" fill="#21468B"/></svg>\',"ar":\'<svg viewBox="0 0 60 40"><rect width="60" height="14" fill="#006233"/><rect y="14" width="60" height="12" fill="#fff"/><rect y="26" width="60" height="14" fill="#C1272D"/></svg>\'}'
)

# 8. hreflang function (line 571)
bp = bp.replace(
    'for l in ["fr","es","it","de"]]))',
    'for l in ["fr","es","it","de","nl","ar"]]))'
)

# 9. NAV dict
bp = bp.replace(
    '("/booking",{"en":"Book Now","fr":"Réserver","es":"Reservar","it":"Prenota","de":"Buchen"})]',
    '("/booking",{"en":"Book Now","fr":"Réserver","es":"Reservar","it":"Prenota","de":"Buchen","nl":"Boeken","ar":"احجز الآن"})]',
    1  # only first occurrence (NAV)
)
# Also update home entry with nl/ar
bp = bp.replace(
    '("",{"en":"Home","fr":"Accueil","es":"Inicio","it":"Home","de":"Start"})',
    '("",{"en":"Home","fr":"Accueil","es":"Inicio","it":"Home","de":"Start","nl":"Home","ar":"الرئيسية"})'
)
bp = bp.replace(
    '("/surf-house",{"en":"Surf House","fr":"Surf House","es":"Surf House","it":"Surf House","de":"Surf House"})',
    '("/surf-house",{"en":"Surf House","fr":"Surf House","es":"Surf House","it":"Surf House","de":"Surf House","nl":"Surf House","ar":"بيت الأمواج"})',
    1  # first occurrence (NAV)
)
bp = bp.replace(
    '("/island",{"en":"Island","fr":"Île","es":"Isla","it":"Isola","de":"Insel"})',
    '("/island",{"en":"Island","fr":"Île","es":"Isla","it":"Isola","de":"Insel","nl":"Eiland","ar":"الجزيرة"})',
    1
)
bp = bp.replace(
    '("/surfing",{"en":"Surfing","fr":"Surf","es":"Surf","it":"Surf","de":"Surfen"})',
    '("/surfing",{"en":"Surfing","fr":"Surf","es":"Surf","it":"Surf","de":"Surfen","nl":"Surfen","ar":"ركوب الأمواج"})',
    1
)
bp = bp.replace(
    '("/blog",{"en":"Blog","fr":"Blog","es":"Blog","it":"Blog","de":"Blog"})',
    '("/blog",{"en":"Blog","fr":"Blog","es":"Blog","it":"Blog","de":"Blog","nl":"Blog","ar":"المدونة"})',
    1
)
bp = bp.replace(
    '("/gallery",{"en":"Gallery","fr":"Galerie","es":"Galería","it":"Galleria","de":"Galerie"})',
    '("/gallery",{"en":"Gallery","fr":"Galerie","es":"Galería","it":"Galleria","de":"Galerie","nl":"Galerij","ar":"معرض الصور"})',
    1
)

# 10. LINKS dict - similar nav for footer
bp = bp.replace(
    '("/booking",{"en":"Book Now","fr":"Réserver","es":"Reservar","it":"Prenota","de":"Buchen"})]',
    '("/booking",{"en":"Book Now","fr":"Réserver","es":"Reservar","it":"Prenota","de":"Buchen","nl":"Boeken","ar":"احجز الآن"})]'
)
bp = bp.replace(
    '("/faq",{"en":"FAQ","fr":"FAQ","es":"FAQ","it":"FAQ","de":"FAQ"})',
    '("/faq",{"en":"FAQ","fr":"FAQ","es":"FAQ","it":"FAQ","de":"FAQ","nl":"FAQ","ar":"الأسئلة الشائعة"})'
)

# 11. COPY, ABOUT, EXP, PP dicts in footer
bp = bp.replace(
    'COPY={"en":"© 2025 Ngor Surfcamp Teranga.","fr":"© 2025 Ngor Surfcamp Teranga.","es":"© 2025 Ngor Surfcamp Teranga.","it":"© 2025 Ngor Surfcamp Teranga.","de":"© 2025 Ngor Surfcamp Teranga."}',
    'COPY={"en":"© 2025 Ngor Surfcamp Teranga.","fr":"© 2025 Ngor Surfcamp Teranga.","es":"© 2025 Ngor Surfcamp Teranga.","it":"© 2025 Ngor Surfcamp Teranga.","de":"© 2025 Ngor Surfcamp Teranga.","nl":"© 2025 Ngor Surfcamp Teranga.","ar":"© 2025 Ngor Surfcamp Teranga."}'
)
bp = bp.replace(
    'ABOUT={"en":"Premium surf camp on Ngor Island, Dakar, Senegal.","fr":"Surf camp premium sur l\'île de Ngor, Dakar, Sénégal.","es":"Surf camp premium en la isla de Ngor, Dakar, Senegal.","it":"Surf camp premium sull\'isola di Ngor, Dakar, Senegal.","de":"Premium Surfcamp auf Ngor Island, Dakar, Senegal."}',
    'ABOUT={"en":"Premium surf camp on Ngor Island, Dakar, Senegal.","fr":"Surf camp premium sur l\'île de Ngor, Dakar, Sénégal.","es":"Surf camp premium en la isla de Ngor, Dakar, Senegal.","it":"Surf camp premium sull\'isola di Ngor, Dakar, Senegal.","de":"Premium Surfcamp auf Ngor Island, Dakar, Senegal.","nl":"Premium surfkamp op Ngor Island, Dakar, Senegal.","ar":"مخيم أمواج متميز في جزيرة نغور، داكار، السنغال."}'
)
bp = bp.replace(
    'EXP={"en":"Explore","fr":"Explorer","es":"Explorar","it":"Esplora","de":"Erkunden"}',
    'EXP={"en":"Explore","fr":"Explorer","es":"Explorar","it":"Esplora","de":"Erkunden","nl":"Verkennen","ar":"استكشاف"}'
)
bp = bp.replace(
    'PP_SLUG={"en":"privacy-policy","fr":"politique-de-confidentialite","es":"politica-de-privacidad","it":"informativa-sulla-privacy","de":"datenschutzrichtlinie"}',
    'PP_SLUG={"en":"privacy-policy","fr":"politique-de-confidentialite","es":"politica-de-privacidad","it":"informativa-sulla-privacy","de":"datenschutzrichtlinie","nl":"privacybeleid","ar":"privacy-policy"}'
)
bp = bp.replace(
    'PP_LBL={"en":"Privacy Policy","fr":"Politique de confidentialité","es":"Política de privacidad","it":"Informativa sulla privacy","de":"Datenschutzrichtlinie"}',
    'PP_LBL={"en":"Privacy Policy","fr":"Politique de confidentialité","es":"Política de privacidad","it":"Informativa sulla privacy","de":"Datenschutzrichtlinie","nl":"Privacybeleid","ar":"سياسة الخصوصية"}'
)

# 12. LABEL (who is this for) and BY (written by)
bp = bp.replace(
    'LABEL = {"en":"Who is this for?","fr":"Pour qui est cet article ?","es":"¿Para quién?","it":"Per chi è?","de":"Für wen?"}',
    'LABEL = {"en":"Who is this for?","fr":"Pour qui est cet article ?","es":"¿Para quién?","it":"Per chi è?","de":"Für wen?","nl":"Voor wie is dit?","ar":"لمن هذا المقال؟"}'
)
bp = bp.replace(
    'BY = {"en":"Written by","fr":"Écrit par","es":"Escrito por","it":"Scritto da","de":"Geschrieben von"}',
    'BY = {"en":"Written by","fr":"Écrit par","es":"Escrito por","it":"Scritto da","de":"Geschrieben von","nl":"Geschreven door","ar":"كتبه"}'
)

# 13. Category slugs (inside the blog cats dict)
bp = bp.replace(
    '"slug":  {"en":"island-life","fr":"vie-ile","es":"vida-isla","it":"vita-isola","de":"insel-leben"}',
    '"slug":  {"en":"island-life","fr":"vie-ile","es":"vida-isla","it":"vita-isola","de":"insel-leben","nl":"eiland-leven","ar":"island-life"}'
)
bp = bp.replace(
    '"slug":  {"en":"surf-conditions","fr":"conditions-surf","es":"condiciones-surf","it":"condizioni-surf","de":"surf-bedingungen"}',
    '"slug":  {"en":"surf-conditions","fr":"conditions-surf","es":"condiciones-surf","it":"condizioni-surf","de":"surf-bedingungen","nl":"surf-omstandigheden","ar":"surf-conditions"}'
)
bp = bp.replace(
    '"slug":  {"en":"coaching-progression","fr":"coaching-progression","es":"coaching-progresion","it":"coaching-progressione","de":"coaching-fortschritt"}',
    '"slug":  {"en":"coaching-progression","fr":"coaching-progression","es":"coaching-progresion","it":"coaching-progressione","de":"coaching-fortschritt","nl":"coaching-progressie","ar":"coaching-progression"}'
)

# 14. CAT_SLUG_WORD and BLOG_SLUG_LG
bp = bp.replace(
    'CAT_SLUG_WORD = {"en":"category","fr":"categorie","es":"categoria","it":"categoria","de":"kategorie"}',
    'CAT_SLUG_WORD = {"en":"category","fr":"categorie","es":"categoria","it":"categoria","de":"kategorie","nl":"categorie","ar":"categorie"}'
)
bp = bp.replace(
    'BLOG_SLUG_LG  = {"en":"blog","fr":"blog","es":"blog","it":"blog","de":"blog"}',
    'BLOG_SLUG_LG  = {"en":"blog","fr":"blog","es":"blog","it":"blog","de":"blog","nl":"blog","ar":"blog"}'
)

# 15. BACK, BOOK dicts
bp = bp.replace(
    'BACK={"en":"Back to Blog","fr":"Retour au Blog","es":"Volver al Blog","it":"Torna al Blog","de":"Zurück zum Blog"}',
    'BACK={"en":"Back to Blog","fr":"Retour au Blog","es":"Volver al Blog","it":"Torna al Blog","de":"Zurück zum Blog","nl":"Terug naar Blog","ar":"العودة إلى المدونة"}'
)
bp = bp.replace(
    'BOOK={"en":"Book Your Stay","fr":"Réserver","es":"Reservar","it":"Prenota","de":"Buchen"}',
    'BOOK={"en":"Book Your Stay","fr":"Réserver","es":"Reservar","it":"Prenota","de":"Buchen","nl":"Boek je verblijf","ar":"احجز إقامتك"}'
)

# 16. LANG_L (read in)
bp = bp.replace(
    'LANG_L={"en":"Read in:","fr":"Lire en :","es":"Leer en:","it":"Leggi in:","de":"Lesen auf:"}',
    'LANG_L={"en":"Read in:","fr":"Lire en :","es":"Leer en:","it":"Leggi in:","de":"Lesen auf:","nl":"Lees in:","ar":"اقرأ بـ:"}'
)

# 17. Hreflang helper for blog
bp = bp.replace(
    'for l in ["fr","es","it","de"]])',
    'for l in ["fr","es","it","de","nl","ar"]])'
)

# 18. Fix V2_DIR to include all langs
bp = bp.replace(
    'V2_DIR   = f"{CONTENT}/articles_v2/en"',
    'V2_DIR   = f"{CONTENT}/articles_v2/en"\nV2_LANGS  = ["en","fr","es","it","de","nl","ar"]'
)

# Check for html tag with lang attribute — add RTL for ar
# The article page typically builds with lang as a variable
# Add dir=rtl support for article pages
bp = bp.replace(
    '<html lang="{lang}">',
    '<html lang="{LANG_LOCALE.get(lang,lang)}" dir=\'{"rtl" if lang=="ar" else "ltr"}\'>'
)

if bp == orig:
    print("⚠️  No changes were made! Check string matching.")
else:
    with open(PATH, "w", encoding="utf-8") as f:
        f.write(bp)
    print(f"✅ 28_fix_blocks.py patched ({len(bp)-len(orig):+d} chars)")

# Check syntax
import ast
try:
    ast.parse(bp)
    print("✅ 28_fix_blocks.py parses OK")
except SyntaxError as e:
    print(f"❌ SyntaxError: line {e.lineno}: {e.msg}")
    lines = bp.split('\n')
    for i in range(max(0,e.lineno-3), min(len(lines), e.lineno+3)):
        print(f"{i+1}: {lines[i]}")
