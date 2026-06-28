"""Spawn each .mcp.json-configured MCP server, assert it attaches + binds to the
staged Lacuna repo. Client mechanism + per-member fallbacks recorded by Phase-0 spike.

MODULE BUNDLING (ADR-note) — parser (load_server_specs/ServerSpec) + probe (_stdio_rpc/
_http_rpc transports) + classify() are co-located in this ONE module because they share a
single seam (.mcp.json → attach evidence) with no external callers beyond steps.py; a
separate ADR file is not warranted. The join census (Phase 5) and/or the transports may
be extracted into their own modules later if they grow.

BINDING EVIDENCE CONTRACT — canonical source: docs/plans/phase0-findings.md (Phase-0
spike, 2026-06-28). Task-2 implementors MUST read that file before implementing probe();
the table below is a pointer, not a reproduction.

Summary of spike refinements (supersedes any pre-spike table):

  Three unwrap shapes (not all structuredContent):
    1. content[0].text → top-level JSON key: filigree (project_root at top level).
    2. content[0].text → nested result.* key: loomweave (result.project_root; the
       text-JSON top level is {ok, result, diagnostics, stats_delta}).
    3. structuredContent.*: wardline, warpline, legis, plainweave.

  Path-vs-store (4 path members must assert BOTH):
    loomweave, filigree, legis, and plainweave return a path field that may echo
    ROOT even when the backing store is absent or unreadable. The gate MUST assert
    BOTH the path predicate AND the store-read signal — check the FULL AND, not one
    field. Precise per-member store-read signals (phase0-findings.md table is canonical):
      loomweave   result.db_present == True AND result.db_identity.data_version is not None
      filigree    db_initialized == True AND schema_compatible == True
      legis       store.binding_chain == "ok" AND store.governance_chain == "ok"
      plainweave  structuredContent.data.initialized == True AND schema_version is not None
    wardline and warpline already return a store-read binding_ok boolean (plus
    store.schema_version is not null) — no separate path predicate needed for those two.

  The envelope ok is call-success, never the verdict:
    All six members' binding tool returns an ok field at the envelope level. This
    signals whether the RPC call succeeded, NOT whether the member is bound to ROOT.
    Legis in particular returns structuredContent.ok = False on benign install warnings
    while being correctly bound. Read the contract field, not the envelope ok.

  Per-member silent-failure modes (Task-2 implementer MUST handle; phase0-findings.md §1-7):
    filigree (streamable-http SSE): the request MUST send the header
      Accept: application/json, text/event-stream — omitting it returns HTTP 406 with a
      JSON-RPC error, the PRIMARY silent failure mode for this transport. The transport is
      STATELESS (no Mcp-Session-Id returned); capture and echo it defensively if a future
      server starts sending one, but follow-up POSTs need only the auth header today.
    legis: the binding call is doctor_get (returns all checks cleanly) — NOT posture_get /
      policy_list, which crash on "no such table: audit_log". Read the NAMED check
      (runtime.policy_cells), not top-level structuredContent.ok (False on benign install
      warnings while correctly bound).
    wardline: the doctor binding read is INDEPENDENT of the loomweave :9730 HTTP companion
      (:9730 serves wardline's emit/scan path, not the binding read) — no spawn-ordering
      requirement; wardline may spawn before loomweave serve.

All 6 members self-report a server-resolved store-read fact. The tautological
cwd==ROOT static lint is NOT used — wardline and warpline now have real binding tools
(doctor and warpline_project_status_get). A member that initialises but fails its
binding-touching call classifies live-empty and the gate fails loudly naming it.

TRANSPORT BOUNDARY — the MCP wire client is two replaceable callables, _stdio_rpc(
command, args, env, *, timeout, binding=None) and _http_rpc(url, headers, *, timeout,
binding=None) — `binding` is a (tool_name, arguments) pair or None: repo-per-call members
(warpline-mcp, whose _repo_arg rejects empty args) carry {"repo": str(ROOT)}, launch/cwd-bound
members carry {}. Each completes the handshake and returns the RAW initialize +
tools/list dicts (plus the optional per-member `binding` response, which rides the same
session). They are the ONLY place the wire framing lives and are member-agnostic (raw
command/args/env or url/headers — never a ServerSpec, no str(ROOT) compare); probe()
picks the per-member binding call and interprets the contract field above, so a
transport/protocol swap (or moving to the official `mcp` SDK) is a one-call change.
scripts/characterize_mcp_attachment.py (Phase 0) reuses these SAME two transports rather
than carrying its own copy. The monkeypatch test seam stays at probe().

SECURITY: .mcp.json carries a live Filigree Bearer token (filigree headers). It is
held in-memory only to authenticate the live probe and is NEVER returned, printed, or
persisted un-redacted — use redacted_headers() / redact() for any emitted structure."""
from __future__ import annotations
import json
import os
import re
import subprocess
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path("/home/john/lacuna")


