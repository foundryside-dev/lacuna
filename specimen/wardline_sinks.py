"""Planted Wardline lacunae — the untrusted-data-reaches-a-dangerous-sink family.

Each function is an INTENTIONAL, catalogued flaw (see tour/lacunae.toml). Every
one pulls an EXTERNAL_RAW value from a boundary and drives it into a dangerous
sink inside a trusted-tier function — the canonical taint-to-sink shape Wardline
flags. Do NOT "fix" them; they are permanent demonstration fixtures.

Theme: a library-catalog "admin/export" surface that (carelessly) lets an
operator-supplied string reach interpreters, the shell, the importer, the
filesystem, the network, and the database.
"""

from __future__ import annotations

import importlib
import os
import pickle
import sqlite3
import subprocess
from collections.abc import Sequence

import requests  # noqa: F401 — sink namespace; not required to be installed for static scan

from weft_markers import external_boundary, trusted


@external_boundary
def read_admin_arg(argv: Sequence[str]) -> str:
    """An operator-supplied string crossing the admin boundary (untrusted)."""
    return argv[0] if argv else ""


@trusted(level="ASSURED")
def import_catalog_blob(argv: Sequence[str]) -> object:
    """LACUNA (PY-WL-106): untrusted bytes reach pickle.loads."""
    blob = read_admin_arg(argv).encode()
    return pickle.loads(blob)  # noqa: S301


@trusted(level="ASSURED")
def eval_report_formula(argv: Sequence[str]) -> object:
    """LACUNA (PY-WL-107): untrusted text reaches eval()."""
    formula = read_admin_arg(argv)
    return eval(formula)  # noqa: S307


@trusted(level="ASSURED")
def run_export_command(argv: Sequence[str]) -> int:
    """LACUNA (PY-WL-108): untrusted text reaches an OS-command sink."""
    cmd = read_admin_arg(argv)
    return os.system(cmd)  # noqa: S605


@trusted(level="ASSURED")
def shell_archive(argv: Sequence[str]) -> int:
    """LACUNA (PY-WL-112): untrusted text reaches a shell=True subprocess."""
    cmd = read_admin_arg(argv)
    return subprocess.call(cmd, shell=True)  # noqa: S602


@trusted(level="ASSURED")
def load_report_plugin(argv: Sequence[str]) -> object:
    """LACUNA (PY-WL-115): untrusted text reaches a dynamic import sink."""
    name = read_admin_arg(argv)
    return importlib.import_module(name)


@trusted(level="ASSURED")
def open_catalog_file(argv: Sequence[str]) -> str:
    """LACUNA (PY-WL-116): untrusted text reaches a filesystem-path sink."""
    path = read_admin_arg(argv)
    with open(path, encoding="utf-8") as fh:  # noqa: PTH123
        return fh.read()


@trusted(level="ASSURED")
def fetch_cover_image(argv: Sequence[str]) -> object:
    """LACUNA (PY-WL-117): untrusted text reaches an HTTP-client sink (SSRF)."""
    url = read_admin_arg(argv)
    return requests.get(url, timeout=5)


@trusted(level="ASSURED")
def lookup_member(argv: Sequence[str]) -> list[object]:
    """LACUNA (PY-WL-118): untrusted text reaches a SQL execution sink."""
    name = read_admin_arg(argv)
    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM members WHERE name = '{name}'")  # noqa: S608
    return cur.fetchall()
