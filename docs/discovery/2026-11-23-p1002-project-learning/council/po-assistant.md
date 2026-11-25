# P1002 council: the PO assistant

The lens: the product's value (Existing first, Risks and assumptions). Read on 2026-11-23, 14:50 to 15:20 Prague
time. A path that starts with `store/` is under `~/.local/share/spark/`.

## Jobs it sees

- J1. When a bench session settles a fact about a board or a module [E diary.md:275-276, 418], I want spark to offer
  to keep it with its source [D the PO 2026-11-22, diary.md:288]. Then the next project does not find it again [D the
  PO 2026-11-23, card #1461].
- J2. Before spark keeps a fact, I want to see what was learned [D the PO 2026-11-23, #1461]. Then nothing false
  reaches the store [H from PO-9].
- J3. When a kept fact proves wrong, I want to undo the change [D the PO 2026-11-23, on P1027 #1506]. Then a mistake
  costs one step.
- J4. I want one setting for the store and one for a project [D the PO 2026-11-23, "lets also make it
  configurable"]. Then the habit fits each project.

## Findings

- PO-1 · The job is real and recent. On 2026-11-22 the PO asked twice, with no prompt, whether bench findings get
  kept. His first words: "do they get to be stored about them? like now that we found out which driver works.." ·
  E · ~/Development/spark-walks/p934-display2/diary.md:275-276 and 418 · supports only: one person, one
  walk, two days.
- PO-2 · In the diary lines I read, the session never offered first. Each keeping started from the PO's question.
  Then came a dry run, then his yes · E · diary.md:275-286, 418-428 · supports only: that walk. I did not read all
  564 lines.
- PO-3 · The review step exists today, by hand. Every write in the walk was a dry run first. The real write came after
  the PO's yes · E · diary.md:277-279 ("Waits on the PO's yes"), 286, 418-428 · supports: the review shape works at
  the bench.
- PO-4 · Spark keeps part facts with a source today. `parts.py --fact-set` writes `facts` entries {value, verified,
  source} into a part record. Then it refreshes the shelf copy. Its answer holds `was` and `now` · E ·
  scripts/spark/sourcing/set_facts.py:29-31 · supports: the part half of J1 exists, with no offer.
- PO-5 · For a board, the writer takes only `pin_roles` and `joined_pads`. A person wrote the deep-sleep facts of
  2026-11-23 into the board record by hand · E · missing_facts.py:48-49 (in scripts/spark/records) · E · the note
  `//deep_sleep` in store/shelf/boards/firebeetle2-esp32c6.json · supports: the board half of J1 has no route today.
- PO-6 · Undo today is a hand copy. The two writes of 2026-11-23 left copies in a new folder, store/backups/, at
  14:38. A write on 2026-11-22 kept its old copies in a session scratchpad · E · `ls -la store/backups`, diary.md row
  15 · supports: J3 is met by hand, once. An agent cleans its scratchpad at its end (CLAUDE.local.md). So that older
  copy is likely gone (H).
- PO-7 · "Probably git" meets a written rule. The shelf and the board shelf are private places. Spark refuses to write
  a private place inside a git work tree. The reason in the code: one `git add .` publishes them · E ·
  scripts/spark/records/store.py:143-145, 341-345 · supports: for a git repository in the store, the PO changes §5.8,
  or the history lives outside the store. The tech lead report has the detail.
- PO-8 · No setting place exists. Only tools.json has a store copy and a project copy, merged entry by entry · E ·
  scripts/spark/records/tool_finder.py:6, 41-43, store.py:108-112 · supports: J4 has a pattern to copy, not a home.
- PO-9 · A wrong fact reached a record in the same walk. The PO found it, not spark. The 13:14 source said "both
  runs, as the person watched". The PO saw only the first run. The fix came at 14:08 · E · diary.md:368-370, row 21 ·
  supports: today the review in J2 catches errors. One case.
- PO-10 · The reach is small today. Of 27 listed projects, two name these records. p934-epaper holds its own copies.
  p934-display2 reads the shelf copies · E · a read of store/projects.json and each project's requirements.json on
  2026-11-23 · supports: no second, different project uses a learned fact yet. The benefit for the next project is a
  belief (H the PO's words).
- PO-11 · Nothing in spark reads a board's `deep_sleep`. Only the library's two boards hold the key, plus one search
  word in datasheets.py · E · `grep -rn deep_sleep scripts/ boards/` · supports: a later project finds a kept fact
  only through the conversation. Spark itself does not show it.
- PO-12 · Three cards on the board overlap. The P1003 #1462 pre-analysis asks to fold its trial results "into P1002's
  keep-a-finding path". P998 #1457 is a fact that research cannot settle. P1027 #1506 rolls back a change to the
  project's own lines · E · the P1003 comments and the two titles (gh) · supports: one keep-a-finding
  path, built once, serves three cards.
- PO-13 · The product's rules decide the content. Spark exports facts, never behaviour. Records grow by need. A null
  is never a typical value. Every fact has a source · D · AGENTS.md, Principles, and the brief's "Already decided" ·
  supports: the scope.
- PO-14 · One kept fact is close to behaviour. The board's `light_sleep` value ends "Do not use lightsleep on this
  board with this build" · E · store/shelf/boards/firebeetle2-esp32c6.json, `deep_sleep.light_sleep` · supports: a
  writer that runs alone needs a rule for fact against instruction.
- PO-15 · Outside spark (Existing first), from model knowledge: chezmoi keeps dotfiles in git. etckeeper keeps the system
  configuration folder in git. LangGraph has a store interface (the epic names it) · H · model knowledge, no source read · supports: reuse
  candidates for P1033, not this card's value.

## What he does not want

- A fact written with no look from him [D #1461].
- A "verified: true" from Claude's reading of a short answer [E #1462 pre-analysis, "the main risk is a false
  verified"].
- A typical or vendor value where nobody measured. The board record follows this rule today: `deep_sleep_current_ua`
  is null, and the vendor figures are only in its source [E store/shelf/boards/firebeetle2-esp32c6.json:897-901].
- Firmware behaviour in a record (PO-14). A change he cannot undo (D, P1027).
- A flat list of 30 or 61 unverified facts to review [E #1462 comment, diary.md:309-310 for the counts].
- New storage before a need. D2 keeps P1002 on the file system, behind the first slice of P1033's seam [D the PO
  2026-11-23].

## Riskiest assumption

A later project reads a fact that an earlier project kept, and saves a trial. No later project uses one yet (PO-10).
Spark itself shows no kept board fact to anyone (PO-11). The keeping has no payoff unless the next project reads the
record at the moment the fact matters. Cheapest test: the next project with the FireBeetle 2 ESP32-C6 that plans deep
sleep. Pass line (proposed, written 2026-11-23 before any result): the session cites a kept
deep-sleep fact and its source before it writes the sleep code. It runs no trial for that fact.

## Options

- A · Offer and keep, review first. After a bench step, spark lists the facts the session learned. Each line shows
  the old value and the new one. The person says yes per fact. Spark writes each fact into the record's home with its
  source. One setting with two values, off and offer, for the store and for a project. "Keep without asking" waits
  for a real project to ask for it. Cost: about two stories (a board writer for learned facts, one offer list, one
  setting file). Proves: J1, J2 and J4 on the next walk.
- B · Keep only, no offer yet. The board record gets the writer the part record has. Spark keeps a copy before each
  write. The conversation still makes the offer, as today. Cost: about one story. Proves: J1 and J3, with no setting.
  It leaves the PO's "always offering" (D 2026-11-22) unmet.

## What I could not check

- Whether a project before p934 learned a fact on the bench that was then lost. I read one walk only.
- The p934-display2 issue #7 comments that the board facts cite. I did not open them.
- Whether the PO wants "keep without asking" as a setting value, or only "offer". He said "automatically". He also
  said to tell him first what will be saved. The two pull apart.

## Questions for the decider

- Which of the two does "automatically" mean: spark offers each time, or spark writes with no question by the
  setting? · decides: a third setting value, and whether J2 can be switched off.
- Is a hand backup folder enough undo for the first slice, or is git a must? · decides: whether §5.8 changes in this
  card or in P1033.
- Is "do not use lightsleep with this build" a fact or behaviour? · decides: what the writer refuses.

## Searches

none
