# wl-none-leak

_Generated from `tour/lacunae.toml`. Do not edit by hand._

- **Location:** `specimen/wardline_boundaries.py` → `renewal_count`
- **Category:** none-leak
- **Demonstrates:** `wardline`
- **Expected finding:** `wardline` / `PY-WL-109`

## Why it's here

A @trusted producer typed to return a non-None int falls through one path and returns None — a contract violation a consumer will trust.

> This is an intentional, permanent demonstration fixture. Removing or "fixing" it fails `make verify`.
