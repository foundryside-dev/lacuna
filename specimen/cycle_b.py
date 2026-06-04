"""LACUNA (half 2 of 2): a deliberate circular import with cycle_a."""

from __future__ import annotations

import specimen.cycle_a


def pong(n: int) -> int:
    return specimen.cycle_a.ping(n - 1)
