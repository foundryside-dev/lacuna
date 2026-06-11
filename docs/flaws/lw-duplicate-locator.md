# lw-duplicate-locator

_Generated from `tour/lacunae.toml`. Do not edit by hand._

- **Location:** `specimen/colliding.py` → `colliding`
- **Category:** archaeology
- **Demonstrates:** `loomweave`
- **Expected finding:** `loomweave` / `LMWV-DUPLICATE-LOCATOR`

## Why it's here

specimen/colliding.py and specimen/colliding/__init__.py both define ShelfMark — an in-run cross-file entity-id collision; LMWV-DUPLICATE-LOCATOR fires (ERROR).

> This is an intentional, permanent demonstration fixture. Removing or "fixing" it fails `make verify`.
