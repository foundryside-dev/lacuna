import sqlite3

from tour.steps import navigation_facts, pairs_from_findings, structure_facts


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


def _mini_loomweave_db(path):
    """Build a minimal loomweave.db with the entities/edges shape the harness reads.

    `parent_id` matters: the dead-code query keeps only module-level functions
    (parent kind module/file), so each function points at its containing module.
    """
    c = sqlite3.connect(str(path))
    c.execute("create table entities (id text, kind text, name text, parent_id text)")
    c.execute("create table edges (kind text, from_id text, to_id text)")
    c.executemany("insert into entities values (?,?,?,?)", [
        ("e1", "function", "specimen.dead_code.orphaned_helper", "md"),  # dead: no incoming
        ("e2", "function", "specimen.cycle_a.ping", "ma"),
        ("e3", "function", "specimen.service.live", "msvc"),             # has an incoming call
        ("ma", "module", "specimen.cycle_a", None),
        ("mb", "module", "specimen.cycle_b", None),
        ("md", "module", "specimen.dead_code", None),
        ("msvc", "module", "specimen.service", None),
    ])
    c.executemany("insert into edges values (?,?,?)", [
        ("calls", "e2", "e3"),          # e3 is called -> live
        ("imports", "ma", "mb"),        # cycle halves (module <-> module)
        ("imports", "mb", "ma"),
    ])
    c.commit()
    c.close()


def test_structure_facts_detects_dead_and_cycle(tmp_path):
    db = tmp_path / "loomweave.db"
    _mini_loomweave_db(db)
    facts = structure_facts(db)
    assert "specimen.dead_code.orphaned_helper" in facts.dead
    assert "specimen.cycle_a" in facts.cycle_members
    assert "specimen.cycle_b" in facts.cycle_members


def test_structure_facts_missing_db(tmp_path):
    facts = structure_facts(tmp_path / "absent.db")
    assert facts.dead == () and facts.cycle_members == ()


def _mini_nav_db(path):
    """Minimal index with a deep call chain, a coupling hub, a `main` entry point,
    and a 4-member subsystem — the shape navigation_facts() reads."""
    c = sqlite3.connect(str(path))
    c.execute("create table entities (id text, kind text, name text, parent_id text)")
    c.execute("create table edges (kind text, from_id text, to_id text)")
    c.execute("create table entity_tags (entity_id text, tag text)")
    ents = [
        # 5-node linear chain ingest->n1->n2->n3->tail (4 edges == CHAIN_MIN)
        ("ig", "function", "specimen.pipeline.ingest", "mp"),
        ("n1", "function", "specimen.pipeline.normalize", "mp"),
        ("n2", "function", "specimen.pipeline.enrich", "mp"),
        ("n3", "function", "specimen.pipeline.validate_record", "mp"),
        ("tl", "function", "specimen.pipeline.persist", "mp"),
        # coupling hub: 2 callers, 2 callees
        ("hb", "function", "specimen.hub.dispatch", "mh"),
        ("c1", "function", "specimen.hub.Dispatcher.handle_a", "kd"),
        ("c2", "function", "specimen.hub.Dispatcher.handle_b", "kd"),
        ("o1", "function", "specimen.hub._audit", "mh"),
        ("o2", "function", "specimen.hub._route", "mh"),
        # entry point: module-level `main`, no incoming, has outgoing call
        ("mn", "function", "specimen.cli.main", "mc"),
        ("mp", "module", "specimen.pipeline", None),
        ("mh", "module", "specimen.hub", None),
        ("kd", "class", "specimen.hub.Dispatcher", "mh"),
        ("mc", "module", "specimen.cli", None),
        # a 4-member subsystem the co-membership query should surface
        ("ss", "subsystem", "Subsystem deadbeef", None),
    ]
    c.executemany("insert into entities values (?,?,?,?)", ents)
    c.executemany("insert into edges values (?,?,?)", [
        ("calls", "ig", "n1"), ("calls", "n1", "n2"),
        ("calls", "n2", "n3"), ("calls", "n3", "tl"),
        ("calls", "c1", "hb"), ("calls", "c2", "hb"),
        ("calls", "hb", "o1"), ("calls", "hb", "o2"),
        ("calls", "mn", "ig"),  # main drives the pipeline
        ("in_subsystem", "mp", "ss"), ("in_subsystem", "mh", "ss"),
        ("in_subsystem", "mc", "ss"), ("in_subsystem", "ig", "ss"),
    ])
    # entity_entry_point_list reads the `entry-point` categorisation tag.
    c.execute("insert into entity_tags values ('mn', 'entry-point')")
    c.commit()
    c.close()


