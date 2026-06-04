"""Load and validate the lacunae manifest — the single source of truth."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Lacuna:
    id: str
    file: str
    symbol: str
    category: str
    demonstrates: tuple[str, ...]
    explanation: str
    expected_tool: str
    expected_rule: str


@dataclass(frozen=True)
class Manifest:
    lacunae: tuple[Lacuna, ...]

    def cells(self) -> set[str]:
        """Every tool / matrix-cell any lacuna demonstrates."""
        return {cell for l in self.lacunae for cell in l.demonstrates}


def load_manifest(path: Path) -> Manifest:
    raw = tomllib.loads(Path(path).read_text())
    entries = raw.get("lacuna", [])
    lacunae = tuple(
        Lacuna(
            id=e["id"],
            file=e["file"],
            symbol=e["symbol"],
            category=e["category"],
            demonstrates=tuple(e["demonstrates"]),
            explanation=e["explanation"],
            expected_tool=e["expected_tool"],
            expected_rule=e["expected_rule"],
        )
        for e in entries
    )
    return Manifest(lacunae=lacunae)
