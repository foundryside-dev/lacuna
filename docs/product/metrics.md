# Metrics — Lacuna

_Standing product artifact. Every target is **falsifiable**: a number and a date
against a BASELINE → TARGET placeholder. A directional word is not a metric._
_Bootstrapped 2026-06-13. Owner must set real numbers where marked `<set>`._

## North star

**Specimen fidelity** — the fraction of catalogued *live* lacunae the tour
actually surfaces, with the generated narrative in lockstep, and zero
*uncatalogued* findings tripping the gate. This is the one number that says "the
proving ground still proves." Measured by `make verify`.

- **Definition:** `make verify` passes on `main` ⇔ (100% of live lacunae
  surfaced) ∧ (narrative/docs in lockstep) ∧ (0 uncatalogued gate-tripping
  findings).
- **BASELINE → TARGET:** green at commit `c9d407f` (44 catalogued lacunae)
  → **100% of live lacunae surfaced and `make verify` green on every `main`
  commit, by 2026-09-13.**
- **Reversal trigger:** if holding fidelity green requires suppressing a *real*
  (uncatalogued) defect to keep the gate quiet, stop — that inverts the product.

## Guardrails

### G1 — Federation seam health

The number of documented cross-tool joins an agent can reach **MCP-first**, with
no CLI / raw-JSON-RPC fallback, in a real attached session.

- **N = 4 documented cross-tool joins** (2026-06-13 dogfood method status table):
  Wardline→Filigree work joins; Loomweave→Filigree Wardline-finding enrichment;
  Loomweave→Filigree issue association; Legis MCP/tools surface.
- **BASELINE → TARGET:** per the 2026-06-13 re-dogfood, all 4 joins *function* but
  **0 of 4 are cleanly reachable MCP-first** in one attached session (Filigree MCP
  → Weft not the staged repo; Loomweave MCP → no-index context; Legis MCP absent
  in-session) → **4 of 4 documented joins reachable MCP-first in one attached
  session, by 2026-09-13.**
- **Reversal trigger:** a "fixed" seam that an agent still has to shell out for is
  not fixed — reopen it.

### G2 — Dogfood friction (open count)

Count of open cross-tool friction items in the most recent dogfood report.

- **BASELINE → TARGET:** 4 remaining cross-tool frictions (2026-06-13 report:
  MCP attachment, port/config truth, scanner job semantics, large-repo ingest)
  → **≤ 1 open cross-tool friction at the next dogfood, by 2026-09-13.**
- **Reversal trigger:** friction count rising report-over-report means seam work
  is regressing faster than it lands — escalate.

### G3 — Demonstration honesty (do-no-harm)

The tour never fakes a member. Design-only members (Charter; Legis where its MCP
is unattached) are **labelled**, never simulated as live.

- **BASELINE → TARGET:** honest as of 2026-06-13 (Charter labelled design-only;
  tour "degrades honestly") → **0 faked-as-live members across all tour runs,
  maintained.**
- **Reversal trigger:** any tour leg presenting a design-only or unreachable
  member as live — hard stop; honesty is the demo's credibility.

> _Note: raw "analyzer findings" counts (155 unbridged / 44 baselined) are
> **telemetry, not a metric** — they are mostly the planted lacunae themselves.
> Do not treat finding-count reduction as progress._
