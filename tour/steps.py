"""Drive each live Loom tool against the specimen. Steps never raise."""

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
        # functions avoids the huge false-positive list Clarion's static call graph
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
        try:  # connect() itself can raise (e.g. corrupt DB) — keep the step total
            con = sqlite3.connect(str(CLARION_DB))
            try:
                ents = con.execute("select count(*) from entities").fetchone()[0]
                edges = con.execute("select count(*) from edges").fetchone()[0]
            finally:
                con.close()
        except sqlite3.Error:
            pass
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
    """Demonstrate the Filigree leg: confirm the tracker is reachable.

    The narrative detail is intentionally a STABLE description, not a live issue
    count — the `.filigree/` DB is gitignored and mutates as scans emit findings,
    so embedding its count would make the byte-for-byte `make verify` lockstep flap
    between runs/environments. The Wardline→Filigree dataflow itself is exercised by
    `wardline scan` posting to the scan-results endpoint configured in wardline.yaml.
    """
    proc = _run([str(BIN / "filigree"), "list", "--json"])
    ok = proc.returncode == 0
    detail = (
        "live — Wardline findings POST to the filigree scan-results bridge (wardline.yaml)"
        if ok
        else "filigree CLI not reachable"
    )
    return StepResult("filigree list", ok=ok, detail=detail)


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
) -> tuple[bool, int]:
    """Run `wardline scan --format legis`, writing the artifact to ``out``.

    Returns ``(produced, exit_code)``. The artifact is signed when the shared
    HMAC key is provisioned (the tour's `.env`). Note: wardline loads that key
    from `.env` on disk and then *refuses to sign a dirty working tree* — and
    `scan --format legis` exposes no `--allow-dirty`, so an unsigned fallback by
    clearing the env is impossible (an env override can only *set* the key, not
    unset a `.env` one). The tour's canonical run (`make verify` / CI) is
    post-commit on a clean tree, where signing succeeds; on a dirty tree this
    yields no artifact and the step degrades to ``ok=False`` (tour contract).
    """
    scan_env = {**os.environ}
    if secret:
        scan_env["WARDLINE_LEGIS_ARTIFACT_KEY"] = secret
    proc = subprocess.run(
        [wardline, "scan", ".", "--format", "legis", "--output", str(out)],
        cwd=ROOT, capture_output=True, text=True, check=False, env=scan_env,
    )
    return out.exists(), proc.returncode


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
            produced, last_exit = _produce_legis_artifact(wardline, artifact_path, secret)
            if not produced:
                return StepResult(name, ok=False,
                                  detail=f"wardline produced no legis artifact (exit {last_exit})")
            artifact = json.loads(artifact_path.read_text())
            signed = bool(artifact.get("artifact_signature"))

            # Real auth: provision an ephemeral API secret and present it as a
            # Bearer token on the writer route (legis HTTPBearer + LEGIS_API_SECRET).
            # The throwaway server is loopback-only and torn down in `finally`.
            api_secret = secrets.token_hex(16)
            port = _free_port()
            serve_env = {
                **os.environ,
                "LEGIS_WARDLINE_CELL": "surface_override",
                "LEGIS_API_SECRET": api_secret,
            }
            # Only assert verification when BOTH a key is provisioned AND the
            # winning artifact carries a signature (the unsigned fallback drops it).
            if secret and signed:
                serve_env["LEGIS_WARDLINE_ARTIFACT_KEY"] = secret
            gov_db = f"sqlite:///{Path(tmp) / 'gov.db'}"
            proc = subprocess.Popen(
                [legis, "serve", "--host", "127.0.0.1", "--port", str(port),
                 "--governance-db", gov_db],
                cwd=ROOT, env=serve_env,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            if not _wait_health(port):
                return StepResult(name, ok=False, detail="legis serve did not become healthy")

            body = json.dumps({"agent_id": "lacuna-tour", "scan": artifact}).encode("utf-8")
            req = urllib.request.Request(
                f"http://127.0.0.1:{port}/wardline/scan-results",
                data=body,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_secret}",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                routed = json.loads(resp.read()).get("routed", [])

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
            if proc is not None:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
