# Weft Federation — Senior Agent Dogfood Report
**Date:** 2026-06-11 · **Commit:** d233c32 · **Against prior report:** `docs/dogfood-findings.md` @ 144fd10 (2026-06-09)

**Method:** Live exploration of every tool surface (CLI + MCP) in a realistic agentic session.
Tools exercised: Filigree, Wardline, Loomweave, Legis. Charter: design-only, no live surface.

**Severity:** S1 = blocks / silent data corruption · S2 = obnoxious friction, tolerated · S3 = papercut/polish

**Friction class:** `missing-tool` · `missing-option` · `inconsistent-args` · `bad-error` · `unusable-output` · `discoverability` · `grep-loss`

**Status tags:** ✅ FIXED · ⬆ IMPROVED · 🔴 OPEN · 🆕 NEW (not in prior report)

---

## Demo gate state

| Gate | Status | Notes |
|------|--------|-------|
| `make scan` | **GREEN** ✓ | WL-1 fingerprint drift fixed by e385a13 re-baseline |
| `make verify` | **RED** ✗ | `docs/tour.md is stale` after d233c32 federation migration — run `make tour && git commit` |
| All lacunae surfaced | **GREEN** ✓ | The six Loomweave lacunae that DEMO-1 flagged are now surfaced correctly by d233c32 |

**Immediate action:** `make tour` then commit the regenerated `docs/tour.md`. The specimen and tooling are correct; only the narrative file needs regenerating.

---

## Top-3 to fix first (agentic blast radius order)

**1. N-3 + X-2** (scan root + qualname dialects): Silent failures that corrupt every cross-tool query. An agent that scans the wrong root gets wrong qualnames, no baseline suppression, and the wrong output path — zero errors, maximum confusion.

**2. N-4** (session-context CLI command names): The banner is the first thing an agent reads and acts on. Instructing `` `finding_list` `` when the CLI command is `filigree finding list` breaks the session before work starts. One-line template fix.

**3. N-5 + X-5** (severity case mismatch + filter-shape divergence): The two most-reached surfaces for "what broke?" speak opposite dialects. An agent writes the right query in the wrong case and gets silent empty results.

---

## Loomweave

### 🔴 LW-1 · S2 · `grep-loss` — `entity_find` is a name matcher, not a concept search

`entity_find "library"` → empty. `entity_find "borrow"` → empty. Both terms are present in the source; grep finds them immediately. `entity_find` matches entity name/short_name/summary, but summaries are off by default (LW-2), so it degrades to a Python-identifier substring matcher. Once you have a name fragment (`service`, `add_book`) recall is excellent — the cliff is concept word → grep wins.

**grep? YES** for any term that isn't a substring of a symbol name.

---

### 🔴 LW-2 · S2 · `missing-tool` — Semantic search, the "find by meaning" path, is off by default

`entity_semantic_search_list "main entry point"` → `result_kind: not_enabled`. This is the tool that would fix LW-1. The honest-empty (it names the disabled flag) is good design, but the capability the MCP banner advertises as the reason to pick Loomweave over grep is dark out of the box. Net: the two "find the thing that does Y" surfaces are (a) off and (b) name-only.

---

### 🔴 LW-3 · S2 · `unusable-output` — `scope_excludes` is an unconditional disclaimer; empty callers lists are un-trustable without grep

`entity_callers_list(hub.dispatch)` → 5 resolved callers AND `scope_excludes: ["attribute-receiver-calls"]`. The caveat fires even though the traversal successfully resolved all callers for this entity. An agent receiving an empty callers list cannot tell a true-empty (the entity really is dead) from a genuine blind-spot miss — so it must grep to confirm. The tool's own honesty disclaimer *causes* the grep fallback.

**Fix:** make `scope_excludes` per-query (did *this* traversal actually skip a candidate?), not a constant footer.

---

### 🔴 LW-4 · S3 · `discoverability` — One file, two entities, different `kind`

`entity_find "service"` returns both `python:module:specimen.service` and `core:file:specimen/service.py` for the same path. Minor "which one do I feed the next tool" tax; the `kind=` filter mitigates it if you remember it exists.

---

