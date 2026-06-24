"""Seed a deterministic Plainweave intent corpus over the specimen, for the
`plainweave_intent` tour leg.

Plainweave's store (`.plainweave/`, gitignored) is regenerable, so the leg
self-populates it COLD every run — exactly like `loomweave_analyze` rebuilds the
loomweave index and warpline's leg rebuilds its snapshot. The corpus is a
deliberate **covered + uncovered mix** (John, 2026-06-24): some public surfaces
are justified (`SEI -> requirement -> goal`) and some are left as honest gaps, so
`intent coverage` reports a *partial* ratio with real `justified` AND `unjustified`
rows, and `intent orphans` / `intent trace` have something to surface.

SEIs are resolved by **stable locator** at seed time (never hardcoded hex), so the
seed survives a `loomweave analyze` re-run. `catalog record` takes the SEI as its
positional `entity_id` (NOT the locator) so it matches `entity_associations`.
"""

from __future__ import annotations

import shutil
from collections.abc import Callable
from pathlib import Path

ROOT = Path("/home/john/lacuna")
ACTOR = "agent:lacuna-pw-seed"

# The 4 public surfaces in Lacuna's Loomweave catalog, by STABLE dotted locator.
ADD_BOOK = "python:function:specimen.cli._add_book"   # cli-command  -> justified  (covered)
REGISTER = "python:function:specimen.cli._register"   # cli-command  -> deprecated (liveness)
CLI_MAIN = "python:function:specimen.cli.main"        # entry-point  -> justified  (covered)
TOUR_MAIN = "python:function:tour.__main__.main"       # entry-point  -> orphan + scoped-out


def seed(pw: Callable[[list[str]], dict], *, deprecate: bool = True) -> None:
    """Build the corpus. ``pw(args) -> data`` runs ``plainweave <args> --json`` and
    returns the envelope's ``data`` (raising on an error envelope).

    ``deprecate=False`` is the liveness positive-control: it skips the deprecation
    so ``_register`` stays justified — proving a passing liveness assertion is the
    deprecation dropping the surface, not a broken seed.
    """
    shutil.rmtree(ROOT / ".plainweave", ignore_errors=True)
    pw(["init", "--project-key", "lacuna"])

    cov = pw(["intent", "coverage"])
    locmap = {it["locator"]: it["sei"] for it in cov["unjustified"]}
    for loc in (ADD_BOOK, REGISTER, CLI_MAIN, TOUR_MAIN):
        if loc not in locmap:
            # Deterministic, hex-free message (the leg keeps detail digit-free).
            raise ValueError(f"surface not in catalog: {loc}")

    goal = pw([
        "goal", "add",
        "--title", "Library catalog is trustworthy",
        "--statement", "Members can add books and accounts through a documented, safe surface.",
        "--actor", ACTOR,
    ])["id"]

    def justify(loc: str, title: str, statement: str) -> str:
        req = pw(["req", "add", "--title", title, "--statement", statement, "--actor", ACTOR])["id"]
        pw(["req", "approve", req, "--expected-version", "0", "--actor", ACTOR])
        pw(["bind", "sei", locmap[loc], req, "--entity-kind", "loomweave_entity", "--actor", ACTOR])
        pw(["goal", "link", goal, req, "--actor", ACTOR])
        return req

    # COVERED (2 justified surfaces): the healthy half of the mix.
    justify(ADD_BOOK, "Add-a-book command", "The CLI can add a book to the catalog.")
    justify(CLI_MAIN, "Library CLI entry point", "The app exposes a single CLI entry point.")

    # UNCOVERED #1 — liveness: bound + laddered, then the requirement is DEPRECATED,
    # so the surface drops out of the north-star numerator (a dead obligation must
    # not inflate honest coverage).
    reg = justify(REGISTER, "Register command (legacy)", "The CLI can register an account.")
    if deprecate:
        pw(["req", "deprecate", reg, "--expected-version", "1", "--actor", ACTOR])

    # UNCOVERED #2 — orphan: record the tour entry-point as a PUBLIC code entity with
    # no requirement, so `intent orphans code` surfaces it. entity_id is the SEI
    # (positional), NOT the locator, so it matches entity_associations.
    pw(["catalog", "record", locmap[TOUR_MAIN], "--entity-kind", "loomweave_entity", "--actor", ACTOR])
