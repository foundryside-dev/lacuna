# Lacuna — repivot design

**Date:** 2026-06-05
**Status:** Design (awaiting review → implementation plan)
**Supersedes:** the `testo` "Loom suite integration sandbox" framing (`README.md`, `INTEGRATION_LOG.md`)

> **Federation roster/axiom — defer to the hub.** This spec narrates Lacuna's
> place in the Loom suite and references the member matrix. The authoritative
> source for the federation axiom and roster is the Loom hub at `~/loom`:
> see `~/loom/doctrine.md` (axiom + roster) and `~/loom/federation-map.md`
> (integration matrix). Per the hub, Lacuna is the federation's **demonstration
> specimen, not a roster member** (`~/loom/members/lacuna.md`); the "first-class
> Loom member" phrasing below predates the hub's ruling and is superseded by it
> for roster purposes. Everything below about the *specimen, manifest, and tour
> design* remains Lacuna's own and is unaffected.

## One-line

Lacuna is the **MissingNo of the Loom suite**: a first-class Loom member whose role
is inverted — where the other tools are *instruments*, Lacuna is the *specimen*. It
is a clean-cored reference application seeded with documented, curated **lacunae**
(planted flaws), each one placed to make a specific Loom tool or matrix-combination
light up. Pointing the suite at Lacuna is how you see what Loom does.

## Why this exists

`testo` is currently a private scratch sandbox that proves the four arms install and
interoperate. That work is done and green (see `INTEGRATION_LOG.md`). The repivot
turns that throwaway into a durable, runnable, narratable **demonstrator** — the
canonical thing a newcomer (human or agent) runs to understand the suite, and the
thing the suite is regression-demonstrated against.

The name **Lacuna** = a gap or missing portion in a manuscript ("the missing one").
The specimen is defined by what is absent or wrong; each Loom tool fills the lacuna
with its own typed facts. Naming the planted flaws "lacunae" is literal, not cute.

## Locked decisions (from brainstorming)

| Decision | Choice |
|---|---|
| Code-quality model | **Layered** — a genuinely well-architected core, deliberately seeded with *curated, documented* flaws (not incidental sloppiness). The bad code is permanent and intentional; "first-class" applies to packaging, narrative, and positioning — never to cleaning the planted flaws away. |
| Scope | **Heavy runnable showcase** — automated harness + narrative + reproducible setup. |
| Rename depth | **Full re-key** across all four tools (new Filigree prefix, fresh Clarion SEIs, rewritten configs/hooks, new directory). |
| Showcase spine | **Both** — an automated harness that is the source of truth, a narrative kept in lockstep with it, and a machine-readable flaw manifest underneath both. |
| Home | `/home/john/lacuna` (copy already made; `/home/john/testo` retained as the pre-rekey snapshot for reversibility). |

## Architecture

### 1. The flaw manifest — single source of truth

`tour/lacunae.toml` is the canonical catalog. Each entry is one planted lacuna:

```toml
[[lacuna]]
id            = "WL-101-trust-violation"
location      = { file = "specimen/trust_flow.py", symbol = "unsafe_account_key" }
category      = "trust-boundary"
demonstrates  = ["wardline", "wardline+clarion", "wardline+filigree"]
expected      = { tool = "wardline", rule = "PY-WL-101" }   # asserted by the harness
explanation   = "Declares return trust ASSURED but returns EXTERNAL_RAW — untrusted data reaches a trusted producer."
```

Everything derives from the manifest:
- the **harness** drives the tour from it and *asserts* each `expected` finding;
- the **narrative** (`docs/tour.md`) is generated from a harness run;
- the **per-flaw doc pages** (`docs/flaws/`) are generated from it;
- the **matrix coverage report** (`docs/matrix.md`) is computed from the union of
  `demonstrates` across all entries.

Rejected alternative: a hand-written tour doc beside a separate harness — they rot
out of sync. The manifest is what guarantees the runnable artifact and the story
never drift.

