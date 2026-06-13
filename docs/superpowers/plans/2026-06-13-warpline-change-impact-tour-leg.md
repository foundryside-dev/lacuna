# Warpline Change-Impact Tour Leg Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add one tour leg (`warpline_change_impact`) and four catalogued entries that bring **warpline** onto Lacuna's demonstrated surface at parity with the other four federation members.

**Architecture:** Warpline is advisory/enrich-only and never gates, so the leg asserts **change-impact correctness** (not flaw detection): touching `specimen/cli.py::_add_book` must surface its downstream `LibraryService.add_book` in both blast-radius and the reverify worklist, and warpline must carry the anchor's change history (churn + timeline). All warpline access goes through one mockable seam (`_warpline_json`). Determinism for the byte-for-byte `make verify` lockstep is achieved by membership-assert + frozen prose + stable surfaced tokens — never counts, key_ids, timestamps, or set sizes. The leg self-populates warpline's snapshot first, mirroring `loomweave_analyze`.

**Tech Stack:** Python 3.12 (`.venv/bin/python`), pytest, `warpline` CLI (`/home/john/.local/bin/warpline`, `--json`), TOML manifest, Makefile (`make tour`/`make verify`/`make ci`).

**Spec:** `docs/superpowers/specs/2026-06-13-warpline-change-impact-tour-leg-design.md`

