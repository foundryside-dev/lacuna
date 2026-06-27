from tour.__main__ import _drive


def test_drive_includes_the_legis_governance_step(monkeypatch):
    # Stub the mcp_attachment leg so this ordering test does NOT spawn all 6 live
    # MCP probes (~slow) for what is just a presence+ordering assertion (R6).
    from tour import steps
    from tour.report import StepResult

    monkeypatch.setattr(
        steps, "mcp_attachment",
        lambda: StepResult("mcp attachment", ok=True, detail="stub"),
    )
    _caps, results = _drive()
    names = [r.name for r in results]
    assert "legis govern" in names
    # ordering: legis runs after the wardline scan it consumes
    assert names.index("legis govern") > names.index("wardline scan")


def test_drive_includes_the_plainweave_intent_step(monkeypatch):
    # Stub the self-seeding plainweave leg so this ordering test does NOT wipe/
    # rebuild .plainweave/ (the live seed is exercised by test_steps_plainweave and
    # the live `make tour`/`make verify`). We only assert presence + ordering here.
    # Also stub mcp_attachment to avoid spawning live MCP probes for an ordering test (R6).
    from tour import steps
    from tour.report import StepResult

    monkeypatch.setattr(
        steps, "plainweave_intent",
        lambda: StepResult("plainweave intent", ok=True, detail="stub"),
    )
    monkeypatch.setattr(
        steps, "mcp_attachment",
        lambda: StepResult("mcp attachment", ok=True, detail="stub"),
    )
    _caps, results = _drive()
    names = [r.name for r in results]
    assert "plainweave intent" in names
    # ordering: plainweave consumes the freshly-analyzed loomweave catalog
    assert names.index("plainweave intent") > names.index("loomweave analyze")
