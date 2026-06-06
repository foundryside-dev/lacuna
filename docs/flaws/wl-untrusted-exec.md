# wl-untrusted-exec

_Generated from `tour/lacunae.toml`. Do not edit by hand._

- **Location:** `specimen/wardline_sinks.py` → `eval_report_formula`
- **Category:** injection
- **Demonstrates:** `wardline`
- **Expected finding:** `wardline` / `PY-WL-107`

## Why it's here

Untrusted text reaches eval() inside a trusted-tier function — dynamic code execution.

> This is an intentional, permanent demonstration fixture. Removing or "fixing" it fails `make verify`.
