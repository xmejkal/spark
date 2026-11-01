# P510 between-cards council: the twelve new cards against the open cards and the plans (round 2)

> The order holds at its top (N1 the pad-name build defect, then P507 and P508), with five changes. N6 (deploy grant) and N7
> (deploy's end) change deploy's printed lines and the grant file, so they wait for W4-2 and W4-3, as P476 did in walk 3.
> N7 waits for W4-2, not P507, because deploy reports through the seam only in E2. Three cards invent a second word for
> "what to do next" (`fixes`, `grant_command`, `next`). One agent in four roles on Sonnet 5.5.

I read `plan.md`, `cards.md`, `refuter.md`, the rows file, `wave4-plan.md`, `event-seam-plan.md`, the P469 (#637) plan, the
bodies of #702, #703, #637, #628, #634, #667, #515, #445, #430, #535, #669, #52, #505, and the code at `8595309b`.
Not checked: Ready's columns (taken from refuter R12), Miro, the bench claims, the TypeScript converter.

| # | role | finding | evidence | proposal | sev |
|---|---|---|---|---|---|
| 1 | tech lead | N7 says "after P507", but deploy reports through the seam only in E2, inside W4-2. E1 gives the look one `BEGIN` and nothing to deploy. | `event-seam-plan.md:226` (E2 is W4-2's PR, `show_line` goes there), #702 body (the look only) | N7 waits for W4-2, not P507. Its "late port" half (G40) is deploy logic that W4-2 moves, so land it after W4-2 too. | high |
| 2 | tech lead | N6 changes deploy's printed lines (the "used the deploy grant of ..." line) and the grant file's fields (project, count), and adds a `grant_command` key to the gate-stop envelope. W4-2 retargets 34 deploy mutation rows and W4-3 moves grant onto the core. Walk 3 moved P476 behind W4-2 for the same reason. | `wave4-plan.md:111` (34 rows), `:15-16` (W4-3 is grant, live, reach), P480 between-cards row P476 | Split N6. N6a, XS, now: the deploy page tells Claude to offer the existing `grant.py --scope deploy` command once, and the question says what it covers. No code. N6b (count, project, used-line, serial words) after W4-3. This still serves the PO's I3 (ten yeses) at once. | high |
| 3 | AI/UX | Three cards name "what to do next" three ways: N4 a new `fixes` list, N6 a new `grant_command` key, N5 a `next` on the build verdict. The contract has one word: an item's `fix` (a sentence) and the envelope's `next` (commands with effects). `check_spine.py` has no `next` key today. | `docs/guide/agents/json.md:234,256` (`fix`, `next`, "no operation fills it"), `json.md:140` (check_spine keys: `check, stages, status, kept`) | N4 and N6 put their commands in `next` as `NextStep`s, carried with P473's `env`. N5 says which key it adds to `check_spine --json` (`next`, one step) and updates `json.md:140`. No new key. | high |
| 4 | AI/UX | N4's third fix, "raise the owned count" with the `--drawer-set` line, lets Claude unblock a pick by editing what the person owns. The count is a fact about the person's drawer, so it is not Claude's to change. | `never-assume.md` (a null or a count is no value to fill in), N4 "The change" | List the third fix as a question for the person: "only if you own another one". Its command is not a `next` step that Claude runs. Test: the JSON marks it `needs the person`. | high |
| 5 | senior | N1's Done when says `BoardPads` is "the only Python reader of `pad_aliases`". `boards.py:694` (the validator) and `parts.py:189` (a comment) also name it, and `breadboard.py:150,315`, `assign_pins.py:418` read it. | `/usr/bin/grep pad_aliases scripts/*.py` | Reword to "the only code that maps a pin label to a pad". The validator may read the raw dict. Say so in the card, so the grep test does not fail on its own PR. | medium |
| 6 | senior | N2 cites `design.py:128-150` for the refusal "both TFT_BL". That range validates the file's `signals` list. The refusal text is at `design.py:376-382`, in the derive step. | `design.py:130-150` (shape checks), `:380` (the message) | Cite `design.py:376-382`. The fix goes where signals are derived: a signal named like a part's signal sets that signal's pin instead of adding a second. | low |
| 7 | senior | N9 takes the flash size from the look's `BoardReading.flash_mb`, but `flash_image.py` has no reading and no look. The reading would be a new parameter through deploy, which W4-2 rewrites. | `flash_image.py` (no `flash_mb`), `board_look.py:44`, `deploy.py` | Two choices: pass the size by one explicit argument `--flash-mb` now (small, testable), or move N9 behind W4-2. Pick the argument. Label it story, not bug, since it adds a capability. | medium |
| 8 | senior | N12 puts `labels` on `onboard_button`. With labels the plain name `ONBOARD_BUTTON` disappears and only `ONBOARD_BUTTON_USER` and `_BOOT` remain. The record's `gpio: [47]` drives the pick and the scenario, so adding GPIO0 to `gpio` would offer BOOT as the button to press. No board record uses `labels` for a button today. | `assign_pins.py:435-437,453` (labels replace the plain name), `boards/*.json` (grep `"labels"`: none), `firebeetle2-esp32s3.json:250-256` | Keep `gpio: [47]`. Add `labels` only. State in Done when that `ONBOARD_BUTTON` stops existing, and that `ONBOARD_BUTTON_ON` stays. A test imports the old name and gets the card's own message. Merge the rename warning into the PR text. | medium |
| 9 | tech lead | P469's edit adds "deploy enters download mode by `machine.bootloader()`" to a card in Build with its plan held. Deploy is W4-2's. The look is already on the core. | #637 body, plan header "HELD for the PO", `wave4-plan.md:86-92` | Two slices in the P469 edit. Slice 1, the look reads through mpremote (the held plan, decision 2). Slice 2, the no-hands entry in deploy, after W4-2. Decision 2 of `plan.md` is the gate for both. | medium |
| 10 | PO assistant | The plan ranks N6 at 5 "ready only after decisions 1 and 3", with N2 holding rank 5 until then. A rank that depends on two answers will block Ready's limit of 5. | `plan.md` order table, rank 5 | Rank N6a (finding 2) in the top 5, and N6b outside Ready. N2 gets rank 4 for good: it follows N1, is S, and finishes the module journey the PO asked for in A1. | medium |
| 11 | tech lead | N8 puts one "a scenario can reach this pin" reader into `--match`, `--pick`, the build and the look. P399 (#515) PR 1 builds `ScenarioSteps` with component ids from `sim/diagram.json`. P469 slice 2 also edits the look. Two readers of one fact is the pattern the PO prunes. | #515 "The change", `plan.md` N8 row | N8's change reads the fact P399 PR 1 exposes, or N8 states that it is the one reader and P399 reuses it. Put one line in both cards. N8 lands after P469 slice 1 so the look's text changes once. | medium |
| 12 | AI/UX | N7 says "the port came back after N seconds, read it again", but its Done when says "ready with no retry by Claude". The text tells Claude to retry what the card removes. | `cards.md` N7 "The change" and "Done when" | The sentence says what happened and nothing to do: "the port came back after N seconds. The board is ready." `ready unknown` stays only when the wait ran out. | medium |
| 13 | AI/UX | One word for one thing breaks in three places. "drop" means a need (N3) and a pins.py line (P460 edit). "free" and "release" both mean a hold's end. P460's body says "plug", the plan says `kind` and "part plugs into". "Stage" means the chain stage in N8's title and the walk's step elsewhere. | `cards.md` N3, N4, P460 edit; `plan.md` "Names" paragraph; `patterns-and-names.md` rule 1 | One word each: `drop` only for a need (`--needs-drop`), `free` for a hold, `remove` for a pins.py line. P460's edit renames its "plug" to "connector" and "plugs_into". N8 says "the chain's stages" in its title. | low |
| 14 | AI/UX | Codes N1 to N12 repeat P480's N1 to N11 (P490's body cites "N10" of walk 3; N3 of walk 3 is the diagram, N3 here is drop). A reader of `rows` meets two N3. | #669 "Source" (N10), `p480-walk3-council/between-cards.md` | In every card and row write "N3 (walk 4, drop a need)" until the PO files them, then use only the P number. | low |
| 15 | senior | N3's `effects` names the file. P488 (#667) is about to replace `effects` text with `place` and `path` for every write, planned with P481 (#660). A third copy of the wording appears if N3 comes first. | #667 "The change" | N3 declares `effects` in today's form and cites P488. P488's PR then updates `DropNeed` with the other writers. No second field. | low |
| 16 | PO assistant | Every new card serves P100 (#6) and has the PO's words, except N11 (stand-ins), N12 (BOOT) and N10 (interpreter name): their "Needed by" is a gap, not a PO sentence. N11 is a chore with a workaround the walk found (`import` inside a function). | `cards.md` N10, N11, N12 "Needed by" | Keep the order (13 to 15). Mark N11 and N12 as "ride-along": they enter Ready only as a pair with a card that touches `import_firmware.py` or a board record. | low |
| 17 | PO assistant | N5 holds two surfaces: the idea page order (a skill text) and the build's next step (code in `check_spine.py`, which N1 also edits). Sized XS. | `cards.md` N5, `check_spine.py:496` (N1 too) | Size S, or split: N5a the skill page (XS, now), N5b the build's `next` after N1 and P473. | low |

## Dependencies that the plan does not state

- N1 then N5b, because both edit the verdict in `check_spine.py`. N1 then N2, as stated.
- P473 (#647) before N4, N5b and N6a: they put commands in `next`, and `env` names the store.
- N3 before N4, as stated. N3 and P488 touch `effects`: either order, one wording.
- W4-2 before N6b, N7, N10 (its "last deploy" fields change what deploy writes) and P469 slice 2.
- P511 (#706) before N9 and N10, as stated. N9 takes the size by an argument (finding 7).
- Edits to open cards (P460, P466, P490, P409, P336, P349, P399, P118, P488, P390, P492) only add a section. None
  conflicts with E1 or E2a. P118's first PR (`check_all.py:466`) and N5b share no file.

## The order I propose

Same as `plan.md` for ranks 1 to 3. Then:

| rank | card | change |
|---|---|---|
| 4 | N2 | up from 6: follows N1, finishes the module journey (A1) |
| 5 | N6a | the offer of the existing grant, a docs change, XS (finding 2) |
| 6 | N5a | the skill page. N5b joins after P473 |
| 7 | P473 (#647) | as before, now a dependency of N4, N5b and N6a |
| 8 | N3, then N4 | as before |
| 9 | N8, N12 | N8 after P469 slice 1 |
| 10 | after W4-2: N7, N6b, N10, N9, P469 slice 2 | N11 rides with a card that touches the import child |

Ready at the start: N1, P507, P508, N2, N6a (P473, P503, P506 leave, as `plan.md` already says for the last two).

## What waits on the PO

The OK on the order above and on splitting N6 and N5. The four decisions in `plan.md` stay open. Decision 2 (does the
yes for P469 cover `machine.bootloader()`) gates P469's slice 2.
