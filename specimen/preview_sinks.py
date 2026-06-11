"""Planted Wardline PREVIEW-rule lacunae — the PY-WL-121…126 sink families.

Each function is an INTENTIONAL, catalogued flaw (see tour/lacunae.toml). Every
one pulls an EXTERNAL_RAW value from a boundary and drives it into one of the
six 2026-06-11 preview sink families. Preview rules fire by default but are
gate-immune (Maturity.PREVIEW is filtered from --fail-on). Do NOT "fix" them.

NOTE: ``log_export_request`` (PY-WL-125) is the tour's designated SENTINEL —
deliberately NOT baselined; the filigree tour leg promotes and cycles it.
Do not baseline it.

Theme: the library-catalog admin surface grows feed-parsing, templating,
preferences, codecs, logging and notification — each one (carelessly) driving
an operator-supplied string into a new interpreter.
"""

from __future__ import annotations

import ctypes
import logging
import smtplib
from collections.abc import Sequence

import jinja2  # noqa: F401 — sink namespace; not required to be installed for static scan
from lxml import etree  # noqa: F401 — sink namespace; not required to be installed for static scan

from weft_markers import external_boundary, trusted

logger = logging.getLogger(__name__)


@external_boundary
def read_report_field(argv: Sequence[str]) -> str:
    """An operator-supplied string crossing the reporting boundary (untrusted)."""
    return argv[0] if argv else ""


@trusted(level="ASSURED")
def parse_catalog_feed(argv: Sequence[str]) -> object:
    """LACUNA (PY-WL-121): untrusted XML text reaches lxml.etree.fromstring (XXE)."""
    text = read_report_field(argv)
    return etree.fromstring(text)


@trusted(level="ASSURED")
def render_report_template(argv: Sequence[str]) -> str:
    """LACUNA (PY-WL-122): untrusted template source reaches jinja2.Template (SSTI)."""
    source = read_report_field(argv)
    return jinja2.Template(source).render()


@trusted(level="ASSURED")
def apply_display_option(argv: Sequence[str], prefs: object) -> None:
    """LACUNA (PY-WL-123): untrusted attribute NAME reaches setattr (reflection injection)."""
    name = read_report_field(argv)
    setattr(prefs, name, True)


@trusted(level="ASSURED")
def load_codec_library(argv: Sequence[str]) -> object:
    """LACUNA (PY-WL-124): untrusted path reaches ctypes.CDLL (native-library load)."""
    path = read_report_field(argv)
    return ctypes.CDLL(path)


@trusted(level="ASSURED")
def log_export_request(argv: Sequence[str]) -> None:
    """LACUNA (PY-WL-125) — THE TOUR SENTINEL: untrusted text reaches logging (log injection)."""
    msg = read_report_field(argv)
    logger.info(msg)


@trusted(level="ASSURED")
def notify_member(argv: Sequence[str]) -> None:
    """LACUNA (PY-WL-126): untrusted recipient/body reach smtplib sendmail (mail injection)."""
    field = read_report_field(argv)
    smtp = smtplib.SMTP("localhost")
    smtp.sendmail("library@example.org", [field], field)
