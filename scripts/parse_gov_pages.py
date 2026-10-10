# -*- coding: utf-8 -*-
"""Parse official sport.gov.cn per-Games champion pages (4 layout variants).

Outputs one record per gold medal:
  {"games_no", "city", "games_name", "date"(opt), "athlete", "sport"(opt),
   "event", "score"(opt), "team_members"(opt)}
"""
import os
import re
import json
import glob

RAW = "data/raw/champions/gov/pages"
OUT = "data/staging/gov_champions_raw.json"

SPORTS = sorted(
    ["射击", "举重", "体操", "蹦床", "艺术体操", "乒乓球", "羽毛球", "跳水", "游泳", "花样游泳",
     "田径", "柔道", "跆拳道", "拳击", "摔跤", "击剑", "帆船", "帆板", "赛艇", "皮划艇", "排球",
     "篮球", "足球", "网球", "曲棍球", "自行车", "现代五项", "铁人三项", "举重", "柔道",
     "自由式滑雪", "单板滑雪", "短道速滑", "速度滑冰", "花样滑冰", "冰壶", "冰球", "越野滑雪",
     "高山滑雪", "冬季两项", "跳台滑雪", "北欧两项", "雪车", "雪橇", "钢架雪车"],
    key=len, reverse=True)

GAMES_NAME = {23: "洛杉矶奥运会", 24: "汉城奥运会", 25: "巴塞罗那奥运会", 26: "亚特兰大奥运会",
              27: "悉尼奥运会", 28: "雅典奥运会", 29: "北京奥运会", 30: "伦敦奥运会",
              31: "里约奥运会", 32: "东京奥运会", 33: "巴黎奥运会"}


def clean(s: str) -> str:
    return re.sub(r"[\s\u3000]+", "", s)


def find_sport(compacted: str):
    for sp in SPORTS:
        i = compacted.find(sp)
        if i >= 0:
            return i, sp
    return -1, None


def extract_zone(html: str) -> list[str]:
    t = re.sub(r"<script.*?</script>", " ", html, flags=re.S)
    t = re.sub(r"<style.*?</style>", " ", t, flags=re.S)
    t = re.sub(r"<[^>]+>", "\n", t.replace("&nbsp;", " ").replace("&gt;", ">").replace("&lt;", "<"))
    lines = [re.sub(r"[ \t\u3000]+", " ", l).strip() for l in t.split("\n")]
    return [l for l in lines if l]


# ---------- layout A: 1984-2000 column format ----------
def parse_a(lines):
    start = next(i for i, l in enumerate(lines) if "中国获金牌" in l)
    end = next((i for i in range(start, len(lines)) if "打印此页" in lines[i] or "版权所有" in lines[i]), len(lines))
    zone = lines[start + 1 : end]
    records, cur = [], None
    buf = ""
    for raw in zone + [""]:
        line = (buf + " " + raw).strip() if buf else raw
        if line.count("（") == 1 and line.count("）") == 0:
            buf = line  # team member list wraps to next line
            continue
        buf = ""
        comp = clean(line)
        if not comp or re.fullmatch(r"[\d.]+", comp):
            continue
        # team line: 男子团体体操（...） or 女子排球（...）
        m = re.match(r"^([\u4e00-\u9fff]+)（([^）]+)）$", comp)
        if m:
            event, members = m.group(1), [clean(x) for x in m.group(2).split("、") if clean(x)]
            _, sp = find_sport(event)
            records.append({"athlete": "/".join(members) if len(members) <= 6 else None,
                            "team_members": members if len(members) > 6 else None,
                            "sport": sp, "event": event})
            cur = None
            continue
        i, sp = find_sport(comp)
        if i > 0:
            records.append({"athlete": clean(comp[:i].replace("／", "/")),
                            "team_members": None, "sport": sp, "event": comp[i + len(sp):]})
            cur = None
            continue
        if cur and i < 0:
            records.append({"athlete": cur, "team_members": None, "sport": None, "event": comp})
            continue
        # line without sport keyword & no current athlete: probably team row without （)
        records.append({"athlete": None, "team_members": None, "sport": None, "event": comp})
    return records


# ---------- layout B: 2008 numbered list ----------
def parse_b(lines):
    start = next(i for i, l in enumerate(lines) if "金牌" in l and "枚" in l)
    end = next((i for i in range(start, len(lines)) if "打印此页" in lines[i] or "版权所有" in lines[i]), len(lines))
    zone = lines[start + 1 : end]
    records, cur, pending_names = [], None, []

    def flush(names, date, event, score):
        names = [clean(n) for n in names if clean(n)]
        athlete = "/".join(names) if names else None
        records.append({"athlete": athlete, "team_members": None, "sport": None,
                        "event": event, "date": date, "score": clean(score)})

    date, names, event, score = None, [], None, []
    for raw in zone:
        comp = clean(raw)
        if re.fullmatch(r"\d{1,3}", comp):  # entry number -> flush previous
            if event is not None:
                flush(names, date, event, " ".join(score))
            date, names, event, score = None, [], None, []
            cur_number = True
            continue
        m = re.fullmatch(r"(8|9)月(\d{1,2})日", comp)
        if m:
            date = comp
            continue
        if comp == "相关报道":
            continue
        looks_event = bool(re.search(r"男子|女子|混合|双人|团体|单打|双打|个人|公斤级|[0-9]+米|跳台|跳板|自由泳|仰泳|蛙泳|蝶泳|接力|公开级|女双|男双|女单|男单|混双", comp))
        looks_name = bool(re.fullmatch(r"[\u4e00-\u9fff/／、·]{2,24}", comp))
        if event is None:
            if looks_event:
                event = comp
                continue
            if looks_name:
                names.append(raw)
                continue
            # mixed line: name+event glued (e.g. 庞伟男子10米气手枪)
            m = re.match(r"^([\u4e00-\u9fff/·]{2,6})((?:男子|女子|混合|团体|双人).+)$", comp)
            if m:
                names.append(m.group(1))
                event = m.group(2)
            continue
        score.append(comp)
    if event is not None:
        flush(names, date, event, " ".join(score))
    return [r for r in records if r["event"]]


