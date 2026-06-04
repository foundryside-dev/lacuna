# Plan reality-check — Lacuna repivot (2026-06-05)

Verdict: **Conditional GO.** Phases 0–1 are safe to run after two small fixes.
**Phases 2–3 are a NO-GO as written** — they rest on an inaccurate model of the
live tools, and they *regress* integrations the `testo` log proves already worked.
Insert a "tool-reality spike" before Phase 2 and fold its results into the
manifest, the fixtures, and `tour/steps.py`.

## What the plan gets right (keep)
- Manifest-as-single-source-of-truth; TDD on the pure-logic modules
  (`manifest`/`capability`/`report`/`steps` parsing); honest capability
  degradation; Wardline baseline discipline. The *structure* is sound.
- Re-key phase is the highest-confidence work. `filigree init --name lacuna
  --prefix lacuna` is **confirmed valid**. `clarion doctor --path . --fix` and
  `clarion analyze <path>` are **proven** by `INTEGRATION_LOG.md`.

## Blocking findings (verified against live tools + sources)

1. **`loom-markers` is unpublished.** It lives at
   `/home/john/wardline/packages/loom-markers` (name `loom-markers`, exports
   `external_boundary`/`trust_boundary`/`trusted`). `uv pip install loom-markers`
   fails ("not found in registry"). → Task 0.2 install line and
   `pyproject.dependencies = ["loom-markers"]` both fail as written. Fix: install
   from path (`-e /home/john/wardline/packages/loom-markers`) and reference it as
   a path/editable dep, not a registry name.

2. **Wrong Wardline rule IDs (fabricated).** Real rules:
   - 101 untrusted→trusted — `unsafe_account_key` ✓ correct (confirmed: a bare
     `wardline scan .` emits PY-WL-101 for it).
   - 102 boundary_without_rejection — `non_rejecting_boundary` ✓ plausibly correct.
   - 103 broad_exception — plan says **PY-WL-201**, which **does not exist.**
     Real = 103.
   - 104 silent_exception — plan says **PY-WL-202**, which **does not exist.**
     Real = 104.
   Both 103 and 104 are **tier-modulated** (`severity = modulate(base, tier)`) and
   their `examples_violation` are `@trusted` functions — so an undecorated fixture
   may not fire, or fire only weakly. Fix: correct IDs to 103/104 **and** confirm
   the trigger against a live scan, decorating the fixtures `@trusted` if needed.

   *(Reversed from an earlier draft: `wardline scan .` **does** write
   `findings.jsonl` to cwd by default — verified empirically, PY-WL-101 present —
   so the harness's `wardline_scan()` file-read mechanism is sound. The earlier
   "scan doesn't write the file" claim was wrong.)*

3. **Clarion structural lacunae have no surfacing path.** Clarion's CLI has no
   query/dead/circular/list verb (subcommands: install, analyze, serve, hook, db,
   guidance, doctor, sarif). Dead-code/cycles are exposed via the **MCP server**
   (`clarion serve` → `mcp__clarion__*`) or by reading `.clarion/clarion.db`, not
   via a CLI the harness can shell out to. Task 3.5 Step 3 proposes
   `clarion dead/circular list` — **those verbs do not exist.** Also the coverage
   model only ingests `surfaced_rules` from Wardline, so `clarion_analyze()`
   contributes nothing → `cl-dead-code` / `cl-circular-import` are *always*
   missing → `verify` always fails on them. Needs a real, designed
   `clarion_structure()` source (MCP query or direct DB read) — its own task with
   its own test, not a checkpoint footnote.

## Scope finding (the harness under-asserts a bridge that already fires)
4. `wardline.yaml` already configures `filigree.url` and `clarion.url`, so **every
   `wardline scan` auto-emits findings to Filigree and taint to Clarion** (verified:
   a bare scan reported "emitted 33 finding(s) to …/scan-results"). The
   Wardline→Filigree bridge is therefore *not* regressed — it fires automatically.
   But the plan's harness only **lists** Filigree issues and never *asserts* the
   bridge, so the spec's headline "finding → tracked work" combination is wired yet
   unverified. Two consequences for the plan: (a) Phase 1 re-key must keep the
   dashboard serving that `scan-results` URL (and re-point it if the port/identity
   changes), or scans start failing to emit; (b) add a coverage assertion that the
   PY-WL-101 finding appears as a `lacuna-` Filigree issue, turning an automatic
   side-effect into a demonstrated cell. `INTEGRATION_LOG.md` also records
   `wardline file-finding` and `clarion sarif import` as richer bridges if wanted.

## Minor (recoverable friction)
- `filigree dashboard-stop` is not a verb (only `dashboard`, `ensure-dashboard`);
  guarded by `2>/dev/null` + `pkill`, so non-fatal.
- `clarion install --path .` flag unconfirmed (analyze uses positional PATH +
  `--config`); verify before relying on it.
- `filigree mcp-status` / `--json` global flag unconfirmed against this build.
- `wardline doctor --repair` flag unconfirmed.
- Handover says cwd resets to `/home/john/testo`; observed it resets to
  `/home/john/lacuna`. Absolute paths make this moot, but the note is wrong.

## Recommended revision (before executing Phase 2+)
Root cause: the plan was written against an *assumed* tool model when a *proven*
one already sits in the repo. `INTEGRATION_LOG.md` records the exact working
commands (`wardline findings . --where …`, `wardline scan . --filigree-url …`,
`clarion sarif import …`, `clarion doctor --path … --fix`). Anchor the harness to
those, rather than rediscovering the tools.

Add **Task 1.5 — Tool-reality spike** (after re-key, before planting): against the
live tools, (a) confirm rule IDs/fingerprints from a real `findings.jsonl`;
(b) confirm whether each exception fixture must be `@trusted` to fire, and at what
severity; (c) determine the Clarion dead/cycle surface (MCP query vs reading
`.clarion/clarion.db`) and prototype the parse — there is **no** dead/cycle CLI
verb; (d) decide whether to assert the already-wired Filigree bridge. Feed results
into the manifest (Task 2.6), the fixtures (2.3/2.4), and `tour/steps.py` (3.4).
Then Phases 2–3 execute against verified reality instead of an assumed model.
