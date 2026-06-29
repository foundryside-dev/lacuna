# Roadmap — Lacuna

_Standing product artifact. **INTENT ONLY.**_
_Bootstrapped 2026-06-13 from observed direction (recent commits + open dogfood friction)._

> **Routing banner.** This roadmap expresses **intent and relative horizon
> only** — Now / Next / Later. It carries **no dates, no WSJF scores, and no
> sequencing**. Sequencing, cost-of-delay/WSJF prioritization, and dated
> forecasts are produced by **`/axiom-program-management`**, never here. The
> committed top bet is handed there for scheduling.

## Now — the current bet

**Federation seam integrity, agent-native.** Make the cross-tool *joins* — the
federation's actual pitch — work the way an agent would naturally reach for them
(MCP-first, no CLI/JSON-RPC fallback), with consistent config/port truth. The
06-13 post-fix re-dogfood confirmed the big seams now function (wardline→filigree
work joins, loomweave→filigree finding/issue enrichment) but flagged that MCP
attachment was still inconsistent in a real session.

> **Updated: 2026-06-25 (PDR-0006, PDR-0007).** The MCP-attachment-truth workstream is
> COMPLETE — G1 = 4/4 joins reachable MCP-first in one attached session (probed in-session,
> the three 06-13 gaps resolved by member config-fixes). The Now theme holds; its successor
> workstream is **plainweave MCP attachment** (the 6th member is MCP-absent in Lacuna) — see
> Next + PDR-0007.
>
> **Updated: 2026-06-26 (PDR-0009, PDR-0010, PDR-0011).** Plainweave Phase 1 ACCEPTED —
> reachable MCP-first (PDR-0010). But the seam proved more fragile than recorded: a stale
> loomweave v10 build silently de-attached loomweave's MCP server and red-lit `make verify`
> (caught, root-caused, fixed — PDR-0011). G1 is now a **live join census** (PDR-0009), and the
> Phase-2 **6-member attachment regression-harness** is the live Next bet — its whole point is
> to trip `make verify` on exactly the silent de-attach that went undetected this session.
>
> **Updated: 2026-06-28 (PDR-0012, PDR-0013, PDR-0014).** The Phase-2 harness is **DELIVERED +
> GREEN** — `make verify` now asserts all 6 members attach AND store-bind live on every run, so a
> silent de-attach trips the gate by name (built end-to-end; opus whole-branch review
> Fix-then-merge, all fixed; branch unpushed pending owner). **G1 is now a GATE, not a manual
> probe.** Two refinements landed: warpline+wardline got server-side store-read binding tools (R1,
> PDR-0013), and the spike strengthened the 4 path-members to path-AND-store (PDR-0014). The Now
> theme's centerpiece is realized; the remaining Next items carry it forward.
>
> **Updated: 2026-06-29 (PDR-0018, PDR-0019).** PR #2 **MERGED to `main`** (merge `5107462`): the
> harness + the plainweave/warpline peer-facts cells are now on `main` — **G1 is a gate on `main`**,
> not a branch. Corpus 52 → **62** catalogued lacunae. The merge-gate dogfood's consumer-boundary
> findings are filed/reconciled (PDR-0019); the loomweave←warpline churn join flipped NO-GO →
> **live-GO on main** when loomweave PR #77 merged (2026-06-29). The Now theme continues with the
> remaining Next items + the deferred Phase-5 join census.

- _Moves:_ federation seam health (guardrail) and dogfood friction count.
- _Why now:_ the joins are the product's reason to exist as a demo; a join that
  only works via raw shell undercuts "point the suite and watch it work."

## Next — proposed (intent, not committed)

- **6-member attachment regression-harness — ✅ DELIVERED + MERGED TO MAIN 2026-06-29 (PDR-0012,
  PDR-0018).** The durable win is on `main` (PR #2, merge `5107462`): `make verify` asserts all 6
  members attach AND store-bind to the staged repo on every run, so a silent de-attach trips the
  gate by name. _Caveat now a property of `main`:_ green only against sibling **release** builds
  (D1/D2 `weft-ca12d859bb`); `tour.md` byte-locked to PyPI plainweave 1.0.0 (PDR-0016). _Remaining
  sub-increment:_ **Phase 5 join census** (the `live-bound | live-empty | reachable-gated | absent`
  per-join liveness classes) DEFERRED to its own PR. _(Moved: federation seam health — now a gate
  on `main`.)_
- **Plainweave + warpline peer-facts cells — ✅ MERGED 2026-06-29 (PDR-0015/0016/0017, PDR-0018).**
  Four tour cells exercising members **consuming** siblings' facts (plainweave→wardline,
  plainweave→warpline, wardline→warpline, the 4-member federation cell), each asserting the
  no-silent-clean invariant. Emerged as sibling-driven tasking, not a planned bet. **OPEN PRODUCT
  QUESTION for the next DECIDE:** promote "peer-facts cells" to an explicit Next theme, or treat as
  completed one-off tasking? (not yet decided — see current-state). _(Moves: combination-matrix
  coverage.)_
- **One freshness/port oracle per tool.** Reconcile contradictory status
  surfaces (e.g. Loomweave doctor advertising an unreachable `:35541` while
  `:9730` is the working URL). _(Moves: dogfood friction count.)_
- **Scanner job semantics as a product finding.** Treat foreground, low-feedback
  scans with no pollable job/status handle as a first-class friction even when
  Lacuna's small scan passes. _(Moves: dogfood friction count.)_
- **Rust wing depth.** The Wave-3 Rust wing landed (52 lacunae total); extend
  coverage of rust-specific taint/archaeology combinations. _(Moves: specimen
  fidelity / combination-matrix coverage.)_

## Later — horizon

- **Large-repo ingest story.** Chunking / async ingest for the Wardline→Filigree
  pair beyond Lacuna's small corpus (the 1000-finding cap is now visible).
- **Charter promotion.** When Charter graduates from design-only to live, add the
  lacunae + tour legs that exercise it (today it is honestly labelled design-only).
- **Combination-matrix completeness.** Fill remaining empty cells in
  `docs/matrix.md` so every advertised tool-combination has a planted exemplar.
- **Graduate from dogfood range to demonstrator.** Owner-confirmed end-state
  (2026-06-13): once the suite is finished, Lacuna turns from internal proving
  ground into the external "watch it work" demonstrator. This is a *Later*
  horizon gated on suite completion — the trigger to revisit demonstrator polish
  (tour narrative quality, onboarding the "point it and watch" path) as primary
  rather than in service of dogfooding. Not started; do not pull forward until
  the Now/Next seam work clears.
