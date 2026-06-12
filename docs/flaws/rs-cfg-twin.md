# rs-cfg-twin

_Generated from `tour/lacunae.toml`. Do not edit by hand._

- **Location:** `specimen-rs/src/catalog.rs` → `Shelf`
- **Category:** archaeology
- **Demonstrates:** `loomweave`
- **Expected finding:** `loomweave` / `cfg-twin`

## Why it's here

Two mutually-exclusive #[cfg] impls of Shelf split into @cfg(...) qualname twins (ADR-049 Am.5) instead of colliding.

> This is an intentional, permanent demonstration fixture. Removing or "fixing" it fails `make verify`.
