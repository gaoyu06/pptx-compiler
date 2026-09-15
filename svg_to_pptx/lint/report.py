"""Console summary and JSON/text report export."""

from .common import *  # noqa: F401,F403


class ReportMixin:
    """Mixin: Console summary and JSON/text report export."""

    def _print_result(self, result: Dict):
        """Print check result for a single file"""
        if result['passed']:
            if result['warnings']:
                icon = "[WARN]"
                status = "Passed (with warnings)"
            else:
                icon = "[OK]"
                status = "Passed"
        else:
            icon = "[ERROR]"
            status = "Failed"

        print(f"{icon} {result['file']} - {status}")

        # Display basic info
        if result['info']:
            info_items = []
            if 'viewbox' in result['info']:
                info_items.append(f"viewBox: {result['info']['viewbox']}")
            calibration = result['info'].get(
                'roundtrip_text_calibration'
            )
            if isinstance(calibration, dict):
                factor = calibration.get('factor')
                measured = calibration.get('measured_unchanged')
                positive = calibration.get('positive_unchanged')
                if (
                    isinstance(factor, (int, float))
                    and isinstance(measured, int)
                    and isinstance(positive, int)
                ):
                    info_items.append(
                        f'text calibration: {factor:.1%} '
                        f'({positive}/{measured} unchanged source texts)'
                    )
            if info_items:
                print(f"   {' | '.join(info_items)}")

        # Display errors
        if result['errors']:
            for error in result['errors']:
                print(f"   [ERROR] {error}")

        # Display the complete warning set from this run. The generation
        # workflow reviews all findings before one consolidated repair pass.
        if result['warnings']:
            for warning in result['warnings']:
                print(f"   [WARN] {warning}")

        print()


    def print_summary(self):
        """Print check summary"""
        self._apply_aggregated_issue_counts()

        print("=" * 80)
        print("[SUMMARY] Check Summary")
        print("=" * 80)

        print(f"\nTotal files: {self.summary['total']}")
        print(
            f"  [OK] Fully passed: {self.summary['passed']} ({self._percentage(self.summary['passed'])}%)")
        print(
            f"  [WARN] With warnings: {self.summary['warnings']} ({self._percentage(self.summary['warnings'])}%)")
        print(
            f"  [ERROR] With errors: {self.summary['errors']} ({self._percentage(self.summary['errors'])}%)")

        self._print_provenance_category_summary()
        self._print_carrier_receipt_summary()

        if self.issue_types:
            print(f"\nIssue categories:")
            for issue_type, count in sorted(self.issue_types.items(), key=lambda x: x[1], reverse=True):
                print(f"  {issue_type}: {count}")

        # spec_lock anchor comparison (only printed when a lock was found)
        self._print_anchor_value_summary()

        # Template-mode aggregation (orphan/missing roster + placeholder hints)
        self._print_template_summary()

        # Animation config aggregation.
        self._print_animation_summary()

        # Communication contract and per-page audience movement.
        self._print_communication_trace_summary()

        # Explicit PowerPoint master/layout structure aggregation.
        self._print_pptx_structure_summary()

        # Source-owned import recovery belongs to the template, not this run.
        self._print_source_import_summary()

        # Fix suggestions
        if self.summary['errors'] > 0 or self.summary['warnings'] > 0:
            print(f"\n[TIP] Common fixes:")
            print(f"  1. XML well-formedness: write typography as raw Unicode (—, ©, →, NBSP); escape XML reserved chars as &amp; &lt; &gt; &quot; &apos; — never use HTML named entities like &nbsp; &mdash; &copy;")
            print(f"  2. viewBox issues: root viewBox is the canvas authority (see references/canvas-formats.md)")
            print(
                "  3. Paint recommendation: generated SVG prefers uppercase "
                "#RRGGBB plus channel-specific opacity; compatible alternatives "
                "remain non-blocking"
            )
            print(f"  4. foreignObject: Use <text> + <tspan> for manual line breaks")
            print(f"  5. Font issues: use PPT-safe exported typefaces (e.g. Arial / Consolas, with the CJK face of the deck language)")


    def _carrier_receipt_summary(self) -> Dict:
        """Aggregate factual per-page carrier receipts for compact review."""
        receipts = [
            result.get('info', {}).get('carrier_receipt')
            for result in self.results
            if result.get('info', {}).get('carrier_receipt')
        ]
        totals = Counter({
            'text_elements': 0,
            'image_placements': 0,
            'icons': 0,
            'svg_geometry_elements': 0,
            'preset_shapes': 0,
            'page_frame_elements': 0,
            'marker_uses': 0,
            'inline_emphasis_runs': 0,
            'gradient_uses': 0,
            'filter_uses': 0,
            'text_effects': 0,
        })
        pages_with = Counter({
            'images': 0,
            'icons': 0,
            'presets': 0,
            'charts': 0,
            'tables': 0,
            'formulas': 0,
            'inline_emphasis_runs': 0,
            'gradient_uses': 0,
            'filter_uses': 0,
            'text_effects': 0,
        })
        geometry_counts: Counter[str] = Counter()
        preset_names: Counter[str] = Counter()
        native_objects: Counter[str] = Counter()
        image_frame_shares: List[float] = []

        for receipt in receipts:
            images = receipt['images']
            geometry = receipt['geometry']
            native = receipt['native_objects']
            effects = receipt.get('effects', {})
            totals['text_elements'] += receipt['text_elements']
            totals['image_placements'] += images['placements']
            totals['icons'] += receipt['icons']
            totals['preset_shapes'] += geometry['preset_shapes']
            totals['page_frame_elements'] += geometry['page_frame_elements']
            totals['marker_uses'] += sum(geometry['marker_uses'].values())
            geometry_counts.update(geometry['svg_elements'])
            preset_names.update(geometry['preset_names'])
            native_objects.update(native)

            if images['placements']:
                pages_with['images'] += 1
                image_frame_shares.append(images['max_frame_share'])
            if receipt['icons']:
                pages_with['icons'] += 1
            if geometry['preset_shapes']:
                pages_with['presets'] += 1
            if native.get('chart'):
                pages_with['charts'] += 1
            if native.get('table'):
                pages_with['tables'] += 1
            if native.get('formula_block') or native.get('formula_inline'):
                pages_with['formulas'] += 1
            for name in (
                'inline_emphasis_runs',
                'gradient_uses',
                'filter_uses',
                'text_effects',
            ):
                count = effects.get(name, 0)
                totals[name] += count
                if count > 0:
                    pages_with[name] += 1

        totals['svg_geometry_elements'] = sum(geometry_counts.values())
        frame_share_range = (
            [round(min(image_frame_shares), 4), round(max(image_frame_shares), 4)]
            if image_frame_shares
            else []
        )
        return {
            'scope': 'informational-not-a-quota',
            'pages': len(receipts),
            'totals': dict(totals),
            'pages_with': dict(pages_with),
            'relationship_pages': self._relationship_page_count(),
            'geometry_elements': dict(sorted(geometry_counts.items())),
            'preset_names': dict(sorted(preset_names.items())),
            'native_objects': dict(sorted(native_objects.items())),
            'image_page_max_frame_share_range': frame_share_range,
        }


    def _relationship_page_count(self) -> int | None:
        """Count design_spec §IX pages whose Relationships line names a carried relation.

        The executor's receipt review compares pages carrying a preset or
        connector against pages whose ``Relationships`` line names ``order``,
        ``link``, ``parent``, or ``membership``; this reads that count from the
        project's ``design_spec.md`` so the comparison is on the receipt. None
        when no exact ``design_spec.md`` is present (Quick, templates).
        """
        paths = [
            Path(result['path'])
            for result in self.results
            if result.get('path') and result.get('info', {}).get('carrier_receipt')
        ]
        if not paths:
            return None
        spec_path = self._resolve_project_path(paths[0]) / 'design_spec.md'
        if not spec_path.is_file():
            return None
        try:
            text = spec_path.read_text(encoding='utf-8')
        except OSError:
            return None
        return count_carried_relationship_pages(text)


    def _print_carrier_receipt_summary(self) -> None:
        """Print a compact actual-use receipt without a score or threshold."""
        if self.template_mode:
            return
        receipt = self._carrier_receipt_summary()
        if not receipt['pages']:
            return
        totals = receipt['totals']
        native = receipt['native_objects']
        print("\n[CARRIERS] Actual-use receipt (informational; not a quota)")
        print(
            f"  Pages: {receipt['pages']} | text: {totals['text_elements']} | "
            f"images: {totals['image_placements']} | icons: {totals['icons']}"
        )
        print(
            f"  Geometry: SVG elements {totals['svg_geometry_elements']} | "
            f"native presets {totals['preset_shapes']} | "
            f"page-frame elements {totals['page_frame_elements']} | "
            f"marker uses {totals['marker_uses']}"
        )
        pages_with = receipt['pages_with']
        print(
            f"  Effects: inline emphasis {totals['inline_emphasis_runs']} "
            f"(pages {pages_with['inline_emphasis_runs']}) | "
            f"gradients {totals['gradient_uses']} "
            f"(pages {pages_with['gradient_uses']}) | "
            f"filters {totals['filter_uses']} "
            f"(pages {pages_with['filter_uses']}) | "
            f"text effects {totals['text_effects']} "
            f"(pages {pages_with['text_effects']})"
        )
        print(
            f"  Native objects: charts {native.get('chart', 0)} | "
            f"tables {native.get('table', 0)} | formulas "
            f"{native.get('formula_block', 0) + native.get('formula_inline', 0)}"
        )
        presets = receipt['preset_names']
        preset_text = (
            ', '.join(f'{name} x{count}' for name, count in presets.items())
            if presets
            else '(none)'
        )
        print(f"  Presets: {preset_text}")
        relationship_pages = receipt.get('relationship_pages')
        preset_pages = pages_with['presets']
        if relationship_pages is None:
            print(f"  Pages carrying a preset or connector: {preset_pages}")
        else:
            print(
                f"  Relationship pages: {relationship_pages} "
                "(§IX names order / link / parent / membership) | "
                f"pages carrying a preset or connector: {preset_pages}"
            )
        image_range = receipt['image_page_max_frame_share_range']
        if image_range:
            print(
                "  Largest image-frame share on image pages: "
                f"{image_range[0] * 100:.1f}%–{image_range[1] * 100:.1f}%"
            )


    def _print_provenance_category_summary(self):
        """Print compact JSON-equivalent counts for token-safe gate handling."""
        categories = self._provenance_categories()
        rows = (
            (
                'blocking',
                len(categories['blocking']),
                'hard findings; gate also requires exit 0',
            ),
            (
                'introduced',
                len(categories['introduced']),
                'advisory; new or changed',
            ),
            (
                'inherited',
                len(categories['inherited']),
                'informational; prototype-identical',
            ),
            (
                'source-import',
                _source_import_warning_count(categories['source_import']),
                'informational; source-conversion loss',
            ),
        )

        print("\nProvenance categories:")
        for name, count, note in rows:
            print(f"  {f'{name}: {count}':<20} {note}")


    def _print_animation_summary(self):
        """Print animations.json validation issues if present."""
        if not self._animation_issues:
            return

        errors = [item for item in self._animation_issues if item[0] == 'error']
        warnings = [item for item in self._animation_issues if item[0] == 'warning']

        print("\n[ANIMATION] animations.json checks")
        for _severity, msg in errors:
            print(f"  [ERROR] {msg}")
        for _severity, msg in warnings:
            print(f"  [WARN] {msg}")


    def _print_pptx_structure_summary(self):
        """Print project-level PowerPoint structure contract issues."""
        if not self._pptx_structure_issues:
            return
        print("\n[PPTX STRUCTURE] Master/layout contract checks")
        for severity, message in self._pptx_structure_issues:
            print(f"  [{severity.upper()}] {message}")


    def _print_communication_trace_summary(self):
        """Print project-level communication trace issues."""
        if not self._communication_trace_issues:
            return
        print("\n[COMMUNICATION TRACE] Contract, Audience move, and outline roster checks")
        for severity, message in self._communication_trace_issues:
            print(f"  [{severity.upper()}] {message}")


    def _print_source_import_summary(self):
        """Print source-owned tolerant-import diagnostics as information."""
        warning_count = _source_import_warning_count(
            self._source_import_summary
        )
        if warning_count <= 0:
            return
        print("\n[SOURCE IMPORT] Template-owned compatibility diagnostics")
        print(
            f"  [INFO] {warning_count} source-import warning(s); unchanged "
            "template recovery is not attributed to generated content."
        )
        by_code = self._source_import_summary.get('by_code')
        if isinstance(by_code, dict):
            for code, count in sorted(by_code.items()):
                print(f"    {code}: {count}")


    def _print_template_summary(self):
        """Aggregate template-mode roster / placeholder issues at the bottom.

        Errors land under the ``errors`` summary count (so the exit signal
        from ``main`` agrees), warnings under ``warnings``. Both are listed
        per file so the user can act on them directly.
        """
        if not self._template_issues and self._spec_only_template_kind is None:
            return

        errors = [item for item in self._template_issues if item[0] == 'error']
        warnings = [item for item in self._template_issues if item[0] == 'warning']

        print("\n[TEMPLATE] Template mode checks")
        if errors:
            print(f"  Errors ({len(errors)}):")
            for _sev, kind, msg in errors:
                print(f"    [{kind}] {msg}")
        if warnings:
            print(f"  Warnings ({len(warnings)}):")
            for _sev, kind, msg in warnings:
                print(f"    [{kind}] {msg}")
        if self._spec_only_template_kind is not None and not errors:
            pretty_kind = self._spec_only_template_kind.title()
            print(f"  {pretty_kind} design_spec.md contract passed.")
        if not errors:
            if self._spec_only_template_kind is None:
                print("  No structural roster issues.")
                print("  Conventional placeholder-name hints may be declared through "
                      "'placeholders:' frontmatter. Placeholder bounds are mandatory "
                      "design-zone metadata.")


    def _apply_aggregated_issue_counts(self):
        """Mirror project-level aggregate issues into summary counters once."""
        if self._aggregate_counts_applied:
            return
        self._aggregate_counts_applied = True

        animation_errors = [item for item in self._animation_issues if item[0] == 'error']
        animation_warnings = [item for item in self._animation_issues if item[0] == 'warning']
        self.summary['errors'] += len(animation_errors)
        self.summary['warnings'] += len(animation_warnings)
        for severity, _msg in self._animation_issues:
            self.issue_types[f'animation_config_{severity}'] += 1

        template_errors = [item for item in self._template_issues if item[0] == 'error']
        template_warnings = [item for item in self._template_issues if item[0] == 'warning']
        self.summary['errors'] += len(template_errors)
        self.summary['warnings'] += len(template_warnings)
        for severity, kind, _msg in self._template_issues:
            self.issue_types[f'template_{kind}_{severity}'] += 1


        communication_errors = [
            item for item in self._communication_trace_issues
            if item[0] == 'error'
        ]
        communication_warnings = [
            item for item in self._communication_trace_issues
            if item[0] == 'warning'
        ]
        self.summary['errors'] += len(communication_errors)
        self.summary['warnings'] += len(communication_warnings)
        for severity, _msg in self._communication_trace_issues:
            self.issue_types[f'communication_trace_{severity}'] += 1

        structure_errors = [item for item in self._pptx_structure_issues if item[0] == 'error']
        structure_warnings = [item for item in self._pptx_structure_issues if item[0] == 'warning']
        self.summary['errors'] += len(structure_errors)
        self.summary['warnings'] += len(structure_warnings)
        for severity, _msg in self._pptx_structure_issues:
            self.issue_types[f'pptx_structure_{severity}'] += 1


    def _print_anchor_value_summary(self):
        """Print anchor comparisons without treating contextual paint/type as drift."""
        if not self._lock_seen:
            return
        has_contextual = any(
            self._anchor_value_summary[category]
            for category in ('colors', 'fonts')
        )
        has_undeclared_sizes = bool(self._anchor_value_summary['sizes'])
        if not has_contextual and not has_undeclared_sizes:
            print(
                "\n[OK] spec_lock anchor comparison: no additional contextual "
                "colors/fonts or out-of-band font sizes"
            )
            return

        if has_contextual:
            print("\nContextual values beyond spec_lock anchors (informational):")
            for category, label in (
                ('colors', 'Colors'),
                ('fonts', 'Font families'),
            ):
                items = self._anchor_value_summary.get(category, {})
                if not items:
                    continue
                entries = sorted(
                    items.items(), key=lambda item: (-len(item[1]), item[0])
                )
                print(f"  {label}:")
                for val, files in entries:
                    count = len(files)
                    suffix = "file" if count == 1 else "files"
                    print(f"    {val}  ({count} {suffix})")
            print(
                "Note: contextual page paint, gradient/effect colors, and "
                "export-safe typefaces are allowed.\n"
                "      Add a spec_lock row only when a value becomes a "
                "recurring named semantic role."
            )

        if has_undeclared_sizes:
            print(
                "\nTypography sizes outside every declared role anchor ±2px "
                "(up to 2 occurrences are sparse; the 3rd is recurring):"
            )
            entries = sorted(
                self._anchor_value_summary['sizes'].items(),
                key=lambda item: (-len(item[1]), item[0]),
            )
            for val, files in entries:
                occurrences = self._undeclared_size_occurrences.get(
                    val,
                    len(files),
                )
                file_count = len(files)
                file_suffix = "file" if file_count == 1 else "files"
                policy = (
                    "sparse"
                    if occurrences <= SPARSE_UNDECLARED_FONT_SIZE_MAX_OCCURRENCES
                    else "recurring — declare a role"
                )
                print(
                    f"  {val}  ({occurrences} occurrences in {file_count} "
                    f"{file_suffix}; {policy})"
                )


    def _percentage(self, count: int) -> int:
        """Calculate percentage"""
        if self.summary['total'] == 0:
            return 0
        return min(100, int(count / self.summary['total'] * 100))


    def export_report(self, output_file: str = 'svg_quality_report.txt'):
        """Export check report"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("pptx-compiler SVG Quality Check Report\n")
            f.write("=" * 80 + "\n\n")

            for result in self.results:
                status = "[OK] Passed" if result['passed'] else "[ERROR] Failed"
                f.write(f"{status} - {result['file']}\n")
                f.write(f"Path: {result.get('path', 'N/A')}\n")

                if result['info']:
                    f.write(f"Info: {result['info']}\n")

                if result['errors']:
                    f.write(f"\nErrors:\n")
                    for error in result['errors']:
                        f.write(f"  - {error}\n")

                if result['warnings']:
                    f.write(f"\nWarnings:\n")
                    for warning in result['warnings']:
                        f.write(f"  - {warning}\n")

                f.write("\n" + "-" * 80 + "\n\n")

            # Write summary
            f.write("\n" + "=" * 80 + "\n")
            f.write("Check Summary\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Total files: {self.summary['total']}\n")
            f.write(f"Fully passed: {self.summary['passed']}\n")
            f.write(f"With warnings: {self.summary['warnings']}\n")
            f.write(f"With errors: {self.summary['errors']}\n")

        print(f"\n[REPORT] Check report exported: {output_file}")


    def _provenance_categories(self) -> Dict[str, object]:
        """Classify every issue by provenance.

        Single source for the JSON report's ``categories`` block and the
        terminal summary, so the console and the report never disagree about
        what blocks a release export.
        """
        self._apply_aggregated_issue_counts()
        introduced: List[Dict[str, str]] = []
        blocking: List[Dict[str, str]] = []
        inherited: List[Dict[str, str]] = []
        for result in self.results:
            filename = str(result.get('file') or '')
            introduced.extend({
                'file': filename,
                'message': warning,
            } for warning in result.get('warnings', []))
            blocking.extend({
                'file': filename,
                'message': error,
            } for error in result.get('errors', []))
            info = result.get('info') or {}
            for item in info.get('inherited', []):
                if isinstance(item, dict):
                    inherited.append({
                        'file': filename,
                        'kind': str(item.get('kind') or 'prototype'),
                        'message': str(item.get('message') or ''),
                    })

        project_issues = {
            'template': [
                {'severity': severity, 'kind': kind, 'message': message}
                for severity, kind, message in self._template_issues
            ],
            'animation': [
                {'severity': severity, 'message': message}
                for severity, message in self._animation_issues
            ],
            'communication_trace': [
                {'severity': severity, 'message': message}
                for severity, message in self._communication_trace_issues
            ],
            'pptx_structure': [
                {'severity': severity, 'message': message}
                for severity, message in self._pptx_structure_issues
            ],
        }
        for group, issues in project_issues.items():
            for issue in issues:
                item = {
                    'scope': group,
                    'message': issue['message'],
                }
                if issue['severity'] == 'error':
                    blocking.append(item)
                else:
                    introduced.append(item)

        return {
            'blocking': blocking,
            'introduced': introduced,
            'inherited': inherited,
            'project_issues': project_issues,
            'source_import': dict(self._source_import_summary),
        }


    def export_json_report(
        self,
        output_file: str,
        *,
        target: str,
        stage: str,
    ) -> None:
        """Write a machine-readable quality report with provenance classes."""
        categories = self._provenance_categories()
        blocking = categories['blocking']
        introduced = categories['introduced']
        inherited = categories['inherited']
        project_issues = categories['project_issues']

        # Keep the legacy `drift` JSON field for report compatibility. Its
        # colors/fonts entries are informational anchor comparisons; sparse
        # size entries are informational until their third occurrence.
        drift = {
            category: {
                value: sorted(files)
                for value, files in sorted(values.items())
            }
            for category, values in self._anchor_value_summary.items()
        }
        source_import = categories['source_import']
        payload = {
            'schema': 'ppt-master.svg-quality-report.v1',
            'stage': stage,
            'target': str(Path(target).resolve()),
            'source_fingerprint': _quality_source_fingerprint(self.results),
            'summary': dict(self.summary),
            'issue_types': dict(sorted(self.issue_types.items())),
            'categories': {
                'blocking': {
                    'count': len(blocking),
                    'issues': blocking,
                },
                'introduced': {
                    'count': len(introduced),
                    'issues': introduced,
                },
                'inherited': {
                    'count': len(inherited),
                    'issues': inherited,
                },
                'source-import': {
                    'count': _source_import_warning_count(source_import),
                    'summary': source_import,
                },
            },
            'drift': drift,
            'carrier_receipt': self._carrier_receipt_summary(),
            'project_issues': project_issues,
            'files': self.results,
        }
        report_path = Path(output_file)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + '\n',
            encoding='utf-8',
        )
        print(f"\n[REPORT] JSON quality report exported: {report_path}")


def _source_import_warning_count(summary: Dict[str, object]) -> int:
    """Return only a schema-compatible non-negative warning count."""
    value = summary.get('warning_count')
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return 0
    return value


def _quality_source_fingerprint(results: List[Dict]) -> Dict[str, object]:
    """Bind a quality report to the exact SVG bytes that were checked."""
    files: List[Dict[str, object]] = []
    aggregate = hashlib.sha256()
    candidates = sorted(
        (
            result
            for result in results
            if result.get('exists') and result.get('path')
        ),
        key=lambda result: Path(str(result['path'])).name,
    )
    for result in candidates:
        path = Path(str(result['path']))
        file_sha256 = result.get('source_sha256')
        if not isinstance(file_sha256, str):
            files.append({
                'file': path.name,
                'sha256': None,
                'error': 'source bytes were not available during validation',
            })
            file_sha256 = 'unreadable'
        else:
            files.append({'file': path.name, 'sha256': file_sha256})
        aggregate.update(path.name.encode('utf-8'))
        aggregate.update(b'\0')
        aggregate.update(file_sha256.encode('ascii'))
        aggregate.update(b'\n')
    return {
        'algorithm': 'sha256',
        'digest': aggregate.hexdigest(),
        'file_count': len(files),
        'files': files,
    }


