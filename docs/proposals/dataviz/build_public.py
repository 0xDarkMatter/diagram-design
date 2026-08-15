#!/usr/bin/env python3
"""All contribution-candidate charts rebuilt on PUBLIC data everyone knows.

Sources, fetched 2026-08-15 into ./data/ and parsed at build time:
  - Our World in Data grapher CSVs (population, life expectancy, energy,
    CO2 per capita, temperature anomaly, electricity by source, gapminder)
  - FiveThirtyEight US births 2000-2014 (SSA)
  - UN DESA 2020 migrant-stock corridors, IOC medal tables, WMO climate
    normals, and European land borders embedded as cited constants.

Fifteen charts: nine forms redone on public data + six new forms (bubble,
ridgeline, small multiples, marimekko, warming stripes, punch card). The US
hex map already used public data and stands unchanged.
"""
from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path

from build_dataviz import emit

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"


def rows(name):
    with open(DATA / f"{name}.csv", encoding="utf-8-sig") as f:
        yield from csv.DictReader(f)


def fnum(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


CONTINENTS = ["Asia", "Africa", "Europe", "North America", "South America", "Oceania"]


# ===========================================================================
# 1. TREEMAP - world population by region (OWID/UN 2023)
# ===========================================================================
def squarify(items, x, y, w, h):
    total = sum(i[1] for i in items)
    scale = (w * h) / total
    areas = [(item, item[1] * scale) for item in items]
    rects = []
    cx, cy, cw, ch = float(x), float(y), float(w), float(h)
    row = []

    def worst(ra, ln):
        s = sum(ra)
        return max((ln ** 2) * max(ra) / (s ** 2), (s ** 2) / ((ln ** 2) * min(ra)))

    def flush():
        nonlocal cx, cy, cw, ch
        s = sum(a for _, a in row)
        if cw >= ch:
            rw = s / ch
            yy = cy
            for payload, a in row:
                rects.append((payload, cx, yy, rw, a / rw)); yy += a / rw
            cx += rw; cw -= rw
        else:
            rh = s / cw
            xx = cx
            for payload, a in row:
                rects.append((payload, xx, cy, a / rh, rh)); xx += a / rh
            cy += rh; ch -= rh
        row.clear()

    for payload, a in areas:
        ln = min(cw, ch)
        cur = [ar for _, ar in row]
        if not row or worst(cur + [a], ln) <= worst(cur, ln):
            row.append((payload, a))
        else:
            flush(); row.append((payload, a))
    if row:
        flush()
    return rects


def treemap():
    pop = {}
    for r in rows("population"):
        if r["Entity"] in CONTINENTS and r["Year"] == "2023":
            pop[r["Entity"]] = fnum(r["Population"])
    data = sorted(((k, v) for k, v in pop.items()), key=lambda kv: -kv[1])
    total = sum(v for _, v in data)
    ramp = [0.85, 0.68, 0.52, 0.4, 0.28, 0.18]
    body = []
    for i, (item, x, y, w, h) in enumerate(squarify(data, 40, 40, 920, 480)):
        name, v = item
        x = round(x / 4) * 4; y = round(y / 4) * 4
        w = max(4, round(w / 4) * 4 - 4); h = max(4, round(h / 4) * 4 - 4)
        focal = i == 0
        cls = "cell-focal" if focal else "cell"
        op = "" if focal else f' opacity="{ramp[i]}"'
        light = (not focal) and ramp[i] <= 0.5
        lab, sml = ("name", "sub") if light else ("cell-label", "cell-sub")
        bn = v / 1e9
        tip = f"*{bn:.2f} billion people*|{v / total * 100:.1f}% of the world"
        body.append(f'      <rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="2"{op} data-tip-label="{name}" data-tip="{tip}"/>')
        if w >= 96 and h >= 56:
            body.append(f'      <text class="{lab}" x="{x + 12}" y="{y + 24}" font-size="13">{name}</text>')
            body.append(f'      <text class="{sml}" x="{x + 12}" y="{y + 40}" font-size="9">{bn:.2f}B · {v / total * 100:.0f}%</text>')
        elif w >= 64 and h >= 32:
            body.append(f'      <text class="{lab}" x="{x + 8}" y="{y + 18}" font-size="10">{name}</text>')
            body.append(f'      <text class="{sml}" x="{x + 8}" y="{y + 31}" font-size="8">{bn:.2f}B</text>')
        else:
            body.append(f'      <text class="{sml}" x="{x + 6}" y="{y + 14}" font-size="8">{name[:2].upper()}</text>')
    body.append(f'      <text class="sub" x="40" y="552" font-size="8" letter-spacing="0.06em">AREA = POPULATION · OUR WORLD IN DATA (UN WPP), 2023 · {total / 1e9:.2f} BILLION TOTAL</text>')
    emit("world-population-treemap", "Treemap · world population",
         "Eight billion people, six rectangles",
         "Area is people. Asia alone is nearly six in every ten of us; Oceania is a sliver you could mistake for a border. Hover any region.",
         "Treemap of world population by region in 2023 from UN data; Asia dominates with about 59 percent of the total.",
         "\n".join(body), "0 0 1000 568")


# ===========================================================================
# 2. SANKEY - the world's largest migration corridors (UN DESA 2020)
# ===========================================================================
def sankey():
    links = [  # origin, destination, millions living abroad (UN DESA 2020 stock)
        ("Mexico", "United States", 10.9),
        ("India", "UAE", 3.5), ("India", "United States", 2.7), ("India", "Saudi Arabia", 2.5),
        ("Syria", "Turkey", 3.7),
        ("China", "United States", 2.9),
        ("Ukraine", "Russia", 3.3),
        ("Philippines", "United States", 2.0), ("Philippines", "Saudi Arabia", 1.2),
    ]
    lorder = ["Mexico", "India", "Syria", "China", "Ukraine", "Philippines"]
    rorder = ["United States", "UAE", "Saudi Arabia", "Turkey", "Russia"]
    ltot = {k: sum(n for a, b, n in links if a == k) for k in lorder}
    rtot = {k: sum(n for a, b, n in links if b == k) for k in rorder}
    total = sum(ltot.values())
    X1, X2, TOP, H, GAP = 240, 740, 72, 400, 24
    scale = (H - GAP * (len(lorder) - 1)) / total
    lp, y = {}, TOP
    for k in lorder:
        lp[k] = {"top": y, "cur": y, "h": ltot[k] * scale}; y += ltot[k] * scale + GAP
    rp, y = {}, TOP + 16
    for k in rorder:
        rp[k] = {"top": y, "cur": y, "h": rtot[k] * scale}; y += rtot[k] * scale + 32
    body = []
    for a, b, n in links:
        h = n * scale
        sy = lp[a]["cur"]; lp[a]["cur"] += h
        ty = rp[b]["cur"]; rp[b]["cur"] += h
        focal = (a, b) == ("Mexico", "United States")
        cls = "ribbon-focal" if focal else "ribbon"
        mid = (X1 + X2) / 2
        tip = f"*{n:.1f} million people* born in {a}|now living in {b}|UN migrant stock, 2020"
        body.append(f'      <path class="{cls}" d="M {X1},{sy:.1f} C {mid},{sy:.1f} {mid},{ty:.1f} {X2},{ty:.1f} '
                    f'L {X2},{ty + h:.1f} C {mid},{ty + h:.1f} {mid},{sy + h:.1f} {X1},{sy + h:.1f} Z" '
                    f'data-tip-label="{a} → {b}" data-tip="{tip}"/>')
    for k in lorder:
        p = lp[k]
        body.append(f'      <rect class="bar-node" x="{X1 - 8}" y="{p["top"]:.1f}" width="8" height="{p["h"]:.1f}"/>')
        cy = p["top"] + p["h"] / 2
        body.append(f'      <text class="name" x="{X1 - 20}" y="{cy + 4:.1f}" font-size="12" text-anchor="end">{k}</text>')
        body.append(f'      <text class="sub" x="{X1 - 20}" y="{cy + 18:.1f}" font-size="8" text-anchor="end">{ltot[k]:.1f}M</text>')
    for k in rorder:
        p = rp[k]
        body.append(f'      <rect class="bar-node" x="{X2}" y="{p["top"]:.1f}" width="8" height="{p["h"]:.1f}"/>')
        cy = p["top"] + p["h"] / 2
        body.append(f'      <text class="name" x="{X2 + 20}" y="{cy + 4:.1f}" font-size="12">{k}</text>')
        body.append(f'      <text class="sub" x="{X2 + 20}" y="{cy + 18:.1f}" font-size="8">{rtot[k]:.1f}M</text>')
    body.append('      <text class="sub" x="40" y="548" font-size="8" letter-spacing="0.06em">'
                'MIGRANT STOCK (PEOPLE LIVING OUTSIDE THEIR BIRTH COUNTRY) · UN DESA INTERNATIONAL MIGRANT STOCK 2020 · '
                'NINE OF THE LARGEST CORRIDORS - MANY OTHERS OMITTED</text>')
    emit("migration-sankey", "Sankey · migration corridors",
         "The world's largest migration corridors",
         "Where people born in one country now live in another. Mexico to the United States is the largest corridor on Earth - nearly eleven million people - and India feeds three of the top nine.",
         "Sankey diagram of the largest international migration corridors from UN 2020 migrant-stock data; Mexico to the United States is the widest ribbon at 10.9 million.",
         "\n".join(body), "0 0 1000 564")


# ===========================================================================
# 3. SLOPEGRAPH - life expectancy by region, 1950 vs 2023 (OWID/UN)
# ===========================================================================
def slope():
    le = defaultdict(dict)
    for r in rows("life-expectancy"):
        if r["Entity"] in CONTINENTS + ["World"] and r["Year"] in ("1950", "2023"):
            le[r["Entity"]][r["Year"]] = fnum(r["Life expectancy"])
    data = [(k, v["1950"], v["2023"], k == "World") for k, v in le.items()
            if "1950" in v and "2023" in v]
    data.sort(key=lambda d: -d[2])
    X1, X2, BASE, S = 320, 680, 520, 6  # y = BASE - v*S
    body = []
    for x, lab, sub in ((X1, "1950", ""), (X2, "2023", "")):
        body.append(f'      <line class="axis" x1="{x}" y1="40" x2="{x}" y2="{BASE}" stroke-width="1"/>')
        body.append(f'      <text class="sub" x="{x}" y="{BASE + 28}" font-size="9" text-anchor="middle" letter-spacing="0.14em">{lab}</text>')

    def nudge(vals):
        ys = sorted((BASE - v * S, i) for i, v in enumerate(vals))
        out = [0.0] * len(vals)
        prev = -1e9
        for yy, i in ys:
            yy = max(yy, prev + 17)
            out[i] = yy; prev = yy
        return out

    lys = nudge([d[1] for d in data])
    rys = nudge([d[2] for d in data])
    for i, (name, a, b, focal) in enumerate(data):
        y1, y2 = BASE - a * S, BASE - b * S
        cls = "slope-focal" if focal else "slope"
        dot = "dot-accent" if focal else "dot"
        tip = f"*{a:.0f} → {b:.0f} years*|+{b - a:.0f} years in three generations"
        body.append(f'      <line class="{cls}" x1="{X1}" y1="{y1:.0f}" x2="{X2}" y2="{y2:.0f}" stroke-width="{2 if focal else 1.2}"/>')
        body.append(f'      <circle class="{dot}" cx="{X1}" cy="{y1:.0f}" r="4" data-tip-label="{name}" data-tip="{tip}"/>')
        body.append(f'      <circle class="{dot}" cx="{X2}" cy="{y2:.0f}" r="4" data-tip-label="{name}" data-tip="{tip}"/>')
        lcls = "name" if focal else "sub"
        body.append(f'      <text class="{lcls}" x="{X1 - 16}" y="{lys[i] + 4:.0f}" font-size="11" text-anchor="end">{name}  {a:.0f}</text>')
        body.append(f'      <text class="{lcls}" x="{X2 + 16}" y="{rys[i] + 4:.0f}" font-size="11">{b:.0f}  {name}</text>')
    body.append('      <text class="sub" x="60" y="592" font-size="8" letter-spacing="0.06em">'
                'LIFE EXPECTANCY AT BIRTH, YEARS · OUR WORLD IN DATA (UN WPP), 1950 AND 2023 · EVERY REGION GAINED AT LEAST 16 YEARS</text>')
    emit("life-expectancy-slope", "Slopegraph · life expectancy",
         "Seventy years of longer lives",
         "Every region on Earth, 1950 against 2023. Asia gains thirty-one years - the steepest climb in human history - and the world line crosses from 47 to 73.",
         "Slopegraph of life expectancy by world region comparing 1950 with 2023; every region rises, Asia most steeply.",
         "\n".join(body), "0 0 1000 616")


# ===========================================================================
# 4. DUMBBELL - the gender longevity gap (WHO/UN 2023)
# ===========================================================================
def dumbbell():
    data = [  # country, male, female (life expectancy at birth, UN WPP 2023)
        ("Japan", 81.1, 87.1, False),
        ("United Kingdom", 79.2, 82.9, False),
        ("United States", 75.5, 80.9, False),
        ("China", 75.6, 80.9, False),
        ("Russia", 67.6, 77.8, True),   # the famous ten-year gap
        ("India", 70.5, 73.6, False),
    ]
    X0, X1V, VMIN, VMAX = 260, 920, 60, 90
    xv = lambda v: X0 + (v - VMIN) / (VMAX - VMIN) * (X1V - X0)
    body = []
    for v in (60, 70, 80, 90):
        x = xv(v)
        body.append(f'      <line class="grid" x1="{x:.0f}" y1="64" x2="{x:.0f}" y2="472" stroke-width="0.8"/>')
        body.append(f'      <text class="axis-label sub" x="{x:.0f}" y="496" font-size="8" text-anchor="middle">{v}</text>')
    y = 96
    for name, m, f, focal in data:
        xa, xb = xv(m), xv(f)
        dl = "dot-accent-hollow" if focal else "dot-hollow"
        dd = "dot-accent" if focal else "dot"
        tip = f"men *{m:.1f}* · women *{f:.1f}*|a {f - m:.1f}-year gap|UN World Population Prospects, 2023"
        body.append(f'      <line class="range" x1="{xa:.0f}" y1="{y}" x2="{xb:.0f}" y2="{y}" stroke-width="2" data-tip-label="{name}" data-tip="{tip}"/>')
        body.append(f'      <circle class="{dl}" cx="{xa:.0f}" cy="{y}" r="6" stroke-width="1.5" data-tip-label="{name}" data-tip="{tip}"/>')
        body.append(f'      <circle class="{dd}" cx="{xb:.0f}" cy="{y}" r="6" data-tip-label="{name}" data-tip="{tip}"/>')
        body.append(f'      <text class="name" x="{X0 - 56}" y="{y + 4}" font-size="12" text-anchor="end">{name}</text>')
        body.append(f'      <text class="sub" x="{xa - 12:.0f}" y="{y + 4}" font-size="8" text-anchor="end">{m:.1f}</text>')
        body.append(f'      <text class="sub" x="{xb + 12:.0f}" y="{y + 4}" font-size="8">{f:.1f}</text>')
        y += 68
    body.append('      <circle class="dot-hollow" cx="272" cy="536" r="6" stroke-width="1.5"/>')
    body.append('      <text class="sub" x="288" y="540" font-size="9">men</text>')
    body.append('      <circle class="dot" cx="372" cy="536" r="6"/>')
    body.append('      <text class="sub" x="388" y="540" font-size="9">women</text>')
    body.append('      <text class="sub" x="60" y="576" font-size="8" letter-spacing="0.06em">'
                'LIFE EXPECTANCY AT BIRTH BY SEX, YEARS · UN WORLD POPULATION PROSPECTS 2023 · WOMEN OUTLIVE MEN EVERYWHERE - RUSSIA BY A DECADE</text>')
    emit("gender-gap-dumbbell", "Dumbbell · longevity gap",
         "Women outlive men, everywhere",
         "Hollow dot men, filled dot women. The gap is universal but not uniform: three and a half years in the UK, ten in Russia - the widest of any large country.",
         "Dumbbell chart of male versus female life expectancy in six large countries from UN 2023 data; Russia shows the widest gap at about ten years.",
         "\n".join(body), "0 0 1000 592")


# ===========================================================================
# 5. WAFFLE - global primary energy, one square = 1% (OWID 2023)
# ===========================================================================
def waffle():
    world = {r["Year"]: r for r in rows("global-energy-substitution") if r["Entity"] == "World"}
    y = world[max(world)]
    groups = [
        ("Oil", fnum(y["Oil"]), False),
        ("Coal", fnum(y["Coal"]), False),
        ("Gas", fnum(y["Gas"]), False),
        ("Hydro", fnum(y["Hydropower"]), False),
        ("Biomass", (fnum(y["Traditional biomass"]) or 0) + (fnum(y["Biofuels"]) or 0), False),
        ("Nuclear", fnum(y["Nuclear"]), False),
        ("Wind", fnum(y["Wind"]), False),
        ("Solar", fnum(y["Solar"]), True),
    ]
    total = sum(v for _, v, _ in groups) + fnum(y["Other renewables"])
    # one square = 1%, largest-remainder rounding to exactly 100 incl "other"
    pct = [(n, v / total * 100, f) for n, v, f in groups]
    pct.append(("Other renewables", fnum(y["Other renewables"]) / total * 100, False))
    floors = [(n, int(p), p - int(p), f) for n, p, f in pct]
    left = 100 - sum(fl for _, fl, _, _ in floors)
    floors.sort(key=lambda t: -t[2])
    counts = {n: fl + (1 if i < left else 0) for i, (n, fl, _, f) in enumerate(floors)}
    order = [n for n, _, _ in pct]
    focal = {n: f for n, _, f in pct}
    ramp = {"Oil": 0.85, "Coal": 0.7, "Gas": 0.55, "Hydro": 0.42, "Biomass": 0.32,
            "Nuclear": 0.24, "Wind": 0.17, "Other renewables": 0.12}
    COLS, SIZE, GAP, X0, Y0 = 10, 32, 6, 80, 56
    body = []
    idx = 0
    for name in order:
        for _ in range(counts[name]):
            r, c = divmod(idx, COLS)
            x = X0 + c * (SIZE + GAP)
            yy = Y0 + r * (SIZE + GAP)
            cls = "cell-focal" if focal[name] else "cell"
            op = "" if focal[name] else f' opacity="{ramp[name]}"'
            tip = f"*{counts[name]}%* of world primary energy|substitution method|Our World in Data / Energy Institute, {max(world)}"
            body.append(f'      <rect class="{cls}" x="{x}" y="{yy}" width="{SIZE}" height="{SIZE}" rx="3"{op} data-tip-label="{name}" data-tip="{tip}"/>')
            idx += 1
    ly = Y0 + 8
    lx = X0 + COLS * (SIZE + GAP) + 56
    for name in order:
        cls = "cell-focal" if focal[name] else "cell"
        op = "" if focal[name] else f' opacity="{ramp[name]}"'
        body.append(f'      <rect class="{cls}" x="{lx}" y="{ly - 12}" width="16" height="16" rx="3"{op}/>')
        body.append(f'      <text class="name" x="{lx + 28}" y="{ly + 1}" font-size="12">{name}</text>')
        body.append(f'      <text class="sub" x="{lx + 260}" y="{ly + 1}" font-size="10" text-anchor="end">{counts[name]}%</text>')
        ly += 42
    body.append(f'      <text class="sub" x="{X0}" y="472" font-size="8" letter-spacing="0.06em">'
                f'ONE SQUARE = 1% OF GLOBAL PRIMARY ENERGY · OUR WORLD IN DATA (ENERGY INSTITUTE), {max(world)} · '
                f'FOSSIL FUELS STILL {counts["Oil"] + counts["Coal"] + counts["Gas"]} OF THE 100 SQUARES</text>')
    emit("energy-waffle", "Waffle · world energy",
         "The world's energy, in one hundred squares",
         "One square is one percent of everything humanity burns, splits, or harvests. The accent squares are solar - growing fastest, still countable on one hand.",
         "Waffle chart of the global primary energy mix, one square per percent; fossil fuels fill roughly three-quarters of the grid and solar takes the accent.",
         "\n".join(body), "0 0 1000 496")


# ===========================================================================
# 6. BUMP - Olympic gold-medal table, 2000-2024 (IOC)
# ===========================================================================
def bump():
    snaps = ["SYDNEY 2000", "BEIJING 2008", "RIO 2016", "PARIS 2024"]
    golds = {  # IOC medal tables as currently published
        "United States": [37, 36, 46, 40],
        "China": [28, 48, 26, 40],
        "Great Britain": [11, 19, 27, 14],
        "Russia": [32, 24, 19, None],   # absent from Paris - drawn as absence
        "Germany": [13, 16, 17, 12],
        "Japan": [5, 9, 12, 20],
        "Australia": [16, 14, 8, 18],
        "France": [13, 7, 10, 16],
    }
    ranks = {k: [None] * 4 for k in golds}
    for i in range(4):
        present = [(k, v[i]) for k, v in golds.items() if v[i] is not None]
        present.sort(key=lambda kv: (-kv[1], kv[0]))
        for rk, (k, _) in enumerate(present, 1):
            ranks[k][i] = rk
    X = [220, 420, 620, 820]
    y_of = lambda r: 88 + (r - 1) * 52
    body = []
    for x, s in zip(X, snaps):
        body.append(f'      <line class="axis" x1="{x}" y1="72" x2="{x}" y2="{y_of(8) + 16}" stroke-width="1"/>')
        body.append(f'      <text class="sub" x="{x}" y="{y_of(8) + 44}" font-size="8" text-anchor="middle" letter-spacing="0.1em">{s}</text>')
    for name, g in golds.items():
        pts = [(X[i], y_of(ranks[name][i])) for i in range(4) if ranks[name][i]]
        focal = name == "China"
        lcl = "slope-focal" if focal else "slope"
        dcl = "dot-accent" if focal else "dot"
        segs = [(i, i + 1) for i in range(3) if ranks[name][i] and ranks[name][i + 1]]
        for a, b in segs:
            body.append(f'      <line class="{lcl}" x1="{X[a]}" y1="{y_of(ranks[name][a])}" x2="{X[b]}" y2="{y_of(ranks[name][b])}" stroke-width="{2 if focal else 1.2}"/>')
        tip = "|".join(f"{s.split()[0].title()}: *{golds[name][i]}* golds" for i, s in enumerate(snaps) if golds[name][i] is not None)
        for i in range(4):
            if ranks[name][i]:
                body.append(f'      <circle class="{dcl}" cx="{X[i]}" cy="{y_of(ranks[name][i])}" r="5" data-tip-label="{name}" data-tip="{tip}"/>')
        lcls = "name" if focal else "sub"
        body.append(f'      <text class="{lcls}" x="{X[0] - 16}" y="{y_of(ranks[name][0]) + 4}" font-size="11" text-anchor="end">{name}</text>')
        last = 3 if ranks[name][3] else 2
        body.append(f'      <text class="{lcls}" x="{X[last] + 16}" y="{y_of(ranks[name][last]) + 4}" font-size="11">{name}  {golds[name][last]}</text>')
    body.append('      <text class="sub" x="60" y="588" font-size="8" letter-spacing="0.06em">'
                'RANK BY GOLD MEDALS, SUMMER GAMES · IOC MEDAL TABLES AS CURRENTLY PUBLISHED · '
                'RUSSIA DID NOT COMPETE AS A TEAM IN PARIS - THE LINE SIMPLY ENDS</text>')
    emit("olympic-bump", "Bump chart · Olympic golds",
         "Six Games of gold, ranked",
         "Rank by gold medals across four summer Games. China's accent line spikes to first at home in 2008, and Japan climbs from seventh toward its own home Games and beyond.",
         "Bump chart of Olympic gold-medal rank for eight countries across the 2000, 2008, 2016 and 2024 summer Games.",
         "\n".join(body), "0 0 1000 608")


# ===========================================================================
# 7. STREAMGRAPH - global primary energy by source, 1900-2023 (OWID)
# ===========================================================================
def stream():
    world = {int(r["Year"]): r for r in rows("global-energy-substitution") if r["Entity"] == "World"}
    years = [y for y in range(1900, 2021, 10)] + [2023]
    series = [  # label, columns to sum
        ("Biomass", ["Traditional biomass", "Biofuels"]),
        ("Coal", ["Coal"]), ("Oil", ["Oil"]), ("Gas", ["Gas"]),
        ("Hydro & nuclear", ["Hydropower", "Nuclear"]),
        ("Wind & solar", ["Wind", "Solar", "Other renewables"]),
    ]
    vals = {lab: [sum(fnum(world[y][c]) or 0 for c in cols) for y in years] for lab, cols in series}
    totals_per_year = [sum(vals[lab][i] for lab, _ in series) for i in range(len(years))]
    X0, X1, CY = 80, 960, 300
    SCALE = 260 / max(totals_per_year)
    xs = [X0 + i * (X1 - X0) / (len(years) - 1) for i in range(len(years))]
    tops = defaultdict(list)
    for i in range(len(years)):
        yy = CY - totals_per_year[i] * SCALE / 2
        for lab, _ in series:
            v = vals[lab][i] * SCALE
            tops[lab].append((yy, yy + v)); yy += v

    def smooth(points):
        p = [points[0]] + list(points) + [points[-1]]
        d = ""
        for i in range(1, len(p) - 2):
            c1 = (p[i][0] + (p[i + 1][0] - p[i - 1][0]) / 6, p[i][1] + (p[i + 1][1] - p[i - 1][1]) / 6)
            c2 = (p[i + 1][0] - (p[i + 2][0] - p[i][0]) / 6, p[i + 1][1] - (p[i + 2][1] - p[i][1]) / 6)
            d += f" C {c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p[i + 1][0]:.1f},{p[i + 1][1]:.1f}"
        return d

    body = []
    opac = {"Biomass": 0.2, "Coal": 0.72, "Oil": None, "Gas": 0.5, "Hydro & nuclear": 0.32, "Wind & solar": 0.13}
    for lab, _ in series:
        up = [(xs[i], tops[lab][i][0]) for i in range(len(years))]
        dn = [(xs[i], tops[lab][i][1]) for i in range(len(years))][::-1]
        focal = lab == "Oil"
        cls = "cell-focal" if focal else "cell"
        op = "" if focal else f' opacity="{opac[lab]}"'
        share = vals[lab][-1] / totals_per_year[-1] * 100
        tip = f"*{vals[lab][-1]:,.0f} TWh* in 2023 - {share:.0f}% of primary energy|substitution method"
        d = f"M {up[0][0]:.1f},{up[0][1]:.1f}" + smooth(up) + f" L {dn[0][0]:.1f},{dn[0][1]:.1f}" + smooth(dn) + " Z"
        body.append(f'      <path class="{cls}" d="{d}"{op} data-tip-label="{lab}" data-tip="{tip}"/>')
    for i, y in enumerate(years):
        if y % 20 == 0 or y == 2023:
            body.append(f'      <text class="sub" x="{xs[i]:.0f}" y="540" font-size="8" text-anchor="middle" letter-spacing="0.1em">{y}</text>')
    lx = 80
    for lab, _ in series:
        cls = "cell-focal" if lab == "Oil" else "cell"
        op = "" if lab == "Oil" else f' opacity="{opac[lab]}"'
        body.append(f'      <rect class="{cls}" x="{lx}" y="564" width="14" height="14" rx="2"{op}/>')
        body.append(f'      <text class="sub" x="{lx + 20}" y="575" font-size="9">{lab}</text>')
        lx += len(lab) * 6 + 56
    body.append('      <text class="sub" x="80" y="612" font-size="8" letter-spacing="0.06em">'
                'GLOBAL PRIMARY ENERGY, TWh, SUBSTITUTION METHOD · OUR WORLD IN DATA / ENERGY INSTITUTE · DECADE STEPS 1900-2020 PLUS 2023</text>')
    emit("energy-stream", "Streamgraph · world energy",
         "How humanity powered a century",
         "The river widens twentyfold. Coal hands the lead to oil after mid-century, gas swells beside it, and the thin bright edge - wind and solar - only appears in the last two bends.",
         "Streamgraph of global primary energy by source from 1900 to 2023; total width grows enormously and oil, in accent, dominates after 1960.",
         "\n".join(body), "0 0 1000 632")


# ===========================================================================
# 8. BEESWARM - GDP per capita, one dot per country (OWID 2023)
# ===========================================================================
def beeswarm():
    pts = []
    for r in rows("life-expectancy-vs-gdp-per-capita"):
        if r["Year"] == "2022" and r["Code"] and len(r["Code"]) == 3 and r["Code"] != "OWID_WRL":
            g = fnum(r["GDP per capita"])
            if g:
                pts.append((r["Entity"], g))
    pts.sort(key=lambda p: p[1])
    X0, X1 = 100, 940
    lo = min(g for _, g in pts) * 0.9
    hi = max(g for _, g in pts) * 1.1
    xv = lambda g: X0 + (math.log10(g) - math.log10(lo)) / (math.log10(hi) - math.log10(lo)) * (X1 - X0)
    CY, RAD = 300, 6
    placed = []

    def dodge(x):
        y = CY; step = 0
        while any((px - x) ** 2 + (py - y) ** 2 < (2 * RAD + 2) ** 2 for px, py in placed):
            step += 1
            y = CY + (step + 1) // 2 * (2 * RAD + 2) * (1 if step % 2 else -1)
        placed.append((x, y))
        return y

    body = []
    for v in (1000, 3000, 10000, 30000, 100000):
        x = xv(v)
        lbl = f"${v // 1000}k" if v >= 1000 else str(v)
        body.append(f'      <line class="grid" x1="{x:.0f}" y1="104" x2="{x:.0f}" y2="496" stroke-width="0.8"/>')
        body.append(f'      <text class="axis-label sub" x="{x:.0f}" y="520" font-size="8" text-anchor="middle">{lbl}</text>')
    top = pts[-1][0]
    ypos = {}
    for name, g in pts:
        x = xv(g)
        y = dodge(x)
        ypos[name] = (x, y)
        focal = name == top
        cls = "dot-accent" if focal else "dot"
        op = "" if focal else ' opacity="0.55"'
        tip = f"*${g:,.0f}* GDP per capita|international-$ at PPP|Our World in Data, 2022"
        body.append(f'      <circle class="{cls}" cx="{x:.1f}" cy="{y:.1f}" r="{RAD}"{op} data-tip-label="{name}" data-tip="{tip}"/>')
    for i, (name, g) in enumerate([pts[-1], pts[-2], pts[-3], pts[0], pts[1]]):
        x, y = ypos[name]
        ly = y - 28 - (i % 3) * 16
        anchor, lx = ("end", max(x - 10, 180)) if x > 520 else ("start", min(x + 10, 820))
        body.append(f'      <line class="grid" x1="{x:.0f}" y1="{ly + 4}" x2="{x:.0f}" y2="{y - RAD - 2:.0f}" stroke-width="0.8"/>')
        body.append(f'      <text class="sub" x="{lx:.0f}" y="{ly}" font-size="9" text-anchor="{anchor}">{name}</text>')
    body.append(f'      <text class="sub" x="60" y="576" font-size="8" letter-spacing="0.06em">'
                f'ONE DOT = ONE COUNTRY ({len(pts)}) · GDP PER CAPITA, INTERNATIONAL-$ (PPP), LOG SCALE · OUR WORLD IN DATA, 2022 · VERTICAL DODGE ONLY</text>')
    emit("gdp-beeswarm", "Beeswarm · world incomes",
         "Every country, one dot",
         "The whole world economy on a log scale - a hundredfold spread from the poorest to the richest. The swarm thickens in the middle-income band; the accent dot sits alone at the top.",
         "Beeswarm plot of GDP per capita for every country in 2022 on a log axis, from under a thousand dollars to over a hundred thousand.",
         "\n".join(body), "0 0 1000 600")


# ===========================================================================
# 9. ARC - land borders of western & central Europe
# ===========================================================================
def arc():
    order = ["Portugal", "Spain", "France", "Belgium", "Netherlands", "Luxembourg",
             "Germany", "Denmark", "Switzerland", "Italy", "Austria", "Slovenia",
             "Czechia", "Slovakia", "Poland", "Hungary"]
    A = {"Portugal": ["Spain"], "Spain": ["France"],
         "France": ["Belgium", "Luxembourg", "Germany", "Switzerland", "Italy"],
         "Belgium": ["Netherlands", "Luxembourg", "Germany"],
         "Netherlands": ["Germany"], "Luxembourg": ["Germany"],
         "Germany": ["Denmark", "Switzerland", "Austria", "Czechia", "Poland"],
         "Switzerland": ["Italy", "Austria"], "Italy": ["Austria", "Slovenia"],
         "Austria": ["Slovenia", "Czechia", "Slovakia", "Hungary"],
         "Slovenia": ["Hungary"], "Czechia": ["Slovakia", "Poland"],
         "Slovakia": ["Poland", "Hungary"]}
    pairs = sorted({tuple(sorted((a, b))) for a, bs in A.items() for b in bs})
    deg = defaultdict(int)
    for a, b in pairs:
        deg[a] += 1; deg[b] += 1
    hub = max(deg, key=lambda n: (deg[n], n))
    xpos = {n: 80 + i * (880 / (len(order) - 1)) for i, n in enumerate(order)}
    BASE = 420
    body = []
    for a, b in pairs:
        x1, x2 = sorted((xpos[a], xpos[b]))
        r = (x2 - x1) / 2
        focal = hub in (a, b)
        cls = "slope-focal" if focal else "slope"
        op = "" if focal else ' opacity="0.35"'
        body.append(f'      <path class="{cls}" d="M {x1:.1f},{BASE} A {r:.1f} {r:.1f} 0 0 1 {x2:.1f},{BASE}" fill="none" stroke-width="{1.5 if focal else 1}"{op}/>')
    for n in order:
        x = xpos[n]
        focal = n == hub
        cls = "dot-accent" if focal else "dot"
        partners = sorted(p for a, b in pairs for p in ((b,) if a == n else (a,) if b == n else ()))
        tip = f"*{deg[n]} land borders* in this set|" + ", ".join(partners)
        body.append(f'      <circle class="{cls}" cx="{x:.1f}" cy="{BASE}" r="{5 if focal else 4}" data-tip-label="{n}" data-tip="{tip}"/>')
        body.append(f'      <text class="sub" x="{x:.1f}" y="{BASE + 24}" font-size="8" transform="rotate(-42 {x:.1f} {BASE + 24})" style="text-anchor:end">{n}</text>')
    body.append(f'      <line class="axis" x1="60" y1="{BASE}" x2="960" y2="{BASE}" stroke-width="1"/>')
    body.append(f'      <text class="sub" x="60" y="560" font-size="8" letter-spacing="0.06em">'
                f'{len(pairs)} SHARED LAND BORDERS AMONG 16 COUNTRIES, ORDERED ROUGHLY WEST TO EAST · MICROSTATES AND SEA BORDERS OMITTED</text>')
    emit("europe-borders-arc", "Arc diagram · shared borders",
         "Who borders whom",
         "Sixteen countries on one line, every shared land border an arc. The accent arcs belong to Germany - nine neighbours, the most connected country in Europe.",
         "Arc diagram of land borders among sixteen western and central European countries; Germany is the hub with nine neighbours in the set.",
         "\n".join(body), "0 0 1000 580")


# ===========================================================================
# 10. BUBBLE (Gapminder) - health vs wealth, sized by population (OWID 2023)
# ===========================================================================
def bubble():
    pts = []
    for r in rows("life-expectancy-vs-gdp-per-capita"):
        if r["Year"] == "2022" and r["Code"] and len(r["Code"]) == 3 and r["Code"] != "OWID_WRL":
            g, le, p = fnum(r["GDP per capita"]), fnum(r["Life expectancy at birth"]), fnum(r["Population"])
            if g and le and p:
                pts.append((r["Entity"], g, le, p))
    pts.sort(key=lambda t: -t[3])   # draw big bubbles first so small stay clickable
    X0, X1, Y0, Y1 = 100, 940, 80, 480
    glo, ghi = 500, 160000
    llo, lhi = 50, 90
    xv = lambda g: X0 + (math.log10(g) - math.log10(glo)) / (math.log10(ghi) - math.log10(glo)) * (X1 - X0)
    yv = lambda l: Y1 - (l - llo) / (lhi - llo) * (Y1 - Y0)
    rmax = max(p for _, _, _, p in pts)
    rv = lambda p: 3 + math.sqrt(p / rmax) * 34
    body = []
    for v in (1000, 3000, 10000, 30000, 100000):
        x = xv(v)
        body.append(f'      <line class="grid" x1="{x:.0f}" y1="{Y0}" x2="{x:.0f}" y2="{Y1}" stroke-width="0.8"/>')
        body.append(f'      <text class="axis-label sub" x="{x:.0f}" y="{Y1 + 24}" font-size="8" text-anchor="middle">${v // 1000}k</text>')
    for v in (50, 60, 70, 80, 90):
        y = yv(v)
        body.append(f'      <line class="grid" x1="{X0}" y1="{y:.0f}" x2="{X1}" y2="{y:.0f}" stroke-width="0.8"/>')
        body.append(f'      <text class="axis-label sub" x="{X0 - 12}" y="{y + 3:.0f}" font-size="8" text-anchor="end">{v}</text>')
    labeled = {"China", "India", "United States", "Nigeria", "Japan", "Germany",
               "Brazil", "Indonesia", "Ethiopia", "Norway"}
    for name, g, le, p in pts:
        if not (glo <= g <= ghi and llo <= le <= lhi):
            continue
        x, y, r = xv(g), yv(le), rv(p)
        focal = name == "China"
        cls = "dot-accent" if focal else "dot"
        op = "" if focal else ' opacity="0.35"'
        tip = (f"GDP per capita *${g:,.0f}* · life expectancy *{le:.1f}*|"
               f"population {p / 1e6:,.0f} million|Our World in Data, 2022")
        body.append(f'      <circle class="{cls}" cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}"{op} '
                    f'stroke="var(--color-paper)" stroke-width="1" data-tip-label="{name}" data-tip="{tip}"/>')
        if name in labeled:
            body.append(f'      <text class="name" x="{x:.1f}" y="{y - r - 6:.1f}" font-size="9" text-anchor="middle">{name}</text>')
    body.append(f'      <text class="sub" x="{(X0 + X1) // 2}" y="{Y1 + 48}" font-size="9" text-anchor="middle" letter-spacing="0.1em">GDP PER CAPITA, INTERNATIONAL-$ (PPP), LOG SCALE</text>')
    body.append(f'      <text class="sub" x="60" y="72" font-size="9" letter-spacing="0.1em">LIFE EXPECTANCY, YEARS</text>')
    body.append('      <text class="sub" x="60" y="568" font-size="8" letter-spacing="0.06em">'
                'THE GAPMINDER VIEW · BUBBLE AREA = POPULATION · EVERY COUNTRY WITH COMPLETE 2022 DATA · OUR WORLD IN DATA (UN WPP / WORLD BANK)</text>')
    emit("health-wealth-bubble", "Bubble chart · health & wealth",
         "The health and wealth of nations",
         "Hans Rosling's famous view, one frame of it (2022): richer is healthier, the slope flattens past thirty thousand dollars, and the two giant bubbles - China in accent, India beside it - carry a third of humanity.",
         "Gapminder-style bubble chart of GDP per capita against life expectancy for all countries in 2022, bubbles sized by population.",
         "\n".join(body), "0 0 1000 592")


# ===========================================================================
# 11. RIDGELINE - a year of temperatures in eight cities (WMO normals)
# ===========================================================================
def ridgeline():
    cities = [  # name, 12 monthly mean temps degC (1991-2020 climate normals, rounded)
        ("Reykjavik", [0, 0, 1, 3, 7, 10, 12, 11, 8, 5, 2, 0]),
        ("Moscow", [-6, -6, -1, 7, 13, 17, 19, 17, 11, 5, -1, -4]),
        ("London", [6, 6, 8, 10, 14, 17, 19, 19, 16, 12, 8, 6]),
        ("New York", [1, 2, 6, 12, 17, 23, 26, 25, 21, 15, 9, 4]),
        ("Sydney", [23, 23, 21, 19, 16, 13, 13, 14, 16, 18, 20, 22]),
        ("Dubai", [19, 20, 23, 27, 31, 33, 35, 36, 33, 29, 25, 21]),
        ("Mumbai", [24, 25, 27, 29, 30, 29, 28, 27, 27, 28, 27, 25]),
        ("Singapore", [27, 27, 28, 28, 29, 29, 28, 28, 28, 28, 27, 27]),
    ]
    MONTHS = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]
    X0, X1 = 240, 920
    ROW, AMP = 56, 2.6   # row pitch; px per degC
    xs = [X0 + i * (X1 - X0) / 11 for i in range(12)]
    body = []
    for i, m in enumerate(MONTHS):
        body.append(f'      <text class="sub" x="{xs[i]:.0f}" y="600" font-size="8" text-anchor="middle">{m}</text>')

    def smooth(points):
        p = [points[0]] + list(points) + [points[-1]]
        d = ""
        for i in range(1, len(p) - 2):
            c1 = (p[i][0] + (p[i + 1][0] - p[i - 1][0]) / 6, p[i][1] + (p[i + 1][1] - p[i - 1][1]) / 6)
            c2 = (p[i + 1][0] - (p[i + 2][0] - p[i][0]) / 6, p[i + 1][1] - (p[i + 2][1] - p[i][1]) / 6)
            d += f" C {c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p[i + 1][0]:.1f},{p[i + 1][1]:.1f}"
        return d

    for k, (name, temps) in enumerate(cities):
        base = 128 + k * ROW
        up = [(xs[i], base - t * AMP) for i, t in enumerate(temps)]
        focal = name == "Sydney"   # the inverted ridge - southern hemisphere
        cls = "cell-focal" if focal else "cell"
        op = "" if focal else ' opacity="0.25"'
        lo, hi = min(temps), max(temps)
        tip = f"monthly means *{lo}° to {hi}°C*|1991-2020 climate normals (WMO)|" + \
              ("winter in July - southern hemisphere" if focal else f"annual swing {hi - lo}°C")
        d = (f"M {up[0][0]:.1f},{up[0][1]:.1f}" + smooth(up)
             + f" L {xs[-1]:.1f},{base} L {xs[0]:.1f},{base} Z")
        body.append(f'      <path class="{cls}" d="{d}"{op} data-tip-label="{name}" data-tip="{tip}"/>')
        body.append(f'      <line class="hairline grid" x1="{X0}" y1="{base}" x2="{X1}" y2="{base}" stroke-width="0.8"/>')
        body.append(f'      <text class="name" x="{X0 - 16}" y="{base - 2}" font-size="11" text-anchor="end">{name}</text>')
        body.append(f'      <text class="sub" x="{X1 + 12}" y="{base - 2}" font-size="8">{min(temps)}..{max(temps)}°</text>')
    body.append('      <text class="sub" x="60" y="640" font-size="8" letter-spacing="0.06em">'
                'MEAN MONTHLY TEMPERATURE, °C, 1991-2020 CLIMATE NORMALS (WMO, ROUNDED) · SHARED SCALE: 1°C = 2.6PX ON EVERY RIDGE · '
                'RIDGES OVERLAP BY DESIGN</text>')
    emit("city-temps-ridgeline", "Ridgeline · city climates",
         "A year of weather, eight skylines",
         "Each ridge is one city's year. Singapore barely breathes, Moscow heaves through 25 degrees, and the accent ridge - Sydney - is upside down because its winter is everyone else's July.",
         "Ridgeline plot of mean monthly temperatures for eight world cities; Sydney's inverted curve marks the southern hemisphere.",
         "\n".join(body), "0 0 1000 664")


