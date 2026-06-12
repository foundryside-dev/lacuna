# Weft federation dogfood report — 2026-06-12

**Method:** one agent session in `/home/john/lacuna`, exercising every reachable
MCP tool and CLI verb of filigree, loomweave, wardline, and legis against the
live lacuna index/tracker/baseline. Write paths were exercised on throwaway
artifacts and cleaned up (two test issues created → cycled → hard-deleted; tree
verified clean after). One genuine observation was left in filigree
(`lacuna-obs-8aa96160f2`, the legis RecursionError).

**Framing question per the brief:** *would an agent reach for these tools
first, ahead of grep/Read/Bash?* Verdicts at the end.

---

## A. Broken — didn't work right

### A1. wardline `fix` crashes on any invocation (even dry-run)
`mcp__wardline__fix {dry_run: true}` →
`wardline internal error: '/home/john/lacuna/specimen/wardline_boundaries.py' is not in the subpath of '.'`
Path-relativization bug: the MCP server's `--root .` is compared against
absolute file paths. The only autofix verb is unusable.

### A2. legis `policy-boundary-check` dies with RecursionError on a hostile file
Walking `specimen/nesting_bomb.py` (the planted lw-too-complex lacuna) blows
the recursion limit in `legis/policy/boundary_scan.py`:
- **CLI:** raw traceback on stderr, **empty stdout, exit 1** — indistinguishable
  from "violations found" for any caller switching on exit code.
- **MCP:** wrapped as structured `INTERNAL_ERROR` (better), but
  `next_action: "Inspect the error message before retrying"` is boilerplate,
  and `recoverable: false` is all you get.
The tour only works because `tour/steps.py:977` shells the venv python with
`sys.setrecursionlimit(100000)`. Upstream fix: per-file degrade (skip + flag),
exactly loomweave's `LMWV-PY-TOO-COMPLEX` posture. Filed as observation
`lacuna-obs-8aa96160f2`.

### A3. wardline `scan_file_findings` rejects wardline's own configured URL
`.mcp.json` launches wardline with
`--filigree-url http://127.0.0.1:8749/api/p/lacuna/weft/scan-results` (a full
*endpoint*). `scan`'s emit path accepts it (149 findings updated, auth ok), but
`scan_file_findings` refuses:
`filigree URL must be a Weft endpoint containing '/api/weft/'`.
Same config value, two interpretations. The flag should take a **base URL**
(plus project) and each code path should derive its route.

### A4. wardline → filigree work-joins all 404
`dossier.work`, and the `work` block on **every one of 33** `decorator_coverage`
rows: `"filigree returned HTTP 404"`. Almost certainly the same root cause as
A3 — routes derived from an endpoint-shaped URL. Net effect: the dossier's
"open work joined on SEI" promise is dead in practice, on the one repo where
everything is supposedly wired.

### A5. loomweave → filigree enrichment 401s
`entity_orientation_pack_get`, `entity_issue_list`'s `wardline_findings`
section, and (consequently) `entity_wardline_list` taint facts:
`Filigree returned HTTP 401: Missing or invalid bearer token`.
Filigree requires a bearer token (see `.mcp.json`); loomweave's own
filigree client doesn't send one. The *issues* join works (different path);
the *wardline-findings* join never can. Honest degrade text, but the seam is
broken on the flagship demo.

### A6. legis MCP server registered, healthy — and absent from the session
`.mcp.json` registers `legis mcp --agent-id claude-code`; a manual JSON-RPC
probe shows it initializes instantly and serves **21 well-schema'd tools**
(`policy_explain`, `policy_list`, `override_submit`, `scan_route`,
`git_rename_feed_get`, `filigree_closure_gate_get`, …). Yet zero
`mcp__legis__*` tools surfaced in this session, while CLAUDE.md instructs
agents to *prefer* them. Whether harness or server handshake, this is the
single biggest "agent can't reach for it first" failure: the governance tool
is effectively CLI-only in real sessions.

### A7. wardline `rekey` probe reports a healthy baseline as 100% orphaned
Read-only probe on a clean tree: `matched: 0, orphaned: 44/44, clean: false`,
cause string "source moved/deleted, or a custom multi-emit rule…". The same
scan run shows all 44 baseline entries matching and suppressing findings. An
agent consulting the probe before a migration would conclude the entire
baseline is dead. Either the probe is comparing the wrong scheme (no migration
is pending — it should report a clean no-op) or it's plain wrong. Also: 44 raw
fingerprints dumped inline is token noise; counts + a sample would do.

---

## B. Misleading — worked, but the answer points the wrong way

