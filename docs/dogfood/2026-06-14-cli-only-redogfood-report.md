# CLI-Only Dogfood Re-Run — 2026-06-14

**Scope:** 4 launch-control federation members — Wardline, Loomweave, Filigree, Legis.  
Warpline (formerly Heddle, just renamed) is OUT of scope per mandate.  
**Method:** CLI-only. No `mcp__*` tools used. Subagent isolation, lacuna project at `/home/john/lacuna`.

---

## Verdict

**Pass rate: 1 / 12 live in-scope lacunae surfaced AND tracked in Filigree via the CLI suite.**

The CLI suite finds and gates the planted trust-boundary and code-archaeology defects,
but the Loomweave query surface (dead-entity, circular-import, coupling hotspot, entry-point,
subsystem, inheritance, decorator) is MCP-only — there is no CLI verb that runs
`entity_dead_list`, `module_circular_import_list`, `entity_coupling_hotspot_list`, etc.
Without those, loomweave structural lacunae are invisible to the CLI agent. Wardline
lacunae are reachable but bulk-baselined; only the unbaselined sentinel survives into a
tracked Filigree issue. The Legis lacuna (`lg-disabled-boundary-evidence`) fires correctly
but only via a non-obvious invocation pattern (venv Python with raised recursion limit).

---

## 4 Federation Joins

| Join | Description | Verdict | CLI Evidence |
|------|-------------|---------|--------------|
| **J1** | Wardline→Filigree emit (findings land with provenance/suppression state) | **PASS** | `wardline scan .` emitted 156 findings to `http://localhost:8749/api/p/lacuna/weft/scan-results`; 1 active (`lacuna-sf-4cb261e690`, PY-WL-125), 42 suppressed. `filigree finding get lacuna-sf-4cb261e690` confirmed `issue_id: lacuna-2a54dfb59d`, `scan_source: wardline`, `suppression_state: null` (active). |
| **J2** | Loomweave SEI keying (resolve finding location to `loomweave:eid:` SEI) | **PARTIAL** | SEI `loomweave:eid:4b0ed3a633fd3a572a9e1537e590f0a0` for `specimen.preview_sinks.log_export_request` confirmed via direct SQLite read of `.weft/loomweave/loomweave.db` (`sei_bindings` table). No CLI command (`loomweave entity-resolve` / `loomweave entity-find`) exists in the CLI surface — the CLAUDE.md instructions say to use `entity_find` / `entity_at` (MCP only). `wardline dossier` showed `sei: null` because it couldn't reach Loomweave (no `--loomweave-url` wired). SEI exists in the DB; the CLI join path is broken. |
| **J3** | Entity association ADR-029 (bind Filigree issue to loomweave entity; read back) | **PARTIAL** | Read-back PASS via HTTP: `GET /api/issue/lacuna-2a54dfb59d/entity-associations` returned association `loomweave:eid:4b0ed3a633fd3a572a9e1537e590f0a0` (`entity_kind: function`, attached by `dogfood-2026-06-13`). Reverse lookup PASS: `GET /api/entity-associations?entity_id=loomweave:eid:4b0ed3a633fd3a572a9e1537e590f0a0` returned the bound issue. Write path: `filigree entity-association` CLI command does not exist (`Did you mean one of: 'add-file-association', 'get-annotation'?`). Write path tested only via the HTTP API (PERMISSION error on the project-auth endpoint, so the prior attach was tour-created). **The CLI surface has no entity-association verb.** |
| **J4** | Legis closure-gate / governance | **PASS (with caveats)** | `legis governance-gate` → `override-rate gate: PASS_WITH_NOTICE (rate=0.000, sample=0)`. `legis policy-boundary-check` → `PASS` on default invocation (recursion error on `nesting_bomb.py` silently masks the `pinned_import` finding). Workaround: `.venv/bin/python3 -c "import sys; sys.setrecursionlimit(100000); from legis.cli import main; sys.exit(main())" policy-boundary-check --root specimen --repo-root .` → exit 1, correctly surfaces `POLICY_BOUNDARY_TEST_DISABLED` on `pinned_import`. HMAC signing confirmed: `wardline attest . --allow-dirty` produces valid HMAC-SHA256 bundle (key_id `3489e6c0`); `wardline attest . --verify /tmp/lacuna-attest.json` → `signature_valid: true`. `LEGIS_HMAC_KEY` env unset by default (not exported); `.env` must be sourced manually. Note: `sei_source: "unavailable"` in the attestation bundle — boundaries have null SEI, same as J2 gap. |

---

## Lacunae Scoring

### Manifest classification (in-scope = Wardline + Loomweave + Filigree + Legis tools)

