# -*- coding: utf-8 -*-
"""Build chart-ready JSONs for the Olympics statistics hall.

Inputs : data/raw/olympics/{results,bios,noc_regions}.csv (1896-2022)
Outputs: data/clean/olympics/*.json
"""
import os
import json
import pandas as pd

RAW = "data/raw/olympics"
OUT = "data/clean/olympics"
os.makedirs(OUT, exist_ok=True)

GAMES_CITY = {  # summer games host info (2024 from our own supplement)
    1896: ("Athens",), 1900: ("Paris",), 1904: ("St. Louis",), 1908: ("London",),
    1912: ("Stockholm",), 1920: ("Antwerp",), 1924: ("Paris",), 1928: ("Amsterdam",),
    1932: ("Los Angeles",), 1936: ("Berlin",), 1948: ("London",), 1952: ("Helsinki",),
    1956: ("Melbourne",), 1960: ("Rome",), 1964: ("Tokyo",), 1968: ("Mexico City",),
    1972: ("Munich",), 1976: ("Montreal",), 1980: ("Moscow",), 1984: ("Los Angeles",),
    1988: ("Seoul",), 1992: ("Barcelona",), 1996: ("Atlanta",), 2000: ("Sydney",),
    2004: ("Athens",), 2008: ("Beijing",), 2012: ("London",), 2016: ("Rio",),
    2020: ("Tokyo",), 2024: ("Paris",),
}
WINTER_CITY = {1924: "Chamonix", 1928: "St. Moritz", 1932: "Lake Placid", 1936: "Garmisch",
               1948: "St. Moritz", 1952: "Oslo", 1956: "Cortina", 1960: "Squaw Valley",
               1964: "Innsbruck", 1968: "Grenoble", 1972: "Sapporo", 1976: "Innsbruck",
               1980: "Lake Placid", 1984: "Sarajevo", 1988: "Calgary", 1992: "Albertville",
               1994: "Lillehammer", 1998: "Nagano", 2002: "Salt Lake City", 2006: "Turin",
               2010: "Vancouver", 2014: "Sochi", 2018: "PyeongChang", 2022: "Beijing"}


def dump(name, obj):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, separators=(",", ":"))
    print(name, "->", len(obj) if hasattr(obj, "__len__") else obj)


