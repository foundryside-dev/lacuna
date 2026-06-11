# Lacuna — federation 48h-additions design

**Date:** 2026-06-12
**Status:** Design (awaiting review → implementation plan)
**Builds on:** `2026-06-05-lacuna-repivot-design.md` (manifest-driven specimen + tour architecture — unchanged here)

## One-line

Fold the federation's last 48 hours of shipped capability (wardline preview rules +
Rust frontend gold, loomweave Rust plugin gold + collision/complexity alarms, legis
1.0.0 governance reads, filigree 3.0.0 work-cycle verbs) into the lacuna demo as
**13 new lacunae and 4 new tour legs**, landed in three always-green waves.

## Locked decisions (from brainstorming)

| Decision | Choice |
|---|---|
| Scope | All six candidate items, one spec. |
| Structure | **Approach A — three waves on the existing single-tour spine.** Each wave merges with `make ci` green; a dogfood pass can run between waves. |
| Rust quality bar | Crate must compile; `make ci` runs `cargo check` **capability-gated** (honest degrade when no Rust toolchain — same pattern as tour tool detection). |
| Filigree leg repeatability | **Single sentinel issue, cycled**: first run promotes one designated finding; later runs reopen → claim → close the same issue. Exactly one durable, labelled tracker artifact. |
| Fail-closed fixtures | **Committed quarantine dir** `specimen_quarantine/`, excluded from the main scan root, pytest, and loomweave indexing; a dedicated tour leg scans/feeds it expecting the gate to TRIP (failure asserted as pass). |

## Cross-cutting rules (all waves)

- `tour/lacunae.toml` remains the single source of truth. It gains three **optional**
  fields, defaulted so existing entries are untouched:
  - `lang` — `"python"` (default) or `"rust"`.
  - `expected_kind` — `"finding"` (default) or `"gate-trip"` (the lacuna is
    demonstrated by a gate/ingest **failure**, asserted by nonzero exit / rejection).
  - `scan_target` — defaults to the main scan root; quarantine entries point at
    `specimen_quarantine/`.
- Id prefixes: `wl-` / `lw-` continue; `lg-` (legis) and `rs-` (Rust) join.
- Always-green invariant: every wave merges with `make ci` green. Gate-eligible
  planted findings are baselined exactly like the current 34. The one deliberate
  exception (the gate-immune sentinel) is documented below.
- Everything downstream (verify assertions, `docs/flaws/` pages, `docs/matrix.md`,
  `docs/tour.md`) continues to derive from the manifest; no hand-maintained docs.
- New dev dependency: **legis** joins lacuna's `.venv` (installed from
  `/home/john/legis`) so `from legis.policy.decorator import policy_boundary`
  imports cleanly under pytest. The boundary *check* itself is a static AST scan
  and does not import the specimen.

## Wave 1 — eight new Python lacunae (no harness changes)

### Six wardline preview-rule lacunae — new `specimen/preview_sinks.py`

Mirrors the `wardline_sinks.py` pattern: one minimal, documented trigger per rule.

| Lacuna id | Rule | Severity | Planted trigger |
|---|---|---|---|
| `wl-xxe` | PY-WL-121 | ERROR (lxml) | tainted text → `lxml.etree.fromstring` |
| `wl-ssti` | PY-WL-122 | ERROR | tainted source → `jinja2.Template` |
| `wl-reflection-injection` | PY-WL-123 | WARN | tainted NAME arg → `setattr` |
| `wl-native-lib-load` | PY-WL-124 | ERROR | tainted path → `ctypes.CDLL` |
| `wl-log-injection` | PY-WL-125 | INFO | tainted msg → `logging.info` |
| `wl-mail-injection` | PY-WL-126 | WARN | tainted to_addrs/msg → `smtplib.SMTP.sendmail` |

Preview rules fire by default but are **not gate-eligible** (wardline filters
`Maturity.PREVIEW` from the `--fail-on` gate), so `make scan` stays green
regardless. Five of the six are **baselined** anyway to keep the Filigree banner
quiet. `wl-log-injection` deliberately stays **unbaselined**: it is the designated
sentinel for the Wave-2 filigree leg, because `finding_promote` refuses suppressed
findings without `force=true`, and an active, gate-immune INFO finding is the
honest thing to promote.

