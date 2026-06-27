# Phase 0 Findings: MCP-Attachment Characterization

**Date:** 2026-06-28  
**Script:** `scripts/characterize_mcp_attachment.py`  
**Evidence dump:** `.weft/mcp-attachment/characterization.json` (gitignored, token-redacted)  
**Task:** PDR-0007, Task 0 — feasibility spike  

---

## Decision: Handshake viable

- **Stdio transport:** hand-rolled newline-delimited JSON-RPC works against all 5 stdio members. The `recv()` loop correlates by `msg.get("id")` and discards interleaved notifications (DoD requirement met — a single `readline()` would mis-parse a notification as the result).
- **HTTP transport:** `urllib` POST + minimal SSE parser works against filigree. No SDK dependency needed at this phase.
- **Proceed to Phase 1+** as written. No member required the real `mcp` SDK client.

---

## Per-Member Binding Evidence Contract

All 6 members characterized 2026-06-28 by spawning fresh binaries (cwd=ROOT, env from `.mcp.json`).

### Table: Canonical Binding Contract

| Member | Transport | Binding Tool | Arguments | Unwrap Path | Predicate vs `str(ROOT)` | Store-Read Signal (de-attach) |
|--------|-----------|-------------|-----------|-------------|--------------------------|-------------------------------|
| **loomweave** | stdio | `project_status_get` | `{}` | `content[0].text` → JSON → `result.project_root` | `== str(ROOT)` | `result.db_present == True` AND `result.db_identity.data_version is not None` |
| **filigree** | streamable-http (SSE) | `mcp_status_get` | `{}` | `content[0].text` → JSON → `project_root` (top-level) | `== str(ROOT)` | `db_initialized == True` AND `schema_compatible == True` |
| **legis** | stdio | `doctor_get` | `{}` | `structuredContent.checks[id=="runtime.policy_cells"].message` | `startswith(str(ROOT))` | `store.binding_chain == "ok"` AND `store.governance_chain == "ok"` |
| **wardline** | stdio | `doctor` | `{}` | `structuredContent.repo_binding` | `binding_ok == True` AND `store.schema_version is not None` | `structuredContent.repo_binding.store.readable == True` |
| **warpline** | stdio | `warpline_project_status_get` | `{"repo": str(ROOT)}` | `structuredContent.data` | `binding_ok == True` AND `store.schema_version is not None` | `structuredContent.data.store.readable == True` |
| **plainweave** | stdio | `plainweave_project_context_get` | `{}` | `structuredContent.data` | `db_path.startswith(str(ROOT))` AND `initialized == True` | `structuredContent.data.initialized == True` AND `schema_version is not None` |

**Critical design note on path-vs-store predicates:** For the 4 "path" members (loomweave, filigree, legis, plainweave), a path match against ROOT is NOT sufficient to catch the 2026-06-26 de-attach class (server started clean but store unreadable). The path may echo ROOT even when the DB is absent. The gate MUST assert BOTH the path predicate AND the store-read signal. The 2 "binding_ok" members (wardline, warpline) already return a true store-read boolean — no path needed.

### Unwrap path shapes (three distinct forms)

1. **`content[0].text` → top-level JSON key**: filigree — `project_root` at top level of the text-JSON.
2. **`content[0].text` → nested `result.*` key**: loomweave — `result.project_root` (text-JSON has top-level `ok`, `result`, `diagnostics`).
3. **`structuredContent.*`**: wardline, warpline, legis, plainweave — MCP `structuredContent` object present; no need to parse `content[0].text` (though it carries the same payload for legis/plainweave).

The gate's interpreter (Task 2) must handle all three shapes per member.

---

## Resolution of the 4 Unknowns

### Unknown 1: Filigree SSE framing

**Resolved.** filigree uses `Content-Type: text/event-stream` (SSE) for all MCP responses. The body format is `event: message\ndata: <JSON>\n\n`. A minimal SSE parser (strip `data:` prefix, `json.loads`) is sufficient.

Key findings:
- `Accept: application/json, text/event-stream` header is **required** — omitting it returns HTTP 406 (Not Acceptable) with a JSON-RPC error. This is the primary silent failure mode for this transport.
- **STATELESS**: filigree returns no `Mcp-Session-Id` header. Follow-up POSTs work with just the auth header (no session state). Confirmed by probing `tools/list` and `mcp_status_get` independently.
- Defensive implementation: capture `Mcp-Session-Id` if present and echo it on follow-ups — safe to do, costs nothing, future-proofs against protocol evolution.
- Server-resolved `project_root` comes from `content[0].text` parsed as JSON, at the top level (not nested under `result`).
- `protocolVersion` echoed: `2024-11-05` (same as requested).

### Unknown 2: Legis crash status

