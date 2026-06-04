from tour.capability import detect

LIVE = {"clarion", "filigree", "wardline"}


def test_detects_installed_tools():
    caps = detect(which=lambda name: f"/usr/bin/{name}" if name in LIVE else None)
    by_name = {c.name: c for c in caps}
    assert by_name["clarion"].available is True
    assert by_name["wardline"].available is True


def test_design_only_tools_reported_unavailable():
    caps = detect(which=lambda name: f"/usr/bin/{name}" if name in LIVE else None)
    by_name = {c.name: c for c in caps}
    assert by_name["legis"].available is False
    assert "design-only" in by_name["legis"].detail
    assert by_name["charter"].available is False
