# PDR-0018 — Merge the 6-member seam-integrity harness + peer-facts cells to main (PR #2)

- **Date:** 2026-06-29
- **Status:** Accepted (owner-directed in-session via `/own-product`; within the authority grant)
- **Decider:** human owner (John) directed the merge; agent:lacuna-po executed + reconciled
- **Related:** PDR-0012/0013/0014 (the harness), PDR-0015/0016/0017 (the peer-facts cells it carries),
  PDR-0009 (G1 as live census/gate), metrics.md north-star + G1, PR #2

## Context

`/own-product` RESUME found `current-state.md` materially stale: it called the harness branch
`plainweave-mcp-attach` **UNPUSHED, blocked-on-owner**. Reality (reconciled against git/gh): the
branch was pushed, renamed `release/plainweave-mcp-attach`, and was **PR #2 — OPEN and MERGEABLE
against `main`** (old PR #1 closed). Nine commits had also landed since the prior checkpoint adding
the plainweave + warpline **peer-facts cells** (PDR-0015/0016/0017). The owner's escalated
push/PR action had already been taken; the merge was the open call.

## Options

1. **Merge PR #2 to main now.** Advances the north-star baseline and makes the G1 gate live on
   `main`. Accepts the release-build environment-pinning as a documented prerequisite on `main`.
2. **Hold PR #2 open.** Baseline stays at 52; no environment-pinning commitment to `main`.
3. **Merge after sibling fixes (D1/D2).** Wait until warpline/wardline binding contracts are
   forward-ported to their `main` so a fresh-clone-from-`main` gate is green before merging.

## Call

**Option 1 — merged** (owner: "Merge to main now"). Merge commit `5107462`; release branch
deleted; merge-commit method chosen to preserve the curated PDR commit history (git history is
itself part of this specimen's demonstration). `main` baseline moved `d09da33` → `5107462`;
corpus **52 → 62 catalogued lacunae** (+6 `mcp-attach-*`, +4 peer-facts).

## Rationale

The harness was delivered, green, opus-reviewed, and the bet's whole point — make G1 a **gate** on
`main`, not a manual probe — is only realized once it is on `main`. The environment-pinning caveat
(gate green only against sibling **release** builds — D1/D2 `weft-ca12d859bb`; `tour.md` byte-locked
to PyPI plainweave 1.0.0 — PDR-0016) is a **documented prerequisite, not a defect**, and the two
plainweave peer-facts cells honestly render `[N/A]` under 1.0.0 rather than faking green (PDR-0016).
Holding (Option 2) leaves `current-state` perpetually drifting from a merged-in-practice branch;
waiting on sibling main-forward-ports (Option 3) couples Lacuna's baseline to other members' release
cadence, which the consumer boundary says Lacuna must not depend on.

## Reversal trigger

- If keeping `make verify` green on `main` ever requires **suppressing a real (uncatalogued)
  defect** — stop; that inverts the north-star (metrics.md north-star reversal trigger).
- If the **release-build environment-pinning** means no contributor can reproduce a green
  `make verify` from `main` without the exact sibling release builds *and that blocks real work*,
  revisit the pinning (e.g. capability-gate the binding-tool legs the way PDR-0016 gates the
  plainweave cells, so a `main`-built sibling renders `[N/A]` instead of redding the gate).
- If a silent member de-attach ever passes the gate green, G1's reversal trigger (PDR-0009) fires
  regardless of this merge.
