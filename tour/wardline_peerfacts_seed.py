"""Frozen two-snapshot Wardline fixture for the plainweave+wardline tour leg.

Materializes a deterministic .wardline/ into a fresh temp workspace so the
`plainweave wardline-peer-facts` producer has a manifest-bearing scenario to read:
a finding resolved in scope, an out-of-scope prior finding honestly flagged, and a
stable active-defect + non-defect pair. Content is frozen constants -> byte-identical
every run; the temp path never appears in rendered output, so `make verify` stays
deterministic. (Lacuna's live .wardline/ is a volatile rolling window with no scan
manifest, so it cannot drive this; we plant our own.)
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

RULESET = "demo-ruleset-1"


def _finding(fingerprint, kind, path, qualname, severity, message):
    return {
        "fingerprint": fingerprint,
        "rule_id": "PY-WL-101",
        "kind": kind,
        "severity": severity,
        "suppression_state": "active",
        "suppression_reason": None,
        "location": {"path": path, "line_start": 1, "line_end": 1, "col_start": 0, "col_end": 1},
        "qualname": qualname,
        "message": message,
    }


def _manifest(covered):
    return {
        "kind": "scan_manifest",
        "scan_id": "scan-fixed",
        "ruleset_id": RULESET,
        "commit": "0" * 40,
        "scope": {"covered_paths": covered},
    }


# Stable findings present in BOTH snapshots (never resolved/unseen).
_ACTIVE = _finding("fp-active", "defect", "specimen/peerfacts.py", "specimen.peerfacts.unsafe_sink", "ERROR", "untrusted reaches a trusted producer")
_NONDEFECT = _finding("fp-nondefect", "fact", "specimen/peerfacts.py", "specimen.peerfacts.audited_helper", "INFO", "trust boundary documented")
# Resolved in scope: gone from latest; its path IS in the latest scan's covered scope.
_RESOLVED = _finding("fp-resolved", "defect", "specimen/peerfacts.py", "specimen.peerfacts.fixed_sink", "WARN", "previously untrusted; now bounded")
# Out of latest scope: gone from latest; its path is NOT in the latest covered scope ->
# indeterminate (never silently "resolved") + an honest wardline_scope_mismatch.
_OUTOFSCOPE = _finding("fp-outofscope", "defect", "specimen/legacy_area.py", "specimen.legacy_area.untouched", "ERROR", "not re-scanned this run")

_PRIOR = [_manifest(["specimen/peerfacts.py", "specimen/legacy_area.py"]), _ACTIVE, _NONDEFECT, _RESOLVED, _OUTOFSCOPE]
_LATEST = [_manifest(["specimen/peerfacts.py"]), _ACTIVE, _NONDEFECT]


def _write(wdir: Path, name: str, records: list) -> None:
    wdir.mkdir(parents=True, exist_ok=True)
    (wdir / name).write_text("\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")


def materialize() -> Path:
    """Write the frozen two-snapshot .wardline/ into a fresh temp dir; return its root."""
    root = Path(tempfile.mkdtemp(prefix="pw-wardline-peerfacts-"))
    wdir = root / ".wardline"
    _write(wdir, "20260101T000000Z-findings.jsonl", _PRIOR)
    _write(wdir, "20260102T000000Z-findings.jsonl", _LATEST)
    return root


def materialize_absent() -> Path:
    """A fresh temp dir with NO .wardline/ — drives the absent->unavailable assertion."""
    return Path(tempfile.mkdtemp(prefix="pw-wardline-absent-"))
