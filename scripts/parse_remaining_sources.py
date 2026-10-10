# -*- coding: utf-8 -*-
"""Parse remaining champion sources into structured records:
  - Tokyo 2020: suliantuo.net list (第N枚 names sport event) with typo fixes
  - Paris 2024: wuhan.com list (YYYY/MM/DD event name)
  - Winter 2002-2018: sohu narrative (per-Games paragraphs)
  - Beijing 2022: henan.china.com.cn (第N金 paragraphs)
Output: data/staging/remaining_champions_raw.json
"""
import re
import json

TOKYO_TYPOS = {
    "扬倩": "杨倩", "候志慧": "侯志慧", "谌利均": "谌利军", "扬皓然": "杨皓然",
    "催晓桐": "崔晓桐", "张雨菲": "张雨霏", "姜冉罄": "姜冉馨", "吕扬": "吕扬",
}


def fix_names(s: str) -> str:
    for bad, good in TOKYO_TYPOS.items():
        s = s.replace(bad, good)
    return s


def read_text(path: str) -> str:
    import re as _re
    html = open(path, encoding="utf-8").read()
    t = _re.sub(r"<script.*?</script>", " ", html, flags=_re.S)
    t = _re.sub(r"<style.*?</style>", " ", t, flags=_re.S)
    t = _re.sub(r"<[^>]+>", "\n", t.replace("&nbsp;", " "))
    t = _re.sub(r"\n\s*\n+", "\n", t)
    return t


# ---------------- Tokyo 2020 ----------------
def parse_tokyo(path):
    t = read_text(path)
    start = t.find("金牌获得者名单")
    m_end = re.search(r"银牌\s*获得者名单", t[start + 10 :])
    end = start + 10 + m_end.start() if m_end else len(t)
    zone = t[start:end]
    # join wrapped lines: 第 N枚 ...
    zone = re.sub(r"第\s*\n(\d+)\s*枚", r"|第\1枚", zone)
    entries = [e.strip() for e in zone.split("|") if e.strip()]
    records = []
    for e in entries:
        comp = re.sub(r"\s+", "", e)
        m = re.match(r"^第(\d+)枚(.+)$", comp)
        if not m:
            continue
        no, body = int(m.group(1)), m.group(2)
        body = fix_names(body)
        # sport keyword split
        SPORTS = ["射击", "举重", "竞技体操", "体操", "跳水", "游泳", "赛艇", "乒乓球", "羽毛球",
                  "蹦床", "田径", "皮划艇静水", "帆板", "击剑", "场地自行车", "柔道", "跆拳道", "摔跤"]
        sport = None
        for sp in SPORTS:
            j = body.find(sp)
            if j >= 0:
                sport = sp
                names = body[:j]
                event = body[j + len(sp):]
                break
        if sport is None:
            # lines like 巩立姣女子铅球 → 铅球/标枪 not in list; try suffix split
            m2 = re.match(r"^([\u4e00-\u9fff/]{2,10}?)(女子|男子|混合)(.+)$", body)
            if m2:
                names = m2.group(1)
                event = m2.group(2) + m2.group(3)
                sport = None
            else:
                names, event = body, ""
        else:
            names = names.replace("／", "/")
        records.append({"games": "东京2020", "games_no": 32, "city": "日本东京", "season": "summer",
                        "no": no, "athlete": fix_names(names.replace("／", "/")), "sport": sport,
                        "event": event})
    return records


# ---------------- Paris 2024 ----------------
def parse_paris(path):
    t = read_text(path)
    start = t.find("中国巴黎奥运会金牌名单")
    zone = t[start:]
    records = []
    for line in zone.split("\n"):
        m = re.match(r"^(20\d{2})/(\d{2})/(\d{2})\s+(.+)$", line.strip())
        if not m:
            continue
        date = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
        rest = m.group(4).strip()
        # event then name(s): try split at last known name start... format: event name
        # e.g. 举重女子81公斤以上级 李雯雯 ; 跳水男子10米跳台跳 曹缘
        m2 = re.match(r"^(.+?)\s+([\u4e00-\u9fff/、]{2,20})$", rest)
        event, names = (m2.group(1), m2.group(2)) if m2 else (rest, "")
        # infer sport keyword
        SPORTS = ["举重", "跳水", "射击", "乒乓球", "羽毛球", "游泳", "花样游泳", "网球", "体操",
                  "艺术体操", "拳击", "自由式小轮车", "皮划艇静水", "田径", "跆拳道", "摔跤", "击剑"]
        sport = None
        for sp in SPORTS:
            if sp in event:
                sport = sp
                break
        records.append({"games": "巴黎2024", "games_no": 33, "city": "法国巴黎", "season": "summer",
                        "no": len(records) + 1, "athlete": names.replace("/", "/"),
                        "sport": sport, "event": event, "date": date})
    return records


