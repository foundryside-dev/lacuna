import json
import threading
import time
from pathlib import Path

from tour.mcp_attachment import classify, load_server_specs, probe, redact, ServerSpec
from tour import mcp_attachment as mod
from tour import steps
from tour.manifest import load_manifest
from tour.report import StepResult
from tour import __main__ as tour_main
from tour.capability import Capability

MANIFEST = Path("/home/john/lacuna/tour/lacunae.toml")


# ── Task-1 tests (existing) ────────────────────────────────────────────────────

def test_load_server_specs_parses_stdio_and_http_and_redacts(tmp_path: Path):
    cfg = tmp_path / ".mcp.json"
    cfg.write_text(json.dumps({"mcpServers": {
        "loomweave": {"type": "stdio", "command": "/x/loomweave", "args": ["serve"], "env": {}},
        "legis": {"type": "stdio", "command": "/x/legis",
                  "args": ["mcp", "--agent-id", "codex"], "env": {"LEGIS_WARDLINE_CELL": "surface_override"}},
        "filigree": {"type": "streamable-http", "url": "http://h/mcp/?project=lacuna",
                     "headers": {"Authorization": "Bearer SECRET-TOKEN"}},
    }}))
    specs = load_server_specs(cfg)
    assert specs["loomweave"].transport == "stdio"
    assert specs["loomweave"].command == "/x/loomweave" and specs["loomweave"].args == ("serve",)
    assert specs["legis"].env == {"LEGIS_WARDLINE_CELL": "surface_override"}
    assert specs["filigree"].transport == "streamable-http"
    assert specs["filigree"].url == "http://h/mcp/?project=lacuna"
    assert specs["filigree"].redacted_headers() == {"Authorization": "Bearer <redacted>"}
    # the raw token is never exposed by the redacting accessor
    assert "SECRET-TOKEN" not in json.dumps(specs["filigree"].redacted_headers())


def test_serverspec_repr_does_not_leak_token():
    s = ServerSpec(name="filigree", transport="streamable-http",
                   url="http://h/mcp/", env={"SECRET_CELL": "ENV-SECRET-123"},
                   headers={"Authorization": "Bearer SECRET-TOKEN-XYZ"})
    assert "SECRET-TOKEN-XYZ" not in repr(s)
    assert "SECRET-TOKEN-XYZ" not in str(s)
    # env can carry secrets generally — defense-in-depth, also kept out of repr
    assert "ENV-SECRET-123" not in repr(s)
    assert "ENV-SECRET-123" not in str(s)
    # the redacting accessor is still the way to surface headers safely
    assert s.redacted_headers() == {"Authorization": "Bearer <redacted>"}


# ── Task-2 tests ───────────────────────────────────────────────────────────────

def test_classify_maps_outcomes_to_liveness_classes():
    assert classify(initialized=True,  bound_repo_ok=True,  gated=False, errored=False) == "live-bound"
    assert classify(initialized=True,  bound_repo_ok=False, gated=False, errored=False) == "live-empty"
    assert classify(initialized=False, bound_repo_ok=False, gated=True,  errored=True)  == "reachable-gated"
    # gated wins regardless of errored: the gate, not an error, defines the class. NOTE:
    # `reachable-gated` is PRODUCED only by the Phase-5 join census (e.g. legis→filigree
    # closure-gate), not by the Phase-2 attach probe(); these cases pin the classify contract
    # for that consumer (PDR-0009), so the gated branch is not dead Phase-2 infrastructure.
    assert classify(initialized=True,  bound_repo_ok=False, gated=True,  errored=False) == "reachable-gated"
    assert classify(initialized=False, bound_repo_ok=False, gated=False, errored=True)  == "absent"
    # server returned empty/EOF: nothing initialized, no gate, no error → still absent
    assert classify(initialized=False, bound_repo_ok=False, gated=False, errored=False) == "absent"


