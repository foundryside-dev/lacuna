# Weft federation post-fix re-dogfood report - 2026-06-13

**Method:** one Codex session in `/home/john/lacuna`, following the 2026-06-12
dogfood method: verify the staged installs, exercise Filigree, Loomweave,
Wardline, and Legis against the live lacuna repo, prove each join with command
output, and clean up throwaway artifacts. The tree started intentionally dirty
from parent install staging; this run did not revert those changes.

## Status summary

**Overall verdict:** the four requested joins are live enough for the lacuna
post-fix dogfood, with two important agent-experience caveats.

| Join | Verdict | Evidence |
|---|---|---|
| Wardline -> Filigree work joins | PASS | `wardline decorator-coverage . --loomweave-url http://127.0.0.1:9730 --filigree-url http://127.0.0.1:8749 --format json` returned 33 rows, 33 `identity.available`, 33 `work.available`; tickets were empty because no issue was currently bound to those SEIs. |
| Loomweave -> Filigree Wardline findings enrichment | PASS | Direct Loomweave MCP `entity_issue_list` for `python:function:specimen.preview_sinks.log_export_request` returned `wardline_findings.items[0]` for `PY-WL-125`, status `open`, severity `low`, exact confidence. |
| Legis MCP/tools install surface | PASS as a launched MCP/CLI, FAIL as an attached Codex session tool | Direct `legis mcp --agent-id codex` initialized and advertised 21 tools; `doctor_get`, `policy_list`, `policy_explain`, and `override_rate_get` all responded. No `mcp__legis__*` tools were attached to this Codex session. |
| Loomweave -> Filigree issues | PASS | Temporary entity association on `lacuna-2046f5ae8a` was read back through Loomweave `entity_issue_list` with hydrated issue `{id,title,status,priority}`, then deleted; reverse lookup returned `{"associations":[]}` after cleanup. |

Would an agent reach for these first? Filigree CLI/MCP and Loomweave direct MCP
are agent-useful, Wardline scan/dossier are useful but still push the agent to
raw shell for long foreground scans, and Legis still pushes this Codex session
to CLI/direct JSON-RPC because its MCP namespace did not attach.

## Loomweave

Health:

```bash
loomweave --version
# loomweave 1.1.0-rc5

loomweave doctor --path /home/john/lacuna --format json
# ok: true; schema v10; 369 entities including 26 subsystems; 339 alive SEI bindings
# warns only that codex_cli.model is unset
```

Direct MCP launch works:

```bash
FILIGREE_API_TOKEN=<from .mcp.json> loomweave serve
# initialize -> serverInfo.version 1.1.0-rc5
# tools/list -> 46 tools
```

Wardline findings enrichment now populates:

```bash
# JSON-RPC tools/call entity_find {pattern: "log_export_request", limit: 5}
# chose python:function:specimen.preview_sinks.log_export_request

# JSON-RPC tools/call entity_issue_list
# {id: "python:function:specimen.preview_sinks.log_export_request", include_contained: true}
```

Outcome: `available: true`, `filigree_endpoint.resolved_url:
http://127.0.0.1:8749`, and `wardline_findings.items[0]` for fingerprint
`wlfp2:b235...a772`, rule `PY-WL-125`, message naming
`specimen.preview_sinks.log_export_request`, `resolution_confidence: exact`.

Issue association join also works. I added a temporary association:

```bash
curl -X POST \
  -H "Authorization: Bearer <redacted>" \
  -H "Content-Type: application/json" \
  -d '{"entity_id":"loomweave:eid:4b0ed3a633fd3a572a9e1537e590f0a0","entity_kind":"function","content_hash":"70e5b154589dce8425515829f88de1c41db979b6fbdb4b72595aa67e29b5b3bd"}' \
  http://127.0.0.1:8749/api/issue/lacuna-2046f5ae8a/entity-associations
# HTTP 201
```

Then `entity_issue_list` returned `matched[0].issue` as:

```json
{"id":"lacuna-2046f5ae8a","priority":4,"status":"planning","title":"Future"}
```

Cleanup:

```bash
curl -X DELETE \
  -H "Authorization: Bearer <redacted>" \
  "http://127.0.0.1:8749/api/issue/lacuna-2046f5ae8a/entity-associations?entity_id=loomweave:eid:4b0ed3a633fd3a572a9e1537e590f0a0"
# {"removed":true}

curl -H "Authorization: Bearer <redacted>" \
  "http://127.0.0.1:8749/api/entity-associations?entity_id=loomweave:eid:4b0ed3a633fd3a572a9e1537e590f0a0"
# {"associations":[]}
```