### 🔴 LW-5 · S2 · `unusable-output` — `entity_dead_list` over-reports; violates its own "fails toward live" contract

160 candidates on a 29-file project, including `specimen/cli.py` — which contains the catalogued `entry-point`-tagged entity `specimen.cli.main` that `entity_entry_point_list` returns in the same session. The docstring promises it "under-reports rather than over-reports." An agent hunting the one planted dead-code lacuna (`dead_code.py`) has to find it in a 160-row haystack that includes the app's own entry point. The signal is there but the noise floor defeats it.

Root cause: file/subsystem-kind nodes not sitting on call+import edges, so reachability can't reach them and marks them dead — but the result doesn't distinguish "structurally off-graph" from "genuinely unreachable."

---

### ✅ DEMO-1 · S1 — Six Loomweave lacunae unsurfaced (fixed by d233c32)

Previously `make verify` failed on all six Loomweave facet lacunae (dead-entity, circular-import, execution-path, coupling-hotspot, entry-point, subsystem). All now surface correctly. Only `docs/tour.md` is stale.

---

### What beats grep in Loomweave

- **`module_circular_import_list`** — one call, SCC members sorted, no grep equivalent for import cycles. Nailed `cycle_a ↔ cycle_b` exactly.
- **`entity_coupling_hotspot_list`** — confirmed `hub.dispatch` (fan-in 5, fan-out 5, coupling 10) as the top hotspot. No grep equivalent.
- **`entity_entry_point_list`** — instant, SEI-carrying, better than grepping `if __name__ == "__main__"`.
- **`entity_callers_list` (resolved edges)** — beat grep on the hard attribute-receiver case (`add_book`).
- **`entity_at` / `entity_neighborhood_get`** — callees/refs/container with byte offsets and confidence tiers. No grep equivalent.

---

## Wardline

### ✅ WL-1 · S1 — Fingerprint drift: baselined lacuna escaped baseline, gate was red (fixed by e385a13)

The live wardline fingerprint for `specimen.wardline_sinks.lookup_member` PY-WL-101 had drifted from the value in `baseline.yaml`. The baseline keyed on the old hash silently failed to suppress the new one, tripping `make scan`. `e385a13` re-baselined against the stabilised fingerprint; `make scan` is now green.

---

### ✅ WL-3 · S1 — Filigree emit 401 seam (confirmed still fixed)

Prior session memory flagged wardline→Filigree emit as 401. Confirmed live: `filigree_emit: { reachable: true, token_sent: true, auth_rejected: false }`. The project-scoped URL in `wardline.yaml` closed it.

---

### 🆕 N-2 · S2 · `missing-tool` — `wardline explain-taint` doesn't exist as a CLI command

```
$ wardline explain-taint ...
Error: No such command 'explain-taint'.
```

`mcp__wardline__explain_taint` exists and works. The CLAUDE.md `wardline-gate` skill describes a **scan → explain → fix → rescan** loop as the primary agent workflow. A CLI-only agent hits a dead end at step 2.

**Fix:** expose a thin `wardline explain-taint <fingerprint> [PATH]` CLI wrapper, or annotate the skill to state "MCP-only; no CLI equivalent."

---

### 🆕 N-3 · S2 · `inconsistent-args` + `bad-error` — Scan root governs qualnames; wrong root silently breaks all downstream cross-tool queries

Scanning a subdirectory vs the project root produces completely different qualname formats:

```
$ wardline scan specimen/   →   qualname: "trust_flow.unsafe_account_key"
$ wardline scan .           →   qualname: "specimen.trust_flow.unsafe_account_key"
```

Loomweave, Filigree, and `wardline dossier` all expect the full package-qualified form. Scanning a subdirectory silently:

1. Generates qualnames that don't match the other tools — cross-tool lookups return empty with no error
2. Misses the project-root baseline (`.weft/wardline/` is at root); all baselined findings surface as active
3. Writes output to the wrong location (`specimen/findings.jsonl` instead of `./findings.jsonl`)

**Confirmation:** `wardline findings specimen/ --where '{"qualname":"specimen.trust_flow.unsafe_account_key"}'` → empty; `wardline findings . --where '{"qualname":"specimen.trust_flow.unsafe_account_key"}'` → correct result.

