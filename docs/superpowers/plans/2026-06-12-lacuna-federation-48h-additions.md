# Lacuna Federation 48h-Additions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add 16 new lacunae and 4 new tour legs to the lacuna demo, covering the federation's 2026-06-10/11 shipped capability, in three always-green waves.

**Architecture:** Everything derives from `tour/lacunae.toml` (the manifest). Wave 1 plants eight Python lacunae (no harness changes beyond one new read-only step). Wave 2 adds four tour legs (legis policy-boundary, filigree sentinel cycle, two fail-closed negative demos against a committed quarantine dir). Wave 3 adds a `specimen-rs/` crate and the Rust scan/archaeology wing. Spec: `docs/superpowers/specs/2026-06-12-lacuna-federation-48h-additions-design.md`.

**Tech Stack:** Python 3.12 (`.venv/bin/python`), pytest, TOML manifest, wardline/loomweave/filigree/legis CLIs + HTTP, sqlite3 reads of `.weft/loomweave/loomweave.db`, Rust (tree-sitter-scanned; `cargo check` optional).

**Conventions (read first):**
- Working dir: `/home/john/lacuna`. Python: `.venv/bin/python`; tools at `/home/john/.local/bin/`.
- Every wave ends with `make ci` green and a regenerated, committed `docs/tour.md`/`docs/matrix.md` (verify compares byte-for-byte — tour `detail` strings must be deterministic: never echo raw tool stdout, counts that flap, or live issue ids).
- The tour `StepResult.surfaced` carries `(rule_token, qualname)` pairs; `tour/report.py::coverage` credits a lacuna when `rule == expected_rule` and the qualname equals `symbol` or ends with `"." + symbol`. Harness-synthesized tokens (like the existing `dead-entity`) are legitimate rule tokens.
- Planted flaws get a `LACUNA (<rule>)` docstring line and are permanent. Never "fix" them.

---

## Wave 1 — eight Python lacunae

### Task 1: Manifest schema extension (`lang`, `expected_kind`, `scan_target`)

**Files:**
- Modify: `tour/manifest.py`
- Test: `tests/test_manifest.py`

- [ ] **Step 1: Write the failing test** (append to `tests/test_manifest.py`)

```python
def test_optional_fields_default(tmp_path):
    from tour.manifest import load_manifest
    p = tmp_path / "m.toml"
    p.write_text(
        '[[lacuna]]\nid = "x"\nfile = "f.py"\nsymbol = "s"\ncategory = "c"\n'
        'demonstrates = ["wardline"]\nexplanation = "e"\n'
        'expected_tool = "wardline"\nexpected_rule = "R"\n'
    )
    lac = load_manifest(p).lacunae[0]
    assert lac.lang == "python"
    assert lac.expected_kind == "finding"
    assert lac.scan_target == ""


def test_optional_fields_explicit(tmp_path):
    from tour.manifest import load_manifest
    p = tmp_path / "m.toml"
    p.write_text(
        '[[lacuna]]\nid = "x"\nfile = "f.rs"\nsymbol = "s"\ncategory = "c"\n'
        'demonstrates = ["wardline"]\nexplanation = "e"\n'
        'expected_tool = "wardline"\nexpected_rule = "R"\n'
        'lang = "rust"\nexpected_kind = "gate-trip"\nscan_target = "specimen_quarantine"\n'
    )
    lac = load_manifest(p).lacunae[0]
    assert (lac.lang, lac.expected_kind, lac.scan_target) == ("rust", "gate-trip", "specimen_quarantine")
```

- [ ] **Step 2: Run to verify failure**

Run: `.venv/bin/python -m pytest tests/test_manifest.py -v`
Expected: FAIL — `TypeError`/`AttributeError`: `Lacuna` has no `lang`.

- [ ] **Step 3: Implement** — in `tour/manifest.py` add three defaulted fields to `Lacuna` and read them in `load_manifest`:

```python
@dataclass(frozen=True)
class Lacuna:
    id: str
    file: str
    symbol: str
    category: str
    demonstrates: tuple[str, ...]
    explanation: str
    expected_tool: str
    expected_rule: str
    lang: str = "python"
    expected_kind: str = "finding"   # "finding" | "gate-trip"
    scan_target: str = ""            # non-empty only for quarantine legs
```

and in the `Lacuna(...)` construction inside `load_manifest` append:

```python
            lang=e.get("lang", "python"),
            expected_kind=e.get("expected_kind", "finding"),
            scan_target=e.get("scan_target", ""),
```

- [ ] **Step 4: Run the full suite** — `.venv/bin/python -m pytest` → all pass.
- [ ] **Step 5: Commit** — `git add tour/manifest.py tests/test_manifest.py && git commit -m "feat(manifest): optional lang/expected_kind/scan_target fields"`

### Task 2: `specimen/preview_sinks.py` — six preview-rule lacunae

**Files:**
- Create: `specimen/preview_sinks.py`
- Modify: `tour/lacunae.toml` (append 6 entries)

- [ ] **Step 1: Create `specimen/preview_sinks.py`** (full content — mirrors `specimen/wardline_sinks.py`; module-level sink imports need not be installed, same as `requests` there):

```python
"""Planted Wardline PREVIEW-rule lacunae — the PY-WL-121…126 sink families.

Each function is an INTENTIONAL, catalogued flaw (see tour/lacunae.toml). Every
one pulls an EXTERNAL_RAW value from a boundary and drives it into one of the
six 2026-06-11 preview sink families. Preview rules fire by default but are
gate-immune (Maturity.PREVIEW is filtered from --fail-on). Do NOT "fix" them.

NOTE: ``log_export_request`` (PY-WL-125) is the tour's designated SENTINEL —
deliberately NOT baselined; the filigree tour leg promotes and cycles it.
Do not baseline it.

Theme: the library-catalog admin surface grows feed-parsing, templating,
preferences, codecs, logging and notification — each one (carelessly) driving
an operator-supplied string into a new interpreter.
"""

from __future__ import annotations

import ctypes
import logging
import smtplib
from collections.abc import Sequence

import jinja2  # noqa: F401 — sink namespace; not required to be installed for static scan
from lxml import etree  # noqa: F401 — sink namespace; not required to be installed for static scan

from weft_markers import external_boundary, trusted

logger = logging.getLogger(__name__)


@external_boundary
def read_report_field(argv: Sequence[str]) -> str:
    """An operator-supplied string crossing the reporting boundary (untrusted)."""
    return argv[0] if argv else ""


@trusted(level="ASSURED")
def parse_catalog_feed(argv: Sequence[str]) -> object:
    """LACUNA (PY-WL-121): untrusted XML text reaches lxml.etree.fromstring (XXE)."""
    text = read_report_field(argv)
    return etree.fromstring(text)


@trusted(level="ASSURED")
def render_report_template(argv: Sequence[str]) -> str:
    """LACUNA (PY-WL-122): untrusted template source reaches jinja2.Template (SSTI)."""
    source = read_report_field(argv)
    return jinja2.Template(source).render()


@trusted(level="ASSURED")
def apply_display_option(argv: Sequence[str], prefs: object) -> None:
    """LACUNA (PY-WL-123): untrusted attribute NAME reaches setattr (reflection injection)."""
    name = read_report_field(argv)
    setattr(prefs, name, True)


@trusted(level="ASSURED")
def load_codec_library(argv: Sequence[str]) -> object:
    """LACUNA (PY-WL-124): untrusted path reaches ctypes.CDLL (native-library load)."""
    path = read_report_field(argv)
    return ctypes.CDLL(path)


@trusted(level="ASSURED")
def log_export_request(argv: Sequence[str]) -> None:
    """LACUNA (PY-WL-125) — THE TOUR SENTINEL: untrusted text reaches logging (log injection)."""
    msg = read_report_field(argv)
    logger.info(msg)


@trusted(level="ASSURED")
def notify_member(argv: Sequence[str]) -> None:
    """LACUNA (PY-WL-126): untrusted recipient/body reach smtplib sendmail (mail injection)."""
    field = read_report_field(argv)
    smtp = smtplib.SMTP("localhost")
    smtp.sendmail("library@example.org", [field], field)
```

- [ ] **Step 2: Verify all six rules fire**

Run: `/home/john/.local/bin/wardline scan . 2>/dev/null >/dev/null; for r in 121 122 123 124 125 126; do grep -c "PY-WL-$r" findings.jsonl; done`
Expected: six lines, each `>= 1`. If a rule does not fire, read its trigger spec in `/home/john/wardline/src/wardline/scanner/rules/untrusted_to_*.py` and adjust the planted call shape (e.g. argument slot) until it does. PY-WL-123 taints **slot 1** (the name) — the call shape above is correct.

