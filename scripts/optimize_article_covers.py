#!/usr/bin/env python3
"""Recompress blog cover + island guide hero WebPs when cwebp yields a smaller file.

Requires: cwebp (libwebp). Run from repo root:
  python3 scripts/optimize_article_covers.py

Targets: cloudflare-demo/assets/images/{slug}.webp for EN article slugs,
island guide bw-*.webp heroes, and author-*.webp avatars.
"""
from __future__ import annotations

import json
import os
import subprocess
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "cloudflare-demo", "assets", "images")
ART_DIR = os.path.join(ROOT, "content", "articles_v2", "en")

ISLAND_BW = [
    "bw-day-trips-from-ngor-island.webp",
    "bw-ngor-island-history-culture.webp",
    "bw-ngor-island-practical-travel-tips.webp",
    "bw-ngor-island-surf-right-left-guide.webp",
    "bw-ngor-island-things-to-do.webp",
]
AUTHORS = ["author-kofi-mensah.webp", "author-luca-ferretti.webp", "author-sophie-renard.webp"]


def article_slugs() -> list[str]:
    slugs = []
    for name in sorted(os.listdir(ART_DIR)):
        if not name.endswith(".json"):
            continue
        path = os.path.join(ART_DIR, name)
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            s = data.get("slug")
            if s:
                slugs.append(s)
        except (OSError, json.JSONDecodeError):
            continue
    return slugs


def try_replace(path: str, quality: int, min_ratio: float = 0.97) -> bool:
    if not os.path.isfile(path):
        return False
    old = os.path.getsize(path)
    fd, tmp = tempfile.mkstemp(suffix=".webp", dir=IMG)
    os.close(fd)
    try:
        r = subprocess.run(
            ["cwebp", "-q", str(quality), "-m", "6", "-mt", "-af", path, "-o", tmp],
            capture_output=True,
            timeout=180,
        )
        if r.returncode != 0:
            os.remove(tmp)
            return False
        new = os.path.getsize(tmp)
        if new < old * min_ratio:
            os.replace(tmp, path)
            print(f"{os.path.basename(path)}: {old} -> {new} bytes (q={quality})")
            return True
        os.remove(tmp)
        return False
    finally:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass


def main() -> None:
    targets: list[str] = []
    for s in article_slugs():
        targets.append(os.path.join(IMG, f"{s}.webp"))
    for n in ISLAND_BW + AUTHORS:
        targets.append(os.path.join(IMG, n))

    for p in targets:
        if not os.path.isfile(p):
            continue
        if not try_replace(p, 82, min_ratio=0.97):
            try_replace(p, 80, min_ratio=1.0)
            try_replace(p, 75, min_ratio=1.0)


if __name__ == "__main__":
    main()