def test_probe_times_out_on_a_hung_server_and_classifies_absent(monkeypatch):
    class _NeverReturns:                       # readline() that blocks forever
        def readline(self) -> str:
            threading.Event().wait()
            return ""                          # unreachable
    class _Sink:                               # swallow the JSON-RPC we write out
        def write(self, _data: str) -> int: return 0
        def flush(self) -> None: pass
        def close(self) -> None: pass
    class _HungProc:                           # a Popen test double
        def __init__(self) -> None:
            self.stdin, self.stdout, self.stderr = _Sink(), _NeverReturns(), _NeverReturns()
            self.terminated = self.killed = False
        def terminate(self) -> None: self.terminated = True
        def wait(self, timeout: float | None = None) -> int: return 0
        def kill(self) -> None: self.killed = True
        def communicate(self, timeout: float | None = None) -> tuple[str, str]: return ("", "")
    created: list[_HungProc] = []
    monkeypatch.setattr(mod.subprocess, "Popen",
                        lambda *a, **k: created.append(_HungProc()) or created[-1])
    started = time.monotonic()
    r = probe(ServerSpec(name="loomweave", transport="stdio",
                         command="/bin/sh", args=("serve",)), timeout=1)
    elapsed = time.monotonic() - started
    assert 0.8 <= elapsed < 5                   # the deadline fired at ~timeout, not an instant early-return
    assert created and created[0].terminated    # probe spawned the server AND tore the hung one down
    assert r.attached is False and r.bound is False
    assert r.liveness == "absent"
    assert r.bound_context == "handshake-failed"  # D18: the binary RAN but the handshake stalled → a
                                                  # de-attach (investigate the regression), NOT a missing binary


def test_probe_never_raises_returns_absent_on_spawn_failure(monkeypatch):
    def _boom(*_a, **_k):                           # the binary is gone: spawn raises
        raise FileNotFoundError("[Errno 2] No such file or directory: '/x/loomweave'")
    monkeypatch.setattr(mod.subprocess, "Popen", _boom)
    r = probe(ServerSpec(name="loomweave", transport="stdio",
                         command="/x/loomweave", args=("serve",)), timeout=1)
    assert r.member == "loomweave"
    assert r.attached is False and r.bound is False
    assert r.liveness == "absent"                   # classify(False, False, gated=False, errored=True)
    assert r.error is not None                      # the failure is captured, never propagated
    assert r.bound_context == "not-installed"       # D18: a MISSING binary reads "not installed" (install the
                                                    # *-mcp binary), NOT a silent de-attach — the two must not be confused


def test_redact_strips_authorization_token():       # R5/QA: a real token must NEVER reach AttachResult.error
    leaked = "POST /mcp/ Authorization: Bearer SECRET-TOKEN-123 -> 401 Unauthorized"
    out = redact(leaked)
    assert "SECRET-TOKEN-123" not in out            # the token is gone (a no-op `return s` stub FAILS here)
    assert "Bearer <redacted>" in out


def test_probe_binding_predicate_requires_binding_ok_AND_schema_version(monkeypatch):
    # R1 (CRITICAL): the load-bearing predicate is binding_ok==True AND store.schema_version is
    # not None. An impl that checks ONLY binding_ok is BLIND to wardline's absent-baseline
    # deviation (doctor keeps binding_ok/ok True with schema_version=null), so pin BOTH arms.
    # The interpreter reads structuredContent[K] (K="repo_binding" for wardline); _stdio_rpc is
    # the seam — craft its (init, tools, binding_raw) return to exercise the predicate only.
    init = {"id": 1, "result": {"protocolVersion": "2025-06-18"}}
    tools = {"id": 2, "result": {"tools": []}}
    def _rb(binding_ok, schema_version):                     # wardline-shaped tools/call result
        return {"id": 3, "result": {"structuredContent": {"repo_binding":
                {"binding_ok": binding_ok, "store": {"schema_version": schema_version}}}}}
    spec = ServerSpec(name="wardline", transport="stdio", command="/x/wardline",
                      args=("mcp", "--root", "."))
    def run(binding_ok, schema_version):
        monkeypatch.setattr(mod, "_stdio_rpc",
                            lambda *a, **k: (init, tools, _rb(binding_ok, schema_version)))
        return probe(spec, timeout=1)
    assert run(True, 1).bound is True  and run(True, 1).liveness == "live-bound"        # bound
    assert run(True, None).bound is False and run(True, None).liveness == "live-empty"  # absent-baseline → NOT bound
    assert run(False, 1).bound is False and run(False, 1).liveness == "live-empty"      # verdict false → NOT bound


