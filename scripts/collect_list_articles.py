# -*- coding: utf-8 -*-
"""One-shot pipeline: sogou search -> resolve redirects -> fetch -> save HTML.

Usage: python collect_list_articles.py "<query>" <outdir> [max_pages]
Saves every fetched page into outdir with a slug filename and writes index.json.
"""
import sys
import os
import re
import json
import time
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from search_sogou import search  # noqa: E402
from fetch_pages import http_get, resolve_sogou  # noqa: E402


def slugify(s: str, maxlen: int = 40) -> str:
    s = re.sub(r"[^\w\u4e00-\u9fff-]+", "_", s)
    return s[:maxlen] or "page"


def main():
    query, outdir = sys.argv[1], sys.argv[2]
    max_pages = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    os.makedirs(outdir, exist_ok=True)
    index = []
    seen_domains = {}
    for r in search(query, pages=max_pages)[:15]:
        url = r["url"]
        if "sogou.com/web?" in url or "yuanbao" in url:
            continue
        try:
            real = resolve_sogou(url) if "sogou.com/link" in url else url
            if "sogou.com" in real:
                continue
            dom = urllib.parse.urlparse(real).netloc
            if seen_domains.get(dom, 0) >= 2:
                continue
            seen_domains[dom] = seen_domains.get(dom, 0) + 1
            page_url, html = http_get(real)
            fname = slugify(r["title"]) + ".html"
            with open(os.path.join(outdir, fname), "w", encoding="utf-8") as f:
                f.write(f"<!-- src: {page_url} -->\n" + html)
            text = re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>", " ", html, flags=re.S))
            cn = len(re.findall(r"[\u4e00-\u9fff]", text))
            hits = sum(x in text for x in ("许海峰", "杨倩", "全红婵", "李宁", "张怡宁", "孙颖莎"))
            index.append({"title": r["title"], "url": page_url, "file": fname, "cn_chars": cn, "champion_hits": hits})
            print(f"OK  {hits}hits cn={cn} {page_url[:80]} -> {fname}")
            time.sleep(1)
        except Exception as e:
            print(f"ERR {url[:60]} : {e}")
    with open(os.path.join(outdir, "index.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
