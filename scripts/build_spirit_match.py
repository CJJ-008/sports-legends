# -*- coding: utf-8 -*-
"""Build the 'Spirit Match' (精神同类) dataset.

- Person profiles: champions (from medal records) + legends (curated stories)
- Six spirit dimensions scored from data rules (0-100):
    persistence 坚韧持久 / dominance 巅峰统治 / teamwork 团队协作 /
    versatility 多面开花 / legacy 时代传奇 / breakthrough 突破先锋
- Embeddings via sentence-transformers (paraphrase-multilingual-MiniLM-L12-v2)

Output: data/clean/spirit_match.json
"""
import json
import os
from collections import defaultdict

import numpy as np

os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
from sentence_transformers import SentenceTransformer  # noqa: E402

TEAM_EVENT_HINTS = ["团体", "接力", "双人", "双人滑", "集体", "团体体操", "混合"]

# known "first gold" breakthrough people (零的突破)
BREAKTHROUGH = {"许海峰", "杨扬", "刘翔", "郑钦文", "苏翊鸣", "谷爱凌", "高亭宇",
                "张娟娟", "仲满", "雷声", "韩晓鹏", "穆罕默德·阿里", "杰西·欧文斯",
                "娜迪亚·科马内奇", "埃鲁德·基普乔格"}

# legends -> spirit dims override (from curated stories)
LEGEND_DIMS = {
    "尤塞恩·博尔特": dict(persistence=70, dominance=100, teamwork=40, versatility=45, legacy=95, breakthrough=95),
    "迈克尔·菲尔普斯": dict(persistence=95, dominance=100, teamwork=70, versatility=70, legacy=95, breakthrough=60),
    "穆罕默德·阿里": dict(persistence=85, dominance=90, teamwork=30, versatility=40, legacy=100, breakthrough=95),
    "迈克尔·乔丹": dict(persistence=85, dominance=100, teamwork=75, versatility=50, legacy=100, breakthrough=70),
    "利昂内尔·梅西": dict(persistence=90, dominance=95, teamwork=70, versatility=60, legacy=95, breakthrough=65),
    "克里斯蒂亚诺·罗纳尔多": dict(persistence=100, dominance=95, teamwork=65, versatility=65, legacy=95, breakthrough=60),
    "贝利": dict(persistence=75, dominance=95, teamwork=70, versatility=55, legacy=95, breakthrough=85),
    "迭戈·马拉多纳": dict(persistence=70, dominance=90, teamwork=55, versatility=50, legacy=90, breakthrough=80),
    "罗杰·费德勒": dict(persistence=90, dominance=90, teamwork=30, versatility=50, legacy=95, breakthrough=55),
    "拉斐尔·纳达尔": dict(persistence=100, dominance=90, teamwork=35, versatility=55, legacy=95, breakthrough=60),
    "诺瓦克·德约科维奇": dict(persistence=95, dominance=95, teamwork=30, versatility=55, legacy=95, breakthrough=60),
    "埃鲁德·基普乔格": dict(persistence=100, dominance=85, teamwork=40, versatility=40, legacy=90, breakthrough=100),
    "卡尔·刘易斯": dict(persistence=95, dominance=90, teamwork=50, versatility=75, legacy=90, breakthrough=70),
    "杰西·欧文斯": dict(persistence=70, dominance=85, teamwork=45, versatility=70, legacy=100, breakthrough=100),
    "娜迪亚·科马内奇": dict(persistence=60, dominance=90, teamwork=40, versatility=55, legacy=85, breakthrough=100),
    "谢尔盖·布勃卡": dict(persistence=90, dominance=90, teamwork=25, versatility=40, legacy=85, breakthrough=95),
    "伊莲娜·伊辛巴耶娃": dict(persistence=85, dominance=90, teamwork=25, versatility=40, legacy=85, breakthrough=90),
    "伊恩·索普": dict(persistence=70, dominance=85, teamwork=65, versatility=55, legacy=75, breakthrough=55),
    "海勒·格布雷西拉西耶": dict(persistence=95, dominance=85, teamwork=35, versatility=45, legacy=85, breakthrough=85),
    "泰格·伍兹": dict(persistence=90, dominance=90, teamwork=25, versatility=40, legacy=90, breakthrough=75),
    "迈克尔·舒马赫": dict(persistence=95, dominance=95, teamwork=70, versatility=35, legacy=90, breakthrough=55),
    "埃尔顿·塞纳": dict(persistence=85, dominance=90, teamwork=60, versatility=35, legacy=90, breakthrough=65),
    "罗纳尔多": dict(persistence=75, dominance=85, teamwork=55, versatility=50, legacy=85, breakthrough=60),
    "齐内丁·齐达内": dict(persistence=75, dominance=85, teamwork=70, versatility=50, legacy=85, breakthrough=60),
    "弗朗茨·贝肯鲍尔": dict(persistence=75, dominance=85, teamwork=80, versatility=60, legacy=90, breakthrough=85),
    "约翰·克鲁伊夫": dict(persistence=70, dominance=85, teamwork=75, versatility=60, legacy=95, breakthrough=90),
    "塞雷娜·威廉姆斯": dict(persistence=95, dominance=100, teamwork=30, versatility=45, legacy=95, breakthrough=70),
    "韦恩·格雷茨基": dict(persistence=90, dominance=95, teamwork=70, versatility=50, legacy=95, breakthrough=65),
    "科比·布莱恩特": dict(persistence=100, dominance=90, teamwork=70, versatility=50, legacy=95, breakthrough=55),
    "勒布朗·詹姆斯": dict(persistence=100, dominance=95, teamwork=75, versatility=60, legacy=95, breakthrough=60),
    "斯蒂芬·库里": dict(persistence=90, dominance=90, teamwork=75, versatility=50, legacy=90, breakthrough=95),
    "郑钦文": dict(persistence=80, dominance=70, teamwork=35, versatility=45, legacy=60, breakthrough=100),
}

