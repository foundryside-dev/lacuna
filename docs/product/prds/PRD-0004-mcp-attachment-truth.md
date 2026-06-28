# PRD-0004 — MCP attachment truth            Status: CLOSED 2026-06-25 (G1 4/4 met; reproduce-and-report moot) — superseded by the plainweave-MCP-attachment Next bet

> **STATUS UPDATE (2026-06-25, in-session live probe).** Planning probed the three
> attachment gaps directly via this attached session's `mcp__*` tools (the faithful
> G1 measurement). **All three are RESOLVED:** Loomweave MCP bound to
> `/home/john/lacuna` (423 entities, fresh index); Filigree MCP bound to lacuna
> (schema 29/29); Legis MCP present and answering (`doctor_get` responds,
> filigree-scoped to lacuna). The 0/4 baseline (06-13) is stale — member config-fixes
> since then closed the seams. **Criteria 1–2 (reproduce + report member bugs) are
> moot** (no member bugs exist); **criterion 3 (G1 outcome) is substantially met.**
> Evidence + the dissolved-premise reframe: `docs/plans/2026-06-25-mcp-attachment-truth-harness.md`.
> **Owner decision (2026-06-25): CLOSED — open plainweave as a fresh Next bet.**
> G1 confirmed 4/4 reachable MCP-first in this attached session (Wardline→Filigree,
> Loomweave→Filigree enrichment, Loomweave→Filigree issue-assoc, Legis governance) —
> outcome met. Reproduce-and-report criteria 1–2 accepted as **moot** (no member bugs
> exist). The live frontier — plainweave (6th member) MCP-absent in Lacuna (source ships
> a FastMCP server; installed `0.0.1` build is stale; not in `.mcp.json`) — is filed as a
> **new Next bet**: wire the newest member MCP-first + a 6-member attachment
> regression-harness. PDR (close PRD-0004 + record the bet), roadmap Next, G1 reading,
> and current-state rewrite are written and committed at the next `/product-checkpoint`.

Status (historical): in-planning (dispatched 2026-06-25, owner-reconfirmed after Plainweave detour)
Decision: PDR-0003   Bet (roadmap.md): Now → first dispatched workstream   Target metric (metrics.md): G1 federation seam health

## Problem

**Who:** an agent (or evaluator) working *in the staged Lacuna repo* and reaching
for the Weft federation the way the project instructions tell it to — MCP-first.
**The problem (their pain):** the federation's entire value proposition is its
cross-tool *joins*, but in a real attached session the three MCP servers do not
bind to the staged Lacuna repo. Filigree MCP points at the Weft hub instead of
the staged repo; Loomweave MCP is attached to a no-index context; Legis MCP does
not attach at all. The agent is silently pushed to CLI / raw JSON-RPC to do what
the docs promise is an MCP call. **Desired outcome:** an agent in the Lacuna repo
can exercise all four documented joins through the advertised `mcp__*` surface in
one attached session, without falling back to shell — and where it *can't* yet,
Lacuna reliably **reproduces and reports** the gap rather than papering over it.
**Why now:** the 2026-06-13 post-fix re-dogfood proved the joins *function* (the
hard seam bugs are fixed) — so attachment is now the single thing standing
between "works if you launch the process by hand" and "point the suite and watch
it work." It is the last mile of the Now bet, and it is the most visible friction
an evaluator hits on contact.

## Success metric (the signal the bet paid off)

**G1 — federation seam health** (`metrics.md`): documented cross-tool joins
reachable **MCP-first** in one attached session.
**BASELINE 0 of 4 → TARGET 4 of 4, by 2026-09-13.**

> **Lever note (consumer boundary, PDR-0002):** Lacuna does not *own* the MCP
> servers, so it cannot directly move G1 — the attachment fixes land in the
> filigree / loomweave / legis repos. Lacuna's lever is a **deterministic
> reproduction + a filed bug report** per gap; G1 is the *downstream outcome* the
> reports are meant to produce once the owning members act. Acceptance of this
> PRD is judged on the Lacuna-ownable deliverable (criteria 1–2); G1 reaching 4/4
> is the outcome confirmation, expected to lag the reports.

## Acceptance criteria (falsifiable)

1. **DELIVERABLE — reproduction fixtures.** Each of the 3 MCP-attachment gaps
   (Filigree-MCP→hub-not-staged-repo; Loomweave-MCP→no-index-context;
   Legis-MCP-absent-in-session) has a **deterministic, re-runnable reproduction
   fixture** committed in Lacuna that demonstrates the failure from a clean
   attached session, by 2026-09-13.
   *Reject branch:* any of the 3 gaps lacking a fixture that reproduces on a
   second machine/run → criterion unmet; PRD stays open.
2. **DELIVERABLE — bug reports filed.** For each of the 3 gaps, a bug report is
   filed to the **owning member** (filigree / loomweave / legis) carrying the
   reproduction steps, the expected-vs-actual attachment, and the relevant SEI /
   evidence, by 2026-09-13. Lacuna does **not** attempt the fix.
   *Reject branch:* any gap without a filed, member-routed report → criterion
   unmet, regardless of fixture quality.