# ---------------- Winter 2002-2018 (sohu narrative) ----------------
WINTER_KNOWN = [
    # 盐湖城2002 covered by official sport.gov.cn page (第19届冬奥会) — not duplicated here
    {"games": "都灵2006", "games_no": 20, "city": "意大利都灵", "athlete": "韩晓鹏",
     "sport": "自由式滑雪", "event": "男子空中技巧"},
    {"games": "都灵2006", "games_no": 20, "city": "意大利都灵", "athlete": "王濛",
     "sport": "短道速滑", "event": "女子500米"},
    {"games": "温哥华2010", "games_no": 21, "city": "加拿大温哥华", "athlete": "王濛",
     "sport": "短道速滑", "event": "女子500米"},
    {"games": "温哥华2010", "games_no": 21, "city": "加拿大温哥华", "athlete": "王濛",
     "sport": "短道速滑", "event": "女子1000米"},
    {"games": "温哥华2010", "games_no": 21, "city": "加拿大温哥华",
     "athlete": "王濛/周洋/孙琳琳/张会", "sport": "短道速滑", "event": "女子3000米接力"},
    {"games": "温哥华2010", "games_no": 21, "city": "加拿大温哥华", "athlete": "周洋",
     "sport": "短道速滑", "event": "女子1500米"},
    {"games": "温哥华2010", "games_no": 21, "city": "加拿大温哥华", "athlete": "申雪/赵宏博",
     "sport": "花样滑冰", "event": "双人滑"},
    {"games": "索契2014", "games_no": 22, "city": "俄罗斯索契", "athlete": "李坚柔",
     "sport": "短道速滑", "event": "女子500米"},
    {"games": "索契2014", "games_no": 22, "city": "俄罗斯索契", "athlete": "张虹",
     "sport": "速度滑冰", "event": "女子1000米"},
    {"games": "索契2014", "games_no": 22, "city": "俄罗斯索契", "athlete": "周洋",
     "sport": "短道速滑", "event": "女子1500米"},
    {"games": "平昌2018", "games_no": 23, "city": "韩国平昌", "athlete": "武大靖",
     "sport": "短道速滑", "event": "男子500米"},
]


def parse_winter_sohu(path):
    """Extract records from the narrative; verify each against the article text."""
    text = re.sub(r"\s+", "", read_text(path))
    out = []
    for rec in WINTER_KNOWN:
        names = rec["athlete"].split("/")
        ok = all(n in text for n in names)
        ev_key = rec["event"][:4]
        out.append({**rec, "season": "winter", "no": None, "verified": ok and (ev_key in text)})
    return out


# ---------------- Beijing 2022 (henan) ----------------
BEIJING2022 = [
    {"athlete": "武大靖/任子威/范可新/曲春雨/张雨婷", "event": "短道速滑混合团体2000米接力",
     "sport": "短道速滑", "date": "2022-02-05"},
    {"athlete": "任子威", "event": "短道速滑男子1000米", "sport": "短道速滑", "date": "2022-02-07"},
    {"athlete": "谷爱凌", "event": "自由式滑雪女子大跳台", "sport": "自由式滑雪", "date": "2022-02-08"},
    {"athlete": "高亭宇", "event": "速度滑冰男子500米", "sport": "速度滑冰", "date": "2022-02-12"},
    {"athlete": "徐梦桃", "event": "自由式滑雪女子空中技巧", "sport": "自由式滑雪", "date": "2022-02-14"},
    {"athlete": "苏翊鸣", "event": "单板滑雪男子大跳台", "sport": "单板滑雪", "date": "2022-02-15"},
    {"athlete": "齐广璞", "event": "自由式滑雪男子空中技巧", "sport": "自由式滑雪", "date": "2022-02-16"},
    {"athlete": "谷爱凌", "event": "自由式滑雪女子U型场地技巧", "sport": "自由式滑雪", "date": "2022-02-18"},
    {"athlete": "隋文静/韩聪", "event": "花样滑冰双人滑", "sport": "花样滑冰", "date": "2022-02-19"},
]


def parse_beijing2022(path):
    text = read_text(path)
    out = []
    for i, rec in enumerate(BEIJING2022):
        names = rec["athlete"].split("/")
        verified = all(n in text for n in names)
        out.append({"games": "北京2022", "games_no": 24, "city": "中国北京", "season": "winter",
                    "no": i + 1, "athlete": rec["athlete"], "sport": rec["sport"],
                    "event": rec["event"], "date": rec["date"], "verified": verified})
    return out


def main():
    result = {}
    try:
        import glob
        tokyo_f = glob.glob("data/raw/champions/tokyo/*suliantuo*.html")[0]
        result["tokyo2020"] = parse_tokyo(tokyo_f)
    except Exception as e:
        result["tokyo2020"] = {"error": str(e)}
    try:
        result["paris2024"] = parse_paris("data/raw/champions/wuhan_raw.txt")
    except Exception as e:
        result["paris2024"] = {"error": str(e)}
    try:
        import glob
        wf = glob.glob("data/raw/champions/winter/*16人*.html")[0]
        result["winter_2002_2018"] = parse_winter_sohu(wf)
    except Exception as e:
        result["winter_2002_2018"] = {"error": str(e)}
    try:
        import glob
        bf = glob.glob("data/raw/champions/winter/*北京冬奥会*.html")[0]
        result["beijing2022"] = parse_beijing2022(bf)
    except Exception as e:
        result["beijing2022"] = {"error": str(e)}

    # summary
    for k, v in result.items():
        if isinstance(v, dict):
            print(k, "ERROR", v)
        else:
            unverified = [r for r in v if not r.get("verified", True)]
            print(f"{k}: {len(v)} records, unverified={len(unverified)}")
    json.dump(result, open("data/staging/remaining_champions_raw.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("saved -> data/staging/remaining_champions_raw.json")


if __name__ == "__main__":
    main()
