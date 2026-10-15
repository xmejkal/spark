# P263 (#288): the plan council, the review, the refuter and the mutation run

1. Plan council (Sonnet): 7 more reads on `validate`'s path crash the same way as the card's cases (`facts: 5`, a fact
   that is a string, `host_parts: 5`, `sourcing: 5`, a pin that is a list, a `bus` or `needs` that is a list,
   `cites.document` that is a list). Acted: the plan became one type table in place of about 20 guards.
2. Review (Sonnet, no shell): no defect. The `facts ... is not an object` branch in `validate` became dead (removed).
   The `document_problems` and `host_part_problems` guards stay, because `boards.py` and a test call them directly.
   The walker's parameter `kind` also names a record field (renamed `expected`). The early return can take two runs
   to show every problem (kept, said in the comment).
3. Refuter (Opus): 556 cases compared with main. All 142 real records give the same output. 20 cases with a `rail`
   that is a list or an object now give their problems in place of the shape line (an improvement). 6 shapes still
   crashed: a null item in `needs`, `power`, `unused_pins`, `host_parts` or `needs[0].needs`, and an I2C need with no
   pin. Acted: a null list item is wrong unless the list allows it (`pin_order` does), and the I2C check reads only
   needs with a pin. The early-return comment was not true (rewritten), and `rail` is now named in the table's note.
4. Mutation run, `tools/mutate.py --copy tests/mutations/p263-types.json`: 9 planted, 8 caught. The owed filter
   escaped: no test gave an owed key an empty value of the wrong type. Acted: a `pin_order` of `""` is owed, not
   broken. That row alone, rerun: caught. So 9 of 9.
