# Current State — Lacuna

_The resume brief: fastest path back to the running picture. Read this first._
_Last checkpoint: 2026-07-01 (`/product-checkpoint`). Bootstrapped 2026-06-13._

## The bet right now

**Comprehensive demo of the full suite, as it comes online** (PDR-0020/0021 — the PRIMARY intent),
riding above the standing **federation seam integrity** bet (the 6-member MCP-attachment harness is
merged, so **G1 is a gate on `main`**). This session delivered the **first concrete member-surface
increment** of that theme: plainweave's own-surface coverage (baseline / verification / dossier).
North star = `make verify` green with every live lacuna surfaced.

## What this checkpoint did

- **Shipped the 3 plainweave coverage cells** (`pw-baseline-drift`, `pw-verification-status`,
  `pw-requirement-dossier`) — corpus 62 → **65** — answering last checkpoint's open COVERAGE question
  (net-new, owner-directed). Subagent-driven TDD, whole-branch opus review = ready-to-merge (0
  Critical/0 Important); `make verify` green; §8.4 smoke passes vs real plainweave 1.2.0. Shipped as
  **PR #3** (owner-authorized). [PDR-0023]
- **Re-blessed the tour narrative to exercised plainweave 1.2.0** — PDR-0016's reversal trigger firing
  (the gate resolves plainweave BIN-first at 1.2.0, which runs the peer-facts subcommands): the 2
  peer-facts cells flipped `[N/A]` → `[PASS]`. Cleared two prereqs first: reinstalled
  `wardline[loomweave,rust]` (rust lacunae were dark) and absorbed the legis v1.3.0→v1.4.0 re-stamp.
  [PDR-0022]
- **Reconciled the product workspace to `main`:** fast-forwarded the unmerged `product/checkpoint-
  2026-06-29` branch (PDR-0018→0021) into local `main` (owner-directed), then checkpointed this
  session on top. `main` is now the single product-history line (PDR-0018→0023).

## In flight

- **PR #3** (`feat/plainweave-coverage-lacunae` → main): the coverage cells, opus-reviewed,
  **awaiting merge** (owner-gated). Base is `origin/main@5107462`; docs-only vs the feature — no
  conflict with the reconciled product commits.
- **Lacuna tracker:** `lacuna-2046f5ae8a` (`[release] P4` "Future") unchanged. Observation
  `lacuna-obs-c116dca009` filed (`materialize_workspace()` outside try across 3 plainweave legs).
- **Sibling refs (theirs):** loomweave `clarion-f8fc8aebca` (P3 signaling ask). Churn thread CLOSED.

## Open questions / blocked-on-owner (escalations)

- **[OWNER — push] Local `main` is ahead of `origin/main` by 4 unpushed commits** (PDR-0018→0021 from
  the reconcile + this checkpoint's PDR-0022/0023). Push is your gate — say the word. (The now-merged
  `product/checkpoint-2026-06-29` branch is redundant once main is pushed; safe to delete.)
- **[OWNER — merge] PR #3** (coverage cells) is ready-to-merge; merging to `main` is your gate.
- **[COVERAGE, residual] plainweave `preflight` surface still unplanted** — the next plainweave
  own-surface pickup under PDR-0020. (`goal`/`criterion`/`bind`/`trace`/`catalog` already exercised;
  `actor` → tabard's forthcoming domain.)
- **[TOUR SOURCE] `matrix.md`/tour roster still says "charter — design-only"** (generated; do-not-
  hand-edit). Reconcile in the tour source: charter → plainweave (live); add tabard (forthcoming). A
  manifest/code change + `make tour` regen. Still outstanding.

## Watch-items (not escalations)

- **legis re-stamp** now at **v1.4.0** (absorbed this session); re-absorb on the next legis bump.
- **wardline extras** — a `uv tool` reinstall/upgrade can drop `[rust]`/`[scanner]` (rust lacunae go
  dark); reinstall `wardline[loomweave,rust]` ([[loom-uvtool-build-staleness]]).
- **`make verify` is the LOCAL north-star** — no CI verify gate (only `deploy-site.yml`); green needs
  plainweave 1.2.0 + wardline `[loomweave,rust]` + sibling release builds for the attach gate.

## Authority grant

CONFIRMED as-is (re-confirmed 2026-06-29); next review 2026-09-25. **No vision/strategy/grant change
this session.** Big actions were owner-directed in-session (wardline reinstall, the §10 re-bless, the
main reconcile, the PR #3 push) — all within grant; the two outward-facing steps still held (push
`main`, merge PR #3).

## Where the next session starts

1. **The two owner git decisions:** push local `main` (PDR-0018→0023) and merge **PR #3**.
2. **Plant plainweave `preflight` coverage** (residual gap) + **reconcile the tour-source roster**
   (charter→plainweave, +tabard) with a `make tour` regen.
3. **Sequence the seam-integrity Next items + tabard onboarding** via `/axiom-program-management`.
