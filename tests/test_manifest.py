from pathlib import Path

from tour.manifest import load_manifest

MANIFEST = Path("/home/john/lacuna/tour/lacunae.toml")


def test_loads_all_lacunae():
    m = load_manifest(MANIFEST)
    assert len(m.lacunae) == 6
    ids = {l.id for l in m.lacunae}
    assert "wl-trust-violation" in ids


def test_lacuna_fields():
    m = load_manifest(MANIFEST)
    l = next(x for x in m.lacunae if x.id == "wl-trust-violation")
    assert l.file == "specimen/trust_flow.py"
    assert l.symbol == "unsafe_account_key"
    assert l.expected_tool == "wardline"
    assert l.expected_rule == "PY-WL-101"
    assert "wardline+clarion" in l.demonstrates


def test_cells_are_the_union_of_demonstrates():
    m = load_manifest(MANIFEST)
    assert "wardline+filigree" in m.cells()
    assert "clarion" in m.cells()
