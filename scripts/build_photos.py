# -*- coding: utf-8 -*-
"""Photo pipeline: fetch portrait photos for athletes via Baidu image search.

- query "{name} {role_keyword}" -> top N results -> download portrait-ish image
- saves to data/clean/photos/{slug}.jpg, manifest data/clean/photos/manifest.json
- failures are recorded; frontend falls back to initial-card rendering

Usage: python build_photos.py [--limit N]
"""
import os
import re
import json
import time
import sys
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_pages import http_get  # noqa: E402

OUT = "data/clean/photos"
os.makedirs(OUT, exist_ok=True)
MANIFEST = os.path.join(OUT, "manifest.json")

UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Referer": "https://image.baidu.com/",
}


def search_images(query: str, n: int = 12):
    q = urllib.parse.quote(query)
    url = (f"https://image.baidu.com/search/acjson?tn=resultjson_com&ipn=rj"
           f"&word={q}&pn=0&rn={n}&ie=utf-8&z=9&face=1")
    try:
        _, t = http_get(url)
        d = json.loads(t)
    except Exception:
        return []
    out = []
    for x in d.get("data") or []:
        if not isinstance(x, dict):
            continue
        u = x.get("middleURL") or x.get("thumbURL") or x.get("hoverURL")
        if u:
            out.append({"url": u, "w": x.get("width"), "h": x.get("height")})
    return out


def download(url: str, path: str, timeout: int = 20) -> bool:
    try:
        req = urllib.request.Request(url, headers=UA)
        data = urllib.request.urlopen(req, timeout=timeout).read()
        if len(data) < 4000:  # too small = placeholder
            return False
        with open(path, "wb") as f:
            f.write(data)
        return True
    except Exception:
        return False


def portrait_score(w, h):
    try:
        w, h = int(w), int(h)
        if w < 120 or h < 160:
            return -1
        r = h / w
        if 1.1 <= r <= 2.2:  # portrait-ish
            return 2
        if 0.8 <= r < 1.1:  # square-ish
            return 1
        return 0
    except Exception:
        return 0


def slugify(name: str) -> str:
    s = re.sub(r"[^\w\u4e00-\u9fff]+", "_", name.strip())
    return s[:40] or "x"


def process(name: str, role: str, force: bool = False):
    manifest = {}
    if os.path.exists(MANIFEST):
        manifest = json.load(open(MANIFEST, encoding="utf-8"))
    if name in manifest and not force:
        return manifest[name]
    cands = search_images(f"{name} {role}")
    cands.sort(key=lambda c: portrait_score(c["w"], c["h"]), reverse=True)
    slug = slugify(name)
    got = None
    for c in cands[:5]:
        path = os.path.join(OUT, slug + ".jpg")
        if download(c["url"], path):
            got = {"file": f"photos/{slug}.jpg", "src": c["url"][:160]}
            break
    manifest[name] = got
    json.dump(manifest, open(MANIFEST, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return got


def load_athletes():
    athletes = json.load(open("data/staging/champions_athletes.json", encoding="utf-8"))
    result = [(a["name"], "奥运冠军") for a in athletes]
    return result


if __name__ == "__main__":
    limit = 400
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])
    people = load_athletes()[:limit]
    ok = fail = 0
    for i, (name, role) in enumerate(people):
        r = process(name, role)
        if r:
            ok += 1
        else:
            fail += 1
        if (i + 1) % 20 == 0:
            print(f"[{i+1}/{len(people)}] ok={ok} fail={fail}", flush=True)
        time.sleep(0.4)
    print(f"DONE ok={ok} fail={fail} -> {MANIFEST}")
