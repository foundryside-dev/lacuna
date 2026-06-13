# PDR-0002 — Audience sequence + consumer boundary (owner-confirmed)

- **Date:** 2026-06-13
- **Status:** Accepted
- **Decider:** human owner (direct confirmation during `/own-product` session)

## Context

PDR-0001 bootstrapped the workspace from inferred state and left two questions
open, with a reversal trigger to revisit vision once the owner confirmed them.
The owner answered both directly this session.

## Decision

1. **Audience is both, in temporal sequence.** Lacuna is an **internal dogfood
   range now**, and **graduates into an external demonstrator once the suite is
   finished.** The two audiences are not co-equal today — demonstrator polish
   currently serves the dogfood range, and the "watch it work" external framing
   is a *future* end-state gated on suite completion, not an active goal.

2. **Lacuna is a consumer of the federation, not a part of it.** When dogfooding
   surfaces a federation-tool bug, **Lacuna only ever owes a bug report** — the
   specimen, a reproducing fixture, and the friction write-up. The fix lives in
   the owning member's repository. Lacuna never reaches across to fix another
   member, which is consistent with (and the reason behind) the authority grant
   escalating any change to the hub or another federation member.

## Consequences

- `vision.md` → *Who it serves* rewritten as a two-audience sequence; *Anti-goals*
  sharpened to "consumer, owes only a bug report."
- `roadmap.md` → *Later* gains "graduate from dogfood range to demonstrator,"
  gated on suite completion.
- `current-state.md` → both open questions marked resolved.
- PDR-0001's reversal trigger is now **satisfied** (audience + boundary
  confirmed). The only open bootstrap item remaining is operational: set `N` =
  total documented joins for guardrail G1.

## Reversal trigger

Revisit if the owner later decides Lacuna should ship as a demonstrator *before*
the suite is "finished" (collapsing the sequence), or if Lacuna is asked to carry
a federation-tool fix itself (breaking the consumer boundary) — either would be a
vision change requiring a new PDR.
