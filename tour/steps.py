"""Drive each live Weft tool against the specimen. Steps never raise."""

from __future__ import annotations

import json
import os
import secrets
import shutil
import socket
import sqlite3
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from tour import plainweave_seed
from tour.report import StepResult

ROOT = Path("/home/john/lacuna")
BIN = Path("/home/john/.local/bin")
LOOMWEAVE_DB = ROOT / ".weft" / "loomweave" / "loomweave.db"


def _run(cmd: list[str], cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)


@dataclass(frozen=True)
class StructureFacts:
    dead: tuple[str, ...]           # function entities with no incoming call/ref/import edge
    cycle_members: tuple[str, ...]  # entity names participating in an `imports` 2-cycle


def structure_facts(db_path: Path = LOOMWEAVE_DB) -> StructureFacts:
    """Read structural facts straight from Loomweave's SQLite index.

    Loomweave ships no dead-code/cycle CLI verb, so the harness queries the DB the
    `loomweave analyze` pass already wrote. Never raises: a missing/locked DB yields
    empty facts.

    Scoped to ``specimen.*`` entities: the specimen is the subject of the demo,
    whereas ``tour/`` (the harness) and ``tests/`` are instruments — their
    uncalled functions are not specimen lacunae and would only be narrative noise.
    """
    if not Path(db_path).exists():
        return StructureFacts(dead=(), cycle_members=())
    try:
        con = sqlite3.connect(str(db_path))
    except sqlite3.Error:
        return StructureFacts(dead=(), cycle_members=())
    try:
        # "Dead" = a module-level (not a method/dunder) specimen function with no
        # incoming call/reference/import edge. Restricting to module-level non-dunder
        # functions avoids the huge false-positive list Loomweave's static call graph
        # would otherwise produce (dunders invoked by operators, methods reached by
        # dynamic dispatch) — those have no `calls` edge but are not dead.
        dead = tuple(
            r[0]
            for r in con.execute(
                "select e.name from entities e "
                "left join entities p on p.id = e.parent_id "
                "where e.kind='function' and e.name like 'specimen.%' "
                "and e.name not glob '*.__*__' "
                "and (p.kind is null or p.kind in ('module', 'file')) "
                "and e.id not in "
                "(select to_id from edges where kind in ('calls','references','imports'))"
            )
        )
        members: list[str] = []
        for ef, et in con.execute(
            "select ef.name, et.name from edges a "
            "join edges b on a.from_id=b.to_id and a.to_id=b.from_id "
            "join entities ef on ef.id=a.from_id "
            "join entities et on et.id=a.to_id "
            "where a.kind='imports' and b.kind='imports' and a.from_id<a.to_id "
            "and ef.name like 'specimen.%' and et.name like 'specimen.%'"
        ):
            members.extend((ef, et))
        return StructureFacts(dead=dead, cycle_members=tuple(dict.fromkeys(members)))
    except sqlite3.Error:
        return StructureFacts(dead=(), cycle_members=())
    finally:
        con.close()


def loomweave_structure() -> StepResult:
    """Surface Loomweave's structural lacunae as (token, qualname) pairs the coverage
    map matches against a SPECIFIC lacuna symbol — never a bare token."""
    facts = structure_facts()
    surfaced = tuple(("dead-entity", n) for n in facts.dead) + tuple(
        ("circular-import", n) for n in facts.cycle_members
    )
    dead_short = ", ".join(sorted(n.rsplit(".", 1)[-1] for n in facts.dead)) or "(none)"
    cyc_short = ", ".join(sorted(n.rsplit(".", 1)[-1] for n in facts.cycle_members)) or "(none)"
    return StepResult(
        "loomweave structure",
        ok=Path(LOOMWEAVE_DB).exists(),
        detail=f"dead entities: {dead_short}; import cycle: {cyc_short}",
        surfaced=surfaced,
    )


@dataclass(frozen=True)
class RelationFacts:
    inherits: tuple[tuple[str, str], ...]   # (subclass, base) qualname pairs
    decorates: tuple[tuple[str, str], ...]  # (decorator, decorated) qualname pairs


def relation_facts(db_path: Path = LOOMWEAVE_DB) -> RelationFacts:
    """Read specimen-scoped relation edges (inherits_from / decorates) from the index.

    Python relation edges landed in plugin ontology 0.8.0; ADR-051 pins the edge
    direction (subclass→base, decorator→decorated). Never raises: a missing or
    locked DB yields empty facts and the step degrades to not-surfaced.
    """
    if not Path(db_path).exists():
        return RelationFacts(inherits=(), decorates=())
    try:
        con = sqlite3.connect(str(db_path))
    except sqlite3.Error:
        return RelationFacts(inherits=(), decorates=())
    try:
        out: dict[str, tuple[tuple[str, str], ...]] = {}
        for kind in ("inherits_from", "decorates"):
            out[kind] = tuple(
                (frm, to)
                for frm, to in con.execute(
                    "select ef.name, et.name from edges e "
                    "join entities ef on ef.id=e.from_id "
                    "join entities et on et.id=e.to_id "
                    "where e.kind=? and ef.name like 'specimen.%' "
                    "and et.name like 'specimen.%' order by ef.name, et.name",
                    (kind,),
                )
            )
        return RelationFacts(inherits=out["inherits_from"], decorates=out["decorates"])
    except sqlite3.Error:
        return RelationFacts(inherits=(), decorates=())
    finally:
        con.close()


def loomweave_relations() -> StepResult:
    """Surface the relation-edge lacunae as (token, qualname) pairs — the
    inherits-from token carries the subclass, the decorates token the decorator,
    so coverage matches the planted symbols (InMemoryRepository / audited)."""
    facts = relation_facts()
    surfaced = tuple(("inherits-from", sub) for sub, _ in facts.inherits) + tuple(
        ("decorates", dec) for dec, _ in facts.decorates
    )
    inh_short = (
        ", ".join(f"{s.rsplit('.', 1)[-1]}→{b.rsplit('.', 1)[-1]}" for s, b in facts.inherits)
        or "(none)"
    )
    dec_short = ", ".join(sorted({d.rsplit(".", 1)[-1] for d, _ in facts.decorates})) or "(none)"
    return StepResult(
        "loomweave relations",
        ok=Path(LOOMWEAVE_DB).exists(),
        detail=f"inheritance: {inh_short}; decorators: {dec_short}",
        surfaced=surfaced,
    )


# Minimum length (in `calls` edges) for a chain to count as a demonstrable
# execution path. The planted specimen.pipeline chain is 4 hops deep.
CHAIN_MIN = 4
# How many top coupling hotspots to surface — mirrors a paged
# entity_coupling_hotspot_list read.
HOTSPOT_TOP = 5
# The module whose subsystem the gate asserts membership of (the app's CLI front
# end always clusters with its service/repository/model layers).
SUBSYS_ANCHOR = "specimen.cli"


@dataclass(frozen=True)
class NavigationFacts:
    # (head qualname, chain depth in calls-edges) for chains >= CHAIN_MIN.
    chain_heads: tuple[tuple[str, int], ...]
    # (qualname, fan_in+fan_out) ranked desc — mirrors entity_coupling_hotspot_list,
    # which ranks distinct fan-in + fan-out over call+import edges (no "both arms" gate).
    hotspots: tuple[tuple[str, int], ...]
    # qualnames carrying Loomweave's `entry-point` categorisation tag (what
    # entity_entry_point_list returns), specimen-scoped.
    entry_points: tuple[str, ...]
    # specimen modules sharing SUBSYS_ANCHOR's subsystem (what subsystem_member_list
    # returns for it) — keyed on membership, not the unstable generated name.
    subsystem_members: tuple[str, ...]