`wardline scan --help` has no warning. Nothing prevents a CI step or agent from passing a subdirectory.

**Fix:** detect that the scan root is a subdirectory without a `.weft/wardline/` sibling and emit a warning. On the `dossier` path, try the package-qualified form before failing with "entity not found."

---

### 🆕 N-5 · S2 · `inconsistent-args` — `wardline findings --where` severity is uppercase; silent empty on mismatch

```
$ wardline findings . --where '{"severity":"WARN"}'   # → results
$ wardline findings . --where '{"severity":"warn"}'   # → empty, no error, no diagnostic
```

`filigree finding list --severity medium` uses lowercase. An agent that works with Filigree first, learns lowercase, then switches to wardline gets silent empty results. See also X-5 in the cross-tool section.

**Fix:** standardize on one case across the suite and reject the other with a clear error. Or accept both in each tool.

---

### 🆕 N-8 · S3 · `inconsistent-args` — `wardline dossier` CLI rejects Loomweave/Filigree-format qualname

```
$ wardline dossier specimen.trust_flow.unsafe_account_key specimen/
error: entity not found in scanned set: specimen.trust_flow.unsafe_account_key

$ wardline dossier trust_flow.unsafe_account_key specimen/
{ ... works ... }
```

`mcp__wardline__dossier` accepts either form. The CLI requires the scan-relative form. An agent that receives a qualname from Loomweave and passes it to the CLI dossier hits a misleading "not found" error when the entity is present.

**Fix:** apply the same resolution logic the MCP tool uses. At minimum: `entity not found — if you passed a package-qualified name, try without the leading prefix relative to PATH`.

---

### What beats grep in Wardline

- **`scan.agent_summary`** is the gold standard for the suite: active defects first, each with pre-populated `next_tool_calls` carrying the exact fingerprint; explicit `next_actions`; `truncation.next_offset` cursor; bounded by default (≤25 bodies). Zero ambiguity about the next move. Every other tool result should look like this.
- **`assure --format human`** — "Trust-surface coverage: 100.0% (26/26 boundaries)" in one line. No grep equivalent for coverage posture.
- **`scan --where`** filter (`rule_id`, `severity`, `kind`, `suppression`, `sink`, `tier`, `path_glob`) is richer than Filigree's `finding list` and should be ported there.

---

## Filigree

### ⬆ FIL-1 · S1 → S2 — Session-context finding count was false; now improved

Previously: `session_context` reported "0 baselined/suppressed" when every real defect was baselined — an agent that trusted it would promote ~100 intentional flaws as real issues.

Now: correctly shows "73 actionable, 34 baselined/suppressed". The split is accurate. However, the 73 "actionable" are mostly low-severity engine telemetry (WLN `kind:metric` unresolved-calls findings), not real defects. An agent reading "73 actionable" and running `filigree finding list` to triage them will see a wall of noise before the signal.

---

### ✅ FIL-2 · S2 — `kind` filter missing from `finding list` (fixed)

`--kind defect/fact/metric/suggestion` now exists on `filigree finding list`. The prior "no kind filter" gap that forced client-side jq filtering is closed.

---

### 🔴 FIL-3 · S2 · `inconsistent-args` — "Who am I" is `assignee` or `actor` depending on the verb

`work_start`/`work_start_next` require `assignee` and accept `actor` (defaults to assignee). `finding_promote`, `observation_create`, `work_release` take `actor` only. An agent must re-derive the identity parameter name per verb within the same tool. See also X-1 in the cross-tool section.

---

### 🆕 N-4 · S2 · `bad-error` / `discoverability` — Session-context names MCP verbs as CLI commands

```
ANALYZER FINDINGS: 107 not yet bridged — review with `finding_list`, bridge with `finding_promote`
```

`finding_list` and `finding_promote` are MCP verb stems. The CLI commands are `filigree finding list` and `filigree finding promote`. An agent in a CLI-first session runs the backtick'd string and gets `No such command`. This is the first instruction an agent acts on.

**Fix:** use CLI forms in the session-context output, or show both: `` `filigree finding list` (CLI) / `finding_list` (MCP) ``.

---

