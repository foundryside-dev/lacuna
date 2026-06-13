# Consumer-boundary report — warpline `capture-snapshot` is `$PATH`-fragile

**Reporter:** Lacuna (demonstration specimen / dogfood range)
**Date:** 2026-06-13
**Owning member:** warpline (with a loomweave-plugin contribution)
**Severity (to Lacuna):** low — the make-based tour gate is unaffected; this is
latent fragility surfaced while wiring the warpline change-impact tour leg.

Per Lacuna's consumer-boundary role, this is a **bug report only**: a specimen,
a reproduction, and a friction write-up. The fix lives in the owning member's
repo, not here.

## Summary

`warpline capture-snapshot` builds its edge graph by shelling the `loomweave`
CLI. That subprocess is resolved via **bare `$PATH`** (warpline default), and
even when the command is pinned to an absolute path, loomweave's own plugin
loading degrades when `~/.local/bin` is wholly off `$PATH`. Either way the
snapshot comes back `completeness: SKIPPED, edges: 0`, and any downstream
`blast-radius` / `reverify` reads return empty.

This is the one tool subprocess in the federation that is **not** pinned
BIN-first. The pattern matters because agent/subagent shells frequently do not
carry `~/.local/bin` on `$PATH` — Lacuna's own `tour/capability.py:_locate`
exists precisely to defend against that split for tool *detection*.

## Reproduction

```bash
# loomweave installed at ~/.local/bin/loomweave (uv tool); a loomweave index exists.

# (1) command resolution via bare $PATH — warpline's default:
env PATH=/usr/bin:/bin warpline capture-snapshot --json
#   -> completeness: SKIPPED, edges: 0, source: command_unavailable

# (2) command pinned to an absolute path — loomweave now RUNS,
#     but its plugin loading still degrades off-PATH:
env PATH=/usr/bin:/bin warpline capture-snapshot \
    --loomweave-command /home/john/.local/bin/loomweave --json
#   -> source_version: "loomweave 1.1.0-rc5"   (loomweave ran)
#   -> completeness: SKIPPED, edges: 0          (but produced no edges)

# With ~/.local/bin on $PATH, the same call yields completeness: DELTA, edges: ~419.
```

## Impact on the consumer (Lacuna)

The warpline change-impact tour leg (`tour/steps.py::warpline_change_impact`)
runs `capture-snapshot` to build the edge graph that `blast-radius` / `reverify`
traverse. If the snapshot is `SKIPPED`, those reads are empty and the leg
degrades to `ok=False` (it **fails loud — never a silent pass**), which breaks
the byte-for-byte `make verify` lockstep. The make-based gate is safe because
`make` runs with `~/.local/bin` on `$PATH`; a hand-run `python -m tour verify`
in a stripped shell would flap.

## Lacuna's local mitigation (already shipped)

The leg pins loomweave BIN-first via `--loomweave-command _tool("loomweave")`
(commit on `main`), matching the tour's `_locate` doctrine. This removes the
*command-resolution* coupling. It does **not** fix the residual loomweave
plugin-loading degradation — that is upstream.

## Suggested fixes (upstream)

1. **warpline:** resolve `loomweave` BIN-first (try `~/.local/bin` before bare
   `$PATH`), or make the absent/degraded-loomweave case a typed, non-silent
   result rather than a `SKIPPED` snapshot that reads as "no edges".
2. **loomweave:** make plugin discovery `$PATH`-independent (entry-points within
   loomweave's own environment) so an off-`$PATH` invocation still loads
   `loomweave-plugin-python` / `-rust`.
