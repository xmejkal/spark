# Open questions and replies

Part of the [guide for AI agents](../agents.md). An Operation that cannot answer a question itself puts the question
on the run's open list. This is [P737](https://github.com/xmejkal/spark/issues/1013). The shape is the core's, so
it reads the same in every script that asks. `research.py` asks (below), and `look.py` asks before it reads a board
([P865](https://github.com/xmejkal/spark/issues/1231), [the look's question](#the-looks-question)).

## What a run with open questions prints

- `data.open` is the one home of the open questions. Each is `{key, text, kind, asked_of, why, unit, answer_form, example, choices, cites}`.
- `key` is the fact path that the answer fills, for example `physical.mounting_holes`, or the name of a decision.
- `kind` is `yes_no`, `value` or `choice`. A `choice` question lists its `choices`.
- `asked_of` is `agent`, `person` or `either`. You answer an `agent` question. Never put it to a person in a terminal.
  A `person` question needs the person's hands or eyes, and comes first in the list. An `either` question goes to whoever
  is there: a person at the terminal, or you under `--json`. Every question `research.py` asks today is `either`, and the
  look's question is `person`.
- `answer_form` says the shape of the answer in words. `example` holds placeholders, never a value to copy.
- `cites` is `{document, at}`: the kept document and the page that hold the answer, `at` in the words `page 1`, as the
  prompt and the source repeat it. Read that document and nothing else.
  A question with `cites: null` is one that no source placed. Find the fact where you can, and name the place in your reply's `note`.
- One `unchecked` item per open question, with the code `needs_reply` and the key as `subject`. The status is
  `could-not-run` and the exit is 2 while a question is open.
- `notes` say what the run wrote, so nothing is lost. `next[0]` is the same run with `--replies <file>`.

## The replies file

The file is the project's `.spark/research-replies.json`. Run 1 writes it as a template:

```json
{"replies": {"<key>": {"value": null, "note": "", "cites": {"document": "...", "at": "..."}}}}
```

Fill `value` for each key that you can answer. When you read the value off a document, add a `note` and `cites`.
Invent no key. A null stays "not answered yet", and the question stays open on every run. If the vendor did not publish
the size, the record says so in `physical_proof.not_published`, written with `parts.py --fact-set`; a reply form for it
is a later card. A bare `"<key>": value` is accepted too, an object as well, unless the object has a key named `value`:
then write the long form. A rerun with the same file adds nothing twice.

## Live mode

In a terminal, with no `--json`, `research.py` asks each question whose `asked_of` is `person` or `either`, one at a time,
after the replies file answered what it could. Enter leaves a question open. Ctrl-C or Ctrl-D keeps the answers typed so far
and leaves the rest open. An answer that does not fit the question's `kind`, or a word where the question names a unit, is said
and the question stays open. A value the record's contract refuses is a `part_contract_broken` problem: nothing is written, and
every typed value is kept in the replies file, where you fix the one and run again with `--replies`. A replies file with a
problem asks nobody. A question with `cites` is asked live too, with the line `see <document>, <at>` under it, so the person
reads the kept drawing at that page ([P763](https://github.com/xmejkal/spark/issues/1050)). The value they type gets the
source `read from <document> <at>, typed in a terminal by <login>`. You run with `--json`, or with no tty, so you never see
a prompt. The template is written for what stays open, as in run 1.

## The look's question

Before `look.py` reads a board, it asks the person, because the read restarts the board. It asks once per board, except for the two rows of
the table below that are asked every time, and then remembers the board for the project in the person's store, never in the project. The key is
`look.read_board.<id>`, or `look.switch_board.<id>` for a board that is not the kept one. `<id>` is an id made from the
serial, or from the port when the board has no serial: copy the key from `data.open`. The text names the port and the restart. `data.known_board` holds the `state` and the kept board's
`mac_ends`. A MAC is the board's own address, six bytes; spark shows only the last two.

Ask the person in this conversation. Name the port and say that the board restarts. Write `true` only after they say
yes to that message, in a file of your own outside the project, never in research's file:
`{"replies": {"look.read_board.1a2b": true}}`. Only the JSON value `true` is a yes. Then run the `next[0]` step, with your
file in place of `<your replies file>`. One yes is for one look: the look sets every `look.` key of the file back to null
right after it starts, also when it then stops. A `false` is a no: code `answered_no`, and nothing is read. Never add `--port` to avoid the question:
a `--port` that names a port the list does not hold, or a listed port with no USB serial, is read as before, with no question; every other board is asked as without `--port`. Such a read keeps nothing.

| What is on USB | The look |
| --- | --- |
| no kept board | asks once, and keeps the board after the yes and the read |
| the kept board | reads it with no question |
| another board | stops before the read with `other_board`, names both as `MAC ends 34:56`, and asks `switch_board` |
| a bridge chip's board (CP2104, CH340) with a serial | asks once: the bridge's serial names the board |
| a native USB board whose firmware set its serial | asks on every look: a custom build gives every board one serial. A yes to another board makes it the project's |
| a board with no serial, or no `--port` row | asks on every look, or with `--port` reads as before |
| a board with no serial named with `--port`, and a kept board | reads with no yes, then stops as `other_board` when the MAC differs |

Two bridge clones with one serial cannot be told apart before a read. The read then finds another MAC: `other_board`,
and the sentence says that the board did restart. `other_board` after a read gives no token and no deploy step. With no MAC read nothing is kept, and a note says so. A kept record
that cannot be read is `known_board_unreadable`: repair or remove the file that the `fix` names.

## The requirements' yes

`parts.py --requirements` asks no question that waits: a run after a re-pick or a dropped need writes as today and exits 0. It names each entry that spark
wrote for a pick that is gone (`data.unexplained`, code `entry_pick_gone`) and prints `data.remove_key`, the reply key of those entries on the file the run left. The `next[0]` step
says how to remove them. Ask the person in this conversation, and name the entries and their needs. Write `true` only after their yes, in a file of your own outside the project. Read `remove_key` again from the newest answer, because it changes with the file. On a yes, write `{"replies": {"requirements.remove_entries.1a2b3c4d": true}}` to a file of your own and run
`--requirements <project> --replies <file>`. Only the JSON value `true` is a yes, and `false` is a no: the entries are the person's from then on. A key that fits other bytes or other entries removes nothing,
and a note names the key that fits now: ask the person again with that key. After a `false` the run says `kept as yours`, and `data.unexplained` is empty. A previous version that cannot be kept leaves the entries and spends the yes. The run sets every `requirements.` key of the file back to null before it changes anything, so one yes is for one run. A dry run and a refused run read nothing. A yes keeps the file before as `.spark/previous/requirements.json.txt`, the one previous version.

## The research run

```
${CLAUDE_PLUGIN_ROOT}/scripts/research.py --part <id> --project . --json
```

It reads the record from the project's `parts/` or the person's shelf, never from spark's library. `data.gaps` lists
the facts that `data/fact-needs.json` says the chain reads and the record lacked when the run started, minus what
`physical_proof.not_published` names. `data.sources` is the order the run asked. The first source is `dfrobot-wiki`. For a
record whose `vendor` is dfrobot, it fetches `https://wiki.dfrobot.com/<sku>/` once per record. It keeps the PDFs and
images that the page lists in the store and writes them into `documents`. A zip or a STEP file is written as `{url,
kept: false, title}`. The page's URL goes into `sources`. When the page lists no dimension drawing, the thickness, the
holes and the header go into `physical_proof.not_published`. The second source is `kept-documents`. With a kept dimension
drawing in the record's `documents`, each gap is an `either` question that cites it at page 1. With no gap, no source
runs. Run 1 writes the documents it kept and the template, and exits 2.
Run 2, with `--replies`, writes each value as a fact: `physical` with its `physical_proof`, or `body_mm`. The fact has
`verified: false` and a `source` that names the document, the page and who read it. An older proof is merged, not
lost. `data.written` names the keys, and `notes` repeat them. In text mode a refusal prints its code, sentence and fix. A key the record already holds with the
same value is settled and flags nothing. A run with no gaps is `ok` and writes no file.

## The codes

| code | what it is | what to do |
| --- | --- | --- |
| `needs_reply` | an `unchecked` item per question that the run did not answer itself. `subject` is the key, the question is in `data.open` | answer it in the replies file (for the look, see [the look's question](#the-looks-question)), then run the `next[0]` step. Exit 2 here means "run again with replies", not "broken". Relay a `person` question to the person |
| `unknown_reply` | a `problems` item: a reply to a key that no open question has, and the `fix` names the nearest. Also a reply to a fact that the record holds with another value | fix the key in the replies file. Never reply to a fact that is not open |
| `bad_reply` | a `problems` item: a reply that does not fit its question's `kind`. It is not a yes or no, not one of the `choices`, empty, or not a finite number | answer as the question's `answer_form` and `example` say |
| `part_contract_broken` | a `problems` item of `research.py`: the folded record breaks a rule that the record did not break before, for example a size that is not above 0. Nothing is written, and every typed value is kept in the replies file that the `fix` names | fix the value in that file, then run the `fix` line with `--replies` |
| `url_unreachable`, `url_refused`, `file_name_refused`, `document_not_kept` | an `unchecked` item of `research.py`, `subject` the source name (`--fetch` gives it too, P722). The wiki page, or one file it lists, did not answer, or the store refused it. The sentence names the URL. The other sources still ran. Even a run that wrote every reply ends with exit 2 | when the page answers, run again. A wrong page address shows here too |
| `no_sku` | an `unchecked` item. The record's `vendor` is dfrobot and it has no `sku`, so the wiki page has no address | write the maker's part number as `sku` (`parts.py --skeleton --sku`), then run again |
| `no_document_list` | an `unchecked` item. The page answered but holds no document list spark can read (its JSON-LD block), so nothing was kept | keep the documents by hand. Put their URLs in the record's `sources` and run `parts.py --fetch` |
| `more_documents` | an `unchecked` item. The page lists more than twelve files. The first twelve were taken, and the sentence names the rest | if a decision needs one of the named files, keep it by hand, as for `no_document_list` |
