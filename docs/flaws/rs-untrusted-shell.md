# rs-untrusted-shell

_Generated from `tour/lacunae.toml`. Do not edit by hand._

- **Location:** `specimen-rs/src/main.rs` → `shell_archive`
- **Category:** injection
- **Demonstrates:** `wardline`
- **Expected finding:** `wardline` / `RS-WL-112`

## Why it's here

Operator input reaches a `sh -c` command line — Rust shell injection.

> This is an intentional, permanent demonstration fixture. Removing or "fixing" it fails `make verify`.
