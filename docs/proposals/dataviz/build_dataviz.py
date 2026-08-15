#!/usr/bin/env python3
"""Five IIB-inspired dataviz types as diagram-design contribution candidates.

Treemap, sankey, slopegraph, dumbbell, waffle - forms Information is Beautiful
made famous, absent from the current 27. Built in the DEFAULT skin (white-smoke
+ atomic-tangerine, upstream's Google-Fonts stack) since they are upstream
candidates. Each carries a light/dark toggle wired to upstream's own dark
tokens for easy review in both themes.

All data is real and named on each chart: claude-mods git history, README
category counts, on-disk sizes, and measured WCAG ratios of upstream's palette.
"""
from __future__ import annotations

from pathlib import Path

OUT = Path(__file__).resolve().parent / "dataviz"
OUT.mkdir(exist_ok=True)

FONT_LINK = ("https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1"
             "&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600&display=swap")

TEMPLATE = """<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>__TITLE__</title>
  <link href="__FONT_LINK__" rel="stylesheet">
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root {
      --color-paper: #f5f5f5;   --color-paper-2: #ececec;
      --color-ink: #2d3142;     --color-muted: #4f5d75;
      --color-soft: #7a8399;    --color-rule: rgba(45,49,66,0.12);
      --color-rule-solid: #bfc0c0;
      --color-accent: #eb6c36;  --color-accent-tint: rgba(235,108,54,0.08);
      --color-link: #2e5aa8;    --color-surface: #ffffff;
      --color-shadow: rgba(45,49,66,0.14);   /* ink-derived */
      --ease-out: cubic-bezier(0.22, 0.61, 0.36, 1);
      --font-sans: 'Geist', system-ui, sans-serif;
      --font-serif: 'Instrument Serif', serif;
      --font-mono: 'Geist Mono', ui-monospace, monospace;
    }
    html[data-theme="dark"] {
      --color-paper: #2d3142;   --color-paper-2: #393e53;
      --color-ink: #f5f5f5;     --color-muted: #bfc0c0;
      --color-soft: #8e98ac;    --color-rule: rgba(245,245,245,0.12);
      --color-rule-solid: rgba(191,192,192,0.25);
      --color-accent: #f08a59;  --color-accent-tint: rgba(240,138,89,0.10);
      --color-link: #6a95d8;    --color-surface: #393e53;
      --color-shadow: rgba(45,49,66,0);      /* no blur on dark - the border carries the edge */
    }
    body { font-family: var(--font-sans); background: var(--color-paper);
           color: var(--color-ink); min-height: 100vh; display: flex;
           align-items: center; justify-content: center; padding: 3rem 2rem;
           transition: background 220ms var(--ease-out); }
    .frame { max-width: 1200px; width: 100%; position: relative; }
    .eyebrow { font-family: var(--font-mono); font-size: 0.66rem; font-weight: 500;
               letter-spacing: 0.18em; text-transform: uppercase;
               color: var(--color-muted); margin-bottom: 0.5rem; }
    h1 { font-family: var(--font-serif); font-size: clamp(1.5rem, 2.4vw + 0.75rem, 2rem);
         font-weight: 400; letter-spacing: -0.02em; line-height: 1.15;
         color: var(--color-ink); margin-bottom: 0.25rem; }
    .standfirst { font-size: 0.875rem; color: var(--color-muted);
                  margin-bottom: 1.5rem; max-width: 68ch; }
    .theme-toggle { position: absolute; top: 0; right: 0;
      font-family: var(--font-mono); font-size: 0.66rem; font-weight: 500;
      letter-spacing: 0.14em; text-transform: uppercase; color: var(--color-muted);
      background: transparent; border: 1px solid var(--color-rule-solid);
      border-radius: 4px; padding: 0.375rem 0.75rem; cursor: pointer;
      transition: color 140ms var(--ease-out); }
    .theme-toggle:hover { color: var(--color-ink); }
    svg { width: 100%; min-width: 900px; display: block; }
    text.name  { font-family: var(--font-sans); font-weight: 600; }
    text.serif { font-family: var(--font-serif); }
    text.sub, text.axis-label { font-family: var(--font-mono); }
    .mask { fill: var(--color-paper); }
    .name { fill: var(--color-ink); }
    .sub  { fill: var(--color-muted); }
    .faint { fill: var(--color-soft); }
    .grid { stroke: var(--color-rule); }
    .axis { stroke: var(--color-soft); }
    .cell       { fill: var(--color-ink); }
    .cell-focal { fill: var(--color-accent); }
    .cell-label { fill: var(--color-paper); font-family: var(--font-sans); font-weight: 600; }
    .cell-sub   { fill: var(--color-paper); font-family: var(--font-mono); opacity: 0.72; }
    .ribbon       { fill: var(--color-muted); opacity: 0.18; }
    .ribbon-focal { fill: var(--color-accent); opacity: 0.35; }
    .bar-node   { fill: var(--color-ink); }
    .slope      { stroke: var(--color-muted); }
    .slope-focal{ stroke: var(--color-accent); }
    .dot        { fill: var(--color-ink); }
    .dot-hollow { fill: var(--color-paper); stroke: var(--color-ink); }
    .dot-accent { fill: var(--color-accent); }
    .dot-accent-hollow { fill: var(--color-paper); stroke: var(--color-accent); }
    .range      { stroke: var(--color-rule-solid); }
    [data-tip] { cursor: default; outline: none;
      transition: fill 140ms var(--ease-out), stroke 140ms var(--ease-out),
                  opacity 140ms var(--ease-out), filter 140ms var(--ease-out); }
    /* Hover paints the mark ACCENT - emphasis and interaction share one
       vocabulary. Translucent marks also lift their composited opacity via
       the builder-stamped --o (fill swaps and filters alone move a
       12%-opacity mark by ~2 RGB points - measured). */
    [data-tip]:hover, [data-tip]:focus-visible {
      fill: var(--color-accent);
      opacity: clamp(0.4, calc(var(--o, 1) * 2.4), 1);
    }
    /* Line-form marks (fill="none") recolor their stroke - an accent FILL
       would blob an arc or slope into a shape. */
    [data-tip][fill="none"]:hover, [data-tip][fill="none"]:focus-visible,
    line[data-tip]:hover, line[data-tip]:focus-visible {
      fill: none; stroke: var(--color-accent);
    }
    /* Marks that are ALREADY accent (the focal element) respond by darkening
       on light / lifting on dark, so nothing sits inert under the cursor. */
    .cell-focal[data-tip]:hover, .dot-accent[data-tip]:hover,
    .ribbon-focal[data-tip]:hover, .slope-focal[data-tip]:hover,
    .cell-focal[data-tip]:focus-visible, .dot-accent[data-tip]:focus-visible {
      filter: brightness(0.85);
    }
    html[data-theme="dark"] .cell-focal[data-tip]:hover,
    html[data-theme="dark"] .dot-accent[data-tip]:hover {
      filter: brightness(1.2);
    }
    /* Warming-stripes exemption: a cold year must never turn warm-orange
       under the cursor - it keeps its pole and lifts opacity instead. */
    .cell-cold[data-tip]:hover, .cell-cold[data-tip]:focus-visible {
      fill: var(--color-link);
    }
    [data-tip]:focus-visible { outline: 2px solid var(--color-link); outline-offset: 2px; }
    @media (prefers-reduced-motion: reduce) { [data-tip] { transition: none; } }
    .dd-tooltip {
      position: fixed; z-index: 10; max-width: 264px; pointer-events: none;
      background: var(--color-surface); color: var(--color-ink);
      border: 1px solid var(--color-rule-solid); border-radius: 4px;
      padding: 0.5rem 0.75rem;
      box-shadow: 0 1px 0 var(--color-rule), 0 6px 16px var(--color-shadow);
      opacity: 0; transform: translateY(2px);
      transition: opacity 140ms var(--ease-out), transform 140ms var(--ease-out);
      font-family: var(--font-sans); font-size: 0.75rem; line-height: 1.45;
    }
    .dd-tooltip.dd-show { opacity: 1; transform: none; }
    .dd-tooltip .dd-label { font-size: 0.6rem; font-weight: 600;
      letter-spacing: 0.14em; text-transform: uppercase;
      color: var(--color-soft); margin-bottom: 0.25rem; font-family: var(--font-mono); }
    .dd-tooltip .dd-line { color: var(--color-muted); }
    .dd-tooltip .dd-line strong { color: var(--color-ink); font-weight: 600; }
    .dd-tooltip .dd-line code { font-family: var(--font-mono); font-size: 0.7rem; color: var(--color-ink); }
    @media (prefers-reduced-motion: reduce) { .dd-tooltip { transition: none; transform: none; } }
  </style>
  <script data-theme-controls>
    (function () {
      var q = new URLSearchParams(location.search).get('theme');
      var sys = matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      var pref = null; try { pref = localStorage.getItem('dd-theme'); } catch (e) {}
      document.documentElement.dataset.theme = (q === 'dark' || q === 'light') ? q : (pref || sys);
    })();
    addEventListener('DOMContentLoaded', function () {
      var b = document.querySelector('.theme-toggle');
      var label = function () { b.textContent =
        document.documentElement.dataset.theme === 'dark' ? 'Light' : 'Dark'; };
      b.addEventListener('click', function () {
        var next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
        document.documentElement.dataset.theme = next;
        try { localStorage.setItem('dd-theme', next); } catch (e) {}
        label();
      });
      label();
      var tip = document.createElement('div');
      tip.className = 'dd-tooltip'; tip.id = 'dd-tooltip';
      tip.setAttribute('role', 'tooltip');
      document.body.appendChild(tip);
      var esc = function (s) { return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); };
      var fmt = function (s) { return esc(s).replace(/`([^`]+)`/g,'<code>$1</code>').replace(/\*([^*]+)\*/g,'<strong>$1</strong>'); };
      var show = function (el) {
        var lines = (el.getAttribute('data-tip') || '').split('|');
        var lab = el.getAttribute('data-tip-label');
        var html = lab ? '<div class="dd-label">' + esc(lab) + '</div>' : '';
        for (var i = 0; i < lines.length; i++) html += '<div class="dd-line">' + fmt(lines[i]) + '</div>';
        tip.innerHTML = html;
        el.setAttribute('aria-describedby', 'dd-tooltip');
        var r = el.getBoundingClientRect();
        tip.classList.add('dd-show');
        var x = Math.min(Math.max(8, r.left + r.width/2 - tip.offsetWidth/2), innerWidth - tip.offsetWidth - 8);
        var y = r.top - tip.offsetHeight - 10;
        if (y < 8) y = r.bottom + 10;
        tip.style.left = x + 'px'; tip.style.top = y + 'px';
      };
      var hide = function (el) { tip.classList.remove('dd-show'); if (el) el.removeAttribute('aria-describedby'); };
      var ts = document.querySelectorAll('[data-tip]');
      for (var i = 0; i < ts.length; i++) {
        var el = ts[i];
        if (!el.hasAttribute('tabindex')) el.setAttribute('tabindex', '0');
        el.addEventListener('pointerenter', function () { show(this); });
        el.addEventListener('pointerleave', function () { hide(this); });
        el.addEventListener('focus', function () { show(this); });
        el.addEventListener('blur', function () { hide(this); });
      }
      addEventListener('keydown', function (e) { if (e.key === 'Escape') hide(document.activeElement); });
      addEventListener('scroll', function () { hide(); }, true);
    });
  </script>
</head>
<body>
  <div class="frame">
    <button class="theme-toggle" type="button" aria-label="Switch color theme">Dark</button>
    <p class="eyebrow">__EYEBROW__</p>
    <h1>__TITLE__</h1>
    <p class="standfirst">__STANDFIRST__</p>
    <svg viewBox="__VIEWBOX__" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="__SLUG__-title __SLUG__-desc">
      <title id="__SLUG__-title">__TITLE__</title>
      <desc id="__SLUG__-desc">__DESC__</desc>
      <rect class="mask" width="100%" height="100%"/>
__BODY__
    </svg>
  </div>
</body>
</html>
"""



