"""Detect which Loom tools are runnable. Degrade honestly — never fake a tool."""

from __future__ import annotations

import shutil
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

# Tools that ship a runnable CLI today.
RUNNABLE = ("clarion", "filigree", "wardline")
# Members that exist in the suite but are not yet first-class here.
DESIGN_ONLY = ("legis", "charter")
# Known install dir — the tools live here whether or not it is on $PATH.
BIN = Path("/home/john/.local/bin")


@dataclass(frozen=True)
class Capability:
    name: str
    available: bool
    detail: str


def _locate(name: str, which: Callable[[str], str | None]) -> str | None:
    """Find a tool by PATH first, then the known install dir. A subagent's PATH may
    not include ~/.local/bin, and a false 'unavailable' would make `verify` assert
    nothing and report a hollow green — so never rely on PATH alone."""
    found = which(name)
    if found:
        return found
    candidate = BIN / name
    return str(candidate) if candidate.exists() else None


def detect(which: Callable[[str], str | None] = shutil.which) -> list[Capability]:
    caps: list[Capability] = []
    for name in RUNNABLE:
        path = _locate(name, which)
        caps.append(
            Capability(
                name=name,
                available=path is not None,
                detail=path or "not found (PATH or ~/.local/bin)",
            )
        )
    for name in DESIGN_ONLY:
        caps.append(
            Capability(name=name, available=False, detail="design-only (not yet first-class)")
        )
    return caps
