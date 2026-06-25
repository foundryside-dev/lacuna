# Current State — Lacuna

_The resume brief: fastest path back to the running picture. Read this first._
_Last checkpoint: 2026-06-25 (`/product-checkpoint`). Bootstrapped 2026-06-13._

## The bet right now

**Federation seam integrity, agent-native** (roadmap → Now). The first workstream —
**MCP attachment truth (PRD-0004)** — is **DONE**: probed in-session 2026-06-25, **G1 = 4/4
documented joins reachable MCP-first** in one attached session (the three 06-13 attachment
gaps were resolved by member config-fixes, not by Lacuna). The bet's *successor* workstream is
**plainweave MCP attachment** (PDR-0007): the 6th and newest member is **MCP-absent in Lacuna**
— its source ships a FastMCP server, but the installed `0.0.1` build is stale and it is not in
`.mcp.json`. The Now theme holds; the frontier moved one member forward.

## In flight (tracker — Filigree)

- **`lacuna-5d0e4ba6d7`** — `[bug] P1, triage`. loomweave duplicate-locator / last-write-wins
  shadowing of `specimen.colliding.ShelfMark` (the planted `colliding.py` lacuna). **Routed as a
  loomweave bug report** (PDR-0006, owner-approved; comment recorded on the issue). **FILED 2026-06-25** as `clarion-48af930f2a` in loomweave's own tracker; loomweave owns the fix.
  Lacuna keeps the consumer-side record (consumer boundary — Lacuna reports,
  loomweave fixes; Lacuna must NOT "fix" the planted lacuna).
- **`lacuna-2046f5ae8a`** — `[release] P4` "Future". Placeholder bucket, not active work.

## Metric readings (2026-06-25)

- **G1 federation seam health: 4/4 — TARGET MET** (ahead of 2026-09-13). No reversal trigger tripped.
- **North star (`make verify`): RED, but NOT a regression** — caused solely by uncommitted *tooling*
  churn (SKILL.md / AGENTS.md / CLAUDE.md install blocks) → dirty tree → legis won't sign → `tour.md`
  stale. Green on a clean tree at `d09da33`. (See [[lacuna-green-tour-constraints]] memory.)
- **Corpus: 52 catalogued lacunae** (reconciled from the stale "44" across vision/roadmap/metrics).

## Open questions / blocked-on-owner

- **Plainweave bet (PDR-0007) is not yet sequenced** → hand to `/axiom-program-management` for
  Now/Next sequencing + dated forecast (roadmap is intent-only).
- **Env mutation deferred:** reconciling plainweave's MCP needs a reinstall-from-source + `.mcp.json`
  wiring (within grant; PDR-0005 precedent) — but reinstalling the build that ARMS `make verify`'s
  `pw-*` gate risks the north-star (verify-after), and MCP-first verification only completes in a
  session that *re-attaches* after the config change. Owner chose "no env mutation this session."
- **Tree hygiene (owner):** non-product tooling churn (install-block edits) sits uncommitted and
  keeps `make verify` red until committed or stashed — not part of the product workspace; flag for owner.

## Authority grant

CONFIRMED as-is by the owner this session (2026-06-25); next review 2026-09-25 (quarterly).
No grant change. Plainweave was **ratified into `vision.md`** per explicit owner approval (PDR-0008).

## What this checkpoint did

- **PDR-0006:** accepted PRD-0004 outcome (G1 4/4), **closed it**; resolved its two open questions
  (now moot); routed the P1 to loomweave.
- **PDR-0007:** opened the plainweave-MCP-attachment + 6-member regression-harness as a Next bet.
- **PDR-0008:** ratified Plainweave into `vision.md` (owner-approved); refreshed the grant review date.
- Reconciled corpus 44→52; recorded the 2026-06-25 metric readings.

## Where the next session starts

1. **Hand PDR-0007 (plainweave MCP attachment) to `/axiom-program-management`** to sequence against
   the other open Next items (port/config truth, scanner job semantics, rust-wing depth).
2. **When dispatched:** reinstall plainweave from source → wire `.mcp.json` → re-verify the tour
   (guard the north-star) → verify plainweave attaches MCP-first in a fresh session → build the
   6-member attachment regression-harness.
3. **(Done 2026-06-25)** P1 loomweave report filed as `clarion-48af930f2a`; follow loomweave's triage if it stalls.