QUALITIES = [
    {"id": "persistence", "label": "坚韧持久", "phrase": "十年如一日的坚持，用漫长岁月打磨自己，永不言弃"},
    {"id": "dominance", "label": "巅峰统治", "phrase": "在自己领域建立统治力，金牌收割机，无可争议的最强者"},
    {"id": "teamwork", "label": "团队协作", "phrase": "把后背交给队友，团队协作与集体荣誉高于一切"},
    {"id": "versatility", "label": "多面开花", "phrase": "多线作战样样精通，全面型选手"},
    {"id": "legacy", "label": "时代传奇", "phrase": "跨越时代的影响力，体育史册的书写者"},
    {"id": "breakthrough", "label": "突破先锋", "phrase": "打破偏见与纪录，完成零的突破，人类没有极限"},
    {"id": "prodigy", "label": "少年成名", "phrase": "年少成名，天才少年的横空出世"},
    {"id": "comeback", "label": "王者归来", "phrase": "从重伤与低谷中归来，再次登顶"},
]


def champion_profiles():
    medals = json.load(open("data/staging/champions_master.json", encoding="utf-8"))
    roster = json.load(open("data/staging/champions_athletes.json", encoding="utf-8"))
    photos = {}
    if os.path.exists("data/clean/photos/manifest.json"):
        photos = json.load(open("data/clean/photos/manifest.json", encoding="utf-8"))

    per_person_events = defaultdict(list)
    for m in medals:
        names = m["athlete"].split("/") if m["athlete"] else []
        if m.get("team_members"):
            names = m["team_members"]
        for n in names:
            n = n.strip()
            if n:
                per_person_events[n].append(m)

    people = []
    for a in roster:
        name = a["name"]
        ms = per_person_events.get(name, [])
        if not ms:
            continue
        games = sorted({(m["year"], m["games"], m["season"]) for m in ms})
        events = sorted({m["event"] for m in ms})
        sports = sorted({m["sport"] for m in ms if m["sport"]})
        team_golds = sum(1 for m in ms if any(h in m["event"] for h in TEAM_EVENT_HINTS))
        years = [int(g[0]) for g in games]
        span = (max(years) - min(years)) if len(years) > 1 else 0
        n_golds = a["gold_medals"]
        max_g = 6
        dims = {
            "persistence": min(100, round(span / 12 * 100)),
            "dominance": min(100, round(n_golds / max_g * 100)),
            "teamwork": min(100, round(team_golds / max(n_golds, 1) * 100)) if team_golds else 15,
            "versatility": min(100, round(len(sports) / 2 * 100)),
            "legacy": min(100, round(len(games) / 4 * 100)),
            "breakthrough": 100 if name in BREAKTHROUGH else 30,
        }
        # prodigy: first games before 2000 -> era talent? use era-based approximation only
        first_year = min(years)
        age_unknown = True
        dims["prodigy"] = 60 if first_year <= 2000 else 40  # neutral-ish default
        dims["comeback"] = 40

        gtxt = "、".join(f'{g[0]}{g[1]}' for g in games)
        profile = (f"{name}，中国奥运冠军，{n_golds}枚奥运金牌。"
                   f"主项{'、'.join(sports) if sports else '未知'}。"
                   f"夺冠征程：{gtxt}。代表战绩：{'；'.join(events[:8])}。"
                   f"{'多次团体项目夺金，团队中坚。' if team_golds >= 2 else ''}"
                   f"{'横跨' + str(span) + '年的长青传奇。' if span >= 8 else ''}")
        people.append({
            "name": name, "kind": "champion", "sport": sports[0] if sports else None,
            "gold_medals": n_golds, "games": [g[0] for g in games],
            "events": events, "photo": (photos.get(name) or {}).get("file"),
            "dims": dims, "profile": profile,
        })
    return people


