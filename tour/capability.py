"""Detect which Weft tools are runnable. Degrade honestly — never fake a tool."""

from __future__ import annotations

import re
import shutil
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

# Tools that ship a runnable CLI today. plainweave is installed as a uv tool
# (`uv tool install /home/john/plainweave`) → ~/.local/bin/plainweave, exactly like
# its siblings; adding it here ARMS verify's coverage gate for the pw-* lacunae.
RUNNABLE = ("loomweave", "filigree", "wardline", "legis", "warpline", "plainweave")
# Members that exist in the suite but are not yet first-class here.
DESIGN_ONLY = ("charter",)
# Known install dir — the tools live here whether or not it is on $PATH.
BIN = Path("/home/john/.local/bin")

# Per-subcommand plainweave capabilities. The peer-facts tour cells need a SPECIFIC
# plainweave CLI surface, not merely the binary: PyPI 1.0.0 ships `plainweave` but
# not these subcommands (they land with Plainweave PDR-015 / plainweave >= 1.1).
# Gating each cell on its own subcommand (rather than one combined capability) means
# a PARTIAL plainweave release lights up exactly the cells whose surface is present
# and gates only the ones whose surface is absent. Maps subcommand -> capability name
# (a lacuna's `expected_tool`).
PLAINWEAVE_PEER_FACT_SUBCOMMANDS = {
    "requirements-enrichment": "plainweave-requirements-enrichment",
    "wardline-peer-facts": "plainweave-wardline-peer-facts",
}

# Per-option warpline capabilities. The risk-as-verification tour cell needs a SPECIFIC
# warpline CLI surface — `reverify --attest-bundle` — not merely the binary: a warpline
# built before the wardline-attest-2 consumer landed (a main-branch or PyPI build sharing
# the 1.2.0 version string) ships `warpline` but not that flag — the stale-build trap.
# Maps reverify option -> capability name (a lacuna's `expected_tool`).
WARPLINE_PEER_FACT_OPTIONS = {
    "--attest-bundle": "warpline-attest-bundle",
}

# Per-subcommand plainweave COVERAGE capabilities (coverage-lacunae, spec §4). These
# gate each coverage cell on its base subcommand. NOTE: baseline/verify/status/dossier
# ship in plainweave's BASE surface (present in 1.0.0), so these light up on any
# plainweave that exposes the subcommand — the [N/A] path is reached only when the
# surface is genuinely absent (a stripped/pre-baseline build). Maps subcommand ->
# capability name (a lacuna's `expected_tool`).
PLAINWEAVE_COVERAGE_SUBCOMMANDS = {
    "baseline": "plainweave-baseline",
    "verify": "plainweave-verify",
    "dossier": "plainweave-dossier",
}


