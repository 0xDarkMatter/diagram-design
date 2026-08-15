# Proposal: sixteen editorial dataviz types

Sixteen chart forms in the lineage of Information is Beautiful, proposed in
three waves - treemap, sankey, slopegraph, dumbbell, waffle; hex tile map, bump
chart, streamgraph, beeswarm, arc diagram; then bubble chart, ridgeline, small
multiples, marimekko, warming stripes, and punch card - as candidate additions
to the 27 visual types.

**Every example uses public data a stranger already knows**: OWID/UN population
and life expectancy, Energy Institute energy mix, HadCRUT5 temperature, IOC
medal tables, UN migration corridors, US Census, FiveThirtyEight births, WMO
climate normals. Source CSVs ship in `dataviz/data/` so every chart rebuilds
deterministically from `build_public.py`.
**Interaction contract shared by every example**: any mark carrying `data-tip`
shows a floating tooltip on hover AND keyboard focus, and the mark itself
lights up - stroke shifts to the interactive `link` color with a small
brightness lift, 140ms, dropped under reduced-motion. Hover answers "am I on
it?", the tooltip answers "what is it?".

Each is drafted below in the house type-reference format, and each has a working
example built against the default skin with real, cited data. None require new
tokens; all fit the existing semantic-role system and the one-accent doctrine.

Why these five: they cover the quantitative stories the current set can't tell.
Bar compares categories and line follows time, but nothing today shows
**hierarchical proportion** (treemap), **flow between two categorical axes**
(sankey), **rank-and-magnitude change between two moments** (slopegraph),
**paired measurements per category** (dumbbell), or **discrete part-of-whole
counts** (waffle). Radar is the only multi-series quantitative type, and it is
the wrong grammar for all five of these jobs.

House rules carried through every spec: one accent element, ink-opacity ramps
instead of a rainbow, 4px grid, mono for numbers and meta, a sourced footnote
naming where the data came from, and an honest-data rule per type. Examples:
`docs/proposals/dataviz/*.html` (light/dark switchable).

---

## Treemap

**Best for:** hierarchical proportion - where a total decomposes into parts and
the parts' relative sizes ARE the story. Disk usage, budget breakdowns, market
share, time allocation.

### Layout conventions
- Squarified algorithm (Bruls et al.) - compute in area units, lay each row
  against the shorter side of the remaining rectangle. Aspect ratios stay near
  1 and the eye can compare areas.
- 4px gutters between cells, `rx=2`. Cells snap to the 4px grid after layout.
- **One accent cell** - the largest or the editorially focal category. All
  other cells are `ink` at a rank-ordered opacity ramp (e.g. 0.85 → 0.22), so
  size order survives even in greyscale.
- **Labels live inside cells**: name in sans 600, value in mono, top-left with
  12px padding. Three tiers by cell size: name+value+count / name+value /
  3-letter mono abbreviation. Cells with paper-colored labels need ≥50% ink
  opacity behind them; lighter cells flip to `ink`/`muted` label colors.
- A sourced footnote states what area encodes and the measurement date.

### Honest-data rule
Area is the ONLY encoding - never clip, floor, or log-scale a cell. If a
category is too small to label, abbreviate it; footnote the full name if needed.

### Budget
Max 10 cells. Below 2% of total, merge into an "everything else" cell and say
so in the footnote.

### Anti-patterns
- Slice-and-dice strips (full-width rows) - that is a stacked bar pretending.
- A hue per category - the opacity ramp carries order; hue carries nothing.
- Nesting two levels deep - use two treemaps (overview + focal category).

---

## Sankey

**Best for:** flow between two categorical axes where magnitude matters -
commits by type into components, budget sources into programs, traffic sources
into outcomes.

### Layout conventions
- Two columns of node bars (8px wide, `ink`), sources left, sinks right.
  Ribbon thickness ∝ value; ribbons are cubic Béziers meeting the bars flush:
  `M x1,y C mid,y mid,ty x2,ty L x2,ty+h C … Z`.
- Ribbons: `muted` at 0.18 opacity. **One focal ribbon** in `accent` at 0.35 -
  the headline flow. Crossing ribbons at low opacity read fine; do not route
  around.
- Node label (sans 600) + total (mono) sit outside their column - left-anchored
  for sinks, right-anchored for sources. 20px gaps between source bars.
- Node totals equal the sum of DRAWN ribbons, and a footnote declares any
  omitted small flows with their combined count - totals must reconcile.

### Honest-data rule
Never omit a flow silently. The cutoff and the omitted total go in the
footnote. Two-column only - multi-stage sankeys exceed the skill's remit.

