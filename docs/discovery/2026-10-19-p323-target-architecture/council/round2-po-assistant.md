# Round 2: the PO's assistant

Verdict: **fix, then ship.** The design answers his ask and keeps walk 1 first. The top is too technical for a two-minute yes or no, and one open question is not his.

## Findings

**1. The TL;DR is jargon.** Petr will not know stdlib, Operations, registries, AST test, baseline, envelope or door. Replace the TL;DR with:

> **TL;DR.** We move spark's logic out of the big scripts into one package, area by area. Each script stays and keeps its name, flags and output. Each job gets one declared list of arguments and results, so the script, `--help` and Claude read the same thing. One automatic test enforces the code rules and only lets the list of known breaches shrink. Only step 1, a small frame, runs before walk 1, and it changes no output. About 32 small PRs follow, one area at a time.

**2. No plain yes or no line.** Add under the TL;DR: "**Your call:** say yes to this design and to slice 1 before walk 1, or say what to change. Two questions are in section 8."

**3. Progress is visible, but only as jargon.** The SCORE line has 11 columns. Add one headline above it in 5.4: "**Areas moved: 0 of 10. Known breaches left: N.** The other columns are detail." The Miro table keeps one row per area. Good.

**4. Question 2 is not his.** A crash exit status is a technical call, and his rule (delegate row decisions) says the council decides. Move it to a "Decided by the council" line: "A crash exits 2, could-not-run, in slice 2, because a crash is not a finding." Keep only Question 1.

**5. Missing question that is his.** Slice 1 runs before walk 1, so it is the one thing that could delay walk 1. Add as question 1 and renumber:

> 1. **Slice 1 before or after walk 1.** Example: you start the walk on the bench tomorrow. (a) The frame lands first. It is one PR and no script output changes. (b) Walk 1 first and the frame after. The council proposes (a), since the frame makes the later moves safe.

Ask one question at a time. Question 2 (capacity) stays as written.

**6. Undefined words.** Section 4 lacks: **Value** (a small fixed record), **baseline** (the list of today's breaches, which may only shrink), **golden** (a saved correct output), **registry** (a name-to-class list), **seam** (a swap point), **AST test** (a test that reads code structure), **stdlib** (Python's built-ins), **mutation row** (a planted defect). Add these rows.

**7. Reading time.** Sections 1 and 3 are dense tables. Put a line before section 1: "Sections 1 to 7 are reference. The TL;DR and section 8 are enough to decide."

**8. No widening found.** Deferred items say so. Walk 1 first, diagrams and names pass.

## Verdict

Apply fixes 1 to 7. Then Petr can decide in two minutes.