### 🆕 N-6 · S2 · `missing-option` — `filigree list --priority` is exact-match only; no range filter on issues

```
$ filigree list --priority 2   # only P2 — not "P2 or above"
```

An agent wanting "all high-priority issues" must run multiple queries and merge. The inconsistency across surfaces compounds the problem:

| Surface | Priority filter |
|---------|----------------|
| `filigree list` CLI | `--priority N` (exact match only) |
| `filigree observation list` CLI | `--priority-min` + `--priority-max` |
| `mcp__filigree__work_start_next` | `priority_min` + `priority_max` |
| `mcp__filigree__work_ready` | no filter at all |

The observation sub-command solved this correctly. Port the same flags to `issue list`.

---

### 🆕 N-7 · S3 · `discoverability` — `filigree observation create` doesn't exist; natural first-try fails silently

```
$ filigree observation create "noticed a smell"
Error: No such command 'create'.
```

The actual verb is the top-level `filigree observe`. The group help explains this, but only after you hit the error.

**Fix:** add `filigree observation create` as an alias, or add a hint to the error: `No such command 'create' — use \`filigree observe\` to record a new observation.`

---

### What beats grep in Filigree

- **`issue_get` with `include_transitions=true`** — `valid_transitions` with `ready`/`missing_fields`/`enforcement` per transition. The ready≠startable model is legible from one read.
- **MCP schemas are unusually self-documenting** — `work_start` describes `AmbiguousTransitionError` and the triage-bug advance walk inline. Discoverability of *behaviour* is high even where *args* are inconsistent.

---

## Legis

### ⬆ LEG-1 · S2 — No policy discovery verb (partially fixed)

`mcp__legis__policy_list` now exists and returns the full routing table with each cell's real enabled state. This closes the "I can't discover what policies exist" gap.

What remains: `policy_explain` still answers for non-existent policy names with no "unknown" signal — see N-9 below.

---

### 🔴 LEG-2 · S2 · `bad-error` — Error envelope quality is uneven

Two errors triggered live in the same server session:

- `scan_route` with agent-supplied routing → `INVALID_CELL_SPEC: Wardline routing is server-owned; configure LEGIS_WARDLINE_CELL or LEGIS_WARDLINE_CELL_BY_SEVERITY` — **names the exact env vars.** Excellent.
- `filigree_closure_gate_get` → `CELL_NOT_ENABLED: binding ledger not enabled` — terse, **no remediation**, no pointer to `LEGIS_HMAC_KEY`.

Same server, two error qualities. The `legis-workflow` skill exists to backfill the terse ones, making the doc load-bearing for correctness rather than a nicety. Wardline solved this generically with `agent_summary.next_actions` inline on every result — Legis should carry `next_action` in the error envelope the same way.

---

### ⬆ LEG-3 · S2 — `scan_route` `cell` arg silently ignored (improved)

Previously: passing `cell: "nonexistent-cell"` produced the same generic server-owned error as passing no cell at all — the supplied arg was discarded silently.

Now: returns `INVALID_CELL_SPEC` naming the required env var (`LEGIS_UNSAFE_WARDLINE_REQUEST_ROUTING`). No longer silent. Still slightly misleading because the schema advertises the `cell` param without explaining it's gated — consider adding a note in the schema description.

---

### 🆕 N-1 · S2 · `missing-tool` — `legis session-context` is silently empty

```
$ legis session-context
$               # exit 0, no output
```

Every other tool's `session-context` emits at minimum a status banner. An agent calling this during session initialization gets no signal and cannot distinguish "nothing to report" from "command is broken" from "server not running."

**Fix:** print a one-line posture summary (`legis: governance db absent, cells: all disabled`) rather than exiting silently.

---

### 🆕 N-9 · S2 · `bad-error` — `policy_explain` answers for non-existent policies; no "unknown" signal

```
policy_explain(policy="completely-made-up-policy-xyz")
→ {"cell":"structured", "matched_rule": null, "enabled": false, "available_moves": []}
```

`matched_rule: null` is the only distinguisher from a real policy that falls through to the default cell. An agent cannot tell "this policy is real but its cell is disabled" from "I hallucinated this policy name." Both render identically. `policy_list` now exists (good) — but an agent discovering a new policy name from another tool still can't validate it without knowing the `matched_rule: null` signal.

