def test_trust_flow_uses_weft_markers():
    import specimen.trust_flow as tf
    src = __import__("inspect").getsource(tf)
    assert "from weft_markers import" in src
    assert "wardline.decorators" not in src
