# Current State — Lacuna

_The resume brief: fastest path back to the running picture. Read this first._
_Last checkpoint: 2026-06-26 (`/product-checkpoint`). Bootstrapped 2026-06-13._

## The bet right now

**Federation seam integrity, agent-native** (roadmap → Now). Two workstreams of the bet
are now settled: MCP-attachment-truth for the original 5 (PRD-0004, closed) and **plainweave
Phase 1 — reachable MCP-first — ACCEPTED** this session (PDR-0010). The live bet is now
**Phase 2: the 6-member attachment regression-harness** (PDR-0007 Phase 2, scope upgraded to a
join census, PDR-0009). Its necessity was proven hard this session — see below.

## What happened this session (the short version)

ORIENT found the workspace's recorded state was false on its headline numbers. Root cause:
**loomweave's installed binary was a stale same-version build** (`1.3.1`/schema v10) against a
**v11 DB**. That silently de-attached loomweave's MCP server (G1 regressed ~2/4, reversal
trigger tripped) and red-lit `make verify` (5 lacunae dark) — masquerading as a benign
dirty-tree RED. Fixed: reinstalled loomweave v11 from source + reconciled the tour's
duplicate-locator matcher to v11's renamed evidence contract. **`make verify` is GREEN at
`445c270`; loomweave MCP reattached; G1 restored.** [PDR-0011]

## In flight (tracker — Filigree)

- **`lacuna-2046f5ae8a`** — `[release] P4` "Future". Placeholder bucket, not active work.
- _(`lacuna-5d0e4ba6d7`, the loomweave duplicate-locator P1, is CLOSED — the loomweave-side fix
  lives in its own tracker as `clarion-48af930f2a`; consumer boundary.)_

## Metric readings (2026-06-26)

- **North star (`make verify`): GREEN, exit 0 at `445c270`** (clean tree; all 52 lacunae
  surface). Corrects the 06-25 "RED = dirty-tree only" reading — it was a *real* loomweave-
  staleness fidelity failure, root-caused and fixed, not suppressed.
- **G1: regressed (~2/4, reversal trigger tripped) then RESTORED** (5/5 enumerated joins; now a
  live census, PDR-0009). New live joins + honest gated states catalogued.
- **G2:** plainweave-attachment friction resolved; loomweave build-staleness friction resolved;
  loomweave duplicate-locator evidence-rename logged (consumer-boundary, report pending owner).
- **G3:** maintained — census classified every join honestly; no member faked.

## Open questions / blocked-on-owner (escalations)

- **[ESCALATION] Consumer-boundary report to loomweave** — v11 silently renamed the
  `LMWV-DUPLICATE-LOCATOR` evidence contract (anchor `core:project:*`→`python:class:…`; planted
  path `first_source_file_path`→`colliding_source_file_path`), breaking a downstream reader with
  no signal. Filing to loomweave's tracker gates to the owner (mirrors PDR-0006's routing).
  **Awaiting your go.**
- **[OWNER ACTION] Push `plainweave-mcp-attach`** — 3 commits (`c2f4b5a`, `4734a4e`, `445c270`)
  are committed (authored tachyon-beep) but **not pushed**, per your git sensitivity. Say the
  word and I push.
- **loomweave reinstall durability:** v11 was installed by copying `target/release` over the uv
  path (old v10 at `…/loomweave/bin/loomweave.v10-stale.bak`); uv's receipt still reads `1.3.1`,
  so a `uv tool upgrade loomweave` could revert it. Re-sync from source if so.

## Authority grant

CONFIRMED as-is by the owner this session (2026-06-26); next review 2026-09-25 (quarterly).
No grant change. The loomweave reinstall + the 3 commits were explicitly owner-authorized
in-session; both within grant (Lacuna's own env; loomweave source untouched).

## Where the next session starts

1. **Resolve the loomweave consumer-boundary report** (owner go/no-go) and **push** if wanted.
2. **Hand Phase 2 (6-member attachment regression-harness, census scope) to
   `/axiom-program-management`** to sequence against the other Next items (port/config oracle,
   scanner job semantics, rust-wing depth). This harness is now the top seam-integrity bet — it
   would have caught this session's silent loomweave de-attach automatically.
3. **Re-probe the full G1 census** at next ORIENT (the original 4 joins weren't each
   individually re-verified MCP-first post-restart; loomweave MCP attach + plainweave→loomweave
   were confirmed).