### 2. The specimen — clean core + planted lacunae

`sampleapp/` → `specimen/`. Keep the existing rich, *well-formed* pattern set (ABCs,
`Protocol` structural typing, bounded generics, mixins/MRO, decorator factories,
classmethod factories, properties, operator overloading, enums, dataclasses, and the
strategy/observer/decorator/registry patterns). Then seed **isolated, catalogued**
flaws spanning Loom's combination matrix:

- **Wardline** — all four policy rules exercised: the existing trust violation
  (`unsafe_account_key` / `PY-WL-101`), a non-rejecting boundary, a broad exception
  handler, and a silently-swallowed exception.
- **Clarion** — rich structure to surface: a coupling hotspot, a circular import,
  dead code, a deep execution path, a clear entry point.
- **Filigree** — Wardline findings become tracked work; a planted bug that exercises
  the hard `fix_verification` gate; a dependency chain that produces a critical path.
- **Combinations** — the dossier read (Wardline+Clarion), finding→work
  (Wardline+Filigree), an issue bound to a SEI that survives a rename
  (Clarion+Filigree), and a policy-tripping change at the git/CI boundary
  (Wardline+Legis / Filigree+Legis), demonstrated where the tool is live.

Each planted flaw is isolated enough that its manifest entry can point at a single
file+symbol and explain it without unpicking the whole app.

**Honest dogfooding of the gate.** The specimen intentionally contains trust
violations, which would trip `wardline scan --fail-on ERROR`. The planted lacunae are
therefore **baselined/waivered** in `wardline.yaml` with reasons that cite the
manifest. Result: the planted lacunae are catalogued (not "new"), and the gate still
catches genuinely new mistakes introduced while working on Lacuna. This is the
baseline-vs-waiver discipline from the `wardline-gate` skill, used as intended.

### 3. The showcase spine — `tour/`

`make tour` runs `tour/tour.py`, which:

0. **Preflight / capability detection.** Detect which Loom tools are actually
   runnable (filigree ✅, clarion ✅, wardline ✅; legis `1.0.0rc1` partial; charter
   scaffold). Report capability honestly and **degrade honestly** — never fake or
   stub a step for a tool that is not present. This is Loom's freshness-honesty
   doctrine applied to the demo itself.
1. **Clarion** `analyze` → structural graph.
2. **Wardline** `scan` → findings; assert each `expected` finding from the manifest.
3. **Filigree** — file the findings as tracked work; show the dependency/critical path.
4. **Dossier** read for the headline lacuna (Wardline+Clarion in one view).
5. Each **live** matrix cell demonstrated in turn; design-only cells reported as
   "design-only (tool not yet first-class)".
6. Emit a **narrated transcript** plus a **coverage report**: which lacunae were
   demonstrated, which matrix cells were exercised, which were honestly skipped.

`docs/tour.md` and `docs/matrix.md` are generated from a tour run. `make verify`
re-runs the harness in **assert-mode** (fails if any `expected` lacuna is not
surfaced — catching tool drift or an accidentally-removed flaw) and diffs the
regenerated narrative against the committed one (fails if stale). The harness is the
test.

### 4. The re-key — `testo` → `lacuna`

Scripted, reversible (backup is the retained `/home/john/testo`), verified with each
tool's `doctor`. Files that carry the `testo` identity or absolute paths and must be
rewritten:

- **Directory** — work out of `/home/john/lacuna`.
- **Absolute-path configs** — `.mcp.json`, `.filigree.conf`, `clarion.yaml`,
  `wardline.yaml`, `.claude/settings.json` hooks, `.codex/config.toml` +
  `.codex/hooks.json`.
- **Instruction blocks** — `CLAUDE.md`, `AGENTS.md` (regenerated by the tools'
  `install`/`doctor` where possible, rather than hand-edited).