def _specimen_calls(con: sqlite3.Connection) -> dict[str, set[str]]:
    """Adjacency of specimen→specimen `calls` edges, keyed by qualname."""
    adj: dict[str, set[str]] = {}
    for frm, to in con.execute(
        "select ef.name, et.name from edges e "
        "join entities ef on ef.id=e.from_id "
        "join entities et on et.id=e.to_id "
        "where e.kind='calls' and ef.name like 'specimen.%' and et.name like 'specimen.%'"
    ):
        adj.setdefault(frm, set()).add(to)
    return adj


def _longest_chain(node: str, adj: dict[str, set[str]], stack: frozenset[str]) -> int:
    """Longest acyclic outgoing call-path length (in edges) from ``node``.

    ``stack`` carries the nodes on the current path so the walk is cycle-guarded —
    the specimen's deliberate ``cycle_a``/``cycle_b`` 2-cycle would otherwise recurse
    forever. Bounded depth, tiny graph: a plain DFS is fine.
    """
    best = 0
    for nxt in adj.get(node, ()):  # noqa: SIM118 — set membership, not dict keys
        if nxt in stack:
            continue
        best = max(best, 1 + _longest_chain(nxt, adj, stack | {nxt}))
    return best


def navigation_facts(db_path: Path = LOOMWEAVE_DB) -> NavigationFacts:
    """Read navigation-shaped facts (deep call chains) from the Loomweave index.

    Loomweave's MCP navigation tools (entity_execution_path_list, entity_callers_list)
    expose these live; the harness reconstructs the same facts from the index so the
    gate can assert a SPECIFIC planted symbol offline. Never raises (tour contract).
    """
    if not Path(db_path).exists():
        return NavigationFacts(
            chain_heads=(), hotspots=(), entry_points=(), subsystem_members=()
        )
    try:
        con = sqlite3.connect(str(db_path))
    except sqlite3.Error:
        return NavigationFacts(
            chain_heads=(), hotspots=(), entry_points=(), subsystem_members=()
        )
    try:
        adj = _specimen_calls(con)
        heads = tuple(
            sorted(
                (n, depth)
                for n in adj
                if (depth := _longest_chain(n, adj, frozenset({n}))) >= CHAIN_MIN
            )
        )
        # Coupling: distinct fan-in + fan-out over call + import edges, ranked desc —
        # the same metric entity_coupling_hotspot_list uses (structural contains/
        # in_subsystem edges are excluded so membership fan-out doesn't dominate).
        ranked = sorted(
            (
                (name, fan_in + fan_out)
                for name, fan_in, fan_out in con.execute(
                    "select e.name, "
                    "(select count(distinct from_id) from edges "
                    " where to_id=e.id and kind in ('calls','imports')), "
                    "(select count(distinct to_id) from edges "
                    " where from_id=e.id and kind in ('calls','imports')) "
                    "from entities e where e.name like 'specimen.%'"
                )
                if fan_in + fan_out > 0
            ),
            key=lambda t: (-t[1], t[0]),  # coupling desc, ties by name (matches tool)
        )
        hotspots = tuple(ranked[:HOTSPOT_TOP])
        # Entry points: entities carrying Loomweave's `entry-point` categorisation tag —
        # exactly what entity_entry_point_list returns (the Python plugin emits it).
        entry_points = tuple(
            name
            for (name,) in con.execute(
                "select e.name from entity_tags t join entities e on e.id=t.entity_id "
                "where t.tag='entry-point' and e.name like 'specimen.%' order by e.name"
            )
        )
        # Subsystem co-members: the specimen modules sharing SUBSYS_ANCHOR's subsystem,
        # i.e. what subsystem_member_list returns for it. Keyed on membership, not the
        # generated name (the coherent app cluster is hash-named for this corpus, and
        # which cluster wins the bare package name is not stable). DISTINCT guards
        # against stale subsystem rows from repeated in-place analyze (CI rebuilds clean).
        subsystem_members = tuple(
            name
            for (name,) in con.execute(
                "select distinct m.name from edges e "
                "join entities m on m.id = e.from_id "
                "where e.kind='in_subsystem' and m.name like 'specimen.%' "
                "and e.to_id in ("
                "  select e2.to_id from edges e2 "
                "  join entities a on a.id = e2.from_id "
                "  where e2.kind='in_subsystem' and a.name = ?"
                ") order by m.name",
                (SUBSYS_ANCHOR,),
            )
        )
        return NavigationFacts(
            chain_heads=heads,
            hotspots=hotspots,
            entry_points=entry_points,
            subsystem_members=subsystem_members,
        )
    except sqlite3.Error:
        return NavigationFacts(
            chain_heads=(), hotspots=(), entry_points=(), subsystem_members=()
        )
    finally:
        con.close()


def loomweave_navigation() -> StepResult:
    """Surface Loomweave's graph-navigation facts as (token, qualname) pairs — the
    structural counterpart to a taint chain: a path the tool traces end-to-end."""
    facts = navigation_facts()
    surfaced = (
        tuple(("execution-path", n) for n, _ in facts.chain_heads)
        # Only the #1-ranked hotspot is asserted, so the gate fails loudly if the
        # (volatile) wardline fixtures ever push a sink past the planted hub — keeping
        # the "ranks #1" claim honest rather than merely "appears in the top-N".
        + tuple(("coupling-hotspot", n) for n, _ in facts.hotspots[:1])
        + tuple(("entry-point", n) for n in facts.entry_points)
        + tuple(("subsystem", n) for n in facts.subsystem_members)
    )
    chain_short = (
        ", ".join(f"{n.rsplit('.', 1)[-1]} (depth {d})" for n, d in facts.chain_heads)
        or "(none)"
    )
    hot_short = (
        ", ".join(f"{n.rsplit('.', 1)[-1]} ({c})" for n, c in facts.hotspots) or "(none)"
    )
    entry_short = (
        ", ".join(n.rsplit(".", 2)[-2] + "." + n.rsplit(".", 1)[-1] for n in facts.entry_points)
        or "(none)"
    )
    sub_short = (
        f"{len(facts.subsystem_members)} specimen modules "
        f"({', '.join(n.rsplit('.', 1)[-1] for n in facts.subsystem_members)})"
        if facts.subsystem_members
        else "(none)"
    )
    return StepResult(
        "loomweave navigation",
        ok=Path(LOOMWEAVE_DB).exists(),
        detail=(
            f"execution paths: {chain_short}; coupling hotspots: {hot_short}; "
            f"entry points: {entry_short}; cli subsystem: {sub_short}"
        ),
        surfaced=surfaced,
    )


def pairs_from_findings(path: Path) -> tuple[tuple[str, str], ...]:
    """Read Wardline's findings.jsonl → de-duped (rule_id, qualname) pairs."""
    if not Path(path).exists():
        return ()
    pairs: list[tuple[str, str]] = []
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        rule = obj.get("rule_id")
        if rule:
            pairs.append((rule, obj.get("qualname") or ""))
    return tuple(dict.fromkeys(pairs))  # de-duped, order-preserving


