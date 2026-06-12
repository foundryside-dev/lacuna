# rs-untrusted-command

_Generated from `tour/lacunae.toml`. Do not edit by hand._

- **Location:** `specimen-rs/src/main.rs` → `run_export`
- **Category:** injection
- **Demonstrates:** `wardline`
- **Expected finding:** `wardline` / `RS-WL-108`

## Why it's here

Operator input reaches the program slot of Command::new inside a /// @trusted(level=ASSURED) fn — Rust program injection.

> This is an intentional, permanent demonstration fixture. Removing or "fixing" it fails `make verify`.
