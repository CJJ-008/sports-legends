# -*- coding: utf-8 -*-
"""Sogou web search scraper — returns result titles + redirect links."""
import urllib.request
import urllib.parse
import re
import sys

UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9",
}


def http_get(url: str, timeout: int = 25) -> str:
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "ignore")


def strip_tags(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s).strip()


def search(query: str, pages: int = 1):
    results = []
    for page in range(1, pages + 1):
        q = urllib.parse.quote(query)
        url = f"https://www.sogou.com/web?query={q}&page={page}"
        html = http_get(url)
        # each result block: <h3 class="vr-title"> <a ... href="..." ...>title</a>
        for m in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', html, re.S):
            href, title = m.group(1), strip_tags(m.group(2))
            if not title or len(title) < 6:
                continue
            if href.startswith("/link?url="):
                href = "https://www.sogou.com" + href
            elif not href.startswith("http"):
                continue
            results.append({"title": title, "url": href})
    # dedupe keep order
    seen, uniq = set(), []
    for r in results:
        if r["url"] not in seen:
            seen.add(r["url"])
            uniq.append(r)
    return uniq


if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "中国奥运冠军名单"
    for r in search(query)[:20]:
        print(r["title"], "|", r["url"][:120])
