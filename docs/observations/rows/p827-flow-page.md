# P827: page.html shows the flow's phases: rows

Card: [P827 #1185](https://github.com/xmejkal/spark/issues/1185), a story, PR #1255. New logic: a plan check on the
strongest model, a plan council (one lens, the refuter), then one lens and the refuter on the PR. This file holds
the acted, raised and rejected findings only (rules.md). 2026-11-17.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | written after the build record, the page tells the person to run the build they just ran | plan refuter | acted | the page is written last, after the simulation folder is kept; a test and a mutation row pin the order |
| 2 | a file write in a flow module breaks the rule that only an Adapter writes a file | plan lens | acted | `FlowPageStore`, an Adapter that a test replaces with a fake |
| 3 | the page value depended on the tabbed page's `Tab`, so a second renderer could not take it | plan lens | acted | `Picture` is the flow's own Value; the PR lens ran a ten-line second renderer through the Operation |
| 4 | the mask covered the phases only, and the old home-path test could not fail | plan refuter | acted | the whole page value is masked; the new test sets HOME and fails when the mask is skipped |
| 5 | "none recorded" for the bench says that spark looked, and the page never looks | plan refuter | acted | the bench line says what the page does not know |
| 6 | a crash while the flow page is written makes a passing build exit 2 with an empty output | PR refuter | acted | the keep step turns any failure of the page into one "no page" entry; the build keeps its exit code |
| 7 | `flow.py page` prints nothing when it cannot write the page in text mode | PR refuter | acted | the result carries the sentence; exit 2 |
| 8 | a breadboard.svg that cannot be read is reported as missing | PR refuter | acted | "cannot be read" when the file exists |
| 9 | `KeptFlowPage` was no Service, held a `NOUN` nobody read, and its docstring was untrue | PR lens | acted | a function, `write_kept_page`, with a true docstring |
| 10 | the first picture stood above the phases by a rule that only the renderer knew | PR lens | acted | all pictures stand in one section after the phases, with a link in the rail |
| 11 | a build record whose `stages` is not a list crashes the flow's build reader | PR refuter | raised | card [P886 #1256](https://github.com/xmejkal/spark/issues/1256) |
| 12 | after a build that did not finish, a project has no page at all (P280's rule) | PR refuter | raised | a comment on [P873 #1241](https://github.com/xmejkal/spark/issues/1241), with the question whether P280's rule is reversed |
| 13 | the PO's D7 allows one inline script and the card names tools/flow-page/; this PR builds neither | plan refuter | raised | the PO: named in the PR's text as his to reverse; the first card that needs a script brings it (P828 #1186) |
| 14 | six mutation rows of other tables would be refused by `--anchors` | the builder | rejected | dropped because the refuter ran the same on origin/main: the six are older than this PR, and P459's row 1 already raised them on P284 |
| 15 | the step that makes every build write the flow page could move to its own card | plan lens | rejected | dropped because one file with two writers, the tabbed page after a build and the flow page after `flow.py page`, would confuse a person |
