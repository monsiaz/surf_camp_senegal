#!/usr/bin/env python3
"""Patch 22_build_surfing_faq.py to add nl and ar."""
import re, ast

PATH = "/Users/simonazoulay/SurfCampSenegal/_legacy_scripts/22_build_surfing_faq.py"
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

# Find and update all inline dicts (SLUG, NAV labels, footer, etc.)
# NAV labels
bp = bp.replace(
    '("",{"en":"Home","fr":"Accueil","es":"Inicio","it":"Home","de":"Start"})',
    '("",{"en":"Home","fr":"Accueil","es":"Inicio","it":"Home","de":"Start","nl":"Home","ar":"الرئيسية"})'
)
bp = bp.replace(
    '("/surf-house",{"en":"Surf House","fr":"Surf House","es":"Surf House","it":"Surf House","de":"Surf House"})',
    '("/surf-house",{"en":"Surf House","fr":"Surf House","es":"Surf House","it":"Surf House","de":"Surf House","nl":"Surf House","ar":"بيت الأمواج"})'
)
bp = bp.replace(
    '("/island",{"en":"Island","fr":"Île","es":"Isla","it":"Isola","de":"Insel"})',
    '("/island",{"en":"Island","fr":"Île","es":"Isla","it":"Isola","de":"Insel","nl":"Eiland","ar":"الجزيرة"})'
)
bp = bp.replace(
    '("/surfing",{"en":"Surfing","fr":"Surf","es":"Surf","it":"Surf","de":"Surfen"})',
    '("/surfing",{"en":"Surfing","fr":"Surf","es":"Surf","it":"Surf","de":"Surfen","nl":"Surfen","ar":"ركوب الأمواج"})'
)
bp = bp.replace(
    '("/blog",{"en":"Blog","fr":"Blog","es":"Blog","it":"Blog","de":"Blog"})',
    '("/blog",{"en":"Blog","fr":"Blog","es":"Blog","it":"Blog","de":"Blog","nl":"Blog","ar":"المدونة"})'
)
bp = bp.replace(
    '("/gallery",{"en":"Gallery","fr":"Galerie","es":"Galería","it":"Galleria","de":"Galerie"})',
    '("/gallery",{"en":"Gallery","fr":"Galerie","es":"Galería","it":"Galleria","de":"Galerie","nl":"Galerij","ar":"معرض الصور"})'
)
bp = bp.replace(
    '("/booking",{"en":"Book Now","fr":"Réserver","es":"Reservar","it":"Prenota","de":"Buchen"})',
    '("/booking",{"en":"Book Now","fr":"Réserver","es":"Reservar","it":"Prenota","de":"Buchen","nl":"Boeken","ar":"احجز الآن"})'
)

# Footer dicts
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

# FLAG_SVG if present in this file
bp = bp.replace(
    '"de":\'<svg viewBox="0 0 60 40"><rect width="60" height="13" fill="#000"/><rect y="13" width="60" height="14" fill="#DD0000"/><rect y="27" width="60" height="13" fill="#FFCE00"/></svg>\'}',
    '"de":\'<svg viewBox="0 0 60 40"><rect width="60" height="13" fill="#000"/><rect y="13" width="60" height="14" fill="#DD0000"/><rect y="27" width="60" height="13" fill="#FFCE00"/></svg>\',"nl":\'<svg viewBox="0 0 60 40"><rect width="60" height="13" fill="#AE1C28"/><rect y="13" width="60" height="14" fill="#fff"/><rect y="27" width="60" height="13" fill="#21468B"/></svg>\',"ar":\'<svg viewBox="0 0 60 40"><rect width="60" height="14" fill="#006233"/><rect y="14" width="60" height="12" fill="#fff"/><rect y="26" width="60" height="14" fill="#C1272D"/></svg>\'}'
)

# hreflang for loops
bp = bp.replace(
    'for l in ["fr","es","it","de"]])',
    'for l in ["fr","es","it","de","nl","ar"]])'
)
bp = bp.replace(
    'for l in ["fr","es","it","de"]]))',
    'for l in ["fr","es","it","de","nl","ar"]]))'
)

# CTA strings if present
bp = bp.replace(
    '{"en":"Book your stay","fr":"Réserver","es":"Reservar","it":"Prenota","de":"Buchen"}',
    '{"en":"Book your stay","fr":"Réserver","es":"Reservar","it":"Prenota","de":"Buchen","nl":"Boek je verblijf","ar":"احجز إقامتك"}'
)
bp = bp.replace(
    '{"en":"WhatsApp us","fr":"WhatsApp","es":"WhatsApp","it":"WhatsApp","de":"WhatsApp"}',
    '{"en":"WhatsApp us","fr":"WhatsApp","es":"WhatsApp","it":"WhatsApp","de":"WhatsApp","nl":"WhatsApp","ar":"واتساب"}'
)

print(f"Changed: {len(bp) - len(orig):+d} chars")

# Save
with open(PATH, "w", encoding="utf-8") as f:
    f.write(bp)

# Syntax check
try:
    ast.parse(bp)
    print("✅ 22_build_surfing_faq.py parses OK")
except SyntaxError as e:
    print(f"❌ SyntaxError: line {e.lineno}: {e.msg}")
