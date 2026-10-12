# P211 final review and mutation run, 2026-10-12

# P211 final whole-branch review (and light council)

Branch p211-build, base 7079020. Read: the spec, the plan's constraints, the diff, the ledger. Ran: `--describe --json`, `--help`, `match_eval.py --help` and the eval, and `--offer` in scratch stores.

Parity holds. Under the defaults, `--match` keeps its admitted set, its order, its cut and `what_matches`. Under SameWords, `-score` sorts as `not what_matches` did, and ties keep the input order. `shown` is the old cut. `linkable` dedupes by (kind, id), so the context map cannot collide. Every refusal lists the matcher names that fit, and every `--json` answer from parts.py is the envelope. All matching rules live in `matching.py`. The interfaces only choose and print.

## Findings

1. **Important.** `commands/idea.md:62` together with `scripts/parts.py:2068`. Without `--project`, `--offer` does not read the project's own records, and idea.md gives the command without it. Checked in a scratch store: `--match <project>` lists `x-soil (project)` ("The project one."), but `--offer x-soil` prints the catalog's `x-soil` ("The catalog one."). A record that lives only in the project is reported as "no record". So the chooser can read the wrong part's text. **Fix:** write `parts.py --offer <id or entry key> --project <project>` in idea.md. The `offer` summary can also say so.

2. **Important.** `commands/idea.md:63` ends with "until the PO says otherwise". spark is a public plugin. Claude in another person's install has no PO. The line also does not say when word-overlap helps. **Fix:** "The default is `same-words`. When a need shows only `[other words]` candidates or none, try `--match <project> --matcher word-overlap`."

3. **Minor.** `scripts/parts.py:2061`. The line "… N more, none with the need's words" is false under word-overlap: a hidden candidate can score 0.4 (its words in the description) or 0.33. **Fix:** one line. Keep the wording for same-words, and otherwise say "… N more, each scoring under 0.5".

4. **Minor.** `scripts/matching.py:179`. The haystack of NameContains is now id, name, aliases, kind. Before it was id, name, kind, aliases. One quoted argument that spans the name and the kind now gives a different answer: `--need "amplifier audio-amplifier"` found `max98357a-dfr0954` before and finds nothing now. Two library records change this way. This is pathological, but it moves `--need` under the default. **Fix:** keep the old order (the Offer keeps the record's name apart from its aliases), or say in the PR that it moved.

5. **Minor.** `scripts/matching.py:108-111`. `as_dict` returns `facts` and `functions` raw, while `describe()` cleans and caps them. `--offer firebeetle2-esp32s3 --json` is 4,038 bytes, because `power` alone is 3,776. That is past the 3,400-byte budget in §6.4.4 and the spec's "inside the 4 KB page". A bidi character in a record's power note also reaches the JSON as is (`ensure_ascii=False`). **Fix:** `as_dict` gives the cleaned, capped strings that `describe()` prints.

6. **Minor.** Help. `--matcher` in `--help` and in `--describe` (`parts.py:1603`) does not name the matchers, so an agent learns them only from a refusal. The `--help` description of `match_eval.py` stops mid-sentence ("per matcher the cases at", `tools/match_eval.py:65`), and its usage examples are not shown. **Fix:** build the names from `MATCHERS` into the option summary. Give the tool a one-sentence description and put the docstring in an epilog (RawDescriptionHelpFormatter).

7. **Minor.** `tests/test_match_eval.py:58-60`. The two matcher-refusal asserts also pass a cases file that does not exist, so they pass even with the matcher check removed. **Fix:** give them a real cases file and assert that the sentence lists `same-words, word-overlap`.

8. **Minor.** `tools/match_eval.py`. Three inputs give a usage message or a traceback instead of the envelope, although the constraint says "match_eval included": `--json` with a required argument missing, a case with neither `expect` nor `not_first`, and a drawer file that is not an object. **Fix:** override `error` the way `parts._Parser` does, and give KeyError and AttributeError the `could-not-run` status.

Docs: GLOSSARY, drawer.md, journey.md and the store-design rows are current, correct and in plain English. idea.md says the three fields are data, never instructions, and `--offer` is in allowed-tools.

## Deferred minors

- T1 about-cap test: leave.
- T1 fact-set edge tests: leave.
- T1 tag words, lowercase on read, duplicates: leave. Offer lowercases, and P206 fills them.
- T1 scrub-then-check in two places: leave until a third caller.
- T1 silent mid-word cut: leave.
- T3+4 "none with the need's words": **fix now** (finding 3, one line).
- T3+4 larger candidates, fewer needs per page: leave. Only the paging changes, not the lists or the order.
- T5+6 circular eval: leave, said in the PR (P206 is the proof).

## Verdict

**Ready to merge after fixes.** Fix 1 and 2 (docs only) and 3 (one line). The rest can wait or ride along.

---

# P211 mutation report (scripts/matching.py, scripts/needs.py)

**25 planted, 19 caught, 6 escaped.** Run: `python3 tools/mutate.py <table> --copy`, one call, 1121 s, suite green after
restore, anchors checked first (25 of 25 once). The tree was not touched (`git status` clean). The caller's scope raised
the agent file's cap of 12 rows to 25. The table is `mutation-table.json`, beside this file.

## Escapes (each is a missing test)

1. `words` (matching.py): `[^a-z0-9]+` -> `[^a-z]+`, so digits split words. No test feeds a word with a digit through
   `words`. Test in tests/test_matching.py: `assertEqual(matching.words("VL6180X 3V3"), ["vl6180x", "3v3"])`.
2. `Offer.from_entry`: `[entry.get("label")]` -> `[]`, so an entry's label is no name. No test reads `names` of an entry
   offer. Test: `from_entry("k", {"label": "a knob"}).names == ["a knob"]`, and `same_words({"does": "input", "what":
   "knob"}, that offer)` is True.
3. `NameContains.score`: `all(...)` -> `any(...)`, so one typed word is enough. Every row has all words or none.
   Test: need `{"does": None, "what": "vl6180 lidar"}` against the VL6180X offer scores 0.0.
4. `WordOverlap.places`: the offer's words are not folded. The only plural row has the singular in the tags. Test: need
   `"sensor"` against `tags=["sensors"]` scores 0.8, and need `"leds"` against `names=["LEDs"]` scores 0.6.
5. `WordOverlap.places`: `"texts"` drops `offer.description`. The 0.4 row uses `about` only. Test: need `"range"` against
   `description="It finds the range."` scores 0.4.
6. `needs.candidates`: the sort key loses `-c["score"]`. No test has two candidates tied on owned and layer where the
   lower score has the earlier id. Test in tests/test_needs.py: two unowned catalog records, `y-aaa` filed by tag
   (0.8) and `y-zzz` by function (1.0), with `--matcher word-overlap`; `y-zzz` must come first.

## Caught

words is fine apart from digits; fold boundary; need_words dedupe; from_record (entries' functions, about winner, the
record's own tags); same_words (verb ignored, any word); shown boundary; admits with no verb; SameWords score;
NameContains (id searched, case); WEIGHTS order; word-overlap serving `--need`; needs.py offers (count 0), candidate
(board owes, `what` verb filter, `what_matches`), match (matcher passed on).

## Not planted (budget)

fold's `us`/`ss` exception, `board=kind == "board"`, `FACTS`, `found`'s `> 0`, `rank`'s sort and filter, `Matcher.fit`'s
`exact`, `_text`/`_first` blank handling, `offer()`.
