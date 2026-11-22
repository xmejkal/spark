# P993: the page and /spark:page say what blocks the next step, and offer a step only when it can run: rows

Card: [P993 #1446](https://github.com/xmejkal/spark/issues/1446). The gaps come from the p934-display walk of 2026-11-22
(`~/Development/spark-walks/p934-display/diary.md`) and P991's rows. The plan check: a lens on Sonnet and the refuter on
Opus, one round. This file holds the acted, raised and rejected findings only. 2026-11-22.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | /spark:page outside the session's folders: publish_files refused page.html | the walk p934-display, row 6 | acted | commands/page.md step 0: ask for `/add-dir` first, never copy page.html |
| 2 | the guide line with the button says "Ask Claude in the chat" | the walk, row 10 | acted | the four NOW sentences of the parts list and the build name the step only; on the published page the script adds "Use the button." before the NOW button (plan council lens 1). `tests/flow_script` and row 6 of `tests/mutations/p993-blockers.json` |
| 3 | "Write the parts list" offered while no need has a pick | the walk, row 5 | acted | `RequirementsReader` offers the parts list only when `need_requirements.requirements` has no problems. `TheBlockersTest.test_no_pick_offers_no_parts_list`; rows 1 and 2 |
| 4 | the e-paper owes a simulation stance, unsaid before the click | the walk, row 12 | acted | the rule's lines are the phase's says; an owed fact is said by the part's name, its need and the fact, in plain words (plan council lens 2). The walk copy: `“MH-ET LIVE 2.9 Inch E-paper Module, …” for screen still lacks what spark needs: simulation. Ask Claude how to fill it in.` Rows 1 and 5, and a page test |
| 5 | "Picked for board: C6" above "… refuses this pick" | P991's rows, row 25 | acted | `NO_NEW_PICK_MESSAGE`: `Spark can save no new pick for board: the pick for button, wifi cannot get “DFRobot FireBeetle 2 ESP32-C6” (…).` Row 4; P976's row re-anchored |
| 6 | group a need's Pick buttons under its pick | P991's rows, row 4 | raised | not MVP: a later card, which the session files |
| 7 | the parts phase says ok while its own picks cannot get their part (the C6 held elsewhere), and the line repeats per need | the plan's run | raised | a later card, one line, which the session files |
| 8 | with every counted need picked, a refusal of the parts list makes `flow.py show` exit 1 | plan council lens 3 | rejected | no command calls `flow.py show`; /spark:page runs `flow.py page`, which exits 0 (the walk copy), and the guide's "the phase has problems" says what to do next |
| 9 | the merged refusal sentence is long; rows 3 and 4 could fold into tests | plan council lens 4 and 7 | rejected | dropped because MVP first: the sentence is true and the rows are each caught by a test |
| 10 | mutation row 4's anchor occurs four times | plan council refuter | acted | the anchor is `NO_NEW_PICK_MESSAGE % (need, `; `--anchors` refuses none of the new rows |
| 11 | no page test for a pick that owes a fact | plan council refuter | acted | `test_flow_page.TheCommandTest.test_a_pick_that_owes_a_fact_gives_no_parts_list_button_and_shows_what_it_owes` |
| 12 | "Ask Claude to fill it in" is not true for a record in spark's own library, filled by a commit in spark's repository | PR lens (Sonnet) | acted | fixed: `Ask Claude how to fill it in.` |
| 13 | the requirements-file test pins no says line | PR lens (Sonnet) | acted | fixed: it pins both lines of the refusal |
| 14 | the parts' NOW line can carry a pick button, so "Use the button." stood after "Tell Claude a pick" | PR refuter (Opus) | acted | fixed: the script adds it on a `<p>` whose key is no pick; a JS assertion and row 7 |
| 15 | a pick stored as its drawer entry is named with no need | PR refuter (Opus) | acted | fixed: `needs_holding` reads each pick through `needs.as_record`; a test and row 8 |
| 16 | the owed line was chosen by the rule's sentence (`startswith("owes ")`) | the hook's quick run, test_no_magic_strings | acted | fixed: the record's owed facts decide (`owed_facts`), never the sentence |
