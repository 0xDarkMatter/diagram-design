# Line Chart

**Best for:** continuous trends over time or a sequential index — signups over weeks, revenue by month, latency over releases. Use when the direction and rate of change between points is the primary message.

## Layout conventions

- **Plot area margins:** left 80px, bottom 60px, top 40px, right 40px — inside `0 0 1000 500` viewBox.
- **Points:** 4–12 data points. Fewer → consider a summary stat; more → aggregate into periods.
- **X-axis:** evenly spaced time/index labels below the plot. Use Geist Mono 8px, centered on each point x.
- **Y-axis gridlines:** 4–6 horizontals at regular intervals. Same faint treatment as bar chart.
- **Lines:** `<polyline>` with `fill="none"`. Focal series `stroke-width="1.8"`, others `"1.2"`.
- **Vertex dots:** only on the focal series (`r=4`, filled). Other series: line only.
- **Area fill (optional):** `<polygon>` closing back to `y=420` (x-axis baseline) at 0.08 opacity. Use for the focal series only when the area meaning is important.
- **Multi-series:** up to 5 series. Focal = `accent`. Others = `series-1`, `series-2`, `series-3`, `series-4` from style-guide.md. Apply series palette in order — don't skip.
- **Legend:** horizontal strip at the bottom. Swatch = 16×8px rect with the series fill/stroke. One entry per series.

### Polyline pattern

```svg
<!-- Focal series -->
<polyline points="x0,y0 x1,y1 x2,y2 ..."
          fill="none" stroke="#eb6c36" stroke-width="1.8" stroke-linejoin="round"/>
<!-- Dots at each point (focal only) -->
<circle cx="x0" cy="y0" r="4" fill="#eb6c36"/>

<!-- Non-focal series -->
<polyline points="x0,y0 x1,y1 ..."
          fill="none" stroke="#7c8f6f" stroke-width="1.2" stroke-linejoin="round"/>
```

## Anti-patterns

- More than 5 series (visual mush — reduce or split).
- Lines that don't start at a shared zero baseline unless explicitly annotated.
- Smoothed/spline curves when the underlying data is sampled — polyline is honest.
- Dots on every series when there are 4+ series (only focal gets dots).
- Y-axis that doesn't include zero when the absolute magnitude matters.
- Connecting discontinuous data segments without a visual gap.

## Variants

All three inherit the plot area, gridline treatment, and legend block above, and all three are straight-segment constructions — the smoothed-spline anti-pattern holds. A kernel density estimate is already a continuous function, so sampling it densely and joining the samples with straight segments is honest; spline-smoothing raw sampled points is not.

- **Bump chart:** rank over time — one line per series through a fixed grid of rank rows, which replace the value gridlines. Rows are a *designed* grid: first row at `y=64`, pitch divisible by 4 and chosen so the last row clears `y=420` (5 ranks → 80px, 4 → 96px). Period columns sit on an even pitch divisible by 4, inset ≥ 96px from both plot edges, leaving gutters for the entry and exit series labels. Up to 5 series, as above — one rank row per series, and `series-1`…`series-4` covers the non-focal set. 4–8 periods (the base type allows 12; rank columns need the width). Focal series `accent` at 1.8 with `r=4` vertex dots, others at 1.2.
  - **Rank is ordinal.** Equal row spacing is not equal distance in the ranked quantity: 1st to 2nd may be a chasm and 4th to 5th a hair. Name the ranked measure in the legend, and never read a steeper segment as a faster rate.

- **Streamgraph:** composition of an additive total over time, stacked around a centered (“wiggle”) baseline instead of `y=420`. Centre the stack on `y=230`. Drop the y-axis line and its labels — a floating baseline has no fixed zero to label, and an axis implying one is a lie; keep the period labels below `y=420`. Cap 4–7 bands. Focal band `accent-tint` with `accent` stroke; the rest on an ink opacity ramp stepped evenly from `0.04` to `0.13` with an `ink @ 0.30` stroke. `0.14` is the hard ceiling — dark mode binds, and past it a `muted` 9px label sitting on the band drops under 4.5:1. One accent, no rainbow.
  - **Shows composition, not magnitude.** Only band *thickness* encodes a value; no band’s top or bottom edge is readable, so a reader cannot recover any series’ level. Never stack non-additive quantities — rates, averages, or percentages of different denominators. If individual series need comparing over time, that is a line chart.

- **Ridgeline:** several distributions stacked vertically, one per row, each filled on its own baseline. Widen the left gutter for the category names — ridges start at `x=200`, not `x=80` — and left-align each label in it at that row’s baseline. Gridlines run *vertical* on the shared x-scale; the horizontal value gridlines above do not apply, because each row’s y is its own density, not a shared quantity. Ridge height is 1.6× the row pitch, giving 0.6 overlap; the pitch is divisible by 4 and must satisfy `pitch × (rows + 0.6) ≤ 380` so the tallest ridge still clears the plot top — 4 rows → 80px, 6 → 56px, 8 → 44px. Paint the back row first and give each ridge an opaque `paper` fill so the row in front reads cleanly over the one behind. Cap 4–8 ridges. Focal ridge `accent-tint` with `accent` stroke; the rest on the same ink ramp and the same `0.14` ceiling as the streamgraph.
  - **One x-scale and one y-scale across every ridge**, always. Per-row normalisation turns a magnitude comparison into a shape comparison, and nothing in the rendered figure reveals it. State the overlap fraction on the source line, because overlap hides the foot of each ridge behind the row in front.

## Examples

- `assets/example-line.html` — minimal light
- `assets/example-line-dark.html` — minimal dark
- `assets/example-line-full.html` — full editorial
