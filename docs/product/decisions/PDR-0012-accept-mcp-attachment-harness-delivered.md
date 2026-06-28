# PDR-0012 — Phase-2 MCP-attachment regression-harness DELIVERED + accepted (the top seam-integrity bet)

- **Date:** 2026-06-28
- **Status:** Accepted (built within grant; owner-directed execution in-session). Push/PR is owner-gated — see current-state.
- **Decider:** human owner (John) directed the build + execution; agent:claude-product-owner ran the subagent-driven build + the acceptance.
- **Related:** PDR-0007 (Phase-2 bet), PDR-0009 (G1 live join census), [[PDR-0013]] (R1 sibling tools), [[PDR-0014]] (path-AND-store strengthening), metrics.md north-star + G1, [[mcp-attachment-harness-state]] memory.

## Context

The roadmap's committed top bet — the 6-member MCP-attachment regression-harness (PDR-0007 Phase 2, scope-upgraded to a join census, PDR-0009) — was "Next, hand to `/axiom-program-management`" at the last checkpoint. Its necessity was proven hard by the 2026-06-26 loomweave incident: a stale binary started clean but could not serve its binding, silently de-attached, and `make verify` did **not** catch it (only manual probing did). This session the owner directed building it directly after the plan passed 3 Workflow review rounds (execution-ready).

## Decision

Built the harness via subagent-driven-development (Tasks 0–6: feasibility spike → `ServerSpec` parser+redaction → `probe`/`classify`/wire-transports/per-member interpreters → 6 `mcp-attach-*` lacunae → the `steps.mcp_attachment()` leg → live regen+verify → negative tests). 16 commits on `plainweave-mcp-attach` (`a490b08..HEAD`), authored tachyon-beep. Every code task implemented → per-reviewed → approved; a final opus whole-branch review returned **Fix-then-merge (no Critical)** → all findings fixed.

**Accepted against the bet's success criteria:**
- `make verify` exits 0 end-to-end: all 6 federation MCP servers (filigree, legis, loomweave, plainweave, wardline, warpline) attach **AND store-bind** to the staged repo, LIVE; the 6 `mcp-attach-*` lacunae surface; narrative in lockstep; tree clean.
- A silent de-attach now **trips `make verify` by name**, with the cause (D17), distinguishing a de-attach from a not-installed binary (D18) — proven by two negative tests at the real `run_verify()` altitude. This is the exact failure the gate exists to catch.

## Consequences

- **G1 (federation seam health) is now a GATE, not a manual probe** — `make verify` re-asserts the 6-member attach+bind census on every run. PDR-0009's reversal trigger ("a silent member de-attach the gate does NOT catch is a G1 failure even if a later manual probe passes") is structurally addressed.
- **North-star corpus grew 52 → 58** (the 6 seam-integrity `mcp-attach-*` lacunae).
- **UNPUSHED** — the branch is merge-ready but not pushed; push/PR gates to the owner (git sensitivity).
- Discovered + mitigated: spawning the legis MCP server re-stamps its `AGENTS.md`/`CLAUDE.md` instruction-block on a version bump (absorbed v1.3.0; re-absorb on a future legis upgrade — current-state open item).
- Task 7 (Phase 5 join census) DEFERRED to its own future PR (the plan ships the gate first).

## Reversal trigger

If holding `make verify` green ever requires suppressing a real (uncatalogued) defect — stop (north-star reversal). If the harness proves flaky in practice (a transient probe failure red-lights verify with no real de-attach), reopen the determinism/timeout design rather than relax the gate. If a member's MCP attach contract changes such that the gate goes dark on a real de-attach without tripping, that is a G1 failure to fix, not absorb.
