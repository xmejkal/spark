# The backlog in GitHub — design (P102a)

**Status:** the spec, for the PO's review (2026-10-05). Designed with the PO in one sitting, after he asked for the
tools chore (P102) before the next epic. It takes in P70 (2026-10-03), whose design stands except where §2 says
otherwise. Every decision the PO made is in §11 with its date.

## 1. What it is for

The PO, 2026-10-05: *"switch to github projects, for every epic and user story if appropriate … so that the new
functionality can already be having good discovery and the PB and the epic and also planning tasks for user stories
is already in gh."* He also asked to be *"always aware of what we're actually doing now, what the functionality is …
how much of that is already working and what's remaining, also if we're actually finishing epics."*

So the backlog moves out of a 1,200-line Markdown file, and into issues and a board that show:
- what is in progress;
- which epic each story belongs to;
- whether an epic's stories are finished.

**Done means** (P70's line, kept):
- `gh project item-list` lists every open spark item with *Needed by* filled;
- the frozen file says it is the archive;
- the W14 check reads the issues and fails on one without *Needed by*.

## 2. Where things live — each repository its own project

The PO, 2026-10-05: *"I'd like spark to have a separate gh project and repo and also the demo projects should."* This
replaces P70's "one user-level project spans spark and the bin".

| repository | its project | what goes there | done by |
| --- | --- | --- | --- |
| `xmejkal/spark` (public) | **spark** (public, user-level) | every spark item | this spec |
| `xmejkal/sisuo-brain-transplant` (public) | **the bin** (public) | the bin's items: B1, B5, B8 | this spec |
| `xmejkal/spark-demos` (new, public) | **spark demos** (public) | irrigation, rc-car, plant-alarm, the quickstart and P100's new idea, one folder each | P102f, its own design — each history is checked before it is published (vendor files, GPS in photos, tokens) |

A demo that becomes a real product moves out to its own repository, as the bin did.

## 3. The project

The same shape for spark and the bin.

- **Status:** Backlog → Ready → In progress → In review → Done.
- **Iteration:** one week each, starting Monday 2026-10-05. An iteration is a sprint; the sprint's review and retro
  stay in `scrum/`.
- **Slice:** a single select. Its options are the story map's slices 1–10, *team tools* and *desk lane*. It places an
  item on the map, as `STORY_MAP.md` does today.
- **Order:** the Backlog column's row order, set by the PO by dragging (W11: the PO orders).
- **Views:**
  - Table (all fields);
  - Board by Status, with a WIP limit of 2 on In progress;
  - Roadmap by Iteration.

  GitHub's API cannot create views or set a column limit. They are made by hand in the browser, a few clicks, by the
  PO or by Claude with his go.
- **Proven** (proven / not proven / not run) is added by P102d, not here.

## 4. Issues

- **One issue per item,** in the repository it is about.
- **The title keeps the id,** so commits, plans and the archive still trace: `P96 — Store 1b: a goal, matched`.
- **The body comes from an issue form,** `.github/ISSUE_TEMPLATE/item.yml`. Its sections are:
  - *Needed by* (required);
  - *Value proven by* (required);
  - *Proof*, the command that proves it (optional until P102d);
  - *Archive*, a link to the item's heading in the frozen file (moved items only).

  These facts live in the body, not in project fields, so a check, a CI job or a stranger's agent can read them with
  no project scope and no token.
- **Labels say what the issue is.** Personal repositories have no issue types, so the labels are `epic`, `story`,
  `task`, `chore` and `bug`. Of these, only `bug` exists today.
- **Hierarchy is GitHub's sub-issues.**
  - An epic's stories are its sub-issues, and the epic shows their progress.
  - When a story is planned, each task of its plan becomes a sub-issue of the story, and its plan document stays in
    `docs/`.

## 5. Revalidation — only what still holds moves

P70's rule, and the PO's choice: a lens proposes and the PO confirms.

1. A W14 lens reads each of the 35 open items (34 for spark and the bin; P102 itself is kept). It proposes one of:
   - **keep**, as an epic, story, chore or bug, with its slice and its parent epic;
   - **close as done**, naming the commit that proves it;
   - **park**, with what pulls it back;
   - **merge into** another item.

   Every proposal carries one line of reason.
2. The PO confirms or changes the table in one pass.
3. The confirmed table is the migration's only input.

## 6. The migration — once, not shipped

A one-off script runs from the PR's scratch space and never enters `scripts/` or `tools/`. A shipped importer would be
dead code after one run (W16). It goes in this order:

1. Create the labels.
2. Commit the issue form.
3. Create the issues.
4. Link the sub-issues.
5. Create the projects and their fields.
6. Add the items to the projects.
7. Set Status, Slice and Iteration.

It is **idempotent**: an issue is found by its title's id before one is created, so a second run changes nothing. It
runs **as a dry run first**, printing every issue it would create. It runs for real **only with the PO's yes**,
because it publishes around 30 public issues. It works through `gh` with the PO's own login and stores nothing.

## 7. The archive

- **`PRODUCT_BACKLOG.md`** is frozen.
  - It opens with a banner: the date, *this is the archive*, and the projects' links.
  - Each moved heading ends `— MOVED to xmejkal/<repo>#N`. A closed item ends `— DONE` or `— CLOSED <date>: <reason>`,
    as the revalidation table says.
  - The test's closed pattern gains `MOVED`.
  - Nothing is added to the file after the freeze.
- **`STORY_MAP.md`** keeps the map as text: the backbone, the slices and which items sit in each, by issue number.
  This text is what P102b draws in Miro and Canva. Order and status leave it for the project.

## 8. The checks

- **`tools/check_backlog.py`,** in the pre-push gate (`tools/check_commit.py` calls it). It reads the spark project's
  open items with `gh project item-list --format json` and fails the push on any open item with an empty *Needed by*
  section or no Slice.
  - With no network or no `gh`, it prints that it was skipped and does not fail. The gate must work offline.
  - Its test feeds it a recorded `gh` answer, so the suite stays offline.
- **`tests/test_orphans.py`:** its two backlog checks become one. The archive is frozen when no open heading lacks a
  `MOVED`, `DONE`, `CLOSED`, `PARKED`, `MERGED`, `DELETED` or `SPLIT` marker.
- **The bin:** it has only three items, so no check is built for its project yet (W14). One is added when an item
  first lacks *Needed by*.

## 9. What changes in how we work

| rule | before | after |
| --- | --- | --- |
| **W19:** the item exists before the work | a Markdown entry | an issue on the project |
| **W8:** big items go through a PR | unchanged | the PR body says `Closes #N` |
| a plan's tasks | checkboxes in the plan only | also sub-issues of the story (the plan stays the source of each task's text) |
| **W11:** the PO orders | `STORY_MAP.md`'s order lines | the Backlog column's row order |
| a sprint | `scrum/SPRINT.md` | an iteration; `SPRINT.md` keeps the review and the retro |

`scrum/WORKING_AGREEMENTS.md` gets these lines in the same commit as the freeze (R7: a document changes with the thing
it describes).

## 10. Not in this spec

- P102c, the session-start status;
- P102b, maps in Miro and Canva;
- P102e, the discovery skill;
- P102d, proofs and the *Proven* field;
- P102f, `spark-demos`;
- any CI for spark (none exists).

## 11. Decisions (the PO, 2026-10-05)

1. The tools chore comes first, before P100.
2. P102 is split into a, then c, b, e and d, each designed on its own. f was added for the demos.
3. Open items move only after revalidation: the lens proposes and the PO confirms.
4. Item facts live in the issue body; project fields hold only Status, Iteration, Slice and later Proven.
5. The projects are public.
6. Iterations are one week long.
7. Each repository has its own project: spark, the bin, and one `spark-demos` for the demo projects.
8. Diagrams go in both Miro and Canva (P102b).
9. All four helpers are in: epics with sub-issues, the session-start status, diagrams as text first, and proofs run.
