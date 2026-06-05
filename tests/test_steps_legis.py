import re
import shutil

import pytest

from tour import steps


def _tools_present() -> bool:
    return all(
        (steps.BIN / t).exists() or shutil.which(t)
        for t in ("legis", "wardline")
    )


@pytest.mark.skipif(not _tools_present(), reason="legis/wardline not installed")
def test_legis_govern_runs_the_live_handshake_and_reports_a_count():
    r = steps.legis_govern()
    assert r.name == "legis govern"
    assert r.ok is True
    # Deterministic governance outcome in the LOCKED detail.
    assert "→ surface_override" in r.detail
    assert "governed" in r.detail
    # Guard against silent regression to a hollow demo: the specimen carries a
    # genuine active (un-baselined WARN) defect, so legis must govern >= 1.
    m = re.search(r"governed (\d+) active defects", r.detail)
    assert m and int(m.group(1)) >= 1
    # Signed/unsigned status rides the non-rendered note, not the detail.
    assert ("verified" in r.note) or ("unverified" in r.note)


def test_legis_govern_never_raises_when_tools_missing(monkeypatch):
    # Point the binaries at a non-existent dir so production/probe fails, and assert
    # the step degrades to ok=False instead of raising (tour contract).
    monkeypatch.setattr(steps, "BIN", steps.Path("/nonexistent/bin"))
    monkeypatch.setattr(steps.shutil, "which", lambda *_a, **_k: None)
    r = steps.legis_govern()
    assert r.ok is False
    assert r.name == "legis govern"


def test_legis_govern_never_raises_on_a_live_path_error(monkeypatch):
    # tools resolve, but a live call inside the try raises -> must degrade, not raise.
    monkeypatch.setattr(steps, "_tool", lambda name: f"/home/john/.local/bin/{name}")
    def _boom():
        raise OSError("disk gone")
    monkeypatch.setattr(steps, "_artifact_secret", _boom)
    r = steps.legis_govern()
    assert r.ok is False
    assert r.name == "legis govern"


def test_legis_govern_never_raises_on_non_object_response(monkeypatch):
    # Drive the handshake to the POST with all live I/O stubbed, then have legis
    # return a JSON ARRAY (`[]`). `.get("routed", ...)` on a list raises
    # AttributeError, which must be caught -> ok=False, not a raise.
    monkeypatch.setattr(steps, "_tool", lambda name: f"/home/john/.local/bin/{name}")
    monkeypatch.setattr(steps, "_artifact_secret", lambda: None)

    def _fake_produce(_wardline, out, _secret):
        out.write_text('{"findings": []}')  # valid object, no signature
        return True, 0

    monkeypatch.setattr(steps, "_produce_legis_artifact", _fake_produce)
    monkeypatch.setattr(steps, "_free_port", lambda: 65000)
    monkeypatch.setattr(steps, "_wait_health", lambda *_a, **_k: True)

    class _FakeProc:
        def terminate(self): ...
        def wait(self, timeout=None): ...
        def kill(self): ...

    monkeypatch.setattr(steps.subprocess, "Popen", lambda *_a, **_k: _FakeProc())

    class _FakeResp:
        def __enter__(self): return self
        def __exit__(self, *_a): return False
        def read(self): return b"[]"  # a JSON array, not an object

    monkeypatch.setattr(steps.urllib.request, "urlopen", lambda *_a, **_k: _FakeResp())

    r = steps.legis_govern()
    assert r.ok is False
    assert r.name == "legis govern"
