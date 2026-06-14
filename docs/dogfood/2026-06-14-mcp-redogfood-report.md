# Final MCP-Surface Dogfood — REPORT (2026-06-14)

**Run from a session rooted in `/home/john/lacuna`** (mandatory — MCP tools
resolve against the project's own `.mcp.json`). Companion to the same-day
CLI-only run (`2026-06-14-cli-only-redogfood-report.md`, verdict **1/12**). This
report measures the **MCP agent surface** — the experience a real agent has.

Deployed versions (confirmed live): **wardline 1.0.0rc4 · loomweave 1.1.0-rc5 ·
filigree 3.0.0 · legis 1.0.0 · warpline 1.0.0**.

---

## Verdict

**MCP-surface pass rate: 12 / 12 in-scope lacunae reachable via MCP, vs the
CLI-only run's 1 / 12.**

Every lacuna the CLI-only agent could not see — the 8 Loomweave structural/
navigation queries, the 2 Loomweave findings-table archaeology items, and the
Legis governance lacuna — is reachable through the MCP surface. The 4 federation
joins all PASS via MCP only (the CLI run scored J2/J3 PARTIAL, falling back to
raw SQLite and HTTP). The discovery story the CLI run found "MCP-exclusive by
design" holds up: **the MCP surface is the discovery tool the CLI is not.**

Two real frictions and one doc mismatch were found (below); none block a join,
all are recorded as Filigree observations for hub triage. One is launch-gate
relevant (the Loomweave→Filigree finding bridge).

---

## Preflight (all PASS)

| Check | Result |
|-------|--------|
| cwd / branch | `/home/john/lacuna`, `main`, tree clean |
| Secrets | `WEFT_FEDERATION_TOKEN` set, `LEGIS_HMAC_KEY` set |
| 5 MCP servers attached + routing to lacuna | filigree `:8749`, loomweave (`project_root=/home/john/lacuna`, SEI `populated:true`), wardline (`fresh:true`, `filigree.auth ok`), legis (`filigree_scope` project-pinned to lacuna), warpline (`local_only:true`) |
| Index freshness | loomweave index **1 commit behind** (last analyzed `74af4a92`; HEAD `e144554`, a docs-only commit). specimen/ unchanged ⇒ structural queries valid. Noted, non-material. |

---

## 4 Federation Joins — all PASS via MCP

| Join | Verdict | MCP evidence |
|------|---------|--------------|
| **J1** Wardline→Filigree emit | **PASS** | `wardline scan` (MCP): `filigree_emit` reachable, `updated:156 failed:0 token_sent:true auth_rejected:false`, project-pinned `…/api/p/lacuna/weft/scan-results`; `loomweave_write:227`. `finding_get lacuna-sf-4cb261e690` asserts `scan_source=wardline`, `issue_id=lacuna-2a54dfb59d`, `suppression_state=null` (active), `rule_id=PY-WL-125` (sentinel). |
| **J2** Loomweave SEI keying | **PASS** | `entity_find log_export_request` → SEI `loomweave:eid:4b0ed3a633fd3a572a9e1537e590f0a0` (no DB touch). `wardline dossier specimen.preview_sinks.log_export_request` → `sei` non-null, `keyed_on_sei:true`, `linkages.available:true` (callee `read_report_field`), `work.available:true` joined to `lacuna-2a54dfb59d`. **This is exactly the CLI gap (`sei:null`) closed.** |
| **J3** ADR-029 entity association (both directions) | **PASS** | Reverse: `entity_association_list_by_entity(loomweave:eid:4b0ed3a…)` → issue `lacuna-2a54dfb59d` (`freshness_status:fresh`). Forward: `entity_association_list(lacuna-2a54dfb59d)` → the SEI. `entity_association_add` idempotent (refreshed `attached_at`, preserved original `attached_by`). **CLI surface has no verb here — MCP delivers.** |
| **J4** Legis governance / closure + attestation | **PASS** | `policy_list`/`policy_explain`: `protected` cell `enabled:true`, `available_moves:[override_submit]` ⇒ `LEGIS_HMAC_KEY` live (**not** CELL_NOT_ENABLED). `filigree_closure_gate_get(lacuna-2a54dfb59d)` → honest `allowed:false` (no verified binding). `override_rate_get` → `PASS_WITH_NOTICE`. `wardline attest` (clean tree) → HMAC-SHA256 bundle `key_id:3489e6c0`, SEI-keyed (`sei_source:loomweave`); `verify_attestation reproduce=true` → `signature_valid:true reproduced:true mismatches:[]`. |

**Joins: 4/4 PASS** (CLI run: J1 PASS, J2 PARTIAL, J3 PARTIAL, J4 PASS-with-caveats).

---

## 8 (+2) Structural Lacunae — the core delta vs the CLI run

| Lacuna | MCP query | Surfaced? | Evidence |
|--------|-----------|-----------|----------|
| `lw-dead-code` | `entity_dead_list` | **YES** | `specimen.dead_code.orphaned_helper` (141 dead candidates total) |
| `lw-circular-import` | `module_circular_import_list` | **YES** | 1 cycle: `specimen.cycle_a ↔ specimen.cycle_b` |
| `lw-coupling-hotspot` | `entity_coupling_hotspot_list` | **YES** | `specimen.hub.dispatch` (coupling 10), 203 ranked |
| `lw-entry-point` | `entity_entry_point_list` → `entity_tag_list` | **YES** (alt facet) | `entity_entry_point_list` is honest-empty (no `entry-point` tag emitted); entry points surface via `entity_tag_list(cli-command)` → `specimen.cli._add_book`, `_register` |
| `lw-subsystem` | `entity_subsystem_get` | **YES** | `core:subsystem:545aadaf97f0` "specimen" (Leiden, 7 modules, modularity 0.32) |
| `lw-inheritance` | `entity_relation_list inherits_from` | **YES** | `specimen.repository.InMemoryRepository` ⟶ `Repository` (line 57) |
| `lw-decorator` | `entity_relation_list decorates direction=in` | **YES** | `_add_book` decorated by `@App.command("add-book")` (line 44) |
| `lw-call-chain` | `entity_execution_path_list` | **YES** | `specimen.hub.dispatch` → `_audit/_format/_meter/_persist/_route` |
| `lw-too-complex` | `project_finding_list` | **YES (discover)** | `LMWV-PY-TOO-COMPLEX` on `specimen/nesting_bomb.py`. *Trackable only via manual bridge — see Friction A.* |
| `lw-duplicate-locator` | `project_finding_list` → bridge → `finding_promote` | **YES (discover + tracked)** | `LMWV-DUPLICATE-LOCATOR` (`specimen.colliding.ShelfMark`). Tracked end-to-end: `finding_report` → `finding_promote` → **issue `lacuna-0b21f65e82`** + `entity_association_add` SEI `loomweave:eid:1ff30e4e7054…`. |

All 8 navigation/structure lacunae the CLI run scored **invisible (MCP-only)** are
reachable here. `lw-entry-point` needs the alternate `cli-command` facet because
the python plugin emits no `entry-point` tag (`entity_entry_point_list` is
honestly empty, not falsely clean).

---

## Legis policy-boundary trap (#3) — MCP does NOT reproduce the CLI silent-pass

CLI friction F7: `legis policy-boundary-check` exits 0 because `nesting_bomb.py`
raises `RecursionError` at default stack depth, masking the `pinned_import`
finding.

**MCP `policy_boundary_check(repo_root=., root=specimen)` → `outcome:FINDINGS`:**
- `POLICY_BOUNDARY_FILE_TOO_COMPLEX` on `specimen/nesting_bomb.py` — *"nesting too deep to analyze; file skipped, scan continued (per-file degrade)"*
- `POLICY_BOUNDARY_TEST_FINGERPRINT_MISMATCH` on `specimen/policy_boundaries.py:43` (**`pinned_import`** — the masked finding, surfaced)
- `POLICY_BOUNDARY_TEST_FINGERPRINT_MISMATCH` on `:30` (`validated_recovery`)

The MCP tool **per-file degrades** instead of crashing the whole scan, and
surfaces `pinned_import` **without** the `sys.setrecursionlimit` workaround. This
is an MCP-surface win over the CLI — the trap's "if the MCP tool reproduces the
silent-pass, that is a finding" condition is **not** met.

---

## Warpline (5th member) — enrich-only, captured, NOT pass/fail-scored

All four advisory demos on `specimen/cli.py::_add_book` (key 128) enrich and
never gate; every response `local_only:true`, `peer_side_effects:[]`,
`enrichment` a closed vocab.

| Demo | Result |
|------|--------|
| `wp-churn` | `churn_count:1` (added 2026-06-05) |
| `wp-timeline` | 1 change (`added` @ `fb01a013`); `sei_resolution:unresolved` (honestly reported — warpline keys on locators, never claims lineage) |
| `wp-blast-radius` | `completeness:DELTA` (1 commit behind); affected: `App`, `Genre`, `LibraryService.add_book` (d1) → `Book`, `InMemoryRepository.add`, `specimen.cli` (d2) |
| `wp-reverify` | 7-entity worklist with `suggested_verification` per entity |

---

## Head-to-head scoreboard (same 12-item denominator as the CLI run)

| # | Lacuna | CLI-only | MCP surface |
|---|--------|----------|-------------|
| 1 | `wl-log-injection` (sentinel) | ✅ surfaced+tracked | ✅ J1 (active, `lacuna-2a54dfb59d`) |
| 2 | `lw-dead-code` | ❌ MCP-only | ✅ `entity_dead_list` |
| 3 | `lw-circular-import` | ❌ MCP-only | ✅ `module_circular_import_list` |
| 4 | `lw-call-chain` | ❌ MCP-only | ✅ `entity_execution_path_list` |
| 5 | `lw-coupling-hotspot` | ❌ MCP-only | ✅ `entity_coupling_hotspot_list` |
| 6 | `lw-entry-point` | ❌ MCP-only | ✅ `entity_tag_list(cli-command)` |
| 7 | `lw-subsystem` | ❌ MCP-only | ✅ `entity_subsystem_get` |
| 8 | `lw-inheritance` | ❌ MCP-only | ✅ `entity_relation_list` |
| 9 | `lw-decorator` | ❌ MCP-only | ✅ `entity_relation_list` |
| 10 | `lw-too-complex` | ❌ no promote path | ⚠️ discoverable; trackable via manual bridge (Friction A) |
| 11 | `lw-duplicate-locator` | ❌ no promote path | ✅ discovered + **tracked** (`lacuna-0b21f65e82`) |
| 12 | `lg-disabled-boundary-evidence` | ⚠️ workaround only | ✅ `policy_boundary_check` surfaces `pinned_import` cleanly |

**CLI-only: 1/12. MCP surface: 12/12 reachable** (11 cleanly, 1 — `lw-too-complex`
— discoverable with the same manual-bridge needed for any Loomweave finding).

---

## Friction log (every fallback / deviation — a fallback IS the finding)

| # | Severity | Friction | Detail | Filed |
|---|----------|----------|--------|-------|
| **A** | **launch-gate** | Loomweave findings never reach Filigree's finding store | `finding_list scan_source=loomweave` → empty; all 45 Filigree defects are `PY-WL-`/`RS-WL-` (wardline only). The brief's `loomweave findings list → finding_promote` path can't complete — `finding_promote` needs a Filigree `finding_id`. **Workaround proven:** `finding_report` (scan_source=agent) → `finding_promote` → `entity_association_add` SEI (issue `lacuna-0b21f65e82`). Fix: wire a loomweave→Filigree finding emit, or document the manual bridge as the intended path. | obs `lacuna-obs-1c7e6ddee5` |
| **B** | medium | Loomweave `scope` param is a full entity-ID prefix match; `scope=<package>` silently empty | `entity_dead_list`/`module_circular_import_list`/`entity_coupling_hotspot_list` with `scope='specimen'`, `'specimen.dead_code'`, `'specimen/'` → 0 rows; only `scope='python:module:specimen.dead_code'` (or unscoped) matches. An agent tries the package name, reads the empty as "no dead code". Fix: match qualname/path prefix too, or emit a scope-not-matched diagnostic. | obs `lacuna-obs-cc01cb6424` |
| **C** | low (doc) | `policy/cells.toml` claims keyless coached lane returns `enabled:true`; live `policy_explain` reports coached `enabled:false` | cells.toml line 16 vs reality (judge_inline cell, provider not wired). The protected closure-gate showcase is unaffected (`enabled:true`). Fix comment or wire the judge. | obs `lacuna-obs-bdcb0cb0eb` |

No raw-SQLite or raw-HTTP fallbacks were needed (the CLI run needed 7). Every
join and every lacuna was reached through MCP tools; the only deviations are the
three above, all logged.

---

## "Prefer MCP over grep?" verdict

**YES.** Where the CLI run fell back to direct SQLite (`sei_bindings`, `edges`,
`findings`) and raw HTTP (entity-associations) **7 times**, the MCP surface
answered every join and every structural query natively. The MCP tools are
honest about their limits — `entity_entry_point_list` says "honest-empty, see
known_tags"; `wardline dossier` freshness-stamps both identity and content;
warpline marks `sei_resolution:unresolved` rather than fabricating lineage;
`policy_boundary_check` per-file-degrades rather than silent-passing. The one
grep used this run was to locate a decorator call site to choose the right entity
id — orientation, not a data fallback.

The MCP surface is the **discovery tool** the CLI suite (a **gate tool**) is not.

---

## Outputs / housekeeping

- **New tracked issue:** `lacuna-0b21f65e82` (`lw-duplicate-locator`, SEI-keyed
  `loomweave:eid:1ff30e4e7054…`) — demonstrates trackability via the manual
  bridge. Planted lacuna left in place (not "fixed"; trap #5).
- **Observations for hub triage:** `lacuna-obs-1c7e6ddee5` (bridge, launch-gate),
  `lacuna-obs-cc01cb6424` (scope trap), `lacuna-obs-bdcb0cb0eb` (cells.toml doc).
- **Surface to hub PM (weft repo):** Friction A (loomweave→Filigree finding
  bridge) is launch-gate-relevant — feeds cutover `weft-4b2f948f70` / dogfood gate
  `weft-cd62a4da9b`. It is a dogfood *complaint* (expected-vs-actual tooling
  behaviour), filed as an observation per the brief; not an invariant collision,
  so not a PM escalation — but worth a line in the gate's known-gaps list.
- **Tree:** runtime DBs / `findings.jsonl` remain gitignored; only this report is
  a tracked change.