def main():
    r = pd.read_csv(os.path.join(RAW, "results.csv"))
    r = r[((r["type"] == "Summer") & (r["year"].isin(list(GAMES_CITY)))) |
          ((r["type"] == "Winter") & (r["year"].isin(list(WINTER_CITY))))]
    # Youth Olympic Games rows leak into Summer/Winter types — drop them
    r = r[~r["event"].str.contains("YOG", case=False, na=False)]
    noc = pd.read_csv(os.path.join(RAW, "noc_regions.csv"))
    nocmap = dict(zip(noc["NOC"], noc["region"]))

    medal = r[r["medal"].notna()].copy()
    medal["medal"] = medal["medal"].str.strip().str.title()
    # team events list every member as a row; standard tables count ONE medal
    # per event x NOC x color
    medal = medal.drop_duplicates(subset=["year", "type", "discipline", "event", "noc", "medal"])

    # ---------- games list (standard Games only; dataset also has Youth Olympics) ----------
    summer_years = [y for y in sorted(r[r["type"] == "Summer"]["year"].dropna().unique())
                    if int(y) in GAMES_CITY]
    winter_years = [y for y in sorted(r[r["type"] == "Winter"]["year"].dropna().unique())
                    if int(y) in WINTER_CITY]
    games = [{"year": int(y), "city": GAMES_CITY[int(y)][0], "season": "summer"}
             for y in summer_years] + \
            [{"year": int(y), "city": WINTER_CITY[int(y)], "season": "winter"}
             for y in winter_years]
    games.sort(key=lambda g: g["year"])
    dump("games_list.json", games)

    # ---------- all-time medal tally (top 20, split by season) ----------
    for season, fname in [("Summer", "medal_tally_summer.json"), ("Winter", "medal_tally_winter.json")]:
        sub = medal[medal["type"] == season]
        t = sub.groupby(["noc", "medal"]).size().unstack(fill_value=0)
        for c in ["Gold", "Silver", "Bronze"]:
            if c not in t:
                t[c] = 0
        t["total"] = t[["Gold", "Silver", "Bronze"]].sum(axis=1)
        t = t.sort_values(["Gold", "total"], ascending=False).head(20)
        out = [{"noc": i, "region": nocmap.get(i, i),
                "gold": int(row["Gold"]), "silver": int(row["Silver"]),
                "bronze": int(row["Bronze"]), "total": int(row["total"])}
               for i, row in t.iterrows()]
        dump(fname, out)

    # ---------- per-games medal table (summer, for year-by-year explore) ----------
    sub = medal[medal["type"] == "Summer"]
    t = sub.groupby(["year", "noc", "medal"]).size().unstack(fill_value=0)
    rows = []
    for (year, n), row in t.iterrows():
        rows.append({"year": int(year), "noc": n, "region": nocmap.get(n, n),
                     "gold": int(row.get("Gold", 0)), "silver": int(row.get("Silver", 0)),
                     "bronze": int(row.get("Bronze", 0))})
    dump("summer_medals_by_year.json", rows)

    # ---------- selected countries gold trend (summer) ----------
    SEL = ["USA", "CHN", "URS", "GER", "GBR", "FRA", "ITA", "HUN", "JPN", "KOR", "AUS", "EUN", "RUS"]
    trend = {}
    for c in SEL:
        s = sub[(sub["noc"] == c) & (sub["medal"] == "Gold")]
        per = s.groupby("year").size()
        trend[c] = {"name": nocmap.get(c, c), "years": [int(y) for y in per.index],
                    "golds": [int(v) for v in per.values]}
    dump("summer_gold_trend.json", trend)

    # ---------- China by games (summer + winter) ----------
    # China numbers come from OUR official champions master (327 golds, exact),
    # because results.csv is missing a few Tokyo-era rows.
    m = json.load(open("data/staging/champions_master.json", encoding="utf-8"))
    agg = {}
    for x in m:
        key = (x["season"], x["year"])
        a = agg.setdefault(key, {"gold": 0, "silver": 0, "bronze": 0, "sports": {}})
        a["gold"] += 1
        if x["sport"]:
            a["sports"][x["sport"]] = a["sports"].get(x["sport"], 0) + 1
    rows = []
    for (season, year), a in sorted(agg.items(), key=lambda kv: (kv[0][0], int(kv[0][1]))):
        rows.append({"season": season, "year": int(year), "gold": a["gold"],
                     "total": a["gold"]})
    dump("china_by_games.json", rows)

    # ---------- China golds by discipline (from champions master) ----------
    out = []
    for (season, year), a in agg.items():
        for sp, n in a["sports"].items():
            out.append({"season": season, "discipline": sp, "gold": n})
    agg2 = {}
    for o in out:
        k = (o["season"], o["discipline"])
        agg2[k] = agg2.get(k, 0) + o["gold"]
    out = [{"season": s, "discipline": d, "gold": n} for (s, d), n in agg2.items()]
    out.sort(key=lambda x: -x["gold"])
    dump("china_gold_by_sport.json", out)

    # ---------- women's events evolution (summer) ----------
    ev = r[(r["type"] == "Summer")].copy()
    ev["is_women"] = ev["event"].str.contains("Women", case=False, na=False)
    ev["is_mixed"] = ev["event"].str.contains("Mixed", case=False, na=False)
    g = ev.groupby("year").agg(events=("event", "nunique"),
                               women_events=("is_women", lambda s: s[s].nunique()),
                               mixed_events=("is_mixed", lambda s: s[s].nunique()))
    out = [{"year": int(y), "events": int(row["events"]),
            "women": int(row["women_events"]), "mixed": int(row["mixed_events"])}
           for y, row in g.iterrows()]
    dump("women_events_evolution.json", out)

    # ---------- athletes per games (summer) ----------
    per = r[r["type"] == "Summer"].dropna(subset=["athlete_id"]).groupby("year")["athlete_id"].nunique()
    out = [{"year": int(y), "athletes": int(v)} for y, v in per.items()]
    dump("athletes_per_games.json", out)

    # ---------- China vs USA summer gold head-to-head ----------
    h2h = {}
    for c in ["CHN", "USA"]:
        s = sub[(sub["noc"] == c) & (sub["medal"] == "Gold")].groupby("year").size()
        h2h[c] = {int(y): int(v) for y, v in s.items()}
    dump("china_usa_gold.json", h2h)


if __name__ == "__main__":
    main()
