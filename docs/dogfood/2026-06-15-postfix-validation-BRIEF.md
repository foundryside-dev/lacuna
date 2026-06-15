# Post-Fix Validation Dogfood — RUN BRIEF (2026-06-15)

**Run from a session rooted in `/home/john/lacuna`.** This run is the
confirming dogfood after a day of fixes. It does two things: (1) **regression-test
every fix landed today** (they were broken in the last report), and (2) re-confirm
the 4 joins + structural lacunae are still green. Deployed now:
**loomweave 1.1.0-rc8 · legis 1.0.0 (D-fix) · filigree 3.0.0 · wardline 1.0.0rc4 ·
warpline 1.0.0**, plus a **live local embeddings server**.

> Supersedes `2026-06-15-...post-rc6` report friction list. The prior report's
> open items — residual Friction A (file-less findings), Friction D (vacuous
> PASS), Friction B (untested), and embeddings (off) — are all addressed. **Verify
> them; don't re-file them.**

---

## 0 — Preflight (abort if any fails)

- cwd `/home/john/lacuna`; `WEFT_FEDERATION_TOKEN` + `LEGIS_HMAC_KEY` exported.
- **5 MCP servers** attached and routing to lacuna (filigree `:8749`, loomweave,
  wardline, legis, warpline). The loomweave/legis daemons must be **fresh** (this
  session, so they carry rc8 / the D-fix) — confirm loomweave reports
  `version 1.1.0-rc8` (e.g. via its doctor/status surface) before scoring.
- Embeddings server up: `curl -s 127.0.0.1:8770/health` → 200.

---

## 1 — Regression tests for today's fixes (the headline of this run)

### Fix B — `scope` by qualname (was: silent-empty on a package name)
- `entity_dead_list(scope="specimen")` → **expect dead-code rows** (e.g.
  `specimen.dead_code.orphaned_helper`). Previously a bare package name returned
  **0** (misclassified as a path glob).
- Repeat with `scope="specimen.dead_code"` and on
  `module_circular_import_list` / `entity_coupling_hotspot_list` — a dotted
  qualname scope must now resolve to entities, not silently match nothing.
- Negative control: `scope="totally.bogus.name"` → honest empty (falls back to a
  path glob), not an error.
- **PASS if** a package/module-name scope returns the same entities an unscoped
  call would (filtered), instead of 0.

### Fix A (all four layers + residual) — loomweave findings reach Filigree
- `finding_list(scan_source="loomweave")` → **expect ≥3 findings**, including
  `LMWV-PY-TOO-COMPLEX`, `LMWV-PY-SYNTAX-ERROR`, **and `LMWV-DUPLICATE-LOCATOR`**.
  The duplicate-locator one must be **file-anchored** (`specimen/colliding.py`),
  not project-anchored. (Last report: it was *not* in the store — the residual gap.)
- `finding_promote` the `LMWV-DUPLICATE-LOCATOR` finding → **creates an issue
  natively** (no manual `issue_create` bridge). This is the residual-A fix.
- Confirm the emit is healthy: findings carry **project-relative paths**, the
  endpoint is **project-scoped** (`?project=lacuna`), no 400s.
- **Correct (not a regression):** genuinely file-less facts (e.g.
  `LMWV-FACT-...WEAK-MODULARITY`, a subsystem-level fact) are **absent** from the
  store — they have no real file path, so they are honestly skipped, never forced
  under a bogus path. Note them as *expected store-only*, do not file as a gap.

### Fix D — legis `policy_boundary_check` no longer vacuous-PASSes
- `policy_boundary_check()` **with no args** → **expect `outcome: "NO_ROOT"`**
  (NOT `PASS`), with `scanned_root` / `repo_root` echoed in the result. Previously
  a bare call returned a vacuous `PASS` (the silent-clean footgun, peer of
  `weft-ef2e898642`).
- `policy_boundary_check(repo_root=".", root="specimen")` → **`outcome:
  FINDINGS`**, surfacing `pinned_import` on `specimen/policy_boundaries.py`
  (the `lg-disabled-boundary-evidence` lacuna).
- **PASS if** the no-arg call refuses to report a clean PASS over a non-scanned
  root, and the explicit call surfaces the planted finding.

### New capability — semantic search (embeddings) is live
- `entity_semantic_search_list(query="add a book to the library")` (or the live
  tool name) → **expect ranked entity hits** (e.g. `specimen.cli._add_book`,
  `specimen.service.LibraryService.add_book`). Previously the tool degraded to
  "not enabled".
- Confirm the provider is `local_openai`, model `bge-small-en-v1.5` (384-dim),
  sidecar `embeddings.db` populated (~311 vectors).
- **PASS if** a natural-language query returns semantically-relevant entities,
  not a "semantic search not enabled" stub.

### Fix E (rc8) — a routine `loomweave analyze` no longer 400s its emit
- Run a plain **`loomweave analyze`** (default incremental mode) on the unchanged
  tree from a shell. Previously this 400'd with `mark_unseen=True requires at
  least one finding or scanned path` (an incremental no-op POSTed an empty
  sweep-batch). **Expect** `posted findings ... emitted=0 ... warnings=0` and **no
  `could not post`/400 WARN**. (Optional sanity, not an MCP-surface call.)
- Bonus: `llm_policy.codex_cli.model: "default"` is now a valid explicit opt-in —
  `loomweave config check` / `doctor` should NOT warn "model is unset" when it's
  set to `default`.

---

## 2 — Re-confirm the 4 federation joins (should still be green, via MCP only)

| Join | Confirm |
|------|---------|
| **J1** Wardline→Filigree emit | `wardline scan` emits; sentinel `PY-WL-125` active |
| **J2** Loomweave SEI keying | `wardline dossier <qualname>` → non-null `sei`, `linkages.available:true` |
| **J3** ADR-029 entity association | `entity_association_list` + `_list_by_entity` both directions; freshness stamped |
| **J4** Legis governance / attest | `policy_list` cells enabled; `wardline attest` → `verify_attestation reproduced:true` |

Plus the 8 structural lacunae (dead-code, circular-import, coupling, entry-point,
subsystem, inheritance, decorator, call-chain) reachable via MCP.

---

## 3 — Known traps (unchanged — do not mis-score)
- Sentinel `wl-log-injection` (PY-WL-125): `1 active` is correct, do not baseline.
- Warpline demos are enrich-only, not pass/fail-scored.
- Wrong-project routing = session-rooting artifact, not a bug.
- Don't "fix" any planted lacuna.

---

## 4 — Output
- Write `docs/dogfood/2026-06-15-postfix-validation-report.md` with a **per-fix
  verdict** (B / A / A-residual / D / embeddings — each PASS/FAIL with the MCP
  evidence), the 4-join confirmation, and an MCP-surface pass rate.
- The prior report's open frictions should now read **resolved**; if any fix does
  NOT hold, that is a real new finding — file it and surface it to the hub.
- File any genuinely new defect in lacuna's Filigree (`:8749`). Leave the tree
  clean (commit regen docs before any verify leg; keep DBs/`findings.jsonl`
  gitignored).
