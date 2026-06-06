# wl-stored-taint

_Generated from `tour/lacunae.toml`. Do not edit by hand._

- **Location:** `specimen/wardline_boundaries.py` → `load_member_record`
- **Category:** stored-taint
- **Demonstrates:** `wardline`
- **Expected finding:** `wardline` / `PY-WL-120`

## Why it's here

Data read from persistent storage (a file read) reaches a @trusted producer's return value with no validation — stored/persisted taint promoted to trusted.

> This is an intentional, permanent demonstration fixture. Removing or "fixing" it fails `make verify`.
