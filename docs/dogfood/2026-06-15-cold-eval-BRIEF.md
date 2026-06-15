# Code-Intelligence Tooling — Independent Evaluation (cold boot)

You are an **independent reviewer**. You have been contracted to evaluate the
code-intelligence tooling available in this environment by **using it to answer
real questions about an unfamiliar codebase**, and then writing an **honest
review**. You have **no stake** in these tools succeeding. Your only value is
candour: a flattering review that hides friction is worthless to whoever paid for
it. Treat clunk, extra steps, dead-ends, and "I gave up and read the file myself"
as real defects worth marking down.

You are rooted in a project directory. Some tools are attached to this session
(you will see them — MCP servers and/or CLIs); you also have your normal abilities
(reading files, searching text, running commands). **Use whatever you judge
fastest and most reliable for each question — exactly as you would on a real job.**
There is no "right" tool. Which tool you reach for *is the data we care about.*

---

## Ground rules (read once, then work)

1. **Answer the questions in Part A.** For each, give the actual answer (specifics:
   names, paths, line numbers where relevant).
2. **Keep a tool log as you go.** For each question record: *what you reached for
   first*, whether it answered cleanly, and — critically — **any point you fell
   back to reading files / text-search / manual reasoning, and why.** "I tried X,
   it returned nothing / needed a flag I had to guess / took three calls, so I
   grepped instead" is the single most useful sentence you can write.
3. **Do not assume the fancy tool is the right answer.** If plain file-reading or
   text search is faster or more trustworthy for a question, use it and say so.
4. **Don't fix anything.** This is read-only assessment.

---

## Part A — Questions about this codebase

1. **Orientation.** In a few sentences: what is this project, and what are its
   major parts / subsystems?
2. **Dead code.** Is there any code that appears unused or unreachable? Name
   specific examples (with locations).
3. **Structural health.** Are there circular imports, or components that are
   unusually tightly coupled? Which ones?
4. **Locate by intent.** Where is the functionality that **adds a book to the
   library** implemented? (You may not know the exact function name.)
5. **Quality / security signal.** Are there any flagged quality or security issues
   in this code? List a few, with locations and what each is.
6. **Scoped question.** Considering **only the `specimen` package**, which
   functions or classes are its biggest coupling hotspots?
7. **Change impact.** If you modified the function that adds a book, what else in
   the codebase would likely be affected?
8. **Governance.** Is there any governance / policy / compliance signal on this
   code — e.g. attestations, policy boundaries, sign-off state? What does it say?

---

## Part B — Your review (the part we're actually buying)

Be the reviewer who gets hired again because their reviews are *useful*, not the
one who gives everything five stars. Write the following:

### Per-question tool log
A short table: question · first tool reached for · did it answer cleanly (Y/N) ·
fell back to file-read/text-search? (Y/N + why).

### Scores (1–5, 5 = best) — with one line of justification each
- **Ease** — how easily did you get correct answers?
- **Trust** — did you trust the answers, or feel you had to double-check by reading
  the code yourself?
- **Discoverability** — before trying, did you *know* a tool could answer the
  question, or did you stumble onto it / nearly miss it?
- **Speed / ergonomics** — flags to guess, extra calls, URLs/tokens to wire,
  cryptic errors: how much friction per answer?
- **Reach-for** — honestly, next time, would you reach for these tools first, or
  go straight to reading files / text search?

### Open questions
- **Biggest friction:** the single worst moment.
- **Biggest win:** the single moment the tooling did something you *couldn't*
  easily do yourself.
- **Where you defected:** every point you abandoned a tool for grep/file-reading,
  and exactly why. (Most valuable section — don't soften it.)
- **One fix:** if the makers could change one thing, what?
- **Net recommendation:** would you tell another engineer to adopt these tools over
  their current habits? **Yes / No**, plus one sentence.

### Headline
One sentence a busy manager would read: is this tooling worth reaching for, and
what's the catch?

---

## Output

Write your answers + review to
`docs/dogfood/2026-06-15-cold-eval-report.md`. Keep any generated DBs / scan output
out of version control. That's it — answer honestly, log where you defected, and
score it like your reputation depends on the review being *true*, not kind.
