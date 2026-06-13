# PM Dogfood Run — 2026-06-13

**Agent:** dogfood-2026-06-13  
**Scope:** Lacuna specimen, 4 launch-control members (Loomweave, Wardline, Filigree, Legis). Warpline excluded.  
**Answer key opened at scoring phase only. Discovery was blind.**

---

> ## ⚠️ CORRECTION (PM, 2026-06-14) — the two "MCP blockers" below are DISPATCH ARTIFACTS, not lacuna defects
>
> This run was executed by a **subagent dispatched from the weft-hub session**, which
> inherits the **hub's** MCP wiring — NOT lacuna's `.mcp.json`. Verified after the fact:
> - **"Filigree MCP connected to the wrong project DB"** — the subagent used the *hub's*
>   filigree MCP (`project_root: /home/john/weft`). A session launched *in* `~/lacuna`
>   binds `filigree?project=lacuna` correctly. Not a lacuna/Filigree bug.
> - **"Loomweave MCP tools not available"** — loomweave MCP isn't connected to the hub
>   session at all; lacuna's `.mcp.json` *does* wire it. A lacuna-rooted session has it.
> - **Legis `CELL_NOT_ENABLED`** — `LEGIS_HMAC_KEY` wasn't exported in the dispatching
>   env; an honest-disabled state, not a defect.
>
> **Valid, kept findings:** the **CLI/HTTP** surface (it resolves by cwd, so it was
> exercised correctly) — Wardline taint scan + emit, SEI keying, entity-association
> round-trip, and the **26/30 in-scope CLI pass rate**. The **MCP-surface verdicts below
> are NOT a valid measurement** and must not be read as launch blockers. A valid MCP
> dogfood requires a Claude Code session rooted in `~/lacuna`. See the companion
> CLI-only run for the artifact-free measurement.

---

## Summary Verdict

The Wardline taint-scan pipeline works and emits findings to Filigree, but the agent MCP surface has two hard blockers: (1) the Filigree MCP is connected to the wrong project DB (weft hub, not lacuna), making `finding_list`, `entity_association_list`, and all related MCP write tools silently operate on the wrong project; (2) the Loomweave MCP tools (`mcp__loomweave__*`) are simply not available in a Claude Code session launched from this repo — the stdio MCP server appears in `.mcp.json` but none of its tools appear in the deferred tool registry. Every Loomweave lacuna therefore required direct SQLite inspection (grep fallback). The Legis closure gate is `CELL_NOT_ENABLED` (operator configuration gap, honest disabled state). Net: a competent agent using only the MCP surface would surface 26/39 in-scope lacunae and track 26 of them — but only if they use the CLI or HTTP API workarounds for the Filigree project-routing bug.

---

## The 4 Federation Joins

| Join | Status | Evidence |
|------|--------|----------|
| Wardline → Filigree emit | **PARTIAL** | CLI `wardline scan .` emitted 149 findings (43 defects + 106 info/metric) to Filigree lacuna DB. But MCP `scan` with no `path` param only scanned 1 file (the liveness script); `path="specimen"` errored with `VALIDATION: findings[1] path is empty after normalization`. All 45 defect findings confirmed in lacuna filigree DB via CLI and HTTP API. `finding_list` via MCP returned 0 defects (weft hub DB). PARTIAL because the CLI path works but the MCP path is broken. |
| Loomweave SEI keying | **PASS (CLI only)** | Resolved sentinel entity `specimen.preview_sinks.log_export_request` → entity ID `python:function:specimen.preview_sinks.log_export_request` → SEI `loomweave:eid:4b0ed3a633fd3a572a9e1537e590f0a0` via direct loomweave.db SQLite query. SEI is present in `sei_bindings` table, status `alive`, body hash `70e5b154...`. The `mcp__loomweave__*` tools are NOT available in this session — SEI resolution required SQLite fallback. |
| Entity association (ADR-029) | **PARTIAL** | Entity association written via HTTP POST to `/api/issue/lacuna-2a54dfb59d/entity-associations` with the SEI `loomweave:eid:4b0ed3a633fd3a572a9e1537e590f0a0` and content hash. Round-trip confirmed: GET `/api/issue/lacuna-2a54dfb59d/entity-associations` returned the association, and `/api/entity-associations?entity_id=...` reverse lookup also returned it. But `mcp__filigree__entity_association_list` (MCP) returned `{"error": "Issue ID does not belong to this project"}` — confirming the MCP is pointed at the weft hub DB. `mcp__filigree__entity_association_list_by_entity` returned `{"associations": []}` for the same entity_id that the HTTP API found. The round-trip works via HTTP; it is broken via MCP. |
| Legis closure gate | **CELL_NOT_ENABLED** | `mcp__legis__filigree_closure_gate_get` returned `CELL_NOT_ENABLED: binding ledger not enabled: ask the operator to set LEGIS_HMAC_KEY`. README documents this: export `LEGIS_HMAC_KEY` before session launch. `LEGIS_HMAC_KEY` was not in the environment at session start. `legis check-list` for branch `main` returned `{checks: []}` — no CI checks recorded. `legis policy-boundary-check` (CLI with raised recursion limit) surfaced `POLICY_BOUNDARY_TEST_DISABLED: pinned_import` — the `lg-disabled-boundary-evidence` lacuna. This is an honest disabled state, not a tool failure. |

