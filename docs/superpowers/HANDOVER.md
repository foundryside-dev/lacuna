# Handover — Lacuna repivot

*Paste everything below the line into a fresh session to continue this work.*

---

You are picking up an approved, fully-planned piece of work. **Read this whole
prompt, then read the spec and plan it points to before doing anything.**

## What this is

`/home/john/testo` was a throwaway "Loom suite integration sandbox." It is being
repivoted into a **first-class Loom product called Lacuna** — *the MissingNo of
Loom*: a clean-cored reference application seeded with documented, **permanent**
flaws ("lacunae"), each one planted to make a specific Loom tool or
tool-combination light up. The bad code is the feature and must stay; "first
class" applies to packaging, narrative, and a runnable showcase — never to
cleaning the planted flaws away.

The brainstorming and planning phases are **done and approved by the user.** Your
job is to **execute the implementation plan**, not to redesign it.

## Read these first (in order)

1. **Plan (your task list):** `/home/john/lacuna/docs/superpowers/plans/2026-06-05-lacuna-repivot.md`
2. **Spec (the why):** `/home/john/lacuna/docs/superpowers/specs/2026-06-05-lacuna-repivot-design.md`
3. **Memory:** `/home/john/.claude/projects/-home-john-testo/memory/lacuna-repivot.md`
4. **Suite context:** the READMEs of `/home/john/{clarion,filigree,wardline,legis,charter}`.

## Current state (nothing implemented yet)

- The plan and spec exist; **no plan task has been executed.**
- `/home/john/lacuna` is a **verbatim copy** of `testo`: its config still points at
  `testo` paths and its Filigree DB / Clarion index are still `testo`-keyed. The
  re-key (plan Phase 1) fixes this.
- `/home/john/lacuna` is **not a git repo yet** — plan Phase 0 Task 0.1 runs
  `git init`. (So the spec/plan/handover get committed in that first task.)
- `/home/john/testo` is the **rollback snapshot — do not touch it.**

## How to execute

- **Use the superpowers:subagent-driven-development skill** (the plan header marks
  it REQUIRED; it is recommended over inline). Dispatch a fresh subagent per task,
  review between tasks. Inline via superpowers:executing-plans is the fallback.
- Work the phases **in order** (0→5); each depends on the prior. Commit after every
  task (the plan's steps include the commit commands).
- Do **not** re-enter brainstorming or writing-plans. The design is settled.

## Gotchas that will bite you

- **The shell cwd resets to `/home/john/testo` between Bash calls.** Always use
  absolute paths or prefix with `cd /home/john/lacuna && …`.
- **This session's MCP tools + hooks are still wired to `/home/john/testo`** until
  Phase 1 lands. Until then, drive the Loom tools via their **CLIs at
  `/home/john/.local/bin/{filigree,clarion,wardline}`** against `/home/john/lacuna`,
  not via the `mcp__*` tools. After Phase 1 + a session restart, MCP re-points.
- **Python:** use `/home/john/lacuna/.venv/bin/python` (the venv has no `pip`; install
  with `uv pip install --python .venv/bin/python …`). The editable install in
  Phase 0 Task 0.2 may need re-running once `specimen/` and `tour/` exist
  (Tasks 2.1, 2.6) — the plan notes this.
- **The only hardcoded `/home/john/testo` path** is the Clarion hook in
  `.claude/settings.json` (Phase 1 Task 1.2). Everything else is relative or a
  binary path.
- **Honest Wardline gate:** the planted flaws are *baselined* (Task 2.5) so
  `wardline scan --fail-on ERROR` exits 0 on them while still tripping on genuinely
  new findings. Never delete a lacuna to make the gate pass — that fails
  `make verify`.
- **Tool-reality reconciled (2026-06-05):** see `REVIEW-2026-06-05-plan-reality-check.md`.
  Real Wardline ids are `PY-WL-101/102/103/104` (the old `201/202` were fabricated);
  the two exception fixtures are `@trusted` (tier-modulated rules); Task 2.3 Step 3
  captures the live ids. Clarion has **no** dead/cycle CLI — the harness reads
  `.clarion/clarion.db` (`tour/steps.py::structure_facts`); cycle fixtures use
  module-level imports. `wardline scan .` does write `findings.jsonl`. These are
  baked into the plan; just execute it.
- **`filigree init` flags:** the plan uses `--name lacuna --prefix lacuna`; if that
  CLI doesn't accept those flags, edit `.filigree.conf` directly (set
  `project_name` and `prefix` to `lacuna`) against a fresh DB and run
  `filigree doctor`.
- **Degrade honestly:** Legis (rc1) and Charter (scaffold) are *design-only* here.
  The harness must label them, never fake their steps.

## Definition of done (plan Phase 5)

`make ci` is green: `make test` (pytest) passes, `make scan`
(`wardline scan . --fail-on ERROR`) exits 0, and `make verify` prints `VERIFY OK`
— every live lacuna surfaced, narrative (`docs/tour.md`) in lockstep. Filigree
issues carry the `lacuna-` prefix; `clarion`/`filigree` doctors are green at
`/home/john/lacuna`; no live `testo` references remain outside `docs/history/`.

## First action

Start the subagent-driven-development skill and dispatch **Phase 0, Task 0.1
(git init + .gitignore)**. Then proceed task-by-task through the plan.
