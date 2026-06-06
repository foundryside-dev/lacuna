"""LACUNA: an entity with no callers — Loomweave's entity_dead_list surfaces it.

Intentional, catalogued fixture (tour/lacunae.toml). Do not delete.
"""

from __future__ import annotations


def orphaned_helper(value: str) -> str:
    """Never referenced anywhere in the specimen — deliberately dead."""
    return value[::-1]
