# PDR-0011 — loomweave v10→v11 build sync + duplicate-locator harness reconcile (north-star restored)

- **Date:** 2026-06-26
- **Status:** Accepted (env reinstall + the 3 commits owner-authorized in-session; harness reconcile within grant)
- **Decider:** human owner (John) authorized the reinstall and the commits; agent:claude-product-owner for the diagnosis + reconcile
- **Related:** [[loom-uvtool-build-staleness]] memory, metrics.md north-star + G1, PDR-0009, PDR-0010, PDR-0005 (env-reinstall precedent), [[loomweave-filigree-finding-bridge-gap]] memory

## Context

ORIENT found the workspace's recorded state was **false on its two headline numbers**: it said "G1 4/4 met" and "north-star RED only due to dirty tree (green at `d09da33`)." Both were wrong.

Root cause (single): **loomweave's installed uv-tool binary was a stale same-version build** — `1.3.1`, schema **v10** — against a **v11** DB written by a newer source build (`/home/john/loomweave` HEAD, 27 commits past the `v1.3.1` tag). A naive version check can't see this (same version string — the [[loom-uvtool-build-staleness]] pattern). One root cause explained every symptom:

- **loomweave MCP server silently de-attached** (`loomweave serve` couldn't open the v11 DB) → no `mcp__loomweave__*` → G1's two Loomweave→Filigree joins unreachable → **G1 regressed to ~2/4, tripping its reversal trigger**.
- **`make verify` RED** — its `loomweave analyze` + warpline `capture-snapshot` ran the v10 binary against the v11 DB → **5 catalogued lacunae dark** (`lw-duplicate-locator` + 4 `wp-*`) → a real specimen-fidelity failure, not the recorded dirty-tree artifact.

The gate caught the breakage **loud** (fail-loud, no silent pass) — but only after manual probing; `make verify` itself had been mis-reported green.

## Decision

1. **Reinstall loomweave v11 from source HEAD** over the pinned binary (owner-authorized; Lacuna's own env, PDR-0005 precedent; loomweave **source untouched** — installed the owner's already-built `target/release` binary; old v10 backed up at `…/uv/tools/loomweave/bin/loomweave.v10-stale.bak`).
2. **Reconcile the tour's `_finding_qualname`** to v11's reshaped `LMWV-DUPLICATE-LOCATOR` evidence (v11 anchors to `python:class:…` and moved the planted path from `first_source_file_path` to a new `colliding_source_file_path`, repurposing the old key for the package `__init__.py`). Prefer the new key, fall back to the old — tolerant of both builds. Added a v11 regression test.
3. **Commit** the fix (`c2f4b5a` fix, `4734a4e` chore, `445c270` tour regen), authored as tachyon-beep, not pushed.

**Result:** all 52 lacunae surface; `make verify` exit 0 on a clean tree at `445c270`; loomweave MCP reattached after the owner's MCP restart; G1 joins reachable again.

## Consequences

- **North-star restored GREEN** — root-caused and fixed, not suppressed; the metrics reading is corrected (the prior "dirty-tree only" reading was wrong).
- **G1 restored** from its tripped state.
- **Strong evidence for Phase 2** (PDR-0010): a silent member de-attach went undetected by the gate until manual probing. A 6-member attachment regression-harness with liveness classes (PDR-0009) would have tripped `make verify` automatically.
- **Escalated (pending owner sign-off):** a consumer-boundary bug report to loomweave that v11 **silently renamed the duplicate-locator evidence contract** (anchor + key) with no signal, breaking a downstream reader. Filing to a sibling member's tracker gates to the owner (mirrors PDR-0006).

## Reversal trigger

North-star reversal trigger (suppressing a real defect to keep the gate quiet) was **NOT** tripped — a real defect was fixed honestly. If a `uv tool upgrade loomweave` later reverts the binary to the stale published build, re-sync from source (the install is a `cp` over the uv path; uv's receipt still reads `1.3.1`). If the duplicate-locator emission proves order-non-deterministic across analyze runs, that is itself a consumer-boundary loomweave finding to report, not a Lacuna fix.
