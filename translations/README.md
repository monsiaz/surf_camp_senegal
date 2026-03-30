# Translations

This directory contains the translation JSON files for all languages added after the initial launch.

## Files

| File | Description |
|------|-------------|
| `ui_nl_ar.json` | UI strings: SLUG, navigation, labels, buttons, blog categories |
| `pages_nl_ar.json` | Page copy: SURF_PAGE_COPY, SURF_HOUSE_PAGE, BOOKING_PAGE, PP, FAQ, Island, Footer |
| `blog_nl_ar.json` | Blog UI strings: 28_fix_blocks.py article page UI elements |

## Languages

| Code | Language | Country | hreflang | RTL |
|------|----------|---------|---------|-----|
| `nl` | Nederlands | Netherlands 🇳🇱 | `nl-NL` | No |
| `ar` | العربية | Morocco 🇲🇦 | `ar-MA` | Yes |

## Usage

These files are reference material. The actual translations are embedded directly in:
- `build.py` — main page builder
- `surf_house_page.py` — surf house content
- `scripts/build_blog.py` — blog/article pages (HTML depuis `content/articles_v2`)
- `scripts/build_faq.py` — FAQ pages (+ `scripts/faq_ar_nl_merge.py`)
- `content/articles_v2/nl/` — Dutch article content
- `content/articles_v2/ar/` — Arabic article content

## Re-generating

To add another language, use the translation scripts in `scripts/`:
```
python3 scripts/translate_new_langs.py  # UI strings
python3 scripts/translate_pages.py      # page copy
python3 scripts/translate_articles.py   # articles
```
