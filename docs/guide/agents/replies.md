# Open questions and replies

Part of the [guide for AI agents](../agents.md). An Operation that cannot answer a question itself puts the question
on the run's open list. This is [P737](https://github.com/xmejkal/spark/issues/1013). The shape is the core's, so
it reads the same in every script that asks. The first script that asks is `research.py` (below).

## What a run with open questions prints

- `data.open` is the one home of the open questions. Each is `{key, text, kind, asked_of, why, unit, answer_form, example, choices, cites}`.
- `key` is the fact path that the answer fills, for example `physical.mounting_holes`, or the name of a decision.
- `kind` is `yes_no`, `value` or `choice`. A `choice` question lists its `choices`.
- `asked_of` is `agent`, `person` or `either`. You answer an `agent` question. Never put it to a person in a terminal.
  A `person` question needs the person's hands or eyes, and comes first in the list.
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

## The research run

```
${CLAUDE_PLUGIN_ROOT}/scripts/research.py --part <id> --project . --json
```

It reads the record from the project's `parts/` or the person's shelf, never from spark's library. `data.gaps` lists
the facts that `data/fact-needs.json` says the chain reads and the record lacked when the run started, minus what
`physical_proof.not_published` names. `data.sources` is the order the run asked, today `kept-documents` alone: with a kept dimension drawing in the
record's `documents`, each gap is an `agent` question that cites it at page 1. Run 1 writes the template and exits 2.
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
| `part_contract_broken` | a `problems` item of `research.py`: the folded record breaks a rule that the record did not break before, for example a size that is not above 0. Nothing is written | fix the value in the replies file, then run again |
