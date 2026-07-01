---
# Plainweave Coverage Lacunae Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** Plant three NOT-A-FLAW plainweave capability-depth lacunae (`pw-baseline-drift`, `pw-verification-status`, `pw-requirement-dossier`) that each assert plainweave's no-silent-clean invariant over its baseline / verification / dossier surfaces, raising the catalogued corpus from 62 to 65.

**Architecture:** One new capability-gated tour leg (`tour/steps.py::plainweave_coverage`) self-seeds an isolated, offline plainweave store, mutates it (baseline lock + one supersede + verify methods/evidence), reads the three CLI surfaces over their `--json` envelopes, and emits up to three `(rule_token, qualname)` `surfaced` pairs — one per cell, each gated by a load-bearing conjunction (mirrors the multi-pair `plainweave_intent` leg, NOT the single-pair peer-facts legs). Three new per-subcommand capabilities (`tour/capability.py`) gate the leg and the three lacunae out of `make verify` when the surface is absent.

**Tech Stack:** Python 3, pytest with `monkeypatch` dependency injection, TOML manifest, plainweave 1.2.0 CLI (subprocess `--json` seam), Makefile-driven `make tour` / `make verify` lockstep gate.

## Global Constraints
- **plainweave version posture:** the local editable install is 1.2.0; the merge gate resolves plainweave BIN-first from `/home/john/.local/bin/plainweave` (1.2.0) with NO CI version pin — so the gate exercises whatever is installed. Reference the REAL 1.2.0 surface.
- **Capability-gating is BEHAVIOUR-probed:** gate on the `plainweave --help` argparse choices block (`capability.plainweave_subcommands`), never on a version string (the stale-build trap).
- **No-silent-clean invariant:** every cell emits its `surfaced` pair ONLY when ALL conjuncts of its honest-state assertion hold; a collapsed/absent state drops the pair → the lacuna lands in `missing_ids` → `make verify` reds (fail loud, no partial credit).
- **Determinism:** `StepResult.detail` is FROZEN prose with NO digits; all live/variable data (ids, counts) rides the non-rendered `note`; no wall-clock, no hardcoded hex; SEIs/req-ids resolved at seed time.
- **Advisory / local / never-gates:** plainweave never gates; these cells assert capability correctness only.
- **Byte-stable `tour.md`:** `render_tour_md` writes only `detail`; `run_verify` byte-compares the committed `docs/tour.md`/`docs/matrix.md` against a fresh render.
- **Consumer boundary:** ZERO changes to plainweave itself — Lacuna only consumes the installed binary.
- **`[N/A]` honesty (DIVERGENCE — read Task 1 note):** the committed `_HELP_1_0_0` fixture shows `baseline`/`verify`/`status`/`dossier` are present in plainweave 1.0.0, so unlike the peer-facts subcommands these do NOT vanish under 1.0.0. The `[N/A]` path is reachable only when the surface is genuinely absent (stripped/pre-baseline build), which the tests simulate via an empty `--help` surface. Gated `detail` and manifest `explanation` MUST NOT claim "absent in PyPI 1.0.0".
---

## File Structure

| File | Created/Modified | Responsibility |
|---|---|---|
| `tour/capability.py` | Modify | Add `PLAINWEAVE_COVERAGE_SUBCOMMANDS` map + a parallel `detect()` loop emitting `plainweave-baseline` / `plainweave-verify` / `plainweave-dossier` capabilities probed from the live surface. |
| `tour/plainweave_seed.py` | Modify | Change `seed()` to capture all three `justify()` req-ids and return a `{locator: req_id}` map (non-breaking; existing callers ignore it). |
| `tour/steps.py` | Modify | Add the `plainweave_coverage()` leg + two frozen module constants. |
| `tour/__main__.py` | Modify | Register `steps.plainweave_coverage()` in `_drive()` after the peer-facts legs. |
| `tour/lacunae.toml` | Modify | 3 new `[[lacuna]]` entries + a section-comment header, inserted after `pw-wardline-peer-facts` (line 617) and before the mcp-attach header (line 619). |
| `tests/test_capability.py` | Modify | Cases for the 3 coverage capabilities (present → available; simulated-absent → `[N/A]` + machine-readable detail). |
| `tests/test_steps_plainweave_coverage.py` | Create | Unit tests for the leg: happy-path, degrade-not-raise, capability-gated, and 12 per-conjunct drop-tests. |
| `tests/test_steps_plainweave_coverage_integration.py` | Create | Real-producer integration smoke (spec §8.4), `@pytest.mark.integration` (deselected in unit-only CI): seeds a real workspace, runs the actual `plainweave baseline/verify/status/dossier`, pins the predicate-keyed envelope fields. |
| `tests/test_steps_plainweave_seed.py` | Create | Direct test that `seed()` returns the `{locator: req_id}` map via a fake `pw` (default + `with_trace_links` paths). |
| `pyproject.toml` | Modify | Register the `integration` pytest marker + deselect it by default (`addopts = "-q -m 'not integration'"`). |
| `tests/test_manifest.py` | Modify | Bump count `62 → 65`; add the 3 new ids to the membership block. |
| `tests/test_drive.py` | Modify | Assert the new leg is present in `_drive()` results. |
| `docs/tour.md`, `docs/matrix.md`, `docs/flaws/pw-*.md` | Regenerated | Produced by `make tour` (docs/flaws are GENERATED from the manifest — never hand-authored). |

---

### Task 0: Establish a clean-tree `make verify` baseline

**Files:** Modify (commit) `AGENTS.md`, `CLAUDE.md` if dirty. No test files.
**Interfaces:** Produces nothing consumed by later tasks — this is a precondition gate.

Context: the working tree shows `AGENTS.md` + `CLAUDE.md` modified — the legis session-start instruction-block re-stamp (documented friction, NOT plan work). `make verify` has no explicit `git status` check, but the `legis_govern` leg runs `wardline scan . --format legis`, wardline REFUSES to sign a dirty tree, so `legis_govern` returns `[WARN]` with a dirty-tree detail that differs byte-for-byte from the committed `## [PASS] legis govern` line → `run_verify` fails with `docs/tour.md is stale`. The tree must be clean before baselining.

- [ ] **Step 1: Inspect the dirty files.**
  Command: `git -C /home/john/lacuna status --porcelain && git -C /home/john/lacuna diff -- AGENTS.md CLAUDE.md | head -80`
  Expected: only `AGENTS.md` and `CLAUDE.md` modified; the diff shows the legis/wardline instruction blocks re-stamped. Confirm there is no plan-unrelated content.

- [ ] **Step 2: Absorb the re-stamp onto the feature branch.**
  Command: `git -C /home/john/lacuna add AGENTS.md CLAUDE.md && git -C /home/john/lacuna commit -m "chore(tour): absorb legis instruction-block re-stamp (clean-tree precondition)
Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"`
  Expected: commit succeeds; `git status` is now clean.

- [ ] **Step 3: Record the §10 narrative-bless condition under local plainweave 1.2.0.**
  Command: `cd /home/john/lacuna && make verify`
  Expected — ONE of two outcomes, RECORD which in the task's completion note:
  - `VERIFY OK` → the committed `docs/tour.md` already agrees with local 1.2.0; proceed.
  - `docs/tour.md is stale` (NOT a legis dirty-tree line) → the pre-existing §10 condition (committed bless was against a plainweave whose surface differs from local 1.2.0). **This resolves the pre-existing §10 divergence.** Spec §10 deferred it, but a green `make verify` baseline is a prerequisite — a failing `make verify` before adding cells makes pre-existing failures indistinguishable from new ones. Confirm with the spec owner; consider a separate commit/PR before the feature branch. Run `cd /home/john/lacuna && make tour` ONCE to re-bless `docs/tour.md`/`docs/matrix.md` to the local exercised state, commit it (`git add docs/tour.md docs/matrix.md docs/flaws && git commit -m "docs(tour): re-bless narrative to local plainweave 1.2.0 (PDR-0016 §10)"`), and re-run `make verify` → `VERIFY OK`. This establishes the clean green baseline the rest of the plan builds on.

- [ ] **Step 4: Confirm the baseline is green.**
  Command: `cd /home/john/lacuna && git status --porcelain && make verify`
  Expected: clean tree, `VERIFY OK`.

---

### Task 1: Add the three per-subcommand coverage capabilities

**Files:**
- Modify `tour/capability.py` (insert after line 40, the `WARPLINE_PEER_FACT_OPTIONS` dict; new `detect()` loop after line 156, the peer-facts loop).
- Test `tests/test_capability.py`.

**Interfaces:**
- Consumes: `detect(which, pw_subcommands, wp_reverify_options) -> list[Capability]`, `Capability(name: str, available: bool, detail: str)`, `_extract_subcommand_choices`.
- Produces: module constant `PLAINWEAVE_COVERAGE_SUBCOMMANDS: dict[str, str]` and three `Capability` rows named `"plainweave-baseline"`, `"plainweave-verify"`, `"plainweave-dossier"` whose `available` is `(subcommand in surface)`. These names become the three lacunae's `expected_tool` (Task 5) and the leg's verify-side gate.

> **DIVERGENCE NOTE (load-bearing):** `tests/test_capability.py` line 8-12 pins `_HELP_1_0_0` whose argparse choices block already contains `baseline,…,verify,status,dossier`. So these subcommands exist in 1.0.0 and the caps read `available` under BOTH 1.0.0 and 1.2.0. We implement spec §4 literally (gate on `baseline`/`verify`/`dossier`) — do NOT redesign to a narrower 1.2.0-only probe; that is design drift past the approved spec. The absent-branch `detail` MUST NOT claim "absent in PyPI 1.0.0" (that is false for these three). The `[N/A]` path is tested via a simulated EMPTY surface, not a real 1.0.0.

- [ ] **Step 1: Write the failing test for the present surface.**
  Append to `tests/test_capability.py`:
  ```python
  # ── Per-subcommand COVERAGE capabilities (plainweave baseline/verify/dossier) ──
  # baseline/verify/dossier ship in plainweave's BASE surface (present in 1.0.0 per
  # _HELP_1_0_0), so these caps read available on any plainweave that exposes them.
  # The [N/A] path is exercised below via a SIMULATED empty surface, not a real 1.0.0.


  def test_coverage_caps_live_when_surface_present():
      caps = {c.name: c for c in detect(
          _fake_which(_FULL),
          pw_subcommands=lambda path: frozenset(
              {"intent", "baseline", "verify", "status", "dossier"}
          ),
      )}
      assert caps["plainweave-baseline"].available is True
      assert caps["plainweave-verify"].available is True
      assert caps["plainweave-dossier"].available is True
  ```
  Command: `cd /home/john/lacuna && .venv/bin/python -m pytest tests/test_capability.py::test_coverage_caps_live_when_surface_present -q`
  Expected FAIL: `KeyError: 'plainweave-baseline'`.

