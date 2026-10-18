# Keep-current sweep, 2026-10-18: finding rows

These rows go into `docs/observations/INDEX.md` when the PO has read them. The sweep read the README's "What works
today" table, `tools/journey.py` and the journey guide against what merged since v0.9.0.

| Row | Finding | Status |
| --- | --- | --- |
| KC1 | The README said a moved resistor or jumper is "not kept yet", but P287 (#350) keeps both. The journey guide already said so. Fixed in this PR. | acted |
| KC2 | The README never named P272 (the page follows the Artifact page rules). Added to the Build story. | acted |
| KC3 | The Build step's note in the picture now says a moved part, jumper or resistor is kept (2026-10-18). Its status stays "works". | acted |
| KC4 | The Bench row says the deploy grant (P242) was "tested with fakes, not yet run on a real board". No bench log for P242 is in the repository. The PO said P242 is done with the bench run. A log is needed before the row can change. | open, waits on the PO |
| KC5 | P239's refactors (LookReport, Flasher, DeployService) change no step's status or note. No edit. | no change |
| KC6 | P294 and P295 are findings (reusing Wokwi, an own live simulator). They change nothing a user can do yet. No edit. | no change |
| KC7 | The GitHub board sweep hit the GraphQL secondary limit after two calls. Board fixes were not made. See the report. | open |
