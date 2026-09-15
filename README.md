# pptx-compiler — an SVG superset that compiles to editable PPTX

**Project-normalized SVG + `pptx:` namespace extensions → native, editable
PPTX.** The language is specified in `SPEC.md`.

The toolchain ships three commands:

- `svg-to-pptx` — compile `svg_output/*.svg` (or a `deck.xml` page list)
  into a native PPTX (DrawingML shapes, charts, tables, OMML formulas,
  transitions, object animations, speaker notes)
- `svg-lint` — run the compiler's advisory SVG lint pass
  (also runs automatically at export)
- `pptx-to-svg` — import an existing PPTX back into the authoring SVG
  form (round-trip editing)

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

Every page is a standalone, valid SVG; `pptx:` attributes and elements
compile to native DrawingML/PresentationML — editable shapes, real
animations, real speaker notes, never rasterized. See `SPEC.md` for the
full language and `examples/showcase/` for a project that exercises
every feature.

## Install

```bash
# install the CLI tools from PyPI
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

For development from a checkout, the same commands exist as thin repo
wrappers: `python3 svg_to_pptx.py`, `python3 svg_lint.py`,
`python3 pptx_to_svg.py`. Internal tools are modules:
`python3 -m svg_to_pptx.update_spec`, `python3 -m svg_to_pptx.register_template`,
etc.

Run `svg-to-pptx --help` for transitions (`-t`), object animations (`-a`),
native charts/tables, and round-trip options.

Originally derived from [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master);
the prompt workflows, design references, style presets, icon/sound libraries,
source-document converters, image/TTS backends, and preview UIs were removed
and the compiler core rebuilt into this package. MIT license — see LICENSE.
