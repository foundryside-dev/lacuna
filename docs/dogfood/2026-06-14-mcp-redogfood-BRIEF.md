# Final MCP-Surface Dogfood — RUN BRIEF (2026-06-14)

**Authored from the weft hub session; to be RUN from a session rooted in
`/home/john/lacuna`.** This is the companion to the same-day CLI-only run
(`2026-06-14-cli-only-redogfood-report.md`). The CLI run deliberately scoped to
the CLI surface and found it is a *gate* tool, not a *discovery* tool. This run
measures the **MCP agent surface** — the experience a real agent actually has.

> **Why a lacuna-rooted session is mandatory.** MCP tools resolve against the
> session's own `.mcp.json`. A subagent dispatched from the hub inherits the
> *hub's* MCP wiring and routes to the wrong project — every "tool absent /
> wrong-project" verdict it emits is a **dispatch artifact, not a bug** (this
> exact mistake was already made and corrected; see hub PDR + `current-state.md`).
> Run this from `cwd=/home/john/lacuna` and nowhere else.

---

## 0 — Preflight (do this first; abort if any fails)

```bash
cd /home/john/lacuna
# Secrets into the shell BEFORE launching Claude Code (not in .mcp.json):
export WEFT_FEDERATION_TOKEN="$(cat ~/.config/filigree/federation_token)"
set -a; . ./.env; set +a          # exports LEGIS_HMAC_KEY (+ artifact keys)
make setup                         # idempotent; ensures .env exists
```

Then, inside the lacuna-rooted Claude session, confirm the MCP surface is live:
- **5 servers attached**: `filigree`, `legis`, `loomweave`, `wardline`, `warpline`.
- Sanity-ping each (e.g. `filigree session_context_get`, a `loomweave` doctor/
  status tool). If a server is missing or a call routes to a project that is not
  `lacuna`, **stop** — fix session rooting, do not record it as a finding.
- Live infra confirmed from hub at brief-authoring time: lacuna Filigree on
  `:8749` (auth-gated, alive), fresh `loomweave.db` (18:12), all 5 MCP servers
  running. (Known background noise: defunct/zombie MCP procs — `weft-9865f65699`
  — ignore.)

---

## Scope

**In scope (the four launch-control members):** Wardline, Loomweave, Filigree,
Legis. **Warpline** is the admitted 5th member but its lacunae
(`wp-blast-radius`, `wp-reverify`, `wp-churn`, `wp-timeline` on
`specimen/cli.py::_add_book`) are **advisory enrich-only capability demos, not
defects** — exercise them and confirm they *enrich*, but they never gate and are
**not scored as pass/fail flaws**. `_add_book` carries no `LACUNA` docstring by
design.

---

## The measurement: 4 federation joins, via MCP only

For each join, use the **MCP tools** (not CLI, not SQLite, not raw HTTP). Falling
back is allowed but **log every fallback** — a fallback is the finding.

| Join | What to prove | MCP path (confirm exact tool names against your live surface) |
|------|---------------|----------------------------------------------------------------|
| **J1** | Wardline→Filigree emit: findings land with provenance + suppression state | `wardline scan` (MCP) → `filigree finding_list --kind defect` → `finding_get` (assert `scan_source`, `issue_id`, `suppression_state`) |
| **J2** | Loomweave SEI keying: resolve a finding's location to a `loomweave:eid:` SEI **without** touching the DB | `loomweave entity_find` / `entity_at` for `specimen.preview_sinks.log_export_request`; then `wardline dossier <qualname>` and assert `sei` is **non-null** and `linkages.available: true` (this is exactly what the CLI run could NOT do — `sei: null`) |
| **J3** | ADR-029 entity association: bind a Filigree issue to the loomweave entity and read it back **both directions** via MCP | `filigree entity_association_add` (issue ↔ `loomweave:eid:…`), `entity_association_list`, `entity_association_list_by_entity` (reverse lookup). The CLI surface has **no** verb here — MCP must. |
| **J4** | Legis governance / closure gate | `legis policy_evaluate` / governance + closure-gate tools; `wardline attest` then `verify_attestation`. Confirm `LEGIS_HMAC_KEY` is live (gate **enabled**, not `CELL_NOT_ENABLED`). |

**Target: 4/4 joins PASS via the MCP surface.** (The launch-gate re-dogfood
already passed 4/4 once; this is the confirming measurement on the current
deployed versions: wardline 1.0.0rc4, loomweave 1.1.0-rc5, filigree 3.0.0,
legis 1.0.0.)

---

## The discovery surface the CLI couldn't reach — score these now

The CLI-only run scored these **8 loomweave structural lacunae as invisible**
(MCP-only). This run must reach them via the loomweave MCP query tools. For each,
confirm the lacuna surfaces and is promotable/trackable in Filigree:

| Lacuna | Expected MCP query (confirm exact name) |
|--------|-----------------------------------------|
| `lw-dead-code` | `entity_dead_list` |
| `lw-circular-import` | `module_circular_import_list` |
| `lw-coupling-hotspot` | `entity_coupling_hotspot_list` |
| `lw-entry-point` | entry-point list |
| `lw-subsystem` | subsystem list |
| `lw-inheritance` | inheritance query |
| `lw-decorator` | decorator-relation query |
| `lw-call-chain` | call-chain navigation |
| `lw-too-complex`, `lw-duplicate-locator` | loomweave findings list → `finding_promote` into Filigree |

This is the **core delta** vs the CLI run: if these are reachable + trackable via
MCP, the suite's discovery story holds; if not, that is a real launch-gate finding.

---

## Known traps — do NOT mis-score these

1. **Sentinel:** `wl-log-injection` (PY-WL-125, `preview_sinks.py`) is
   **deliberately unbaselined** — `1 active` is **correct, not drift**. Do not
   baseline it; the filigree leg promotes and work-cycles exactly this finding.
2. **Warpline = enrich, not flaw** (above). Capture enrichment; don't pass/fail-score.
3. **`legis policy-boundary-check` default-passes** because `nesting_bomb.py`
   raises `RecursionError` at default stack depth, masking the `pinned_import`
   finding (CLI friction F7). Use the MCP `policy_boundary_check` or the
   `.venv/bin/python3 -c "import sys; sys.setrecursionlimit(100000); …"`
   invocation. If the MCP tool reproduces the silent-pass, **that is a finding**
   (compare `weft-ef2e898642`, the known `--root`-empty silent-clean bug).
4. **Wrong-project routing = session-rooting artifact, not a bug** (Preflight).
5. The planted flaws are **permanent** — do not "fix" any lacuna; a removed
   lacuna fails `make verify`.

---

## Output

1. Write `docs/dogfood/2026-06-14-mcp-redogfood-report.md` with: per-join verdict
   + MCP evidence, the 8-structural-lacunae scoreboard, a friction log (every
   fallback), and an **MCP-surface pass rate** compared head-to-head with the
   CLI-only run's 1/12.
2. File any **genuinely new** defect (not an artifact) in **lacuna's** Filigree
   (`:8749`), keyed to the loomweave SEI via `entity_association_add` where it
   applies.
3. Surface anything **launch-gate-relevant** back to the hub PM (weft repo) — it
   feeds cutover `weft-4b2f948f70` / dogfood gate `weft-cd62a4da9b`. Dogfood
   *complaints* are observations, not specs; *invariant collisions* escalate to PM.
4. Leave the lacuna tree **clean** (commit regen docs before any verify leg;
   keep ledger/DBs/`findings.jsonl` gitignored).
