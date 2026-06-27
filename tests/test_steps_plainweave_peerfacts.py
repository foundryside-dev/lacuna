"""Tests for the plainweave peer-facts tour legs (mirrors test_steps_plainweave.py).

The single mockable seam is `steps._plainweave_json`; the enrichment leg also self-seeds
via `steps.plainweave_seed.seed`, and the wardline leg materializes a frozen fixture via
`steps.wardline_peerfacts_seed`.
"""

from pathlib import Path

from tour import steps

# Frozen enrichment anchors (the contract the leg pins against).
ENRICH_COVERED = "python:function:specimen.cli._add_book"
ENRICH_ABSENT = "python:function:tour.__main__.main"
ENRICH_UNAVAILABLE = "python:function:specimen.cli._does_not_exist"


def _enrichment_env(covered_status="present", absent_status="absent", unavailable_status="unavailable"):
    return {
        "ok": True,
        "data": {
            "items": [
                {
                    "entity_ref": ENRICH_COVERED,
                    "status": covered_status,
                    "requirements": [{"requirement_id": "req-1"}] if covered_status == "present" else [],
                    "reason": None if covered_status == "present" else "x",
                    "freshness": "current",
                },
                {
                    "entity_ref": ENRICH_ABSENT,
                    "status": absent_status,
                    "requirements": [],
                    "reason": "Entity resolves locally but no requirement is bound to it.",
                    "freshness": "unknown",
                },
                {
                    "entity_ref": ENRICH_UNAVAILABLE,
                    "status": unavailable_status,
                    "requirements": [],
                    "reason": "Entity identity is not resolvable locally; cannot determine requirements.",
                    "freshness": "unavailable",
                },
            ]
        },
    }


def _arm_enrichment(monkeypatch, env):
    monkeypatch.setattr(steps, "_tool", lambda name: f"/home/john/.local/bin/{name}")
    monkeypatch.setattr(steps.plainweave_seed, "seed", lambda pw: None)

    def pwj(args, cwd=None):
        if args[:1] == ["requirements-enrichment"]:
            return env
        return {"ok": True, "data": {}}

    monkeypatch.setattr(steps, "_plainweave_json", pwj)


def test_enrichment_surfaces_pair_on_present_absent_unavailable(monkeypatch):
    _arm_enrichment(monkeypatch, _enrichment_env())
    r = steps.plainweave_requirements_enrichment()
    assert r.name == "plainweave requirements-enrichment"
    assert r.ok is True
    assert ("pw-requirements-enrichment", "specimen.cli._add_book") in r.surfaced
    assert len(r.surfaced) == 1


def test_enrichment_drops_pair_when_unavailable_collapses_to_absent(monkeypatch):
    # The no-silent-clean regression: if the unresolvable ref wrongly reads `absent`
    # instead of `unavailable`, the fact must NOT surface (the pair is omitted).
    _arm_enrichment(monkeypatch, _enrichment_env(unavailable_status="absent"))
    r = steps.plainweave_requirements_enrichment()
    assert r.ok is False
    assert r.surfaced == ()


def test_enrichment_degrades_never_raises_on_failed_call(monkeypatch):
    monkeypatch.setattr(steps, "_tool", lambda name: f"/home/john/.local/bin/{name}")
    monkeypatch.setattr(steps.plainweave_seed, "seed", lambda pw: None)
    monkeypatch.setattr(steps, "_plainweave_json", lambda args, cwd=None: None)
    r = steps.plainweave_requirements_enrichment()
    assert r.ok is False
    assert r.surfaced == ()


# ── pw-wardline-peer-facts ────────────────────────────────────────────────────
_PRESENT_DIR = Path("/tmp/pw-present")
_ABSENT_DIR = Path("/tmp/pw-absent")


def _present_env(freshness="current", resolved=True, scope_mismatch=True):
    facts = [
        {"qualname": "specimen.peerfacts.unsafe_sink", "suppression_state": "active", "non_defect": False, "kind": "defect"},
        {"qualname": "specimen.peerfacts.audited_helper", "suppression_state": "active", "non_defect": True, "kind": "fact"},
    ]
    degraded = [{"code": "wardline_scope_mismatch", "message": "out-of-scope prior finding"}] if scope_mismatch else []
    resolved_items = [{"fingerprint": "fp-resolved", "rule_id": "PY-WL-101", "location": {"path": "specimen/peerfacts.py"}}]
    return {
        "ok": True,
        "data": {
            "freshness": freshness,
            "facts": facts,
            "resolved_or_unseen": resolved_items if resolved else [],
            "degraded": degraded,
        },
    }


def _absent_env(freshness="unavailable", findings_absent=True):
    degraded = [{"code": "wardline_findings_absent", "message": "no snapshot"}] if findings_absent else []
    return {"ok": True, "data": {"freshness": freshness, "facts": [], "resolved_or_unseen": [], "degraded": degraded}}


def _arm_wardline(monkeypatch, present_env, absent_env):
    monkeypatch.setattr(steps, "_tool", lambda name: f"/home/john/.local/bin/{name}")
    monkeypatch.setattr(steps.wardline_peerfacts_seed, "materialize", lambda: _PRESENT_DIR)
    monkeypatch.setattr(steps.wardline_peerfacts_seed, "materialize_absent", lambda: _ABSENT_DIR)

    def pwj(args, cwd=None):
        if cwd == _ABSENT_DIR:
            return absent_env
        return present_env

    monkeypatch.setattr(steps, "_plainweave_json", pwj)


def test_wardline_peer_facts_surfaces_pair_on_full_scenario(monkeypatch):
    _arm_wardline(monkeypatch, _present_env(), _absent_env())
    r = steps.plainweave_wardline_peer_facts()
    assert r.name == "plainweave wardline peer facts"
    assert r.ok is True
    assert ("pw-wardline-peer-facts", "specimen.peerfacts.unsafe_sink") in r.surfaced
    assert len(r.surfaced) == 1


def test_wardline_peer_facts_drops_pair_when_resolved_unseen_empty(monkeypatch):
    _arm_wardline(monkeypatch, _present_env(resolved=False), _absent_env())
    r = steps.plainweave_wardline_peer_facts()
    assert r.ok is False
    assert r.surfaced == ()


def test_wardline_peer_facts_drops_pair_when_scope_mismatch_not_flagged(monkeypatch):
    _arm_wardline(monkeypatch, _present_env(scope_mismatch=False), _absent_env())
    r = steps.plainweave_wardline_peer_facts()
    assert r.ok is False
    assert r.surfaced == ()


def test_wardline_peer_facts_drops_pair_when_absent_not_unavailable(monkeypatch):
    # The no-silent-clean regression: an absent .wardline/ that reads `current` (clean)
    # instead of `unavailable` must NOT surface the fact.
    _arm_wardline(monkeypatch, _present_env(), _absent_env(freshness="current", findings_absent=False))
    r = steps.plainweave_wardline_peer_facts()
    assert r.ok is False
    assert r.surfaced == ()


def test_wardline_peer_facts_degrades_never_raises_on_failed_call(monkeypatch):
    monkeypatch.setattr(steps, "_tool", lambda name: f"/home/john/.local/bin/{name}")
    monkeypatch.setattr(steps.wardline_peerfacts_seed, "materialize", lambda: _PRESENT_DIR)
    monkeypatch.setattr(steps.wardline_peerfacts_seed, "materialize_absent", lambda: _ABSENT_DIR)
    monkeypatch.setattr(steps, "_plainweave_json", lambda args, cwd=None: None)
    r = steps.plainweave_wardline_peer_facts()
    assert r.ok is False
    assert r.surfaced == ()
