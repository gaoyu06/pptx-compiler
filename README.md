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

## Install

```bash
# zero-install run straight from the repo
uvx --from git+https://github.com/gaoyu06/pptx-compiler svg-to-pptx <project>

# or install the CLI tools
pipx install git+https://github.com/gaoyu06/pptx-compiler
# or: pip install git+https://github.com/gaoyu06/pptx-compiler
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
