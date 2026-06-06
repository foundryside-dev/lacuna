# wl-path-traversal

_Generated from `tour/lacunae.toml`. Do not edit by hand._

- **Location:** `specimen/wardline_sinks.py` → `open_catalog_file`
- **Category:** injection
- **Demonstrates:** `wardline`
- **Expected finding:** `wardline` / `PY-WL-116`

## Why it's here

Untrusted text reaches a filesystem open() — path traversal.

> This is an intentional, permanent demonstration fixture. Removing or "fixing" it fails `make verify`.