@dataclass(frozen=True)
class ServerSpec:
    name: str
    transport: str                      # "stdio" | "streamable-http"
    command: str | None = None
    args: tuple[str, ...] = ()
    env: dict[str, str] = field(default_factory=dict, repr=False)
    url: str | None = None
    headers: dict[str, str] = field(default_factory=dict, repr=False)

    def redacted_headers(self) -> dict[str, str]:
        return {k: ("Bearer <redacted>" if k.lower() == "authorization" else v)
                for k, v in self.headers.items()}


def load_server_specs(cfg_path: Path = ROOT / ".mcp.json") -> dict[str, ServerSpec]:
    raw = json.loads(Path(cfg_path).read_text())
    out: dict[str, ServerSpec] = {}
    for name, s in raw.get("mcpServers", {}).items():
        out[name] = ServerSpec(
            name=name, transport=s.get("type", "stdio"),
            command=s.get("command"), args=tuple(s.get("args", [])),
            env=dict(s.get("env", {})), url=s.get("url"),
            headers=dict(s.get("headers", {})))
    return out


# ── Security: token redaction ─────────────────────────────────────────────────

# Redact an Authorization header VALUE in any free string, robust to the serialized
# forms an error/repr can take. Capture groups:
#   sep    — the Authorization NAME (optionally wrapped in quotes, as in a JSON/dict key
#            "Authorization": …) plus its separator (`:` or `=`) and any opening quote of
#            the VALUE. Handles  Authorization: …  Authorization = …  AND the JSON/dict
#            forms  "Authorization": "…"  /  'Authorization': '…'  — the pre-hardening
#            regex missed these because the char after the bare name is a quote, not :/=.
#   scheme — an optional auth scheme to PRESERVE (Bearer/Basic/Digest/Token); the secret
#            that FOLLOWS it is what we strip. A non-Bearer value (Basic CREDS) previously
#            leaked CREDS because only `bearer` was matched.
#   secret — the value run (stops at a closing quote or whitespace) — dropped, never echoed.
_AUTH_RE = re.compile(
    r"""(?ix)
    (?P<sep>
        ["']? authorization ["']?      # the header NAME, optionally quoted (JSON/dict key)
        \s* [:=] \s*                   # separator (mandatory once the name is matched)
        ["']?                          # optional opening quote of the VALUE
    )
    (?P<scheme> (?: bearer | basic | digest | token ) \s+ )?   # optional scheme to keep
    (?P<secret> [^"'\s]+ )                                     # the secret value
    """
)


