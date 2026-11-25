# Words that the code and the docs share

Rule 1 of [One responsibility, one name](patterns-and-names.md#one-responsibility-one-name) gives one word one meaning.
Each table here holds the words of one area. The [glossary](../../GLOSSARY.md) says why each word exists.

Words for a rules file (P454, #615): a *rule* is one `fabrication` entry of a project's `.spark/rules.json`.

| Word | Means | Where |
|---|---|---|
| `lowest` | the table of limits, one per process key | `data/fabrication.json`, `fab.DATA["lowest"]` |
| `above`, `at_least` | the two kinds of limit: the value must be greater, or may equal it | the entries of `lowest` |
| `TOO_LOW`, `NOT_A_NUMBER`, `NOT_AN_OBJECT` | the reason `fab.fabrication_problem` returns beside the field | `scripts/spark/design/fab.py` |

Words for the project timeline ([P1157](https://github.com/xmejkal/spark/issues/1693)). A council of three on Fable chose
them on 2026-11-25, delegated by the PO and his to change. The discovery `docs/discovery/2026-11-25-spark-and-git/`
(`brief.md` and `items.md`) wrote "the project-history strategy" for the first word. No code holds these names
yet. The epic [P1152](https://github.com/xmejkal/spark/issues/1688) builds them under the planned names.

| Word | Means | It is not | Planned names |
|---|---|---|---|
| project timeline | the exchangeable Strategy that makes a project's folder and repository, keeps each kept step, lists the kept steps and runs a take-back. Git fills it first, and a person by hand or a server can fill it another way (D5). It is handed in, never built inside an Operation | the store's history, `history.jsonl` ("your history", read by `store.events()`), and LangGraph's history of a graph's state | `ProjectTimeline` (its docstring starts Strategy), `GitProjectTimeline` (reuses `ProjectCommit`), `HumanProjectTimeline`, `FakeProjectTimeline` |
| kept step | the records of one decision of the person, kept as one unit with their stamps, for example `needs.json` with `needs-basis.json` (D8, P1160 change 3). Always the two words. Its JSON is `kept_step`, and `kept_step.id` holds git's commit id (D11) | a spine step (`parts.py --step`, the history's `step` event), a wiring step, a `NextStep` or a build stage. It is no file that the build's `--keep` writes (`kept_files`) and no kept document (`parts.py --keep`, `--kept`) | `KeptStep` (a Value), `--kept-step` |
| take-back | the return of kept step records to their earlier content. It takes back one kept step, or a kept step and the kept steps after it. It runs after a preview and the person's yes through the core (D7, D14) | git's `revert`, a word only the git Adapter says. It is not the brief's printed `git revert` line, which "the way back" names until P1152. "Undo that" stays the person's phrase (D11) | `TakeBackKeptStep` (op `take-back-kept-step`), `TakeBackPreview` (a Value) |

A kept step's files are "the kept step's records", never "kept files". The P1160 finding's "kept files" (`finding.md:194`)
means those records. "The way back" also names `Answer.from_result` (`record_kind.py:89`).

Four words stay out of these names, because each has a meaning already. "History" is the store's event log. "Commit"
is git's word and a method of `ProjectCommit`, `PreviousVersionFiles`, `StagedFile` and `WiringLogStore`. "Revision"
is a board's hardware revision (`replies.py:34`, `physics_check.py:404`). "Change" has `ChangeList`, the bench's changes to a wiring
(`breadboard/bench_changes.py`).

Git's two words for a file differ (P1150). "Held" is `ProjectCommit.held_as_is`: in HEAD and the same on disk. "Tracked" is git's
word for a file in the index (`tracks`, `tracked_files`, `IgnoreList.already_tracked`), committed or not.
