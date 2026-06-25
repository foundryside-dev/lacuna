# Plainweave MCP Attachment + 6-Member Regression-Harness — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make plainweave (the 6th member) reachable MCP-first in Lacuna, then add a
durable, regenerable harness that asserts all 6 federation members stay reachable
MCP-first so a silent de-attachment trips `make verify`.

**Architecture:** Two phases. **Phase 1 (reconcile)** is environment + config: reinstall
plainweave from source so the `plainweave-mcp` console script exists, wire it into
`.mcp.json` (mirroring the `warpline-mcp` stdio entry), and re-establish the green tour.
**Phase 2 (regression-harness)** adds `tour/mcp_attachment.py` + a tour leg that, for each
of the 6 members, spawns its `.mcp.json`-configured server and asserts an MCP `initialize`
handshake + binding to the staged repo — because the tour runs as a CLI subprocess and
cannot introspect the agent's own MCP session, the harness must spawn-and-probe (the same
mechanism scoped in `docs/plans/2026-06-25-mcp-attachment-truth-harness.md`).

**Tech Stack:** Python 3.12, `uv tool`, the tour harness (`tour/{steps,capability,__main__,
manifest,report}.py`), the `mcp` SDK as a stdio client (plainweave already depends on
`mcp>=1.2.0`; confirm importable in Lacuna's `.venv` or vendor a minimal client), `pytest`.

**Prerequisites:**
- plainweave source at `/home/john/plainweave` (confirmed: console scripts `plainweave` +
  `plainweave-mcp = plainweave.mcp_server:main`; dep `mcp>=1.2.0`).
- Installed `plainweave 0.0.1` is **stale** (no `plainweave-mcp`) — Phase 1 Task 1 fixes this.
- `.mcp.json` at repo root (gitignored; carries a live Filigree token — never echo/commit it).
- **Clean working tree before any `make verify`** — a dirty tree flips `legis govern` to
  `[WARN]` and trips verify (see [[lacuna-green-tour-constraints]]). Commit/stash between a
  mutation and a verify.
- Read PDR-0007 (the bet) and PDR-0005 (plainweave leg; its reversal trigger warns plainweave
  CLI/oracle drift can break the seed).

**Authority / boundary:** reinstalling plainweave and editing `.mcp.json` are Lacuna's own
env + config (within grant; PDR-0005 precedent) — NOT a member-repo change. No plainweave
source is modified. The bug already filed against loomweave (`clarion-48af930f2a`) is unrelated.

---

## ⚠️ The load-bearing risk (read first)

Reinstalling plainweave to a newer build can **drift the `plainweave_intent` tour leg's
output**, which the tour captures verbatim for narrative lockstep. PDR-0005's own reversal
trigger calls this out. So the reinstall is NOT a safe no-op: it can break `make verify` (the
north-star). Phase 1 therefore reinstalls, regenerates, and **diffs the plainweave leg**, and
treats any drift as specimen-reconciliation work (update `plainweave_seed.py`/`lacunae.toml`/
docs so the 4 `pw-*` lacunae still surface) — not as a failure to paper over. **Do Phase 1 on
a branch** so a bad reinstall is trivially revertible.

---

## Phase 1 — Reconcile plainweave's MCP surface

### Task 1: Reinstall plainweave from source (get the `plainweave-mcp` binary)

**Step 1 — branch + confirm the gap.**
```bash
git -C /home/john/lacuna switch -c plainweave-mcp-attach
ls /home/john/.local/bin/plainweave-mcp 2>/dev/null && echo "EXISTS (unexpected)" || echo "absent (expected)"
/home/john/.local/bin/plainweave doctor --json 2>/dev/null | python3 -c "import sys,json;print([c for c in json.load(sys.stdin).get('checks',[]) if c.get('id')=='mcp_surface'])"
```
Expected: `plainweave-mcp` absent; doctor `mcp_surface` = error ("not importable").

**Step 2 — reinstall from source.**
```bash
uv tool install --force /home/john/plainweave
ls -l /home/john/.local/bin/plainweave-mcp
/home/john/.local/bin/plainweave --version
```
**Definition of Done:** `~/.local/bin/plainweave-mcp` exists; `plainweave doctor` `mcp_surface`
check = ok ("entry point is importable"). Record the new version.

**Step 3 — guardrail check: did the reinstall drift the tour leg?**
```bash
cd /home/john/lacuna && make tour >/dev/null 2>&1; git status --short -- docs/
git diff -- docs/tour.md docs/matrix.md docs/flaws/pw-*.md
```
- **No diff** → reinstall is output-compatible; proceed.
- **Diff in the plainweave leg** → drift. Inspect; if the 4 `pw-*` lacunae still surface with
  the same meaning, commit the regenerated docs (lockstep). If the intent-coverage envelope
  shape changed, reconcile `tour/plainweave_seed.py` + `tour/lacunae.toml` so the `pw-*` demos
  still hold (PDR-0005 semantics), then regenerate. **Do not** suppress a real change to keep
  the gate quiet (north-star reversal trigger).

**Step 4 — verify green on a clean tree.**
```bash
cd /home/john/lacuna && git add -A && git commit -q -m "chore(env): reinstall plainweave from source (adds plainweave-mcp); regenerate tour"
make verify; echo "exit: $?"
```
**Definition of Done:** `make verify` → exit 0 ("every live lacuna surfaced; narrative in
lockstep"); all 4 `pw-*` lacunae present. If red for a real specimen reason, fix the specimen,
not the gate.

### Task 2: Wire plainweave into `.mcp.json`

**Step 1 — add the stdio entry** (mirror the `warpline-mcp` pattern). `.mcp.json` is gitignored;
edit in place, preserve the Filigree token untouched, do not commit it.
```jsonc
"plainweave": {
  "command": "/home/john/.local/bin/plainweave-mcp",
  "args": [],
  "type": "stdio",
  "env": {}
}
```
**Step 2 — validate JSON + entry.**
```bash
python3 -c "import json; d=json.load(open('/home/john/lacuna/.mcp.json')); assert 'plainweave' in d['mcpServers']; print(sorted(d['mcpServers']))"
```
Expected: `['filigree','legis','loomweave','plainweave','wardline','warpline']` (6).

**Definition of Done:** `.mcp.json` has a well-formed plainweave stdio entry; JSON parses; token
intact; file NOT staged/committed (gitignored).

> **Constraint — cannot verify MCP-first this session.** A `.mcp.json` change only attaches on
> the *next* agent session. So criterion "plainweave reachable MCP-first" is verified by
> **re-attaching in a fresh session** and calling an `mcp__plainweave__*` tool that binds to the
> staged repo's `.plainweave` context. Record that as the Phase-1 acceptance step, run next session.

---

## DECISION GATE (after Phase 1)
- Phase-1 done = `plainweave-mcp` installed, `.mcp.json` wired, `make verify` green, and (next
  session) `mcp__plainweave__*` attaches to the staged repo. That alone discharges the
  "wire the newest member MCP-first" half of PDR-0007 and moves G1 from a 5-server to a
  6-server baseline.
- Only then build Phase 2 (the regression-harness), which makes the win durable.

---

## Phase 2 — 6-member attachment regression-harness

> Specified at task altitude; the spawn-and-handshake feasibility is the gating unknown, so
> Task 1 here is a characterization spike (do not fabricate handshake code before it). Reuse
> the module scoped in `docs/plans/2026-06-25-mcp-attachment-truth-harness.md`.

### Task 1: Prove the MCP stdio handshake mechanism (spike)
- Confirm an MCP stdio client is usable from Lacuna's `.venv` (`import mcp`), else vendor a
  minimal JSON-RPC stdio client.
- For ONE stdio server (plainweave-mcp), spawn per `.mcp.json`, complete `initialize` +
  one probe call, capture bound context. DoD: captured evidence that the handshake works (or a
  documented fallback to `tools/list`-only liveness + static config-lint).

### Task 2: `tour/mcp_attachment.py` — probe all 6 members
- Reuse `load_server_specs()` + `probe()` (parse `.mcp.json`, redact the token, spawn stdio /
  GET http, capture `initialized` + `bound_context`). TDD the deterministic parts (parsing,
  redaction, classification); treat the live probe as captured-evidence.

### Task 3: Tour leg `steps.mcp_attachment()` + wire into `__main__._drive()`
- Returns a `Result` asserting each of the 6 members is reachable MCP-first and bound to the
  staged repo; **honest-degrade** — a genuinely unreachable member is labelled, never faked
  live (G3). Add `mcp-attach-*` capability entries to `tour/lacunae.toml`.

### Task 4: Make it a `make verify` gate (the durable win)
- `verify` fails if any of the 6 members is not reachable MCP-first (silent de-attach trips the
  gate). **Determinism bound** (PRD bet-critical assumption): assert "reachable + bound", not a
  brittle exact-string match, since probes hit live servers. Regenerate `docs/{tour,matrix}.md`
  in lockstep; commit on a clean tree.

---

## Validate before execution
High-risk (env mutation + north-star guardrail + unproven handshake). After Phase 1, before
Phase-2 atomic-planning:

**RECOMMENDED SUB-SKILL:** `/review-plan docs/plans/2026-06-26-plainweave-mcp-attachment.md`
— reality reviewer must validate the handshake mechanism, the determinism bound, and that the
reinstall path does not silently corrupt the `pw-*` specimen.

## Open assumptions (recorded, not hidden)
- The newer plainweave build's `plainweave_intent` output is compatible with the committed tour,
  OR drift is reconcilable as specimen work. *If the oracle shape changed materially, PDR-0005's
  reversal trigger fires and the plainweave leg is re-seeded before this bet proceeds.*
- `plainweave-mcp` speaks a clean MCP stdio `initialize` from a plain subprocess. *If not, the
  harness degrades to liveness + static config-lint and that limitation is logged.*
- Live-probe results are stable enough across runs to gate in `verify`. *If not, assert
  classification (reachable/bound vs absent), not exact bound-context strings.*
- `mcp__plainweave__*` will appear in a fresh session once `.mcp.json` is wired. *If the client
  ignores the entry, that is itself the finding — report to the MCP host config owner, not plainweave.*