- **Filigree** — re-init clean with project prefix `lacuna`; the canonical demo
  issues are re-planted *from the manifest*, so IDs become `lacuna-…`. The old
  `testo-…` IDs and `INTEGRATION_LOG.md` are retired into a historical doc
  (`docs/history/testo-integration-log.md`), not carried forward as live state.
- **Clarion** — re-analyze under the new path → fresh SEIs.
- **Wardline** — update config, re-scan, re-baseline the planted lacunae.

Verification: `filigree doctor`, `clarion doctor --fix`, `wardline doctor --repair`
all green against the new paths; `mcp_status_get` shows the new project.

### 5. Resulting structure

```
lacuna/
  README.md  AGENTS.md  CLAUDE.md      ← repositioned as the Loom demonstrator
  specimen/                            ← clean-core app + planted, catalogued lacunae
  tour/
    lacunae.toml                       ← the manifest (source of truth)
    tour.py                            ← the harness (tour + assert/verify modes)
  docs/
    tour.md   matrix.md                ← generated from a tour run
    flaws/                             ← per-lacuna pages generated from the manifest
    history/testo-integration-log.md   ← retired sandbox log
    superpowers/specs/                 ← this design + future specs
  Makefile                            ← make tour | make verify | make rekey
  wardline.yaml                       ← planted lacunae baselined/waivered
  .filigree/ .clarion/ .mcp.json ...  ← re-keyed tool state
```

## Work-streams (sequenced in the plan)

1. **Re-key** (`testo` → `lacuna`): paths, configs, hooks, Filigree prefix, Clarion
   re-analyze, Wardline re-scan. *Lands first* — the harness depends on the new paths.
2. **Specimen + manifest**: restructure `sampleapp/` → `specimen/`, plant the
   catalogued lacunae, author `tour/lacunae.toml`, baseline them in `wardline.yaml`.
3. **Harness + narrative**: `tour/tour.py` (tour + verify modes), generated
   `docs/tour.md` / `docs/matrix.md` / `docs/flaws/`, `Makefile` targets.
4. **Positioning docs**: rewrite `README.md` / `AGENTS.md` / `CLAUDE.md` as the
   demonstrator; retire the sandbox log into `docs/history/`.
5. **Verification / CI**: `make verify` as the gate; `wardline scan --fail-on ERROR`
   green via baseline; each tool's `doctor` green.

## Acceptance criteria

- `make tour` runs end-to-end against the specimen, drives every **live** tool, and
  emits a narrated transcript + coverage report.
- `make verify` passes: every manifest `expected` finding is surfaced, and
  `docs/tour.md` matches a fresh harness run.
- `wardline scan . --fail-on ERROR` exits 0 (planted lacunae baselined; no new
  findings).
- `filigree`/`clarion`/`wardline` `doctor` all green against `/home/john/lacuna`;
  Filigree issues carry the `lacuna-` prefix.
- The combination matrix coverage report shows every live cell exercised and every
  design-only cell honestly labelled.
- README/AGENTS/CLAUDE read as a product, not a sandbox.

## Risks & mitigations

- **Absolute-path rewiring is fiddly** (every config hard-codes `/home/john/testo`).
  Mitigation: scripted `make rekey`; `/home/john/testo` retained as rollback; each
  tool's `doctor` is the post-condition check.
- **Tool drift breaks the demo silently.** Mitigation: `make verify` asserts every
  `expected` finding; CI-style gate fails loudly.
- **Legis/Charter not first-class yet.** Mitigation: capability detection +
  degrade-honestly; design-only cells are labelled, never faked.
- **Over-planting flaws makes the core look sloppy** (defeats "clean core").
  Mitigation: every flaw must have a manifest entry justifying it by the tool/cell it
  demonstrates; un-catalogued smells are bugs, not features.

## Non-goals

- Not making the specimen's planted flaws "correct" — they are permanent fixtures.
- Not implementing Legis/Charter functionality — Lacuna consumes them when live and
  degrades honestly when not.
- Not a general SAST/coverage target — Lacuna demonstrates *Loom*, not tools at large.
