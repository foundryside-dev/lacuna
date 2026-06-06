"""LACUNA: a coupling hotspot — Loomweave's entity_coupling_hotspot_list ranks it.

`dispatch` is a bidirectional hub: five `Dispatcher` methods call into it (fan-in)
and it calls five module-level routines (fan-out). Loomweave ranks coupling as
distinct fan-in + fan-out over the call/import graph, so a node heavy on BOTH arms
tops the list — `dispatch` (coupling 10) leads the specimen app's hotspots.

Self-contained on purpose: it imports no other specimen module, so it adds coupling
without creating an import cycle. Catalogued in tour/lacunae.toml — intentional,
permanent fixture.
"""

from __future__ import annotations


class Dispatcher:
    """Five thin entry methods, all funnelling through ``dispatch`` (fan-in)."""

    def handle_create(self, payload: str) -> str:
        return dispatch("create", payload)

    def handle_update(self, payload: str) -> str:
        return dispatch("update", payload)

    def handle_delete(self, payload: str) -> str:
        return dispatch("delete", payload)

    def handle_list(self, payload: str) -> str:
        return dispatch("list", payload)

    def handle_query(self, payload: str) -> str:
        return dispatch("query", payload)


def dispatch(kind: str, payload: str) -> str:
    """The hotspot: fans out to five routines after fanning in from five callers."""
    _audit(kind)
    _route(kind, payload)
    _meter(kind)
    _persist(kind, payload)
    return _format(kind, payload)


def _audit(kind: str) -> None:
    _ = f"audit:{kind}"


def _route(kind: str, payload: str) -> None:
    _ = f"route:{kind}:{payload}"


def _meter(kind: str) -> None:
    _ = f"meter:{kind}"


def _persist(kind: str, payload: str) -> None:
    _ = f"persist:{kind}:{payload}"


def _format(kind: str, payload: str) -> str:
    return f"{kind}:{payload}"
