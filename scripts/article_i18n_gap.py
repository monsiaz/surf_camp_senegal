#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fill missing (or stale) article translations from English canonical JSON.

Source of truth: content/articles/en/*.json
Output:          content/articles_v2/{lang}/{slug}.json

The site build prefers articles_v2 when content_markdown is non-empty, so this is
the right place for long-form NL/AR (and any lang you add).

Environment:
  OPENAI_API_KEY  Required.
  OPENAI_MODEL    Optional. Default: gpt-4o (override e.g. to your GPT-5.x deployment name).

Examples:
  python3 scripts/article_i18n_gap.py --langs ar --dry-run
  python3 scripts/article_i18n_gap.py --langs ar --limit 1
  python3 scripts/article_i18n_gap.py --langs ar,nl --stale
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BASE not in sys.path:
    sys.path.insert(0, _BASE)

try:
    from openai import OpenAI
except ImportError:
    print("Install the OpenAI SDK: pip install openai", file=sys.stderr)
    raise SystemExit(1)

ARTICLES_EN = os.path.join(_BASE, "content", "articles", "en")
ARTICLES_V2 = os.path.join(_BASE, "content", "articles_v2")

LANG_LABEL = {
    "ar": "Modern Standard Arabic (MSA); keep proper nouns: Ngor, Dakar, Senegal, Teranga, ISA",
    "nl": "Dutch; natural surf-travel tone; keep proper nouns in original form where standard",
    "fr": "French",
    "es": "Spanish",
    "it": "Italian",
    "de": "German",
}


def _client() -> OpenAI:
    key = (os.environ.get("OPENAI_API_KEY") or "").strip()
    if not key:
        raise SystemExit("OPENAI_API_KEY is not set.")
    return OpenAI(api_key=key)


def _model() -> str:
    return (os.environ.get("OPENAI_MODEL") or "gpt-4o").strip()


def list_en_slugs() -> List[str]:
    if not os.path.isdir(ARTICLES_EN):
        return []
    out: List[str] = []
    for name in sorted(os.listdir(ARTICLES_EN)):
        if not name.endswith(".json") or name.startswith("_"):
            continue
        out.append(name[:-5])
    return out


def load_json(path: str) -> Optional[Dict[str, Any]]:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def needs_translation(
    en_path: str,
    out_path: str,
    *,
    stale: bool,
    min_md_chars: int,
    min_ratio: Optional[float],
) -> Tuple[bool, str]:
    en = load_json(en_path)
    if not en:
        return False, "skip (unreadable EN)"
    en_md = (en.get("content_markdown") or "").strip()
    if len(en_md) < 50:
        return False, "skip (EN markdown too short)"
    en_len = len(en_md)

    if not os.path.isfile(out_path):
        return True, "missing file"

    tgt = load_json(out_path)
    if not tgt:
        return True, "unreadable target"
    md = (tgt.get("content_markdown") or "").strip()
    if len(md) < min_md_chars:
        return True, f"short markdown ({len(md)} chars)"

    if min_ratio is not None and en_len > 0 and len(md) < min_ratio * en_len:
        return True, f"thin vs EN ({len(md)/en_len:.0%} < {min_ratio:.0%})"

    if stale:
        try:
            if os.path.getmtime(en_path) > os.path.getmtime(out_path):
                return True, "stale (EN newer than target)"
        except OSError:
            pass

    return False, "ok"


def translate_meta(client: OpenAI, title: str, meta: str, lang: str) -> Dict[str, str]:
    spec = LANG_LABEL.get(lang, f"the language with code {lang}")
    sys_prompt = f"""You translate surf-camp SEO fields into {spec}.
Return ONLY JSON: {{"title":"...","meta_description":"..."}}
Keep proper nouns (Ngor, Dakar, Senegal, Ngor Right, Ngor Left, Teranga)."""

    for attempt in range(3):
        try:
            r = client.chat.completions.create(
                model=_model(),
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": f'title: {json.dumps(title, ensure_ascii=False)}\nmeta_description: {json.dumps(meta, ensure_ascii=False)}'},
                ],
                max_completion_tokens=800,
                response_format={"type": "json_object"},
            )
            raw = (r.choices[0].message.content or "").strip()
            data = json.loads(raw)
            return {
                "title": str(data.get("title") or title),
                "meta_description": str(data.get("meta_description") or meta),
            }
        except Exception as e:
            print(f"      meta attempt {attempt + 1}: {e}")
            time.sleep(2)
    return {"title": title, "meta_description": meta}


def translate_markdown(client: OpenAI, md: str, lang: str) -> str:
    spec = LANG_LABEL.get(lang, f"language code {lang}")
    sys_prompt = f"""You are a professional translator for surf travel articles.
Translate the markdown into {spec}.
Rules:
- Preserve ALL markdown structure (# headings, lists, **bold**, links, FAQ formatting).
- Do not add or remove sections.
- Keep proper nouns where convention keeps them in Latin script (place names, brand)."""

    for attempt in range(3):
        try:
            r = client.chat.completions.create(
                model=_model(),
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": md},
                ],
                max_completion_tokens=16000,
            )
            out = (r.choices[0].message.content or "").strip()
            if out:
                return out
        except Exception as e:
            print(f"      body attempt {attempt + 1}: {e}")
            time.sleep(3)
    return ""


def build_article(en: Dict[str, Any], lang: str, title: str, meta: str, md: str) -> Dict[str, Any]:
    article = dict(en)
    article["lang"] = lang
    article["title"] = title
    article["meta_description"] = meta
    article["content_markdown"] = md
    article["slug"] = en.get("slug", "")
    article["hreflang_en"] = en.get("slug", "")
    return article


def main() -> None:
    ap = argparse.ArgumentParser(description="Translate missing EN articles to articles_v2/{lang}.")
    ap.add_argument("--langs", default="ar", help="Comma-separated ISO codes (default: ar)")
    ap.add_argument("--dry-run", action="store_true", help="List work only; no API calls")
    ap.add_argument("--stale", action="store_true", help="Retranslate when EN file is newer than target")
    ap.add_argument("--limit", type=int, default=0, help="Max articles per language (0 = no limit)")
    ap.add_argument("--min-md-chars", type=int, default=400, help="Treat shorter target markdown as missing")
    ap.add_argument(
        "--min-ratio",
        type=float,
        default=None,
        metavar="R",
        help="Retranslate if len(target_md) < R * len(en_md) (e.g. 0.35 catches partial translations)",
    )
    args = ap.parse_args()

    langs = [x.strip().lower() for x in args.langs.split(",") if x.strip()]
    if not langs:
        raise SystemExit("No languages given.")

    slugs = list_en_slugs()
    if not slugs:
        raise SystemExit(f"No EN articles under {ARTICLES_EN}")

    client: Optional[OpenAI] = None
    if not args.dry_run:
        client = _client()
        print(f"Model: {_model()!r}", flush=True)

    for lang in langs:
        out_dir = os.path.join(ARTICLES_V2, lang)
        os.makedirs(out_dir, exist_ok=True)
        todo: List[str] = []
        for slug in slugs:
            en_path = os.path.join(ARTICLES_EN, f"{slug}.json")
            out_path = os.path.join(out_dir, f"{slug}.json")
            need, reason = needs_translation(
                en_path,
                out_path,
                stale=args.stale,
                min_md_chars=args.min_md_chars,
                min_ratio=args.min_ratio,
            )
            if need:
                todo.append(slug)
        if args.limit:
            todo = todo[: args.limit]

        print(f"\n== {lang.upper()} — {len(todo)} file(s) to process ==", flush=True)
        for slug in todo:
            en_path = os.path.join(ARTICLES_EN, f"{slug}.json")
            out_path = os.path.join(out_dir, f"{slug}.json")
            _, reason = needs_translation(
                en_path,
                out_path,
                stale=args.stale,
                min_md_chars=args.min_md_chars,
                min_ratio=args.min_ratio,
            )
            print(f"  • {slug}.json ({reason})", flush=True)
            if args.dry_run:
                continue

            assert client is not None
            en = load_json(en_path)
            if not en:
                continue
            title = en.get("title") or ""
            meta = en.get("meta_description") or ""
            md_in = (en.get("content_markdown") or "").strip()

            meta_tr = translate_meta(client, title, meta, lang)
            md_out = translate_markdown(client, md_in, lang) if md_in else ""
            if not md_out:
                print("    ⚠️  empty body; skipping write", flush=True)
                continue

            article = build_article(en, lang, meta_tr["title"], meta_tr["meta_description"], md_out)
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(article, f, ensure_ascii=False, indent=2)
            print(f"    ✓ wrote {lang}/{slug}.json", flush=True)
            time.sleep(0.4)

    if args.dry_run:
        print("\nDry run only — set OPENAI_API_KEY and re-run without --dry-run to translate.", flush=True)


if __name__ == "__main__":
    main()