# ---------- layout C: 2012 table ----------
def parse_c(html):
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.S)
    records = []
    pending_name = None
    for row in rows:
        tds = [clean(re.sub(r"<[^>]+>", " ", td)) for td in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)]
        tds = [td for td in tds if td and td != "详细信息"]
        if not tds:
            continue
        joined = "|".join(tds)
        if re.fullmatch(r"\d{4}\.\d{2}\.\d{2}", tds[0]):
            if pending_name:
                records.append({"athlete": pending_name, "team_members": None, "sport": None,
                                "event": tds[1] if len(tds) > 1 else "", "date": tds[0].replace(".", "-")})
                pending_name = None
            continue
        if len(tds) >= 2 and not re.search(r"^\d{4}", tds[0]):
            pending_name = clean(tds[0].replace("／", "/"))
            # event may be same row or next (date row)
            ev = tds[1]
            if ev and not re.fullmatch(r"\d{4}\.\d{2}\.\d{2}", ev):
                records.append({"athlete": pending_name, "team_members": None, "sport": None,
                                "event": ev})
                pending_name = None
    return records


# ---------- layout D: 2016 name/event columns ----------
def parse_d(lines):
    start = next(i for i, l in enumerate(lines) if clean(l).startswith("金牌") and i + 1 < len(lines))
    end = len(lines)
    for i in range(start + 1, len(lines)):
        c = clean(lines[i])
        if c.startswith("银牌") or c.startswith("铜牌") or "打印此页" in c or "版权所有" in c:
            end = i
            break
    zone = lines[start + 1 : end]
    records = []
    for line in zone:
        comp = clean(line)
        if not comp or comp.startswith("金牌枚"):
            continue
        if re.fullmatch(r"[\d.]+", comp):
            continue
        m = re.match(r"^([\u4e00-\u9fff/]+?)(女子|男子|混合|场地|双人|公开|团体)", comp)
        if m and len(m.group(1)) <= 20:
            records.append({"athlete": m.group(1).replace("／", "/").replace("/", "/"),
                            "team_members": None, "sport": None, "event": comp[len(m.group(1)):]})
    return records


# ---------- layout E: 2004 numbered list, names split with / lines ----------
def parse_2004(lines):
    # sections: 金牌 ... 银牌 ... 铜牌 ; only gold section wanted
    start = end = None
    for i, l in enumerate(lines):
        c = clean(l)
        if c == "金牌" and start is None:
            start = i + 1
        elif c == "银牌" and start is not None:
            end = i
            break
    if start is None:
        return []
    end = end or len(lines)
    zone = lines[start:end]
    # split into entries by bare-number lines
    entries, cur = [], []
    for l in zone:
        c = l.strip()
        if re.fullmatch(r"\d{1,2}", c):
            if cur:
                entries.append(cur)
            cur = []
        else:
            cur.append(c)
    if cur:
        entries.append(cur)
    records = []
    for ent in entries:
        parts = [p for p in ent if p and p not in ("相关链接", "/") and not p.startswith("破") and "记录" not in p and "纪录" not in p]
        names, event, score = [], None, []
        for p in parts:
            comp = clean(p)
            looks_event = bool(re.search(r"男子|女子|混合|双人|团体|单打|双打|个人|公斤级|[0-9]+米|跳台|跳板|自由泳|蛙泳|蝶泳|接力|女双|男双|女单|男单|混双", comp))
            looks_name = bool(re.fullmatch(r"[\u4e00-\u9fff/／、·]{2,12}", comp))
            if looks_event and event is None:
                event = comp
            elif looks_name and event is None:
                names.append(comp)
            elif event is not None:
                score.append(comp)
            elif looks_name:
                names.append(comp)
        if event:
            records.append({"athlete": "/".join(names), "team_members": None,
                            "sport": None, "event": event,
                            "score": " ".join(score)[:60]})
    return records


LAYOUT = {
    "1984洛杉矶_c21054304.html": "A", "1988汉城_c21054164.html": "A",
    "1992巴塞罗那_c21054236.html": "A", "1996亚特兰大_c21054130.html": "A",
    "2000悉尼_c21054181.html": "A", "第19届冬奥_c21054201.html": "A",
    "2004雅典_c21054109.html": "E",
    "2008北京_c21054372.html": "B", "2012伦敦_c21054219.html": "C",
    "2016里约_c21054312.html": "D",
}


def main():
    out = {}
    for path in sorted(glob.glob(os.path.join(RAW, "*.html"))):
        base = os.path.basename(path)
        layout = LAYOUT.get(base)
        if not layout:
            continue
        html = open(path, encoding="utf-8").read()
        lines = extract_zone(html)
        if layout == "A":
            recs = parse_a(lines)
        elif layout == "B":
            recs = parse_b(lines)
        elif layout == "C":
            recs = parse_c(html)
        elif layout == "E":
            recs = parse_2004(lines)
        else:
            recs = parse_d(lines)
        out[base] = {"layout": layout, "records": recs}
        print(f"{base}: layout={layout} records={len(recs)}")
        for r in recs[:3]:
            print("   ", json.dumps(r, ensure_ascii=False)[:110])
    os.makedirs("data/staging", exist_ok=True)
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("saved ->", OUT)


if __name__ == "__main__":
    main()