def test_probe_tolerates_protocol_version_mismatch(monkeypatch):
    # D19 (MEDIUM): a member that echoes a DIFFERENT protocolVersion than requested must still be
    # `attached` — the echoed version is NEVER compared (initialized = "result" in init), so a
    # version bump must not false-RED as absent (the inverse of the failure this gate exists for).
    init = {"id": 1, "result": {"protocolVersion": "2024-11-05"}}   # older than the requested 2025-06-18
    tools = {"id": 2, "result": {"tools": []}}
    rb = {"id": 3, "result": {"structuredContent": {"data":
          {"binding_ok": True, "store": {"schema_version": 4}}}}}
    monkeypatch.setattr(mod, "_stdio_rpc", lambda *a, **k: (init, tools, rb))
    r = probe(ServerSpec(name="warpline", transport="stdio", command="/x/warpline-mcp"), timeout=1)
    assert r.attached is True            # initialized = "result" in init; the version echo is not compared
    assert r.liveness != "absent"


# ── Task-2 DoD extension: binding-predicate tests per legacy stdio member ─────
# Per the DoD: "add a binding-predicate test per legacy stdio member (loomweave, plainweave,
# legis) mirroring the wardline/warpline one — monkeypatch _stdio_rpc to return a crafted
# (init, tools, binding_raw) in that member's unwrap shape and assert `bound` is True only
# when path AND store-read both hold (and False when the store-read arm fails)."

def _base_init_tools():
    init = {"id": 1, "result": {"protocolVersion": "2024-11-05"}}
    tools = {"id": 2, "result": {"tools": []}}
    return init, tools


def _make_loomweave_binding(project_root, db_present, data_version):
    """Craft loomweave binding_raw: content[0].text -> JSON -> result.* shape."""
    inner = {
        "ok": True,
        "result": {
            "project_root": project_root,
            "db_present": db_present,
            "db_identity": {"data_version": data_version},
        },
    }
    return {"id": 3, "result": {"content": [{"type": "text", "text": json.dumps(inner)}]}}


def test_probe_loomweave_binding_predicate_requires_path_AND_db_present_AND_version(monkeypatch):
    """loomweave: bound only when project_root==ROOT AND db_present==True AND data_version is not None."""
    ROOT_STR = str(mod.ROOT)
    init, tools = _base_init_tools()
    spec = ServerSpec(name="loomweave", transport="stdio", command="/x/loomweave", args=("serve",))

    def run(project_root, db_present, data_version):
        binding_raw = _make_loomweave_binding(project_root, db_present, data_version)
        monkeypatch.setattr(mod, "_stdio_rpc", lambda *a, **k: (init, tools, binding_raw))
        return probe(spec, timeout=1)

    # All three conditions satisfied → bound
    assert run(ROOT_STR, True, 2).bound is True
    assert run(ROOT_STR, True, 2).liveness == "live-bound"

    # Store-read arm fails: db_present=False → NOT bound (the de-attach class)
    assert run(ROOT_STR, False, 2).bound is False
    assert run(ROOT_STR, False, 2).liveness == "live-empty"

    # Store-read arm fails: data_version=None → NOT bound
    assert run(ROOT_STR, True, None).bound is False
    assert run(ROOT_STR, True, None).liveness == "live-empty"

    # Path arm fails: wrong root → NOT bound
    assert run("/other/path", True, 2).bound is False
    assert run("/other/path", True, 2).liveness == "live-empty"


def _make_plainweave_binding(db_path, initialized, schema_version):
    """Craft plainweave binding_raw: structuredContent.data shape."""
    return {"id": 3, "result": {"structuredContent": {"data": {
        "db_path": db_path,
        "initialized": initialized,
        "schema_version": schema_version,
    }}}}


