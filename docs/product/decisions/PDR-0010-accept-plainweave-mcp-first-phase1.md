# PDR-0010 — Accept PDR-0007 Phase 1: plainweave reachable MCP-first

- **Date:** 2026-06-26
- **Status:** Accepted (ACCEPT against the bet's criteria, under the standing grant)
- **Decider:** agent:claude-product-owner
- **Related:** PDR-0007 (the bet), `docs/plans/2026-06-26-plainweave-mcp-attachment.md` (Phase 1), PDR-0009 (G1 census), metrics.md G1

## Context

PDR-0007 Phase 1 (reinstall plainweave 1.0.0 + wire `.mcp.json`) was executed between the last checkpoint and this session (commits `b36a33c`, `11170cc`). Its acceptance step was deferred — _"plainweave reachable MCP-first, bound to the staged repo"_ can only be confirmed in a session that **re-attaches** after the `.mcp.json` change.

This session ran in such a re-attached session. `mcp__plainweave__plainweave_project_context_get` returned `ok / initialized`, bound to project `lacuna` at `.plainweave/plainweave.db`, producer **v1.0.0**, and the plainweave→loomweave catalog read returned live data. The Phase-1 "PENDING (next session)" criterion is met.

## Decision

**Accept PDR-0007 Phase 1 as DONE** — the "wire the newest member MCP-first" half of the bet is satisfied. Phase 2 (the durable **6-member attachment regression-harness**) remains open and is now the live Next item, with scope upgraded to the join census (PDR-0009).

## Consequences

- roadmap.md Next: Phase 1 marked complete; Phase 2 carried forward with census scope.
- plainweave→loomweave folded into G1 as a counted member (PDR-0009).
- The MCP-attachment-truth theme is validated — but see PDR-0011: this session also proved the gate did **not** catch a silent loomweave de-attach, which is exactly the hole Phase 2 must close.

## Reversal trigger

If any future session finds plainweave **not** reachable MCP-first (a silent de-attach), reopen — and that silent de-attach is precisely what the Phase-2 harness must trip on `make verify`, rather than being found by manual probing (the PDR-0011 lesson).
