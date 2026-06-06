# wl-untrusted-callee

_Generated from `tour/lacunae.toml`. Do not edit by hand._

- **Location:** `specimen/wardline_boundaries.py` → `register_member`
- **Category:** trust-boundary
- **Demonstrates:** `wardline`
- **Expected finding:** `wardline` / `PY-WL-105`

## Why it's here

An untrusted value is passed straight into a @trusted callee at the call site, with no validating boundary in between.

> This is an intentional, permanent demonstration fixture. Removing or "fixing" it fails `make verify`.
