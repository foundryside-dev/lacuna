"""Drive each live Loom tool against the specimen. Steps never raise."""

from __future__ import annotations

import json
import sqlite3
import subprocess
from dataclasses import dataclass
from pathlib import Path

from tour.report import StepResult

ROOT = Path("/home/john/lacuna")
BIN = Path("/home/john/.local/bin")
CLARION_DB = ROOT / ".clarion" / "clarion.db"


def _run(cmd: list[str], cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)


@dataclass(frozen=True)
class StructureFacts:
    dead: tuple[str, ...]           # function entities with no incoming call/ref/import edge
    cycle_members: tuple[str, ...]  # entity names participating in an `imports` 2-cycle


def structure_facts(db_path: Path = CLARION_DB) -> StructureFacts:
    """Read structural facts straight from Clarion's SQLite index.

    Clarion ships no dead-code/cycle CLI verb, so the harness queries the DB the
    `clarion analyze` pass already wrote. Never raises: a missing/locked DB yields
    empty facts.
    """
    if not Path(db_path).exists():
        return StructureFacts(dead=(), cycle_members=())
    try:
        con = sqlite3.connect(str(db_path))
    except sqlite3.Error:
        return StructureFacts(dead=(), cycle_members=())
    try:
        dead = tuple(
            r[0]
            for r in con.execute(
                "select name from entities where kind='function' and id not in "
                "(select to_id from edges where kind in ('calls','references','imports'))"
            )
        )
        members: list[str] = []
        for ef, et in con.execute(
            "select ef.name, et.name from edges a "
            "join edges b on a.from_id=b.to_id and a.to_id=b.from_id "
            "join entities ef on ef.id=a.from_id "
            "join entities et on et.id=a.to_id "
            "where a.kind='imports' and b.kind='imports' and a.from_id<a.to_id"
        ):
            members.extend((ef, et))
        return StructureFacts(dead=dead, cycle_members=tuple(dict.fromkeys(members)))
    except sqlite3.Error:
        return StructureFacts(dead=(), cycle_members=())
    finally:
        con.close()


def clarion_structure() -> StepResult:
    """Surface Clarion's structural lacunae as (token, qualname) pairs the coverage
    map matches against a SPECIFIC lacuna symbol — never a bare token."""
    facts = structure_facts()
    surfaced = tuple(("dead-entity", n) for n in facts.dead) + tuple(
        ("circular-import", n) for n in facts.cycle_members
    )
    dead_short = ", ".join(sorted(n.rsplit(".", 1)[-1] for n in facts.dead)) or "(none)"
    cyc_short = ", ".join(sorted(n.rsplit(".", 1)[-1] for n in facts.cycle_members)) or "(none)"
    return StepResult(
        "clarion structure",
        ok=Path(CLARION_DB).exists(),
        detail=f"dead entities: {dead_short}; import cycle: {cyc_short}",
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


def clarion_analyze() -> StepResult:
    # The generated narrative is compared byte-for-byte by `make verify`, so the
    # detail MUST be deterministic — never echo raw tool stdout (it may carry timing
    # or a run-id and would flap the lockstep check). Derive a stable count from the
    # DB the analyze pass just wrote.
    proc = _run([str(BIN / "clarion"), "analyze"])
    ents = edges = 0
    if CLARION_DB.exists():
        con = sqlite3.connect(str(CLARION_DB))
        try:
            ents = con.execute("select count(*) from entities").fetchone()[0]
            edges = con.execute("select count(*) from edges").fetchone()[0]
        except sqlite3.Error:
            pass
        finally:
            con.close()
    return StepResult(
        "clarion analyze",
        ok=proc.returncode == 0,
        detail=f"{ents} entities, {edges} edges",
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


def filigree_findings() -> StepResult:
    proc = _run([str(BIN / "filigree"), "list", "--json"])
    ok = proc.returncode == 0
    try:
        items = json.loads(proc.stdout) if ok else []
        count = len(items) if isinstance(items, list) else len(items.get("issues", []))
    except (json.JSONDecodeError, AttributeError):
        count = 0
    return StepResult("filigree list", ok=ok, detail=f"{count} tracked issue(s)")