def test_navigation_facts_surfaces_chain_hub_entry_and_subsystem(tmp_path):
    db = tmp_path / "loomweave.db"
    _mini_nav_db(db)
    nf = navigation_facts(db)
    assert ("specimen.pipeline.ingest", 4) in nf.chain_heads
    assert nf.hotspots and nf.hotspots[0][0] == "specimen.hub.dispatch"
    assert nf.entry_points == ("specimen.cli.main",)
    assert "specimen.cli" in nf.subsystem_members


def test_navigation_facts_missing_db(tmp_path):
    nf = navigation_facts(tmp_path / "absent.db")
    assert nf.chain_heads == () and nf.hotspots == ()
    assert nf.entry_points == () and nf.subsystem_members == ()


def test_loomweave_findings_maps_paths_to_module_qualnames(tmp_path):
    """The real findings schema carries entity_id (+ JSON evidence), not a
    file_path column: file-scoped alarms attach to `core:file:<relpath>` and the
    duplicate-locator attaches to `core:project:*` with the colliding path in
    evidence metadata — the step must map both shapes to module qualnames."""
    from tour import steps

    db = tmp_path / "loomweave.db"
    con = sqlite3.connect(db)
    con.execute("create table findings (rule_id text, entity_id text, evidence text)")
    con.execute(
        "insert into findings values "
        "('LMWV-PY-TOO-COMPLEX', 'core:file:specimen/nesting_bomb.py', '{}')"
    )
    con.execute(
        "insert into findings values ('LMWV-DUPLICATE-LOCATOR', 'core:project:lacuna', ?)",
        (
            '{"metadata": {"first_source_file_path": "'
            f"{steps.ROOT}/specimen/colliding.py" '"}}',
        ),
    )
    con.commit(); con.close()

    result = steps.loomweave_findings(db_path=db)
    assert result.ok
    assert ("LMWV-PY-TOO-COMPLEX", "specimen.nesting_bomb") in result.surfaced
    assert ("LMWV-DUPLICATE-LOCATOR", "specimen.colliding") in result.surfaced


def test_filigree_work_cycle_detail_is_deterministic(monkeypatch):
    from tour import steps

    calls = []

    def fake_api(method, path, token, body=None):
        calls.append((method, path))
        if path.endswith("/findings/promote"):
            return {"issue_id": "lacuna-sentinel1", "status": "closed", "created": False}
        if path.endswith("/reopen"):
            return {"status": "fixing"}
        if path.endswith("/claim"):
            return {"assignee": "tour"}
        if path.endswith("/close"):
            return {"status": "closed"}
        if "files/stats" in path:
            return {"suppressed": {"critical": 10, "high": 20, "medium": 9, "low": 0, "info": 0}}
        if "issues?" in path:
            return [{"id": "lacuna-sentinel1"}]
        raise AssertionError(path)

    monkeypatch.setattr(steps, "_filigree_api", fake_api)
    monkeypatch.setattr(steps, "_federation_token", lambda: "tok")
    monkeypatch.setattr(steps, "_sentinel_fingerprint", lambda: "fp123")
    r = steps.filigree_work_cycle()
    assert r.ok
    assert "sentinel issue cycled" in r.detail
    assert "lacuna-sentinel1" not in r.detail  # live ids must never enter the locked narrative