def test_probe_plainweave_binding_predicate_requires_path_AND_initialized_AND_schema_version(monkeypatch):
    """plainweave: bound only when db_path under ROOT AND initialized==True AND schema_version is not None."""
    ROOT_STR = str(mod.ROOT)
    GOOD_DB_PATH = f"{ROOT_STR}/.plainweave/plainweave.db"
    init, tools = _base_init_tools()
    spec = ServerSpec(name="plainweave", transport="stdio", command="/x/plainweave-mcp")

    def run(db_path, initialized, schema_version):
        binding_raw = _make_plainweave_binding(db_path, initialized, schema_version)
        monkeypatch.setattr(mod, "_stdio_rpc", lambda *a, **k: (init, tools, binding_raw))
        return probe(spec, timeout=1)

    # All conditions satisfied → bound
    assert run(GOOD_DB_PATH, True, 2).bound is True
    assert run(GOOD_DB_PATH, True, 2).liveness == "live-bound"

    # Store-read arm fails: initialized=False → NOT bound
    assert run(GOOD_DB_PATH, False, 2).bound is False
    assert run(GOOD_DB_PATH, False, 2).liveness == "live-empty"

    # Store-read arm fails: schema_version=None → NOT bound
    assert run(GOOD_DB_PATH, True, None).bound is False
    assert run(GOOD_DB_PATH, True, None).liveness == "live-empty"

    # Path arm fails: db_path not under ROOT → NOT bound
    assert run("/other/path/plainweave.db", True, 2).bound is False
    assert run("/other/path/plainweave.db", True, 2).liveness == "live-empty"


def _make_legis_binding(policy_cells_message, binding_chain_status, governance_chain_status):
    """Craft legis binding_raw: structuredContent.checks[] shape."""
    checks = [
        {"id": "runtime.policy_cells", "status": "ok", "message": policy_cells_message},
        {"id": "store.binding_chain", "status": binding_chain_status},
        {"id": "store.governance_chain", "status": governance_chain_status},
        # benign install warnings (top-level ok=False)
        {"id": "install.gitignore", "status": "error", "message": ".weft/legis/ not in .gitignore"},
    ]
    return {"id": 3, "result": {"structuredContent": {"ok": False, "checks": checks}}}


def test_probe_legis_binding_predicate_requires_path_AND_store_chains(monkeypatch):
    """legis: bound only when policy_cells.message under ROOT AND both store chains 'ok'.
    Top-level structuredContent.ok=False is benign (install warnings) — do NOT use it."""
    ROOT_STR = str(mod.ROOT)
    GOOD_CELLS_PATH = f"{ROOT_STR}/policy/cells.toml"
    init, tools = _base_init_tools()
    spec = ServerSpec(name="legis", transport="stdio", command="/x/legis",
                      args=("mcp", "--agent-id", "test"))

    def run(policy_cells_message, binding_chain_status, governance_chain_status):
        binding_raw = _make_legis_binding(policy_cells_message, binding_chain_status, governance_chain_status)
        monkeypatch.setattr(mod, "_stdio_rpc", lambda *a, **k: (init, tools, binding_raw))
        return probe(spec, timeout=1)

    # All conditions satisfied → bound (even though top-level ok=False)
    r = run(GOOD_CELLS_PATH, "ok", "ok")
    assert r.bound is True
    assert r.liveness == "live-bound"

    # Store-read arm fails: binding_chain not ok → NOT bound
    r = run(GOOD_CELLS_PATH, "error", "ok")
    assert r.bound is False
    assert r.liveness == "live-empty"

    # Store-read arm fails: governance_chain not ok → NOT bound
    r = run(GOOD_CELLS_PATH, "ok", "error")
    assert r.bound is False
    assert r.liveness == "live-empty"

    # Path arm fails: policy_cells not under ROOT → NOT bound
    r = run("/other/policy/cells.toml", "ok", "ok")
    assert r.bound is False
    assert r.liveness == "live-empty"


# ── R8: _http_rpc fake-transport test ─────────────────────────────────────────
# DoD: "a Content-Type: text/event-stream response with a data: JSON-RPC body +
# an Mcp-Session-Id header → assert the SSE body parses and the session-id is
# echoed on the follow-up request."

