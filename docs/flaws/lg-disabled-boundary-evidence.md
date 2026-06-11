# lg-disabled-boundary-evidence

_Generated from `tour/lacunae.toml`. Do not edit by hand._

- **Location:** `specimen/policy_boundaries.py` → `pinned_import`
- **Category:** governance
- **Demonstrates:** `legis`
- **Expected finding:** `legis` / `POLICY_BOUNDARY_TEST_DISABLED`

## Why it's here

A @policy_boundary whose evidence test is @pytest.mark.skip — legis policy-boundary-check flags POLICY_BOUNDARY_TEST_DISABLED; the healthy sibling boundary passes, proving the check discriminates.

> This is an intentional, permanent demonstration fixture. Removing or "fixing" it fails `make verify`.
