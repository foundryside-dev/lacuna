# PDR-0013 — R1: warpline + wardline seam-binding verified via NEW server-side store-read tools (not attach-only)

- **Date:** 2026-06-28
- **Status:** Accepted (owner-directed; the sibling-member tool builds were explicitly authorized in-session).
- **Decider:** human owner (John) chose to build the server-side tools ("we'll do those mcp servers today") and ran the warpline/wardline implementations; agent:claude-product-owner specified the binding contract + ground-truthed it live.
- **Related:** [[PDR-0012]], PDR-0009, [[loom-portfolio]], [[mcp-attachment-harness-state]] + [[loom-uvtool-build-staleness]] memories.

## Context

The harness verifies each member is not merely *attached* but *store-bound* to the staged repo (so a stale-but-running binary that can't read its store is caught). Four members self-report a binding fact via an existing MCP tool. But warpline + wardline had **no** root/store-reporting tool, so the plan inferred binding from a `.mcp.json` + spawn-cwd static lint — `cwd == ROOT`, which is **tautological** (the probe spawns with `cwd=ROOT`, so it is always true): the gate was BLIND to a stale-but-running de-attach for those 2 members (a round-2 review finding, R1).

## Options

- (a) Settle for **attach-only** verification of warpline/wardline (catches a crash, not the stale-but-running incident) and label the limitation honestly.
- (b) **Add real server-side store-read binding tools** to the warpline + wardline MCP servers (sibling Loom-portfolio members the owner controls), making them self-report like the other 4.

## Decision

Chose **(b)** — the owner directed building the tools that day. Specified a binding contract (a read-only health tool returning a **store-read fact** — `binding_ok` + a `schema_version` read from *inside* the member's repo-scoped store, NOT directory existence or a path echo), wrote the two implementation prompts, and the owner shipped them: warpline `warpline_project_status_get`; wardline an extended `doctor` `repo_binding` block. Ground-truthed LIVE by spawning the fresh reinstalled binaries (warpline `binding_ok=true`/`schema=4`; wardline `binding_ok=true`/`schema=1`). The tautological static-lint is removed.

## Consequences

- All 6 members now verify seam-binding via a store-read fact — the gate catches the loomweave-class stale-binary incident for warpline/wardline too, not just process-start.
- A cross-member coordination pattern: Lacuna (the consumer) specifies a binding contract; sibling members ship the tool. The contract (exact field paths) is recorded in `docs/plans/phase0-findings.md` + the [[mcp-attachment-harness-state]] memory.
- Caveat (current-state): a future stale reinstall of `warpline-mcp`/`wardline` reverts the tool (the [[loom-uvtool-build-staleness]] pattern); re-sync from source.

## Reversal trigger

If a member's store-read tool proves unreliable or its contract drifts (the field the harness reads moves) such that the gate false-reds a healthy member, treat it as a consumer-boundary finding to *that member*, not a Lacuna gate relaxation. If a future member genuinely cannot expose a store-read tool, fall back to attach-only with the limitation labelled in `note` (per the plan's Phase-0 Step 5) — never back to the tautology.