### Two loomweave lacunae

- **`lw-too-complex`** — a committed, generated deep-nesting bomb
  (`specimen/nesting_bomb.py`, excluded from pytest imports). The python plugin
  degrades it to a single module entity with `parse_status="too_complex"` and
  emits the `LMWV-PY-TOO-COMPLEX` warning finding. Asserted via
  `project_finding_list` (rule-id filter).
- **`lw-duplicate-locator`** — a planted entity-id collision that fires
  **`LMWV-DUPLICATE-LOCATOR`** (ERROR, project-anchored), asserted via
  `project_finding_list`. ⚠️ **Open verification item (first implementation task
  of this lacuna):** Python qualnames embed the module path, so the candidate
  trigger is the classic module-route collision `specimen/colliding.py` +
  `specimen/colliding/__init__.py` (in-run cross-file duplicate). Fallback if
  that resolves cleanly: a property getter/setter same-qualname pair — but per
  ADR-052 the python plugin drops duplicates first-wins *plugin-side*, so the
  fallback may demonstrate the drop-stats path rather than the host alarm.
  Verify empirically which construct reaches the host-side duplicate guard;
  the manifest entry records whichever fires.

**Wave-1 exit:** 36 lacunae in the manifest; one baseline refresh; `make ci` green.

## Wave 2 — four new tour legs

### Legis policy-boundary leg (`lg-disabled-boundary-evidence`)

The specimen gains two `@policy_boundary`-decorated functions:

- **Passing:** `source`, `suppresses`, `invariant`, `test_ref`, `test_fingerprint`
  all valid; the referenced test calls the boundary and asserts the suppressed
  policy name alongside the call result.
- **Failing (the lacuna):** identical shape, but its evidence test carries
  `@pytest.mark.skip` → `POLICY_BOUNDARY_TEST_DISABLED`.

The leg runs `legis policy-boundary-check` and asserts: exit 1; the findings name
exactly the planted failing qualname; the passing boundary is **absent** from the
findings (the check discriminates, it does not blanket-fail).

### Filigree sentinel leg (work-cycle + query honesty)

Driven over HTTP against the live server (`:8749`, project `lacuna`):

- **First run:** `POST /api/weft/findings/promote` by the sentinel's fingerprint
  (`labels: ["tour-sentinel"]`, `actor: "tour"`) → bug issue at `triage`
  (`created=true`); then `start-work --advance` using the new **claim-by-actor**
  form (no `--assignee`); then close.
- **Subsequent runs:** promote is idempotent (same issue, `created=false`) →
  `issue_reopen` → claim-by-actor → close.
- **Query assertions every run:** a `priority_min`/`priority_max` range filter
  returns the sentinel; the `summary_get` / files-stats **suppressed-severity
  breakdown** sums to the baselined count — the live proof of the FIL-1
  "baselined counted as actionable" honesty fix.

### Wardline fail-closed leg (`wl-unparseable`, `gate-trip`)

