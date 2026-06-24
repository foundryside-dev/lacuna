# Current State — Lacuna

_The resume brief: fastest path back to the running picture. Read this first._
_Bootstrapped 2026-06-13 via `/own-product` (BOOTSTRAP branch — workspace was absent)._

## The bet right now

**Federation seam integrity, agent-native** (see `roadmap.md` → Now). Make the
cross-tool joins work MCP-first, not just via raw shell. The Wave-3 Rust wing has
landed (corpus now **44 catalogued lacunae**) and the 2026-06-13 post-fix
re-dogfood confirmed the major seams function — the live edge of work is closing
the *MCP-attachment* and *config-truth* gaps that still push agents to CLI.

## Added 2026-06-24 — Plainweave tour member (PDR-0005)

Plainweave is now the 6th live tour member (intent-coverage capability demos:
`pw-intent-justified` / `-liveness` / `-orphan`, `pw-surface-scoping`). The corpus is
now **52 catalogued lacunae** (the "44" referenced elsewhere in this brief is stale).
Banked as a demonstrator + deterministic regression-harness, not north-star movement.
**Two owner escalations** are recorded in PDR-0005: (1) `vision.md`'s tool enumeration
omits Plainweave (demonstrated, deliberately not rostered — owner to ratify or keep as-is);
(2) reconcile the stale corpus count in this brief. No specimen source or sibling-member
repo was modified (consumer boundary, PDR-0002).

## In flight (tracker — Filigree)

- **`lacuna-2046f5ae8a`** — `[release]` "Future", P4. The only open tracker item;
  a placeholder release bucket, not active work. (Was used transiently in the
  06-13 dogfood as an SEI-association target; association cleaned up.)
- **`lacuna-obs-8aa96160f2`** — DISMISSED 2026-06-13. Was the legis
  `policy-boundary-check` RecursionError on `nesting_bomb.py`; verified resolved
  upstream live (returns typed `POLICY_BOUNDARY_FILE_TOO_COMPLEX`, continues).
  Exemplar of the consumer boundary: Lacuna reported, legis fixed.
- **Analyzer findings:** 155 unbridged (111 actionable telemetry/info, 0
  defect-signal; 44 baselined/suppressed). This is *expected* — they are largely
  the planted lacunae. Not a backlog. See `[[metrics.md]]` G-note.

## Latest signal — 2026-06-13 post-fix re-dogfood

What is now working (was broken on 06-12):
- Wardline → Filigree work joins (given the Loomweave URL + Filigree base URL)
- Loomweave → Filigree Wardline-finding enrichment (with `FILIGREE_API_TOKEN`)
- Loomweave → Filigree issue association round-trip (hydrates title/status/priority)
- Legis `policy-boundary-check` no longer `RecursionError`s on `nesting_bomb.py`

Remaining friction (→ feeds Next bets):
1. **MCP attachment mismatch** — Filigree MCP points at Weft; Loomweave MCP on a
   no-index context; Legis MCP absent in-session. Direct launches work; natural
   "reach for MCP first" does not.
2. **Port/config truth** — Loomweave doctor advertises unreachable `:35541`;
   `:9730` is the working URL.
3. **Scanner job semantics** — foreground, low-feedback scans with no pollable
   job/status handle.
4. **Large-repo ingest** — Wardline/Filigree pair needs chunking/async beyond
   Lacuna's small corpus.

## Resolved by owner (2026-06-13) — see PDR-0002

- **Audience weighting → RESOLVED.** Both, *in sequence*: Lacuna is the **internal
  dogfood range now**, and graduates into an external **demonstrator** once the
  suite is finished. Demonstrator polish currently serves the dogfood range, not
  vice versa. (Captured in `vision.md` → Who it serves.)
- **Product boundary → RESOLVED.** Lacuna is a **consumer of the federation, not
  part of it**. When dogfooding finds a federation-tool bug, **Lacuna only ever
  owes a bug report** (specimen + reproducing fixture + friction write-up); the
  fix lives in the owning member's repo. (Captured in `vision.md` → Anti-goals.)

## Open questions still outstanding

- **N for guardrail G1:** the total count of "documented joins" needs to be set
  from the matrix/dogfood method. `<set>`

## Decided & dispatched this session (2026-06-13)

- **DECIDE → PDR-0003:** committed "federation seam integrity, agent-native" as
  the active Now bet; dispatched "MCP attachment truth" as its first workstream.
- **DISPATCH → PRD-0004** (`prds/PRD-0004-mcp-attachment-truth.md`, status
  `ready-for-planning`): reproduce + report the 3 MCP-attachment gaps (Filigree→
  hub, Loomweave→no-index, Legis→absent). Success metric G1 (0/4 → 4/4 MCP-first,
  2026-09-13); judged on Lacuna's deliverable (fixtures + reports), G1 as
  downstream outcome (consumer boundary).
- **Triaged:** observation `lacuna-obs-8aa96160f2` dismissed (resolved upstream).

## Where the next session starts

1. **Hand PRD-0004's top item to `/axiom-planning`** — the reproduction-fixture
   harness (a deterministic way to launch a clean attached session and capture
   each MCP server's attachment state, off the existing `tour/`+dogfood machinery).
2. **Route solution shape to `/axiom-solution-architect`** — how the harness hangs
   off `tour/` and the report/SEI-evidence schema.
3. **Route the committed bet to `/axiom-program-management`** for sequencing + the
   dated forecast (PRD-0004 emits no date).
4. **Resolve PRD-0004's open questions** — esp. the Legis "auto-attach vs.
   documented-launch" bar, and which tracker carries member-routed bug reports.
5. **CHECKPOINT** with `/product-checkpoint` at session end — the only step that
   commits the workspace (everything above is currently untracked on disk).
