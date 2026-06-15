# Post-Fix Validation Dogfood — REPORT (2026-06-15)

Confirming dogfood after a day of fixes. Run from a session rooted in
`/home/john/lacuna`, MCP-surface only (plus one CLI sanity for Fix E).

**Deployed:** loomweave 1.1.0-rc8 · legis 1.0.0 · filigree 3.0.0 ·
wardline 1.0.0rc4 · warpline 1.0.0 · live local embeddings server.
**Tree:** lacuna @ `56a3d95` (committed the Fix E `model: default` config to
clean the tree for the attest leg). Loomweave index fresh, 391 entities.

## Headline

**MCP-surface pass rate: 16/17 fully green; 1 partial (Fix B package-name scope).**
Four of five regression fixes hold cleanly; **Fix B holds for module qualnames
but not for top-level package names** — filed as new bug **lacuna-522ab56124**.
All 4 federation joins green; all 8 structural lacunae reachable.

---

## 0 — Preflight

| Check | Result |
|-------|--------|
| cwd `/home/john/lacuna` | ✅ |
| `WEFT_FEDERATION_TOKEN` exported | ✅ |
| `LEGIS_HMAC_KEY` exported | ⚠️ not in shell — but `legis doctor` `runtime.hmac_key: ok` ("no protected policies configured"); not a blocker (no policy routes to the protected cell) |
| 5 MCP servers routing to lacuna | ✅ filigree `:8749`, loomweave, wardline, legis, warpline |
| loomweave reports `1.1.0-rc8` | ✅ (CLI + fresh daemon) |
| Embeddings `127.0.0.1:8770/health` | ✅ 200 |

---

## 1 — Regression tests for today's fixes

### Fix B — `scope` by qualname — ⚠️ **PARTIAL** (module ✅ / package ❌)

| Call | Result | Verdict |
|------|--------|---------|
| `entity_dead_list(scope="specimen.dead_code")` | 2 rows incl. planted `specimen.dead_code.orphaned_helper` | ✅ |
| `entity_coupling_hotspot_list(scope="specimen.hub")` | 11 hotspots | ✅ |
| `entity_dead_list(scope="totally.bogus.name")` | honest empty `[]`, no error | ✅ |
| `entity_dead_list(scope="specimen")` | **only** `python:module:specimen` (the `__init__`), NOT `orphaned_helper` | ❌ |
| `entity_coupling_hotspot_list(scope="specimen")` | **0** (unscoped surfaces `specimen.hub.dispatch` coupling=10) | ❌ |
| `module_circular_import_list(scope="specimen")` | **0** (unscoped surfaces the `cycle_a`↔`cycle_b` cycle) | ❌ |

