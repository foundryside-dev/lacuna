# Final MCP-Surface Dogfood — REPORT (2026-06-14 brief; re-run 2026-06-15 post-rc6)

**Run from a session rooted in `/home/john/lacuna`** (mandatory — MCP tools
resolve against the project's own `.mcp.json`). Companion to the same-day
CLI-only run (`2026-06-14-cli-only-redogfood-report.md`, verdict **1/12**). This
report measures the **MCP agent surface** — the experience a real agent has.

Deployed versions (confirmed live): **wardline 1.0.0rc4 · loomweave 1.1.0-rc5 ·
filigree 3.0.0 · legis 1.0.0 · warpline 1.0.0**.

> **Supersedes the pre-rc6 measurement** committed in `49b09c6`. That run was
> taken *before* the two config commits that landed after it —
> `c5450d1` ("close loomweave→Filigree emit gap + correct cells.toml coached-lane
> doc") and `13e2e4d` ("pin integrations.filigree.project=lacuna for loomweave
> emit"). This re-run measures the **post-fix deployed state at HEAD `13e2e4d`**.
> The headline change: the prior run's launch-gate friction (Friction A — loomweave
> findings never reaching Filigree's store) is now **substantially resolved**, and
> two of its three frictions (A, C) are closed. See **Delta since prior report**.

---

## Verdict

**MCP-surface pass rate: 12 / 12 in-scope lacunae reachable via MCP, vs the
CLI-only run's 1 / 12. All 4 federation joins PASS via MCP only — zero raw-SQLite
or raw-HTTP fallbacks.**

Every lacuna the CLI-only agent could not see — the 8 Loomweave structural/
navigation queries, the 2 Loomweave findings-table archaeology items, and the
Legis governance lacuna — is reachable through the MCP surface. **New this run:**
the loomweave→Filigree finding bridge now carries file-anchored structural
findings into Filigree's store, so `lw-too-complex` is promotable *natively* via
`finding_promote` (no manual workaround) — proven end-to-end below. The discovery
story holds and strengthens: **the MCP surface is the discovery tool the CLI is
not.**

One **residual** launch-gate friction remains (the bridge is partial: project-
level / file-less loomweave findings such as `lw-duplicate-locator` still do not
emit). One inherent sharp edge on ADR-029 auto-attach for degraded files. Both
are recorded below for the hub gate's known-gaps list; neither blocks a join.

---

## Delta since the prior (pre-rc6) report `49b09c6`

| Prior friction | Prior severity | Status now | Evidence this run |
|----------------|----------------|------------|-------------------|
| **A** — loomweave findings never reach Filigree's store; `finding_promote` path can't complete | launch-gate | **Partially resolved** | `finding_list scan_source=loomweave` now returns **2** findings (`LMWV-PY-TOO-COMPLEX` `lacuna-sf-9be178c53a`, `LMWV-PY-SYNTAX-ERROR` `lacuna-sf-d58a1a8048`); `finding_promote` of the too-complex finding created issue `lacuna-aedc466d84` natively. Residual gap below. |
| **C** — `cells.toml` claims keyless coached returns `enabled:true`; live says `false` | low (doc) | **Fixed** | `policy/cells.toml:10-12` now documents coached as judge-requiring; `enabled:false` without a provider is "honest gating, not a key gap" — matches live `policy_list`. |
| **B** — loomweave `scope` param is a full entity-ID prefix match; package-name scope silently empty | medium | **Not re-tested** this run (no scoped query exercised); carried forward as open. |

Also improved incidentally: `lw-entry-point` now surfaces **directly** via
`entity_entry_point_list` (the `entry-point` tag is emitted) — the prior run
needed the alternate `entity_tag_list(cli-command)` facet.

---

## Preflight (all PASS)

| Check | Result |
|-------|--------|
| cwd / branch | `/home/john/lacuna`, `main`, tracked tree clean |
| Secrets | `WEFT_FEDERATION_TOKEN` set, `LEGIS_HMAC_KEY` set |
| 5 MCP servers attached + routing to lacuna | filigree `:8749`; loomweave (`project_root=/home/john/lacuna`, `sei.populated:true`, db `…/.weft/loomweave/loomweave.db`); wardline (`fresh:true`, `filigree.auth ok`, pid 1286600); legis (`install.filigree_scope` → `…/api/p/lacuna/…`, `runtime.hmac_key ok`); warpline (`local_only:true`) |
| Index freshness | loomweave index analyzed at `c5450d19` (HEAD `13e2e4d`, +1 config commit); `staleness:stale` from config-file churn only — `specimen/` entity graph intact ⇒ structural queries valid. Warpline snapshot `commits_behind:1` (DELTA). Both honest, non-material. |

---

## 4 Federation Joins — all PASS via MCP

| Join | Verdict | MCP evidence |
|------|---------|--------------|
| **J1** Wardline→Filigree emit | **PASS** | `wardline scan` (MCP): `filigree_emit{reachable:true, updated:156, failed:0, token_sent:true, auth_rejected:false, destination.project_pinned:true}`, url `…/api/p/lacuna/weft/scan-results`; `loomweave_write{written:227}`. Gate `NOT_EVALUATED` (no `--fail-on`), `would_trip_at:ERROR`. `finding_get lacuna-sf-4cb261e690` asserts `scan_source=wardline`, `issue_id=lacuna-2a54dfb59d`, `rule_id=PY-WL-125`, `suppression_state=null` (active — the sentinel, trap #1 honoured). |
| **J2** Loomweave SEI keying | **PASS** | `entity_find log_export_request` → SEI `loomweave:eid:4b0ed3a633fd3a572a9e1537e590f0a0` (no DB touch). `wardline dossier specimen.preview_sinks.log_export_request` → `sei` non-null, `keyed_on_sei:true`, `linkages.available:true` (callee `read_report_field`), `work.available:true` joined to `lacuna-2a54dfb59d`. **Exactly the CLI gap (`sei:null`) closed.** |
| **J3** ADR-029 entity association (both directions) | **PASS** | Forward: `entity_association_list(lacuna-2a54dfb59d)` → the SEI binding. Reverse: `entity_association_list_by_entity(loomweave:eid:4b0ed3a…, current_content_hash=70e5b154…)` → issue `lacuna-2a54dfb59d`, `freshness_status:fresh` (drift detection live). `entity_association_add` idempotent (refreshed `attached_at` to 00:35:08, preserved original `attached_by`). **CLI surface has no verb here — MCP delivers.** |
| **J4** Legis governance / closure + attestation | **PASS** | `policy_list`: `structured` cell `enabled:true` (human-in-loop), `protected` `enabled:true` (judge_inline) ⇒ `LEGIS_HMAC_KEY` live (**not** CELL_NOT_ENABLED). `filigree_closure_gate_get(lacuna-2a54dfb59d)` → honest `allowed:false` ("no verified governance binding"). `wardline attest` (clean tree, `dirty:false`) → HMAC-SHA256 bundle `key_id:3489e6c0`, SEI-keyed (`sei_source:loomweave`, 30/33 boundaries proven, `coverage_pct:93.9`); `verify_attestation reproduce=true` → `signature_valid:true, reproduced:true, mismatches:[]`. |

**Joins: 4/4 PASS** (CLI run: J1 PASS, J2 PARTIAL, J3 PARTIAL, J4 PASS-with-caveats). No fallbacks.

---

## 8 (+2) Structural Lacunae — the core delta vs the CLI run

| Lacuna | MCP query | Surfaced? | Evidence |
|--------|-----------|-----------|----------|
| `lw-dead-code` | `entity_dead_list` | **YES** | `specimen.dead_code.orphaned_helper` (+ `specimen.hub.*`, `specimen.pipeline.*`); 141 dead candidates total, rust plugin honestly excluded (no root tags) |
| `lw-circular-import` | `module_circular_import_list` | **YES** | 1 cycle: `specimen.cycle_a ↔ specimen.cycle_b` (length 2, `confidence:resolved`) |
| `lw-coupling-hotspot` | `entity_coupling_hotspot_list` | **YES** | top `tour.__main__._drive` (coupling 19); `specimen.hub.dispatch` (10); 203 ranked |
| `lw-entry-point` | `entity_entry_point_list` | **YES (direct)** | `specimen.cli.main`, `tour.__main__.main` (tag `entry-point`) — prior run needed the `cli-command` facet; now native |
| `lw-subsystem` | `entity_find kind=subsystem` | **YES** | 26 subsystems (e.g. `core:subsystem:018f62de5fe8…`); `project_status_get` confirms `subsystems:26` |
| `lw-inheritance` | `entity_relation_list(Entity, in, inherits_from)` | **YES** | `specimen.models.Book` & `specimen.models.User` inherit `Entity` (lines 70, 83) |
| `lw-decorator` | `entity_relation_list(audited, out, decorates)` | **YES** | `specimen.service.audited` decorates `LibraryService.add_book` (`@audited("catalog")`) & `register_user` (`@audited("register")`) |
| `lw-call-chain` | `entity_execution_path_list(dispatch)` | **YES** | `specimen.hub.dispatch` → `_audit / _format / _meter / _persist / _route` |
| `lw-too-complex` | `project_finding_list` → **`finding_promote`** | **YES (discover + tracked NATIVELY)** | `LMWV-PY-TOO-COMPLEX` on `specimen/nesting_bomb.py`; bridged to Filigree (`lacuna-sf-9be178c53a`); `finding_promote` → issue `lacuna-aedc466d84`. **No manual bridge needed (delta vs prior run).** |
| `lw-duplicate-locator` | `project_finding_list` | **YES (discover only)** | `LMWV-DUPLICATE-LOCATOR` (`specimen.colliding.ShelfMark`, declared twice). **Not** in Filigree's store (`scan_source=loomweave` returns only file-anchored findings) — anchors to `core:project:lacuna` (file-less). `finding_promote` cannot reach it; trackable only via manual `issue_create`. **Residual Friction A.** |

All 8 navigation/structure lacunae the CLI run scored **invisible (MCP-only)** are
reachable. Every loomweave row that resolves to an entity is honest: `briefing_blocked:"secret_present"`
rows in the coupling list are withheld with a reason, not fabricated.

---

## Legis policy-boundary trap (#3) — default root silently passes; explicit root surfaces it

CLI friction F7: `legis policy-boundary-check` exits 0 because `nesting_bomb.py`
raises `RecursionError`, masking the `pinned_import` finding.

**MCP `policy_boundary_check` reproduces a silent-pass *by default*, but for a
different reason than the CLI:** with no args it defaults `repo_root` to the
**server's own source root** (legis), not the session project — so it scans
legis's `src/`, finds nothing about lacuna, and returns `outcome:PASS, findings:[]`.
This is the same class as the known `--root`-empty silent-clean bug
(`weft-ef2e898642`).

**Pointed at lacuna explicitly — `policy_boundary_check(repo_root=/home/john/lacuna,
root=/home/john/lacuna/specimen)` → `outcome:FINDINGS` (3):**
- `POLICY_BOUNDARY_FILE_TOO_COMPLEX` on `specimen/nesting_bomb.py` — *"nesting too deep to analyze; file skipped, scan continued (per-file degrade)"* (degrades, does not crash the scan)
- `POLICY_BOUNDARY_TEST_FINGERPRINT_MISMATCH` on `specimen/policy_boundaries.py:43` — **`pinned_import`** (the masked finding, surfaced — no `sys.setrecursionlimit` workaround needed)
- `POLICY_BOUNDARY_TEST_FINGERPRINT_MISMATCH` on `:30` — `validated_recovery`

**Verdict on the trap:** the MCP tool *can* surface `pinned_import` cleanly (an
improvement over the CLI's crash-mask), but the **no-arg default-root footgun
persists** — a tool that defaults to scanning its own server source returns a
vacuous green for the session project. Flagged for the hub (Friction D).

---

## Warpline (5th member) — enrich-only, captured, NOT pass/fail-scored

All four advisory demos on `specimen.cli._add_book` (SEI `loomweave:eid:dc1e5d19…`,
no `LACUNA` docstring by design) enrich and never gate; every response
`meta.local_only:true`, `peer_side_effects:[]`, `enrichment` a closed vocab
(`present|absent|unavailable`).

| Demo | Result |
|------|--------|
| `wp-churn` | `churn_count:0`, `last_changed_at:null` — `_add_book` not yet in a captured snapshot; honest zero, not error |
| `wp-timeline` | empty; `sei:null`, `sei_resolution:"unknown"` (warpline keys on locators, never claims lineage) |
| `wp-blast-radius` | `completeness:DELTA`, `staleness{snapshot_commit:c5450d19, commits_behind:1}`, `changed:[] affected:[]` with explicit `DELTA: graph snapshot is partial` warning |
| `wp-reverify` | `HEAD~3..HEAD` worklist: `loomweave.yaml`, `policy/cells.toml`, this report — each with `suggested_verification`; `enrichment.sei:absent` (honest, never fabricated) |

---

## Head-to-head scoreboard (same 12-item denominator as the CLI run)

| # | Lacuna | CLI-only | MCP surface |
|---|--------|----------|-------------|
| 1 | `wl-log-injection` (sentinel) | ✅ surfaced+tracked | ✅ J1 (active, `lacuna-2a54dfb59d`, `suppression_state:null`) |
| 2 | `lw-dead-code` | ❌ MCP-only | ✅ `entity_dead_list` |
| 3 | `lw-circular-import` | ❌ MCP-only | ✅ `module_circular_import_list` |
| 4 | `lw-call-chain` | ❌ MCP-only | ✅ `entity_execution_path_list` |
| 5 | `lw-coupling-hotspot` | ❌ MCP-only | ✅ `entity_coupling_hotspot_list` |
| 6 | `lw-entry-point` | ❌ MCP-only | ✅ `entity_entry_point_list` (now direct) |
| 7 | `lw-subsystem` | ❌ MCP-only | ✅ `entity_find kind=subsystem` (26) |
| 8 | `lw-inheritance` | ❌ MCP-only | ✅ `entity_relation_list inherits_from` |
| 9 | `lw-decorator` | ❌ MCP-only | ✅ `entity_relation_list decorates` |
| 10 | `lw-too-complex` | ❌ no promote path | ✅ discovered + **tracked natively** (`finding_promote` → `lacuna-aedc466d84`) |
| 11 | `lw-duplicate-locator` | ❌ no promote path | ⚠️ discovered; **not** bridged (file-less) → manual `issue_create` only (residual Friction A) |
| 12 | `lg-disabled-boundary-evidence` | ⚠️ workaround only | ✅ `policy_boundary_check` surfaces `pinned_import` (with explicit root) |

**CLI-only: 1/12. MCP surface: 12/12 reachable** (10 cleanly, `lw-too-complex` now
also cleanly *tracked*, `lw-duplicate-locator` discoverable but not auto-bridgeable).

---

## Friction log (every fallback / deviation — a fallback IS the finding)

| # | Severity | Friction | Detail | Disposition |
|---|----------|----------|--------|-------------|
| **A (residual)** | **launch-gate** | loomweave→Filigree bridge is **partial** | File-anchored loomweave findings (`LMWV-PY-TOO-COMPLEX`, `LMWV-PY-SYNTAX-ERROR`) now emit to Filigree and are natively `finding_promote`-able (delta vs prior run, ✅). **But** project-level / file-less findings (`LMWV-DUPLICATE-LOCATOR` → `core:project:lacuna`) and secret findings do **not** emit — so `lw-duplicate-locator` still has no native promote path. Fix: extend the loomweave emit to project-anchored findings, or document `issue_create` as the intended path for file-less findings. | Surfaced to hub (below) |
| **B (carried)** | medium | loomweave `scope` param is a full entity-ID prefix match; package-name scope silently empty | From prior run; **not re-tested** this session. Carried forward open. | Carried |
| **D (new)** | medium | `legis policy_boundary_check` no-arg default `repo_root` is the **server's own source root**, not the session project → vacuous `PASS` (silent-clean) | Same class as `weft-ef2e898642`. Surfaces correctly only with explicit `root`/`repo_root`. An agent calling it bare reads a false green. Fix: default `repo_root` to the session/project root (or refuse with a NO_ROOT diagnostic) instead of the server source. | Surfaced to hub (below) |
| **E (new, minor)** | low | `finding_promote` of a file-anchored loomweave finding cannot auto-attach the ADR-029 association | `lacuna-aedc466d84`: `entity_attachment.attached:false` — degraded/unparseable file record (`core:file:specimen/nesting_bomb.py`) carries no content hash to baseline; tool correctly points to `finding_promote_and_attach_entity` with explicit `content_hash`. Inherent to too-complex-to-parse files; a sharp edge, not a defect. | Noted |

No raw-SQLite or raw-HTTP fallbacks were needed (the CLI run needed 7). Every join
and lacuna was reached through MCP tools.

---

## "Prefer MCP over grep?" verdict

**YES.** Where the CLI run fell back to direct SQLite (`sei_bindings`, `edges`,
`findings`) and raw HTTP (entity-associations) **7 times**, the MCP surface
answered every join and every structural query natively, with zero fallbacks. The
MCP tools are honest about their limits — `entity_dead_list` excludes the rust
plugin (no root tags) rather than false-flagging it dead; `wardline dossier`
freshness-stamps both identity and content; warpline marks `sei_resolution:unknown`
and `enrichment.sei:absent` rather than fabricating lineage; `policy_boundary_check`
per-file-degrades rather than crashing. The two grep/`jq` touches this run were to
read the oversized `wardline scan` payload from disk and inspect `cells.toml` —
orientation, not data fallbacks.

The MCP surface is the **discovery tool** the CLI suite (a **gate tool**) is not.

---

## Outputs / housekeeping

- **Demo issue (cycled clean):** `lacuna-aedc466d84` — promoted from loomweave
  finding `lacuna-sf-9be178c53a` to prove the now-working native bridge, then
  closed (`close_reason` records it as the MCP-redogfood demonstration). Planted
  lacuna (`nesting_bomb.py`) left in place (not "fixed"; trap #5).
- **No genuinely new defect filed:** the residual bridge gap (A) and the
  policy-boundary default-root footgun (D) are tooling frictions surfaced for the
  hub, not new lacuna-side defects; E is inherent. Nothing fabricated to fill a quota.
- **Surface to hub PM (weft repo):** Friction **A (residual, launch-gate)** and
  **D (new, default-root silent-pass)** are launch-gate-relevant — feed cutover
  `weft-4b2f948f70` / dogfood gate `weft-cd62a4da9b`. Both are dogfood *complaints*
  (expected-vs-actual tooling behaviour), not invariant collisions ⇒ known-gaps
  entries, not PM escalations. This report is the surface (lacuna-rooted session;
  no cross-into-weft, per the wrong-project rule).
- **Tree:** runtime DBs / `findings.jsonl` / `.env` remain gitignored; only this
  report is a tracked change.
