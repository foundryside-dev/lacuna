# wl-contradictory-trust

_Generated from `tour/lacunae.toml`. Do not edit by hand._

- **Location:** `specimen/wardline_boundaries.py` → `contradictory_member`
- **Category:** decorator-hygiene
- **Demonstrates:** `wardline`
- **Expected finding:** `wardline` / `PY-WL-110`

## Why it's here

A function marked BOTH @trusted and @external_boundary — contradictory markers the engine resolves silently. (Asserted via wardline.decorators; the weft_markers variant is a known gap, filigree wardline-d62845bb18.)

> This is an intentional, permanent demonstration fixture. Removing or "fixing" it fails `make verify`.