**Finding:** the fix resolves a dotted qualname to its **exact module namespace**
but does **not recurse into subpackages**. A top-level *package* name (`specimen`)
therefore returns only entities in its own `__init__` — and on edge-derived tools
(coupling, circular-import) that means **0**, reproducing the "silent-empty on a
package name" symptom the fix is named for, narrowed to parent names. The
originally-reported path-glob *misclassification* is gone (qualnames now resolve,
no error), and module-qualname scoping — the common case — works. Filed as
**lacuna-522ab56124** (P2/bug). Brief PASS bar ("a package/module-name scope
returns the same entities an unscoped call would, filtered, instead of 0") is met
for module names, missed for package names.

### Fix A — loomweave findings reach Filigree — ✅ **PASS**

`finding_list(scan_source="loomweave")` → exactly the 3 expected findings:

| Rule | Anchor | Issue |
|------|--------|-------|
| `LMWV-PY-TOO-COMPLEX` | `specimen/nesting_bomb.py` | prior demo issue (closed) |
| `LMWV-PY-SYNTAX-ERROR` | `specimen_quarantine.unparseable` | — |
| `LMWV-DUPLICATE-LOCATOR` | **file-anchored** `core:file:specimen/colliding.py` (severity high) | — (promoted, see A-residual) |

The duplicate-locator finding is **file-anchored, not project-anchored** (the prior
report's residual gap). Emit healthy: findings land in the project-scoped lacuna
store, no 400s. File-less facts (`LMWV-FACT-…WEAK-MODULARITY`) are correctly
**absent** — honestly skipped, never forced under a bogus path (`skipped_no_path=1`
observed on the analyze emit).

### Fix A-residual — native promote of duplicate-locator — ✅ **PASS**

`finding_promote(lacuna-sf-d074a7b921)` → created issue **lacuna-5d0e4ba6d7**
natively (no manual `issue_create` bridge), description carries project-relative
`specimen/colliding.py`. The ADR-029 entity attach gracefully degraded
(`attached:false` — local-registry file carries no content hash to baseline drift;
enrichment-only warning, the promote still succeeded). The residual gap from the
post-rc6 report is closed.

### Fix D — `policy_boundary_check` no longer vacuous-PASSes — ✅ **PASS**

| Call | Outcome | Verdict |
|------|---------|---------|
| `policy_boundary_check()` (no args) | `NO_ROOT` — echoes `scanned_root=/home/john/lacuna/src`, `repo_root=/home/john/lacuna`; refuses to clean-PASS a non-scanned root | ✅ (not a vacuous `PASS`) |
| `policy_boundary_check(repo_root=".", root="specimen")` | `FINDINGS` — surfaces `pinned_import` (the `lg-disabled-boundary-evidence` lacuna) on `specimen/policy_boundaries.py:43`, plus `validated_recovery` and a too-complex skip on `nesting_bomb.py` | ✅ |

### Embeddings — semantic search live — ✅ **PASS**

`entity_semantic_search_list(query="add a book to the library")` → ranked hits,
top two exactly as expected: `specimen.service.LibraryService.add_book` (0.83),
`specimen.cli._add_book` (0.80). Provider `local_openai`, model
`bge-small-en-v1.5` (384-dim), sidecar `embeddings.db` present with **311 vectors**.
No "not enabled" stub.

### Fix E — routine `loomweave analyze` no longer 400s its emit — ✅ **PASS** (CLI sanity)

Plain incremental `loomweave analyze` on the unchanged tree:
`posted findings … endpoint=…/api/v1/scan-results?project=lacuna emitted=0
skipped_no_path=1 created=0 updated=0 warnings=0` — **no `could not post`/400 WARN**.
**Bonus:** `loomweave config check` reports `Effective model: default` + **"No
warnings"** — `model: "default"` is a valid explicit opt-in, not flagged unset.

---

## 2 — Federation joins (MCP only) — 4/4 ✅

| Join | Evidence | Verdict |
|------|----------|---------|
| **J1** Wardline→Filigree emit | `wardline scan`: `filigree_emit reachable:true, updated:156, failed:0, auth_rejected:false, token_sent:true`, URL project-pinned `…/api/p/lacuna/…`. Sentinel **PY-WL-125** `active:1` (`specimen.preview_sinks.log_export_request`, log-injection sink) — correct, not baselined. | ✅ |
| **J2** Loomweave SEI keying | `wardline dossier specimen.service.LibraryService.add_book` → `sei: loomweave:eid:b033…`, `keyed_on_sei:true`, `linkages.available:true`, `identity_status:alive`. | ✅ |
| **J3** ADR-029 entity association | Bound issue `lacuna-5d0e4ba6d7` → `python:class:specimen.colliding.ShelfMark` (w/ content hash). `entity_association_list` (forward) and `entity_association_list_by_entity` (reverse) both return it; reverse with current hash → `freshness_status:"fresh"`. Freshness stamped both axes. | ✅ |
| **J4** Legis governance / attest | `policy_list`: 4 policies mapped to cells (chill keyless / coached needs LLM judge / structured human-loop / protected needs HMAC — gated cells reporting `enabled:false` is the intended tiering showcase per `cells.toml`). `policy_evaluate` returns an honest structured `UNKNOWN`+`provenance_gap` (not a vacuous pass). `wardline attest` → signed, SEI-keyed bundle (`dirty:false`, HMAC `key_id:3489e6c0`); `verify_attestation(reproduce=true)` → `signature_valid:true, reproduced:true, mismatches:[]`. | ✅ |

### Structural lacunae (MCP) — 8/8 reachable ✅

| Lacuna | Tool | Evidence |
|--------|------|----------|
| dead-code | `entity_dead_list` | `specimen.dead_code.orphaned_helper` |
| circular-import | `module_circular_import_list` | `specimen.cycle_a`↔`specimen.cycle_b` |
| coupling | `entity_coupling_hotspot_list` | `specimen.hub.dispatch` (coupling 10) |
| entry-point | `entity_entry_point_list` | `specimen.cli.main`, `tour.__main__.main` |
| subsystem | `entity_subsystem_get` | `core:subsystem:0846c0a5982a` "specimen" (6 members, modularity 0.328) |
| inheritance | `entity_relation_list(kind=inherits_from)` | `InMemoryRepository` → `Repository` |
| decorator | `entity_relation_list(kind=decorates)` | `specimen.service.audited` decorates `add_book` (`@audited("catalog")`) |
| call-chain | `entity_execution_path_list` | `dispatch` → `_audit`/`_format`/`_meter`/`_persist`/`_route` |

---

## 3 — Known traps (correctly NOT mis-scored)

- Sentinel `wl-log-injection` (PY-WL-125): `1 active` — correct, not baselined.
- Warpline: enrich-only, not pass/fail-scored (not exercised here).
- No planted lacuna was "fixed".

---

## 4 — Prior frictions: status

| Prior (post-rc6) open item | Now |
|----------------------------|-----|
| Friction A — file-less / project-level findings don't emit | **Resolved** — `LMWV-DUPLICATE-LOCATOR` is file-anchored & promotable; genuinely file-less facts correctly skipped |
| Friction A-residual — duplicate-locator not promotable | **Resolved** — native `finding_promote` → issue lacuna-5d0e4ba6d7 |
| Friction D — `policy_boundary_check` vacuous PASS | **Resolved** — no-arg → `NO_ROOT`; explicit → `FINDINGS` |
| Friction B — `scope` untested | **Tested → PARTIAL** — module qualnames ✅; package-name recursion ❌ (new bug **lacuna-522ab56124**) |
| Embeddings off | **Resolved** — live, 311 vectors, ranked hits |

### New finding filed
- **lacuna-522ab56124** (P2/bug) — loomweave rc8 `scope`-by-qualname resolves the
  exact module but does not recurse into subpackages; a package name returns 0 on
  coupling / circular-import.

**Verdict: confirming run substantially green (16/17 MCP-surface checks).** Four of
five regression fixes fully hold; the day's emit/promote/boundary-check/embeddings
fixes are confirmed end-to-end. The one gap (Fix B package-name recursion) is
narrow, filed, and does not block any join.
