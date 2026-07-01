# pw-verification-status

_Generated from `tour/lacunae.toml`. Do not edit by hand._

- **Location:** `specimen/cli.py` → `_register`
- **Category:** verification
- **Demonstrates:** `plainweave`
- **Expected finding:** `plainweave-verify` / `pw-verification-status`

## Why it's here

NOT A FLAW — a positive plainweave capability demo. A requirement with a verification method AND passing evidence reports `satisfied` (plainweave has no 'verified' status string — the rollup is `satisfied` with reason `passing_evidence`); a requirement with a method but NO evidence reports `unverified` and is listed by `status unverified` — never silently satisfied; and evidence orphaned by a supersede reports `stale` and is listed by `status stale` — an outdated obligation is honestly flagged, never silently passing. The honest satisfied / unverified / stale trichotomy. Advisory, local-only, never gates. Capability-gated on the `verify` CLI surface: renders [N/A] under a plainweave that lacks the subcommand.

> This is an intentional, permanent demonstration fixture. Removing or "fixing" it fails `make verify`.
