# Cold-eval onboarding report — 2026-06-19

> **Resolution note (added post-run):** the two Legis discrepancies this report
> surfaced were root-caused and fixed in **legis 1.1.0**: posture_get / policy_list
> on an unprovisioned ledger no longer throw `no such table: audit_log` — they
> degrade to a fail-closed `structured` floor (legis-5fd3b257c3); and the
> both-boundary `POLICY_BOUNDARY_TEST_FINGERPRINT_MISMATCH` was the fingerprint
> scheme being interpreter-fragile (raw `ast.dump`) — 1.1.0 makes it version-stable
> (`_stable_ast_repr`, legis-13b4e97bf4) and lacuna's specimen pins were regenerated
> against it. The observations below are preserved as the point-in-time record of
> the 2026-06-19 run. (The Warpline stale-snapshot item is unrelated and still open.)

**Brief:** `docs/dogfood/2026-06-15-cold-eval-BRIEF.md` ("come up to speed on an
unfamiliar repo", answer Part A, then a candid debrief). Run fresh on 2026-06-19;
the `2026-06-15` report already existed, so this is dated to the actual run day.

**Posture:** read-only. Nothing in the tree was changed. Index/state observed at
git `3158d62`; Loomweave index fresh (391 entities, 808 edges, 26 subsystems,
analyzed `3158d62`); Warpline snapshot `c5450d19`, **18 commits behind HEAD**.

---

## Part A — answers

### 1. Orientation
**Lacuna is a deliberately-flawed reference application** — the *specimen* the
Weft tool federation is demonstrated against. It is not a roster member; it is the
shared test corpus. (`README.md:1-8`.)

Major parts:
- **`specimen/`** — a clean-cored in-memory library app (books, users, loans)
  with documented *lacunae* (planted flaws) isolated into named modules. Core
  domain: `models.py` (Book/User/Loan/Money), `repository.py` (repos +
  mixins/inheritance), `service.py` (`LibraryService`, strategy + observer +
  audit-decorator), `cli.py` (argv → service, the untrusted-input boundary).
  Flaw modules: `trust_flow.py`, `exception_flow.py`, `wardline_sinks.py`,
  `wardline_boundaries.py`, `preview_sinks.py`, `policy_boundaries.py`,
  `dead_code.py`, `cycle_a/b.py`, `hub.py`, `nesting_bomb.py`, `colliding*.py`.
- **`specimen-rs/`** — a small Rust specimen (command/shell-injection slice).
- **`specimen_quarantine/`** — intentionally unparseable / malformed artifacts
  (fail-closed demos).
- **`tour/`** — the harness (`python -m tour`) that drives every live Weft tool
  against the specimen and regenerates docs; **`tour/lacunae.toml`** is the single
  source of truth for the planted flaws.
- **`docs/flaws/`** — generated per-lacuna explainers; **`docs/`** also holds the
  generated tour narrative/matrix and the dogfood reports.
- **`site/`** — a static marketing/docs site (GitHub Pages).

*How I got it:* `README.md` + `loomweave project_status_get` for counts/freshness,
then `find specimen*` + the head of `tour/lacunae.toml`. Clean and fast — the
README is unusually explicit about the project's purpose.

### 2. Dead code
**Yes — the canonical example is `specimen/dead_code.py::orphaned_helper`**
(`specimen/dead_code.py:9-11`), a function with no callers. This is the planted
`lw-dead-code` lacuna and `loomweave entity_dead_list` surfaces it.

**Caveat I want to be honest about:** `entity_dead_list` returned **141 dead
candidates (52% of analysed entities)** and *self-flagged the result as LOW
confidence* — the configured reachability roots don't cover this corpus (a library
exercised mainly by tests), so it over-reports. Genuinely-live code like
`LibraryService`, `Repository`, and `Book.key` appears in the "dead" list. So I
trust the *named planted orphan* (and `hub.py`'s `Dispatcher`, which nothing
reaches), but the broader list needs per-entity confirmation by reading. The tool
told me this itself, which is the right behaviour — but it means the raw list is
not directly answerable.

*How I got it:* `loomweave entity_dead_list`; cross-checked against
`tour/lacunae.toml` and read the advisory block.

### 3. Structural health
**Circular import:** `specimen.cycle_a ↔ specimen.cycle_b`
(`specimen/cycle_a.py` ⇄ `specimen/cycle_b.py`) — a clean 2-module cycle, the
planted `lw-circular-import`. `loomweave module_circular_import_list` returns
exactly this one cycle, confidence `resolved`.

**Tight coupling (in-package):** `specimen/hub.py::dispatch` is the specimen's
coupling hotspot — coupling score 10 (fan-in 5 / fan-out 5), the planted
`lw-coupling-hotspot`. Loomweave also flags `LMWV-FACT-CLUSTERING-WEAK-MODULARITY`
(weak subsystem modularity) at the project level.

