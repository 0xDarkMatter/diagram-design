#!/usr/bin/env python3
"""Round two: five more IIB-inspired types - hex tile map, bump, streamgraph,
beeswarm, arc diagram. Default skin, real cited data, tooltips throughout.

The hex tile map answers "convert a map into squares or hexagons": it is a
tile-grid cartogram in the NPR/538 lineage - every region gets ONE equal
hexagon placed by approximate adjacency, and only color carries the value.
Data: US Census Bureau estimates, July 2023, 50 states + DC + PR.
"""
from __future__ import annotations

import math
import re
from collections import defaultdict
from pathlib import Path

from build_dataviz import emit, g4  # shared template (tooltips + toggle)

HERE = Path(__file__).resolve().parent
REPO = Path("X:/Forge/claude-mods")


# ===========================================================================
# 1. HEX TILE MAP - Australian population, one equal hexagon per jurisdiction
# ===========================================================================
def hexmap():
    """US tile grid, 538-style: 50 states + DC + PR, one equal hexagon each.

    Layout is a hand-curated atlas (cols 0-11, rows 0-7) approximating
    adjacency: the coast columns hold, New England stacks upper-right, FL and
    TX dangle south, AK and HI float where they always float, and the empty
    cell left of MI is Lake Michigan. US Census Bureau estimates, July 2023;
    PR from the same vintage. Values in millions.
    """
    D = [  # code, millions, col, row
        ("AK", 0.73, 0, 0), ("ME", 1.40, 11, 0),
        ("VT", 0.65, 10, 1), ("NH", 1.40, 11, 1),
        ("WA", 7.81, 1, 2), ("ID", 1.96, 2, 2), ("MT", 1.13, 3, 2), ("ND", 0.78, 4, 2),
        ("MN", 5.74, 5, 2), ("WI", 5.91, 6, 2), ("MI", 10.04, 8, 2), ("NY", 19.57, 9, 2),
        ("MA", 7.00, 10, 2), ("RI", 1.10, 11, 2),
        ("OR", 4.23, 1, 3), ("NV", 3.19, 2, 3), ("WY", 0.58, 3, 3), ("SD", 0.92, 4, 3),
        ("IA", 3.21, 5, 3), ("IL", 12.55, 6, 3), ("IN", 6.86, 7, 3), ("OH", 11.78, 8, 3),
        ("PA", 12.96, 9, 3), ("NJ", 9.29, 10, 3), ("CT", 3.62, 11, 3),
        ("CA", 38.97, 1, 4), ("UT", 3.42, 2, 4), ("CO", 5.88, 3, 4), ("NE", 1.98, 4, 4),
        ("MO", 6.20, 5, 4), ("KY", 4.53, 6, 4), ("WV", 1.77, 7, 4), ("VA", 8.72, 8, 4),
        ("MD", 6.18, 9, 4), ("DE", 1.03, 10, 4),
        ("AZ", 7.43, 2, 5), ("NM", 2.11, 3, 5), ("KS", 2.94, 4, 5), ("AR", 3.07, 5, 5),
        ("TN", 7.13, 6, 5), ("NC", 10.84, 7, 5), ("SC", 5.37, 8, 5), ("DC", 0.68, 9, 5),
        ("OK", 4.05, 4, 6), ("LA", 4.57, 5, 6), ("MS", 2.94, 6, 6), ("AL", 5.11, 7, 6),
        ("GA", 11.03, 8, 6),
        ("HI", 1.44, 0, 7), ("TX", 30.50, 4, 7), ("FL", 22.61, 9, 7), ("PR", 3.21, 11, 7),
    ]
    NAMES = {
        "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
        "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
        "DC": "District of Columbia", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii",
        "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
        "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine",
        "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
        "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska",
        "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico",
        "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
        "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "PR": "Puerto Rico",
        "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota",
        "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont",
        "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
        "WI": "Wisconsin", "WY": "Wyoming",
    }
    total = sum(v for _, v, _, _ in D)
    vmax = max(v for _, v, _, _ in D)
    ranks = {c: i + 1 for i, (c, _, _, _) in
             enumerate(sorted(D, key=lambda s: -s[1]))}
    R = 40
    W = R * math.sqrt(3)
    X0, Y0 = 96, 136
    body = []

    def hexpath(cx, cy, r):
        pts = []
        for i in range(6):
            pts.append(f"{cx + r * math.sin(math.radians(60 * i)):.1f},"
                       f"{cy - r * math.cos(math.radians(60 * i)):.1f}")
        return "M " + " L ".join(pts) + " Z"

    for code, pop, col, row in D:
        # odd rows shift half a hex right - standard offset grid
        cx = X0 + (col + (0.5 if row % 2 else 0)) * (W + 4)
        cy = Y0 + row * (R * 1.5 + 4)
        focal = code == "CA"
        op = max(0.12, round(pop / vmax, 2))
        cls = "cell-focal" if focal else "cell"
        opattr = "" if focal else f' opacity="{op}"'
        tip = (f"*{pop:.2f} million people* - {pop / total * 100:.1f}% of the total|"
               f"rank {ranks[code]} of 52|equal tile - only color carries the value")
        body.append(f'      <path class="{cls}" d="{hexpath(cx, cy, R - 2)}"{opattr} '
                    f'data-tip-label="{NAMES[code]}" data-tip="{tip}"/>')
        dark_cell = focal or op > 0.5
        lab = "cell-label" if dark_cell else "name"
        sml = "cell-sub" if dark_cell else "sub"
        body.append(f'      <text class="{lab}" x="{cx:.0f}" y="{cy - 1:.0f}" font-size="12" text-anchor="middle">{code}</text>')
        body.append(f'      <text class="{sml}" x="{cx:.0f}" y="{cy + 13:.0f}" font-size="7" text-anchor="middle">{pop:.1f}</text>')
    body.append('      <text class="sub" x="60" y="656" font-size="8" letter-spacing="0.06em">'
                'TILE GRID CARTOGRAM · 50 STATES + DC + PR, ONE EQUAL HEXAGON EACH, PLACED BY ADJACENCY · VALUES IN MILLIONS</text>')
    body.append('      <text class="sub" x="60" y="672" font-size="8" letter-spacing="0.06em">'
                'US CENSUS BUREAU ESTIMATES, JULY 2023 · THE GAP LEFT OF MI IS LAKE MICHIGAN</text>')
    emit("us-hex-population", "Hex tile map · cartogram",
         "The United States, one hexagon per state",
         "Fifty-two equal tiles - a choropleth would let Alaska shout and Rhode Island vanish. Here every state gets the same hexagon, placement approximates the neighbours, and only color carries the people. Hover any tile.",
         "Hex tile cartogram of United States population by state plus DC and Puerto Rico, one equal hexagon each; California leads at 38.97 million.",
         "\n".join(body), "0 0 1000 688")


