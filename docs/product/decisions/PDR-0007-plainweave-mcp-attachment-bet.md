# PDR-0007 — Open plainweave MCP attachment + 6-member regression-harness as a Next bet

- **Date:** 2026-06-25
- **Status:** Accepted (intent; not yet sequenced — hands to `/axiom-program-management`)
- **Decider:** agent:claude-product-owner, executing under the human owner's explicit disposition this session ("open as a fresh Next bet")
- **Related:** [[PDR-0006-close-prd0004-g1-met]] (predecessor workstream, closed met), PDR-0005 (Plainweave tour member), PDR-0002 (consumer boundary), metrics.md G1

## Context

Closing PRD-0004 established G1 = 4/4 for the **five** servers wired in `.mcp.json`
(loomweave, filigree, wardline, legis, warpline). But the federation grew since G1 was
defined (06-13): **plainweave is the 6th and newest member**, and it is **MCP-absent in
Lacuna** —
- plainweave *source* (`/home/john/plainweave/src/plainweave/mcp_server.py` + `mcp_surface.py`)
  ships a `FastMCP` server;
- the *installed* uv-tool build (`plainweave 0.0.1`) is **stale** — exposes no `mcp` command
  (the known [[loom-uvtool-build-staleness]] pattern);
- `.mcp.json` has **no plainweave entry**.

So plainweave is CLI-only in Lacuna's attached session — the same shape as the old Legis gap,
now for member #6. This is the live continuation of the Now theme (federation seam integrity,
agent-native, MCP-first), not a fresh direction.

## Decision

**Open a new Next bet: "Wire the newest member (plainweave) MCP-first + a 6-member attachment
regression-harness."** Scope (intent, to be shaped/sequenced downstream):
1. Reconcile plainweave's MCP surface in Lacuna — reinstall from source to get the
   MCP-server-bearing build, wire it into `.mcp.json`, verify it attaches and binds to the
   staged repo (MCP-first, in a fresh session — a `.mcp.json` change only attaches on the
   *next* session). All within grant (Lacuna's own env + config; PDR-0005 precedent).
2. Build a durable, regenerable **attachment regression-harness** asserting all 6 members
   stay reachable MCP-first — the Plainweave-style "durable proof over one-shot read" value,
   so a silent de-attachment trips `make verify` rather than going unnoticed.

The "MCP-first = auto-attach via `.mcp.json`" bar and "report to the owning member's own
tracker" routing (resolved in PRD-0004 / PDR-0006) carry forward to this bet.

## Consequences

- roadmap.md Next: plainweave MCP attachment + regression-harness added as the top Next item;
  the completed MCP-attachment-truth workstream drops out of Next.
- Handed to `/axiom-program-management` for sequencing + dated forecast (no date here).
- Two known constraints recorded for the planner: reinstalling the build that ARMS
  `make verify`'s `pw-*` coverage gate risks the north-star guardrail (verify-after); and
  MCP-first verification can only complete in a session that re-attaches after the config change.
- No action taken this session (owner chose "open as a Next bet", no environment mutation).

## Reversal trigger

Drop/demote this bet if **plainweave is not adopted as a rostered Weft member**, or if its
source MCP server is withdrawn (mirrors PDR-0005's trigger) — in which case keep plainweave a
CLI-only tour member and close this bet. Do **not** pull it into Now until `/axiom-program-management`
sequences it against the other open Next items (port/config truth, scanner job semantics, rust-wing depth).
