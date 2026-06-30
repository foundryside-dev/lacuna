# Design — Plainweave coverage lacunae (baseline / verification-status / dossier)

- **Date:** 2026-06-30
- **Status:** Approved scope (owner, 2026-06-30) — design for implementation
- **Drives:** the comprehensive-coverage theme (Lacuna PDR-0020) and the elevate-to-primary
  intent (PDR-0021): cover each member's full surface as it comes online.
- **Pattern source:** `pw-intent-*` (`tour/plainweave_seed.py`, `tour/steps.py`) and the
  capability-gated peer-facts cells (PDR-0015/0016, `tour/capability.py`).

## 1. Problem & intent

Plainweave's tour coverage today exercises only its **intent** surface (`pw-intent-justified`,
`pw-intent-liveness`, `pw-intent-orphan`, `pw-surface-scoping`) plus two peer-facts cells.
Plainweave (requirements management — the member formerly *charter*) also ships **baseline**,
**verification**, and **dossier** surfaces with no planted lacuna. Under the comprehensive-coverage
intent, those are coverage gaps. This design plants three NOT-A-FLAW capability demos that each
assert plainweave's load-bearing **no-silent-clean** invariant over one of those surfaces.

These are **single-member capability-depth** cells (matrix cell `plainweave`, already exercised) —
they deepen plainweave's own-surface coverage rather than adding a new *combination* cell. That is
in scope: "comprehensive demo of the full suite" means each member's full surface, not only
cross-member combinations. The matrix's exercised-cell list will not visibly change; the coverage
shows in the lacunae count + the new tour legs.

## 2. Grounding — the real plainweave 1.1 surfaces

Verified against the installed `plainweave 1.1.0` (`uv tool`, editable from `/home/john/plainweave`):

- `plainweave baseline {create, show, list, diff}` — lock a baseline of approved requirements;
  `diff` reports drift vs current approved requirements.
- `plainweave verify {method, evidence, status}` and `plainweave status {requirement, unverified,
  stale}` — verification methods + evidence; verified / unverified / stale reporting.
- `plainweave dossier <requirement_id> [--json]` — the full requirement dossier.

These land with plainweave ≥ 1.1; **PyPI 1.0.0 lacks them** (same situation as the peer-facts
subcommands). So each cell is **capability-gated** on its subcommand (Section 4).

## 3. The three lacunae

Each is `category`-tagged, `demonstrates = ["plainweave"]`, advisory/local/never-gates, and
asserts a no-silent-clean contract. `explanation` follows the established "NOT A FLAW — a positive
plainweave capability demo …" voice.

### 3.1 `pw-baseline-drift` (category: `baseline`)
- **Anchor:** `specimen/cli.py` · `_add_book` (reuse an existing covered surface; anchors are
  presentational, the seed is what matters).
- **Assertion (all must hold to surface):** over the seed, lock a baseline of the approved
  requirements (`baseline create`), then mutate one approved requirement → `baseline diff` reports
  that requirement as **changed/removed**; an unchanged requirement does **not** appear as drift;
  and `baseline diff` with **no locked baseline** reports an honest unavailable/empty-baseline
  state — **never a silent "clean / no drift."**
- **`expected_tool`:** `plainweave-baseline` (capability) · **`expected_rule`:** `pw-baseline-drift`