# ===========================================================================
# 12. SMALL MULTIPLES - CO2 per capita, twelve countries (OWID)
# ===========================================================================
def smallmult():
    want = ["United States", "Australia", "Russia", "Germany", "Japan", "China",
            "United Kingdom", "South Africa", "France", "Brazil", "India", "World"]
    series = defaultdict(dict)
    for r in rows("co-emissions-per-capita"):
        if r["Entity"] in want:
            y = int(r["Year"])
            if 1950 <= y <= 2023:
                v = fnum(r["CO₂ emissions per capita"])
                if v is not None:
                    series[r["Entity"]][y] = v
    VMAX = 24   # shared scale - the honest choice; the US peak defines it
    CW, CH, PX0, PY0, GX, GY = 200, 108, 76, 72, 28, 48
    body = []
    for k, name in enumerate(want):
        gx = PX0 + (k % 4) * (CW + GX)
        gy = PY0 + (k // 4) * (CH + GY)
        pts = sorted(series[name].items())
        xs = lambda yr: gx + (yr - 1950) / 73 * CW
        ys = lambda v: gy + CH - min(v, VMAX) / VMAX * CH
        d = "M " + " L ".join(f"{xs(y):.1f},{ys(v):.1f}" for y, v in pts)
        focal = name == "China"
        cls = "slope-focal" if focal else "slope"
        body.append(f'      <line class="axis" x1="{gx}" y1="{gy + CH}" x2="{gx + CW}" y2="{gy + CH}" stroke-width="1"/>')
        body.append(f'      <line class="grid" x1="{gx}" y1="{gy + CH - 10 / VMAX * CH:.0f}" x2="{gx + CW}" y2="{gy + CH - 10 / VMAX * CH:.0f}" stroke-width="0.8"/>')
        last_y, last_v = pts[-1]
        first_v = pts[0][1]
        tip = f"1950: *{first_v:.1f}t* · {last_y}: *{last_v:.1f}t* per person|{'up' if last_v > first_v else 'down'} {abs(last_v - first_v):.1f}t across the window"
        body.append(f'      <path class="{cls}" d="{d}" fill="none" stroke-width="{1.8 if focal else 1.2}" data-tip-label="{name}" data-tip="{tip}"/>')
        ncls = "name" if focal else "sub"
        body.append(f'      <text class="{ncls}" x="{gx}" y="{gy - 8}" font-size="10">{name}</text>')
        body.append(f'      <text class="sub" x="{gx + CW}" y="{gy - 8}" font-size="8" text-anchor="end">{last_v:.1f}t</text>')
    body.append('      <text class="sub" x="76" y="60" font-size="8" letter-spacing="0.1em">TONNES CO2 PER PERSON PER YEAR · SHARED 0-24t SCALE · FAINT LINE = 10t</text>')
    body.append('      <text class="sub" x="76" y="564" font-size="8" letter-spacing="0.06em">'
                'FOSSIL CO2 EMISSIONS PER CAPITA, 1950-2023 · OUR WORLD IN DATA (GLOBAL CARBON BUDGET) · '
                'SAME SCALE IN EVERY PANEL - THAT IS THE POINT</text>')
    emit("co2-small-multiples", "Small multiples · CO2 per person",
         "Twelve carbon stories, one scale",
         "Every panel shares the same axis, so the shapes are comparable: America's long plateau and decline, China's accent line climbing five-fold since 2000, India barely off the floor - and the world line creeping upward through it all.",
         "Small-multiples grid of CO2 emissions per capita for eleven countries and the world, 1950 to 2023, on one shared scale.",
         "\n".join(body), "0 0 1000 588")


# ===========================================================================
# 13. MARIMEKKO - electricity by region x source (OWID/Ember 2023)
# ===========================================================================
def marimekko():
    ents = {"Asia", "North America", "Europe", "South America", "Africa", "Oceania"}
    latest = {}
    for r in rows("electricity-prod-source-stacked"):
        if r["Entity"] in ents:
            y = int(r["Year"])
            # a row is only a candidate if it actually carries generation data -
            # OWID ships empty placeholder rows for some entity-years
            if not any(fnum(r[c]) for c in ("Coal", "Gas", "Hydropower", "Solar", "Wind")):
                continue
            if r["Entity"] not in latest or y > latest[r["Entity"]][0]:
                latest[r["Entity"]] = (y, r)
    year = min(v[0] for v in latest.values())
    segs = [  # label, columns
        ("Coal", ["Coal"]), ("Gas", ["Gas"]), ("Hydro", ["Hydropower"]),
        ("Nuclear", ["Nuclear"]), ("Wind & solar", ["Wind", "Solar"]),
        ("Other", ["Oil", "Bioenergy", "Other renewables"]),
    ]
    data = []
    for ent, (y, r) in latest.items():
        vals = {lab: sum(fnum(r[c]) or 0 for c in cols) for lab, cols in segs}
        data.append((ent, sum(vals.values()), vals))
    data.sort(key=lambda d: -d[1])
    grand = sum(t for _, t, _ in data)
    X0, X1, Y0, Y1 = 80, 960, 96, 496
    ramp = {"Coal": 0.8, "Gas": 0.55, "Hydro": 0.38, "Nuclear": 0.26, "Other": 0.15}
    body = []
    x = X0
    for ent, tot, vals in data:
        w = tot / grand * (X1 - X0)
        y = Y0
        for lab, _ in segs:
            h = vals[lab] / tot * (Y1 - Y0)
            focal = lab == "Wind & solar"
            cls = "cell-focal" if focal else "cell"
            op = "" if focal else f' opacity="{ramp[lab]}"'
            share = vals[lab] / tot * 100
            tip = f"*{vals[lab]:,.0f} TWh* {lab.lower()} - {share:.0f}% of {ent}|region total {tot:,.0f} TWh|Ember via Our World in Data, {year}"
            body.append(f'      <rect class="{cls}" x="{x:.1f}" y="{y:.1f}" width="{max(w - 3, 1):.1f}" height="{max(h - 2, 1):.1f}"{op} '
                        f'data-tip-label="{ent} · {lab}" data-tip="{tip}"/>')
            if w > 90 and h > 26:
                light = (not focal) and ramp.get(lab, 1) <= 0.4
                lcls = "name" if light else "cell-label"
                body.append(f'      <text class="{lcls}" x="{x + 10:.1f}" y="{y + 17:.1f}" font-size="9">{lab} {share:.0f}%</text>')
            y += h
        if w > 80:   # narrow columns stay unlabelled - the footnote says so
            body.append(f'      <text class="name" x="{x + (w - 3) / 2:.1f}" y="{Y1 + 24}" font-size="11" text-anchor="middle">{ent}</text>')
            body.append(f'      <text class="sub" x="{x + (w - 3) / 2:.1f}" y="{Y1 + 40}" font-size="8" text-anchor="middle">{tot / 1000:.1f}k TWh</text>')
        x += w
    body.append(f'      <text class="sub" x="60" y="560" font-size="8" letter-spacing="0.06em">'
                f'COLUMN WIDTH = REGION SHARE OF WORLD GENERATION · SEGMENT HEIGHT = SOURCE SHARE WITHIN REGION · '
                f'EMBER VIA OUR WORLD IN DATA, {year} · SMALL REGIONS UNLABELLED, NOT OMITTED</text>')
    emit("electricity-marimekko", "Marimekko · world electricity",
         "Who makes electricity, and from what",
         "Width is how much a region generates; height is what it is made of. Asia is half the world's electricity and half of that is coal - while the accent band, wind and solar, is widest in Europe.",
         "Marimekko chart of electricity generation by region and source; Asia's wide coal-heavy column dominates, with wind and solar highlighted across all regions.",
         "\n".join(body), "0 0 1000 584")


# ===========================================================================
# 14. WARMING STRIPES - global temperature anomaly, 1850-2024
# ===========================================================================
def stripes():
    anoms = []
    for r in rows("temperature-anomaly"):
        if r["Entity"] in ("World", "Global"):
            v = fnum(r["Average"])
            if v is not None:
                anoms.append((int(r["Year"]), v))
    anoms.sort()
    lo = min(v for _, v in anoms)
    hi = max(v for _, v in anoms)
    X0, X1, Y0, Y1 = 60, 960, 96, 440
    n = len(anoms)
    w = (X1 - X0) / n
    body = []
    for i, (yr, v) in enumerate(anoms):
        # diverging on the EXISTING palette: link (cold) <-> accent (warm),
        # paper at zero. Opacity encodes magnitude - no new hues invented.
        if v >= 0:
            cls, op = "cell-focal", max(0.06, v / hi)
        else:
            cls, op = "cell-cold", max(0.06, v / lo)
        tip = f"*{v:+.2f}°C* vs 1961-1990 average|HadCRUT5 via Our World in Data"
        body.append(f'      <rect class="{cls}" x="{X0 + i * w:.2f}" y="{Y0}" width="{w + 0.3:.2f}" height="{Y1 - Y0}" '
                    f'opacity="{op:.2f}" data-tip-label="{yr}" data-tip="{tip}"/>')
    for yr in (1850, 1900, 1950, 2000, 2024):
        i = next(i for i, (y, _) in enumerate(anoms) if y == yr)
        body.append(f'      <text class="sub" x="{X0 + i * w:.0f}" y="{Y1 + 24}" font-size="8" letter-spacing="0.1em">{yr}</text>')
    body.append(f'      <text class="sub" x="60" y="500" font-size="8" letter-spacing="0.06em">'
                f'ONE STRIPE = ONE YEAR ({n} YEARS) · ANOMALY VS 1961-1990 MEAN, {lo:+.2f} TO {hi:+.2f}°C · '
                f'HADCRUT5 VIA OUR WORLD IN DATA · AFTER ED HAWKINS</text>')
    extra = "    .cell-cold { fill: var(--color-link); }\n"
    emit("warming-stripes", "Warming stripes · 1850-2024",
         "One stripe per year since 1850",
         "Ed Hawkins' famous form on this design system's own two poles: the link blue for cool years, the accent for warm ones, paper for the average. No axis needed - the drift to the right says everything.",
         "Warming stripes of 177 years of global temperature anomaly from 1850; blue early decades give way to increasingly intense warm stripes toward the present.",
         "\n".join(body), "0 0 1000 524")
    # inject the one extra class the template lacks
    f = HERE / "dataviz" / "warming-stripes.html"
    t = f.read_text(encoding="utf-8")
    t = t.replace("    .range      { stroke: var(--color-rule-solid); }",
                  "    .range      { stroke: var(--color-rule-solid); }\n" + extra)
    f.write_text(t, encoding="utf-8")


# ===========================================================================
# 15. PUNCH CARD - when America is born (538 births 2000-2014)
# ===========================================================================
def punchcard():
    sums = defaultdict(float)
    counts = defaultdict(int)
    for r in rows("births"):
        key = (int(r["month"]), int(r["day_of_week"]))   # dow: 1=Mon..7=Sun
        sums[key] += int(r["births"])
        counts[key] += 1
    avg = {k: sums[k] / counts[k] for k in sums}
    lo, hi = min(avg.values()), max(avg.values())
    peak = max(avg, key=avg.get)
    MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    X0, Y0, CW, CH, GAP = 148, 96, 60, 44, 6
    body = []
    for m in range(12):
        body.append(f'      <text class="sub" x="{X0 + m * (CW + GAP) + CW // 2}" y="{Y0 - 16}" font-size="9" text-anchor="middle">{MONTHS[m]}</text>')
    for d in range(7):
        body.append(f'      <text class="name" x="{X0 - 20}" y="{Y0 + d * (CH + GAP) + CH // 2 + 4}" font-size="11" text-anchor="end">{DAYS[d]}</text>')
    for m in range(12):
        for d in range(7):
            v = avg[(m + 1, d + 1)]
            x = X0 + m * (CW + GAP)
            y = Y0 + d * (CH + GAP)
            t = (v - lo) / (hi - lo)
            focal = (m + 1, d + 1) == peak
            cls = "cell-focal" if focal else "cell"
            op = "" if focal else f' opacity="{0.08 + t * 0.84:.2f}"'
            tip = (f"*{v:,.0f} births* on an average {DAYS[d]} in {MONTHS[m]}|"
                   f"{(v - lo) / lo * 100:.0f}% above the quietest cell" if v > lo else f"*{v:,.0f} births* - the quietest cell")
            body.append(f'      <rect class="{cls}" x="{x}" y="{y}" width="{CW}" height="{CH}" rx="3"{op} '
                        f'data-tip-label="{DAYS[d]} · {MONTHS[m]}" data-tip="{tip}"/>')
    body.append('      <text class="sub" x="148" y="470" font-size="8" letter-spacing="0.06em">'
                'AVERAGE US BIRTHS PER DAY, BY MONTH AND WEEKDAY, 2000-2014 · FIVETHIRTYEIGHT / US SSA · '
                'THE PALE WEEKEND COLUMNS ARE SCHEDULED DELIVERIES TAKING WEEKDAYS OFF</text>')
    emit("births-punchcard", "Punch card · when America is born",
         "Wednesdays in September",
         "Fifteen years of American birth certificates in one grid. The weekend rows go pale - inductions and cesareans keep office hours - and the accent cell is the single busiest square: September Wednesdays, nine months after the winter holidays.",
         "Punch-card heatmap of average US daily births by month and weekday from 2000 to 2014; weekends are markedly quieter and September Wednesdays are the peak.",
         "\n".join(body), "0 0 1000 496")


if __name__ == "__main__":
    treemap(); sankey(); slope(); dumbbell(); waffle(); bump(); stream()
    beeswarm(); arc(); bubble(); ridgeline(); smallmult(); marimekko()
    stripes(); punchcard()
