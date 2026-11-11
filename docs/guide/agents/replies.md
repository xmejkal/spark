# Open questions and replies

Part of the [guide for AI agents](../agents.md). An Operation that cannot answer a question itself puts the question
on the run's open list. This is [P737](https://github.com/xmejkal/spark/issues/1013). The shape is the core's, so
it reads the same in every script that asks. The first script that asks is `research.py` (below).

## What a run with open questions prints

- `data.open` is the one home of the open questions. Each is `{key, text, kind, asked_of, why, unit, answer_form, example, choices, cites}`.
- `key` is the fact path that the answer fills, for example `physical.mounting_holes`, or the name of a decision.
- `kind` is `yes_no`, `value` or `choice`. A `choice` question lists its `choices`.
- `asked_of` is `agent`, `person` or `either`. You answer an `agent` question. Never put it to a person in a terminal.
  A `person` question needs the person's hands or eyes, and comes first in the list. An `either` question goes to whoever
  is there: a person at the terminal, or you under `--json`. Every question `research.py` asks today is `either`.
- `answer_form` says the shape of the answer in words. `example` holds placeholders, never a value to copy.
- `cites` is `{document, at}`: the kept document and the page that hold the answer. Read that document and nothing else.
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
| `needs_reply` | an `unchecked` item per question that the run did not answer itself. `subject` is the key, the question is in `data.open` | answer it in the replies file, then run the `next[0]` step. Exit 2 here means "run again with replies", not "broken". Relay a `person` question to the person |
| `unknown_reply` | a `problems` item: a reply to a key that no open question has, and the `fix` names the nearest. Also a reply to a fact that the record holds with another value | fix the key in the replies file. Never reply to a fact that is not open |
| `bad_reply` | a `problems` item: a reply that does not fit its question's `kind`. It is not a yes or no, not one of the `choices`, empty, or not a finite number | answer as the question's `answer_form` and `example` say |
| `part_contract_broken` | a `problems` item of `research.py`: the folded record breaks a rule that the record did not break before, for example a size that is not above 0. Nothing is written, and every typed value is kept in the replies file that the `fix` names | fix the value in that file, then run the `fix` line with `--replies` |
| `url_unreachable`, `url_refused`, `file_name_refused`, `document_not_kept` | an `unchecked` item of `research.py`, `subject` the source name. The wiki page, or one file it lists, did not answer, or the store refused it. The sentence names the URL. The other sources still ran. Even a run that wrote every reply ends with exit 2 | when the page answers, run again. A wrong page address shows here too |
| `no_sku` | an `unchecked` item. The record's `vendor` is dfrobot and it has no `sku`, so the wiki page has no address | write the maker's part number as `sku` (`parts.py --skeleton --sku`), then run again |
| `no_document_list` | an `unchecked` item. The page answered but holds no document list spark can read (its JSON-LD block), so nothing was kept | keep the documents by hand. Put their URLs in the record's `sources` and run `parts.py --fetch` |
| `more_documents` | an `unchecked` item. The page lists more than twelve files. The first twelve were taken, and the sentence names the rest | if a decision needs one of the named files, keep it by hand, as for `no_document_list` |