### B1. Two freshness oracles, opposite verdicts (loomweave)
At the same instant: `project_status_get` → `staleness: "stale"` (+ orientation
packs warn "re-run analyze", + the SessionStart hook said the same) while
`index_diff_get` → `overall: "fresh"`, `drift_detected: false`,
`modified_since_analyze: []`, commit match. A re-analyze cleared the flag
(incidentally re-processing exactly 1 python file every run — mtime-based
detector, presumably the cause). Agents need ONE freshness verdict, or an
explicit pointer from each surface to the authoritative one.

### B2. `entity_dead_list` is unusable as a survey
225 of 369 entities flagged on a tree whose runtime entry points are indexed.
Specific failures: `.env.example` listed as dead *code*; `specimen-rs/src/main.rs`
dead because **Rust binary roots aren't in the root set** (only python
`entry-point` tags are); fully-redacted rows (`briefing_blocked:
"secret_present"` with id/name/path all null) that can't be acted on or even
identified; the same five-line `reason` string repeated verbatim on all 20 rows
of every page.

### B3. filigree `stats_get.blocked_count` disagrees with `work_blocked`
`blocked_count: 0` while `work_blocked` returned one blocked issue (it was
wip-category). Two definitions of "blocked"; neither says so.

### B4. `issue_close` default target is type-blind
Closing a bug at `confirmed` defaulted to target `closed` — not a bug-type
done state and not reachable — yielding INVALID_TRANSITION. The docstring
promises "first done-category state **for the type**". The error recovery was
excellent (valid_transitions listed), but the default forced a retry.

### B5. `issue_search` silently can't see labels
`issue_search "dogfood-exercise"` → 0 results, while two issues carried exactly
that **label** (the hyphen triggers LIKE fallback over title/description only).
The label filter lives on `issue_list`, but search returning empty with no
"labels not searched" hint is a silent miss an agent won't recover from.

### B6. wardline `scan summary_only=true` returned 59 kB
Documented as "the smallest 'did the gate pass?' payload", it blew the MCP
token cap and spilled to a file. Cause: `legis_artifact` (55,963 chars — all
149 findings, verbatim, signed) auto-attached even though `legis_artifact:
true` was **not** passed. The artifact must respect `summary_only`/opt-in.

### B7. `explain_taint` explains nothing on the flagship sentinel
On PY-WL-125 (`log_export_request`): `immediate_tainted_callee: null`,
`source_boundary_qualname: null`, chain of one hop with null contributor, and a
generic remediation ("Review the finding and apply the rule-specific fix").
The taint source (`read_report_field`, 3 lines up) is never named. If the
chain walk needed the Loomweave store and didn't have it, the response should
say so explicitly (cf. B8).

### B8. wardline `doctor` contradicts the server's own launch args
`doctor` reports `loomweave.url: not configured` and `filigree.url: not
configured` while `.mcp.json` launches the same server with both
`--loomweave-url` and `--filigree-url`, and the dossier successfully reads the
loomweave store. Doctor is checking a config file, not the runtime wiring it's
supposed to vouch for.

### B9. ADR-029 round trip works — but hydration and adoption gaps blunt it
- `entity_association_add` → loomweave `entity_issue_list` matched with
  `drift_status: "matched"`, and the reverse lookup computed
  `freshness_status: "fresh"`. The mechanism is sound.
- But the matched row carries `issue: null` — no title/status despite
  `filigree_issues_returned_total: 1` — so the agent needs a second filigree
  call per issue.
- And nothing in the live workflow *creates* these bindings: the tour's
  promoted sentinel issue is invisible from every loomweave entity surface
  because `finding_promote` links files, not SEIs.
  `finding_promote_and_attach_entity` and `file_finding
  {attach_loomweave_identity}` exist but are opt-in and unused. Findings carry
  qualnames; promotion should attach the SEI by default when resolvable.

### B10. Duplicate findings, contradictory facet text (loomweave)
`project_finding_list` shows two `LMWV-SEC-SECRET-DETECTED` rows for
`specimen/policy_boundaries.py:41` (different finding ids from different runs)
— per-run dedup gap. And `entity_tag_list`'s honest-empty reason claims "the
Python plugin emits none today" while `test`/`data-model`/`entry-point` tags
are demonstrably populated.

---

## C. Friction — missing options, second calls, token waste

