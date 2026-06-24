# pw-intent-orphan

_Generated from `tour/lacunae.toml`. Do not edit by hand._

- **Location:** `tour/__main__.py` → `__main__.main`
- **Category:** intent-coverage
- **Demonstrates:** `plainweave`
- **Expected finding:** `plainweave` / `pw-intent-orphan`

## Why it's here

NOT A FLAW — a positive plainweave capability demo. The tour entry-point is recorded as a public code entity with no requirement, so `plainweave intent orphans code` surfaces it as an honest gap (and it appears in coverage's unjustified list). Plainweave never hides an unjustified public surface. Advisory, local-only, never gates.

> This is an intentional, permanent demonstration fixture. Removing or "fixing" it fails `make verify`.
