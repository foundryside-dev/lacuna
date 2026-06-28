from tour.capability import Capability
from tour.manifest import Lacuna, Manifest
from tour.report import StepResult, coverage, render_matrix_md, render_tour_md


def _manifest():
    return Manifest(
        lacunae=(
            Lacuna("a", "specimen/trust_flow.py", "unsafe_account_key", "trust-boundary",
                   ("wardline", "wardline+loomweave"), "exp a", "wardline", "PY-WL-101"),
            Lacuna("b", "specimen/dead_code.py", "orphaned_helper", "structure",
                   ("loomweave",), "exp b", "loomweave", "dead-entity"),
        )
    )


def test_coverage_matches_on_rule_AND_symbol():
    m = _manifest()
    results = [StepResult("scan", ok=True, detail="",
                          surfaced=(("PY-WL-101", "specimen.trust_flow.unsafe_account_key"),))]
    cov = coverage(m, results)
    assert cov.demonstrated_ids == {"a"}
    assert cov.missing_ids == {"b"}


def test_coverage_does_not_credit_token_on_wrong_symbol():
    """Anti-hollow-gate: a `dead-entity` token for an unrelated symbol (e.g. an
    incidental uncalled dunder) must NOT mark the planted lacuna demonstrated.
    Otherwise deleting the lacuna would still pass `make verify`."""
    m = _manifest()
    results = [StepResult("loomweave", ok=True, detail="",
                          surfaced=(("dead-entity", "specimen.models.Entity.__hash__"),))]
    cov = coverage(m, results)
    assert "b" in cov.missing_ids          # orphaned_helper was NOT surfaced
    # and the real planted symbol IS credited:
    results2 = [StepResult("loomweave", ok=True, detail="",
                           surfaced=(("dead-entity", "specimen.dead_code.orphaned_helper"),))]
    assert "b" in coverage(m, results2).demonstrated_ids


def test_coverage_uses_suffix_match_not_substring():
    """`safe_account_key` is a substring of `unsafe_account_key`. A surfaced pair for
    `unsafe_account_key` must NOT credit a lacuna whose symbol is `safe_account_key`."""
    m = Manifest(lacunae=(
        Lacuna("safe", "specimen/trust_flow.py", "safe_account_key", "structure",
               ("loomweave",), "exp", "loomweave", "dead-entity"),
    ))
    results = [StepResult("loomweave", ok=True, detail="",
                          surfaced=(("dead-entity", "specimen.trust_flow.unsafe_account_key"),))]
    assert "safe" in coverage(m, results).missing_ids


def test_tour_md_lists_each_step():
    md = render_tour_md([StepResult("loomweave analyze", ok=True, detail="85 entities")])
    assert "loomweave analyze" in md
    assert "85 entities" in md


def test_matrix_md_labels_design_only_cells():
    m = _manifest()
    caps = [Capability("legis", False, "design-only (not yet first-class)")]
    md = render_matrix_md(m, caps)
    assert "design-only" in md


def test_note_is_not_rendered_into_locked_markdown():
    r = StepResult("legis govern", ok=True, detail="governed 3 active defects → surface_override",
                   note="artifact: verified")
    md = render_tour_md([r])
    assert "governed 3 active defects → surface_override" in md
    assert "verified" not in md            # note stays OUT of the locked narrative


def test_note_defaults_empty_and_is_optional():
    r = StepResult("x", ok=True, detail="d")
    assert r.note == ""


# ── Capability-gating render (PDR-0016) ────────────────────────────────────────


def test_step_result_available_defaults_true():
    assert StepResult("x", ok=True, detail="d").available is True


def test_tour_md_renders_na_for_capability_gated_leg():
    # available=False (capability-gated) renders [N/A], distinct from [PASS]/[WARN] —
    # a gated leg did not run, did not fail, and is NOT faked green.
    gated = render_tour_md([StepResult("plainweave requirements-enrichment", ok=False,
                                       detail="capability-gated — surface absent", available=False)])
    assert "[N/A] plainweave requirements-enrichment" in gated
    assert "[WARN]" not in gated and "[PASS]" not in gated
    # a ran-and-degraded leg is still [WARN], not [N/A]
    warned = render_tour_md([StepResult("x", ok=False, detail="d")])
    assert "[WARN] x" in warned


def test_matrix_md_annotates_capability_gated_cell_not_flat_listed():
    # A cell whose only demonstrating lacuna is gated (expected_tool capability present
    # but unavailable) must be annotated "not exercised", never listed as exercised —
    # otherwise the matrix makes a confident-false coverage claim.
    m = Manifest(lacunae=(
        Lacuna("g", "specimen/cli.py", "_add_book", "peer-facts",
               ("plainweave+warpline",), "exp", "plainweave-requirements-enrichment",
               "pw-requirements-enrichment"),
        Lacuna("live", "specimen/dead_code.py", "orphaned_helper", "structure",
               ("loomweave",), "exp", "loomweave", "dead-entity"),
    ))
    caps = [
        Capability("loomweave", True, "/bin/loomweave"),
        Capability("plainweave-requirements-enrichment", False,
                   "plainweave `requirements-enrichment` CLI surface absent (not in PyPI 1.0.0)"),
    ]
    md = render_matrix_md(m, caps)
    assert "- `loomweave`" in md                                 # live cell: flat-listed
    assert "`plainweave+warpline` — _not exercised" in md        # gated cell: annotated
    assert "requirements-enrichment" in md                       # machine-readable reason carried
