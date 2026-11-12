# P777: the brief holds the goal, and init says what is still open: rows

Card: [P777 #1075](https://github.com/xmejkal/spark/issues/1075), from P776's read of the open rows (walk 2's G4, G5, G21 and
walk 4's row 9). Plan `~/.claude/plans/p777-brief-goal.md` (written on the best model; one lens on Sonnet and the refuter on
Fable, two rounds). This file holds the acted, raised and rejected findings only (rules.md). 2026-11-12.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | `open_fields` says "open", which is `data.open`'s word; the code's word is "unanswered" (`nulls_in`'s docstring, the CLI's text) | plan lens | acted | `unanswered_fields` |
| 2 | `--brief <file>` names the brief, which is project.json; the file's noun is "answers", as sourcing's `write_answers.py`; `brief_answers` the same | plan lens | acted | `--answers <file>`, `answers_in` |
| 3 | one code for an unusable answers file, with its sentence, covering an unreadable file, an unknown key and a wrong shape (goal a text, the four lists) | plan lens | acted | `build_codes.ANSWERS_UNUSABLE`, in `CODES` |
| 4 | an exit 2 after rules.json was merged leaves the project half-written: read the answers and the brief before the loop | plan refuter | acted | `main` reads both through `answers_in` before the loop; test 7 holds rules.json at `{}` after the refusal |
| 5 | no test for an unreadable answers file, a wrong shape, a kept `prefer`, an answered rules field after `--force` | plan refuter | acted | tests 8, 9, 10, 11 |
| 6 | the sixth mutation row (`merged`'s `and value` removed) is an equivalent mutant on existing code | plan refuter | acted | dropped; five rows |
| 7 | the plan said the P114 sentence is wrong today for both files; true for rules.json only (the refuter's run 6) | plan refuter | acted | the plan's text; refuted again in round 2 (row 12) |
| 8 | `idea.md:3`'s `allowed-tools` lists `parts.py` lines only, so the new run would ask for permission each time | plan lens | acted | the `init_project.py *` line, in `init.md`'s form |
| 9 | `--goal "text"` on the command line | plan lens | rejected | dropped because a word the person said never goes on a command line (`idea.md` item 3) |
| 10 | the P737 replies file for the answers | plan lens | rejected | dropped because the replies file answers an Operation's `data.open`, and init is not an Operation yet |
| 11 | each answer as a `{value, verified, source}` fact (`provenance.py`) | plan lens | rejected | dropped because no check reads the goal's source, and `has_answers` and idea's Read of `goal` would move; the answers file is the goal's origin |
| 12 | round 1's claim that `--force` leaves an answered rules field out of the list today is wrong: `init_project.py:66` appended the pre-merge payload, so it was listed (5 fields with 400000 on disk) | plan refuter 2 | acted | the disk-read list is a behaviour change named for the PO; test 11 pins it and delivers P114 #48's missing test |
| 13 | `journey/checks.md:11-13` is at 175 of 175 lines | plan refuter 2 | acted | rewritten in place, 175 lines |
| 14 | the items of `must`, `prefer`, `sellers` must be strings: `Brief._names` reads a non-string item as None and `has_answers` would count it | plan refuter 2 | acted | `answers_in`'s shapes: lists of texts; test 9's `["gme", 1]` |
| 15 | no card holds "init onto the core" | plan refuter | closed | the refuter's search over the open issues and #94 |
| 16 | the plan's `write_brief(path, answers)` cannot name the answers file in its note ("… from answers.json") | build | acted | `write_brief(path, answers, answers_file)`, three parameters |
| 17 | the plan's `answers_in(file)` reads the answers alone, and names no function for the brief's read before the loop | build | acted | `answers_in(file, brief)` reads both; a brief that is no JSON object gives the Refusal naming it; no new function |
| 18 | the plan's golden argv `--answers PROJECT/answers.json`: `golden_firmware.run_script` (:122) replaces an argument only when it equals `PROJECT` whole | build | acted | the Case passes `answers.json`, relative to the project, the child's cwd |
| 19 | the plan's "`store.add_project` runs before the refusal, as it does for today's tools-file refusal": today's refusal (`why_project_refused`, `init_project.py:42`) runs before the listing (:46) | build | acted | the decision as written stands (the listing, then the answers' refusal); the "as today" claim was wrong |
| 20 | R1: `main` rose from 79 to 89 lines (a span, blank lines too) with the flag, the read and the branch | build, `test_architecture` | acted | compressed in the file's own one-line style (`written += [path] if did else []`, the two prints joined) back to 79; no baseline move |
| 21 | T1: `write_brief`'s own `write_text` was a third file-write in `project_setup.py` (baseline 2) | build, `test_architecture` | acted | it writes through `write(path, payload, force=True)`, and keeps `write`'s note when the answers state nothing |
| 22 | R1: `answers_in` spanned 42 lines, over the 40 of `scripts/spark/` | build, `test_architecture` | acted | the blank lines around its nested helpers removed: 40 |
| 23 | `init_project.EXIT_NOTHING_TO_DO` is an alias (C3), not the vocabulary `test_self_confirmation` allows a test to read | build, `test_self_confirmation` | acted | the three tests pin the literal 1 |
| 24 | test 4 expected "2 field(s)" after the goal is answered in a new project; a new project's rules.json holds the two I²C nulls, so 4 | build | acted | the test's number (mine, not the plan's) |
| 25 | the plan's "not checked which test asks every code a sentence" | build | closed | `tests/test_json_contracts.py:276`, `TheBenchCodesTableTest`; it passes with the new code |
| 26 | the plan's "whether `plant` writes a file at the project root" | build | closed | `golden_firmware.plant` (:100-110) makes the parent folder and writes; the Case ran |
| 27 | `merged(answers, existing)` puts the answers' keys first, so a new brief would open with `goal` before its `//` note | build | acted | the payload is re-ordered to the template's keys, a person's own keys after (one line); test 4 pins the order |
| 28 | the goldens: only `init-project-nothing-to-do.txt` (the fixture's 13 fields read from disk before the last line) and the new `init-project-ok-brief.txt` moved | build | closed | `git status --short` on the six golden folders shows those two |
| 29 | the plan's `merged` at `:277-307`, `write` at `:309-320`, `PROJECT_TEMPLATE` at `:205-224`: `:277-306`, `:309-331`, `:205-223` | build | acted | the citations; nothing built on them |
| 30 | the plan's Review size says "seven tests in one file"; its Tests section lists eleven | build | acted | eleven built, in `WhatIsStillOpenTest` (4) and `TheBriefAnswersTest` (7) |
