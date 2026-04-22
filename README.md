# Ngor Surfcamp Teranga — Website

Production website for **Ngor Surfcamp Teranga**, a licensed surf camp on Ngor Island, Dakar, Senegal.

🌊 **Live:** [surf-camp-senegal.vercel.app](https://surf-camp-senegal.vercel.app)

---

## What this is

A fully custom **Python-generated static site** — no CMS, no framework, no template engine dependency.
Every HTML page is produced by `build.py`, a ~9 300-line Python script that handles content generation, i18n, SEO, image optimisation, and asset pipeline in a single deterministic build.

The site is served as pure static files on Vercel with edge middleware for geo-based language redirection.

---

## Numbers

| Metric | Value |
|--------|-------|
| Generated HTML pages | **354** |
| Languages | **9** (EN · FR · ES · IT · DE · NL · AR · PT · DA) |
| Blog articles (JSON source) | **135** |
| Published blog posts (EN) | **19** |
| Optimised WebP images tracked in git | **293** |
| Build scripts | **28** |
| Build time (full) | **~5 s** |

---

## Tech stack

| Layer | Technology |
|-------|-----------|
| Site generator | Python 3.11 — `build.py` (custom, no deps) |
| Hosting | Vercel (static output → `cloudflare-demo/`) |
| Edge middleware | Vercel Edge Functions — geo-redirect + Accept-Language |
| Booking API | Vercel Serverless Functions → Neon serverless Postgres |
| CSS | Single hand-crafted stylesheet (`ngor-surfcamp.css`, ~3.3 MB minified) |
| JavaScript | Vanilla JS (`ngor-surfcamp.js`) — no framework |
| Images | WebP, converted from PNG via Pillow at build time |
| CI/CD | GitHub Actions → `build.py` → Vercel |
| Content | JSON per language (`content/articles_v2/`) |
| Translations | JSON translation maps per UI string (`translations/`) |

---

## Architecture highlights

### Static site generator (`build.py`)
- Generates every page from Python string templates — full control over HTML output, zero runtime overhead
- Handles 9 languages with per-locale URL slugs, `hreflang` clusters, and `lang` attributes
- Injects structured data (JSON-LD: `LocalBusiness`, `WebSite`, `AggregateRating`, `BlogPosting`, `FAQPage`) on every relevant page
- Builds a responsive image gallery with filter tags, lightbox, and lazy loading
- Produces `sitemap.xml` shards + `sitemap-index.xml` (per-language, ~37 URLs each)
- Writes `robots.txt` with production/preview branch awareness

### Cache-busting system
Assets under `/assets/` are served with `Cache-Control: max-age=31536000, immutable`.
`build.py` computes an MD5 hash of `ngor-surfcamp.css` + `ngor-surfcamp.js` at **build time** and appends `?v=<8-char-hash>` to every reference in every HTML file.
This guarantees that a browser always fetches the latest CSS/JS on deploy, while keeping the 1-year cache for unchanged assets.

The `_final_cache_bust()` function at the end of `build.py` uses a regex (`\?v=[0-9a-f]+`) instead of `str.replace()` to handle any pre-existing hash length and avoid stray-character accumulation between build runs.

### Multilingual SEO
- Every page has a canonical URL, 9 `hreflang` alternate links, and `og:locale` meta
- Slug translation per language (e.g. `/fr/conditions-surf/`, `/de/surf-bedingungen/`)
- `AggregateRating` schema reflects real Google review score (4.7 / 54 reviews)
- Blog articles carry `BlogPosting` JSON-LD with `datePublished`, `author`, `image`, `wordCount`

### Edge middleware (`middleware.js`)
- Reads `Accept-Language` header and geo-IP (Vercel's `x-vercel-ip-country`)
- Redirects first-time visitors to their locale root (`/fr/`, `/de/`, etc.)
- Skips redirect for bots, static assets, and already-localised paths

### Back-office (`/admin/`)

A fully custom private back-office, accessible at `/admin/`, built without any third-party admin framework.

**Authentication — two-layer security:**
- Login screen with username/password validated against a `ADMIN_USERS` env var (bcrypt-hashed, stored as JSON on Vercel)
- All admin API endpoints protected by `Authorization: Bearer <token>` with `crypto.timingSafeEqual()` to prevent timing attacks
- GitHub OAuth flow (`api/auth.js` + `api/callback.js`) for Decap CMS integration
- All admin pages served with `noindex, nofollow` — invisible to search engines

**Bookings panel (`/admin/bookings.html`):**
- Fetches reservations from Neon Postgres via `GET /api/admin-bookings`
- Displays status, guest info, dates, room type, pricing
- CRUD operations on booking records

**Availability & pricing panel (`/admin/availability.html`):**
- Manager view of bed/room availability per date range
- Reads from `GET /api/availability` + writes via `POST /api/admin-availability`
- Real-time update of available capacity and rates

**User management panel (`/admin/users/`):**
- `GET /api/admin-users` — list users (passwords never exposed)
- `POST` — add user with hashed password
- `PUT` — change password
- `DELETE` — revoke access
- User store updated in-place via Vercel API (`VERCEL_TOKEN`) — no external user database needed

### Booking API
- Serverless function (`api/booking.js`) validates form, writes to Neon Postgres
- `api/_db.js` — shared Neon Postgres client (pooled, edge-compatible)
- Edge-side CORS + rate limiting headers in `vercel.json`
- Environment-gated: `DATABASE_URL` required only in production

### Performance
- All images converted to WebP at build time (Pillow)
- `loading="lazy"` + `decoding="async"` on every non-LCP image
- Chart.js deferred with `IntersectionObserver` on surf-conditions pages
- `<link rel="preload">` for Google Fonts
- Mobile-specific optimisations applied post-build across all 354 pages

---

## Project structure

```
├── build.py                    # Main static site generator (~9 300 lines)
├── surf_house_page.py          # Surf house page builder (imported by build.py)
├── requirements.txt            # Python dependencies
├── package.json                # npm scripts (build, deploy, check)
├── vercel.json                 # Vercel routing, redirects, headers (cache, CSP, HSTS)
├── middleware.js               # Vercel Edge — geo + Accept-Language redirect
├── version.json                # Build version (auto-bumped by CI)
├── CHANGELOG.md                # Deployment log (auto-updated by CI)
│
├── scripts/                    # 28 build + QA scripts
│   ├── build_blog.py           # Blog article HTML from JSON
│   ├── build_faq.py            # FAQ page builder
│   ├── build_gallery_enhanced.py
│   ├── pre_deploy_check.py     # Pre-deploy QA (canonical, hreflang, assets)
│   ├── site_assets.py          # Asset name constants (single source of truth)
│   └── ...
│
├── content/                    # Source content (JSON)
│   ├── articles_v2/            # 135 blog articles, one JSON per language
│   ├── island_guides/          # Island guide cards (JSON + locale data)
│   └── surf_history_2025.json  # Surf session history for the conditions page
│
├── translations/               # UI string maps per language
│
├── api/                        # Vercel serverless functions
│   ├── _db.js                  # Shared Neon Postgres client
│   ├── booking.js              # Public booking form → Neon Postgres
│   ├── availability.js         # Public availability query
│   ├── auth.js                 # GitHub OAuth initiation (Decap CMS)
│   ├── callback.js             # GitHub OAuth callback
│   ├── password-login.js       # Admin password auth
│   ├── token-relay.js          # Token relay for CMS
│   ├── admin-bookings.js       # Protected: read/manage bookings
│   ├── admin-availability.js   # Protected: update availability & pricing
│   └── admin-users.js          # Protected: full user CRUD via Vercel API
│
├── cloudflare-demo/admin/      # Private back-office (noindex)
│   ├── index.html              # Login + dashboard
│   ├── bookings.html           # Bookings management panel
│   ├── availability.html       # Availability & pricing panel
│   └── users/index.html        # User management panel
│
├── static/                     # Files copied verbatim into output
│
├── docs/                       # Internal documentation
│
├── .github/workflows/          # CI/CD pipelines
│
└── cloudflare-demo/            # Generated static output — committed to git, served by Vercel
    ├── assets/
    │   ├── css/ngor-surfcamp.css        # Hand-crafted stylesheet (cache-busted)
    │   ├── js/ngor-surfcamp.js          # Vanilla JS (cache-busted)
    │   └── images/                      # 293 WebP images + gallery manifest
    ├── index.html                        # EN home
    ├── {fr,es,it,de,nl,ar,pt,da}/      # 8 localised roots
    ├── blog/                            # EN blog
    ├── surf-house/, island/, surfing/   # Section pages
    ├── faq/, gallery/, booking/
    └── sitemap*.xml + robots.txt
```

---

## Quick start

```bash
# Python dependencies
pip install -r requirements.txt

# Build the site (outputs to cloudflare-demo/)
python3 build.py

# Pre-deploy quality check
python3 scripts/pre_deploy_check.py

# Full pipeline
npm run build && npm run check
```

---

## Deployment

Fully automated on every push to `main`:

1. `python3 build.py` — generates all HTML, injects schema, updates `?v=` hashes
2. `python3 scripts/pre_deploy_check.py --fix` — canonical/hreflang/asset QA
3. CI commits a version bump back to `main` (skipped from re-trigger via `[skip ci]`)
4. Vercel picks up the commit and serves the new `cloudflare-demo/` output

To deploy manually:

```bash
npm run deploy
```

---

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Content scripts only | GPT-4o article generation & translation |
| `VERCEL_TOKEN` | CI | Vercel deployment token |
| `VERCEL_ORG_ID` | CI | Vercel organisation ID |
| `VERCEL_PROJECT_ID` | CI | Vercel project ID |
| `DATABASE_URL` | API functions | Neon Postgres connection string |
| `PUBLIC_SITE_URL` | Optional | Override canonical origin (default: Vercel URL) |
| `ADMIN_API_KEY` | Admin API | Protects `/api/admin-bookings` |
| `ADMIN_USERS` | Admin API | JSON array of hashed user credentials |
| `ADMIN_USERS_API_TOKEN` | Admin API | Bearer token for `/api/admin-users` |

---

## Git & backup

The entire site — source code, build scripts, generated HTML, and all 293 WebP image assets — is committed to this repository.
Losing the local machine loses nothing: a `git clone` restores the full production-ready state including all assets.

Files intentionally excluded from git (see `.gitignore`):
- `content/images/` and `content/images_v2/` — raw PNG sources (large; processed WebPs are in git)
- `node_modules/`, `__pycache__/`
- `.env*` — secrets never committed
- `.DS_Store`, `*.pdf`, `retours/`
