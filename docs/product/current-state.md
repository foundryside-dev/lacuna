# Current State — Lacuna

_The resume brief: fastest path back to the running picture. Read this first._
_Last checkpoint: 2026-06-28 (`/product-checkpoint`). Bootstrapped 2026-06-13._

## The bet right now

**Federation seam integrity, agent-native** (roadmap → Now). Its centerpiece — **the Phase-2
6-member MCP-attachment regression-harness — is DELIVERED + GREEN** this session (PDR-0012). The
bet's metric, G1 (seam health), is now a **gate** instead of a manual probe: `make verify`
re-asserts that all 6 federation MCP servers attach AND store-bind to the staged repo on every run,
so a silent de-attach (the 2026-06-26 loomweave incident) trips the gate by name. The Now theme
continues with the remaining items (port/config oracle, scanner job semantics, rust-wing depth) +
the deferred Phase-5 join census.

## What happened this session (the short version)

Reviewed the harness plan through **3 Workflow review rounds** (round-1 fixes → round-2 regression
remediation → round-3 test-pins) to execution-ready. Resolved **R1** by having warpline + wardline
ship **server-side store-read binding tools** (PDR-0013), confirmed live. Then **BUILT the harness**
via subagent-driven-development (Tasks 0–6, 16 commits on `plainweave-mcp-attach`): the Phase-0 spike
**strengthened the 4 path-members to path-AND-store binding** (PDR-0014 — a real gap the spike caught
in a thrice-reviewed plan). Every code task was per-reviewed + approved; an opus whole-branch review
returned Fix-then-merge → all fixed. **`make verify` exits 0 end-to-end, all 6 live-bound.**
[PDR-0012, PDR-0013, PDR-0014]

## In flight

- **Branch `plainweave-mcp-attach`** — the harness: 16 commits (`a490b08..HEAD`), authored
  tachyon-beep, **UNPUSHED** (push/PR owner-gated, below).
- **Filigree tracker:** `lacuna-2046f5ae8a` (`[release] P4` "Future") unchanged; the self-tracker
  has the known [[filigree-self-tracker-schema-lag]] (returned nothing this session — reconciled in
  the workspace, not the tracker).

## Metric readings (2026-06-28)

- **North star (`make verify`): GREEN end-to-end with the harness on the (unpushed) branch; corpus
  52 → 58 there.** The main-commit baseline (445c270, 52 lacunae) is unchanged until merge. The gate
  is bidirectional — proven to trip + name the member on a de-attach.
- **G1: the live census is now a GATE** (PDR-0012) — all 6 attach+store-bind verified every run;
  PDR-0009's reversal trigger structurally addressed. Binding is store-read for all 6 (PDR-0013/0014).
- **G2:** warpline/wardline binding-tool gap RESOLVED; NEW friction — legis re-stamps
  `AGENTS.md`/`CLAUDE.md` on spawn (absorbed v1.3.0; re-absorb on a future legis upgrade).
- **G3:** maintained — the 6 `mcp-attach` lacunae honestly "NOT A FLAW"; the leg honest-degrades.

## Open questions / blocked-on-owner (escalations)

- **[OWNER ACTION] Push / open a PR for `plainweave-mcp-attach`** — the harness is merge-ready
  (16 commits, opus-reviewed, `make verify` green) but **UNPUSHED**, per your git sensitivity. Say
  the word and I push / open the PR. (Supersedes the prior 3-commit push item — those commits are
  now part of this branch.)
- **[ESCALATION, carried] Consumer-boundary report to loomweave** — v11 silently renamed the
  `LMWV-DUPLICATE-LOCATOR` evidence contract (PDR-0011); filing to loomweave's tracker gates to you.
  **Still awaiting your go** (not addressed this session).
- **[MAINTENANCE] legis instruction-block re-stamp** — the harness leg spawns legis on every
  `make verify`; a future legis version upgrade will re-stamp `AGENTS.md`/`CLAUDE.md` → dirty tree →
  trip the clean-tree gate. Absorbed v1.3.0 (durable now); re-absorb on the next legis upgrade, or
  have the leg guard those files (a Phase-5-era hardening).
- **loomweave reinstall durability** (carried, now broader): a `uv tool upgrade` can revert a
  `cp`-over-uv-path install; the same now applies to the new `warpline-mcp`/`wardline` binding tools
  — re-sync from source if a stale reinstall reverts them ([[loom-uvtool-build-staleness]]).

## Authority grant

CONFIRMED as-is (2026-06-26); next review 2026-09-25 (quarterly). No grant change. This session's
big actions were explicitly owner-directed in-session: the harness build/execution (Lacuna's own
repo) and the warpline + wardline binding-tool builds (the owner's own Loom-portfolio members) —
both within grant. Nothing pushed/released; the one outward-facing step (push/PR) is correctly held.

## Where the next session starts

1. **The push/PR decision** on `plainweave-mcp-attach` (owner go/no-go), and the loomweave
   consumer-boundary report.
2. **Sequence the remaining seam-integrity Next items** with `/axiom-program-management`: the
   deferred **Phase-5 join census** (the next harness increment — per-join liveness classes), the
   port/config oracle, scanner job semantics, rust-wing depth.
3. **Watch the legis re-stamp** on any legis upgrade before trusting a green `make verify`.
