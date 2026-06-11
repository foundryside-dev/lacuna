"""Planted Legis lacuna — @policy_boundary metadata vs behavioural evidence.

``validated_recovery`` is the HEALTHY boundary: its evidence test runs and
asserts the suppressed policy. ``pinned_import`` is the LACUNA
(lg-disabled-boundary-evidence): its evidence test is @pytest.mark.skip, so
`legis policy-boundary-check` flags POLICY_BOUNDARY_TEST_DISABLED. Permanent
demonstration fixtures — do not "fix" either.

NOTE (harness): the stock `legis policy-boundary-check --root specimen` CLI
hits RecursionError walking specimen/nesting_bomb.py (the planted deep-nesting
bomb — also permanent). Invoke the check with a raised recursion limit:
``.venv/bin/python -c "import sys; sys.setrecursionlimit(100000); \
from legis.cli import main; sys.exit(main())" policy-boundary-check \
--root specimen --repo-root .`` — exit 1, flags ``pinned_import`` (bare
qualname, not dotted) and not ``validated_recovery``.
"""

from __future__ import annotations

from legis.policy.decorator import policy_boundary


@policy_boundary(
    source="docs/flaws/lg-disabled-boundary-evidence.md",
    suppresses=("no-broad-except",),
    invariant="catalog payloads are type-validated before recovery handling is allowed",
    test_ref="tests/test_policy_boundaries.py::test_validated_recovery_boundary",
    test_fingerprint="a38e30007cc0970a9853cfb7cc32888110bd47c8c87104006cd2ddf284a3a0e7",
)
def validated_recovery(payload: dict) -> dict:
    if not isinstance(payload, dict):
        raise TypeError("payload must be a dict")
    return payload


@policy_boundary(
    source="docs/flaws/lg-disabled-boundary-evidence.md",
    suppresses=("import-allowlist",),
    invariant="plugin imports are pinned to the catalog allowlist",
    test_ref="tests/test_policy_boundaries.py::test_pinned_import_boundary",
    test_fingerprint="6930d963db51c6a1b18925886e68dc2bf3e0445ca25da3ea915952d9bf6279a5",
)
def pinned_import(name: str) -> str:
    """LACUNA (lg-disabled-boundary-evidence): the evidence test is skip-marked."""
    if name not in {"json", "csv"}:
        raise ValueError("import not allowlisted")
    return name