def test_http_rpc_parses_sse_and_echoes_session_id(monkeypatch):
    """R8: fake urlopen → text/event-stream body with Mcp-Session-Id header.
    Verify: SSE parses correctly and session-id is echoed on follow-up POSTs."""
    import io
    import http.client

    SESSION_ID = "test-session-abc123"
    ROOT_STR = str(mod.ROOT)

    # Build SSE bodies for each call
    def _sse_body(msg: dict) -> bytes:
        line = f"data: {json.dumps(msg)}\n\n"
        return f"event: message\n{line}".encode()

    init_msg = {"id": 1, "result": {"protocolVersion": "2024-11-05",
                                     "serverInfo": {"name": "filigree", "version": "1.28.0"}}}
    tools_msg = {"id": 2, "result": {"tools": [{"name": "mcp_status_get"}]}}
    binding_status = {
        "status": "ok", "db_initialized": True, "schema_compatible": True,
        "project_root": ROOT_STR, "installed_schema_version": 29,
        "database_schema_version": 29, "code": None, "error": None
    }
    binding_msg = {"id": 3, "result": {"content": [{"type": "text",
                                                      "text": json.dumps(binding_status)}]}}

    call_log: list[dict] = []

    class _FakeResp:
        def __init__(self, body: bytes, has_session_id: bool = False) -> None:
            self._body = body
            h = {"Content-Type": "text/event-stream"}
            if has_session_id:
                h["Mcp-Session-Id"] = SESSION_ID
            self.headers = h
        def read(self) -> bytes:
            return self._body
        def __enter__(self): return self
        def __exit__(self, *a): pass

    responses = [
        _FakeResp(_sse_body(init_msg), has_session_id=True),   # init → returns session id
        _FakeResp(_sse_body(tools_msg)),                        # tools/list
        _FakeResp(_sse_body(binding_msg)),                      # binding call
    ]
    response_iter = iter(responses)

    def _fake_urlopen(req, timeout=None):
        call_log.append({
            "url": req.full_url,
            "session_id_header": req.get_header("Mcp-session-id"),
            "accept_header": req.get_header("Accept", ""),
        })
        return next(response_iter)

    monkeypatch.setattr(mod.urllib.request, "urlopen", _fake_urlopen)

    init, tools, binding_raw = mod._http_rpc(
        "http://localhost:8749/mcp/?project=lacuna",
        {"Authorization": "Bearer TEST-TOKEN"},
        timeout=5,
        binding=("mcp_status_get", {}))

    # SSE parsed correctly
    assert "result" in init
    assert init["result"]["serverInfo"]["name"] == "filigree"
    assert "result" in tools
    assert "result" in binding_raw

    # Session-id was echoed on follow-up calls (calls 2 and 3)
    assert len(call_log) == 3
    assert call_log[0]["session_id_header"] is None    # init: no session-id yet
    # Python's urllib lowercases the header name when retrieving via get_header()
    # The second and third calls should carry the session-id
    assert call_log[1]["session_id_header"] == SESSION_ID
    assert call_log[2]["session_id_header"] == SESSION_ID

    # The Accept header MUST be sent on EVERY request — omitting it returns HTTP 406
    # (the PRIMARY silent failure mode for filigree's SSE transport). A refactor dropping
    # it must trip this test, not silently 406 at runtime.
    for entry in call_log:
        assert "application/json, text/event-stream" in entry["accept_header"]


# ── Task 4: steps.mcp_attachment() leg tests ──────────────────────────────────

def test_mcp_attachment_leg_surfaces_attached_members(monkeypatch):
    members = ["loomweave", "filigree", "wardline", "legis", "warpline", "plainweave"]
    monkeypatch.setattr(mod, "load_server_specs",
                        lambda *a, **k: {x: mod.ServerSpec(name=x, transport="stdio") for x in members})
    def fake_probe(spec, **k):
        bound = spec.name != "loomweave"          # loomweave de-attached (binary ran, handshake failed)
        return mod.AttachResult(spec.name, attached=bound, bound=bound,
                                liveness="live-bound" if bound else "absent",
                                bound_context="lacuna" if bound else "handshake-failed", error=None)
    monkeypatch.setattr(mod, "probe", fake_probe)
    r = steps.mcp_attachment()
    assert ("mcp-attach", "loomweave") not in r.surfaced     # not faked live (G3)
    assert ("mcp-attach", "filigree") in r.surfaced
    # D13: `ok` is FROZEN True — the leg never flaps the byte-compared docs/tour.md
    # ([PASS]/[WARN] renders from `ok`). The de-attach trips `make verify` SOLELY via the
    # coverage check (loomweave drops from `surfaced` → its lacuna goes missing), never by
    # turning the narrative stale. The loud signal rides `note`, not `ok`.
    assert r.ok is True                                      # frozen narrative — never flaps lockstep
    assert "loomweave" in r.note                             # the de-attach is flagged in note (stdout)
    # D18: within `absent`, the note distinguishes a real de-attach (handshake-failed) from a
    # never-installed *-mcp binary (not-installed). The diagnostic is variable data → it rides
    # `note` only, NEVER the frozen `detail`. loomweave here is a de-attach.
    assert "loomweave:absent (handshake-failed)" in r.note
    # detail is the EXACT frozen prose — never a live list. An exact-string match is the
    # ONLY assertion that catches an impl that renders live member names/counts/timestamps
    # into detail (a `"loomweave" not in r.detail` no-op passes trivially for ANY
    # member-free string). Quote the leg's frozen detail verbatim:
    assert r.detail == (
        "all .mcp.json members reachable MCP-first and bound to the staged repo — "
        "federation seam integrity asserted; a silent de-attach trips this gate")


