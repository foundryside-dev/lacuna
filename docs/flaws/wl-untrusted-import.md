# wl-untrusted-import

_Generated from `tour/lacunae.toml`. Do not edit by hand._

- **Location:** `specimen/wardline_sinks.py` → `load_report_plugin`
- **Category:** injection
- **Demonstrates:** `wardline`
- **Expected finding:** `wardline` / `PY-WL-115`

## Why it's here

Untrusted text reaches importlib.import_module — dynamic-import injection.

> This is an intentional, permanent demonstration fixture. Removing or "fixing" it fails `make verify`.
