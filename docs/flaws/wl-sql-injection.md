# wl-sql-injection

_Generated from `tour/lacunae.toml`. Do not edit by hand._

- **Location:** `specimen/wardline_sinks.py` → `lookup_member`
- **Category:** injection
- **Demonstrates:** `wardline`
- **Expected finding:** `wardline` / `PY-WL-118`

## Why it's here

Untrusted text is interpolated into a SQL string reaching cursor.execute — SQL injection.

> This is an intentional, permanent demonstration fixture. Removing or "fixing" it fails `make verify`.