| # | Tool | Gap |
|---|------|-----|
| C1 | `entity_callers_list` | Rows carry **byte offsets only** — no line number or line text. `entity_call_site_list` has both, so "who calls X, where" is always two calls. Inline `line`/`line_text` on callers. |
| C2 | `entity_execution_path_list` | ~110 near-duplicate path arrays for one small module (`run_tour`/`run_verify` re-enumerate every downstream path). No path-count cap, no tree/DAG form. Unusable on a real codebase. |
| C3 | `project_finding_list` / `entity_finding_list` | Filter supports kind/severity/status but **not `rule_id` or file/path** — the two things an agent actually pivots on. |
| C4 | `entity_find` | No path/scope filter (every facet tool has `scope`; the main search doesn't). |
| C5 | `entity_summary_get` | Write-gated even though reading a *cached* summary spends nothing. The cost-preview tool is registered; the spend/read tool never is. Pair them. |
| C6 | wardline waivers | `waiver_add` exists; **no `waiver_list` / `waiver_remove`**. Waiver hygiene (the thing 05-false-positive discipline cares about) requires hand-editing YAML. |
| C7 | `assure` | `unknown[]` rows have `reason: null` — "honestly unknown" with no why. |
| C8 | legis CLI | `check-override-rate` / `governance-gate` print one-line plain text, no `--json`. `policy_list` has no CLI counterpart at all. |
| C9 | filigree CLI | `finding list` plain-text default truncates the message mid-word ("EXTERNAL_RAW (unt"). |
| C10 | filigree MCP writes | Every write (even `label_add`) returns the full PublicIssue (~1 kB). Good for state sync, but a `slim: true` option would cut sustained-session token cost substantially. |
| C11 | filigree events | The dependency event on the *blocked* issue reads `new_value: "blocks:lacuna-93bb…"` — inverted semantics for a reader. |
| C12 | Degrade-reason repetition | `decorator_coverage` repeats the identical filigree-404 `work` block 33×; `entity_dead_list` repeats its reason per row. Hoist repeated degrades to one top-level marker. |
| C13 | `dependency_add` | Happily blocks an already-claimed in-progress issue with no warning. |

---

## D. What is genuinely right (keep, and make the norm)

- **Honest-empty signals** (loomweave): every empty list says *why* it's empty
  (`signal.available/reason`, `scope_excludes`, `unresolved_name_matches`).
  This is the single best agentic-first pattern in the federation.
- **filigree error shapes**: `INVALID_TRANSITION` returning `current_status`,
  `next_action`, `valid_transitions` with readiness, and a hint is exactly
  what an agent needs to self-correct in one hop. `work_start advance=true`
  walking soft transitions with field warnings is excellent.
- **`issue_delete` receipts** (per-table cascade counts) and tombstones.
- **`entity_resolve`**: batch, order-preserving, `::`-normalizing, honest
  `unresolved`/`ambiguous` — never errors, never fabricates.
- **Orientation pack** `suggested_next_reads` (tool + args + why) is a model
  for cross-tool handoffs.
- **attest → verify_attestation** round trip: `signature_valid: true,
  reproduced: true` first try.
- **judge**'s no-key error is honest and actionable; **baseline** refuses to
  clobber by default; **scan** is bounded by default with a real pagination
  contract.
- **legis MCP structured errors** (`error_code`/`recoverable`/`next_action`)
  — right shape, even when (A2) the content is boilerplate.

---

## E. Verdicts — "would I reach for it first?"

- **filigree: yes, unreservedly.** The MCP surface is the most agent-native
  issue tracker I've used; the error contracts actively teach the workflow.
  Fix the search/label blind spot (B5) and stats skew (B3).
- **loomweave: yes for graph questions** (callers, where-defined, resolve,
  relations, subsystems) — genuinely faster and more trustworthy than grep,
  and the honesty discipline means empties are believable. **Not yet** for the
  survey tier (dead-list B2, execution-paths C2) or anything that crosses into
  filigree (A5).
- **wardline: yes for scan/gate/dossier/assure** — `scan` with `where` +
  `explain` and the bounded default is a strong primary loop. But `fix` (A1),
  `rekey` (A7), the URL/seam mess (A3/A4/B8), and an `explain_taint` that
  can't name the boundary (B7) mean the edges can't be trusted blind yet.
- **legis: cannot be reached for first today** — not because the tools are bad
  (the MCP catalog is well-designed) but because they don't surface in the
  session (A6), and the one CLI verb an agent would run unprompted
  (`policy-boundary-check`) crashes on a file this very repo plants (A2).

## F. Cross-cutting recommendations (ranked)

1. **Fix the seams, then re-dogfood**: A3/A4 (wardline→filigree URL), A5
   (loomweave→filigree token), A6 (legis MCP in-session). The federation's
   pitch is the joins; today every join except loomweave→filigree-issues is
   broken in some direction.
2. **One freshness oracle** per tool (B1, B8): status surfaces must agree or
   defer to a named authority.
3. **Fail-degraded, never fail-dead** on hostile inputs (A2; loomweave already
   does this — make it a federation-wide contract, and add a conformance
   fixture like `nesting_bomb.py` to each member's test corpus).
4. **Respect the payload contract**: `summary_only` means small (B6); probes
   report counts not 44 fingerprints (A7); hoist repeated degrade blocks (C12).
5. **Close the loop on SEI bindings** (B9): promote-with-entity by default;
   hydrate `issue` in loomweave's matched rows.
6. **Add the missing inverse/list verbs**: waiver_list/remove (C6),
   rule_id/file finding filters (C3), labels in search or a search hint (B5).
