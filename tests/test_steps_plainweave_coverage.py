"""Tests for the plainweave_coverage tour leg (baseline / verification / dossier).

The single mockable seam is steps._plainweave_json; the leg self-seeds via
steps.plainweave_seed.seed (mocked to return a canned {locator: req_id} map) in a
workspace from steps.plainweave_seed.materialize_workspace (mocked to a fixed Path).

The leg is MULTI-PAIR (emits up to 3 pairs, ok = len==3, like plainweave_intent), so a
per-conjunct drop-test asserts the SPECIFIC pair is gone and the OTHER two remain — NOT
`surfaced == ()` (that single-pair shape from the peer-facts tests would falsely fail here).
"""

from pathlib import Path

from tour import steps
from tour.plainweave_seed import ADD_BOOK, CLI_MAIN, REGISTER

_WS = Path("/tmp/pw-coverage-ws")
ADD_BOOK_ID = "REQ-lacuna-0001"
CLI_MAIN_ID = "REQ-lacuna-0002"
REGISTER_ID = "REQ-lacuna-0003"
BASELINE_ID = "BASELINE-0001"

BASELINE_PAIR = ("pw-baseline-drift", "specimen.cli._add_book")
VERIFY_PAIR = ("pw-verification-status", "specimen.cli._register")
DOSSIER_PAIR = ("pw-requirement-dossier", "specimen.cli.main")


def _diff_env(drift_flagged=True, control_unchanged=True):
    return {"ok": True, "data": {"baseline_id": BASELINE_ID, "summary": {
        "unchanged": 2, "changed": 0, "missing_current": 0,
        "new_since_baseline": 0, "superseded_since_baseline": 1 if drift_flagged else 0},
        "items": [
            {"id": ADD_BOOK_ID, "requirement_id": "req-1",
             "status": "superseded_since_baseline" if drift_flagged else "unchanged"},
            {"id": CLI_MAIN_ID, "requirement_id": "req-2",
             "status": "unchanged" if control_unchanged else "superseded_since_baseline"},
        ]}}


def _list_env(items):
    return {"ok": True, "data": {"items": items, "has_more": False, "next_offset": None}}


def _status_env(rid, status, reason):
    return {"ok": True, "data": {
        "requirement_id": "req-x", "id": rid, "current_version": 1, "status": status,
        "reasons": [{"code": reason, "message": "m", "evidence_id": None}],
        "current_evidence": [], "stale_evidence": []}}


def _dossier_env(verification_ok=True, baseline_current=True, trace_present=True):
    return {"ok": True, "data": {
        "identity": {"id": CLI_MAIN_ID, "requirement_id": "req-2",
                     "stable_id": "plainweave:req:lacuna:0002", "current_version": 1},
        "verification": {"status": "satisfied" if verification_ok else "unverified",
                         "reasons": [{"code": "passing_evidence", "evidence_id": "EVID-0001"}],
                         "current_evidence": [], "stale_evidence": []},
        "baseline_exposure": {"summary": {"current": 1}, "items": (
            [{"baseline_id": BASELINE_ID, "state": "current"}] if baseline_current else [])},
        "traces": {"incoming": ([{"id": "LINK-0001", "state": "accepted"}]
                                if trace_present else []), "outgoing": []},
        "acceptance_criteria": {"current_version": [], "active_draft": []},
        "computed_gaps": [], "next_actions": [],
        "peer_facts": {"live_peer_calls": False, "sources": ["loomweave"]}}}


