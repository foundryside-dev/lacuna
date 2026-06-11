from pathlib import Path

from tour.manifest import load_manifest

MANIFEST = Path("/home/john/lacuna/tour/lacunae.toml")


def test_loads_all_lacunae():
    m = load_manifest(MANIFEST)
    assert len(m.lacunae) == 34
    ids = {l.id for l in m.lacunae}
    assert "wl-trust-violation" in ids
    # the loomweave navigation showcases (call chain, coupling, entry point, subsystem,
    # and the rc4 relation-edge pair: inheritance + decorator)
    assert {
        "lw-call-chain",
        "lw-coupling-hotspot",
        "lw-entry-point",
        "lw-subsystem",
        "lw-inheritance",
        "lw-decorator",
    } <= ids


def test_lacuna_fields():
    m = load_manifest(MANIFEST)
    l = next(x for x in m.lacunae if x.id == "wl-trust-violation")
    assert l.file == "specimen/trust_flow.py"
    assert l.symbol == "unsafe_account_key"
    assert l.expected_tool == "wardline"
    assert l.expected_rule == "PY-WL-101"
    assert "wardline+loomweave" in l.demonstrates


def test_cells_are_the_union_of_demonstrates():
    m = load_manifest(MANIFEST)
    assert "wardline+filigree" in m.cells()
    assert "loomweave" in m.cells()


def test_optional_fields_default(tmp_path):
    from tour.manifest import load_manifest
    p = tmp_path / "m.toml"
    p.write_text(
        '[[lacuna]]\nid = "x"\nfile = "f.py"\nsymbol = "s"\ncategory = "c"\n'
        'demonstrates = ["wardline"]\nexplanation = "e"\n'
        'expected_tool = "wardline"\nexpected_rule = "R"\n'
    )
    lac = load_manifest(p).lacunae[0]
    assert lac.lang == "python"
    assert lac.expected_kind == "finding"
    assert lac.scan_target == ""


def test_optional_fields_explicit(tmp_path):
    from tour.manifest import load_manifest
    p = tmp_path / "m.toml"
    p.write_text(
        '[[lacuna]]\nid = "x"\nfile = "f.rs"\nsymbol = "s"\ncategory = "c"\n'
        'demonstrates = ["wardline"]\nexplanation = "e"\n'
        'expected_tool = "wardline"\nexpected_rule = "R"\n'
        'lang = "rust"\nexpected_kind = "gate-trip"\nscan_target = "specimen_quarantine"\n'
    )
    lac = load_manifest(p).lacunae[0]
    assert (lac.lang, lac.expected_kind, lac.scan_target) == ("rust", "gate-trip", "specimen_quarantine")
