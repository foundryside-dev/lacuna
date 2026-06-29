# Current State — Lacuna

_The resume brief: fastest path back to the running picture. Read this first._
_Last checkpoint: 2026-06-29 (`/product-checkpoint`). Bootstrapped 2026-06-13._

## The bet right now

**Federation seam integrity, agent-native** (roadmap → Now). Its centerpiece — the 6-member
MCP-attachment regression-harness — is **DELIVERED + MERGED TO `main`** (PR #2, merge `5107462`).
**G1 (federation seam health) is now a GATE on `main`**, not a branch or a manual probe: `make
verify` re-asserts all 6 federation MCP servers attach AND store-bind on every run, so a silent
de-attach trips the gate by name. North-star + G1 are the metrics it moves.

## What this checkpoint did

- **Merged PR #2** to `main` (owner-directed): the harness + plainweave/warpline peer-facts cells.
  Corpus 52 → **62** catalogued lacunae; release branch deleted. [PDR-0018]
- **Filed + reconciled the merge-gate consumer-boundary escalations** (owner-authorized), with
  dedup (3+ duplicates avoided) and ground-truth verification that **caught and corrected two
  stale-info errors** (a churn verdict that was already fixed; a duplicate-locator report mis-framed
  as a live bug). Filed loomweave `clarion-f8fc8aebca` (P3); corrected the churn record on the hub.
  [PDR-0019]
- **Recorded readings** (corpus 62; G1 gate live on `main`; churn join NO-GO → **live-GO** after
  loomweave PR #77 merged) — **no PDR reversal trigger tripped.**
- **Authority grant** re-confirmed as-is.

## In flight

- **Lacuna tracker:** `lacuna-2046f5ae8a` (`[release] P4` "Future") unchanged; self-tracker quiet
  ([[filigree-self-tracker-schema-lag]]).
- **Sibling/hub refs (owned by them, not Lacuna — informational):** loomweave `clarion-f8fc8aebca`
  (P3, signaling-discipline ask, open); hub `weft-ca12d859bb` (D1/D2 member-main-behind, open). The
  churn thread (`weft-6fc4a166dc`/`weft-e585382ff3`/`weft-670ec2fe90`) is **CLOSED**.

## Open questions / next decisions (for the next DECIDE)

- **[PRODUCT QUESTION] Peer-facts cells — explicit Next theme or completed one-off?** The four
  peer-facts cells (PDR-0015/0016/0017) shipped via sibling-driven tasking, off the planned roadmap.
  Decide whether to recognize "members consuming siblings' facts" as an explicit Next theme or close
  it as done. Not yet decided.
- **[SEQUENCING] Hand the remaining Now/Next seam items to `/axiom-program-management`:** the
  deferred **Phase-5 join census** (per-join liveness classes), the port/config oracle, scanner job
  semantics, rust-wing depth.

## Watch-items (not escalations)

- **legis instruction-block re-stamp** — legis spawns on every `make verify`; a future legis
  version upgrade re-stamps `AGENTS.md`/`CLAUDE.md` → dirty tree → trips the clean-tree gate.
  Absorbed v1.3.0 (durable now); re-absorb on the next legis upgrade.
- **uv-tool build staleness** — a `uv tool upgrade` can revert a `cp`-over-uv-path install for
  loomweave / warpline-mcp / wardline; re-sync from source if a stale reinstall reverts them
  ([[loom-uvtool-build-staleness]]).

## Authority grant

CONFIRMED as-is (re-confirmed 2026-06-29); next review 2026-09-25 (quarterly). No grant change.
**Nothing escalated this checkpoint** — all prior open escalations (push/PR; the carried loomweave
duplicate-locator report) were RESOLVED this session. The push/PR/merge and the sibling-tracker
filings were all owner-directed or owner-authorized in-session; the hub closed its own #77 issues.

## Where the next session starts

1. **Decide the peer-facts-cells question** (explicit Next theme vs. one-off).
2. **Sequence the remaining seam-integrity Next items** with `/axiom-program-management`.
3. **Watch the legis re-stamp** on any legis upgrade before trusting a green `make verify`.
