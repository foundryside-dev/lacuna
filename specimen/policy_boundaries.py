"""Planted Legis lacuna — @policy_boundary metadata vs behavioural evidence.

``validated_recovery`` is the HEALTHY boundary: its evidence test runs and
asserts the suppressed policy. ``pinned_import`` is the LACUNA
(lg-disabled-boundary-evidence): its evidence test is @pytest.mark.skip, so
`legis policy-boundary-check` flags POLICY_BOUNDARY_TEST_DISABLED. Permanent
demonstration fixtures — do not "fix" either.

NOTE (test_fingerprint pinning): legis pins each boundary's evidence test by
``test_fingerprint = content_hash`` of a *version-stable* AST serialization
(legis >= 1.1.0 ``decorator._stable_ast_repr`` — every AST field emitted in a
fixed order). Unlike the older ``ast.dump`` hash, this does NOT drift across
CPython versions: the same unchanged test hashes identically under Python 3.12
and 3.13. The values below were re-pinned once for the legis 1.1.0 scheme change
(a breaking bump of the serializer itself — legis-13b4e97bf4 — not a Python
version difference), and are stable from here. If a boundary ever reports
POLICY_BOUNDARY_TEST_FINGERPRINT_MISMATCH while the test source is unchanged,
regenerate against the *installed* legis (``fingerprint_source`` over the
decorated test segment), not the editable dev tree. Run the check straight:
``legis policy-boundary-check --root specimen --repo-root .`` — exit 1, flags
``pinned_import`` (bare qualname, not dotted) as POLICY_BOUNDARY_TEST_DISABLED,
leaves ``validated_recovery`` clean, and degrades specimen/nesting_bomb.py
gracefully (POLICY_BOUNDARY_FILE_TOO_COMPLEX, scan continues). The old
recursion-limit workaround is obsolete.
"""

from __future__ import annotations

from legis.policy.decorator import policy_boundary


@policy_boundary(
    source="docs/flaws/lg-disabled-boundary-evidence.md",
    suppresses=("no-broad-except",),
    invariant="catalog payloads are type-validated before recovery handling is allowed",
    test_ref="tests/test_policy_boundaries.py::test_validated_recovery_boundary",
    test_fingerprint="62521cb624e51e48c4f12075ab6fb3257142caacc350cb8e7fae506d0f1d05ac",
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
    test_fingerprint="abbdf270093d01e37f66f1adf6e08f1e9d26543478788e2d45cea78e3a9f5643",
)
def pinned_import(name: str) -> str:
    """LACUNA (lg-disabled-boundary-evidence): the evidence test is skip-marked."""
    if name not in {"json", "csv"}:
        raise ValueError("import not allowlisted")
    return name
