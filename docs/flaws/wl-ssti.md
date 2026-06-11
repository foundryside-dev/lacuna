# wl-ssti

_Generated from `tour/lacunae.toml`. Do not edit by hand._

- **Location:** `specimen/preview_sinks.py` → `render_report_template`
- **Category:** injection
- **Demonstrates:** `wardline`
- **Expected finding:** `wardline` / `PY-WL-122`

## Why it's here

Untrusted template source reaches jinja2.Template — server-side template injection (preview).

> This is an intentional, permanent demonstration fixture. Removing or "fixing" it fails `make verify`.
