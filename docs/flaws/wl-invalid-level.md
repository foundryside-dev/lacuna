# wl-invalid-level

_Generated from `tour/lacunae.toml`. Do not edit by hand._

- **Location:** `specimen/wardline_boundaries.py` → `invalid_level_member`
- **Category:** decorator-hygiene
- **Demonstrates:** `wardline`
- **Expected finding:** `wardline` / `PY-WL-114`

## Why it's here

A builtin trust decorator declares a level (`SUPERUSER`) that is not in Wardline's trust lattice.

> This is an intentional, permanent demonstration fixture. Removing or "fixing" it fails `make verify`.