*How I got it:* `loomweave module_circular_import_list` and
`entity_coupling_hotspot_list`. Both landed first try.

### 4. Find by intent — "adds a book to the library"
Two layers:
- **`specimen/cli.py:44-48` `_add_book`** — the `add-book` CLI command handler
  (tagged `cli-command`); takes `isbn,title,author` from untrusted argv and calls
  the service.
- **`specimen/service.py:81-83` `LibraryService.add_book`** — the domain method,
  decorated `@audited("catalog")`; delegates to `BookRepository.add`.

*How I got it:* `README.md` already names `specimen/cli.py::_add_book`; I confirmed
with `loomweave entity_find pattern=add_book` (returned both layers in one call)
and read the source. **Friction:** my first `entity_find` call failed — I guessed
the arg name `query`; the schema wants `pattern`. One wasted call.

### 5. Known quality / security issues
Lacuna is *seeded* with catalogued flaws (`tour/lacunae.toml`, ~40 entries). The
live tools confirm them:

**Security / trust-boundary (Wardline taint scan, 34 files):** the gate trips with
a full slate of planted defects — e.g.
- `eval()` on untrusted input — `wardline_sinks.eval_report_formula` (PY-WL-107, `specimen/wardline_sinks.py:44`)
- `pickle.loads()` on untrusted blob — `import_catalog_blob` (PY-WL-106, line 37)
- `os.system` / `subprocess(shell=True)` command injection — `run_export_command` (PY-WL-108, line 51), `shell_archive` (PY-WL-112, line 58)
- SQL injection via `execute()` — `lookup_member` (PY-WL-118, line 89)
- SSRF `requests.get()` — `fetch_cover_image` (PY-WL-117), XXE `lxml` (PY-WL-121), SSTI `jinja2.Template` (PY-WL-122)
- trust-boundary logic flaws — fail-open boundary (PY-WL-113), assert-only boundary stripped under `-O` (PY-WL-111), degenerate/non-rejecting boundaries (PY-WL-119/102)
- Rust: `Command::new` program injection (RS-WL-108) and `sh -c` shell injection (RS-WL-112) in `specimen-rs/src/main.rs`.

**Structural / archaeology (Loomweave `project_finding_list`, 11 findings):**
duplicate entity locator `specimen.colliding.ShelfMark` (LMWV-DUPLICATE-LOCATOR,
ERROR — same id declared in `colliding.py` and `colliding/__init__.py`, last write
wins), `nesting_bomb.py` too complex to extract (LMWV-PY-TOO-COMPLEX),
`specimen_quarantine/unparseable.py` syntax error, weak subsystem modularity, and
**secret-detection ERRORs** (HighEntropyHex in `.env`, `tour/steps.py:481`,
`policy_boundaries.py`).

**Live gate state:** `wardline scan --fail-on ERROR` reports `active: 1` (the
deliberately-unbaselined sentinel `wl-log-injection` / PY-WL-125 in
`preview_sinks.py`), `baselined: 42`. The gate shows `FAILED` here because the
secure default re-evaluates the baselined population unless you pass
`--trust-suppressions` on a trusted checkout — so "FAILED / 22 suppressed ERROR+
re-enter the gate" is the *expected* secure-default reading, not drift. The
intended green state is "1 active" (the sentinel). This matched prior project
notes.

*How I got it:* `wardline scan` (live), `loomweave project_finding_list`, and
`.weft/wardline/baseline.yaml` for the catalogued IDs. All landed cleanly.

### 6. Biggest coupling hotspots in *just* `specimen`
Filtering `entity_coupling_hotspot_list` to `specimen/` paths (the raw list is
whole-project and dominated by `tour/`):
1. **`specimen.hub.dispatch`** — coupling 10 (fan-in 5 / fan-out 5). *The* hotspot.
2. **`specimen.wardline_sinks.read_admin_arg`** — coupling 8 (fan-in 8) — a shared
   untrusted-source helper many sinks pull from.
3. **`specimen.preview_sinks.read_report_field`** — coupling 6 (fan-in 6) — same
   shape for the preview sinks.
4. **`specimen.models.Entity.key`** — coupling 5 (fan-in 5) — the identity method
   the repositories key on.

*How I got it:* `entity_coupling_hotspot_list`. **Friction:** there's no
package/path filter argument — I scoped to `specimen` by eye against the
whole-project list (top entries were all `tour.*`). Minor, but I did the filtering
by hand.