def redact(s: str) -> str:
    """R5: strip any Authorization header VALUE from an ARBITRARY string (error messages,
    stderr tails, dict/JSON reprs) before it lands in AttachResult.error, is printed, or
    persisted. Distinct from ServerSpec.redacted_headers() (a headers-dict redactor); this
    sanitises free strings. Robust to the separator (`:`/`=`/quoted JSON form) and to the
    auth scheme (Bearer/Basic/Digest/Token — the scheme is kept, the secret is replaced).
    Required — probe()'s except handlers call redact(str(e)); filigree is the only token-
    carrying member (its 401s can echo the header). Tested by test_redact_*."""
    def _sub(m: re.Match) -> str:
        scheme = m.group("scheme") or "Bearer "   # default label when no scheme present
        return m.group("sep") + scheme + "<redacted>"
    return _AUTH_RE.sub(_sub, s)


# ── Result type ───────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class AttachResult:
    """R5: the per-member probe outcome (referenced across Tasks 2/4 but defined HERE). For an
    absent member `bound_context` carries the D18 diagnostic — "not-installed" | "handshake-failed"
    | "probe-raised"; for a live member it carries the binding evidence. `error` is redact()-
    sanitised and length-bounded."""
    member: str
    attached: bool
    bound: bool
    liveness: str            # "live-bound" | "live-empty" | "reachable-gated" | "absent"
    bound_context: str
    error: str | None = None


# ── Classification ────────────────────────────────────────────────────────────

def classify(initialized: bool, bound_repo_ok: bool, gated: bool, errored: bool) -> str:
    """R5: raw probe outcome → liveness class (pure; the single decision point). Precedence:
    a `gated` member is REACHABLE (an auth/operator gate, e.g. legis→filigree closure-gate) and
    wins over everything; then initialized+bound → live-bound, initialized-but-unbound →
    live-empty; anything else (no initialize, or a raised/early error) → absent. `errored` is
    recorded for caller intent + the absent diagnostic; it does NOT override `gated` and
    otherwise never changes the class (errors already fold into initialized=False/bound=False
    at the call site), so its presence in the signature is documentation, not a live branch."""
    if gated:
        return "reachable-gated"
    if initialized and bound_repo_ok:
        return "live-bound"
    if initialized:
        return "live-empty"
    return "absent"


# ── Deadline-bounded readline ─────────────────────────────────────────────────

def _readline_deadline(stream, remaining_s: float) -> str | None:
    """Bound the otherwise-unbounded readline() by a wall-clock deadline. Returns the
    line, or None if `remaining_s` elapses first — the caller then tears the server
    down and classifies it `absent` (never a bare blocking readline())."""
    box: list[str] = []
    t = threading.Thread(target=lambda: box.append(stream.readline()), daemon=True)
    t.start()
    t.join(max(0.0, remaining_s))
    return box[0] if (not t.is_alive() and box) else None


def _recv_result(stream, want_id: int, deadline: float) -> dict | None:
    """Correlate by JSON-RPC id: read deadline-bounded lines until one whose
    msg.get("id") == want_id arrives, discarding interleaved notification messages
    (no "id" field — progress/log notifications MCP servers may emit mid-sequence).
    Returns the parsed response, or None if the deadline elapses (caller tears the
    server down and classifies it `absent`). A bare one-readline()-per-request would
    mis-parse a notification as the result and KeyError on missing result/id."""
    while True:
        line = _readline_deadline(stream, deadline - time.monotonic())
        if not line:                               # None = deadline elapsed (hung server); "" = EOF
            return None                            #   (server closed stdout). Both are falsy → return None
        msg = json.loads(line)                     #   BEFORE json.loads, so it is never called on "" (probe folds → absent)
        if msg.get("id") == want_id:               # the response to OUR request
            return msg
        # else: a notification (no "id") or a stale id — discard, keep reading


def _teardown(proc) -> None:                       # mirror tour/steps.py:1160 (local; no import of steps)
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


# ── Wire transports (D10) ─────────────────────────────────────────────────────

