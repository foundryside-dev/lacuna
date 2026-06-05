# Legis Live Governance Tour Member — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refurbish Lacuna's tour to run the latest Loom tools and add **Legis** as a live governance member that governs the specimen's Wardline scan via the real signed `POST /wardline/scan-results` handshake.

**Architecture:** A new `legis_govern` step in `tour/steps.py` plays the agent role: it runs `wardline scan . --format legis` to produce a (signed-when-keyed) artifact, starts a throwaway `legis serve` with server-owned `surface_override` routing, POSTs the artifact, records the deterministic governed-defect count, and stops the server. Determinism for `make verify` is preserved by locking only the governance outcome in the narrative; the signed/unsigned status rides a non-rendered `note`.

**Tech Stack:** Python 3.12 (stdlib only in the harness: `subprocess`, `json`, `urllib.request`, `socket`, `tempfile`), `uv tool` / `cargo` for installs, pytest.

**Spec:** `docs/superpowers/specs/2026-06-05-legis-tour-member-design.md`

**Conventions:** Work in `/home/john/lacuna`. Commit on a short-lived branch and `git merge --ff-only` to `main` (keep linear history). End commit messages with the `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>` trailer.

---

### Task 1: Install the latest tools into ~/.local/bin

**Files:** none (environment).

- [ ] **Step 1: Install legis (not currently installed) + upgrade filigree/wardline via uv tool**

```bash
uv tool install --force /home/john/legis              # installs `legis` (committed HEAD)
uv tool install --force /home/john/filigree           # 2.3.0 -> 3.0.0 (committed, closure-gate)
uv tool install --force "wardline[scanner,clarion] @ /home/john/wardline"           # working tree -> includes B4a --format legis (scanner+clarion extras required)
```

- [ ] **Step 2: Install the freshly-built clarion 1.3.0 binary (B3)**

```bash
cargo build --release --manifest-path /home/john/clarion/Cargo.toml -p clarion-cli
cp /home/john/clarion/target/release/clarion /home/john/.local/bin/clarion
```

- [ ] **Step 3: Verify versions and the legis-artifact producer exist**

```bash
export PATH="/home/john/.local/bin:$PATH"
legis --help | head -1
clarion --version            # expect: clarion 1.3.0
filigree --version           # expect: 3.x
wardline --version           # expect: 1.0.0rc1
wardline scan --help | grep -- "--format"   # expect choices include: legis
```
Expected: all four resolve; `wardline scan --help` lists `legis` as a `--format` choice.

- [ ] **Step 4: Commit (no repo change; record the install step as a marker commit is unnecessary — skip)**

No commit; this task only changes `~/.local/bin`.

---

### Task 2: Provision the shared artifact secret

**Files:**
- Create: `/home/john/lacuna/.env.example`
- Modify (local, gitignored): `/home/john/lacuna/.env`

- [ ] **Step 1: Add a documented key example (committed)**

Create `/home/john/lacuna/.env.example`:

```bash
# Shared HMAC secret for the Wardline -> Legis signed scan handoff (demo bed).
# Copy to .env (gitignored) and set the SAME 64-hex value on both names.
# Generate: python -c 'import secrets; print(secrets.token_hex(32))'
# When unset, the tour runs the handshake UNSIGNED (legis optional-verify).
WARDLINE_LEGIS_ARTIFACT_KEY=
LEGIS_WARDLINE_ARTIFACT_KEY=
```

- [ ] **Step 2: Provision a real value locally (gitignored .env)**

```bash
cd /home/john/lacuna
KEY="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
printf 'WARDLINE_LEGIS_ARTIFACT_KEY=%s\nLEGIS_WARDLINE_ARTIFACT_KEY=%s\n' "$KEY" "$KEY" >> .env
grep -c ARTIFACT_KEY .env      # expect: 2
git check-ignore .env          # expect: .env  (confirms it is gitignored)
```

- [ ] **Step 3: Commit the example**

```bash
cd /home/john/lacuna
git switch -c feat/legis-tour-member
git add .env.example
git commit -m "feat(tour): document the Wardline->Legis shared artifact secret"
```