### Budget
Max 6 sources, 4 sinks, 13 ribbons. One focal ribbon.

### Anti-patterns
- A hue per source (the rainbow sankey) - opacity + one accent is the system.
- Curvature so tight ribbons kink - keep the control points at the midpoint.
- Unreconciled totals - bars that don't match their ribbons are a lie.

---

## Slopegraph

**Best for:** how each series' rank and magnitude changed between exactly two
moments - before/after a restructure, two survey waves, two fiscal years.

### Layout conventions
- Two vertical axes (thin `soft` lines), dated mono labels beneath each.
- One straight line per series; dots (`r=4`) at both ends. **One focal series**
  in `accent`, stroke 2; all others `muted`, stroke 1.2.
- Labels sit outside the axes: `name value` right-aligned on the left,
  `value name` left-aligned on the right. Collision-nudge to ≥18px separation,
  processing labels in y-order - the lines stay honest, only labels move.
- Linear y scale from zero. Same scale both sides, obviously.

### Honest-data rule
Exactly two time points, actually comparable, both dated in the footnote with
their sources. If the underlying counting method changed between the two
moments, the chart is invalid - say so instead of drawing it.

### Budget
Max 8 series. One focal.

### Anti-patterns
- Three or more time points - that is a line chart.
- Log scale to tame an outlier - the outlier is the story.
- Curved connectors - the straight line IS the encoding.

---

## Dumbbell

**Best for:** two measurements of the same categories - light vs dark, before
vs after, min vs max, this year vs last - where the gap is the story.

### Layout conventions
- One row per category, 72px pitch. Connector: `rule-solid`, 2px. Endpoint
  dots `r=6`: **hollow** (paper fill + ink stroke) for state A, **filled** ink
  for state B - the pairing must survive greyscale. Focal row uses accent for
  both dots.
- Values in mono 8px just outside each dot. Category name sans 600,
  right-aligned in the left margin.
- Reference lines (dashed `rule`) with small mono captions above the plot for
  domain thresholds - WCAG AA, SLA targets, budget lines.
- A legend row: one hollow + one filled dot, labeled.

### Honest-data rule
Both measurements per row must share units and method. The axis starts at a
meaningful zero or a declared floor - declare it if not zero.

### Budget
Max 8 rows. One focal row.

### Anti-patterns
- Arrowheads on connectors - direction is the dots' job.
- Color-coding which end is which - the hollow/filled pairing does it.
- Sorting rows arbitrarily - sort by one of the two values and hold it.

---

## Waffle

**Best for:** discrete part-of-whole counts where every unit is countable and
deserves its own mark - 103 skills, 50 states, 12 team members. The IIB-style
humanizer: a number becomes a field of squares.

### Layout conventions
- Fixed columns (10-13), squares 24-28px with 4-6px gaps, `rx=3`, filling
  left-to-right, top-to-bottom, categories in descending size order.
- **One accent category**; the rest are `ink` at a descending opacity ramp -
  category order is readable without the legend.
- Legend to the right: swatch + name + count per row, mono counts right-aligned.
- Footnote: "one square = one X", the total, source, and date.

### Honest-data rule
One square is one unit - never let a square mean 2.5 things. If the total is
too big to draw, change units honestly ("one square = 10 commits") and say so
in BOTH the footnote and the desc.

### Budget
Max 200 squares, max 8 categories.

### Anti-patterns
- Percentage waffles rounded to 100 squares that don't sum to the real total.
- Icon waffles (pictograms) - squares stay squares in this system.
- Two accent categories - the reader loses the focal thread.

---

## Compatibility notes

- All five paint via semantic roles only: `ink`, `muted`, `soft`, `accent`,
  `rule`, `paper`. No new tokens. The ink-opacity ramp is the one convention
  worth adding to the style guide if these land.
- Complexity budgets above slot into SKILL.md §7's table as five new rows.
- The §6 connector rules apply to none of these (no node-to-node connectors);
  the sankey ribbon and slopegraph line are type-specific primitives, like
  Loop's ring arcs.
- Working examples with real, cited data ship in `docs/proposals/dataviz/`.

---

# Wave two

## Hex tile map (tile grid cartogram)

