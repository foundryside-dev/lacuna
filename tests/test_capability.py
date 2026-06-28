from tour.capability import _extract_subcommand_choices, detect

LIVE = {"loomweave", "filigree", "wardline"}

_FULL = {"loomweave", "filigree", "wardline", "legis", "warpline", "plainweave"}

# Real argparse usage lines (captured from `plainweave --help`).
_HELP_1_0_0 = (
    "usage: plainweave [-h] [--version]\n"
    "                  {init,doctor,req,criterion,trace,catalog,goal,bind,intent,"
    "baseline,actor,verify,status,dossier} ...\n\nPlainweave requirements ...\n"
)
_HELP_CLI_PARITY = (
    "usage: plainweave [-h] [--version]\n"
    "                  {init,doctor,req,criterion,trace,catalog,goal,bind,intent,"
    "baseline,actor,verify,status,dossier,requirements-enrichment,wardline-peer-facts,web} ...\n"
)


def test_detects_installed_tools():
    caps = detect(which=lambda name: f"/usr/bin/{name}" if name in LIVE else None)
    by_name = {c.name: c for c in caps}
    assert by_name["loomweave"].available is True
    assert by_name["wardline"].available is True


def test_design_only_tools_reported_unavailable():
    caps = detect(which=lambda name: f"/usr/bin/{name}" if name in LIVE else None)
    by_name = {c.name: c for c in caps}
    assert by_name["charter"].available is False
    assert "design-only" in by_name["charter"].detail


def _fake_which(present):
    return lambda name: f"/home/john/.local/bin/{name}" if name in present else None


def test_legis_is_a_detectable_live_member_when_installed():
    caps = {c.name: c for c in detect(_fake_which({"loomweave", "filigree", "wardline", "legis"}))}
    assert "legis" in caps
    assert caps["legis"].available is True
    # charter remains design-only
    assert caps["charter"].available is False


def test_legis_absent_reports_unavailable_not_design_only(monkeypatch):
    monkeypatch.setattr("tour.capability.BIN", __import__("pathlib").Path("/nonexistent/bin"))
    caps = {c.name: c for c in detect(_fake_which({"loomweave", "filigree", "wardline"}))}
    assert caps["legis"].available is False
    assert "design-only" not in caps["legis"].detail


def test_warpline_is_a_detectable_live_member_when_installed():
    # warpline must be a RUNNABLE capability so verify's coverage gate actually
    # asserts the wp-* entries (`expected_tool in live`); without this the leg
    # could degrade silently. NOT design-only — warpline ships a runnable CLI.
    caps = {c.name: c for c in detect(_fake_which({"loomweave", "filigree", "wardline", "legis", "warpline"}))}
    assert "warpline" in caps
    assert caps["warpline"].available is True


def test_plainweave_is_a_detectable_live_member_when_installed():
    # plainweave must be RUNNABLE so verify's coverage gate asserts the pw-* entries
    # (`expected_tool in live`). It is installed as a uv tool in ~/.local/bin like its
    # siblings; NOT design-only.
    caps = {c.name: c for c in detect(_fake_which(
        {"loomweave", "filigree", "wardline", "legis", "warpline", "plainweave"}
    ))}
    assert "plainweave" in caps
    assert caps["plainweave"].available is True


def test_plainweave_absent_reports_unavailable_not_design_only(monkeypatch):
    monkeypatch.setattr("tour.capability.BIN", __import__("pathlib").Path("/nonexistent/bin"))
    caps = {c.name: c for c in detect(_fake_which({"loomweave", "filigree", "wardline", "legis", "warpline"}))}
    assert caps["plainweave"].available is False
    assert "design-only" not in caps["plainweave"].detail


# ── Per-subcommand peer-facts capabilities (PDR-0016) ──────────────────────────
# The peer-facts cells gate on a SPECIFIC plainweave CLI surface, probed by behaviour
# (`plainweave --help`), not on the bare binary — PyPI 1.0.0 ships the binary but not
# the subcommands. `pw_subcommands` is injected so these tests never shell out.


def test_peer_facts_caps_live_when_surface_present():
    caps = {c.name: c for c in detect(
        _fake_which(_FULL),
        pw_subcommands=lambda path: frozenset({"intent", "requirements-enrichment", "wardline-peer-facts"}),
    )}
    assert caps["plainweave-requirements-enrichment"].available is True
    assert caps["plainweave-wardline-peer-facts"].available is True


