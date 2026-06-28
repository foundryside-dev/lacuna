# Live cross-member dogfood + merge-gate validation — 2026-06-28

**Run from:** a session rooted in `/home/john/lacuna` (member MCP servers resolve
correctly; no hub-dispatch misrouting).
**Posture:** read-only on the tracked tree. Nothing committed, pushed, or merged.
The two fill branches stayed checked out in their repos; no member `main` was
modified.

**Method note (load-bearing):** the session's standing MCP servers were spawned
at session start from the *pre-fill* builds, so Part 2 was validated by driving
**freshly-installed feature-branch binaries as controlled subprocesses** (reusing
`tour/mcp_attachment.py:_stdio_rpc`), toggling each sibling on/off via the
consumer's real config/env seam. This is the only way to exercise the fills —
e.g. the running `legis` MCP is v1.3.0 main and has no `plainweave_preflight_get`
at all. Feature-presence was asserted by **behaviour**, not version string (both
fill branches keep their parent's version string — the stale-build trap).

---

## 1. Installed-version table (versions under test)

| Member | Version string | Source ref installed | Notes |
|--------|---------------|----------------------|-------|
| **loomweave** | 1.3.1 | `feat/warpline-churn-consumer` @ `6a4f567` | **fill under test (2A)**; installed via `#subdirectory=crates/loomweave-cli` (repo root is a Cargo workspace — bare `git+file://…@branch` fails `not a Python project`) |
| **legis** | 1.3.0 | `feat/plainweave-preflight-consumer` @ `cee8526` | **fill under test (2B)** |
| **filigree** | 3.1.0 | `main` | latest main |
| **wardline** | 1.0.7 | `release/consolidation-2026-06-26` @ `a1f121f1`, extras `[scanner,rust]` | **NOT main** — see Defect D2; brief said "latest main" but main lacks `doctor.repo_binding` |
| **warpline** | 1.2.0 | `release/1.2.0` @ `def6d43` | **NOT main** — see Defect D1; brief said "latest main" but main lacks `warpline_project_status_get` |
| **plainweave** | 1.0.0 | PyPI | per brief (local main wheel is broken — `weft-5b26c6129d`) |

`make setup` ran clean (posture floor `chill`, signed GENESIS). All six members
install and the four read-relevant members (loomweave, legis, filigree,
plainweave) attach **live-bound**. The wardline/warpline rows diverge from the
brief's "latest main" instruction *deliberately* — see Part 4.

---

## 2. Part 1 — standard full dogfood (`make verify`, the north-star)

`make verify` drives 18 legs over the live members + the 6-member MCP-attachment
gate + a narrative-lockstep check. Result is reported **per leg** (not by exit
code), because `run_verify()` also fails on narrative drift, which must not be
conflated with a join failure.

### 2.1 The 4 federation joins — all GREEN

| Join | Leg(s) | Status |
|------|--------|--------|
| **J1 Wardline→Filigree emit** | `wardline scan` + `filigree list` | **PASS** — Python scan emits findings to filigree; rust scan emits 4 findings (`0 created / 4 updated`) |
| **J2 Loomweave SEI keying** | `loomweave findings` / `rust archaeology` | **PASS** |
| **J3 Warpline change-impact** | `warpline change impact` | **PASS** (advisory enrich) |
| **J4 Plainweave intent** | `plainweave intent` | **PASS** |

### 2.2 6-member MCP-attachment gate

With the harness-expected builds (release wardline/warpline) **all 6 attach
live-bound**: `filigree, legis, loomweave, plainweave, wardline, warpline` →
`mcp attachment` leg **PASS**. Both fill members (loomweave, legis) attach
live-bound in **every** configuration tested, including the brief's "latest main"
wardline/warpline.

### 2.3 Per-leg census (release builds + both fills)

17 / 18 legs **PASS**. The single non-PASS:

```
[WARN] legis govern
  wardline refused to sign the legis artifact: dirty working tree (uncommitted
  changes) — commit first … the signed Wardline→Legis handshake requires a clean tree
```

This is the **designed clean-tree-signing behaviour**, tripped by 4 *pre-existing*
provisioning-drift files dirty at session start (`AGENTS.md`, `CLAUDE.md`,
`.gitignore`, `.weft/filigree/INSTALL_VERSION` — filigree v3.1.0 marker bumps +
legis gitignore entries). On a clean tree this leg PASSes (the committed
`docs/tour.md` shows `[PASS] legis govern → governed 43 active defects`). `git
stash` is operator-blocked and these files are not mine to commit, so the tree was
left as-is and this WARN is reported as an artifact, not a defect.

### 2.4 `make verify` exit status

`make verify` exits **2** in all runs — but the *only* residual failure on the
correct builds + a dirty tree is **`docs/tour.md is stale`**, whose entire fresh-
vs-committed diff (14 lines) is the one `legis govern` PASS→WARN above. Per the
brief's "keep the tree clean" guidance, on a clean tree this run would be green.
The narrative was **not** regenerated/committed.

### 2.5 Confident-empty seams

**None observed** among the live joins. Every seam that returned empty/degraded
did so with a machine-readable reason (the churn DISABLED path in 2A, the
plainweave ABSENT path in 2B, the wardline rust-extra error, the warpline
"unknown tool" error). The honesty standard held throughout.

---

## 3. Part 2 — targeted merge-gate validation

### 3.1 — 2A: Loomweave churn/recency consumer → **NO-GO**

Driven via fresh `loomweave serve --config <warpline on|off>` subprocesses;
warpline command supplied via `LOOMWEAVE_WARPLINE_MCP_COMMAND=…/warpline-mcp`.

**Producer pre-check (warpline, healthy):** a direct newline-framed
`warpline_entity_churn_count_get` call (`repo` + real refs) returns the frozen
`warpline.entity_churn_count.v1` envelope in **0.05 s** with **real nonzero
churn** (`file:.claude/settings.json` churn=6, `…/wardline-gate/SKILL.md` churn=4,
…) and correctly reports never-observed refs as `churn_count: 0` (not an error).
The sibling is up and has data.

**DISABLED (warpline off) — CORRECT honest-empty:**
```json
{"ok": true, "error": null,
 "result": {"churn_source": "warpline", "entities": [],
   "page": {"limit":0,"offset":0,"returned":0,"total":0,"truncated":false},
   "reason": "warpline-disabled",
   "signal": {"available": false, "signal": "warpline_churn",
     "reason": "Warpline churn integration is disabled (integrations.warpline.enabled: false); enable it to rank by change count"}}}
```
`total:0`, `entities:[]`, `churn_source:"warpline"`, a reason + signal note, JSON-RPC
`error` null. Exactly the contract the brief requires. ✓ (both
`entity_high_churn_list` and `entity_recent_change_list`).

**LIVE (warpline enabled) — FAILS (deadlock/hang):** both
`entity_high_churn_list` and `entity_recent_change_list` **hang to timeout**
(`TimeoutError: probe timed out after 40s`); the consumer has no per-call timeout
so it would block indefinitely. No churn data, no `churn_source` payload — the
"dead-by-design" surface never lights up. Reproduced against **both** warpline
builds — `@main` (`02aa7f0`) and the blessed **`release/1.2.0` (`def6d43`)** — so
the failure is warpline-version-independent (the mismatch is structural). The
same harness's DISABLED path returns instantly, confirming the hang is the
warpline interaction, not loomweave startup.

**Root cause (code-confirmed + empirically reproduced):**
1. **Transport framing incompatibility (primary).** The consumer drives
   `warpline-mcp` over loomweave's **internal plugin transport** —
   `loomweave_core::plugin::{read_frame, write_frame}`, LSP-style **`Content-Length`**
   framing (the wire contract for loomweave's *own* plugins). But `warpline-mcp`
   speaks **standard MCP newline-delimited JSON-RPC**
   (`print(json.dumps(...), flush=True)`), as the green attach gate's
   newline-delimited probe and Claude Code itself confirm. `read_frame` parses
   warpline's reply line as an LSP header, never matches `Content-Length`, and
   blocks on the next read → deadlock.
2. **Missing mandatory `repo` arg (secondary).** Even with framing fixed, the
   consumer builds `arguments = {entity_refs, sort_by, sort_order, actor}` and
   omits `repo`, which `warpline_entity_churn_count_get` **requires**
   (`_repo_arg` → `MissingRequiredFieldError`). It also sends `actor`, which is
   not in warpline's allowed field set for that tool.
3. **Key-granularity risk (to verify after 1+2).** warpline keys lacuna churn at
   **file** granularity (`file:specimen/cli.py`), while the consumer's candidates
   are function/class entities (`specimen/cli.py::_add_book`). A direct probe of
   those function locators returned `churn_count: 0`. So even after the transport
   fix the ranking may come back all-zero until key alignment is verified.

**Why the unit test missed it:** GV-LW-2 drives the parse path through an
**injected fake** `WarplineLookup` (the commit says so) — the real wire transport
and the real `warpline_entity_churn_count_get` arg contract are never exercised.
The fill's own commit message flags this as the open follow-up `weft-6fc4a166dc`
("live cross-member validation … a tracked follow-up"). This dogfood is that
validation, and it **fails**.

**Verdict:** `weft-6fc4a166dc` is **NOT** cleared — it is confirmed as a real,
reproducible break. **GV-LW-2 must NOT be re-marked live-captured.** The
honest-degrade-when-disabled half is excellent; the actual feature (live churn
ranking) does not work end-to-end.

**Specific failing assertion:** *"With warpline live, `entity_high_churn_list` /
`entity_recent_change_list` return real churn ranked by warpline's count, each
item carrying `churn_count` + `churn_source:"warpline"`, ≥1 nonzero"* — instead
both calls hang to timeout with zero data.

### 3.2 — 2B: Legis←Plainweave advisory preflight → **GO**

Driven via fresh `legis mcp` subprocesses with `.env` sourced; plainweave toggled
via `PLAINWEAVE_MCP_CMD=…/plainweave-mcp`.

**Feature-presence:** fresh legis `tools/list` contains **`plainweave_preflight_get`**
(absent on running v1.3.0 main) and `policy_evaluate`. ✓

**Producer pre-check (plainweave, healthy):** direct
`plainweave_preflight_facts_get {scope_kind:"commit_range", base, head}` returns
`ok:true`, schema `weft.plainweave.preflight_facts.v1`, 3 scoped requirements,
9 facts, `freshness:"partial"`. ✓

**LIVE (plainweave present) — `status:"checked"`, envelope passed through verbatim:**
```json
{"status": "checked",
 "preflight_facts": {"schema": "weft.plainweave.preflight_facts.v1", "ok": true,
   "data": {"producer": {"tool":"plainweave","version":"1.0.0","project":"lacuna"},
     "scope": {"kind":"commit_range","base":"HEAD~1","head":"HEAD",
               "requirement_ids":["REQ-lacuna-0001","REQ-lacuna-0002","REQ-lacuna-0003"]},
     "freshness": "partial",
     "authority_boundary": {"local_only": true, "live_peer_calls": false,
                            "governance_verdicts": false, "legis_policy_cells": "external"},
     "facts": [ …9 facts… ]}}}
```
All three required boundary fields correct (`local_only:true`,
`live_peer_calls:false`, `governance_verdicts:false`) + `freshness` present. ✓

**ABSENT (plainweave unconfigured) — `status:"unavailable"`, with reason:**
```json
{"status": "unavailable", "unavailable": [{"reason": "plainweave client not configured"}]}
```
Not empty-as-clean, not `INTERNAL_ERROR`, JSON-RPC `error` null. ✓

**Enrich-only proof (the core assertion) — verdict byte-identical with/without plainweave:**

| policy | target | outcome | present == absent |
|--------|--------|---------|-------------------|
| import-allowlist | `{"value":"os"}` | **CLEAR** | **identical** |
| import-allowlist | `{"value":"requests"}` | **VIOLATION** | **identical** |
| import-allowlist | `{"module":…,"imports":…}` | UNKNOWN | identical |
| protected.demo | `{"value":"x"}` | UNKNOWN | identical |

Determinism pre-check (same absent config twice) was byte-identical first, ruling
out timestamp/run-id noise. Real verdicts (CLEAR **and** VIOLATION) are unchanged
whether plainweave is present or absent — plainweave is purely advisory and never
moves a governance verdict. ✓

The legis client is notably well-built: **newline-delimited** JSON-RPC (matches
plainweave-mcp), correct `{scope_kind, base, head}` args (no spurious fields), and
full GV-LG-3 fail-closed boundary validation. Contrast 2A's transport.

**Verdict:** `weft-a0d04046f5` **can be cleared**; the legis golden
`_provenance.source` can be re-marked **`live-captured`** and `GOLDEN_BLOB_SHA`
re-pinned. (Conformance was previously CONSTRUCTED because the hub session
misroutes plainweave; this lacuna-rooted run is the live capture.)

---

## 4. New defects surfaced (file nothing — for PM triage)

| # | Severity | Member / area | Defect |
|---|----------|---------------|--------|
| **D-FILL-2A** | **High (blocks merge)** | loomweave `feat/warpline-churn-consumer` | Live warpline churn join is non-functional: (1) consumer uses loomweave's Content-Length plugin transport against newline-JSON `warpline-mcp` → deadlock/hang; (2) omits the mandatory `repo` arg (+ sends disallowed `actor`); (3) likely key-granularity mismatch behind those. No per-call timeout → unbounded hang. Honest-degrade-disabled path is correct. |
| **D1** | Medium (harness/infra) | warpline `main` | `warpline_project_status_get` (the lacuna attach gate's warpline binding tool) exists only on `release/1.2.0`, not on `main`/`origin/main`. Installing warpline from main (as the brief instructs) → warpline `live-empty` → attach gate RED. Forward-port to main, or pin the harness/brief to the release ref. |
| **D2** | Medium (harness/infra) | wardline `main` | `doctor.repo_binding` (the attach gate's wardline binding field) exists only on `release/consolidation-2026-06-26`, not on `main`. Same attach-gate RED from main. Additionally: `wardline mcp` requires the `[scanner]` extra (else crashes on spawn) and the rust frontend requires the `[rust]` extra (else `WLN-ENGINE-FILE-FAILED` on the rust specimen). Both are honest, self-naming errors — install `wardline[scanner,rust]`. The brief's plain "latest main" install omits both. |
| **D3** | Low (doc/process) | this brief | The brief's Part-0 instruction "wardline, warpline → latest main" is incompatible with the merge gate it asks to run: the attach binding contracts the harness depends on live only on the members' release branches. The brief should pin the release refs (and the `[scanner,rust]` extras) or note the divergence. |

None filed (per the brief). All are environment/cross-member-integration findings
except D-FILL-2A, which is the 2A merge blocker itself.

---

## 5. GO / NO-GO

| Fill branch | Verdict | Basis |
|-------------|---------|-------|
| **loomweave `feat/warpline-churn-consumer`** | **🔴 NO-GO** | LIVE churn join deadlocks/hangs (Content-Length-vs-newline transport mismatch + missing `repo` arg). Feature never lights up against a real, healthy warpline. Disabled-degrade path is correct; producer is healthy. Unit test mocked the transport, so green-on-CI ≠ working live. `weft-6fc4a166dc` stays open; GV-LW-2 stays CONSTRUCTED. |
| **legis `feat/plainweave-preflight-consumer`** | **🟢 GO** | LIVE→checked (full envelope + correct authority_boundary/freshness), ABSENT→unavailable (reasoned, no INTERNAL_ERROR), and real verdicts (CLEAR/VIOLATION) byte-identical with/without plainweave. Clears `weft-a0d04046f5`; golden can be re-marked `live-captured`. |

**Bottom line:** merge **legis** `feat/plainweave-preflight-consumer`. Do **not**
merge **loomweave** `feat/warpline-churn-consumer` until the warpline-mcp wire
transport (newline JSON-RPC, not loomweave's Content-Length plugin framing) and
the `repo` argument are fixed and re-validated live — and add a per-call timeout
so a transport fault degrades honestly instead of hanging. Separately, the merge
gate / brief needs warpline+wardline pinned to their release refs with the
`[scanner,rust]` extras (D1–D3); neither fill is responsible for those.
