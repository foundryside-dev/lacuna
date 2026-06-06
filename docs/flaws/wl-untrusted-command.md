# wl-untrusted-command

_Generated from `tour/lacunae.toml`. Do not edit by hand._

- **Location:** `specimen/wardline_sinks.py` → `run_export_command`
- **Category:** injection
- **Demonstrates:** `wardline`
- **Expected finding:** `wardline` / `PY-WL-108`

## Why it's here

Untrusted text reaches os.system — OS-command injection.

> This is an intentional, permanent demonstration fixture. Removing or "fixing" it fails `make verify`.
