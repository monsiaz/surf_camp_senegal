"""
Build "How to Get to Ngor Island" page for all 5 languages.
Features:
- Leaflet.js interactive map (dark tiles, custom pins, DA-matched)
- Country selector (FR / UK / USA / Canada / Australia)
- Real flight info per country + practical tips
- Step-by-step arrival guide
- Homepage teaser block
"""
import importlib.util
import os, re

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_site_assets_spec = importlib.util.spec_from_file_location(
    "site_assets", os.path.join(_BASE_DIR, "scripts", "site_assets.py")
)
_site_assets_mod = importlib.util.module_from_spec(_site_assets_spec)
_site_assets_spec.loader.exec_module(_site_assets_mod)
ASSET_VERSION = _site_assets_mod.ASSET_VERSION
ASSET_CSS_MAIN = _site_assets_mod.ASSET_CSS_MAIN
ASSET_JS_MAIN = _site_assets_mod.ASSET_JS_MAIN

DEMO     = "/Users/simonazoulay/SurfCampSenegal/cloudflare-demo"
SITE_URL = (os.environ.get("PUBLIC_SITE_URL") or "https://surf-camp-senegal.vercel.app").strip().rstrip("/")
LANGS    = ["en","fr","es","it","de"]
LANG_PFX = {"en":"","fr":"/fr","es":"/es","it":"/it","de":"/de"}
LANG_LOCALE = {"en":"en","fr":"fr-FR","es":"es-ES","it":"it-IT","de":"de-DE"}
LANG_NAMES  = {"en":"English","fr":"Français","es":"Español","it":"Italiano","de":"Deutsch"}

_WIX = "/assets/images/wix"
LOGO = f"{_WIX}/c2467f_a31779010ce34c4c8c61cc5868d81f31.webp"

SLUG_GET_HERE = {"en":"getting-here","fr":"comment-venir","es":"como-llegar","it":"come-arrivare","de":"anreise"}

SLUG = {
    "en": {"surf-house":"surf-house","island":"island","surfing":"surfing","booking":"booking","gallery":"gallery","faq":"faq","blog":"blog"},
    "fr": {"surf-house":"surf-house","island":"ile","surfing":"surf","booking":"reservation","gallery":"galerie","faq":"faq","blog":"blog"},
    "es": {"surf-house":"surf-house","island":"isla","surfing":"surf","booking":"reservar","gallery":"galeria","faq":"faq","blog":"blog"},
    "it": {"surf-house":"surf-house","island":"isola","surfing":"surf","booking":"prenota","gallery":"galleria","faq":"faq","blog":"blog"},
    "de": {"surf-house":"surf-house","island":"insel","surfing":"surfen","booking":"buchen","gallery":"galerie","faq":"faq","blog":"blog"},
}

WA_ICO = '<svg viewBox="0 0 24 24" fill="currentColor" width="18" height="18"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>'
CHEV = '<svg viewBox="0 0 16 16" fill="none" width="14" height="14"><path d="M4 6l4 4 4-4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
MENU = '<svg viewBox="0 0 24 24" fill="none" width="22" height="22"><path d="M3 7h18M3 12h18M3 17h12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>'

FLAG_SVG = {"en":'<svg viewBox="0 0 60 40"><rect width="60" height="40" fill="#012169"/><path d="M0,0 L60,40 M60,0 L0,40" stroke="#fff" stroke-width="8"/><path d="M0,0 L60,40 M60,0 L0,40" stroke="#C8102E" stroke-width="5"/><path d="M30,0 V40 M0,20 H60" stroke="#fff" stroke-width="12"/><path d="M30,0 V40 M0,20 H60" stroke="#C8102E" stroke-width="8"/></svg>',"fr":'<svg viewBox="0 0 60 40"><rect width="20" height="40" fill="#002395"/><rect x="20" width="20" height="40" fill="#fff"/><rect x="40" width="20" height="40" fill="#ED2939"/></svg>',"es":'<svg viewBox="0 0 60 40"><rect width="60" height="40" fill="#c60b1e"/><rect y="10" width="60" height="20" fill="#ffc400"/></svg>',"it":'<svg viewBox="0 0 60 40"><rect width="20" height="40" fill="#009246"/><rect x="20" width="20" height="40" fill="#fff"/><rect x="40" width="20" height="40" fill="#CE2B37"/></svg>',"de":'<svg viewBox="0 0 60 40"><rect width="60" height="13" fill="#000"/><rect y="13" width="60" height="14" fill="#DD0000"/><rect y="27" width="60" height="13" fill="#FFCE00"/></svg>'}
FLAGS_EXTRA = {
    "uk":'<svg viewBox="0 0 60 40"><rect width="60" height="40" fill="#012169"/><path d="M0,0 L60,40 M60,0 L0,40" stroke="#fff" stroke-width="8"/><path d="M0,0 L60,40 M60,0 L0,40" stroke="#C8102E" stroke-width="5"/><path d="M30,0 V40 M0,20 H60" stroke="#fff" stroke-width="12"/><path d="M30,0 V40 M0,20 H60" stroke="#C8102E" stroke-width="8"/></svg>',
    "us":'<svg viewBox="0 0 60 40"><rect width="60" height="40" fill="#B22234"/><rect y="3" width="60" height="3" fill="#fff"/><rect y="9" width="60" height="3" fill="#fff"/><rect y="15" width="60" height="3" fill="#fff"/><rect y="21" width="60" height="3" fill="#fff"/><rect y="27" width="60" height="3" fill="#fff"/><rect y="33" width="60" height="3" fill="#fff"/><rect width="24" height="21" fill="#3C3B6E"/></svg>',
    "ca":'<svg viewBox="0 0 60 40"><rect width="15" height="40" fill="#FF0000"/><rect x="15" width="30" height="40" fill="#fff"/><rect x="45" width="15" height="40" fill="#FF0000"/><text x="30" y="28" text-anchor="middle" font-size="20" fill="#FF0000">🍁</text></svg>',
    "au":'<svg viewBox="0 0 60 40"><rect width="60" height="40" fill="#00008B"/><path d="M0,0 L30,20 M30,0 L0,20" stroke="#fff" stroke-width="4"/><path d="M0,0 L30,20 M30,0 L0,20" stroke="#C8102E" stroke-width="2.5"/><path d="M15,0 V20 M0,10 H30" stroke="#fff" stroke-width="6"/><path d="M15,0 V20 M0,10 H30" stroke="#C8102E" stroke-width="4"/></svg>',
}

def flag(lang, size=22):
    h = round(size*0.667)
    svg = FLAG_SVG.get(lang, FLAG_SVG["en"])
    return f'<span style="width:{size}px;height:{h}px;display:inline-flex;border-radius:3px;overflow:hidden;flex-shrink:0;box-shadow:0 1px 3px rgba(0,0,0,0.22)">{svg}</span>'

def flag_extra(code, size=22):
    h = round(size*0.667)
    svg = FLAGS_EXTRA.get(code, '')
    return f'<span style="width:{size}px;height:{h}px;display:inline-flex;border-radius:3px;overflow:hidden;flex-shrink:0;box-shadow:0 1px 3px rgba(0,0,0,0.22)">{svg}</span>'

