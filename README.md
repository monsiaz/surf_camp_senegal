# Ngor Surfcamp Teranga — Website

Static website for **Ngor Surfcamp Teranga**, a licensed surf camp on Ngor Island, Dakar, Senegal.

🌊 Live: [surf-camp-senegal.vercel.app](https://surf-camp-senegal.vercel.app)

---

## Tech stack

| Layer | Technology |
|-------|-----------|
| Site generation | Python 3.11 (`build.py`) |
| Hosting | Vercel (static output) |
| Database (bookings) | Neon serverless Postgres |
| Edge middleware | Vercel Edge (`middleware.js`) |
| Image format | WebP (optimised via Pillow) |
| CI/CD | GitHub Actions → Vercel |

---

## Supported languages

English · Français · Español · Italiano · Deutsch · Nederlands · العربية · Português · Dansk

---

## Quick start

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node dependencies
npm install

# Build the site (outputs to cloudflare-demo/)
python3 build.py

# Run quality check
python3 scripts/pre_deploy_check.py

# Full local build + check
npm run build && npm run check
```

---

## Project structure

```
├── build.py                    # Main static site generator
├── surf_house_page.py          # Surf house page module (loaded by build.py)
├── requirements.txt            # Python dependencies
├── package.json                # Node dependencies + npm scripts
├── vercel.json                 # Vercel routing + headers config
├── middleware.js               # Vercel edge middleware (geo-redirect)
├── version.json                # Current build version (updated by CI)
├── CHANGELOG.md                # Deployment changelog (updated by CI)
│
├── scripts/                    # Build + QA scripts (see scripts/README.md)
│   ├── build_blog.py
│   ├── build_faq.py
│   ├── build_gallery_enhanced.py
│   ├── pre_deploy_check.py
│   └── maintenance/            # One-off / infrequently-run scripts
│
├── content/                    # Source content
│   ├── articles_v2/            # Blog articles (JSON, per language)
│   ├── island_guides/          # Island guide cards (JSON)
│   ├── images/                 # Source images (PNGs for articles; gallery zips excluded from git)
│   └── surf_history_2025.json  # Surf session history data
│
├── translations/               # UI string translations per language
│
├── cloudflare-demo/            # Generated static output (committed; served by Vercel)
│   ├── assets/css/             # Stylesheet
│   ├── assets/js/              # JavaScript
│   └── assets/images/         # Optimised WebP images + gallery manifest
│
├── api/                        # Vercel serverless functions (bookings, auth)
├── static/                     # Static files copied verbatim
├── docs/                       # Internal documentation
└── .github/workflows/          # CI/CD pipelines
```

---

## Deployment

Deployment is fully automated via GitHub Actions on every push to `main`:

1. Python build (`build.py`)
2. Pre-deploy QA check (`scripts/pre_deploy_check.py --fix`)
3. Version bump committed back to repo
4. `vercel build --prod` + `vercel deploy --prebuilt --prod`

To deploy manually:

```bash
npm run deploy
```

---

## Content pipeline

See [`docs/CONTENT_PIPELINE.md`](docs/CONTENT_PIPELINE.md) for details on how articles, gallery images, and island guides are generated and translated.

---

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | For content scripts only | GPT-4o image labeling & translation |
| `VERCEL_TOKEN` | CI | Vercel deployment token |
| `VERCEL_ORG_ID` | CI | Vercel organisation ID |
| `VERCEL_PROJECT_ID` | CI | Vercel project ID |
| `DATABASE_URL` | API functions | Neon Postgres connection string |

---

## Version

Current version is tracked in [`version.json`](version.json) and updated automatically on each successful CI deploy.
