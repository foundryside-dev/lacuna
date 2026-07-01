# PDR-0022 — Re-bless the tour narrative to exercised plainweave 1.2.0 (PDR-0016 reversal trigger fired)

- **Date:** 2026-07-01
- **Status:** Accepted (owner-approved in-session; the change to what the committed demo *shows* was surfaced and confirmed, not silently applied)
- **Decider:** human owner (John) approved the re-bless; agent:lacuna-po executed + recorded
- **Supersedes:** PDR-0016 *Consequences* bullet 3 (the "committed narrative re-blessed against PyPI 1.0.0, so the two cells read `[N/A]`" bless-state). PDR-0016's capability-gating **mechanism** is unchanged and still in force.
- **Related:** PDR-0016 (whose reversal trigger this fires), PDR-0015 (the cells), PDR-0021 (comprehensive-demo-as-primary), metrics G3, `docs/tour.md`, `docs/matrix.md`, `tour/steps.py`, [[loom-uvtool-build-staleness]]

## Context

Establishing a clean-tree `make verify` baseline before planting the plainweave coverage cells (PDR-0023) surfaced that `main`'s committed `docs/tour.md` was byte-locked against a subcommand-less plainweave (PyPI 1.0.0), rendering the two peer-facts cells `[N/A]` (PDR-0016). But Lacuna's Makefile resolves plainweave **BIN-first** from `/home/john/.local/bin/plainweave` with **no CI version pin**, and the installed BIN is **1.2.0** (PyPI now carries {1.0.0, 1.2.0}), which **exposes** `requirements-enrichment` + `wardline-peer-facts` → the cells exercise `[PASS]` and the committed `[N/A]` narrative is stale. This is exactly PDR-0016's reversal trigger ("if plainweave ships the subcommands to the release the gate pins, re-bless to the exercised state").

Two prerequisites had to clear first for an honest green baseline (not a papered-over one):
- **wardline's `[rust]` extra was missing** (installed as `wardline[loomweave]`), so its rust frontend (tree-sitter) threw `RustToolingError` and the two rust taint lacunae (RS-WL-108/112) went dark. Reinstalled `wardline[loomweave,rust]==1.2.0` (owner-authorized; uv extras REPLACE, so both needed) — the "watch wardline extras" trap ([[loom-uvtool-build-staleness]]). Rust lacunae restored.
- **legis re-stamped its AGENTS.md/CLAUDE.md instruction-block v1.3.0→v1.4.0** on spawn; absorbed (the documented friction).

## Decision

Re-bless `docs/tour.md` + `docs/matrix.md` to the **exercised** state under the gate's real environment (plainweave 1.2.0): the two peer-facts cells render `[PASS]`, and the `plainweave+wardline` / `plainweave+warpline` combination cells read as exercised. Committed as a standalone commit (`84d159c`), independent of the coverage-cells feature (PDR-0023). All lacunae surface (62 at this commit; 65 after PDR-0023); `make verify` exits 0.

## Consequences

- The committed demo now honestly shows plainweave's peer-facts joins **live**, matching the gate's installed plainweave — the primary comprehensive-demo posture (PDR-0021), not a design-only `[N/A]`.
- G3 (demonstration honesty) is **maintained, not weakened**: the cells exercise because plainweave 1.2.0 genuinely runs them; behaviour-probed capability-gating still renders `[N/A]` if a future env lacks the surface. No member is faked.
- The bless is against the **local/BIN plainweave**, not a CI-pinned version (there is no make-verify CI gate — only `deploy-site.yml`; `make verify` is the local north-star). The canonical demo env is "whatever plainweave the runner has installed," currently 1.2.0.

## Reversal trigger

- If the canonical gate env reverts to a plainweave lacking the peer-facts subcommands, the behaviour-probe re-gates the cells to `[N/A]` and `make verify` reds on the stale `[PASS]` narrative → re-bless back to `[N/A]` (same single-environment lockstep, honest either way).
- If serving the demo blessed to a **local editable/BIN** plainweave diverges from what an external evaluator would install from PyPI (a demonstrator-credibility risk, G3-adjacent), pin the tour's plainweave to a PyPI release and re-bless to that — escalate, as it touches the demonstrator posture (PDR-0021).