# ════════════════════════════════════════════════════════════════
# FLIGHT DATA PER COUNTRY
# ════════════════════════════════════════════════════════════════
FLIGHT_DATA = {
    "fr": {
        "flag": "fr",
        "name_en": "France", "name_fr": "France", "name_es": "Francia", "name_it": "Francia", "name_de": "Frankreich",
        "hub": "Paris CDG / ORY",
        "duration": "~6h",
        "price_range": "€200–600",
        "airlines": ["Air France","Transavia","Air Sénégal","Corsair"],
        "direct": True,
        "tips_en": "The most connected route. Air France and Transavia both fly direct Paris → Dakar from Roissy-CDG and Orly. Book 2–3 months ahead for the best fares. Air Sénégal also offers competitively priced direct services.",
        "tips_fr": "La route la mieux connectée. Air France et Transavia proposent des vols directs Paris → Dakar depuis CDG et Orly. Réservez 2–3 mois à l'avance pour les meilleurs tarifs. Air Sénégal propose aussi des vols directs à prix compétitifs.",
        "tips_es": "La ruta mejor conectada. Air France y Transavia vuelan directo desde París a Dakar. Reserva con 2-3 meses de antelación.",
        "tips_it": "La rotta più connessa. Air France e Transavia volano diretto da Parigi a Dakar. Prenota con 2-3 mesi di anticipo.",
        "tips_de": "Die bestverbundene Route. Air France und Transavia fliegen direkt Paris → Dakar. 2–3 Monate im Voraus buchen für die besten Preise.",
        "search_url": "https://www.google.com/travel/flights/search?q=Paris+to+Dakar+flights",
    },
    "uk": {
        "flag": "uk",
        "name_en": "United Kingdom", "name_fr": "Royaume-Uni", "name_es": "Reino Unido", "name_it": "Regno Unito", "name_de": "Vereinigtes Königreich",
        "hub": "London LHR / LGW / STN",
        "duration": "~8–10h",
        "price_range": "£350–700",
        "airlines": ["Brussels Airlines","Air France","KLM","Iberia","Royal Air Maroc"],
        "direct": False,
        "connection": "Brussels, Paris, Amsterdam or Casablanca",
        "tips_en": "No direct flights from the UK to Dakar. The best options are Brussels Airlines via Brussels (good connections from London Heathrow) or Air France via Paris. Royal Air Maroc via Casablanca is often the most affordable. Total journey time 8–10 hours.",
        "tips_fr": "Pas de vol direct depuis le Royaume-Uni. Meilleures options : Brussels Airlines via Bruxelles ou Air France via Paris. Royal Air Maroc via Casablanca est souvent le plus abordable.",
        "tips_es": "No hay vuelos directos desde el Reino Unido. Las mejores opciones son Brussels Airlines vía Bruselas o Air France vía París.",
        "tips_it": "Nessun volo diretto dal Regno Unito. Le migliori opzioni sono Brussels Airlines via Bruxelles o Air France via Parigi.",
        "tips_de": "Keine Direktflüge aus dem UK. Beste Optionen: Brussels Airlines über Brüssel oder Air France über Paris.",
        "search_url": "https://www.google.com/travel/flights/search?q=London+to+Dakar+flights",
    },
    "us": {
        "flag": "us",
        "name_en": "USA", "name_fr": "États-Unis", "name_es": "EE.UU.", "name_it": "USA", "name_de": "USA",
        "hub": "New York JFK / Washington IAD / Atlanta ATL",
        "duration": "~12–15h",
        "price_range": "$600–1,300",
        "airlines": ["Delta","Air France","Brussels Airlines","Royal Air Maroc","Turkish Airlines"],
        "direct": False,
        "connection": "Paris, Brussels, Casablanca or Istanbul",
        "tips_en": "Most US travelers route through Paris (Air France), Brussels (Brussels Airlines), or Casablanca (Royal Air Maroc). From the US East Coast, budget 12–14 hours total. West Coast travelers add 5–6 hours. Book business class for a more comfortable long-haul journey.",
        "tips_fr": "La plupart des voyageurs américains passent par Paris, Bruxelles ou Casablanca. Depuis la côte Est, comptez 12–14h au total.",
        "tips_es": "La mayoría de los viajeros americanos hacen escala en París, Bruselas o Casablanca. Desde la Costa Este, contad con 12-14h en total.",
        "tips_it": "La maggior parte dei viaggiatori americani fa scalo a Parigi, Bruxelles o Casablanca. Dalla Costa Est, circa 12-14h totali.",
        "tips_de": "Die meisten US-Reisenden reisen über Paris, Brüssel oder Casablanca. Von der Ostküste ca. 12–14h gesamt.",
        "search_url": "https://www.google.com/travel/flights/search?q=New+York+to+Dakar+flights",
    },
    "ca": {
        "flag": "ca",
        "name_en": "Canada", "name_fr": "Canada", "name_es": "Canadá", "name_it": "Canada", "name_de": "Kanada",
        "hub": "Toronto YYZ / Montréal YUL / Vancouver YVR",
        "duration": "~14–18h",
        "price_range": "CAD 900–1,800",
        "airlines": ["Air France","Brussels Airlines","Air Canada","Royal Air Maroc"],
        "direct": False,
        "connection": "Paris, Brussels, or Casablanca",
        "tips_en": "From Montréal, Air France via Paris offers the most natural connection. From Toronto, Brussels Airlines via Brussels is a solid option. From Vancouver, expect a longer journey of 18+ hours with at least one connection.",
        "tips_fr": "Depuis Montréal, Air France via Paris est la meilleure option. Depuis Toronto, Brussels Airlines via Bruxelles est idéal. Depuis Vancouver, comptez 18h+ avec au moins une correspondance.",
        "tips_es": "Desde Montreal, Air France vía París es la mejor opción. Desde Toronto, Brussels Airlines vía Bruselas es sólido.",
        "tips_it": "Da Montreal, Air France via Parigi offre la connessione più naturale. Da Toronto, Brussels Airlines via Bruxelles è un'ottima scelta.",
        "tips_de": "Ab Montreal ist Air France via Paris die beste Verbindung. Ab Toronto bietet Brussels Airlines via Brüssel eine gute Option.",
        "search_url": "https://www.google.com/travel/flights/search?q=Toronto+to+Dakar+flights",
    },
    "au": {
        "flag": "au",
        "name_en": "Australia", "name_fr": "Australie", "name_es": "Australia", "name_it": "Australia", "name_de": "Australien",
        "hub": "Sydney SYD / Melbourne MEL / Brisbane BNE",
        "duration": "~24–30h",
        "price_range": "AUD 1,800–3,500",
        "airlines": ["Emirates","Qatar Airways","Air France","Etihad"],
        "direct": False,
        "connection": "Dubai, Doha or European hub",
        "tips_en": "Australia to Senegal is a significant journey — budget 24–30 hours with 2 connections. The most comfortable route is Emirates via Dubai, or Qatar Airways via Doha. Once in Europe, connect to Dakar via Air France or Brussels Airlines. Consider a stopover in Europe to break the journey.",
        "tips_fr": "L'Australie au Sénégal est un long voyage — comptez 24–30h avec 2 correspondances. Emirates via Dubaï ou Qatar Airways via Doha sont les options les plus confortables. Envisagez une escale en Europe pour décomposer le trajet.",
        "tips_es": "Australia a Senegal es un viaje largo — entre 24-30h con 2 conexiones. Emirates vía Dubái o Qatar Airways vía Doha son las opciones más cómodas.",
        "tips_it": "Dall'Australia al Senegal è un viaggio lungo — 24-30h con 2 scali. Emirates via Dubai o Qatar Airways via Doha sono le opzioni più comode.",
        "tips_de": "Australien nach Senegal ist eine lange Reise — 24–30 Stunden mit 2 Verbindungen. Emirates via Dubai oder Qatar Airways via Doha sind die komfortabelsten Optionen.",
        "search_url": "https://www.google.com/travel/flights/search?q=Sydney+to+Dakar+flights",
    },
}

# Default country per language
DEFAULT_COUNTRY = {"en":"uk","fr":"fr","es":"es","it":"it","de":"de"}
# But for DE/ES/IT country, use the matching data
FLIGHT_DATA["de_country"] = {**FLIGHT_DATA["fr"], "flag":"de",
    "hub":"Frankfurt FRA / Munich MUC / Berlin BER", "duration":"~7h", "price_range":"€250–650",
    "airlines":["Lufthansa","Air France","Eurowings","Air Sénégal"],
    "direct":False, "connection":"Paris or Brussels",
    "tips_en":"From Germany, the best connections to Dakar are via Paris (Air France) or Brussels (Brussels Airlines). Lufthansa codeshares can also get you there via Paris or Casablanca.",
    "tips_de":"Von Deutschland sind die besten Verbindungen nach Dakar via Paris (Air France) oder Brüssel (Brussels Airlines). Auch Lufthansa-Codeshares via Paris oder Casablanca sind möglich.",
    "search_url":"https://www.google.com/travel/flights/search?q=Frankfurt+to+Dakar+flights"}
FLIGHT_DATA["es_country"] = {**FLIGHT_DATA["fr"], "flag":"es",
    "hub":"Madrid MAD / Barcelona BCN","duration":"~6-7h","price_range":"€200–550",
    "airlines":["Iberia","Air France","Volotea","Air Sénégal"],
    "direct":False,"connection":"Madrid direct (seasonal) or Paris/Casablanca",
    "tips_en":"From Spain, Iberia flies direct Madrid → Dakar seasonally. Otherwise, connect via Paris or Casablanca with Royal Air Maroc. Barcelona travelers can fly via Madrid or Paris.",
    "tips_es":"Desde España, Iberia vuela directo Madrid → Dakar de forma estacional. De lo contrario, conecta vía París o Casablanca con Royal Air Maroc.",
    "search_url":"https://www.google.com/travel/flights/search?q=Madrid+to+Dakar+flights"}
FLIGHT_DATA["it_country"] = {**FLIGHT_DATA["fr"], "flag":"it",
    "hub":"Rome FCO / Milan MXP / Turin TRN","duration":"~7-8h","price_range":"€280–650",
    "airlines":["ITA Airways","Air France","Neos","Air Sénégal"],
    "direct":False,"connection":"Paris, Brussels or Casablanca",
    "tips_en":"From Italy, connect via Paris (Air France) or Casablanca (Royal Air Maroc). Rome Fiumicino offers the most connections. Neos occasionally operates seasonal charters from Italian cities to Dakar.",
    "tips_it":"Dall'Italia, collegati via Parigi (Air France) o Casablanca (Royal Air Maroc). Roma Fiumicino offre le migliori connessioni. Neos opera occasionalmente charter stagionali da città italiane a Dakar.",
    "search_url":"https://www.google.com/travel/flights/search?q=Rome+to+Dakar+flights"}

