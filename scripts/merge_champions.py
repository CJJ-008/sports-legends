# -*- coding: utf-8 -*-
"""Merge all champion sources into master dataset + athlete roster.

Output:
  data/staging/champions_master.json   — one record per gold medal
  data/staging/champions_athletes.json — one card per unique athlete
"""
import json
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_gov_pages import find_sport  # reuse sport keyword anchor

SUMMER_META = {
    23: ("1984", "洛杉矶奥运会", "美国洛杉矶"), 24: ("1988", "汉城奥运会", "韩国汉城"),
    25: ("1992", "巴塞罗那奥运会", "西班牙巴塞罗那"), 26: ("1996", "亚特兰大奥运会", "美国亚特兰大"),
    27: ("2000", "悉尼奥运会", "澳大利亚悉尼"), 28: ("2004", "雅典奥运会", "希腊雅典"),
    29: ("2008", "北京奥运会", "中国北京"), 30: ("2012", "伦敦奥运会", "英国伦敦"),
    31: ("2016", "里约奥运会", "巴西里约"), 32: ("2020", "东京奥运会", "日本东京"),
    33: ("2024", "巴黎奥运会", "法国巴黎"),
}
WINTER_META = {
    19: ("2002", "盐湖城冬奥会", "美国盐湖城"), 20: ("2006", "都灵冬奥会", "意大利都灵"),
    21: ("2010", "温哥华冬奥会", "加拿大温哥华"), 22: ("2014", "索契冬奥会", "俄罗斯索契"),
    23: ("2018", "平昌冬奥会", "韩国平昌"), 24: ("2022", "北京冬奥会", "中国北京"),
}

# doping-disqualified golds (2008 weightlifting) — kept but flagged
DQ_2008 = {"陈燮霞", "刘春红", "曹磊"}
# reallocated golds recorded by medal table but not in as-awarded lists
REALLOCATED = {
    ("2012", "伦敦奥运会", "切阳什姐", "田径", "女子20公里竞走"),
    ("2016", "里约奥运会", "吕小军", "举重", "男子81公斤级"),
}

# team golds whose member rosters are filled from public records
# (Paris rosters cross-checked against sohu/a/800113265 article text)
TEAM_ROSTERS = {
    ("2004", "女子排球"): "冯坤/杨昊/周苏红/刘亚男/张萍/王丽娜/张越红/赵蕊蕊/宋妮娜/李珊/陈静/张娴",
    ("2008", "男子体操团体"): "李小鹏/杨威/黄旭/肖钦/陈一冰/邹凯",
    ("2008", "女子体操团体"): "程菲/杨伊琳/江钰源/何可欣/李珊珊/邓琳琳",
    ("2008", "女子四人双桨"): "唐宾/金紫薇/奚爱华/张杨杨",
    ("2008", "乒乓球女子团体"): "张怡宁/王楠/郭跃",
    ("2008", "男子乒乓球团体"): "马琳/王皓/王励勤",
    ("2012", "男子团体"): "陈一冰/冯喆/郭伟阳/张成龙/邹凯",
    ("2012", "女子重剑团体"): "李娜/骆晓娟/孙玉洁/许安琪",
    ("2012", "女乒团体"): "李晓霞/丁宁/郭跃",
    ("2012", "男乒团体"): "马龙/王皓/张继科",
    ("2016", "女子排球"): "袁心玥/朱婷/杨方旭/龚翔宇/魏秋月/张常宁/张晓雅/惠若琪/徐云丽/丁霞/颜妮/刘晓彤",
    ("2024", "艺术体操团体全能"): "丁欣怡/郭崎琪/郝婷/黄张嘉洋/王澜静",
    ("2024", "花样游泳团体"): "常昊/冯雨/王柳懿/王芊懿/向玢璇/肖雁宁/王赐月/张雅怡",
    ("2024", "游泳男子4x100米混合泳接力"): "徐嘉余/覃海洋/孙家俊/潘展乐",
}
# official-page typos -> correct names
NAME_FIXES = {"邱键": "邱健"}
# unseparated multi-name strings from suliantuo source
JOIN_FIXES = {
    "许昕马龙樊振东": "许昕/马龙/樊振东",
    "陈梦孙颖莎王曼昱": "陈梦/孙颖莎/王曼昱",
}
# broken split from wuhan.com line-wrap: 刘浩/季博文 lost leading char
SPLIT_FIXES = {
    "浩/季博文": ("刘浩/季博文", None),
}