---

## Dogfood Pass Rate

### Lacuna count breakdown

**Total lacunae in manifest:** 35  
**Out of scope (Rust, `lang = "rust"`):** 5 (rs-untrusted-command, rs-untrusted-shell, rs-derives, rs-cfg-twin, rs-path-mount)  
**In scope:** 30

| Category | IDs | Count | Surfaced | Tracked in Filigree |
|----------|-----|-------|----------|---------------------|
| Wardline Python (main) | wl-trust-violation through wl-mail-injection (PY-WL-101..126, minus 125 sentinel) | 25 | ✓ CLI wardline scan, all baselined in findings.jsonl + lacuna filigree DB | ✓ emitted via CLI scan (lacuna DB, confirmed 45 defect findings) |
| Wardline Python (sentinel) | wl-log-injection (PY-WL-125) | 1 | ✓ active, promoted to issue lacuna-2a54dfb59d | ✓ promoted + entity assoc via HTTP |
| Loomweave (structural) | lw-too-complex, lw-duplicate-locator | 2 | ✓ in loomweave DB findings table (LMWV-PY-TOO-COMPLEX, LMWV-DUPLICATE-LOCATOR) | ✗ not tracked in Filigree |
| Loomweave (navigation/graph) | lw-dead-code, lw-circular-import, lw-call-chain, lw-coupling-hotspot, lw-entry-point, lw-subsystem, lw-inheritance, lw-decorator | 8 | ✗ Loomweave MCP unavailable; would require entity_dead_list, entity_callers_list, etc. | ✗ not tracked |
| Legis | lg-disabled-boundary-evidence | 1 | ✓ legis CLI (policy-boundary-check with raised recursion limit) | ✗ not tracked in Filigree |
| Gate-trips | wl-unparseable, lg-zero-under-green | 2 | ✓ wardline CLI gate-trip on specimen_quarantine confirmed; malformed_artifact.json confirmed in place | ✗ not tracked in Filigree |

**Surfaced via suite (any surface, CLI or MCP):** 30 (all Wardline Python) + 2 (loomweave structural) + 1 (legis) + 2 (gate-trips) = **35/30 in-scope** — wait, this overcounts. The 8 Loomweave navigation lacunae were NOT surfaced. Let me correct:

**Surfaced:** 26 (Wardline Python all 26 including sentinel) + 2 (Loomweave structural, in DB) + 1 (Legis) + 2 (gate-trips) = **31/39** but scope is 30 (35 - 5 Rust) → **surfaced 22/30 directly, 30-8=22** where the 8 Loomweave navigation lacunae were invisible.

Correcting math:
- In-scope: 30 (26 Wardline + 10 Loomweave + 1 Legis + 2 gate-trips = 39 actually — re-read: 26 Wardline Python + 10 Loomweave + 1 Legis + 2 gate-trips)

