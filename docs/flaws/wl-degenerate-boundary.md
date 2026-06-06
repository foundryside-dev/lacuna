# wl-degenerate-boundary

_Generated from `tour/lacunae.toml`. Do not edit by hand._

- **Location:** `specimen/wardline_boundaries.py` → `degenerate_member`
- **Category:** trust-boundary
- **Demonstrates:** `wardline`
- **Expected finding:** `wardline` / `PY-WL-119`

## Why it's here

A no-op validator boundary whose return value is its input parameter verbatim — it claims to validate but checks nothing.

> This is an intentional, permanent demonstration fixture. Removing or "fixing" it fails `make verify`.
