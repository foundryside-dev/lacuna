# wp-reverify

_Generated from `tour/lacunae.toml`. Do not edit by hand._

- **Location:** `specimen/cli.py` → `_add_book`
- **Category:** change-impact
- **Demonstrates:** `warpline`
- **Expected finding:** `warpline` / `wp-reverify`

## Why it's here

NOT A FLAW — a positive warpline capability demo. warpline's reverify worklist for a change to _add_book lists LibraryService.add_book as reason=downstream, the 'what must I re-verify' surface. Advisory, never gates.

> This is an intentional, permanent demonstration fixture. Removing or "fixing" it fails `make verify`.
