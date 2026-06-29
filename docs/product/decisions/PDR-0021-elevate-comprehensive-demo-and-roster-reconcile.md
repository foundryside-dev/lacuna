# PDR-0021 — Elevate the comprehensive demo to primary intent; reconcile the roster (charter→plainweave, +tabard)

- **Date:** 2026-06-29
- **Status:** Accepted (owner-directed via `/product-checkpoint` session — an explicit, recorded vision change, not a silent edit)
- **Decider:** human owner (John) directed the change; agent:lacuna-po recorded + edited the living artifacts
- **Supersedes:** PDR-0002's **audience-sequence** half (the "internal dogfood now → external
  demonstrator later, gated on suite completion" temporal ordering). PDR-0002's **consumer-boundary**
  half is **unchanged and still in force**.
- **Related:** PDR-0020 (comprehensive-coverage theme — this is its vision-level corollary),
  PDR-0008 (ratified plainweave; its "charter design-only" enumeration is now reconciled here),
  `vision.md`, `roadmap.md`, `metrics.md` (G3), `docs/matrix.md`

## Context

Resolving the peer-facts question (PDR-0020), the owner stated Lacuna's intent: *"a comprehensive
demo of the full suite as it comes online — when tabard comes online, you'll pick up identity
management as well."* Asked how that sits against the standing audience sequence (dogfood-now /
demonstrator-later, PDR-0002), the owner chose to **elevate the comprehensive demo to the primary
intent now** (a real strategy shift, knowingly recorded as such). The owner also corrected the
roster: **charter became plainweave** (requirements management), and **tabard** is a genuinely new
forthcoming member (identity management — *issuing agent names*).

## Decision

1. **Elevate: the growing comprehensive demo is the PRIMARY deliverable now**, not a future
   graduation gated on suite completion. The same artifact (`tour.md` + `matrix.md`) serves the
   federation's own developers (dogfood range) AND prospective evaluators (live demonstrator)
   continuously. Coverage grows member-by-member as the suite comes online (the PDR-0020 theme).
2. **Roster reconciliation (living artifacts only):** "charter" is **not** a separate design-only
   member — it shipped as **plainweave** (requirements management). Drop the stale "charter remains
   design-only" framing from `vision.md`/`metrics.md`/`matrix.md`/`roadmap.md`. Add **tabard** as the
   forthcoming member (identity management / agent-name issuance) on the roster + roadmap horizon.
3. **Unchanged:** the honesty discipline (G3 — absent/design-only members are labelled, never faked)
   and the consumer-boundary (anti-goal #4 — Lacuna demonstrates and reports, never fixes a member).
   Historical PDRs/PRDs (PDR-0008, PRD-0004) are **not** edited — they were true when written.

## Consequences

- `vision.md` "Who it serves" reframed: comprehensive-demo-as-primary + reconciled roster.
- `roadmap.md` Later: "Charter promotion" retired (charter→plainweave, already live); "graduate to
  demonstrator" reframed (no longer a gated far-future step — it is the continuous primary intent);
  **tabard / identity-management coverage** added as the next forthcoming pickup.
- `metrics.md` G3 + `matrix.md`: charter reconciled to plainweave; tabard noted as the design-only/
  forthcoming member the honesty discipline now points at.
- The next member-onboarding (tabard) has an explicit home: when its surface is **released**, Lacuna
  plants the identity-management lacunae + tour legs + matrix cells (PDR-0020 intake gate).

## Reversal trigger

- If serving demonstrator + dogfood from one artifact continuously degrades demonstrator credibility
  (e.g. in-flight dogfood churn makes the public-facing tour misleading), re-introduce a separation
  (a blessed demonstrator cut vs. the rolling dogfood range) — and escalate, as that is a vision move.
- If "charter→plainweave" or "tabard = identity management" proves a mis-statement, correct via a new
  PDR (never edit this one).
