# P510 council: UX and AI lens (Sonnet 5.5)

> A deploy grant already exists (P242), so C6 is not new: it is a grant that spark never offers when the person needs it. The grant names no project and no image, and a file in the store holds it, which Claude can write. The automatic mode is safe only if the yes is narrower than today's, not wider.

## Findings

| # | finding | evidence | card or plan | proposal | severity |
|---|---|---|---|---|---|
| 1 | C6 says the standing yes is new. A deploy grant for N minutes exists, with a standing-consent strategy. | `scripts/board_grant.py:85` (DEPLOY_QUESTION), `:172` (StandingConsentStrategy), `scripts/grant.py:41` | C6 | Rewrite C6 as: offer, narrow and extend the existing grant. Do not build a second yes. | high |
| 2 | In the walk, deploy.py printed the grant line once (step 17) and Claude gave the person the paste line. The grant was never offered again. | diary step 17 ("printed the line ... and the deploy grant line"), S6, S13, S16, S19, S22, S24, S27, S29, S30, S34: ten typed yeses | C6 | After a gate stop with `no_terminal`, the JSON carries a `grant_command` key. The skill page tells Claude to offer it once per session. | high |
| 3 | From step 20 every deploy ran with `--no-simulation`, and a grant never covers that. So the grant would not have helped. | `board_grant.py:107`, `image_evidence.py:353`, diary step 20 | C6 | Keep the exclusion. A person who wants no-simulation images in the automatic mode types a second, named yes (see "The standing yes"). | high |
| 4 | The grant question says "write any passed image of any project". It names no project, no image and no count. | `board_grant.py:85`, `Grant` fields at `:41`: mac, token, who, when, until, scope | C6 | Add the project folder and a deploy count to the grant. The question names both. | high |
| 5 | The grant file is a plain JSON file. The code says "anything that can write your store can write it". Claude has Bash and can write it. | `scripts/grant.py:27-33` (epilog), `board_grant.py:150` (`store.write_json`) | C6 | Safety lives in the permission system, so `/spark:init` writes a deny rule for `grants/**` in the project settings. The synthesis decides if a signature is worth its code. | high |
| 6 | The no-hands download mode runs `machine.bootloader()` on the board. That is code on the board, which the live scope covers, not the deploy scope. | P472 finding step 9 in diary; `board_grant.py:14` (two scopes) | C6, P469 | One question names both acts: enter download mode with fixed text, erase and write. See P469 below. | high |
| 7 | P469's plan pins `--after hard-reset`. C6 uses `--after watchdog-reset`. The two differ and neither card says why. | plan `p469-look-without-restart.md` line 28, rows C6 | C6, P469 | Say: hard-reset after a read, watchdog-reset after a write. Mark "not checked on the bench" until P509's step 59 evidence is cited. | medium |
| 8 | `grant.py --check` looks for a live grant only. Claude cannot ask whether a deploy grant holds. | `grant.py:36` (epilog, last line) | C6 | `--check --scope deploy`, with the minutes left and the project in the JSON. | medium |
| 9 | Claude Code's auto mode refused deploy.py in walk 3 and let it run in walk 4. The gate inside deploy.py held both times. | diary O4 | C6 | Never rely on the host's auto mode. Keep the gate in deploy.py as the only gate. | medium |
| 10 | The refusal for a held board gives two fixes. The third (raise the count) and the key that `--drawer-set` needs are missing. | diary G6, G7, step 3 | C4 | Add both to the refusal and to a `fixes` list in `--json` (see C4). | medium |
| 11 | The build verdict ends with a fact, not a next step. The person did not know what to ask (stall S3). | diary S3, G11, step 7 | C5 | Add one last line (see C5). | medium |
| 12 | Three stages say three things about the Wokwi run. Claude had to merge them by hand. | diary G10, step 6 | C7 | One fact in the board record, one sentence from one function (see C7). | medium |
| 13 | `ready unknown` came 3 times after a late port. The words do not say "try again". Claude took 3 reads to find out. | diary G40, step 43 | C6 | Say "the port came back after N seconds, read it again", and retry inside deploy.py first. | medium |
| 14 | Claude read the s3lcd start as a crash at each try, five times. The person's next message showed it ran. A silent port gave no signal. | diary step 58, G45 | C8 | When a build reports a fixed serial, the look says "the firmware may have taken the USB port. Ask the person what the screen shows." | medium |
| 15 | Claude wrote the goal into `project.json` by hand, because init left it empty. Claude also fetched `firmware.bin` itself to get a sha256. Both are work-arounds that no spark message offered. | diary steps 5, 57 | C5, C8 | Add the goal to init. Add a `--sha256` line to `tools.py --new`. | low |
| 16 | A sub-agent contradicted its own tables, and another read a datasheet further than its text. Claude caught both by reading the source. | diary O5, O8 | C2 | A record keeps `verified: false` for a pin read off an image, and the pick says so in words. Already so for O5. Keep. | low |

## The standing yes (C6, the person's I3)

A standing yes must name five things, all shown in the question the person types:

1. The board: its MAC and token. Today's grant has this.
2. The project folder. Today's grant has none. A yes for walk4 does not open a deploy of another project.
3. The act: "enter download mode on the board, then erase ALL of the flash and write". Today's question says only the erase.
4. The limits: N minutes (1 to 1440) and a count of deploys, for example 10. The grant ends at the first of the two.
5. The image rule: only an image that a simulation passed. A separate second yes in the same terminal line names `--no-simulation` images, with the words "no run tested this code".

