# PDR-0020 — Comprehensive suite coverage is an explicit standing theme (peer-facts question resolved)

- **Date:** 2026-06-29
- **Status:** Accepted (owner-stated intent; prioritization within the authority grant)
- **Decider:** human owner (John) stated the intent; agent:lacuna-po recorded
- **Related:** PDR-0015/0016/0017 (the peer-facts cells that raised the question), the open question
  in `current-state.md` (2026-06-29), `roadmap.md` (Later: combination-matrix completeness, graduate
  to demonstrator), `vision.md` (audience + roster — refinement pending owner confirmation, see Note)

## Context

`/own-product` flagged the four peer-facts cells (PDR-0015/0016/0017) as strategy drift: they
shipped via sibling-driven tasking, off the planned roadmap, and it was undecided whether
"members consuming siblings' facts" was an explicit theme or a one-off batch. Asked to rule, the
owner stated Lacuna's intent directly: **"Lacuna provides a comprehensive demo of the full suite as
it comes online — when tabard comes online, you'll pick up identity management as well."**

## Options

1. **Promote to an explicit, standing theme** — Lacuna systematically covers each member's surfaces
   as they ship; peer-facts cells are one instance.
2. **Close as a completed one-off** — bank the four cells; pick up future cells only ad hoc.
3. **Bounded middle** — a theme, but with gated intake so it doesn't mirror every sibling PR.

## Call

**Option 1, realized via Option 3's intake gate.** Comprehensive coverage of the full suite, growing
**as it comes online**, IS Lacuna's intent (owner-stated). The peer-facts cells are not a special
case to adjudicate — they are an instance of the general rule: **as each member ships a capability
or cross-member surface, Lacuna picks it up** (planted lacuna + tour leg + `matrix.md` cell + honest
degrade when absent). The canonical forthcoming instance: when **`tabard`** comes online, Lacuna
picks up **identity management**.

**Intake gate (so the theme tracks the suite deliberately, not reactively):** add a cell when (a)
the member surface is **released, not branch-only** (the D1/D2 / byte-lock lesson — never pin the
tour to a branch build) and (b) it fills a currently-empty `matrix.md` cell. The sequencing of
*which* cells in *what order* routes to `/axiom-program-management`, not this PDR.

## Rationale

This is the vision's own logic made explicit: the joins/combinations are the product's reason to
exist, `matrix.md` completeness is already a stated goal, and "point the suite and watch it work"
demands breadth. Treating coverage as a standing theme makes the roadmap **deliberately track suite
growth** rather than react ad hoc or relitigate the question every time a sibling ships. The
no-silent-clean invariant the peer-facts cells assert is among the strongest federation-honesty
demonstrations in the tour.

## Reversal trigger

- If comprehensive-coverage intake starts **crowding out the core seam-integrity gate work** (G1)
  or pushes the tour toward non-determinism / unmaintainability, re-scope to a bounded subset and
  hand the trade to `/axiom-program-management`.
- If a covered member's surface is withdrawn, the cell **follows** (gates to `[N/A]`, never reds) —
  same discipline as PDR-0016.
- This theme does not license reaching across the consumer boundary: Lacuna still only demonstrates
  and reports, never fixes a member (vision anti-goal #4 unchanged).

## Note — vision-text refinement pending owner confirmation

The owner's statement also bears on `vision.md` (the audience framing and the member roster, incl.
`tabard`). Per the authority discipline, `vision.md` is **not** rewritten from this PDR; the precise
phrasing and the audience-sequence reconciliation are being confirmed with the owner, and a separate
PDR will record any vision change once confirmed.
