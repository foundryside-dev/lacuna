# wp-attest-no-silent-clean

_Generated from `tour/lacunae.toml`. Do not edit by hand._

- **Location:** `specimen/cli.py` → `_add_book`
- **Category:** peer-facts
- **Demonstrates:** `warpline`, `wardline+warpline`
- **Expected finding:** `warpline-attest-bundle` / `wp-attest-no-silent-clean`

## Why it's here

NOT A FLAW — a positive warpline capability demo. `warpline reverify --attest-bundle` reads risk_verification=proven-good ONLY when the worklist is impact-complete AND every affected entity is attested-clean-at-current-body (an all-or-nothing echo of wardline's authority; signature not re-verified by warpline); an absent/partial/unkeyed/schema-skewed/dirty/unmatched bundle degrades to risk_verification=unavailable with an explicit machine reason_code, NEVER a warpline-minted clean. This leg hands warpline a wardline-attest bundle and asserts that no-silent-clean DEGRADE. On the installed toolset proven-good is doubly unreachable — wardline emits wardline-attest-1 (warpline needs -2) AND the specimen's snapshot is impact-incomplete (DELTA), whose completeness gate pre-empts attestation — so the bundle content is not the discriminator; the point proven is that warpline returns unavailable+reason, never a silent clean (the one-line predicate flip lights up proven-good under a wardline-attest-2 producer over a complete snapshot). Capability-gated on the `reverify --attest-bundle` surface (the wardline-attest-2 consumer; PDR-0017): renders [N/A] under a pre-attest-2 warpline (e.g. a main-branch or PyPI 1.2.0 build). Advisory/enrich-only, never gates.

> This is an intentional, permanent demonstration fixture. Removing or "fixing" it fails `make verify`.
