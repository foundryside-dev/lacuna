# Loom suite integration sandbox (`/home/john/testo`)

Scratch environment to test how the four **Loom** arms install and interoperate
in one shared Python 3.12 venv. This README is the source of truth — written so
the project can be rediscovered from files alone, without filigree/MCP/memory.

## Purpose

The Loom suite models a codebase as **entities** (one durable identity, "SEI"),
each carrying typed facts from different tools, all read in one call. The four
arms live in sibling directories under `/home/john/`:

| Arm | Source dir | Kind | Role in the suite |
|-----|-----------|------|-------------------|
| **filigree** | `/home/john/filigree` | Python (issue tracker, MCP) | issue associations on entities |
| **clarion** | `/home/john/clarion` | Rust CLI + Python plugin | **identity authority + fact store (the hub)** |
| **wardline** | `/home/john/wardline` | Python (taint analyzer) | taint facts on entities |
| **legis** | `/home/john/legis` | Python (design-ready, NOT implemented) | governance attestations |

Goal: install all four side-by-side and exercise the cross-product seams
(entity identity, dossier reads, Clarion↔Wardline probe, Filigree entity
associations).

## Environment

- `.venv/` — Python 3.12 venv, created with `uv venv` (has **no pip**; install
  project-local packages with `uv pip install --python .venv/bin/python ...`).
- Filigree is intentionally **not** installed in `.venv/`; project hooks use
  the global uv tool install at `/home/john/.local/bin/filigree`.
- Python 3.12 satisfies every `requires-python` for the local sandbox packages.

## Install status

| Arm | Installed? | How |
|-----|-----------|-----|
| filigree | ✅ **yes** (v2.3.0, global uv tool from PyPI) | `uv tool install filigree==2.3.0` |
| clarion | ⬜ not yet — **next** | `cargo install --path /home/john/clarion/crates/clarion-cli --root .venv` + `uv pip install -e /home/john/clarion/plugins/python` |
| wardline | ⬜ not yet | `uv pip install -e /home/john/wardline` |
| legis | ⬜ not yet (design-only; nothing runnable to install) | n/a |

Install Filigree from the published package, not the local source checkout.

## filigree — local wiring (important)

filigree is installed as a global uv tool and **project config points at the
global binary**, NOT a `.venv` install. If the MCP tools or hooks ever look
wrong, check these:

- `.mcp.json` → `filigree` server command = `/home/john/.local/bin/filigree-mcp`
- `.claude/settings.json` → hooks (`session-context`, `ensure-dashboard`) =
  `/home/john/.local/bin/filigree`
- `.codex/config.toml` and `.codex/hooks.json` use the same global uv tool
  binaries.
- DB: `.filigree/filigree.db` (project prefix `testo`).
- Verify the live server is local: CLI `filigree mcp-status` (or MCP
  `mcp_status_get`) — `install_context` should be `uv_tool`, with package files
  under `/home/john/.local/share/uv/tools/filigree`.

A full CLI + MCP smoke test was run (~70 CLI verbs + the MCP lifecycle): all
green, no bugs. Every apparent failure was either wrong args or a guardrail
firing correctly (claim-aware writes, transition validation, project-prefix
import isolation, force-required deletes).

## `specimen/` — test corpus for Clarion/Wardline

A tiny, runnable in-memory library system, deliberately structured to give
Clarion's extractor a rich entity/edge graph and Wardline a taint boundary.

```
specimen/
  __init__.py
  models.py      # Genre(Enum), Identifiable(Protocol), Entity(ABC),
                 # Money(frozen dataclass, operator overloading), Book, User, Loan
  repository.py  # TimestampMixin, Repository[T](ABC+Generic, container dunders),
                 # InMemoryRepository (mixin/MRO), BookRepository, UserRepository
  service.py     # audited (decorator factory), LoanPolicy(Protocol),
                 # StandardPolicy, PremiumPolicy (decorator pattern),
                 # LibraryService (strategy + observer + classmethod factory)
  cli.py         # App (class-level command registry via decorator),
                 # untrusted argv boundary -> service  (Wardline taint source)
```

Patterns exercised: abstract base classes, `Protocol` structural typing, bounded
generics (`TypeVar(bound=...)`), mixins + multiple inheritance/MRO, decorator
factories, classmethod factories, properties, dunder/operator overloading, enums,
dataclasses, and strategy/observer/decorator/registry patterns.

Cross-module edges: `cli → service → repository → models` (imports = references;
method calls = calls) plus inheritance edges.

Run it: `.venv/bin/python -m specimen.cli register grace "Grace Hopper"`

## Next steps

1. **Clarion** (the hub): build the Rust CLI (`cargo`, ~68K LOC, a few min) and
   `pip install -e` the `clarion_plugin_python` plugin. Then point `clarion
   analyze` at `specimen/` and test the Filigree↔Clarion binding (Filigree
   `entity_association_*` ↔ Clarion `issues_for` / WP9-A).
2. **Wardline**: pip install; scan `specimen/` (the `cli.py` argv→service flow).
3. **Legis**: design review only — check its intended contracts against what the
   live three expose.
