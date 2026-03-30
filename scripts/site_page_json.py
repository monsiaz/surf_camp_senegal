# -*- coding: utf-8 -*-
"""Load marketing page JSON from content/pages/{lang}_{stem}.json and merge into build dicts.

CMS (Decap) edits these files in Git; build.py applies overrides on each run.
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional


def load_json(path: str) -> Optional[Dict[str, Any]]:
    if not path or not os.path.isfile(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def load_site_page_json(repo_root: str, lang: str, stem: str) -> Optional[Dict[str, Any]]:
    """stem examples: homepage, surfing, island, surf_house, gallery, book_online, faq"""
    path = os.path.join(repo_root, "content", "pages", f"{lang}_{stem}.json")
    return load_json(path)


def _norm_bullets(raw: Any) -> List[str]:
    if not raw:
        return []
    out: List[str] = []
    for x in raw:
        if isinstance(x, str):
            out.append(x)
        elif isinstance(x, dict):
            for v in x.values():
                if isinstance(v, str) and v.strip():
                    out.append(v.strip())
                    break
    return out


def section_paragraphs(j: Dict[str, Any], max_n: int) -> List[str]:
    """Concatenate section content (+ optional bullets) into plain paragraphs."""
    parts: List[str] = []
    for sec in (j.get("sections") or [])[:max_n]:
        if not isinstance(sec, dict):
            continue
        c = (sec.get("content") or "").strip()
        bullets = _norm_bullets(sec.get("bullets"))
        if c:
            parts.append(c)
        if bullets:
            parts.append(" ".join(f"• {b}" for b in bullets))
    return parts


def merge_surfing_copy(repo_root: str, lang: str, base: Dict[str, Any]) -> Dict[str, Any]:
    j = load_site_page_json(repo_root, lang, "surfing")
    if not j:
        return base
    out = dict(base)
    if j.get("title_tag"):
        out["title"] = j["title_tag"]
    if j.get("meta_description"):
        out["meta"] = j["meta_description"]
    if j.get("h1"):
        out["h1"] = j["h1"]
    if j.get("hero_subtitle"):
        out["tag"] = j["hero_subtitle"]
    if j.get("intro"):
        out["p1"] = j["intro"]
    paras = section_paragraphs(j, 6)
    for i, k in enumerate(("p2", "p3", "p4", "p5")):
        if i < len(paras):
            out[k] = paras[i]
    return out


def merge_gallery_copy(repo_root: str, lang: str, base: Dict[str, Any]) -> Dict[str, Any]:
    j = load_site_page_json(repo_root, lang, "gallery")
    if not j:
        return base
    out = dict(base)
    if j.get("title_tag"):
        out["title"] = j["title_tag"]
    if j.get("meta_description"):
        out["meta"] = j["meta_description"]
    if j.get("h1"):
        out["h1"] = j["h1"]
    if j.get("hero_subtitle"):
        out["sub"] = j["hero_subtitle"]
    if j.get("intro"):
        out["lead"] = j["intro"]
    if j.get("cta_heading"):
        out["cta_h2"] = j["cta_heading"]
    if j.get("cta_button"):
        out["book"] = j["cta_button"]
    return out


def merge_surf_house_copy(repo_root: str, lang: str, base: Dict[str, Any]) -> Dict[str, Any]:
    j = load_site_page_json(repo_root, lang, "surf_house")
    if not j:
        return base
    out = dict(base)
    if j.get("title_tag"):
        out["title"] = j["title_tag"]
    if j.get("meta_description"):
        out["meta"] = j["meta_description"]
    if j.get("h1"):
        out["h1"] = j["h1"]
    if j.get("hero_subtitle"):
        out["tagline"] = j["hero_subtitle"]
    if j.get("intro"):
        out["p1"] = j["intro"]
    paras = section_paragraphs(j, 5)
    for i, k in enumerate(("p2", "p3", "p4")):
        if i < len(paras):
            out[k] = paras[i]
    if j.get("cta_heading"):
        out["cta_h2"] = j["cta_heading"]
    if j.get("cta_text"):
        out["cta_p"] = j["cta_text"]
    if j.get("cta_button"):
        out["book"] = j["cta_button"]
    return out


def merge_booking_copy(repo_root: str, lang: str, T: Dict[str, Dict[str, str]]) -> Dict[str, Dict[str, str]]:
    j = load_site_page_json(repo_root, lang, "book_online")
    if not j:
        return T
    out = {k: dict(v) for k, v in T.items()}
    if j.get("title_tag") and "title" in out:
        out["title"][lang] = j["title_tag"]
    if j.get("meta_description") and "meta" in out:
        out["meta"][lang] = j["meta_description"]
    if j.get("h1") and "h1" in out:
        out["h1"][lang] = j["h1"]
    if j.get("hero_subtitle") and "sub" in out:
        out["sub"][lang] = j["hero_subtitle"]
    if j.get("intro") and "sub2" in out:
        out["sub2"][lang] = j["intro"]
    if j.get("cta_heading") and "h2" in out:
        out["h2"][lang] = j["cta_heading"]
    return out