def loomweave_analyze() -> StepResult:
    # The generated narrative is compared byte-for-byte by `make verify`, so the
    # detail MUST be deterministic — never echo raw tool stdout (it may carry timing
    # or a run-id and would flap the lockstep check). Derive a stable count from the
    # DB the analyze pass just wrote — EXCLUDING clustering artifacts: subsystem
    # entities and in_subsystem edges are order-sensitive across re-analyze of an
    # unchanged tree (loomweave clarion-14398b2536), so counting them flaps the
    # lockstep too.
    proc = _run([str(BIN / "loomweave"), "analyze"])
    ents = edges = 0
    if LOOMWEAVE_DB.exists():
        try:  # connect() itself can raise (e.g. corrupt DB) — keep the step total
            con = sqlite3.connect(str(LOOMWEAVE_DB))
            try:
                ents = con.execute(
                    "select count(*) from entities where kind != 'subsystem'"
                ).fetchone()[0]
                edges = con.execute(
                    "select count(*) from edges where kind != 'in_subsystem'"
                ).fetchone()[0]
            finally:
                con.close()
        except sqlite3.Error:
            pass
    return StepResult(
        "loomweave analyze",
        ok=proc.returncode == 0,
        detail=f"{ents} entities, {edges} structural edges",
    )


def _finding_qualname(entity_id: str, evidence: str) -> str:
    """Map a loomweave finding to a module qualname the coverage gate can match.

    File-scoped alarms attach to ``core:file:<relpath>``; the duplicate-locator
    attaches to ``core:project:*`` and carries the first colliding source path in
    its evidence metadata. Anything else (e.g. subsystem-scoped facts) yields ""
    — surfaced but matching no planted symbol.
    """
    path = ""
    if entity_id.startswith("core:file:"):
        path = entity_id[len("core:file:"):]
    else:
        try:
            meta = json.loads(evidence or "{}").get("metadata", {})
        except (json.JSONDecodeError, AttributeError):
            meta = {}
        if isinstance(meta, dict):
            path = meta.get("first_source_file_path") or ""
    if not path:
        return ""
    p = Path(path)
    if p.is_absolute():
        try:
            p = p.relative_to(ROOT)
        except ValueError:
            return ""
    return str(p).removesuffix(".py").replace("/", ".")


# The loomweave analyzer alarms the tour DEMONSTRATES (planted lacunae). The
# index also carries incidental, environment/history-dependent FACT-class
# findings — LMWV-FACT-ENTITY-DELETED (incremental-churn deletion tracking),
# LMWV-FACT-CLUSTERING-WEAK-MODULARITY, LMWV-SEC-SECRET-DETECTED,
# LMWV-PY-SYNTAX-ERROR — which come and go with git/index state and would flap
# the byte-for-byte verify lockstep. Scope to the planted set so the narrative
# is deterministic.
PLANTED_LOOMWEAVE_ALARMS = ("LMWV-PY-TOO-COMPLEX", "LMWV-DUPLICATE-LOCATOR")


def loomweave_findings(db_path: Path = LOOMWEAVE_DB) -> StepResult:
    """Surface the PLANTED loomweave analyzer alarms (LMWV-*) from the index DB.

    Deterministic detail: sorted de-duped rule ids of the demonstrated alarms
    only — incidental churn/secret/syntax FACTs are excluded (see
    PLANTED_LOOMWEAVE_ALARMS). Never raises (tour contract): a missing/corrupt DB
    degrades to ok=False / no pairs.
    """
    name = "loomweave findings"
    pairs: list[tuple[str, str]] = []
    if Path(db_path).exists():
        placeholders = ",".join("?" for _ in PLANTED_LOOMWEAVE_ALARMS)
        try:  # connect() itself can raise (e.g. corrupt DB) — keep the step total
            con = sqlite3.connect(str(db_path))
            try:
                rows = con.execute(
                    "select rule_id, entity_id, evidence from findings "
                    f"where rule_id in ({placeholders})",
                    PLANTED_LOOMWEAVE_ALARMS,
                ).fetchall()
            finally:
                con.close()
        except sqlite3.Error:
            rows = []
        for rule, entity_id, evidence in rows:
            pairs.append((rule, _finding_qualname(entity_id or "", evidence or "")))
    pairs = list(dict.fromkeys(pairs))
    rules = sorted({r for r, _ in pairs})
    return StepResult(
        name,
        ok=bool(pairs),
        detail=f"analyzer alarms: {', '.join(rules) or '(none)'}",
        surfaced=tuple(pairs),
    )


# --- warpline: change-impact correctness (advisory, never gates) ---------------

WARPLINE_ANCHOR_LOCATOR = "python:function:specimen/cli.py::_add_book"
# The commit at which warpline first records the specimen-path locator (the
# sampleapp -> specimen rename). Warpline does not follow renames, so this is where
# `_add_book` is "added" in warpline's timeline. A minimal pinned rev-range
# (COMMIT~1..COMMIT) always contains it, so runtime key_id resolution never
# depends on a moving HEAD.
WARPLINE_ANCHOR_COMMIT = "fb01a0138d58fa5326fb855d8dd15687f1960af7"
# The frozen expected downstream: the service method the CLI flow delegates to.
WARPLINE_EXPECTED_DOWNSTREAM = "python:function:specimen/service.py::LibraryService.add_book"


def _warpline_json(args: list[str]) -> dict | None:
    """Run `warpline <args> --json` and parse stdout. None on any failure.

    The single mockable seam for the warpline leg (tests monkeypatch this).
    Never raises (tour contract).
    """
    warpline = _tool("warpline")
    if not warpline:
        return None
    proc = _run([warpline, *args, "--json"])
    try:
        return json.loads(proc.stdout)
    except (json.JSONDecodeError, TypeError):
        return None


def _warpline_data(payload: dict | None) -> dict:
    if isinstance(payload, dict):
        data = payload.get("data")
        if isinstance(data, dict):
            return data
    return {}


def _warpline_items(payload: dict | None) -> list[dict]:
    items = _warpline_data(payload).get("items")
    return items if isinstance(items, list) else []


def _locator_to_qualname(locator: str) -> str:
    """`python:function:specimen/cli.py::_add_book` -> `specimen.cli._add_book`.

    Strips the `{plugin}:{kind}:` prefix, then maps the `path::tail` body to a
    dotted qualname so `report.py::_symbol_matches` credits the planted symbol.
    """
    body = locator.split(":", 2)[-1]
    if "::" in body:
        path, _, tail = body.partition("::")
        module = path.removesuffix(".py").replace("/", ".")
        return f"{module}.{tail}"
    return body.removesuffix(".py").replace("/", ".")