- [ ] **Step 2: Add the map and the detect() loop (minimal impl).**
  In `tour/capability.py`, after line 40 (the closing `}` of `WARPLINE_PEER_FACT_OPTIONS`) insert:
  ```python

  # Per-subcommand plainweave COVERAGE capabilities (coverage-lacunae, spec §4). These
  # gate each coverage cell on its base subcommand. NOTE: baseline/verify/status/dossier
  # ship in plainweave's BASE surface (present in 1.0.0), so these light up on any
  # plainweave that exposes the subcommand — the [N/A] path is reached only when the
  # surface is genuinely absent (a stripped/pre-baseline build). Maps subcommand ->
  # capability name (a lacuna's `expected_tool`).
  PLAINWEAVE_COVERAGE_SUBCOMMANDS = {
      "baseline": "plainweave-baseline",
      "verify": "plainweave-verify",
      "dossier": "plainweave-dossier",
  }
  ```
  Then, in `detect()`, immediately after the peer-facts loop (after line 156, the `)` closing the `caps.append(...)` of the `PLAINWEAVE_PEER_FACT_SUBCOMMANDS` loop) insert — reusing the already-computed `surface`:
  ```python
      # Per-subcommand coverage capabilities, probed from the same plainweave surface.
      # Absent surface (stripped/pre-baseline build) -> cap UNAVAILABLE with a
      # machine-readable reason, so the coverage lacunae are gated out of verify's
      # coverage assertion rather than reported as a failed surface.
      for sub, cap_name in PLAINWEAVE_COVERAGE_SUBCOMMANDS.items():
          present = sub in surface
          caps.append(
              Capability(
                  name=cap_name,
                  available=present,
                  detail=(
                      (plainweave_path or "plainweave")
                      if present
                      else f"plainweave `{sub}` CLI surface absent"
                  ),
              )
          )
  ```
  Command: `cd /home/john/lacuna && .venv/bin/python -m pytest tests/test_capability.py::test_coverage_caps_live_when_surface_present -q`
  Expected: `1 passed`.

- [ ] **Step 3: Write the failing test for the absent (simulated) surface.**
  Append to `tests/test_capability.py`:
  ```python
  def test_coverage_caps_unavailable_when_surface_absent():
      # plainweave binary present, but the base subcommands are NOT in the (simulated)
      # surface — a stripped/pre-baseline build. Caps must read UNAVAILABLE with a
      # machine-readable reason, NOT a silent-empty. (No "1.0.0" claim: these ship in 1.0.0.)
      caps = {c.name: c for c in detect(
          _fake_which(_FULL),
          pw_subcommands=lambda path: frozenset({"intent", "req", "trace"}),
      )}
      assert caps["plainweave"].available is True          # the binary IS present
      assert caps["plainweave-baseline"].available is False
      assert caps["plainweave-verify"].available is False
      assert caps["plainweave-dossier"].available is False
      assert "baseline" in caps["plainweave-baseline"].detail
      assert "absent" in caps["plainweave-baseline"].detail


  def test_coverage_caps_gate_per_subcommand_not_combined():
      # Mirrors test_peer_facts_caps_gate_per_subcommand_not_combined: a PARTIAL plainweave
      # release exposing only `baseline` (not verify/dossier) must light up EXACTLY
      # `plainweave-baseline` and gate the other two — proving the three coverage caps are
      # probed per-subcommand, never conflated across PLAINWEAVE_COVERAGE_SUBCOMMANDS.
      caps = {c.name: c for c in detect(
          _fake_which(_FULL),
          pw_subcommands=lambda path: frozenset({"baseline"}),
      )}
      assert caps["plainweave-baseline"].available is True
      assert caps["plainweave-verify"].available is False
      assert caps["plainweave-dossier"].available is False
  ```
  Command: `cd /home/john/lacuna && .venv/bin/python -m pytest tests/test_capability.py -k coverage_caps -q`
  Expected: `2 passed` (the absent-surface + per-subcommand tests; the impl from Step 2 already satisfies both).

- [ ] **Step 4: Pin the 1.0.0 divergence, run the whole capability suite, commit.**
  First pin the load-bearing DIVERGENCE NOTE with a test, so a future `_HELP_1_0_0` fixture change cannot silently invalidate it. In `tests/test_capability.py`, in the existing `test_extract_choices_pins_real_1_0_0_surface_excludes_peer_facts` (line 157, which already binds `subs = _extract_subcommand_choices(_HELP_1_0_0)`), append:
  ```python
      # Divergence pin (coverage-lacunae): baseline/verify/status/dossier DO ship in 1.0.0
      # (UNLIKE the peer-facts subcommands above) — so the coverage caps read available
      # under 1.0.0 too, and the [N/A] path is reachable only via a genuinely-absent surface.
      assert {"baseline", "verify", "status", "dossier"} <= subs
  ```
  Command: `cd /home/john/lacuna && .venv/bin/python -m pytest tests/test_capability.py -q`
  Expected: all pass (existing peer-facts/warpline cases unaffected; 3 new coverage-cap tests + the augmented 1.0.0 pin pass).
  Command: `git -C /home/john/lacuna add tour/capability.py tests/test_capability.py && git -C /home/john/lacuna commit -m "feat(capability): per-subcommand plainweave coverage caps (baseline/verify/dossier)
Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"`

---

### Task 2: Make `seed()` return the `{locator: req_id}` map

**Files:**
- Modify `tour/plainweave_seed.py` (the `seed()` body, lines 98-128, and its return annotation line 58).
- Test `tests/test_steps_plainweave_seed.py` (create).

**Interfaces:**
- Consumes: `seed(pw, *, deprecate=True, with_trace_links=False, root=ROOT)`; the inner `justify(loc, title, statement) -> str`; module constants `ADD_BOOK`, `CLI_MAIN`, `REGISTER`, `TOUR_MAIN`, `ACTOR`.
- Produces: `seed(...) -> dict[str, str]` mapping each justified locator (`ADD_BOOK`, `CLI_MAIN`, `REGISTER`) to its req-id (the `req add` `["id"]`). Existing callers (`steps.py:935`, `steps.py:1043`) ignore the return — non-breaking. The leg (Task 3) consumes this map.

- [ ] **Step 1: Write the failing test.**
  Create `tests/test_steps_plainweave_seed.py`:
  ```python
  """Direct test that plainweave_seed.seed returns the {locator: req_id} map.

  Drives seed() with a fake `pw` closure (no real plainweave) returning canned
  envelopes for the calls seed makes; asserts the three justified req-ids come back.
  """

  from tour import plainweave_seed
  from tour.plainweave_seed import ADD_BOOK, CLI_MAIN, REGISTER, TOUR_MAIN


  def _fake_pw():
      state = {"n": 0}
      surfaces = [
          {"locator": ADD_BOOK, "sei": "sei-a"},
          {"locator": REGISTER, "sei": "sei-r"},
          {"locator": CLI_MAIN, "sei": "sei-c"},
          {"locator": TOUR_MAIN, "sei": "sei-t"},
      ]

      def pw(args):
          if args[:2] == ["intent", "coverage"]:
              return {"justified": surfaces, "unjustified": []}
          if args[:2] == ["goal", "add"]:
              return {"id": "GOAL-1"}
          if args[:2] == ["req", "add"]:
              state["n"] += 1
              return {"id": f"REQ-{state['n']}"}
          return {}

      return pw


  def _fake_pw_with_trace():
      # Like _fake_pw but also answers the `trace propose`/`trace accept` calls the
      # with_trace_links=True branch makes — the coverage leg (Task 3) calls
      # seed(..., with_trace_links=True), and the dossier_trace conjunct depends on this
      # branch, so it needs direct unit coverage (the leg test mocks `seed` wholesale).
      state = {"n": 0, "link": 0}
      surfaces = [
          {"locator": ADD_BOOK, "sei": "sei-a"},
          {"locator": REGISTER, "sei": "sei-r"},
          {"locator": CLI_MAIN, "sei": "sei-c"},
          {"locator": TOUR_MAIN, "sei": "sei-t"},
      ]

      def pw(args):
          if args[:2] == ["intent", "coverage"]:
              return {"justified": surfaces, "unjustified": []}
          if args[:2] == ["goal", "add"]:
              return {"id": "GOAL-1"}
          if args[:2] == ["req", "add"]:
              state["n"] += 1
              return {"id": f"REQ-{state['n']}"}
          if args[:2] == ["trace", "propose"]:
              state["link"] += 1
              return {"id": f"LINK-{state['link']}"}
          if args[:2] == ["trace", "accept"]:
              return {}
          return {}

      return pw


  def test_seed_returns_locator_to_req_id_map(tmp_path):
      m = plainweave_seed.seed(_fake_pw(), root=tmp_path)
      # justify() is called for ADD_BOOK, CLI_MAIN, REGISTER in that order.
      assert m == {ADD_BOOK: "REQ-1", CLI_MAIN: "REQ-2", REGISTER: "REQ-3"}


  def test_seed_returns_map_with_trace_links(tmp_path):
      # with_trace_links=True must drive the trace propose/accept branch without KeyError
      # and return the SAME {locator: req_id} map (trace links don't change the contract).
      m = plainweave_seed.seed(_fake_pw_with_trace(), with_trace_links=True, root=tmp_path)
      assert m == {ADD_BOOK: "REQ-1", CLI_MAIN: "REQ-2", REGISTER: "REQ-3"}
  ```
  Command: `cd /home/john/lacuna && .venv/bin/python -m pytest tests/test_steps_plainweave_seed.py -q`
  Expected FAIL: both fail with `assert None == {...}` (seed currently returns `None`).

- [ ] **Step 2: Change the return annotation.**
  In `tour/plainweave_seed.py` line 58, change `) -> None:` to `) -> dict[str, str]:`.
  (Docstring lines 59-76 stay; the contract addition is the return.)