Remaining findings:

- `loomweave doctor` reported HTTP read API on `http://127.0.0.1:35541`, but
  `curl http://127.0.0.1:35541/health` failed to connect. The `.mcp.json`
  runtime URL `http://127.0.0.1:9730` worked for Wardline joins and taint writes.
- `entity_wardline_get` returns the specific taint/finding record, but
  `entity_wardline_list {has_findings: true}` still returned zero rows with an
  honest-empty reason. That is a list/facet bug, not a targeted lookup failure.

## Wardline

Install/extras:

```bash
wardline --version
# wardline, version 1.0.0rc4

/home/john/.local/share/uv/tools/wardline/bin/python -c \
  "import tree_sitter, tree_sitter_rust, blake3"
# all imports ok
```

Scan and scoped upload:

```bash
time wardline scan . \
  --fail-on ERROR \
  --trust-suppressions \
  --filigree-url http://127.0.0.1:8749/api/p/lacuna/weft/scan-results \
  --loomweave-url http://127.0.0.1:9730
```

Outcome:

```text
emitted 149 finding(s) to http://127.0.0.1:8749/api/p/lacuna/weft/scan-results [project 'lacuna'] - 0 created / 149 updated
wrote 215 taint fact(s) to http://127.0.0.1:9730
scanned 34 file(s); 149 finding(s) - 42 suppressed (42 baseline / 0 waiver / 0 judged), 1 active -> findings.jsonl
real 0m0.523s
```

The analyzer path and emission path both succeeded in lacuna. This differs from
the esper-lite comparison case: there was no stale scanner-extra failure here,
and the 149-finding upload is below Filigree's 1000-finding cap.

Work join:

```bash
FILIGREE_API_TOKEN=<from .mcp.json> wardline decorator-coverage . \
  --loomweave-url http://127.0.0.1:9730 \
  --filigree-url http://127.0.0.1:8749 \
  --format json
```

Outcome summary: 33 rows, 33 live identities, 33 live work blocks, no 404s.
Sample row had `identity_status: alive`, `work.available: true`,
`content_status: fresh`, and `tickets: []`.

Remaining findings:

- Long-running scanner principle: `wardline scan` is still a silent foreground
  scan with no job id, pollable status handle, or meaningful progress surface.
  It completed quickly in lacuna, but the interface still violates the job
  principle for larger repos.
- `WARDLINE_FILIGREE_URL=` did not suppress upload in this repo; the scan still
  emitted to `http://localhost:8749/api/p/lacuna/weft/scan-results`. Agents need
  an explicit local-only/no-emit switch.
- The command created default `findings.jsonl` when no `--output` was provided;
  I removed that throwaway root artifact after evidence capture.

## Filigree

Health and project state:

```bash
filigree --version
# filigree, version 3.0.0rc12

filigree mcp-status
# Status: ok
# DB initialized: True
# Schema compatible: True
# Installed schema version: 27
# Database schema version: 27
# Project dir: /home/john/lacuna/.weft/filigree
# install_context: uv_tool

filigree session-context
# READY TO WORK: P4 lacuna-2046f5ae8a [release] "Future"
# ANALYZER FINDINGS: 155 not yet bridged...
# OBSERVATIONS: 1 pending
```

Wardline upload readback:

```bash
filigree finding list --rule-id PY-WL-125 --suppression all --json
```

Outcome: one row, `finding_id: lacuna-sf-4cb261e690`, `scan_source:
wardline`, `fingerprint: wlfp2:b235...a772`, `issue_id:
lacuna-2a54dfb59d`, `issue_status: closed`, `issue_resolution: tour sentinel
cycle complete`.

Payload-cap path:

```bash
# 1001 synthetic findings, scan_source=codex-dogfood-cap-probe
curl -X POST \
  -H "Authorization: Bearer <redacted>" \
  -H "Content-Type: application/json" \
  --data-binary @/tmp/lacuna-cap-probe.json \
  http://127.0.0.1:8749/api/p/lacuna/weft/scan-results
```

Outcome:

```json
{"error":"findings must contain at most 1000 findings","code":"VALIDATION"}
```

`filigree finding list --scan-source codex-dogfood-cap-probe --no-limit --json`
returned no rows, so the live cap rejects before ingest. The error is visible
and actionable, but the Wardline side still needs chunking/job behavior for
large repos like esper-lite.

