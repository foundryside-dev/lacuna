from tour.docs_gen import render_flaw_page
from tour.manifest import Lacuna


def test_flaw_page_has_location_and_explanation():
    lac = Lacuna("wl-trust-violation", "specimen/trust_flow.py", "unsafe_account_key",
                 "trust-boundary", ("wardline",), "untrusted reaches trusted",
                 "wardline", "PY-WL-101")
    md = render_flaw_page(lac)
    assert "specimen/trust_flow.py" in md
    assert "unsafe_account_key" in md
    assert "PY-WL-101" in md
    assert "untrusted reaches trusted" in md