- [ ] **Step 3: Capture all three req-ids and return the map.**
  Replace the body from line 114 (`# COVERED (2 justified surfaces): ...`) through line 128 (the `catalog record` call) with:
  ```python
      # COVERED (2 justified surfaces): the healthy half of the mix. Capture every
      # req-id into a {locator: req_id} map so the coverage leg can thread baseline /
      # verification / dossier setup onto specific requirements (non-breaking: the
      # intent + enrichment legs ignore this return).
      reqs: dict[str, str] = {}
      reqs[ADD_BOOK] = justify(ADD_BOOK, "Add-a-book command", "The CLI can add a book to the catalog.")
      reqs[CLI_MAIN] = justify(CLI_MAIN, "Library CLI entry point", "The app exposes a single CLI entry point.")

      # UNCOVERED #1 — liveness: bound + laddered, then the requirement is DEPRECATED,
      # so the surface drops out of the north-star numerator (a dead obligation must
      # not inflate honest coverage).
      reqs[REGISTER] = justify(REGISTER, "Register command (legacy)", "The CLI can register an account.")
      if deprecate:
          pw(["req", "deprecate", reqs[REGISTER], "--expected-version", "1", "--actor", ACTOR])

      # UNCOVERED #2 — orphan: record the tour entry-point as a PUBLIC code entity with
      # no requirement, so `intent orphans code` surfaces it. entity_id is the SEI
      # (positional), NOT the locator, so it matches entity_associations.
      pw(["catalog", "record", locmap[TOUR_MAIN], "--entity-kind", "loomweave_entity", "--actor", ACTOR])
      return reqs
  ```
  Command: `cd /home/john/lacuna && .venv/bin/python -m pytest tests/test_steps_plainweave_seed.py -q`
  Expected: `2 passed` (default path + trace-links path).

- [ ] **Step 4: Confirm existing seed-consuming leg tests still pass + commit.**
  Command: `cd /home/john/lacuna && .venv/bin/python -m pytest tests/test_steps_plainweave.py tests/test_steps_plainweave_peerfacts.py tests/test_steps_plainweave_seed.py -q`
  Expected: all pass (the intent/enrichment leg tests mock `seed`; the return change is invisible to them).
  Command: `git -C /home/john/lacuna add tour/plainweave_seed.py tests/test_steps_plainweave_seed.py && git -C /home/john/lacuna commit -m "feat(seed): return {locator: req_id} map from plainweave_seed.seed (non-breaking)
Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"`

---

### Task 3: Add the `plainweave_coverage()` leg + full unit tests

**Files:**
- Modify `tour/steps.py` (three module constants near line 859; the leg after `plainweave_wardline_peer_facts` ends — after line ~1155).
- Test `tests/test_steps_plainweave_coverage.py` (create).
- Test `tests/test_steps_plainweave_coverage_integration.py` (create — Step 10, real-producer smoke).
- Modify `pyproject.toml` (register + deselect the `integration` marker — Step 10).

**Interfaces:**
- Consumes: `_plainweave_json(args, cwd=ROOT) -> dict | None`; `_plainweave_supports(subcommand: str) -> bool`; `_tool(name)`; `plainweave_seed.materialize_workspace() -> Path`; `plainweave_seed.seed(...) -> dict[str, str]` (Task 2); `plainweave_seed.{ADD_BOOK,CLI_MAIN,REGISTER,ACTOR}`; `StepResult(name, ok, detail, surfaced=(), note="", available=True)`; frozen anchors `PLAINWEAVE_ADD_BOOK`/`PLAINWEAVE_REGISTER`/`PLAINWEAVE_CLI_MAIN` (steps.py:847-849); `shutil`.
- Produces: `plainweave_coverage() -> StepResult` with `name="plainweave coverage"`, emitting up to three pairs: `("pw-baseline-drift","specimen.cli._add_book")`, `("pw-verification-status","specimen.cli._register")`, `("pw-requirement-dossier","specimen.cli.main")`; `ok = len(pairs) == 3`. Consumed by Task 4 (drive registration) and Task 5 (manifest coverage match).

**Conjunct map (the no-silent-clean assertions — each is a drop-test in Step 8+):**
- `pw-baseline-drift` (3): `drift_flagged` (superseded req shows `superseded_since_baseline`), `control_unchanged` (untouched req shows `unchanged`), `no_baseline_honest` (spec §3.1: `baseline diff` of a NEVER-created baseline id, run BEFORE `baseline create`, reports an honest `ok=False` NOT_FOUND envelope — or `ok=True` with empty `items` — never a silent "clean / no drift". Verified against real plainweave 1.2.0: `baseline diff <bogus>` in a store with no locked baseline returns `ok=False` code `NOT_FOUND`. `baseline diff` requires a `baseline_id` positional, so the no-baseline state is probed by diffing a frozen never-created id, NOT by `baseline list`).
- `pw-verification-status` (5): `satisfied` (`status=="satisfied"` + reason `passing_evidence`), `unverified` (`status=="unverified"`, never silently satisfied), `unverified_listed` (`status unverified` lists it), `stale_status` (`status=="stale"` after supersede), `stale_listed` (`status stale` lists it).
- `pw-requirement-dossier` (4): `dossier_verification` (`verification.status=="satisfied"`), `dossier_baseline_current` (a `baseline_exposure` item `state=="current"`), `dossier_trace` (`traces.incoming` non-empty), `unknown_honest` (unknown id → non-ok/None envelope, never empty-as-clean).

> **SETUP ORDERING (load-bearing — do not reorder):** `_add_book` does double duty (baseline-drift target AND stale-evidence target). The single supersede must run AFTER both `verify evidence record` (so the v1 passing evidence becomes stale at v2) AND `baseline create` (so the baseline locks v1 and the diff shows drift). Order: (1) seed; (2) verify method+passing evidence on `_add_book` and `cli.main`, method-only on `_register`; (3) `baseline diff <PLAINWEAVE_COVERAGE_BOGUS_BASELINE>` (no-baseline arm — honest `ok=False` NOT_FOUND, NOT a silent clean; because this read is LEGITIMATELY `ok=False`, it is EXCLUDED from the strict read-ok loop that raises on the other reads); (4) `baseline create`; (5) `req supersede _add_book → v2`; (6) all reads. NOTE on terminology (G6): plainweave has NO `"verified"` status string — the verified state is `status=="satisfied"` + reason `passing_evidence`. Keying on `"verified"` would silently never fire.

> **Capability gate:** `baseline`/`verify`/`dossier` are co-present in any real plainweave (all in 1.0.0 + 1.2.0), so the leg gates on all three but in practice they go available/absent together (documented co-presence). The leg renders `[N/A]` (`available=False`) only when the surface is genuinely absent.

- [ ] **Step 1: Add the two frozen module constants.**
  In `tour/steps.py`, after line 859 (`PLAINWEAVE_WARDLINE_ACTIVE = ...`) insert:
  ```python
  # Coverage-depth demos (pw-baseline-drift / pw-verification-status / pw-requirement-dossier).
  PLAINWEAVE_COVERAGE_BASELINE = "lacuna-coverage-lock"   # frozen baseline name (no wall-clock)
  PLAINWEAVE_COVERAGE_BOGUS_REQ = "REQ-lacuna-9999"       # never-seeded id (unknown-dossier negative)
  PLAINWEAVE_COVERAGE_BOGUS_BASELINE = "BASELINE-lacuna-9999"  # never-created id (no-baseline negative)
  ```

