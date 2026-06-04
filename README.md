# Lacuna

**The MissingNo of the [Loom](https://github.com/tachyon-beep) suite** — a
deliberately-flawed reference application the suite is demonstrated against.

Where Loom's other members are instruments, Lacuna is the *specimen*: a
clean-cored library app seeded with documented **lacunae** (planted flaws), each
one placed to make a specific Loom tool or tool-combination light up. Point the
suite at Lacuna and watch it work.

## What's here

| Path | What it is |
|------|------------|
| `specimen/` | The clean-core app + isolated, catalogued planted flaws |
| `tour/lacunae.toml` | The flaw manifest — single source of truth |
| `tour/` | The tour harness (`python -m tour`) |
| `docs/tour.md`, `docs/matrix.md` | Generated narrative + combination-matrix coverage |
| `docs/flaws/` | Per-lacuna explainer pages (generated) |

## Run the tour

```bash
make tour     # drive every live Loom tool against the specimen; regenerate docs
make verify   # assert every live lacuna is surfaced and the narrative is in lockstep
```

The tour detects which Loom tools are runnable and **degrades honestly** —
design-only members (Legis, Charter) are labelled, never faked.

## The lacunae

Each planted flaw is permanent and intentional. They are catalogued in
`tour/lacunae.toml` and explained in `docs/flaws/`. Do not "fix" them — a
removed lacuna fails `make verify`. New, *un*-catalogued findings are bugs, not
features: Wardline's gate stays green on the baselined lacunae and trips on
anything new.

## Part of Loom

Loom models a codebase as **entities**, each carrying typed facts from different
tools, keyed on one durable identity (SEI), read in one call. Lacuna is the
shared specimen that demonstrates the whole matrix: Clarion (structure),
Wardline (trust), Filigree (work), Legis (governance), Charter (requirements).