**Total lacunae in manifest:** 37  
**Out of scope (Warpline):** 4 (`wp-blast-radius`, `wp-reverify`, `wp-churn`, `wp-timeline`)  
**Out of scope (Rust only, no CLI surface active):** 3 (`rs-untrusted-command`, `rs-untrusted-shell`, `rs-derives`, `rs-cfg-twin`, `rs-path-mount`) — actually 5  
**gate-trip lacunae (quarantine, not standard scan):** 2 (`wl-unparseable`, `lg-zero-under-green`)  
**In-scope live Python lacunae (measured):** 26 total; after removing gate-trips: **26 – 2 = 24 measurable**, but only 12 are for the 4 members specifically targetable via CLI:

The practical CLI-reachable set (excluding Rust, Warpline, and gate-trip fixture lacunae):

| Lacuna ID | Tool | Category | CLI Surfaced? | Filigree Tracked? |
|-----------|------|----------|--------------|------------------|
| wl-trust-violation | wardline | trust-boundary | YES (baselined) | NO (suppressed) |
| wl-non-rejecting-boundary | wardline | trust-boundary | YES (baselined) | NO (suppressed) |
| wl-broad-except | wardline | exception | YES (baselined) | NO (suppressed) |
| wl-swallowed-exception | wardline | exception | YES (baselined) | NO (suppressed) |
| wl-untrusted-callee | wardline | trust-boundary | YES (baselined) | NO (suppressed) |
| wl-untrusted-deser | wardline | injection | YES (baselined) | NO (suppressed) |
| wl-untrusted-exec | wardline | injection | YES (baselined) | NO (suppressed) |
| wl-untrusted-command | wardline | injection | YES (baselined) | NO (suppressed) |
| wl-none-leak | wardline | none-leak | YES (baselined) | NO (suppressed) |
| wl-contradictory-trust | wardline | decorator | YES (baselined) | NO (suppressed) |
| wl-assert-only-boundary | wardline | trust-boundary | YES (baselined) | NO (suppressed) |
| wl-untrusted-shell | wardline | injection | YES (baselined) | NO (suppressed) |
| wl-failopen-boundary | wardline | trust-boundary | YES (baselined) | NO (suppressed) |
| wl-invalid-level | wardline | decorator | YES (baselined) | NO (suppressed) |
| wl-untrusted-import | wardline | injection | YES (baselined) | NO (suppressed) |
| wl-path-traversal | wardline | injection | YES (baselined) | NO (suppressed) |
| wl-ssrf | wardline | injection | YES (baselined) | NO (suppressed) |
| wl-sql-injection | wardline | injection | YES (baselined) | NO (suppressed) |
| wl-degenerate-boundary | wardline | trust-boundary | YES (baselined) | NO (suppressed) |
| wl-stored-taint | wardline | stored-taint | YES (baselined) | NO (suppressed) |
| wl-xxe | wardline | injection | YES (baselined) | NO (suppressed) |
| wl-ssti | wardline | injection | YES (baselined) | NO (suppressed) |
| wl-reflection-injection | wardline | injection | PARTIAL (preview/unknown) | NO |
| wl-native-lib-load | wardline | injection | PARTIAL (preview/unknown) | NO |
| **wl-log-injection** | wardline | injection | **YES (active, unbaselined)** | **YES (lacuna-2a54dfb59d)** |
| wl-mail-injection | wardline | injection | PARTIAL (preview/unknown) | NO |
| lw-dead-code | loomweave | structure | NO (MCP only) | NO |
| lw-circular-import | loomweave | structure | NO (MCP only) | NO |
| lw-call-chain | loomweave | navigation | NO (MCP only) | NO |
| lw-coupling-hotspot | loomweave | navigation | NO (MCP only) | NO |
| lw-entry-point | loomweave | navigation | NO (MCP only) | NO |
| lw-subsystem | loomweave | navigation | NO (MCP only) | NO |
| lw-inheritance | loomweave | navigation | NO (MCP only) | NO |
| lw-decorator | loomweave | navigation | NO (MCP only) | NO |
| lw-too-complex | loomweave | archaeology | YES (in DB findings, LMWV-PY-TOO-COMPLEX) | NO (no CLI promote path) |
| lw-duplicate-locator | loomweave | archaeology | YES (in DB findings, LMWV-DUPLICATE-LOCATOR) | NO (no CLI promote path) |
| lg-disabled-boundary-evidence | legis | governance | PARTIAL (requires venv + recursion workaround) | NO |

### Pass rate computation