Session MCP caveat: the attached `mcp__filigree` tools in this Codex session
were pointed at `/home/john/weft/.weft/filigree`, not lacuna. For lacuna-scoped
evidence, CLI and HTTP were the reliable surfaces.

## Legis

CLI health:

```bash
legis --version
# legis 1.0.0

legis doctor --root /home/john/lacuna --format json
# ok: true
# only notable warning in parent run is resolved under MCP env:
# runtime.wardline_routing -> LEGIS_WARDLINE_CELL=surface_override

legis session-context
# legis: instructions current; skill pack current; cells config: policy/cells.toml (4 policies mapped)
```

Policy boundary check now degrades instead of crashing:

```bash
legis policy-boundary-check --root specimen --repo-root . --format json
```

Outcome: exit 1 with real findings, not a traceback:

```json
[
  {"file_path":"specimen/nesting_bomb.py","rule_id":"POLICY_BOUNDARY_FILE_TOO_COMPLEX","reason":"nesting too deep to analyze; file skipped, scan continued (per-file degrade)"},
  {"file_path":"specimen/policy_boundaries.py","line":30,"qualname":"validated_recovery","rule_id":"POLICY_BOUNDARY_TEST_FINGERPRINT_MISMATCH"},
  {"file_path":"specimen/policy_boundaries.py","line":43,"qualname":"pinned_import","rule_id":"POLICY_BOUNDARY_TEST_FINGERPRINT_MISMATCH"}
]
```

Governance gates:

```bash
legis check-override-rate
legis governance-gate
# override-rate gate: PASS_WITH_NOTICE (rate=0.000, sample=0)
```

Direct MCP launch:

```bash
LEGIS_WARDLINE_CELL=surface_override legis mcp --agent-id codex
# initialize -> {"name":"legis","version":"1.0.0"}
# tools/list -> 21 tools
```

Advertised tools included `policy_explain`, `policy_list`, `override_submit`,
`scan_route`, `git_rename_feed_get`, `filigree_closure_gate_get`,
`override_list`, `doctor_get`, `policy_boundary_check`, and `check_report`.
`doctor_get` returned `ok: true`; `override_rate_get` returned
`PASS_WITH_NOTICE`; `policy_explain` responded with a structured disabled
`structured` cell for an unknown `surface_override` policy.

Remaining finding: Legis is installed and launchable, but it was not naturally
available as `mcp__legis__*` in this Codex session. An agent following the
project instructions still has to fall back to CLI or manual JSON-RPC.

## Cross-tool

What improved since the 2026-06-12 report:

- Wardline -> Filigree no longer 404s on work joins when given the working
  Loomweave URL and Filigree base URL.
- Loomweave -> Filigree no longer 401s for Wardline finding enrichment when
  `FILIGREE_API_TOKEN` is supplied from `.mcp.json`.
- Loomweave -> Filigree issue association round trip hydrates issue details,
  including title/status/priority.
- Legis `policy-boundary-check` no longer dies with `RecursionError` on
  `nesting_bomb.py`; it returns a typed finding and continues.
- Lacuna Wardline scanner extras are present, and scoped Filigree upload works.

Remaining cross-tool friction:

- MCP attachment does not match the staged repo cleanly in this Codex session:
  Filigree MCP points at Weft, Loomweave MCP is attached to a no-index context,
  and Legis MCP is absent. Direct process launches work, but that is not the
  same as "agents naturally reach for MCP first."
- Port/config truth is still inconsistent: Loomweave doctor advertises an
  unreachable `35541` HTTP port while `.mcp.json`'s `9730` is the working
  runtime URL.
- Scanner paths still need job semantics: foreground, low-feedback scans with
  no pollable job/status handle should be treated as a product finding even
  when lacuna's small scan succeeds.
- The 1000-finding cap is now visible and actionable in Filigree, but the
  Wardline/Filigree pair still needs a chunking or async ingest story for
  large external repos.

## Cleanup

- Removed the temporary SEI association from `lacuna-2046f5ae8a`; reverse lookup
  returned `{"associations":[]}`.
- Removed root `findings.jsonl` generated by the explicit Wardline scan.
- Removed `/tmp/lacuna-*` probe payloads and response files.
- Did not create, claim, close, or delete any Filigree issues.
- Left the existing observation `lacuna-obs-8aa96160f2` untouched.
