"""Planted Wardline lacunae — the trust-boundary / decorator-shape family.

Each function is an INTENTIONAL, catalogued flaw (see tour/lacunae.toml). These
exercise Wardline's structural trust rules (boundary shape, decorator validity,
contradictory markers, none-leak, stored taint) rather than taint-to-sink flows.
Do NOT "fix" them; they are permanent demonstration fixtures.
"""

from __future__ import annotations

from collections.abc import Sequence

from weft_markers import external_boundary, trust_boundary, trusted

# PY-WL-110 currently does NOT fire for weft_markers markers (engine gap,
# tracked as filigree wardline-d62845bb18). To still demonstrate the rule
# firing, the asserted 110 fixture below uses Wardline's own canonical
# `wardline.decorators` namespace, where 110 works. The weft_markers variant
# (`contradictory_member`) is kept as a documented known-gap demonstrator.
from wardline.decorators import external_boundary as wl_external_boundary
from wardline.decorators import trusted as wl_trusted


@external_boundary
def read_member_field(argv: Sequence[str]) -> str:
    """A raw operator-supplied field crossing the boundary (untrusted)."""
    return argv[0] if argv else ""


@trusted(level="ASSURED")
def persist_member(field: str) -> str:
    """A trusted producer that expects a validated member field."""
    return f"member:{field}"


def register_member(argv: Sequence[str]) -> str:
    """LACUNA (PY-WL-105): an untrusted value is passed straight into a trusted
    callee at the call site, with no boundary in between."""
    return persist_member(read_member_field(argv))


@trusted(level="ASSURED")
def renewal_count(flag: bool) -> int:
    """LACUNA (PY-WL-109): the contract promises a non-None int, but one path
    falls through and returns None."""
    if flag:
        return 1
    return  # type: ignore[return-value]


@wl_trusted
@wl_external_boundary
def contradictory_member(argv: Sequence[str]) -> str:
    """LACUNA (PY-WL-110): a function marked BOTH @trusted and @external_boundary —
    it cannot be a trusted producer and an untrusted source at once.

    Uses `wardline.decorators` (not weft_markers) because PY-WL-110 does not yet
    fire for the weft_markers namespace — see `contradictory_member_gap` below and
    filigree wardline-d62845bb18."""
    return argv[0] if argv else ""


@trusted
@external_boundary
def contradictory_member_gap(argv: Sequence[str]) -> str:
    """KNOWN-GAP demonstrator (NOT asserted): the SAME contradictory stack as
    `contradictory_member`, but via weft_markers — PY-WL-110 silently fails to
    fire here. Tracked as filigree wardline-d62845bb18; this fixture exists to
    make lacuna surface the gap honestly rather than hide it."""
    return argv[0] if argv else ""


@trust_boundary(to_level="ASSURED")
def assert_only_member(field: str) -> str:
    """LACUNA (PY-WL-111): the boundary's only rejection path is `assert`, which
    is stripped under `python -O` — so in production it validates nothing."""
    assert field, "member field must be non-empty"
    return field.strip()


@trust_boundary(to_level="ASSURED")
def failopen_member(field: str) -> str:
    """LACUNA (PY-WL-113): the boundary fails OPEN — on any validation error it
    returns the raw input unchanged instead of rejecting it."""
    try:
        if not field.isalnum():
            raise ValueError("invalid member field")
        return field
    except ValueError:
        return field  # fail-open: untrusted value escapes the boundary


@trusted(level="SUPERUSER")
def invalid_level_member(field: str) -> str:
    """LACUNA (PY-WL-114): the decorator declares a trust level that is not a
    valid Wardline level (`SUPERUSER` is not in the lattice)."""
    return f"member:{field}"


@trust_boundary(to_level="ASSURED")
def degenerate_member(field: str) -> str:
    """LACUNA (PY-WL-119): a no-op validator boundary whose return value is
    its input parameter verbatim — it claims to validate but checks nothing."""
    return field


@trusted(level="ASSURED")
def load_member_record() -> str:
    """LACUNA (PY-WL-120): data read from persistent storage (a file read) reaches
    a trusted producer's return value with no validation boundary in between —
    stored/persisted taint promoted straight to trusted."""
    with open("members.dat", encoding="utf-8") as fh:  # noqa: PTH123 — fixed path; not PY-WL-116
        record = fh.read()
    return record
