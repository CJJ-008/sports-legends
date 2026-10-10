# -*- coding: utf-8 -*-
"""Prepare site assets: compress photos, copy JSON data into site/data/."""
import os
import json
import shutil
from PIL import Image

SRC_PHOTOS = "data/clean/photos"
SITE = "site"
OUT_PHOTOS = os.path.join(SITE, "data", "photos")
MAX_EDGE = 520
QUALITY = 82


def compress_all():
    os.makedirs(OUT_PHOTOS, exist_ok=True)
    total = 0
    n = 0
    for f in sorted(os.listdir(SRC_PHOTOS)):
        if not f.endswith(".jpg"):
            continue
        src = os.path.join(SRC_PHOTOS, f)
        dst = os.path.join(OUT_PHOTOS, f)
        if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
            total += os.path.getsize(dst)
            n += 1
            continue
        try:
            im = Image.open(src).convert("RGB")
            w, h = im.size
            scale = MAX_EDGE / max(w, h)
            if scale < 1:
                im = im.resize((round(w * scale), round(h * scale)), Image.LANCZOS)
            im.save(dst, "JPEG", quality=QUALITY, optimize=True, progressive=True)
            total += os.path.getsize(dst)
            n += 1
        except Exception as e:
            print("skip", f, e)
    print(f"photos: {n} files, {round(total/1e6, 1)} MB total")


def copy_json():
    os.makedirs(os.path.join(SITE, "data"), exist_ok=True)
    mapping = {
        "data/clean/olympics/games_list.json": "games_list.json",
        "data/clean/olympics/medal_tally_summer.json": "medal_tally_summer.json",
        "data/clean/olympics/medal_tally_winter.json": "medal_tally_winter.json",
        "data/clean/olympics/summer_medals_by_year.json": "summer_medals_by_year.json",
        "data/clean/olympics/summer_gold_trend.json": "summer_gold_trend.json",
        "data/clean/olympics/china_by_games.json": "china_by_games.json",
        "data/clean/olympics/china_gold_by_sport.json": "china_gold_by_sport.json",
        "data/clean/olympics/women_events_evolution.json": "women_events_evolution.json",
        "data/clean/olympics/athletes_per_games.json": "athletes_per_games.json",
        "data/clean/olympics/china_usa_gold.json": "china_usa_gold.json",
        "data/clean/legends.json": "legends.json",
        "data/clean/spirit_themes.json": "spirit_themes.json",
        "data/clean/nba/star_curves.json": "nba_curves.json",
        "data/clean/fifa/star_curves.json": "fifa_curves.json",
        "data/clean/spirit_match.json": "spirit_match.json",
        "data/staging/champions_master.json": "champions_master.json",
        "data/staging/champions_athletes.json": "champions_athletes.json",
        "data/clean/photos/manifest.json": "photos_manifest.json",
    }
    for src, dst in mapping.items():
        if os.path.exists(src):
            shutil.copy(src, os.path.join(SITE, "data", dst))
            print("copy", dst)
        else:
            print("MISSING", src)


if __name__ == "__main__":
    copy_json()
    compress_all()
