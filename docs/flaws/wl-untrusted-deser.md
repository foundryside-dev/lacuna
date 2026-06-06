# wl-untrusted-deser

_Generated from `tour/lacunae.toml`. Do not edit by hand._

- **Location:** `specimen/wardline_sinks.py` → `import_catalog_blob`
- **Category:** injection
- **Demonstrates:** `wardline`
- **Expected finding:** `wardline` / `PY-WL-106`

## Why it's here

Untrusted bytes reach pickle.loads inside a trusted-tier function — arbitrary-object deserialization.

> This is an intentional, permanent demonstration fixture. Removing or "fixing" it fails `make verify`.
