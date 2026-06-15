# Cold-eval report — new-repo onboarding (2026-06-15)

Worked the questions as a newcomer to the repo, reaching for whatever was fastest
per question. Tooling available: the Weft MCP suite (loomweave, wardline, legis,
warpline, filigree) plus ordinary file reads / shell. Read-only throughout; no
source changed. The one scan I ran (wardline) posts to a local Filigree and
writes nothing into version control.

---

## Part A — answers

### 1. Orientation
**Lacuna** is a *deliberately-flawed reference application* — the README calls it
"the MissingNo of the Weft suite." It's a clean-cored library app seeded with
~45 catalogued **lacunae** (planted flaws), each positioned to make a specific
Weft tool light up. It is a test specimen, not a real product.

Major parts (from README + `project_status_get`): 391 entities / 808 edges /
26 subsystems, split across plugins **python (306)**, **core (68)**, **rust (17)**.

- `specimen/` — the clean-core library domain (`Book`, `LibraryService`,
  `Repository`, `cli`) plus isolated planted-flaw modules (`dead_code.py`,
  `cycle_a/b.py`, `colliding.py`, `nesting_bomb.py`, `wardline_sinks.py`,
  `trust_flow.py`, `preview_sinks.py`, `policy_boundaries.py`, …).
- `specimen-rs/` — Rust specimen (the `rs-*` lacunae).
- `specimen_quarantine/` — intentionally unparseable source.
- `tour/` — the tour harness (`python -m tour`) that drives every live tool.
- `docs/flaws/` — 45 per-lacuna explainer pages (`lw-*`, `wl-*`, `rs-*`,
  `lg-*`, `wp-*`).
- `policy/` — legis governance cell config; `tests/`, `weft.toml`, `Makefile`.

*How I got it:* `project_status_get` (counts/plugins) + `README.md` +
`ls docs/flaws/`. Clean and fast; no fallback needed beyond reading the README,
which is the right primary source for "what is this."

