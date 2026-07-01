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
- **BASELINE → TARGET:** green at commit `445c270` (2026-06-26, clean tree, exit 0,
  52 catalogued lacunae; was 44 at 2026-06-13 bootstrap)
  → **100% of live lacunae surfaced and `make verify` green on every `main`
  commit, by 2026-09-13.**
- **Reversal trigger:** if holding fidelity green requires suppressing a *real*
  (uncatalogued) defect to keep the gate quiet, stop — that inverts the product.

## Guardrails

### G1 — Federation seam health

The **live census** of documented cross-tool joins an agent can reach
**MCP-first** (no CLI / raw-JSON-RPC fallback) in a real attached session — the
count **plus a per-join liveness class** (`live-bound | live-empty |
reachable-gated | absent`). Measured each session and, durably, by the Phase-2
6-member attachment harness — **not** a hand-set integer (PDR-0009). The seam set
grows as members ship interfaces, so the census tracks reality, not a frozen N.

- **Enumerated joins (2026-06-26 census):** the original 4 — Wardline→Filigree
  work; Loomweave→Filigree finding-enrichment; Loomweave→Filigree issue-assoc;
  Legis surface — **plus plainweave→loomweave** (ratified, PDR-0009). Also observed
  live but not yet enumerated: plainweave→legis preflight, legis→loomweave
  rename-feed; live-but-empty: filigree↔loomweave entity-assoc; reachable-but-gated:
  legis→filigree closure-gate (needs operator `LEGIS_HMAC_KEY`).
- **BASELINE → TARGET:** 5 of 5 enumerated joins reachable MCP-first in one attached
  session (the 4 originals + plainweave→loomweave), each labelled by liveness class,
  **by 2026-09-13** — and a silent de-attach must trip `make verify` (Phase-2
  harness), not require manual probing.
- **Reversal trigger:** a "fixed" seam an agent still has to shell out for is not
  fixed — reopen it. A silent member de-attach the gate does **not** catch is a G1
  failure even if a later manual probe passes (the 2026-06-26 loomweave incident).

### G2 — Dogfood friction (open count)

Count of open cross-tool friction items in the most recent dogfood report.

- **BASELINE → TARGET:** 4 remaining cross-tool frictions (2026-06-13 report:
  MCP attachment, port/config truth, scanner job semantics, large-repo ingest)
  → **≤ 1 open cross-tool friction at the next dogfood, by 2026-09-13.**
- **Reversal trigger:** friction count rising report-over-report means seam work
  is regressing faster than it lands — escalate.

### G3 — Demonstration honesty (do-no-harm)

The tour never fakes a member. Design-only / not-yet-released members (**tabard**,
forthcoming — identity management; Legis where its MCP is unattached) are
**labelled**, never simulated as live. _(Charter is no longer the example here — it
shipped as plainweave, now live; PDR-0021.)_

- **BASELINE → TARGET:** honest as of 2026-06-13 (Charter labelled design-only;
  tour "degrades honestly") → **0 faked-as-live members across all tour runs,
  maintained.**
- **Reversal trigger:** any tour leg presenting a design-only or unreachable
  member as live — hard stop; honesty is the demo's credibility.

## Readings (dated)

