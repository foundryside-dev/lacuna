from tour.__main__ import _drive


def test_drive_includes_the_legis_governance_step():
    _caps, results = _drive()
    names = [r.name for r in results]
    assert "legis govern" in names
    # ordering: legis runs after the wardline scan it consumes
    assert names.index("legis govern") > names.index("wardline scan")
