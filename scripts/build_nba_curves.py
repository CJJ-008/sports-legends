# -*- coding: utf-8 -*-
"""Build NBA star career curves (1950-2017) from Seasons_Stats.csv.

Output: data/clean/nba/star_curves.json
"""
import os
import json
import pandas as pd

RAW = "data/raw/nba"
OUT = "data/clean/nba"
os.makedirs(OUT, exist_ok=True)

# canonical name -> list of dataset spellings (dataset uses no accents, e.g. "Kareem Abdul-Jabbar")
STARS = {
    "迈克尔·乔丹": ["Michael Jordan*"],
    "勒布朗·詹姆斯": ["LeBron James"],
    "科比·布莱恩特": ["Kobe Bryant"],
    "斯蒂芬·库里": ["Stephen Curry"],
    "凯文·杜兰特": ["Kevin Durant"],
    "沙奎尔·奥尼尔": ["Shaquille O'Neal"],
    "蒂姆·邓肯": ["Tim Duncan"],
    "凯文·加内特": ["Kevin Garnett"],
    "阿伦·艾弗森": ["Allen Iverson"],
    "德维恩·韦德": ["Dwyane Wade"],
    "德克·诺维茨基": ["Dirk Nowitzki"],
    "斯蒂夫·纳什": ["Steve Nash"],
    "克里斯·保罗": ["Chris Paul"],
    "詹姆斯·哈登": ["James Harden"],
    "拉塞尔·威斯布鲁克": ["Russell Westbrook"],
    "扬尼斯·阿德托昆博": ["Giannis Antetokounmpo"],
    "魔术师约翰逊": ["Magic Johnson*"],
    "拉里·伯德": ["Larry Bird"],
    "卡里姆·阿卜杜勒-贾巴尔": ["Kareem Abdul-Jabbar*"],
    "威尔特·张伯伦": ["Wilt Chamberlain*"],
    "比尔·拉塞尔": ["Bill Russell"],
    "姚明": ["Yao Ming*"],
    "特雷西·麦克格雷迪": ["Tracy McGrady"],
    "比尔·拉塞尔": ["Bill Russell*"],
    "卡梅罗·安东尼": ["Carmelo Anthony"],
    "德马库斯·考辛斯": ["DeMarcus Cousins"],
    "安东尼·戴维斯": ["Anthony Davis"],
    "达米安·利拉德": ["Damian Lillard"],
    "科怀·伦纳德": ["Kawhi Leonard"],
    "扬尼斯-阿德托昆博": ["Giannis Antetokounmpo"],
}


def main():
    df = pd.read_csv(os.path.join(RAW, "Seasons_Stats.csv"))
    df["Player"] = df["Player"].astype(str).str.strip()
    name_lookup = {}
    for cn, spellings in STARS.items():
        for s in spellings:
            name_lookup[s] = cn
    df["cn"] = df["Player"].map(name_lookup)
    stars = df[df["cn"].notna()].copy()
    stars = stars[stars["G"] > 0]

    out = []
    for cn, g in stars.groupby("cn"):
        g = g.sort_values("Year")
        # aggregate rows if a season has multiple teams (trades): sum G/PTS etc, recompute per-game
        agg = g.groupby("Year").agg(
            tm=("Tm", lambda s: "-".join(dict.fromkeys(s.astype(str)))),
            g=("G", "sum"), mp=("MP", "sum"),
            pts=("PTS", "sum"), ast=("AST", "sum"), trb=("TRB", "sum"),
            stl=("STL", "sum"), blk=("BLK", "sum"),
            fg=("FG", "sum"), fga=("FGA", "sum"),
            fg3=("3P", "sum"), fg3a=("3PA", "sum"),
            per=("PER", "mean"), ws=("WS", "sum"),
        ).reset_index()
        # pre-1979 no 3P data
        rows = []
        for _, r in agg.iterrows():
            rows.append({
                "year": int(r["Year"]), "tm": r["tm"], "g": int(r["g"]),
                "ppg": round(r["pts"] / r["g"], 1) if r["g"] else None,
                "rpg": round(r["trb"] / r["g"], 1) if r["g"] else None,
                "apg": round(r["ast"] / r["g"], 1) if r["g"] else None,
                "spg": round(r["stl"] / r["g"], 1) if r["g"] and r["stl"] == r["stl"] else None,
                "bpg": round(r["blk"] / r["g"], 1) if r["g"] and r["blk"] == r["blk"] else None,
                "fg_pct": round(r["fg"] / r["fga"], 3) if r["fga"] else None,
                "fg3_pct": round(r["fg3"] / r["fg3a"], 3) if r["fg3a"] else None,
                "per": round(r["per"], 1) if r["per"] == r["per"] else None,
                "ws": round(r["ws"], 1) if r["ws"] == r["ws"] else None,
            })
        out.append({"name": cn, "name_en": g["Player"].iloc[0], "seasons": rows})
    out.sort(key=lambda x: x["seasons"][0]["year"] if x["seasons"] else 9999)
    os.makedirs(OUT, exist_ok=True)
    json.dump(out, open(os.path.join(OUT, "star_curves.json"), "w", encoding="utf-8"),
              ensure_ascii=False, separators=(",", ":"))
    for s in out:
        ys = f'{s["seasons"][0]["year"]}-{s["seasons"][-1]["year"]}' if s["seasons"] else "none"
        print(s["name"], s["name_en"], ys, f'{len(s["seasons"])} seasons')


if __name__ == "__main__":
    main()
