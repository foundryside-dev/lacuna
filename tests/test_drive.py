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
    # the include_federation leg spawns warpline-mcp; stub it for this ordering test.
    monkeypatch.setattr(
        steps, "warpline_reverify_federation",
        lambda: StepResult("warpline reverify federation", ok=True, detail="stub"),
    )
    _caps, results = _drive()
    names = [r.name for r in results]
    assert "legis govern" in names
    # ordering: legis runs after the wardline scan it consumes
    assert names.index("legis govern") > names.index("wardline scan")


def test_drive_includes_the_warpline_peer_facts_steps(monkeypatch):
    # The two Tier-B warpline peer-facts legs must run AFTER warpline_change_impact (which
    # populates the hot store both reuse). Stub the MCP-spawning legs for a fast ordering test.
    from tour import steps
    from tour.report import StepResult

    monkeypatch.setattr(
        steps, "mcp_attachment",
        lambda: StepResult("mcp attachment", ok=True, detail="stub"),
    )
    monkeypatch.setattr(
        steps, "warpline_reverify_federation",
        lambda: StepResult("warpline reverify federation", ok=True, detail="stub"),
    )
    _caps, results = _drive()
    names = [r.name for r in results]
    assert "warpline attest bundle" in names
    assert "warpline reverify federation" in names
    # both consume the store warpline_change_impact populates, so they run after it
    assert names.index("warpline attest bundle") > names.index("warpline change impact")
    assert names.index("warpline reverify federation") > names.index("warpline change impact")


def test_drive_includes_the_plainweave_coverage_step(monkeypatch):
    from tour import steps
    from tour.report import StepResult
    monkeypatch.setattr(steps, "plainweave_coverage",
                        lambda: StepResult("plainweave coverage", ok=True, detail="stub"))
    monkeypatch.setattr(steps, "mcp_attachment",
                        lambda: StepResult("mcp attachment", ok=True, detail="stub"))
    monkeypatch.setattr(steps, "warpline_reverify_federation",
                        lambda: StepResult("warpline reverify federation", ok=True, detail="stub"))
    _caps, results = _drive()
    names = [r.name for r in results]
    assert "plainweave coverage" in names


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
    monkeypatch.setattr(
        steps, "warpline_reverify_federation",
        lambda: StepResult("warpline reverify federation", ok=True, detail="stub"),
    )
    _caps, results = _drive()
    names = [r.name for r in results]
    assert "plainweave intent" in names
    # ordering: plainweave consumes the freshly-analyzed loomweave catalog
    assert names.index("plainweave intent") > names.index("loomweave analyze")
