"""`python -m tour [tour|verify]` — run the showcase or assert it.

tour   : drive every live tool, write docs/tour.md and docs/matrix.md, print a report.
verify : run the same drive in assert-mode — exit non-zero if any expected lacuna
         is not surfaced, or if the regenerated narrative differs from the committed one.
"""

from __future__ import annotations

import sys
from pathlib import Path

from tour import steps
from tour.capability import detect
from tour.manifest import load_manifest
from tour.report import coverage, render_matrix_md, render_tour_md

ROOT = Path("/home/john/lacuna")
MANIFEST = ROOT / "tour" / "lacunae.toml"
TOUR_MD = ROOT / "docs" / "tour.md"
MATRIX_MD = ROOT / "docs" / "matrix.md"


def _drive() -> tuple[list, list]:
    caps = detect()
    results = [
        steps.loomweave_analyze(),
        steps.loomweave_structure(),
        steps.loomweave_relations(),
        steps.loomweave_navigation(),
        steps.loomweave_findings(),
        steps.wardline_scan(),
        steps.wardline_fail_closed(),
        steps.legis_govern(),
        steps.legis_policy_check(),
        steps.legis_reject_malformed(),
        steps.filigree_findings(),
        steps.filigree_work_cycle(),
    ]
    return caps, results


def run_tour() -> int:
    caps, results = _drive()
    TOUR_MD.parent.mkdir(parents=True, exist_ok=True)
    TOUR_MD.write_text(render_tour_md(results))
    manifest = load_manifest(MANIFEST)
    MATRIX_MD.write_text(render_matrix_md(manifest, caps))
    cov = coverage(manifest, results)
    print(render_tour_md(results))
    for r in results:
        if r.note:
            print(f"note [{r.name}]: {r.note}")
    print(f"\nDemonstrated lacunae: {sorted(cov.demonstrated_ids)}")
    print(f"Not surfaced:         {sorted(cov.missing_ids)}")
    return 0


def run_verify() -> int:
    caps, results = _drive()
    manifest = load_manifest(MANIFEST)
    cov = coverage(manifest, results)
    failures: list[str] = []

    # 1. Every lacuna whose expected tool is LIVE must be surfaced.
    live = {c.name for c in caps if c.available}
    for lac in manifest.lacunae:
        if lac.expected_tool in live and lac.id in cov.missing_ids:
            failures.append(f"expected lacuna not surfaced: {lac.id} ({lac.expected_rule})")

    # 2. Narrative lockstep: regenerated docs must match the committed files.
    fresh_tour = render_tour_md(results)
    if not TOUR_MD.exists() or TOUR_MD.read_text() != fresh_tour:
        failures.append("docs/tour.md is stale — run `make tour` and commit")
    fresh_matrix = render_matrix_md(manifest, caps)
    if not MATRIX_MD.exists() or MATRIX_MD.read_text() != fresh_matrix:
        failures.append("docs/matrix.md is stale — run `make tour` and commit")

    if failures:
        print("VERIFY FAILED:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("VERIFY OK — every live lacuna surfaced; narrative in lockstep.")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    mode = args[0] if args else "tour"
    if mode == "verify":
        return run_verify()
    return run_tour()


if __name__ == "__main__":
    raise SystemExit(main())