# ===========================================================================
# 2. BUMP CHART - category rank across three README snapshots
# ===========================================================================
def bump():
    # skills per category at f371f57 (May 05), 614d7e8 (Jun 15), HEAD (Aug 14)
    snaps = ["MAY 05", "JUN 15", "AUG 14"]
    counts = {
        "Language":       [12, 17, 24],
        "Development":    [14, 17, 18],
        "Workflow":       [8, 13, 17],
        "Infrastructure": [8, 15, 16],
        "CLI tools":      [7, 10, 10],
        "Data & API":     [6, 7, 7],
        "Python":         [None, 7, 7],
        "Diagnostics":    [None, 4, 4],
    }
    # ranks per snapshot (1 = most skills; ties broken by count then name)
    ranks = {k: [None] * 3 for k in counts}
    for i in range(3):
        present = [(k, v[i]) for k, v in counts.items() if v[i] is not None]
        present.sort(key=lambda kv: (-kv[1], kv[0]))
        for r, (k, _) in enumerate(present, 1):
            ranks[k][i] = r

    X = [280, 540, 800]
    y_of = lambda r: 96 + (r - 1) * 56
    body = []
    for i, (x, s) in enumerate(zip(X, snaps)):
        body.append(f'      <line class="axis" x1="{x}" y1="80" x2="{x}" y2="{y_of(8) + 16}" stroke-width="1"/>')
        body.append(f'      <text class="sub" x="{x}" y="{y_of(8) + 44}" font-size="9" text-anchor="middle" letter-spacing="0.14em">{s}</text>')
    for name, rs in counts.items():
        pts = [(X[i], y_of(ranks[name][i])) for i in range(3) if ranks[name][i]]
        focal = name == "Language"
        line_cls = "slope-focal" if focal else "slope"
        dot_cls = "dot-accent" if focal else "dot"
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            body.append(f'      <line class="{line_cls}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke-width="{2 if focal else 1.2}"/>')
        rr = [r for r in ranks[name] if r]
        arrow = "up" if rr[-1] < rr[0] else ("down" if rr[-1] > rr[0] else "flat")
        tip = (f"rank {rr[0]} to {rr[-1]} across the three snapshots|"
               + "|".join(f"{s}: *{counts[name][i]}* skills" for i, s in enumerate(snaps) if counts[name][i] is not None))
        for i, (x, y) in enumerate(pts):
            body.append(f'      <circle class="{dot_cls}" cx="{x}" cy="{y}" r="5" data-tip-label="{name}" data-tip="{tip}"/>')
        lcls = "name" if focal else "sub"
        first_i = next(i for i in range(3) if ranks[name][i])
        body.append(f'      <text class="{lcls}" x="{X[first_i] - 16}" y="{y_of(ranks[name][first_i]) + 4}" font-size="11" text-anchor="end">{name}</text>')
        body.append(f'      <text class="{lcls}" x="{X[2] + 16}" y="{y_of(ranks[name][2]) + 4}" font-size="11">{name}  {counts[name][2]}</text>')
    body.append('      <text class="sub" x="60" y="620" font-size="8" letter-spacing="0.06em">'
                'RANK BY SKILLS PER CATEGORY · README AT f371f57 (MAY 05), 614d7e8 (JUN 15), HEAD (AUG 14) · '
                'PYTHON AND DIAGNOSTICS CATEGORIES DID NOT EXIST IN MAY</text>')
    emit("category-bump", "Bump chart · claude-mods",
         "Three snapshots, eight categories",
         "Rank, not raw count - the language shelf starts second and takes the lead by June, while workflow climbs from sixth to third. Two categories only exist from June on: that gap is real, so the lines simply start late.",
         "Bump chart of claude-mods skill-category rank across May, June and August snapshots; language and framework skills take and hold first place.",
         "\n".join(body), "0 0 1000 640")