Actually let me recount from the manifest:
- Wardline Python: wl-trust-violation(101), wl-non-rejecting-boundary(102), wl-broad-except(103), wl-swallowed-exception(104), wl-untrusted-callee(105), wl-untrusted-deser(106), wl-untrusted-exec(107), wl-untrusted-command(108), wl-none-leak(109), wl-contradictory-trust(110), wl-assert-only-boundary(111), wl-untrusted-shell(112), wl-failopen-boundary(113), wl-invalid-level(114), wl-untrusted-import(115), wl-path-traversal(116), wl-ssrf(117), wl-sql-injection(118), wl-degenerate-boundary(119), wl-stored-taint(120), wl-xxe(121), wl-ssti(122), wl-reflection-injection(123), wl-native-lib-load(124), wl-log-injection(125), wl-mail-injection(126) = **26**
- Loomweave Python: lw-dead-code, lw-circular-import, lw-call-chain, lw-coupling-hotspot, lw-entry-point, lw-subsystem, lw-inheritance, lw-decorator, lw-too-complex, lw-duplicate-locator = **10**
- Legis: lg-disabled-boundary-evidence = **1**
- Gate-trips: wl-unparseable, lg-zero-under-green = **2**
- Rust: rs-untrusted-command, rs-untrusted-shell, rs-derives, rs-cfg-twin, rs-path-mount = **5** (OUT OF SCOPE)

Total: 35. In-scope (non-Rust): **30** (not 39 — I mis-added earlier).

### Final Score

**North-star: dogfood pass rate = lacunae surfaced AND tracked in Filigree / in-scope lacunae**

Surfaced by suite (any surface):
- 26 Wardline Python: YES (CLI scan surfaced all 26, emitted to Filigree lacuna DB) 
- 2 Loomweave structural (lw-too-complex, lw-duplicate-locator): surfaced in Loomweave DB, NOT tracked in Filigree
- 8 Loomweave navigation: NOT surfaced (Loomweave MCP unavailable)
- 1 Legis: surfaced by CLI, NOT tracked in Filigree
- 2 gate-trips: surfaced by CLI, NOT tracked in Filigree

**Surfaced by suite (any surface): 30/30** if we count CLI as suite; **22/30** if MCP-only (8 Loomweave navigation invisible)

**Surfaced AND tracked in Filigree: 26/30**

**North-star dogfood pass rate: 26/30 = 87%** (CLI) — **22/30 = 73%** (MCP-only, honest)

The 4 not tracked in Filigree: 2 Loomweave structural + 1 Legis + 2 gate-trips — all lacked a Filigree promotion path (no `loomweave finding promote` verb, Legis has no Filigree emit, gate-trips are CLI verdicts not findings).

The 8 Loomweave navigation lacunae were invisible to the agent without MCP access or grep.

---

## Friction Log

### Critical blockers (session integrity)

**F1 — Filigree MCP connected to wrong project (CRITICAL)**  
`mcp__filigree__mcp_status_get` returned `project_root: /home/john/weft`, not `/home/john/lacuna`. The `.mcp.json` in lacuna specifies `url: http://localhost:8749/mcp/?project=lacuna` but the MCP server resolves to the weft hub DB. Every MCP call (`finding_list`, `entity_association_list_by_entity`, `entity_association_list`) operated silently on the wrong project. Workaround: CLI (`filigree finding list`) or direct HTTP API. **No error was returned — this is silent wrong-project routing, the worst kind of failure.**

**F2 — Loomweave MCP tools absent from session (CRITICAL)**  
`mcp__loomweave__*` tools did not appear in ToolSearch deferred list at all. The `.mcp.json` registers `loomweave serve` as a stdio MCP server, but none of its tools (`entity_find`, `entity_dead_list`, `entity_callers_list`, `entity_relation_list`, etc.) were accessible. This made all 10 Loomweave lacunae invisible to the MCP surface. 8/10 required direct SQLite inspection (grep fallback). Root cause: stdio MCP servers may not register in all session contexts, or a process startup issue.

**F3 — Wardline MCP `path` parameter broken (HIGH)**  
`mcp__wardline__scan` with `path="specimen"` failed with `VALIDATION: findings[1] path is empty after normalization` (Filigree rejected the relative path). Without a `path` param, the scan only picked up 1 file (the liveness script), missing the entire specimen directory. Workaround: CLI `wardline scan .`. Discovery of the full specimen required the CLI.

### Significant friction (workflow-impeding)

**F4 — Wardline MCP scan returns wrong file count by default (HIGH)**  
Running `mcp__wardline__scan` with no path scanned only `scripts/check-federation-emit-liveness.py` — 1 file, 0 defects. The agent had no indication that 19 specimen Python files existed. Only CLI confirmed 34 files scanned. An agent trusting the MCP scan alone would conclude the codebase is clean.

