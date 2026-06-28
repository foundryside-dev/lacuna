# PDR-0006 — Close PRD-0004: G1 met (4/4 MCP-first), reproduce-and-report moot

- **Date:** 2026-06-25
- **Status:** Accepted
- **Decider:** agent:claude-product-owner, executing under the human owner's explicit disposition this session (grant CONFIRMED as-is 2026-06-25)
- **Related:** PDR-0003 (committed the federation-seam bet + dispatched PRD-0004), PDR-0002 (consumer boundary), PRD-0004, metrics.md G1; superseded-by-successor: [[PDR-0007-plainweave-mcp-attachment-bet]]

## Context

PRD-0004 (MCP attachment truth) was dispatched 2026-06-13 to reproduce + report three
MCP-attachment gaps (Filigree→hub-not-repo, Loomweave→no-index, Legis→absent) so an agent
could reach all four documented cross-tool joins MCP-first. The bet then sat unadvanced
through the owner-directed Plainweave detour (~12 days). This session resumed it: resolved
its two open questions, then — instead of building the planned subprocess reproduction
harness — probed the gaps **directly through this attached session's `mcp__*` tools**, the
most faithful measurement of G1's "reachable MCP-first in one attached session."

## Decision

1. **Resolved PRD-0004's two open questions** (recorded in the PRD): (Q1) member-routed bug
   reports go to **the owning member's own tracker**; (Q2) "MCP-first reachable" means
   **auto-attach via `.mcp.json`**, with a member that architecturally cannot auto-attach
   making that constraint the reported finding. Both are now largely moot (no reports filed
   — see below), but stand as the routing/bar definitions for the successor bet.
2. **ACCEPTED the bet's outcome: G1 = 4/4.** Live in-session evidence (2026-06-25): all
   three "misattached" servers are attached and bound to `/home/john/lacuna`, and all four
   documented joins are reachable MCP-first:
   - Loomweave `project_status_get` → `project_root=/home/john/lacuna`, 423 entities, fresh.
   - Filigree `mcp_status_get` → `project_root=/home/john/lacuna`, schema 29/29.
   - Legis `doctor_get`/`posture_get` → responds, filigree-scoped to lacuna, no crash.
   - Joins: Wardline→Filigree findings present; Loomweave→Filigree enrichment (28 entities);
     Loomweave→Filigree issue-assoc channel reachable (`available:true`); Legis governance read.
3. **CLOSED PRD-0004.** The 0/4 baseline (06-13) was stale — member config-fixes since then
   closed the seams. **Criteria 1–2 (reproduce + report member bugs) are MOOT** — there are
   no member bugs to report; **criterion 3 (G1) is MET**, ahead of the 2026-09-13 target.
4. **Routed the unbriefed P1 `lacuna-5d0e4ba6d7`** (loomweave duplicate-locator / last-write-wins
   shadowing of `specimen.colliding.ShelfMark`) as a **loomweave bug report** (owner-approved),
   honouring the consumer boundary (PDR-0002): it is the planted `colliding.py` lacuna doing
   its job; Lacuna owes the report, loomweave owns the fix.

## Consequences

- PRD-0004 status → CLOSED (outcome met). The successor — plainweave MCP attachment — is a
  new Next bet ([[PDR-0007-plainweave-mcp-attachment-bet]]).
- metrics.md G1 reading 4/4 recorded; the original 4 frictions reduce (MCP attachment resolved).
- The planned reproduction harness (`docs/plans/2026-06-25-mcp-attachment-truth-harness.md`)
  is retained as record only; its characterization gate fired in-session and returned "resolved."
- No member repo, hub, or `.mcp.json` was modified; no environment reinstall performed.

## Reversal trigger

Reopen if a future attached-session probe shows **any of the 4 documented joins NOT reachable
MCP-first** (G1 drops below 4/4) — per G1's own trigger, a seam an agent must shell out for is
not fixed. Also reopen if the north-star (`make verify`) goes red for a **real specimen reason**
(an uncatalogued defect), as distinct from the known dirty-tree tooling-churn false alarm.