def test_peer_facts_caps_unavailable_when_surface_absent():
    # plainweave binary present, but the peer-facts subcommands are NOT in its surface.
    caps = {c.name: c for c in detect(
        _fake_which(_FULL),
        pw_subcommands=lambda path: frozenset({"intent", "req", "trace"}),
    )}
    assert caps["plainweave"].available is True              # the binary IS present
    assert caps["plainweave-requirements-enrichment"].available is False
    assert caps["plainweave-wardline-peer-facts"].available is False
    # machine-readable reason, not a design-only / silent-empty
    assert "requirements-enrichment" in caps["plainweave-requirements-enrichment"].detail
    assert "1.0.0" in caps["plainweave-requirements-enrichment"].detail


def test_peer_facts_caps_gate_per_subcommand_not_combined():
    # A PARTIAL plainweave release (only one subcommand) must light up exactly that
    # cell and gate only the other — proves the gate is per-subcommand.
    caps = {c.name: c for c in detect(
        _fake_which(_FULL),
        pw_subcommands=lambda path: frozenset({"requirements-enrichment"}),
    )}
    assert caps["plainweave-requirements-enrichment"].available is True
    assert caps["plainweave-wardline-peer-facts"].available is False


def test_warpline_attest_bundle_cap_live_when_surface_present():
    # a warpline carrying the wardline-attest-2 consumer exposes `reverify --attest-bundle`.
    caps = {c.name: c for c in detect(
        _fake_which(_FULL),
        wp_reverify_options=lambda path: frozenset({"--repo", "--depth", "--attest-bundle", "--json"}),
    )}
    assert caps["warpline-attest-bundle"].available is True


def test_warpline_attest_bundle_cap_gated_when_surface_absent():
    # warpline binary present, but a pre-attest-2 build (main/PyPI, same 1.2.0 string)
    # lacks the `--attest-bundle` flag -> the capability is honestly unavailable.
    caps = {c.name: c for c in detect(
        _fake_which(_FULL),
        wp_reverify_options=lambda path: frozenset({"--repo", "--depth", "--json"}),
    )}
    assert caps["warpline"].available is True               # the binary IS present
    assert caps["warpline-attest-bundle"].available is False
    assert "attest-bundle" in caps["warpline-attest-bundle"].detail  # machine-readable reason


def test_peer_facts_caps_unavailable_when_plainweave_binary_absent(monkeypatch):
    # No plainweave binary at all → the real probe is handed None and returns empty,
    # so the caps are unavailable (cannot tell == unavailable, never silent-present).
    monkeypatch.setattr("tour.capability.BIN", __import__("pathlib").Path("/nonexistent/bin"))
    caps = {c.name: c for c in detect(_fake_which({"loomweave", "filigree", "wardline"}))}
    assert caps["plainweave"].available is False
    assert caps["plainweave-requirements-enrichment"].available is False
    assert caps["plainweave-wardline-peer-facts"].available is False


# ── The --help parse (PRESENT-extraction path) — the linchpin of "probe by surface,
#    not version string". Unit-tested directly so a regex/usage-format regression can't
#    silently break detection after a >=1.1 plainweave upgrade (only the ABSENT path is
#    live-reachable under the pinned 1.0.0).


def test_extract_choices_pins_real_1_0_0_surface_excludes_peer_facts():
    subs = _extract_subcommand_choices(_HELP_1_0_0)
    assert "intent" in subs                                  # a real 1.0.0 subcommand
    assert "requirements-enrichment" not in subs            # absent in 1.0.0
    assert "wardline-peer-facts" not in subs


def test_extract_choices_pins_cli_parity_surface_includes_peer_facts():
    # The reconciliation claim: a >=1.1 / CLI-parity build's --help yields BOTH subcommands.
    subs = _extract_subcommand_choices(_HELP_CLI_PARITY)
    assert "requirements-enrichment" in subs
    assert "wardline-peer-facts" in subs


def test_extract_choices_survives_line_wrapped_block():
    wrapped = "usage: x [-h]\n  {init,\n   requirements-enrichment,\n   wardline-peer-facts} ...\n"
    subs = _extract_subcommand_choices(wrapped)
    assert {"init", "requirements-enrichment", "wardline-peer-facts"} <= subs


def test_extract_choices_empty_on_no_choices_block():
    assert _extract_subcommand_choices("usage: x [-h]\n\nno subparsers here\n") == frozenset()
