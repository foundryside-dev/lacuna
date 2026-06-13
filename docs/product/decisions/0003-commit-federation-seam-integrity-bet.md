# PDR-0003 — Commit the federation-seam-integrity bet; dispatch MCP-attachment-truth

- **Date:** 2026-06-13
- **Status:** Accepted
- **Decider:** product-owner agent (DECIDE step, `/own-product` session; grant CONFIRMED, PDR-0001)

## Context

Bootstrap (PDR-0001) seeded "federation seam integrity, agent-native" as the
roadmap **Now** bet from observed direction; PDR-0002 confirmed the audience
sequence and the **consumer boundary** (Lacuna owes only a bug report). The Now
bet had a roadmap entry but no recorded decision committing it, and no dispatched
first workstream. This PDR records the DECIDE.

## Decision

1. **Commit "federation seam integrity, agent-native" as the active Now bet.**
   The federation's whole pitch is its cross-tool *joins*; a join that only works
   via raw shell undercuts "point the suite and watch it work." This is the bet
   the next slot of work serves.
2. **Dispatch "MCP attachment truth" as its first workstream** (roadmap Next →
   pulled into active dispatch). Specified by **PRD-0004**.
3. **Honour the consumer boundary in how the bet is judged.** Because Lacuna is a
   consumer of the federation (PDR-0002), its deliverable for any seam gap is the
   **reproduction fixture + bug report to the owning member**, never the fix.
   Therefore the bet's *outcome* metric (G1 seam health) is influenced but not
   controlled by Lacuna; acceptance is judged on the Lacuna-ownable deliverable,
   with G1 as the downstream signal.

## Consequences

- `metrics.md` G1 quantified: N=4 documented joins, baseline 0/4 MCP-first.
- Pending observation `lacuna-obs-8aa96160f2` (legis RecursionError) dismissed —
  resolved upstream, verified live 2026-06-13; it was the exemplar of the
  consumer boundary in action (Lacuna reported, legis fixed).
- PRD-0004 written specifying the MCP-attachment-truth workstream.

## Reversal trigger

Revisit if the dogfood signal shifts — e.g. if the major joins regress (G2
friction rising report-over-report) such that seam *function*, not seam
*reachability*, becomes the binding problem again; or if the owner reprioritizes
the Now bet away from seams (e.g. toward Rust-wing depth or demonstrator
graduation).
