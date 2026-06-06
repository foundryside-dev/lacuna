# wl-failopen-boundary

_Generated from `tour/lacunae.toml`. Do not edit by hand._

- **Location:** `specimen/wardline_boundaries.py` → `failopen_member`
- **Category:** trust-boundary
- **Demonstrates:** `wardline`
- **Expected finding:** `wardline` / `PY-WL-113`

## Why it's here

A trust boundary that fails OPEN — on a validation error it returns the raw input unchanged instead of rejecting it.

> This is an intentional, permanent demonstration fixture. Removing or "fixing" it fails `make verify`.
