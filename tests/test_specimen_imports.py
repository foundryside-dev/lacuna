def test_trust_flow_uses_loom_markers():
    import specimen.trust_flow as tf
    src = __import__("inspect").getsource(tf)
    assert "from loom_markers import" in src
    assert "wardline.decorators" not in src