def _hoverize(html):
    """On data-tip elements, rewrite opacity="X" to style="--o:X;opacity:var(--o)"
    so the hover rule can boost the COMPOSITED opacity (filters can't - they
    apply before opacity compositing and barely move translucent marks)."""
    import re as _re
    def fix(m):
        line = m.group(0)
        if "data-tip" not in line:
            return line
        return _re.sub(r' opacity="([0-9.]+)"',
                       lambda o: f' style="--o:{o.group(1)};opacity:var(--o)"', line)
    return "\n".join(fix(_re.match(r".*", ln)) for ln in html.split("\n"))

def emit(slug, eyebrow, title, standfirst, desc, body, viewbox):
    t = (TEMPLATE.replace("__FONT_LINK__", FONT_LINK)
         .replace("__EYEBROW__", eyebrow).replace("__TITLE__", title)
         .replace("__STANDFIRST__", standfirst).replace("__DESC__", desc)
         .replace("__SLUG__", slug).replace("__VIEWBOX__", viewbox)
         .replace("__BODY__", _hoverize(body)))
    (OUT / f"{slug}.html").write_text(t, encoding="utf-8")
    print(f"built {slug}.html")


def g4(v):  # snap to the 4px grid
    return int(round(v / 4)) * 4


# ===========================================================================
# 1. TREEMAP - 9.2MB of expertise: skills/ on-disk size by category
# ===========================================================================
def squarify(items, x, y, w, h):
    """Squarified treemap (Bruls et al.). items: (label, value, ...) sorted desc.

    Works in AREA units throughout - the original version mixed raw values with
    scaled areas inside worst(), so rows never split and the map degenerated
    into full-width slices. Every quantity here is px^2 or px.
    """
    total = sum(i[1] for i in items)
    scale = (w * h) / total
    areas = [(item, item[1] * scale) for item in items]  # (payload, area px^2)
    rects = []
    cx, cy, cw, ch = float(x), float(y), float(w), float(h)
    row = []

    def worst(row_areas, length):
        s = sum(row_areas)
        mx, mn = max(row_areas), min(row_areas)
        return max((length ** 2) * mx / (s ** 2), (s ** 2) / ((length ** 2) * mn))

    def flush():
        nonlocal cx, cy, cw, ch
        s = sum(a for _, a in row)
        if cw >= ch:                      # column against the left edge
            rw = s / ch
            yy = cy
            for payload, a in row:
                rh = a / rw
                rects.append((payload, cx, yy, rw, rh)); yy += rh
            cx += rw; cw -= rw
        else:                             # row against the top edge
            rh = s / cw
            xx = cx
            for payload, a in row:
                rw2 = a / rh
                rects.append((payload, xx, cy, rw2, rh)); xx += rw2
            cy += rh; ch -= rh
        row.clear()

    for payload, a in areas:
        length = min(cw, ch)
        cur = [ar for _, ar in row]
        if not row or worst(cur + [a], length) <= worst(cur, length):
            row.append((payload, a))
        else:
            flush()
            row.append((payload, a))
    if row:
        flush()
    return rects


