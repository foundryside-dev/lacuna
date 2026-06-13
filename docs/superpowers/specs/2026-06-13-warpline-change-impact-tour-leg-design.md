# Warpline Change-Impact Tour Leg — Design

**Date:** 2026-06-13
**Status:** approved (brainstorming → spec)
**Goal:** Bring **warpline** onto Lacuna's demonstrated surface as a first-class
federation member, at parity with wardline/loomweave/legis/filigree. Warpline is
the fifth launch-control tool now live at the agent-tooling layer (MCP server,
skill pack, CLAUDE.md/AGENTS.md) but **absent from the tour and manifest** — an
agent can reach for it, but the tour does not prove it works.

## The core problem this solves

The other four members fit a **plant-a-flaw → tool-surfaces-it** model. Warpline
does not: it is the temporal / change-impact authority ("if I touch X, what
breaks, and what must I re-verify?"), and it is **advisory, enrich-only, and
never gates** (`meta.local_only: true`, `peer_side_effects: []`, `enrichment` a
closed `present|absent|unavailable` vocab). There is no flaw for it to catch.

So warpline's demonstration leg asserts **change-impact correctness over a frozen
anchor** instead of flaw detection — a positive-capability demonstration. This
mirrors the established loose use of "lacuna" in the manifest, where
`lw-entry-point` / `lw-inheritance` already catalogue *facts a tool surfaces*,
not defects.

## Empirical grounding (verified live, 2026-06-13)

All claims below were confirmed against the live `warpline` CLI on this repo:

- `warpline changed --rev-range A..B` is **deterministic** for fixed commits and
  returns changed entities with both a stable git-derived **locator**
  (`python:function:specimen/cli.py::_add_book`) and an **integer `key_id`**.
- `warpline blast-radius --changed-entity-key-id K --depth D` traverses **outbound
  call/reference edges** with per-edge provenance (`via_edges`,
  `from/kind/to`). High-out-degree **orchestrators** have rich radii; leaf data
  classes (`Money`, `Entity`) return **empty**. This corrected an initial
  assumption that high-fan-in helpers would be the rich anchors — they are not.
- `warpline reverify --changed-entity-key-id K --depth D` returns a worklist with
  `reason: changed|downstream`, `why` provenance, `staleness.snapshot_commit`,
  and `completeness: DELTA`.
- `warpline churn --locator L` and `warpline timeline --entity L` take **locators
  directly** (no key_id needed).
- **key_ids renumber on re-ingest; locators are stable.** The leg must key off
  locators and resolve key_ids at runtime.
- The edge snapshot is `partial`/`DELTA`, and `.weft/warpline/warpline.db` is
  **gitignored** (the project's runtime-DB-stay-gitignored constraint). The
  affected *set* can therefore vary by environment/snapshot freshness.

### The anchor: `specimen/cli.py::_add_book`

Chosen because it uniquely satisfies **all four** capabilities at once:

- **blast-radius:** 6 affected entities, depth 1–2, spanning
  `cli`→`service`→`repository`→`models` — reaches `LibraryService.add_book`,
  `InMemoryRepository.add`, `Book`, `Genre`, `App`, the `specimen.cli` module. A
  genuinely cross-module "if I touch add-book, here is everything to re-verify."
- **churn:** `churn_count = 1`. **timeline:** 1 entry. Both non-empty (it is
  within warpline's ingest horizon, unlike `read_report_field` which returned
  `churn_count: 0`).

The **frozen expected downstream** asserted for membership is
`python:function:specimen/service.py::LibraryService.add_book` — the service
method `_add_book` delegates to, a permanent structural edge.

## Design

### Architecture

One new tour step, `warpline_change_impact()` in `tour/steps.py`, registered in
`tour/__main__.py::_drive` after the loomweave legs. It follows the
**`filigree work cycle` / `wardline fail-closed` discipline**: a live assertion
gates `ok`, but `detail` is **frozen prose** and `surfaced` carries only stable
`(token, qualname)` pairs. Counts, key_ids, timestamps, set sizes, and snapshot
commits **never** enter `detail` or `surfaced` — they all flap and would break
the byte-for-byte `make verify` lockstep.

### Step behavior

1. **Ensure snapshot** — warpline's index must exist before querying. The step is
   self-populating, exactly as `loomweave_analyze` is the leg that populates the
   loomweave DB: it ensures a captured snapshot (warpline's only mutating command,
   `capture-snapshot`, writes `.weft/warpline/` only) before its read queries. If
   warpline is not installed or the snapshot cannot be built, the step returns
   `ok=False` with a stable "unavailable" detail (no `surfaced`).
2. **Resolve key_id at runtime** — from `warpline changed` over a **pinned
   historical rev-range** that includes `_add_book`, match by locator → `key_id`.
   Never hardcode the integer.
3. **blast-radius(key_id)** — assert `…service.add_book` ∈ affected locators.
4. **reverify(key_id)** — assert `…service.add_book` present with
   `reason=downstream`.
5. **churn --locator …_add_book** — assert `churn_count >= 1`.
6. **timeline --entity …_add_book** — assert ≥1 entry.

`ok` is the conjunction of all four assertions. When `ok`, the step surfaces the
four `(token, qualname)` pairs; the qualname is the locator normalized to a
dotted form (e.g. `specimen.cli._add_book`) so `report.py::_symbol_matches`
credits each entry (`name` ends with `"." + symbol`).

### The four catalogued entries (`tour/lacunae.toml`)

New tool token `warpline`; new `category = "change-impact"`; harness-synthesized
rule tokens (legitimate per the existing `dead-entity` precedent). All four
share `file = "specimen/cli.py"` and `symbol = "_add_book"`, differing by
`expected_rule`:

| id | expected_rule | asserts |
|----|---------------|---------|
| `wp-blast-radius` | `wp-blast-radius` | downstream `add_book` appears in the impact radius |
| `wp-reverify` | `wp-reverify` | `add_book` in the reverify worklist, `reason=downstream` |
| `wp-churn` | `wp-churn` | `_add_book` has tracked change history (`churn_count >= 1`) |
| `wp-timeline` | `wp-timeline` | `_add_book` timeline non-empty |

Each `explanation` states plainly that these are **positive-capability
demonstrations, not flaws** — warpline is advisory/enrich-only and never gates —
so no maintainer tries to "fix" them. No planted-flaw docstring is added to
`_add_book` (it is library scaffolding, not a flaw); the catalogue entries carry
the demonstration intent.

### What changes in the harness (revised post-scrutiny)

- `tour/capability.py` — **`warpline` is added to `RUNNABLE`.** This was NOT in the
  original spec and is load-bearing: the verify gate (`__main__.py`) only asserts
  a lacuna when `expected_tool in live`. Without warpline in `RUNNABLE`, `detect()`
  never reports it live, so the four `hd-*` entries would never be checked and a
  degraded warpline leg could pass silently — defeating this spec's own fail-loud
  success criterion. Adding it also gives warpline a `- **warpline** — live` line in
  `docs/matrix.md` (true parity), not only a cell.
- `tour/report.py` — a new `warpline` tool token becomes a cell automatically via
  the `demonstrates` → `cells()` union (asserted by
  `test_cells_are_the_union_of_demonstrates`). No coverage-logic change.
- `tour/manifest.py` — the `lang`/`expected_kind`/`scan_target` fields added in
  the 48h-additions Wave 1 already cover everything; warpline entries use the
  defaults (`lang="python"`, `expected_kind="finding"`).

### Determinism & CI wiring (the load-bearing risk)

`make ci` runs `verify`, which re-runs the tour and byte-compares against the
committed `docs/tour.md` / `docs/matrix.md`. For the warpline leg to be stable:

- **Frozen prose + stable surfaced tokens** guarantee byte-identity regardless
  of snapshot drift — designed in above.
- **Cold-DB self-population (revised post-scrutiny).** `.weft/warpline/warpline.db`
  is gitignored, so CI / a fresh clone start with NO warpline index. The step must
  run **`warpline backfill --no-resolve-sei` THEN `warpline capture-snapshot`** —
  `capture-snapshot` alone only rebuilds the loomweave edge graph (for
  blast-radius/reverify) and does NOT populate the git-history tables that
  `changed`/`churn`/`timeline` read, so a capture-only step degrades to
  `ok=False` on every cold run. This was verified live: from an empty
  `.weft/warpline`, `backfill → capture-snapshot` yields key_id 128 and the
  `_add_book → add_book` edge at depth 2; capture-only yields `changed: 0`.
  (The original spec's claim that one `capture-snapshot` "mirrors
  `loomweave_analyze`" was wrong — `loomweave analyze` is a full rebuild.)

### Detail string (frozen, illustrative)

```
## ✅ warpline change impact

touching _add_book surfaces downstream service.add_book in blast-radius +
reverify worklist (edge-provenanced); change history tracked via churn +
timeline — advisory, never gates
```

## Verification-first items for the implementation plan

Pin these against live warpline as **plan Step 1** (the way the Rust trust-marker
dialect was pinned in Wave 3), before writing the step:

1. The exact runtime mechanism + pinned rev-range to resolve
   `_add_book` locator → `key_id`.
2. That a clean-tree freshly-captured snapshot still yields the
   `_add_book → LibraryService.add_book` edge at the chosen depth.
3. The exact locator → dotted-qualname normalization that makes
   `report.py::_symbol_matches("_add_book", name)` credit all four entries.
4. The snapshot-build invocation the step uses (`capture-snapshot` vs
   `backfill`/`ingest-commit`) and that it writes only under `.weft/warpline/`.

## Out of scope (YAGNI)

- The federation-seam / enrichment-contract variants (the rejected 3-entry
  option) — not in this leg.
- Any warpline gate or CI-failing behavior — warpline never gates; the leg only
  reports and asserts.
- Recording this as a product bet/PRD — by decision, it is a straight
  engineering addition; it will be noted in `docs/product/` at the next
  `/product-checkpoint`, not wrapped in a PRD first.

## Success criteria

- Four new entries (`wp-blast-radius`, `wp-reverify`, `wp-churn`, `wp-timeline`)
  in `tour/lacunae.toml`; manifest count grows from 44 → 48.
- `make tour` regenerates `docs/tour.md` (new `## ✅ warpline change impact`
  section) and `docs/matrix.md` (new `warpline` cell) with `Not surfaced: []`.
- `make ci` exits 0 (test + scan + verify + cargo-check), including a clean-tree
  snapshot rebuild.
- Warpline is demonstrated, not merely available: the leg fails loudly if warpline
  stops returning the `_add_book → add_book` impact edge.
