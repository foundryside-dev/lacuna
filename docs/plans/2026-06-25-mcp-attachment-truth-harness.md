# MCP Attachment Truth — Reproduction Harness Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a deterministic, re-runnable harness in `tour/` that launches each
federation MCP server the way `.mcp.json` configures it, captures where it binds,
classifies each of PRD-0004's three attachment gaps, and (for genuine member bugs)
produces a reproduction fixture + report — discharging PRD-0004 criteria 1–2 while
holding the north-star (`make verify`) and demonstration-honesty (G3) guardrails.

**Architecture:** The existing tour drives every tool by **CLI subprocess** (`tour/steps.py::_run`),
never over MCP — so MCP *attachment* is currently unexercised. This adds a probe
module (`tour/mcp_attachment.py`) that reads the gitignored `.mcp.json`, spawns each
target server (stdio: `command`+`args`+`env`, MCP `initialize` handshake + one probe
call; http: the configured URL with its auth header), and records bound-context
evidence. A new tour leg `steps.mcp_attachment()` surfaces the catalogued `mcp-*`
lacunae, degrading honestly (an absent member is labelled absent, never faked live).
The probe report is a regenerable, gitignored artifact (`.weft/mcp-attachment/`,
token redacted), mirroring how `plainweave_seed.py` self-seeds `.plainweave/` cold each run.

**Tech Stack:** Python 3.12 (stdlib `subprocess`, `json`, `tomllib`, `pathlib`), the
tour harness (`tour/{steps,capability,manifest,report}.py`), an MCP stdio client
(official `mcp` SDK if available; else a minimal hand-rolled JSON-RPC-over-stdio
client — **Phase 1 decides which**), `pytest`.

**Prerequisites:**
- Federation tools installed at `~/.local/bin` (confirmed: loomweave/filigree/wardline/legis/warpline present).
- A working `.mcp.json` at repo root (confirmed present, gitignored, carries a live Filigree Bearer token — **never echo or commit it**).
- Confirm whether an MCP stdio client library is importable: `.venv/bin/python -c "import mcp; print(mcp.__version__)"`. If it errors, Phase 1 Task 1 selects the hand-rolled fallback.
- Read PRD: `docs/product/prds/PRD-0004-mcp-attachment-truth.md` (criteria 1–5, both resolved open questions).

---

## ⚠️ SUPERSEDING FINDING — Phase 1 ran in-session (2026-06-25): all three gaps RESOLVED

The Phase-1 characterization was executed directly through **this attached session's
`mcp__*` tools** — the most faithful measurement of G1's "reachable MCP-first in one
attached session" — instead of the planned subprocess harness. Live evidence:

| Gap (PRD-0004, 06-13 baseline) | In-session probe (2026-06-25) | Verdict |
|---|---|---|
| Loomweave → no-index | `project_status_get`: `project_root=/home/john/lacuna`, 423 entities, `staleness=fresh`, indexed @ `d09da33` | **RESOLVED** — bound to staged repo, not no-index |
| Filigree → hub-not-repo | `mcp_status_get`: `project_root=/home/john/lacuna`, schema 29/29 compatible | **RESOLVED** — bound to lacuna, not Weft hub¹ |
| Legis → absent | `doctor_get`: responds in full; `filigree_scope` project-scoped to lacuna | **RESOLVED** — present & answering, not absent² |

¹ `actor_verification.verified=false` over MCP-HTTP is a known *deferred* limitation
(`filigree-81d3971467`), not an attachment fault. ² `doctor ok:false` = config-hygiene
warns (`.weft/legis` gitignore, operator_key, wardline_artifact_key) — none are
attachment faults; no `audit_log` crash.

**Consequence:** the 0/4 baseline is stale (the member config-fixes in the git log
since 06-13 closed these seams). **Phase 2 below is MOOT** — there are no `member-bug`
gaps to reproduce or report. Per the DECISION GATE, this is surfaced to the owner for
disposition (accept-as-met / re-scope to a durable regression-harness / close). The
reproduce-and-report Phases below are **retained for the record only**; do not execute
them as written. The remaining *real* value, if any, is a durable regression-harness
that asserts these now-working seams stay MCP-first attached — a smaller, re-scoped bet.

---

### G1 confirmed in-session (2026-06-25): 4 of 4 documented joins reachable MCP-first

| Join (metrics.md G1) | In-session MCP call | Result |
|---|---|---|
| Wardline to Filigree work join | `mcp__filigree__finding_list scan_source=wardline` | OK - wardline findings in filigree (`scanner:wardline`, last-seen 2026-06-25) |
| Loomweave to Filigree wardline enrichment | `mcp__loomweave__entity_wardline_list has_findings=true` | OK - 28 entities carry wardline taint facts + findings |
| Loomweave to Filigree issue association | `mcp__loomweave__entity_issue_list` (ShelfMark) | OK - `available:true`, `result_kind:no_matches` (reachable, empty - NOT `unavailable`), endpoint `:8749` |
| Legis governance surface | `mcp__legis__posture_get surface_override` | OK - `floor:chill / effective_cell:structured` (no `audit_log` crash) |