def _arm_coverage(
    monkeypatch, *,
    baseline_drift_flagged=True, baseline_control_unchanged=True, no_baseline_honest=True,
    verify_satisfied=True, verify_unverified=True, unverified_listed=True,
    verify_stale=True, stale_listed=True,
    dossier_verification_ok=True, dossier_baseline_current=True, dossier_trace_present=True,
    dossier_unknown_honest=True,
):
    monkeypatch.setattr(steps, "_tool", lambda name: f"/home/john/.local/bin/{name}")
    monkeypatch.setattr(steps, "_plainweave_supports", lambda sub: True)
    monkeypatch.setattr(steps.plainweave_seed, "materialize_workspace", lambda: _WS)
    monkeypatch.setattr(steps.plainweave_seed, "seed",
                        lambda pw, **kw: {ADD_BOOK: ADD_BOOK_ID, CLI_MAIN: CLI_MAIN_ID, REGISTER: REGISTER_ID})

    def pwj(args, cwd=None):
        # ── setup calls (return handle envelopes the leg threads forward) ──
        if args[:2] == ["baseline", "create"]:
            return {"ok": True, "data": {"id": BASELINE_ID}}
        if args[:3] == ["verify", "method", "add"]:
            return {"ok": True, "data": {"id": "VERM-0001"}}
        if args[:3] == ["verify", "evidence", "record"]:
            return {"ok": True, "data": {"id": "EVID-0001"}}
        if args[:2] == ["req", "supersede"]:
            return {"ok": True, "data": {"id": args[2]}}
        # ── reads ──
        if args[:2] == ["baseline", "diff"]:
            if args[2] == steps.PLAINWEAVE_COVERAGE_BOGUS_BASELINE:
                # no-baseline arm (run BEFORE create). Honest: ok=False NOT_FOUND (real
                # plainweave 1.2.0). Dishonest knob: a silent clean (ok=True with a
                # populated/unchanged diff) that the conjunct must REFUSE to credit.
                if no_baseline_honest:
                    return {"ok": False, "error": {"code": "NOT_FOUND", "message": "baseline not found"}}
                return {"ok": True, "data": {"baseline_id": BASELINE_ID, "summary": {},
                                             "items": [{"id": ADD_BOOK_ID, "status": "unchanged"}]}}
            return _diff_env(baseline_drift_flagged, baseline_control_unchanged)
        if args[:2] == ["verify", "status"]:
            rid = args[2]
            if rid == CLI_MAIN_ID:
                return _status_env(rid, "satisfied" if verify_satisfied else "unverified",
                                   "passing_evidence" if verify_satisfied else "no_current_evidence")
            if rid == REGISTER_ID:
                return _status_env(rid, "unverified" if verify_unverified else "satisfied",
                                   "no_current_evidence" if verify_unverified else "passing_evidence")
            if rid == ADD_BOOK_ID:
                return _status_env(rid, "stale" if verify_stale else "satisfied",
                                   "stale_evidence" if verify_stale else "passing_evidence")
        if args[:2] == ["status", "unverified"]:
            return _list_env([{"id": REGISTER_ID}] if unverified_listed else [])
        if args[:2] == ["status", "stale"]:
            return _list_env([{"id": ADD_BOOK_ID}] if stale_listed else [])
        if args[:1] == ["dossier"]:
            if args[1] == steps.PLAINWEAVE_COVERAGE_BOGUS_REQ:
                if dossier_unknown_honest:
                    return {"ok": False, "error": {"code": "NOT_FOUND", "message": "x"}}
                return {"ok": True, "data": {"identity": {}, "verification": {}}}
            return _dossier_env(dossier_verification_ok, dossier_baseline_current, dossier_trace_present)
        return {"ok": True, "data": {}}

    monkeypatch.setattr(steps, "_plainweave_json", pwj)


def test_coverage_surfaces_all_three_pairs_on_full_scenario(monkeypatch):
    _arm_coverage(monkeypatch)
    r = steps.plainweave_coverage()
    assert r.name == "plainweave coverage"
    assert r.ok is True
    assert set(r.surfaced) == {BASELINE_PAIR, VERIFY_PAIR, DOSSIER_PAIR}
    assert len(r.surfaced) == 3


def test_coverage_degrades_never_raises_on_failed_call(monkeypatch):
    monkeypatch.setattr(steps, "_tool", lambda name: f"/home/john/.local/bin/{name}")
    monkeypatch.setattr(steps, "_plainweave_supports", lambda sub: True)
    monkeypatch.setattr(steps.plainweave_seed, "materialize_workspace", lambda: _WS)
    monkeypatch.setattr(steps.plainweave_seed, "seed",
                        lambda pw, **kw: {ADD_BOOK: ADD_BOOK_ID, CLI_MAIN: CLI_MAIN_ID, REGISTER: REGISTER_ID})
    monkeypatch.setattr(steps, "_plainweave_json", lambda args, cwd=None: None)
    r = steps.plainweave_coverage()
    assert r.ok is False
    assert r.surfaced == ()
    # A present-but-failed call is [WARN] (ran and degraded), NOT [N/A] (gated).
    assert r.available is True


def test_coverage_capability_gated_when_surface_absent(monkeypatch):
    # plainweave installed but the base subcommands are absent (stripped/pre-baseline
    # build). The leg must render [N/A] (available=False) with a machine-readable
    # reason — not [WARN], not faked green, and never raising.
    monkeypatch.setattr(steps, "_plainweave_supports", lambda sub: False)
    r = steps.plainweave_coverage()
    assert r.available is False
    assert r.ok is False
    assert r.surfaced == ()
    assert "capability-gated" in r.detail
    assert "baseline" in r.detail


def test_coverage_detail_is_digit_free(monkeypatch):
    # `detail` is rendered into the byte-locked tour.md; any digit (a live count/id)
    # would break determinism. Live data must ride `note`, not `detail`.
    _arm_coverage(monkeypatch)
    r = steps.plainweave_coverage()
    assert not any(ch.isdigit() for ch in r.detail)


# ── Per-conjunct drop-tests: every condition in each cell's gate is load-bearing ──
# MULTI-PAIR leg: each test drives exactly ONE conjunct False and asserts THAT cell's
# pair is gone while the OTHER two remain (isolation), and r.ok goes False.