def warpline_change_impact() -> StepResult:
    """Demonstrate warpline's change-impact authority over a FROZEN anchor.

    Warpline has no flaw rules — it is advisory/enrich-only and never gates. This
    leg asserts change-impact CORRECTNESS: touching the add-a-book CLI flow
    (`specimen/cli.py::_add_book`) must surface its downstream service method in
    both the blast-radius and the reverify worklist, and warpline must carry the
    anchor's change history (churn + timeline).

    Self-populates a COLD warpline DB first (it is gitignored, so CI / a fresh
    clone start empty): `backfill` rebuilds the git-history tables that
    changed/churn/timeline read, then `capture-snapshot` rebuilds the loomweave
    edge graph that blast-radius/reverify traverse. capture-snapshot ALONE is
    insufficient — it does not populate git history.

    Two ordering/availability dependencies are load-bearing for the edge graph:
    (1) a freshly-analyzed loomweave index must exist — `_drive()` runs
    `loomweave_analyze` before this leg; (2) `capture-snapshot` shells the
    loomweave CLI, so we pin it BIN-first via `--loomweave-command` exactly as
    `capability._locate` pins every tool (warpline's default is bare-$PATH).
    `make ci` runs via `make` with ~/.local/bin on $PATH, so the edge build
    succeeds there. NOTE: pinning fixes warpline's command *resolution*, but
    loomweave's own plugin loading can still degrade if ~/.local/bin is wholly
    off $PATH (e.g. a hand-run `python -m tour verify` in a stripped shell),
    yielding a SKIPPED snapshot — an upstream loomweave/warpline limitation. In
    that case the leg degrades to ok=False (fail-loud), never a silent pass.

    Determinism (`make verify` is byte-for-byte): the affected SET is snapshot-
    state dependent and key_ids renumber on re-ingest, so `detail` is FROZEN
    prose and `surfaced` carries only stable (token, qualname) pairs — never
    counts, key_ids, timestamps, or set sizes. Never raises (tour contract).
    """
    name = "warpline change impact"
    if not _tool("warpline"):
        return StepResult(name, ok=False, detail="warpline not installed")

    # 1. Self-populate a cold DB (writes .weft/warpline/ only). backfill BEFORE
    #    capture-snapshot — the temporal reads need git history, not just edges.
    #    Pin loomweave BIN-first (warpline's default loomweave resolution is
    #    bare-$PATH; ~/.local/bin may be off a subagent's $PATH).
    loomweave = _tool("loomweave") or "loomweave"
    _warpline_json(["backfill", "--no-resolve-sei"])
    _warpline_json(["capture-snapshot", "--loomweave-command", loomweave])

    anchor_q = _locator_to_qualname(WARPLINE_ANCHOR_LOCATOR)
    want = WARPLINE_EXPECTED_DOWNSTREAM

    # 2. Resolve the anchor's key_id at runtime from a PINNED rev-range that
    #    always contains the anchor's first-seen commit (never hardcode it).
    key_id = None
    rng = f"{WARPLINE_ANCHOR_COMMIT}~1..{WARPLINE_ANCHOR_COMMIT}"
    for item in _warpline_items(_warpline_json(["changed", "--rev-range", rng])):
        entity = item.get("entity", {})
        if entity.get("locator") == WARPLINE_ANCHOR_LOCATOR:
            key_id = entity.get("warpline_entity_key_id")
            break

    blast_ok = reverify_ok = False
    if key_id is not None:
        blast = _warpline_json(["blast-radius", "--changed-entity-key-id", str(key_id), "--depth", "2"])
        blast_ok = any(
            a.get("entity", {}).get("locator") == want
            for a in (_warpline_data(blast).get("affected") or [])
        )
        rev = _warpline_json(["reverify", "--changed-entity-key-id", str(key_id), "--depth", "2"])
        reverify_ok = any(
            it.get("entity", {}).get("locator") == want and it.get("reason") == "downstream"
            for it in _warpline_items(rev)
        )

    # 3. Temporal facts: the anchor carries tracked change history.
    churn_ok = any(
        int(it.get("churn_count", 0)) >= 1
        for it in _warpline_items(_warpline_json(["churn", "--locator", WARPLINE_ANCHOR_LOCATOR]))
    )
    timeline_ok = len(_warpline_items(_warpline_json(["timeline", "--entity", WARPLINE_ANCHOR_LOCATOR]))) >= 1

    ok = blast_ok and reverify_ok and churn_ok and timeline_ok
    surfaced = (
        ("wp-blast-radius", anchor_q),
        ("wp-reverify", anchor_q),
        ("wp-churn", anchor_q),
        ("wp-timeline", anchor_q),
    ) if ok else ()
    return StepResult(
        name,
        ok=ok,
        detail=(
            "touching _add_book surfaces downstream service.add_book in "
            "blast-radius + reverify worklist (edge-provenanced); change history "
            "tracked via churn + timeline — advisory, never gates"
        ),
        surfaced=surfaced,
    )


# ── Plainweave intent-coverage capability demo (pw-*) ──────────────────────────
# Plainweave is advisory / enrich-only / local — no flaw rules; it answers
# "why does this code exist?" via SEI -> requirement -> goal. Like warpline, this
# leg asserts CAPABILITY correctness over frozen anchors, not flaw detection.
PLAINWEAVE_ADD_BOOK = "specimen.cli._add_book"    # justified  (covered)
PLAINWEAVE_REGISTER = "specimen.cli._register"    # deprecated (liveness)
PLAINWEAVE_CLI_MAIN = "specimen.cli.main"         # justified  (covered)
PLAINWEAVE_TOUR_MAIN = "tour.__main__.main"        # orphan + scoped-out
PLAINWEAVE_ABSENT_TAGS = {"exported-api", "http-route"}  # the honest-degradation classes


def _plainweave_json(args: list[str]) -> dict | None:
    """Run `plainweave <args> --json` and parse stdout. None on any failure.

    The single mockable seam for the plainweave leg (tests monkeypatch this). Uses
    `_tool('plainweave')` — NOT import-based detection — because plainweave is
    installed as a uv tool in ~/.local/bin like its siblings. Never raises.
    """
    plainweave = _tool("plainweave")
    if not plainweave:
        return None
    proc = _run([plainweave, *args, "--json"])
    try:
        return json.loads(proc.stdout)
    except (json.JSONDecodeError, TypeError):
        return None


