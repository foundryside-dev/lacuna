import sqlite3

from tour.steps import pairs_from_findings, structure_facts


def test_parses_rule_symbol_pairs_from_jsonl(tmp_path):
    p = tmp_path / "findings.jsonl"
    p.write_text(
        '{"rule_id": "PY-WL-101", "qualname": "specimen.trust_flow.unsafe_account_key"}\n'
        '{"rule_id": "PY-WL-103", "qualname": "specimen.exception_flow.broad_handler"}\n'
        '{"rule_id": "WLN-ENGINE-METRICS", "qualname": null}\n'
    )
    pairs = pairs_from_findings(p)
    assert ("PY-WL-101", "specimen.trust_flow.unsafe_account_key") in pairs
    assert ("PY-WL-103", "specimen.exception_flow.broad_handler") in pairs


def test_missing_file_yields_no_pairs(tmp_path):
    assert pairs_from_findings(tmp_path / "nope.jsonl") == ()


def _mini_clarion_db(path):
    """Build a minimal clarion.db with the entities/edges shape the harness reads."""
    c = sqlite3.connect(str(path))
    c.execute("create table entities (id text, kind text, name text)")
    c.execute("create table edges (kind text, from_id text, to_id text)")
    c.executemany("insert into entities values (?,?,?)", [
        ("e1", "function", "specimen.dead_code.orphaned_helper"),
        ("e2", "function", "specimen.cycle_a.ping"),
        ("e3", "function", "specimen.service.live"),
        ("ma", "module", "specimen.cycle_a"),
        ("mb", "module", "specimen.cycle_b"),
    ])
    c.executemany("insert into edges values (?,?,?)", [
        ("calls", "e2", "e3"),
        ("imports", "ma", "mb"),
        ("imports", "mb", "ma"),
    ])
    c.commit()
    c.close()


def test_structure_facts_detects_dead_and_cycle(tmp_path):
    db = tmp_path / "clarion.db"
    _mini_clarion_db(db)
    facts = structure_facts(db)
    assert "specimen.dead_code.orphaned_helper" in facts.dead
    assert "specimen.cycle_a" in facts.cycle_members
    assert "specimen.cycle_b" in facts.cycle_members


def test_structure_facts_missing_db(tmp_path):
    facts = structure_facts(tmp_path / "absent.db")
    assert facts.dead == () and facts.cycle_members == ()