**Best for:** per-region values where geography aids recognition but real areas
would lie - population, per-state metrics, election-style maps. Every region
gets ONE equal hexagon placed by approximate adjacency; color is the only data
channel. This is the honest cousin of the choropleth, which over-weights big
empty regions (WA at 4x Victoria's area, a third of its population).

- Pointy-top hexagons on an offset grid, 4-8px gutters, layout hand-curated per
  geography and shipped as a named tile atlas (US 50+DC+PR here; UK/EU/AU atlases are
  data files, not code).
- Value encoding: `ink` at value-proportional opacity; **one accent tile** for
  the maximum or focal region. Region code + value inside each tile; label
  color flips ink/paper at 50% cell opacity.
- Honest-data rule: equal tiles ONLY - the moment tiles vary in size the chart
  is a cartogram of a different species and needs its own spec. Placement
  approximates adjacency; a footnote says so.
- Budget: max 16 tiles; more than that wants a real map, not a diagram.
- Anti-patterns: tiles sized by value; diverging palettes for a sequential
  quantity; omitting a region because it is small (ACT stays).

## Bump chart

**Best for:** rank movement across 3-6 ordered snapshots when position, not
magnitude, is the story. Slopegraph shows two moments and magnitude; bump shows
several moments and rank only.

- One vertical axis per snapshot, equal rank pitch (56px), straight segments
  between adjacent snapshots, dots at every vertex, labels at first and last
  appearance (value on the last).
- **One focal series** in accent. Series entering late or leaving early simply
  start/stop - a real gap is drawn as absence, never interpolated.
- Honest-data rule: state the ranking key and tie-break in the footnote; if the
  categories changed definition between snapshots, the chart is invalid.
- Budget: max 8 series, 6 snapshots. Anti-patterns: curved "subway" splines
  (they invent data between snapshots); ranking by different measures per
  column; smoothing a tie into a crossing.

## Streamgraph

**Best for:** how a total and its composition breathe across many periods -
commit activity, traffic mix, headcount by team. The silhouette (symmetric)
baseline makes the total's envelope the hero while layers keep their share.

- Symmetric stacking: baseline = -total/2 per period. Catmull-Rom smoothed
  layer boundaries (control points at 1/6 chord) - smoothing the DRAWING, with
  vertices staying on true values.
- **One accent layer** (the headline series); others in the ink-opacity ramp,
  stacked largest-innermost. Legend row with per-series totals; annotate at
  most one landmark period with a hairline and a short label.
- Honest-data rule: zero periods stay in the domain - the pinch IS data. Say
  the bucket size in the footnote and never resample to prettify.
- Budget: max 6 layers, 24 periods. Anti-patterns: wiggle-minimised baselines
  that reorder layers per period (unreadable legend); rainbow layers; y-axis
  ticks (the form is about shape, totals go in the legend or tooltip).

## Beeswarm

**Best for:** a full distribution where every unit deserves its own mark -
Snake Oil energy. One dot per item on a value axis, dodged perpendicular so
nothing overlaps and vertical position means nothing.

- Log or linear axis chosen by the data's spread and DECLARED in the footnote.
  Faint gridlines at round values. Greedy dodge: first free slot alternating
  above/below the midline, dot pitch 2r+2.
- Dots `ink` at ~0.55 opacity so density reads; **one accent dot**; the top
  handful labeled with hairline leaders, one tier per label, alternating sides.
- Honest-data rule: one dot = one item, no binning; if two dots must share a
  position the dodge shows it as thickness, never as a darker dot.
- Budget: max 300 dots, 6 labeled. Anti-patterns: meaning smuggled into the
  dodge axis; dot size as a second encoding (that is a bubble chart); opacity
  as a value encoding while also dodging.

## Arc diagram

**Best for:** relationships over a modest node set where the pattern of
connection - hubs, cliques, strangers - matters more than topology. Nodes on
one baseline, links as semicircular arcs above it.

- Nodes ordered by a DECLARED key (alphabetical here; degree or category are
  fine - say which). Arc radius = half the node distance; all arcs above.
- Links `muted` at ~0.35 opacity; **the focal node's arcs** in accent, its dot
  slightly larger. Rotated labels (-42deg) below the baseline. Tooltips carry
  each node's partner list.
- Honest-data rule: name the link source (frontmatter declarations here - so
  the chart shows declared kinship, not observed coupling) and count omitted
  nodes in the footnote.
- Budget: max 40 nodes, 80 arcs. Anti-patterns: arcs below the line as a
  second link type (split the diagram); opacity by weight AND width by weight
  (pick one); force-directed layouts smuggled onto a line.

---

# Wave three

## Bubble chart (Gapminder view)

**Best for:** three quantities per item - x, y, and size - where the cloud's
shape is the story. The canonical case: wealth vs health, bubbles sized by
population.

- x on a declared (often log) scale, y linear, bubble area (never radius)
  proportional to the third quantity. Bubbles get a 1px `paper` rim so
  overlaps stay separable; draw LARGEST first so small bubbles stay hoverable.
- All bubbles `ink` at ~0.35 opacity; **one accent bubble**; label only items
  a reader will look for (the giants, the outliers) - 8-12 max.
- Honest-data rule: area = value, exactly; omitted items (missing data,
  out-of-domain) are counted in the footnote.
- Budget: 250 bubbles, 12 labels. Anti-patterns: radius-proportional sizing
  (quadruples the visual lie); a hue per continent (one accent, opacity does
  density); trend lines drawn through log axes without saying so.

## Ridgeline

**Best for:** one cyclic or distributional curve per series, stacked with
deliberate overlap - monthly climates, daily rhythms, score distributions.

- One baseline per series at fixed pitch; the curve rises from it on a SHARED
  amplitude scale declared in the footnote ("1°C = 2.6px on every ridge").
  Catmull-Rom smoothing of the drawing, vertices on true values.
- Fills `ink` at low opacity so overlaps read as depth; **one accent ridge**;
  name left of each baseline, range right of it.
- Honest-data rule: shared amplitude or the chart is invalid - per-ridge
  normalisation turns shape comparison into a lie. Overlap is a feature;
  occlusion of a peak behind a peak is not (increase pitch).
- Budget: 12 ridges. Anti-patterns: per-ridge scales; rainbow ridges;
  smoothing that invents extrema.

## Small multiples

**Best for:** the same simple chart repeated per category so shapes compare -
one metric, many countries/teams/years.

- A grid of identical mini-panels (3-4 columns), each with its own baseline
  and ONE shared y-scale across all panels - that constraint IS the form.
  One faint reference gridline; name top-left, latest value top-right.
- **One accent panel** (the editorial subject); all others `muted`.
- Honest-data rule: shared scale, stated in the header note. A panel that
  clips at the shared max is annotated, not rescaled.
- Budget: 16 panels, one series per panel. Anti-patterns: per-panel scales
  (the deadly sin); multi-series panels (that is a line chart per panel);
  sparkline-sized panels with axis labels (drop the labels or grow the panel).

## Marimekko (mosaic)

**Best for:** two nested proportions at once - column width is each group's
share of the total, segment height is composition within the group.

- Columns ordered by size, widths proportional to group totals, 3px column
  gutters and 2px segment gutters. Same segment ORDER in every column.
- Segments in the ink-opacity ramp; **one accent segment across all columns**
  (the series being tracked). Segment labels only where they fit; narrow
  columns keep their data, lose their labels, and the footnote says so.
- Honest-data rule: widths from the same measure as heights (both from the
  underlying quantity, not mixed units). Nothing is omitted to tidy the
  layout.
- Budget: 8 columns, 6 segments. Anti-patterns: alphabetical column order;
  per-column segment orders; percentage heights on absolute widths without
  declaring both.

## Warming stripes

**Best for:** one value per period, many periods, where the drift IS the
message. After Ed Hawkins. Deliberately axis-free.

- One full-height stripe per period, no gaps. Diverging encoding built from
  the EXISTING palette poles: `link` below the reference, `accent` above,
  `paper` at zero, magnitude as opacity. This is the one sanctioned
  two-hue diverging scale in the system - the poles already exist.
- A handful of period labels beneath; the footnote carries reference period,
  range, and source. No y-axis, no gridlines - adding them un-makes the form.
- Honest-data rule: every period present, equal width, chronological. The
  reference baseline is named.
- Budget: 250 stripes. Anti-patterns: red-blue hues imported from outside
  the palette; smoothing; cherry-picked start years.

## Punch card

**Best for:** activity by two cyclic axes - weekday x hour, month x weekday -
where the working rhythm is the story.

- A cells grid (rows = coarser cycle), rounded 3px, gap 6px. Value maps to
  `ink` opacity from a declared floor (0.08) to 0.92; **the single peak cell**
  takes the accent. Row and column labels in their own gutters.
- Tooltips carry the actual value per cell - the grid shows pattern, the
  tooltip shows numbers.
- Honest-data rule: cells are aggregates of equal-sized buckets (say the
  aggregation - mean, sum - in the footnote); missing buckets render at the
  floor with a footnote, never interpolated.
- Budget: 24x12 cells. Anti-patterns: circles sized by value in a grid (the
  classic GitHub punch card's area lie); normalising per-row (kills the
  cross-row story); rainbow scales.