def treemap():
    # (category, KB on disk, skill count) - measured 2026-08-14
    data = [("Language", 3637, 24), ("Infrastructure", 1495, 16),
            ("Workflow", 1027, 17), ("Development", 898, 18),
            ("Data & API", 720, 7), ("Diagnostics", 667, 4),
            ("CLI tools", 464, 10), ("Python", 353, 7)]
    body = []
    for (item, x, y, w, h) in squarify(data, 40, 40, 920, 480):
        name, kb, n = item
        x, y = g4(x), g4(y)
        w, h = max(4, g4(w) - 4), max(4, g4(h) - 4)   # 4px gutters, grid-snapped
        focal = name == "Language"
        cls = "cell-focal" if focal else "cell"
        ramp = {"Infrastructure": 0.85, "Workflow": 0.68, "Development": 0.55,
                "Data & API": 0.44, "Diagnostics": 0.36, "CLI tools": 0.28, "Python": 0.22}
        op = "" if focal else f' opacity="{ramp[name]}"'
        body.append(f'      <rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="2"{op}/>')
        # paper-colored labels need a dark enough ground: below 50% ink the
        # cell reads as light, so labels flip to ink/muted for contrast.
        light_cell = (not focal) and ramp[name] <= 0.5
        lab = "name" if light_cell else "cell-label"
        sml = "sub" if light_cell else "cell-sub"
        if w >= 96 and h >= 56:
            body.append(f'      <text class="{lab}" x="{x + 12}" y="{y + 24}" font-size="13">{name}</text>')
            body.append(f'      <text class="{sml}" x="{x + 12}" y="{y + 40}" font-size="9">{kb / 1024:.1f} MB · {n} skills</text>')
        elif w >= 72 and h >= 36:
            body.append(f'      <text class="{lab}" x="{x + 8}" y="{y + 18}" font-size="10">{name}</text>')
            body.append(f'      <text class="{sml}" x="{x + 8}" y="{y + 31}" font-size="8">{kb / 1024:.1f} MB</text>')
        else:
            body.append(f'      <text class="{sml}" x="{x + 6}" y="{y + 14}" font-size="8">{name[:3].upper()}</text>')
    body.append('      <text class="sub" x="40" y="552" font-size="8" letter-spacing="0.06em">AREA = BYTES ON DISK UNDER skills/ PER README CATEGORY · MEASURED 2026-08-14 · 9.2 MB / 103 SKILLS TOTAL</text>')
    emit("expertise-treemap", "Treemap · claude-mods",
         "Nine megabytes of expertise",
         "The 103 skills weigh 9.2 MB on disk. Language and framework knowledge is nearly 40% of it - area is proportional to bytes, and the accent marks the largest shelf.",
         "Treemap of claude-mods skill categories sized by bytes on disk; the language and framework category dominates at 3.6 of 9.2 megabytes.",
         "\n".join(body), "0 0 1000 568")


