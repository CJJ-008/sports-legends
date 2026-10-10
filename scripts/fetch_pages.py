# -*- coding: utf-8 -*-
"""Resolve Sogou redirect links and probe candidate champion-list pages."""
import urllib.request
import re
import gzip
import io

UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
    "Accept-Encoding": "gzip",
}


def http_get(url: str, timeout: int = 30) -> tuple[str, str]:
    """Return (final_url, html)."""
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read()
        if resp.headers.get("Content-Encoding") == "gzip":
            data = gzip.GzipFile(fileobj=io.BytesIO(data)).read()
        return resp.geturl(), data.decode("utf-8", "ignore")


def resolve_sogou(link_url: str) -> str:
    """Follow a sogou /link?url=... redirect to the real target."""
    final, html = http_get(link_url)
    # sogou sometimes returns a JS-redirect page instead of HTTP redirect
    m = re.search(r'window\.location\.replace\("([^"]+)"\)', html)
    if m:
        return m.group(1)
    m = re.search(r'URL=\'?([^\'">]+)', html)
    if m:
        return m.group(1)
    return final


CANDIDATES = [
    ("国家体育总局 中国历届奥运冠军",
     "https://www.sogou.com/link?url=hedJjaC291NhmBVU00uX76mYohZbRUbyh4HEL4m2C1IObnk3vGSw-dU1JITsiCGazkbYeA79-gNs6xw-AJV4WvxD-"),
    ("搜狐 40年完整金牌榜冠军全记录",
     "https://www.sogou.com/link?url=hedJjaC291NpfjleHbQLM1nwmkVGvOnNp9Z8gTRfCxAUk7QGXvDxGPEgSus7bJtJ"),
    ("搜狐 中国40金 1984-2024十一届金牌全记录",
     "https://www.sogou.com/link?url=hedJjaC291Ok-E9WTygIKqZt6DizBOEjpLTgf4tdJ_iIyTeviZ5ZNfFrXf7c6ovK"),
    ("头条 中国历届奥运会完整金牌榜一览表",
     "https://www.sogou.com/link?url=hedJjaC291PD0T3DYzJqFDoBhFbePHvernilvTOuwmlpdShWbtDczfMJHWTYPGlTC3k2uQQ9IRY."),
    ("武汉生活网 金牌榜一览表",
     "https://www.sogou.com/link?url=DSOYnZeCC_rZFjElXO0INUlqAmoJJManyDVrIRn0coC_eANodtCjxg.."),
    ("中国历届奥运会冠军名单（汇总）",
     "https://www.sogou.com/link?url=DSOYnZeCC_rfvnSvg03SRo13OlJEagXi9Suqp7Ts6iywaWHpao41jBDl-6sO9oPPtsCnpVGpPpA."),
]

if __name__ == "__main__":
    for name, link in CANDIDATES:
        try:
            real = resolve_sogou(link)
            page_url, html = http_get(real)
            text = re.sub(r"<[^>]+>", " ", html)
            cn_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
            has_names = int("许海峰" in text) + int("杨倩" in text) + int("全红婵" in text) + int("李宁" in text)
            print(f"{name}\n  -> {page_url}\n     html={len(html)}B cn={cn_chars} 关键冠军名命中={has_names}")
        except Exception as e:
            print(f"{name}\n  -> ERROR {e}")
