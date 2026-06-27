# mcp-attach-warpline

_Generated from `tour/lacunae.toml`. Do not edit by hand._

- **Location:** `.mcp.json` → `warpline`
- **Category:** mcp-attachment
- **Demonstrates:** `warpline`
- **Expected finding:** `warpline` / `mcp-attach`

## Why it's here

NOT A FLAW — a federation seam-integrity demo. warpline's .mcp.json-configured MCP server (`warpline-mcp`) spawns, completes the MCP initialize handshake, and binds to the staged lacuna repo via a server-side store read — reachable MCP-first, no CLI fallback. A silent de-attach (a stale build that starts clean but cannot read its repo-scoped store — the 2026-06-26 loomweave incident class) makes this lacuna go dark and trips make verify.

> This is an intentional, permanent demonstration fixture. Removing or "fixing" it fails `make verify`.
