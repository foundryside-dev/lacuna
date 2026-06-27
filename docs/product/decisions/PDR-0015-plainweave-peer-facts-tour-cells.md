# PDR-0015 — Tour exercises Plainweave's peer-facts producers (plainweave+wardline, plainweave+warpline)

- **Date:** 2026-06-28
- **Status:** Accepted (under the standing tour-regression grant; sibling-repo tasking from Plainweave)
- **Decider:** agent (ultracode, subagent-driven)
- **Related:** PDR-0010 (plainweave reachable, the intent leg this extends), PDR-0012/0013/0014 (MCP-attachment harness), Plainweave PDR-015 (the CLI parity this depends on), `tour/lacunae.toml` (manifest), `docs/matrix.md`

## Context

Plainweave 1.1 shipped two cross-member peer-facts producers —
`weft.plainweave.wardline_peer_facts.v1` and `weft.plainweave.requirements_enrichment.v1`
— but they were MCP-only and the cross-member tour did not exercise either. The matrix
had `plainweave` and `plainweave+loomweave` but no `plainweave+wardline` /
`plainweave+warpline` cell, so two shipped capabilities had no regression guard in the
suite. Plainweave closed the CLI parity gap (its PDR-015); this is the Lacuna-side half.

## Decision

Add two advisory, local-only, deterministic tour legs over the new CLI surfaces, each
asserting the **load-bearing no-silent-clean invariant**, not just happy paths:

- **`pw-requirements-enrichment`** (`plainweave+warpline`) — over the covered+uncovered
  seed: a covered surface reports `present` (non-empty requirements); the recorded-but-
  unbound orphan reports `absent`; a well-formed-but-absent locator reports `unavailable`
  (an identity gap is "cannot tell", NEVER a silent `absent`). All three must hold to
  surface the fact.
- **`pw-wardline-peer-facts`** (`plainweave+wardline`) — over a frozen, tour-time two-
  snapshot `.wardline/` fixture with scan-identity manifests: an active defect and a non-
  defect finding surface; a finding gone from the latest in-scope snapshot is reported
  `resolved_or_unseen`; an out-of-scope prior finding is honestly flagged
  `wardline_scope_mismatch` (never silently resolved); an absent `.wardline/` is
  `freshness=unavailable` (never clean).

Two design choices keep both legs deterministic and offline:
- the wardline fixture is generated in a temp workspace from frozen constants (Lacuna's
  live `.wardline/` is a volatile rolling window with no scan manifest);
- the enrichment leg seeds in an isolated workspace holding a copy of the Loomweave
  catalog but **no `ephemeral.port`**, so creating the accepted trace link a `present`
  result needs resolves identity locally instead of depending on a live Loomweave HTTP
  endpoint.

## Consequences

- `docs/matrix.md` gains `plainweave+wardline` and `plainweave+warpline`;
  `make verify` is green (every live lacuna surfaced; narrative in lockstep); the manifest
  count test and `docs/flaws/` are updated.
- The tour now **requires an installed plainweave that carries the two new subcommands**
  (Plainweave PDR-015). Until that build is installed, the two legs degrade to `[WARN]`
  and `make verify` reds on the two new lacunae — the expected dependency, not a defect.
- `tour/plainweave_seed.py` gains opt-in `with_trace_links` and a `root` parameter plus a
  `materialize_workspace()` helper; the intent leg's behavior is unchanged (it uses the
  defaults).

## Clean-checkout prerequisites (owner handoff — two environment items, not code defects)

`make verify` is green in the authoring environment, but reproducible green on a **fresh
clone** needs two owner actions; neither is a defect in the two demos (both are
determinism-clean, with unit + per-conjunct drop-tests and real-producer integration
smokes passing):

1. **Install the updated `plainweave`.** The tour shells out to `~/.local/bin/plainweave`,
   which must carry the new `wardline-peer-facts` / `requirements-enrichment` subcommands
   (Plainweave PDR-015). `uv tool install` currently fails on a **pre-existing Plainweave
   packaging bug**: `[tool.hatch.build.targets.wheel.force-include]` re-includes
   `src/plainweave/web/static`, so hatchling double-adds `plainweave/web/static/.gitkeep`
   ("A second file is being added to the wheel archive at the same path"). Fix that
   (e.g. drop `.gitkeep` from the force-included tree), then install. Verified here against
   an editable build of the Plainweave feature branch.
2. **Regenerate `docs/tour.md` on a clean tree.** The pre-existing `legis govern` leg bakes
   git-tree-cleanliness into the byte-locked narrative (it `[WARN]`s on a dirty tree, signs
   `[PASS]` on a clean one). This branch's `make tour` ran while concurrent, un-owned
   changes (`AGENTS.md`, `CLAUDE.md`, …) left the tree dirty, so the committed `tour.md`
   shows `[WARN] legis govern`. On a clean checkout, `make tour` regenerates `[PASS]`
   automatically — re-run it after item 1 and recommit. (`docs/matrix.md` is
   manifest-derived and tree-independent, so its two new cells are already correct.)

## Reversal trigger

If Plainweave reopens either `.v1` item shape (its PDR-015 reversal trigger), these legs
follow — they assert status/contract semantics, not byte-pinned shapes, so a structure-
pinned change survives. If a future Wardline scan-identity contract changes the
`scan_manifest` record, the frozen wardline fixture is updated in lockstep.
