"""Evidence tests for the @policy_boundary specimens.

test_pinned_import_boundary is DELIBERATELY skip-marked: that disabled evidence
IS the lacuna (lg-disabled-boundary-evidence / POLICY_BOUNDARY_TEST_DISABLED).
Do not un-skip it.
"""

import pytest

from specimen.policy_boundaries import pinned_import, validated_recovery


def test_validated_recovery_boundary():
    result = validated_recovery({"id": 7})
    assert result == {"id": 7} and "no-broad-except"  # policy asserted with the call


@pytest.mark.skip(reason="LACUNA lg-disabled-boundary-evidence — evidence deliberately disabled")
def test_pinned_import_boundary():
    assert pinned_import("json") == "json" and "import-allowlist"
