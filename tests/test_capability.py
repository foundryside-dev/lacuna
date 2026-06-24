from tour.capability import detect

LIVE = {"loomweave", "filigree", "wardline"}


def test_detects_installed_tools():
    caps = detect(which=lambda name: f"/usr/bin/{name}" if name in LIVE else None)
    by_name = {c.name: c for c in caps}
    assert by_name["loomweave"].available is True
    assert by_name["wardline"].available is True


def test_design_only_tools_reported_unavailable():
    caps = detect(which=lambda name: f"/usr/bin/{name}" if name in LIVE else None)
    by_name = {c.name: c for c in caps}
    assert by_name["charter"].available is False
    assert "design-only" in by_name["charter"].detail


def _fake_which(present):
    return lambda name: f"/home/john/.local/bin/{name}" if name in present else None


def test_legis_is_a_detectable_live_member_when_installed():
    caps = {c.name: c for c in detect(_fake_which({"loomweave", "filigree", "wardline", "legis"}))}
    assert "legis" in caps
    assert caps["legis"].available is True
    # charter remains design-only
    assert caps["charter"].available is False


def test_legis_absent_reports_unavailable_not_design_only(monkeypatch):
    monkeypatch.setattr("tour.capability.BIN", __import__("pathlib").Path("/nonexistent/bin"))
    caps = {c.name: c for c in detect(_fake_which({"loomweave", "filigree", "wardline"}))}
    assert caps["legis"].available is False
    assert "design-only" not in caps["legis"].detail


def test_warpline_is_a_detectable_live_member_when_installed():
    # warpline must be a RUNNABLE capability so verify's coverage gate actually
    # asserts the wp-* entries (`expected_tool in live`); without this the leg
    # could degrade silently. NOT design-only — warpline ships a runnable CLI.
    caps = {c.name: c for c in detect(_fake_which({"loomweave", "filigree", "wardline", "legis", "warpline"}))}
    assert "warpline" in caps
    assert caps["warpline"].available is True


def test_plainweave_is_a_detectable_live_member_when_installed():
    # plainweave must be RUNNABLE so verify's coverage gate asserts the pw-* entries
    # (`expected_tool in live`). It is installed as a uv tool in ~/.local/bin like its
    # siblings; NOT design-only.
    caps = {c.name: c for c in detect(_fake_which(
        {"loomweave", "filigree", "wardline", "legis", "warpline", "plainweave"}
    ))}
    assert "plainweave" in caps
    assert caps["plainweave"].available is True


def test_plainweave_absent_reports_unavailable_not_design_only(monkeypatch):
    monkeypatch.setattr("tour.capability.BIN", __import__("pathlib").Path("/nonexistent/bin"))
    caps = {c.name: c for c in detect(_fake_which({"loomweave", "filigree", "wardline", "legis", "warpline"}))}
    assert caps["plainweave"].available is False
    assert "design-only" not in caps["plainweave"].detail
