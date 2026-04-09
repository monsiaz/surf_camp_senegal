# Maintenance Scripts

One-off and infrequently-run scripts used during content migrations, image processing, and data generation. These are **not** part of the automated build pipeline.

Run all scripts from the **repo root**:

```bash
python3 scripts/maintenance/<script>.py
```

---

## Image pipeline

| Script | Purpose |
|--------|---------|
| `process_images.py` | Process source image archives → optimised WebP gallery. Requires `OPENAI_API_KEY` and extracted zip files in `content/images/extracted/`. |
| `relabel_gallery.py` | Re-run GPT-4o Vision labeling on existing gallery images to refresh tags/captions in `manifest.json`. |

## Content generation

| Script | Purpose |
|--------|---------|
| `translate_new_langs.py` | Translate all EN articles to Portuguese (`pt`) and Danish (`da`) using GPT-4o (20 workers). Requires `OPENAI_API_KEY`. |
| `fix_article_completeness.py` | Fix incomplete or stub articles in `content/articles_v2/`. |
| `fix_remaining_articles.py` | Secondary pass to fill in any remaining article gaps. |
| `gen_island_guides_json.py` | Regenerate `content/island_guides/*.json` from locale data files. |
| `article_i18n_gap.py` | Audit which articles are missing translations for a given language. |

## One-off HTML patches (superseded)

These patched the generated HTML directly and are now superseded by the main `build.py` pipeline. Kept for reference.

| Script | What it patched |
|--------|----------------|
| `35_footer_quotes.py` | Footer quotes/attributions |
| `36_fix_hero_reviews.py` | Hero section review stars |
| `37_getting_here.py` | "Getting here" page generation |
| `capture_cmp_popup.py` | CMP/cookie popup screenshot capture |

## Data files (used by gen_island_guides_json.py)

- `island_guide_locale_data.py` — "Things to do" guide content
- `island_guide_locale_data_more.py` — Day trips, history, practical info, surf guide content