# ════════════════════════════════════════════════════════════════
# TRANSLATIONS
# ════════════════════════════════════════════════════════════════
T = {
    "page_title": {
        "en":"How to Get to Ngor Island, Senegal",
        "fr":"Comment se rendre à l'Île de Ngor, Sénégal",
        "es":"Cómo llegar a la Isla de Ngor, Senegal",
        "it":"Come arrivare all'Isola di Ngor, Senegal",
        "de":"Wie kommt man nach Ngor Island, Senegal",
    },
    "page_meta": {
        "en":"Step-by-step guide to reaching Ngor Island, Dakar, Senegal. Flights, transfers, pirogue ride — everything you need to plan your journey.",
        "fr":"Guide complet pour se rendre à l'île de Ngor, Dakar, Sénégal. Vols, transferts, pirogue — tout ce qu'il faut savoir pour planifier votre voyage.",
        "es":"Guía paso a paso para llegar a la isla de Ngor, Dakar, Senegal. Vuelos, traslados, piragua — todo lo que necesitas para planificar tu viaje.",
        "it":"Guida passo passo per raggiungere l'isola di Ngor, Dakar, Senegal. Voli, trasferimenti, piroga — tutto il necessario per pianificare il tuo viaggio.",
        "de":"Schritt-für-Schritt-Anleitung nach Ngor Island, Dakar, Senegal. Flüge, Transfers, Piroge — alles was Sie für Ihre Reiseplanung benötigen.",
    },
    "h1": {
        "en":"Getting to Ngor Island",
        "fr":"Se Rendre à l'Île de Ngor",
        "es":"Cómo Llegar a la Isla de Ngor",
        "it":"Come Arrivare a Ngor Island",
        "de":"Anreise nach Ngor Island",
    },
    "subtitle": {
        "en":"From airport to paradise — your complete travel guide to Ngor Island, Dakar, Senegal.",
        "fr":"De l'aéroport au paradis — votre guide complet pour rejoindre l'île de Ngor, Dakar, Sénégal.",
        "es":"Del aeropuerto al paraíso — tu guía completa para llegar a la isla de Ngor, Dakar, Senegal.",
        "it":"Dall'aeroporto al paradiso — la tua guida completa per raggiungere l'isola di Ngor, Dakar, Senegal.",
        "de":"Vom Flughafen ins Paradies — Ihr vollständiger Reiseführer nach Ngor Island, Dakar, Senegal.",
    },
    "map_title": {"en":"Where is Ngor Island?","fr":"Où se trouve l'Île de Ngor ?","es":"¿Dónde está la Isla de Ngor?","it":"Dove si trova Ngor Island?","de":"Wo liegt Ngor Island?"},
    "map_sub": {
        "en":"Ngor Island sits 800 meters off the Cap-Vert peninsula in Dakar, just 20 minutes from the international airport.",
        "fr":"L'île de Ngor se trouve à 800 mètres de la péninsule du Cap-Vert à Dakar, à seulement 20 minutes de l'aéroport international.",
        "es":"La isla de Ngor se encuentra a 800 metros de la península de Cap-Vert en Dakar, a solo 20 minutos del aeropuerto internacional.",
        "it":"L'isola di Ngor si trova a 800 metri dalla penisola di Cap-Vert a Dakar, a soli 20 minuti dall'aeroporto internazionale.",
        "de":"Ngor Island liegt 800 Meter vor der Cap-Vert-Halbinsel in Dakar, nur 20 Minuten vom internationalen Flughafen entfernt.",
    },
    "steps_title": {"en":"Step-by-Step: Airport to Island","fr":"Étape par Étape : De l'Aéroport à l'Île","es":"Paso a Paso: Del Aeropuerto a la Isla","it":"Passo dopo Passo: Dall'Aeroporto all'Isola","de":"Schritt für Schritt: Vom Flughafen zur Insel"},
    "steps": {
        "en":[
            ("✈️","Land at Blaise Diagne Airport (DSS)","Dakar's international airport, Blaise Diagne (DSS), is located about 45km east of the city. It serves flights from Europe, Africa and North America."),
            ("🚕","Taxi or Uber to Ngor Beach","Take a taxi or Uber from the airport to Ngor beach (Plage de Ngor). The journey takes 20–30 minutes and costs approximately 5,000–8,000 CFA (€8–12). Book your taxi inside the arrivals hall to avoid touts."),
            ("🚢","Pirogue to Ngor Island","At Ngor beach, walk to the small pier and take a traditional pirogue (wooden boat) to Ngor Island. The 5-minute crossing costs less than 500 CFA (under €1). Pirogues run continuously until around 10pm."),
            ("🏄","Arrive at Ngor Surfcamp Teranga","Once on the island, Ngor Surfcamp Teranga is a 3-minute walk from the pirogue landing. Our team can meet you — just WhatsApp us your arrival time!"),
        ],
        "fr":[
            ("✈️","Atterrissage à l'Aéroport Blaise Diagne (DSS)","L'aéroport international de Dakar, Blaise Diagne (DSS), est situé à environ 45km à l'est de la ville. Il dessert des vols depuis l'Europe, l'Afrique et l'Amérique du Nord."),
            ("🚕","Taxi ou Uber jusqu'à la Plage de Ngor","Prenez un taxi ou Uber depuis l'aéroport jusqu'à la plage de Ngor. Le trajet dure 20–30 minutes et coûte environ 5 000–8 000 CFA (8–12€). Réservez votre taxi dans le hall des arrivées pour éviter les rabatteurs."),
            ("🚢","Pirogue vers l'Île de Ngor","À la plage de Ngor, marchez jusqu'à la petite jetée et prenez une pirogue traditionnelle vers l'île de Ngor. La traversée de 5 minutes coûte moins de 500 CFA (moins d'1€). Les pirogues fonctionnent en continu jusqu'à environ 22h."),
            ("🏄","Bienvenue au Ngor Surfcamp Teranga","Une fois sur l'île, le Ngor Surfcamp Teranga est à 3 minutes à pied du débarcadère. Notre équipe peut vous accueillir — envoyez-nous simplement un WhatsApp avec votre heure d'arrivée !"),
        ],
        "es":[
            ("✈️","Aterrizaje en el Aeropuerto Blaise Diagne (DSS)","El aeropuerto internacional de Dakar, Blaise Diagne (DSS), está a unos 45km al este de la ciudad. Recibe vuelos desde Europa, África y Norteamérica."),
            ("🚕","Taxi o Uber hasta la Playa de Ngor","Toma un taxi o Uber desde el aeropuerto hasta la playa de Ngor. El trayecto dura 20-30 minutos y cuesta aproximadamente 5.000-8.000 CFA (8-12€). Reserva el taxi en la sala de llegadas."),
            ("🚢","Piragua hasta la Isla de Ngor","En la playa de Ngor, camina hasta el pequeño embarcadero y toma una piragua tradicional hasta la isla de Ngor. La travesía de 5 minutos cuesta menos de 500 CFA (menos de 1€). Las piraguas funcionan hasta las 22h."),
            ("🏄","Bienvenido a Ngor Surfcamp Teranga","Una vez en la isla, Ngor Surfcamp Teranga está a 3 minutos caminando del embarcadero. ¡Escríbenos por WhatsApp con tu hora de llegada!"),
        ],
        "it":[
            ("✈️","Atterraggio all'Aeroporto Blaise Diagne (DSS)","L'aeroporto internazionale di Dakar, Blaise Diagne (DSS), si trova a circa 45km a est della città. Serve voli da Europa, Africa e Nord America."),
            ("🚕","Taxi o Uber fino alla Spiaggia di Ngor","Prendi un taxi o Uber dall'aeroporto alla spiaggia di Ngor. Il percorso dura 20-30 minuti e costa circa 5.000-8.000 CFA (8-12€). Prenota il taxi nell'area arrivi."),
            ("🚢","Piroga verso Ngor Island","Alla spiaggia di Ngor, cammina fino al piccolo molo e prendi una piroga tradizionale verso Ngor Island. La traversata di 5 minuti costa meno di 500 CFA (meno di 1€). Le piroghe funzionano fino alle 22h."),
            ("🏄","Benvenuto al Ngor Surfcamp Teranga","Una volta sull'isola, il Ngor Surfcamp Teranga è a 3 minuti a piedi dall'approdo. Scrivici su WhatsApp con il tuo orario di arrivo!"),
        ],
        "de":[
            ("✈️","Landung am Flughafen Blaise Diagne (DSS)","Der internationale Flughafen Dakar, Blaise Diagne (DSS), liegt etwa 45km östlich der Stadt. Er bedient Flüge aus Europa, Afrika und Nordamerika."),
            ("🚕","Taxi oder Uber zum Ngor-Strand","Nehmen Sie ein Taxi oder Uber vom Flughafen zum Ngor-Strand. Die Fahrt dauert 20–30 Minuten und kostet ca. 5.000–8.000 CFA (8–12€). Buchen Sie das Taxi im Ankunftsbereich."),
            ("🚢","Piroge nach Ngor Island","Am Ngor-Strand gehen Sie zum kleinen Pier und nehmen eine traditionelle Piroge nach Ngor Island. Die 5-minütige Überfahrt kostet weniger als 500 CFA (unter 1€). Piroge fahren bis ca. 22 Uhr."),
            ("🏄","Willkommen im Ngor Surfcamp Teranga","Auf der Insel ist das Ngor Surfcamp Teranga 3 Gehminuten vom Anleger entfernt. Schreiben Sie uns einfach auf WhatsApp mit Ihrer Ankunftszeit!"),
        ],
    },
    "practical_title": {"en":"Practical Information","fr":"Informations Pratiques","es":"Información Práctica","it":"Informazioni Pratiche","de":"Praktische Informationen"},
    "practical": {
        "en":[
            ("🛂","Visa","Citizens of EU countries, UK, USA, Canada and most Western nations do not need a visa for Senegal. You receive a free 90-day stamp on arrival. Always verify with your country's foreign affairs office before travelling."),
            ("💱","Currency","Senegal uses the West African CFA Franc (XOF). 1 EUR ≈ 655 CFA | 1 GBP ≈ 760 CFA | 1 USD ≈ 605 CFA. Withdraw cash from ATMs in Dakar before taking the pirogue — most transactions on Ngor Island are cash only."),
            ("📱","SIM Card","Free Orange SIM cards available at the airport. Data packages from €5/week. WhatsApp works perfectly throughout Dakar and Ngor Island."),
            ("🕐","Best Time to Fly","Book flights 6–12 weeks in advance for the best prices. High surf season (Nov–Apr) sees more demand. Flying on Tuesdays and Wednesdays is generally cheaper. Paris and Brussels routes offer the most flexibility."),
            ("🧳","Luggage","Most surf travelers bring minimal luggage: a board bag (if bringing your own board) + a carry-on. Boards can be rented at the camp. For budget airlines, watch for baggage fees."),
            ("🏥","Health","No mandatory vaccines for Senegal. Malaria prophylaxis is recommended — consult your GP 4–6 weeks before departure. Bring high-SPF sun protection and reef-safe sunscreen."),
        ],
        "fr":[
            ("🛂","Visa","Les citoyens des pays de l'UE, du Royaume-Uni, des États-Unis, du Canada et de la plupart des nations occidentales n'ont pas besoin de visa pour le Sénégal. Vous recevez un tampon gratuit de 90 jours à l'arrivée. Vérifiez toujours avec votre ministère des Affaires étrangères avant de voyager."),
            ("💱","Monnaie","Le Sénégal utilise le Franc CFA d'Afrique de l'Ouest (XOF). 1 EUR ≈ 655 CFA. Retirez des espèces aux distributeurs à Dakar avant de prendre la pirogue — la plupart des transactions sur l'île de Ngor se font en espèces."),
            ("📱","Carte SIM","Cartes SIM Orange gratuites disponibles à l'aéroport. Forfaits data à partir de 5€/semaine. WhatsApp fonctionne parfaitement sur Dakar et l'île de Ngor."),
            ("🕐","Meilleur Moment pour Voler","Réservez vos vols 6–12 semaines à l'avance pour les meilleurs prix. La haute saison de surf (nov–avr) est plus demandée. Voler le mardi ou mercredi est généralement moins cher."),
            ("🧳","Bagages","La plupart des surfeurs voyagent léger. Les planches peuvent être louées au camp. Pour les compagnies low-cost, attention aux frais de bagages."),
            ("🏥","Santé","Pas de vaccin obligatoire pour le Sénégal. Une prophylaxie antipaludéenne est recommandée — consultez votre médecin 4–6 semaines avant le départ. Apportez une crème solaire haute protection et respect de la barrière corallienne."),
        ],
        "es":[
            ("🛂","Visado","Los ciudadanos de la UE, UK, EE.UU., Canadá y la mayoría de naciones occidentales no necesitan visado para Senegal. Recibes un sello gratuito de 90 días a la llegada."),
            ("💱","Moneda","Senegal usa el Franco CFA de África Occidental (XOF). 1 EUR ≈ 655 CFA. Retira efectivo en cajeros de Dakar antes de tomar la piragua — la mayoría de transacciones en Ngor son en efectivo."),
            ("📱","Tarjeta SIM","Tarjetas SIM Orange gratuitas en el aeropuerto. Paquetes de datos desde 5€/semana. WhatsApp funciona perfectamente en Dakar y Ngor Island."),
            ("🕐","Mejor Momento para Volar","Reserva con 6-12 semanas de antelación. La temporada alta de surf (nov-abr) tiene más demanda. Volar martes o miércoles suele ser más barato."),
            ("🧳","Equipaje","La mayoría de surfistas viajan ligero. Las tablas se pueden alquilar en el camp. Con aerolíneas low-cost, atención a las tasas de equipaje."),
            ("🏥","Salud","No hay vacunas obligatorias para Senegal. Se recomienda profilaxis antipalúdica. Consulta a tu médico 4-6 semanas antes del viaje."),
        ],
        "it":[
            ("🛂","Visto","I cittadini UE, UK, USA, Canada e la maggior parte delle nazioni occidentali non hanno bisogno del visto per il Senegal. Ricevi un timbro gratuito di 90 giorni all'arrivo."),
            ("💱","Valuta","Il Senegal usa il Franco CFA dell'Africa Occidentale (XOF). 1 EUR ≈ 655 CFA. Preleva contanti dai bancomat a Dakar prima di prendere la piroga — la maggior parte delle transazioni su Ngor Island sono in contanti."),
            ("📱","SIM Card","SIM Orange gratuita disponibile all'aeroporto. Pacchetti dati da 5€/settimana. WhatsApp funziona perfettamente a Dakar e Ngor Island."),
            ("🕐","Miglior Momento per Volare","Prenota 6-12 settimane prima. L'alta stagione surf (nov-apr) ha più richiesta. Volare martedì o mercoledì è generalmente più economico."),
            ("🧳","Bagaglio","La maggior parte dei surfisti viaggia leggera. Le tavole possono essere noleggiate al camp. Con le compagnie low-cost, attenzione alle tasse bagaglio."),
            ("🏥","Salute","Nessun vaccino obbligatorio per il Senegal. Si raccomanda la profilassi antimalarica. Consulta il medico 4-6 settimane prima della partenza."),
        ],
        "de":[
            ("🛂","Visum","Bürger der EU, UK, USA, Kanada und der meisten westlichen Länder benötigen kein Visum für Senegal. Sie erhalten einen kostenlosen 90-Tage-Stempel bei der Einreise."),
            ("💱","Währung","Senegal verwendet den westafrikanischen CFA-Franc (XOF). 1 EUR ≈ 655 CFA. Heben Sie Bargeld von Geldautomaten in Dakar ab — die meisten Transaktionen auf Ngor Island sind nur in bar möglich."),
            ("📱","SIM-Karte","Kostenlose Orange-SIM-Karten am Flughafen erhältlich. Datenpakete ab 5€/Woche. WhatsApp funktioniert in ganz Dakar und auf Ngor Island einwandfrei."),
            ("🕐","Beste Reisezeit zum Fliegen","6–12 Wochen im Voraus buchen für beste Preise. Dienstags und mittwochs fliegen ist oft günstiger."),
            ("🧳","Gepäck","Die meisten Surfer reisen mit wenig Gepäck. Surfboards können im Camp gemietet werden."),
            ("🏥","Gesundheit","Keine Pflichtimpfungen für Senegal. Malaria-Prophylaxe wird empfohlen. 4–6 Wochen vor der Abreise beim Arzt nachfragen."),
        ],
    },
    "flights_title": {"en":"Flights from Your Country","fr":"Vols depuis votre Pays","es":"Vuelos desde tu País","it":"Voli dal tuo Paese","de":"Flüge aus Ihrem Land"},
    "select_country": {"en":"Select your departure country","fr":"Sélectionnez votre pays de départ","es":"Selecciona tu país de origen","it":"Seleziona il tuo paese di partenza","de":"Wählen Sie Ihr Abflugland"},
    "direct": {"en":"Direct","fr":"Direct","es":"Directo","it":"Diretto","de":"Direkt"},
    "via": {"en":"Via","fr":"Via","es":"Via","it":"Via","de":"Via"},
    "airlines": {"en":"Airlines","fr":"Compagnies","es":"Aerolíneas","it":"Compagnie","de":"Airlines"},
    "duration": {"en":"Flight time","fr":"Durée du vol","es":"Tiempo de vuelo","it":"Durata del volo","de":"Flugzeit"},
    "price": {"en":"From","fr":"À partir de","es":"Desde","it":"Da","de":"Ab"},
    "search_flights": {"en":"Search flights","fr":"Rechercher des vols","es":"Buscar vuelos","it":"Cerca voli","de":"Flüge suchen"},
    "book_now": {"en":"Book Your Stay","fr":"Réserver votre Séjour","es":"Reserva tu Estancia","it":"Prenota il tuo Soggiorno","de":"Aufenthalt buchen"},
    "any_questions": {"en":"Any questions? Chat with us on WhatsApp.","fr":"Des questions ? Écrivez-nous sur WhatsApp.","es":"¿Preguntas? Escríbenos por WhatsApp.","it":"Domande? Scrivici su WhatsApp.","de":"Fragen? Schreiben Sie uns auf WhatsApp."},
    "stats": {
        "en":[("20 min","from airport"),("800m","from mainland"),("5 min","pirogue crossing"),("<1€","to reach the island")],
        "fr":[("20 min","depuis l'aéroport"),("800m","du continent"),("5 min","traversée en pirogue"),("<1€","pour rejoindre l'île")],
        "es":[("20 min","desde el aeropuerto"),("800m","del continente"),("5 min","travesía en piragua"),("<1€","para llegar a la isla")],
        "it":[("20 min","dall'aeroporto"),("800m","dalla terraferma"),("5 min","traversata in piroga"),("<1€","per raggiungere l'isola")],
        "de":[("20 min","vom Flughafen"),("800m","vom Festland"),("5 min","Pirogenfahrt"),("<1€","um die Insel zu erreichen")],
    },
    "homepage_block": {
        "title": {"en":"Getting to Ngor Island","fr":"Comment se rendre à Ngor","es":"Cómo llegar a Ngor","it":"Come arrivare a Ngor","de":"Anreise nach Ngor"},
        "sub":   {"en":"Complete travel guide — flights, transfers, pirogue and everything you need to know to reach us.","fr":"Guide voyage complet — vols, transferts, pirogue et tout ce qu'il faut savoir pour nous rejoindre.","es":"Guía de viaje completa — vuelos, traslados, piragua y todo lo que necesitas saber para llegar.","it":"Guida di viaggio completa — voli, trasferimenti, piroga e tutto ciò che devi sapere per arrivare.","de":"Vollständiger Reiseführer — Flüge, Transfers, Piroge und alles Wissenswerte für Ihre Anreise."},
        "cta":   {"en":"Plan Your Journey","fr":"Planifier votre Voyage","es":"Planifica tu Viaje","it":"Pianifica il tuo Viaggio","de":"Reise planen"},
    },
}