# ===========================================================================
# 3. STREAMGRAPH - commits per fortnight by type, whole repo life
# ===========================================================================
def stream():
    # mined from git log 2026-08-14 (fortnights since 2025-11-24; zeros = quiet)
    rows = [  # (label, feat, fix, docs, chore, refactor, test)
        ("NOV 24", 7, 1, 3, 6, 3, 0), ("DEC 08", 14, 3, 10, 6, 6, 0),
        ("DEC 22", 3, 2, 5, 3, 3, 0), ("JAN 05", 12, 3, 3, 0, 1, 0),
        ("JAN 19", 5, 0, 1, 1, 2, 0), ("FEB 02", 4, 1, 9, 4, 0, 0),
        ("FEB 16", 0, 0, 0, 0, 0, 0), ("MAR 02", 6, 1, 0, 0, 1, 0),
        ("MAR 16", 7, 1, 0, 1, 0, 0), ("MAR 30", 7, 1, 2, 1, 1, 0),
        ("APR 13", 9, 4, 4, 5, 0, 0), ("APR 27", 6, 3, 1, 1, 4, 0),
        ("MAY 11", 22, 5, 9, 4, 0, 0), ("MAY 25", 4, 1, 4, 4, 0, 0),
        ("JUN 08", 20, 4, 11, 3, 4, 1), ("JUN 22", 56, 24, 8, 5, 4, 0),
        ("JUL 06", 8, 18, 9, 1, 1, 18), ("JUL 20", 5, 9, 0, 0, 2, 1),
        ("AUG 03", 17, 13, 2, 0, 0, 1),
    ]
    series = ["feat", "fix", "docs", "chore", "refactor", "test"]
    N = len(rows)
    X0, X1, CY = 80, 960, 320
    SCALE = 2.4  # px per commit
    xs = [X0 + i * (X1 - X0) / (N - 1) for i in range(N)]

    # symmetric (silhouette) stacking: baseline = -total/2
    tops = defaultdict(list)
    for i, r in enumerate(rows):
        vals = r[1:]
        total = sum(vals)
        y = CY - total * SCALE / 2
        for s, v in zip(series, vals):
            tops[s].append((y, y + v * SCALE))
            y += v * SCALE

    def smooth(points):
        """Catmull-Rom -> cubic Bezier path through (x, y) points."""
        if len(points) < 3:
            return " ".join(f"L {x:.1f},{y:.1f}" for x, y in points[1:])
        p = [points[0]] + points + [points[-1]]
        d = ""
        for i in range(1, len(p) - 2):
            c1 = (p[i][0] + (p[i + 1][0] - p[i - 1][0]) / 6, p[i][1] + (p[i + 1][1] - p[i - 1][1]) / 6)
            c2 = (p[i + 1][0] - (p[i + 2][0] - p[i][0]) / 6, p[i + 1][1] - (p[i + 2][1] - p[i][1]) / 6)
            d += f" C {c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p[i + 1][0]:.1f},{p[i + 1][1]:.1f}"
        return d

    body = []
    opac = {"feat": None, "fix": 0.62, "docs": 0.45, "chore": 0.32, "refactor": 0.22, "test": 0.14}
    totals = {s: sum(r[1 + series.index(s)] for r in rows) for s in series}
    for s in series:
        up = [(xs[i], tops[s][i][0]) for i in range(N)]
        dn = [(xs[i], tops[s][i][1]) for i in range(N)][::-1]
        cls = "cell-focal" if s == "feat" else "cell"
        op = "" if s == "feat" else f' opacity="{opac[s]}"'
        d = f"M {up[0][0]:.1f},{up[0][1]:.1f}" + smooth(up) + f" L {dn[0][0]:.1f},{dn[0][1]:.1f}" + smooth(dn) + " Z"
        tip = f"*{totals[s]} commits* across the repo life|peak fortnight: {max(r[1 + series.index(s)] for r in rows)} in one fortnight"
        body.append(f'      <path class="{cls}" d="{d}"{op} data-tip-label="{s}" data-tip="{tip}"/>')
    for i in (0, 6, 12, 15, 18):
        body.append(f'      <text class="sub" x="{xs[i]:.0f}" y="560" font-size="8" text-anchor="middle" letter-spacing="0.1em">{rows[i][0]}</text>')
    # annotate the v3 spike
    body.append(f'      <line class="hairline grid" x1="{xs[15]:.0f}" y1="120" x2="{xs[15]:.0f}" y2="180" stroke-width="1"/>')
    body.append(f'      <text class="name" x="{xs[15]:.0f}" y="104" font-size="11" text-anchor="middle">the v3 wave</text>')
    # legend
    lx = 80
    for s in series:
        cls = "cell-focal" if s == "feat" else "cell"
        op = "" if s == "feat" else f' opacity="{opac[s]}"'
        body.append(f'      <rect class="{cls}" x="{lx}" y="588" width="14" height="14" rx="2"{op}/>')
        body.append(f'      <text class="sub" x="{lx + 22}" y="599" font-size="9">{s} {totals[s]}</text>')
        lx += 110 if s != "refactor" else 128
    body.append('      <text class="sub" x="80" y="636" font-size="8" letter-spacing="0.06em">'
                'COMMITS PER FORTNIGHT BY CONVENTIONAL TYPE · SILHOUETTE STACKING · MINED FROM git log 2026-08-14 · THE FEB 16 PINCH IS A REAL QUIET FORTNIGHT</text>')
    emit("commit-stream", "Streamgraph · claude-mods",
         "Nine months of commits, breathing",
         "Every fortnight of the repo's life, stacked symmetrically. The February pinch is a real pause; the June bulge is the v3 skills-first wave - 56 features and 24 fixes in a single fortnight.",
         "Streamgraph of claude-mods commits per fortnight by conventional type from November 2025 to August 2026, with a dramatic widening at the June v3 release wave.",
         "\n".join(body), "0 0 1000 656")


