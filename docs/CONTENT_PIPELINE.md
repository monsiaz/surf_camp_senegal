# Pipeline contenu & déploiement (source de vérité → site statique)

## Où vivent les actions ?

| Étape | Où ça s’exécute |
|--------|------------------|
| **Édition CMS (Decap)** | Navigateur → API **GitHub** → **commit sur la branche `main`** du repo |
| **Build HTML** | **GitHub Actions** (`.github/workflows/deploy.yml`) : `python3 build.py` |
| **Hébergement** | **Vercel** reçoit le dossier **pré-généré** `cloudflare-demo/` (`vercel build --prod` puis `vercel deploy --prebuilt`) |

**Important :** ce n’est **pas** Vercel qui lance Python pour régénérer le site. Vercel sert surtout de CDN / edge pour les fichiers déjà construits dans l’Action. Le CMS ne parle **pas** à Vercel : il ne fait qu’écrire dans Git.

**Migrabilité :** tout est dans le repo (JSON + `build.py` + `scripts/`). Changer d’hébergeur statique = garder la même sortie `cloudflare-demo/` et un équivalent de l’étape « upload du dossier ».

## Source de vérité

1. **`content/articles_v2/{lang}/*.json`** — articles de blog (Markdown dans `content_markdown`). Une entrée par langue ; le slug d’URL doit rester aligné entre langues pour le hreflang.
2. **`content/pages/{lang}_{page}.json`** — textes marketing des pages générées par `build.py` pour **Surfing**, **Galerie**, **Surf House**, **Booking** (`scripts/site_page_json.py` fusionne ces champs dans les dictionnaires Python du build).
3. **`content/island_guides/*.json`** — guides île (corps Markdown + métadonnées).
4. **Code Python** (`build.py`, `surf_house_page.py`, etc.) — structure HTML, composants, textes par défaut si un JSON manque.

**Pas encore piloté par `content/pages/` :** home `index.html` (patchs successifs sur HTML existant), hub **Island** principal (généré autrement). Les JSON `en_homepage.json` etc. sont éditables dans le CMS pour préparer une future génération home depuis JSON.

## Build local (rapide)

```bash
cd /chemin/vers/SurfCampSenegal
PUBLIC_SITE_URL=https://votre-domaine.tld python3 build.py
```

Sortie : `cloudflare-demo/`. Pour itérer vite : ne modifier que JSON + relancer `build.py` (pas besoin de Node pour le site statique).

## Scripts principaux (dans `scripts/`)

| Fichier | Rôle |
|---------|------|
| `build_blog.py` | Régénère **toutes** les pages article + index blog à partir de `articles_v2` |
| `build_faq.py` | Régénère les pages **FAQ** (dont fusion NL/AR via `faq_ar_nl_merge.py`) |
| `site_page_json.py` | Charge / normalise `content/pages/*.json` pour le merge dans `build.py` |
| `island_md.py` | Markdown → HTML pour les guides île |

`build.py` appelle `build_faq.py` puis `build_blog.py` en fin de pipeline.

## CMS (Decap)

- Config : `static/admin/config.yml` (copié vers `cloudflare-demo/admin/` au build pour servir `/admin`).
- Collections : articles **en, fr, es, it, de, nl, ar** + collection dossier **`site_pages`** sur `content/pages/*.json`.
- **Nom de fichier** pour une nouvelle page marketing : convention `xx_nompage.json` (ex. `nl_homepage.json`) pour rester cohérent avec le chargeur (à créer manuellement si la langue n’existe pas encore).

## Fichiers déplacés

- `content/pages/all_pages_all_langs.json` et `hreflang_all_pages.html` → `content/archive/` (agrégats / snippets historiques, non utilisés par `build.py`).

## Optimisation

- **CI :** un seul `build.py` par push sur `main` (déjà le cas).
- **Cache :** assets versionnés via `ASSET_VERSION` dans `build.py` + en-têtes Vercel sur `/assets/*`.
- **Édition :** préférer des commits CMS petits et ciblés pour limiter les rebuilds complets ; le build reste linéaire mais rapide tant que les dépendances Python sont en cache sur l’Action.