# Per-member stdio binding tool + ARGUMENTS for its tools/call. Launch-/cwd-bound members
# (loomweave serve, legis, wardline `--root .`, plainweave resolves root from cwd) take NO
# per-call repo → {}. warpline-mcp is REPO-PER-CALL — its `_repo_arg` REJECTS an empty
# `arguments` object — so its binding call MUST pass {"repo": str(ROOT)}; sending {} would
# raise MissingRequiredFieldError and false-RED a perfectly healthy warpline (a NEW break R1
# introduces: pre-R1 warpline was binding=None, so {} was never sent to a repo-requiring tool).
# R1 (CONFIRMED LIVE 2026-06-28): warpline → repo-per-call `warpline_project_status_get`;
# wardline → its launch-bound `doctor` (the doctor.repo_binding block). Every member is self-
# report now — no static-lint entry, no tautological cwd==ROOT check. probe() reads the binding
# fact from result["structuredContent"] — warpline under ["data"], wardline under ["repo_binding"].
_STDIO_BINDING = {
    "loomweave": ("project_status_get", {}),                           # launch-bound (serve)
    "legis": ("doctor_get", {}),                                       # launch-bound
    "plainweave": ("plainweave_project_context_get", {}),             # cwd-bound; only optional include_contracts
    "warpline": ("warpline_project_status_get", {"repo": str(ROOT)}),  # R1 CONFIRMED — REPO-PER-CALL (_repo_arg)
    "wardline": ("doctor", {}),                                        # R1 CONFIRMED — launch-bound; doctor.repo_binding
}


