# P976: at most three plausible picks per need, word-overlap by default: rows

Card: [P976 #1406](https://github.com/xmejkal/spark/issues/1406). The PO, 2026-11-21, on the p934-epaper page: "so
many unrelated things, like some lora or other needs or boards"; his yes the same evening: word-overlap becomes the
default matcher. The plan check: a lens on Sonnet and the refuter on Opus. This file holds the acted, raised and
rejected findings only. 2026-11-21.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | `matching.shown` keeps every candidate in the first eight, so it filters nothing at a cap of three; owned junk at score 0 would take a place | the plan check, finding 1 | acted | fixed: `phase_readers.is_plausible`: the need's words (`what_matches`) or a score above 0, filtered before the cap. Row 1 of `tests/mutations/p976-offers.json` |
| 2 | the order, the current pick and the two kinds of refusal were left open | the plan check, finding 2 | acted | fixed: `need_picks` keeps the matcher's order, leaves out the current pick, counts a pick refused for its own part, and for a refusal by another need's pick gives one line with `OTHER_PICK_MESSAGE` and no offers. Tests in `OffersPerNeedTest` and `TheReviewRoundTest` |
| 3 | the says line said "held", and a refusal is not always a hold | the plan check, finding 3 | acted | fixed: three sentences in `flow_codes` with "refused"; a count of 0 is left out |
| 4 | `match_needs.py` picked the below-the-cut sentence by `needs.MATCHER`, so word-overlap as the default would say "none with the need's words" | the plan check, finding 4 | acted | fixed: keyed on `matching.SameWords.name`; row 10 |
| 5 | the P829 tests that pin refused-pick offers must change on purpose | the plan check, finding 5 | acted | fixed: each changed assertion in `tests/test_flow.py` carries a comment naming P976. The NOT_FREE sentence is gone from the page (its count stays), so `NOT_FREE_MESSAGE` and the P825 row that guarded it are removed; the P829 row on the refused offer moved its anchor to `need_picks`. The PO's to change |
| 6 | idea.md (journey) and commands/idea.md name same-words as the default | the plan check, finding 6 | acted | fixed: both rewritten; scripts.md and json.md name no default |
| 7 | the fingerprint hashes offers, not says lines | the plan check, finding 7 | rejected | dropped because a change in counts alone changes no offer, so no click goes stale; no code changed |
| 8 | the mutation rows the plan lists | the plan check, finding 8 | acted | fixed: ten rows in `tests/mutations/p976-offers.json`, each run by hand against the tests its name gives, all caught |
| 9 | the verify must show the e-paper offered first for screen with no pick | the plan check, finding 9 | acted | done on a copy of p934-epaper; the result is in the PR body |
| 10 | a need whose words no board holds (button-light's `brain`, compute / control) gets no offers with word-overlap | the build, TheRunOnButtonLightTest | raised | a card the session files from the PR body (p934-epaper's board need, "microcontroller", is matched; "control" is not). The test now reads a pick of the button |