> **Amendments applied during execution (post-scrutiny, 2026-06-13).** A
> multi-agent scrutiny pass red-teamed this plan against live warpline and found
> three issues fixed in the shipped implementation; the step code below predates
> them — the SHIPPED `tour/steps.py` is authoritative:
> 1. **Cold-DB self-populate (was a blocker).** The step runs
>    `warpline backfill --no-resolve-sei` **then** `warpline capture-snapshot` —
>    capture-snapshot alone does NOT populate the git-history tables
>    `changed`/`churn`/`timeline` read, so a capture-only step degrades to
>    `ok=False` on every cold CI/clone. The "mirrors `loomweave_analyze`"
>    analogy in the Goal/Architecture above is therefore imprecise.
> 2. **Capability registration (was a fail-loud gap).** `warpline` is added to
>    `tour/capability.py::RUNNABLE` (+ a `tests/test_capability.py` assertion),
>    so the verify gate (`expected_tool in live`) actually asserts the four
>    `hd-*` entries. Without it the leg could degrade silently.
> 3. **Anchor-commit wording.** `fb01a013…` is where warpline first records the
>    `specimen/cli.py::_add_book` path-locator (the `sampleapp → specimen`
>    rename); warpline is rename-blind, so that is its "added" commit. The pin is
>    correct; the comment was reworded (it is not git's add commit).

**Conventions (read first):**
- Working dir `/home/john/lacuna`. Python `.venv/bin/python`; warpline at `/home/john/.local/bin/warpline`.
- Steps in `tour/steps.py` **never raise** (tour contract): any failure degrades to `ok=False` / empty `surfaced`.
- The tour `StepResult.surfaced` carries `(rule_token, qualname)` pairs; `tour/report.py::coverage` credits a lacuna when `rule == expected_rule` and the qualname equals `symbol` or ends with `"." + symbol`. Harness-synthesized tokens (like `dead-entity`) are legitimate.
- `detail` strings are compared byte-for-byte by `make verify` — they must be deterministic: never echo counts, key_ids, timestamps, or live set contents.
- These four entries are **positive-capability demonstrations, not flaws** — `_add_book` gets **no** `LACUNA (...)` docstring; the catalogue carries the intent. Never "fix" them.

**Verified facts (live, 2026-06-13 — do not re-derive, but Task 1 re-confirms):**
- Anchor locator: `python:function:specimen/cli.py::_add_book`, key_id `128` (renumbers on re-ingest — resolved at runtime).
- Anchor was added in commit `fb01a0138d58fa5326fb855d8dd15687f1960af7`; the pinned rev-range `fb01a013…~1..fb01a013…` always contains it.
- `blast-radius(128, depth 2)` includes `python:function:specimen/service.py::LibraryService.add_book`.
- `churn --locator …_add_book` → `churn_count: 1`; `timeline --entity …_add_book` → 1 item.
- `capture-snapshot` is `ok=True`, `peer_side_effects: []`, `local_only: True`, writes only gitignored `.weft/warpline/`, and rebuilds the `_add_book → add_book` edge.

---

## Task 1: Verification-first — re-confirm the warpline invocations

No code changes. This task re-pins the live behaviour the step is built on (the way the Wave-3 Rust trust-marker dialect was pinned), so later tasks rest on fact, not assumption. If any check below disagrees with the recorded output, STOP and reconcile before writing code.

- [ ] **Step 1: Confirm the anchor's key_id from the pinned rev-range**

Run:
```bash
cd /home/john/lacuna
C=fb01a0138d58fa5326fb855d8dd15687f1960af7
/home/john/.local/bin/warpline changed --rev-range "$C~1..$C" --json \
 | python3 -c "import sys,json;d=json.load(sys.stdin);print(next((it['entity']['warpline_entity_key_id'] for it in d['data']['items'] if it['entity']['locator']=='python:function:specimen/cli.py::_add_book'), 'MISSING'))"
```
Expected: an integer (currently `128`). **Decision rule:** if `MISSING`, the anchor's add-commit differs — find it with `warpline timeline --entity "python:function:specimen/cli.py::_add_book" --json` (read `data.items[].commit`) and use that commit as `WARPLINE_ANCHOR_COMMIT` in Task 2.

- [ ] **Step 2: Confirm capture-snapshot rebuilds the downstream edge**

Run:
```bash
cd /home/john/lacuna
/home/john/.local/bin/warpline capture-snapshot --json \
 | python3 -c "import sys,json;d=json.load(sys.stdin);print('capture ok:',d['ok'],'side_effects:',d['meta']['peer_side_effects'])"
C=fb01a0138d58fa5326fb855d8dd15687f1960af7
KID=$(/home/john/.local/bin/warpline changed --rev-range "$C~1..$C" --json | python3 -c "import sys,json;d=json.load(sys.stdin);print(next(it['entity']['warpline_entity_key_id'] for it in d['data']['items'] if it['entity']['locator'].endswith('::_add_book')))")
/home/john/.local/bin/warpline blast-radius --changed-entity-key-id "$KID" --depth 2 --json \
 | python3 -c "import sys,json;d=json.load(sys.stdin);print('add_book present:', any(a['entity']['locator']=='python:function:specimen/service.py::LibraryService.add_book' for a in d['data']['affected']))"
```
Expected: `capture ok: True side_effects: []` and `add_book present: True`. **Decision rule:** if `add_book present: False` after a fresh capture, raise `--depth` to `3` (and in Task 2's step), or pick a sturdier downstream `D` from the affected list (e.g. `python:function:specimen/repository.py::InMemoryRepository.add`) and use it consistently as `WARPLINE_EXPECTED_DOWNSTREAM` everywhere below.

- [ ] **Step 3: Confirm churn + timeline are non-empty for the anchor**

Run:
```bash
cd /home/john/lacuna
/home/john/.local/bin/warpline churn --locator "python:function:specimen/cli.py::_add_book" --json | python3 -c "import sys,json;print('churn_count:', json.load(sys.stdin)['data']['items'][0]['churn_count'])"
/home/john/.local/bin/warpline timeline --entity "python:function:specimen/cli.py::_add_book" --json | python3 -c "import sys,json;print('timeline items:', len(json.load(sys.stdin)['data']['items']))"
```
Expected: `churn_count: 1` (or higher) and `timeline items: 1` (or higher), both `>= 1`. No commit — this task is verification only.

---

## Task 2: The `warpline_change_impact` step + helpers (TDD)

**Files:**
- Modify: `tour/steps.py` (append helpers + the step near the loomweave block, e.g. after `loomweave_findings`)
- Test: `tests/test_steps.py` (append)

- [ ] **Step 1: Write the failing tests** (append to `tests/test_steps.py`)

```python
def test_locator_to_qualname_forms():
    from tour.steps import _locator_to_qualname

    assert _locator_to_qualname("python:function:specimen/cli.py::_add_book") == "specimen.cli._add_book"
    assert _locator_to_qualname("python:class:specimen/models.py::Book") == "specimen.models.Book"
    assert _locator_to_qualname("python:module:specimen.cli") == "specimen.cli"


def _fake_warpline_json(args):
    sub = args[0]
    if sub == "capture-snapshot":
        return {"ok": True, "data": {}, "meta": {"peer_side_effects": [], "local_only": True}}
    if sub == "changed":
        return {"data": {"items": [
            {"entity": {"locator": "python:function:specimen/cli.py::_add_book",
                        "warpline_entity_key_id": 128}}
        ]}}
    if sub == "blast-radius":
        return {"data": {"affected": [
            {"depth": 1, "entity": {"locator": "python:function:specimen/service.py::LibraryService.add_book"}}
        ]}}
    if sub == "reverify":
        return {"data": {"items": [
            {"depth": 1, "reason": "downstream",
             "entity": {"locator": "python:function:specimen/service.py::LibraryService.add_book"}}
        ]}}
    if sub == "churn":
        return {"data": {"items": [{"churn_count": 1}]}}
    if sub == "timeline":
        return {"data": {"items": [{"commit": "fb01a013"}]}}
    raise AssertionError(args)


def test_warpline_change_impact_detail_is_deterministic(monkeypatch):
    from tour import steps

    monkeypatch.setattr(steps, "_tool", lambda name: "/fake/warpline")
    monkeypatch.setattr(steps, "_warpline_json", _fake_warpline_json)
    r = steps.warpline_change_impact()

    assert r.ok
    # frozen prose — no live numbers/ids may leak into the byte-compared detail
    assert not any(ch.isdigit() for ch in r.detail)
    assert "128" not in r.detail
    # all four capabilities credited against the anchor symbol
    for token in ("wp-blast-radius", "wp-reverify", "wp-churn", "wp-timeline"):
        assert (token, "specimen.cli._add_book") in r.surfaced


def test_warpline_change_impact_missing_tool(monkeypatch):
    from tour import steps

    # _tool returns None when warpline is absent -> step degrades, never raises
    monkeypatch.setattr(steps, "_tool", lambda name: None)
    r = steps.warpline_change_impact()
    assert not r.ok
    assert r.surfaced == ()


def test_warpline_change_impact_requires_all_four(monkeypatch):
    from tour import steps

    def missing_downstream(args):
        if args[0] == "blast-radius":
            return {"data": {"affected": []}}  # downstream absent -> blast fails
        return _fake_warpline_json(args)

    monkeypatch.setattr(steps, "_tool", lambda name: "/fake/warpline")
    monkeypatch.setattr(steps, "_warpline_json", missing_downstream)
    r = steps.warpline_change_impact()
    assert not r.ok
    assert r.surfaced == ()
```

- [ ] **Step 2: Run to verify failure**

Run: `.venv/bin/python -m pytest tests/test_steps.py -k warpline_change_impact -v`
Expected: FAIL — `AttributeError`/`ImportError`: `warpline_change_impact` / `_locator_to_qualname` not defined.

- [ ] **Step 3: Implement the helpers + step in `tour/steps.py`** (append after `loomweave_findings`)

```python
# --- warpline: change-impact correctness (advisory, never gates) ---------------

WARPLINE_ANCHOR_LOCATOR = "python:function:specimen/cli.py::_add_book"
# The commit that ADDED the anchor — a permanent, fixed point in main's history.
# A minimal pinned rev-range (COMMIT~1..COMMIT) always contains it, so runtime
# key_id resolution never depends on a moving HEAD. (Re-pinned in plan Task 1.)
WARPLINE_ANCHOR_COMMIT = "fb01a0138d58fa5326fb855d8dd15687f1960af7"
# The frozen expected downstream: the service method the CLI flow delegates to.
WARPLINE_EXPECTED_DOWNSTREAM = "python:function:specimen/service.py::LibraryService.add_book"


def _warpline_json(args: list[str]) -> dict | None:
    """Run `warpline <args> --json` and parse stdout. None on any failure.

    The single mockable seam for the warpline leg (tests monkeypatch this).
    Never raises (tour contract).
    """
    warpline = _tool("warpline")
    if not warpline:
        return None
    proc = _run([warpline, *args, "--json"])
    try:
        return json.loads(proc.stdout)
    except (json.JSONDecodeError, TypeError):
        return None


def _warpline_data(payload: dict | None) -> dict:
    if isinstance(payload, dict):
        data = payload.get("data")
        if isinstance(data, dict):
            return data
    return {}


def _warpline_items(payload: dict | None) -> list[dict]:
    items = _warpline_data(payload).get("items")
    return items if isinstance(items, list) else []


def _locator_to_qualname(locator: str) -> str:
    """`python:function:specimen/cli.py::_add_book` -> `specimen.cli._add_book`.

    Strips the `{plugin}:{kind}:` prefix, then maps the `path::tail` body to a
    dotted qualname so `report.py::_symbol_matches` credits the planted symbol.
    """
    body = locator.split(":", 2)[-1]
    if "::" in body:
        path, _, tail = body.partition("::")
        module = path.removesuffix(".py").replace("/", ".")
        return f"{module}.{tail}"
    return body.removesuffix(".py").replace("/", ".")


def warpline_change_impact() -> StepResult:
    """Demonstrate warpline's change-impact authority over a FROZEN anchor.

    Warpline has no flaw rules — it is advisory/enrich-only and never gates. This
    leg asserts change-impact CORRECTNESS: touching the add-a-book CLI flow
    (`specimen/cli.py::_add_book`) must surface its downstream service method in
    both the blast-radius and the reverify worklist, and warpline must carry the
    anchor's change history (churn + timeline).

    Determinism (`make verify` is byte-for-byte): the affected SET is snapshot-
    state dependent and key_ids renumber on re-ingest, so `detail` is FROZEN
    prose and `surfaced` carries only stable (token, qualname) pairs — never
    counts, key_ids, timestamps, or set sizes. Self-populates warpline's snapshot
    first, mirroring `loomweave_analyze`. Never raises (tour contract).
    """
    name = "warpline change impact"
    if not _tool("warpline"):
        return StepResult(name, ok=False, detail="warpline not installed")

    # 1. Self-populate the snapshot (warpline's only mutating verb; .weft/warpline/
    #    only). Non-fatal: the read queries below degrade on their own.
    _warpline_json(["capture-snapshot"])

    anchor_q = _locator_to_qualname(WARPLINE_ANCHOR_LOCATOR)
    want = WARPLINE_EXPECTED_DOWNSTREAM

    # 2. Resolve the anchor's key_id at runtime from a PINNED rev-range that
    #    always contains the add-commit (never hardcode the integer).
    key_id = None
    rng = f"{WARPLINE_ANCHOR_COMMIT}~1..{WARPLINE_ANCHOR_COMMIT}"
    for item in _warpline_items(_warpline_json(["changed", "--rev-range", rng])):
        entity = item.get("entity", {})
        if entity.get("locator") == WARPLINE_ANCHOR_LOCATOR:
            key_id = entity.get("warpline_entity_key_id")
            break

    blast_ok = reverify_ok = False
    if key_id is not None:
        blast = _warpline_json(["blast-radius", "--changed-entity-key-id", str(key_id), "--depth", "2"])
        blast_ok = any(
            a.get("entity", {}).get("locator") == want
            for a in (_warpline_data(blast).get("affected") or [])
        )
        rev = _warpline_json(["reverify", "--changed-entity-key-id", str(key_id), "--depth", "2"])
        reverify_ok = any(
            it.get("entity", {}).get("locator") == want and it.get("reason") == "downstream"
            for it in _warpline_items(rev)
        )

    # 3. Temporal facts: the anchor carries tracked change history.
    churn_ok = any(
        int(it.get("churn_count", 0)) >= 1
        for it in _warpline_items(_warpline_json(["churn", "--locator", WARPLINE_ANCHOR_LOCATOR]))
    )
    timeline_ok = len(_warpline_items(_warpline_json(["timeline", "--entity", WARPLINE_ANCHOR_LOCATOR]))) >= 1

    ok = blast_ok and reverify_ok and churn_ok and timeline_ok
    surfaced = (
        ("wp-blast-radius", anchor_q),
        ("wp-reverify", anchor_q),
        ("wp-churn", anchor_q),
        ("wp-timeline", anchor_q),
    ) if ok else ()
    return StepResult(
        name,
        ok=ok,
        detail=(
            "touching _add_book surfaces downstream service.add_book in "
            "blast-radius + reverify worklist (edge-provenanced); change history "
            "tracked via churn + timeline — advisory, never gates"
        ),
        surfaced=surfaced,
    )
```

- [ ] **Step 4: Run the targeted tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/test_steps.py -k warpline_change_impact -v`
Expected: PASS (4 tests: `_forms`, `_detail_is_deterministic`, `_missing_tool`, `_requires_all_four`).

- [ ] **Step 5: Run the full suite**

Run: `.venv/bin/python -m pytest`
Expected: all pass (no regression).

- [ ] **Step 6: Commit**

```bash
git add tour/steps.py tests/test_steps.py
git commit -m "feat(tour): warpline_change_impact step — change-impact correctness leg"
```

---

## Task 3: Register the step, catalogue four entries, document them

**Files:**
- Modify: `tour/__main__.py` (register in `_drive`)
- Modify: `tour/lacunae.toml` (append 4 entries)
- Modify: `tests/test_manifest.py:10` (count 44 → 48)
- Modify: `README.md` (planted-flaws section — note the warpline entries are capability demos)

- [ ] **Step 1: Update the manifest count test first** (it will fail until the entries are added)

In `tests/test_manifest.py`, change line 10:
```python
    assert len(m.lacunae) == 48
```
(was `== 44`).

- [ ] **Step 2: Append the four entries to `tour/lacunae.toml`**

```toml
[[lacuna]]
id = "wp-blast-radius"
file = "specimen/cli.py"
symbol = "_add_book"
category = "change-impact"
demonstrates = ["warpline"]
explanation = "NOT A FLAW — a positive warpline capability demo. Touching the add-a-book CLI flow (_add_book), warpline's blast-radius surfaces the downstream LibraryService.add_book it delegates to, with edge provenance. Warpline is advisory/enrich-only and never gates."
expected_tool = "warpline"
expected_rule = "wp-blast-radius"

[[lacuna]]
id = "wp-reverify"
file = "specimen/cli.py"
symbol = "_add_book"
category = "change-impact"
demonstrates = ["warpline"]
explanation = "NOT A FLAW — a positive warpline capability demo. warpline's reverify worklist for a change to _add_book lists LibraryService.add_book as reason=downstream, the 'what must I re-verify' surface. Advisory, never gates."
expected_tool = "warpline"
expected_rule = "wp-reverify"

[[lacuna]]
id = "wp-churn"
file = "specimen/cli.py"
symbol = "_add_book"
category = "change-impact"
demonstrates = ["warpline"]
explanation = "NOT A FLAW — a positive warpline capability demo. warpline tracks _add_book's change history (churn_count >= 1) from ingested commits — the temporal-churn surface. Advisory, never gates."
expected_tool = "warpline"
expected_rule = "wp-churn"

[[lacuna]]
id = "wp-timeline"
file = "specimen/cli.py"
symbol = "_add_book"
category = "change-impact"
demonstrates = ["warpline"]
explanation = "NOT A FLAW — a positive warpline capability demo. warpline's timeline for _add_book returns its per-entity change history (>= 1 entry). Advisory, never gates."
expected_tool = "warpline"
expected_rule = "wp-timeline"
```

- [ ] **Step 3: Register the step in `tour/__main__.py::_drive`**

After `steps.rust_archaeology(),` (the last loomweave-family leg), add a line so the block reads:
```python
        steps.loomweave_findings(),
        steps.rust_archaeology(),
        steps.warpline_change_impact(),
        steps.wardline_scan(),
```
(Registering after the loomweave/archaeology family guarantees `loomweave analyze` has populated `.weft/loomweave/` before warpline's `capture-snapshot` reads it for edges.)

- [ ] **Step 4: Document the entries in `README.md`** (so no maintainer "fixes" them). Append to the planted-flaws section:

```markdown
> **Warpline entries are capability demos, not flaws.** `wp-blast-radius`,
> `wp-reverify`, `wp-churn`, and `wp-timeline` (all on `specimen/cli.py::_add_book`)
> assert warpline's change-impact *correctness*, not a defect — warpline is
> advisory/enrich-only and never gates. `_add_book` carries no `LACUNA` docstring
> by design. Do not "fix" them; the catalogue holds the intent.
```

- [ ] **Step 5: Run the manifest + report tests**

Run: `.venv/bin/python -m pytest tests/test_manifest.py -v`
Expected: PASS — `len == 48`; `warpline` now appears in `m.cells()` (the cells = union of `demonstrates`, asserted by `test_cells_are_the_union_of_demonstrates`).

- [ ] **Step 6: Run the full suite**

Run: `.venv/bin/python -m pytest`
Expected: all pass.

- [ ] **Step 7: Commit**

```bash
git add tour/__main__.py tour/lacunae.toml tests/test_manifest.py README.md
git commit -m "feat(tour): catalogue + register the four warpline change-impact entries (44->48)"
```

---

## Task 4: Live run, docs regen, wave close

**Files:**
- Modify: `docs/tour.md`, `docs/matrix.md` (regenerated), `docs/flaws/*` (generated per-lacuna pages, if the generator emits them)

- [ ] **Step 1: Live-run the tour and confirm the warpline leg surfaces**

Run: `.venv/bin/python -m tour tour 2>&1 | grep -iA1 "warpline change impact"`
Expected: a `✅ warpline change impact` line followed by the frozen detail (`touching _add_book surfaces downstream service.add_book …`). If `⚠️`/`❌`, the live snapshot lacks the edge — re-run Task 1 Step 2's decision rule (raise depth / sturdier `D`) and adjust `warpline_change_impact`.

- [ ] **Step 2: Confirm full coverage (no orphaned entries)**

Run: `.venv/bin/python -m tour tour 2>&1 | grep -i "not surfaced"`
Expected: `Not surfaced: []`. If the four `hd-*` ids appear, the qualname normalization or token didn't match — check `_locator_to_qualname` output equals `specimen.cli._add_book` and the `expected_rule`s match the surfaced tokens exactly.

- [ ] **Step 3: Regenerate the docs**

Run: `make tour`
Expected: exit 0; `git status --short docs/` shows `docs/tour.md` and `docs/matrix.md` modified (and any `docs/flaws/hd-*.md` added if the generator emits per-lacuna pages). `docs/tour.md` gains a `## ✅ warpline change impact` section; `docs/matrix.md` gains a `warpline` cell.

- [ ] **Step 4: Byte-for-byte verify**

Run: `make verify`
Expected: exit 0 (the regenerated docs match a second tour run byte-for-byte — proves the detail is deterministic).

- [ ] **Step 5: Full CI gate**

Run: `make ci`
Expected: exit 0 (`test scan verify cargo-check` all pass).

- [ ] **Step 6: Commit the regenerated docs**

```bash
git add docs/
git commit -m "docs(tour): regen for warpline change-impact leg (48 lacunae, 5 members demonstrated)"
```

---

## Self-review notes (for the implementer)

- **Determinism is the whole game.** If you ever feel tempted to put a count, key_id, timestamp, affected-set size, or snapshot commit into `detail` or `surfaced`, stop — that breaks `make verify`. The frozen prose and the four fixed tokens are the only things that may appear.
- **Never hardcode key_id 128.** It is resolved at runtime in Step `2` of the function. The `128` literals exist only in test fixtures and the verification commands.
- **The warpline entries are not flaws.** Reviewers will see four catalogue entries with no `LACUNA` docstring in the source — that is correct and documented in `README.md`.
