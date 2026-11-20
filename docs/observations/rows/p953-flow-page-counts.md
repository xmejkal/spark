# P953: the flow page's counts after rails by role

| # | finding | source | state | note |
| --- | --- | --- | --- | --- |
| 1 | `tests/test_flow_page.py` failed twice on main after PR 3 (#1374): TheInlinePictureTest counted 4 jumper steps and saw 5, TheBudgetTest counted 8 jumpers in 10 steps and saw 10 in 12 | the builder of PR 4a (#1377) | acted | PR 3 puts ground through a - rail: on the drawn XIAO fixture GND, LED K and button B take three jumpers (steps 7 to 9) in place of two. Both tests now pin the new counts, with the cause in a comment; no assertion weaker |
| 2 | the hook's story run of PR 3 did not select `test_flow_page`, which reads the breadboard's steps through the page | this PR | raised | to the retro: the story run picks tests by the changed modules' imports, and the page test reads the sheet's output, not the module |
