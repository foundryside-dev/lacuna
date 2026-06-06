# lw-circular-import

_Generated from `tour/lacunae.toml`. Do not edit by hand._

- **Location:** `specimen/cycle_a.py` → `cycle_a`
- **Category:** structure
- **Demonstrates:** `loomweave`
- **Expected finding:** `loomweave` / `circular-import`

## Why it's here

specimen.cycle_a and specimen.cycle_b import each other — Loomweave's import graph (module_circular_import_list) contains a 2-cycle the harness surfaces from .loomweave/loomweave.db.

> This is an intentional, permanent demonstration fixture. Removing or "fixing" it fails `make verify`.
