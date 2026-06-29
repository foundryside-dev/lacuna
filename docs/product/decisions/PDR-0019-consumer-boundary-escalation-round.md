# PDR-0019 — Consumer-boundary escalation round: merge-gate dogfood findings filed + reconciled (+ verify-before-file discipline)

- **Date:** 2026-06-29
- **Status:** Accepted (owner-authorized in-session via `/own-product`; consumer-boundary discipline per vision anti-goal #4)
- **Decider:** human owner (John) authorized filing; agent:lacuna-po filed, verified, and corrected
- **Related:** vision.md (consumer-boundary anti-goal), PDR-0011 (the carried duplicate-locator
  report), `docs/dogfood/2026-06-28-merge-gate-live-dogfood-report.md`, [[loom-uvtool-build-staleness]]

## Context

The 2026-06-28 merge-gate live dogfood (committed in the repo) surfaced cross-member findings that,
per the vision, Lacuna owes as **bug reports** to the owning members (Lacuna never reaches across to
fix). Filing into sibling/hub trackers is owner-gated; the owner authorized the full set via
`/own-product` AskUserQuestion: the merge-gate sibling reports, the legis GO live-capture, and the
carried loomweave duplicate-locator report (PDR-0011).

## Options

1. File the full authorized set into the relevant sibling/hub trackers, **dedup against existing
   items and verify each claim against ground truth first**.
2. File everything straight from the dogfood report / PDR-0011 text without re-verification.
3. Hold — write report artifacts in Lacuna only, hand off later.

## Call

**Option 1.** Outcome after dedup + verification:

- **Already filed (no duplicate created):** loomweave churn deadlock = hub `weft-e585382ff3`;
  member-main-behind (D1/D2) = `weft-ca12d859bb`; legis←plainweave GO = `weft-a0d04046f5` (CLOSED
  with GO). The dedup discipline avoided 3+ duplicate issues.
- **Filed new:** the loomweave duplicate-locator report → loomweave **`clarion-f8fc8aebca`**.
- **Recorded then resolved:** the churn join — commented NO-GO then **CORRECTED** to GO on the hub
  (gate `weft-6fc4a166dc` comments 377/378, bug `weft-e585382ff3` comment 379). Resolved end-to-end
  when loomweave **PR #77** (`30549a3`) **merged 2026-06-29** (`1d2b4fa`); all three hub items
  (`weft-6fc4a166dc`, `weft-e585382ff3`, parent `weft-670ec2fe90`) are now CLOSED with merge-tied
  reasons. Churn join is **live-GO on `main`**.

## Rationale

Two findings I initially treated as current were stale (the SessionStart memory digest was
truncated): the churn NO-GO had already been **fixed** (PR #77), and the duplicate-locator report
was filed present-tense as a "blind bug" when loomweave is **actively working that thread** (PR #74
disclosure, rc7 `anchor_file_path`). Verifying against ground truth before/after filing caught both:
the churn comment was corrected on the record, and `clarion-f8fc8aebca` was reframed (retitled, P2→
**P3**, comment 408) into an accurate change-signaling-discipline ask. This is the load-bearing
lesson of the round.

## Reversal trigger

- **Process trigger:** if a future consumer-boundary escalation is filed from an N-day-old
  PDR/dogfood **without** a ground-truth re-verification step and proves stale on contact (as both
  did here before correction), that is the signal the verify-before-file step was skipped —
  reinstate it as a hard precondition.
- If a sibling disputes a report's accuracy, re-verify against their live source before defending it
  (the file/contract may have moved — memories and PDRs reflect what was true when written).
