# PDR-0017 — Warpline peer-facts tour cells (risk-as-verification + include_federation)

- **Date:** 2026-06-28
- **Status:** Accepted (under the standing tour-regression grant)
- **Decider:** agent (ultracode, subagent-driven)
- **Related:** PDR-0015 / PDR-0016 (the plainweave peer-facts cells this mirrors),
  PDR-0013 (warpline server-side binding tools), `tour/capability.py`, `tour/steps.py`,
  `tour/__main__.py`, `tour/lacunae.toml`, warpline `[Unreleased]` CHANGELOG (release/1.2.0)

## Context

warpline's last-7-day work (release/1.2.0 `[Unreleased]`) shipped two cross-member
consumer surfaces the tour did not exercise: the **wardline-attest-2 risk-as-verification**
consumer (`reverify --attest-bundle` → `data.risk_verification`) and the **include_federation**
live consult (legis governance + wardline dossier risk + filigree work merged into the reverify
worklist). These are the *warpline half* of the peer-facts theme PDR-0015/0016 established for
plainweave: a member CONSUMING a sibling's facts. The demonstration harness must show them.

Live measurement settled what is deterministically reachable on the installed toolset:

1. **proven-good is unreachable.** The installed `wardline` (1.0.7) emits `wardline-attest-1`;
   warpline's consumer requires `wardline-attest-2`. Independently, the specimen's loomweave
   index leaves ~387 entities unresolvable (skill markdown/JSON under `.agents/`), so
   `capture-snapshot` reads `completeness=DELTA` and reverify degrades to
   `risk=unavailable, reason_code=completeness_partial` *before* the bundle is even examined.
2. **governed-present is non-deterministic.** A verified legis clearance (governance=present)
   is write-only via HTTP `POST /overrides` with a fresh wall-clock `as_of` per write, and
   needs entity SEIs that `--resolve-sei` does not populate on this tree — incompatible with a
   byte-for-byte `make verify`.
3. **The installed warpline CLI was stale.** `~/.local/bin/warpline` was a uv-tool built from
   warpline's `main` branch (`uv-receipt.toml`: `rev=main`); `main` has `include_federation`
   (so the MCP demo worked) but NOT the `release/1.2.0` `reverify --attest-bundle` / `verify-record`
   surface (same `1.2.0` version string — the stale-build trap). Refreshed via
   `uv tool install --force /home/john/warpline` (release/1.2.0); this also wired the legis
   governance consumer, so the federation block's `legis` member moved `disabled → clean`.

A separate measurement note: the pre-existing `warpline_change_impact` leg appears RED only with
a **warm** `.weft/warpline` store accumulated across many captures; from a cold store (the
fresh-clone / CI path) a single `backfill` + `capture-snapshot` is green. This is orthogonal to
Tier B and not a code defect.

## Decision

Add the two cells as **honesty-invariant peer-facts demos** — they assert warpline's thesis (it
never mints a silent clean; the federation block always names every member with a reason even
when degraded), NOT proven-good / live-verdict cells.

1. **`wp-attest-no-silent-clean`** (CLI, wardline→warpline). Builds a wardline-attest bundle into
   a throwaway tempdir (never the repo) and asserts `reverify --attest-bundle` reads
   `risk_verification.risk == "unavailable"` with a `reason_code` in a closed no-silent-clean set
   — the verdict CLASS, never a specific code. **Capability-gated** on the `reverify --attest-bundle`
   surface (`tour/capability.py::warpline_reverify_options`, registered as the
   `warpline-attest-bundle` capability), so a pre-attest-2 warpline renders `[N/A]`, exactly as
   the plainweave cells do under PyPI 1.0.0 (PDR-0016). The future flip to proven-good is one
   predicate line.
   - **Self-contained, no demo-secret dependency.** `wardline attest` needs a minted
     `WARDLINE_ATTEST_KEY` (`.env` / `wardline install`); since on a DELTA snapshot the
     impact-completeness gate pre-empts attestation (the verdict is `completeness_partial`
     regardless of the bundle — verified: real, garbage, and absent bundles all yield it), a real
     `wardline attest` is used when the key is present and a synthetic wardline-attest-shaped
     bundle is the fallback when it is not. A missing secret must never flip a *rendered* mark —
     so `make verify` is green with OR without `.env` sourced (the original live-attest call hard-
     [WARN]'d without the key, redding the gate; that regression is closed).
   - **Honest scope (no overclaim).** The cell proves the no-silent-clean *degrade* (warpline
     returns unavailable + an explicit machine reason, never a silent clean), NOT that the
     attest-consumer read path is exercised — on this snapshot the completeness gate pre-empts it.
2. **`wp-reverify-federation`** (MCP-only, legis+wardline+filigree→warpline). Drives warpline-mcp
   through the attachment transport with `include_federation=true` and asserts the federation
   STRUCTURE: all three members present, each with a `weft_reason.reason_class` in
   `{clean,disabled,unreachable}`, plus the closed-vocab `{work,risk,governance}` enrichment
   scalars. Per-member verdicts vary with reachability and ride the non-rendered `note`. Gated
   `expected_tool = "warpline"` (mandatory) because `include_federation` is an MCP-only feature
   that cannot be probed cheaply *and deterministically* in `detect()` without risking a
   `matrix.md` flap; a federation-less warpline-mcp would red it (an honest signal), with the
   cause named in `note`.

Determinism mirrors the existing warpline/peer-facts legs: `detail` is frozen prose (no digits),
`surfaced` is a stable `(token, qualname)` pair emitted only when the predicate holds (else the
lacuna lands in `missing_ids` and `make verify` reds — fail-loud, no partial credit), and all
live/variable data rides `note` (printed, never byte-compared).

## Consequences

- Both cells exercise green on the refreshed toolset: `wp-attest-no-silent-clean` is `[PASS]`
  (`reason_code=completeness_partial`), `wp-reverify-federation` is `[PASS]` (members
  filigree=clean, wardline=unreachable, legis=clean). New matrix cells `wardline+warpline` and
  `filigree+legis+wardline+warpline` render exercised.
- `make verify` byte-locks `docs/tour.md` + `docs/matrix.md` against the refreshed environment
  (release/1.2.0 warpline, wardline 1.0.7). A different member version requires a `make tour` regen
  — the normal consequence of a version change, not a defect.
- `wp-attest-no-silent-clean` gates to `[N/A]` under any warpline lacking `reverify --attest-bundle`
  (fresh clone with a PyPI/main warpline), so the cell is robust, not a forced red.

## Reversal trigger

- When a `wardline-attest-2` producer is installed AND the specimen snapshot reaches
  `completeness=FULL`, proven-good becomes reachable: flip `wp-attest-no-silent-clean`'s predicate
  to `risk=="proven" and reason_code=="attested_clean"` and re-bless `docs/tour.md`.
- If a governed-present (legis clearance) cell becomes a hard requirement, it needs a committed
  frozen-clock pre-seeded legis store + enum-only assertions + `--resolve-sei` actually populating
  entity SEIs (it did not on this tree); revisit then.
- If warpline's reverify `--help` format changes such that the option probe returns empty, the cell
  gates to `[N/A]` rather than silently passing — update `capability.warpline_reverify_options`.
