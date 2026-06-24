from tour.__main__ import _drive


def test_drive_includes_the_legis_governance_step():
    _caps, results = _drive()
    names = [r.name for r in results]
    assert "legis govern" in names
    # ordering: legis runs after the wardline scan it consumes
    assert names.index("legis govern") > names.index("wardline scan")


def test_drive_includes_the_plainweave_intent_step(monkeypatch):
    # Stub the self-seeding plainweave leg so this ordering test does NOT wipe/
    # rebuild .plainweave/ (the live seed is exercised by test_steps_plainweave and
    # the live `make tour`/`make verify`). We only assert presence + ordering here.
    from tour import steps
    from tour.report import StepResult

    monkeypatch.setattr(
        steps, "plainweave_intent",
        lambda: StepResult("plainweave intent", ok=True, detail="stub"),
    )
    _caps, results = _drive()
    names = [r.name for r in results]
    assert "plainweave intent" in names
    # ordering: plainweave consumes the freshly-analyzed loomweave catalog
    assert names.index("plainweave intent") > names.index("loomweave analyze")
