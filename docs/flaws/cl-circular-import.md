# cl-circular-import

_Generated from `tour/lacunae.toml`. Do not edit by hand._

- **Location:** `specimen/cycle_a.py` → `cycle_a`
- **Category:** structure
- **Demonstrates:** `clarion`
- **Expected finding:** `clarion` / `circular-import`

## Why it's here

specimen.cycle_a and specimen.cycle_b import each other — Clarion's import graph contains a 2-cycle the harness surfaces from .clarion/clarion.db.

> This is an intentional, permanent demonstration fixture. Removing or "fixing" it fails `make verify`.
