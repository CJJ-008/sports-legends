# -*- coding: utf-8 -*-
"""Build FIFA star rating curves (FIFA 07-23) from Big-Data-FC all_years.csv.

The dataset concatenates sofifa dumps; the FIFA version is encoded in
player_url: /player/<id>/<slug>/070002/ -> "07" = FIFA 2007.
Rows have ragged field counts (unquoted commas) -> position-aware parsing.

Output: data/clean/fifa/star_curves.json
"""
import csv
import json
import statistics
from collections import defaultdict

RAW = "data/raw/fifa/all_years.csv"
OUT = "data/clean/fifa/star_curves.json"

STARS = {  # dataset short_name -> display info
    "L. Messi": ("梅西", "阿根廷", "前锋"),
    "Cristiano Ronaldo": ("C·罗纳尔多", "葡萄牙", "前锋"),
    "Ronaldinho": ("罗纳尔迪尼奥", "巴西", "前腰"),
    "Kaká": ("卡卡", "巴西", "前腰"),
    "A. Iniesta": ("伊涅斯塔", "西班牙", "中场"),
    "Xavi": ("哈维", "西班牙", "中场"),
    "Andres Iniesta Lujan": ("伊涅斯塔", "西班牙", "中场"),
    "Xavier Hernández": ("哈维", "西班牙", "中场"),
    "Neymar Jr": ("内马尔", "巴西", "前锋"),
    "K. Mbappé": ("姆巴佩", "法国", "前锋"),
    "K. Mbappe": ("姆巴佩", "法国", "前锋"),
    "E. Haaland": ("哈兰德", "挪威", "前锋"),
    "K. De Bruyne": ("德布劳内", "比利时", "中场"),
    "Mohamed Salah": ("萨拉赫", "埃及", "前锋"),
    "R. Lewandowski": ("莱万多夫斯基", "波兰", "前锋"),
    "L. Modrić": ("莫德里奇", "克罗地亚", "中场"),
    "Luka Modric": ("莫德里奇", "克罗地亚", "中场"),
    "T. Kroos": ("克罗斯", "德国", "中场"),
    "Sergio Ramos": ("拉莫斯", "西班牙", "后卫"),
    "S. Ramos": ("拉莫斯", "西班牙", "后卫"),
    "L. Suárez": ("苏亚雷斯", "乌拉圭", "前锋"),
    "Z. Ibrahimović": ("伊布拉希莫维奇", "瑞典", "前锋"),
    "Zlatan Ibrahimovic": ("伊布拉希莫维奇", "瑞典", "前锋"),
    "S. Agüero": ("阿圭罗", "阿根廷", "前锋"),
    "Sergio Agüero": ("阿圭罗", "阿根廷", "前锋"),
    "G. Bale": ("贝尔", "威尔士", "前锋"),
    "W. Rooney": ("鲁尼", "英格兰", "前锋"),
    "D. Drogba": ("德罗巴", "科特迪瓦", "前锋"),
    "S. Eto'o": ("埃托奥", "喀麦隆", "前锋"),
    "Casillas": ("卡西利亚斯", "西班牙", "门将"),
    "I. Casillas": ("卡西利亚斯", "西班牙", "门将"),
    "G. Buffon": ("布冯", "意大利", "门将"),
    "Gianluigi Buffon": ("布冯", "意大利", "门将"),
    "M. Neuer": ("诺伊尔", "德国", "门将"),
    "H. Kane": ("凯恩", "英格兰", "前锋"),
    "V. van Dijk": ("范戴克", "荷兰", "后卫"),
    "Son Heung-Min": ("孙兴慜", "韩国", "前锋"),
    "Son Heung-MIn": ("孙兴慜", "韩国", "前锋"),
    "K. Benzema": ("本泽马", "法国", "前锋"),
    "L. Fabregas": ("法布雷加斯", "西班牙", "中场"),
    "Cesc Fàbregas": ("法布雷加斯", "西班牙", "中场"),
    "P. Viera": ("维埃拉", "法国", "中场"),
    "T. Henry": ("亨利", "法国", "前锋"),
    "Thierry Henry": ("亨利", "法国", "前锋"),
    "R. van Nistelrooy": ("范尼斯特鲁伊", "荷兰", "前锋"),
    "D. Beckham": ("贝克汉姆", "英格兰", "中场"),
    "David Beckham": ("贝克汉姆", "英格兰", "中场"),
    "A. Pirlo": ("皮尔洛", "意大利", "中场"),
    "F. Totti": ("托蒂", "意大利", "前锋"),
    "Fernando Torres": ("托雷斯", "西班牙", "前锋"),
    "F. Torres": ("托雷斯", "西班牙", "前锋"),
    "V. Persie": ("范佩西", "荷兰", "前锋"),
    "R. v. Persie": ("范佩西", "荷兰", "前锋"),
    "Robin van Persie": ("范佩西", "荷兰", "前锋"),
    "Vinícius Jr": ("维尼修斯", "巴西", "前锋"),
    "Vinicius Junior": ("维尼修斯", "巴西", "前锋"),
    "J. Bellingham": ("贝林厄姆", "英格兰", "中场"),
    "Lamine Yamal": ("亚马尔", "西班牙", "前锋"),
    "E. Haaland": ("哈兰德", "挪威", "前锋"),
}