- [ ] **Step 2: Write the failing happy-path test (with the full test harness).**
  Create `tests/test_steps_plainweave_coverage.py`:
  ```python
  """Tests for the plainweave_coverage tour leg (baseline / verification / dossier).

  The single mockable seam is steps._plainweave_json; the leg self-seeds via
  steps.plainweave_seed.seed (mocked to return a canned {locator: req_id} map) in a
  workspace from steps.plainweave_seed.materialize_workspace (mocked to a fixed Path).

  The leg is MULTI-PAIR (emits up to 3 pairs, ok = len==3, like plainweave_intent), so a
  per-conjunct drop-test asserts the SPECIFIC pair is gone and the OTHER two remain — NOT
  `surfaced == ()` (that single-pair shape from the peer-facts tests would falsely fail here).
  """

  from pathlib import Path

  from tour import steps
  from tour.plainweave_seed import ADD_BOOK, CLI_MAIN, REGISTER

  _WS = Path("/tmp/pw-coverage-ws")
  ADD_BOOK_ID = "REQ-lacuna-0001"
  CLI_MAIN_ID = "REQ-lacuna-0002"
  REGISTER_ID = "REQ-lacuna-0003"
  BASELINE_ID = "BASELINE-0001"

  BASELINE_PAIR = ("pw-baseline-drift", "specimen.cli._add_book")
  VERIFY_PAIR = ("pw-verification-status", "specimen.cli._register")
  DOSSIER_PAIR = ("pw-requirement-dossier", "specimen.cli.main")


  def _diff_env(drift_flagged=True, control_unchanged=True):
      return {"ok": True, "data": {"baseline_id": BASELINE_ID, "summary": {
          "unchanged": 2, "changed": 0, "missing_current": 0,
          "new_since_baseline": 0, "superseded_since_baseline": 1 if drift_flagged else 0},
          "items": [
              {"id": ADD_BOOK_ID, "requirement_id": "req-1",
               "status": "superseded_since_baseline" if drift_flagged else "unchanged"},
              {"id": CLI_MAIN_ID, "requirement_id": "req-2",
               "status": "unchanged" if control_unchanged else "superseded_since_baseline"},
          ]}}


  def _list_env(items):
      return {"ok": True, "data": {"items": items, "has_more": False, "next_offset": None}}


  def _status_env(rid, status, reason):
      return {"ok": True, "data": {
          "requirement_id": "req-x", "id": rid, "current_version": 1, "status": status,
          "reasons": [{"code": reason, "message": "m", "evidence_id": None}],
          "current_evidence": [], "stale_evidence": []}}


  def _dossier_env(verification_ok=True, baseline_current=True, trace_present=True):
      return {"ok": True, "data": {
          "identity": {"id": CLI_MAIN_ID, "requirement_id": "req-2",
                       "stable_id": "plainweave:req:lacuna:0002", "current_version": 1},
          "verification": {"status": "satisfied" if verification_ok else "unverified",
                           "reasons": [{"code": "passing_evidence", "evidence_id": "EVID-0001"}],
                           "current_evidence": [], "stale_evidence": []},
          "baseline_exposure": {"summary": {"current": 1}, "items": (
              [{"baseline_id": BASELINE_ID, "state": "current"}] if baseline_current else [])},
          "traces": {"incoming": ([{"id": "LINK-0001", "state": "accepted"}]
                                  if trace_present else []), "outgoing": []},
          "acceptance_criteria": {"current_version": [], "active_draft": []},
          "computed_gaps": [], "next_actions": [],
          "peer_facts": {"live_peer_calls": False, "sources": ["loomweave"]}}}


  def _arm_coverage(
      monkeypatch, *,
      baseline_drift_flagged=True, baseline_control_unchanged=True, no_baseline_honest=True,
      verify_satisfied=True, verify_unverified=True, unverified_listed=True,
      verify_stale=True, stale_listed=True,
      dossier_verification_ok=True, dossier_baseline_current=True, dossier_trace_present=True,
      dossier_unknown_honest=True,
  ):
      monkeypatch.setattr(steps, "_tool", lambda name: f"/home/john/.local/bin/{name}")
      monkeypatch.setattr(steps, "_plainweave_supports", lambda sub: True)
      monkeypatch.setattr(steps.plainweave_seed, "materialize_workspace", lambda: _WS)
      monkeypatch.setattr(steps.plainweave_seed, "seed",
                          lambda pw, **kw: {ADD_BOOK: ADD_BOOK_ID, CLI_MAIN: CLI_MAIN_ID, REGISTER: REGISTER_ID})

      def pwj(args, cwd=None):
          # ── setup calls (return handle envelopes the leg threads forward) ──
          if args[:2] == ["baseline", "create"]:
              return {"ok": True, "data": {"id": BASELINE_ID}}
          if args[:3] == ["verify", "method", "add"]:
              return {"ok": True, "data": {"id": "VERM-0001"}}
          if args[:3] == ["verify", "evidence", "record"]:
              return {"ok": True, "data": {"id": "EVID-0001"}}
          if args[:2] == ["req", "supersede"]:
              return {"ok": True, "data": {"id": args[2]}}
          # ── reads ──
          if args[:2] == ["baseline", "diff"]:
              if args[2] == steps.PLAINWEAVE_COVERAGE_BOGUS_BASELINE:
                  # no-baseline arm (run BEFORE create). Honest: ok=False NOT_FOUND (real
                  # plainweave 1.2.0). Dishonest knob: a silent clean (ok=True with a
                  # populated/unchanged diff) that the conjunct must REFUSE to credit.
                  if no_baseline_honest:
                      return {"ok": False, "error": {"code": "NOT_FOUND", "message": "baseline not found"}}
                  return {"ok": True, "data": {"baseline_id": BASELINE_ID, "summary": {},
                                               "items": [{"id": ADD_BOOK_ID, "status": "unchanged"}]}}
              return _diff_env(baseline_drift_flagged, baseline_control_unchanged)
          if args[:2] == ["verify", "status"]:
              rid = args[2]
              if rid == CLI_MAIN_ID:
                  return _status_env(rid, "satisfied" if verify_satisfied else "unverified",
                                     "passing_evidence" if verify_satisfied else "no_current_evidence")
              if rid == REGISTER_ID:
                  return _status_env(rid, "unverified" if verify_unverified else "satisfied",
                                     "no_current_evidence" if verify_unverified else "passing_evidence")
              if rid == ADD_BOOK_ID:
                  return _status_env(rid, "stale" if verify_stale else "satisfied",
                                     "stale_evidence" if verify_stale else "passing_evidence")
          if args[:2] == ["status", "unverified"]:
              return _list_env([{"id": REGISTER_ID}] if unverified_listed else [])
          if args[:2] == ["status", "stale"]:
              return _list_env([{"id": ADD_BOOK_ID}] if stale_listed else [])
          if args[:1] == ["dossier"]:
              if args[1] == steps.PLAINWEAVE_COVERAGE_BOGUS_REQ:
                  if dossier_unknown_honest:
                      return {"ok": False, "error": {"code": "NOT_FOUND", "message": "x"}}
                  return {"ok": True, "data": {"identity": {}, "verification": {}}}
              return _dossier_env(dossier_verification_ok, dossier_baseline_current, dossier_trace_present)
          return {"ok": True, "data": {}}

      monkeypatch.setattr(steps, "_plainweave_json", pwj)


  def test_coverage_surfaces_all_three_pairs_on_full_scenario(monkeypatch):
      _arm_coverage(monkeypatch)
      r = steps.plainweave_coverage()
      assert r.name == "plainweave coverage"
      assert r.ok is True
      assert set(r.surfaced) == {BASELINE_PAIR, VERIFY_PAIR, DOSSIER_PAIR}
      assert len(r.surfaced) == 3
  ```
  Command: `cd /home/john/lacuna && .venv/bin/python -m pytest tests/test_steps_plainweave_coverage.py::test_coverage_surfaces_all_three_pairs_on_full_scenario -q`
  Expected FAIL: `AttributeError: module 'tour.steps' has no attribute 'plainweave_coverage'`.

- [ ] **Step 3: Implement the leg (minimal — full predicate logic).**
  In `tour/steps.py`, after the `plainweave_wardline_peer_facts` leg ends, insert:
  ```python
  def plainweave_coverage() -> StepResult:
      """plainweave capability-depth: baseline / verification / dossier, no-silent-clean.

      Seeds the covered+uncovered corpus in an isolated offline workspace, then exercises
      three plainweave surfaces over their --json envelopes:
        * pw-baseline-drift     — lock a baseline, supersede one approved requirement ->
          `baseline diff` reports it as drift; an untouched requirement stays unchanged;
          and in a store with no locked baseline, diffing a baseline reports honestly
          (a NOT_FOUND error) rather than a silent clean.
        * pw-verification-status — a requirement with a method AND passing evidence reports
          `satisfied`; one with a method but NO evidence reports `unverified` (never
          silently satisfied) and is listed by `status unverified`; orphaned evidence
          reports `stale` and is listed by `status stale`.
        * pw-requirement-dossier — `dossier <known>` is coherent (satisfied verification,
          current baseline member, an incoming trace); `dossier <unknown>` reports an honest
          error (never an empty-as-clean dossier).

      Determinism (`make verify` is byte-for-byte): `detail` is FROZEN prose with no digits;
      live ids/counts ride the non-rendered `note`. Capability-gated; never raises (tour
      contract). _add_book does double duty (drift + stale): the single supersede AFTER
      lock+evidence produces both.
      """
      name = "plainweave coverage"
      if not (
          _plainweave_supports("baseline")
          and _plainweave_supports("verify")
          and _plainweave_supports("dossier")
      ):
          return StepResult(
              name, ok=False, available=False,
              detail=(
                  "capability-gated — the installed plainweave does not expose the "
                  "`baseline`/`verify`/`dossier` CLI surface. These plainweave coverage "
                  "cells are intentionally not exercised when the surface is absent (a "
                  "stripped or pre-baseline build) — install a plainweave carrying the "
                  "subcommands to light them up; advisory, local-only, never gates"
              ),
          )

      workspace = plainweave_seed.materialize_workspace()

      def pw(args: list[str]) -> dict:
          env = _plainweave_json(args, cwd=workspace)
          if env is None or not env.get("ok"):
              raise RuntimeError(f"plainweave call failed: {args[0] if args else '?'}")
          return env.get("data") or {}

      try:
          reqs = plainweave_seed.seed(pw, deprecate=False, with_trace_links=True, root=workspace)
          add_book = reqs[plainweave_seed.ADD_BOOK]
          cli_main = reqs[plainweave_seed.CLI_MAIN]
          register = reqs[plainweave_seed.REGISTER]

          # Verification setup: passing evidence on add_book (v1) + cli_main (satisfied);
          # register gets a method but NO evidence (unverified).
          m_add = pw(["verify", "method", "add", add_book, "--method", "test",
                      "--target", "tests/test_cli.py::test_add_book", "--actor", plainweave_seed.ACTOR])["id"]
          pw(["verify", "evidence", "record", m_add, "--status", "passing",
              "--evidence-ref", "ci://run/coverage-add-book", "--actor", plainweave_seed.ACTOR])
          m_cli = pw(["verify", "method", "add", cli_main, "--method", "test",
                      "--target", "tests/test_cli.py::test_main", "--actor", plainweave_seed.ACTOR])["id"]
          pw(["verify", "evidence", "record", m_cli, "--status", "passing",
              "--evidence-ref", "ci://run/coverage-cli-main", "--actor", plainweave_seed.ACTOR])
          pw(["verify", "method", "add", register, "--method", "test",
              "--target", "tests/test_cli.py::test_register", "--actor", plainweave_seed.ACTOR])

          # No-baseline arm: BEFORE locking, diffing a never-created baseline must report an
          # honest NOT_FOUND (or empty items) — never a silent clean. `ok=False` is the
          # EXPECTED answer here (real plainweave 1.2.0 returns NOT_FOUND), so this read is
          # EXCLUDED from the strict read-ok loop below (it must not trip the degrade path).
          no_baseline = _plainweave_json(
              ["baseline", "diff", PLAINWEAVE_COVERAGE_BOGUS_BASELINE], cwd=workspace)

          # Lock at v1, THEN supersede add_book -> v2 (yields drift AND stale from one change).
          baseline_id = pw(["baseline", "create", "--name", PLAINWEAVE_COVERAGE_BASELINE,
                            "--actor", plainweave_seed.ACTOR])["id"]
          pw(["req", "supersede", add_book, "--title", "Add-a-book command (revised)",
              "--statement", "The CLI can add a book to the catalog with validation.",
              "--expected-version", "1", "--actor", plainweave_seed.ACTOR])

          diff = _plainweave_json(["baseline", "diff", baseline_id], cwd=workspace)
          st_add = _plainweave_json(["verify", "status", add_book], cwd=workspace)
          st_cli = _plainweave_json(["verify", "status", cli_main], cwd=workspace)
          st_reg = _plainweave_json(["verify", "status", register], cwd=workspace)
          unver = _plainweave_json(["status", "unverified"], cwd=workspace)
          stale = _plainweave_json(["status", "stale"], cwd=workspace)
          doss = _plainweave_json(["dossier", cli_main], cwd=workspace)
          doss_unknown = _plainweave_json(["dossier", PLAINWEAVE_COVERAGE_BOGUS_REQ], cwd=workspace)
          # `no_baseline` is intentionally absent here: an honest NOT_FOUND is its expected
          # value, asserted by the no_baseline_honest conjunct below (not a failed read).
          for env in (diff, st_add, st_cli, st_reg, unver, stale, doss):
              if env is None or not env.get("ok"):
                  raise RuntimeError("plainweave coverage read failed")
      except Exception as exc:  # tour contract: degrade, never raise. Type name only — no hex/digits.
          return StepResult(name, ok=False, detail=f"plainweave coverage seed/read failed: {type(exc).__name__}")
      finally:
          shutil.rmtree(workspace, ignore_errors=True)  # single-use isolated workspace

      # Tolerate either id form (display `REQ-...` or internal `req-N`) on items/lists.
      def _item(items: list, rid: str) -> dict:
          for it in items:
              if it.get("id") == rid or it.get("requirement_id") == rid:
                  return it
          return {}

      def _ids(env: dict) -> set:
          out: set = set()
          for it in (env.get("data") or {}).get("items", []):
              out |= {it.get("id"), it.get("requirement_id")}
          return out

      def _status(env: dict) -> str | None:
          return (env.get("data") or {}).get("status")

      def _reasons(env: dict) -> set:
          return {r.get("code") for r in (env.get("data") or {}).get("reasons", [])}

      pairs: list[tuple[str, str]] = []

      # ── pw-baseline-drift ────────────────────────────────────────────────────
      diff_items = (diff.get("data") or {}).get("items", [])
      drift_flagged = _item(diff_items, add_book).get("status") == "superseded_since_baseline"
      control_unchanged = _item(diff_items, cli_main).get("status") == "unchanged"
      # Honest no-baseline: a structured envelope that is EITHER an `ok=False` error
      # (real plainweave 1.2.0 -> NOT_FOUND) OR `ok=True` with empty items — never a
      # silent clean (`ok=True` with a populated diff), and never a None (subprocess crash).
      no_baseline_honest = no_baseline is not None and (
          not no_baseline.get("ok")
          or (no_baseline.get("data") or {}).get("items") == []
      )
      if drift_flagged and control_unchanged and no_baseline_honest:
          pairs.append(("pw-baseline-drift", PLAINWEAVE_ADD_BOOK))

      # ── pw-verification-status ─────────────────────────────────────────────────
      satisfied = _status(st_cli) == "satisfied" and "passing_evidence" in _reasons(st_cli)
      unverified = _status(st_reg) == "unverified"
      unverified_listed = register in _ids(unver)
      stale_status = _status(st_add) == "stale"
      stale_listed = add_book in _ids(stale)
      if satisfied and unverified and unverified_listed and stale_status and stale_listed:
          pairs.append(("pw-verification-status", PLAINWEAVE_REGISTER))

      # ── pw-requirement-dossier ─────────────────────────────────────────────────
      ddata = doss.get("data") or {}
      dossier_verification = (ddata.get("verification") or {}).get("status") == "satisfied"
      dossier_baseline_current = any(
          it.get("state") == "current"
          for it in ((ddata.get("baseline_exposure") or {}).get("items") or [])
      )
      dossier_trace = bool((ddata.get("traces") or {}).get("incoming"))
      unknown_honest = doss_unknown is None or not doss_unknown.get("ok")
      if dossier_verification and dossier_baseline_current and dossier_trace and unknown_honest:
          pairs.append(("pw-requirement-dossier", PLAINWEAVE_CLI_MAIN))

      note = (
          f"baseline={baseline_id}; add_book={add_book} cli_main={cli_main} register={register}; "
          f"superseded={(diff.get('data') or {}).get('summary', {}).get('superseded_since_baseline')}"
      )
      return StepResult(
          name,
          ok=len(pairs) == 3,
          detail=(
              "seeded the covered+uncovered corpus, then exercised plainweave's baseline, "
              "verification, and dossier surfaces: locking a baseline and superseding one "
              "approved requirement makes baseline diff report it as drift while an untouched "
              "requirement stays unchanged, and diffing a baseline in a store with no locked "
              "baseline reports an honest error rather than a silent clean; a requirement with a method "
              "and passing evidence reports satisfied while one with a method but no evidence "
              "reports unverified (never silently satisfied) and orphaned evidence reports "
              "stale; and the requirement dossier is coherent for a known requirement and "
              "reports an honest error for an unknown one — never an empty-as-clean dossier; "
              "advisory, local-only, never gates"
          ),
          surfaced=tuple(pairs),
          note=note,
      )
  ```
  Command: `cd /home/john/lacuna && .venv/bin/python -m pytest tests/test_steps_plainweave_coverage.py::test_coverage_surfaces_all_three_pairs_on_full_scenario -q`
  Expected: `1 passed`.

