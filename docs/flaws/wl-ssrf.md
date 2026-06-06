# wl-ssrf

_Generated from `tour/lacunae.toml`. Do not edit by hand._

- **Location:** `specimen/wardline_sinks.py` → `fetch_cover_image`
- **Category:** injection
- **Demonstrates:** `wardline`
- **Expected finding:** `wardline` / `PY-WL-117`

## Why it's here

Untrusted text reaches an HTTP client (requests.get) — server-side request forgery.

> This is an intentional, permanent demonstration fixture. Removing or "fixing" it fails `make verify`.
