# pw-surface-scoping

_Generated from `tour/lacunae.toml`. Do not edit by hand._

- **Location:** `tour/__main__.py` → `__main__.main`
- **Category:** intent-coverage
- **Demonstrates:** `plainweave`
- **Expected finding:** `plainweave` / `pw-surface-scoping`

## Why it's here

NOT A FLAW — a positive plainweave capability demo. The harness's own entry-point (tour.__main__.main) is a public surface in the raw catalog; `plainweave intent coverage --exclude-namespace tour.` scopes it OUT of the product denominator, measuring the real exported API, and honestly reports the catalog incomplete (denominator_complete=false; absent tag classes exported-api, http-route) rather than overstating coverage. Advisory, local-only, never gates.

> This is an intentional, permanent demonstration fixture. Removing or "fixing" it fails `make verify`.
