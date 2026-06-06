"""LACUNA (half 1 of 2): a deliberate circular import with cycle_b.

Catalogued in tour/lacunae.toml. The import is MODULE-LEVEL (so Loomweave records an
`imports` edge) but imports the module object, so the cycle does not break load.
"""

from __future__ import annotations

import specimen.cycle_b


def ping(n: int) -> int:
    return specimen.cycle_b.pong(n) if n > 0 else 0
