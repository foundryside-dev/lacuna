# Lacuna

**A deliberately-flawed reference application the suite is demonstrated against.**

Where Weft's other members are instruments, Lacuna is the *specimen*: a
clean-cored library app seeded with documented **lacunae** (planted flaws), each
one placed to make a specific Weft tool or tool-combination light up. Point the
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

Likewise for the **legis binding ledger / closure gate**: `make setup` generates
`LEGIS_HMAC_KEY` into `.env`, but the standing legis MCP server reads it from the
shell env (not `.mcp.json` — never put the secret there). Export it before
launching Claude Code so the gate is enabled:

```bash
set -a; . ./.env; set +a        # export everything in .env (incl. LEGIS_HMAC_KEY)
# or, just the one key:  export LEGIS_HMAC_KEY=...
```

Without it, the closure gate stays honestly disabled (`CELL_NOT_ENABLED`).

## Run the tour

```bash
make tour     # drive every live Weft tool against the specimen; regenerate docs
make verify   # assert every live lacuna is surfaced and the narrative is in lockstep
```

The tour detects which Weft tools are runnable and **degrades honestly**. Legis
runs live in the tour (three passing legs — govern, policy-boundary-check, and
malformed-artifact rejection — plus two live `legis` lacunae entries). Charter
is the only member still design-only/planned, and is labelled as such, never
faked.

## The lacunae

Each planted flaw is permanent and intentional. They are catalogued in
`tour/lacunae.toml` and explained in `docs/flaws/`. Do not "fix" them — a
removed lacuna fails `make verify`. New, *un*-catalogued findings are bugs, not
features: Wardline's gate stays green on the baselined lacunae and trips on
anything new.

> **The sentinel:** `wl-log-injection` (PY-WL-125, `specimen/preview_sinks.py`)
> is deliberately **unbaselined** — preview rules are gate-immune, and the
> filigree tour leg promotes and work-cycles exactly this finding. The scan
> summary showing `1 active` is correct, not drift. Do not baseline it.

> **Warpline entries are capability demos, not flaws.** `wp-blast-radius`,
> `wp-reverify`, `wp-churn`, and `wp-timeline` (all on `specimen/cli.py::_add_book`)
> assert warpline's change-impact *correctness*, not a defect — warpline is
> advisory/enrich-only and never gates. `_add_book` carries no `LACUNA` docstring
> by design. Do not "fix" them; the catalogue holds the intent.

## Part of Weft

Weft models a codebase as **entities**, each carrying typed facts from different
tools, keyed on one durable identity (SEI), read in one call. Lacuna is the
shared specimen that demonstrates the whole matrix.

The Weft federation hub is the authoritative source for the federation
narrative and roster — see
[the doctrine](https://weft.foundryside.dev/#doctrine) for the axiom and the
member roster, and
[`members/lacuna.md`](https://github.com/foundryside-dev/weft/blob/main/members/lacuna.md)
for Lacuna's place in the suite as the demonstration specimen (it is **not** a
roster member). This README does not restate the roster; the hub owns it.
Lacuna owns its own specimen, planted-flaw manifest, and tour, as described
above.

Two complementary roles share Loomweave's analysis surface: Lacuna is the
showcase specimen (this small, deliberately-flawed app), while **elspeth**
(~425k LOC of real Python) is Loomweave's first-customer scale target — the
showcase versus the scale proof.
