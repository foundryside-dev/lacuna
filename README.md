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

Likewise for the **legis MCP server** — its binding ledger / closure gate **and**
a clean `legis doctor`: `make setup` writes the legis keys to `.env`, but the
standing server reads them from the shell env (not `.mcp.json` — never put them
there; legis deliberately scrubs operator keys out of `.mcp.json`). Export `.env`
before launching Claude Code:

```bash
set -a; . ./.env; set +a        # export everything in .env: LEGIS_OPERATOR_KEY,
                                # LEGIS_WARDLINE_ARTIFACT_KEY, LEGIS_HMAC_KEY, …
```

This both enables the closure gate (otherwise `CELL_NOT_ENABLED`) **and** makes
`legis doctor` read clean: without it the standing MCP server inherits none of the
`.env` keys, so doctor flags the operator-key and wardline-artifact-key warnings.
With `.env` loaded it settles to a single, expected note (the operator key is
plaintext-in-env — usable, by design, for this demo tier).

**Tip:** with [direnv](https://direnv.net) installed, the committed `.envrc`
auto-loads `.env` on `cd` (`direnv allow` once after `make setup`) — no manual
export needed, so the agent you launch from this directory inherits the keys.

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

> **Plainweave entries are capability demos, not flaws.** `pw-intent-justified`,
> `pw-intent-liveness`, `pw-intent-orphan`, and `pw-surface-scoping` assert
> Plainweave's code-up intent graph (`SEI → requirement → goal`) — Plainweave is
> advisory/enrich-only/local and never gates. The `plainweave intent` tour leg
> self-seeds a deterministic covered+uncovered corpus (gitignored `.plainweave/`).
> The catalog's **2/4** public-surface tag coverage (`exported-api`/`http-route`
> absent) is the *demonstrated honest-degradation point* — **do not "fix" it by
> adding a web framework** to chase 4/4. The anchors carry no `LACUNA` docstring;
> the catalogue holds the intent. `make verify` requires plainweave installed
> (`uv tool install /home/john/plainweave`), like the other live tools.

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