**G1 = 4/4 (baseline 0/4 @ 06-13; target 4/4 by 2026-09-13) - outcome MET, ahead of schedule.**

### NEW frontier (2026-06-25): plainweave - the 6th member - is MCP-absent in Lacuna

The federation grew since G1 was defined (06-13). Lacuna's `.mcp.json` wires **5** servers
(loomweave, filigree, wardline, legis, warpline) - all attached & bound to the staged repo -
but **not plainweave**, the newest member. Evidence:
- `/home/john/plainweave/src/plainweave/mcp_server.py` + `mcp_surface.py` exist => plainweave
  **does ship** an MCP server (`create_mcp_server() -> FastMCP`).
- The **installed** build (`plainweave 0.0.1`, `~/.local/bin/plainweave`) exposes **no `mcp`
  command** => stale uv-tool build (the known `loom-uvtool-build-staleness` pattern).
- `.mcp.json` has no `plainweave` entry.

So in Lacuna's attached session plainweave is **CLI-only / MCP-absent** - the same shape as
the old Legis gap, now for member #6. **This is the live continuation of the Now bet.**
Reconciling it (reinstall from source -> wire into `.mcp.json` -> verify attach in a fresh
session -> regression-proof) is within grant (Lacuna's own env + config; PDR-0005 precedent),
**but** carries two real constraints: (a) reinstalling the build that ARMS `make verify`'s
`pw-*` coverage gate risks the north-star guardrail - verify after; (b) a `.mcp.json` change
only attaches on the *next* session, so MCP-first verification of plainweave cannot complete
in this session.

---

## Reality discovered during planning (read before executing — it changes the work)

Probing the live `.mcp.json` shows PRD-0004's "three member-reported gaps" framing
(written 2026-06-13) has **drifted**. Each gap must be re-classified before any bug
report is filed — filing a member bug for a Lacuna-config fault or an already-fixed
seam would be a false report:

| Gap (PRD-0004) | Live `.mcp.json` evidence | Hypothesis to test in Phase 1 |
|---|---|---|
| Loomweave → no-index | `loomweave serve` launched with **no `--root`/cwd** (wardline passes `--root .`) | Likely **Lacuna-config-fixable** in our own `.mcp.json` (within grant) — *not* a member bug, unless `loomweave serve` cannot accept a root |
| Filigree → hub-not-repo | URL already `…/mcp/?project=lacuna` | May be **already resolved** since 06-13; confirm the bound project/DB is the staged repo, not Weft |
| Legis → absent | Entry **present** (`legis mcp --agent-id codex`, `env LEGIS_WARDLINE_CELL=surface_override`) | Likely **member bug**: starts then drops (cf. legis MCP governance-read crash `no such table: audit_log`) — reproduce the crash-on-init |

**Consequence for the plan:** Phase 1 is a characterization spike that proves the
probe mechanism *and* re-classifies each gap into `lacuna-config-fixable` |
`member-bug` | `resolved`. Only confirmed `member-bug` gaps get a reproduction
fixture + report (Phase 2). `lacuna-config-fixable` gaps are fixed in our own
`.mcp.json` (autonomous; not a member-repo change — PDR-0002 honored). `resolved`
gaps are recorded closed against G1. This is why a full atomic-TDD plan for "report
3 gaps" is **not** written below the gate — it would presume an answer the spike exists to find.

---

## Phase 1 — Characterize & de-risk (atomic, executable now)

### Task 1: MCP stdio probe client (the load-bearing mechanism)

**Files:**
- Create: `tour/mcp_attachment.py`
- Test: `tests/test_mcp_attachment.py`

**Step 1: Write the failing test (deterministic parsing, not the live probe)**

```python
# tests/test_mcp_attachment.py
import json
from pathlib import Path
from tour.mcp_attachment import load_server_specs, ServerSpec

def test_load_server_specs_parses_stdio_and_http(tmp_path: Path):
    cfg = tmp_path / ".mcp.json"
    cfg.write_text(json.dumps({"mcpServers": {
        "loomweave": {"type": "stdio", "command": "/x/loomweave", "args": ["serve"], "env": {}},
        "filigree": {"type": "streamable-http", "url": "http://h/mcp/?project=lacuna",
                     "headers": {"Authorization": "Bearer SECRET"}},
    }}))
    specs = load_server_specs(cfg)
    assert specs["loomweave"] == ServerSpec(
        name="loomweave", transport="stdio", command="/x/loomweave",
        args=("serve",), env={}, url=None, headers={})
    # token is preserved in-memory for the probe but flagged secret for redaction
    assert specs["filigree"].transport == "streamable-http"
    assert specs["filigree"].url == "http://h/mcp/?project=lacuna"
    assert specs["filigree"].redacted_headers() == {"Authorization": "Bearer <redacted>"}
```

**Why this test:** Locks the config contract and the redaction guarantee (PRD secrets
constraint) before any live process is spawned. Deterministic — no servers involved.

**Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_mcp_attachment.py::test_load_server_specs_parses_stdio_and_http -v`

Expected: `FAILED - ImportError: cannot import name 'load_server_specs'`

**Step 3: Write minimal implementation**

```python
# tour/mcp_attachment.py  (parsing + spec only — probe added in Task 2)
from __future__ import annotations
import json
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path("/home/john/lacuna")

@dataclass(frozen=True)
class ServerSpec:
    name: str
    transport: str               # "stdio" | "streamable-http"
    command: str | None = None
    args: tuple[str, ...] = ()
    env: dict[str, str] = field(default_factory=dict)
    url: str | None = None
    headers: dict[str, str] = field(default_factory=dict)

    def redacted_headers(self) -> dict[str, str]:
        return {k: ("Bearer <redacted>" if k.lower() == "authorization" else v)
                for k, v in self.headers.items()}

def load_server_specs(cfg_path: Path = ROOT / ".mcp.json") -> dict[str, ServerSpec]:
    raw = json.loads(Path(cfg_path).read_text())
    out: dict[str, ServerSpec] = {}
    for name, s in raw.get("mcpServers", {}).items():
        out[name] = ServerSpec(
            name=name, transport=s.get("type", "stdio"),
            command=s.get("command"), args=tuple(s.get("args", [])),
            env=dict(s.get("env", {})), url=s.get("url"),
            headers=dict(s.get("headers", {})),
        )
    return out
```

**Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_mcp_attachment.py::test_load_server_specs_parses_stdio_and_http -v` → `PASSED`

**Step 5: Commit**

```bash
git add tour/mcp_attachment.py tests/test_mcp_attachment.py
git commit -m "feat(tour): mcp_attachment server-spec parser + header redaction

- Reads gitignored .mcp.json into typed ServerSpec
- Redacts Authorization for any emitted report (PRD-0004 secrets constraint)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

**Definition of Done:**
- [ ] Parser test passes; token never appears in any returned/emitted structure except the in-memory spec used to authenticate the live probe.
- [ ] No other tests broken (`.venv/bin/python -m pytest -q`).

---

### Task 2: Live probe — capture bound context per server (CHARACTERIZATION SPIKE)

> This task is **exploratory** (the skill: don't over-constrain a spike). Its DoD is
> *captured evidence*, not a frozen assertion — the assertion is designed in Task 3
> once we see real output. Run against the live, attached environment.

**Files:**
- Modify: `tour/mcp_attachment.py` (add `probe(spec) -> ProbeResult`)
- Create: `scripts/characterize_mcp_attachment.py` (one-shot evidence dump → `.weft/mcp-attachment/characterization.json`, gitignored)

**Step 1: Decide the stdio client.** Run the prereq import check. If `mcp` SDK is
importable, use its `stdio_client`; else implement a minimal newline/Content-Length
JSON-RPC client (`initialize` → `notifications/initialized` → one call). Record the
choice in `tour/mcp_attachment.py` module docstring.

**Step 2: Implement `probe(spec)`** capturing, per server:
- `initialized: bool` (did the MCP handshake complete?)
- `bound_context: str` — loomweave: `project_status_get` root/index id (or read `loomweave://context`); filigree: resolved `project` from a status/`tools/list` echo; legis: handshake success + first error if it drops.
- `error: str | None` (redacted — never include the token or absolute home paths beyond repo root).

**Step 3: Run the one-shot characterizer:**

Run: `.venv/bin/python scripts/characterize_mcp_attachment.py`

Capture (do **not** assert yet) for loomweave, filigree, legis the `initialized`,
`bound_context`, and `error`. Expected shape (illustrative — record the REAL values):
```
loomweave: initialized=True  bound_context=<root?>   → no-index? config-fixable?
filigree:  initialized=True  bound_context=lacuna    → resolved?
legis:     initialized=False error="no such table: audit_log" → member-bug
```

**Step 4: Classify each gap** in a short markdown note
`docs/plans/2026-06-25-mcp-attachment-characterization.md`: each gap →
`lacuna-config-fixable` | `member-bug` | `resolved`, with the captured evidence line.

**Step 5: Commit** (code + characterization note; the `.weft/mcp-attachment/` dump stays gitignored).

```bash
git add tour/mcp_attachment.py scripts/characterize_mcp_attachment.py docs/plans/2026-06-25-mcp-attachment-characterization.md
# ensure .weft/mcp-attachment/ is ignored first (see Task 5 gitignore step)
git commit -m "feat(tour): live MCP attachment probe + gap characterization

- probe() spawns each .mcp.json server, captures bound-context evidence
- characterization note classifies each PRD-0004 gap (config/member/resolved)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

**Definition of Done:**
- [ ] `initialized`/`bound_context`/`error` captured for all three target servers from a clean run.
- [ ] Each gap classified with evidence; classification note committed.
- [ ] No token or non-repo absolute path in any committed artifact.

---

## DECISION GATE (after Phase 1 — re-enter DECIDE before Phase 2)

Route by the Task 2 classification:
- **`lacuna-config-fixable`** → fix our own `.mcp.json` (e.g. add loomweave `--root`/cwd); **autonomous, within grant** (Lacuna's own file, not a member repo). Re-probe to confirm; record against G1.
- **`member-bug`** → proceed to Phase 2 for *that* gap: catalogue an `mcp-*` lacuna, build the reproduction fixture, file the report to **the owning member's own tracker** (PRD-0004 resolved-routing).
- **`resolved`** → record closed against G1; no fixture.

**If 0 gaps remain `member-bug`,** PRD-0004's criteria 1–2 collapse to "config fix +
G1 measurement" and Phase 2's tour-leg scope shrinks accordingly — surface this to
the owner, do not invent member bugs to justify the original plan shape.

---

## Phase 2 — Productionize confirmed member-bugs as a tour leg (gated; finalize with solution-architect)

> Intentionally specified at outline altitude: the exact `mcp-*` lacuna entries,
> the report/SEI-evidence schema, and how the leg's determinism is bounded depend on
> Phase 1's findings. **Route solution shape to `/axiom-solution-architect`** (PRD-0004
> handoff) before expanding these into atomic TDD tasks. Shape, not yet code:

- **2a. Catalogue lacunae.** Add one `mcp-*` entry per confirmed member-bug to
  `tour/lacunae.toml` (`expected_tool`, `expected_rule`, `category`, `demonstrates`)
  — mirrors the `pw-*`/`warpline` capability-demo pattern, not a planted-flaw pattern.
- **2b. Tour leg `steps.mcp_attachment()`.** Returns a `Result`; surfaces each
  catalogued `mcp-*` lacuna by reproducing its attachment fault; **honest-degrade**:
  an unreachable member is labelled, never shown live (G3). Wire into `tour/__main__.py::_drive()`.
- **2c. Reproduction fixture (criterion 1).** Deterministic, re-runnable; distinguishes
  "member not attached" from "attached but join broken" (honest-degrade contract).
  Determinism risk (PRD bet-critical assumption): probes hit live servers — bound the
  assertion to "fault reproduced", not brittle exact-string match. **This is the #1 item
  for `/review-plan`'s reality reviewer to validate.**
- **2d. Report + member routing (criterion 2).** Emit a per-gap report (token redacted)
  to the owning member's tracker; record the returned issue ID back into PRD-0004.
- **2e. Guardrails (criteria 4–5).** `make verify` green across every added fixture;
  regenerate `docs/{tour,matrix}.md` in lockstep (commit on a clean tree — a dirty
  tree flips `legis govern` to `[WARN]` and trips verify; see green-tour constraint).

---

## Validate before execution

This is high-risk/high-complexity (spawns live servers, unproven probe mechanism,
determinism assumption). After Phase 1 and before Phase 2 atomic-planning, run:

**RECOMMENDED SUB-SKILL:** `/review-plan docs/plans/2026-06-25-mcp-attachment-truth-harness.md`

Reality reviewer must validate: (a) the MCP stdio handshake mechanism is real for these
servers, (b) the determinism bound on live probes, (c) the gap re-classification is
evidence-backed. Revise until `APPROVED` / `APPROVED_WITH_WARNINGS`.

## Open assumptions (recorded, not hidden)
- The probe can complete an MCP `initialize` with each stdio server from a plain
  subprocess. *If false* (a server needs the real client's capabilities), the harness
  falls back to a `tools/list`-only liveness check + static `.mcp.json` lint, and that
  limitation becomes part of the member report.
- Live-probe results are stable enough across runs to assert in `verify`. *If false*,
  the leg asserts classification (config/member/resolved), not exact bound-context strings.
- Report/SEI evidence schema is `/axiom-solution-architect`'s to shape; this plan assumes a
  minimal `{gap, classification, evidence, member, issue_id}` record until then.
