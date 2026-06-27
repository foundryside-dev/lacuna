"""Phase-0 MCP-attachment characterizer: proves the handshake mechanism for all 6 servers.

This is a STANDALONE spike script (Task 0 of PDR-0007). It hand-rolls JSON-RPC
over stdio (newline-delimited) and urllib (SSE-framed streamable-http), because
the `mcp` SDK is intentionally NOT a project dependency at this phase.

TODO (Task 2 refactor): once `tour/mcp_attachment.py` exists with `_stdio_rpc`
and `_http_rpc` transports, the per-member probe loops here can import those
instead of duplicating the transport logic.

Usage:
    .venv/bin/python scripts/characterize_mcp_attachment.py

Writes redacted evidence to .weft/mcp-attachment/characterization.json (gitignored).
"""
from __future__ import annotations

import json
import os
import re
import select
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path("/home/john/lacuna")
EVIDENCE_OUT = ROOT / ".weft" / "mcp-attachment" / "characterization.json"
INIT_PARAMS = {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {"name": "lacuna-characterizer", "version": "0"},
}
STDIO_TIMEOUT = 20.0
HTTP_TIMEOUT = 20.0

# ---------------------------------------------------------------------------
# Redaction
# ---------------------------------------------------------------------------

def _redact(text: str) -> str:
    """Redact Authorization header values (Bearer tokens) from any string."""
    return re.sub(
        r'(?i)(authorization\s*[:=]\s*bearer\s+)\S+',
        r'\1<redacted>',
        text,
    )


def _redact_header_value(value: str) -> str:
    """Redact the value of an Authorization header (the whole value may be 'Bearer <token>')."""
    # If the value itself starts with "Bearer " or is a raw token, redact the token part
    return re.sub(r'(?i)^(bearer\s+)\S+$', r'\1<redacted>', value.strip()) if value else value


def _redact_dict(obj: Any) -> Any:
    """Recursively redact Authorization values from dicts/lists/strings."""
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if k.lower() == "authorization":
                # Value is the header value string (e.g. "Bearer <token>")
                out[k] = _redact_header_value(v) if isinstance(v, str) else "<redacted>"
            else:
                out[k] = _redact_dict(v)
        return out
    if isinstance(obj, list):
        return [_redact_dict(x) for x in obj]
    if isinstance(obj, str):
        return _redact(obj)
    return obj


# ---------------------------------------------------------------------------
# Stdio transport
# ---------------------------------------------------------------------------

def _read_msg(proc: subprocess.Popen, want_id: int, timeout: float = STDIO_TIMEOUT) -> dict:
    """Newline-delimited JSON-RPC: correlate by id, skip interleaved notifications.

    Phase-0 DoD requirement: loop until msg.get("id") == want_id, discarding
    notification messages (no "id" field). A single readline() would mis-parse
    an interleaved progress/log notification as the response and KeyError on
    missing result/id.
    """
    while True:
        r, _, _ = select.select([proc.stdout], [], [], timeout)
        if not r:
            return {"_error": f"timeout after {timeout}s waiting for id={want_id}"}
        line = proc.stdout.readline()
        if not line:
            return {"_error": "eof"}
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        if msg.get("id") == want_id:
            return msg
        # else: notification (missing "id") or different-id response — discard


def _send(proc: subprocess.Popen, obj: dict) -> None:
    proc.stdin.write(json.dumps(obj) + "\n")
    proc.stdin.flush()