def plainweave_subcommands(plainweave_path: str | None) -> frozenset[str]:
    """The top-level subcommands the installed plainweave actually exposes.

    Probed by parsing the argparse choices block of `plainweave --help`, so the
    peer-facts cells gate on BEHAVIOUR (the real CLI surface), not on a version
    string — PyPI 1.0.0 and an unreleased CLI-parity build can share a version
    string but not a surface (the stale-build trap). Returns an empty set on any
    failure (absent binary, probe error, parse miss): the caller treats "cannot
    tell" as "surface unavailable", never as a silent present.
    """
    if not plainweave_path:
        return frozenset()
    try:
        proc = subprocess.run(
            [plainweave_path, "--help"],
            capture_output=True, text=True, check=False, timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return frozenset()
    return _extract_subcommand_choices(proc.stdout)


def warpline_reverify_options(warpline_path: str | None) -> frozenset[str]:
    """The long-option flags `warpline reverify` exposes, parsed from its --help.

    Probed by SURFACE (the real CLI surface), not a version string: a main-branch or PyPI
    warpline can share the `1.2.0` version yet lack `--attest-bundle` (it ships with the
    wardline-attest-2 consumer). Returns an empty set on any failure (absent binary, probe
    error): "cannot tell" ⇒ surface unavailable, never a silent present.
    """
    if not warpline_path:
        return frozenset()
    try:
        proc = subprocess.run(
            [warpline_path, "reverify", "--help"],
            capture_output=True, text=True, check=False, timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return frozenset()
    return frozenset(re.findall(r"--[a-z][a-z0-9-]+", proc.stdout))


def _extract_subcommand_choices(help_text: str) -> frozenset[str]:
    """Pull argparse's first `{a,b,c,...}` choices block (the subcommand list) out of
    `--help` text. Pure (no I/O) so the parse — the linchpin of "probe by surface, not
    version string" — is unit-testable independently of an installed plainweave. The
    pattern is non-greedy (stops at the first `}`) and `\\s`-tolerant so a line-wrapped
    choices block still parses. Returns an empty set on a parse miss ("cannot tell" ⇒
    surface unavailable, never a silent present)."""
    match = re.search(r"\{([a-z0-9_,\s\-]+?)\}", help_text)
    if not match:
        return frozenset()
    return frozenset(tok for tok in re.sub(r"\s+", "", match.group(1)).split(",") if tok)


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


def detect(
    which: Callable[[str], str | None] = shutil.which,
    pw_subcommands: Callable[[str | None], frozenset[str]] = plainweave_subcommands,
    wp_reverify_options: Callable[[str | None], frozenset[str]] = warpline_reverify_options,
) -> list[Capability]:
    caps: list[Capability] = []
    plainweave_path: str | None = None
    warpline_path: str | None = None
    for name in RUNNABLE:
        path = _locate(name, which)
        if name == "plainweave":
            plainweave_path = path
        if name == "warpline":
            warpline_path = path
        caps.append(
            Capability(
                name=name,
                available=path is not None,
                detail=path or "not found (PATH or ~/.local/bin)",
            )
        )
    # Per-subcommand peer-facts capabilities, probed from the actual plainweave CLI
    # surface. Under PyPI 1.0.0 the binary is present but the subcommands are not, so
    # these report UNAVAILABLE with a machine-readable reason — and the peer-facts
    # lacunae (whose `expected_tool` is one of these names) are gated out of verify's
    # coverage assertion rather than reported as a failed surface.
    surface = pw_subcommands(plainweave_path)
    for sub, cap_name in PLAINWEAVE_PEER_FACT_SUBCOMMANDS.items():
        present = sub in surface
        caps.append(
            Capability(
                name=cap_name,
                available=present,
                detail=(
                    (plainweave_path or "plainweave")
                    if present
                    else f"plainweave `{sub}` CLI surface absent "
                    "(Plainweave PDR-015 / plainweave >= 1.1; not in PyPI 1.0.0)"
                ),
            )
        )
    # Per-subcommand coverage capabilities, probed from the same plainweave surface.
    # Absent surface (stripped/pre-baseline build) -> cap UNAVAILABLE with a
    # machine-readable reason, so the coverage lacunae are gated out of verify's
    # coverage assertion rather than reported as a failed surface.
    for sub, cap_name in PLAINWEAVE_COVERAGE_SUBCOMMANDS.items():
        present = sub in surface
        caps.append(
            Capability(
                name=cap_name,
                available=present,
                detail=(
                    (plainweave_path or "plainweave")
                    if present
                    else f"plainweave `{sub}` CLI surface absent"
                ),
            )
        )
    # Per-option warpline capabilities, probed from the actual warpline reverify surface.
    # A warpline built before the wardline-attest-2 consumer (main/PyPI, same 1.2.0 string)
    # lacks `--attest-bundle`, so the risk-as-verification lacuna (whose `expected_tool` is
    # this capability name) gates out of verify's coverage assertion rather than reporting a
    # failed surface — exactly like the plainweave peer-facts cells under PyPI 1.0.0.
    wp_options = wp_reverify_options(warpline_path)
    for opt, cap_name in WARPLINE_PEER_FACT_OPTIONS.items():
        present = opt in wp_options
        caps.append(
            Capability(
                name=cap_name,
                available=present,
                detail=(
                    (warpline_path or "warpline")
                    if present
                    else f"warpline `reverify {opt}` surface absent "
                    "(pre-attest-2 build; ships with the wardline-attest-2 consumer)"
                ),
            )
        )
    for name in DESIGN_ONLY:
        caps.append(
            Capability(name=name, available=False, detail="design-only (not yet first-class)")
        )
    return caps