`specimen_quarantine/unparseable.py` is a committed file with a syntax error.
The quarantine dir is excluded from the main root via the wardline config
`exclude` patterns (fnmatch; scanning a subdirectory directly bypasses the
parent's excludes — confirmed mechanism) and from pytest collection. Loomweave
exclusion is preferred but its config mechanism is unverified: if loomweave has
no per-path ignore, accept the one parse-degraded entity and keep it out of the
clean-core count assertions instead. The leg runs
`wardline scan specimen_quarantine --fail-on-unanalyzed` and asserts the gate
**trips** with `WLN-ENGINE-PARSE-ERROR` in the unanalyzed set. (Parse failures
are FACT findings — not baseline-eligible — which is exactly why the quarantine
design is needed rather than in-tree baselining.)

### Legis G1 negative leg (`lg-zero-under-green`, `gate-trip`)

`specimen_quarantine/malformed_artifact.json` — a structurally valid wardline
scan artifact whose `findings` key is **absent**. The leg hands it to legis's
ingest path and asserts the rejection (`WardlinePayloadError` →
`INVALID_ARGUMENT` / HTTP 422: "a renamed or dropped findings key must not read
as zero defects"), demonstrating fail-closed routing instead of zero-under-green.

**Wave-2 exit:** 39 lacunae (three new manifest entries; the filigree leg reuses
the Wave-1 sentinel rather than adding one); tour has four new legs; exactly one
new durable tracker artifact (the labelled sentinel issue); `make ci` green.

## Wave 3 — the Rust wing

### The crate

`specimen-rs/` at repo root: `Cargo.toml` (package `specimen_rs`) + `src/` — a
small, genuinely clean-cored CLI slice in the lacuna ethos, with five planted
lacunae:

| Lacuna id | Surface | Demonstrates |
|---|---|---|
| `rs-untrusted-command` | wardline RS-WL-108 | external input reaches `Command::new` inside a `/// @trusted` fn |
| `rs-untrusted-shell` | wardline RS-WL-112 | tainted argument on a `sh -c` command line |
| `rs-derives` | loomweave | `#[derive(...)]` → anchored `derives` edges |
| `rs-cfg-twin` | loomweave | two mutually-exclusive `#[cfg]` impls split into `@cfg(...)` qualname twins |
| `rs-path-mount` | loomweave | a `#[path]` module mount routed correctly (ADR-049 Amendment 8) |

RS-WL findings are stable (wlfp2 fingerprints), gate-eligible, and
baseline-eligible — both taint lacunae are **baselined** like the Python 34.
The three archaeology lacunae follow the existing `lw-` navigation-token style:
the harness asserts the planted structures from the loomweave DB; they are not
wardline rules. A tour step additionally resolves a pasted
`specimen_rs::...` `::`-dialect path through `entity_resolve`.

### Wiring

- `make scan` gains a second line:
  `wardline scan . --lang rust --fail-on ERROR --trust-suppressions`.
  The editable wardline install already carries the `rust` extra; the loomweave
  rust plugin is confirmed installed (it loads and skips on zero `.rs` files today).
- `make ci` gains the capability-gated `cargo check` (runs when a Rust toolchain
  is present; degrades with an honest note when not).
- Manifest entries carry `lang = "rust"`. Loomweave needs no config change —
  the rust plugin auto-discovers `.rs` by extension once the `Cargo.toml`
  crate root exists.
- Known upstream gap, accepted: wardline config severity overrides do not yet
  apply to Rust findings (hardcoded base severities).

**Wave-3 exit:** 44 lacunae across two languages; `make ci` green.

## Testing & error handling

- Tests follow the existing per-surface pattern (`test_steps*.py`,
  `test_manifest.py`, `test_docs_gen.py`); `test_specimen_imports.py` learns to
  skip the nesting bomb and the quarantine dir.
- `make verify` keeps its contract — every manifest lacuna surfaced, narrative in
  lockstep. `expected_kind = "gate-trip"` entries are asserted by expecting the
  failure (nonzero exit / rejection); a quarantine gate that does NOT trip fails
  verify.
- Capability degradation stays honest, per `tour/capability.py`: missing cargo →
  compile check skipped with a note; the Rust scan/archaeology legs run whenever
  wardline/loomweave are present (the frontends ship inside them).

## Risks

1. **LMWV-DUPLICATE-LOCATOR trigger uncertainty** — carried as an explicit
   first-task verification with two named candidate constructs (Wave 1).
2. **Day-old gold Rust plugins** (wardline Rust frontend, loomweave rust plugin
   both went gold 2026-06-10/11) — quarantined to the last wave; any upstream
   defect found becomes a filigree issue in the *tool's own* tracker, which is
   itself dogfooding output.
3. **The unbaselined sentinel changes the scan summary** from "0 active" to
   "1 active (preview, gate-immune)". The narrative is regenerated so it stays
   truthful; the README's framing must mention the sentinel so nobody "fixes" it.

## Rejected alternatives

- **Big-bang single branch** — `make ci` red for the whole window; the riskiest
  part (Rust) holds the easy 80% hostage.
- **Ephemeral fail-closed fixtures** — repo stays pristine but the fixture isn't
  a browsable committed lacuna; rejected in favour of the quarantine dir.
- **In-tree baselined unparseable file** — impossible: parse failures are FACT
  findings and not baseline-eligible; would also break pytest/loomweave on the
  broken file.
- **Create-and-delete filigree cycle** — leans on the irreversible admin delete
  verb and leaves no durable trace of the demo.
