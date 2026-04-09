# Scripts

Build and content pipeline scripts for Ngor Surfcamp Teranga.

## Build pipeline (run by `build.py`)

| Script | Role |
|--------|------|
| `site_assets.py` | CSS/JS asset version constants used across the build |
| `site_page_json.py` | Page content JSON merging helpers |
| `island_md.py` | Island page markdown/HTML builder |
| `build_blog.py` | Blog index + article page generator (called via subprocess) |
| `build_faq.py` | FAQ page generator (called via subprocess) |
| `build_gallery_enhanced.py` | Gallery page generator with tag filter UI (called via subprocess) |
| `faq_ar_nl_merge.py` | Arabic & Dutch FAQ content merger, imported by `build_faq.py` |
| `env_utils.py` | Shared utility to load `OPENAI_API_KEY` from `.env` if not set |

## Quality assurance

| Script | Role |
|--------|------|
| `pre_deploy_check.py` | Pre-deploy QA gate — checks translations, CSS/JS integrity, critical content, SEO basics, and bumps `version.json` + `CHANGELOG.md`. Run with `--fix` in CI. |

## Maintenance / one-off scripts

See [`scripts/maintenance/README.md`](maintenance/README.md).
