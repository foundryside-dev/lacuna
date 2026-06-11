# Loom suite — dogfood findings

**Driver:** Claude (Opus 4.8), acting as the agent the suite is built for.
**Date:** 2026-06-09 · **Repo:** lacuna @ `144fd10` · **Method:** drive each live
tool surface on realistic agent tasks; log friction *in the moment*.

**The bar (user's words):** "This is an agent-first system, so if the agent
doesn't prefer using it to grep, then it has failed." A clean feature-tour is a
*failed* dogfood pass. Findings = friction only.

Every interaction carries a **grep?** verdict: would I, the agent, have reached
for `grep`/`Read`/raw shell instead of (or after) this tool? `grep? no` is a
pass; `grep? yes` is the tool losing to a 40-year-old line matcher.

Severity: **S1** blocks/forces fallback · **S2** obnoxious friction, tolerated ·
**S3** papercut/polish.

Friction class: `missing-tool` · `missing-option` · `inconsistent-args` ·
`bad-error` · `unusable-output` · `discoverability` · `grep-loss`.

---

## Top of the pile (read this if nothing else)

> **CONFIRMED LIVE: `make ci` is RED on this commit.** `make scan` exits 2
> (`gate: FAILED — 1 active ERROR+ defect`, *evaluated post-suppression, baseline
> honored*). `make verify` exits 2 (6 Loomweave lacunae not surfaced + stale
> `docs/tour.md`). This is not a design demo of red — see DEMO-1. The
> "repivot complete / make ci passes" state has regressed.

1. **WL-1 / X-3 — a baselined lacuna's fingerprint no longer matches the
   baseline, so it escaped suppression, trips `make scan`, and got DUPLICATED
   into Filigree.** Baseline holds `fc1bc079`; the current wardline (both CLI
   `1.0.0rc4` and MCP) emits `8f68f390` for the identical, unchanged-since-Jun-6
   finding. `wardline scan . --fail-on ERROR --trust-suppressions` **fails the
   gate on it (verified live, exit 2)** with the baseline honored. **Confirmed:**
   gate red, baseline stale, federation join key broke. **Open:** the *trigger*
   (wardline version bump vs. resolution-context change vs. hash instability) —
   I ruled out source-changed; in-session the hash was stable, so it's not
   observed drift. Needs the wardline maintainer to name the cause. **S1.**
2. **FIL-1 / WL-2 — Filigree's "106 actionable, 0 baselined/suppressed" is
   false.** Wardline computed `active: 1, baselined: 33` and *emitted* the
   suppression state; Filigree drops it on the floor and counts every baselined
   lacuna as actionable. An agent that trusts the banner promotes ~100 issues for
   intentional flaws. **S1.** Only external memory saved me; the tool surface
   doesn't.
3. **Grep still wins for "find the thing that does Y."** Loomweave's
   `entity_find` is a name matcher (concept words → empty → grep), and semantic
   search ships **off**. The graph is excellent *once you have a name*; the
   discovery step that's supposed to replace grep doesn't. **S2.**
4. **The suite leaks at its seams** (consistency pass): one function has three
   identifier dialects (X-2), "who am I" has three models (X-1), "suppressed" has
   three vocabularies (X-4), and the two finding-filter surfaces are shaped
   oppositely (X-5). Each tool is internally coherent; the *edges between them*
   are where the agent pays.

**What's genuinely agent-first (keep / clone elsewhere):** Wardline's
`agent_summary` (active-first, pre-filled `next_tool_calls` with exact
fingerprints, bounded-by-default, honest truncation) is the gold standard the
other three should copy. Filigree's `issue_get` transition model and Loomweave's
`entity_source_get`/`entity_at`/neighborhood all beat grep cleanly. The bones are
good; the failures are at integration boundaries and discovery entry points.

---

## Coverage ledger (sampled vs skipped — no silent truncation)

| Tool | Live? | Verbs driven | Skipped |
|------|-------|--------------|---------|
| Loomweave | yes | entity_find, entity_at, entity_source_get, entity_callers_list (resolved+ambiguous), entity_neighborhood_get, entity_entry_point_list, entity_semantic_search_list, entity_dead_list, module_circular_import_list, entity_coupling_hotspot_list | high_churn/todo/http_route/data_model facets, index_diff_get, subsystem_member_list |
| Filigree | yes | session_context_get, finding_list (×filters), issue_get(+transitions), work_start/_next + work_release (schema-level), observation_create (schema) | mutating verbs (claim/close/promote — avoided to not churn demo), plan_*, annotation_*, dependency_* |
| Wardline | yes | scan (+integrations, agent_summary), assure, explain_taint(chain), where-filter; baseline/waiver/fix/judge (schema-level) | did NOT mutate: baseline --overwrite, waiver_add, fix --apply, judge (network) — all would alter the specimen |
| Legis | yes | git_commit_get, override_rate_get, policy_explain, scan_route (→INVALID_CELL_SPEC ×2), filigree_closure_gate_get (→CELL_NOT_ENABLED) | override_submit (harness-blocked, unauthorized mutation), policy_evaluate, pull_request_get/check_list (no PR data), git_rename_feed_get, sei-backfill |
| Charter | **no — design-only** | not exercised (no live MCP/CLI surface in this repo) | all |

---

## Findings

### Loomweave

What I did: oriented cold on the specimen — found entry points, searched for
the app's domain, read an entity's source, and ran the canonical "what calls X"
on `LibraryService.checkout` / `.add_book`.

**LW-1 — `entity_find` is a name matcher, not a code search. `grep? YES.`**
`class: grep-loss · S2`
`entity_find "library"` → **empty**. `entity_find "borrow"` → **empty**. Both
terms are all over the source (grep finds `library` in 4 files, `borrow` in
`service.py`). `entity_find` only matches entity id/name/short_name/**summary**,
and summaries are off by default (LW-2), so it degrades to a Python-identifier
matcher. The skill's headline promise — "find the thing that does Y" — fails for
any term that isn't part of a symbol name, and an empty result is the single
strongest nudge to abandon the tool for `grep`. Once I had a *name* fragment
(`service`, `add_book`) recall was excellent (21 entities, full class map). The
cliff is: name-fragment → great; concept word → grep.

**LW-2 — semantic search, the actual "find by meaning" path, is OFF by default.**
`class: missing-option · S2 · grep? YES (fall through to LW-1 then grep)`
`entity_semantic_search_list "main entry point…"` → `result_kind: not_enabled`.
This is the tool that would *fix* LW-1, and it's the most natural agent reach
for an unfamiliar tree. The honest-empty (it names the disabled flag) is good
design — but the capability the MCP banner advertises as the reason to pick
Loomweave over grep is dark out of the box. Net: the two "find the thing that
does Y" surfaces are (a) off and (b) name-only.

**LW-3 — `scope_excludes` is an unconditional disclaimer, so empty results are
un-trustable without grep.** `class: unusable-output · S2 · grep? YES (to disambiguate)`
`entity_callers_list(checkout)` → `callers: [], scope_excludes:
["attribute-receiver-calls"]`. But `entity_callers_list(add_book)` →
**resolves** `_add_book`, *which calls it as `app.service.add_book(...)`* — an
attribute-receiver call. So the blind-spot caveat is emitted **even when the
graph successfully resolved that exact edge class**. Consequence: when callers
is empty, the agent cannot tell a true-empty (checkout really is dead) from a
genuine blind-spot miss. I had to `grep "checkout("` to confirm — the tool's own
honesty caveat *caused* the grep fallback. Fix: make `scope_excludes` per-query
(did THIS traversal actually skip a candidate?), not a constant footer.

**LW-4 — one file, two entities, different `kind`.** `class: discoverability · S3`
`entity_find "service"` returns both `python:module:specimen.service` and
`core:file:specimen/service.py` for the same path. Minor "which one do I feed
the next tool" tax; `kind=` filter mitigates if you remember it exists.

**LW-5 — `entity_dead_list` over-reports the entire tree, violating its own
"fails toward live" contract.** `class: unusable-output · S2 · grep? you'd trust
vulture/grep over this`
One call returned **180 dead-code candidates** — including every test file
(`tests/test_*.py`), every `tour/*` module, `specimen/service.py`, and
`specimen/cli.py` *which contains the catalogued entry point* `specimen.cli.main`
(`entity_entry_point_list` lists it!). The docstring promises it "fails toward
`live`… under-reports rather than over-reports" and returns "zero candidates with
a missing-signal note" when root tags are absent. Instead it flagged ~the whole
repo as dead. Root cause looks like file/subsystem-kind nodes not sitting on
call+import edges, so reachability can't reach them and marks them dead — but the
result doesn't distinguish "structurally off-graph" from "genuinely unreachable."
An agent hunting the *one* planted dead-code lacuna (`dead_code.py`) has to find
it in a 180-row haystack that includes the app's own entry point. The signal is
there (`dead_code.py` is row N) but the noise floor defeats it.

**Passes (grep? NO — genuinely beat the alternative):**
- `module_circular_import_list` nailed the planted `cycle_a ↔ cycle_b` cycle
  exactly, one row, SCC members sorted. grep can't do this. Gold.
- `entity_coupling_hotspot_list` → ranked fan-in/fan-out, `read_admin_arg`
  (fan_in 8) surfaced as the taint-relevant hub. Useful, no grep equivalent.
- `entity_entry_point_list` → 2 entry points with SEI + path, instant. Better
  than grepping `if __name__`.
- `entity_source_get` → line-numbered window, `in_entity` flags, `source_status`
  drift signal. Better than `Read` for a single entity.
- `entity_at`, `entity_neighborhood_get` → callees/refs/container with byte
  offsets and confidence tiers. No grep equivalent.
- `add_book` callers resolved through an attribute-receiver call — the hard case
  worked; my prior assumption was wrong and the graph beat it.

**Cross-tool seed (see consistency pass):** every entity carries BOTH an `id`
(`python:function:…`) and a `sei` (`loomweave:eid:…`). Loomweave's own tools
want the `id`; Filigree's `entity_association_*` want the `sei`. Same entity, two
identifiers, two tools — easy to paste the wrong one.

### Filigree

What I did: read the SessionStart banner's "106 findings to bridge", pulled
`finding_list` (all + by severity), inspected the work-claim verbs, and read the
one ready issue's transitions. Did **not** mutate the demo tracker via *tracker*
verbs (claim/close would churn `make verify` state and the only ready item is a
release). **Faithful-reporting caveat:** my Wardline `scan` later in this pass
emitted with `created: 1` — that one created row is the active `8f68f390`
finding (WL-1), absent from the pre-scan `finding_list`. So this pass *did* add
one active finding to the tracker as a side effect of exercising `scan`. By the
same standard I used to flag FIL-4 (prior-pass cruft), I flag my own.

**FIL-1 — the headline count actively misleads: "106 actionable, 0
baselined/suppressed" is false; every real defect is baselined.** `class:
unusable-output / data-model · S1 · this is the one that wastes an agent's hour`
The banner (and `session_context_get`) says *"ANALYZER FINDINGS: 106 not yet
bridged … (106 actionable, 0 baselined/suppressed) — bridge with
finding_promote."* But pulling the findings: **all 22** high-severity rows are
`kind:defect, internal_severity:ERROR` and **every single one** carries
`metadata.wardline.suppressed: "baselined"` — they are the planted lacunae, the
specimen's whole point. Yet Filigree's own first-class fields read
`status:"open"`, `suppression_state:null`, and the rollup says
`0 baselined/suppressed`. **Wardline's suppression verdict crosses the
federation wire inside `metadata.wardline.suppressed` but Filigree never lifts it
into the queryable projection it then counts.** An agent that believes the
banner and runs `finding_promote` across the "106 actionable" would manufacture
~100 issues for already-accepted, intentional flaws — precisely the noise the
tool exists to prevent. I only know not to because external memory told me;
nothing *in the tool's own surface* protects a fresh agent. Fix: lift
`metadata.wardline.suppressed` → `suppression_state` and exclude it from the
`actionable` count.

**FIL-2 — `finding_list` can't filter out the noise it's full of.** `class:
missing-option · S2 · grep? you end up jq-ing the JSON, which is grep`
Filters are `file_id / issue_id / scan_run_id / scan_source / severity / status`.
There is **no `kind` filter** (so you can't exclude the ~80 `kind:metric` rows —
WLN-ENGINE-METRICS, WLN-L3-LOW-RESOLUTION "has 100% unresolved calls" — which are
wardline's *own engine telemetry*, not code defects), and **no `suppressed`
filter** (FIL-1). The `status` enum is `open/acknowledged/false_positive/fixed/
unseen_in_latest` — note "baselined"/"suppressed" aren't even in it, though the
banner speaks in exactly those words. Net: to answer "show me the real,
un-suppressed defects" I must pull all 106 and client-side filter on nested
`metadata.wardline.{kind,suppressed}` — i.e. do the analysis the tool should do.

**FIL-3 — two identity params with overlapping meaning, and only on some
verbs.** `class: inconsistent-args · S2`
`work_start`/`work_start_next` require `assignee` **and** accept `actor`
("defaults to assignee"). `finding_promote`, `observation_create`, `work_release`
take `actor` only. So "who am I" is sometimes `assignee`, sometimes `actor`,
sometimes both-but-one-defaults-to-the-other — within a single tool. (Cross-tool
it gets worse — see consistency pass: legis wants `--agent-id`.) An agent has to
re-derive the identity-arg name per verb.

**FIL-4 — leftover dogfood cruft in the live tracker.** `class: hygiene · S3`
Finding `lacuna-sf-0abc5d3e17` is linked to issue `lacuna-da37dd4107`, whose own
resolution text reads *"Dogfood artifact … Not a real defect … Safe to delete."*
A prior dogfood pass left a promoted issue behind. Not a tool defect, but it's
sitting in the demo's `is_ready`/finding surface where the next agent trips over
it. (I'm flagging, not deleting — `issue_delete` is irreversible and yours to
call.)

**Passes (grep? NO):**
- `issue_get include_transitions=true` → `is_ready`, `valid_transitions` with
  per-transition `ready`/`missing_fields`/`enforcement`. The ready≠startable
  model is legible from one read; the release task correctly shows a single-hop
  soft transition to `development`. This part is genuinely good.
- The MCP schemas are unusually self-documenting (the `work_start` description
  explains AmbiguousTransitionError and the triage-bug advance walk inline).
  Discoverability of *behaviour* is high even where *args* are inconsistent.

### Wardline

What I did: ran a whole-program `scan`, `assure` for coverage posture,
`explain_taint --chain` on the one active defect, then chased that defect into
`baseline.yaml` and `lacunae.toml`.

**WL-1 — fingerprint drift: a baselined lacuna escaped its baseline, and the
escape wrote a DUPLICATE into Filigree.** `class: data-model / correctness · S1 ·
the report's headline finding`
`scan` reports `active: 1` — `specimen.wardline_sinks.lookup_member` PY-WL-101
(lines 84–90), fingerprint **`8f68f390…`**. But `.weft/wardline/baseline.yaml`
line 57 *already baselines that exact finding* — same rule, same path, same
message — under fingerprint **`fc1bc079…`**. Same logical defect, two
fingerprints; the baseline keyed on the old hash silently fails to suppress the
new one, so it surfaces ACTIVE.

**Mechanism — narrowed, not fully closed (honesty note):** I confirmed the
*effect* but must not overclaim the *cause*. What's evidence-backed:
  - The fingerprint is **stable in-session**: both the MCP `scan` and the
    `make scan` CLI (`wardline 1.0.0rc4`, the uv-tool at
    `~/.local/share/uv/tools/wardline/bin/wardline`) emit `8f68f390`. So this is
    **not** observed run-to-run drift — I never saw the hash move within a run.
  - The specimen source is **unchanged since before the baseline**:
    `specimen/wardline_sinks.py` last changed Jun-6 (`46fa415`); `baseline.yaml`
    was written Jun-7 (`544c484`). So the source can't be what changed → a
    "stale-because-code-moved" explanation is **ruled out**.
  - Therefore the fingerprint changed **once, between baseline-capture and now,
    with identical source.** The most likely cause is a **wardline
    build/version change to the fingerprint scheme (or its resolution inputs)**
    that silently invalidated the baseline — consistent with the known Loom
    uv-tool build-staleness hazard (a CLI and the source/MCP build can diverge
    under one version string). `explain_taint` (`resolved 1 / unresolved 4`,
    `source_boundary: null`) shows the hash *can* fold in resolution state, which
    is a plausible secondary contributor — but I have no in-session evidence it
    drifts continuously, so I'm not asserting it.
  Net: **confirmed = gate red + baseline stale + federation join key broke;
  open = whether the trigger was a wardline version bump, a resolution-context
  change at capture time, or fingerprint instability.** The fix differs per
  cause (pin/stamp the wardline build & re-baseline vs. make the fingerprint
  version- and resolution-invariant), so this needs the wardline maintainer to
  name the trigger before remediation.

Two compounding consequences, regardless of cause:
  1. **The demo's core invariant is at risk.** CLAUDE.md mandates `wardline scan
     --fail-on ERROR`. This 1 active ERROR *trips that gate* — on a finding that
     is supposed to be green. ("stays green on the baselined lacunae" — README.)
  2. **The drift pollutes the sibling tracker.** This same scan reported
     `filigree: created: 1, updated: 105`. The `created: 1` *is* `8f68f390` —
     Filigree now holds BOTH `fc1bc079` (baselined, stale) and `8f68f390`
     (active, new) for one defect. Fingerprint drift manufactures duplicate
     issues across the federation on every scan where resolution shifts.
  **Arbiter run (live):** `make scan` → `gate: FAILED (--fail-on ERROR) — 1
  active ERROR+ defect(s)`, `evaluated post-suppression (repository baseline …
  honored — trusted-local)`, **exit 2**. So this is not intended demo state: the
  baseline is honored and the gate *still* trips, because the live fingerprint
  isn't the one the baseline holds. Confirmed drift, not design. I did **not**
  `baseline --overwrite` to paper over it (that masks the finding and mutates the
  specimen) — the fix is to make the fingerprint resolution-invariant, then
  re-baseline.

**WL-2 — the same suppression seam as FIL-1, now proven from the source end.**
`class: data-model · S1 (== FIL-1)`
`scan.summary` = `active: 1, baselined: 33`; `assure` = `defect_total: 1,
baselined_total: 33, coverage_pct: 100`. Wardline computes suppression correctly
**and emits it** — the payload carries `metadata.wardline.suppressed` (FIL-1
showed Filigree storing it). Yet Filigree's rollup says `0 baselined, 106
actionable`. So the data is correct at the producer, correct on the wire, and
dropped in the consumer's projection. This is the airtight version of FIL-1:
wardline did its job; Filigree's count is the bug.

**WL-3 (memory update, not a defect) — the Filigree-emit 401 seam is FIXED.**
Prior session memory said `wardline emit → 401, tracker looks empty`. Live now:
`filigree_emit: { reachable: true, token_sent: true, auth_rejected: false,
failed: 0, url: …/api/p/lacuna/weft/scan-results }`. The project-scoped URL
(`wardline.yaml`, committed this session as `144fd10`) closed it. Recording so
the stale memory gets corrected.

**Passes (grep? emphatically NO — this is the agent-first gold standard):**
- `scan.agent_summary` is what the whole suite should look like: active defects
  listed first, each with a pre-filled `next_tool_calls` carrying the **exact
  fingerprint** to paste into `explain_taint`/`file_finding`; `next_actions`
  with reasons; `truncation` with `next_offset`; bounded-by-default (≤25 bodies)
  so it can't overflow context. Zero ambiguity about the next move.
- `where` filter on `scan` (`suppression: active`, `kind`, `rule_id`, `sink`,
  `tier`) is exactly the filtering vocabulary FIL-2 is *missing* — the producer
  has it, the tracker doesn't. Worth porting the verb surface to Filigree.
- `assure` answers "should I trust this module" (coverage %, unknown list,
  waiver-debt) in one call — no grep equivalent exists.
- `explain_taint` is honest about unresolved provenance (`source_boundary:
  null`, resolution counts) rather than fabricating a chain.

**Note on `legis_artifact_status`:** `scan` refused to sign the legis artifact —
`"refusing to sign … for a dirty working tree (uncommitted changes)"`. Correct
and well-explained (the dirty tree is `findings.jsonl` + my in-progress report).
Flagging only as a sequencing note: scan-emit-to-Filigree succeeds on a dirty
tree, but scan-sign-for-Legis won't — two integrations on one verb with
different cleanliness contracts. Not wrong; worth knowing.

### Legis

What I did: read git/CI context (`git_commit_get`, `override_rate_get`),
probed policy routing with a deliberately **invented** policy name, and
triggered both governance error paths (`INVALID_CELL_SPEC`, `CELL_NOT_ENABLED`)
to verify the `next_action` guidance I committed this session (`144fd10`) against
live behaviour.

**LEG-1 — no way to discover policy/cell names, and `policy_explain` answers for
policies that don't exist.** `class: discoverability · S2 · grep? you'd grep the
server's source for policy names`
There is no `policy_list` / `cell_list` verb. I passed a policy name I made up on
the spot — `no-broad-except` — to `policy_explain` and it returned a fully-formed
answer: `cell: "structured", human_in_loop: true, enabled: false`. No "unknown
policy" signal. So an agent cannot (a) discover what policies exist, nor (b)
distinguish *"this policy is real but its cell is disabled"* from *"I
hallucinated this policy name."* Both render as `enabled: false, available_moves:
[]`. For an agent-first governance layer, "what can I even ask about" has no
answer inside the toolset.

**LEG-2 — error envelopes are inconsistent: one names the fix inline, the next is
a dead-end.** `class: bad-error / inconsistent-args · S2`
Triggered live:
  - `scan_route` → `INVALID_CELL_SPEC: Wardline routing is server-owned;
    configure LEGIS_WARDLINE_CELL or LEGIS_WARDLINE_CELL_BY_SEVERITY` — **names
    the exact env vars.** Excellent.
  - `filigree_closure_gate_get` → `CELL_NOT_ENABLED: binding ledger not enabled`
    — terse, **no remediation**, no pointer to `LEGIS_HMAC_KEY` / the cells
    config.
  Same server, two error qualities. The `next_action` table in the
  `legis-workflow` skill exists precisely to backfill the terse ones — which
  means the doc is *load-bearing for correctness*, not a nicety. Wardline solved
  this generically (`agent_summary.next_actions` inline on every result); Legis
  should carry `next_action` in the error envelope the same way. **Loop-closer:
  both live messages match the guidance I committed in `144fd10` — the doc edit
  is accurate.**

**LEG-3 — `scan_route` advertises a `cell` arg it silently ignores.** `class:
inconsistent-args / misleading-schema · S2`
The `scan_route` schema accepts `cell`. I passed `cell: "nonexistent-cell"` and
got the **generic** server-owned error — identical to passing no cell at all.
The supplied cell was discarded (request-side routing is gated behind
`LEGIS_UNSAFE_WARDLINE_REQUEST_ROUTING`), but the error never says "your `cell`
argument was ignored." A schema knob that does nothing by default, failing with a
message that doesn't mention the knob, is a trap an agent walks into once per
project.

**Passes (grep? NO):**
- `git_commit_get` → full structured commit (author, parents, files_changed,
  insertions/deletions) — better than parsing `git show`.
- `override_rate_get` → `PASS_WITH_NOTICE, rate: 0` with the honest note "measures
  operator force-pasts; not movable by agent retries" — tells the agent not to
  game it. Good.
- The discriminated-outcome design (`ROUTED` / `SKIPPED_DIRTY_TREE`,
  `CELL_NOT_ENABLED`) is the right shape; the gap is purely that some envelopes
  under-describe the next move (LEG-2).

**Not exercised — `override_submit` (correctly blocked).** The harness permission
layer denied it: submitting an override writes to the shared append-only audit
trail, which this recording task never authorized. That's the right call and I
did not work around it — so the disabled-cell override envelope is unobserved.
Worth a follow-up run *with explicit authorization* if you want that path
dogfooded.

---

## Live gate state (the demo is currently red)

Ran the project's own gates as the arbiter for WL-1. Both fail.

**DEMO-1 — `make verify` fails: 6 Loomweave-facet lacunae are not surfaced, and
the committed tour narrative is stale.** `class: correctness / coverage · S1`
```
VERIFY FAILED:
  - expected lacuna not surfaced: lw-dead-code (dead-entity)
  - expected lacuna not surfaced: lw-circular-import (circular-import)
  - expected lacuna not surfaced: lw-call-chain (execution-path)
  - expected lacuna not surfaced: lw-coupling-hotspot (coupling-hotspot)
  - expected lacuna not surfaced: lw-entry-point (entry-point)
  - expected lacuna not surfaced: lw-subsystem (subsystem)
  - docs/tour.md is stale — run `make tour` and commit
```
Six catalogued Loomweave lacunae are expected by `lacunae.toml` but the tour
harness reports them un-surfaced. **Root-caused live:** I called the underlying
facet tools directly and they *do* surface the lacunae —
`entity_dead_list` returns `specimen/dead_code.py`; `module_circular_import_list`
returns the `specimen.cycle_a ↔ specimen.cycle_b` cycle; `entity_coupling_
hotspot_list` returns ranked hotspots. So the Loomweave index is fine — **the
break is in the tour harness's query/match layer or a catalogue drift between
`lacunae.toml` and what the facets emit**, not the engine. Plus `docs/tour.md`
no longer matches generation. **`make ci` (= test + scan + verify) is red on two
of three stages.** This contradicts the "repivot complete, make ci passes" prior
state — it regressed and nothing caught it (no recorded PR/check data in Legis
either; `check_list` had nothing to read — the governance layer that's supposed
to catch this is itself unfed).

**DEMO-2 — `make scan` gate is RED (see WL-1).** `class: correctness · S1`
`gate: FAILED (--fail-on ERROR) — 1 active ERROR+ defect(s)`, exit 2, baseline
honored. The fingerprint-drift escape (WL-1) is what trips it.

These two are the specimen's *own* state, surfaced by its *own* tooling — the
dogfood pass's sharpest result is that the suite caught its own demo regressing,
but only because I ran the gates by hand. The engine warnings on the scan
(`WLN-ENGINE-FLOW-INSENSITIVE-FALLBACK` on `register_user`/`add_book` and several
tests) hint the resolver fell back to flow-insensitive mode — plausibly the same
resolution instability behind WL-1's fingerprint drift.

---

## Cross-tool consistency pass

These are invisible when you test one tool at a time. They are the "same idea,
different shape in each sibling" friction — the tax an agent pays for the suite
*being* a suite.

**X-1 — "who am I" has three incompatible models.** `class: inconsistent-args · S2`
| Tool | Identity arg | Model |
|------|-------------|-------|
| Filigree | `assignee` **and** `actor` | per-call; `actor` defaults to `assignee`; only claim verbs take `assignee` |
| Legis | `--agent-id` | **launch-bound** (set when the MCP server starts; not a per-call arg) |
| Wardline | — | no actor concept |
| Loomweave | — | no actor concept |
An agent moving filigree→legis in one task must switch from passing `assignee`/
`actor` per call to having its identity fixed at server launch. Nothing in either
toolset signals the handoff.

**X-2 — the same function has THREE names across the suite.** `class:
inconsistent-args · S2 · this is the single biggest paste-the-wrong-thing trap`
For `specimen.wardline_sinks.lookup_member`:
| Form | Who wants it | Example |
|------|-------------|---------|
| Loomweave entity id | `mcp__loomweave__*` | `python:function:specimen.wardline_sinks.lookup_member` |
| SEI | Filigree `entity_association_*` | `loomweave:eid:…` |
| bare qualname | Wardline `explain_taint(sink_qualname)`, Legis `policy_explain(entity)` | `specimen.wardline_sinks.lookup_member` |
Three identifiers, one entity, and the agent must know per-tool which dialect to
speak. Loomweave helpfully emits all of id+sei on every row — but nothing maps
the bare qualname *back* to an id/sei, so wardline→loomweave round-trips by
hand.

**X-3 — the cross-tool join key (wardline fingerprint) is unstable.** `class:
correctness · S1 · see WL-1`
The wardline fingerprint is the join key into both Filigree findings *and*
`baseline.yaml`. It folds in call-resolution state, so it drifts (WL-1), and when
it drifts the join silently breaks: baseline misses, Filigree duplicates. The one
identifier meant to be stable across the wardline→filigree→baseline seam is the
one that moves.

**X-4 — "suppressed" has three vocabularies.** `class: inconsistent-args · S2`
Wardline: `active / baselined / waived / judged`. Filigree finding `status`:
`open / acknowledged / false_positive / fixed / unseen_in_latest`, plus a
separate `suppression_state` (which is `null` even when wardline said baselined —
FIL-1). The SessionStart banner narrates in a *fourth* register:
"baselined/suppressed". An agent reasoning across the emit boundary has to
translate between vocabularies that don't have a clean mapping.

**X-5 — filter shape inverts between the two finding surfaces.** `class:
inconsistent-args · S2 · the "backwards in some but not others" you named`
Both Wardline `scan` and Filigree `finding_list` filter findings. Wardline:
**nested** `where: {rule_id, severity, kind, suppression, sink, tier, path_glob}`
— rich, including `kind`/`suppression`. Filigree: **flat top-level**
`file_id / severity / status / scan_source` — and missing exactly the
`kind`/`suppressed` axes (FIL-2) that wardline has. So the producer filters one
way with more power; the consumer filters another way with less. Port wardline's
`where` grammar onto `finding_list`.

**X-6 — context-overflow discipline is uneven.** `class: unusable-output · S2`
Wardline `scan` is bounded-by-default (≤25 bodies, `truncation.next_offset`
cursor) — it *cannot* blow your context, and says so. Filigree `finding_list`
defaults to `limit: 100`; my high-severity pull returned 22 full findings with
deeply-nested `metadata` and was enormous. Loomweave `entity_find` returned 21
rows unbounded. Only wardline treats "don't overflow the agent" as a default.
The good pattern exists in the suite; it just isn't adopted suite-wide.

**Cross-cutting positive — SEI rename-stability is the right spine.** Legis and
Loomweave both key on SEI so governance/identity survives rename/move. The design
instinct is correct; X-2/X-3 are about the *edges* between identifier dialects,
not the spine itself.
