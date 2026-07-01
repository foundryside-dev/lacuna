# pw-baseline-drift

_Generated from `tour/lacunae.toml`. Do not edit by hand._

- **Location:** `specimen/cli.py` → `_add_book`
- **Category:** baseline
- **Demonstrates:** `plainweave`
- **Expected finding:** `plainweave-baseline` / `pw-baseline-drift`

## Why it's here

NOT A FLAW — a positive plainweave capability demo. Over the seeded corpus, `plainweave baseline create` locks the approved requirements; superseding one (cli._add_book's requirement) makes `baseline diff` report it as `superseded_since_baseline` drift while an untouched requirement (cli.main's) stays `unchanged`; and in a store with no locked baseline, `baseline diff` of a never-created baseline reports an honest `NOT_FOUND` error — never a silent 'clean / no drift'. The load-bearing no-silent-clean contract over the baseline surface. Advisory, local-only, never gates. Capability-gated on the `baseline` CLI surface: renders [N/A] under a plainweave that lacks the subcommand.

> This is an intentional, permanent demonstration fixture. Removing or "fixing" it fails `make verify`.
