# PDR-0005 — Add Plainweave as a tour member (intent-coverage capability demos)

- **Date:** 2026-06-24
- **Status:** Accepted
- **Decider:** agent:claude-product-owner (Plainweave), executing under the human owner's explicit direction this session
- **Related:** PDR-0002 (consumer boundary), warpline tour-leg precedent, Plainweave PDR-008

## Context

Lacuna demonstrates the live Weft tools (loomweave, filigree, wardline, legis,
warpline) but **not Plainweave** — the newest member, whose code-up intent graph
(`Loomweave SEI → requirement → goal`) answers "why does this code exist?".
The human owner directed adding Plainweave to the tour and merging it. Plainweave
is advisory / enrich-only / local (no flaw rules, never gates), so it fits the
**warpline NOT-A-FLAW capability-demo** pattern, not a planted-flaw pattern.

## Options considered

1. **Read-only peer dogfood only** (as Plainweave PDR-008 already did) — leaves no
   durable, regenerable proof in the specimen; the seam is re-verified by hand each time.
2. **Permanent in-repo tour member** — a self-seeding leg + catalogued lacunae that
   the tour drives and `make verify` asserts every run. (Chosen.)

## Decision

1. **Add Plainweave as the 6th live tour member.** A self-seeding leg
   (`tour/plainweave_intent`, `tour/plainweave_seed.py`) builds a deterministic,
   gitignored `.plainweave/` intent corpus over the specimen each run, then asserts
   four catalogued `pw-*` capability demos: `pw-intent-justified`, `pw-intent-liveness`
   (deprecated requirements drop from the numerator), `pw-intent-orphan`, and
   `pw-surface-scoping` (+ honest degradation: `denominator_complete=false`,
   absent `exported-api`/`http-route`). Corpus 48 → 52 lacunae.
2. **Frame it honestly as a demonstrator + deterministic regression-harness, NOT
   north-star movement.** Plainweave's seam was already proven over Lacuna read-only
   at 75% (Plainweave PDR-008); this bet adds *durable, regenerable* proof — it fails
   loud if Plainweave's liveness/deprecation numerator semantics ever break — which a
   one-shot dogfood cannot. The seed deliberately constructs a **covered + uncovered
   mix** (2 justified : 2 uncovered → north-star 2/4 default, 2/3 scoped) so the reads
   tell a real story (owner principle, 2026-06-24).
3. **Honour the consumer boundary (PDR-0002).** The leg only *consumes* Plainweave
   (a `uv tool install`ed binary like its siblings); no Plainweave (or other member)
   repo was modified. No specimen source was changed (all new code in `tour/`).

## Consequences

- `tour/lacunae.toml` +4 `pw-*` entries; `tour/{steps,capability,__main__}.py`,
  `tests/`, `.gitignore` (`.plainweave/`, `.wardline/`), and the generated
  `docs/{tour,matrix}.md` + `docs/flaws/pw-*.md` updated. `make ci` green; all 52
  lacunae surface.
- **Environment provisioning (demo bed):** plainweave installed as a uv tool, and the
  pre-existing `wardline[rust]` (tree-sitter) gap was closed so the rust lacunae
  surface again — both are local tool-venv provisioning, not member-repo changes.

## Escalations / drift for the owner (flag at next `/own-product` or `/product-checkpoint`)

- **vision.md tool enumeration is now stale.** `vision.md` lists the dogfood-range
  tools without Plainweave; the tour now drives it. This PDR deliberately did **not**
  edit `vision.md` (a reserved vision/strategy change). Owner to decide: ratify
  Plainweave into the dogfood-range narrative, or keep it *demonstrated-not-rostered*.
- **Corpus-count drift (pre-existing):** `current-state.md` says "44 catalogued
  lacunae"; the manifest is now 52 (was already 48 before this change). Owner to
  reconcile the brief.

## Reversal trigger

Reopen if Plainweave's CLI/oracle drifts such that the seed no longer reproduces
deterministically (e.g. the four stable anchor surfaces leave the catalog, or the
intent-coverage envelope shape changes), or if Plainweave is not adopted as a
recognized Weft member — in which case demote the leg to a read-only dogfood note.
