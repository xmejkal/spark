# UX and AI-UX lens: change tracking (P1193), with the user's journey

The UX and AI-UX lens on Opus, 2026-11-26. Its role is read-only, so the main session wrote this file from its
returned report, word for word. The times in this report are the lens's own, not read from a clock by the main session, and some are later than the commit that first held the file (council/refuter.md, "Home paths and times"). The sketches' times are examples.

Read on 2026-11-26, about 09:10 to 09:35 CET, on branch p1193-change-tracking at c0b914e2. I read the repository, the store's councils folder and part records, and two walk projects, all read-only. I used GIT_OPTIONAL_LOCKS=0 for every git read. I took the PO's decisions D2 to D5 (2026-11-26, 09:08 CET, relayed by the coordinator) as D: the shared side starts now, the central repository is a new public repository under his account, only pictures that spark or the person drew are shared, and the project timeline comes first.

## 1. Findings

Format: UX-n · claim · tag · pointer · supports only.

- **UX-1** · A real outside change happened in a project and spark says nothing. In p934-display2, the squash-merged PR e5f6be0 (2026-11-23 14:18 CET, "(#12)") changed `.spark/project.json` together with firmware/main.py, schedule.py and a test. It dropped the must line "The time and the date show within 30 seconds of a press…". needs.json last changed in 1edc3ee (11-22 19:05) and still lists the `button` need. The project has no `.spark/needs-basis.json`, because it was made before P1027 (needs_basis.py was added on 2026-11-23). For a project with no basis record, `basis_says` returns `(False, [])` (scripts/spark/flow/phase_readers.py:164-170), so the needs phase reads ok with no line. Only 1 of the 6 projects with a build record has a needs-basis.json. · E: `git show --stat e5f6be0`, `git log -- .spark/needs.json`, `ls .spark`, a python read of needs.json and project.json · caveat: whether the button need is still wanted is the PO's call (the goal still names a press) · supports D-q2: a record without a stamp should read "spark cannot tell", never silence (never-assume.md).

- **UX-2** · The PO already pushes and pulls projects to a central repository. p934-display2 has a GitHub `origin`, 36 commits, PR numbers in its subjects, 0 `spark: ` commits and 0 tags. e5f6be0 has the shape of a GitHub squash merge: four `* ` bullet lines under one subject. D11 stores `kept_step.id` as git's commit id. A squash merge on the host replaces spark's commits with one new commit. After the next pull, the kept steps list points at ids that are not on the branch, and a "back to the mark" cannot find its mark. Two problems follow for the person. "Push and pull" means one thing for his project (GitHub) and another for the store's shared side (D3). And project_commit.py:5 says spark never pushes, while his own projects are pushed. · E for the remote, the counts and the commit format (`git remote -v`, `git log`, `git tag`). The id loss after a squash is H (git's documented behaviour, not tested here) · supports D-q2, D-q3, D-q6, and the firmer mark of spark's steps that P1160 Q4 asks for.

- **UX-3** · Each word a person would naturally see for these moments already means something else in spark:
  - **tag**: a resistor's tag on the breadboard, 79 + 32 uses (breadboard/bench_changes.py:15-16)
  - **mark**: the flow JSON's key `mark`, the status glyph (docs/guide/agents/flow.md:59), and the Operation `MarkStep`, named `step` (sourcing/mark_step.py), 186 + 124 uses
  - **pull**: a pull-up resistor, 76 uses (breadboard/before_power.py:16)
  - **push**: a push button (breadboard/features_picture.py:118)
  - **pinned**, as in the 10-04 plan's "pinned commit": a pin in a group, 50 uses, in a tool where "pin" is a GPIO pin (713 uses)
  - **compare**: `compare_design`, written rules against a built design, 39 uses
  - **snapshot**: the page script's request snapshot
  - **shared**: breadboard `row-shared` and a shared net

  The catalogue's 51 Operations already include `keep`, `kept`, `keep-picture` and `step`. An agent that picks a tool by name would then see them beside the planned `kept-step` and `take-back-kept-step`. words.md:16-29 says "kept step" is not `--keep` or `--kept`, but `--describe` and an MCP list show bare names. · E: `git grep -i -w -c` per word on scripts/spark, the catalogue read, the files cited · supports D-q3, D-q4, D-q5 (naming) and P1157's table.

