# lw-decorator

_Generated from `tour/lacunae.toml`. Do not edit by hand._

- **Location:** `specimen/service.py` → `audited`
- **Category:** navigation
- **Demonstrates:** `loomweave`
- **Expected finding:** `loomweave` / `decorates`

## Why it's here

specimen.service.audited decorates LibraryService.add_book and register_user — the Python plugin's decorates relation edges anchor decorator→decorated (ADR-051), so entity_relation_list on the decorator enumerates every method it wraps.

> This is an intentional, permanent demonstration fixture. Removing or "fixing" it fails `make verify`.