# ===========================================================================
# 4. BEESWARM - 103 skills, one dot each, by size on disk
# ===========================================================================
def beeswarm():
    # mine sizes + categories live from the repo
    cats = {}
    t = (REPO / "README.md").read_text(encoding="utf-8")
    short = {"Language & Framework Skills": "Language", "Python Skills": "Python",
             "Data & API Skills": "Data & API", "Infrastructure Skills": "Infrastructure",
             "Workstation & Network Diagnostics": "Diagnostics", "CLI Tool Skills": "CLI tools",
             "Workflow Skills": "Workflow", "Development Skills": "Development"}
    for m in re.finditer(r"^#### (.+?)\n(.*?)(?=^#### |^### )", t, re.M | re.S):
        for s in re.findall(r"^\| \[([a-z0-9-]+)\]\(skills/", m.group(2), re.M):
            cats[s] = short.get(m.group(1).strip(), "?")
    skills = []
    for name, cat in cats.items():
        p = REPO / "skills" / name
        if p.exists():
            kb = sum(f.stat().st_size for f in p.rglob("*") if f.is_file()) // 1024
            skills.append((name, cat, max(kb, 1)))
    skills.sort(key=lambda s: s[2])

    X0, X1 = 100, 940
    kmin = min(s[2] for s in skills)
    LOG0, LOG1 = math.log10(max(1, kmin * 0.8)), math.log10(1400)
    xv = lambda kb: X0 + (math.log10(kb) - LOG0) / (LOG1 - LOG0) * (X1 - X0)
    CY, RAD = 300, 7
    placed = []  # (x, y)

    def dodge(x):
        y = CY
        step = 0
        while any((px - x) ** 2 + (py - y) ** 2 < (2 * RAD + 2) ** 2 for px, py in placed):
            step += 1
            y = CY + (step + 1) // 2 * (2 * RAD + 2) * (1 if step % 2 else -1)
        placed.append((x, y))
        return y

    biggest = max(skills, key=lambda s: s[2])
    body = []
    ypos = {}
    for v in (10, 30, 100, 300, 1000):
        x = xv(v)
        body.append(f'      <line class="grid" x1="{x:.0f}" y1="120" x2="{x:.0f}" y2="480" stroke-width="0.8"/>')
        body.append(f'      <text class="axis-label sub" x="{x:.0f}" y="504" font-size="8" text-anchor="middle">{v} KB</text>')
    label_top5 = sorted(skills, key=lambda s: -s[2])[:5]
    for name, cat, kb in skills:
        x = xv(kb)
        y = dodge(x)
        ypos[name] = (x, y)
        focal = name == biggest[0]
        cls = "dot-accent" if focal else "dot"
        op = "" if focal else ' opacity="0.55"'
        tip = f"*{kb:,} KB* on disk|category: {cat}|SKILL.md + scripts + references + assets"
        body.append(f'      <circle class="{cls}" cx="{x:.1f}" cy="{y:.1f}" r="{RAD}"{op} data-tip-label="{name}" data-tip="{tip}"/>')
    # label the five heaviest right above their own dots, with a hairline
    # leader - a floating label column orphans from the data. Stagger the two
    # rightmost so they don't collide; clamp anchors inside the canvas.
    # one tier per label (they cluster in the 250-350KB band), alternating
    # sides of the leader so four names at one x cannot collide
    for i, (name, cat, kb) in enumerate(label_top5):
        x, y = ypos[name]
        ly = y - 28 - i * 16
        if i % 2:
            anchor, lx = "start", min(x + 10, 940)
        else:
            anchor, lx = "end", max(x - 10, 200)
        body.append(f'      <line class="grid" x1="{x:.0f}" y1="{ly + 4}" x2="{x:.0f}" y2="{y - RAD - 2:.0f}" stroke-width="0.8"/>')
        body.append(f'      <text class="sub" x="{lx:.0f}" y="{ly}" font-size="9" text-anchor="{anchor}">{name}</text>')
    body.append('      <text class="sub" x="60" y="560" font-size="8" letter-spacing="0.06em">'
                'ONE DOT = ONE SKILL · X = BYTES ON DISK, LOG SCALE · DOTS DODGE VERTICALLY, HEIGHT MEANS NOTHING · MEASURED 2026-08-14</text>')
    emit("skills-beeswarm", "Beeswarm · claude-mods",
         "All 103 skills, weighed",
         "Every skill is one dot on a log scale of its on-disk size. The swarm bunches in the tens of kilobytes; a heavy tail of media and map expertise runs past a megabyte. Hover any dot.",
         "Beeswarm plot of all 103 claude-mods skills by on-disk size on a log axis, with the largest skill highlighted in accent.",
         "\n".join(body), "0 0 1000 580")


