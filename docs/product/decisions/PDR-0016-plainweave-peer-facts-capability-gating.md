# PDR-0016 — Plainweave peer-facts cells are capability-gated, not red, under PyPI 1.0.0

- **Date:** 2026-06-28
- **Status:** Accepted (under the standing tour-regression grant; resolves the merge-gate dogfood finding)
- **Decider:** agent (ultracode, subagent-driven)
- **Supersedes:** PDR-0015 *Consequences* bullet 2 ("Until that build is installed, the two
  legs degrade to `[WARN]` and `make verify` reds on the two new lacunae — the expected
  dependency, not a defect") — that consequence is **withdrawn**; see Decision.
- **Related:** PDR-0015 (the cells this gates), PDR-0010 (plainweave reachable),
  `docs/dogfood/2026-06-28-merge-gate-live-dogfood-report.md` (the run that surfaced this),
  `tour/capability.py`, `tour/report.py`, `tour/steps.py`, `tour/__main__.py`,
  `tour/lacunae.toml`

## Context

The merge-gate dogfood pins **`plainweave==1.0.0` from PyPI** (the local main wheel is broken
— `weft-5b26c6129d`), and Legis's advisory preflight join is validated **GO against exactly
that version** (`plainweave_preflight_facts_get`). But the two peer-facts tour cells added in
PDR-0015 shell out to plainweave CLI subcommands — `requirements-enrichment` and
`wardline-peer-facts` — that land only with **Plainweave PDR-015 / plainweave ≥ 1.1**. PyPI
1.0.0 exposes **neither the CLI subcommands nor the MCP producers**
(`plainweave_requirements_enrichment_get`, `plainweave_wardline_peer_facts_list`); argparse
rejects the subcommands as invalid choices.

Under PDR-0015's design (`expected_tool = "plainweave"`, gated only on the *binary*) this made
`make verify` do two dishonest things at once under the brief-pinned 1.0.0:
1. **red the two lacunae** as "expected lacuna not surfaced" — reading a *not-yet-released
   capability* as a *broken demo*; and
2. degrade each leg to an opaque `[WARN] … failed: RuntimeError` — a confident-false failure
   with no machine-readable reason.

PDR-0015 anticipated (1) and called it "the expected dependency, not a defect", with the
intended fix being **install the updated plainweave** (its clean-checkout prerequisite #1).
That path is incompatible with the merge gate: it requires fixing a Plainweave packaging bug
in a sibling repo, replaces 1.0.0 globally (disturbing the validated Legis-preflight join),
is not reproducible from PyPI, and contradicts the gate's own `uv tool install --force
plainweave` step. Switching the tour to the MCP surface is also impossible — 1.0.0 lacks the
MCP producers too.

## Decision

Keep `plainweave==1.0.0` from PyPI. Make the two cells **capability-gated on the specific CLI
surface each needs**, probed by behaviour (not version string), so that under a plainweave
lacking the surface they are **honestly unavailable** — neither red nor faked green — and the
gate is explicit on every surface:

1. **Per-subcommand capabilities** (`tour/capability.py`). `detect()` probes the live
   `plainweave --help` choices and emits one capability per peer-facts subcommand
   (`plainweave-requirements-enrichment`, `plainweave-wardline-peer-facts`). Behaviour-probed,
   because PyPI 1.0.0 and the CLI-parity build **share a version string but not a surface**
   (the stale-build trap the dogfood itself calls out). Gated **per subcommand** so a partial
   plainweave release lights up exactly the cells whose surface is present.
2. **`expected_tool` re-pointed** (`tour/lacunae.toml`) from `plainweave` to the per-subcommand
   capability. `make verify`'s coverage assertion (`expected_tool in live AND missing`) no
   longer reds a cell whose surface is absent — the capability is not in `live`.
3. **A distinct `[N/A]` render state** (`tour/report.py`, `StepResult.available`). A gated leg
   renders `[N/A]` — *did not run, did not fail, not faked green* — separate from `[WARN]`
   (ran and degraded). The step (`tour/steps.py`) emits a frozen, machine-readable reason.
4. **Honest matrix + explicit verify output.** `render_matrix_md` annotates a cell whose only
   demonstrating lacuna is gated as *not exercised* (with the reason) instead of flat-listing
   it as exercised (which would be a confident-false coverage claim). `run_verify` prints an
   explicit `CAPABILITY-GATED (… not a failure)` block naming each gated lacuna + reason, so a
   silent gate is never itself a swallow.

This **reconciles** PDR-0015 rather than reversing its intent: when a plainweave carrying the
subcommands is installed, the surface probe sees it, the capabilities go live, and the cells
exercise green automatically.

## Consequences

- Under the brief-pinned PyPI 1.0.0, the two cells are `[N/A]` and **gated out of verify's
  coverage assertion** — `make verify` no longer reds on them, and the missing CLI surface is
  explicit in `docs/tour.md`, `docs/matrix.md`, and verify's stdout. No fake green.
- The Legis advisory-preflight join is **untouched** and still validated against PyPI 1.0.0.
- The committed narrative (`docs/tour.md`) is re-blessed against PyPI 1.0.0, so the two cells
  read `[N/A]`. **This is a single-environment lockstep, blessed against PyPI 1.0.0.** With a
  plainweave that carries the subcommands installed, the coverage gate passes (cells light up)
  but the byte-locked narrative will then be stale and **requires a `make tour` regen** — the
  normal consequence of changing a member's version, not a defect.
- PDR-0015's clean-checkout prerequisite #1 ("install the updated plainweave") is **no longer
  required for a green merge gate**; it remains the path to demonstrate the cells *exercising*
  rather than gated.

## Reversal trigger

If Plainweave ships the `requirements-enrichment` / `wardline-peer-facts` CLI subcommands to
the PyPI release the gate pins, the probe will see them and the cells will exercise green; at
that point re-bless `docs/tour.md` to the exercised state and this capability-gate becomes a
no-op (correctly — the surface is present). If the `plainweave --help` usage format changes
such that the argparse choices block is no longer parseable, the probe returns empty ("cannot
tell" ⇒ unavailable) and the cells gate to `[N/A]` rather than silently passing — at which
point the probe in `capability.plainweave_subcommands` is updated.
