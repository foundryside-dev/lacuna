# wl-non-rejecting-boundary

_Generated from `tour/lacunae.toml`. Do not edit by hand._

- **Location:** `specimen/exception_flow.py` → `non_rejecting_boundary`
- **Category:** trust-boundary
- **Demonstrates:** `wardline`
- **Expected finding:** `wardline` / `PY-WL-102`

## Why it's here

A @trust_boundary that normalizes but never rejects — it cannot actually validate anything.

> This is an intentional, permanent demonstration fixture. Removing or "fixing" it fails `make verify`.
