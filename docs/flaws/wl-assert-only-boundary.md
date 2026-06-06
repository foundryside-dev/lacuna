# wl-assert-only-boundary

_Generated from `tour/lacunae.toml`. Do not edit by hand._

- **Location:** `specimen/wardline_boundaries.py` → `assert_only_member`
- **Category:** trust-boundary
- **Demonstrates:** `wardline`
- **Expected finding:** `wardline` / `PY-WL-111`

## Why it's here

A trust boundary whose only rejection path is `assert` — stripped under `python -O`, so it validates nothing in production.

> This is an intentional, permanent demonstration fixture. Removing or "fixing" it fails `make verify`.