- [ ] **Step 4: Add the degrade-never-raises test.**
  Append to `tests/test_steps_plainweave_coverage.py`:
  ```python
  def test_coverage_degrades_never_raises_on_failed_call(monkeypatch):
      monkeypatch.setattr(steps, "_tool", lambda name: f"/home/john/.local/bin/{name}")
      monkeypatch.setattr(steps, "_plainweave_supports", lambda sub: True)
      monkeypatch.setattr(steps.plainweave_seed, "materialize_workspace", lambda: _WS)
      monkeypatch.setattr(steps.plainweave_seed, "seed",
                          lambda pw, **kw: {ADD_BOOK: ADD_BOOK_ID, CLI_MAIN: CLI_MAIN_ID, REGISTER: REGISTER_ID})
      monkeypatch.setattr(steps, "_plainweave_json", lambda args, cwd=None: None)
      r = steps.plainweave_coverage()
      assert r.ok is False
      assert r.surfaced == ()
      # A present-but-failed call is [WARN] (ran and degraded), NOT [N/A] (gated).
      assert r.available is True
  ```
  Command: `cd /home/john/lacuna && .venv/bin/python -m pytest tests/test_steps_plainweave_coverage.py::test_coverage_degrades_never_raises_on_failed_call -q`
  Expected: `1 passed`.

- [ ] **Step 5: Add the capability-gated test.**
  Append to `tests/test_steps_plainweave_coverage.py`:
  ```python
  def test_coverage_capability_gated_when_surface_absent(monkeypatch):
      # plainweave installed but the base subcommands are absent (stripped/pre-baseline
      # build). The leg must render [N/A] (available=False) with a machine-readable
      # reason — not [WARN], not faked green, and never raising.
      monkeypatch.setattr(steps, "_plainweave_supports", lambda sub: False)
      r = steps.plainweave_coverage()
      assert r.available is False
      assert r.ok is False
      assert r.surfaced == ()
      assert "capability-gated" in r.detail
      assert "baseline" in r.detail
  ```
  Command: `cd /home/john/lacuna && .venv/bin/python -m pytest tests/test_steps_plainweave_coverage.py::test_coverage_capability_gated_when_surface_absent -q`
  Expected: `1 passed`.

- [ ] **Step 6: Add the digit-free determinism test.**
  Append to `tests/test_steps_plainweave_coverage.py`:
  ```python
  def test_coverage_detail_is_digit_free(monkeypatch):
      # `detail` is rendered into the byte-locked tour.md; any digit (a live count/id)
      # would break determinism. Live data must ride `note`, not `detail`.
      _arm_coverage(monkeypatch)
      r = steps.plainweave_coverage()
      assert not any(ch.isdigit() for ch in r.detail)
  ```
  Command: `cd /home/john/lacuna && .venv/bin/python -m pytest tests/test_steps_plainweave_coverage.py::test_coverage_detail_is_digit_free -q`
  Expected: `1 passed`.

- [ ] **Step 7: Add the three pw-baseline-drift drop-tests.**
  Append to `tests/test_steps_plainweave_coverage.py`:
  ```python
  # ── Per-conjunct drop-tests: every condition in each cell's gate is load-bearing ──
  # MULTI-PAIR leg: each test drives exactly ONE conjunct False and asserts THAT cell's
  # pair is gone while the OTHER two remain (isolation), and r.ok goes False.


  def test_coverage_drops_baseline_when_drift_not_flagged(monkeypatch):
      _arm_coverage(monkeypatch, baseline_drift_flagged=False)
      r = steps.plainweave_coverage()
      assert r.ok is False
      assert BASELINE_PAIR not in r.surfaced
      assert VERIFY_PAIR in r.surfaced and DOSSIER_PAIR in r.surfaced


  def test_coverage_drops_baseline_when_control_flagged_as_drift(monkeypatch):
      _arm_coverage(monkeypatch, baseline_control_unchanged=False)
      r = steps.plainweave_coverage()
      assert r.ok is False
      assert BASELINE_PAIR not in r.surfaced
      assert VERIFY_PAIR in r.surfaced and DOSSIER_PAIR in r.surfaced


  def test_coverage_drops_baseline_when_no_baseline_reads_silently_clean(monkeypatch):
      # The no-silent-clean regression: a no-baseline store whose pre-create `baseline diff`
      # silently returns ok=True with a populated/clean diff (instead of an honest NOT_FOUND)
      # must NOT credit the no_baseline_honest conjunct.
      _arm_coverage(monkeypatch, no_baseline_honest=False)
      r = steps.plainweave_coverage()
      assert r.ok is False
      assert BASELINE_PAIR not in r.surfaced
      assert VERIFY_PAIR in r.surfaced and DOSSIER_PAIR in r.surfaced
  ```
  Command: `cd /home/john/lacuna && .venv/bin/python -m pytest tests/test_steps_plainweave_coverage.py -k baseline -q`
  Expected: `3 passed`.

