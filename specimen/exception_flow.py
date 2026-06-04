"""Planted Wardline lacunae for the exception-handling rules.

Each function here is an INTENTIONAL, catalogued flaw (see tour/lacunae.toml).
Do not "fix" them — they are permanent demonstration fixtures.
"""

from __future__ import annotations

from collections.abc import Sequence

from loom_markers import external_boundary, trust_boundary, trusted


@external_boundary
def read_config_value(argv: Sequence[str]) -> str:
    """Raw external value crossing the boundary."""
    return argv[0] if argv else ""


@trust_boundary(to_level="ASSURED")
def non_rejecting_boundary(raw: str) -> str:
    """LACUNA (PY-WL-102): a trust boundary that never rejects — it normalizes but
    has no rejection path, so nothing is actually validated."""
    return raw.strip().lower()


@trusted(level="ASSURED")
def broad_handler(argv: Sequence[str]) -> str:
    """LACUNA (PY-WL-103): a broad `except Exception` in a trusted-tier function."""
    try:
        return read_config_value(argv).upper()
    except Exception:  # noqa: BLE001 - intentional Wardline fixture
        return "DEFAULT"


@trusted(level="ASSURED")
def swallowed_error(argv: Sequence[str]) -> str:
    """LACUNA (PY-WL-104): an exception silently swallowed with `pass` in a
    trusted-tier function."""
    result = "DEFAULT"
    try:
        result = read_config_value(argv).upper()
    except ValueError:
        pass  # intentional Wardline fixture: silently swallowed
    return result