def norm_names(a: str) -> str:
    if not a:
        return ""
    a = a.replace("、", "/").replace("／", "/").strip("/")
    a = re.sub(r"/{2,}", "/", a)
    return a


def infer_sport(event: str, existing):
    if existing:
        return existing
    if not event:
        return None
    _, sp = find_sport(event)
    if sp:
        return sp
    # common suffix heuristics
    for kw, sp in [("铅球", "田径"), ("标枪", "田径"), ("铁饼", "田径"), ("竞走", "田径"),
                   ("跳远", "田径"), ("跳高", "田径"), ("110米栏", "田径"), ("栏", "田径"),
                   ("跳板", "跳水"), ("跳台", "跳水"), ("双人3米", "跳水"), ("双人10米", "跳水"),
                   ("鞍马", "体操"), ("吊环", "体操"), ("高低杠", "体操"), ("平衡木", "体操"),
                   ("双杠", "体操"), ("单杠", "体操"), ("自由体操", "体操"), ("蹦床", "蹦床"),
                   ("混合泳", "游泳"), ("蛙泳", "游泳"), ("蝶泳", "游泳"), ("仰泳", "游泳"),
                   ("自由泳", "游泳"), ("游泳", "游泳"), ("跆拳道", "跆拳道"), ("拳击", "拳击"),
                   ("女排", "排球"), ("排球", "排球"), ("体操团体", "体操"),
                   ("女双", "羽毛球"), ("女单", "羽毛球"), ("男双", "羽毛球"),
                   ("混双", "羽毛球"), ("羽毛球", "羽毛球"),
                   ("靶", "射击"), ("手枪", "射击"), ("步枪", "射击"), ("飞碟", "射击"),
                   ("气步枪", "射击"), ("皮划艇", "皮划艇"), ("划艇", "皮划艇"),
                   ("赛艇", "赛艇"), ("帆板", "帆船"), ("双人划", "皮划艇"), ("争先赛", "自行车"),
                   ("万米", "田径"), ("佩剑", "击剑"), ("花剑", "击剑"), ("重剑", "击剑"),
                   ("射箭", "射箭"), ("双桨", "赛艇"), ("镭迪尔", "帆船"), ("帆船", "帆船"),
                   ("乒乓", "乒乓球"), ("小轮车", "自由式小轮车"), ("空手道", "空手道")]:
        if kw in event:
            return sp
    return None


