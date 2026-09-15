# pptx-svg — Language Specification (v0.1)

The authoring language of [pptx-compiler](https://github.com/gaoyu06/pptx-compiler).

> Implementation status: all of §3–§7 and `deck.xml` (§1) are implemented
> and compile-checked. `pptx:ph` binds to the structured-deck placeholder
> contract (slot `<g>` + `data-pptx-bounds` + carrier child); `pic`/`tbl`
> alias to `picture`/`table`. `pptx:data` JSON declares itself
> authoritative and must carry `x`/`y`/`width`/`height` in px.

An SVG superset for authoring PowerPoint decks. Every page is a
standalone, valid SVG document; PowerPoint semantics are expressed
through the `pptx:` namespace and compile to native OOXML
(DrawingML / PresentationML) objects — never rasterized.

```xml
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:pptx="http://pptx-svg.dev/ns/1"
     viewBox="0 0 1280 720" lang="zh-CN">
```

## 1. File model

A deck is a directory. One file per page, ordered by filename:

```
deck/
├── deck.xml            # optional manifest
└── pages/
    ├── 01-cover.svg    # standalone valid SVG + pptx: extensions
    ├── 02-agenda.svg
    └── 03-charts.svg
```

- Page order = lexicographic filename order.
- `deck.xml` is optional; when present it sets deck-level properties
  and may override page order:

```xml
<pptx:deck xmlns:pptx="http://pptx-svg.dev/ns/1"
           format="ppt169" lang="zh-CN" title="Q3 Review">
  <pptx:page src="pages/02-agenda.svg"/>
  <pptx:page src="pages/01-cover.svg"/>
</pptx:deck>
```

`format` selects the canvas (`ppt169`=1280×720 default, `ppt43`,
`banner`, `story`, `moments`, `xiaohongshu`, `wechat`, `a4`, or an
explicit `viewBox`).

## 2. Language tiers

| Tier | Syntax | Meaning |
|---|---|---|
| SVG core | standard elements/attributes | the visual layer — drawn verbatim |
| `pptx:*` attribute | `pptx:vert`, `pptx:effect`… | element-scoped visual/behavioral extension |
| `pptx:*` element | `<pptx:anim>`… | non-visual semantics (order, timing, notes) |
| `data-pptx-*` | reserved | compiler-internal metadata (round-trip bookkeeping); never authored by hand |

An element's `id` is its animation/anchor identity. Top-level `<g>`
elements are the animation targets and compile to `p:grpSp`.

## 3. Element-level extension attributes

On any drawing element (`text`, `rect`, `circle`, `path`, `image`,
`g`, …):

### Text body (on `<text>`)

| Attribute | Values | OOXML |
|---|---|---|
| `pptx:vert` | `eaVert` `vert` `vert270` `wordArtVert` `eaVert270` `mongolianVert` | `a:bodyPr@vert` |
| `pptx:anchor` | `t` `ctr` `b` `just` `dist` | `a:bodyPr@anchor` |
| `pptx:autofit` | `none` `norm` `shape` | `a:noAutofit` `a:normAutofit` `a:spAutoFit` |

### Effects (on any shape/image)

`pptx:effect` is a whitespace-separated list of calls:

```
pptx:effect="inner-shadow(blur=8,dist=4,dir=90,color=#00000066) soft-edge(rad=6)"
```

| Effect | Keys | OOXML |
|---|---|---|
| `outer-shadow` | `blur` `dist` `dir` `color` `alpha` | `a:outerShdw` |
| `inner-shadow` | same | `a:innerShdw` |
| `glow` | `rad` `color` `alpha` | `a:glow` |
| `reflection` | `blur` `dist` `dir` `alpha` `pos` `end` `fade` | `a:reflection` |
| `soft-edge` | `rad` | `a:softEdge` |
| `blur` | `rad` | `a:blur` |

Units: `blur`/`dist`/`rad` in px, `dir` in degrees, `alpha`/`pos`/`end`
in percent or `0–1`, `color` is `#rgb[a]`/`#rrggbb[aa]`.

### Structure/behavior

| Attribute | Values | Meaning |
|---|---|---|
| `pptx:build` | `paragraph` | by-paragraph text build — one animation step per `a:p` |
| `pptx:name` | string | shape name shown in the Selection/Animation pane |
| `pptx:ph` | `title` `body` `pic` `chart` `tbl` … | placeholder binding (structured decks) |
| `pptx:crop` | `l,t,r,b` fractions | image crop (`a:srcRect`) |

### Text paragraph control

`pptx:line-height` goes on `<text>` and applies to all its paragraphs;
the rest go on individual `<tspan>` lines (one `<tspan>` = one `a:p`):

| Attribute | Element | Meaning |
|---|---|---|
| `pptx:line-height` | `<text>` | line spacing: `38`/`38px` in px, `1.6x`/`160%` as multiple |
| `pptx:space-before` | `<tspan>` | paragraph space before (px) |
| `pptx:line-break` | `<tspan>` | hard line break inside the paragraph (`a:br`) |
| `pptx:soft-break` | `<tspan>` | intra-paragraph soft line break flag |

### Native objects

- `pptx:formula="…LaTeX…"` on `<text>` → editable OMML math
- `pptx:data="<json>"` on `<g>` → native chart/table graphicFrame
  (closed schemas, see §7)

## 4. Extension elements

### `<pptx:anim>` — object animation

Child of the animated element; document order = pane order.
Multiple children on one element form an ordered sequence
(entrance → motion → emphasis → exit chains).

```xml
<g id="hero">
  <circle …/>
  <pptx:anim effect="fly" start="click" dur="0.5" dir="up"/>
  <pptx:anim effect="path" path="M 0 0 L .35 0 C .5 .3 .15 .3 .3 0"
             start="after" dur="2"/>
  <pptx:anim effect="emphasis_grow_shrink" start="with" dur="0.8" size="1.1"/>
</g>
```

| Attribute | Values | Default |
|---|---|---|
| `effect` | registry name (see §6) or `path` | required |
| `start` | `click` `with` `after` | `click` |
| `dur` | seconds | effect default |
| `delay` | seconds | `0` |
| `path` | path data, slide fractions (`M 0 0 L .3 .1`) | — |
| `relative` | `true` `false` (pathEditMode) | `true` |
| `on` | `idref` of another anchor element → interactive click trigger | — |
| `repeat` | count (`3`), seconds (`2s`), or `indefinite` | — |
| `autorev` `rewind` `accel` `decel` `bounce` `restart` | booleans/fractions/enum | — |
| `after` | `dim` `hide` `hide-on-next-click` `color=#…` | — |
| `sound` | project-relative `.wav` | — |
| `dir` `amount` `color` `font` `size` | per-effect options (validated against the registry) | — |

`pptx:build="paragraph"` on the containing `<g>`/`<text>` makes an
anim sequence build one paragraph at a time.

### `<pptx:transition>` — page transition

Child of the page-root `<svg>`:

```xml
<pptx:transition effect="morph" dur="0.4" advance="5"/>
```

48 native effects (subtle/exciting/dynamic-content groups, incl.
`morph`); `advance` = auto-advance seconds; direction/shape options
pass as extra attributes (`dir`, `style`, …).

### `<pptx:notes>` — speaker notes

```xml
<pptx:notes>开场先讲大盘增速，再讲利润率结构。</pptx:notes>
```

## 5. Canvas & units

- `viewBox="0 0 W H"` defines the page; 1 px = 9,525 EMU, font px =
  0.75 pt.
- Absolute positioning only; document order = z-order.
- First full-bleed `<rect>` may promote to `p:bg`.
- Path/anim-path coordinates are slide fractions (`0–1`) unless
  `relative="false"`.

## 6. Animation registry

`effect` resolves against the preset registry: 82 entrance, 33
emphasis, 65 path presets, 53 exit, plus `path` (custom).
Unknown names are compile errors, not fallbacks.

## 7. Native objects (closed JSON payloads)

`pptx:data` carries a JSON object selecting a native object schema.
Payloads compile to `graphicFrame` parts with editable data workbooks;
fields outside the schema are compile errors.

```jsonc
// chart — compile to c:chart + embedded workbook
{"kind":"chart","type":"bar","name":"季度销售",
 "categories":["Q1","Q2","Q3","Q4"],
 "series":[{"name":"收入","values":[120,190,160,240]}],
 "x":80,"y":130,"width":540,"height":320}

// table — schema "ppt-master.semantic-table.v2", compile to a:tbl
{"kind":"table","name":"指标表","header_rows":1,
 "column_widths":[200,160,160],
 "columns":["指标","Q3","Q4"],
 "rows":[["收入","160","240"],["成本","95","140"]],
 "x":680,"y":130,"width":520,"height":200}
```

`x`/`y`/`width`/`height` are required (px, slide coordinates) because the
JSON declares itself authoritative over the `<g>` fallback geometry.
Chart `type` and table cell-style options follow the closed schemas in
`svg_to_pptx/native_objects/` and `svg_to_pptx/semantic_table.py`;
working payloads live in `examples/showcase/pages/05-data.svg`.

## 8. Validation

`svg-lint <project>` validates the full language and also runs
automatically at export: SVG core well-formedness, `pptx:` attribute
values against their enums, anim/transition effect names against the
registry, `on` idrefs resolvable, `pptx:build` targets having ≥1
paragraph. Errors are compile failures — the language has no silent
fallback.

## 9. Non-goals (v1)

SmartArt, OLE/VBA, video, hover triggers, media commands, 3D models,
masters/layouts authoring (placeholder binding only), WordArt warps.
Absence from the schema is the contract — not a runtime rejection.

## 10. Migration from the authoring dialect

| Old | New |
|---|---|
| `data-pptx-effect` on `<filter>` | `pptx:effect="…"` on the element |
| `data-pptx-vert/anchor/autofit` | `pptx:vert/anchor/autofit` |
| `data-paragraph-line-height` etc. | `pptx:line-height` `pptx:space-before` `pptx:soft-break` |
| `animations.json` sidecar | `<pptx:anim>` elements |
| transition config | `<pptx:transition>` element |
| notes sidecar | `<pptx:notes>` element |
