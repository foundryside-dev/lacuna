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

## Set up

```bash
make setup    # provision the demo's gitignored secrets (idempotent)
```

`make setup` generates `.env` (gitignored, `0600`) with a fresh shared HMAC for
the Wardline→Legis signed-scan handshake. Secrets are **never committed** — a
fresh clone bootstraps its own, and `make setup` never clobbers an existing
`.env`. `make tour`/`make verify` depend on it, so the signed handshake just
works (without it, the tour degrades honestly to an *unsigned* handshake).

For the agent's Filigree MCP (the dashboard transport on `:8749`), export the
federation token into the shell **before** launching Claude Code — `.mcp.json`
interpolates `${WEFT_FEDERATION_TOKEN}` from the environment, not from `.env`:

```bash
export WEFT_FEDERATION_TOKEN="$(cat ~/.config/filigree/federation_token)"
```

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
shared specimen that demonstrates the whole matrix.

The Loom federation hub at `~/loom` is the authoritative source for the
federation narrative and roster — see `~/loom/doctrine.md` for the axiom and the
member roster, and `~/loom/members/lacuna.md` for Lacuna's place in the suite as
the demonstration specimen (it is **not** a roster member). This README does not
restate the roster; the hub owns it. Lacuna owns its own specimen, planted-flaw
manifest, and tour, as described above.
