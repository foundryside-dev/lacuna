# pw-requirements-enrichment

_Generated from `tour/lacunae.toml`. Do not edit by hand._

- **Location:** `specimen/cli.py` → `_add_book`
- **Category:** peer-facts
- **Demonstrates:** `plainweave`, `plainweave+warpline`
- **Expected finding:** `plainweave-requirements-enrichment` / `pw-requirements-enrichment`

## Why it's here

NOT A FLAW — a positive plainweave capability demo. Over the covered+uncovered seed, `plainweave requirements-enrichment` is the Plainweave producer for Warpline's reserved enrichment.requirements slot: a covered surface (cli._add_book) reports `present` with non-empty requirements; the recorded-but-unbound orphan (tour.__main__.main) reports `absent`; and a well-formed-but-absent locator reports `unavailable` — an identity gap is 'cannot tell', NEVER a silent `absent`. The load-bearing no-silent-clean contract. Advisory, local-only, never gates. Capability-gated on the `requirements-enrichment` CLI surface (PDR-0016): renders [N/A] under a plainweave that lacks it (e.g. PyPI 1.0.0).

> This is an intentional, permanent demonstration fixture. Removing or "fixing" it fails `make verify`.