### 3.2 `pw-verification-status` (category: `verification`)
- **Anchor:** `specimen/cli.py` · `_register` (or another seeded requirement's surface).
- **Assertion:** a requirement with a declared verification **method AND evidence** reports
  `verified`; a requirement with a **method but no evidence** reports `unverified` (never silently
  verified); `status unverified` lists the gap; and stale evidence is surfaced by `status stale` —
  an outdated obligation is honestly flagged, **never silently passing.** The honest
  verified / unverified / stale trichotomy.
- **`expected_tool`:** `plainweave-verify` (capability) · **`expected_rule`:** `pw-verification-status`

### 3.3 `pw-requirement-dossier` (category: `dossier`)
- **Anchor:** `specimen/cli.py` · `main` (a covered requirement's surface).
- **Assertion:** `dossier <known-req> --json` yields a **coherent** dossier (criteria + trace +
  verification status, consistent with 3.1/3.2); an **unknown** requirement id reports honestly
  (error/unavailable envelope), **never an empty-as-clean dossier.**
- **`expected_tool`:** `plainweave-dossier` (capability) · **`expected_rule`:** `pw-requirement-dossier`

## 4. Capability-gating (`tour/capability.py`)

Extend `PLAINWEAVE_PEER_FACTS_SUBCOMMANDS`-style mapping (or add a sibling map) so `detect()`
emits one capability per new subcommand, probed from the live `plainweave --help` choices block
(behaviour-probed, not version-string — the stale-build trap):

| subcommand probed | capability name (a lacuna's `expected_tool`) |
|---|---|
| `baseline` | `plainweave-baseline` |
| `verify` (or `status`) | `plainweave-verify` |
| `dossier` | `plainweave-dossier` |

Under a plainweave lacking a subcommand (PyPI 1.0.0 / fresh clone) the capability is absent → the
cell is gated **out of verify's coverage assertion** and renders `[N/A]` (did-not-run, not-failed,
not-faked) with a frozen machine-readable reason — identical to PDR-0016. `run_verify` prints the
`CAPABILITY-GATED (… not a failure)` block naming each gated lacuna.

## 5. Seed design (extend `tour/plainweave_seed.py`)

Add an opt-in seed path (parameter flags on `seed()` or a sibling `seed_coverage()` helper) that,
in an **isolated workspace** (`materialize_workspace()` pattern — copy the loomweave catalog, drop
`ephemeral.port`, offline-deterministic), additionally:
- **baseline:** `baseline create` a locked baseline over the approved requirements; then mutate one
  (`req update`/new version, or `req deprecate`) so `baseline diff` has real drift. Keep one
  requirement unchanged as the negative control. Also exercise the **no-baseline** path in a second
  clean store (or before `create`).
- **verification:** for one requirement add a `verify method` + `verify evidence` → verified; leave
  another with a method but no evidence → unverified; (stale: seed evidence then advance the
  requirement version so the evidence is stale, if the CLI supports it; else assert verified vs
  unverified only and note stale as a follow-up).
- **dossier:** no extra seeding — `dossier <req>` reads a requirement the seed already created;
  the unknown-id negative uses a non-existent id.

Determinism: frozen constants (titles/statements/ids derived from stable locators), no wall-clock,
no hardcoded hex; SEIs resolved by locator at seed time (existing discipline). The seed must be
idempotent/cold-rebuild (`rmtree .plainweave` then re-seed), like the intent leg.

## 6. Tour leg (`tour/steps.py`)

One new leg (e.g. `plainweave_coverage()`), or extend the existing pw structure, that: seeds the
coverage corpus, runs the three surfaces, evaluates each cell's predicate, and emits `surfaced`
`(token, qualname)` pairs **only when the predicate holds** (else the lacuna lands in `missing_ids`
and `make verify` reds — fail-loud, no partial credit). Determinism discipline (mirror the peer-facts
legs): `detail` is **frozen prose, no digits**; all live/variable data rides the printed-but-not-
byte-compared `note`. Each cell is capability-gated (renders `[N/A]` when its capability is absent).

## 7. Files touched

- `tour/lacunae.toml` — 3 new `[[lacuna]]` entries (Section 3) + a section comment.
- `tour/capability.py` — 3 new per-subcommand capabilities + probe.
- `tour/plainweave_seed.py` — the coverage seed extension (Section 5).
- `tour/steps.py` — the `plainweave_coverage` leg + wire into the drive; `run_verify` gated-block
  text already generic.
- `tour/__main__.py` — register the leg in the drive order if a new leg.
- `docs/flaws/pw-baseline-drift.md`, `pw-verification-status.md`, `pw-requirement-dossier.md`.
- `tests/` — `test_steps_*` unit + per-conjunct drop-tests; `test_capability.py` cases;
  `test_manifest.py` count bump (62 → 65); `test_drive.py` if leg order asserted.
- Regenerate `docs/tour.md` + `docs/matrix.md` via `make tour`.

## 8. Testing

- **Unit:** each cell's predicate evaluator with a fabricated envelope (verified/unverified;
  drift/no-drift/no-baseline; coherent/unknown dossier).
- **Per-conjunct drop-tests:** for each cell, drop each conjunct of its no-silent-clean assertion
  and confirm the cell goes `missing` (proves no hollow-gate credit) — the discipline PDR-0017 used.
- **Capability gating:** with the subcommand present → exercises; absent (simulated empty `--help`
  surface) → `[N/A]`, gated out of the coverage assertion.
- **Real-producer integration smoke:** run the actual `plainweave baseline/verify/status/dossier`
  against the seed in a temp workspace; assert envelope shapes the predicates depend on.

## 9. Acceptance criteria

1. `make verify` exits 0 on a clean tree with plainweave 1.1 installed: the 3 cells exercise green,
   surface their tokens, narrative + matrix in lockstep.
2. With a plainweave lacking the subcommands (PyPI 1.0.0 / fresh clone): the 3 cells render `[N/A]`,
   are gated out of the coverage assertion, and `make verify` does **not** red on them
   (the missing surface is explicit in stdout + `tour.md`). No fake green.
3. Per-conjunct drop-tests prove each cell fails-loud when any conjunct of its no-silent-clean
   assertion breaks (no hollow gate).
4. Manifest count test updated (65 lacunae); `docs/flaws/` complete; determinism (byte-stable
   `tour.md` across re-runs in a fixed env).

## 10. Version / narrative-bless handling

These cells inherit the PDR-0016 condition exactly: the canonical tour env is the local editable
plainweave (1.1, surfaces present → cells exercise), while the merge-gate pins PyPI 1.0.0 (surfaces
absent → cells `[N/A]`). The committed `docs/tour.md` is blessed against whichever plainweave the
merge gate pins, consistent with the peer-facts cells; capability-gating makes both renderings
honest. **No new bless mechanism is introduced** — this is the same single-environment lockstep
PDR-0016 already governs. (If `make verify` currently disagrees with the committed narrative because
the local install is 1.1 while the committed bless is 1.0.0, that pre-existing condition is logged
as a separate observation, not resolved here.)

## 11. Out of scope

- `goal` (already exercised via intent→goal laddering in `pw-intent-justified`).
- `actor` (identity-adjacent — **tabard's** forthcoming domain; planting it now would duplicate
  future tabard coverage; PDR-0021).
- `criterion` / `bind` / `trace` / `catalog` (substrate the existing intent cells already exercise).
- Any change to plainweave itself (consumer boundary — Lacuna only consumes the installed binary).

## 12. Reversal / maintenance

- If plainweave's `baseline`/`verify`/`status`/`dossier` envelope shapes change, the predicates
  (status/contract semantics, not byte-pinned) survive structure-pinned changes; update the seed +
  predicate if a contract field is renamed (and file a consumer-boundary report per PDR-0019's
  verify-before-file discipline).
- When plainweave 1.1 releases to PyPI and the merge gate pins it, the cells exercise on the gate
  too; re-bless `tour.md` to the exercised state (PDR-0016 reversal trigger).
