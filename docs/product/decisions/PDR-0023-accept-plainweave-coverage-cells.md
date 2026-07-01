# PDR-0023 — Accept the plainweave comprehensive-coverage cells (baseline / verification / dossier); first increment of PDR-0020

- **Date:** 2026-07-01
- **Status:** Accepted (subagent-driven build; whole-branch opus review = ready-to-merge, 0 Critical/0 Important; owner-authorized push/PR)
- **Decider:** agent:lacuna-po (built + accepted against criteria); human owner authorized the PR
- **Related:** PDR-0020 (comprehensive-coverage theme — this is its first concrete increment), PDR-0015/0016 (the pattern + capability-gating this reuses), PDR-0022 (the §10 re-bless that cleared the baseline), spec `docs/superpowers/specs/2026-06-30-plainweave-coverage-lacunae-design.md`, plan `docs/superpowers/plans/2026-07-01-plainweave-coverage-lacunae.md`, PR #3, observation `lacuna-obs-c116dca009`

## Context

Last checkpoint's open COVERAGE question (current-state 2026-06-29): plainweave's **baseline / verification-status / dossier** surfaces had no planted lacuna; confirm net-new vs. a reconcile. The owner confirmed **net-new** and directed planting them. This is the first member-surface-deepening increment of the comprehensive-coverage theme (PDR-0020): cover each member's FULL surface, not only cross-member combinations.

## Decision

Plant three capability-gated, no-silent-clean, single-member capability-depth cells — `pw-baseline-drift`, `pw-verification-status`, `pw-requirement-dossier` — over plainweave's baseline / verification / dossier surfaces (corpus 62 → **65**). Built via subagent-driven TDD (one task per commit, each per-reviewed; the core leg + whole branch reviewed by opus = ready-to-merge, 0 Critical/0 Important). `make verify` green; the §8.4 real-producer integration smoke passes against **real plainweave 1.2.0**; the feature adds **no new boundary taint** (`wardline --new-since` = exit 0). Shipped as **PR #3** (owner-authorized push/PR); merge to `main` remains owner-gated.

**DIVERGENCE recorded (corrects the design spec's assumption):** unlike the peer-facts subcommands (genuinely absent in 1.0.0, PDR-0016), `baseline`/`verify`/`status`/`dossier` **ship in PyPI 1.0.0** (proven by the committed `tests/test_capability.py::_HELP_1_0_0` fixture). So these coverage cells do **not** degrade to `[N/A]` on an old PyPI plainweave — their `[N/A]` path is reachable only via a genuinely stripped/pre-baseline build (tests simulate it). Their gated `detail`/`explanation` must not (and do not) claim "absent in PyPI 1.0.0."

## Consequences

- plainweave's own-surface coverage is deepened; the matrix `plainweave` cell was already exercised, so coverage shows in the +3 lacunae + the new `plainweave coverage` tour leg + 3 capability rows, not a new matrix cell (spec §1).
- **Residual gap:** plainweave's **preflight** surface (legis-facing) remains unplanted — the next plainweave own-surface pickup under PDR-0020. `goal`/`criterion`/`bind`/`trace`/`catalog` are already exercised by the intent cells; `actor` is out of scope (identity → **tabard's** forthcoming domain, PDR-0021).
- One pre-existing pattern (`materialize_workspace()` sits outside the leg try/except across all 3 plainweave legs) filed as observation `lacuna-obs-c116dca009` — address collectively, non-blocking.

## Reversal trigger

- If any cell's no-silent-clean predicate proves hollow (a per-conjunct drop-test stops failing when its conjunct breaks) or a real plainweave contract change silently breaks a predicate, reopen the cell (fix the predicate + re-verify) — the same fidelity discipline as the north star.
- If the DIVERGENCE means these cells never demonstrate honest `[N/A]` degradation on any plainweave an evaluator realistically runs, that is acceptable — they still demonstrate the load-bearing no-silent-clean invariant (their primary purpose); revisit only if that invariant demo proves redundant with the intent cells.
