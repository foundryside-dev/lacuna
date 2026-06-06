# lw-call-chain

_Generated from `tour/lacunae.toml`. Do not edit by hand._

- **Location:** `specimen/pipeline.py` → `ingest`
- **Category:** navigation
- **Demonstrates:** `loomweave`
- **Expected finding:** `loomweave` / `execution-path`

## Why it's here

A five-hop call chain ingest→normalize→enrich→validate_record→persist — Loomweave's entity_execution_path_list traces it end-to-end, and entity_callers_list walks it back from the tail.

> This is an intentional, permanent demonstration fixture. Removing or "fixing" it fails `make verify`.