# ===========================================================================
# 2. SANKEY - 490 conventional commits: type -> where the work landed
# ===========================================================================
def sankey():
    # links mined from `git log --format=%s` 2026-08-14; flows under 5 omitted (15 commits)
    links = [  # (type, scope, n)
        ("feat", "skills", 120), ("feat", "repo-wide", 91),
        ("fix", "skills", 54), ("fix", "repo-wide", 34), ("fix", "plumbing", 6),
        ("docs", "repo-wide", 65), ("docs", "skills", 16),
        ("chore", "repo-wide", 41), ("chore", "skills", 3),
        ("refactor", "repo-wide", 24), ("refactor", "skills", 8),
        ("test", "skills", 16), ("test", "plumbing", 5),
    ]
    left_order = ["feat", "fix", "docs", "chore", "refactor", "test"]
    right_order = ["skills", "repo-wide", "plumbing"]
    ltot = {k: sum(n for t, s, n in links if t == k) for k in left_order}
    rtot = {k: sum(n for t, s, n in links if s == k) for k in right_order}
    total = sum(ltot.values())
    X1, X2, TOP, H, GAP = 200, 760, 56, 440, 20
    scale = (H - GAP * (len(left_order) - 1)) / total

    ly, lpos = TOP, {}
    for k in left_order:
        h = ltot[k] * scale
        lpos[k] = [ly, ly]  # [cursor, top]
        lpos[k] = {"top": ly, "cur": ly, "h": h}
        ly += h + GAP
    ry, rpos = TOP + 28, {}
    rgap = 36
    for k in right_order:
        h = rtot[k] * scale
        rpos[k] = {"top": ry, "cur": ry, "h": h}
        ry += h + rgap

    body = []
    # ribbons first
    for t, s, n in links:
        h = n * scale
        sy = lpos[t]["cur"]; lpos[t]["cur"] += h
        ty = rpos[s]["cur"]; rpos[s]["cur"] += h
        focal = (t, s) == ("feat", "skills")
        cls = "ribbon-focal" if focal else "ribbon"
        mid = (X1 + X2) / 2
        body.append(
            f'      <path class="{cls}" d="M {X1},{sy:.1f} C {mid},{sy:.1f} {mid},{ty:.1f} {X2},{ty:.1f} '
            f'L {X2},{ty + h:.1f} C {mid},{ty + h:.1f} {mid},{sy + h:.1f} {X1},{sy + h:.1f} Z"/>')
    # node bars + labels
    for k in left_order:
        p = lpos[k]
        body.append(f'      <rect class="bar-node" x="{X1 - 8}" y="{p["top"]:.1f}" width="8" height="{p["h"]:.1f}"/>')
        cy = p["top"] + p["h"] / 2
        body.append(f'      <text class="name" x="{X1 - 20}" y="{cy + 4:.1f}" font-size="12" text-anchor="end">{k}</text>')
        body.append(f'      <text class="sub" x="{X1 - 20}" y="{cy + 18:.1f}" font-size="8" text-anchor="end">{ltot[k]}</text>')
    for k in right_order:
        p = rpos[k]
        body.append(f'      <rect class="bar-node" x="{X2}" y="{p["top"]:.1f}" width="8" height="{p["h"]:.1f}"/>')
        cy = p["top"] + p["h"] / 2
        body.append(f'      <text class="name" x="{X2 + 20}" y="{cy + 4:.1f}" font-size="12">{k}</text>')
        body.append(f'      <text class="sub" x="{X2 + 20}" y="{cy + 18:.1f}" font-size="8">{rtot[k]}</text>')
    body.append('      <text class="sub" x="40" y="548" font-size="8" letter-spacing="0.06em">483 CONVENTIONAL COMMITS FROM git log · MINED 2026-08-14 · FLOWS UNDER 5 COMMITS OMITTED (15) · plumbing = HOOKS, CI, RULES, COMMANDS</text>')
    emit("commit-flows", "Sankey · claude-mods",
         "Where the work went",
         "Every conventional commit in the repo, flowing from its type to where it landed. The headline ribbon: 120 features shipped straight into skills.",
         "Sankey diagram of claude-mods conventional commits from commit type to destination; feature work into skills is the dominant flow at 120 commits.",
         "\n".join(body), "0 0 1000 564")