def test_coverage_drops_baseline_when_drift_not_flagged(monkeypatch):
    _arm_coverage(monkeypatch, baseline_drift_flagged=False)
    r = steps.plainweave_coverage()
    assert r.ok is False
    assert BASELINE_PAIR not in r.surfaced
    assert VERIFY_PAIR in r.surfaced and DOSSIER_PAIR in r.surfaced


def test_coverage_drops_baseline_when_control_flagged_as_drift(monkeypatch):
    _arm_coverage(monkeypatch, baseline_control_unchanged=False)
    r = steps.plainweave_coverage()
    assert r.ok is False
    assert BASELINE_PAIR not in r.surfaced
    assert VERIFY_PAIR in r.surfaced and DOSSIER_PAIR in r.surfaced


def test_coverage_drops_baseline_when_no_baseline_reads_silently_clean(monkeypatch):
    # The no-silent-clean regression: a no-baseline store whose pre-create `baseline diff`
    # silently returns ok=True with a populated/clean diff (instead of an honest NOT_FOUND)
    # must NOT credit the no_baseline_honest conjunct.
    _arm_coverage(monkeypatch, no_baseline_honest=False)
    r = steps.plainweave_coverage()
    assert r.ok is False
    assert BASELINE_PAIR not in r.surfaced
    assert VERIFY_PAIR in r.surfaced and DOSSIER_PAIR in r.surfaced


def test_coverage_drops_verify_when_not_satisfied(monkeypatch):
    _arm_coverage(monkeypatch, verify_satisfied=False)
    r = steps.plainweave_coverage()
    assert r.ok is False
    assert VERIFY_PAIR not in r.surfaced
    assert BASELINE_PAIR in r.surfaced and DOSSIER_PAIR in r.surfaced


def test_coverage_drops_verify_when_unverified_reads_satisfied(monkeypatch):
    # The no-silent-clean regression: a method-but-no-evidence req that wrongly reads
    # satisfied must NOT credit the cell (never silently verified).
    _arm_coverage(monkeypatch, verify_unverified=False)
    r = steps.plainweave_coverage()
    assert r.ok is False
    assert VERIFY_PAIR not in r.surfaced
    assert BASELINE_PAIR in r.surfaced and DOSSIER_PAIR in r.surfaced


def test_coverage_drops_verify_when_unverified_not_listed(monkeypatch):
    _arm_coverage(monkeypatch, unverified_listed=False)
    r = steps.plainweave_coverage()
    assert r.ok is False
    assert VERIFY_PAIR not in r.surfaced
    assert BASELINE_PAIR in r.surfaced and DOSSIER_PAIR in r.surfaced


def test_coverage_drops_verify_when_stale_reads_satisfied(monkeypatch):
    # Orphaned evidence that wrongly reads satisfied (silently passing) must NOT credit.
    _arm_coverage(monkeypatch, verify_stale=False)
    r = steps.plainweave_coverage()
    assert r.ok is False
    assert VERIFY_PAIR not in r.surfaced
    assert BASELINE_PAIR in r.surfaced and DOSSIER_PAIR in r.surfaced


def test_coverage_drops_verify_when_stale_not_listed(monkeypatch):
    _arm_coverage(monkeypatch, stale_listed=False)
    r = steps.plainweave_coverage()
    assert r.ok is False
    assert VERIFY_PAIR not in r.surfaced
    assert BASELINE_PAIR in r.surfaced and DOSSIER_PAIR in r.surfaced


def test_coverage_drops_dossier_when_verification_inconsistent(monkeypatch):
    _arm_coverage(monkeypatch, dossier_verification_ok=False)
    r = steps.plainweave_coverage()
    assert r.ok is False
    assert DOSSIER_PAIR not in r.surfaced
    assert BASELINE_PAIR in r.surfaced and VERIFY_PAIR in r.surfaced


def test_coverage_drops_dossier_when_baseline_not_current(monkeypatch):
    _arm_coverage(monkeypatch, dossier_baseline_current=False)
    r = steps.plainweave_coverage()
    assert r.ok is False
    assert DOSSIER_PAIR not in r.surfaced
    assert BASELINE_PAIR in r.surfaced and VERIFY_PAIR in r.surfaced


def test_coverage_drops_dossier_when_trace_absent(monkeypatch):
    _arm_coverage(monkeypatch, dossier_trace_present=False)
    r = steps.plainweave_coverage()
    assert r.ok is False
    assert DOSSIER_PAIR not in r.surfaced
    assert BASELINE_PAIR in r.surfaced and VERIFY_PAIR in r.surfaced


def test_coverage_drops_dossier_when_unknown_returns_empty_as_clean(monkeypatch):
    # The no-silent-clean regression: an unknown req id that returns an ok envelope with
    # an empty body (instead of an honest error) must NOT credit the cell.
    _arm_coverage(monkeypatch, dossier_unknown_honest=False)
    r = steps.plainweave_coverage()
    assert r.ok is False
    assert DOSSIER_PAIR not in r.surfaced
    assert BASELINE_PAIR in r.surfaced and VERIFY_PAIR in r.surfaced