### 7. Change impact of the add-book function
Reconstructed from Loomweave call graph + source (see friction below):
- **`cli._add_book`** is invoked *dynamically* via the `App._commands` decorator
  registry (`App.run`), so the static caller edge is unresolved — Loomweave reports
  1 unresolved attribute-receiver call site (`app.service.add_book`). Changing its
  signature affects the `add-book` CLI command contract.
- **`service.add_book`** is wrapped by **`@audited("catalog")`**, so every call
  emits a `catalog:<book.key>` event to all subscribers (the stderr audit lambda
  registered in `App.__init__`). Touching its return type or `Book.key` ripples
  into the audit string.
- Downstream callees: **`BookRepository.add`** (`InMemoryRepository.add`) and the
  **`Book` / `Book.key`** model. Loan/checkout paths are unaffected.

**The honest part:** the *right* tool for this question is Warpline
(`blast_radius` / `reverify`), and **it could not answer**. The stored edge
snapshot is `c5450d19`, **18 commits behind HEAD**, and `_add_book`'s SEI returned
`sei_not_in_snapshot` → it degraded honestly to `DELTA`/`STALE` with an *empty*
affected set and a warning to `warpline capture-snapshot` first. So I fell back to
`loomweave entity_callers_list` + reading `cli.py`/`service.py` to hand-build the
impact set. Warpline degraded correctly (it didn't fabricate an answer), but it
gave me no usable change-impact without first re-capturing a snapshot.

### 8. Governance / policy / sign-off signal
There **is** a governance layer (Legis), attached at the policy-boundary level:
- `specimen/policy_boundaries.py` declares two **`@policy_boundary`** decorators
  with `invariant` / `suppresses` / `test_ref` / `test_fingerprint` metadata —
  `validated_recovery` (intended HEALTHY) and `pinned_import` (the planted
  `lg-disabled-boundary-evidence` lacuna; its evidence test is `@pytest.mark.skip`).
- The catalogue expects `legis policy-boundary-check` to flag `pinned_import` with
  **`POLICY_BOUNDARY_TEST_DISABLED`**.
- Other governance demos: `lg-zero-under-green` — Legis rejects a wardline artifact
  with the `findings` key absent (HTTP 422) rather than routing "zero defects under
  green"; plus the malformed-artifact rejection leg.
- `override_rate_get` (the one Legis MCP tool that responded): `PASS_WITH_NOTICE`,
  rate 0, sample 0.

**Two honest discrepancies surfaced by the live tools:**
1. **Legis MCP governance reads are broken in this session.** `posture_get` and
   `policy_list` both threw `INTERNAL_ERROR: no such table: audit_log` — the
   binding-ledger DB has no `audit_log` table (the closure gate is effectively
   un-provisioned). The SessionStart hook claims "posture floor: none
   (fail-closed structured)" and `policy/cells.toml` maps 4 policies, but I could
   not read posture or the policy routing table over MCP. I fell back to reading
   `policy_boundaries.py` and `docs/flaws/lg-*.md`.
2. **The live boundary check disagrees with the catalogue.**
   `legis policy_boundary_check root=specimen` returned, for *both* boundaries,
   **`POLICY_BOUNDARY_TEST_FINGERPRINT_MISMATCH`** (not the expected
   `TEST_DISABLED` on `pinned_import`), plus a graceful
   `POLICY_BOUNDARY_FILE_TOO_COMPLEX` per-file degrade on `nesting_bomb.py`. So the
   stored `test_fingerprint`s in `policy_boundaries.py:28,41` no longer match the
   referenced tests. That is either unflagged fixture drift or a tool ordering
   choice (fingerprint checked before skip-mark) — worth a maintainer's eye; I did
   not change anything. (The MCP path *did* handle `nesting_bomb.py` gracefully,
   unlike the CLI's documented RecursionError — a genuine improvement.)

---

## Part B — debrief

### How you worked

| Q | Reached for first | Answered cleanly? | Fell back to reading/searching by hand? |
|---|---|---|---|
| 1 Orientation | `README.md` + `project_status_get` | Y | Y — README is the real answer; tools confirmed counts |
| 2 Dead code | `entity_dead_list` | Partly | Y — tool self-flagged LOW confidence (52% FP), so I confirmed the named orphan by reading |
| 3 Structure | `module_circular_import_list` + `coupling_hotspot_list` | Y | N |
| 4 Add-book | `entity_find` (+ README) | Y (2nd try) | Y — read `cli.py`/`service.py` to confirm; 1st `entity_find` failed on arg name |
| 5 Known issues | `wardline scan` + `project_finding_list` | Y | N (read `baseline.yaml`/`lacunae.toml` to enumerate IDs, by choice) |
| 6 specimen hotspots | `entity_coupling_hotspot_list` | Y | Y — no package filter; scoped to `specimen/` by eye |
| 7 Change impact | `warpline blast_radius`/`reverify` | **N** | Y — snapshot 18 commits stale → fell back to `entity_callers_list` + source |
| 8 Governance | `legis posture_get`/`policy_list` | **N** | Y — MCP threw `no such table: audit_log`; read source + `docs/flaws/` |

### Scores (1–5, 5 = best)
- **Ease — 4.** For the structural/archaeology questions (2,3,4,6) the right query
  existed and returned the answer in one call. The two questions that lean on
  *temporal* and *governance* state (7,8) didn't answer at all and forced a manual
  fallback.
- **Trust — 4.** Where the tools answered, I trusted them *because* they were
  candid about their own limits — `entity_dead_list` told me it was low-confidence,
  Warpline told me its snapshot was stale, the wardline gate explained exactly why
  it said FAILED. That honesty is the product's best feature; it's worth more than a
  confident wrong number. I still confirmed planted items against source.
- **Knew-where-to-look — 4.** The CLAUDE.md / skill routing made the
  tool→question mapping obvious (dead code → loomweave, taint → wardline, impact →
  warpline, governance → legis). I nearly answered Q6 from the raw whole-project
  list before noticing it was `tour`-dominated and needed manual scoping.
- **Friction — 3.** Three distinct snags: an arg-name guess (`query` vs
  `pattern`), an unhelpful empty-arg error from `entity_kind_list`, a stale Warpline
  snapshot, and a hard SQLite error from two Legis tools. None catastrophic, but Q7
  and Q8 each cost a fallback.
- **Next time — 4.** I'd work this way again for *structure/security/archaeology*
  — it's genuinely faster and more trustworthy than grepping a 391-entity tree by
  hand. For *change-impact and governance* I'd either fix the prerequisite
  (`warpline capture-snapshot`, provision the Legis ledger) first, or go straight to
  the call graph + source.

### Open
- **Worst moment:** Q8. Two Legis MCP tools (`posture_get`, `policy_list`) crashing
  with `no such table: audit_log` — a stack-trace SQLite error, not a graceful
  `CELL_NOT_ENABLED`. The governance read surface was simply unavailable, and the
  one check that *did* run (`policy_boundary_check`) contradicted the catalogue's
  expected rule. Governance was the question I could *least* answer from the tools.
- **Best moment:** the live `wardline scan` — one call returned 34 files scanned,
  the active-vs-baselined split, the exact gate reason, *and* emitted to Filigree +
  wrote 227 entity facts to Loomweave. Reconstructing that whole-program taint map
  (eval/pickle/SQLi/SSRF/SSTI + the boundary-logic flaws) by reading would have
  taken an hour and I'd have missed cases.
- **Where you fell back (the unsoftened list):**
  - **Q4** — `entity_find` failed on a guessed arg name (`query`); retried with
    `pattern`. Then read `cli.py`/`service.py` to confirm the two layers.
  - **Q2** — `entity_dead_list` self-rated LOW confidence (52% false-positive
    rate, roots don't cover a test-exercised library), so I trusted only the named
    planted orphan and read to confirm rather than believing the list.
  - **Q6** — no package-scope filter on `coupling_hotspot_list`; I filtered the
    whole-project list to `specimen/` paths by hand.
  - **Q7** — Warpline `blast_radius`/`reverify` returned an empty set
    (`sei_not_in_snapshot`, snapshot 18 commits stale). Rebuilt the impact set from
    `entity_callers_list` + source. The proper answer needs `capture-snapshot` first.
  - **Q8** — Legis `posture_get`/`policy_list` threw SQLite errors; read
    `policy_boundaries.py` and `docs/flaws/lg-*.md` instead.
  - **Setup** — `entity_kind_list` rejected an empty argument with a bare
    "kind must be a non-empty string"; not blocking, but an unhelpful first contact.
- **One change:** make the *temporal* and *governance* surfaces fail like the
  others do — *with a next-action, not a crash or a silent stale answer*. Warpline
  already points me at `capture-snapshot`; Legis should say "ledger not provisioned,
  run X" instead of leaking a `no such table` SQLAlchemy trace. Same honesty
  standard the wardline gate and dead-code list already meet.
- **Would you recommend this way of working to another engineer? Yes** — for
  orientation, dead-code, structure, and security the curated graph/taint queries
  beat hand-searching decisively; just keep the source open to confirm anything a
  tool self-flags as low-confidence, and don't expect the temporal/governance
  layers to answer until their snapshots/ledgers are provisioned.

### Headline
A genuinely good way to onboard — the Loomweave/Wardline queries answered
structure, dead-code, and security faster and more honestly than grepping ever
would; **the catch is the two state-dependent layers (Warpline's stale snapshot,
Legis's un-provisioned ledger) couldn't answer their questions, and both times I
fell back to the call graph and the source.**