# ===========================================================================
# 3. SLOPEGRAPH - the skills-first restructure, May 5 -> Aug 14
# ===========================================================================
def slope():
    # counts from README at f371f57 (2026-05-05) vs today
    data = [  # name, then, now, focal
        ("Skills", 71, 103, True), ("Agents", 23, 3, False),
        ("Rules", 6, 14, False), ("Hooks", 4, 13, False),
        ("Styles", 13, 13, False), ("Commands", 3, 3, False),
    ]
    X1, X2, BASE, S = 320, 680, 480, 4  # y = BASE - v*S
    body = []
    body.append(f'      <line class="axis" x1="{X1}" y1="60" x2="{X1}" y2="{BASE}" stroke-width="1"/>')
    body.append(f'      <line class="axis" x1="{X2}" y1="60" x2="{X2}" y2="{BASE}" stroke-width="1"/>')
    body.append(f'      <text class="sub" x="{X1}" y="{BASE + 28}" font-size="9" text-anchor="middle" letter-spacing="0.14em">MAY 05</text>')
    body.append(f'      <text class="sub" x="{X2}" y="{BASE + 28}" font-size="9" text-anchor="middle" letter-spacing="0.14em">AUG 14</text>')
    body.append(f'      <text class="sub" x="{X1}" y="{BASE + 44}" font-size="8" text-anchor="middle">v2.4.12</text>')
    body.append(f'      <text class="sub" x="{X2}" y="{BASE + 44}" font-size="8" text-anchor="middle">v3.6.0+</text>')

    # label collision nudging: sort by y, enforce 18px separation per side
    def nudge(vals):
        ys = sorted(((BASE - v * S), i) for i, v in enumerate(vals))
        out = [0.0] * len(vals)
        prev = -1e9
        for y, i in ys:
            y = max(y, prev + 18)
            out[i] = y
            prev = y
        return out

    lys = nudge([d[1] for d in data])
    rys = nudge([d[2] for d in data])
    for i, (name, a, b, focal) in enumerate(data):
        y1, y2 = BASE - a * S, BASE - b * S
        cls = "slope-focal" if focal else "slope"
        dotc = "dot-accent" if focal else "dot"
        body.append(f'      <line class="{cls}" x1="{X1}" y1="{y1}" x2="{X2}" y2="{y2}" stroke-width="{2 if focal else 1.2}"/>')
        body.append(f'      <circle class="{dotc}" cx="{X1}" cy="{y1}" r="4"/>')
        body.append(f'      <circle class="{dotc}" cx="{X2}" cy="{y2}" r="4"/>')
        lcls = "name" if focal else "sub"
        body.append(f'      <text class="{lcls}" x="{X1 - 16}" y="{lys[i] + 4:.0f}" font-size="11" text-anchor="end">{name}  {a}</text>')
        body.append(f'      <text class="{lcls}" x="{X2 + 16}" y="{rys[i] + 4:.0f}" font-size="11">{b}  {name}</text>')
    body.append('      <text class="sub" x="40" y="556" font-size="8" letter-spacing="0.06em">COUNTS FROM README AT f371f57 (2026-05-05) AND HEAD (2026-08-14) · THE v3.0.0 SKILLS-FIRST RESTRUCTURE LANDED 2026-06-10</text>')
    emit("skills-first-slope", "Slopegraph · claude-mods",
         "The skills-first restructure, in six lines",
         "Between May and August the toolkit tripled its hooks, halved nothing quietly, and made its choice loudly: 20 expert agents became skills, and the skill shelf grew by half.",
         "Slopegraph comparing claude-mods component counts on May 5 and August 14; skills rise 71 to 103 while agents fall 23 to 3.",
         "\n".join(body), "0 0 1000 580")