Where it lives, in order of strength:

- The question and the answer happen in the person's own terminal. The code already checks this (`TerminalConsentStrategy`, `grant.py` exit 2 without a terminal).
- The record lives in the store as now, with the project and the count added. It is a fact for deploy.py and the board log, not a defence.
- The defence is the permission system. `/spark:init` writes a rule that denies Claude writes to `grants/**` and to `grant.py`. Without that rule a grant that Claude writes looks the same as a grant that the person gives. Mark this "not checked": I did not test Claude Code's deny rules.
- Every use prints one line in the answer: "used the standing yes of Petr, 4 of 10 deploys, 38 minutes left". Claude must repeat that line to the person (the strategy's `who` text, `board_grant.py:181`, already holds the base).

Message for the person, plain words: "Let Claude put firmware from the folder walk4 on the board 8c-bf-ea... for 60 minutes or 10 deploys. This erases ALL of the board's flash each time and starts the board in download mode with no button. Claude still stops for any image that no simulation tested."

Message for Claude, in the JSON when no grant holds: `grant_command` (the exact line for the person), `grant_scope` ("deploy"), `covers` (project, act, limits). Rule for the skill page: offer the grant once, after the first gate stop, then stop asking.

Comparison with P469 (#637, held for the PO):

- P469 asks if a read-only mpremote snippet may run with no grant. My view: yes, with the snippet text fixed in the docs and shown in the JSON as `read_by` and `restarted`.
- C6 goes one step past P469: `machine.bootloader()` is not read-only. It restarts the chip into download mode. So P469's yes does not cover it, and the standing yes must name it.
- Order: P469's decision first, because C6 reads its `read_by` field to say to the person how the board was entered.
- P469's plan has no cap on time or count, because a read changes nothing. C6 needs both, because it erases.
- P469 says an S3 or C6 stays in download mode after `hard-reset` from a BOOT entry. C6 must use `watchdog-reset` after a write only. State this in both plans.

## C1 to C11

| card | verdict | why and the change |
|---|---|---|
| C1 `pad_aliases` bug | keep | The message gap (G30) is the UX part. The verdict names the trace: "no wire reaches pad MO (alias of MOSI) on U1". Done when the JSON carries `trace` and `pad`. |
| C2 module on a fixed connector | merge into P460 (#628) | The pick must say it in words: "dfr0664-tft-2in plugs into GDI. GDI backlight and the onboard LED share GPIO21." Claude needs a `shares` list per pin in the JSON. |
| C3 remove a part | keep | Message: "removed light. pins.py no longer names ONBOARD_LED. firmware/main.py still imports it (line 4)". Dry run first. |
| C4 presets and holds | merge into P466 (#634) | Rewrite below. |
| C5 first steps | rewrite | Rewrite below. |
| C6 automatic mode | rewrite, merge into P469 (#637) | The change: offer, name and cap the existing deploy grant, and add the no-hands entry under the same question. Done when a person types one line, a second project is refused by the grant, and a fake clock ends it by time and by count. |
| C7 one honest word | merge into P490 (#669) and P409 (#535) | Rewrite below. |
| C8 own MicroPython build | split | Two cards: the carry (G42, G44, G46) and the words (G37 to G39, G45). The words are small and go first. |
| C9 free firmware tests | merge into P492 (#671) | Message gap only: the stand-in notice must say which names it fakes. Not checked in code. |
| C10 BOOT as a button | keep | Small. The caveat text is the UX part: "GPIO0 is the BOOT button. Held at reset it enters download mode." |
| C11 C driver | keep, outside spark | Its UX returns: a USB console that stays alive, so the look can read the board (G45). |

C4 rewrite. The change: a refusal names three fixes in order (free a hold, raise the count with the entry key printed, pick another) and gives `fixes` as a list of exact commands in `--json`. `--drawer` prints each entry key. A preset starts from "clean" or "one free board". Done when a refused pick prints the key and the third fix, and `--drawer --json` has `key` for each entry.

C5 rewrite. The change: step S writes the goal into the brief, or says "run /spark:init first". The build verdict ends with "next: write firmware/main.py from pins.py, then run look.py". The `--needs-set` dry run says "would write .spark/needs.json and list walk4". Done when a new project's first build ends with the next step and the brief holds the goal.

C7 rewrite. The change: one function in the board record turns "a scenario cannot reach this pin" into one sentence. `--match`, `--pick`, the build and the look all print it. A must line that no run can test is marked "bench only", and the look lists it even with `--no-simulation`. Done when the four outputs show the same sentence and a bench result has a store place.

## New cards

- P? — a grant that spark offers late and names loosely → a deploy grant that names project, act and count. Need: the person's I3. Done when C6's test above passes and `/spark:init` denies Claude writes to `grants/**`.
- P? — Claude cannot ask if a grant holds → `grant.py --check --scope deploy --json`. Need: the skill page offers the grant once, only when none holds. Done when the JSON shows scope, project and minutes left.

## Not checked

- Claude Code's permission deny rules for a path in the store. I did not run them.
- Whether `watchdog-reset` after a write works on the S3 and C6 beyond the diary's step 59.
- Skill page text for `/spark:deploy` and `/spark:idea`: I read the grant code, the diary and the rows, not every page.
- G5, G8, G13 and G16 (rows open since walks 2 and 3): no message reading done.