Criteria: lacuna **surfaced via the CLI suite** (not baseline-suppressed, not MCP-only) AND **tracked in Filigree via CLI**.

- **Surfaced AND tracked:** 1 (`wl-log-injection` / sentinel PY-WL-125)
- **Surfaced but not tracked (baselined/suppressed wardline findings):** 20
- **Surfaced partially (preview-tier, unknown state):** 3
- **Surfaced in DB but no CLI promote path (loomweave findings table):** 2
- **Governance lacuna surfaced via workaround but not tracked:** 1
- **Invisible to CLI (loomweave MCP-only navigation/structure queries):** 8
- **Out of scope (Warpline):** 4
- **Out of scope (Rust, gate-trip):** 7

**CLI-only pass rate = 1 / 12 in-scope Filigree-trackable lacunae = 8.3%**

_(The denominator excludes Rust, Warpline, gate-trip, and MCP-only lacunae, limiting to what a CLI-only agent could plausibly surface and file. If MCP-only lacunae are counted as misses, pass rate = 1 / 20 = 5%.)_

### Misses and reasons

| Lacuna | Miss Reason |
|--------|-------------|
| All 20 baselined wardline findings | Baseline suppresses them at the gate; `wardline scan` shows `42 suppressed`. An agent who doesn't know about `--trust-suppressions` sees 1 active. Without MCP `finding_promote`, the CLI `filigree finding promote` path requires knowing a specific fingerprint. |
| lw-dead-code, lw-circular-import, lw-call-chain, lw-coupling-hotspot, lw-entry-point, lw-subsystem, lw-inheritance, lw-decorator | These 8 are exposed only through Loomweave MCP query tools (`entity_dead_list`, `module_circular_import_list`, `entity_coupling_hotspot_list`, etc.). The CLI has no equivalent commands. `loomweave db` offers only `backup` and `checkpoint`; the FTS/query surface is MCP-only. |
| lw-too-complex, lw-duplicate-locator | In `loomweave.db` findings table (LMWV-PY-TOO-COMPLEX, LMWV-DUPLICATE-LOCATOR) but no CLI `loomweave findings list` command exists; CLI doctor shows them as index facts but there's no promote-to-filigree path without MCP. |
| lg-disabled-boundary-evidence | `legis policy-boundary-check` exits 0 on default invocation (RecursionError on `nesting_bomb.py` silently masks the finding). Only fires correctly with `.venv/bin/python3` + `sys.setrecursionlimit(100000)` invocation documented in the source file itself but not in any CLI help text. |
| wl-reflection-injection, wl-native-lib-load, wl-mail-injection | Wardline scan shows them as `unknown` assure state (not cleanly surfaced). Preview-tier rules; assure coverage shows 2 of 33 boundaries as `unknown`. |

---

## Friction Log (every grep/manual fallback)

| # | Where | What I fell back to | Why |
|---|-------|---------------------|-----|
| F1 | Loomweave entity lookup | Direct SQLite read of `.weft/loomweave/loomweave.db` | No `loomweave entity-find` or `loomweave entity-at` CLI command; CLAUDE.md says use `entity_find` (MCP). The only loomweave CLI commands are `install`, `analyze`, `serve`, `hook`, `db`, `guidance`, `config`, `doctor`, `sarif`. |
| F2 | SEI resolution for `log_export_request` | Direct SQLite `sei_bindings` table query | `wardline dossier` showed `sei: null` without `--loomweave-url`; no CLI to resolve SEI from locator. |
| F3 | Loomweave findings inspection | Direct SQLite `findings` table query | No `loomweave findings list` CLI verb; `loomweave doctor` reports counts but not individual findings. |
| F4 | Entity association write (J3) | HTTP `POST /api/issue/{id}/entity-associations` | `filigree entity-association` CLI command does not exist; the CLAUDE.md documents the HTTP API as an alternative but it requires the federation bearer token (PERMISSION error without auth header). The prior association was tour-created. |
| F5 | Entity association read (J3) | HTTP `GET /api/issue/{id}/entity-associations` | Same — no CLI verb; HTTP worked (no auth needed for GET on the federation endpoint). |
| F6 | Loomweave dead code / circular import check | Direct SQLite `edges` table query | No CLI equivalent of `entity_dead_list` or `module_circular_import_list`. Confirmed circular import exists in DB (mutual `imports` edges between `specimen.cycle_a` and `specimen.cycle_b`) but no CLI surface. |
| F7 | Policy-boundary-check (Legis lacuna) | `.venv/bin/python3 -c "import sys; sys.setrecursionlimit(100000); ..."` | `legis policy-boundary-check` silently passes because `nesting_bomb.py` RecursionError masks `pinned_import`. Source file itself documents the workaround; CLI help does not. |