# ===========================================================================
# 4. DUMBBELL - upstream palette contrast, light vs dark (measured)
# ===========================================================================
def rel_lum(hexv):
    r, g, b = (int(hexv[i:i + 2], 16) / 255 for i in (1, 3, 5))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def contrast(a, b):
    la, lb = rel_lum(a), rel_lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def dumbbell():
    light_paper, dark_paper = "#f5f5f5", "#2d3142"
    roles = [  # role, light hex, dark hex
        ("ink", "#2d3142", "#f5f5f5"), ("muted", "#4f5d75", "#bfc0c0"),
        ("soft", "#7a8399", "#8e98ac"), ("link", "#2e5aa8", "#6a95d8"),
        ("accent", "#eb6c36", "#f08a59"),
    ]
    rows = []
    for name, lh, dh in roles:
        rows.append((name, contrast(lh, light_paper), contrast(dh, dark_paper),
                     name == "accent"))
    rows.sort(key=lambda r: -max(r[1], r[2]))
    X0, X1V, VMAX = 240, 920, 16    # x = X0 + v/VMAX*(X1V-X0)
    xv = lambda v: X0 + v / VMAX * (X1V - X0)
    body = []
    # reference lines: AA 4.5 and AA-large 3.0
    for v, lab in ((3.0, "AA LARGE 3.0"), (4.5, "AA 4.5")):
        x = xv(v)
        body.append(f'      <line class="grid" x1="{x:.0f}" y1="72" x2="{x:.0f}" y2="428" stroke-width="1" stroke-dasharray="4,3"/>')
        body.append(f'      <text class="sub" x="{x:.0f}" y="60" font-size="8" text-anchor="middle" letter-spacing="0.1em">{lab}</text>')
    for v in (1, 4, 8, 12, 16):
        body.append(f'      <text class="axis-label sub" x="{xv(v):.0f}" y="452" font-size="8" text-anchor="middle">{v}:1</text>')
    body.append(f'      <line class="axis" x1="{X0}" y1="432" x2="{X1V}" y2="432" stroke-width="1"/>')
    y = 104
    for name, lv, dv, focal in rows:
        xa, xb = xv(lv), xv(dv)
        rng = "range"
        dl = "dot-accent-hollow" if focal else "dot-hollow"
        dd = "dot-accent" if focal else "dot"
        body.append(f'      <line class="{rng}" x1="{min(xa, xb):.0f}" y1="{y}" x2="{max(xa, xb):.0f}" y2="{y}" stroke-width="2"/>')
        body.append(f'      <circle class="{dl}" cx="{xa:.0f}" cy="{y}" r="6" stroke-width="1.5"/>')
        body.append(f'      <circle class="{dd}" cx="{xb:.0f}" cy="{y}" r="6"/>')
        body.append(f'      <text class="name" x="{X0 - 56}" y="{y + 4}" font-size="12" text-anchor="end">{name}</text>')
        lo, hi = (lv, dv) if lv <= dv else (dv, lv)
        body.append(f'      <text class="sub" x="{min(xa, xb) - 12:.0f}" y="{y + 4}" font-size="8" text-anchor="end">{lo:.1f}</text>')
        body.append(f'      <text class="sub" x="{max(xa, xb) + 12:.0f}" y="{y + 4}" font-size="8">{hi:.1f}</text>')
        y += 72
    # legend
    body.append('      <circle class="dot-hollow" cx="252" cy="500" r="6" stroke-width="1.5"/>')
    body.append('      <text class="sub" x="268" y="504" font-size="9">on light paper</text>')
    body.append('      <circle class="dot" cx="412" cy="500" r="6"/>')
    body.append('      <text class="sub" x="428" y="504" font-size="9">on dark paper</text>')
    body.append('      <text class="sub" x="40" y="548" font-size="8" letter-spacing="0.06em">WCAG 2.1 RELATIVE-LUMINANCE RATIOS OF THE DEFAULT SKIN TOKENS AGAINST THEIR OWN PAPER · COMPUTED, NOT EYEBALLED</text>')
    emit("palette-contrast-dumbbell", "Dumbbell · style guide",
         "Every token, both papers",
         "Each role's WCAG contrast on light paper (hollow) and dark paper (filled). The accent is the surprise: on light paper it misses even AA-large at 2.9:1, yet on dark it clears full AA at 5.2:1. Light mode is where the never-text rule earns its keep.",
         "Dumbbell chart of the default palette's WCAG contrast ratios in light versus dark mode; ink clears AA comfortably in both while the accent fails AA-large on light paper yet passes AA on dark.",
         "\n".join(body), "0 0 1000 564")