---

### Task 3: Promote legis to a live capability

**Files:**
- Modify: `tour/capability.py`
- Test: `tests/test_capability.py`

- [ ] **Step 1: Write the failing test**

Add to `tests/test_capability.py` (create if absent):

```python
from tour.capability import detect


def _fake_which(present):
    return lambda name: f"/home/john/.local/bin/{name}" if name in present else None


def test_legis_is_a_detectable_live_member_when_installed():
    caps = {c.name: c for c in detect(_fake_which({"clarion", "filigree", "wardline", "legis"}))}
    assert "legis" in caps
    assert caps["legis"].available is True
    # charter remains design-only
    assert caps["charter"].available is False


def test_legis_absent_reports_unavailable_not_design_only():
    caps = {c.name: c for c in detect(_fake_which({"clarion", "filigree", "wardline"}))}
    assert caps["legis"].available is False
    assert "design-only" not in caps["legis"].detail
```

- [ ] **Step 2: Run to verify it fails**

Run: `cd /home/john/lacuna && python -m pytest tests/test_capability.py -q`
Expected: FAIL — legis is currently in `DESIGN_ONLY`, so `available` is `False` even when installed, and its detail says "design-only".

- [ ] **Step 3: Implement — move legis out of DESIGN_ONLY into the runnable set**

In `tour/capability.py`:

```python
# Tools that ship a runnable CLI today.
RUNNABLE = ("clarion", "filigree", "wardline", "legis")
# Members that exist in the suite but are not yet first-class here.
DESIGN_ONLY = ("charter",)
```

(No other change — `detect()` already locates `RUNNABLE` names via PATH/`~/.local/bin`.)

- [ ] **Step 4: Run to verify it passes**

Run: `cd /home/john/lacuna && python -m pytest tests/test_capability.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tour/capability.py tests/test_capability.py
git commit -m "feat(tour): detect legis as a live member (no longer design-only)"
```

---

### Task 4: Add a non-rendered `note` to StepResult for the live report

**Files:**
- Modify: `tour/report.py`
- Modify: `tour/__main__.py`
- Test: `tests/test_report.py`

**Why:** the locked narrative (`render_tour_md`) must stay environment-independent for `make verify`. The signed/unsigned artifact status is environment-dependent (depends on `.env`), so it must NOT enter the rendered markdown. A `note` field carries it to the live console only.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_report.py` (create if absent):

```python
from tour.report import StepResult, render_tour_md


def test_note_is_not_rendered_into_locked_markdown():
    r = StepResult("legis govern", ok=True, detail="governed 3 active defects → surface_override",
                   note="artifact: verified")
    md = render_tour_md([r])
    assert "governed 3 active defects → surface_override" in md
    assert "verified" not in md            # note stays OUT of the locked narrative


def test_note_defaults_empty_and_is_optional():
    r = StepResult("x", ok=True, detail="d")
    assert r.note == ""
```

- [ ] **Step 2: Run to verify it fails**

Run: `cd /home/john/lacuna && python -m pytest tests/test_report.py -q`
Expected: FAIL — `StepResult` has no `note` field (TypeError on the keyword).

- [ ] **Step 3: Implement — add `note` field (not rendered)**

In `tour/report.py`, add to `StepResult` after `surfaced`:

```python
    # Environment-dependent live-only detail (e.g. signed/unsigned artifact status).
    # Deliberately NOT rendered into the locked markdown so `make verify` stays
    # byte-for-byte deterministic across machines.
    note: str = ""
```

`render_tour_md` is unchanged (it already reads only `r.name`/`r.ok`/`r.detail`).

- [ ] **Step 4: Print notes in the live tour (not in docs)**

In `tour/__main__.py` `run_tour()`, after `print(render_tour_md(results))` and before the coverage prints, add:

```python
    for r in results:
        if r.note:
            print(f"note [{r.name}]: {r.note}")
```

- [ ] **Step 5: Run to verify it passes**

Run: `cd /home/john/lacuna && python -m pytest tests/test_report.py -q`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add tour/report.py tour/__main__.py tests/test_report.py
git commit -m "feat(tour): add non-rendered StepResult.note for env-dependent live detail"
```

