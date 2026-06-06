# wl-trust-violation

_Generated from `tour/lacunae.toml`. Do not edit by hand._

- **Location:** `specimen/trust_flow.py` → `unsafe_account_key`
- **Category:** trust-boundary
- **Demonstrates:** `wardline`, `wardline+loomweave`, `wardline+filigree`
- **Expected finding:** `wardline` / `PY-WL-101`

## Why it's here

Declares return trust ASSURED but returns EXTERNAL_RAW — untrusted data reaches a trusted producer with no validation.

> This is an intentional, permanent demonstration fixture. Removing or "fixing" it fails `make verify`.
