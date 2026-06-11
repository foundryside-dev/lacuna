# wl-unparseable

_Generated from `tour/lacunae.toml`. Do not edit by hand._

- **Location:** `specimen_quarantine/unparseable.py` → `unparseable`
- **Category:** fail-closed
- **Demonstrates:** `wardline`
- **Expected finding:** `wardline` / `WLN-ENGINE-PARSE-ERROR`

## Why it's here

A committed parse failure in the quarantine dir; the fail-closed analyzer surfaces WLN-ENGINE-PARSE-ERROR and --fail-on-unanalyzed trips the gate (exit 1). The demo asserts the FAILURE.

> This is an intentional, permanent demonstration fixture. Removing or "fixing" it fails `make verify`.
