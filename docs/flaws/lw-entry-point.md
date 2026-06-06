# lw-entry-point

_Generated from `tour/lacunae.toml`. Do not edit by hand._

- **Location:** `specimen/cli.py` → `main`
- **Category:** navigation
- **Demonstrates:** `loomweave`
- **Expected finding:** `loomweave` / `entry-point`

## Why it's here

specimen.cli.main is the app's entry point — the Python plugin tags it `entry-point`, so Loomweave's entity_entry_point_list returns it (vs. library internals reached only through it).

> This is an intentional, permanent demonstration fixture. Removing or "fixing" it fails `make verify`.
