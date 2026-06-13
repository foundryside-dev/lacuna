# wp-blast-radius

_Generated from `tour/lacunae.toml`. Do not edit by hand._

- **Location:** `specimen/cli.py` → `_add_book`
- **Category:** change-impact
- **Demonstrates:** `warpline`
- **Expected finding:** `warpline` / `wp-blast-radius`

## Why it's here

NOT A FLAW — a positive warpline capability demo. Touching the add-a-book CLI flow (_add_book), warpline's blast-radius surfaces the downstream LibraryService.add_book it delegates to, with edge provenance. Warpline is advisory/enrich-only and never gates.

> This is an intentional, permanent demonstration fixture. Removing or "fixing" it fails `make verify`.