- **UX-4** · A part record holds text that must never reach a public repository (D3), and a field filter cannot catch all of it:
  - The shelf record epaper-2in9-bwr-mh-et-live: 2 `facts.*.source` strings hold the PO's full name and a folder path under his home that names a walk project.
  - `based_on.project` names a project in 9 of 13 shelf records.
  - `documents` holds 65 entries with vendor file names. `sources/` holds 70 PDFs, 28 JPGs and 13 PNGs, and records name vendor photos (for example DFR0457_Main_01.jpg).
  - The drawer (114 entries: `count`, `bought`, `from`, `used_in`, `photos`) is private as a whole (C7).

  A public push cannot be taken back once it is cloned. It belongs with the flash and the order ("cannot be undone", past-breadboard architect.md:166, 183), not with the take-back's yes. Git's commit author name and email travel too. · E: python reads of the store's shelf, catalog and drawer, `find sources`. The author line and "cannot be taken back" are H (git's behaviour) · supports D-q5, D-q8, and the push moment's yes.

- **UX-5** · D4 ("only pictures spark or the person drew") cannot be read from today's record. `--made-by` is a free word: "who or what made it, one word: photo, drawing, an AI's name" (sourcing/keep_picture.py:33). The one SVG says `made_by: "conversation"`. "photo" does not say whose photo. `url: null` holds 2 of 65 documents, the drawn SVG and a vendor PDF (goodisplay-…pdf), so "no URL" does not mean "drawn by us". The SVG's own `<title>` names the PO's photo and the walk P934. The document entry says `retrieved: 2026-11-20` for a picture that its credit dates from a photo of 2026-11-20 and its title ties to the walk of 11-22. · E: the store record and sources/f6a03caa…/epaper-breadboard-top.svg, the python counts · supports D4's check (a closed set of makers), D-q5.

- **UX-6** · J1's layout edit is a predicted case, not an observed one. In the 6 projects that hold a build record, no board.tsx differs from its `written_sha256`. breadboard.json exists in 1 of 42 project folders with `.spark/` (reaction-game), in a repository that has no commit. The flow never reads `written_sha256` (no hit in scripts/spark/flow or scripts/spark/core). A person's board.tsx edit shows only at the next build, as `left alone` and `traces differ` (build/kept_files.py:113-115). · E: the python read of the six build.json files, `find`, `git grep` · caveat: n = 6 · supports D-q1, D-q7. J2's outside change (UX-1) is observed, while J1 step 3 is not.

- **UX-7** · The page cannot notice an outside change when it happens. It is a file made again by spark's own writes. Its line says "If you changed or deployed something after that, type /spark:page in the chat" (flow/flow_codes.py:303-306). A click after a change is refused with "The project changed after you clicked. Reload this page" (:278). After a `git pull` or a hand edit, the page shows the old state, under a freshness line in the machine's zone. · E: lines cited · supports D-q2: "noticed" means at the next reading, not live, unless something watches the folder.

- **UX-8** · Claude cannot tell from data what changed outside spark. A phase in `show-flow` JSON has `status: stale`, `mark`, `by`, `says` (sentences) and `offers` with `makes_stale` (docs/guide/agents/flow.md:57-62). No key names the file, its kept step, the step it changed since, or whether git holds it. Codes for that last point exist only inside the git Adapter (`held_as_is`: UNHELD, NOT_ON_BRANCH, UNCOMMITTED, records/project_commit.py:69-79). To offer "keep it as a step" or "take it back", Claude must parse English. · E · supports D-q2, D-q6 (one reading for every interface, D12).

