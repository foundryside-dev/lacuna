# Vision — Lacuna

_Standing product artifact. Source of truth for purpose, audience, anti-goals, and the authority grant._
_Bootstrapped 2026-06-13 from observed repo/tracker/git reality._

## Purpose

Lacuna is the **demonstration specimen** of the Weft federation: a clean-cored
reference application deliberately seeded with catalogued, permanent flaws
("**lacunae**"), each one placed to make a specific Weft tool — or tool
*combination* — light up. Pointing the suite at Lacuna and watching it work is
how the federation proves, demonstrates, and regression-tests itself.

The product is not the library app; it is the **proving ground**: the specimen
corpus, the single-source-of-truth flaw manifest (`tour/lacunae.toml`), the tour
harness that drives every live tool against the specimen and regenerates the
narrative, and the dogfood discipline that runs the real suite against Lacuna and
records the friction.

> "Where Weft's other members are instruments, Lacuna is the specimen." — README

## Who it serves — a comprehensive demo of the full suite, as it comes online

Lacuna's intent is to be a **comprehensive, growing demonstration of the full Weft
suite as each member comes online** (owner-directed 2026-06-29, PDR-0021 — this
**supersedes** the 2026-06-13 "dogfood now, demonstrator later" sequencing). The
growing demo is the **primary deliverable now**, not a future graduation gated on
the suite being "finished." As each member ships a capability or cross-member
surface, Lacuna picks it up — a planted lacuna + tour leg + matrix cell — and
degrades honestly where a member is absent or design-only.

One artifact serves both audiences, continuously:

1. **The Weft federation's developers and product owner.** Lacuna is the
   **dogfood range** and regression corpus: when a seam between two tools breaks,
   Lacuna is where it is caught.
2. **Prospective evaluators of the Weft suite.** `docs/tour.md` and
   `docs/matrix.md` are the "point the suite and watch it work" demonstration —
   credible and honest, surfacing every live lacuna and labelling any absent or
   design-only member rather than faking it (the G3 honesty discipline).

**Roster covered today:** loomweave, filigree, wardline, legis, warpline, and
**plainweave** (requirements management — the member formerly tracked as
*charter*). **Forthcoming:** **tabard** (identity management — issuing agent
names); Lacuna picks up identity-management coverage when tabard's surface is
released (the PDR-0020 intake gate). The Weft hub (`~/weft`) still owns the
canonical roster; this list is only what Lacuna currently *demonstrates*.

## Anti-goals — what Lacuna is deliberately NOT

- **Not a real app to be made bug-free.** The planted lacunae are permanent and
  intentional. "Fixing" one is a *regression* that fails `make verify`. Cleanly
  removing flaws is the opposite of the product's job.
- **Not a roster member of the federation.** The Weft hub (`~/weft`) owns the
  roster and the federation narrative; Lacuna is the specimen, not an instrument.
  Lacuna does not restate or own the roster.
- **Not a place to chase analyzer-finding zero.** Most "findings" are the planted
  lacunae themselves (44 baselined/suppressed). A green gate on the baseline +
  trip-on-anything-new is the desired state, not a backlog to burn down.
- **Not the owner of the tools it demonstrates — it is a *consumer* of the
  federation, not a part of it** (owner-confirmed 2026-06-13). When dogfooding
  surfaces a federation-tool bug, **Lacuna only ever owes a bug report** — the
  specimen, a reproducing fixture, and the friction write-up. The fix lives in
  the owning member's repo; Lacuna never reaches across to fix it. (This is why
  the authority grant escalates any change to the hub or another member.)

## Authority grant

**Status: CONFIRMED** (ratified by owner via `/own-product`, 2026-06-13; re-confirmed as-is 2026-06-25)
**Last reviewed: 2026-06-25 · Review cadence: quarterly (next: 2026-09-25)**

The product-owner agent acts **autonomously within strategy** and **escalates
before anything hard-to-reverse or outward-facing.**

**Autonomous (no ask required):**
- Prioritize and reprioritize the lacunae / tour / dogfood backlog
- Write PRDs and acceptance criteria
- Dispatch delivery and accept work against stated criteria
- Kill a failing bet
- Run and regenerate the tour; run the dogfood cycle and record friction reports

**Escalate to the human owner first (hard-to-reverse / outward-facing):**
- Changing the vision, strategy, or this authority grant (a grant change is
  itself a vision change — escalate, never silently edit)
- **Removing or "fixing" a planted lacuna** — destructive, fails `make verify`,
  and alters the specimen's identity
- Any change to the **Weft hub** or **another federation member** (external party)
- A public release or announcement
- Deleting tracker, governance, or audit data

_A widened or narrowed grant must be escalated as a vision change, not edited in
place._