def g(key, lang): return T[key].get(lang, T[key]["en"])

# ════════════════════════════════════════════════════════════════
# NAV + FOOTER helpers (reuse same pattern)
# ════════════════════════════════════════════════════════════════
def build_nav(lang):
    pfx = LANG_PFX[lang]
    NAV=[("",{"en":"Home","fr":"Accueil","es":"Inicio","it":"Home","de":"Start"}),("surf-house",{"en":"Surf House","fr":"Surf House","es":"Surf House","it":"Surf House","de":"Surf House"}),("island",{"en":"Island","fr":"Île","es":"Isla","it":"Isola","de":"Insel"}),("surfing",{"en":"Surfing","fr":"Surf","es":"Surf","it":"Surf","de":"Surfen"}),("blog",{"en":"Blog","fr":"Blog","es":"Blog","it":"Blog","de":"Blog"}),("gallery",{"en":"Gallery","fr":"Galerie","es":"Galería","it":"Galleria","de":"Galerie"}),("booking",{"en":"Book Now","fr":"Réserver","es":"Reservar","it":"Prenota","de":"Buchen"})]
    items = "".join([f'<a href="{pfx}/{SLUG[lang].get(k,k)}/" class="nav-link{ " nav-cta" if k=="booking" else ""}">{l.get(lang,l["en"])}</a>' if k else f'<a href="{pfx}/" class="nav-link">{l.get(lang,l["en"])}</a>' for k,l in NAV])
    gh = SLUG_GET_HERE[lang]
    get_here_label = {"en":"Getting Here","fr":"Comment Venir","es":"Cómo Llegar","it":"Come Arrivare","de":"Anreise"}[lang]
    items += f'<a href="{pfx}/{gh}/" class="nav-link active">{get_here_label}</a>'
    opts = "".join([f'<a class="lang-dd-item" href="{LANG_PFX[l]}/{SLUG_GET_HERE[l]}/" hreflang="{LANG_LOCALE[l]}">{flag(l,18)} {LANG_NAMES[l]}</a>' for l in LANGS if l!=lang])
    return f'<nav id="nav"><div class="nav-inner"><a href="{pfx}/" class="nav-logo"><img src="{LOGO}" alt="Ngor Surfcamp Teranga" width="130" height="44" loading="eager"></a><div class="nav-links" id="nav-links">{items}</div><div class="nav-right"><div class="lang-dd" id="lang-dd"><button class="lang-dd-btn" onclick="toggleLangDD(event)">{flag(lang,20)} {lang.upper()} <span style="display:inline-flex">{CHEV}</span></button><div class="lang-dd-menu" role="menu">{opts}</div></div><a href="https://wa.me/221789257025" target="_blank" rel="noopener" class="nav-wa" aria-label="WhatsApp"><span style="display:inline-flex">{WA_ICO}</span><span class="nav-wa-label">WhatsApp</span></a><button class="nav-toggle" id="nav-toggle" aria-label="Menu" onclick="toggleMenu()"><span style="display:inline-flex;color:#fff">{MENU}</span></button></div></div></nav>'

