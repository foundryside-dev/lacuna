# PDR-0014 — Phase-0 spike strengthened the 4 path-members to path-AND-store binding (beyond the reviewed plan)

- **Date:** 2026-06-28
- **Status:** Accepted (technical refinement within the execution grant; owner informed in-session and invited to veto, no objection).
- **Decider:** agent:claude-product-owner carried the spike finding forward; human owner informed ("flag me if you'd rather the gate stay path-only for the legacy four").
- **Related:** [[PDR-0012]], [[PDR-0013]], docs/plans/phase0-findings.md, [[mcp-attachment-harness-state]] memory.

## Context

The 3×-reviewed plan had the 4 self-report members (loomweave/filigree/legis/plainweave) verify binding by a **path** predicate (the server-resolved `project_root == ROOT`, etc.). The Phase-0 feasibility spike — the first time the binding tools were probed live across all 6 — found path-only **insufficient**: a path can echo ROOT while the member's store is unreadable, which is *exactly* the 2026-06-26 stale-binary incident class. The spike also surfaced three distinct response-unwrap shapes (loomweave + filigree use a `content[0].text` JSON blob, not `structuredContent`) and that filigree's SSE transport requires an `Accept: application/json, text/event-stream` header (else a silent HTTP 406).

## Decision

Carried the spike's strengthening forward: the gate now asserts **path AND a store-read signal** for all 4 path-members (loomweave `db_present` + `data_version`; filigree `db_initialized` + `schema_compatible`; legis store binding/governance chains; plainweave `initialized` + `schema_version`) — matching the store-read approach R1 gives warpline/wardline. This **deviates** from the reviewed plan (path-only for those 4). The owner was told and did not object. `docs/plans/phase0-findings.md` is now the authoritative binding contract (supersedes the plan's pre-spike path-only table).

## Consequences

- The gate catches the stale-binary incident class for ALL 6 members, not just on process-start — a stronger gate than the reviewed plan specified.
- Each path-member has a binding-predicate test that **fails a path-only implementation** (verified by a mutation test in the final whole-branch review) — the strengthening is regression-protected.
- A worked example of the spike doing its job: it caught a real gap in a thrice-reviewed design before any code shipped.

## Reversal trigger

If a store-read signal for a path-member drifts across legitimate member versions (false-reds a healthy member), narrow *that* member's predicate to the stable signal, recording the change — do not silently revert to path-only, which re-opens the incident-class blindness.