### 2. Dead code
`entity_dead_list` → **141 candidates** (conservative, confidence 0.6, "static
reachability cannot prove dynamic/reflective reach"). The genuinely planted one:

- **`specimen.dead_code.orphaned_helper`** — `specimen/dead_code.py:9-11`.

Caveat I'd flag to the next person: the list is **noisy here by design**. Because
`specimen` is a library with no entry-point roots, much of the *legitimate* core
shows up as "dead" — `LibraryService` (`service.py:52`), `Repository`/
`InMemoryRepository` (`repository.py`), `models.Entity/Genre/Identifiable`, the
whole `hub.Dispatcher.handle_*` family. These are exercised only by tests, so the
reachability heuristic flags them. The tool is honest about this: it returns an
`excluded` block (rust excluded — "emitted no reachability root tags … excluded
rather than false-flagged dead") and `withheld: 5 (secret_present)`. So the
*answer* is trustworthy only once you read the caveat — the raw row count would
mislead.

### 3. Structural health
- **Circular import:** exactly one — `specimen.cycle_a ↔ specimen.cycle_b`
  (`module_circular_import_list`, resolved confidence, 2-member SCC). Planted
  (`docs/flaws/lw-circular-import.md`).
- **Coupling (whole-repo):** top hotspot `tour.__main__._drive` (coupling 19),
  then `specimen.hub.dispatch` (10), `specimen.wardline_sinks.read_admin_arg`
  (8). Subsystem modularity is flagged **weak** (`LMWV-FACT-CLUSTERING-WEAK-MODULARITY`,
  INFO).
- Honest snag: several top coupling rows came back **nulled with
  `briefing_blocked: secret_present`** — files that tripped the secret scanner are
  redacted out of the ranking, so the coupling list has holes I can't see into
  without separately clearing the secret gate.

### 4. Find by intent — "adds a book to the library"
**`specimen.service.LibraryService.add_book`** — `specimen/service.py:81-83`,
with CLI wrapper **`specimen.cli._add_book`** — `specimen/cli.py:44-48`.

*How I got it:* `entity_find "add book"` returned exactly those two rows on the
first try. This was the single cleanest moment of the job — concept word →
correct function, no grep.

### 5. Known issues (quality / security)
Three sources, all agreeing:

- **loomweave findings (11):** duplicate locator `specimen.colliding.ShelfMark`
  (ERROR), `nesting_bomb.py` too-complex (WARN), `specimen_quarantine.unparseable`
  syntax error (WARN), weak modularity (INFO), and **5 secret detections** —
  `.env` (lines 1-3,5), `tour/steps.py:481`, `policy_boundaries.py:28,41`.
- **wardline taint scan:** 156 findings — **1 active** (`PY-WL-125` log-injection,
  INFO, `preview_sinks.log_export_request`) and **42 baselined defects**: a full
  sweep of ERROR-class taint flaws `PY-WL-101` (×12) through `PY-WL-124`
  (SQL/SSRF/SSTI/path-traversal/deser/exec/etc — one per `docs/flaws/wl-*`).
  The gate **trips** at `--fail-on ERROR` because the baseline isn't trusted by
  default ("22 suppressed ERROR+ … pass `--trust-suppressions`").
- **filigree tracker:** 2 open **P1** bugs — `lacuna-5d0e4ba6d7` (the duplicate
  locator) and `lacuna-522ab56124` (loomweave scope-by-qualname doesn't recurse
  into subpackages). Both are real tool-defect tickets, not specimen flaws.

### 6. `specimen` package — biggest coupling hotspots
`entity_coupling_hotspot_list scope="specimen"`:
1. **`specimen.hub.dispatch`** — coupling 10 (fan-in 5 / fan-out 5), `hub.py:35`.
2. **`specimen.wardline_sinks.read_admin_arg`** — 8 (fan-in 8), `wardline_sinks.py:27`.
3. **`specimen.preview_sinks.read_report_field`** — 6 (fan-in 6), `preview_sinks.py:32`.
4. **`specimen.models.Entity.key`** — 5 (fan-in 5), `models.py:36`.
5. `InMemoryRepository.add` (4), `LibraryService._emit` (4).

*Caveat:* scoping to a **package name** is the exact thing tracked as broken in
`lacuna-522ab56124` — for edge-derived tools a bare `scope="specimen"` can return
0. It worked here for coupling, but per the ticket it's unreliable for
circular-import/dead-code at the package level; module-level scopes
(`scope="specimen.hub"`) are the safe form.

### 7. Change impact — if I changed `add_book`
**The dedicated tool (warpline) could not answer this** (see debrief). I answered
from loomweave `entity_neighborhood_get` + `entity_callers_list`:

- **Callers:** `specimen.cli._add_book` (the CLI command path) — plus **1
  unresolved name-matched call site** the resolver couldn't bind.
- **Callees:** `specimen.repository.InMemoryRepository.add` (the persistence
  contract).
- **References:** `specimen.models.Book` (the model it constructs).
- **Decorated by:** `specimen.service.audited` (an audit/logging wrapper —
  `relations_in: decorates`).
- **Container:** `LibraryService`.

So a change to `add_book` plausibly affects the CLI command, the repository
`add` contract, the `Book` model shape, and anything relying on the `audited`
decorator's behavior — plus that one unresolved caller worth chasing by hand.

### 8. Governance
- **legis doctor:** all checks **ok** — governance chain, binding chain, store
  all healthy; cells config at `policy/cells.toml`; wardline routing
  `LEGIS_WARDLINE_CELL=surface_override`. HMAC: *"no protected policies
  configured."*
- **Policy cells (`policy_list`):** default `structured`; rules route
  `import-allowlist` + `no-broad-except` → `coached`, `human.*` → `structured`,
  `protected.*` → `protected`. **All four cells report `enabled: false`** — with
  no `LEGIS_HMAC_KEY` exported the governance gate is honestly disabled
  (matches README's "stays honestly disabled (`CELL_NOT_ENABLED`)").
- **Attestations / `@policy_boundary`:** `specimen/policy_boundaries.py` declares
  two boundaries — `validated_recovery` (the *healthy* one, evidence test asserts
  the suppressed policy) and `pinned_import` (the **lacuna** — its evidence test
  is skip-marked). `legis policy_boundary_check` returned **FINDINGS**: it
  gracefully degraded over `nesting_bomb.py` ("nesting too deep … file skipped,
  scan continued") and flagged both boundaries — **but as
  `POLICY_BOUNDARY_TEST_FINGERPRINT_MISMATCH`, not the
  `POLICY_BOUNDARY_TEST_DISABLED` the planted-flaw doc says `pinned_import` should
  raise.** Either the fingerprints have drifted or the MCP path classifies
  differently than the documented CLI; flagging it as a possible discrepancy, not
  asserting which is right.
- **wardline taint on `add_book`:** present — `UNKNOWN_RAW` return, `source:
  fallback`, 1 unresolved call; no taint findings on it.

---

## Part B — debrief

### How you worked
| Q | reached for first | clean (Y/N) | fell back? |
|---|---|---|---|
| 1 Orientation | `project_status_get` + README | Y | Read README — appropriate, not a fallback |
| 2 Dead code | `entity_dead_list` | Partial | N, but had to read the caveat block to trust it |
| 3 Structure | `module_circular_import_list` + `entity_coupling_hotspot_list` | Y | N (but secret-blocked rows hid some hotspots) |
| 4 Add a book | `entity_find "add book"` | Y | N — first hit, correct |
| 5 Known issues | `project_finding_list` + `wardline scan` + `issue_list` | Y | wardline scan overflowed → jq the saved file |
| 6 specimen coupling | `entity_coupling_hotspot_list scope=specimen` | Y | N (but scope-by-package is a known-flaky path) |
| 7 Change impact | `warpline blast_radius` | **N** | **Yes → loomweave neighborhood/callers** |
| 8 Governance | `legis doctor`/`policy_list`/`policy_boundary_check` | Mostly | Read `policy_boundaries.py` to interpret the finding |

### Scores (1–5)
- **Ease — 4.** Most answers came in one well-named call. `entity_find` and the
  loomweave structural queries were genuinely faster than I could have grepped.
  Knocked down by warpline whiffing on Q7 and the wardline context overflow.
- **Trust — 4.** High where the tools cite provenance (confidence tiers,
  `excluded`/`withheld`/`scope_excludes` blocks, "1 unresolved call site" notes).
  The honesty about what they *can't* see is the reason I trust what they do
  return. Docked one point because Q2's headline number (141) and Q8's
  fingerprint-mismatch both needed me to read further to not be misled.
- **Knew-where-to-look — 4.** The CLAUDE.md / MCP instructions told me which tool
  owns which question, so I rarely guessed. I *did* nearly miss that warpline was
  the "right" Q7 tool until it failed and loomweave was the real answer.
- **Friction — 3.** Three concrete drags: warpline returning empty, the 72k-char
  wardline payload I had to `jq`, and secret-blocked entities silently nulling
  rows. None fatal, all annoying.
- **Next time — 4.** I'd use these again for structure/impact/findings — they
  beat grep decisively. But I'd go straight to loomweave (not warpline) for change
  impact, and `summary_only`/`where` for wardline from the start.

### Open
- **Worst moment:** `warpline blast_radius` for Q7. I fed it `add_book`'s SEI and
  got `changed: []`, `affected: []`, `enrichment.sei: absent`, snapshot "8 commits
  behind." The dedicated change-impact authority returned nothing because my SEI
  ref didn't resolve into its (stale) snapshot. The tool was *honest* about it
  (DELTA completeness, staleness flagged) — but I still had to abandon it and
  reconstruct the answer from loomweave edges.
- **Best moment:** `entity_find "add book"` → the exact function and its CLI
  wrapper, instantly. Concept-to-symbol with no name guessing is the thing I
  genuinely couldn't do as fast by hand.
- **Where you fell back (unsoftened):**
  1. **Q7 → loomweave.** warpline gave an empty/stale answer; I rebuilt change
     impact from `entity_neighborhood_get` + `entity_callers_list`. This is the
     one place a tool *failed* rather than just being noisy.
  2. **Q5 → jq on a saved file.** `wardline scan` returned 72k chars and was
     truncated out of context; I had to query the dumped file. Should have used
     `summary_only` / `where` first — my mistake, but the default scan being
     un-context-safe is a sharp edge.
  3. **Q8 → read `policy_boundaries.py` by hand.** The `policy_boundary_check`
     finding (`TEST_FINGERPRINT_MISMATCH`) didn't match the planted-flaw doc
     (`TEST_DISABLED`), so I opened the file to see what was actually declared.
  4. **Q1 → README.** Not really a fallback — reading the README is the correct
     primary move for "what is this project," and I'd do it again.
- **One change:** make `warpline blast_radius` either resolve a loomweave SEI ref
  against a fresh snapshot, or fail *loudly* ("your ref resolved to nothing —
  re-capture the snapshot") instead of returning a clean-looking empty set that a
  hurried reader could mistake for "nothing is affected."
- **Would you recommend this way of working to another engineer? Yes** — the
  loomweave/wardline/filigree trio answers structure, security, and tracking
  questions faster and more honestly than grep, *provided* you read the
  provenance blocks and don't trust raw counts blind.

### Headline
A good way to do the job — concept-search, structural queries, and the taint/
finding scans pay for themselves immediately — with the catch that you must read
each tool's honesty footnotes (excluded/withheld/stale), and the change-impact
tool (warpline) was the one that left me to finish by hand.