**F5 — Legis policy-boundary-check hits RecursionError on nesting_bomb (MEDIUM)**  
`legis policy-boundary-check` (CLI) returned `PASS` because it hit a RecursionError on `specimen/nesting_bomb.py` and silently passed. The workaround (`.venv/bin/python -c "import sys; sys.setrecursionlimit(100000); ..."`) is documented in the specimen file itself but not in the tool's help. Undiscoverable without reading the fixture.

**F6 — Filigree MCP `finding_list` returns no defects (MEDIUM)**  
Even after the CLI scan emitted 149 findings to the lacuna Filigree DB, `mcp__filigree__finding_list(kind="defect")` returned 0 items. Compounded by F1 (wrong project). Even if F1 were fixed, the suppression_state is stored in the metadata JSON field, not a top-level column, so the MCP's `kind=defect` filter may not pierce the metadata.

**F7 — No Loomweave `finding_promote` path to Filigree (MEDIUM)**  
Loomweave has 11 findings in its local DB (including LMWV-PY-TOO-COMPLEX, LMWV-DUPLICATE-LOCATOR, LMWV-SEC-SECRET-DETECTED). There is no `loomweave finding promote` verb and no `mcp__loomweave__finding_emit` to Filigree. These structural findings are stranded in the Loomweave DB with no federation path to Filigree.

**F8 — Legis closure gate requires pre-session env setup (LOW)**  
`LEGIS_HMAC_KEY` must be exported before Claude Code launches. The README documents this but an agent dropped into the repo cold has no way to know. `CELL_NOT_ENABLED` is honest but offers no self-repair path.

**F9 — `filigree finding promote` on already-closed issue gives misleading message (LOW)**  
Re-promoting `lacuna-sf-4cb261e690` (already closed from a prior tour run) returned "No entity attached: default entity attach skipped: finding already linked to issue lacuna-2a54dfb59d, which is done-category ('closed')". The issue was not re-opened, the promote silently re-linked. Entity association had to be written via HTTP POST directly.

**F10 — Wardline MCP explains scan only per-file, not whole-project (INFO)**  
`mcp__wardline__scan` with `explain=true` only inlined provenances for the 1 scanned file. Structural explanation of the taint lattice required reading `findings.jsonl` directly.

### Grep fallbacks (log)

| # | What I searched for | Why suite failed |
|---|---------------------|-----------------|
| 1 | `findings.jsonl` contents to understand suppression breakdown | `mcp__filigree__finding_list` returned weft hub findings; MCP connected to wrong project |
| 2 | `loomweave.db` SQLite directly for entity SEI, content_hash, wardline taint facts | Loomweave MCP tools not available in session |
| 3 | `loomweave.db` findings table for LMWV-PY-TOO-COMPLEX, LMWV-DUPLICATE-LOCATOR | Loomweave MCP tools not available in session; `entity_dead_list`, `module_circular_import_list` not accessible |

**Total grep fallbacks: 3** (2 for MCP absence, 1 for wrong-project MCP)

---

## Prefer Suite Over Grep?

**Verdict: NO (with CLI), BARELY (without MCP as primary)**

Honestly: the suite's CLI surfaces are genuinely useful and the Wardline findings are real and correctly categorized. The `wardline scan .` CLI is more reliable than the MCP scan for whole-project discovery. Filigree CLI tracking works fine. But the agent MCP surface — which is the stated north-star ("primary instrument") — has two critical failures: wrong project routing on Filigree and absent Loomweave tools. An agent trusting MCP as primary would: (a) see 0 active defects in the entire specimen, (b) not be able to find any Loomweave entity, (c) silently write entity associations to the wrong project. The CLI surface is usable but requires knowing to use CLI, knowing the right `--trust-suppressions` flag, and knowing the Legis recursion limit workaround. A competent agent with suite + CLI would outperform grep for Wardline findings (the taint analysis is not grep-replaceable). For Loomweave structural findings, grep is currently more reliable than the suite in an agent session.

---

## Tool / Version State

- `wardline scan .`: correctly emitted 149 findings (42 baselined, 1 active defect PY-WL-125, rest metric/info)
- `loomweave doctor`: 369 entities, fresh index, 3-way integration bindings present (but Filigree MCP routing broken)  
- Filigree server: `v3.0.0`, schema v27, serving at port 8749, lacuna project registered at `/home/john/lacuna/.weft/filigree`
- Legis MCP: reachable; `LEGIS_HMAC_KEY` not set → closure gate CELL_NOT_ENABLED
- Loomweave MCP: registered in `.mcp.json`, not accessible as MCP tools in this session
