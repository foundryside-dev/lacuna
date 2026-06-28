# 6-Member MCP-Attachment Regression-Harness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a deterministic `make verify` gate that spawns each of the 6 federation MCP servers the way `.mcp.json` configures them, asserts each completes an MCP `initialize` handshake **and binds to the staged Lacuna repo**, so a silent member de-attachment (the 2026-06-26 loomweave incident) trips the gate instead of going unnoticed.

**Architecture:** The tour drives every tool by CLI subprocess (`tour/steps.py::_run`) and never exercises MCP *attachment* — which is exactly why the loomweave de-attach was invisible to `make verify`. This plan adds `tour/mcp_attachment.py` (parse the gitignored `.mcp.json` → per-server spawn-and-probe → per-member attach evidence) and a new tour leg `steps.mcp_attachment()` that surfaces one `mcp-attach-<member>` capability lacuna per attached+bound member. A member whose CLI is installed (so `capability.detect()` marks it live) but whose MCP server fails to attach is **not** surfaced → its lacuna is missing → `verify` fails, naming the member. Honest-degrade (G3) holds: a token is surfaced only for a member that genuinely attached and bound. A later, non-gating phase adds the cross-tool **join census** with liveness classes (PDR-0009).

**Tech Stack:** Python 3.12 (stdlib `subprocess`, `json`, `urllib`, `pathlib`, `tomllib`), the tour harness (`tour/{steps,capability,manifest,report,__main__}.py`), a **hand-rolled minimal JSON-RPC-over-stdio MCP client** (the official `mcp` SDK is NOT importable in `.venv` — confirmed; adding it is the documented alternative), `pytest`.

## Global Constraints

_Every task's requirements implicitly include these._

- **Determinism — `make verify` is byte-for-byte.** A leg's `detail` (rendered into `docs/tour.md`) MUST be **frozen prose**; `surfaced` carries only stable `(token, member)` pairs; any live/variable evidence (bound-context strings, counts, timestamps) goes in the `note` field, which is printed to stdout but **never** rendered into the locked markdown. Mirror `steps.warpline_change_impact()`'s determinism discipline.
- **Secrets.** `.mcp.json` is gitignored and carries a **live Filigree Bearer token** in the `filigree` streamable-http `headers.Authorization`. NEVER echo, log, persist, or commit it. Redact `Authorization` (case-insensitive) → `Bearer <redacted>` in every returned, printed, or persisted structure. The live-evidence dump lives under `.weft/mcp-attachment/` (already gitignored — `.gitignore:29` `.weft/`).
- **Clean-tree commits.** A dirty working tree flips `legis govern` to `[WARN]` and trips `verify` (the [[lacuna-green-tour-constraints]] property). Commit or stash between any `make tour` regen and `make verify`; regenerate `docs/{tour,matrix}.md` on a clean tree.
- **Identity.** Commits are authored as tachyon-beep (the configured `git user.email`). Do NOT run `gh auth` or change `git config user.*` ([[gh-active-account-do-not-switch]]).
- **Honest-degrade (G3).** Never surface a member's attach token unless it truly attached **and** bound to the staged repo. A genuinely unreachable member is labelled in `note`, never faked live.
- **Tool resolution.** Spawn each MCP server with the **`command` from `.mcp.json` verbatim** (it is an absolute path, e.g. `/home/john/.local/bin/warpline-mcp`); stdio servers spawn with `cwd=ROOT` and `env={**os.environ, **spec.env}`. The BIN-first `capability._locate` resolution (`~/.local/bin` may be off a subagent's `$PATH`) applies to `capability.detect()` CLI-availability detection — which ARMS the gate — NOT to the MCP spawn.
- **No heavy deps by default.** Use the stdlib hand-rolled stdio client. Task 0 confirms feasibility; adding the `mcp` SDK to the project is the recorded fallback only if the hand-rolled client cannot complete `initialize`.

---

## File Structure

- **Create `tour/mcp_attachment.py`** — one responsibility: turn `.mcp.json` into per-member attach evidence. Holds `ServerSpec` + `load_server_specs()` (parse + redaction), the two replaceable wire-transport callables `_stdio_rpc()` / `_http_rpc()` (the MCP wire client — the **only** place the wire framing lives, so a transport/protocol swap is a one-call change; reused by the Phase-0 characterizer), `probe(spec) -> AttachResult` (interprets the binding contract), and `classify()` (raw outcome → liveness class). `probe` is the single mockable seam for the leg's tests.
- **Create `tests/test_mcp_attachment.py`** — deterministic unit tests (parsing, redaction, classification, leg surfaced-pair construction, the negative-gate coverage test). No live servers in unit tests.
- **Create `scripts/characterize_mcp_attachment.py`** — one-shot live evidence dump → `.weft/mcp-attachment/characterization.json` (gitignored). The Phase-0 spike harness; not run by `make verify`.
- **Modify `tour/steps.py`** — add `mcp_attachment()` leg (frozen detail, surfaced pairs, live note), with `probe` as the monkeypatchable seam.
- **Modify `tour/__main__.py::_drive()`** — register `steps.mcp_attachment()` in the results list.
- **Modify `tour/lacunae.toml`** — add 6 `mcp-attach-<member>` capability entries.
- **Modify `docs/tour.md` + `docs/matrix.md`** — regenerated in lockstep via `make tour` (Task 7).

---

## Phase 0 — Feasibility spike (exploratory; DoD = captured evidence + a decision)

> The MCP stdio `initialize` handshake from a plain subprocess is the load-bearing unknown. **Do not write the probe in Phase 2 before this proves the mechanism.** This task is a spike: its DoD is captured evidence and a recorded decision, not a frozen assertion.

### Task 0: Prove the handshake mechanism for one stdio + the http server

**Files:**
- Create: `scripts/characterize_mcp_attachment.py`

- [ ] **Step 1: Confirm the SDK posture.** Run `.venv/bin/python -c "import mcp"` → expected `ModuleNotFoundError` (already observed). Records that the client is hand-rolled.

- [ ] **Step 2: Hand-roll a minimal stdio JSON-RPC exchange against ONE stdio server (loomweave).** MCP stdio transport is newline-delimited JSON-RPC on the child's stdin/stdout (logs go to stderr). Sketch:

```python
import json, subprocess, os
from pathlib import Path
ROOT = Path("/home/john/lacuna")

def stdio_probe(command, args, env):
    proc = subprocess.Popen(
        [command, *args], cwd=ROOT, text=True,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        env={**os.environ, **env},
    )
    def send(obj): proc.stdin.write(json.dumps(obj) + "\n"); proc.stdin.flush()
    def recv(want_id):                             # correlate by id; skip interleaved notifications
        while True:
            msg = json.loads(proc.stdout.readline())
            if msg.get("id") == want_id:           # the response to OUR request
                return msg
            # else: a notification (no "id" field) MCP servers may interleave
            # (progress/log) — discard and keep reading; a bare one-readline()
            # would mis-parse it as the result and KeyError on missing result/id.
    send({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
        "protocolVersion": "2025-06-18",
        "capabilities": {}, "clientInfo": {"name": "lacuna-tour", "version": "1"}}})
    init = recv(1)
    send({"jsonrpc": "2.0", "method": "notifications/initialized"})
    send({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    tools = recv(2)
    proc.stdin.close()
    proc.terminate()
    # stderr is the PRIMARY diagnostic when a server fails to start or rejects the
    # handshake (loomweave + legis log startup diagnostics there) — CAPTURE it, do
    # not discard it. communicate() drains stdout+stderr so a full stderr pipe can't
    # deadlock the recv() reads above; keep only a truncated, token-redacted tail.
    _out, stderr = proc.communicate(timeout=5)
    return init, tools, stderr[-2000:]
```

  Run it against loomweave (`~/.local/bin/loomweave serve`). Capture the `initialize` result and whether `tools/list` returns `mcp__loomweave__*` tools. **Record the real protocolVersion the server echoes** — adjust the client's requested version to match if it rejects. **Include the captured (truncated-tail, token-redacted) `stderr` for every probed server in the `.weft/mcp-attachment/characterization.json` evidence dump** — it is the primary diagnostic when a server fails to start or rejects the handshake (loomweave + legis log their startup diagnostics there), so a discarded `stderr` would leave a Phase-0 failure undiagnosable. Run the redaction (`Authorization` → `Bearer <redacted>`, case-insensitive) over the `stderr` tail before it is written.

- [ ] **Step 3: Prove the http transport (filigree) and determine its EXACT `initialize` response framing.** `filigree` is `streamable-http` at `http://localhost:8749/mcp/?project=lacuna` with an `Authorization` header. **Precondition:** :8749 must be live — but `filigree_work_cycle()` (`tour/steps.py`, `FILIGREE_BASE = http://localhost:8749`, via `_filigree_api`) already requires it, so this introduces **no new service requirement**, only the new MCP-framing requirement. Do a minimal `urllib` POST of the `initialize` JSON-RPC to the URL with the header and **record the exact `Content-Type` the server returns**. The MCP streamable-http transport commonly replies with `Content-Type: text/event-stream` — Server-Sent-Events framing (one or more `data:` lines carrying the JSON-RPC body) plus an `Mcp-Session-Id` response header — which a plain `urllib` POST that does `json.loads(resp.read())` will **not** parse. Capture which framing filigree actually uses. **If `text/event-stream`:** the probe MUST include a minimal stdlib SSE parser (a few lines — read the body, take each `data:` line, strip the `data:` prefix, `json.loads` the reassembled payload) **and** echo the returned `Mcp-Session-Id` back as a request header on the follow-up binding call (`mcp_status_get`) — without that session-id round-trip the server rejects the post-`initialize` call and the binding evidence the gate depends on cannot be read. A REST/health `GET` of filigree's `/api` surface is **NOT** an acceptable gate-equivalent fallback: the REST route (`/api`) and the MCP route (`/mcp/`) are **independent failure surfaces**, and the loomweave-class silent de-attach lives on the MCP route — the gate MUST exercise the MCP `initialize` + `mcp_status_get` handshake, not a liveness ping on the REST surface. **Redact the token in anything printed/saved.**

- [ ] **Step 3a: Reproduce or rule out the legis crash-on-init.** legis spawns stdio as `legis mcp --agent-id codex` with `env={"LEGIS_WARDLINE_CELL": "surface_override"}`. Its governance-read path has a documented failure — `posture_get`/`policy_list` throw `INTERNAL_ERROR: no such table: audit_log` when the binding-ledger DB is un-provisioned ([[legis-mcp-governance-read-crash]]; the prior plan `docs/plans/2026-06-25-mcp-attachment-truth-harness.md` flags it "reproduce the crash-on-init" and left it unresolved). The crash is on `posture_get`/`policy_list`, **not** on `initialize` itself, and the binding contract (Step 4) reads `doctor_get` — so drive the hand-rolled stdio client through `initialize` + `tools/list` **and the binding call `doctor_get`**, and capture whether `doctor_get` answers cleanly or hits the same un-provisioned-ledger crash. Record the result as Phase-0 evidence and decide BEFORE Phase 2 commits to it: provision the ledger (`LEGIS_HMAC_KEY` + init), keep `doctor_get` if it is on the safe side, or degrade legis to liveness + static lint per Step 5. Do NOT carry a known-crashing call into the gate.

- [ ] **Step 3b: Characterize wardline's handshake without the :9730 companion, and record the spawn-ordering decision.** wardline spawns as `wardline mcp --root . --loomweave-url http://127.0.0.1:9730 --filigree-url http://127.0.0.1:8749/...`. Its `--loomweave-url` points at a loomweave **HTTP** service at :9730, but loomweave's own `.mcp.json` entry attaches over **stdio** (`args=["serve"]`) — so whether anything is listening at :9730 during `make verify` is an **open question to characterize, not an asserted fact**. Probe wardline's `initialize` + `tools/list` + the binding-touching `doctor` call with **no** loomweave HTTP service running at :9730, and capture whether the handshake and binding-lint still succeed (the companion URL may be lazy/optional) or block/hang/error. Record the spawn-ordering decision: if wardline genuinely needs :9730 live, document how the leg sequences it (or that wardline degrades gracefully when it is absent), and set `probe`'s timeout so a missing companion fails **fast**, not hangs. **LIVE-CONFIRMED 2026-06-28:** wardline's `doctor` `repo_binding` reads the LOCAL baseline store (`schema_version`=1, `baseline_finding_count`=44), so the BINDING fact is INDEPENDENT of :9730 (which serves wardline's emit/scan, not the binding read) — `binding_ok=true` returned with the lacuna baseline present. When re-capturing in Phase 0, bring :9730 explicitly DOWN and record its state alongside the binding evidence.