- [ ] **Step 8: Add the five pw-verification-status drop-tests.**
  Append to `tests/test_steps_plainweave_coverage.py`:
  ```python
  def test_coverage_drops_verify_when_not_satisfied(monkeypatch):
      _arm_coverage(monkeypatch, verify_satisfied=False)
      r = steps.plainweave_coverage()
      assert r.ok is False
      assert VERIFY_PAIR not in r.surfaced
      assert BASELINE_PAIR in r.surfaced and DOSSIER_PAIR in r.surfaced


  def test_coverage_drops_verify_when_unverified_reads_satisfied(monkeypatch):
      # The no-silent-clean regression: a method-but-no-evidence req that wrongly reads
      # satisfied must NOT credit the cell (never silently verified).
      _arm_coverage(monkeypatch, verify_unverified=False)
      r = steps.plainweave_coverage()
      assert r.ok is False
      assert VERIFY_PAIR not in r.surfaced
      assert BASELINE_PAIR in r.surfaced and DOSSIER_PAIR in r.surfaced


  def test_coverage_drops_verify_when_unverified_not_listed(monkeypatch):
      _arm_coverage(monkeypatch, unverified_listed=False)
      r = steps.plainweave_coverage()
      assert r.ok is False
      assert VERIFY_PAIR not in r.surfaced
      assert BASELINE_PAIR in r.surfaced and DOSSIER_PAIR in r.surfaced


  def test_coverage_drops_verify_when_stale_reads_satisfied(monkeypatch):
      # Orphaned evidence that wrongly reads satisfied (silently passing) must NOT credit.
      _arm_coverage(monkeypatch, verify_stale=False)
      r = steps.plainweave_coverage()
      assert r.ok is False
      assert VERIFY_PAIR not in r.surfaced
      assert BASELINE_PAIR in r.surfaced and DOSSIER_PAIR in r.surfaced


  def test_coverage_drops_verify_when_stale_not_listed(monkeypatch):
      _arm_coverage(monkeypatch, stale_listed=False)
      r = steps.plainweave_coverage()
      assert r.ok is False
      assert VERIFY_PAIR not in r.surfaced
      assert BASELINE_PAIR in r.surfaced and DOSSIER_PAIR in r.surfaced
  ```
  Command: `cd /home/john/lacuna && .venv/bin/python -m pytest tests/test_steps_plainweave_coverage.py -k verify -q`
  Expected: `5 passed`.

- [ ] **Step 9: Add the four pw-requirement-dossier drop-tests.**
  Append to `tests/test_steps_plainweave_coverage.py`:
  ```python
  def test_coverage_drops_dossier_when_verification_inconsistent(monkeypatch):
      _arm_coverage(monkeypatch, dossier_verification_ok=False)
      r = steps.plainweave_coverage()
      assert r.ok is False
      assert DOSSIER_PAIR not in r.surfaced
      assert BASELINE_PAIR in r.surfaced and VERIFY_PAIR in r.surfaced


  def test_coverage_drops_dossier_when_baseline_not_current(monkeypatch):
      _arm_coverage(monkeypatch, dossier_baseline_current=False)
      r = steps.plainweave_coverage()
      assert r.ok is False
      assert DOSSIER_PAIR not in r.surfaced
      assert BASELINE_PAIR in r.surfaced and VERIFY_PAIR in r.surfaced


  def test_coverage_drops_dossier_when_trace_absent(monkeypatch):
      _arm_coverage(monkeypatch, dossier_trace_present=False)
      r = steps.plainweave_coverage()
      assert r.ok is False
      assert DOSSIER_PAIR not in r.surfaced
      assert BASELINE_PAIR in r.surfaced and VERIFY_PAIR in r.surfaced


  def test_coverage_drops_dossier_when_unknown_returns_empty_as_clean(monkeypatch):
      # The no-silent-clean regression: an unknown req id that returns an ok envelope with
      # an empty body (instead of an honest error) must NOT credit the cell.
      _arm_coverage(monkeypatch, dossier_unknown_honest=False)
      r = steps.plainweave_coverage()
      assert r.ok is False
      assert DOSSIER_PAIR not in r.surfaced
      assert BASELINE_PAIR in r.surfaced and VERIFY_PAIR in r.surfaced
  ```
  Command: `cd /home/john/lacuna && .venv/bin/python -m pytest tests/test_steps_plainweave_coverage.py -q`
  Expected: `16 passed` (1 happy + degrade + gated + digit-free + 3 + 5 + 4 drop-tests).

- [ ] **Step 10: Add the real-producer integration smoke (spec §8.4).**
  The unit tests above mock `_plainweave_json`, so they never prove the leg's predicates key
  on fields the REAL plainweave emits. Spec §8.4 mandates a real-producer smoke. Add one
  `@pytest.mark.integration` test that seeds a real workspace, runs the actual
  `plainweave baseline/verify/status/dossier`, and PINS the predicate-keyed fields against
  live output. The fields below were verified against real plainweave 1.2.0.

  First register + deselect the marker so unit-only CI does NOT run it. In `pyproject.toml`,
  under `[tool.pytest.ini_options]`, change `addopts = "-q"` to `addopts = "-q -m 'not integration'"`
  and add a markers entry:
  ```toml
  markers = [
      "integration: real-producer smoke against the installed plainweave (deselected by default; run with `pytest -m integration`)",
  ]
  ```
  (pytest shlex-splits `addopts` into one `not integration` token; write the quoting exactly.)

  Create `tests/test_steps_plainweave_coverage_integration.py`:
  ```python
  """Real-producer integration smoke for the plainweave coverage leg (spec §8.4).

  Deselected from unit-only CI by the `integration` marker (pyproject's
  `addopts = "-q -m 'not integration'"`); run explicitly with `pytest -m integration`.
  Drives the ACTUAL `plainweave baseline/verify/status/dossier` against a real seed in an
  isolated offline workspace and PINS the envelope fields the leg's predicates key on, so a
  plainweave contract drift (renamed status string / reason code / dossier field) surfaces as
  a regression rather than silently. Field values verified against real plainweave 1.2.0.
  """

  import shutil

  import pytest

  from tour import plainweave_seed, steps

  pytestmark = [
      pytest.mark.integration,
      pytest.mark.skipif(
          not (
              steps._plainweave_supports("baseline")
              and steps._plainweave_supports("verify")
              and steps._plainweave_supports("dossier")
          ),
          reason="real plainweave baseline/verify/dossier surface not installed",
      ),
  ]


  def _item(items, rid):
      return next((it for it in items
                   if it.get("id") == rid or it.get("requirement_id") == rid), {})


  def _ids(data):
      out = set()
      for it in data.get("items", []):
          out |= {it.get("id"), it.get("requirement_id")}
      return out


  def test_plainweave_coverage_real_producer_envelope_shapes():
      workspace = plainweave_seed.materialize_workspace()

      def pw(args):
          env = steps._plainweave_json(args, cwd=workspace)
          if env is None or not env.get("ok"):
              raise AssertionError(f"setup call failed: {args}")
          return env.get("data") or {}

      try:
          reqs = plainweave_seed.seed(pw, deprecate=False, with_trace_links=True, root=workspace)
          add_book = reqs[plainweave_seed.ADD_BOOK]
          cli_main = reqs[plainweave_seed.CLI_MAIN]
          register = reqs[plainweave_seed.REGISTER]
          actor = plainweave_seed.ACTOR

          m_add = pw(["verify", "method", "add", add_book, "--method", "test",
                      "--target", "tests/test_cli.py::test_add_book", "--actor", actor])["id"]
          pw(["verify", "evidence", "record", m_add, "--status", "passing",
              "--evidence-ref", "ci://run/coverage-add-book", "--actor", actor])
          m_cli = pw(["verify", "method", "add", cli_main, "--method", "test",
                      "--target", "tests/test_cli.py::test_main", "--actor", actor])["id"]
          pw(["verify", "evidence", "record", m_cli, "--status", "passing",
              "--evidence-ref", "ci://run/coverage-cli-main", "--actor", actor])
          pw(["verify", "method", "add", register, "--method", "test",
              "--target", "tests/test_cli.py::test_register", "--actor", actor])

          # No-baseline arm BEFORE create: an honest NOT_FOUND, never a silent clean.
          no_baseline = steps._plainweave_json(
              ["baseline", "diff", steps.PLAINWEAVE_COVERAGE_BOGUS_BASELINE], cwd=workspace)
          assert no_baseline is not None and no_baseline.get("ok") is False

          baseline_id = pw(["baseline", "create", "--name", steps.PLAINWEAVE_COVERAGE_BASELINE,
                            "--actor", actor])["id"]
          pw(["req", "supersede", add_book, "--title", "Add-a-book command (revised)",
              "--statement", "The CLI can add a book to the catalog with validation.",
              "--expected-version", "1", "--actor", actor])

          diff = steps._plainweave_json(["baseline", "diff", baseline_id], cwd=workspace)["data"]
          st_add = steps._plainweave_json(["verify", "status", add_book], cwd=workspace)["data"]
          st_cli = steps._plainweave_json(["verify", "status", cli_main], cwd=workspace)["data"]
          st_reg = steps._plainweave_json(["verify", "status", register], cwd=workspace)["data"]
          unver = steps._plainweave_json(["status", "unverified"], cwd=workspace)["data"]
          stale = steps._plainweave_json(["status", "stale"], cwd=workspace)["data"]
          doss = steps._plainweave_json(["dossier", cli_main], cwd=workspace)["data"]
          doss_unknown = steps._plainweave_json(
              ["dossier", steps.PLAINWEAVE_COVERAGE_BOGUS_REQ], cwd=workspace)
      finally:
          shutil.rmtree(workspace, ignore_errors=True)

      # ── baseline diff: superseded req is drift; untouched req stays unchanged ──
      assert _item(diff["items"], add_book)["status"] == "superseded_since_baseline"
      assert _item(diff["items"], cli_main)["status"] == "unchanged"

      # ── verification trichotomy: satisfied(+passing_evidence) / unverified / stale ──
      assert st_cli["status"] == "satisfied"
      assert "passing_evidence" in {r.get("code") for r in st_cli.get("reasons", [])}
      assert st_reg["status"] == "unverified"
      assert st_add["status"] == "stale"
      assert register in _ids(unver)
      assert add_book in _ids(stale)

      # ── dossier: coherent for known, honest error for unknown ──
      assert doss["verification"]["status"] == "satisfied"
      assert any(it.get("state") == "current" for it in doss["baseline_exposure"]["items"])
      assert doss["traces"]["incoming"]
      assert doss_unknown is not None and doss_unknown.get("ok") is False
  ```
  Command: `cd /home/john/lacuna && .venv/bin/python -m pytest tests/test_steps_plainweave_coverage_integration.py -m integration -q`
  Expected: `1 passed` under local plainweave 1.2.0. Confirm the default run deselects it:
  `cd /home/john/lacuna && .venv/bin/python -m pytest tests/test_steps_plainweave_coverage_integration.py -q` → `1 deselected` (NOT run, NOT errored).

- [ ] **Step 11: Commit.**
  Command: `git -C /home/john/lacuna add pyproject.toml tour/steps.py tests/test_steps_plainweave_coverage.py tests/test_steps_plainweave_coverage_integration.py && git -C /home/john/lacuna commit -m "feat(tour): plainweave_coverage leg — baseline/verification/dossier no-silent-clean cells
Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"`

