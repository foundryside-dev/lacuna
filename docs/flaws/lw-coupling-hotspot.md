# lw-coupling-hotspot

_Generated from `tour/lacunae.toml`. Do not edit by hand._

- **Location:** `specimen/hub.py` → `dispatch`
- **Category:** navigation
- **Demonstrates:** `loomweave`
- **Expected finding:** `loomweave` / `coupling-hotspot`

## Why it's here

specimen.hub.dispatch is called by five Dispatcher methods and calls five routines (fan-in 5 + fan-out 5) — Loomweave's entity_coupling_hotspot_list ranks it the #1 coupling hotspot in the specimen app.

> This is an intentional, permanent demonstration fixture. Removing or "fixing" it fails `make verify`.