**Resolved: CLEAN.** `doctor_get` returned all 25 checks without error. The documented crash (`no such table: audit_log`) affects `posture_get` and `policy_list`, NOT `doctor_get`.

- `initialize` + `tools/list` + `doctor_get`: all succeeded.
- `doctor_get` has `structuredContent` with a `checks` array.
- Top-level `structuredContent.ok = False` due to install warnings (`install.gitignore`, `install.dir_gitignore`) — these are benign configuration reminders. Do NOT use top-level `ok` as the binding predicate.
- Binding signal: `runtime.policy_cells.message = "/home/john/lacuna/policy/cells.toml"` (under ROOT) + `store.binding_chain = "ok"` + `store.governance_chain = "ok"`.
- **Decision:** Use `doctor_get` as the binding call. No degradation needed.

### Unknown 3: Loomweave unwrap path

**Resolved.** `project_status_get` binding is via `content[0].text` → JSON parse → **`result.project_root`** (under the `result` sub-object, not top-level — the top level has `ok`, `result`, `diagnostics`, `stats_delta`).

Additional store-read signal: `result.db_present = True` + `result.db_identity.data_version = 2`. 
The `result.db_path` also contains an absolute path under ROOT.

`protocolVersion` echoed: `2025-11-25` (server reports its own version; client sent `2024-11-05` — accepted without error).

### Unknown 4: Plainweave unwrap path

**Resolved.** `plainweave_project_context_get` returns BOTH `structuredContent` AND `content[0].text` (same payload). The gate should use `structuredContent.data.db_path` (server-resolved path under ROOT) as the path predicate.

Full schema: `structuredContent = {schema, ok, data: {initialized, project_key, schema_version, db_path, capabilities, ...}, meta, warnings}`.

Store-read signal: `structuredContent.data.initialized = True` AND `structuredContent.data.schema_version = 2`.

---

## Wardline :9730 Independence (Step 3b)

**Resolved.** wardline's `doctor` binding read is independent of the loomweave HTTP companion at :9730.

Evidence: probed wardline with `--loomweave-url http://127.0.0.1:9731` (non-listening port — definitively not open). Result: `initialize` succeeded, `doctor` returned `repo_binding.binding_ok = True`, `store.schema_version = 1`, `baseline_finding_count = 44`.

**Spawn-ordering decision:** no required ordering. wardline reads its local baseline store (`/home/john/lacuna/.weft/wardline/`) — :9730 serves wardline's emit/scan path, not the binding read. `wardline` can spawn before `loomweave serve`.

---

## Per-Member Protocol Versions Observed

| Member | Requested | Echoed |
|--------|-----------|--------|
| loomweave | 2024-11-05 | 2025-11-25 |
| filigree | 2024-11-05 | 2024-11-05 |
| legis | 2024-11-05 | 2024-11-05 |
| wardline | 2024-11-05 | 2024-11-05 |
| warpline | 2024-11-05 | 2024-11-05 |
| plainweave | 2024-11-05 | 2024-11-05 |

loomweave echoed its own higher version (`2025-11-25`) but accepted the handshake. No version negotiation failure observed.

---

## Binding Mode: All 6 Self-Report

All 6 members self-report a server-resolved store-read fact. The tautological `cwd==ROOT` static lint is NOT used — per R1, both wardline and warpline now have real store-read tools (`doctor` and `warpline_project_status_get`). A member that initializes but fails its binding-touching call classifies `live-empty` and the gate fails loudly naming it.

**The 2026-06-26 loomweave incident class is caught by all 6 members** — each binding call requires reading a server-side store, not just process startup.

---

## Fallback / Degradation Record

No member required degradation. All 6 binding-touching calls returned cleanly in a single run.

If a member's binding-touching call were absent or crashing (per Step 5 of the brief), the only permitted fallback is `tools/list`-only liveness — documented in `note` as catching process-start failures but NOT stale-binding failures. The tautological `cwd==ROOT` lint is permanently removed as a fallback option.

---

## Files Produced

- `scripts/characterize_mcp_attachment.py` — standalone spike harness (committed)
- `docs/plans/phase0-findings.md` — this document (committed)
- `.weft/mcp-attachment/characterization.json` — redacted evidence dump (gitignored, NOT committed)

## Input to Task 1

The module docstring for `tour/mcp_attachment.py` (created in Task 1) should include:
1. The canonical 6-row binding contract table above.
2. The 3 unwrap-path shapes (filigree top-level, loomweave nested-result, structuredContent).
3. The per-member binding mode (all self-report).
4. The store-read vs path distinction — gate must assert BOTH.
5. The filigree SSE framing notes (Accept header required, stateless, defensive session-id capture).
6. The legis decision (doctor_get clean; top-level ok=False is benign).
7. The wardline spawn-ordering decision (no dependency on :9730 for binding).