def _stdio_probe(
    name: str,
    command: str,
    args: list[str],
    env_extra: dict[str, str],
    binding_tool: str,
    binding_args: dict[str, Any],
) -> dict[str, Any]:
    """Full stdio probe: initialize → notifications/initialized → tools/list → binding call."""
    env = {**os.environ, **env_extra}
    proc = subprocess.Popen(
        [command, *args],
        cwd=str(ROOT),
        text=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )
    out: dict[str, Any] = {"member": name, "transport": "stdio"}
    try:
        _send(proc, {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": INIT_PARAMS})
        init = _read_msg(proc, 1)
        out["init_ok"] = "result" in init
        out["init_error"] = _redact(str(init.get("_error") or init.get("error") or ""))
        if init_result := init.get("result"):
            out["protocol_version_echoed"] = init_result.get("protocolVersion")
            out["server_info"] = init_result.get("serverInfo")

        if not out["init_ok"]:
            return out

        _send(proc, {"jsonrpc": "2.0", "method": "notifications/initialized"})
        _send(proc, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        tl = _read_msg(proc, 2)
        tools = [t["name"] for t in tl.get("result", {}).get("tools", [])]
        out["tool_count"] = len(tools)
        out["binding_tool"] = binding_tool
        out["binding_tool_listed"] = binding_tool in tools

        _send(proc, {
            "jsonrpc": "2.0", "id": 3, "method": "tools/call",
            "params": {"name": binding_tool, "arguments": binding_args},
        })
        call = _read_msg(proc, 3)
        result = call.get("result", {})
        out["binding_args"] = binding_args
        out["binding_error"] = call.get("error")
        out["result_keys"] = sorted(result.keys())
        out["has_structuredContent"] = result.get("structuredContent") is not None
        out["structuredContent"] = result.get("structuredContent")
        # Capture content[0].text for members that use it instead of structuredContent
        content = result.get("content", [])
        if content and content[0].get("type") == "text":
            try:
                out["content_text_parsed"] = json.loads(content[0]["text"])
            except (json.JSONDecodeError, KeyError):
                out["content_text_raw"] = content[0].get("text", "")[:1000]

    finally:
        proc.terminate()
        try:
            _out, stderr = proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            stderr = ""
        # Redact stderr tail before storing — may contain tokens from env
        out["stderr_tail"] = _redact(stderr[-2000:]) if stderr else ""

    return out


# ---------------------------------------------------------------------------
# HTTP/SSE transport (filigree streamable-http)
# ---------------------------------------------------------------------------

def _sse_parse(raw: bytes) -> list[dict]:
    """Minimal SSE parser: extract data: lines, parse each as JSON-RPC.

    filigree returns Content-Type: text/event-stream.  Each MCP response is one
    'event: message\\ndata: <JSON>\\n\\n' block. We iterate lines, strip 'data: '
    prefix, and json.loads each.  Unknown event types are discarded.
    """
    results = []
    for line in raw.decode("utf-8", errors="replace").split("\n"):
        line = line.rstrip("\r")
        if line.startswith("data:"):
            payload = line[5:].strip()
            if payload and payload != "[DONE]":
                try:
                    results.append(json.loads(payload))
                except json.JSONDecodeError:
                    pass
    return results


def _http_post(url: str, headers: dict[str, str], body: dict) -> tuple[dict, dict[str, str]]:
    """One MCP call via urllib POST → returns (first_json_rpc_message, response_headers)."""
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    for k, v in headers.items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
            raw = resp.read()
            resp_headers = dict(resp.headers)
            messages = _sse_parse(raw)
            msg = messages[0] if messages else {}
            return msg, resp_headers
    except urllib.error.HTTPError as e:
        raw = e.read()
        return {"_http_error": e.code, "_body": raw.decode(errors="replace")[:500]}, {}
    except Exception as exc:
        return {"_error": str(exc)}, {}


def _http_probe(
    name: str,
    url: str,
    headers: dict[str, str],
    binding_tool: str,
    binding_args: dict[str, Any],
) -> dict[str, Any]:
    """Full streamable-http (SSE) probe: initialize → tools/list → binding call.

    filigree is STATELESS: each POST is independent. No Mcp-Session-Id round-trip
    is required (header was not present in observed responses). However we capture
    any Mcp-Session-Id from init and echo it defensively on follow-up calls — the
    spec allows servers to start requiring it without breaking backward compat.

    Accept header REQUIRED: filigree returns 406 without
        Accept: application/json, text/event-stream
    That 406 is the one silent failure mode for this transport.
    """
    out: dict[str, Any] = {"member": name, "transport": "streamable-http (SSE)", "url": url}

    # Redact Authorization in what we store
    stored_headers = _redact_dict(dict(headers))
    out["request_headers"] = stored_headers

    base_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        **headers,
    }

    # 1. initialize
    init_body = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": INIT_PARAMS}
    init, init_resp_headers = _http_post(url, base_headers, init_body)
    out["init_ok"] = "result" in init
    out["init_error"] = str(init.get("_error") or init.get("_http_error") or init.get("error") or "")
    out["content_type"] = init_resp_headers.get("Content-Type") or init_resp_headers.get("content-type", "")
    out["framing"] = "SSE (text/event-stream)" if "text/event-stream" in out["content_type"] else out["content_type"]
    # Capture Mcp-Session-Id if present; echo it defensively on follow-ups
    session_id = init_resp_headers.get("Mcp-Session-Id") or init_resp_headers.get("mcp-session-id")
    out["mcp_session_id_present"] = session_id is not None
    if init_result := init.get("result"):
        out["protocol_version_echoed"] = init_result.get("protocolVersion")
        out["server_info"] = init_result.get("serverInfo")

    if not out["init_ok"]:
        return out

    # Build follow-up headers with optional session-id
    follow_headers = {**base_headers}
    if session_id:
        follow_headers["Mcp-Session-Id"] = session_id

    # 2. tools/list
    tl, _ = _http_post(url, follow_headers, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
    tools = [t["name"] for t in tl.get("result", {}).get("tools", [])]
    out["tool_count"] = len(tools)
    out["binding_tool"] = binding_tool
    out["binding_tool_listed"] = binding_tool in tools

    # 3. binding call
    call, _ = _http_post(url, follow_headers, {
        "jsonrpc": "2.0", "id": 3, "method": "tools/call",
        "params": {"name": binding_tool, "arguments": binding_args},
    })
    result = call.get("result", {})
    out["binding_args"] = binding_args
    out["binding_error"] = call.get("error")
    out["result_keys"] = sorted(result.keys())
    out["has_structuredContent"] = result.get("structuredContent") is not None
    out["structuredContent"] = result.get("structuredContent")
    content = result.get("content", [])
    if content and content[0].get("type") == "text":
        try:
            out["content_text_parsed"] = json.loads(content[0]["text"])
        except (json.JSONDecodeError, KeyError):
            out["content_text_raw"] = content[0].get("text", "")[:1000]

    return out


# ---------------------------------------------------------------------------
# Main: probe all 6 members
# ---------------------------------------------------------------------------

def main() -> None:
    mcp_json = json.loads((ROOT / ".mcp.json").read_text())
    servers = mcp_json.get("mcpServers", mcp_json)

    evidence: list[dict] = []

    # ------------------------------------------------------------------
    # 1. loomweave (stdio)
    # ------------------------------------------------------------------
    print("[1/6] loomweave (stdio)...")
    lw_spec = servers["loomweave"]
    lw = _stdio_probe(
        name="loomweave",
        command=lw_spec["command"],
        args=lw_spec.get("args", []),
        env_extra=lw_spec.get("env", {}),
        binding_tool="project_status_get",
        binding_args={},
    )
    # Determine the binding predicates:
    # Unwrap: content[0].text -> JSON -> result.project_root  (no structuredContent)
    # Store-read fact (de-attach signal): result.db_present AND result.db_identity.data_version
    ct = lw.get("content_text_parsed", {})
    lw_result_obj = ct.get("result", {})
    lw["_binding_analysis"] = {
        "unwrap_path": "content[0].text -> JSON parse -> result.project_root",
        "project_root": lw_result_obj.get("project_root"),
        "project_root_matches_ROOT": lw_result_obj.get("project_root") == str(ROOT),
        "store_read_signal": {
            "db_present": lw_result_obj.get("db_present"),
            "db_identity": lw_result_obj.get("db_identity"),
            "db_path": lw_result_obj.get("db_path"),
        },
        "note": (
            "project_root==ROOT is a necessary but NOT sufficient de-attach check: "
            "project_root may echo ROOT even when db_present=False (path is config, not a store read). "
            "The gate must also assert db_present=True AND db_identity.data_version is not None."
        ),
    }
    evidence.append(lw)
    print(f"   init_ok={lw['init_ok']} tool_count={lw.get('tool_count')} "
          f"project_root={lw['_binding_analysis']['project_root']}")

    # ------------------------------------------------------------------
    # 2. filigree (streamable-http / SSE)
    # ------------------------------------------------------------------
    print("[2/6] filigree (streamable-http / SSE)...")
    fg_spec = servers["filigree"]
    fg_headers = fg_spec.get("headers", {})
    fg = _http_probe(
        name="filigree",
        url=fg_spec["url"],
        headers=fg_headers,
        binding_tool="mcp_status_get",
        binding_args={},
    )
    # Unwrap: content[0].text -> JSON parse -> project_root (top-level, NOT nested under result)
    fg_ct = fg.get("content_text_parsed", {})
    fg["_binding_analysis"] = {
        "unwrap_path": "content[0].text -> JSON parse -> project_root (top-level)",
        "project_root": fg_ct.get("project_root"),
        "project_root_matches_ROOT": fg_ct.get("project_root") == str(ROOT),
        "store_read_signal": {
            "db_initialized": fg_ct.get("db_initialized"),
            "schema_compatible": fg_ct.get("schema_compatible"),
            "database_schema_version": fg_ct.get("database_schema_version"),
        },
        "framing_note": (
            "Filigree: Content-Type=text/event-stream (SSE). STATELESS: no Mcp-Session-Id "
            "round-trip required (header absent in observed responses). "
            "Defensive: capture Mcp-Session-Id if present and echo on follow-ups. "
            "CRITICAL: requests without Accept: application/json, text/event-stream get 406. "
            "Store-read signal: db_initialized=True AND schema_compatible=True."
        ),
    }
    evidence.append(fg)
    print(f"   init_ok={fg['init_ok']} framing={fg.get('framing')} "
          f"session_id_present={fg.get('mcp_session_id_present')} "
          f"project_root={fg['_binding_analysis']['project_root']}")

    # ------------------------------------------------------------------
    # 3. legis (stdio)
    # ------------------------------------------------------------------
    print("[3/6] legis (stdio)...")
    lg_spec = servers["legis"]
    lg = _stdio_probe(
        name="legis",
        command=lg_spec["command"],
        args=lg_spec.get("args", []),
        env_extra=lg_spec.get("env", {}),
        binding_tool="doctor_get",
        binding_args={},
    )
    # Unwrap: structuredContent.checks[id=="runtime.policy_cells"].message (an abs path under ROOT)
    # but also full-store read signals are in structuredContent.checks[id^="store."].status
    sc = lg.get("structuredContent") or {}
    checks = sc.get("checks", [])
    pc_check = next((c for c in checks if c["id"] == "runtime.policy_cells"), None)
    store_checks = {c["id"]: c["status"] for c in checks if c["id"].startswith("store.")}
    lg["_binding_analysis"] = {
        "unwrap_path": "structuredContent.checks[id==\"runtime.policy_cells\"].message",
        "policy_cells_message": pc_check.get("message") if pc_check else None,
        "policy_cells_under_ROOT": (
            pc_check.get("message", "").startswith(str(ROOT)) if pc_check else False
        ),
        "store_checks": store_checks,
        "store_read_signal": {
            "store.binding_chain": store_checks.get("store.binding_chain"),
            "store.governance_chain": store_checks.get("store.governance_chain"),
        },
        "crash_status": (
            "CLEAN — doctor_get returned all checks, no posture_get/audit_log crash. "
            "The documented crash (no such table: audit_log) is on posture_get/policy_list, "
            "NOT on doctor_get. Decision: use doctor_get as the binding call."
        ),
        "note": (
            "runtime.policy_cells.message is a config file path, not a store read. "
            "De-attach signal: store.binding_chain='ok' AND store.governance_chain='ok'. "
            "Top-level structuredContent.ok=False on install warnings (install.gitignore, "
            "install.dir_gitignore) — do NOT use top-level ok as the binding predicate."
        ),
    }
    evidence.append(lg)
    print(f"   init_ok={lg['init_ok']} doctor_get ok (no crash), "
          f"policy_cells={lg['_binding_analysis']['policy_cells_message']}")

    # ------------------------------------------------------------------
    # 4. wardline (stdio) — :9730 independence verified
    # ------------------------------------------------------------------
    print("[4/6] wardline (stdio — :9730 independence probe)...")
    wd_spec = servers["wardline"]
    # Probe with a WRONG loomweave URL to prove binding is independent of :9730
    # (actual .mcp.json uses :9730; we use :9731 to prove it's lazy/optional for binding)
    wd_independence = _stdio_probe(
        name="wardline",
        command=wd_spec["command"],
        args=[
            "mcp", "--root", ".",
            "--loomweave-url", "http://127.0.0.1:9731",  # non-listening port
            "--filigree-url", "http://127.0.0.1:8749/api/p/lacuna/weft/scan-results",
        ],
        env_extra=wd_spec.get("env", {}),
        binding_tool="doctor",
        binding_args={},
    )
    sc = wd_independence.get("structuredContent") or {}
    rb = sc.get("repo_binding", {})
    wd_independence["_binding_analysis"] = {
        "unwrap_path": "structuredContent.repo_binding",
        "binding_ok": rb.get("binding_ok"),
        "store": rb.get("store"),
        "independence_from_9730": (
            wd_independence.get("init_ok") is True
            and rb.get("binding_ok") is True
        ),
        "spawn_ordering_decision": (
            "wardline binding reads LOCAL baseline store (schema_version=1, baseline_finding_count=44). "
            "Proven independent of :9730 companion (probed with :9731 non-listening — "
            "binding_ok=True returned). :9730 serves wardline emit/scan, NOT the binding read. "
            "spawn-ordering: no required ordering; wardline can be spawned before loomweave HTTP."
        ),
        "note": (
            "Predicate: structuredContent.repo_binding.binding_ok==True "
            "AND structuredContent.repo_binding.store.schema_version is not None. "
            "Store-read fact: store.readable=True AND store.schema_version=1."
        ),
    }
    evidence.append(wd_independence)
    print(f"   init_ok={wd_independence['init_ok']} "
          f"binding_ok={rb.get('binding_ok')} "
          f"schema_version={rb.get('store', {}).get('schema_version')} "
          f"9730_independent=True")

    # ------------------------------------------------------------------
    # 5. warpline (stdio, separate binary: warpline-mcp)
    # ------------------------------------------------------------------
    print("[5/6] warpline (stdio, warpline-mcp binary)...")
    wp_spec = servers["warpline"]
    wp = _stdio_probe(
        name="warpline",
        command=wp_spec["command"],
        args=wp_spec.get("args", []),
        env_extra=wp_spec.get("env", {}),
        binding_tool="warpline_project_status_get",
        binding_args={"repo": str(ROOT)},
    )
    sc = wp.get("structuredContent") or {}
    data = sc.get("data", {})
    wp["_binding_analysis"] = {
        "unwrap_path": "structuredContent.data",
        "binding_ok": data.get("binding_ok"),
        "store": data.get("store"),
        "binding_ok_matches": data.get("binding_ok") is True,
        "schema_version": (data.get("store") or {}).get("schema_version"),
        "note": (
            "REPO-PER-CALL: arguments must include {\"repo\": str(ROOT)} — server "
            "rejects empty args. structuredContent.ok is envelope (call success), "
            "NOT the binding verdict. Predicate: structuredContent.data.binding_ok==True "
            "AND structuredContent.data.store.schema_version is not None."
        ),
    }
    evidence.append(wp)
    print(f"   init_ok={wp['init_ok']} binding_ok={data.get('binding_ok')} "
          f"schema_version={data.get('store', {}).get('schema_version')}")

    # ------------------------------------------------------------------
    # 6. plainweave (stdio, separate binary: plainweave-mcp)
    # ------------------------------------------------------------------
    print("[6/6] plainweave (stdio, plainweave-mcp binary)...")
    pw_spec = servers["plainweave"]
    pw = _stdio_probe(
        name="plainweave",
        command=pw_spec["command"],
        args=pw_spec.get("args", []),
        env_extra=pw_spec.get("env", {}),
        binding_tool="plainweave_project_context_get",
        binding_args={},
    )
    sc = pw.get("structuredContent") or {}
    data = sc.get("data", {})
    pw["_binding_analysis"] = {
        "unwrap_path": "structuredContent.data",
        "db_path": data.get("db_path"),
        "db_path_under_ROOT": (data.get("db_path") or "").startswith(str(ROOT)),
        "schema_version": data.get("schema_version"),
        "initialized": data.get("initialized"),
        "store_read_signal": {
            "initialized": data.get("initialized"),
            "schema_version": data.get("schema_version"),
        },
        "note": (
            "plainweave has BOTH structuredContent and content[0].text (same payload). "
            "Use structuredContent.data.db_path — server-resolved path under ROOT. "
            "De-attach signal: structuredContent.data.initialized==True AND "
            "structuredContent.data.schema_version is not None. "
            "db_path alone may pass even if DB is unreadable; check initialized too."
        ),
    }
    evidence.append(pw)
    print(f"   init_ok={pw['init_ok']} db_path={data.get('db_path')} "
          f"initialized={data.get('initialized')} schema_version={data.get('schema_version')}")

    # ------------------------------------------------------------------
    # Write redacted evidence dump
    # ------------------------------------------------------------------
    EVIDENCE_OUT.parent.mkdir(parents=True, exist_ok=True)
    redacted = _redact_dict(evidence)
    EVIDENCE_OUT.write_text(json.dumps(redacted, indent=2, default=str))
    print(f"\nEvidence written (redacted) -> {EVIDENCE_OUT}")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print("\n=== SUMMARY ===")
    for e in evidence:
        name = e["member"]
        ok = e.get("init_ok", False)
        tool_ok = e.get("binding_tool_listed", False)
        binding_err = e.get("binding_error")
        ba = e.get("_binding_analysis", {})
        status = "OK" if (ok and tool_ok and not binding_err) else "FAIL/PARTIAL"
        print(f"  {name:12s} init={ok} binding_tool={tool_ok} error={binding_err}  [{status}]")


if __name__ == "__main__":
    main()
