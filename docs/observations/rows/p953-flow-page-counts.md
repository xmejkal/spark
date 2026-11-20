# P953: the flow page's counts after rails by role: rows

Card: [P953 #1359](https://github.com/xmejkal/spark/issues/1359). This file holds the acted, raised and rejected
findings only. 2026-11-20.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | `tests/test_flow_page.py` failed twice on main after PR 3 (#1374): TheInlinePictureTest counted 4 jumper steps and saw 5, TheBudgetTest counted 8 jumpers in 10 steps and saw 10 in 12 | the builder of PR 4a (#1377) | acted | PR 3 puts ground through a - rail: on the drawn XIAO fixture GND, LED K and button B take three jumpers (steps 7 to 9) in place of two. Both tests now pin the new counts, with the cause in a comment; no assertion weaker |
| 2 | the hook's story run of PR 3 did not select `test_flow_page`, which reads the breadboard's steps through the page | this PR | raised | to the retro: the story run picks tests by the changed modules' imports, and the page test reads the sheet's output, not the module |
| 3 | `tests/test_golden_design.py` `test_flow_ok_page_txt` also fails on main since PR 3: the button-light page says "Step N of 9" and joins GND in rows | the refuter of this PR | acted | `SPARK_ACCEPT=flow` wrote the golden again; its diff is only the rails change: "of 10", and steps 7 to 9 join GND, LED K and button B through a - rail |
| 4 | the comment "steps 1 to 4 place a part" leaves out step 10, which places R1's end 2 | the refuter of this PR | acted | the comment names step 10 |