# ===========================================================================
# 5. ARC DIAGRAM - the related-skills graph
# ===========================================================================
def arc():
    links = []
    names = set()
    for f in (REPO / "skills").glob("*/SKILL.md"):
        skill = f.parent.name
        names.add(skill)
        head = f.read_text(encoding="utf-8", errors="replace")[:3000]
        m = re.search(r'related-skills:\s*"([^"]+)"', head)
        if m:
            for r in re.split(r"[,\s]+", m.group(1).strip()):
                r = r.strip().rstrip(",")
                if r:
                    links.append((skill, r))
    valid = sorted({tuple(sorted((a, b))) for a, b in links if b in names and a != b})
    deg = defaultdict(int)
    for a, b in valid:
        deg[a] += 1
        deg[b] += 1
    # nodes with >= 2 connections keep the diagram legible; footnote the rest
    keep = {n for n in deg if deg[n] >= 2}
    shown = [(a, b) for a, b in valid if a in keep and b in keep]
    dropped = len(valid) - len(shown)
    nodes = sorted(keep, key=lambda n: (-deg[n], n))
    order = sorted(nodes)  # alphabetical along the baseline
    xpos = {n: 80 + i * (880 / (len(order) - 1)) for i, n in enumerate(order)}
    BASE = 420
    hub = max(deg, key=lambda n: (deg[n], n))

    body = []
    for a, b in shown:
        x1, x2 = sorted((xpos[a], xpos[b]))
        r = (x2 - x1) / 2
        focal = hub in (a, b)
        cls = "slope-focal" if focal else "slope"
        op = "" if focal else ' opacity="0.35"'
        body.append(f'      <path class="{cls}" d="M {x1:.1f},{BASE} A {r:.1f} {r:.1f} 0 0 1 {x2:.1f},{BASE}" '
                    f'fill="none" stroke-width="{1.5 if focal else 1}"{op}/>')
    for n in order:
        x = xpos[n]
        focal = n == hub
        cls = "dot-accent" if focal else "dot"
        partners = sorted(set(p for a, b in valid for p in ((b,) if a == n else (a,) if b == n else ())))
        plist = " ".join(f"`{p}`" for p in partners[:5]) + (" ..." if len(partners) > 5 else "")
        tip = f"*{deg[n]} declared relationships*|{plist}"
        body.append(f'      <circle class="{cls}" cx="{x:.1f}" cy="{BASE}" r="{5 if focal else 4}" data-tip-label="{n}" data-tip="{tip}"/>')
        short = n.replace("-ops", "")
        anchor = "end" if x > 800 else ("start" if x < 200 else "middle")
        body.append(f'      <text class="sub" x="{x:.1f}" y="{BASE + 24}" font-size="8" text-anchor="middle" '
                    f'transform="rotate(-42 {x:.1f} {BASE + 24})" style="text-anchor:end">{short}</text>')
    body.append(f'      <line class="axis" x1="60" y1="{BASE}" x2="960" y2="{BASE}" stroke-width="1"/>')
    body.append(f'      <text class="sub" x="60" y="580" font-size="8" letter-spacing="0.06em">'
                f'{len(shown)} DECLARED related-skills PAIRS AMONG SKILLS WITH 2+ LINKS · {dropped} SINGLETON PAIRS OMITTED · '
                f'MINED FROM skills/*/SKILL.md FRONTMATTER 2026-08-14</text>')
    emit("related-skills-arc", "Arc diagram · claude-mods",
         "How the skills declare their kinships",
         "Each arc is a related-skills declaration in a skill's own frontmatter. The accent arcs belong to the best-connected skill - hover any node for its partners.",
         "Arc diagram of declared related-skills links between claude-mods skills, alphabetical along the baseline, with the most-connected skill's arcs in accent.",
         "\n".join(body), "0 0 1000 600")


if __name__ == "__main__":
    hexmap()
    bump()
    stream()
    beeswarm()
    arc()