- **2026-07-01 — North star: `make verify` GREEN at 65 lacunae on the coverage feature branch (PR #3, unmerged); `main` baseline still 62 until merge.** The 3 plainweave coverage cells (baseline/verification/dossier) exercise `[PASS]`; §8.4 real-producer integration smoke passes vs real plainweave 1.2.0; feature adds no new boundary taint (`wardline --new-since` exit 0). **Reversal trigger (suppress a real defect): NOT tripped** — the pre-existing wardline `[rust]`-extra gap (rust lacunae RS-WL-108/112 dark) was FIXED (reinstall `wardline[loomweave,rust]`), not suppressed. [PDR-0022, PDR-0023]
- **2026-07-01 — G3 (demonstration honesty): PDR-0016 reversal trigger FIRED as designed (not a failure).** The gate resolves plainweave BIN-first at **1.2.0** (PyPI now has {1.0.0, 1.2.0}; no CI pin), which exercises the peer-facts subcommands → `docs/tour.md` **re-blessed from `[N/A]` (1.0.0) to `[PASS]` (1.2.0)** (PDR-0022, owner-approved), and `plainweave+wardline`/`plainweave+warpline` now read exercised. **Honesty MAINTAINED** — the cells `[PASS]` because 1.2.0 genuinely runs them (not faked); the new coverage cells' DIVERGENCE (baseline/verify/status/dossier ship in 1.0.0 too, so they don't falsely claim 1.0.0-absence) is handled honestly. G3 reversal trigger (present a design-only/unreachable member as live): NOT tripped. [PDR-0022, PDR-0023]
- **2026-07-01 — G2 (dogfood friction):** the **wardline uv-tool build-staleness** trap recurred (installed `[loomweave]` without `[rust]` → rust frontend dark) and was RESOLVED (reinstall `[loomweave,rust]`) — the "watch wardline extras" class ([[loom-uvtool-build-staleness]]). One pre-existing follow-up filed: observation `lacuna-obs-c116dca009` (`materialize_workspace()` outside the try/except across all 3 plainweave legs). No net rise in open cross-tool friction.
- **2026-07-01 — G1 (federation seam health): unchanged** — no seam work this session; the 6-member attach gate remains live on `main` (PR #2). The coverage cells are single-member capability-depth, not new joins.

- **2026-06-29 — North star: PR #2 MERGED to `main` (merge `5107462`); main baseline moves
  `445c270`/52 → `5107462`/**62** catalogued lacunae.** The 6-member attachment harness + the
  plainweave/warpline peer-facts cells are now on `main`. Caveat now a property of `main` (not a
  defect): `make verify` is green only against sibling **release** builds (warpline `release/1.2.0`,
  wardline `1.0.7 [scanner,rust]` — D1/D2 `weft-ca12d859bb`), and `tour.md` is byte-locked to PyPI
  plainweave 1.0.0 (PDR-0016, the two plainweave peer-facts cells render honest `[N/A]`).
  **Reversal trigger (suppress a real defect to keep the gate quiet): NOT tripped.** [PDR-0018]
- **2026-06-29 — G1 (federation seam health): the gate is now LIVE ON `main`** (was branch-only).
  The `loomweave←warpline` churn join flipped **NO-GO → live-GO** when loomweave **PR #77**
  (`30549a3`, NDJSON framing + repo arg + recv-timeout + real wire test) **merged 2026-06-29**
  (`1d2b4fa`); hub items `weft-6fc4a166dc` (validation gate), `weft-e585382ff3` (deadlock bug), and
  parent `weft-670ec2fe90` are all CLOSED with merge-tied reasons. No reversal trigger tripped (a
  real break was fixed honestly, not suppressed). [PDR-0019]
- **2026-06-29 — G2 (dogfood friction): the 2026-06-28 merge-gate findings filed/reconciled**
  (PDR-0019). loomweave churn friction RESOLVED (PR #77 merged). D1/D2 (member LATEST capabilities
  live on release branches, not `main`) filed as `weft-ca12d859bb` — a federation-infra prerequisite
  owned by the hub/members, not a Lacuna-open friction. Carried watch-items: legis MCP re-stamps
  `AGENTS.md`/`CLAUDE.md` on a version bump (absorbed v1.3.0; re-absorb on next legis upgrade);
  loomweave/warpline/wardline uv-tool build-staleness on `uv tool upgrade`. Open Lacuna-side
  frictions unchanged: port/config truth, scanner job semantics, large-repo ingest.
- **2026-06-29 — G3 (demonstration honesty): maintained.** The two plainweave peer-facts cells
  render `[N/A]` (capability-gated, not faked green) under PyPI 1.0.0; the warpline cells assert the
  no-silent-clean invariant; no member faked as live. [PDR-0016, PDR-0017]
- **NO PDR reversal trigger tripped this checkpoint.**

- **2026-06-28 — North star (`make verify`): GREEN end-to-end with the Phase-2 harness on the
  (unpushed) `plainweave-mcp-attach` branch; corpus 52 → 58 there.** The 6-member MCP-attachment
  harness is DELIVERED (PDR-0012): `make verify` exits 0 with the live `steps.mcp_attachment()`
  leg driving all 6 federation MCP servers — all attach+store-bind, the 6 `mcp-attach-*` lacunae
  surface, narrative lockstep, tree clean. The gate is now BIDIRECTIONAL: two negative tests prove
  `make verify` TRIPS (naming the member + cause) on a silent de-attach. Reversal trigger (suppress
  a real defect) NOT tripped. The **main-commit baseline (445c270, 52 lacunae) is unchanged until
  the branch merges** (push/PR owner-gated). (Note: tour.md carries live loomweave entity counts
  that drift on re-index — an existing tour property; regen+commit to re-green, not a fidelity
  failure.)
- **2026-06-28 — G1 (federation seam health): the live census is now a GATE, not a manual probe
  (PDR-0012).** All 6 members attach AND store-bind to the staged repo, re-verified by `make verify`
  on every run — durably, not by a one-off in-session probe. PDR-0009's reversal trigger ("a silent
  member de-attach the gate does NOT catch is a G1 failure even if a later manual probe passes") is
  structurally ADDRESSED: the gate is exactly that catch. Binding is store-read for all 6
  (warpline/wardline new tools, PDR-0013; the 4 path-members strengthened to path-AND-store,
  PDR-0014) — catching the stale-but-running incident class, not just process-start. The attach
  census is MET as a gate, ahead of the 2026-09-13 target; the per-join liveness-class census
  (Phase 5) is deferred to its own PR.
- **2026-06-28 — G2 (dogfood friction):** the warpline/wardline binding-tool gap RESOLVED — both
  sibling members shipped server-side store-read binding tools (PDR-0013). NEW friction discovered
  + mitigated: **the legis MCP server re-stamps its `AGENTS.md`/`CLAUDE.md` instruction-block to the
  installed version on spawn** — the harness leg spawns legis on every `make verify`, so a version
  bump would dirty the tree and trip the clean-tree gate; absorbed v1.3.0 and confirmed durable, but
  a future legis upgrade requires re-absorbing (current-state open item). Open otherwise: port/config
  truth, scanner job semantics, large-repo ingest.
- **2026-06-28 — G3 (demonstration honesty): maintained.** The 6 `mcp-attach-*` lacunae are honestly
  labelled "NOT A FLAW — a federation seam-integrity demo"; the leg honest-degrades (surfaces a token
  only for a member that genuinely attached AND bound); no member faked as live.

- **2026-06-26 — North star: `make verify` GREEN, exit 0 at `445c270` (clean tree); all 52
  lacunae surface.** **CORRECTS the 2026-06-25 reading below:** the RED was NOT merely
  dirty-tree — it was a *real fidelity failure* from a **stale loomweave v10 binary against a
  v11 DB** (same-version uv-tool staleness) that dark-ed 5 lacunae (`lw-duplicate-locator` + 4
  `wp-*`). Root-caused and fixed (loomweave v11 reinstall + `_finding_qualname` reconcile, 3
  commits). Reversal trigger (suppress a real defect) NOT tripped — fixed honestly. [PDR-0011]
- **2026-06-26 — G1: regressed then restored.** Mid-session loomweave MCP **silently
  de-attached** (stale v10 binary) → 2 of the 4 original joins unreachable → G1 ~2/4,
  **reversal trigger TRIPPED**. Restored after the v11 reinstall + owner MCP-restart: loomweave
  MCP reattached; original 4 + plainweave→loomweave reachable (5/5 enumerated). Census also
  surfaced new live joins (plainweave→legis preflight, legis→loomweave rename-feed) and honest
  non-live states (filigree↔loomweave live-empty; legis→filigree closure-gate operator-gated).
  [PDR-0009, PDR-0010, PDR-0011]
- **2026-06-26 — G2 dogfood friction:** plainweave-attachment friction RESOLVED (Phase 1
  accepted, PDR-0010). New friction: **loomweave uv-tool build staleness** (v10/v11 schema split
  → MCP de-attach + verify red) — resolved this session; and the **loomweave duplicate-locator
  evidence-contract rename** (consumer-boundary, report PENDING owner). Open: port/config truth,
  scanner job semantics, large-repo ingest, + the Phase-2 harness gap (silent de-attach went
  undetected by the gate).
- **2026-06-26 — G3 honesty: maintained.** The live census classified each join honestly
  (live/empty/gated/absent); no member faked. Legis closure-gate labelled operator-gated, not
  simulated.
- **2026-06-25 — G1 federation seam health: 4 of 4 (TARGET MET, ahead of 2026-09-13).**
  Probed in-session via `mcp__*` tools — Wardline→Filigree, Loomweave→Filigree enrichment,
  Loomweave→Filigree issue-assoc (channel reachable), Legis governance — all reachable
  MCP-first; the three 06-13 attachment gaps were resolved by member config-fixes. No
  reversal trigger tripped (target reached, not a regression). [PDR-0006]
- **2026-06-25 — North star (specimen fidelity): `make verify` RED, but NOT a regression.**
  Sole cause: uncommitted *tooling* churn (SKILL.md / AGENTS.md / CLAUDE.md install blocks)
  → dirty tree → legis refuses to sign → `tour.md` stale. Green on a clean tree at `d09da33`
  (PDR-0005 `make ci` green). Reversal trigger (suppressing a real defect) NOT tripped.
- **2026-06-25 — Corpus: 52 catalogued lacunae** (was 44 at bootstrap; +4 `pw-*` in PDR-0005).
  Telemetry; reconciled across vision/roadmap/metrics this checkpoint.
- **2026-06-25 — G2 dogfood friction:** the 06-13 MCP-attachment friction is RESOLVED. New
  frontier logged: plainweave (6th member) MCP-absent [PDR-0007]. Open frictions now:
  port/config truth, scanner job semantics, large-repo ingest, plainweave attachment.
- **2026-06-25 — G3 demonstration honesty: maintained.** No member faked as live; plainweave
  honestly CLI-only, charter design-only.

> _Note: raw "analyzer findings" counts (183 unbridged / 44 baselined) are
> **telemetry, not a metric** — they are mostly the planted lacunae themselves.
> Do not treat finding-count reduction as progress._