def parse_year(player_url: str):
    # /player/158023/lionel-messi/070002/ -> "070002" -> year 2007
    try:
        code = player_url.rstrip("/").split("/")[-1]
        yy = int(code[:2])
        return 2000 + yy if yy < 50 else 1900 + yy
    except Exception:
        return None


def main():
    # collect (player_id, year) -> {bov values, age, club}
    found = defaultdict(lambda: {"bov": [], "age": [], "club": set()})
    matched_names = set()
    with open(RAW, encoding="utf-8", errors="ignore") as f:
        reader = csv.reader(f)
        header = next(reader)
        n71 = len(header)
        for row in reader:
            if len(row) < 12:
                continue
            shift = len(row) - n71
            name = row[2].strip()
            info = STARS.get(name)
            if not info:
                continue
            matched_names.add(name)
            url = row[1]
            year = parse_year(url)
            if not year:
                continue
            try:
                bov = int(row[10 + shift])
                age = int(row[3])
            except Exception:
                continue
            club = row[5] if shift >= 0 else row[5]
            d = found[(row[0], year)]
            d["bov"].append(bov)
            d["age"].append(age)
            d["club"].add(club.strip())

    curves = defaultdict(list)
    meta = {}
    for (pid, year), d in found.items():
        pass
    # need name per pid: map pid -> display info via matched names
    pid_name = {}
    with open(RAW, encoding="utf-8", errors="ignore") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if len(row) < 3:
                continue
            name = row[2].strip()
            if name in STARS and row[0] not in pid_name:
                pid_name[row[0]] = name

    for (pid, year), d in found.items():
        name = pid_name.get(pid)
        if not name:
            continue
        cn, nation, pos = STARS[name]
        curves[cn].append({
            "year": year,
            "bov": round(statistics.median(d["bov"])),
            "age": round(statistics.median(d["age"])) if d["age"] else None,
            "club": sorted(d["club"])[0] if d["club"] else None,
        })

    out = []
    for cn, seasons in curves.items():
        seasons.sort(key=lambda s: s["year"])
        # fill club lineage: keep last known club when missing
        last = None
        for s in seasons:
            if s["club"]:
                last = s["club"]
            else:
                s["club"] = last
        info = next(v for v in STARS.values() if v[0] == cn)
        out.append({"name": cn, "nation": info[1], "position": info[2],
                    "seasons": seasons})
    out.sort(key=lambda x: x["seasons"][0]["year"] if x["seasons"] else 9999)

    import os
    os.makedirs("data/clean/fifa", exist_ok=True)
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print("stars matched:", len(out))
    for s in out:
        ys = f'{s["seasons"][0]["year"]}-{s["seasons"][-1]["year"]}' if s["seasons"] else "none"
        sample = [(x["year"], x["bov"]) for x in s["seasons"][::4]][:6]
        print(f'  {s["name"]} {ys} {sample}')


if __name__ == "__main__":
    main()
