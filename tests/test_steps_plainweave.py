"""Tests for the plainweave intent-coverage tour leg (mirrors test_steps_legis.py).

The single mockable seam is `steps._plainweave_json`; the seed is `plainweave_seed.seed`.
"""

from tour import plainweave_seed, steps

ADD_BOOK_LOC = "python:function:specimen.cli._add_book"
REGISTER_LOC = "python:function:specimen.cli._register"
CLI_MAIN_LOC = "python:function:specimen.cli.main"
TOUR_MAIN_LOC = "python:function:tour.__main__.main"


def _surface(loc, sei):
    return {"locator": loc, "sei": sei, "surface_classes": [], "goals": []}


# Canonical "everything works" coverage: 2 covered (justified) : 2 uncovered.
_COV_DEFAULT = {
    "north_star": {"numerator": 2, "denominator": 4, "ratio": 0.5},
    "denominator_complete": False,
    "coverage": {"absent_tags": ["exported-api", "http-route"]},
    "justified": [_surface(ADD_BOOK_LOC, "sei-add"), _surface(CLI_MAIN_LOC, "sei-main")],
    "unjustified": [_surface(REGISTER_LOC, "sei-reg"), _surface(TOUR_MAIN_LOC, "sei-tour")],
}
_COV_SCOPED = {
    "north_star": {"numerator": 2, "denominator": 3, "ratio": 0.667},
    "denominator_complete": False,
    "coverage": {"absent_tags": ["exported-api", "http-route"]},
    "justified": [_surface(ADD_BOOK_LOC, "sei-add"), _surface(CLI_MAIN_LOC, "sei-main")],
    "unjustified": [_surface(REGISTER_LOC, "sei-reg")],  # tour.__main__.main scoped out
}
_ORPHANS = {"items": [{"level": "code", "node_id": "sei-tour"}], "has_more": False, "next_offset": None}


def _fake_pwj(default, scoped, orphans):
    def pwj(args):
        if args[:2] == ["intent", "coverage"] and "--exclude-namespace" in args:
            return {"ok": True, "data": scoped}
        if args[:2] == ["intent", "coverage"]:
            return {"ok": True, "data": default}
        if args[:3] == ["intent", "orphans", "code"]:
            return {"ok": True, "data": orphans}
        return {"ok": True, "data": {}}
    return pwj


def _arm(monkeypatch, default=_COV_DEFAULT, scoped=_COV_SCOPED, orphans=_ORPHANS):
    monkeypatch.setattr(steps, "_tool", lambda name: f"/home/john/.local/bin/{name}")
    monkeypatch.setattr(steps.plainweave_seed, "seed", lambda pw: None)
    monkeypatch.setattr(steps, "_plainweave_json", _fake_pwj(default, scoped, orphans))


def test_plainweave_intent_surfaces_all_four_facts(monkeypatch):
    _arm(monkeypatch)
    r = steps.plainweave_intent()
    assert r.name == "plainweave intent"
    assert r.ok is True
    assert ("pw-intent-justified", "specimen.cli._add_book") in r.surfaced
    assert ("pw-intent-liveness", "specimen.cli._register") in r.surfaced
    assert ("pw-intent-orphan", "tour.__main__.main") in r.surfaced
    assert ("pw-surface-scoping", "tour.__main__.main") in r.surfaced
    assert len(r.surfaced) == 4


def test_plainweave_intent_detail_is_deterministic(monkeypatch):
    # The north-star ratio moves with the catalog, so no digit/id/ratio may enter
    # the byte-locked detail; live numbers ride the non-rendered note.
    _arm(monkeypatch)
    r = steps.plainweave_intent()
    assert not any(ch.isdigit() for ch in r.detail)
    assert "north-star" in r.note  # live numbers live here, not in detail


def test_plainweave_intent_degrades_when_tool_missing(monkeypatch):
    monkeypatch.setattr(steps, "_tool", lambda name: None)
    r = steps.plainweave_intent()
    assert r.ok is False
    assert r.surfaced == ()
    assert "uv tool install" in r.detail  # names the next action


def test_plainweave_intent_never_raises_on_seed_failure(monkeypatch):
    monkeypatch.setattr(steps, "_tool", lambda name: f"/home/john/.local/bin/{name}")

    def _boom(pw):
        raise ValueError("surface not in catalog: python:function:specimen.cli._add_book")

    monkeypatch.setattr(steps.plainweave_seed, "seed", _boom)
    r = steps.plainweave_intent()
    assert r.ok is False
    assert r.name == "plainweave intent"
    # error path detail carries the exception TYPE only — no hex/digits leak.
    assert not any(ch.isdigit() for ch in r.detail)


def test_plainweave_intent_partial_degrade_omits_only_the_failing_pair(monkeypatch):
    # _add_book unjustified ⇒ the justified fact must NOT surface, while the orphan
    # fact (independent of it) still does. A failing sub-check omits ONLY its pair.
    broken = {
        "north_star": {"numerator": 1, "denominator": 4, "ratio": 0.25},
        "denominator_complete": False,
        "coverage": {"absent_tags": ["exported-api", "http-route"]},
        "justified": [_surface(CLI_MAIN_LOC, "sei-main")],
        "unjustified": [
            _surface(ADD_BOOK_LOC, "sei-add"),
            _surface(REGISTER_LOC, "sei-reg"),
            _surface(TOUR_MAIN_LOC, "sei-tour"),
        ],
    }
    _arm(monkeypatch, default=broken)
    r = steps.plainweave_intent()
    assert ("pw-intent-justified", "specimen.cli._add_book") not in r.surfaced
    assert ("pw-intent-orphan", "tour.__main__.main") in r.surfaced
    assert r.ok is False  # fail loud — not all four facts held


# ── Seed-level: liveness positive-control (AC#7 discrimination) ────────────────

def _recording_pw():
    calls: list[list[str]] = []
    locs = (ADD_BOOK_LOC, REGISTER_LOC, CLI_MAIN_LOC, TOUR_MAIN_LOC)

    def pw(args):
        calls.append(args)
        if args[:2] == ["intent", "coverage"]:
            return {"unjustified": [_surface(loc, f"sei-{i}") for i, loc in enumerate(locs)]}
        if args[:2] in (["goal", "add"], ["req", "add"]):
            return {"id": f"ID-{len(calls)}"}
        return {}
    return pw, calls


def test_seed_deprecates_register_only_when_requested(monkeypatch):
    # Positive control: the liveness fact is the DEPRECATION dropping _register, not a
    # broken/absent bind. _register is bound in BOTH cases; deprecate is the only diff.
    monkeypatch.setattr(plainweave_seed.shutil, "rmtree", lambda *a, **k: None)

    pw_on, calls_on = _recording_pw()
    plainweave_seed.seed(pw_on, deprecate=True)
    pw_off, calls_off = _recording_pw()
    plainweave_seed.seed(pw_off, deprecate=False)

    # _register is bound in both runs (so "unjustified" is never a never-bound artifact).
    assert any(c[:2] == ["bind", "sei"] for c in calls_on)
    assert any(c[:2] == ["bind", "sei"] for c in calls_off)
    # deprecate is issued ONLY when requested.
    assert any(c[:2] == ["req", "deprecate"] for c in calls_on)
    assert not any(c[:2] == ["req", "deprecate"] for c in calls_off)
