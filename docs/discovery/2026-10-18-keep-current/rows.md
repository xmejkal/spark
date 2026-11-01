# Keep-current sweep, 2026-10-18: finding rows

These rows stay here as history. Since P296 (#358) no row goes into `docs/observations/INDEX.md`. The sweep read the README's "What works
today" table, `tools/journey.py` and the journey guide against what merged since v0.9.0.

| Row | Finding | Status |
| --- | --- | --- |
| KC1 | The README said a moved resistor or jumper is "not kept yet", but P287 (#350) keeps both. The journey guide already said so. Fixed in this PR. | acted |
| KC2 | The README never named P272 (the page follows the Artifact page rules). Added to the Build story. | acted |
| KC3 | The Build step's note in the picture now says a moved part, jumper or resistor is kept (2026-10-18). Its status stays "works". | acted |
| KC4 | The Bench row said the deploy grant (P242) was "tested with fakes, not yet run on a real board". The lead corrected it: the bench run on 2026-10-18 is in the last comment on #249 and in the store record of board 8c:bf:ea:xx:xx:xx (yes: standing yes typed by petr). | open, waits on the PO |
| KC5 | P239's refactors (LookReport, Flasher, DeployService) change no step's status or note. No edit. | no change |
| KC6 | P294 and P295 are findings (reusing Wokwi, an own live simulator). They change nothing a user can do yet. No edit. | no change |
| KC7 | The GitHub board sweep hit the GraphQL secondary limit after two calls. Board fixes were not made. See the report. | open |