def legend_profiles():
    legends = json.load(open("data/clean/legends.json", encoding="utf-8"))
    photos = {}
    if os.path.exists("data/clean/photos/manifest.json"):
        photos = json.load(open("data/clean/photos/manifest.json", encoding="utf-8"))
    people = []
    for L in legends:
        dims = dict(LEGEND_DIMS.get(L["name"], {}))
        dims.setdefault("prodigy", 50)
        dims.setdefault("comeback", 60)
        profile = (f'{L["name"]}（{L["en"]}），{L["country"]}{L["sport"]}运动员，{L["titles"]}。'
                   f'{L["story"]} 名言：{L["quote_zh"]}')
        people.append({
            "name": L["name"], "kind": "legend", "sport": L["sport"], "country": L["country"],
            "titles": L["titles"], "quote": L["quote"], "quote_zh": L["quote_zh"],
            "photo": (photos.get(L["name"]) or {}).get("file") or L.get("photo"),
            "dims": dims, "profile": profile,
        })
    return people


def main():
    people = champion_profiles() + legend_profiles()
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    profiles = [p["profile"] for p in people]
    emb = model.encode(profiles, batch_size=32, show_progress_bar=True,
                       normalize_embeddings=True)
    q_emb = model.encode([q["phrase"] for q in QUALITIES], normalize_embeddings=True)

    for p, e in zip(people, emb):
        p["emb"] = [round(float(x), 4) for x in e]
    qualities = []
    for q, e in zip(QUALITIES, q_emb):
        weights = {d: 0 for d in
                   ["persistence", "dominance", "teamwork", "versatility",
                    "legacy", "breakthrough", "prodigy", "comeback"]}
        weights[q["id"]] = 1
        qualities.append({**q, "emb": [round(float(x), 4) for x in e], "weights": weights})

    out = {"qualities": qualities, "people": people}
    os.makedirs("data/clean", exist_ok=True)
    json.dump(out, open("data/clean/spirit_match.json", "w", encoding="utf-8"),
              ensure_ascii=False, separators=(",", ":"))
    print("people:", len(people), "| qualities:", len(qualities))
    print("size:", round(os.path.getsize("data/clean/spirit_match.json") / 1e6, 2), "MB")


if __name__ == "__main__":
    main()