**Fix:** add a `policy_known: false` boolean when no rule pattern matched, or return a `POLICY_NOT_FOUND` error for unrecognized names.

---

### What beats grep in Legis

- **`git_commit_get`** — structured commit (author, parents, files_changed, insertions/deletions). Better than parsing `git show`.
- **`override_rate_get`** — `PASS_WITH_NOTICE, rate: 0` with the note "measures operator force-pasts; not movable by agent retries." Tells the agent not to game it.
- **Discriminated outcome design** (`ROUTED` / `SKIPPED_DIRTY_TREE` / `CELL_NOT_ENABLED`) is the right shape; the gap is purely that some envelopes under-describe the next move.

---

## Cross-tool

### 🔴 X-1 · S2 · `inconsistent-args` — "Who am I" has three incompatible identity models

| Tool | Identity arg | Model |
|------|-------------|-------|
| Filigree | `assignee` **and** `actor` | per-call; `actor` defaults to `assignee`; only claim verbs take `assignee` |
| Legis | `--agent-id` | **launch-bound** (set at MCP server start; not a per-call arg) |
| Wardline | — | no actor concept |
| Loomweave | — | no actor concept |

An agent moving Filigree → Legis in one task must switch from passing `assignee`/`actor` per call to having its identity fixed at server launch. Nothing in either toolset signals the handoff.

---

### 🔴 X-2 · S2 · `inconsistent-args` — One entity has three identifier dialects across the suite

For `specimen.wardline_sinks.lookup_member`:

| Form | Who wants it | Example |
|------|-------------|---------|
| Loomweave entity id | `mcp__loomweave__*` | `python:function:specimen.wardline_sinks.lookup_member` |
| SEI | Filigree `entity_association_*` | `loomweave:eid:…` |
| bare qualname | Wardline `explain_taint`, Legis `policy_explain` | `specimen.wardline_sinks.lookup_member` |

Three identifiers, one entity, and the agent must know per-tool which dialect to speak. Loomweave helpfully emits all three on every row — but nothing maps a bare qualname *back* to an id/sei, so wardline→loomweave round-trips require manual construction. N-3 adds a fourth dialect variant: the scan-relative form (`wardline_sinks.lookup_member`) produced when scanning a subdirectory.

---

### 🔴 X-4 · S2 · `inconsistent-args` — "Suppressed" has three vocabularies

| Surface | Vocabulary |
|---------|-----------|
| Wardline | `active / baselined / waived / judged` |
| Filigree finding `status` | `open / acknowledged / false_positive / fixed / unseen_in_latest` |
| Filigree `--suppression` filter | `active / all / baselined / judged / waived` |
| Session-context banner | `actionable / baselined/suppressed` (plain English) |

An agent reasoning across the emit boundary must translate between vocabularies without a canonical mapping. Notably, Filigree's `finding status` field doesn't contain any of the wardline suppression states — they live in a separate `suppression_state` projection.

---

### 🔴 X-5 · S2 · `inconsistent-args` — Filter shape inverts between the two finding surfaces

Both Wardline `scan`/`findings` and Filigree `finding list` filter findings. Wardline: **nested** `where: {rule_id, severity, kind, suppression, sink, tier, path_glob}`. Filigree: **flat** `--severity / --status / --kind / --rule-id / --qualname`. The producer filters one way; the consumer filters another. Plus N-5's case mismatch sits on top: `wardline --where severity "WARN"` vs `filigree --severity medium`.

**Fix:** port wardline's `where` vocabulary (especially `sink` and `tier`) to filigree as flat flags; standardize severity casing across both.

---

### 🔴 X-6 · S2 · `unusable-output` — Context-overflow discipline is uneven

Wardline `scan` is bounded by default (≤25 bodies, explicit truncation cursor) and cannot overflow context. Filigree `finding list` defaults to `limit: 100` with full nested `metadata` per row — a pull of 73 findings is enormous. Loomweave `entity_find` returns up to 20 rows unbounded. Only wardline treats "don't overflow the agent" as a first-class default. The good pattern exists in the suite; it isn't adopted suite-wide.
