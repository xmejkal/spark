# P853 PR 1: the idea area's codes carry their meaning and their fix: rows

Card: [P853 #1217](https://github.com/xmejkal/spark/issues/1217), PR [#1328](https://github.com/xmejkal/spark/pull/1328).
This file holds the acted, raised and rejected findings only. The review: the architecture lens and the refuter, both
on Opus. 2026-11-20.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | patterns-and-names.md kept its line budget by joining lines, not by cutting text | the review | acted | fixed: the P239, P475, P828 and P877 rename history is cut (git holds it, the role table the names), the touched lines wrap at 120, and the page has 279 lines |
| 2 | the page lists `clock` and `privacy` among the leaves of `spark.core`, and they are not in `measure.LEAVES` | the review | acted | fixed: the page names the leaves `outcomes`, `text_guards`, `zone_time` and `codes`, and `clock` and `privacy` apart |
| 3 | the scan misses a subclass of a subclass and an error subclass defined in another file of the area | the refuter, two planted cases | acted | fixed: `coded_errors` closes the set over the bases of every file of the area, and the scan's own test plants both |
| 4 | the scan's code check reads a tuple by index and repeats the table test's `CODES` check | the review | acted | fixed: `module, _, word = ...rpartition(".")`, and the `CODES` check is the table test's alone |
| 5 | `Finding.of`'s docstring repeats the TypeError sentence of `codes.fix_of` | the review | acted | fixed |
| 6 | the class diagram shows `Finding.of` without `fix=None` | the review | acted | fixed |
| 7 | the PR body does not say why U1 comes before the idea codes, and names the pin commit "commit 1" | the review | acted | fixed in the PR body |
| 8 | the scan does not see `**{"fix": ...}`, `Finding.__new__`, an alias `make = Finding` or `_replace(code="plain")` | the refuter, lower-risk gaps | raised | a line on card P853 #1217 for the next area's PR |
| 9 | the `type(x)(` scan does not see `x.__class__(...)` | the refuter | raised | a line on card P853 #1217 for the next area's PR |
| 10 | test_flow's `chmod(0)` passes under root, and it pins the errno text | the refuter | rejected | dropped because spark's suite does not run as root, and the errno text is the message the person reads |
| 11 | `CodeTest`'s hash test proves nothing a str does not | the refuter | rejected | dropped because it guards an override of `__eq__` or `__hash__` |