def _stdio_rpc(command, args, env, *, timeout: float,
               binding: tuple[str, dict] | None = None) -> tuple[dict, dict, dict | None]:
    """stdio wire transport. Reads are deadline-bounded (never a bare readline()); the
    child is ALWAYS reaped in finally. Raises TimeoutError on a hung read and propagates
    FileNotFoundError from a missing binary — probe()'s except folds either into an
    `absent` result (D09). Returns the raw (initialize, tools/list, binding|None) dicts."""
    deadline = time.monotonic() + timeout
    proc = subprocess.Popen(                            # may raise FileNotFoundError (folded by probe)
        [command, *args], cwd=ROOT, text=True,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,                      # R3: NOT PIPE. The production transport never drains
        #   stderr during the read loop, so a verbose server (legis/loomweave log there) that fills the ~64KB
        #   OS pipe buffer before its initialize reply blocks on write(stderr) → readline() never returns →
        #   the deadline fires → false `absent` / false RED on every run. Diagnostic stderr is captured ONLY
        #   by the Phase-0 spike (Step 2), which drains it via communicate(); the gate uses bound_context/note.
        env={**os.environ, **env})
    try:
        def send(obj: dict) -> None:
            proc.stdin.write(json.dumps(obj) + "\n"); proc.stdin.flush()
        send({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
            "protocolVersion": "2025-06-18", "capabilities": {},
            "clientInfo": {"name": "lacuna-tour", "version": "1"}}})
        init = _recv_result(proc.stdout, 1, deadline)   # correlate by id; skip notifications
        send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        send({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        tools = _recv_result(proc.stdout, 2, deadline)
        binding_raw: dict | None = None
        if binding is not None:                         # self-report members only
            binding_name, binding_args = binding        # repo-per-call members (warpline) carry {"repo": ROOT};
            send({"jsonrpc": "2.0", "id": 3, "method": "tools/call",   #   launch/cwd-bound members carry {}
                  "params": {"name": binding_name, "arguments": binding_args}})
            binding_raw = _recv_result(proc.stdout, 3, deadline)
        if init is None or tools is None or (binding is not None and binding_raw is None):
            raise TimeoutError(f"probe timed out after {timeout}s")   # hung: fail FAST, do not hang verify
        return init, tools, binding_raw
    finally:
        _teardown(proc)                                 # always reap the child — return, timeout, OR exception


def _sse_parse(raw: bytes) -> list[dict]:
    """Minimal SSE parser: extract data: lines, parse each as JSON-RPC.

    filigree returns Content-Type: text/event-stream. Each MCP response is one
    'event: message\\ndata: <JSON>\\n\\n' block. We iterate lines, strip 'data: '
    prefix, and json.loads each. Unknown event types are discarded."""
    results = []
    for line in raw.decode("utf-8", errors="replace").split("\n"):
        line = line.rstrip("\r")
        if line.startswith("data:"):
            payload = line[5:].strip()
            if payload and payload != "[DONE]":
                try:
                    results.append(json.loads(payload))
                except json.JSONDecodeError:
                    pass
    return results


def _http_rpc(url, headers, *, timeout: float,
              binding: tuple[str, dict] | None = None) -> tuple[dict, dict, dict | None]:
    """streamable-http wire transport (filigree). Same contract as _stdio_rpc, over
    urllib: POST initialize, then tools/list, then the optional binding call, parsing the
    response framing (SSE `data:` lines + echoing the Mcp-Session-Id response header on
    the follow-ups) exactly as Phase-0 Step 3 determines. Each urlopen passes the
    remaining budget as timeout= so it cannot hang. Returns (init, tools, binding|None).

    CRITICAL: the POST MUST send Accept: application/json, text/event-stream — omitting
    it returns HTTP 406 (the primary silent failure mode for this transport).
    STATELESS: filigree returns no Mcp-Session-Id; capture defensively and echo if present."""
    deadline = time.monotonic() + timeout

    base_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        **headers,
    }

    def _post(body: dict, extra_headers: dict | None = None) -> tuple[dict, dict]:
        """POST body, parse SSE response. Returns (first_jsonrpc_msg, resp_headers)."""
        h = {**base_headers, **(extra_headers or {})}
        data = json.dumps(body).encode()
        req = urllib.request.Request(url, data=data, method="POST")
        for k, v in h.items():
            req.add_header(k, v)
        remaining = deadline - time.monotonic()
        with urllib.request.urlopen(req, timeout=max(1.0, remaining)) as resp:
            raw = resp.read()
            resp_headers = dict(resp.headers)
        messages = _sse_parse(raw)
        msg = messages[0] if messages else {}
        return msg, resp_headers

    # 1. initialize
    init, init_hdrs = _post({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
        "protocolVersion": "2025-06-18", "capabilities": {},
        "clientInfo": {"name": "lacuna-tour", "version": "1"}}})

    # Capture Mcp-Session-Id defensively; echo on follow-ups (filigree is stateless
    # today but future-proofed per the Phase-0 finding)
    session_id = init_hdrs.get("Mcp-Session-Id") or init_hdrs.get("mcp-session-id")
    follow_extra: dict[str, str] = {}
    if session_id:
        follow_extra["Mcp-Session-Id"] = session_id

    # 2. tools/list (skip notifications/initialized — filigree SSE is stateless)
    tools, _ = _post({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
                     extra_headers=follow_extra)

    # 3. binding call (optional)
    binding_raw: dict | None = None
    if binding is not None:
        binding_name, binding_args = binding
        binding_raw, _ = _post(
            {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
             "params": {"name": binding_name, "arguments": binding_args}},
            extra_headers=follow_extra)

    # Defensive: _post returns {} (not None) on an empty SSE body, so this guard is a
    # belt-and-braces mirror of the stdio path — urlopen itself raises on timeout/transport
    # error (folded by probe()), so an empty {} reply surfaces here as a missing "result".
    if init is None or tools is None or (binding is not None and binding_raw is None):
        raise TimeoutError(f"http probe timed out after {timeout}s")

    return init, tools, binding_raw


# ── Per-member binding interpreters ──────────────────────────────────────────

def _interpret_binding(name: str, binding_raw: dict | None) -> tuple[bool, str]:
    """Extract (bound_repo_ok, bound_context) from the raw binding RPC response per the
    canonical per-member contract (phase0-findings.md). Returns (False, "handshake-failed")
    on any missing/null field — never raises. Uses .get() chains throughout so a
    partially-absent store reply yields live-empty (not an exception → absent)."""
    if binding_raw is None:
        return False, "handshake-failed"

    result = binding_raw.get("result") or {}

    if name == "loomweave":
        # Shape 2: content[0].text → JSON → result.* (nested under "result" key)
        # binding_raw["result"]["content"][0]["text"] → JSON → ["result"]["project_root"]
        content = result.get("content") or []
        text = content[0].get("text", "") if content else ""
        try:
            parsed = json.loads(text)
        except (json.JSONDecodeError, ValueError):
            return False, "handshake-failed"
        inner = parsed.get("result") or {}
        project_root = inner.get("project_root")
        db_present = inner.get("db_present")
        db_identity = inner.get("db_identity") or {}
        data_version = db_identity.get("data_version")
        path_ok = project_root == str(ROOT)
        store_ok = db_present is True and data_version is not None
        if path_ok and store_ok:
            return True, str(project_root)
        return False, str(project_root) if project_root else "handshake-failed"

    elif name == "filigree":
        # Shape 1: content[0].text → JSON → top-level keys (NOT nested under result)
        content = result.get("content") or []
        text = content[0].get("text", "") if content else ""
        try:
            parsed = json.loads(text)
        except (json.JSONDecodeError, ValueError):
            return False, "handshake-failed"
        project_root = parsed.get("project_root")
        db_initialized = parsed.get("db_initialized")
        schema_compatible = parsed.get("schema_compatible")
        path_ok = project_root == str(ROOT)
        store_ok = db_initialized is True and schema_compatible is True
        if path_ok and store_ok:
            return True, str(project_root)
        return False, str(project_root) if project_root else "handshake-failed"

    elif name == "legis":
        # Shape 3: structuredContent.checks (list), find by id
        sc = result.get("structuredContent") or {}
        checks = sc.get("checks") or []
        checks_by_id = {c.get("id"): c for c in checks}
        # Path: runtime.policy_cells.message startswith ROOT
        pc = checks_by_id.get("runtime.policy_cells") or {}
        pc_message = pc.get("message") or ""
        path_ok = pc_message.startswith(str(ROOT))
        # Store-read: store.binding_chain and store.governance_chain both "ok"
        bc = checks_by_id.get("store.binding_chain") or {}
        gc = checks_by_id.get("store.governance_chain") or {}
        store_ok = bc.get("status") == "ok" and gc.get("status") == "ok"
        if path_ok and store_ok:
            return True, pc_message
        return False, pc_message if pc_message else "handshake-failed"

    elif name == "wardline":
        # Shape 3: structuredContent.repo_binding
        sc = result.get("structuredContent") or {}
        rb = sc.get("repo_binding") or {}
        binding_ok = rb.get("binding_ok")
        store = rb.get("store") or {}
        schema_version = store.get("schema_version")
        if binding_ok is True and schema_version is not None:
            return True, f"binding_ok=True schema_version={schema_version}"
        return False, f"binding_ok={binding_ok} schema_version={schema_version}"

    elif name == "warpline":
        # Shape 3: structuredContent.data
        sc = result.get("structuredContent") or {}
        data = sc.get("data") or {}
        binding_ok = data.get("binding_ok")
        store = data.get("store") or {}
        schema_version = store.get("schema_version")
        if binding_ok is True and schema_version is not None:
            return True, f"binding_ok=True schema_version={schema_version}"
        return False, f"binding_ok={binding_ok} schema_version={schema_version}"

    elif name == "plainweave":
        # Shape 3: structuredContent.data
        sc = result.get("structuredContent") or {}
        data = sc.get("data") or {}
        db_path = data.get("db_path") or ""
        initialized = data.get("initialized")
        schema_version = data.get("schema_version")
        path_ok = db_path.startswith(str(ROOT))
        store_ok = initialized is True and schema_version is not None
        if path_ok and store_ok:
            return True, db_path
        return False, db_path if db_path else "handshake-failed"

    else:
        # Unknown member — cannot interpret; classify live-empty
        return False, f"unknown-member:{name}"


# ── probe() — the public seam ─────────────────────────────────────────────────

def probe(spec, *, timeout: float = 8) -> AttachResult:
    """INVARIANT (D09): returns an AttachResult for EVERY spec and NEVER raises. A
    missing binary (FileNotFoundError at subprocess.Popen), a broken pipe on send, or
    malformed JSON on recv is caught here and folded into an `absent` result — so one
    un-spawnable member cannot abort the probe sweep over the other 5 with an unhandled
    exception. The token is redacted out of the captured error."""
    try:
        if spec.transport == "streamable-http":
            return _http_probe(spec, timeout)      # urllib + SSE per Phase-0 Step 3
        return _stdio_probe(spec, timeout)
    except FileNotFoundError as e:                  # D18: the *-mcp BINARY is not installed — NOT a de-attach.
        # capability.detect() marks warpline/plainweave live by their CLI name, but .mcp.json spawns the
        # SEPARATE warpline-mcp/plainweave-mcp binaries; a missing one must read "not installed" (install it),
        # not a silent de-attach (investigate the regression). bound_context carries the stable diagnostic.
        return AttachResult(
            spec.name, attached=False, bound=False,
            liveness=classify(initialized=False, bound_repo_ok=False, gated=False, errored=True),
            bound_context="not-installed", error=redact(str(e))[:200])
    except Exception as e:                          # D18: the command RAN but the handshake FAILED (broken pipe /
        # malformed JSON / timeout after spawn) → a de-attach (the 2026-06-26 loomweave class). NEVER propagate.
        return AttachResult(
            spec.name, attached=False, bound=False,
            liveness=classify(initialized=False, bound_repo_ok=False, gated=False, errored=True),
            bound_context="handshake-failed", error=redact(str(e))[:200])


def _http_probe(spec, timeout: float) -> AttachResult:
    """R5: probe()'s http interpreter — filigree only. The wire detail (SSE framing,
    Mcp-Session-Id round-trip) lives in _http_rpc; this reads the binding field per the
    contract: the mcp_status_get SERVER-resolved project_root (NEVER the ?project=lacuna
    URL query the client set), unwrapped from content[0].text (top-level). Same
    never-raises contract — probe()'s except folds any failure into `absent`."""
    init, tools, binding_raw = _http_rpc(spec.url, spec.headers, timeout=timeout,
                                         binding=("mcp_status_get", {}))   # filigree: URL-bound, no repo arg
    initialized = "result" in init
    bound_repo_ok, bound_context = _interpret_binding(spec.name, binding_raw)
    return AttachResult(
        spec.name, attached=initialized, bound=bound_repo_ok,
        liveness=classify(initialized=initialized, bound_repo_ok=bound_repo_ok,
                          gated=False, errored=False),
        bound_context=bound_context, error=None)


def _stdio_probe(spec, timeout: float) -> AttachResult:
    """probe()'s stdio interpreter — calls the wire transport, then reads the binding field per
    the module-docstring contract. Thin: the wire (spawn / deadline-bounded reads / teardown)
    lives in _stdio_rpc; the per-member binding interpretation lives in _interpret_binding."""
    init, tools, binding_raw = _stdio_rpc(             # one wire call (TimeoutError/FileNotFoundError → probe except)
        spec.command, spec.args, spec.env, timeout=timeout,
        binding=_STDIO_BINDING.get(spec.name))
    initialized = "result" in init
    bound_repo_ok, bound_context = _interpret_binding(spec.name, binding_raw)
    return AttachResult(
        spec.name, attached=initialized, bound=bound_repo_ok,
        liveness=classify(initialized=initialized, bound_repo_ok=bound_repo_ok,
                          gated=False, errored=False),
        bound_context=bound_context, error=None)
