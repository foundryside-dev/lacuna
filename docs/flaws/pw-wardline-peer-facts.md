# pw-wardline-peer-facts

_Generated from `tour/lacunae.toml`. Do not edit by hand._

- **Location:** `specimen/peerfacts.py` → `unsafe_sink`
- **Category:** peer-facts
- **Demonstrates:** `plainweave`, `plainweave+wardline`
- **Expected finding:** `plainweave` / `pw-wardline-peer-facts`

## Why it's here

NOT A FLAW — a positive plainweave capability demo. `plainweave wardline-peer-facts` reads sibling-owned .wardline/ snapshots as advisory peer facts (Plainweave never scans; Wardline owns the trust gate). Over a frozen two-snapshot fixture with scan-identity manifests: an active defect and a non-defect finding surface as advisory context; a finding gone from the latest in-scope snapshot is reported resolved_or_unseen while an out-of-scope prior finding is honestly flagged (wardline_scope_mismatch), never silently resolved; and an absent .wardline/ yields freshness=unavailable, never clean. Advisory, local-only, never gates.

> This is an intentional, permanent demonstration fixture. Removing or "fixing" it fails `make verify`.