def test_mcp_attachment_leg_frozen_ok_on_missing_config(monkeypatch):
    # R2/D13 (HIGH): .mcp.json is gitignored → load_server_specs() raises FileNotFoundError on a
    # fresh clone. This is the EXACT invariant that regressed in round 2 (the outer except used to
    # return ok=False). Pin it: the leg keeps ok=True (frozen) with surfaced=() so the [PASS]/[WARN]
    # marker never flips (the stale-baseline trap) — make verify fails via the coverage gate instead.
    def _boom(*_a, **_k):
        raise FileNotFoundError("[Errno 2] No such file or directory: '.mcp.json'")
    monkeypatch.setattr(mod, "load_server_specs", _boom)
    r = steps.mcp_attachment()
    assert r.ok is True                          # FROZEN — never flips the narrative marker (R2)
    assert r.detail == steps._MCP_ATTACH_DETAIL  # byte-identical to the happy path (one shared constant)
    assert r.surfaced == ()                      # all 6 mcp-attach lacunae go missing → verify fails loud
    assert "mcp attachment unavailable" in r.note


# ── Task 3: MCP-attachment lacunae tests ───────────────────────────────────────

def test_mcp_attach_lacunae_match_surfaced_tokens_and_trip_on_miss():
    from pathlib import Path
    from tour.manifest import load_manifest
    from tour.report import coverage, StepResult

    MANIFEST = Path("/home/john/lacuna/tour/lacunae.toml")
    m = load_manifest(MANIFEST)
    ids = {l.id for l in m.lacunae}
    members = ["loomweave", "filigree", "wardline", "legis", "warpline", "plainweave"]
    assert {f"mcp-attach-{x}" for x in members} <= ids
    # all 6 surfaced → all 6 demonstrated
    all6 = StepResult("mcp", True, "", tuple(("mcp-attach", x) for x in members))
    assert {f"mcp-attach-{x}" for x in members} <= coverage(m, [all6]).demonstrated_ids
    # loomweave de-attached (token absent) → its lacuna is MISSING (gate trips)
    five = StepResult("mcp", False, "", tuple(("mcp-attach", x) for x in members if x != "loomweave"))
    assert "mcp-attach-loomweave" in coverage(m, [five]).missing_ids


# ── Task 6: Negative tests — gate trips on a silent de-attach, names cause ─────

