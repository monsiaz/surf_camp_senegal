# -*- coding: utf-8 -*-
"""One-off generator: writes content/island_guides/*.json — run: python3 scripts/gen_island_guides_json.py"""
import json
from pathlib import Path

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from island_guide_locale_data import _guide_things_to_do
from island_guide_locale_data_more import (
    _guide_day_trips,
    _guide_history,
    _guide_practical,
    _guide_surf,
)

ROOT = Path(__file__).resolve().parents[1] / "content" / "island_guides"


def dump(name, data):
    with open(ROOT / name, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    # --- 1 ---
    dump(
        "ngor-island-things-to-do.json",
        {
            "guide_id": "things-to-do",
            "hero_basename": "ngor-island-things-to-do",
            "date_published": "2026-03-27",
            "slugs": {
                "en": "ngor-island-things-to-do",
                "fr": "que-faire-ile-ngor",
                "es": "que-hacer-isla-ngor",
                "it": "cosa-fare-isola-ngor",
                "de": "ngor-insel-unternehmungen",
            },
            "locales": _guide_things_to_do(),
        },
    )
    dump(
        "ngor-island-history-culture.json",
        {
            "guide_id": "history-culture",
            "hero_basename": "ngor-island-history-culture",
            "date_published": "2026-03-27",
            "slugs": {
                "en": "ngor-island-history-culture",
                "fr": "histoire-culture-ile-ngor",
                "es": "historia-cultura-isla-ngor",
                "it": "storia-cultura-isola-ngor",
                "de": "geschichte-kultur-ngor-insel",
            },
            "locales": _guide_history(),
        },
    )
    dump(
        "day-trips-from-ngor-island.json",
        {
            "guide_id": "day-trips",
            "hero_basename": "day-trips-from-ngor-island",
            "date_published": "2026-03-27",
            "slugs": {
                "en": "day-trips-from-ngor-island",
                "fr": "excursions-depuis-ile-ngor",
                "es": "excursiones-desde-isla-ngor",
                "it": "escursioni-da-isola-ngor",
                "de": "tagesausfluege-von-ngor-insel",
            },
            "locales": _guide_day_trips(),
        },
    )
    dump(
        "ngor-island-surf-right-left-guide.json",
        {
            "guide_id": "surf-right-left",
            "hero_basename": "ngor-island-surf-right-left-guide",
            "date_published": "2026-03-27",
            "slugs": {
                "en": "ngor-island-surf-right-left-guide",
                "fr": "surf-ile-ngor-right-left",
                "es": "surf-isla-ngor-right-left",
                "it": "surf-isola-ngor-right-left",
                "de": "surfen-ngor-insel-right-left",
            },
            "locales": _guide_surf(),
        },
    )
    dump(
        "ngor-island-practical-travel-tips.json",
        {
            "guide_id": "practical-tips",
            "hero_basename": "ngor-island-practical-travel-tips",
            "date_published": "2026-03-27",
            "slugs": {
                "en": "ngor-island-practical-travel-tips",
                "fr": "conseils-pratiques-ile-ngor",
                "es": "consejos-practicos-isla-ngor",
                "it": "consigli-pratici-isola-ngor",
                "de": "praktische-tipps-ngor-insel",
            },
            "locales": _guide_practical(),
        },
    )
    print("Wrote 5 island guide JSON files to", ROOT)


if __name__ == "__main__":
    main()
