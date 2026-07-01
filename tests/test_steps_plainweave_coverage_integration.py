"""Real-producer integration smoke for the plainweave coverage leg (spec §8.4).

Deselected from unit-only CI by the `integration` marker (pyproject's
`addopts = "-q -m 'not integration'"`); run explicitly with `pytest -m integration`.
Drives the ACTUAL `plainweave baseline/verify/status/dossier` against a real seed in an
isolated offline workspace and PINS the envelope fields the leg's predicates key on, so a
plainweave contract drift (renamed status string / reason code / dossier field) surfaces as
a regression rather than silently. Field values verified against real plainweave 1.2.0.
"""

import shutil

import pytest

from tour import plainweave_seed, steps

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not (
            steps._plainweave_supports("baseline")
            and steps._plainweave_supports("verify")
            and steps._plainweave_supports("dossier")
        ),
        reason="real plainweave baseline/verify/dossier surface not installed",
    ),
]


def _item(items, rid):
    return next((it for it in items
                 if it.get("id") == rid or it.get("requirement_id") == rid), {})


def _ids(data):
    out = set()
    for it in data.get("items", []):
        out |= {it.get("id"), it.get("requirement_id")}
    return out


def test_plainweave_coverage_real_producer_envelope_shapes():
    workspace = plainweave_seed.materialize_workspace()

    def pw(args):
        env = steps._plainweave_json(args, cwd=workspace)
        if env is None or not env.get("ok"):
            raise AssertionError(f"setup call failed: {args}")
        return env.get("data") or {}

    try:
        reqs = plainweave_seed.seed(pw, deprecate=False, with_trace_links=True, root=workspace)
        add_book = reqs[plainweave_seed.ADD_BOOK]
        cli_main = reqs[plainweave_seed.CLI_MAIN]
        register = reqs[plainweave_seed.REGISTER]
        actor = plainweave_seed.ACTOR

        m_add = pw(["verify", "method", "add", add_book, "--method", "test",
                    "--target", "tests/test_cli.py::test_add_book", "--actor", actor])["id"]
        pw(["verify", "evidence", "record", m_add, "--status", "passing",
            "--evidence-ref", "ci://run/coverage-add-book", "--actor", actor])
        m_cli = pw(["verify", "method", "add", cli_main, "--method", "test",
                    "--target", "tests/test_cli.py::test_main", "--actor", actor])["id"]
        pw(["verify", "evidence", "record", m_cli, "--status", "passing",
            "--evidence-ref", "ci://run/coverage-cli-main", "--actor", actor])
        pw(["verify", "method", "add", register, "--method", "test",
            "--target", "tests/test_cli.py::test_register", "--actor", actor])

        # No-baseline arm BEFORE create: an honest NOT_FOUND, never a silent clean.
        no_baseline = steps._plainweave_json(
            ["baseline", "diff", steps.PLAINWEAVE_COVERAGE_BOGUS_BASELINE], cwd=workspace)
        assert no_baseline is not None and no_baseline.get("ok") is False

        baseline_id = pw(["baseline", "create", "--name", steps.PLAINWEAVE_COVERAGE_BASELINE,
                          "--actor", actor])["id"]
        pw(["req", "supersede", add_book, "--title", "Add-a-book command (revised)",
            "--statement", "The CLI can add a book to the catalog with validation.",
            "--expected-version", "1", "--actor", actor])

        diff = steps._plainweave_json(["baseline", "diff", baseline_id], cwd=workspace)["data"]
        st_add = steps._plainweave_json(["verify", "status", add_book], cwd=workspace)["data"]
        st_cli = steps._plainweave_json(["verify", "status", cli_main], cwd=workspace)["data"]
        st_reg = steps._plainweave_json(["verify", "status", register], cwd=workspace)["data"]
        unver = steps._plainweave_json(["status", "unverified"], cwd=workspace)["data"]
        stale = steps._plainweave_json(["status", "stale"], cwd=workspace)["data"]
        doss = steps._plainweave_json(["dossier", cli_main], cwd=workspace)["data"]
        doss_unknown = steps._plainweave_json(
            ["dossier", steps.PLAINWEAVE_COVERAGE_BOGUS_REQ], cwd=workspace)
    finally:
        shutil.rmtree(workspace, ignore_errors=True)

    # ── baseline diff: superseded req is drift; untouched req stays unchanged ──
    assert _item(diff["items"], add_book)["status"] == "superseded_since_baseline"
    assert _item(diff["items"], cli_main)["status"] == "unchanged"

    # ── verification trichotomy: satisfied(+passing_evidence) / unverified / stale ──
    assert st_cli["status"] == "satisfied"
    assert "passing_evidence" in {r.get("code") for r in st_cli.get("reasons", [])}
    assert st_reg["status"] == "unverified"
    assert st_add["status"] == "stale"
    assert register in _ids(unver)
    assert add_book in _ids(stale)

    # ── dossier: coherent for known, honest error for unknown ──
    assert doss["verification"]["status"] == "satisfied"
    assert any(it.get("state") == "current" for it in doss["baseline_exposure"]["items"])
    assert doss["traces"]["incoming"]
    assert doss_unknown is not None and doss_unknown.get("ok") is False
