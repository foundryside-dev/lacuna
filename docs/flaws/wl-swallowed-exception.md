# wl-swallowed-exception

_Generated from `tour/lacunae.toml`. Do not edit by hand._

- **Location:** `specimen/exception_flow.py` → `swallowed_error`
- **Category:** exception-handling
- **Demonstrates:** `wardline`
- **Expected finding:** `wardline` / `PY-WL-104`

## Why it's here

An exception silently swallowed with `pass` in a trusted-tier function.

> This is an intentional, permanent demonstration fixture. Removing or "fixing" it fails `make verify`.