# ════════════════════════════════════════════════════════════════
# BUILD PAGE
# ════════════════════════════════════════════════════════════════
def build_getting_here(lang):
    pfx   = LANG_PFX[lang]
    slug  = SLUG_GET_HERE[lang]
    title = g("page_title", lang)
    meta  = g("page_meta", lang)

    # Country order and default per lang
    COUNTRY_ORDER = {"en":["uk","fr","us","ca","au"],"fr":["fr","uk","us","ca","au"],"es":["es_country","fr","uk","us","ca","au"],"it":["it_country","fr","uk","us","ca","au"],"de":["de_country","fr","uk","us","ca","au"]}
    country_list = COUNTRY_ORDER.get(lang, ["uk","fr","us","ca","au"])
    default_country = country_list[0]

    # Hreflang
    hrl = "\n".join([f'<link rel="alternate" hreflang="x-default" href="{SITE_URL}/{SLUG_GET_HERE["en"]}/">',f'<link rel="alternate" hreflang="en" href="{SITE_URL}/{SLUG_GET_HERE["en"]}/">']+[f'<link rel="alternate" hreflang="{LANG_LOCALE[l]}" href="{SITE_URL}/{LANG_PFX[l]}/{SLUG_GET_HERE[l]}/">' for l in ["fr","es","it","de"]])
    can = f'<link rel="canonical" href="{SITE_URL}{pfx}/{slug}/">'

    # Country selector HTML
    def flight_panel(country_key):
        fd = FLIGHT_DATA.get(country_key, FLIGHT_DATA["uk"])
        tips_key = f"tips_{lang}"
        tips = fd.get(tips_key, fd.get("tips_en",""))
        flag_html = f'<span style="width:22px;height:15px;display:inline-flex;border-radius:2px;overflow:hidden">{FLAGS_EXTRA.get(fd["flag"],FLAG_SVG.get(fd["flag"],""))}</span>'
        direct_badge = f'<span style="padding:3px 10px;border-radius:20px;background:rgba(34,197,94,0.15);color:#22c55e;font-size:11px;font-weight:700">{g("direct",lang)}</span>' if fd.get("direct") else f'<span style="padding:3px 10px;border-radius:20px;background:rgba(255,90,31,0.12);color:var(--fire);font-size:11px;font-weight:700">{g("via",lang)}: {fd.get("connection","")}</span>'
        return f'''<div class="flight-panel" data-country="{country_key}" style="display:{"block" if country_key==default_country else "none"}">
  <div class="flight-header">
    <div style="display:flex;align-items:center;gap:12px">
      {flag_html}
      <div>
        <div style="font-weight:700;font-size:17px;color:var(--navy)">{fd.get(f"name_{lang}",fd["name_en"])}</div>
        <div style="font-size:13px;color:var(--muted);margin-top:2px">{fd["hub"]}</div>
      </div>
    </div>
    {direct_badge}
  </div>
  <div class="flight-meta">
    <div class="flight-meta-item">
      <span class="fmi-label">{g("duration",lang)}</span>
      <span class="fmi-value">{fd["duration"]}</span>
    </div>
    <div class="flight-meta-item">
      <span class="fmi-label">{g("price",lang)}</span>
      <span class="fmi-value">{fd["price_range"]}</span>
    </div>
    <div class="flight-meta-item">
      <span class="fmi-label">{g("airlines",lang)}</span>
      <span class="fmi-value">{", ".join(fd["airlines"][:3])}</span>
    </div>
  </div>
  <p style="font-size:15px;color:#374151;line-height:1.75;margin:16px 0">{tips}</p>
  <a href="{fd["search_url"]}" target="_blank" rel="noopener" class="btn btn-deep btn-sm" style="display:inline-flex;align-items:center;gap:8px">
    <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16"><path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd"/></svg>
    {g("search_flights",lang)}
  </a>
</div>'''

    country_tabs = ""
    panels = ""
    for ck in country_list:
        fd = FLIGHT_DATA.get(ck, FLIGHT_DATA["uk"])
        flag_html = f'<span style="width:20px;height:13px;display:inline-flex;border-radius:2px;overflow:hidden">{FLAGS_EXTRA.get(fd["flag"],FLAG_SVG.get(fd["flag"],""))}</span>'
        active_cls = "tab-btn active" if ck == default_country else "tab-btn"
        name = fd.get(f"name_{lang}", fd["name_en"])
        country_tabs += f'<button class="{active_cls}" onclick="switchCountry(\'{ck}\')" data-country="{ck}">{flag_html} <span style="font-size:13px">{name}</span></button>'
        panels += flight_panel(ck)

    # Steps
    steps_html = ""
    for i, (ico, title_s, desc_s) in enumerate(T["steps"][lang]):
        steps_html += f'''<div class="step-item reveal">
  <div class="step-num">{i+1}</div>
  <div class="step-icon">{ico}</div>
  <div class="step-content">
    <div class="step-title">{title_s}</div>
    <p class="step-desc">{desc_s}</p>
  </div>
</div>'''

    # Practical info
    practical_html = ""
    for ico, title_p, desc_p in T["practical"][lang]:
        practical_html += f'''<div class="practical-item reveal">
  <div class="practical-icon">{ico}</div>
  <div>
    <div class="practical-title">{title_p}</div>
    <p class="practical-desc">{desc_p}</p>
  </div>
</div>'''

    # Quick stats
    stats_html = "".join([f'<div class="journey-stat"><span class="js-num">{num}</span><span class="js-lbl">{lbl}</span></div>' for num, lbl in T["stats"][lang]])

    html = f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{meta}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{meta}">