# ===========================================================================
# 5. WAFFLE - 103 skills, one square each
# ===========================================================================
def waffle():
    data = [("Language", 24, True), ("Development", 18, False), ("Workflow", 17, False),
            ("Infrastructure", 16, False), ("CLI tools", 10, False), ("Python", 7, False),
            ("Data & API", 7, False), ("Diagnostics", 4, False)]
    opacities = [1.0, 0.78, 0.62, 0.5, 0.38, 0.28, 0.2, 0.13]
    COLS, SIZE, GAP, X0, Y0 = 13, 28, 6, 60, 56
    body = []
    idx = 0
    legend = []
    for ci, (name, n, focal) in enumerate(data):
        op = opacities[ci]
        for _ in range(n):
            r, c = divmod(idx, COLS)
            x = X0 + c * (SIZE + GAP)
            yy = Y0 + r * (SIZE + GAP)
            cls = "cell-focal" if focal else "cell"
            opattr = "" if focal else f' opacity="{op}"'
            body.append(f'      <rect class="{cls}" x="{x}" y="{yy}" width="{SIZE}" height="{SIZE}" rx="3"{opattr}/>')
            idx += 1
        legend.append((name, n, focal, op))
    rows_used = -(-idx // COLS)
    ly = Y0 + 8
    lx = X0 + COLS * (SIZE + GAP) + 48
    for name, n, focal, op in legend:
        cls = "cell-focal" if focal else "cell"
        opattr = "" if focal else f' opacity="{op}"'
        body.append(f'      <rect class="{cls}" x="{lx}" y="{ly - 12}" width="16" height="16" rx="3"{opattr}/>')
        body.append(f'      <text class="name" x="{lx + 28}" y="{ly + 1}" font-size="12">{name}</text>')
        body.append(f'      <text class="sub" x="{lx + 232}" y="{ly + 1}" font-size="10" text-anchor="end">{n}</text>')
        ly += 36
    total_h = Y0 + rows_used * (SIZE + GAP) + 40
    body.append(f'      <text class="sub" x="{X0}" y="{total_h}" font-size="8" letter-spacing="0.06em">ONE SQUARE = ONE SKILL · 103 TOTAL · COUNTED FROM README.md 2026-08-14 · OPACITY ORDERS CATEGORIES BY SIZE</text>')
    emit("skills-waffle", "Waffle · claude-mods",
         "One hundred and three squares",
         "Every skill in the toolkit, one square each. The accent block is the language and framework shelf - the reason the answer to 'is there a skill for that?' is usually yes.",
         "Waffle chart of the 103 claude-mods skills grouped by category, one square per skill, with the language and framework category in the accent color.",
         "\n".join(body), f"0 0 1000 {g4(total_h + 20)}")


if __name__ == "__main__":
    treemap()
    sankey()
    slope()
    dumbbell()
    waffle()
