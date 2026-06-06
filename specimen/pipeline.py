"""LACUNA: a deep linear call chain — Loomweave traces it end-to-end.

`ingest → normalize → enrich → validate_record → persist` is a five-hop chain of
direct module-level calls. Loomweave's `entity_execution_path_list(ingest)` returns
the whole path in one read, and `entity_callers_list` / `entity_call_site_list`
walk it back from the tail — the navigation analog of a taint chain.

Catalogued in tour/lacunae.toml. Intentional, permanent fixture: flattening or
inlining the chain fails `make verify`.
"""

from __future__ import annotations


def ingest(raw: str) -> int:
    """Head of the pipeline — where Loomweave's execution-path query starts."""
    return normalize(raw)


def normalize(raw: str) -> int:
    return enrich(raw.strip())


def enrich(value: str) -> int:
    return validate_record(value.lower())


def validate_record(value: str) -> int:
    return persist(value or "unknown")


def persist(value: str) -> int:
    """Tail of the chain — the deepest hop in the execution path."""
    return len(value)
