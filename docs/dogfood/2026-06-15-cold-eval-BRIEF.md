# New-repo onboarding task + debrief

You've picked up a small piece of work: you're new to this codebase and need to
get oriented and answer the questions below — the ordinary "come up to speed on an
unfamiliar repo" job. **Do it however you normally would.** You have your usual
toolbox (reading files, searching text, running commands) plus whatever else
happens to be wired into this session; reach for whatever you judge fastest and
most reliable for each question, exactly as you would on any real job. No tool is
the "intended" one — pick the right drill for each screw.

When you're done, you'll write a short, **honest debrief** of how the work went.
The debrief is the part that matters. Be the kind of professional whose debrief
gets trusted *because* it's candid: if something slowed you down, made you guess,
returned nothing useful, or made you give up and just read the code yourself — say
so plainly. A smooth-sounding debrief that hides the snags is worthless to the next
person.

---

## Ground rules

1. **Answer the questions in Part A** with specifics — names, paths, line numbers
   where they matter.
2. **Show your work as you go.** For each question, jot down how you actually got
   the answer: what you tried first, whether it landed, and — the useful part —
   **anywhere you fell back to reading files / searching text / reasoning by hand,
   and why.** ("Tried X, it came back empty / wanted a flag I had to guess / took
   three steps, so I just searched the source" is exactly the kind of note we want.)
3. **Use the easy thing when it's easier.** If plain reading or text-search is the
   faster, more trustworthy path for a question, take it and say so. Don't reach
   for something fancier to look thorough.
4. **Read-only.** Don't change anything.

---

## Part A — the questions

1. **Orientation.** In a few sentences: what is this project, and what are its
   major parts / subsystems?
2. **Dead code.** Is there code that looks unused or unreachable? Give specific
   examples with locations.
3. **Structural health.** Any circular imports, or components that are unusually
   tightly coupled? Which?
4. **Find by intent.** Where is the functionality that **adds a book to the
   library** implemented? (You may not know the exact name.)
5. **Known issues.** Are there any flagged quality or security problems in this
   code? List a few — location and what each is.
6. **One package.** Looking at **just the `specimen` package**, which functions or
   classes are its biggest coupling hotspots?
7. **Change impact.** If you changed the function that adds a book, what else would
   likely be affected?
8. **Governance.** Is there any policy / compliance / sign-off signal attached to
   this code — attestations, policy boundaries, governance state? What does it say?

---

## Part B — the debrief

Looking back over the work you just did:

### How you worked (one short table)
Question · what you reached for first · did it answer cleanly (Y/N) · fell back to
reading/searching by hand? (Y/N + why).

### Scores (1–5, 5 = best) — one line of justification each
- **Ease** — how easily did correct answers come?
- **Trust** — did you trust the answers, or feel you had to confirm them by reading
  the code yourself?
- **Knew-where-to-look** — did you know what would answer each question, or nearly
  miss the thing that could?
- **Friction** — flags to guess, extra steps, things to wire up, confusing errors:
  how much did the work fight you? (5 = frictionless.)
- **Next time** — honestly, would you work this way again, or go straight to
  reading/searching the source?

### Open
- **Worst moment:** the single biggest snag.
- **Best moment:** the single thing that did something you couldn't easily have
  done by hand.
- **Where you fell back:** every point you dropped a tool for reading/searching,
  and why. Don't soften this — it's the most useful thing you'll write.
- **One change:** if you could fix one thing about how this work went, what?
- **Would you recommend this way of working to another engineer? Yes / No** + one
  sentence.

### Headline
One sentence for a busy manager: was this a good way to do the job, and what's the
catch?

---

## Output

Write your answers + debrief to `docs/dogfood/2026-06-15-cold-eval-report.md`.
Keep generated DBs / scan output out of version control. Answer honestly, mark
where you fell back, and score it like the next person's choices depend on your
debrief being *true*, not kind.
