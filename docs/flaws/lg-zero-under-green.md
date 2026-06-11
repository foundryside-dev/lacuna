# lg-zero-under-green

_Generated from `tour/lacunae.toml`. Do not edit by hand._

- **Location:** `specimen_quarantine/malformed_artifact.json` → `malformed_artifact`
- **Category:** fail-closed
- **Demonstrates:** `legis`, `wardline+legis`
- **Expected finding:** `legis` / `artifact-missing-findings-rejected`

## Why it's here

A wardline scan artifact with the findings key ABSENT; legis rejects it (HTTP 422, G1) instead of routing zero defects under green. The demo asserts the REJECTION.

> This is an intentional, permanent demonstration fixture. Removing or "fixing" it fails `make verify`.