---

### Task 5: The legis_govern step

**Files:**
- Modify: `tour/steps.py`
- Test: `tests/test_steps_legis.py`

- [ ] **Step 1: Write the test (tool-gated integration)**

Create `tests/test_steps_legis.py`:

```python
import shutil

import pytest

from tour import steps


def _tools_present() -> bool:
    return all(
        (steps.BIN / t).exists() or shutil.which(t)
        for t in ("legis", "wardline")
    )


@pytest.mark.skipif(not _tools_present(), reason="legis/wardline not installed")
def test_legis_govern_runs_the_live_handshake_and_reports_a_count():
    r = steps.legis_govern()
    assert r.name == "legis govern"
    assert r.ok is True
    # Deterministic governance outcome in the LOCKED detail.
    assert "→ surface_override" in r.detail
    assert "governed" in r.detail
    # Signed/unsigned status rides the non-rendered note, not the detail.
    assert ("verified" in r.note) or ("unverified" in r.note)


def test_legis_govern_never_raises_when_tools_missing(monkeypatch):
    # Point the binaries at a non-existent dir so production/probe fails, and assert
    # the step degrades to ok=False instead of raising (tour contract).
    monkeypatch.setattr(steps, "BIN", steps.Path("/nonexistent/bin"))
    monkeypatch.setattr(steps.shutil, "which", lambda *_a, **_k: None)
    r = steps.legis_govern()
    assert r.ok is False
    assert r.name == "legis govern"
```

- [ ] **Step 2: Run to verify it fails**

Run: `cd /home/john/lacuna && python -m pytest tests/test_steps_legis.py -q`
Expected: FAIL — `steps.legis_govern` and `steps.shutil` do not exist yet.

- [ ] **Step 3: Implement the step**

Add to the imports at the top of `tour/steps.py`:

```python
import os
import shutil
import socket
import tempfile
import time
import urllib.error
import urllib.request
```

Add these helpers and the step at the end of `tour/steps.py`:

```python
def _tool(name: str) -> str | None:
    """Resolve a tool by ~/.local/bin then PATH (mirrors capability._locate)."""
    candidate = BIN / name
    if candidate.exists():
        return str(candidate)
    return shutil.which(name)


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _artifact_secret() -> str | None:
    """Read the shared HMAC secret from lacuna's gitignored .env, if provisioned."""
    env_file = ROOT / ".env"
    if not env_file.exists():
        return None
    for line in env_file.read_text().splitlines():
        if line.startswith("WARDLINE_LEGIS_ARTIFACT_KEY="):
            value = line.split("=", 1)[1].strip()
            return value or None
    return None


def _wait_health(port: int, timeout_s: float = 8.0) -> bool:
    deadline = time.monotonic() + timeout_s
    url = f"http://127.0.0.1:{port}/health"
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1.0) as resp:
                if resp.status == 200:
                    return True
        except (urllib.error.URLError, OSError):
            time.sleep(0.2)
    return False


def legis_govern() -> StepResult:
    """Drive the live Wardline -> Legis governance handshake against the specimen.

    Produce a (signed-when-keyed) legis artifact with `wardline scan --format legis`,
    POST it to a throwaway `legis serve` with server-owned surface_override routing,
    and record the deterministic governed-defect count. Never raises (tour contract).
    """
    name = "legis govern"
    wardline = _tool("wardline")
    legis = _tool("legis")
    if not wardline or not legis:
        return StepResult(name, ok=False, detail="legis/wardline not installed")

    secret = _artifact_secret()
    proc = None
    try:
        with tempfile.TemporaryDirectory() as tmp:
            artifact_path = Path(tmp) / "scan.legis.json"
            scan_env = {**os.environ}
            if secret:
                scan_env["WARDLINE_LEGIS_ARTIFACT_KEY"] = secret
            prod = subprocess.run(
                [wardline, "scan", ".", "--format", "legis", "--output", str(artifact_path)],
                cwd=ROOT, capture_output=True, text=True, check=False, env=scan_env,
            )
            if not artifact_path.exists():
                return StepResult(name, ok=False,
                                  detail=f"wardline produced no legis artifact (exit {prod.returncode})")
            artifact = json.loads(artifact_path.read_text())
            signed = bool(artifact.get("artifact_signature"))

            port = _free_port()
            serve_env = {**os.environ, "LEGIS_WARDLINE_CELL": "surface_override"}
            if secret:
                serve_env["LEGIS_WARDLINE_ARTIFACT_KEY"] = secret
            gov_db = f"sqlite:///{Path(tmp) / 'gov.db'}"
            proc = subprocess.Popen(
                [legis, "serve", "--host", "127.0.0.1", "--port", str(port),
                 "--governance-db", gov_db],
                cwd=ROOT, env=serve_env,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            if not _wait_health(port):
                return StepResult(name, ok=False, detail="legis serve did not become healthy")

            body = json.dumps({"agent_id": "lacuna-tour", "scan": artifact}).encode("utf-8")
            req = urllib.request.Request(
                f"http://127.0.0.1:{port}/wardline/scan-results",
                data=body, headers={"Content-Type": "application/json"}, method="POST",
            )
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                routed = json.loads(resp.read()).get("routed", [])

            n = len(routed)
            status = ("verified" if (secret and signed) else "unverified")
            return StepResult(
                name, ok=True,
                detail=f"governed {n} active defects → surface_override",
                note=f"artifact: {status}",
            )
    except (urllib.error.HTTPError, urllib.error.URLError, OSError,
            json.JSONDecodeError, ValueError) as exc:
        return StepResult(name, ok=False, detail=f"handshake failed: {exc}")
    finally:
        if proc is not None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
```