- [ ] **Step 3: Append six manifest entries to `tour/lacunae.toml`**

```toml
[[lacuna]]
id = "wl-xxe"
file = "specimen/preview_sinks.py"
symbol = "parse_catalog_feed"
category = "injection"
demonstrates = ["wardline"]
explanation = "Untrusted XML text reaches lxml.etree.fromstring — XXE (preview rule, gate-immune)."
expected_tool = "wardline"
expected_rule = "PY-WL-121"

[[lacuna]]
id = "wl-ssti"
file = "specimen/preview_sinks.py"
symbol = "render_report_template"
category = "injection"
demonstrates = ["wardline"]
explanation = "Untrusted template source reaches jinja2.Template — server-side template injection (preview)."
expected_tool = "wardline"
expected_rule = "PY-WL-122"

[[lacuna]]
id = "wl-reflection-injection"
file = "specimen/preview_sinks.py"
symbol = "apply_display_option"
category = "injection"
demonstrates = ["wardline"]
explanation = "Untrusted attribute NAME reaches setattr — reflection injection (preview)."
expected_tool = "wardline"
expected_rule = "PY-WL-123"

[[lacuna]]
id = "wl-native-lib-load"
file = "specimen/preview_sinks.py"
symbol = "load_codec_library"
category = "injection"
demonstrates = ["wardline"]
explanation = "Untrusted path reaches ctypes.CDLL — native-library load (preview)."
expected_tool = "wardline"
expected_rule = "PY-WL-124"

[[lacuna]]
id = "wl-log-injection"
file = "specimen/preview_sinks.py"
symbol = "log_export_request"
category = "injection"
demonstrates = ["wardline", "wardline+filigree"]
explanation = "Untrusted text reaches logging — log injection (preview). THE SENTINEL: deliberately unbaselined; the filigree leg promotes and cycles it."
expected_tool = "wardline"
expected_rule = "PY-WL-125"

[[lacuna]]
id = "wl-mail-injection"
file = "specimen/preview_sinks.py"
symbol = "notify_member"
category = "injection"
demonstrates = ["wardline"]
explanation = "Untrusted recipient/body reach smtplib sendmail — mail injection (preview)."
expected_tool = "wardline"
expected_rule = "PY-WL-126"
```

- [ ] **Step 4: Baseline five of six (keep the sentinel active)**

Run: `/home/john/.local/bin/wardline baseline update` then open `.weft/wardline/baseline.yaml` and **delete the entry whose `rule_id` is `PY-WL-125`** (the sentinel must stay unbaselined). Re-scan and confirm: `/home/john/.local/bin/wardline scan . --fail-on ERROR --trust-suppressions; echo exit=$?`
Expected: `exit=0` (preview rules are gate-immune), summary shows the PY-WL-125 finding active and the other five suppressed (baseline count grows by 5).

- [ ] **Step 5: Document the sentinel in README** (spec risk 3 — so nobody "fixes" or baselines it). Append to the planted-flaws section of `README.md`:

```markdown
> **The sentinel:** `wl-log-injection` (PY-WL-125, `specimen/preview_sinks.py`)
> is deliberately **unbaselined** — preview rules are gate-immune, and the
> filigree tour leg promotes and work-cycles exactly this finding. The scan
> summary showing `1 active` is correct, not drift. Do not baseline it.
```

- [ ] **Step 6: Run tests, commit**

Run: `.venv/bin/python -m pytest` → pass.
`git add specimen/preview_sinks.py tour/lacunae.toml .weft/wardline/baseline.yaml README.md && git commit -m "feat(specimen): six PY-WL-121..126 preview-rule lacunae; PY-WL-125 kept as unbaselined sentinel"`

### Task 3: `lw-too-complex` — the nesting bomb

**Files:**
- Create: `specimen/nesting_bomb.py` (generated)
- Create: `weft.toml` (wardline exclude — protects the main gate from the bomb)
- Modify: `tour/lacunae.toml`

- [ ] **Step 1: Generate the committed bomb file**

Run:
```bash
.venv/bin/python - <<'EOF'
chain = "+".join(["1"] * 4000)
content = (
    '"""LACUNA (LMWV-PY-TOO-COMPLEX): a deep-nesting bomb the loomweave python\n'
    'plugin degrades to parse_status=too_complex instead of crashing.\n'
    'GENERATED — do not edit; excluded from the wardline scan root (weft.toml).\n'
    '"""\n\nBOMB = ' + chain + "\n"
)
open("specimen/nesting_bomb.py", "w").write(content)
EOF
```

- [ ] **Step 2: Exclude the bomb (and, ahead of Wave 2, the quarantine dir) from wardline's root scan** — create `weft.toml` at repo root:

```toml
[wardline]
exclude = ["specimen/nesting_bomb.py", "specimen_quarantine", "specimen_quarantine/*"]
```

Verify the config key is honored: `/home/john/.local/bin/wardline scan . 2>&1 | tail -2` then `grep -c nesting_bomb findings.jsonl`
Expected: `0` (bomb skipped). If the exclude is not picked up, check `WardlineConfig` loading in `/home/john/wardline/src/wardline/core/config.py:36-40` for the expected config filename/section and adjust `weft.toml` accordingly. Re-run `make scan` → exit 0.

- [ ] **Step 3: Confirm the loomweave degrade fires**

Run: `/home/john/.local/bin/loomweave analyze . >/dev/null 2>&1; sqlite3 .weft/loomweave/loomweave.db "select rule_id from findings where rule_id like 'LMWV-PY-TOO-COMPLEX%';"`
Expected: at least one `LMWV-PY-TOO-COMPLEX` row. If the `findings` table name/columns differ, inspect with `sqlite3 .weft/loomweave/loomweave.db .schema | grep -A8 finding` and note the real names — Task 5's step code must use them.

- [ ] **Step 4: Append the manifest entry**

```toml
[[lacuna]]
id = "lw-too-complex"
file = "specimen/nesting_bomb.py"
symbol = "nesting_bomb"
category = "archaeology"
demonstrates = ["loomweave"]
explanation = "A generated deep-nesting bomb; the python plugin degrades it to parse_status=too_complex and emits LMWV-PY-TOO-COMPLEX instead of crashing."
expected_tool = "loomweave"
expected_rule = "LMWV-PY-TOO-COMPLEX"
```

- [ ] **Step 5: Run tests, commit** — `.venv/bin/python -m pytest` → pass (nothing imports the bomb). `git add specimen/nesting_bomb.py weft.toml tour/lacunae.toml && git commit -m "feat(specimen): lw-too-complex nesting bomb (wardline-excluded, loomweave-degraded)"`

### Task 4: `lw-duplicate-locator` — entity-id collision (verification-first)

**Files:**
- Create: `specimen/colliding.py`, `specimen/colliding/__init__.py`
- Modify: `tour/lacunae.toml`

**Background:** module-level dual-claims are carved out (silent). The candidate construct is two same-qualname **classes**: `specimen/colliding.py` and `specimen/colliding/__init__.py` both defining `class ShelfMark` → both emit `python:class:specimen.colliding.ShelfMark` → in-run cross-file duplicate → `LMWV-DUPLICATE-LOCATOR` (ERROR).

- [ ] **Step 1: Empirical verification in a scratch dir**

