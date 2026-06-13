# PDR-0001 — Bootstrap the product workspace from observed state

- **Date:** 2026-06-13
- **Status:** Accepted
- **Decider:** product-owner agent (via `/own-product`), grant ratified by human owner

## Context

`/own-product` found no product workspace at `docs/product/` (the `vision.md`
existence check returned ABSENT). There was no prior standing product state to
resume, so the five artifacts had to be constructed rather than loaded.

## What was observed

- **README.md** — Lacuna is "the MissingNo of the Weft suite": a
  deliberately-flawed reference application, the *specimen* the suite is
  demonstrated against. Planted flaws ("lacunae") are permanent; "fixing" one
  fails `make verify`. Lacuna is explicitly **not** a federation roster member;
  the Weft hub (`~/weft`) owns the roster/narrative.
- **git log (30)** — recent direction: growing the specimen corpus (Wave-3 Rust
  wing, 44 lacunae), regenerating `tour.md`/`matrix.md`, and a strong **dogfood**
  cadence (run the live suite against Lacuna → friction report → fix seams →
  re-dogfood).
- **Tracker (Filigree)** — 1 open item (`lacuna-2046f5ae8a`, P4 release
  placeholder), 1 pending observation, 155 unbridged analyzer findings (mostly
  the planted lacunae; 0 defect-signal).
- **Dogfood reports** — `docs/dogfood/2026-06-12…` and `…06-13-post-fix…`: major
  cross-tool seams now function; remaining friction is MCP attachment, port/config
  truth, scanner job semantics, and large-repo ingest.

## The call

- Seed **vision** as: Lacuna = the Weft federation's demonstration specimen &
  proving ground; primary audience = federation developers/PO; anti-goals center
  on *not* removing planted flaws and *not* owning the tools it demonstrates.
- Seed **roadmap Now** = "federation seam integrity, agent-native" (inferred from
  the dominant dogfood-and-seam-fix activity).
- Seed **metrics** = specimen fidelity (north star, via `make verify`) +
  guardrails for seam health, dogfood friction, and demonstration honesty.
- **Authority grant** proposed via `AskUserQuestion` and **confirmed as written**
  by the human owner, tuned so that removing/"fixing" a planted lacuna and any
  change to the hub or another member are escalation-gated.

## Reversal trigger

Revisit this PDR once the human owner confirms (a) the audience weighting
(internal proving ground vs. external demo) and (b) Lacuna's product boundary
for federation-tool bugs surfaced by dogfooding (specimen+fixture+report vs.
fix). Either confirmation may reshape vision and the Now bet; the grant is
already confirmed and is not in scope for this trigger.
