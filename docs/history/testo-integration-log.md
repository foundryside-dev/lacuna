> **Historical.** This is the original `testo` integration-sandbox log, retained
> for provenance. Its `testo-…` issue IDs and `clarion:eid:…` SEIs predate the
> re-key to **Lacuna** and are no longer live. See `README.md` for the product.

# Loom Integration Log

## 2026-06-04

- Started integration exercise across Filigree, Clarion, and Wardline.
- Confirmed `sampleapp/` initially had no Wardline trust decorators.
- Installed Wardline editable into `.venv` with `uv pip install --python .venv/bin/python -e /home/john/wardline` so decorator imports work at runtime.
- Added `sampleapp/trust_flow.py` with:
  - `@external_boundary` on `read_raw_username`
  - `@trust_boundary(to_level="ASSURED")` on `validate_username`
  - `@trusted(level="ASSURED")` on `build_account_key`
  - `safe_account_key` as the validated path
  - `unsafe_account_key` as an intentional trust violation fixture
- Verified runtime decorator imports in `.venv`:
  - `safe_account_key(["Grace_Hopper"])` returned `user:grace_hopper`
  - `unsafe_account_key(["RAW"])` returned `RAW`
  - existing CLI still ran: `.venv/bin/python -m sampleapp.cli register grace "Grace Hopper"`
- Ran `wardline findings . --where '{"rule_id":"PY-WL-101"}'`.
  - Found active `PY-WL-101` at `sampleapp/trust_flow.py:41`
  - Fingerprint: `229469b359596f6dbb5832ac3a65c6b0992a5835883164a68180fb75b7ebf10a`
  - Qualname: `sampleapp.trust_flow.unsafe_account_key`
- Ran `wardline assure . --format json`.
  - `boundaries_total=4`, `proven=3`, `defect_total=1`, `coverage_pct=100.0`
- Re-ran `clarion analyze /home/john/testo`.
  - Fresh index reported by `clarion doctor`: 85 entities, 1 subsystem, 1 finding.
  - New unsafe function SEI: `clarion:eid:6397281cdde1537787cef093a1f10be0`
- Ran integrated `wardline scan . --fail-on ERROR`.
  - Expected exit code: `1`
  - Emitted 34 Wardline findings to Filigree (`3 created / 31 updated`)
  - Wrote 54 taint facts to Clarion
- Ran `mcp__wardline.explain_taint` for the `PY-WL-101` fingerprint.
  - Chain resolved: `unsafe_account_key` -> `read_raw_username`
  - Source boundary: `sampleapp.trust_flow.read_raw_username`
- Ran `wardline dossier sampleapp.trust_flow.unsafe_account_key . --clarion-url http://127.0.0.1:9111 --filigree-url http://127.0.0.1:8749/api/loom/scan-results`.
  - Dossier resolved SEI, decorators, active finding, and Clarion call graph.
  - Observed wording inconsistency: `work.available=true` with empty tickets, but synthesis says `open-work unavailable (no Filigree)`.
- Promoted the Wardline finding to Filigree with `mcp__wardline.file_finding`.
  - Created bug: `testo-6c94c12a81`
  - Linked finding: `testo-sf-54ecaed120`
- Added Filigree entity associations for the promoted bug:
  - SEI binding: `clarion:eid:6397281cdde1537787cef093a1f10be0`
  - Locator compatibility binding: `python:function:sampleapp.trust_flow.unsafe_account_key`
- Verified Filigree file/finding surfaces:
  - `sampleapp/trust_flow.py` file id: `testo-f-c111d2de0c`
  - File association `bug_in` points to `testo-6c94c12a81`
  - Timeline includes finding creation, finding update, and association creation
- Verified Clarion surfaces:
  - Orientation pack sees `unsafe_account_key -> read_raw_username`
  - `entity_wardline_get` returns Wardline taint JSON for `unsafe_account_key`
  - Fresh Clarion MCP subprocess sees Filigree issue `testo-6c94c12a81` through the compatibility locator association
- Verified Clarion SARIF import path:
  - `wardline scan . --format sarif --output /tmp/testo-wardline.sarif`
  - `clarion sarif import /tmp/testo-wardline.sarif --scan-source wardline-sarif --path /home/john/testo`
  - Imported 2 SARIF findings into Filigree under `scan_source=wardline-sarif`
- Ran `clarion doctor --path /home/john/testo --fix`.
  - Repaired `.mcp.json` Clarion entry to the expected local form.

### Open seams found

- Clarion issue lookup still needs locator compatibility bindings until the SEI-primary fix lands.
- Clarion `wardline_findings` enrichment returns unavailable with Filigree `400`:
  `path_prefix must be project-relative`.
- Wardline dossier synthesis says `open-work unavailable (no Filigree)` even when `work.available=true` and tickets are simply empty.
- Wardline records an informational `WLN-ENGINE-UNKNOWN-IMPORT` for `wardline.decorators`; decorators still work and are detected, but import resolution reports the external package unresolved.
- Clarion SARIF import works, but imported SARIF findings have empty fingerprints, so native Wardline emission is the better lifecycle path for promotion/dedup.
- Clarion HTTP is configured unauthenticated on loopback for this sandbox. It is intentionally local-only, but shared-host use should add HMAC or bearer auth.