```bash
mkdir -p /tmp/dupcheck/pkg && cd /tmp/dupcheck
printf 'class ShelfMark:\n    pass\n' > pkg.py
printf 'class ShelfMark:\n    pass\n' > pkg/__init__.py
/home/john/.local/bin/loomweave analyze . >/dev/null 2>&1
sqlite3 .weft/loomweave/loomweave.db "select rule_id, severity from findings where rule_id='LMWV-DUPLICATE-LOCATOR';"
```
Expected: one `LMWV-DUPLICATE-LOCATOR|ERROR` row. **Decision rule:** if no row, vary the construct (same-named module-level *functions* in both files; then a class in `pkg/sub.py` colliding with `pkg.py`'s nested route) until the alarm fires; whatever fires is the committed construct. Record the winning construct in the manifest `explanation`. Clean up `/tmp/dupcheck` after.

- [ ] **Step 2: Commit the winning construct into the specimen** (assuming the candidate works):

`specimen/colliding.py`:
```python
"""LACUNA (LMWV-DUPLICATE-LOCATOR): this file and specimen/colliding/__init__.py
both define ShelfMark, assembling the same entity id from two source files —
loomweave's duplicate-locator alarm (ERROR, silent-data-loss class)."""


class ShelfMark:
    """The flat-module twin."""
```

`specimen/colliding/__init__.py`:
```python
"""LACUNA (LMWV-DUPLICATE-LOCATOR) — the package twin of specimen/colliding.py."""


class ShelfMark:
    """The package twin."""
```

- [ ] **Step 3: Confirm in-tree** — `/home/john/.local/bin/loomweave analyze . >/dev/null 2>&1; sqlite3 .weft/loomweave/loomweave.db "select count(*) from findings where rule_id='LMWV-DUPLICATE-LOCATOR';"` → `>= 1`.

- [ ] **Step 4: Append the manifest entry**

```toml
[[lacuna]]
id = "lw-duplicate-locator"
file = "specimen/colliding.py"
symbol = "colliding"
category = "archaeology"
demonstrates = ["loomweave"]
explanation = "specimen/colliding.py and specimen/colliding/__init__.py both define ShelfMark — an in-run cross-file entity-id collision; LMWV-DUPLICATE-LOCATOR fires (ERROR)."
expected_tool = "loomweave"
expected_rule = "LMWV-DUPLICATE-LOCATOR"
```

- [ ] **Step 5: Run tests (also check wardline still green), commit**

Run: `.venv/bin/python -m pytest && make scan` → pass / exit 0.
`git add specimen/colliding.py specimen/colliding/__init__.py tour/lacunae.toml && git commit -m "feat(specimen): lw-duplicate-locator entity-id collision pair"`

### Task 5: `loomweave_findings` tour step + Wave-1 close

**Files:**
- Modify: `tour/steps.py`, `tour/__main__.py`
- Test: `tests/test_steps.py`

- [ ] **Step 1: Write the failing test** (append to `tests/test_steps.py`; follow that file's existing fixture style for DB-backed steps — it builds a scratch sqlite DB; mirror the nearest existing test of `loomweave_*`):

```python
def test_loomweave_findings_maps_paths_to_module_qualnames(tmp_path):
    import sqlite3
    from tour import steps

    db = tmp_path / "loomweave.db"
    con = sqlite3.connect(db)
    con.execute("create table findings (rule_id text, file_path text)")
    con.execute("insert into findings values ('LMWV-PY-TOO-COMPLEX', 'specimen/nesting_bomb.py')")
    con.execute("insert into findings values ('LMWV-DUPLICATE-LOCATOR', 'specimen/colliding.py')")
    con.commit(); con.close()

    result = steps.loomweave_findings(db_path=db)
    assert result.ok
    assert ("LMWV-PY-TOO-COMPLEX", "specimen.nesting_bomb") in result.surfaced
    assert ("LMWV-DUPLICATE-LOCATOR", "specimen.colliding") in result.surfaced
```

NOTE: the real `findings` schema was inspected in Task 3 Step 3 — if the column is not `file_path` (e.g. it is `subject` or `path`), use the real name in BOTH this test's fixture and Step 3's query.

- [ ] **Step 2: Run to verify failure** — `.venv/bin/python -m pytest tests/test_steps.py::test_loomweave_findings_maps_paths_to_module_qualnames -v` → FAIL (`loomweave_findings` not defined).

- [ ] **Step 3: Implement in `tour/steps.py`** (after `loomweave_analyze`):

```python
def loomweave_findings(db_path: Path = LOOMWEAVE_DB) -> StepResult:
    """Surface loomweave's OWN analyzer alarms (LMWV-*) from the index DB.

    Deterministic detail: sorted rule ids only — counts/paths would flap the
    byte-for-byte verify lockstep across environments.
    """
    name = "loomweave findings"
    pairs: list[tuple[str, str]] = []
    if Path(db_path).exists():
        try:
            con = sqlite3.connect(str(db_path))
            try:
                rows = con.execute(
                    "select rule_id, file_path from findings where rule_id like 'LMWV-%'"
                ).fetchall()
            finally:
                con.close()
        except sqlite3.Error:
            rows = []
        for rule, path in rows:
            qual = (path or "").removesuffix(".py").replace("/", ".")
            pairs.append((rule, qual))
    pairs = list(dict.fromkeys(pairs))
    rules = sorted({r for r, _ in pairs})
    return StepResult(
        name,
        ok=bool(pairs),
        detail=f"analyzer alarms: {', '.join(rules) or '(none)'}",
        surfaced=tuple(pairs),
    )
```

- [ ] **Step 4: Register the step** — in `tour/__main__.py::_drive`, add `steps.loomweave_findings(),` after `steps.loomweave_navigation(),`.

- [ ] **Step 5: Run the suite, then close the wave**

```bash
.venv/bin/python -m pytest          # all pass
make tour                            # regen docs; "Not surfaced: []" must hold
git add -A docs/ tour/ && git commit -m "feat(tour): loomweave findings leg; Wave-1 docs regen (36 lacunae)"
make ci                              # exit 0 — Wave 1 lands green
```
Expected from `make tour`: `Demonstrated lacunae` includes all eight new ids; `Not surfaced: []`.

---

## Wave 2 — four new tour legs

### Task 6: legis joins the venv; `@policy_boundary` specimens

**Files:**
- Create: `specimen/policy_boundaries.py`
- Create: `tests/test_policy_boundaries.py`
- Modify: `tour/lacunae.toml`, `pyproject.toml` (comment only)

- [ ] **Step 1: Install legis into the venv** (same editable-from-path pattern as `weft-markers`):

Run: `.venv/bin/pip install -e /home/john/legis` then `.venv/bin/python -c "from legis.policy.decorator import policy_boundary; print('ok')"` → `ok`.
Add to the `pyproject.toml` NOTE comment: `legis` is also editable-from-path (unpublished), for the `@policy_boundary` specimens.

- [ ] **Step 2: Discover the exact fingerprint helper and CLI shape**

Run: `grep -n "def fingerprint" /home/john/legis/src/legis/policy/*.py` and `/home/john/.local/bin/legis policy-boundary-check --help`
Expected: a `fingerprint_source`-style helper (decorator.py or evidence.py) and the check's root/repo-root options (`src/legis/cli.py:403-412`). Use the real names below.

- [ ] **Step 3: Create `tests/test_policy_boundaries.py`** (tests first — they are also the evidence the checker inspects):

```python
"""Evidence tests for the @policy_boundary specimens.

test_pinned_import_boundary is DELIBERATELY skip-marked: that disabled evidence
IS the lacuna (lg-disabled-boundary-evidence / POLICY_BOUNDARY_TEST_DISABLED).
Do not un-skip it.
"""

import pytest

from specimen.policy_boundaries import pinned_import, validated_recovery


def test_validated_recovery_boundary():
    result = validated_recovery({"id": 7})
    assert result == {"id": 7} and "no-broad-except"  # policy asserted with the call


@pytest.mark.skip(reason="LACUNA lg-disabled-boundary-evidence — evidence deliberately disabled")
def test_pinned_import_boundary():
    assert pinned_import("json") == "json" and "import-allowlist"
```

- [ ] **Step 4: Create `specimen/policy_boundaries.py`** with placeholder fingerprints, then compute the real ones:

```python
"""Planted Legis lacuna — @policy_boundary metadata vs behavioural evidence.

``validated_recovery`` is the HEALTHY boundary: its evidence test runs and
asserts the suppressed policy. ``pinned_import`` is the LACUNA
(lg-disabled-boundary-evidence): its evidence test is @pytest.mark.skip, so
`legis policy-boundary-check` flags POLICY_BOUNDARY_TEST_DISABLED. Permanent
demonstration fixtures — do not "fix" either.
"""

from __future__ import annotations

from legis.policy.decorator import policy_boundary


@policy_boundary(
    source="docs/flaws/lg-disabled-boundary-evidence.md",
    suppresses=("no-broad-except",),
    invariant="catalog payloads are type-validated before recovery handling is allowed",
    test_ref="tests/test_policy_boundaries.py::test_validated_recovery_boundary",
    test_fingerprint="FILL-ME",
)
def validated_recovery(payload: dict) -> dict:
    if not isinstance(payload, dict):
        raise TypeError("payload must be a dict")
    return payload


@policy_boundary(
    source="docs/flaws/lg-disabled-boundary-evidence.md",
    suppresses=("import-allowlist",),
    invariant="plugin imports are pinned to the catalog allowlist",
    test_ref="tests/test_policy_boundaries.py::test_pinned_import_boundary",
    test_fingerprint="FILL-ME",
)
def pinned_import(name: str) -> str:
    """LACUNA (lg-disabled-boundary-evidence): the evidence test is skip-marked."""
    if name not in {"json", "csv"}:
        raise ValueError("import not allowlisted")
    return name
```

Then compute both fingerprints with the helper found in Step 2, e.g.:
`.venv/bin/python -c "from legis.policy.<module> import fingerprint_source; print(fingerprint_source('tests/test_policy_boundaries.py::test_validated_recovery_boundary'))"` (exact signature per Step 2), and replace both `FILL-ME` values.

- [ ] **Step 5: Verify the check discriminates**

Run: `/home/john/.local/bin/legis policy-boundary-check <root args from Step 2 pointing at specimen/>; echo exit=$?`
Expected: `exit=1`; output names `pinned_import` with `POLICY_BOUNDARY_TEST_DISABLED`; does NOT name `validated_recovery`. If `validated_recovery` is also flagged, fix per the reason code (fingerprint drift → recompute; weak assert → keep the policy string inside the asserting line, as written).

- [ ] **Step 6: Append the manifest entry**

```toml
[[lacuna]]
id = "lg-disabled-boundary-evidence"
file = "specimen/policy_boundaries.py"
symbol = "pinned_import"
category = "governance"
demonstrates = ["legis"]
explanation = "A @policy_boundary whose evidence test is @pytest.mark.skip — legis policy-boundary-check flags POLICY_BOUNDARY_TEST_DISABLED; the healthy sibling boundary passes, proving the check discriminates."
expected_tool = "legis"
expected_rule = "POLICY_BOUNDARY_TEST_DISABLED"
```

- [ ] **Step 7: Run tests, commit** — `.venv/bin/python -m pytest` → pass (one skip). `git add specimen/policy_boundaries.py tests/test_policy_boundaries.py tour/lacunae.toml pyproject.toml && git commit -m "feat(specimen): lg-disabled-boundary-evidence @policy_boundary pair"`

### Task 7: `legis_policy_check` tour step

**Files:**
- Modify: `tour/steps.py`, `tour/__main__.py`
- Test: `tests/test_steps_legis.py`

- [ ] **Step 1: Write the failing test** (append to `tests/test_steps_legis.py`, using its existing monkeypatch style for subprocess-driven steps):

```python
def test_legis_policy_check_discriminates(monkeypatch):
    from tour import steps

    fake_out = (
        "specimen/policy_boundaries.py:30: POLICY_BOUNDARY_TEST_DISABLED: "
        "specimen.policy_boundaries.pinned_import: evidence test is skip-marked\n"
    )

    class P:
        returncode = 1
        stdout = fake_out
        stderr = ""

    monkeypatch.setattr(steps, "_run", lambda cmd, cwd=None: P())
    monkeypatch.setattr(steps, "_tool", lambda name: "/fake/legis")
    r = steps.legis_policy_check()
    assert r.ok
    assert ("POLICY_BOUNDARY_TEST_DISABLED", "specimen.policy_boundaries.pinned_import") in r.surfaced
```

- [ ] **Step 2: Run to verify failure** — FAIL (`legis_policy_check` not defined).

- [ ] **Step 3: Implement in `tour/steps.py`** (adjust the check's root arguments to what Task 6 Step 2 found; finding-line format is `{file}:{line}: {rule_id}: {qualname}: {reason}` per `legis/src/legis/cli.py:409`):

```python
def legis_policy_check() -> StepResult:
    """Run `legis policy-boundary-check` over the specimen and assert it
    DISCRIMINATES: the disabled-evidence boundary is flagged, the healthy one is not."""
    name = "legis policy-boundary-check"
    legis = _tool("legis")
    if not legis:
        return StepResult(name, ok=False, detail="legis not installed")
    proc = _run([legis, "policy-boundary-check", "--root", "specimen", "--repo-root", str(ROOT)])
    pairs: list[tuple[str, str]] = []
    for line in (proc.stdout or "").splitlines():
        parts = [p.strip() for p in line.split(": ")]
        if len(parts) >= 4 and parts[1].startswith("POLICY_BOUNDARY"):
            pairs.append((parts[1], parts[2]))
    flagged = [q for _, q in pairs]
    ok = (
        proc.returncode == 1
        and any(q.endswith(".pinned_import") for q in flagged)
        and not any(q.endswith(".validated_recovery") for q in flagged)
    )
    return StepResult(
        name,
        ok=ok,
        detail=(
            "boundary-evidence check discriminates: disabled-evidence boundary flagged, "
            "healthy boundary passes"
        ),
        surfaced=tuple(pairs) if ok else (),
    )
```

- [ ] **Step 4: Register** in `tour/__main__.py::_drive` after `steps.legis_govern(),`: add `steps.legis_policy_check(),`.

- [ ] **Step 5: Run live + tests, commit**

```bash
.venv/bin/python -m pytest && .venv/bin/python -m tour tour | grep "policy-boundary"
git add tour/ tests/test_steps_legis.py && git commit -m "feat(tour): legis policy-boundary-check leg"
```
(`docs/tour.md` regenerates again at the wave close — no separate commit needed if you fold it in here; either way `make verify` must pass at the wave close.)

### Task 8: filigree sentinel work-cycle leg

**Files:**
- Modify: `tour/steps.py`, `tour/__main__.py`
- Test: `tests/test_steps.py`

**Background:** drives `http://localhost:8749` (project `lacuna`) with the federation bearer token. Promote is idempotent (`created=false` + linked issue on re-promote). Reopen lands on the most recent non-done predecessor. All HTTP per the filigree dashboard routes: `POST /api/weft/findings/promote`, `POST /api/weft/issues/{id}/reopen`, `POST /api/weft/issues/{id}/claim`, close via `POST /api/weft/issues/{id}/close`, stats via `GET /api/weft/files/stats`, list via `GET /api/weft/issues?priority_min=&priority_max=`.

- [ ] **Step 1: Confirm the auth + route shape live (one-time probe)**

```bash
TOKEN=$(grep -m1 '^WEFT_FEDERATION_TOKEN=' .env | cut -d= -f2)
[ -z "$TOKEN" ] && TOKEN=$(cat ~/.config/filigree/federation_token 2>/dev/null)
curl -s -o /dev/null -w '%{http_code}\n' -H "Authorization: Bearer $TOKEN" "http://localhost:8749/api/p/lacuna/weft/issues?priority_min=0&priority_max=4"
```
Expected: `200`. **Decision rule:** if `.env` lacks the token, the step reads the `~/.config/filigree/federation_token` fallback (add the same fallback in the code below). If the path-scoped `/api/p/lacuna/...` form 404s on a route, use the documented `/api/weft/...` form with the `X-Filigree-Project: lacuna` header instead — record which form worked and use it consistently in Step 3.

- [ ] **Step 2: Write the failing test** (append to `tests/test_steps.py`):

```python
def test_filigree_work_cycle_detail_is_deterministic(monkeypatch):
    from tour import steps

    calls = []

    def fake_api(method, path, token, body=None):
        calls.append((method, path))
        if path.endswith("/findings/promote"):
            return {"issue_id": "lacuna-sentinel1", "status": "closed", "created": False}
        if path.endswith("/reopen"):
            return {"status": "fixing"}
        if path.endswith("/claim"):
            return {"assignee": "tour"}
        if path.endswith("/close"):
            return {"status": "closed"}
        if "files/stats" in path:
            return {"suppressed": {"critical": 10, "high": 20, "medium": 9, "low": 0, "info": 0}}
        if "issues?" in path:
            return [{"id": "lacuna-sentinel1"}]
        raise AssertionError(path)

    monkeypatch.setattr(steps, "_filigree_api", fake_api)
    monkeypatch.setattr(steps, "_federation_token", lambda: "tok")
    monkeypatch.setattr(steps, "_sentinel_fingerprint", lambda: "fp123")
    r = steps.filigree_work_cycle()
    assert r.ok
    assert "sentinel issue cycled" in r.detail
    assert "lacuna-sentinel1" not in r.detail  # live ids must never enter the locked narrative
```

- [ ] **Step 3: Run to verify failure**, then implement in `tour/steps.py`:

```python
FILIGREE_BASE = "http://localhost:8749"


def _federation_token() -> str | None:
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.startswith("WEFT_FEDERATION_TOKEN="):
                value = line.split("=", 1)[1].strip()
                if value:
                    return value
    fallback = Path.home() / ".config" / "filigree" / "federation_token"
    if fallback.exists():
        return fallback.read_text().strip() or None
    return None


def _sentinel_fingerprint() -> str | None:
    """The sentinel is the (sole, unbaselined) PY-WL-125 finding in findings.jsonl."""
    path = ROOT / "findings.jsonl"
    if not path.exists():
        return None
    for line in path.read_text().splitlines():
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if obj.get("rule_id") == "PY-WL-125":
            return obj.get("fingerprint")
    return None


def _filigree_api(method: str, path: str, token: str, body: dict | None = None) -> object:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        f"{FILIGREE_BASE}{path}",
        data=data,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
        method=method,
    )
    with urllib.request.urlopen(req, timeout=5.0) as resp:
        return json.loads(resp.read())


def filigree_work_cycle() -> StepResult:
    """Cycle ONE sentinel issue through the tracker work lifecycle.

    Run 1: promote the unbaselined PY-WL-125 sentinel finding -> bug at triage,
    claim (actor alone — FIL-3), close. Runs 2+: promote is idempotent (same
    issue, created=false) -> reopen -> claim -> close. Also asserts the two new
    query surfaces: priority-range filter and the suppressed-severity rollup.
    Detail is a STABLE sentence — live ids/counts would flap the verify lockstep.
    """
    name = "filigree work cycle"
    token = _federation_token()
    fp = _sentinel_fingerprint()
    if not token or not fp:
        return StepResult(name, ok=False, detail="sentinel cycle unavailable (token or sentinel finding missing)")
    try:
        promoted = _filigree_api("POST", "/api/p/lacuna/weft/findings/promote", token, {
            "scan_source": "wardline", "fingerprint": fp,
            "labels": ["tour-sentinel"], "actor": "tour",
        })
        issue_id = promoted["issue_id"]
        if not promoted.get("created") and promoted.get("status") == "closed":
            _filigree_api("POST", f"/api/p/lacuna/weft/issues/{issue_id}/reopen", token, {"actor": "tour"})
        _filigree_api("POST", f"/api/p/lacuna/weft/issues/{issue_id}/claim", token, {"actor": "tour"})
        _filigree_api("POST", f"/api/p/lacuna/weft/issues/{issue_id}/close", token, {
            "actor": "tour", "reason": "tour sentinel cycle complete",
        })
        ranged = _filigree_api("GET", "/api/p/lacuna/weft/issues?priority_min=0&priority_max=4", token)
        stats = _filigree_api("GET", "/api/p/lacuna/weft/files/stats", token)
        suppressed = stats.get("suppressed", {}) if isinstance(stats, dict) else {}
        rollup_ok = sum(int(v) for v in suppressed.values()) > 0
        listed_ok = isinstance(ranged, list) and len(ranged) > 0
        ok = rollup_ok and listed_ok
        return StepResult(
            name, ok=ok,
            detail=(
                "sentinel issue cycled: promote (idempotent) → claim by actor → close; "
                "priority-range filter and suppressed-severity rollup asserted"
            ),
        )
    except (urllib.error.HTTPError, urllib.error.URLError, OSError,
            json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        return StepResult(name, ok=False, detail=f"sentinel cycle failed: {exc}")
```

Adjust the five paths to whichever form Step 1's probe validated (path-scoped `/api/p/lacuna/...` vs header-scoped). If `claim` rejects actor-alone, pass `{"actor": "tour", "assignee": "tour"}` — but first re-check against `a2ccde6` (actor-alone is the FIL-3 feature being demoed).

- [ ] **Step 4: Register** in `_drive` after `steps.filigree_findings(),`: add `steps.filigree_work_cycle(),`. Run `.venv/bin/python -m pytest` → pass.

- [ ] **Step 5: Live run twice (first-run create, second-run reopen), commit**

```bash
.venv/bin/python -m tour tour | grep "work cycle"   # run 1: creates the sentinel issue
.venv/bin/python -m tour tour | grep "work cycle"   # run 2: reopen path — must be ok too
/home/john/.local/bin/filigree list --json | grep -c tour-sentinel   # exactly 1 sentinel issue
git add tour/ tests/test_steps.py && git commit -m "feat(tour): filigree sentinel work-cycle leg (FIL-3 claim-by-actor, N-6 ranges, suppressed rollup)"
```

### Task 9: quarantine dir + wardline fail-closed leg

**Files:**
- Create: `specimen_quarantine/unparseable.py`, `specimen_quarantine/README.md`
- Modify: `tour/steps.py`, `tour/__main__.py`, `tour/lacunae.toml`
- Test: `tests/test_steps.py`

- [ ] **Step 1: Create the quarantine fixtures**

`specimen_quarantine/README.md`:
```markdown
# specimen_quarantine — deliberately broken inputs

Committed fixtures for the FAIL-CLOSED tour legs. Excluded from the main
wardline scan root (weft.toml), pytest (testpaths), and the package build.
The tour scans/feeds these expecting the gate to TRIP — a quarantine gate
that passes is a verify failure.
```

`specimen_quarantine/unparseable.py`:
```python
"""LACUNA (wl-unparseable): a committed parse failure — wardline's fail-closed
analyzer surfaces WLN-ENGINE-PARSE-ERROR and --fail-on-unanalyzed trips the gate."""
def broken(:
```

- [ ] **Step 2: Confirm exclusion + direct-scan trip**

```bash
make scan; echo main=$?                 # main gate still green (excluded in Task 3's weft.toml)
cd /home/john/lacuna && /home/john/.local/bin/wardline scan specimen_quarantine --fail-on-unanalyzed --output /tmp/q.jsonl; echo quarantine=$?
grep -c WLN-ENGINE-PARSE-ERROR /tmp/q.jsonl
```
Expected: `main=0`, `quarantine=1`, grep `>= 1`. If `--output` is not a valid scan flag, check `wardline scan --help` for the findings-output option and adjust here and in Step 4.

- [ ] **Step 3: Write the failing test** (append to `tests/test_steps.py`):

```python
def test_wardline_fail_closed_requires_trip(monkeypatch, tmp_path):
    from tour import steps

    out = tmp_path / "q.jsonl"
    out.write_text('{"rule_id": "WLN-ENGINE-PARSE-ERROR", "qualname": ""}\n')

    class P:
        returncode = 1
        stdout = ""
        stderr = ""

    monkeypatch.setattr(steps, "_tool", lambda name: "/fake/wardline")
    monkeypatch.setattr(steps.subprocess, "run", lambda *a, **k: P())
    monkeypatch.setattr(steps.tempfile, "TemporaryDirectory", lambda: _FakeTmp(tmp_path))
    r = steps.wardline_fail_closed()
    assert r.ok
    assert ("WLN-ENGINE-PARSE-ERROR", "specimen_quarantine.unparseable") in r.surfaced


class _FakeTmp:
    def __init__(self, p):
        self.p = p
    def __enter__(self):
        return str(self.p)
    def __exit__(self, *exc):
        return False
```

- [ ] **Step 4: Implement in `tour/steps.py`**:

```python
def wardline_fail_closed() -> StepResult:
    """Scan the quarantine dir expecting the gate to TRIP (fail-closed analyzer).

    The unparseable file must produce WLN-ENGINE-PARSE-ERROR and
    --fail-on-unanalyzed must exit 1. A quarantine scan that PASSES is a failure.
    The surfaced qualname is synthesized from the fixture path (parse-error FACTs
    carry no qualname).
    """
    name = "wardline fail-closed gate"
    wardline = _tool("wardline")
    if not wardline:
        return StepResult(name, ok=False, detail="wardline not installed")
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "quarantine.jsonl"
        proc = subprocess.run(
            [wardline, "scan", str(ROOT / "specimen_quarantine"),
             "--fail-on-unanalyzed", "--output", str(out)],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        rules = {r for r, _ in pairs_from_findings(out)}
    tripped = proc.returncode == 1 and "WLN-ENGINE-PARSE-ERROR" in rules
    return StepResult(
        name,
        ok=tripped,
        detail="unparseable specimen trips the gate: WLN-ENGINE-PARSE-ERROR, exit 1 (fail-closed, not silent)",
        surfaced=(("WLN-ENGINE-PARSE-ERROR", "specimen_quarantine.unparseable"),) if tripped else (),
    )
```

- [ ] **Step 5: Manifest entry + register + commit**

```toml
[[lacuna]]
id = "wl-unparseable"
file = "specimen_quarantine/unparseable.py"
symbol = "unparseable"
category = "fail-closed"
demonstrates = ["wardline"]
explanation = "A committed parse failure in the quarantine dir; the fail-closed analyzer surfaces WLN-ENGINE-PARSE-ERROR and --fail-on-unanalyzed trips the gate (exit 1). The demo asserts the FAILURE."
expected_tool = "wardline"
expected_rule = "WLN-ENGINE-PARSE-ERROR"
expected_kind = "gate-trip"
scan_target = "specimen_quarantine"
```

Register `steps.wardline_fail_closed(),` in `_drive` after `steps.wardline_scan(),`. Run `.venv/bin/python -m pytest && make scan` → pass/0. Commit: `git add specimen_quarantine/ tour/ tests/test_steps.py && git commit -m "feat(tour): wl-unparseable quarantine + fail-closed gate leg"`

### Task 10: legis G1 negative leg (`lg-zero-under-green`)

**Files:**
- Create: `specimen_quarantine/malformed_artifact.json` (generated from a real artifact)
- Modify: `tour/steps.py`, `tour/__main__.py`, `tour/lacunae.toml`
- Test: `tests/test_steps_legis.py`

- [ ] **Step 1: Generate the committed malformed artifact** (real artifact shape, minus `findings`, minus signature so the shape is stable/committable):

```bash
.venv/bin/python - <<'EOF'
import json, subprocess, tempfile, pathlib
with tempfile.TemporaryDirectory() as tmp:
    out = pathlib.Path(tmp) / "scan.legis.json"
    subprocess.run(["/home/john/.local/bin/wardline", "scan", ".", "--format", "legis",
                    "--output", str(out)], check=False, capture_output=True)
    art = json.loads(out.read_text())
art.pop("findings", None)
art.pop("artifact_signature", None)
pathlib.Path("specimen_quarantine/malformed_artifact.json").write_text(
    json.dumps(art, indent=2, sort_keys=True) + "\n")
print("keys:", sorted(art.keys()))
EOF
```
Expected: file written; `findings` absent from printed keys. (Requires a clean tree for signing — but we strip the signature anyway, so a dirty-tree unsigned run is fine; if `--format legis` refuses entirely, commit WIP first, generate, then amend.)

- [ ] **Step 2: Write the failing test** (append to `tests/test_steps_legis.py`, reusing that file's existing fake-server style if present; otherwise this monkeypatch form):

```python
def test_legis_reject_malformed_requires_422(monkeypatch):
    import urllib.error
    from tour import steps

    monkeypatch.setattr(steps, "_tool", lambda name: "/fake/legis")
    monkeypatch.setattr(steps, "_spawn_legis_server", lambda env: ("proc", 9999))
    monkeypatch.setattr(steps, "_teardown", lambda proc: None)

    def fake_post(port, body, token):
        raise urllib.error.HTTPError("u", 422, "Unprocessable", {}, None)

    monkeypatch.setattr(steps, "_post_scan_results", fake_post)
    r = steps.legis_reject_malformed()
    assert r.ok
    assert ("artifact-missing-findings-rejected", "specimen_quarantine.malformed_artifact") in r.surfaced
```

- [ ] **Step 3: Implement.** First refactor the throwaway-server plumbing out of `legis_govern` into three helpers it then calls (pure extraction — `legis_govern` behavior unchanged):

```python
def _spawn_legis_server(env: dict) -> tuple[subprocess.Popen, int]:
    """Start a loopback throwaway `legis serve`; returns (proc, port). Raises OSError if unhealthy."""
    legis = _tool("legis")
    port = _free_port()
    proc = subprocess.Popen(
        [legis, "serve", "--host", "127.0.0.1", "--port", str(port),
         "--governance-db", env.pop("_GOV_DB")],
        cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    if not _wait_health(port):
        proc.terminate()
        raise OSError("legis serve did not become healthy")
    return proc, port


def _post_scan_results(port: int, body: dict, token: str) -> dict:
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/wardline/scan-results",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=5.0) as resp:
        return json.loads(resp.read())


def _teardown(proc: subprocess.Popen | None) -> None:
    if proc is not None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
```

Then the new step:

```python
def legis_reject_malformed() -> StepResult:
    """Feed legis an artifact whose `findings` key is ABSENT and assert the G1
    fail-closed rejection (HTTP 422) — never zero-defects-under-green."""
    name = "legis reject malformed artifact"
    if not _tool("legis"):
        return StepResult(name, ok=False, detail="legis not installed")
    fixture = ROOT / "specimen_quarantine" / "malformed_artifact.json"
    if not fixture.exists():
        return StepResult(name, ok=False, detail="malformed artifact fixture missing")
    proc = None
    try:
        artifact = json.loads(fixture.read_text())
        api_secret = secrets.token_hex(16)
        with tempfile.TemporaryDirectory() as tmp:
            env = {**os.environ, "LEGIS_WARDLINE_CELL": "surface_override",
                   "LEGIS_API_SECRET": api_secret, "_GOV_DB": f"sqlite:///{Path(tmp)}/gov.db"}
            proc, port = _spawn_legis_server(env)
            try:
                _post_scan_results(port, {"agent_id": "lacuna-tour", "scan": artifact}, api_secret)
                return StepResult(name, ok=False, detail="malformed artifact was ACCEPTED — fail-closed contract broken")
            except urllib.error.HTTPError as err:
                if err.code == 422:
                    return StepResult(
                        name, ok=True,
                        detail="absent findings key REJECTED (HTTP 422) — fail-closed, never zero-under-green",
                        surfaced=(("artifact-missing-findings-rejected", "specimen_quarantine.malformed_artifact"),),
                    )
                return StepResult(name, ok=False, detail=f"unexpected rejection status {err.code}")
    except (urllib.error.URLError, OSError, json.JSONDecodeError, ValueError) as exc:
        return StepResult(name, ok=False, detail=f"negative leg failed: {exc}")
    finally:
        _teardown(proc)
```

- [ ] **Step 4: Manifest entry + register**

```toml
[[lacuna]]
id = "lg-zero-under-green"
file = "specimen_quarantine/malformed_artifact.json"
symbol = "malformed_artifact"
category = "fail-closed"
demonstrates = ["legis", "wardline+legis"]
explanation = "A wardline scan artifact with the findings key ABSENT; legis rejects it (HTTP 422, G1) instead of routing zero defects under green. The demo asserts the REJECTION."
expected_tool = "legis"
expected_rule = "artifact-missing-findings-rejected"
expected_kind = "gate-trip"
scan_target = "specimen_quarantine"
```

Register `steps.legis_reject_malformed(),` in `_drive` after `steps.legis_policy_check(),`.

- [ ] **Step 5: Wave-2 close**

```bash
.venv/bin/python -m pytest                  # all pass
git add -A && git commit -m "feat(tour): lg-zero-under-green G1 negative leg"
make tour && git add docs/ && git commit -m "chore(tour): Wave-2 docs regen (39 lacunae, 4 new legs)"
make ci                                      # exit 0 — Wave 2 lands green
```

---

## Wave 3 — the Rust wing

### Task 11: pin the wardline Rust trust-marker dialect (verification-first)

- [x] **Step 1: Find the marker syntax in wardline's own corpus**

Run: `grep -rn "@trusted" /home/john/wardline/tests/ /home/john/wardline/src/wardline/rust/ --include='*.rs' --include='*.py' -l | head` then open the smallest conformance fixture it points to.
Expected: the exact doc-comment / attribute forms for (a) marking a fn trusted (`/// @trusted` per `src/wardline/rust/analyzer.py`) and (b) marking the untrusted SOURCE (how `RustTrustProvider` seeds external input — e.g. an `@external`-style marker or built-in sources like `std::env::args`). Record both; Task 12's specimen uses them verbatim. **Do not guess** — copy from a fixture that the wardline test suite asserts RS-WL-108 against.

**PINNED DIALECT (verified 2026-06-12 against `/home/john/wardline`):**

- **(a) Trusted-fn marker:** `/// @trusted(level=ASSURED)` (or `GUARDED`) — an outer doc comment whose text *leads* with the directive, on the contiguous doc-comment/attribute run immediately preceding the `fn`. Ground truth: `tests/corpus/rust/command_sink.rs` (every RS-WL-108/112 positive in the corpus carries exactly `/// @trusted(level=ASSURED)`; asserted by `tests/unit/rust/test_corpus.py`) and `src/wardline/rust/provider.py` (`_MARKER = re.compile(r"\s*@trusted\s*\(\s*level\s*=\s*(\w+)\s*\)")`, applied with `re.match` — start-anchored). Pitfalls: a bare `/// @trusted` (no `(level=...)`) does **not** match and is silently ignored, leaving the fn unmarked; an invalid level word raises `ValueError`; only `ASSURED`/`GUARDED` are declarable.
- **(b) Untrusted source:** there is **no source marker**. `RustTrustProvider` seeds *declared trust only*; taint sources are built-in vocabulary rows in `src/wardline/rust/rust_taint.yaml`: `env::var`, `env::var_os`, `env::args`, `env::vars`, `fs::read_to_string`, `fs::read` → `EXTERNAL_RAW` (matched by trailing path segments, so `std::env::args(...)` qualifies). **The taint model is flat-local (intra-procedural)** — `rust_taint.yaml`'s own v2 comment names "the flat-local taint model", and every RS-WL-108/112 positive in `tests/corpus/rust/command_sink.rs` calls the source *inside* the same `@trusted` fn as the sink. Taint does **not** cross fn boundaries via parameters or return values: a separate `fn read_operator_arg()` feeding the trusted fns through `main` produces ZERO findings (live-verified 2026-06-12 — only WLN-RUST-COVERAGE). The vocabulary source call must therefore live in the same fn body as the sink.
- **Re-verification (2026-06-12, live scratch crate):** an exact replica of Task 12's main.rs below (source inlined per-fn), scanned with `wardline scan . --lang rust`, fired both `RS-WL-108` (qualname `specimen_rs.run_export`) and `RS-WL-112` (qualname `specimen_rs.shell_archive`); the control with the source hoisted into a helper fn fired neither. `cargo check` exit 0 on the replica.

### Task 12: `specimen-rs/` crate with five lacunae

**Files:**
- Create: `specimen-rs/Cargo.toml`, `specimen-rs/src/main.rs`, `specimen-rs/src/catalog.rs`, `specimen-rs/src/shelf_layout.rs`
- Modify: `tour/lacunae.toml`, `weft.toml` (if needed: keep `specimen-rs/target` excluded — wardline already skips `target` in rust mode)

- [ ] **Step 1: Create the crate** (trust markers below are Task 11's verified, pinned dialect — use verbatim):

`specimen-rs/Cargo.toml`:
```toml
[package]
name = "specimen_rs"
version = "0.1.0"
edition = "2021"
```

`specimen-rs/src/main.rs`:
```rust
//! The Rust wing of the lacuna specimen: a clean-cored catalog CLI slice with
//! five INTENTIONAL, catalogued flaws (see tour/lacunae.toml). Do NOT fix them.

use std::process::Command;

mod catalog;
#[path = "shelf_layout.rs"]
mod shelving; // LACUNA (rs-path-mount): #[path] module mount — loomweave routes it (ADR-049 Am.8)

/// @trusted(level=ASSURED)
fn run_export() {
    // LACUNA (RS-WL-108): operator input reaches the program slot of Command::new.
    // `std::env::args` is a built-in EXTERNAL_RAW vocabulary source (rust_taint.yaml);
    // it must be called HERE — wardline's Rust taint model is flat-local, so taint
    // does not cross fn boundaries via parameters.
    let prog = std::env::args().nth(1).unwrap_or_default();
    Command::new(prog).status().ok();
}

/// @trusted(level=ASSURED)
fn shell_archive() {
    // LACUNA (RS-WL-112): operator input reaches a `sh -c` command line.
    let line = std::env::args().nth(2).unwrap_or_default();
    Command::new("sh").arg("-c").arg(line).status().ok();
}

fn main() {
    run_export();
    shell_archive();
    println!("{}", catalog::summary());
    println!("{}", shelving::label());
}
```

`specimen-rs/src/catalog.rs`:
```rust
//! Clean-core catalog module — plus the two archaeology lacunae.

/// In-project trait so the derives edge resolves in-project (resolved-or-dropped contract).
pub trait Catalogued {
    fn shelf(&self) -> &'static str;
}

// LACUNA (rs-cfg-twin): two mutually-exclusive #[cfg] impls of the same type
// split into @cfg(...) qualname twins in the loomweave index.
pub struct Shelf;

#[cfg(feature = "metric")]
impl Shelf {
    pub fn capacity(&self) -> u32 { 100 }
}

#[cfg(not(feature = "metric"))]
impl Shelf {
    pub fn capacity(&self) -> u32 { 80 }
}

// LACUNA (rs-derives): a derive invocation naming the in-project trait — the
// anchored `derives` edge. Lives under a disabled cfg so `cargo check` never
// name-resolves it (no proc-macro needed) while tree-sitter still extracts it.
#[cfg(feature = "archaeology_specimen")]
mod derive_demo {
    #[derive(Catalogued)]
    pub struct Pamphlet;
}

pub fn summary() -> String {
    format!("shelf capacity: {}", Shelf.capacity())
}
```

`specimen-rs/src/shelf_layout.rs`:
```rust
//! Mounted via `#[path = "shelf_layout.rs"] mod shelving;` in main.rs (rs-path-mount).

pub fn label() -> &'static str {
    "shelving: mounted via #[path]"
}
```

- [ ] **Step 2: Compile gate** — `cd specimen-rs && cargo check -q; echo $?` → `0`. If the cfg'd-out `#[derive(Catalogued)]` still fails name resolution under `cargo check` (it should not — disabled-cfg items are parsed, not resolved), fall back: change `rs-derives` to assert a `references` edge instead (Catalogued used in a fn signature) and update the manifest entry accordingly.

- [ ] **Step 3: Verify both scanners see the crate**

```bash
/home/john/.local/bin/wardline scan . --lang rust --output /tmp/rs.jsonl 2>&1 | tail -1
grep -o 'RS-WL-1[01][28]' /tmp/rs.jsonl | sort -u
/home/john/.local/bin/loomweave analyze . >/dev/null 2>&1
sqlite3 .weft/loomweave/loomweave.db "select count(*) from entities where qualified_name like 'specimen_rs%';"
sqlite3 .weft/loomweave/loomweave.db "select qualified_name from entities where qualified_name like '%@cfg%';"
sqlite3 .weft/loomweave/loomweave.db "select count(*) from edges where kind='derives';"
```
Expected: `RS-WL-108` and `RS-WL-112` both present; entity count > 0; at least two `@cfg(...)` qualname twins; derives count ≥ 1. **Decision rules:** taint rules silent → re-check Task 11's source/trusted markers against the wardline fixture. Derives count 0 → apply Step 2's references-edge fallback. Column names differ → adapt queries (schema from Task 3 Step 3).

- [ ] **Step 4: Baseline the two Rust taint findings — investigate scope first**

Run: `head -5 .weft/wardline/baseline.yaml` and `git diff --stat .weft/wardline/baseline.yaml` after a trial `wardline baseline update` **immediately following a `--lang rust` scan**.
**Decision rule:** if `baseline update` re-derives from only the last scan run (python rows vanish), revert (`git checkout .weft/wardline/baseline.yaml`) and instead hand-append the two RS-WL rows in the existing YAML row format (copy a python row's shape, substitute the rust finding's fingerprint/rule/path from `/tmp/rs.jsonl`). Confirm: `wardline scan . --lang rust --fail-on ERROR --trust-suppressions; echo $?` → `0`, and the python scan also still exits 0.

- [ ] **Step 5: Manifest entries (note `lang = "rust"`), commit**

```toml
[[lacuna]]
id = "rs-untrusted-command"
file = "specimen-rs/src/main.rs"
symbol = "run_export"
category = "injection"
demonstrates = ["wardline"]
explanation = "Operator input reaches the program slot of Command::new inside a /// @trusted(level=ASSURED) fn — Rust program injection."
expected_tool = "wardline"
expected_rule = "RS-WL-108"
lang = "rust"

[[lacuna]]
id = "rs-untrusted-shell"
file = "specimen-rs/src/main.rs"
symbol = "shell_archive"
category = "injection"
demonstrates = ["wardline"]
explanation = "Operator input reaches a `sh -c` command line — Rust shell injection."
expected_tool = "wardline"
expected_rule = "RS-WL-112"
lang = "rust"

[[lacuna]]
id = "rs-derives"
file = "specimen-rs/src/catalog.rs"
symbol = "Pamphlet"
category = "archaeology"
demonstrates = ["loomweave"]
explanation = "A derive invocation naming the in-project trait Catalogued — the anchored `derives` edge (ontology 0.5.0+), extracted from a cfg-disabled module tree-sitter still sees."
expected_tool = "loomweave"
expected_rule = "derives-edge"
lang = "rust"

[[lacuna]]
id = "rs-cfg-twin"
file = "specimen-rs/src/catalog.rs"
symbol = "Shelf"
category = "archaeology"
demonstrates = ["loomweave"]
explanation = "Two mutually-exclusive #[cfg] impls of Shelf split into @cfg(...) qualname twins (ADR-049 Am.5) instead of colliding."
expected_tool = "loomweave"
expected_rule = "cfg-twin"
lang = "rust"

[[lacuna]]
id = "rs-path-mount"
file = "specimen-rs/src/main.rs"
symbol = "shelving"
category = "archaeology"
demonstrates = ["loomweave"]
explanation = "A #[path = \"shelf_layout.rs\"] module mount; loomweave routes the mounted file under the declaring module (ADR-049 Am.8)."
expected_tool = "loomweave"
expected_rule = "path-mount"
lang = "rust"
```

`git add specimen-rs/ tour/lacunae.toml .weft/wardline/baseline.yaml && git commit -m "feat(specimen-rs): Rust wing — 2 taint + 3 archaeology lacunae (baselined)"`

### Task 13: Rust tour legs

**Files:**
- Modify: `tour/steps.py`, `tour/__main__.py`
- Test: `tests/test_steps.py`

- [ ] **Step 1: Write the failing tests** (append to `tests/test_steps.py`):

```python
def test_rust_archaeology_emits_harness_tokens(tmp_path):
    import sqlite3
    from tour import steps

    db = tmp_path / "loomweave.db"
    con = sqlite3.connect(db)
    con.execute("create table entities (qualified_name text, kind text)")
    con.execute("create table edges (kind text, src text, dst text)")
    rows = [
        ("specimen_rs.catalog.Shelf.capacity@cfg(feature=metric)", "function"),
        ("specimen_rs.catalog.Shelf.capacity@cfg(not(feature=metric))", "function"),
        ("specimen_rs.shelving.label", "function"),
        ("specimen_rs.catalog.derive_demo.Pamphlet", "struct"),
    ]
    con.executemany("insert into entities values (?, ?)", rows)
    con.execute("insert into edges values ('derives', 'specimen_rs.catalog.derive_demo.Pamphlet', 'specimen_rs.catalog.Catalogued')")
    con.commit(); con.close()

    r = steps.rust_archaeology(db_path=db)
    assert r.ok
    assert ("cfg-twin", "specimen_rs.catalog.Shelf") in r.surfaced
    assert ("path-mount", "specimen_rs.shelving") in r.surfaced
    assert ("derives-edge", "specimen_rs.catalog.derive_demo.Pamphlet") in r.surfaced


def test_rust_scan_surfaces_rs_rules(monkeypatch, tmp_path):
    from tour import steps

    out_lines = (
        '{"rule_id": "RS-WL-108", "qualname": "specimen_rs.run_export"}\n'
        '{"rule_id": "RS-WL-112", "qualname": "specimen_rs.shell_archive"}\n'
    )

    class P:
        returncode = 0
        stdout = ""
        stderr = ""

    def fake_run(cmd, **kw):
        idx = cmd.index("--output")
        steps.Path(cmd[idx + 1]).write_text(out_lines)
        return P()

    monkeypatch.setattr(steps, "_tool", lambda name: "/fake/wardline")
    monkeypatch.setattr(steps.subprocess, "run", fake_run)
    r = steps.rust_scan()
    assert r.ok
    assert ("RS-WL-108", "specimen_rs.run_export") in r.surfaced
```

NOTE: the fixture column names/qualname dialect above are the candidate shapes — replace them with what Task 12 Step 3's live queries actually returned (the real `@cfg` suffix text, the mounted module's real qualified name, the real edges columns) so the test pins reality, not hope.

- [ ] **Step 2: Run to verify failure**, then implement in `tour/steps.py`:

```python
def rust_scan() -> StepResult:
    """Wardline's Rust frontend over the same tree (`--lang rust`)."""
    name = "wardline scan (rust)"
    wardline = _tool("wardline")
    if not wardline:
        return StepResult(name, ok=False, detail="wardline not installed")
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "rust.jsonl"
        proc = subprocess.run(
            [wardline, "scan", ".", "--lang", "rust", "--output", str(out)],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        pairs = pairs_from_findings(out)
    rules = sorted({r for r, _ in pairs})
    return StepResult(
        name,
        ok=proc.returncode in (0, 1) and bool(pairs),
        detail=f"surfaced rules: {', '.join(rules) or '(none)'}",
        surfaced=pairs,
    )


def rust_archaeology(db_path: Path = LOOMWEAVE_DB) -> StepResult:
    """Rust index facts: @cfg qualname twins, the #[path]-mounted module, and the
    in-project derives edge — emitted as harness tokens (like dead-entity)."""
    name = "loomweave rust archaeology"
    pairs: list[tuple[str, str]] = []
    if Path(db_path).exists():
        try:
            con = sqlite3.connect(str(db_path))
            try:
                twins = con.execute(
                    "select qualified_name from entities where qualified_name like 'specimen_rs%@cfg%'"
                ).fetchall()
                mounted = con.execute(
                    "select qualified_name from entities where qualified_name like 'specimen_rs.shelving%'"
                ).fetchall()
                derive_edges = con.execute(
                    "select src from edges where kind = 'derives' and src like 'specimen_rs%'"
                ).fetchall()
            finally:
                con.close()
        except sqlite3.Error:
            twins, mounted, derive_edges = [], [], []
        if len(twins) >= 2:
            base = twins[0][0].split("@cfg")[0].rsplit(".", 1)[0]
            pairs.append(("cfg-twin", base))
        if mounted:
            pairs.append(("path-mount", "specimen_rs.shelving"))
        for (src,) in derive_edges:
            pairs.append(("derives-edge", src))
        # The ::-dialect demo (spec Wave 3): resolve a PASTED Rust path the way
        # entity_resolve does — normalize `::` to `.` and hit the index.
        pasted = "specimen_rs::shelving::label"
        if Path(db_path).exists():
            try:
                con = sqlite3.connect(str(db_path))
                try:
                    hit = con.execute(
                        "select count(*) from entities where qualified_name = ?",
                        (pasted.replace("::", "."),),
                    ).fetchone()[0]
                finally:
                    con.close()
            except sqlite3.Error:
                hit = 0
            if hit:
                pairs.append(("colon-path-resolved", pasted.replace("::", ".")))
    pairs = list(dict.fromkeys(pairs))
    tokens = sorted({t for t, _ in pairs})
    return StepResult(
        name,
        ok=len(pairs) >= 3,
        detail=f"rust index facts: {', '.join(tokens) or '(none)'}",
        surfaced=tuple(pairs),
    )
```

Adjust both queries/derivations to the REAL schema and qualname dialect from Task 12 Step 3 (e.g. if rust qualnames keep `::` in storage, match on that and normalize for the pair the same way the test fixture does).

- [ ] **Step 3: Register** both in `_drive` (rust_scan after `wardline_fail_closed`, rust_archaeology after `loomweave_findings`). Run `.venv/bin/python -m pytest` → pass.

- [ ] **Step 4: Live check** — `.venv/bin/python -m tour tour | tail -5` → `Not surfaced: []` (all 44).

- [ ] **Step 5: Commit** — `git add tour/ tests/test_steps.py && git commit -m "feat(tour): rust scan + archaeology legs"`

### Task 14: Makefile wiring + Wave-3 close

**Files:**
- Modify: `Makefile`

- [ ] **Step 1: Add the Rust scan line and the capability-gated cargo check**

In `Makefile`, change the `scan` target and add `cargo-check`, extending `ci`:

```makefile
scan:
	# Trusted local checkout: the repo-owned baseline (deliberate planted
	# specimen flaws) is allowed to clear the gate. CI-on-PR should instead
	# scope to new findings with `--new-since <merge-base>`.
	$(WARDLINE) scan . --fail-on ERROR --trust-suppressions
	$(WARDLINE) scan . --lang rust --fail-on ERROR --trust-suppressions

cargo-check:
	@if command -v cargo >/dev/null 2>&1; then \
	  (cd specimen-rs && cargo check -q) && echo "✓ specimen-rs compiles (cargo check)"; \
	else \
	  echo "⚠ cargo not found — Rust compile check skipped (honest degrade)"; \
	fi

ci: test scan verify cargo-check
```

Also add `cargo-check` to the `.PHONY` line. NOTE: the second scan line overwrites `findings.jsonl` with the rust findings by default — if so, give it `--output findings-rust.jsonl` and add `findings-rust.jsonl` to `.gitignore` ONLY if `findings.jsonl` is itself gitignored; if `findings.jsonl` is tracked, keep both outputs consistent with however the repo currently treats it (check `git check-ignore findings.jsonl` first; mirror that).

- [ ] **Step 2: Wave-3 close**

```bash
make ci                                  # all four legs green
make tour && git add -A && git commit -m "feat(rust-wing): make scan rust leg + gated cargo check; Wave-3 docs regen (44 lacunae)"
make ci                                  # still green post-commit (signed legis leg needs the clean tree)
```

- [ ] **Step 3: Final acceptance sweep**

```bash
.venv/bin/python -m tour verify; echo $?          # 0
grep -c '\[\[lacuna\]\]' tour/lacunae.toml         # 44
ls docs/flaws | wc -l                              # 44
/home/john/.local/bin/filigree list --json | grep -c tour-sentinel   # 1
```

---

## Self-review notes (resolved during planning)

- The nesting bomb is **wardline-excluded** (weft.toml) because wardline's fail-closed analyzer would otherwise convert a per-file abort on it into a gate-eligible ERROR.
- The duplicate-locator construct uses same-named **classes** (not modules) across `colliding.py`/`colliding/__init__.py` — module dual-claims are carved out of the alarm.
- `loomweave_findings` / `rust_archaeology` DB column names are pinned by live inspection (Task 3 Step 3 / Task 12 Step 3) before the step code and its test fixtures are finalized.
- `legis_govern` is refactored to share `_spawn_legis_server`/`_post_scan_results`/`_teardown` with the G1 negative leg (pure extraction; its tests must stay green).
- Tour `detail` strings are all static sentences — no live counts, ids, or paths (verify is byte-for-byte).