- **UX-9** · A compare can start as text, because spark already says three kinds of difference in plain words:
  - `needs_basis.changed`: "the goal", "the must lines" (flow_codes.py:36-37)
  - `_compare_traces`: traces "only in yours" (build/kept_files.py:209-211)
  - `bench_changes`: a part moved by its anchor key, a resistor swapped by its value (breadboard/bench_changes.py:15-16)

  An old point's drawings are build outputs, which D8 does not keep. To show the drawing of an old point, spark would have to build it again from that point's records, or keep the pictures. (p934-display2 tracks dist/board/*.svg by its own choice.) · E for the three differs and the tracked files. Text before drawings is H (this lens) · supports D-q4.

- **UX-10** · "Back to a mark" in a real project is refused more often than it runs. P1160 Q4 (2 of 3): spark refuses a range take-back when the person's own commit changed a file that a kept step holds. In p934-display2, the brief changed in 2 of 2 later commits, and one of them was a firmware PR. A mark set before e5f6be0 could not be returned to. The person needs to see that refusal before choosing the mark, in the list of marks, not after a yes. · E: `git log -- .spark/project.json`, the finding's Q4 · supports D-q3.

- **UX-11** · A mark as a name on an existing kept step needs no second object. The return to it is P1160's "This step and the steps after it", which already has a preview and a yes. A separate snapshot object would add a fifth word next to kept step, take-back, project timeline and the store's history. · H (this lens), from finding.md:117-126 and words.md:14-29 · supports D-q3.

- **UX-12** · Other makers cannot push to a repository under the PO's account (D3). They can only offer a change for review, as spark's own library takes only PRs (C9). The 10-04 plan also names "a reviewer's CI". So for every maker but the owner, the person's word is "offer" or "send for review", and the result has a waiting state ("sent, waits for review"). The brief puts "a git host account" out of scope, but an offer through a PR needs one. · E: C9, the 10-04 store discovery:209-217, brief Scope · the waiting state is H · supports D-q5, D3.

- **UX-13** · A pulled record can differ from the person's shelf copy of the same part. `based_on.digest` (C13) can tell them apart, but no moment says which one the build reads. The 10-04 plan reads the shared records "read-only onto the search path", so a pull would add a second source beside the shelf. The person needs one line per part: "yours", "shared, newer than yours" or "only shared". · E for `based_on`. The line is H (this lens) · supports D-q5, D-q8.

## 2. Sketches of the moments

These are proposals (H). Times are in Europe/Prague. Operation names in angle brackets are placeholders, not proposed names.

### A mark, on the page

```
+-- e-paper clock ------------------------------------------------------------------------------+
| idea ✓  needs ✓  parts ✓  build ✓  breadboard ✓  firmware ✓  deploy ✓                           |
|                                                                                                 |
| Kept steps, newest first                                                                        |
|   7  26 Nov 10:42  built the board                          [ Name this point ]    undo that    |
|   6  26 Nov 10:30  picked the e-paper for the screen                                            |
|   5  26 Nov 10:12  wrote the needs                                                              |
|                                                                                                 |
|   Name:  [ works on the breadboard____________ ]   [ Keep the name ]                            |
|   The name goes on step 7. Going back to it later takes back the steps after 7, after a yes.   |
|   ! Your own commit of 23 Nov changed the brief after step 5: going back before it is refused. |
+-------------------------------------------------------------------------------------------------+
```

### A mark, in the CLI's text view

```
$ <name-a-step> --project . --step 7 --name "works on the breadboard"
named: kept step 7 "built the board" (26 Nov 10:42 CET) is "works on the breadboard"
  To come back here, say: back to "works on the breadboard".
--json:  "kept_step": {"id": "<git id>", "n": 7, "name": "works on the breadboard"}
```

### An outside change noticed, on the page

```
+-- Now ------------------------------------------------------------------------------------------+
| ! Changed outside spark after kept step 7 (26 Nov 10:42)                                         |
|     your brief          the must lines: 1 dropped  "The time and the date show ... a press"     |
|     it makes out of date: the needs. The button need may not be needed now                       |
|   [ Keep this as a step ]   [ Show what changed ]   Take it back: ask in the chat (needs a yes)  |
|                                                                                                   |
| This page was made 26 Nov 10:45. It does not watch your files. After a pull, type /spark:page.  |
+---------------------------------------------------------------------------------------------------+
```

For a record with no stamp (UX-1), the second line reads: "? spark cannot tell whether the needs still fit the brief: they were written before spark kept a stamp. Ask Claude to read both."

### An outside change, in the CLI's text view and its JSON

```
$ flow.py show --project .
needs      ! out of date   the must lines changed after the needs were written
changed outside spark, in no kept step:
  .spark/project.json   the must lines: 1 dropped       since kept step 7, 26 Nov 10:42 CET
next: keep it as a step (writes the project, no yes)  ·  review the needs (Claude)

"changed": [{"file": ".spark/project.json", "record": "brief", "since": "<git id>",
             "held": "uncommitted", "makes_stale": ["needs"]}]
```

### A compare of two points, on the page

```
+-- Compare:  "works on the breadboard" (step 7, 26 Nov 10:42)   with   now ---------------------+
| brief       the must lines: 1 dropped                                                         |
| needs       no change                                                                          |
| parts       no change                                                                          |
| board file  yours: 2 traces only in yours (GPIO4 to DIN, 3V3 to VCC)                          |
| breadboard  the display moved 3 rows down                                                      |
|                                                                                                |
| Drawings:  [ now ]   step 7: not kept. [ Build step 7 to see it ] (writes nothing in project) |
| [ Go back to "works on the breadboard" ]  (a preview first, then your yes)                     |
+------------------------------------------------------------------------------------------------+
```

### A compare, in the CLI's text view

```
$ <compare-two-points> --project . --from "works on the breadboard" --to now
brief        must lines: 1 dropped
board.tsx    traces only in yours: GPIO4-DIN, 3V3-VCC
breadboard   moved: display, row 12 to row 15
needs, requirements: no change
```

### A push, on the page

```
+-- Share the e-paper part ---------------------------------------------------------------------+
| Goes to the public parts repository. Anyone can read it, and it cannot be taken back.         |
|   goes        name, pins, power, body size, 6 facts, the breadboard picture (drawn, near)     |
|   stays       how many you own, where you bought it, your projects, 12 shop documents         |
|   check this  2 facts name you and a folder of yours:                                          |
|                 "bench trial by <your name>, ... (<folder>/firmware/main.py)"  [ Edit ] [ Drop ]|
|   [ Share it ]   (waits until each line under "check this" is edited or dropped)                |
+-------------------------------------------------------------------------------------------------+
```

For a maker who is not the owner, the button reads "Send for review", and the record then shows "sent 26 Nov 11:02, waits for review".

### A push, in the CLI's text view

```
$ <share-part> --part epaper-2in9-bwr-mh-et-live --dry-run
would share: 1 record, 1 picture (made by: the conversation, from your photo)
would keep here: drawer, based_on, 12 documents from vendors
needs your words: facts.display_controller.source, facts.deep_sleep_wake.source hold your name
not shared. Edit those two lines, then run without --dry-run. It asks for a yes in your terminal.
```

### A pull, on the page and in the CLI

```
+-- Shared parts: 2 came in (26 Nov 11:20) -------------------------------------------------------+
|   ssd1306-oled        new to you        [ Use it ]                                              |
|   epaper-2in9-...     differs from yours: 1 fact added by someone else   [ Compare ] [ Keep mine]|
+--------------------------------------------------------------------------------------------------+

$ <get-shared-parts>
got 2 records from the public parts repository, at <id>, 26 Nov 11:20 CET
  ssd1306-oled           new, read from the shared place
  epaper-2in9-...        yours stays in use. The shared one has 1 more fact: compare to see it
```

## 3. What I could not check, and why

- I could not read the canvas artboard "Moment: undo that, take a step back". It lives only on claude.ai. The store's canvas copy (councils/p1113/canvas-2026-11-25) is from 07:48, before the artboard was added at about 20:10, and the past-breadboard ux-lens read an Undo.dc.html that is not in the store. My mark and back sketches rest on #1688's description only.
- I did not test how a squash merge on GitHub affects kept-step ids (UX-2). No scratch repository was used, and I found no project with `spark: ` commits.
- I did not test whether git's author name and email reach a public repository through spark's push. That is H.
- I do not know how a maker other than the PO reads these words. Only the PO is reachable.
- I did not run `flow.py show` on p934-display2, because the page hook writes page.html. UX-1 rests on the code path, not on a run.
- I could not tell whether anyone still wants the button need in p934-display2. That is the PO's call.
- My count of 42 `.spark` folders includes nested and walk folders. I did not match it against the projects list.

## 4. Questions for the decider

- Is a mark a name on a kept step, or a separate snapshot? · decides D-q3 and the number of words (UX-11).
- Which person-facing words for a mark, a compare, a push and a pull, given that tag, mark, pull, push, pin and compare are taken (UX-3)? · decides the names table row and every message.
- Does a kept step survive a squash merge on your GitHub projects: should spark refuse a squash, record its own step ids outside git, or accept the loss? · decides D-q2, D-q6, and the firmer mark of P1160 Q4 (UX-2).
- When a record has no stamp, does spark say "cannot tell", or stamp it now at its current bytes? · decides D-q2 for older projects (UX-1).
- Is a public push a yes typed in the person's own terminal, as for a flash, or a page or chat yes? · decides the push moment (UX-4).
- Does a `made_by` closed set (spark, the person, the conversation, a vendor) become a required field before any picture is shared? · decides D4's check (UX-5).
- Does a pulled record replace the person's shelf copy, stand beside it, or wait for the person's pick? · decides D-q5, D-q8 (UX-13).
- Should the page watch the folder, or is "noticed at the next reading" enough? · decides D-q2 on the page (UX-7).

## 5. Searches

None. There was no web, and every local read is cited as E in the findings.
