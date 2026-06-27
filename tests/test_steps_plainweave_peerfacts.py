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