def test_run_verify_trips_when_live_member_de_attaches(monkeypatch, capsys):
    manifest = load_manifest(MANIFEST)
    # The leg surfaces EVERY planted lacuna EXCEPT mcp-attach-loomweave (the de-attached
    # member), so coverage()'s ONLY miss is that one token; distinct member names never
    # cross-match (_symbol_matches is exact / dotted-suffix), so no sibling covers it.
    surfaced = tuple(
        (l.expected_rule, l.symbol) for l in manifest.lacunae if l.id != "mcp-attach-loomweave"
    )
    # The leg carries the failure CAUSE in `note` (the real leg builds this in Task 4:
    # `ATTACH FAILED: … | <member>:<liveness>; …`, members sorted) — run_verify must
    # surface it so the gate names WHY, not only WHICH (D17). loomweave is the de-attach.
    leg = StepResult("mcp attachment", True, "frozen detail", surfaced,
                     note=("ATTACH FAILED: mcp-attach-loomweave — fix before running make "
                           "tour; the coverage gate fails verify by name | "
                           "filigree:live-bound; legis:live-bound; loomweave:absent (handshake-failed); "
                           "plainweave:live-bound; warpline:live-bound; wardline:live-bound"))
    # loomweave's CLI is LIVE — THIS is the `expected_tool in live` condition that ARMS the
    # gate (mcp-attach-loomweave.expected_tool == "loomweave"). Only loomweave is live here,
    # so it is the SOLE member whose missing token can trip verify → exactly one failure.
    caps = [Capability(name="loomweave", available=True, detail="/x/loomweave")]
    # run_verify() already HAS an injection seam: _drive is a module-level function, so the
    # (caps, results) refactor the defect floats is unnecessary — monkeypatch _drive directly.
    monkeypatch.setattr(tour_main, "_drive", lambda: (caps, [leg]))
    # Isolate the lockstep branch: echo the committed docs so fresh == on-disk and the
    # narrative-staleness failure cannot fire, leaving the live-member coverage gate the SOLE cause.
    monkeypatch.setattr(tour_main, "render_tour_md", lambda results: tour_main.TOUR_MD.read_text())
    monkeypatch.setattr(tour_main, "render_matrix_md", lambda m, c: tour_main.MATRIX_MD.read_text())

    rc = tour_main.run_verify()
    out = capsys.readouterr().out
    assert rc == 1                          # the gate trips: a live member's attach token went dark
    assert "mcp-attach-loomweave" in out    # ...and run_verify NAMES the de-attached member
    assert "stale" not in out               # RIGHT reason — the live-member coverage gate, NOT doc drift
    # D17: run_verify names not just WHICH token went dark but WHY — the leg's `note`
    # (per-member liveness / the ATTACH FAILED cause: timed-out / garbled JSON /
    # connected-but-unbound / missing binary) rides through, so the operator sees the
    # cause, not a bare token. `note` is excluded from the locked markdown (StepResult.note
    # is never rendered into docs/tour.md), so emitting it on failure preserves determinism.
    assert "loomweave:absent (handshake-failed)" in out  # the CAUSE is surfaced, not only the token


def test_run_verify_trips_on_not_installed_mcp_binary_distinctly(monkeypatch, capsys):
    # D18: the SECOND absent scenario — a live member whose SEPARATE *-mcp binary is not
    # installed. capability.detect() marks `warpline` live by its CLI name, but .mcp.json
    # spawns the distinct `warpline-mcp` binary; when that binary is absent the probe folds
    # to `absent` with bound_context "not-installed". The gate must still trip and name the
    # member, but the diagnostic must read "not-installed" (install the binary) — NOT
    # "handshake-failed" (a de-attach to investigate), so the two are never confused.
    manifest = load_manifest(MANIFEST)
    surfaced = tuple(
        (l.expected_rule, l.symbol) for l in manifest.lacunae if l.id != "mcp-attach-warpline"
    )
    leg = StepResult("mcp attachment", True, "frozen detail", surfaced,
                     note=("ATTACH FAILED: mcp-attach-warpline — fix before running make "
                           "tour; the coverage gate fails verify by name | "
                           "filigree:live-bound; legis:live-bound; loomweave:live-bound; "
                           "plainweave:live-bound; warpline:absent (not-installed); "
                           "wardline:live-bound"))
    # Only `warpline` (the CLI capability.detect() resolves) is live, so mcp-attach-warpline
    # is the SOLE armed lacuna whose missing token can trip verify → exactly one failure.
    caps = [Capability(name="warpline", available=True, detail="/x/warpline")]
    monkeypatch.setattr(tour_main, "_drive", lambda: (caps, [leg]))
    monkeypatch.setattr(tour_main, "render_tour_md", lambda results: tour_main.TOUR_MD.read_text())
    monkeypatch.setattr(tour_main, "render_matrix_md", lambda m, c: tour_main.MATRIX_MD.read_text())

    rc = tour_main.run_verify()
    out = capsys.readouterr().out
    assert rc == 1                                     # the gate trips for a missing *-mcp binary too
    assert "mcp-attach-warpline" in out                # ...naming the member
    assert "stale" not in out                          # RIGHT reason — the live-member coverage gate, not drift
    assert "warpline:absent (not-installed)" in out    # D18: diagnosed as NOT-INSTALLED (install the binary)...
    assert "handshake-failed" not in out               # ...and NEVER confused with a de-attach
