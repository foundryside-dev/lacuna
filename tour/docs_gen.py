"""Generate one explainer page per lacuna from the manifest."""

from __future__ import annotations

from pathlib import Path

from tour.manifest import Lacuna, load_manifest


def render_flaw_page(lac: Lacuna) -> str:
    cells = ", ".join(f"`{c}`" for c in lac.demonstrates)
    return (
        f"# {lac.id}\n\n"
        f"_Generated from `tour/lacunae.toml`. Do not edit by hand._\n\n"
        f"- **Location:** `{lac.file}` → `{lac.symbol}`\n"
        f"- **Category:** {lac.category}\n"
        f"- **Demonstrates:** {cells}\n"
        f"- **Expected finding:** `{lac.expected_tool}` / `{lac.expected_rule}`\n\n"
        f"## Why it's here\n\n{lac.explanation}\n\n"
        f"> This is an intentional, permanent demonstration fixture. Removing or "
        f"\"fixing\" it fails `make verify`.\n"
    )


def generate(root: Path = Path("/home/john/lacuna")) -> int:
    manifest = load_manifest(root / "tour" / "lacunae.toml")
    out = root / "docs" / "flaws"
    out.mkdir(parents=True, exist_ok=True)
    for lac in manifest.lacunae:
        (out / f"{lac.id}.md").write_text(render_flaw_page(lac))
    return len(manifest.lacunae)


if __name__ == "__main__":
    n = generate()
    print(f"generated {n} flaw page(s)")
