# Open questions and replies

Part of the [guide for AI agents](../agents.md). An Operation that cannot answer a question itself puts the question
on the run's open list. This is [P737](https://github.com/xmejkal/spark/issues/1013). The shape is the core's, so
it reads the same in every script that asks. No script asks today. The research Operation of P737 step 4 is the first.

## What a run with open questions prints

- `data.open` is the one home of the open questions. Each is `{key, text, kind, asked_of, why, unit, answer_form, example, choices, cites}`.
- `key` is the fact path that the answer fills, for example `physical.mounting_holes`, or the name of a decision.
- `kind` is `yes_no`, `value` or `choice`. A `choice` question lists its `choices`.
- `asked_of` is `agent`, `person` or `either`. You answer an `agent` question. Never put it to a person in a terminal.
  A `person` question needs the person's hands or eyes, and comes first in the list.
- `answer_form` says the shape of the answer in words. `example` holds placeholders, never a value to copy.
- `cites` is `{document, at}`: the kept document and the page that hold the answer. Read that document and nothing else.
- One `unchecked` item per open question, with the code `needs_reply` and the key as `subject`. The status is
  `could-not-run` and the exit is 2 while a question is open. The `notes` say what the run wrote, so nothing is lost.
- `next[0]` is the same run with `--replies <file>`.

## The replies file

The file is the project's `.spark/research-replies.json`. Run 1 writes it as a template:

```json
{"replies": {"<key>": {"value": null, "note": "", "cites": {"document": "...", "at": "..."}}}}
```

Fill `value` for each key that you can answer. When you read the value off a document, add a `note` and `cites`.
Invent no key. A null stays "not answered yet", and the question stays open. A bare `"<key>": value` is accepted too.
A rerun with the same file adds nothing twice.

## The codes

| code | what it is | what to do |
| --- | --- | --- |
| `needs_reply` | an `unchecked` item per question that the run did not answer itself. `subject` is the key, the question is in `data.open` | answer it in the replies file, then run the `next[0]` step. Exit 2 here means "run again with replies", not "broken". Relay a `person` question to the person |
| `unknown_reply` | a `problems` item: a reply to a key that no open question has (the `fix` names the nearest), or to a fact that the record already holds | fix the key in the replies file. Never reply to a fact that is not open |
| `bad_reply` | a `problems` item: a reply that does not fit its question's `kind` (not a yes or no, not one of the `choices`, or empty) | answer as the question's `answer_form` and `example` say |