---

### Task 4: Register the leg in the drive order

**Files:**
- Modify `tour/__main__.py` (the `_drive()` results list, after line 38).
- Test `tests/test_drive.py`.

**Interfaces:**
- Consumes: `steps.plainweave_coverage()` (Task 3); `_drive() -> tuple[list, list]`.
- Produces: a `StepResult` named `"plainweave coverage"` present in `_drive()` results, positioned after the loomweave legs (its seed resolves SEIs from the live catalog at seed time).

> **DEFERRED-BLESS WINDOW (Systems W1 — load-bearing):** once Step 2 inserts the leg into
> `_drive()`, the committed `docs/tour.md`/`docs/matrix.md` no longer match a fresh render until
> Task 6 re-blesses them. So `make verify` (and legis preflight / CI on the intermediate Task 4
> and Task 5 commits) WILL fail with `docs/tour.md is stale` — this is EXPECTED and correct, not a
> forgotten bless. Do NOT run `make verify` (or treat its failure as a defect) between this step and
> Task 6 Step 3. The targeted `pytest` commands in Tasks 4-5 are safe to run; only the full
> tour/verify lockstep is intentionally red during this window. (Alternatively, collapse Tasks 4-6
> into a single atomic commit so no intermediate commit is ever stale.)

- [ ] **Step 1: Write the failing drive test.**
  In `tests/test_drive.py`, add (mirror the existing `test_drive_includes_the_plainweave_intent_step`; stub the self-seeding leg and the two slow legs the existing drive tests already stub):
  ```python
  def test_drive_includes_the_plainweave_coverage_step(monkeypatch):
      from tour import steps
      from tour.report import StepResult
      monkeypatch.setattr(steps, "plainweave_coverage",
                          lambda: StepResult("plainweave coverage", ok=True, detail="stub"))
      monkeypatch.setattr(steps, "mcp_attachment",
                          lambda: StepResult("mcp attachment", ok=True, detail="stub"))
      monkeypatch.setattr(steps, "warpline_reverify_federation",
                          lambda: StepResult("warpline reverify federation", ok=True, detail="stub"))
      _caps, results = _drive()
      names = [r.name for r in results]
      assert "plainweave coverage" in names
  ```
  (Match the existing test file's import style for `steps` and `_drive`; if the slow-leg stubs are already provided by a fixture, drop the redundant ones.)
  Command: `cd /home/john/lacuna && .venv/bin/python -m pytest tests/test_drive.py::test_drive_includes_the_plainweave_coverage_step -q`
  Expected FAIL: `assert 'plainweave coverage' in [...]` (leg not registered).

- [ ] **Step 2: Register the leg.**
  In `tour/__main__.py`, after line 38 (`steps.plainweave_wardline_peer_facts(),`) insert:
  ```python
          steps.plainweave_coverage(),
  ```
  Command: `cd /home/john/lacuna && .venv/bin/python -m pytest tests/test_drive.py -q`
  Expected: all pass (existing ordering tests unaffected; new test passes).

- [ ] **Step 3: Commit.**
  Command: `git -C /home/john/lacuna add tour/__main__.py tests/test_drive.py && git -C /home/john/lacuna commit -m "feat(tour): register plainweave_coverage in the drive order
Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"`

---

### Task 5: Add the 3 manifest entries + bump the count to 65

**Files:**
- Modify `tour/lacunae.toml` (insert after line 617, before the mcp-attach header at line 619).
- Modify `tests/test_manifest.py` (line 10 count; membership block).

**Interfaces:**
- Consumes: the `Lacuna` schema (8 required fields, in order: `id`, `file`, `symbol`, `category`, `demonstrates`, `explanation`, `expected_tool`, `expected_rule`); capability names `plainweave-baseline`/`plainweave-verify`/`plainweave-dossier` (Task 1); the rule tokens emitted by the leg (Task 3).
- Produces: 3 catalogued lacunae whose `(expected_rule, symbol)` matches the leg's `surfaced` pairs; `len(m.lacunae) == 65`.

> **DEFERRED-BLESS WINDOW (Systems W1):** still inside the window opened in Task 4 — `make verify`
> stays intentionally red (`docs/tour.md is stale`) until Task 6 Step 3 re-blesses the docs. Run the
> targeted `pytest tests/test_manifest.py` commands below; do NOT run `make verify` yet.

> **Prose voice (orchestrator requirement):** each `explanation` opens with the EXACT "NOT A FLAW — a positive plainweave capability demo." voice and ends "Advisory, local-only, never gates." The capability-gating sentence MUST NOT claim "(e.g. PyPI 1.0.0)" — these subcommands ship in 1.0.0 (see Task 1 DIVERGENCE NOTE). `explanation` is a SINGLE-LINE double-quoted TOML string (no `"""`). No optional fields (`lang`/`expected_kind`/`scan_target`) — they default.

- [ ] **Step 1: Write the failing membership + count test.**
  In `tests/test_manifest.py`, change line 10 `assert len(m.lacunae) == 62` to `assert len(m.lacunae) == 65`, and after line 25 (the peer-facts wing assertion) add:
  ```python
      # the plainweave coverage-depth wing (baseline / verification / dossier)
      assert {"pw-baseline-drift", "pw-verification-status", "pw-requirement-dossier"} <= ids
  ```
  Command: `cd /home/john/lacuna && .venv/bin/python -m pytest tests/test_manifest.py::test_loads_all_lacunae -q`
  Expected FAIL: `assert 62 == 65` (entries not yet added).

- [ ] **Step 2: Add the section header + 3 entries.**
  In `tour/lacunae.toml`, on the blank line 618 (after `pw-wardline-peer-facts` ends at line 617, before the `# ── MCP-attachment ...` header at line 619) insert:
  ```toml

  # ── Plainweave coverage-depth capability demos (pw-baseline-drift / pw-verification-status / pw-requirement-dossier) ──
  # Planted 2026-07-01. Plainweave (requirements management) also ships baseline, verification, and
  # dossier surfaces with no planted lacuna; under the comprehensive-coverage intent (PDR-0020) these
  # are coverage gaps. Each cell is a single-member capability-depth demo (matrix cell `plainweave`,
  # already exercised) asserting the load-bearing NO-SILENT-CLEAN invariant over one surface.
  #
  # CAPABILITY-GATED: each cell's `expected_tool` is a per-subcommand capability (plainweave-{baseline,
  # verify,dossier}), probed from the live `plainweave --help` surface — NOT the bare binary. When the
  # surface is absent (a stripped/pre-baseline build) the cells render `[N/A]` and are gated OUT of
  # verify's coverage assertion (honestly unavailable, not red, not faked green). NOTE: unlike the
  # peer-facts subcommands, baseline/verify/dossier ship in plainweave's BASE surface (present in
  # 1.0.0), so these light up on any plainweave that exposes them.

  [[lacuna]]
  id = "pw-baseline-drift"
  file = "specimen/cli.py"
  symbol = "_add_book"
  category = "baseline"
  demonstrates = ["plainweave"]
  explanation = "NOT A FLAW — a positive plainweave capability demo. Over the seeded corpus, `plainweave baseline create` locks the approved requirements; superseding one (cli._add_book's requirement) makes `baseline diff` report it as `superseded_since_baseline` drift while an untouched requirement (cli.main's) stays `unchanged`; and in a store with no locked baseline, `baseline diff` of a never-created baseline reports an honest `NOT_FOUND` error — never a silent 'clean / no drift'. The load-bearing no-silent-clean contract over the baseline surface. Advisory, local-only, never gates. Capability-gated on the `baseline` CLI surface: renders [N/A] under a plainweave that lacks the subcommand."
  expected_tool = "plainweave-baseline"
  expected_rule = "pw-baseline-drift"

  [[lacuna]]
  id = "pw-verification-status"
  file = "specimen/cli.py"
  symbol = "_register"
  category = "verification"
  demonstrates = ["plainweave"]
  explanation = "NOT A FLAW — a positive plainweave capability demo. A requirement with a verification method AND passing evidence reports `satisfied` (plainweave has no 'verified' status string — the rollup is `satisfied` with reason `passing_evidence`); a requirement with a method but NO evidence reports `unverified` and is listed by `status unverified` — never silently satisfied; and evidence orphaned by a supersede reports `stale` and is listed by `status stale` — an outdated obligation is honestly flagged, never silently passing. The honest satisfied / unverified / stale trichotomy. Advisory, local-only, never gates. Capability-gated on the `verify` CLI surface: renders [N/A] under a plainweave that lacks the subcommand."
  expected_tool = "plainweave-verify"
  expected_rule = "pw-verification-status"

  [[lacuna]]
  id = "pw-requirement-dossier"
  file = "specimen/cli.py"
  symbol = "main"
  category = "dossier"
  demonstrates = ["plainweave"]
  explanation = "NOT A FLAW — a positive plainweave capability demo. `plainweave dossier <known-req> --json` over cli.main's requirement yields a COHERENT dossier — `satisfied` verification, a `current` baseline-exposure member, and an incoming `satisfies` trace — consistent with the baseline-drift and verification-status cells; an unknown requirement id reports an honest `NOT_FOUND` error envelope, NEVER an empty-as-clean dossier. The load-bearing no-silent-clean contract over the dossier surface. Advisory, local-only, never gates. Capability-gated on the `dossier` CLI surface: renders [N/A] under a plainweave that lacks the subcommand."
  expected_tool = "plainweave-dossier"
  expected_rule = "pw-requirement-dossier"
  ```
  Command: `cd /home/john/lacuna && .venv/bin/python -m pytest tests/test_manifest.py -q`
  Expected: all pass (count is 65; membership holds; `test_cells_are_the_union_of_demonstrates` unaffected — `plainweave` is already a cell).

- [ ] **Step 3: Confirm the coverage match wires up (leg pairs → manifest lacunae).**
  Command: `cd /home/john/lacuna && .venv/bin/python -c "from pathlib import Path; from tour.manifest import load_manifest; from tour.report import coverage, StepResult; m=load_manifest(Path('tour/lacunae.toml')); r=StepResult('plainweave coverage', ok=True, detail='x', surfaced=(('pw-baseline-drift','specimen.cli._add_book'),('pw-verification-status','specimen.cli._register'),('pw-requirement-dossier','specimen.cli.main'))); c=coverage(m,[r]); print(sorted({'pw-baseline-drift','pw-verification-status','pw-requirement-dossier'} - c.missing_ids))"`
  Expected: `['pw-baseline-drift', 'pw-requirement-dossier', 'pw-verification-status']` (all three are matched/demonstrated by the leg's pairs — proving `(expected_rule, symbol)` lines up).

- [ ] **Step 4: Commit.**
  Command: `git -C /home/john/lacuna add tour/lacunae.toml tests/test_manifest.py && git -C /home/john/lacuna commit -m "feat(tour): catalog pw-baseline-drift/verification-status/requirement-dossier (62->65)
Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"`

---

### Task 6: Regenerate the locked docs (tour.md + matrix.md + docs/flaws)

**Files:**
- Regenerated: `docs/tour.md`, `docs/matrix.md`, `docs/flaws/pw-baseline-drift.md`, `docs/flaws/pw-verification-status.md`, `docs/flaws/pw-requirement-dossier.md`.

**Interfaces:**
- Consumes: the registered leg (Task 4) + the 3 manifest entries (Task 5).
- Produces: the byte-locked artifacts `make verify` compares against. `docs/flaws/*.md` are GENERATED by `tour/docs_gen.py::render_flaw_page` from the manifest — NOT hand-authored (the header says "Do not edit by hand."). This task must run AFTER Tasks 4+5 because the flaw pages render from the toml entries and the narrative renders from the registered leg.

> Ordering deviation from the orchestrator's list (docs/flaws before count): docs/flaws CANNOT precede the toml entries — they are rendered from them. They are produced here, together with the narrative regen.

- [ ] **Step 1: Run the full drive to regenerate all artifacts.**
  Command: `cd /home/john/lacuna && make tour`
  Expected: the drive runs end-to-end; under local plainweave 1.2.0 the `## ... plainweave coverage` section appears in `docs/tour.md` (exercised, `[PASS]`), and `docs/flaws/pw-baseline-drift.md`, `pw-verification-status.md`, `pw-requirement-dossier.md` are written.

- [ ] **Step 2: Inspect the generated flaw pages + the new narrative section.**
  Command: `cd /home/john/lacuna && git status --porcelain docs/ && head -20 docs/flaws/pw-baseline-drift.md`
  Expected: the three `docs/flaws/pw-*.md` are new/changed; the page shows `# pw-baseline-drift`, the "Do not edit by hand." line, Location/Category/Demonstrates/Expected-finding from the manifest, and the `## Why it's here` body = the `explanation`. `docs/tour.md`/`docs/matrix.md` updated.

- [ ] **Step 3: Commit the regenerated docs.**
  Command: `git -C /home/john/lacuna add docs/tour.md docs/matrix.md docs/flaws && git -C /home/john/lacuna commit -m "docs(tour): regenerate narrative + flaw pages for the plainweave coverage cells
Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"`

---

### Task 7: Final verification + acceptance checklist

**Files:** none modified — this is the gate.
**Interfaces:** Consumes everything above.

- [ ] **Step 1: Run the full unit suite.**
  Command: `cd /home/john/lacuna && .venv/bin/python -m pytest -q`
  Expected: all pass (capability, seed, coverage leg + 12 drop-tests, drive, manifest). The
  `integration` smoke is DESELECTED here by `addopts = "-q -m 'not integration'"` (shown as
  `1 deselected`) — run it explicitly with `.venv/bin/python -m pytest -m integration -q`
  (1 passed under local plainweave 1.2.0; this discharges spec §8.4).

- [ ] **Step 2: Run the merge gate.**
  Command: `cd /home/john/lacuna && git status --porcelain && make verify`
  Expected: clean tree, `VERIFY OK` — the three cells exercise green under local plainweave 1.2.0, surface their tokens, and the regenerated narrative/matrix match the committed files byte-for-byte.

  > **RE-ABSORB FORK (Systems W2 — legis re-stamp):** if `make verify` here FAILS with
  > `docs/tour.md is stale`, first run `git -C /home/john/lacuna status --porcelain`. If the ONLY
  > modified files are `AGENTS.md` and `CLAUDE.md`, this is the legis instruction-block re-stamp
  > (Task 0's friction, re-applied because the session restarted since the Task 6 commit) — NOT a
  > forgotten bless. Absorb it and re-run: `git -C /home/john/lacuna add AGENTS.md CLAUDE.md &&
  > git -C /home/john/lacuna commit -m "chore: absorb legis re-stamp" && cd /home/john/lacuna && make verify`
  > → `VERIFY OK`. If ANY other file differs (e.g. `docs/tour.md`, `tour/*.py`), it is NOT a re-stamp —
  > investigate (a genuine stale bless or an uncommitted change) before committing anything.

- [ ] **Step 3: Prove the capability-gate is honest (simulated absent surface).**
  Command: `cd /home/john/lacuna && .venv/bin/python -c "from tour.capability import detect; caps={c.name:c for c in detect(pw_subcommands=lambda p: frozenset({'intent','req'}))}; print(caps['plainweave-baseline'].available, caps['plainweave-verify'].available, caps['plainweave-dossier'].available)"`
  Expected: `False False False` — under an absent surface the caps are unavailable, so `run_verify` would list the three lacunae in its `CAPABILITY-GATED (… not a failure)` block and NOT red. (The real-1.0.0 path differs — see the acceptance note below.)

- [ ] **Step 4: Confirm the wardline trust-boundary gate is clean (PER-CHANGE scope).**
  Command: `cd /home/john/lacuna && wardline scan . --fail-on ERROR --new-since "$(git merge-base main HEAD)"`
  Expected: exit 0 — the feature introduces NO new boundary findings.
  NOTE: a BARE `wardline scan . --fail-on ERROR` will TRIP here — the specimen is *deliberately* full of planted taint lacunae (`wl-*`/`rs-*`), which are the point of the specimen, not defects introduced by this change. The Makefile `scan:` target documents that CI-on-PR must scope to new findings with `--new-since <merge-base>`; that is the correct per-change gate for a planted-taint specimen. (`--trust-suppressions` alone does NOT clear it — the `.wardline/` baseline suppresses only a few of the planted findings.)

**Acceptance checklist (spec §9, concrete against plainweave 1.2.0 + the BIN-resolved gate):**

- [ ] **AC1 — exercises green under 1.2.0:** `make verify` exits 0 on a clean tree; the `plainweave coverage` leg is `[PASS]`, emits `("pw-baseline-drift","specimen.cli._add_book")`, `("pw-verification-status","specimen.cli._register")`, `("pw-requirement-dossier","specimen.cli.main")`; `docs/tour.md` + `docs/matrix.md` are in lockstep. (Task 7 Step 2.)
- [ ] **AC2 — honest `[N/A]` when the surface is absent:** with a simulated empty `--help` surface the three caps are `available=False`, the cells are gated OUT of the coverage assertion, and `make verify` does NOT red on them (the missing surface is explicit in the `CAPABILITY-GATED` stdout block + the gated `detail`). NO fake green. **DIVERGENCE (flagged):** the committed `_HELP_1_0_0` fixture shows `baseline`/`verify`/`status`/`dossier` ARE present in plainweave 1.0.0 — so the literal spec wording "under PyPI 1.0.0 → `[N/A]`" does NOT hold for these three; `[N/A]` is the genuinely-absent-surface path (tests simulate it), and the merge gate (BIN-first 1.2.0, no pin) EXERCISES the cells. (Task 7 Step 3.)
- [ ] **AC3 — per-conjunct drop-tests fail loud:** all 12 conjuncts (3 baseline + 5 verification + 4 dossier) have a drop-test proving the specific cell goes `missing` (its pair drops, `ok` False) while the other two cells still surface — no hollow gate. (Task 3 Steps 7-9; `pytest -q` → 16 passed.)
- [ ] **AC4 — corpus + docs + determinism:** `test_manifest` asserts 65 lacunae; the three `docs/flaws/pw-*.md` exist and are generated; `detail` is digit-free and `make verify` is byte-stable across re-runs in the fixed env. (Tasks 5-6; Task 3 Step 6.)

---

## Optional hardening (non-blocking reviewer nits)

From the axiom-planning review panel. None blocks execution — the verdict was **minor-revisions** and every must-fix + should-fix is already folded into the tasks above. Each item below is local and reversible; apply at the implementer's discretion.

- **`matrix.md` gains 3 capability rows.** `make tour` (Task 6) adds `plainweave-baseline`/`-verify`/`-dossier` rows to the capability-list section of `docs/matrix.md`. Spec §1's "exercised-cell list will not visibly change" holds for the *exercised-cells* section, not the capability list — expected, not a regression.
- **Tighten `dossier_trace` to the `satisfies` relation.** The conjunct (Task 3) credits any non-empty `traces.incoming`; the manifest prose says "an incoming `satisfies` trace." Tightening to `any(t.get("relation") == "satisfies" ...)` is only safe if the REAL dossier envelope exposes a `relation` field on incoming items — **G6 did not confirm that field.** Confirm against live `plainweave dossier <req> --json` BEFORE tightening (and update both `_dossier_env` and the integration assertion); otherwise leave as-is (the seed does plant a satisfies link, so the prose is accurate).
- **Isolate `satisfied` STATUS from its REASON in a drop-test.** The verification cell's `satisfied` conjunct is `status=="satisfied" AND "passing_evidence" in reasons`; the existing drop (`verify_satisfied=False`) flips both together. A dedicated case (status `satisfied` but a non-`passing_evidence` reason) would prove the reason check is independently load-bearing. Requires decoupling the status/reason knobs in `_arm_coverage`/`_status_env`.
- **Assert leg POSITION, not just presence, in the drive test** (Task 4 Step 1): add `assert names.index("plainweave coverage") > names.index("loomweave analyze")`, matching the existing ordering tests and the SEI-resolution-after-loomweave requirement.
- **Capability gate probes `_plainweave_supports()` 3× on the happy path** (~90 ms, 3 `--help` subprocesses). Cosmetic; optionally collapse to one `plainweave_subcommands` lookup + a set-subset check (the test seam then shifts to `plainweave_subcommands`).
- **Pre-existing (out of plan scope):** `materialize_workspace()` is called outside the leg's `try` (mirroring `plainweave_intent`/`plainweave_requirements_enrichment`); a failure there would raise rather than degrade per the tour contract. Established pattern across the plainweave legs — track as a separate observation against those legs rather than expanding this plan's scope.