- [ ] **Step 4: Run to verify it passes**

Run: `cd /home/john/lacuna && export PATH="/home/john/.local/bin:$PATH" && python -m pytest tests/test_steps_legis.py -q`
Expected: PASS (both tests). The integration test governs the specimen's active defects; the degrade test returns `ok=False`.

- [ ] **Step 5: Commit**

```bash
git add tour/steps.py tests/test_steps_legis.py
git commit -m "feat(tour): add live Wardline->Legis governance step"
```

---

### Task 6: Register the legis step in the tour run

**Files:**
- Modify: `tour/__main__.py`
- Test: `tests/test_drive.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_drive.py`:

```python
from tour.__main__ import _drive


def test_drive_includes_the_legis_governance_step():
    _caps, results = _drive()
    names = [r.name for r in results]
    assert "legis govern" in names
    # ordering: legis runs after the wardline scan it consumes
    assert names.index("legis govern") > names.index("wardline scan")
```

- [ ] **Step 2: Run to verify it fails**

Run: `cd /home/john/lacuna && export PATH="/home/john/.local/bin:$PATH" && python -m pytest tests/test_drive.py -q`
Expected: FAIL — `_drive()` does not yet call `steps.legis_govern()`.

- [ ] **Step 3: Implement — add the step to `_drive()`**

In `tour/__main__.py` `_drive()`, append `steps.legis_govern()` after `steps.wardline_scan()`:

```python
    results = [
        steps.clarion_analyze(),
        steps.clarion_structure(),
        steps.wardline_scan(),
        steps.legis_govern(),
        steps.filigree_findings(),
    ]
```

- [ ] **Step 4: Run to verify it passes**

Run: `cd /home/john/lacuna && export PATH="/home/john/.local/bin:$PATH" && python -m pytest tests/test_drive.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tour/__main__.py tests/test_drive.py
git commit -m "feat(tour): run the legis governance step in the tour drive"
```

---

### Task 7: Confirm the specimen yields a governable defect; regenerate docs; verify

**Files:**
- Modify: `docs/tour.md`, `docs/matrix.md` (regenerated)
- Possibly modify: specimen files (only if zero active defects)

- [ ] **Step 1: Confirm the specimen produces ≥1 Wardline-active defect**

