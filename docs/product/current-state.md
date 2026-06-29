# Current State — Lacuna

_The resume brief: fastest path back to the running picture. Read this first._
_Last checkpoint: 2026-06-29 (`/product-checkpoint`). Bootstrapped 2026-06-13._

## The bet right now

**Federation seam integrity, agent-native** (roadmap → Now) — the 6-member MCP-attachment harness is
**merged to `main`**, so **G1 (seam health) is a gate on `main`**. Sitting above it now is the
**comprehensive-coverage intent** (PDR-0020/0021): Lacuna is a **comprehensive, growing demo of the
full suite as each member comes online**, and that demo is now the **primary deliverable** (not a
future graduation) — serving dogfood AND demonstrator continuously.

## What this checkpoint did

- **Merged PR #2** to `main` (owner-directed): harness + peer-facts cells. Corpus 52 → **62**
  lacunae. [PDR-0018]
- **Filed + reconciled the merge-gate consumer-boundary escalations**, with dedup + ground-truth
  verification that caught/corrected two stale-info errors; churn join resolved (loomweave PR #77
  merged → **live-GO**). [PDR-0019]
- **Resolved the peer-facts question → a standing comprehensive-coverage theme** (owner-stated
  intent). [PDR-0020]
- **Vision change (owner-directed): elevated the comprehensive demo to primary intent** (supersedes
  PDR-0002's dogfood-now/demonstrator-later sequencing) and **reconciled the roster**: charter →
  shipped as **plainweave** (requirements management); **tabard** is new/forthcoming (identity
  management — issuing agent names). Edited `vision.md`, `roadmap.md`, `metrics.md`. [PDR-0021]

## In flight

- **Lacuna tracker:** `lacuna-2046f5ae8a` (`[release] P4` "Future") unchanged.
- **Sibling/hub refs (theirs to action):** loomweave `clarion-f8fc8aebca` (P3, signaling ask). The
  churn thread `weft-6fc4a166dc`/`weft-e585382ff3`/`weft-670ec2fe90` is CLOSED.

## Open questions / next work

- **[COVERAGE] plainweave surface beyond intent-coverage is unplanted.** The 6 `pw-*` lacunae cover
  intent (coverage/liveness/orphan/scoping) + 2 peer-facts; plainweave's **baselines, requirement
  dossiers, verification-status, preflight** surfaces have no planted lacuna yet. Under the
  comprehensive-coverage theme (PDR-0020) that is the gap to assess/fill. **Confirm with owner**
  whether there is a specific intended plainweave lacunae set to reconcile against, or whether this
  is net-new coverage to plant.
- **[TOUR SOURCE] `matrix.md`/tour roster still says "charter — design-only"** (generated; do-not-
  hand-edit). Reconcile in the tour source/manifest: charter → plainweave (live); add tabard
  (forthcoming). A code/manifest change + `make tour` regen, not a doc edit.
- **[SEQUENCING] Hand the remaining seam-integrity Next items to `/axiom-program-management`:**
  Phase-5 join census, port/config oracle, scanner job semantics, rust-wing depth — now alongside the
  standing comprehensive-coverage theme (next pickup: **tabard / identity management** when released).

## Watch-items (not escalations)

- **legis instruction-block re-stamp** on a legis version upgrade → dirty tree → trips clean-tree
  gate. Absorbed v1.3.0; re-absorb on next upgrade.
- **uv-tool build staleness** — `uv tool upgrade` can revert a `cp`-over-uv-path install
  ([[loom-uvtool-build-staleness]]).

## Authority grant

CONFIRMED as-is (re-confirmed 2026-06-29); next review 2026-09-25. **One owner-directed VISION
CHANGE this session** (PDR-0021 — elevate demo to primary + roster reconcile); recorded explicitly,
not silently. The grant's *scope* is unchanged. Nothing else escalated — all prior open escalations
were resolved.

## Where the next session starts

1. **Assess the plainweave-coverage gap** (above) and decide net-new lacunae vs. a reconcile.
2. **Reconcile the tour-source roster** (charter→plainweave, +tabard) and regen `matrix.md`/`tour.md`.
3. **Sequence the seam-integrity Next items + tabard onboarding** via `/axiom-program-management`.
