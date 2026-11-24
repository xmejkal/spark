# P1060 PR B: one secret mask for show, run-request and the page: rows

Card: [P1060 #1558](https://github.com/xmejkal/spark/issues/1558), PR B ([#1610](https://github.com/xmejkal/spark/pull/1610)).
The review ran on 2026-11-24, with one lens on Sonnet and the refuter on Opus. The refuter found two leaks, both fixed in
the PR. This file holds the acted, raised and rejected findings only. PR A has its own rows file.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | LEAK: the `request_secrets_unreadable` refusal still answers the offer's key and label, such as `needs-drop:<value>`, and `/spark:page` publishes that answer | the refuter | acted | fixed in the PR: the refusal passes no offer, so `key` and `label` are `null`. Test `test_the_refusal_names_no_key_or_label_as_they_can_hold_the_value_it_cannot_mask`, mutation row "D5: the refusal answers the offer's key and label" |
| 2 | LEAK: `values_in` misses a positional argument (`connect("net", "pw")`), bytes, an f-string, a string joined with `+` and a call's default (`os.getenv("X", "token")`) | the refuter | acted | fixed in the PR: the whole right side of an assignment and every argument of a call are walked; str and bytes constants (UTF-8, errors left out), f-string parts and a joined string whole are taken; dict keys and docstrings stay out (A3). Tests `test_a_positional_argument_bytes_an_f_string_a_joined_string_and_a_call_s_default_are_read` and `test_bytes_that_are_no_utf_8_give_what_can_be_read`, three new mutation rows. The how-to says it |
| 3 | `commands/page.md`: after a refusal for an unreadable secrets file, `flow.py page` cannot run, so the answer is never written and the page waits for ever | the refuter | acted | fixed in the PR: step 4.4 writes the answer with `db_write` and stops with no page and no republish; `artifact-how-to.md` section 6 says the same |
| 4 | the how-to should say that a value of 8 or more characters is masked wherever it stands, in spark's facts too (`MQTT_TOPIC = "firmware"` masks a phase name) | the refuter | acted | fixed in the PR: one bullet in section 10 |
| 5 | `agents/flow.md`: "every text on it is masked" is not true of a drawing | the refuter | acted | fixed in the PR, within the line: "every text on it except a drawing's" |
| 6 | `MASK_OFF` reads `firmware/firmware` when the folder cannot be listed | the lens | acted | fixed in the PR: `ProjectSecrets.read` names `firmware/` and `firmware/<name>`, and the sentences take the path as it is. Tests assert both forms |
| 7 | a docstring line of `RunRequest` is about 189 characters | the lens | acted | fixed in the PR: rewrapped |
| 8 | `RunRequest.run` computes `refused` before it reads the secrets, which decide first | the lens | acted | fixed in the PR: `unreadable` is read first, with a one-line comment why |
| 9 | `agents/flow.md` joins two lines to stay at its budget of 400 | the review | rejected | dropped because the budget asks for it: the page gains no net line, and no sentence changed |
| 10 | the secrets file is parsed twice per call (the Privacy, then the refusal or the note) | the review | rejected | dropped because it is harmless: a secrets file is a few lines |