<meta property="og:image" content="{WIX}/df99f9_56b9af6efe2841eea44109b3b08b7da1~mv2.jpg">
<meta property="og:type" content="website">
<meta name="robots" content="index,follow">
{can}
{hrl}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Raleway:ital,wght@0,300;0,400;0,600;0,700;0,800;0,900;1,400&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<!-- Leaflet CSS -->
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" crossorigin="">
<link rel="stylesheet" href="/assets/css/{ASSET_CSS_MAIN}?v={ASSET_VERSION}">
<script src="/assets/js/{ASSET_JS_MAIN}?v={ASSET_VERSION}" defer></script>
<style>
/* ── Getting Here Page ─────────────────────────────── */
.gh-hero {{ background: linear-gradient(160deg,#070f1c,#0a2540 50%,#071826); color:#fff; padding:140px 28px 80px; text-align:center; position:relative; overflow:hidden; }}
.gh-hero::before {{ content:''; position:absolute; inset:0; background:radial-gradient(ellipse at 50% 80%,rgba(255,90,31,0.12) 0%,transparent 55%); }}
.gh-hero h1 {{ font-size:clamp(32px,5vw,58px); margin-bottom:16px; position:relative; z-index:1; }}
.gh-hero p {{ font-size:18px; opacity:0.78; max-width:600px; margin:0 auto; position:relative; z-index:1; line-height:1.7; }}
/* Journey stats — light neutral strip */
.journey-stats {{ display:flex; justify-content:center; flex-wrap:wrap; gap:40px; padding:48px 28px; background:linear-gradient(180deg,#f4f6f9 0%,#eef1f5 100%); border-top:1px solid rgba(10,37,64,0.06); border-bottom:1px solid rgba(10,37,64,0.06); }}
.journey-stat {{ text-align:center; }}
.js-num {{ font-family:var(--fh); font-size:clamp(34px,5vw,48px); font-weight:900; color:var(--navy); display:block; line-height:1; }}
.js-lbl {{ font-size:11px; letter-spacing:0.12em; text-transform:uppercase; color:#64748b; margin-top:8px; display:block; font-weight:600; }}
/* Map */
.map-section {{ padding:80px 0 0; }}
#ngor-map {{ height:480px; border-radius:0; position:relative; z-index:1; }}
.leaflet-container {{ background:#e8eaed; }}
/* Custom marker */
.ngor-marker-icon {{ background:var(--fire,#ff5a1f); width:44px; height:44px; border-radius:50%; border:4px solid #fff; display:flex; align-items:center; justify-content:center; box-shadow:0 3px 14px rgba(10,37,64,0.18); font-size:20px; }}
/* Steps */
.steps-section {{ padding:80px 0; background:#f8fafd; }}
.step-item {{ display:flex; align-items:flex-start; gap:20px; padding:24px; background:#fff; border-radius:16px; margin-bottom:16px; box-shadow:0 2px 12px rgba(10,37,64,0.06); transition:transform 0.2s,box-shadow 0.2s; }}
.step-item:hover {{ transform:translateY(-2px); box-shadow:0 8px 24px rgba(10,37,64,0.12); }}
.step-num {{ width:36px; height:36px; border-radius:50%; background:linear-gradient(135deg,var(--fire),#e04a10); color:#fff; display:flex; align-items:center; justify-content:center; font-family:var(--fh); font-weight:800; font-size:15px; flex-shrink:0; }}
.step-icon {{ font-size:28px; flex-shrink:0; width:44px; text-align:center; }}
.step-title {{ font-weight:700; font-size:16px; color:var(--navy); margin-bottom:6px; }}
.step-desc {{ font-size:14.5px; color:#4b5563; line-height:1.7; margin:0; }}
/* Flights */
.flights-section {{ padding:80px 0; }}
.country-tabs {{ display:flex; flex-wrap:wrap; gap:8px; margin-bottom:28px; }}
.tab-btn {{ display:inline-flex; align-items:center; gap:8px; padding:10px 18px; border-radius:50px; background:#f3f4f6; border:2px solid transparent; color:#374151; font-weight:600; font-size:13px; cursor:pointer; transition:all 0.2s; }}
.tab-btn:hover {{ background:var(--navy); color:#fff; }}
.tab-btn.active {{ background:var(--navy); color:#fff; border-color:var(--navy); }}
.flight-panel {{ background:#fff; border-radius:20px; padding:28px; box-shadow:0 4px 24px rgba(10,37,64,0.08); border:1px solid rgba(10,37,64,0.06); }}
.flight-header {{ display:flex; align-items:center; justify-content:space-between; margin-bottom:20px; flex-wrap:wrap; gap:12px; }}
.flight-meta {{ display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin-bottom:16px; background:#f8fafd; border-radius:12px; padding:16px; }}
.flight-meta-item {{ display:flex; flex-direction:column; gap:3px; }}
.fmi-label {{ font-size:11px; text-transform:uppercase; letter-spacing:0.1em; color:#9ca3af; font-weight:600; }}
.fmi-value {{ font-size:15px; font-weight:700; color:var(--navy); }}
/* Practical */
.practical-section {{ padding:80px 0; background:#f8fafd; }}
.practical-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:20px; }}
.practical-item {{ background:#fff; border-radius:16px; padding:22px; display:flex; gap:16px; align-items:flex-start; box-shadow:0 2px 12px rgba(10,37,64,0.05); }}
.practical-icon {{ font-size:26px; flex-shrink:0; width:40px; text-align:center; }}
.practical-title {{ font-weight:700; font-size:15px; color:var(--navy); margin-bottom:6px; }}
.practical-desc {{ font-size:14px; color:#4b5563; line-height:1.68; margin:0; }}
/* Map section label */
.map-label-wrap {{ padding:40px 28px 0; text-align:center; }}
.map-label-wrap h2 {{ font-size:clamp(24px,4vw,40px); margin-bottom:10px; }}
.map-label-wrap p {{ font-size:16px; color:#5b6b7c; max-width:600px; margin:0 auto 32px; }}
/* Responsive */
@media(max-width:640px) {{
  .flight-meta {{ grid-template-columns:1fr 1fr; }}
  .country-tabs {{ gap:6px; }}
  .tab-btn {{ padding:8px 12px; font-size:12px; }}
  #ngor-map {{ height:320px; }}
  .step-item {{ flex-direction:column; gap:12px; }}
  .journey-stats {{ gap:24px; padding:40px 20px; }}
}}
</style>
</head>
<body>
<div id="scroll-progress"></div>
{build_nav(lang)}

<main>
  <!-- Hero -->
  <div class="gh-hero">
    <h1>{g("h1",lang)}</h1>
    <p>{g("subtitle",lang)}</p>
  </div>

  <!-- Quick stats -->
  <div class="journey-stats">
    {stats_html}
  </div>

  <!-- Map -->
  <section class="map-section">
    <div class="map-label-wrap">
      <span class="s-label">{g("map_title",lang)}</span>
      <h2 class="s-title">{g("map_title",lang)}</h2>
      <p>{g("map_sub",lang)}</p>
    </div>
    <div id="ngor-map"></div>
  </section>

  <!-- Steps -->
  <section class="steps-section">
    <div class="container">
      <div style="text-align:center;margin-bottom:48px">
        <span class="s-label">{g("steps_title",lang)}</span>
        <h2 class="s-title">{g("steps_title",lang)}</h2>
      </div>
      {steps_html}
    </div>
  </section>

  <!-- Flights -->
  <section class="flights-section">
    <div class="container">
      <div style="text-align:center;margin-bottom:40px">
        <span class="s-label">{g("flights_title",lang)}</span>
        <h2 class="s-title">{g("flights_title",lang)}</h2>
        <p class="s-sub" style="margin:0 auto">{g("select_country",lang)}</p>
      </div>
      <div class="country-tabs">{country_tabs}</div>
      <div id="flight-panels">{panels}</div>
    </div>
  </section>

  <!-- Practical Info -->
  <section class="practical-section">
    <div class="container">
      <div style="text-align:center;margin-bottom:48px">
        <span class="s-label">{g("practical_title",lang)}</span>
        <h2 class="s-title">{g("practical_title",lang)}</h2>
      </div>
      <div class="practical-grid">{practical_html}</div>
    </div>
  </section>

  <!-- Final CTA -->
  <div class="cta-band">
    <div class="container">
      <h2>{g("book_now",lang)}</h2>
      <p>{g("any_questions",lang)}</p>
      <div class="cta-btns">
        <a href="{pfx}/{SLUG[lang]["booking"]}/" class="btn btn-fire btn-lg">{g("book_now",lang)}</a>
        <a href="https://wa.me/221789257025" target="_blank" rel="noopener" class="btn btn-glass btn-lg"><span style="display:inline-flex">{WA_ICO}</span> WhatsApp</a>
      </div>
    </div>
  </div>
</main>

<!-- Footer (inline simplified) -->
<div class="footer-quotes" id="fq-quotes-block"><div class="footer-quotes-inner"><div class="fq-text-wrap" id="fq-wrap-{lang}"></div></div></div>
<footer>
  <div class="container">
    <div class="footer-bottom" style="justify-content:center;padding-top:24px">
      <p>© 2025 Ngor Surfcamp Teranga.</p>
      <div class="footer-flags" style="display:flex;gap:10px;margin-left:auto">
        {"".join([f'<a href="{LANG_PFX[l]}/{SLUG_GET_HERE[l]}/" style="opacity:0.45;display:inline-flex" title="{LANG_NAMES[l]}"><span style="width:22px;height:15px;display:inline-flex;border-radius:3px;overflow:hidden">{FLAG_SVG[l]}</span></a>' for l in LANGS])}
      </div>
    </div>
  </div>
</footer>

<!-- Leaflet JS -->
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" crossorigin=""></script>

<script>
/* ── Leaflet Map ─────────────────────────────────────── */
(function(){{
  // Coordinates
  var NGOR_ISLAND  = [14.7497, -17.5218];
  var NGOR_BEACH   = [14.7458, -17.5141];
  var DAKAR_CITY   = [14.7167, -17.4677];
  var DSS_AIRPORT  = [14.6708, -17.0726];

  var map = L.map('ngor-map', {{
    center: [14.7400, -17.4800],
    zoom: 12,
    zoomControl: true,
    attributionControl: true,
  }});

  // CARTO Positron-style light tiles (neutral, high readability — no API key)
  L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    subdomains: 'abcd',
    maxZoom: 20,
  }}).addTo(map);

  // Custom icon factory
  function makeIcon(color, emoji, size) {{
    return L.divIcon({{
      html: '<div style="width:' + size + 'px;height:' + size + 'px;border-radius:50%;background:' + color + ';border:3px solid #fff;display:flex;align-items:center;justify-content:center;font-size:' + Math.round(size*0.45) + 'px;box-shadow:0 2px 12px rgba(10,37,64,0.2)">' + emoji + '</div>',
      className: '',
      iconSize: [size, size],
      iconAnchor: [size/2, size/2],
      popupAnchor: [0, -(size/2+4)],
    }});
  }}

  // Surf camp marker (main — fire orange, large)
  L.marker(NGOR_ISLAND, {{ icon: makeIcon('#ff5a1f','🏄',52) }})
    .addTo(map)
    .bindPopup('<div style="font-family:Raleway,sans-serif;text-align:center;padding:6px 2px"><strong style="color:#0a2540;font-size:15px">Ngor Surfcamp Teranga</strong><br><span style="color:#6b7280;font-size:12px">Ngor Island, Dakar, Senegal</span><br><a href="https://wa.me/221789257025" target="_blank" style="color:#ff5a1f;font-weight:600;font-size:12px">📱 WhatsApp us</a></div>', {{ maxWidth:200 }})
    .openPopup();

  // Ngor beach marker
  L.marker(NGOR_BEACH, {{ icon: makeIcon('#334155','🚢',38) }})
    .addTo(map)
    .bindPopup('<div style="font-family:Raleway,sans-serif;padding:4px"><strong style="color:#0a2540">Ngor Beach</strong><br><span style="color:#6b7280;font-size:12px">Pirogue departure point</span></div>');

  // Dakar city
  L.marker(DAKAR_CITY, {{ icon: makeIcon('#475569','🏙',34) }})
    .addTo(map)
    .bindPopup('<div style="font-family:Raleway,sans-serif;padding:4px"><strong style="color:#0a2540">Dakar</strong><br><span style="color:#6b7280;font-size:12px">Capital city</span></div>');

  // Airport
  L.marker(DSS_AIRPORT, {{ icon: makeIcon('#64748b','✈️',38) }})
    .addTo(map)
    .bindPopup('<div style="font-family:Raleway,sans-serif;padding:4px"><strong style="color:#0a2540">Blaise Diagne Airport (DSS)</strong><br><span style="color:#6b7280;font-size:12px">~20min from Ngor Beach</span></div>');

  // Route line: Airport → Ngor Beach (muted on light basemap)
  L.polyline([DSS_AIRPORT, NGOR_BEACH], {{
    color: '#64748b', weight: 2.5, opacity: 0.45, dashArray: '8 6',
  }}).addTo(map);

  // Pirogue route: Ngor Beach → Ngor Island
  L.polyline([NGOR_BEACH, NGOR_ISLAND], {{
    color: '#475569', weight: 2.5, opacity: 0.55, dashArray: '6 5',
  }}).addTo(map);

  // Scale
  L.control.scale({{ imperial: false }}).addTo(map);
}})();

/* ── Country tabs ────────────────────────────────────── */
function switchCountry(key) {{
  document.querySelectorAll('.flight-panel').forEach(p => p.style.display = 'none');
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  var panel = document.querySelector('[data-country="' + key + '"].flight-panel');
  var btn   = document.querySelector('[data-country="' + key + '"].tab-btn');
  if(panel) panel.style.display = 'block';
  if(btn)   btn.classList.add('active');
}}

/* ── Animations ──────────────────────────────────────── */
function toggleLangDD(e) {{ e.stopPropagation(); document.getElementById('lang-dd').classList.toggle('open'); }}
document.addEventListener('click', e => {{ var d=document.getElementById('lang-dd'); if(d&&!d.contains(e.target)) d.classList.remove('open'); }});
function toggleMenu() {{ document.getElementById('nav-links').classList.toggle('open'); }}
document.addEventListener('DOMContentLoaded', () => {{
  const obs=new IntersectionObserver(es=>es.forEach(e=>{{if(e.isIntersecting)e.target.classList.add('up');}}),{{threshold:0.08}});
  document.querySelectorAll('.reveal').forEach(el=>obs.observe(el));
  const nav=document.getElementById('nav');
  if(nav) window.addEventListener('scroll',()=>nav.classList.toggle('scrolled',scrollY>30),{{passive:true}});
}});
</script>
</body>
</html>'''
    return html

# ════════════════════════════════════════════════════════════════
# WRITE ALL PAGES
# ════════════════════════════════════════════════════════════════
total = 0
for lang in LANGS:
    pfx  = LANG_PFX[lang]
    spfx = f"/{lang}" if lang!="en" else ""
    slug = SLUG_GET_HERE[lang]
    out_dir = f"{DEMO}{spfx}/{slug}"
    os.makedirs(out_dir, exist_ok=True)
    html = build_getting_here(lang)
    with open(f"{out_dir}/index.html","w") as f: f.write(html)
    total += 1
    print(f"  ✅ {lang}: /{spfx}/{slug}/  ({len(html)//1024}KB)")

print(f"\nBuilt {total} getting-here pages")

# ════════════════════════════════════════════════════════════════
# ADD HOMEPAGE TEASER BLOCK
# ════════════════════════════════════════════════════════════════
print("\n=== Adding homepage teaser block ===")

TEASER_CSS = """
/* ── Getting Here Teaser Block ──────────────────────── */
.gh-teaser {
  padding: 80px 0;
  background: linear-gradient(135deg, #f0f8ff, #e8f4ff);
  position: relative;
  overflow: hidden;
}
.gh-teaser::before {
  content: '';
  position: absolute; inset: 0;
  background: url("data:image/svg+xml,%3Csvg viewBox='0 0 400 300' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0 200 C100 160,200 180,300 160 C350 150,380 170,400 160 L400 300 L0 300Z' fill='rgba(10,37,64,0.03)'/%3E%3C/svg%3E") bottom;
  background-size: 100%; background-repeat: no-repeat;
  pointer-events: none;
}
.gh-teaser-inner {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 60px;
  align-items: center;
}
.gh-teaser-info { position: relative; z-index: 1; }
.gh-teaser-map-preview {
  border-radius: 20px;
  overflow: hidden;
  position: relative;
  height: 300px;
  box-shadow: 0 12px 40px rgba(10,37,64,0.1);
  background: #e8eaed;
  border: 1px solid rgba(10,37,64,0.08);
}
.gh-preview-map-el { width: 100%; height: 100%; min-height: 200px; z-index: 1; }
.gh-teaser-map-preview .leaflet-container { width:100% !important; height:100% !important; background:#e8eaed !important; }
.gh-teaser-map-preview .leaflet-control-attribution { font-size: 10px; background: rgba(255,255,255,0.85) !important; }
.gh-preview-marker-wrap { background: none !important; border: none !important; }
.gh-preview-marker {
  width: 34px; height: 34px; border-radius: 50%;
  background: var(--fire,#ff5a1f);
  border: 3px solid #fff;
  box-shadow: 0 2px 12px rgba(10,37,64,0.2);
}
.gh-teaser-map-iframe { display:block; width:100%; height:100%; min-height:200px; border:0; }
.gh-teaser-stats {
  display: flex;
  gap: 24px;
  margin: 24px 0 32px;
  flex-wrap: wrap;
}
.gh-ts {
  display: flex;
  flex-direction: column;
  padding: 14px 18px;
  background: white;
  border-radius: 12px;
  border: 1px solid rgba(10,37,64,0.08);
  box-shadow: 0 2px 10px rgba(10,37,64,0.06);
  min-width: 90px;
}
.gh-ts-n { font-family: var(--fh); font-size: 22px; font-weight: 900; color: var(--fire); }
.gh-ts-l { font-size: 11px; text-transform: uppercase; letter-spacing: 0.1em; color: var(--muted); margin-top: 2px; }
@media(max-width:768px){
  .gh-teaser-inner { grid-template-columns:1fr; gap:32px; }
  .gh-teaser-map-preview { height:220px; }
  .gh-teaser-stats { gap:12px; }
}
"""

_CSS_TEASER_SENTINEL = "/* ── Getting Here Teaser Block ──────────────────────── */"
_css_path = f"{DEMO}/assets/css/{ASSET_CSS_MAIN}"
with open(_css_path, "r", encoding="utf-8") as _cf:
    _css_existing = _cf.read()
if _CSS_TEASER_SENTINEL not in _css_existing:
    with open(_css_path, "a", encoding="utf-8") as f:
        f.write("\n" + TEASER_CSS)
    print(f"  appended Getting Here teaser CSS to {ASSET_CSS_MAIN}")
else:
    print(f"  Getting Here teaser CSS already in {ASSET_CSS_MAIN} — skip append")

TEASER_CONTENT = {
    "en":[("20min","airport"),("800m","from Dakar"),("5min","pirogue"),("<1€","to island")],
    "fr":[("20min","aéroport"),("800m","de Dakar"),("5min","pirogue"),("<1€","jusqu'à l'île")],
    "es":[("20min","aeropuerto"),("800m","de Dakar"),("5min","piragua"),("<1€","hasta la isla")],
    "it":[("20min","aeroporto"),("800m","da Dakar"),("5min","piroga"),("<1€","all'isola")],
    "de":[("20min","Flughafen"),("800m","von Dakar"),("5min","Piroge"),("<1€","zur Insel")],
}

WA_MINI = '<svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>'

teaser_patched = 0
for lang in LANGS:
    pfx  = LANG_PFX[lang]
    spfx = f"/{lang}" if lang!="en" else ""
    hp   = f"{DEMO}{spfx}/index.html"
    if not os.path.exists(hp): continue
    with open(hp, encoding="utf-8") as f: html = f.read()

    gh_slug = SLUG_GET_HERE[lang]
    stats   = TEASER_CONTENT[lang]
    gh_title = T["homepage_block"]["title"][lang]
    gh_sub   = T["homepage_block"]["sub"][lang]
    gh_cta   = T["homepage_block"]["cta"][lang]

    stat_html = "".join([f'<div class="gh-ts"><span class="gh-ts-n">{n}</span><span class="gh-ts-l">{l}</span></div>' for n,l in stats])
    arrow_ico = '<svg viewBox="0 0 20 20" fill="currentColor" width="18" height="18"><path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clip-rule="evenodd"/></svg>'
    map_title = {
        "en": "Ngor Island — map",
        "fr": "Île de Ngor — carte",
        "es": "Isla de Ngor — mapa",
        "it": "Isola di Ngor — mappa",
        "de": "Ngor-Insel — Karte",
    }[lang]

    if 'class="gh-teaser"' in html:
        if "gh-teaser-map-iframe" in html:
            html_iframe_fix, n_if = re.subn(
                r'<iframe class="gh-teaser-map-iframe"[^>]*></iframe>',
                f'<div class="gh-preview-map-el" id="gh-preview-map" role="img" aria-label="{map_title}"></div>',
                html,
                count=1,
            )
            if n_if:
                with open(hp, "w", encoding="utf-8") as f:
                    f.write(html_iframe_fix)
                print(f"  ✅ {lang}: teaser map → neutral Leaflet preview")
                teaser_patched += 1
        continue

    teaser_block = f'''
  <!-- Getting Here Teaser -->
  <section class="gh-teaser">
    <div class="container">
      <div class="gh-teaser-inner">
        <div class="gh-teaser-info reveal">
          <span class="s-label">{"How to Get There" if lang=="en" else "Comment se rendre sur place" if lang=="fr" else "Cómo llegar" if lang=="es" else "Come arrivare" if lang=="it" else "Anreise"}</span>
          <h2 class="s-title" style="margin-bottom:14px">{gh_title}</h2>
          <p class="s-sub" style="margin-bottom:0">{gh_sub}</p>
          <div class="gh-teaser-stats">{stat_html}</div>
          <div style="display:flex;gap:12px;flex-wrap:wrap">
            <a href="{pfx}/{gh_slug}/" class="btn btn-deep btn-lg" style="display:inline-flex;align-items:center;gap:10px">
              {arrow_ico} {gh_cta}
            </a>
            <a href="https://wa.me/221789257025" target="_blank" rel="noopener" class="btn btn-wa btn-sm" style="display:inline-flex;align-items:center;gap:7px">
              <span style="display:inline-flex">{WA_MINI}</span> WhatsApp
            </a>
          </div>
        </div>
        <div class="gh-teaser-map-preview">
          <div class="gh-preview-map-el" id="gh-preview-map" role="img" aria-label="{map_title}"></div>
        </div>
      </div>
    </div>
  </section>'''

    # Insert before CTA band
    html_new = html.replace('  <!-- CTA band -->', teaser_block + '\n\n  <!-- CTA band -->', 1)
    if html_new == html:
        # Try alternate
        CTA_RE = re.compile(r'(<div class="cta-band">)', re.DOTALL)
        html_new, n = CTA_RE.subn(teaser_block + '\n\n\\1', html, count=1)
        if n == 0:
            print(f"  ⚠️  {lang}: cta-band not found for teaser")
            continue

    with open(hp, "w", encoding="utf-8") as f:
        f.write(html_new)
    print(f"  ✅ {lang}: homepage teaser added")
    teaser_patched += 1

print(f"\nTeaser added to {teaser_patched}/5 homepages")
print("\n✅ Getting Here page complete!")
