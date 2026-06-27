import json
from pathlib import Path
from tour.mcp_attachment import load_server_specs, ServerSpec


def test_load_server_specs_parses_stdio_and_http_and_redacts(tmp_path: Path):
    cfg = tmp_path / ".mcp.json"
    cfg.write_text(json.dumps({"mcpServers": {
        "loomweave": {"type": "stdio", "command": "/x/loomweave", "args": ["serve"], "env": {}},
        "legis": {"type": "stdio", "command": "/x/legis",
                  "args": ["mcp", "--agent-id", "codex"], "env": {"LEGIS_WARDLINE_CELL": "surface_override"}},
        "filigree": {"type": "streamable-http", "url": "http://h/mcp/?project=lacuna",
                     "headers": {"Authorization": "Bearer SECRET-TOKEN"}},
    }}))
    specs = load_server_specs(cfg)
    assert specs["loomweave"].transport == "stdio"
    assert specs["loomweave"].command == "/x/loomweave" and specs["loomweave"].args == ("serve",)
    assert specs["legis"].env == {"LEGIS_WARDLINE_CELL": "surface_override"}
    assert specs["filigree"].transport == "streamable-http"
    assert specs["filigree"].url == "http://h/mcp/?project=lacuna"
    assert specs["filigree"].redacted_headers() == {"Authorization": "Bearer <redacted>"}
    # the raw token is never exposed by the redacting accessor
    assert "SECRET-TOKEN" not in json.dumps(specs["filigree"].redacted_headers())


def test_serverspec_repr_does_not_leak_token():
    s = ServerSpec(name="filigree", transport="streamable-http",
                   url="http://h/mcp/", headers={"Authorization": "Bearer SECRET-TOKEN-XYZ"})
    assert "SECRET-TOKEN-XYZ" not in repr(s)
    assert "SECRET-TOKEN-XYZ" not in str(s)
    # the redacting accessor is still the way to surface headers safely
    assert s.redacted_headers() == {"Authorization": "Bearer <redacted>"}