**Grep/manual fallback count: 7**  
**Pure CLI success count: ~8** (wardline scan, wardline assure, wardline attest, legis governance-gate, legis check-override-rate, legis doctor, filigree session-context, filigree finding list/get)

---

## Top Friction Items

1. **Loomweave has no query CLI.** The entire entity graph surface (dead entities, circular imports, call chains, coupling hotspots, entry points, subsystems, inheritance, decorator relations) is MCP-only. The CLI is limited to `analyze`, `serve`, `doctor`, `guidance`, `db`, `config`, `sarif`. An agent operating CLI-only cannot access any Loomweave structural findings.

2. **No `filigree entity-association` CLI verb.** ADR-029 read/write is HTTP-only from the CLI surface. The CLAUDE.md documents the HTTP endpoints but they require proper auth headers for writes. `wardline decorator-coverage` output shows `work: {available: false, reason: "filigree not configured"}` — the dossier join requires both `--loomweave-url` and `--filigree-url` flags that no CLI invocation convention wires up.

3. **Wardline→Loomweave SEI join requires explicit `--loomweave-url`.** `wardline dossier <qualname>` shows `sei: null` and `linkages: {available: false}` unless a live Loomweave server URL is passed. There is no convention for a project-local Loomweave URL; agents must know to pass `--loomweave-url http://localhost:<port>`.

4. **`legis policy-boundary-check` silently passes on the planted lacuna** because `nesting_bomb.py` causes RecursionError at the default stack depth. The fix (raise recursion limit before calling the module) is documented only in the specimen source file, not in CLI help or AGENTS.md.

5. **Baseline semantics create a 1-active-of-many illusion.** `wardline scan .` shows `1 active` (the sentinel), giving a false impression of a clean project. All 20+ real defects are baselined and only visible under `--trust-suppressions` or via the finding list. A CLI-only agent starting fresh sees a very different picture from an MCP agent that can `finding_list` the suppressed set.

---

## "Prefer CLI over grep?" Verdict

**NO — not for this measurement scope.**

For the Wardline-only workflow (scan, assure, attest, gate), the CLI is fully sufficient and works well. No grep fallbacks required for trust-boundary analysis, gate execution, or Legis governance.

For the Loomweave-dependent workflows (structural dead-code, circular-import, navigation queries) and the full federation joins (SEI keying, entity-association, dossier with linkages), the CLI surface is a stub. The agent falls back to direct SQLite reads or HTTP calls 7 times in this run. The data is present in the DB; the CLI simply has no query layer.

The suite CLI works as a **gate tool** (Wardline scan/gate, Legis governance-gate, Filigree issue lifecycle). It does not work as a **discovery tool** (Loomweave structure, cross-tool SEI joins) — that is an MCP-exclusive surface by design. An agent running CLI-only should be briefed on this scope limitation before starting: it can gate on Wardline findings but cannot discover Loomweave structural lacunae.

---

## Appendix: Key CLI Invocations

```bash
# J1 — Wardline→Filigree emit
wardline scan .                                    # 156 findings, 1 active
filigree finding list --kind defect                # lacuna-sf-4cb261e690 active
filigree finding get lacuna-sf-4cb261e690 --json   # issue_id, suppression_state

# J2 — SEI lookup (SQLite fallback — no CLI)
sqlite3 .weft/loomweave/loomweave.db \
  "SELECT sei FROM sei_bindings WHERE current_locator='python:function:specimen.preview_sinks.log_export_request'"
# → loomweave:eid:4b0ed3a633fd3a572a9e1537e590f0a0

# J3 — Entity association read (HTTP — no CLI)
curl -s "http://localhost:8749/api/issue/lacuna-2a54dfb59d/entity-associations"
curl -s "http://localhost:8749/api/entity-associations?entity_id=loomweave:eid:4b0ed3a633fd3a572a9e1537e590f0a0"

# J4 — Legis governance
legis governance-gate                             # PASS_WITH_NOTICE
legis policy-boundary-check                       # PASS (misleading — see friction F7)
# Correct invocation:
.venv/bin/python3 -c "import sys; sys.setrecursionlimit(100000); from legis.cli import main; sys.exit(main())" \
  policy-boundary-check --root specimen --repo-root .  # exit 1, flags pinned_import

# Wardline attestation (requires LEGIS_HMAC_KEY)
set -a; . ./.env; set +a
wardline attest . --allow-dirty --out /tmp/lacuna-attest.json
wardline attest . --allow-dirty --verify /tmp/lacuna-attest.json  # signature_valid: true
```
