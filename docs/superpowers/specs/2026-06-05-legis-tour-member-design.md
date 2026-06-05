# Legis as a live governance member of the Lacuna tour — Design

**Date:** 2026-06-05
**Status:** Approved (brainstorming) — pending implementation plan
**Repo:** lacuna (the Loom suite's test bed / demo bed)

## Goal

Refurbish Lacuna so its tour drives the **latest** Loom tools and promotes
**Legis** from `design-only` to a **live, first-class governance member**. Legis
is not a detector (it surfaces no lacunae) — it *governs*. The tour demonstrates
the real, live **Wardline → Legis** handshake against the specimen: an agent runs
a Wardline scan, produces a signed legis artifact, and hands it to a running Legis
which routes the active defects into its enforcement model and records the verdict.

This is the first time Legis appears live in the demo bed; it became first-class
after its home-closeout + deferred-followups work (relaxed Wardline ingest, live
git-rename handshake, closure-gate). The tour's hardcoded
`DESIGN_ONLY = ("legis", "charter")` is now stale for `legis`.

## Context (verified)

- **Tour architecture.** `tour/capability.py` detects which tools are runnable;
  `tour/steps.py` drives each live tool against the specimen and returns a
  `StepResult` (with `surfaced` (token, qualname) pairs for detectors); `tour/report.py`
  + `tour/docs_gen.py` render `docs/tour.md` + `docs/matrix.md`; `make verify`
  asserts every live lacuna is surfaced **and** the narrative is byte-for-byte in
  lockstep. So any new step's narrative detail **must be deterministic**.
- **Outputs are gitignored.** `.gitignore` excludes `findings.jsonl`, `.clarion/`,
  `.filigree/`, and `.env`. A `wardline scan` therefore does **not** dirty the
  tracked tree — the specimen stays clean across tour runs, so Wardline can produce
  a **signed** legis artifact (signing requires a clean committed tree).
- **The producer exists** in wardline's working tree: `wardline scan . --format legis`
  (`src/wardline/cli/scan.py`) builds the artifact via `wardline.core.legis.build_legis_artifact`,
  signed when a key is present (`load_legis_artifact_key`), else unsigned provenance.
- **The wire** (`/home/john/wardline/docs/guides/legis-handoff.md`): post
  `{"cell": …, "agent_id": …, "scan": <artifact>}` to legis `POST /wardline/scan-results`.
  The artifact is `{scanner_identity, rule_set_version, commit_sha, tree_sha, findings, artifact_signature}`.
- **Legis ingest was relaxed** (legis `bc43694`): it now carries diagnostic
  properties verbatim, accepts `baselined`/`judged`, and reads suppression proof
  top-level or in properties — so the projection is minimal and realistic scans are
  accepted.
- **The specimen is ours to shape** (user direction): Lacuna is the test/demo bed;
  the specimen tree may be edited, re-shaped, and committed as needed.

## Tool install plan

Build + install into `~/.local/bin` (the dir `capability.py`/`steps.py` already
reference via `BIN`):

| Tool | Source state | Why |
| --- | --- | --- |
| legis | committed HEAD (CLI) | governance service; all work merged |
| clarion | committed HEAD (1.3.0) | includes B3 rename-feed |
| filigree | committed HEAD (3.0.0) | includes closure-gate |
| **wardline** | **working tree (uncommitted B4a)** | needed for `--format legis` |

The exact per-tool install mechanism (uv tool / pipx / cargo) is resolved in the
implementation plan; each tool is installed by its native packaging.

## The Legis governance leg

A new `legis_govern` step in `tour/steps.py`. The harness plays the **agent role**
(the architecture the handoff doc names): produce → post → record.

1. **Produce.** Run `wardline scan <specimen> --format legis --output <tmp>/scan.legis.json`
   on the clean tree. With the shared secret present (below) the artifact is
   **signed**; without it, unsigned provenance.
2. **Serve.** Start `legis serve` on a free port with:
   - `LEGIS_WARDLINE_CELL=surface_override` — **server-owned routing** (the proven
     posture; the POST body carries no routing fields),
   - a **temp governance DB** (`--governance-db`) so the run is isolated and repeatable,
   - `LEGIS_WARDLINE_ARTIFACT_KEY=<secret>` **iff** the secret is provisioned — when
     set, legis **requires** a valid signature (rejects unsigned/tampered); when
     unset, legis is in optional-verify mode.
   Probe `/health` until ready (bounded), fail-soft if it never comes up.
3. **Post.** `POST /wardline/scan-results` with `{"agent_id": "lacuna-tour", "scan": <artifact>}`.
   Legis routes the active defects into `surface_override` and returns `{"routed": […]}`.
4. **Record + stop.** Derive a **stable** detail (governed active-defect count →
   cell) for the locked narrative; capture the live `artifact_status`
   (verified/unverified) for the run **report only**. Always stop the server.

The step **never raises** (tour contract): any failure (no producer, port, server,
HTTP error) yields `ok=False` with an honest detail.

### The shared secret

Both sides key off the **same** Lacuna `.env` value (gitignored):
- wardline reads `WARDLINE_LEGIS_ARTIFACT_KEY`,
- the harness exports the same bytes as `LEGIS_WARDLINE_ARTIFACT_KEY` to the
  `legis serve` subprocess.

Because both sides read the one `.env`, they are always in sync: secret present →
signed + required + **verified**; secret absent → unsigned + optional + accepted.
Either way the POST succeeds and the governed count is identical. A committed
`.env.example` documents the key; provisioning the real value is the one operator
step (per the handoff doc: "activation, not configuration").

## Determinism (the `make verify` constraint)

`make verify` compares the generated narrative byte-for-byte, so the legis step's
locked detail must be **environment-independent**:
- **Locked narrative detail:** the governance outcome only — e.g.
  `governed N active defects → surface_override`. `N` is stable given the
  specimen's deterministic Wardline scan.
- **Never** echo the signature, `commit_sha`, `tree_sha`, run-id, ports, or the
  signed/unsigned status into the locked narrative — those vary by commit/env.
- The signed/unsigned `artifact_status` appears in the **live run report**
  (`python -m tour tour` output), not in the lockstep-checked docs — mirroring how
  the existing `filigree` step keeps a stable description rather than a live count.

If the specimen's findings change, the committed narrative is regenerated
(`make docs`) in the same commit — the existing lockstep discipline.

## Mechanical changes

- `tour/capability.py`: remove `legis` from `DESIGN_ONLY`; detect it (locate the
  `legis` CLI via PATH/`~/.local/bin`, like the others). `charter` stays design-only.
- `tour/steps.py`: add `legis_govern` (+ small helpers: free-port, server
  lifecycle, findings→post). Keep `ROOT`/`BIN` conventions.
- `tour/manifest.py` / `tour/__main__.py`: register the legis step in the run order
  (after `wardline scan`, since it consumes the scan).
- `tour/report.py` / `tour/docs_gen.py`: a `legis` row in the capability/matrix
  and a narrative paragraph naming it a governance member (not a detector).
- Regenerate `docs/tour.md` + `docs/matrix.md`; `make tour` and `make verify` green;
  `make ci` (test + scan + verify) green.
- Possibly shape the specimen so it carries at least one Wardline-active defect the
  legis leg can govern (the specimen already has planted trust-flow lacunae — to be
  confirmed in the plan; re-shape/commit if needed).

## Out of scope (later/elsewhere)

- The git-rename and Filigree closure-gate legs (a future tour section).
- Promoting `charter` (stays design-only).
- Editing Wardline's repo. **Flag for the Wardline owner:** the handoff doc
  (`wardline/docs/guides/legis-handoff.md`) still describes the *pre-relaxation*
  legis contract ("rejects any non-tier property"; drop diagnostics / map
  `baselined`→`suppressed` / relocate proof). After legis `bc43694` those are no
  longer required by legis; the doc's "legis rejects" rationale is stale.

## Testing / acceptance

- `make tour` runs the legis leg green; the report shows the governed count and the
  artifact status (verified when the secret is provisioned).
- `make verify` passes (legis lacuna/coverage assertions + byte-for-byte narrative).
- `make ci` green (test + scan + verify).
- `docs/matrix.md` shows legis as a **live governance** member.
- With the secret provisioned on a clean tree: the artifact is **signed** and legis
  records it **verified** (the full B4a handshake, demonstrated in the demo bed).