```bash
cd /home/john/lacuna && export PATH="/home/john/.local/bin:$PATH"
wardline scan . >/dev/null 2>&1; wc -l findings.jsonl
```
Expected: `findings.jsonl` is non-empty (the planted trust-flow lacunae, e.g. `PY-WL-101`). If the governed count would be 0 (all findings non-defect/suppressed), add one active defect to `specimen/trust_flow.py` consistent with an existing lacuna and update `tour/lacunae.toml` — but the existing trust-flow lacunae already emit active defects, so this is expected to pass as-is.

- [ ] **Step 2: Regenerate the tour narrative + matrix**

```bash
cd /home/john/lacuna && export PATH="/home/john/.local/bin:$PATH"
make tour
```
Expected: console shows a `## ✅ legis govern` section with `governed N active defects → surface_override`, a `note [legis govern]: artifact: verified` line (when `.env` secret is set), and `docs/matrix.md` lists `legis — live`.

- [ ] **Step 3: Run the full verify (lockstep + coverage)**

```bash
cd /home/john/lacuna && export PATH="/home/john/.local/bin:$PATH"
make verify
```
Expected: `VERIFY OK — every live lacuna surfaced; narrative in lockstep.` (legis adds no lacuna coverage requirement since no lacuna's `expected_tool` is `legis`.)

- [ ] **Step 4: Commit the regenerated docs**

```bash
git add docs/tour.md docs/matrix.md
git commit -m "docs(tour): regenerate narrative + matrix with legis as a live member"
```

---

### Task 8: Full CI + self-sufficiency check; flag the stale Wardline doc; merge

**Files:** none new.

- [ ] **Step 1: Run the full suite**

```bash
cd /home/john/lacuna && export PATH="/home/john/.local/bin:$PATH"
python -m pytest -q
make ci          # test + scan + verify
```
Expected: pytest green; `make ci` green (`wardline scan --fail-on ERROR` stays green on the baselined lacunae; verify OK).

- [ ] **Step 2: Re-run the tour a second time and re-verify (idempotence / determinism)**

```bash
cd /home/john/lacuna && export PATH="/home/john/.local/bin:$PATH"
make tour && make verify
```
Expected: `make verify` still OK — the regenerated narrative is byte-identical (governed count stable; no secret/commit/port leakage into docs).

- [ ] **Step 3: Record the Wardline-doc drift flag**

Append a note to the design spec's out-of-scope section (or a `docs/tour.md` is generated — do NOT hand-edit it). Add to `docs/superpowers/specs/2026-06-05-legis-tour-member-design.md` under "Out of scope" a dated line confirming the Wardline handoff doc (`wardline/docs/guides/legis-handoff.md`) still describes the pre-relaxation legis contract and should be refreshed by the Wardline owner. Commit:

```bash
git add docs/superpowers/specs/2026-06-05-legis-tour-member-design.md
git commit -m "docs: flag stale Wardline legis-handoff contract for its owner"
```

- [ ] **Step 4: Merge to main (linear)**

```bash
cd /home/john/lacuna
git switch main
git merge --ff-only feat/legis-tour-member
git branch -d feat/legis-tour-member
git log --oneline -8
```
Expected: fast-forward; the feature lands on `main` with linear history.

---

## Self-review notes

- **Spec coverage:** install (T1), shared secret (T2), capability promotion (T3), determinism via `note` (T4), the live signed handshake step (T5), tour registration (T6), docs regeneration + verify (T7), CI + doc-flag + merge (T8). Charter stays design-only (T3). The git-rename/closure-gate legs are explicitly out of scope (spec) and not in any task.
- **Determinism:** the only env-dependent value (signed/unsigned) is confined to `StepResult.note`, which `render_tour_md` never reads (asserted in T4). Ports/temp dirs/commit hashes never enter `detail`.
- **Tour contract:** `legis_govern` catches the full failure set and always returns a `StepResult` (asserted by the degrade test in T5); the server is always torn down in `finally`.
- **No new lacuna coverage debt:** no `lacuna` entry has `expected_tool = "legis"`, so promoting legis to live adds no "must be surfaced" obligation (verified against `tour/lacunae.toml`).
