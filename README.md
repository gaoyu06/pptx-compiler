# pptx-compiler

**中文** → [README.zh-CN.md](README.zh-CN.md)

An SVG superset that compiles to editable PPTX.

*Derived from [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master)
(MIT). Thanks to the upstream project — its SVG→DrawingML core is the
foundation this compiler is built on.*

## What it is

pptx-compiler turns a directory of SVG pages into a native PowerPoint
deck. Each page is a standalone, valid SVG file; PowerPoint semantics —
animations, transitions, speaker notes, editable charts, tables,
formulas — are declared inline through a small `pptx:` namespace and
compile to real OOXML objects. Nothing is rasterized: what you open in
PowerPoint is editable shapes, text, and data.

The language is specified in [SPEC.md](SPEC.md) and exercised end to
end by [examples/showcase](examples/showcase/).

## Why a separate project

ppt-master is a complete agent skill: prompt workflows, design
guidance, source-document converters, media backends, and a preview UI
around the same compiler core. That is the right shape when you want an
agent to design a whole deck from source material.

pptx-compiler keeps only the compile step and treats SVG itself as the
authoring language. The motivation: modern models already write
competent SVG, so the design layer can live in the model instead of in
bundled presets. Fewer moving parts, a smaller install, and every
PowerPoint semantic declared explicitly where it belongs — in the page.

| | ppt-master (upstream) | pptx-compiler |
|---|---|---|
| Shape | agent skill + generation workflow | compiler package (`pipx install`) |
| Page semantics | sidecar configs + design specs | inline `pptx:` namespace in each SVG |
| Animations | `animations.json` sidecar | `<pptx:anim>` elements |
| Transitions | transition config | `<pptx:transition>` element |
| Speaker notes | notes sidecar | `<pptx:notes>` element |
| Charts / tables / formulas | structured-deck contract | `pptx:data` / `pptx:formula` inline |
| Placeholder binding | structured decks | `pptx:ph` inline |
| Validation | post-export reports | `svg-lint` + compile-time errors (no silent fallback) |
| Extras | prompts, style presets, converters, image/TTS, preview UI | not bundled — authoring is the caller's job |

If you want the agent to *decide what a deck should look like*, upstream
is the right tool. If you want to *turn authored SVG into editable
PPTX* — deterministically, from any stack — that is all this project
does.

## What a page looks like

```xml
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:pptx="http://pptx-svg.dev/ns/1"
     viewBox="0 0 1280 720">
  <rect width="1280" height="720" fill="#0d1526"/>
  <text x="80" y="140" font-size="56" fill="#fff"
        pptx:effect="outer-shadow(blur=8,dist=4,color=#00000066)">
    <tspan>Quarterly Review</tspan>
  </text>
  <g id="hero">
    <circle cx="640" cy="400" r="90" fill="#e63946"/>
    <pptx:anim effect="fly" start="click" dur="0.5" dir="up"/>
    <pptx:anim effect="emphasis_grow_shrink" start="after"
               repeat="indefinite" autorev="true"/>
  </g>
  <pptx:transition effect="fade" dur="0.5"/>
  <pptx:notes>Open with the headline number.</pptx:notes>
</svg>
```

## Install

```bash
pipx install pptx-compiler
# or: pip install pptx-compiler

# zero-install run
uvx --from pptx-compiler svg-to-pptx <project>
```

## Usage

```bash
# project layout: <project>/svg_output/*.svg  (+ optional deck.xml)
svg-lint <project> --quick-generate --canonical-authoring --stage final --json
svg-to-pptx <project> --quick-generate -o out.pptx
```

Three commands ship with the package:

- `svg-to-pptx` — compile `svg_output/*.svg` (or a `deck.xml` page list)
  into a native PPTX (DrawingML shapes, charts, tables, OMML formulas,
  transitions, object animations, speaker notes)
- `svg-lint` — advisory lint for the language (also runs automatically
  at export)
- `pptx-to-svg` — import an existing PPTX back into the authoring SVG
  form for round-trip editing

For development from a checkout, the same commands exist as thin repo
wrappers: `python3 svg_to_pptx.py`, `python3 svg_lint.py`,
`python3 pptx_to_svg.py`. Internal tools are modules:
`python3 -m svg_to_pptx.update_spec`, `python3 -m svg_to_pptx.register_template`,
etc.

Run `svg-to-pptx --help` for transitions (`-t`), object animations
(`-a`), native charts/tables, and round-trip options.

## License

MIT — see [LICENSE](LICENSE). Original work © 2025-2026 Hugo He;
pptx-compiler changes © 2026 gaoyu06.