def main():
    medals = []

    gov = json.load(open("data/staging/gov_champions_raw.json", encoding="utf-8"))
    for page, data in gov.items():
        gno = {"1984洛杉矶_c21054304.html": 23, "1988汉城_c21054164.html": 24,
               "1992巴塞罗那_c21054236.html": 25, "1996亚特兰大_c21054130.html": 26,
               "2000悉尼_c21054181.html": 27, "2004雅典_c21054109.html": 28,
               "2008北京_c21054372.html": 29, "2012伦敦_c21054219.html": 30,
               "2016里约_c21054312.html": 31, "第19届冬奥_c21054201.html": 19}[page]
        season = "winter" if gno == 19 else "summer"
        meta = (WINTER_META if season == "winter" else SUMMER_META)[gno]
        for r in data["records"]:
            year, gname, city = meta
            athlete = norm_names(r.get("athlete") or "")
            members = r.get("team_members")
            ev = r.get("event") or ""
            medals.append({
                "year": year, "games": gname, "city": city, "season": season,
                "athlete": athlete,
                "team_members": [norm_names(m) for m in members] if members else None,
                "sport": infer_sport(ev, r.get("sport")),
                "event": ev, "date": r.get("date"), "score": r.get("score"),
                "source": "sport.gov.cn",
            })

    rem = json.load(open("data/staging/remaining_champions_raw.json", encoding="utf-8"))
    for r in rem["tokyo2020"]:
        medals.append({"year": "2020", "games": "东京奥运会", "city": "日本东京", "season": "summer",
                       "athlete": norm_names(r["athlete"]), "team_members": None,
                       "sport": infer_sport(r["event"], r.get("sport")), "event": r["event"],
                       "date": None, "score": None, "source": "suliantuo.net"})
    for r in rem["paris2024"]:
        medals.append({"year": "2024", "games": "巴黎奥运会", "city": "法国巴黎", "season": "summer",
                       "athlete": norm_names(r["athlete"]), "team_members": None,
                       "sport": infer_sport(r["event"], r.get("sport")), "event": r["event"],
                       "date": r.get("date"), "score": None, "source": "wuhan.com"})
    for r in rem["winter_2002_2018"] + rem["beijing2022"]:
        gno = r["games_no"]
        year, gname, city = WINTER_META[gno]
        medals.append({"year": year, "games": gname, "city": city, "season": "winter",
                       "athlete": norm_names(r["athlete"]), "team_members": None,
                       "sport": r.get("sport"), "event": r["event"], "date": r.get("date"),
                       "score": None, "source": "sohu/china.com.cn"})

    # flag doping DQ
    for m in medals:
        m["doping_dq"] = bool(m["year"] == "2008" and m["athlete"] in DQ_2008)
        if m["athlete"] in NAME_FIXES:
            m["athlete"] = NAME_FIXES[m["athlete"]]
        if m["athlete"] in JOIN_FIXES:
            m["athlete"] = JOIN_FIXES[m["athlete"]]
        if m["athlete"] in SPLIT_FIXES:
            m["athlete"], _ = SPLIT_FIXES[m["athlete"]]
            m["event"] = re.sub(r"\s*刘\s*$", "", m["event"])

    # fill team rosters
    for m in medals:
        key = (m["year"], m["event"])
        if key in TEAM_ROSTERS:
            roster = TEAM_ROSTERS[key]
            m["athlete"] = roster
            m["team_members"] = roster.split("/")
        # inherit sport from previous medal of same athlete (continuation rows)
    for i, m in enumerate(medals):
        if not m["sport"] and m["athlete"]:
            for j in range(i - 1, -1, -1):
                if medals[j]["athlete"] == m["athlete"] and medals[j]["sport"]:
                    m["sport"] = medals[j]["sport"]
                    break

    json.dump(medals, open("data/staging/champions_master.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    # ---- athlete roster ----
    roster = {}
    for m in medals:
        names = m["athlete"].split("/") if m["athlete"] else []
        if m.get("team_members"):
            names = m["team_members"]
        for n in names:
            n = n.strip()
            if not n:
                continue
            e = roster.setdefault(n, {"name": n, "gold_medals": 0, "sports": set(),
                                      "games": set(), "events": []})
            e["gold_medals"] += 1
            if m["sport"]:
                e["sports"].add(m["sport"])
            e["games"].add(f'{m["year"]}{m["games"][-3:]}')
            e["events"].append(f'{m["year"]} {m["event"]}')
    athletes = []
    for n, e in roster.items():
        athletes.append({"name": n, "gold_medals": e["gold_medals"],
                         "sports": sorted(e["sports"]), "games": sorted(e["games"]),
                         "events": e["events"]})
    athletes.sort(key=lambda x: (-x["gold_medals"], x["name"]))
    json.dump(athletes, open("data/staging/champions_athletes.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    print(f"medals: {len(medals)} | unique athletes: {len(athletes)}")
    print("top10:", [(a["name"], a["gold_medals"]) for a in athletes[:10]])
    nosport = [m for m in medals if not m["sport"]]
    print("medals without sport:", len(nosport), [m["event"] for m in nosport[:8]])


if __name__ == "__main__":
    main()
