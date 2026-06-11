# wl-xxe

_Generated from `tour/lacunae.toml`. Do not edit by hand._

- **Location:** `specimen/preview_sinks.py` → `parse_catalog_feed`
- **Category:** injection
- **Demonstrates:** `wardline`
- **Expected finding:** `wardline` / `PY-WL-121`

## Why it's here

Untrusted XML text reaches lxml.etree.fromstring — XXE (preview rule, gate-immune).

> This is an intentional, permanent demonstration fixture. Removing or "fixing" it fails `make verify`.