- [ ] **Step 3c: Capture the two SEPARATE-binary stdio servers — `warpline-mcp` and `plainweave-mcp`.** These are distinct binaries from the `warpline`/`plainweave` CLIs the rest of the tour drives (`.mcp.json`: `command=/home/john/.local/bin/warpline-mcp` and `.../plainweave-mcp`, both `args=[]`, `type=stdio`), so Step 2's loomweave probe does **not** cover them. Drive each through `initialize` + `tools/list` + its binding call — plainweave self-report `plainweave_project_context_get` → `data["db_path"]` under `str(ROOT)`; warpline-mcp `initialize`/`tools/list` + its self-report `warpline_project_status_get` with `{"repo": str(ROOT)}` (R1 CONFIRMED LIVE → `structuredContent.data.binding_ok` + `.data.store.schema_version`, replacing the tautological `cwd == ROOT` lint). Capture both handshakes; if either binary is missing or its `initialize` fails, record the failing evidence and the fallback (per Step 5) BEFORE Phase 2.

- [ ] **Step 4: Capture binding evidence for ALL SIX members and define the contract.** For every member (loomweave, filigree, wardline, legis, warpline, plainweave) capture how it proves it bound to the staged repo, and assemble the **binding evidence contract** — one row per member: member → the binding-touching MCP call → the response field → the predicate compared against `str(ROOT)`. **All six members self-report** a server-resolved store-read fact — the 4 with existing tools, plus wardline + warpline via NEW tools (R1 CONFIRMED LIVE 2026-06-28; the old tautological static lint is removed):
  - **self-report (the 4 with existing tools)** — a per-member MCP call returns a *server-resolved* path: loomweave `project_status_get` → `result["project_root"]`; filigree `mcp_status_get` → `["project_root"]` (the server's own resolved root — **NOT** the `?project=lacuna` URL query the client itself put in the URL, which always echoes True even against the wrong project); plainweave `plainweave_project_context_get` → `data["db_path"]` (under `str(ROOT)`); legis `doctor_get` → the `checks[id=="runtime.policy_cells"]["message"]` absolute path (under `str(ROOT)`) — read that specific field, **NOT** top-level `ok`, which is `false` on benign install/key warnings.
  - **wardline + warpline (NEW self-report — R1; CONFIRMED LIVE 2026-06-28).** These two originally had no root-reporting tool, so binding was a `.mcp.json` + spawn-`cwd` static lint — but `cwd == ROOT` is TAUTOLOGICAL (the probe spawns with `cwd=ROOT`, so it is `ROOT == ROOT`, always true), so it is replaced by store-read self-report tools, confirmed by spawning the fresh binaries: warpline → `warpline_project_status_get` (args `{"repo": str(ROOT)}`; read `structuredContent.data.binding_ok` + `.data.store.schema_version`); wardline → its `doctor` (args `{}`; read `structuredContent.repo_binding.binding_ok` + `.repo_binding.store.schema_version`). Assert `binding_ok==true` AND `store.schema_version is not null` (a store-read fact, never the path or the envelope `ok`). The tautological static lint is removed (degrade only to `tools/list`-only liveness per Step 5 if a tool is ever absent, never to the tautology).

  The full contract table (one canonical copy) is written into `tour/mcp_attachment.py`'s module docstring in Step 5.

- [ ] **Step 5: Decide and record.** Write the decision into `tour/mcp_attachment.py`'s module docstring (created next task): **(a)** hand-rolled stdio client viable; **(b)** http handled via urllib (+ SSE parse if needed); **(c)** fallback — the default for **every** member is a binding-touching call validated against `str(ROOT)` per the binding-evidence contract above. Degrading a member to a `tools/list`-only **liveness** check + static `.mcp.json` lint is permitted **only** with recorded Phase-0 evidence that the full binding-touching check is genuinely **impossible** for that member (not merely inconvenient — capture the failing call and the reason). A member left on liveness-only MUST be documented in `note` as catching process-**start** failures (the server spawns and answers `tools/list`) but **NOT** stale-**binding** failures — exactly the 2026-06-26 loomweave class, where the binary started cleanly (`initialize` + `tools/list` both succeeded) yet could not serve its binding, so a `tools/list`-only check would have passed it. Log the limitation in `note`. **Also write the canonical binding evidence contract table** (the all-6 table from Step 4: member → call/rule → field → predicate vs `str(ROOT)`) into that same docstring, and record the per-member **binding mode** (all self-report; wardline + warpline via the NEW tools, R1 CONFIRMED LIVE 2026-06-28) plus the **R1 resolution**: every member sets `bound_repo_ok` from a server-resolved store-read fact, so a member that initialises but fails its binding-touching call classifies `live-empty`, does NOT surface, and the gate fails loud naming it (no faked coverage). The tautological `cwd==ROOT` static lint for wardline/warpline is **removed** as the plan-of-record (interim-only); if a NEW tool cannot ship, that member degrades to `tools/list`-only liveness per (c) above — documented in `note` as not catching stale-binding — never to the tautology. The 2026-06-26 loomweave incident is a self-report member, so that regression stays fully caught. Dump raw evidence to `.weft/mcp-attachment/characterization.json` (gitignored, token-redacted).

**Definition of Done:**
- [ ] Captured a handshake result (`initialize` + `tools/list`) for **all six** servers in a clean run — loomweave (stdio), filigree (http), legis, wardline, warpline-mcp, plainweave-mcp — **or**, for any server that cannot complete the handshake, a recorded fallback decision **with the captured failing evidence** (the failing call + reason). No server is left un-probed: specifically legis's documented crash is reproduced or ruled out against the binding call `doctor_get` (Step 3a), wardline's :9730-companion dependency is characterized with the spawn-ordering decision recorded (Step 3b), and the two separate binaries `warpline-mcp` + `plainweave-mcp` each have a captured handshake or recorded fallback (Step 3c).
- [ ] **Binding evidence contract recorded** in `tour/mcp_attachment.py`'s module docstring — all six members (loomweave, filigree, wardline, legis, warpline, plainweave), each row: member → the binding-touching MCP call → the **request `arguments`** (repo-per-call members like warpline-mcp pass `{"repo": str(ROOT)}`; launch/cwd-bound members pass `{}`) → the response field → the predicate compared against `str(ROOT)`. No `etc.`; every row concrete and testable. **Record the tools/call result UNWRAP path per member** — MCP wraps a `tools/call` payload in `result.structuredContent`, NOT `result["project_root"]` directly (a server could instead use a `result.content[].text` JSON blob — Phase 0 records each). **CONFIRMED LIVE for the two R1 tools** (spawned fresh): warpline reads `structuredContent.data.binding_ok` + `.data.store.schema_version`; wardline reads `structuredContent.repo_binding.binding_ok` + `.repo_binding.store.schema_version` — and the envelope `ok` is call-success, never the verdict. Filigree's row reads the server-resolved `mcp_status_get` project state, never the `?project=lacuna` URL query the client set; legis's row reads the `runtime.policy_cells` check path, never top-level `ok`.
- [ ] **Per-member binding mode recorded** (all self-report; wardline + warpline via the NEW tools — R1 CONFIRMED LIVE) **and the R1 tautology resolved**: wardline/warpline no longer infer `bound` from the tautological `cwd==ROOT` static lint — they read a server-resolved store-read fact (`binding_ok` + `store.schema_version`), so a stale-but-running de-attach is caught for these two as well, not faked `bound=True`.
- [ ] **The recv() framing loop correlates responses by JSON-RPC `id`** (Phase 2 inherits this): every read loops until a message arrives whose `msg.get("id")` equals the expected request id, discarding/buffering notification messages (no `"id"` field — progress/log notifications MCP servers may interleave). A bare one-`readline()`-per-request would mis-parse an interleaved notification as the `initialize` result and fail the handshake non-deterministically mid-sequence (`KeyError` on missing `result`/`id`).
- [ ] Decision recorded; no token or non-repo absolute path in any committed artifact (the `.weft/` dump stays gitignored).

---

## DECISION GATE (after Phase 0)

- **Handshake viable** (stdio + http) → proceed to Phase 1+ as written.
- **A member needs the real SDK client** → either add `mcp` to the project (record as a dep decision) or degrade that member to liveness + static lint; either way `verify` still asserts the others fully. Do **not** fabricate handshake code the spike didn't prove.

Run **`/review-plan docs/plans/2026-06-26-mcp-attachment-regression-harness.md`** here — the reality reviewer must validate the handshake mechanism and the determinism bound before the gate task.

---

## Phase 1 — ServerSpec parser + redaction (atomic TDD)

### Task 1: `load_server_specs()` + `ServerSpec` + header redaction

**Files:**
- Create: `tour/mcp_attachment.py`
- Test: `tests/test_mcp_attachment.py`

**Interfaces:**
- Produces: `ServerSpec(name, transport, command, args, env, url, headers)`, `ServerSpec.redacted_headers() -> dict`, `load_server_specs(cfg_path: Path) -> dict[str, ServerSpec]`.

- [ ] **Step 1: Write the failing test** (handles the real 5-stdio + 1-streamable-http shapes):

```python
# tests/test_mcp_attachment.py
import json
from pathlib import Path
from tour.mcp_attachment import load_server_specs, ServerSpec

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
```

- [ ] **Step 2: Run test, verify it fails.** Run: `.venv/bin/python -m pytest tests/test_mcp_attachment.py::test_load_server_specs_parses_stdio_and_http_and_redacts -v` → `FAILED (ImportError: load_server_specs)`.

- [ ] **Step 3: Write minimal implementation:**

```python
# tour/mcp_attachment.py
"""Spawn each .mcp.json-configured MCP server, assert it attaches + binds to the
staged Lacuna repo. Client mechanism + per-member fallbacks recorded by Phase-0 spike.

MODULE BUNDLING (ADR-note) — parser (load_server_specs/ServerSpec) + probe (_stdio_rpc/
_http_rpc transports) + classify() are co-located in this ONE module because they share a
single seam (.mcp.json → attach evidence) with no external callers beyond steps.py; a
separate ADR file is not warranted. The join census (Phase 5) and/or the transports may
be extracted into their own modules later if they grow.

BINDING EVIDENCE CONTRACT — how each .mcp.json member proves it bound to str(ROOT)
(the canonical copy; Phase-0 Step 5 records it here). probe() sets AttachResult.bound
from the row's predicate; classify() consumes that boolean unchanged. R1: ALL six members
are self-report (a per-member MCP call returns a SERVER-resolved store-read fact); wardline +
warpline use NEW tools (R1 CONFIRMED LIVE 2026-06-28: warpline→structuredContent.data.*,
wardline→structuredContent.repo_binding.*), replacing a tautological cwd==ROOT static lint
that is removed. See the R1 note below the table.

  member      mode         binding evidence (MCP call / static rule)   field / predicate (vs str(ROOT))
  loomweave   self-report  project_status_get                         result["project_root"] == str(ROOT)
  filigree    self-report  mcp_status_get  (the SERVER-resolved        ["project_root"] == str(ROOT)
                           project_root, NOT the ?project=lacuna URL
                           query the client itself set — that echoes
                           True even when bound to the wrong project)
  plainweave  self-report  plainweave_project_context_get             data["db_path"] is under str(ROOT)
  legis       self-report  doctor_get  (read the named check, NOT      checks[id=="runtime.policy_cells"]
                           top-level "ok", which is false on benign      ["message"] path is under str(ROOT)
                           install/key warnings)
  wardline    self-report  doctor  args {}  (CONFIRMED LIVE — the      structuredContent.repo_binding.binding_ok
                           doctor.repo_binding block; resolved_root      ==true AND .repo_binding.store.schema_version
                           echoes the relative ".", so the STORE-READ    is not null  (a store-read fact, NOT the
                           schema fact, not the path, is the signal)     path; read repo_binding.*, NOT envelope ok)
  warpline    self-report  warpline_project_status_get  args            structuredContent.data.binding_ok==true AND
                           {"repo": str(ROOT)}  (CONFIRMED LIVE;         .data.store.schema_version is not null
                           schema warpline.project_status.v1)            (store-read; NEVER the repo arg / envelope ok)

UNWRAP (all rows): the "field" column names the LOGICAL binding field. The actual read goes
through result["structuredContent"] — a tools/call result is WRAPPED, never result[<field>]
directly, and never the envelope "ok" (call-success, not the verdict). CONFIRMED LIVE: warpline
under ["data"], wardline under ["repo_binding"]. For the 4 legacy members (loomweave / filigree /
plainweave / legis) the exact wrapper KEY is Phase-0-confirmed (Step 3/4); the logical paths
above (project_root / db_path / runtime.policy_cells message) are read from inside
structuredContent. So the table rows and the _stdio_probe/_http_probe impl comments agree: the
logical field is canonical; structuredContent is the wrapper.

R1 (RESOLVED — CONFIRMED LIVE 2026-06-28). wardline and warpline originally had NO root-
reporting tool, so binding was inferred from a `.mcp.json` + spawn-cwd static lint
(`cwd == str(ROOT)`). That predicate is TAUTOLOGICAL — _stdio_rpc spawns every server with
cwd=ROOT, so `cwd == ROOT` is `ROOT == ROOT`, always true: both members would report bound=True
the instant they spawned, leaving the gate BLIND to a stale-but-running de-attach for 2 of 6
members. FIX: both servers now SELF-REPORT a store-read binding fact — shipped, reinstalled,
and CONFIRMED by spawning the fresh binaries the harness's own way (a subprocess, not this
session's MCP connection):
  - warpline `warpline_project_status_get` (schema warpline.project_status.v1), called with
    {"repo": str(ROOT)} → read `structuredContent.data.binding_ok` (verdict; live=true) and
    `structuredContent.data.store.schema_version` (live=4). Also `.data.store_status` ∈
    {ok, store_absent, store_unreadable, schema_ahead} and `.data.resolved_root`.
  - wardline `doctor` (args {}) → read `structuredContent.repo_binding.binding_ok` (live=true)
    and `structuredContent.repo_binding.store.schema_version` (live=1). wardline's
    `repo_binding.resolved_root` echoes the relative "." (not a server-resolved path) — exactly
    why the store-read schema fact, NOT the path, is the signal; and on an ABSENT baseline
    wardline keeps the doctor/envelope `ok` true by design (not-noisy), so the harness MUST
    assert BOTH `binding_ok==true` AND `schema_version is not null` (the schema-null arm catches
    absent/unreadable), reading `repo_binding.*`, never the envelope `ok`.
For BOTH the facts live under `result.structuredContent` (warpline `.data.*`, wardline
top-level `.repo_binding.*`) — never top-level `result`, never a `content[].text` blob; the
envelope `ok` is call-success, not the verdict. The tautological static-lint is REMOVED. The
harness asserts `binding_ok==true AND schema_version is not null` — a fact read from INSIDE each
member's repo-scoped store, catching the loomweave-class stale-binary-can't-read-store failure
for these two as well.

For self-report members probe() sets bound_repo_ok from the contract field, so a member that
initialises but fails its binding-touching call classifies live-empty and does NOT surface —
the gate then fails loud naming it, rather than faking coverage. The 2026-06-26 loomweave
incident is a self-report member, so that regression stays fully caught.

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
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path("/home/john/lacuna")

@dataclass(frozen=True)
class ServerSpec:
    name: str
    transport: str                      # "stdio" | "streamable-http"
    command: str | None = None
    args: tuple[str, ...] = ()
    env: dict[str, str] = field(default_factory=dict)
    url: str | None = None
    headers: dict[str, str] = field(default_factory=dict)

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
```

- [ ] **Step 4: Run test, verify it passes.** Run the same command → `PASSED`.

- [ ] **Step 5: Commit.**

```bash
git add tour/mcp_attachment.py tests/test_mcp_attachment.py
git commit -m "feat(tour): mcp_attachment ServerSpec parser + Authorization redaction

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

**Definition of Done:** parser test passes; the raw token never appears in any returned/emitted structure; `.venv/bin/python -m pytest -q` still green.

---

## Phase 2 — The probe + liveness classification (spike-built; TDD the deterministic parts)

### Task 2: `probe(spec) -> AttachResult` and `classify()`

> The live spawn is built on Phase 0's proven mechanism (captured-evidence DoD). The **classification** (raw outcome → liveness class + attached/bound booleans) is pure and fully TDD'd.

**Files:**
- Modify: `tour/mcp_attachment.py`
- Test: `tests/test_mcp_attachment.py`

**Interfaces:**
- Produces: `AttachResult(member, attached: bool, bound: bool, liveness: str, bound_context: str, error: str | None)` where `liveness ∈ {"live-bound","live-empty","reachable-gated","absent"}`; `probe(spec, *, timeout=8) -> AttachResult` (a **short** per-server deadline for a local probe; `probe` MUST bound **every** blocking read by it — never a bare `readline()` — so a hung server fails fast, not forever; and MUST return an `AttachResult` for **every** spec and **never raise** — any spawn/send/recv failure folds into an `absent` result (D09); see Step 3); `classify(initialized: bool, bound_repo_ok: bool, gated: bool, errored: bool) -> str`.
- Wire transports (D10): `_stdio_rpc(command, args, env, *, timeout, binding=None)` and `_http_rpc(url, headers, *, timeout, binding=None)`, each returning `(initialize_raw, tools_list_raw, binding_raw | None)` — the **sole** wire boundary. `binding` is a `(tool_name, arguments)` pair or `None`: repo-per-call members (warpline-mcp — its `_repo_arg` rejects empty args) pass `{"repo": str(ROOT)}`, launch/cwd-bound members pass `{}`. The transport sends the args it is handed and does no `str(ROOT)` compare (`probe` interprets the response); `scripts/characterize_mcp_attachment.py` imports the same two.

- [ ] **Step 1: Write the failing tests — `classify` (pure), the `probe` deadline (fake hung Popen), and the `probe` never-raises invariant (D09; monkeypatched spawn that raises):**

```python
from tour.mcp_attachment import classify

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
```

  The deadline test pins D06 — a server that spawns but whose `readline()` never returns (the 2026-06-26 loomweave-class hang: process started, `initialize` may even answer, then stalls) MUST trip the per-server deadline and classify `absent` *within* the timeout, instead of hanging `make verify` forever. It is deterministic (a fake `Popen`, no live server). The lower time-bound **and** the teardown assertion are load-bearing: without them an instant binary-not-found early return would satisfy `absent`/`attached is False` and the test would go green without the deadline ever firing — pinning nothing.

```python
import time, threading
from tour import mcp_attachment as mod
from tour.mcp_attachment import probe, ServerSpec

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
```

  The never-raises test pins D06's sibling **D09** — `probe()` MUST return an `AttachResult` for *every* spec and **never propagate an exception**, so a single un-spawnable member (a missing binary → `FileNotFoundError` at `subprocess.Popen`) folds into an `absent` result instead of aborting the whole probe sweep. Deterministic (monkeypatched spawn, no live server); asserts the spawn failure is *captured* (redacted, length-bounded `error`), not raised:

```python
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
    from tour.mcp_attachment import redact
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
```

- [ ] **Step 2: Run → fail** (`ImportError: classify`; the deadline test fails on the missing `probe`).

- [ ] **Step 3: Implement `classify` (pure) + `probe` (live, spike-built).** `classify` is a small precedence function (gated wins over absent; bound wins over empty). `probe` spawns per `spec.transport` using the Phase-0 client and sets `bound_repo_ok` per the **binding evidence contract** (the module docstring's 6 rows): for self-report members by comparing the *server-resolved* path to `str(ROOT)` — loomweave `project_status_get.result["project_root"]`; filigree `mcp_status_get["project_root"]` (the server's resolved root, **NOT** the `?project=lacuna` URL query the client set) — reached over streamable-http by POSTing `initialize` then `mcp_status_get`, parsing the SSE `data:`-line framing and echoing the `Mcp-Session-Id` response header on the `mcp_status_get` request per the Phase-0 Step 3 finding; a REST/health `GET` of the `/api` surface is **not** a substitute for this MCP-route handshake; plainweave `plainweave_project_context_get.data["db_path"]` under `str(ROOT)`; legis `doctor_get`'s `runtime.policy_cells` check message under `str(ROOT)` (not top-level `ok`) — and for wardline + warpline via their NEW self-report tools (R1 CONFIRMED LIVE — warpline `warpline_project_status_get` with `{"repo": str(ROOT)}` → `structuredContent.data.binding_ok` + `.data.store.schema_version`; wardline `doctor` with `{}` → `structuredContent.repo_binding.binding_ok` + `.repo_binding.store.schema_version`; assert `binding_ok==true` AND `schema_version is not null`, a store-read fact, NOT the tautological `cwd==ROOT` nor the envelope `ok`) so a member that fails its binding call classifies `live-empty` and the gate fails naming it. `redact()` the token out of any `error`. Keep `probe` thin; all decisions flow through `classify` — this is a `probe`-internal change only, so `AttachResult`/`classify` signatures are unchanged.

  **Never-raises invariant (D09 — required, tested).** `probe()` MUST return an `AttachResult` for **every** spec and **never raise**. Wrap the whole spawn/send/recv exchange in try-except-finally: `subprocess.Popen` raises `FileNotFoundError` when a member binary is missing, `send` can hit a broken pipe, and `recv`/`json.loads` can hit malformed output — any of these must fold into an `absent` `AttachResult`, not propagate and abort the sweep over the other 5 members. **D18 — the fold splits the `absent` case so the operator can tell a never-installed `*-mcp` binary from a real de-attach.** `capability.detect()` marks `warpline`/`plainweave` live by their *CLI* name, but `.mcp.json` spawns the *separate* `warpline-mcp`/`plainweave-mcp` binaries, so "CLI live but the `*-mcp` binary not yet installed" would otherwise trip the gate **identically** to a de-attach regression. Catch `FileNotFoundError` (the binary is absent) **before** the generic `except` and set `bound_context="not-installed"`; the generic `except` (the command ran but the handshake failed — broken pipe / malformed JSON / timeout) sets `bound_context="handshake-failed"`. Both keep `liveness="absent"` (D06/D09 classification is unchanged) and carry a redacted, length-bounded `error`; the leg renders the `bound_context` diagnostic into `note` (variable data — never the frozen `detail`), so the operator installs vs investigates. The `except` lives on the `probe()` boundary (below); the `finally` (always `_teardown` the child) lives in `_stdio_rpc` (the wire transport). Tested by the monkeypatched-spawn (`not-installed`) and hung-server (`handshake-failed`) tests in Step 1.

  **Protocol-version tolerance (D19 — required).** The probe MUST tolerate MCP `protocolVersion` negotiation rather than hard-fail on a version bump. `initialized` is taken from **any non-error** `initialize` response (`"result" in init`, as `_stdio_probe` does above) — the `protocolVersion` the server **echoes back** is never compared, so a member that answers with an older *or* newer version is still `attached`. A member MUST NOT be classified `absent` merely because it bumped its protocol version (that would be a false de-attach — the inverse of the failure this gate exists to catch). If Phase-0 evidence shows a server instead **rejects** the requested `"2025-06-18"` with a JSON-RPC `error`, the probe retries `initialize` **once** with the older `"2024-11-05"` baseline before classifying; that retry lives in `_stdio_rpc`/`_http_rpc` (the wire boundary, D10), so it is a one-call change. (Phase 0 Step 2 records the exact version each server echoes; this runtime tolerance is the gate's standing behaviour, not a spike-only adjustment.)

  **Timeout enforcement (D06 — required, tested).** `probe` honours a short per-server deadline (`timeout=8`) on **every** blocking read. A bare `proc.stdout.readline()` has no deadline, so a server that spawns and answers `initialize` then stalls would hang `make verify` **forever** — the exact failure class this harness exists to catch. Bound each read with a reader thread joined to the *remaining* budget (`thread.join(timeout=…)`); on expiry, tear the server down and classify `absent` (`classify(initialized=False, bound_repo_ok=False, gated=False, errored=True)` → `"absent"`, matching Step 1's classify test). The `urllib` http path (filigree) passes the same remaining budget as `urlopen(…, timeout=…)` so it cannot hang either. `_teardown` is a **local** helper mirroring `tour/steps.py:1160` (terminate → `wait(timeout=5)` → kill); do **not** import `steps._teardown` (`steps` imports this module — circular). Complete mechanism:

```python
import os, re, subprocess, threading, time   # module-level in tour/mcp_attachment.py

_AUTH_RE = re.compile(r"(?i)(authorization\s*[:=]\s*)(bearer\s+)?\S+")

def redact(s: str) -> str:
    """R5: strip any Authorization/Bearer token from an ARBITRARY string (error messages,
    stderr tails) before it lands in AttachResult.error, is printed, or persisted. Distinct
    from ServerSpec.redacted_headers() (a headers-dict redactor); this sanitises free strings.
    Required — probe()'s except handlers call redact(str(e)); filigree is the only token-
    carrying member (its 401s can echo the header). Tested by test_redact_strips_authorization_token."""
    return _AUTH_RE.sub(lambda m: m.group(1) + "Bearer <redacted>", s)

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
        if not line:                               # None = deadline elapsed (hung); "" = EOF
            return None                            #   (server crashed/closed stdout) — both → None,
        msg = json.loads(line)                     #   so json.loads("") never raises (probe folds → absent)
        if msg.get("id") == want_id:               # the response to OUR request
            return msg
        # else: a notification (no "id") or a stale id — discard, keep reading

def _teardown(proc) -> None:                       # mirror tour/steps.py:1160 (local; no import of steps)
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()

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

# ── Wire-transport boundary (D10) ─────────────────────────────────────────────
# _stdio_rpc / _http_rpc are the ONLY place the MCP wire framing lives. Each completes
# the handshake (initialize id=1, notifications/initialized, tools/list id=2), issues the
# optional per-member `binding` call (id=3) on the SAME session, and returns the RAW
# JSON-RPC response dicts (init, tools/list, binding|None). Member-agnostic: they take
# raw command/args/env (or url/headers), never a ServerSpec, and do NO str(ROOT) compare
# — probe() interprets. Swapping the wire protocol (or moving to the official `mcp` SDK)
# is a one-call change here; scripts/characterize_mcp_attachment.py imports these SAME two
# callables instead of carrying its own copy. (`import os` is added at module level.)

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

def _http_rpc(url, headers, *, timeout: float,
              binding: tuple[str, dict] | None = None) -> tuple[dict, dict, dict | None]:
    """streamable-http wire transport (filigree). Same contract as _stdio_rpc, over
    urllib: POST initialize, then tools/list, then the optional binding call, parsing the
    response framing (SSE `data:` lines + echoing the Mcp-Session-Id response header on
    the follow-ups) EXACTLY as Phase-0 Step 3 determines — that framing is the spike's to
    fix, so it is built from the Phase-0 finding, not invented here. Each urlopen passes
    the remaining budget as timeout= so it cannot hang. Returns (init, tools, binding|None)."""
    ...   # built from the Phase-0 Step 3 framing finding (urllib + SSE + Mcp-Session-Id round-trip)

# R5: probe()'s http interpreter — mirrors _stdio_probe over _http_rpc (filigree only). The
# wire detail (SSE framing, Mcp-Session-Id round-trip) lives in _http_rpc; this reads the
# binding field per the contract: the mcp_status_get SERVER-resolved project_root (NEVER the
# ?project=lacuna URL query the client set), unwrapped from result["structuredContent"]
# (Phase-0 Step 3 confirms filigree's exact wrapper key) and compared to str(ROOT). Same
# never-raises contract — probe()'s except folds any failure into `absent`.
def _http_probe(spec, timeout: float) -> AttachResult:
    init, tools, binding_raw = _http_rpc(spec.url, spec.headers, timeout=timeout,
                                         binding=("mcp_status_get", {}))   # filigree: URL-bound, no repo arg
    initialized = "result" in init
    bound_repo_ok, bound_context = False, "phase-0-pending"   # PLACEHOLDER so the stub runs (no NameError);
    # ... Step 3 / Phase-0 fills these: bound_repo_ok = (binding_raw["result"]["structuredContent"][...]
    #     ["project_root"] == str(ROOT)); the exact structuredContent wrapper key is Phase-0-confirmed
    #     (Step 3); bound_context = that resolved root (or "handshake-failed" if the call did not answer) ...
    return AttachResult(
        spec.name, attached=initialized, bound=bound_repo_ok,
        liveness=classify(initialized=initialized, bound_repo_ok=bound_repo_ok,
                          gated=False, errored=False),
        bound_context=bound_context, error=None)

# probe()'s stdio interpreter — calls the wire transport, then reads the binding field per
# the module-docstring contract. Thin: the wire (spawn / deadline-bounded reads / teardown)
# lives in _stdio_rpc; the per-member binding interpretation lives here:
def _stdio_probe(spec, timeout: float) -> AttachResult:
    init, tools, binding_raw = _stdio_rpc(             # one wire call (TimeoutError/FileNotFoundError → probe except)
        spec.command, spec.args, spec.env, timeout=timeout,
        binding=_STDIO_BINDING.get(spec.name))
    initialized = "result" in init
    # bound_repo_ok + bound_context per the module-docstring contract. The MCP tools/call result
    #   is WRAPPED: read binding_raw["result"]["structuredContent"], NOT binding_raw["result"][...].
    #   loomweave project_root / plainweave db_path / legis runtime.policy_cells message resolved
    #   under str(ROOT); wardline + warpline (R1 CONFIRMED) read the store-read verdict
    #   structuredContent[K]["binding_ok"] AND structuredContent[K]["store"]["schema_version"] is
    #   not null — K = "data" for warpline, "repo_binding" for wardline (NOT the envelope "ok").
    bound_repo_ok, bound_context = False, "phase-0-pending"   # PLACEHOLDER so the stub runs (no NameError);
    # ... Step 3 sets bound_repo_ok + bound_context from the contract above; classify() consumes them ...
    return AttachResult(
        spec.name, attached=initialized, bound=bound_repo_ok,
        liveness=classify(initialized=initialized, bound_repo_ok=bound_repo_ok,
                          gated=False, errored=False),
        bound_context=bound_context, error=None)
```

**Transport boundary (D10 — required).** The MCP wire client MUST be extracted as the two replaceable callables above — `_stdio_rpc` and `_http_rpc` — each completing the handshake and returning the **raw** `initialize` + `tools/list` dicts (plus the optional per-member `binding` response, which rides the same session: stdio's single spawn, http's `Mcp-Session-Id`). They are the **only** place the wire framing lives and are **member-agnostic** (raw `command/args/env` or `url/headers`, never a `ServerSpec`, no `str(ROOT)` comparison); `probe()` picks the binding method and interprets the contract field, so a transport/protocol swap (or moving to the `mcp` SDK) is a **one-call change**. `scripts/characterize_mcp_attachment.py` (Phase 0) **imports these same two transports** instead of carrying its own copy. The monkeypatch test seam stays at `probe()` (the leg monkeypatches `mcp_attachment.probe`) — unchanged.

- [ ] **Step 4: Run → pass.** `classify` **and** the fake-hung-Popen deadline test green (both deterministic — no live server); `probe`'s live *binding* evidence is still exercised by the characterizer/spike, not asserted byte-exact (live).

- [ ] **Step 5: Commit** (`feat(tour): MCP attach probe + liveness classification`).

**Definition of Done:** `classify` fully tested; **`redact()` is tested to strip a real token (R5) — a no-op `return s` stub fails the test**; `probe` enforces the short per-server deadline on **every** blocking read (the fake-hung-Popen test returns `absent` *within* the timeout, proving a hung server fails fast rather than hanging `make verify` — D06); `probe` returns an `AttachResult` for **every** spec and **never raises** — the monkeypatched-spawn test proves a missing binary folds into a token-redacted `absent` result rather than propagating (D09); **`AttachResult`, `redact()`, `classify`, and `_http_probe` are all DEFINED in this module's code blocks (R5) — no referenced-but-undefined symbol blocks the TDD steps**; **once Phase-0 Step 3 fixes filigree's framing, `_http_rpc` has a fake-transport unit test (R8): a `Content-Type: text/event-stream` response with a `data:` JSON-RPC body + an `Mcp-Session-Id` header → assert the SSE body parses and the session-id is echoed on the follow-up request** (the http wire path otherwise has no deterministic test, unlike the fake-hung-Popen stdio path); `probe` returns an `AttachResult` for each of the 6 specs in a manual run, token-redacted; classification matches the spike evidence; **the R1 binding predicate is pinned (`test_probe_binding_predicate_requires_binding_ok_AND_schema_version`): `bound` requires `binding_ok==True` AND `schema_version is not None` — the absent-baseline arm (`binding_ok=True, schema_version=None`) classifies `live-empty`, not bound**; **D19 protocol-tolerance is pinned (`test_probe_tolerates_protocol_version_mismatch`): a server echoing a different `protocolVersion` stays `attached`, never false-RED `absent`**. **Once Phase-0 confirms each legacy member's exact `structuredContent` shape, extend the binding-predicate test per legacy stdio member (loomweave / plainweave / legis) — cheap pure tests mirroring the wardline/warpline one — so a dispatch bug is caught before live Phase-2 work.**

---

## Phase 3 — Tour leg + lacunae + wiring (atomic TDD on the deterministic parts)

### Task 3: Add 6 `mcp-attach-<member>` capability entries to `tour/lacunae.toml`

**Files:**
- Modify: `tour/lacunae.toml`
- Test: `tests/test_mcp_attachment.py`

- [ ] **Step 1: Write the failing test** (coverage credits an attached member, and a missing member trips it — the gate's core contract, pure):

```python
from pathlib import Path
from tour.manifest import load_manifest
from tour.report import coverage, StepResult

MANIFEST = Path("/home/john/lacuna/tour/lacunae.toml")

def test_mcp_attach_lacunae_match_surfaced_tokens_and_trip_on_miss():
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
```

- [ ] **Step 2: Run → fail** (`KeyError`/assertion: entries absent).

- [ ] **Step 3: Add the 6 entries** to `tour/lacunae.toml` (mirror the `wp-*` capability-demo shape; one per member). Template (repeat for `filigree`, `wardline`, `legis`, `warpline`, `plainweave`):

```toml
[[lacuna]]
id = "mcp-attach-loomweave"
file = ".mcp.json"
symbol = "loomweave"
category = "mcp-attachment"
demonstrates = ["loomweave"]
explanation = "NOT A FLAW — a federation seam-integrity demo. loomweave's .mcp.json-configured MCP server (`loomweave serve`) spawns, completes the MCP initialize handshake, and binds to the staged lacuna repo — reachable MCP-first, no CLI fallback. A silent de-attach (e.g. a stale build whose serve cannot open the index — the 2026-06-26 v10/v11 incident) makes this lacuna go dark and trips make verify."
expected_tool = "loomweave"
expected_rule = "mcp-attach"
```

  (`symbol` = the member name; `coverage()` matches `("mcp-attach", "loomweave")` to `expected_rule="mcp-attach"` + `_symbol_matches("loomweave","loomweave")`. Distinct member names never cross-match.)

- [ ] **Step 3b: Update the hard-coded lacunae count (R4).** `tests/test_manifest.py::test_loads_all_lacunae` asserts `len(m.lacunae) == 52` (line 10) — adding 6 entries makes it **58**, so `make ci` fails immediately after this task unless updated in the SAME commit. Change `== 52` → `== 58` and add a membership assertion for the new ids:

```python
    assert {f"mcp-attach-{x}" for x in
            ("loomweave", "filigree", "wardline", "legis", "warpline", "plainweave")} <= ids
```

- [ ] **Step 4: Run → pass.**

- [ ] **Step 5: Commit** (`feat(tour): catalogue 6 mcp-attach-* capability lacunae`).

**Definition of Done:** all 6 entries load; coverage credits all-6-surfaced and marks a missing member's lacuna missing; **`tests/test_manifest.py`'s count assertion is updated 52 → 58 with a membership assert for the 6 new ids (R4), in the same commit, so `make ci` stays green.**

### Task 4: `steps.mcp_attachment()` leg + wire into `_drive()`

**Files:**
- Modify: `tour/steps.py` (add the leg), `tour/__main__.py` (register it)
- Test: `tests/test_mcp_attachment.py`

**Interfaces:**
- Consumes: `mcp_attachment.load_server_specs`, `mcp_attachment.probe` (the monkeypatchable seam).
- Produces: `steps.mcp_attachment() -> StepResult` surfacing `("mcp-attach", member)` for each `AttachResult.attached and .bound`.

- [ ] **Step 1: Write the failing test** (monkeypatch the probe seam → deterministic):

```python
from tour import steps
from tour import mcp_attachment as mod

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
```

- [ ] **Step 2: Run → fail** (`AttributeError: mcp_attachment`).

- [ ] **Step 3: Implement the leg** in `tour/steps.py` (frozen `detail`; live summary in `note`; never raises — tour contract):

```python
from tour import mcp_attachment as _mcp

# R2/D13: the frozen detail is ONE module constant so the happy path and the config-error
# path return BYTE-IDENTICAL detail — they must never drift, or lockstep breaks. Its value
# must equal the exact literal the determinism test asserts (Task 4 Step 1).
_MCP_ATTACH_DETAIL = (
    "all .mcp.json members reachable MCP-first and bound to the staged repo — "
    "federation seam integrity asserted; a silent de-attach trips this gate")

def mcp_attachment() -> StepResult:
    """Assert each .mcp.json member attaches MCP-first + binds to the staged repo.
    Frozen detail (lockstep); per-member liveness goes in `note` (not rendered).

    D13 — the narrative marker is DECOUPLED from the live probe. `ok` is FROZEN `True`,
    so this leg NEVER flaps the byte-compared `docs/tour.md` (`render_tour_md` renders
    `[PASS]`/`[WARN]` straight from `ok`). The attach gate runs SOLELY through the
    coverage check: a de-attached member drops from `surfaced`, its `mcp-attach-<member>`
    lacuna goes missing, and `make verify` fails naming it — mirroring
    `warpline_change_impact`, whose narrative never flaps. Were `ok` live instead, a
    transient probe failure would flip `[PASS]`→`[WARN]`, flag `docs/tour.md` "stale", and
    a developer's reflexive re-`make tour` + commit would bake a `[WARN]` baseline that
    PERMANENTLY encodes the degraded state (and the next clean run then fails the other
    way). The loud operator signal rides `note` (printed to stdout, NEVER rendered into
    the locked markdown): a failed member is flagged `ATTACH FAILED` there, not in the
    narrative."""
    name = "mcp attachment"
    try:
        specs = _mcp.load_server_specs()
        results = []
        for spec in specs.values():
            try:                                 # per-probe isolation: one member's failure
                results.append(_mcp.probe(spec)) #   must not discard the other five's results
            except Exception as e:               # defence-in-depth: probe() never raises (D09, tested), so this is
                #   dead unless a future change regresses that invariant. If it ever fires, "probe-raised" is a
                #   recognisable D18 diagnostic (not an empty string matching neither not-installed nor handshake-failed).
                results.append(_mcp.AttachResult(
                    member=spec.name, attached=False, bound=False,
                    liveness="absent", bound_context="probe-raised", error=_mcp.redact(str(e))[:200]))
    except Exception as e:                       # R2/D13: never raise (tour contract) AND never flip frozen `ok`.
        # .mcp.json is gitignored → load_server_specs() hits FileNotFoundError on a fresh clone. Returning
        # ok=False would flip the [PASS]/[WARN] marker and re-open the stale-baseline trap D13 closes. Keep `ok`
        # FROZEN True with surfaced=() so ALL 6 mcp-attach lacunae go missing → make verify fails loud naming
        # all 6, the cause in note — never via a stale narrative. (verify is owner-local-only; .mcp.json is
        # always present there, so this is the absent-config precondition, not normal operation.)
        return StepResult(
            name, ok=True, detail=_MCP_ATTACH_DETAIL, surfaced=(),
            note=f"mcp attachment unavailable (config/probe error): {_mcp.redact(str(e))[:200]}")
    surfaced = tuple(("mcp-attach", r.member) for r in results if r.attached and r.bound)
    # D13: `ok` is FROZEN True — the gate is the coverage check (surfaced → missing_ids),
    # never the byte-compared narrative. A de-attach drops the member from `surfaced` (so
    # `make verify` fails naming it) WITHOUT turning docs/tour.md stale, so no reflexive
    # re-`make tour` can bake a [WARN] baseline. The loud signal rides `note` (stdout, not
    # rendered): each failed member is flagged ATTACH FAILED so the operator still sees it.
    failed = sorted(r.member for r in results if not (r.attached and r.bound))
    # D18: within `absent`, distinguish a never-installed *-mcp binary (bound_context "not-installed")
    # from a real de-attach (bound_context "handshake-failed") so the operator installs vs investigates —
    # capability.detect() marks warpline/plainweave live by CLI name, but .mcp.json spawns the separate
    # warpline-mcp/plainweave-mcp binaries. The diagnostic is variable data → it rides `note` only, NEVER
    # the frozen `detail`.
    def _liveness_note(r) -> str:
        diag = f" ({r.bound_context})" if r.liveness == "absent" and r.bound_context else ""
        return f"{r.member}:{r.liveness}{diag}"
    note = "; ".join(_liveness_note(r) for r in sorted(results, key=lambda r: r.member))
    if failed:
        note = ("ATTACH FAILED: " + ", ".join(f"mcp-attach-{m}" for m in failed)
                + " — fix before running make tour; the coverage gate fails verify by name | "
                + note)
    return StepResult(
        name, ok=True,   # FROZEN — never flaps the narrative; the gate is the coverage check (D13)
        detail=_MCP_ATTACH_DETAIL,   # R2: same constant as the config-error path → byte-identical
        surfaced=surfaced, note=note)
```

  Then register it in `tour/__main__.py::_drive()` results (after `steps.plainweave_intent()`):

```python
        steps.plainweave_intent(),
        steps.mcp_attachment(),
```

- [ ] **Step 3b: Stub the leg in `tests/test_drive.py` (R6).** Two existing tests call the live `_drive()` to assert ordering: `test_drive_includes_the_legis_governance_step` (no monkeypatch today) and `test_drive_includes_the_plainweave_intent_step` (stubs only `plainweave_intent`). Once `mcp_attachment()` is in `_drive`, both would spawn all 6 live MCP probes — up to ~6×8s of dead wall-clock per `make ci` run for an ordering check. Stub it in BOTH (mirror the existing `plainweave_intent` stub at `test_drive.py:19-21`); add the `monkeypatch` fixture to the legis test:

```python
    monkeypatch.setattr(steps, "mcp_attachment",
                        lambda: StepResult("mcp attachment", ok=True, detail="stub"))
```

- [ ] **Step 4: Run → pass** (`.venv/bin/python -m pytest tests/test_mcp_attachment.py -v`).

- [ ] **Step 5: Commit** (`feat(tour): mcp_attachment leg surfaces attached members; wire into drive`).

**Definition of Done:** leg test green; full suite green; the leg never raises; `detail` is the `_MCP_ATTACH_DETAIL` constant — a fixed string independent of probe order/counts, returned **byte-identical on BOTH the happy path and the config-error path (R2)**; **`ok` is frozen `True` (D13/R2) on every path** so the rendered `[PASS]`/`[WARN]` marker never flaps — the attach gate runs solely through the coverage check, and a de-attach surfaces via `note` (stdout) + `make verify` failing by name, never via a stale doc; **`tests/test_drive.py` stubs the leg in both ordering tests so `make ci` does not spawn live probes (R6).** **The R2 config-error invariant is pinned (`test_mcp_attachment_leg_frozen_ok_on_missing_config`): a missing `.mcp.json` keeps `ok=True` / `detail==_MCP_ATTACH_DETAIL` / `surfaced==()` — the exact invariant that regressed in round 2.**

---

## Phase 4 — The verify gate + lockstep (clean-tree commit)

### Task 5: Regenerate the narrative and green the gate

**Files:**
- Modify: `docs/tour.md`, `docs/matrix.md` (regenerated)

- [ ] **Step 1: Pre-clean tree.** `git status --short` must be empty (Tasks 1–4 committed). A dirty tree flips `legis govern` → `[WARN]` and would bake into `tour.md`.
- [ ] **Step 2: Regenerate.** Run: `make tour`. Inspect: `git diff -- docs/tour.md docs/matrix.md` — expect a new `## [PASS] mcp attachment` section with the frozen detail. **The `[PASS]` marker is FROZEN (D13): the leg's `ok` is hardcoded `True`, so this section reads `[PASS]` regardless of live attach state and NEVER flaps the byte-compared doc — a transient probe failure can no longer turn `docs/tour.md` "stale" and tempt a re-`make tour` into baking a `[WARN]` baseline that would permanently encode the degraded state.** A real de-attach is therefore detected NOT from this section but from the leg's stdout `note` (the `ATTACH FAILED: mcp-attach-<member>` line `make tour` prints) and, definitively, from `make verify` (the de-attached member drops from `surfaced` → its lacuna is missing → verify fails naming it). If `make tour`'s `note` flags any member not-attached, **stop and diagnose** (real de-attach — fix the env or report consumer-boundary; do NOT relax the assertion or hand-edit the doc).
- [ ] **Step 3: Commit the lockstep docs.** `git add docs/tour.md docs/matrix.md && git commit -m "docs(tour): regenerate with mcp-attachment gate"` (+ Co-Authored-By trailer).
- [ ] **Step 4: Verify green.** Run: `make verify` → `VERIFY OK …`, exit 0.

**Definition of Done:** `make verify` exits 0 on a clean tree with all 6 members attached.

### Task 6: Negative test — prove the gate trips on a de-attach (and names the cause)

**Files:**
- Modify: `tour/__main__.py` (`run_verify` failure-cause emission)
- Test: `tests/test_mcp_attachment.py`

- [ ] **Step 1: Write the failing deterministic negative test at the `run_verify()` altitude.** The gate is the **`expected_tool in live`** filter in `tour/__main__.py::run_verify` (`if lac.expected_tool in live and lac.id in cov.missing_ids: failures.append(...)`) — a lacuna whose member CLI is live but whose token went dark ⇒ a named failure. `coverage()` **alone is the wrong altitude**: it knows nothing about the live-member filter, so a `coverage()`-only assertion (Task 3 already covers that seam) would not exercise the gate this harness exists to be. Drive the **real** `run_verify()` through its monkeypatchable `_drive` seam — make loomweave's CLI report **live** and the leg's `surfaced` **omit** `mcp-attach-loomweave`, then assert `run_verify()` returns `1`, names the member, **and reports the failure cause** (D17 — the leg's `note`, e.g. `loomweave:absent`, not only the bare token). Isolate the narrative-lockstep branch so the **sole** failure is the missing token (the right reason — a live member de-attached — not doc drift). **Two scenarios (D18), one per test function below:** (1) a live member whose binary RAN but whose handshake FAILED → a real **de-attach** (`<member>:absent (handshake-failed)`); (2) a live member whose SEPARATE `*-mcp` binary is **not installed** → `<member>:absent (not-installed)` — the exact `capability.detect()` CLI-name vs `warpline-mcp`/`plainweave-mcp` gap. Both trip the gate and name the member, but the surfaced diagnostic differs so the operator installs vs investigates:

```python
# tests/test_mcp_attachment.py (appended) — MANIFEST, load_manifest, and StepResult are
# already imported at module level (Tasks 1+3); add the run_verify-altitude imports:
from tour import __main__ as tour_main
from tour.capability import Capability

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
```

  (Relies on `docs/tour.md` + `docs/matrix.md` existing on disk — they do: Task 5 regenerates and commits them before this task. This proves the regression-harness's whole reason for being — a silent de-attach is caught, not papered over.)
- [ ] **Step 2: Run → fail.** `run_verify()` already names `mcp-attach-loomweave` / `mcp-attach-warpline` (so `rc == 1` and the token assertions pass), but it prints **no cause** — verify's failure loop emits only the bare `expected lacuna not surfaced: …` line, never the leg's `note` (`run_tour` prints notes at `__main__.py:55-58`; `run_verify` at lines 84-88 does **not**). So both new cause assertions — `assert "loomweave:absent (handshake-failed)" in out` (de-attach) and `assert "warpline:absent (not-installed)" in out` (D18 missing `*-mcp` binary) — **fail**: the gate says WHICH member, not WHY, and cannot tell a de-attach from a never-installed binary.

- [ ] **Step 3: Add the `run_verify()` failure-cause emission** in `tour/__main__.py`. When a missing `mcp-attach-<member>` lacuna trips the live-member filter, append the `mcp attachment` leg's `note` (the per-member liveness / `ATTACH FAILED` cause) to that failure line, so the operator sees whether the probe timed out, got garbled JSON, connected-but-unbound, or the binary was missing — not just the token. The leg's `note` is **excluded from the locked markdown** (`StepResult.note` is never rendered into `docs/tour.md`/`docs/matrix.md`), so emitting it on failure leaves `make verify` byte-for-byte deterministic. Complete `run_verify()` (the existing body with only the live-member loop extended):

```python
def run_verify() -> int:
    caps, results = _drive()
    manifest = load_manifest(MANIFEST)
    cov = coverage(manifest, results)
    failures: list[str] = []

    # 1. Every lacuna whose expected tool is LIVE must be surfaced.
    live = {c.name for c in caps if c.available}
    # D17: the mcp-attachment leg carries the failure CAUSE (per-member liveness — the
    # ATTACH FAILED reason: timed-out / garbled JSON / connected-but-unbound / missing
    # binary) in its `note`. Surface it on a missing attach token so the gate names WHY a
    # member de-attached, not only WHICH. `note` is excluded from the locked markdown, so
    # emitting it keeps `make verify` byte-for-byte deterministic.
    legs_by_name = {r.name: r for r in results}
    for lac in manifest.lacunae:
        if lac.expected_tool in live and lac.id in cov.missing_ids:
            msg = f"expected lacuna not surfaced: {lac.id} ({lac.expected_rule})"
            leg = legs_by_name.get("mcp attachment")
            if lac.id.startswith("mcp-attach-") and leg is not None and leg.note:
                msg += f" — {leg.note}"
            failures.append(msg)

    # 2. Narrative lockstep: regenerated docs must match the committed files.
    fresh_tour = render_tour_md(results)
    if not TOUR_MD.exists() or TOUR_MD.read_text() != fresh_tour:
        failures.append("docs/tour.md is stale — run `make tour` and commit")
    fresh_matrix = render_matrix_md(manifest, caps)
    if not MATRIX_MD.exists() or MATRIX_MD.read_text() != fresh_matrix:
        failures.append("docs/matrix.md is stale — run `make tour` and commit")

    if failures:
        print("VERIFY FAILED:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("VERIFY OK — every live lacuna surfaced; narrative in lockstep.")
    return 0
```

- [ ] **Step 4: Run → pass.**
- [ ] **Step 5: Commit** (`test(tour): mcp-attachment gate trips on a silent de-attach, naming the cause`).

**Definition of Done:** **two** negative tests drive the real `run_verify()` through the `_drive` seam and each asserts it returns `1` naming the de-attached member **and reporting the failure cause** (the leg's `note`) when that live member's attach token is missing — the failure isolated to the live-member coverage gate (`expected_tool in live`), not narrative drift. **D18 — both `absent` scenarios are documented and distinguished:** a real de-attach surfaces `loomweave:absent (handshake-failed)`, and a never-installed `*-mcp` binary (the `capability.detect()` CLI-name vs `warpline-mcp`/`plainweave-mcp` gap) surfaces `warpline:absent (not-installed)`, so the operator installs vs investigates and the two are never confused. `run_verify()` now names WHY a member failed, not only WHICH (D17), and emitting the (never-rendered) `note` keeps `make verify` byte-for-byte deterministic.

---

## Phase 5 — Join census layer (PDR-0009; reporting, NOT a hard gate)

> PDR-0009 upgraded G1 to a live **join census** with liveness classes. The cross-tool joins have honest non-failing states (`live-empty`, `reachable-gated`), so they belong in a **reported artifact**, not the binary attach gate. Keep this separable from Phases 1–4 so the gate ships first.
>
> **Re-spawn, not reuse (D20).** The census CANNOT ride Phase 2's probe sessions: those are spawn-init-terminate — `_teardown` reaps each server immediately after its handshake (Phase 2 Task 2), so by the time the leg returns there is **no** live session left to query. The census is therefore a documented **second pass** that **re-spawns** each relevant member through the *same* `_stdio_rpc`/`_http_rpc` transport contract (D10), never a reuse of the gate's already-closed sessions.

### Task 7: Emit the join census artifact + note

**Files:**
- Modify: `tour/mcp_attachment.py` (add `join_census() -> list[JoinResult]`), `tour/steps.py` (extend the leg's `note`)

- [ ] **Step 0: Lock the `.weft/mcp-attachment/census.json` schema BEFORE any Phase 5 code (D21).** The census is non-gating and deferrable, but its artifact schema MUST be fixed **first** so a later expansion does not churn the byte-compared lockstep surface (the leg's `note` and `docs/tour.md`). Write the canonical schema into `join_census()`'s docstring and emit exactly it in Step 2 — one record per join: `JoinResult(join: str, producer: str, consumer: str, liveness: str, evidence: str)` ⇒ `census.json` record `{"join": "<producer>→<consumer>", "producer": "<member>", "consumer": "<member>", "liveness": "live-bound|live-empty|reachable-gated|absent", "evidence": "<token-redacted str>"}`. No field is added, removed, or renamed after this step without a recorded decision.
- [ ] **Step 1:** Enumerate the PDR-0009 joins and probe each by **re-spawning** the relevant members in a **second pass** through the same `_stdio_rpc`/`_http_rpc` transport contract (D10) — Phase 2's probe sessions are already torn down (spawn-init-terminate; `_teardown` after each handshake), so the census re-attaches rather than reusing them: `plainweave→loomweave` (catalog/intent), `plainweave→legis` (preflight), `legis→loomweave` (rename-feed), `filigree↔loomweave` (entity-assoc), `legis→filigree` (closure-gate, expect `reachable-gated`), plus the 4 originals. Classify each `live-bound | live-empty | reachable-gated | absent` per the Step 0 schema.
- [ ] **Step 2:** Write `.weft/mcp-attachment/census.json` (gitignored, token-redacted) **in the Step 0 locked schema** and append a one-line per-join summary to the leg's `note` (NOT the frozen `detail` — keeps lockstep deterministic).
- [ ] **Step 3:** Do **not** gate `verify` on `live-empty`/`reachable-gated` joins (honest states); only the 6-member attach (Phase 4) gates. Commit.

**Definition of Done:** the `census.json` schema is **locked before any Phase 5 code** (D21, Step 0) so a later join expansion cannot churn the byte-compared lockstep surface; the census runs as a **second pass that re-spawns** each member through the same transport contract (never reusing Phase 2's already-torn-down sessions); each enumerated join is reported with a liveness class; `verify` determinism is unaffected (census lives in `note`/artifact only).

---

## Validate before execution

High-risk (spawns live servers; the stdio handshake is unproven until Task 0; live-probe determinism). After Phase 0 and before Phase 4, run **`/review-plan docs/plans/2026-06-26-mcp-attachment-regression-harness.md`** — the reality reviewer must validate: (a) the MCP `initialize` handshake is real for these servers from a subprocess, (b) the determinism bound (frozen `detail`, stable `surfaced`, live data in `note`), (c) the redaction guarantee on the filigree token.

## Open assumptions (recorded, not hidden)

- **The hand-rolled client can complete `initialize` + one binding-touching call** with each stdio server from a plain subprocess. The default for every member is that binding-touching call validated against `str(ROOT)`. *If a server genuinely cannot answer any binding-touching call* — proven by recorded Phase-0 evidence that the full check is **impossible**, not merely inconvenient — degrade **only that member** to `tools/list`-only liveness + static `.mcp.json` lint, and document it in `note` as catching process-**start** failures but **NOT** stale-**binding** failures (the 2026-06-26 loomweave incident is exactly a clean-start/broken-binding case, so a member left on liveness-only would not catch that class). (Phase-0 decision.)
- **`streamable-http` (filigree) answers a urllib `initialize`** — Phase-0 Step 3 determines the exact framing; if `text/event-stream`, the probe parses the SSE `data:` lines and round-trips the `Mcp-Session-Id` header on the `mcp_status_get` binding call. There is **no** REST/health-`GET` fallback: the `/api` REST route and the `/mcp/` MCP route are independent failure surfaces, and the gate must exercise the MCP route — so if the MCP `initialize` + binding handshake cannot complete, filigree degrades to **not-attached** (gate trips, named), never to a liveness ping that would mask a de-attach.
- **Live-probe results are stable enough to gate.** The gate asserts the **boolean** `attached and bound` per member (not bound-context strings), so transient string variation cannot flap lockstep; only a genuine de-attach changes the surfaced set. *If even attachment flaps*, add a single bounded retry in `probe` before classifying `absent`.
- **All 6 CLIs remain installed** (so `capability.detect()` keeps them live and the gate keeps requiring them) **AND the two separate MCP-server binaries `warpline-mcp` and `plainweave-mcp` are installed alongside their CLI siblings.** `capability.detect()` resolves only the CLI name (`warpline`/`plainweave`), but `.mcp.json` spawns the distinct `*-mcp` binary; their absence trips the gate as **not-installed** (D18 — install the binary), distinct from a de-attach. A member intentionally removed from `.mcp.json` must also drop from the lacunae set in the same commit — otherwise verify correctly fails.
- **The warpline + wardline binding tools SHIPPED + reinstalled (R1 — CONFIRMED LIVE 2026-06-28).** warpline's `warpline_project_status_get` and wardline's extended `doctor` `repo_binding` block are live in the reinstalled `.mcp.json` binaries (the uv-tool build-staleness step, per [[loom-uvtool-build-staleness]]); confirmed by spawning the fresh binaries the harness's way — warpline 16 tools / `binding_ok=true` / `schema_version=4`; wardline `doctor` / `binding_ok=true` / `schema_version=1`. The tautological `cwd==ROOT` static-lint is removed. NOTE: this session's already-attached `mcp__warpline__*`/`mcp__wardline__*` tools point at the OLD process until a reconnect, but the harness spawns FRESH subprocesses, so it sees the new tools (verified); a future warpline/wardline upgrade that reinstalls a stale build would re-break it — re-sync from source.

## Self-review (done at authoring)

- **Spec coverage:** PDR-0007 Phase 2 (6-member attachment harness) → Phases 1–4; PDR-0009 (join census + liveness classes) → Phase 5; the silent-de-attach lesson (PDR-0011) → Task 6 negative test. ✔
- **Placeholders:** deterministic tasks carry real code/tests; the live-probe handshake is honestly spike-gated (Phase 0), not a TODO. ✔
- **Type consistency:** `ServerSpec`, `AttachResult(member, attached, bound, liveness, bound_context, error)`, `redact()`, `classify(...)`, `_stdio_rpc`/`_http_rpc`/`_stdio_probe`/`_http_probe`, leg surfacing `("mcp-attach", member)`, lacunae `expected_rule="mcp-attach"` / `symbol=<member>` — names match across tasks, and every referenced symbol is now DEFINED in a code block (R5). ✔
- **Round-2 panel remediation folded:** R2 frozen-`ok` on all leg paths via the `_MCP_ATTACH_DETAIL` constant; R3 production `_stdio_rpc` uses `stderr=DEVNULL` (the spike drains via `communicate()`); R4 `test_manifest.py` 52→58; R5 `redact`/`AttachResult`/`classify`/`_http_probe` defined + a redact-strips-token test; R6 `test_drive.py` stubs the leg in both ordering tests; R7 unique tags D19 (protocol tolerance) / D20 (census re-spawn) / D21 (census schema lock); R8 `_http_rpc` SSE fake-transport test; plus the LOWs (classify `errored`/reachable-gated annotated, `_STDIO_BINDING` lists every member, inner-except `bound_context="probe-raised"`, `*-mcp` binary assumption recorded). **R1 (warpline/wardline self-report binding tools) is CONFIRMED LIVE 2026-06-28 — warpline `structuredContent.data.binding_ok`/`.store.schema_version`, wardline `structuredContent.repo_binding.binding_ok`/`.store.schema_version`, ground-truthed by spawning the fresh binaries; tautological static-lint removed.** ✔
