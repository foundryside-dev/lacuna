"""Spawn each .mcp.json-configured MCP server, assert it attaches + binds to the
staged Lacuna repo. Client mechanism + per-member fallbacks recorded by Phase-0 spike.

MODULE BUNDLING (ADR-note) — parser (load_server_specs/ServerSpec) + probe (_stdio_rpc/
_http_rpc transports) + classify() are co-located in this ONE module because they share a
single seam (.mcp.json → attach evidence) with no external callers beyond steps.py; a
separate ADR file is not warranted. The join census (Phase 5) and/or the transports may
be extracted into their own modules later if they grow.

BINDING EVIDENCE CONTRACT — canonical source: docs/plans/phase0-findings.md (Phase-0
spike, 2026-06-28). Task-2 implementors MUST read that file before implementing probe();
the table below is a pointer, not a reproduction.

Summary of spike refinements (supersedes any pre-spike table):

  Three unwrap shapes (not all structuredContent):
    1. content[0].text → top-level JSON key: filigree (project_root at top level).
    2. content[0].text → nested result.* key: loomweave (result.project_root; the
       text-JSON top level is {ok, result, diagnostics, stats_delta}).
    3. structuredContent.*: wardline, warpline, legis, plainweave.

  Path-vs-store (4 path members must assert BOTH):
    loomweave, filigree, legis, and plainweave return a path field that may echo
    ROOT even when the backing store is absent or unreadable. The gate MUST assert
    both the path predicate AND the store-read signal (e.g. db_present, db_initialized,
    binding_chain, initialized). wardline and warpline already return a store-read
    binding_ok boolean — no path assertion needed for those two.

  The envelope ok is call-success, never the verdict:
    All six members' binding tool returns an ok field at the envelope level. This
    signals whether the RPC call succeeded, NOT whether the member is bound to ROOT.
    Legis in particular returns structuredContent.ok = False on benign install warnings
    while being correctly bound. Read the contract field, not the envelope ok.

All 6 members self-report a server-resolved store-read fact. The tautological
cwd==ROOT static lint is NOT used — wardline and warpline now have real binding tools
(doctor and warpline_project_status_get). A member that initialises but fails its
binding-touching call classifies live-empty and the gate fails loudly naming it.

TRANSPORT BOUNDARY — the MCP wire client is two replaceable callables, _stdio_rpc(
command, args, env, *, timeout, binding=None) and _http_rpc(url, headers, *, timeout,
binding=None) — `binding` is a (tool_name, arguments) pair or None: repo-per-call members
(warpline-mcp, whose _repo_arg rejects empty args) carry {"repo": str(ROOT)}, launch/cwd-bound
members carry {}. Each completes the handshake and returns the RAW initialize +
tools/list dicts (plus the optional per-member `binding` response, which rides the same
session). They are the ONLY place the wire framing lives and are member-agnostic (raw
command/args/env or url/headers — never a ServerSpec, no str(ROOT) compare); probe()
picks the per-member binding call and interprets the contract field above, so a
transport/protocol swap (or moving to the official `mcp` SDK) is a one-call change.
scripts/characterize_mcp_attachment.py (Phase 0) reuses these SAME two transports rather
than carrying its own copy. The monkeypatch test seam stays at probe().

SECURITY: .mcp.json carries a live Filigree Bearer token (filigree headers). It is
held in-memory only to authenticate the live probe and is NEVER returned, printed, or
persisted un-redacted — use redacted_headers() / redact() for any emitted structure."""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path("/home/john/lacuna")


@dataclass(frozen=True)
class ServerSpec:
    name: str
    transport: str                      # "stdio" | "streamable-http"
    command: str | None = None
    args: tuple[str, ...] = ()
    env: dict[str, str] = field(default_factory=dict)
    url: str | None = None
    headers: dict[str, str] = field(default_factory=dict)

    def redacted_headers(self) -> dict[str, str]:
        return {k: ("Bearer <redacted>" if k.lower() == "authorization" else v)
                for k, v in self.headers.items()}


def load_server_specs(cfg_path: Path = ROOT / ".mcp.json") -> dict[str, ServerSpec]:
    raw = json.loads(Path(cfg_path).read_text())
    out: dict[str, ServerSpec] = {}
    for name, s in raw.get("mcpServers", {}).items():
        out[name] = ServerSpec(
            name=name, transport=s.get("type", "stdio"),
            command=s.get("command"), args=tuple(s.get("args", [])),
            env=dict(s.get("env", {})), url=s.get("url"),
            headers=dict(s.get("headers", {})))
    return out
