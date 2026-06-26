# PDR-0009 — Redefine G1 as a live join census; ratify plainweave→loomweave into it

- **Date:** 2026-06-26
- **Status:** Accepted (owner ratified the plainweave→loomweave addition via `/own-product` AskUserQuestion this session; the census framing is acceptance-criteria design within grant)
- **Decider:** human owner (John) ratified the join addition; agent:claude-product-owner for the census reframe
- **Related:** metrics.md G1, PDR-0006 (G1 4/4 baseline), PDR-0010 (Phase-1 accept), [[loom-join-census-live-not-count]] memory (owner directive "watch for the new ones")

## Context

G1 (federation seam health) was defined 2026-06-13 as **"4 documented cross-tool joins reachable MCP-first"** — a hand-set integer. This session a **live census** of the join-bearing MCP surfaces showed the set is both richer and actively growing (owner, verbatim: _"we've been working to build out those interfaces, so watch for the new ones"_):

- **plainweave→loomweave** (catalog + entity-intent) — LIVE
- **plainweave→legis** preflight facts — LIVE
- **legis→loomweave** git rename-feed — LIVE
- **filigree↔loomweave** entity-assoc reverse-lookup (ADR-029) — LIVE but empty
- **legis→filigree** closure gate — REACHABLE but operator-gated (`CELL_NOT_ENABLED`, needs `LEGIS_HMAC_KEY`)

A frozen integer silently under-reports as new joins ship, and mis-scores honest non-live states (a naive reachability check would fail the gated legis gate or, worse, fake it live).

## Decision

1. **Ratify plainweave→loomweave into G1's enumeration** (owner-confirmed).
2. **Redefine G1 as a live join census**, not a static count: measured each session (and durably by the Phase-2 6-member harness), emitting the count **plus a per-join liveness class** — `live-bound | live-empty | reachable-gated | absent`. The original four joins remain members; the metric tracks reality, so the next new interface is caught automatically.

## Consequences

- metrics.md G1 rewritten from a fixed-N target to a census with liveness classes.
- The Phase-2 harness scope upgrades from "6 servers handshake" to "assert the join census with honest liveness classes" — honest-degrade (G3) becomes load-bearing.
- The plainweave→loomweave join is now a counted G1 member (see PDR-0010).

## Reversal trigger

If the live census proves too unstable to gate on (joins flap reachable/absent across runs), fall back to asserting per-join liveness **class** rather than exact reachability, and record the flap as a consumer-boundary finding — do **not** loosen G1 to paper over a real de-attach (that inverts the guardrail).