3. **OUTCOME — G1.** G1 rises 0/4 → 4/4 joins reachable MCP-first in one attached
   session, measured on the `metrics.md` scoreboard by 2026-09-13.
   *Reject branch:* below 4/4 at the date → the *outcome* is unmet; open a
   follow-up PDR to re-route the still-unattached member(s). (Criteria 1–2 may
   still have passed — that is Lacuna's debt discharged; 3 is the member's.)
4. **GUARDRAIL — specimen fidelity (north star).** `make verify` stays green
   across every fixture added by this bet (no uncatalogued finding trips the
   gate; narrative in lockstep), over the same window.
   *Reject branch:* breached → bet rejected even if 1–3 pass; a reproduction
   fixture that corrupts the specimen is not acceptable.
5. **GUARDRAIL — demonstration honesty (G3).** No fixture, report, or tour leg
   presents an unattached or design-only member as live; attachment failures are
   labelled as failures.
   *Reject branch:* any member shown as live when it is not → bet rejected.

## Non-goals (this bet)

- **Fixing the MCP servers.** Out of scope by the consumer boundary — the fixes
  live in filigree / loomweave / legis. This bet reproduces and reports.
- **Port/config-truth reconciliation** (e.g. Loomweave doctor's `:35541` vs
  working `:9730`) — a *separate* Next bet; touch only where it directly blocks
  reproducing an attachment failure.
- **Scanner job semantics** and **large-repo ingest** — separate Next/Later bets.
- **New lacunae / Rust-wing depth** — separate corpus-growth bet.
- **Charter** — remains design-only; not part of the 4 documented joins.

## Constraints & guardrails

- **Consumer boundary (PDR-0002):** Lacuna may not modify the hub or any member
  repo; deliverable is fixture + report only.
- **Guardrails that must not degrade:** north-star specimen fidelity (`make
  verify` green) and G3 demonstration honesty — both encoded as criteria 4–5.
- **Honest-degrade contract:** reproductions must distinguish "member not
  attached" from "member attached but join broken" — the report's value is in
  naming *which*.
- **Secrets discipline:** reproductions must not commit `.env` / federation
  tokens; the staged-repo attachment context is reproduced via documented setup,
  not by checking in credentials.

## Open questions / assumptions

- **Assumption (bet-critical):** the three attachment failures are
  *configuration/binding* faults reproducible from the staged repo, not
  environment-specific to one machine. If a gap is non-deterministic, criterion 1
  for that gap converts to "characterise the nondeterminism" and G1's 4/4 target
  is at risk. *If wrong, the bet's outcome date slips and may need re-routing.*
- **RESOLVED — Legis bar (DECIDE 2026-06-25, within grant).** "MCP-first
  reachable" for *every* member, Legis included, means the `mcp__*` namespace
  **auto-attaches via `.mcp.json`** in a clean attached session. A documented
  one-command launch does **not** count: requiring the agent to shell out to start
  a server is itself the CLI-fallback friction this bet exists to kill ("point the
  suite and watch it work"); it matches the dogfood method's bar. *Honest-degrade
  rider:* where a member architecturally cannot auto-attach (e.g. Legis's
  launch-bound `--agent-id`), that constraint **is the finding** — the bug report
  names "auto-attach blocked by X", and confirmation with the Legis owner rides on
  the filed report (consumer boundary), not a pre-dispatch ask. *Reversal:* if the
  Legis owner establishes auto-attach is impossible by design, criterion 3's Legis
  leg converts from "Lacuna-reproducible gap" to "member-side limitation," and G1
  is re-scoped to 3 auto-attachable + 1 documented-launch.
- **RESOLVED — report routing (DECIDE 2026-06-25, within grant).** Member-routed
  bug reports (criterion 2) are filed to **the owning member's own tracker**
  (loomweave's / filigree's / legis's own Filigree instance) — that is where the
  fix is worked and therefore where "filed" is authoritatively verified, and it
  co-locates the report with the code that owns it (PDR-0002). A federation-hub
  tracker is the fallback only where a member exposes no own tracker. The
  member-routed report IDs are recorded back here as criterion 2 is discharged.
  *Caveat (cross-member emit seam is not uniformly reliable yet):* "filed" may mean
  a hand-filed issue in the member's tracker rather than an auto-emitted one — the
  verification is the issue ID, not the emit path.

## Handoff

- **Top item → `/axiom-planning`:** the reproduction-fixture harness (criterion 1)
  — a deterministic, re-runnable way to launch a clean attached session and
  capture each MCP server's attachment state. This is the executable core; plan
  it against the repo's tour/dogfood harness.
- **Solution shape → `/axiom-solution-architect`:** how the reproduction harness
  hangs off the existing `tour/` + dogfood machinery, and the report format/SEI
  evidence schema — the PRD names the constraints, not the design.
- **Sequencing / dated forecast → `/axiom-program-management`:** this PRD emits no
  delivery date; the committed bet goes there for the forecast.
- **Tracker IDs:** decision PDR-0003; success metric G1 (`metrics.md`); roadmap
  Now (`roadmap.md`). Member-routed bug-report IDs to be recorded here as
  criterion 2 is discharged.