def plainweave_intent() -> StepResult:
    """Demonstrate plainweave's code-up intent graph over the specimen.

    Plainweave never gates. This leg self-populates a COLD, gitignored .plainweave/
    store with a deliberate covered+uncovered mix (tour.plainweave_seed), then
    asserts four capability facts over FROZEN anchors:
      * pw-intent-justified — specimen.cli._add_book (and cli.main) ladder
        SEI->requirement->goal (north-star numerator; intent trace; corpus).
      * pw-intent-liveness  — specimen.cli._register, bound+laddered then its
        requirement DEPRECATED, drops out of the numerator (dead obligations don't count).
      * pw-intent-orphan    — tour.__main__.main, recorded public + unbound, surfaces
        in `intent orphans code` (and coverage.unjustified): an honest gap.
      * pw-surface-scoping  — `--exclude-namespace tour.` scopes the harness entry-point
        out of the product denominator, and coverage honestly reports the catalog
        incomplete (denominator_complete=false; absent exported-api, http-route).

    Depends on a freshly-analyzed loomweave index — `_drive()` runs `loomweave_analyze`
    before this leg — so the SEIs the seed resolves match the live catalog.

    Determinism (`make verify` is byte-for-byte): the north-star is a ratio that moves
    with the catalog, so `detail` is FROZEN prose and `surfaced` carries only stable
    (token, qualname) pairs; live numbers ride the non-rendered `note`. Concurrency:
    the seed wipes+rebuilds .plainweave/ each run (idempotent) — a second concurrent
    tour against this workspace would race it. Never raises (tour contract).
    """
    name = "plainweave intent"
    if not _tool("plainweave"):
        return StepResult(
            name, ok=False,
            detail="plainweave not installed — uv tool install /home/john/plainweave",
        )

    def pw(args: list[str]) -> dict:
        env = _plainweave_json(args)
        if env is None or not env.get("ok"):
            raise RuntimeError(f"plainweave call failed: {args[0] if args else '?'}")
        return env.get("data") or {}

    # All reads AND the fact-computation run inside the try: any schema drift
    # (a missing key, a non-dict) degrades to ok=False, never raises (tour contract).
    try:
        plainweave_seed.seed(pw)
        cov = pw(["intent", "coverage"])
        cov_scoped = pw(["intent", "coverage", "--exclude-namespace", "tour."])
        orphans = pw(["intent", "orphans", "code"]).get("items", [])

        # Reverse-map SEI <-> locator/qualname from coverage (surfaces carry both
        # fields). Defensive .get(): a surface missing a field is skipped, never raises.
        surfaces = list(cov.get("justified", [])) + list(cov.get("unjustified", []))
        sei2loc = {s["sei"]: s["locator"] for s in surfaces if s.get("sei") and s.get("locator")}
        qual2sei = {_locator_to_qualname(loc): sei for sei, loc in sei2loc.items()}
        just_q = {_locator_to_qualname(s["locator"]) for s in cov.get("justified", []) if s.get("locator")}
        unjust_q = {_locator_to_qualname(s["locator"]) for s in cov.get("unjustified", []) if s.get("locator")}
        scoped = list(cov_scoped.get("justified", [])) + list(cov_scoped.get("unjustified", []))
        scoped_q = {_locator_to_qualname(s["locator"]) for s in scoped if s.get("locator")}
        orphan_q = {
            _locator_to_qualname(sei2loc[it["node_id"]])
            for it in orphans
            if it.get("node_id") in sei2loc
        }
        numerator = (cov.get("north_star") or {}).get("numerator")
        absent = set(((cov.get("coverage") or {}).get("absent_tags")) or [])

        # Liveness discrimination (AC#7): _register must be BOUND — its `intent trace`
        # up-walk still reaches a requirement — yet excluded from the live numerator
        # BECAUSE that requirement is deprecated. This distinguishes the demonstrated
        # drop from a never-bound orphan (whose trace up-walk is empty), so a silent
        # bind regression cannot hollowly credit the lacuna.
        reg_sei = qual2sei.get(PLAINWEAVE_REGISTER)
        reg_bound = bool(pw(["intent", "trace", "code", reg_sei]).get("up")) if reg_sei else False
    except Exception as exc:  # tour contract: degrade, never raise. Type name only — no hex/digits.
        return StepResult(name, ok=False, detail=f"plainweave seed/read failed: {type(exc).__name__}")

    pairs: list[tuple[str, str]] = []
    # Each pair is emitted ONLY if its fact holds (partial -> omitted -> verify reds; fail loud).
    if {PLAINWEAVE_ADD_BOOK, PLAINWEAVE_CLI_MAIN} <= just_q:
        pairs.append(("pw-intent-justified", PLAINWEAVE_ADD_BOOK))
    # numerator == 2 is load-bearing: seed() justifies EXACTLY _add_book + cli.main, so a
    # deprecated _register that still counted would push it to 3. reg_bound proves the drop
    # is a deprecation (bound), not a never-bound orphan.
    if PLAINWEAVE_REGISTER in unjust_q and reg_bound and numerator == 2:
        pairs.append(("pw-intent-liveness", PLAINWEAVE_REGISTER))
    if PLAINWEAVE_TOUR_MAIN in orphan_q:
        pairs.append(("pw-intent-orphan", PLAINWEAVE_TOUR_MAIN))
    if (
        PLAINWEAVE_TOUR_MAIN in unjust_q
        and PLAINWEAVE_TOUR_MAIN not in scoped_q
        and cov.get("denominator_complete") is False
        and PLAINWEAVE_ABSENT_TAGS <= absent
    ):
        pairs.append(("pw-surface-scoping", PLAINWEAVE_TOUR_MAIN))

    ns, ns_s = cov.get("north_star") or {}, cov_scoped.get("north_star") or {}
    note = (
        f"north-star {ns.get('numerator')}/{ns.get('denominator')} default, "
        f"{ns_s.get('numerator')}/{ns_s.get('denominator')} scoped; absent_tags={sorted(absent)}"
    )
    return StepResult(
        name,
        ok=len(pairs) == 4,
        detail=(
            "seeded a covered+uncovered intent corpus over the specimen; "
            "cli._add_book and cli.main are justified (SEI->requirement->goal, traced); "
            "_register drops from the numerator once its requirement is deprecated; "
            "tour.__main__.main surfaces as an orphan and is scoped out of the product "
            "denominator; the catalog honestly reports incomplete public-surface tag "
            "coverage — advisory, local-only, never gates"
        ),
        surfaced=tuple(pairs),
        note=note,
    )


def wardline_scan() -> StepResult:
    proc = _run([str(BIN / "wardline"), "scan", "."])
    pairs = pairs_from_findings(ROOT / "findings.jsonl")
    rules = sorted({r for r, _ in pairs})  # sorted → deterministic narrative
    return StepResult(
        "wardline scan",
        ok=proc.returncode in (0, 1),  # 0 clean, 1 gate tripped; 2 is tool error
        detail=f"surfaced rules: {', '.join(rules) or '(none)'}",
        surfaced=pairs,
    )


