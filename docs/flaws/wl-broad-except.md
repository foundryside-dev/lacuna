# wl-broad-except

_Generated from `tour/lacunae.toml`. Do not edit by hand._

- **Location:** `specimen/exception_flow.py` → `broad_handler`
- **Category:** exception-handling
- **Demonstrates:** `wardline`
- **Expected finding:** `wardline` / `PY-WL-103`

## Why it's here

A broad `except Exception` in a trusted-tier function that masks failures.

> This is an intentional, permanent demonstration fixture. Removing or "fixing" it fails `make verify`.
