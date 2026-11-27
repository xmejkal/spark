# Open questions and replies

Part of the [guide for AI agents](../agents.md). An Operation that cannot answer a question itself puts the question
on the run's open list. This is [P737](https://github.com/xmejkal/spark/issues/1013). The shape is the core's, so
it reads the same in every script that asks. `research.py` asks (below), and `look.py` asks before it reads a board
([P865](https://github.com/xmejkal/spark/issues/1231), [the look's question](#the-looks-question)). `deploy.py`, `grant.py
--minutes`, `reach.py` and `live.py` ask the same board question before they touch a board
([P892](https://github.com/xmejkal/spark/issues/1266), [the deploy's question](#the-deploys-question),
[the question of the grant, reach and live](#the-question-of-the-grant-reach-and-live)).

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

## The deploy's question

`deploy.py --token` asks the same board question before its own read, with the deploy's own words
([P892](https://github.com/xmejkal/spark/issues/1266)). It asks only for a board that spark cannot tell before a read. It never keeps or
replaces a board: the look does that. A dry run asks nothing and changes no replies file.

| What is on USB | The deploy |
| --- | --- |
| the kept board | reads it with no question |
| another board | stops before the read with `other_board` and asks nothing. The board did not restart. `next[0]` is the look, with `needs_person` |
| no kept board, and a board with a USB serial | stops before the read with `no_known_board`. `next[0]` is the look, which asks once and keeps the board |
| a board with no serial, with a kept board a serial that its firmware set, or a `--port` that the list does not hold | asks on every deploy, with `--port` too |
| any board whose MAC after the read is not the kept MAC | stops with `other_board` before the erase's question, also after a yes. The board did restart |

The key is `deploy.read_board.<id>`. A yes under a `look.` key does not answer it. The stop holds `data.open`, `data.port`,
`data.product` (null for a port that the list does not hold) and `data.known_board`. These keys come only with a stop at the board.
`next[0]` is the same deploy with `--replies <your replies file>` and `needs_person`. Ask the person in this conversation, write
`{"replies": {"deploy.read_board.1a2b": true}}` to a file of your own after their yes, and run that step. The deploy sets every
`deploy.` key of the file back to null before it reads. Its read restarts the board, then the erase asks its own yes, as always. With no
terminal and no deploy grant, the run stops at that yes, and the person's own run of `data.run_in_terminal` asks the board question once
more. With the look, such a board restarts three times. A kept board whose USB serial is its MAC, such as a XIAO, is never asked.

## The question of the grant, reach and live

`grant.py --minutes`, `reach.py` and `live.py` ask the same board question before they touch the board, each in the words
of its own touch ([P892](https://github.com/xmejkal/spark/issues/1266)). The grant reads the board, which restarts it. Reach and
live run code on it, which stops its firmware. Like the deploy, each asks only for a board that spark cannot tell by its USB
serial, and none of them keeps or replaces a board. `grant.py --check` asks nothing: it only lists the boards.

| What is on USB | grant.py, reach.py and live.py |
| --- | --- |
| the kept board, known by its USB serial | touch it with no question |
| another board, told apart by its USB serial | stop before the touch with `other_board` and ask nothing. The fix names `look.py`. The board did not restart, and its firmware runs on |
| no kept board, and a board with a USB serial | stop before the touch with `no_known_board`. The fix names `look.py`, which asks once and keeps the board |
| a board with no serial | reach asks on every run, with `--port` too. The grant asks for `--scope deploy` only: a live grant is refused first with `serial_not_mac`, exit 1, with no question and no read. Live refuses it with `refused_no_grant`: `grant.py` gives such a board no live grant |
| a kept board whose record trusts no USB serial (it showed none, or one that its firmware set), and a board on Espressif's own USB whose serial does not start with the kept MAC | ask on every run, with `--port` too: spark cannot tell another board from the kept one. More below the table |
| a `--port` that the list does not hold | stop with `port_not_listed` before the question and touch nothing ([P1056](https://github.com/xmejkal/spark/issues/1553)) |

In the state of the fifth row, a live grant on a serial that a firmware set is refused first with `serial_not_mac`. A board
whose serial is its MAC is asked, and after a yes the grant's read stops another board with `other_board`. It is the one state
in which live asks for a board that `grant.py` granted, for example with a grant given in another project. A kept record
trusts no USB serial when the look read a board that showed none, a serial that its firmware set, or a `--port` that the
list did not hold.

The keys are `grant.read_board.<id>`, `reach.run_on_board.<id>` and `live.run_on_board.<id>`. A yes under another script's key
does not answer. Each sets its own keys of the file back to null before it asks, so one yes or one no is for one run. A `false`
to the board question is a no: code `answered_no`, exit 2, and nothing touched the board. The grant's own yes is another
question, asked after its read: a no to it is `answered_no` too, but exit 1, the board did restart, and no grant is kept. A
list of the boards that fails stops all three, with no question. A
`/dev/tty.` port is its `/dev/cu.` port. Reach and live take `--replies`: ask the person in this conversation, name the port and
that the firmware stops, write `{"replies": {"reach.run_on_board.1a2b": true}}` to a file of your own after their yes, and run the
same command again with `--replies` and that file. `reach.py --json` prints one line for an open question only: `reached` false,
`port`, `product`, `open`, `known_board` and `fix`. Its other stops print nothing on stdout. `live.py --json` adds `open`, `product`
and `known_board` to its stop line for a stop of the board question only. Both lines hold `fix`, the question's fix (P1055). Live's stop line has `answer` `could-not-run` and
no `code`, so read the code from `known_board.state` and `open`:

| `known_board.state` | `open` | the code | the next command |
| --- | --- | --- | --- |
| `other` | empty | `other_board` | the person plugs in the kept board and you run `live.py` again, or you run `look.py`, which asks the person |
| `none` | empty | `no_known_board` | `look.py`, which asks the person once and keeps the board |
| `cannot_tell` | one question | `needs_reply` | ask the person, write the yes to your file, run `live.py` again with `--replies` and that file |
| `cannot_tell` | empty | `answered_no` | none: run `live.py` again only when the person wants it |

`reach.py` exits 2 with no stdout line for `other_board`, `no_known_board` and `answered_no`. Then read its last stderr line:
it is the stop's fix, and the line before it is the stop's sentence.

`live.py` asks after its grant check and its pin check, just before the code runs. A board with no grant is refused with
no question. Its answer fix also asks you to show the person the code that runs. So with another board on USB that has no grant, `live.py` says `refused_no_grant`, and `grant.py` then stops with
`other_board`: two steps, and no board restarts.

`grant.py` needs the person's own terminal, as always, and says `no_terminal` first when it has none. So its board question and
its stops show only in that terminal, never to you. It asks the question there, or reads the yes from the person's `--replies`
file, and the grant still asks its own yes. A live grant on a board whose USB serial cannot be its MAC (no serial, a bridge's
serial, a serial that a firmware set) is refused with `serial_not_mac` from the list alone, before any question or read. A
deploy grant on such a board goes on to the board question, as the table says. After the read, a MAC that is not the kept board's stops the grant with `other_board`
before its own yes, and no grant is kept: the board did restart. With no kept board and a board with no USB serial, a yes and a
read give a deploy grant for a board that no project keeps.

## The requirements' yes

`parts.py --requirements` asks no question that waits: a run after a re-pick or a dropped need writes as today and exits 0. It names each entry that spark
wrote for a pick that is gone (`data.unexplained`, code `entry_pick_gone`) and prints `data.remove_key`, the reply key of those entries on the file the run left. The `next[0]` step
says how to remove them. Ask the person in this conversation, and name the entries and their needs. Write `true` only after their yes, in a file of your own outside the project. Read `remove_key` again from the newest answer, because it changes with the file. On a yes, write `{"replies": {"requirements.remove_entries.1a2b3c4d": true}}` to a file of your own and run
`--requirements <project> --replies <file>`. Only the JSON value `true` is a yes, and `false` is a no: the entries are the person's from then on. A key that fits other bytes or other entries removes nothing,
and a note names the key that fits now: ask the person again with that key. After a `false` the run says `kept as yours`, and `data.unexplained` is empty. A previous version that cannot be kept leaves the entries and spends the yes. The run sets every `requirements.` key of the file back to null before it changes anything, so one yes is for one run. A dry run and a refused run read nothing. A yes keeps the file before as `.spark/previous/requirements.json.txt`, the one previous version.

## The research run

```
${CLAUDE_PLUGIN_ROOT}/scripts/research.py --part '<id>' --project . --json
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