def rust_scan() -> StepResult:
    """Wardline's Rust frontend over the same tree (`--lang rust`).

    The clean Python scan and the Rust scan are two passes of one tool over one
    repo — the multi-language headline. Surfaces the RS-WL-* taint rules
    (specimen-rs/src/main.rs). Never raises (tour contract).
    """
    name = "wardline scan (rust)"
    wardline = _tool("wardline")
    if not wardline:
        return StepResult(name, ok=False, detail="wardline not installed")
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "rust.jsonl"
        proc = subprocess.run(
            [wardline, "scan", ".", "--lang", "rust", "--output", str(out)],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        pairs = pairs_from_findings(out)
    rules = sorted({r for r, _ in pairs})
    return StepResult(
        name,
        ok=proc.returncode in (0, 1) and bool(pairs),
        detail=f"surfaced rules: {', '.join(rules) or '(none)'}",
        surfaced=pairs,
    )


def _cfg_twin_base(impl_name: str) -> str:
    """Reduce an @cfg impl entity name to the type it twins on. The rust plugin
    names cfg-split impls ``…<Type>.impl#<>@cfg(<pred>)`` — strip from ``.impl#``
    so both predicates collapse to the same ``specimen_rs.catalog.Shelf`` base."""
    return impl_name.split(".impl#", 1)[0]


def rust_archaeology(db_path: Path = LOOMWEAVE_DB) -> StepResult:
    """Rust index facts as harness tokens (like ``dead-entity``): the @cfg impl
    twins, the ``#[path]``-mounted module, the in-project derives edge, and a
    pasted ``::``-path resolved the way ``entity_resolve`` normalizes it.

    Deterministic detail: sorted token names only. Never raises (tour contract).
    Schema (live-pinned 2026-06-12): ``entities(id, kind, name, …)`` — ``name`` is
    the qualname; ``edges(kind, from_id, to_id)`` joined back to entities.
    """
    name = "loomweave rust archaeology"
    pairs: list[tuple[str, str]] = []
    if Path(db_path).exists():
        try:  # connect() itself can raise (e.g. corrupt DB) — keep the step total
            con = sqlite3.connect(str(db_path))
            try:
                twins = con.execute(
                    "select name from entities "
                    "where kind = 'impl' and name like 'specimen_rs%@cfg%'"
                ).fetchall()
                mounted = con.execute(
                    "select count(*) from entities where name = 'specimen_rs.shelving'"
                ).fetchone()[0]
                derive_edges = con.execute(
                    "select ef.name from edges e "
                    "join entities ef on ef.id = e.from_id "
                    "where e.kind = 'derives' and ef.name like 'specimen_rs%'"
                ).fetchall()
                # ::-dialect demo: a pasted Rust path resolves once normalized
                # `::` -> `.` (what entity_resolve does before lookup).
                pasted = "specimen_rs::shelving::label"
                colon_hit = con.execute(
                    "select count(*) from entities where name = ?",
                    (pasted.replace("::", "."),),
                ).fetchone()[0]
            finally:
                con.close()
        except sqlite3.Error:
            twins, mounted, derive_edges, colon_hit = [], 0, [], 0
        if len(twins) >= 2:
            pairs.append(("cfg-twin", _cfg_twin_base(twins[0][0])))
        if mounted:
            pairs.append(("path-mount", "specimen_rs.shelving"))
        for (src,) in derive_edges:
            pairs.append(("derives-edge", src))
        if colon_hit:
            pairs.append(("colon-path-resolved", "specimen_rs.shelving.label"))
    pairs = list(dict.fromkeys(pairs))
    tokens = sorted({t for t, _ in pairs})
    return StepResult(
        name,
        ok=len(pairs) >= 3,
        detail=f"rust index facts: {', '.join(tokens) or '(none)'}",
        surfaced=tuple(pairs),
    )


def wardline_fail_closed() -> StepResult:
    """Scan the quarantine dir expecting the gate to TRIP (fail-closed analyzer).

    The unparseable file must produce WLN-ENGINE-PARSE-ERROR and
    --fail-on-unanalyzed must exit 1. A quarantine scan that PASSES is a failure.
    The surfaced qualname is synthesized from the fixture path (parse-error FACTs
    carry no qualname).
    """
    name = "wardline fail-closed gate"
    wardline = _tool("wardline")
    if not wardline:
        return StepResult(name, ok=False, detail="wardline not installed")
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "quarantine.jsonl"
        proc = subprocess.run(
            [wardline, "scan", str(ROOT / "specimen_quarantine"),
             "--fail-on-unanalyzed", "--output", str(out)],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        rules = {r for r, _ in pairs_from_findings(out)}
    tripped = proc.returncode == 1 and "WLN-ENGINE-PARSE-ERROR" in rules
    return StepResult(
        name,
        ok=tripped,
        detail="unparseable specimen trips the gate: WLN-ENGINE-PARSE-ERROR, exit 1 (fail-closed, not silent)",
        surfaced=(("WLN-ENGINE-PARSE-ERROR", "specimen_quarantine.unparseable"),) if tripped else (),
    )


def filigree_findings() -> StepResult:
    """Demonstrate the Filigree leg: confirm the tracker is reachable.

    The narrative detail is intentionally a STABLE description, not a live issue
    count — the `.filigree/` DB is gitignored and mutates as scans emit findings,
    so embedding its count would make the byte-for-byte `make verify` lockstep flap
    between runs/environments. The Wardline→Filigree dataflow itself is exercised by
    `wardline scan` posting to the scan-results endpoint (the Wardline→Filigree
    bridge — the CLI uses its built-in default; the agent MCP surface is wired in
    `.mcp.json`).
    """
    proc = _run([str(BIN / "filigree"), "list", "--json"])
    ok = proc.returncode == 0
    detail = (
        "live — Wardline findings POST to the filigree scan-results bridge"
        if ok
        else "filigree CLI not reachable"
    )
    return StepResult("filigree list", ok=ok, detail=detail)


FILIGREE_BASE = "http://localhost:8749"


def _federation_token() -> str | None:
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.startswith("WEFT_FEDERATION_TOKEN="):
                value = line.split("=", 1)[1].strip()
                if value:
                    return value
    fallback = Path.home() / ".config" / "filigree" / "federation_token"
    if fallback.exists():
        return fallback.read_text().strip() or None
    return None


def _sentinel_fingerprint() -> str | None:
    """The sentinel is the (sole, unbaselined) PY-WL-125 finding in findings.jsonl.

    findings.jsonl stores the bare 64-hex digest, but wardline's filigree emit
    stamps the wire/store form with its fingerprint scheme
    (``format_fingerprint(FINGERPRINT_SCHEME, ...)`` → ``wlfp2:<hex>``), and
    promote-by-fingerprint matches the stored form — so stamp it here too.
    """
    path = ROOT / "findings.jsonl"
    if not path.exists():
        return None
    for line in path.read_text().splitlines():
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if obj.get("rule_id") == "PY-WL-125":
            fp = obj.get("fingerprint")
            if fp and ":" not in fp:
                fp = f"wlfp2:{fp}"
            return fp
    return None


def _filigree_api(method: str, path: str, token: str, body: dict | None = None) -> object:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        f"{FILIGREE_BASE}{path}",
        data=data,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
        method=method,
    )
    with urllib.request.urlopen(req, timeout=5.0) as resp:
        return json.loads(resp.read())


def filigree_work_cycle() -> StepResult:
    """Cycle ONE sentinel issue through the tracker work lifecycle.

    Run 1: promote the unbaselined PY-WL-125 sentinel finding -> bug at triage,
    claim, walk the bug workflow (triage -> confirmed -> fixing -> verifying),
    close (``fix_verification`` is a required close field from ``verifying``).
    Runs 2+: promote is idempotent (same issue, created=false) -> reopen (lands
    on the most recent non-done predecessor, ``verifying``) -> claim -> close.
    The HTTP claim route requires an explicit assignee (FIL-3 actor-alone landed
    on the MCP/CLI claim verbs, not this dashboard surface — a2ccde6 touches
    cli_commands/mcp_tools only), so the claim passes actor AND assignee. Also
    asserts the two new query surfaces: the priority-range query params (N-6)
    and the suppressed-severity rollup (classic ``/files/stats`` — the weft
    prefix carries no stats route). Detail is a STABLE sentence — live
    ids/counts would flap the verify lockstep.
    """
    name = "filigree work cycle"
    token = _federation_token()
    fp = _sentinel_fingerprint()
    if not token or not fp:
        return StepResult(name, ok=False, detail="sentinel cycle unavailable (token or sentinel finding missing)")
    try:
        promoted = _filigree_api("POST", "/api/p/lacuna/weft/findings/promote", token, {
            "scan_source": "wardline", "fingerprint": fp,
            "labels": ["tour-sentinel"], "actor": "tour",
        })
        issue_id = promoted["issue_id"]
        if not promoted.get("created"):
            # rc12's promote response carries no status field — re-read the issue.
            status = promoted.get("status")
            category = None
            if status is None:
                issue = _filigree_api("GET", f"/api/p/lacuna/weft/issues/{issue_id}", token)
                if isinstance(issue, dict):
                    status = issue.get("status")
                    category = issue.get("status_category")
            if status in ("closed", "done") or category == "closed":
                _filigree_api("POST", f"/api/p/lacuna/weft/issues/{issue_id}/reopen", token, {"actor": "tour"})
        claimed = _filigree_api("POST", f"/api/p/lacuna/weft/issues/{issue_id}/claim", token, {
            "actor": "tour", "assignee": "tour",
        })
        # Walk the bug workflow's soft transitions to the closable status —
        # close is INVALID_TRANSITION except from `verifying`.
        ladder = ("triage", "confirmed", "fixing", "verifying")
        current = claimed.get("status") if isinstance(claimed, dict) else None
        if current in ladder:
            for nxt in ladder[ladder.index(current) + 1:]:
                _filigree_api("PATCH", f"/api/p/lacuna/weft/issues/{issue_id}", token, {
                    "status": nxt, "actor": "tour",
                })
        _filigree_api("POST", f"/api/p/lacuna/weft/issues/{issue_id}/close", token, {
            "actor": "tour", "reason": "tour sentinel cycle complete",
            "fields": {"fix_verification": "tour sentinel cycle — demo lifecycle only; the planted lacuna stays"},
        })
        ranged = _filigree_api("GET", "/api/p/lacuna/weft/issues?priority_min=0&priority_max=4", token)
        stats = _filigree_api("GET", "/api/p/lacuna/files/stats", token)
        suppressed = stats.get("suppressed", {}) if isinstance(stats, dict) else {}
        rollup_ok = sum(int(v) for v in suppressed.values()) > 0
        items = ranged.get("items") if isinstance(ranged, dict) else ranged
        listed_ok = isinstance(items, list) and len(items) > 0
        ok = rollup_ok and listed_ok
        return StepResult(
            name, ok=ok,
            detail=(
                "sentinel issue cycled: promote (idempotent) → claim by actor → close; "
                "priority-range filter and suppressed-severity rollup asserted"
            ),
        )
    except (urllib.error.HTTPError, urllib.error.URLError, OSError,
            json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        return StepResult(name, ok=False, detail=f"sentinel cycle failed: {exc}")


def _tool(name: str) -> str | None:
    """Resolve a tool by ~/.local/bin then PATH (mirrors capability._locate)."""
    candidate = BIN / name
    if candidate.exists():
        return str(candidate)
    return shutil.which(name)


def _free_port() -> int:
    # NOTE: bind→close→reuse is racy (no SO_REUSEPORT); acceptable for a throwaway tour server.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _artifact_secret() -> str | None:
    """Read the shared HMAC secret from lacuna's gitignored .env, if provisioned."""
    env_file = ROOT / ".env"
    if not env_file.exists():
        return None
    for line in env_file.read_text().splitlines():
        if line.startswith("WARDLINE_LEGIS_ARTIFACT_KEY="):
            value = line.split("=", 1)[1].strip()
            return value or None
    return None


def _wait_health(port: int, timeout_s: float = 8.0) -> bool:
    deadline = time.monotonic() + timeout_s
    url = f"http://127.0.0.1:{port}/health"
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1.0) as resp:
                if resp.status == 200:
                    return True
        except (urllib.error.URLError, OSError):
            time.sleep(0.2)
    return False


def _produce_legis_artifact(
    wardline: str, out: Path, secret: str | None
) -> tuple[bool, int, str]:
    """Run `wardline scan --format legis`, writing the artifact to ``out``.

    Returns ``(produced, exit_code, reason)``. The artifact is signed when the
    shared HMAC key is provisioned (the tour's `.env`). Note: wardline loads that
    key from `.env` on disk and then *refuses to sign a dirty working tree* — and
    `scan --format legis` exposes no `--allow-dirty`, so an unsigned fallback by
    clearing the env is impossible (an env override can only *set* the key, not
    unset a `.env` one). The tour's canonical run (`make verify` / CI) is
    post-commit on a clean tree, where signing succeeds; on a dirty tree this
    yields no artifact and the step degrades to ``ok=False`` (tour contract).

    ``reason`` is a short, deterministic explanation when production fails — most
    importantly the dirty-tree signing refusal, so the tour reports *why* legis
    is red instead of a bare exit code. It is "" on success or an unclassified
    failure (the caller falls back to the exit code there).
    """
    scan_env = {**os.environ}
    if secret:
        scan_env["WARDLINE_LEGIS_ARTIFACT_KEY"] = secret
    proc = subprocess.run(
        [wardline, "scan", ".", "--format", "legis", "--output", str(out)],
        cwd=ROOT, capture_output=True, text=True, check=False, env=scan_env,
    )
    produced = out.exists()
    reason = ""
    if not produced and "dirty working tree" in (proc.stderr or ""):
        # Deterministic + actionable: wardline won't sign a legis artifact for a
        # dirty tree, so the signed handshake can't run until the tree is clean.
        reason = (
            "wardline refused to sign the legis artifact: dirty working tree "
            "(uncommitted changes) — commit first, then re-run "
            "(the signed Wardline→Legis handshake requires a clean tree)"
        )
    return produced, proc.returncode, reason


def _spawn_legis_server(env: dict) -> tuple[subprocess.Popen, int]:
    """Start a loopback throwaway `legis serve`; returns (proc, port). Raises OSError if unhealthy."""
    legis = _tool("legis")
    port = _free_port()
    proc = subprocess.Popen(
        [legis, "serve", "--host", "127.0.0.1", "--port", str(port),
         "--governance-db", env.pop("_GOV_DB")],
        cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    if not _wait_health(port):
        proc.terminate()
        raise OSError("legis serve did not become healthy")
    return proc, port


def _post_scan_results(port: int, body: dict, token: str) -> dict:
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/wardline/scan-results",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=5.0) as resp:
        return json.loads(resp.read())


def _teardown(proc: subprocess.Popen | None) -> None:
    if proc is not None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


def legis_govern() -> StepResult:
    """Drive the live Wardline -> Legis governance handshake against the specimen.

    Produce a (signed-when-keyed) legis artifact with `wardline scan --format legis`,
    POST it to a throwaway `legis serve` with server-owned surface_override routing,
    and record the deterministic governed-defect count. Never raises (tour contract).
    """
    # NOTE: signing needs a clean tree, so on a dirty working tree this step
    # degrades to ok=False; the tour's operating condition is a clean checkout
    # (make verify / CI).
    name = "legis govern"
    wardline = _tool("wardline")
    legis = _tool("legis")
    if not wardline or not legis:
        return StepResult(name, ok=False, detail="legis/wardline not installed")

    # The temp dir wraps the try/finally so teardown order on return is:
    # finally (kill the server) FIRST, then TemporaryDirectory.__exit__ deletes
    # the dir (incl. gov.db) — never the inverse.
    with tempfile.TemporaryDirectory() as tmp:
        proc = None
        try:
            # _artifact_secret() reads .env from disk; its OSError must be caught
            # by the except below, so it lives INSIDE the try (never-raises contract).
            secret = _artifact_secret()
            artifact_path = Path(tmp) / "scan.legis.json"
            produced, last_exit, reason = _produce_legis_artifact(wardline, artifact_path, secret)
            if not produced:
                return StepResult(
                    name, ok=False,
                    detail=reason or f"wardline produced no legis artifact (exit {last_exit})",
                )
            artifact = json.loads(artifact_path.read_text())
            signed = bool(artifact.get("artifact_signature"))

            # Real auth: provision an ephemeral API secret and present it as a
            # Bearer token on the writer route (legis HTTPBearer + LEGIS_API_SECRET).
            # The throwaway server is loopback-only and torn down in `finally`.
            api_secret = secrets.token_hex(16)
            serve_env = {
                **os.environ,
                "LEGIS_WARDLINE_CELL": "surface_override",
                "LEGIS_API_SECRET": api_secret,
                "_GOV_DB": f"sqlite:///{Path(tmp) / 'gov.db'}",
            }
            # Only assert verification when BOTH a key is provisioned AND the
            # winning artifact carries a signature (the unsigned fallback drops it).
            if secret and signed:
                serve_env["LEGIS_WARDLINE_ARTIFACT_KEY"] = secret
            proc, port = _spawn_legis_server(serve_env)

            routed = _post_scan_results(
                port, {"agent_id": "lacuna-tour", "scan": artifact}, api_secret
            ).get("routed", [])

            n = len(routed)
            status = ("verified" if (secret and signed) else "unverified")
            return StepResult(
                name, ok=True,
                detail=f"governed {n} active defects → surface_override",
                note=f"artifact: {status}",
            )
        except (urllib.error.HTTPError, urllib.error.URLError, OSError,
                json.JSONDecodeError, ValueError, AttributeError, TypeError) as exc:
            # AttributeError/TypeError guard a non-object JSON response (array/scalar)
            # whose `.get("routed", ...)` would otherwise escape the never-raises contract.
            return StepResult(name, ok=False, detail=f"handshake failed: {exc}")
        finally:
            _teardown(proc)


def legis_reject_malformed() -> StepResult:
    """Feed legis an artifact whose `findings` key is ABSENT and assert the G1
    fail-closed rejection (HTTP 422) — never zero-defects-under-green."""
    name = "legis reject malformed artifact"
    if not _tool("legis"):
        return StepResult(name, ok=False, detail="legis not installed")
    fixture = ROOT / "specimen_quarantine" / "malformed_artifact.json"
    if not fixture.exists():
        return StepResult(name, ok=False, detail="malformed artifact fixture missing")
    proc = None
    try:
        artifact = json.loads(fixture.read_text())
        api_secret = secrets.token_hex(16)
        with tempfile.TemporaryDirectory() as tmp:
            env = {**os.environ, "LEGIS_WARDLINE_CELL": "surface_override",
                   "LEGIS_API_SECRET": api_secret, "_GOV_DB": f"sqlite:///{Path(tmp)}/gov.db"}
            proc, port = _spawn_legis_server(env)
            try:
                _post_scan_results(port, {"agent_id": "lacuna-tour", "scan": artifact}, api_secret)
                return StepResult(name, ok=False, detail="malformed artifact was ACCEPTED — fail-closed contract broken")
            except urllib.error.HTTPError as err:
                if err.code == 422:
                    return StepResult(
                        name, ok=True,
                        detail="absent findings key REJECTED (HTTP 422) — fail-closed, never zero-under-green",
                        surfaced=(("artifact-missing-findings-rejected", "specimen_quarantine.malformed_artifact"),),
                    )
                return StepResult(name, ok=False, detail=f"unexpected rejection status {err.code}")
    except (urllib.error.URLError, OSError, json.JSONDecodeError, ValueError) as exc:
        return StepResult(name, ok=False, detail=f"negative leg failed: {exc}")
    finally:
        _teardown(proc)


def legis_policy_check() -> StepResult:
    """Run `legis policy-boundary-check` over the specimen and assert it
    DISCRIMINATES: the disabled-evidence boundary is flagged, the healthy one is not."""
    name = "legis policy-boundary-check"
    legis = _tool("legis")
    if not legis:
        return StepResult(name, ok=False, detail="legis not installed")
    # Run the INSTALLED legis directly — the same uv-tool build the standing MCP
    # server runs, so the tour validates the surface agents actually hit (the
    # test_fingerprints in specimen/policy_boundaries.py are pinned to its Python;
    # see that file's NOTE). nesting_bomb.py now degrades gracefully
    # (POLICY_BOUNDARY_FILE_TOO_COMPLEX) instead of raising RecursionError, so the
    # old raised-recursion-limit shim is gone.
    proc = _run([
        legis, "policy-boundary-check", "--root", "specimen", "--repo-root", str(ROOT),
    ])
    # Finding-line format: {file}:{line}: {rule_id}: {qualname}: {reason}.
    pairs: list[tuple[str, str]] = []
    for line in (proc.stdout or "").splitlines():
        parts = [p.strip() for p in line.split(": ")]
        if len(parts) >= 4 and parts[1].startswith("POLICY_BOUNDARY"):
            pairs.append((parts[1], parts[2]))
    flagged = [q for _, q in pairs]
    # The live check emits BARE qualnames (`pinned_import`); accept dotted too.
    ok = (
        proc.returncode == 1
        and any(q == "pinned_import" or q.endswith(".pinned_import") for q in flagged)
        and not any(q == "validated_recovery" or q.endswith(".validated_recovery") for q in flagged)
    )
    return StepResult(
        name,
        ok=ok,
        detail=(
            "boundary-evidence check discriminates: disabled-evidence boundary flagged, "
            "healthy boundary passes"
        ),
        surfaced=tuple(pairs) if ok else (),
    )


def legis_posture() -> StepResult:
    """Read the signed posture floor — demonstrates legis's posture layer:
    an operator-minted, hash-chained minimum-enforcement floor, readable over
    MCP (posture_get / policy_list) without the operator key. Provisioned by
    `make setup` (a gitignored, local GENESIS); absent it, those reads cannot
    answer."""
    name = "legis posture floor"
    legis = _tool("legis")
    if not legis:
        return StepResult(name, ok=False, detail="legis not installed")
    proc = _run([legis, "posture", "show"])
    floor = ""
    for line in (proc.stdout or "").splitlines():
        text = line.strip()
        if text.startswith("posture floor:"):
            floor = text.split(":", 1)[1].strip()
            break
    # A readable, ledger-backed floor (not the "structured (no ledger)" default)
    # means the posture surface is provisioned and answerable.
    ok = proc.returncode == 0 and bool(floor) and "no ledger" not in floor
    detail = (
        "signed posture floor is provisioned and readable: an operator-minted "
        "GENESIS pins the minimum enforcement cell in an append-only, hash-chained "
        "ledger; reads need no operator key, raising the floor needs `legis posture "
        "set` under an open operator session — so posture_get / policy_list answer "
        "over MCP instead of failing closed"
        if ok else
        "posture ledger not provisioned — run `make setup` to write the signed "
        "GENESIS; without it posture_get / policy_list cannot read a floor"
    )
    # The concrete cell is environment state (operator-set), kept out of the
    # locked narrative so `make verify` stays byte-deterministic across machines.
    return StepResult(name, ok=ok, detail=detail, note=f"floor={floor or 'unreadable'}")
