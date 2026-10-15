# P262 (#286): the plan council, the review and the mutation run

1. Plan council (Sonnet): a missing `id` is owed, so through `broken_problems` only `owes` names it; use
   `isinstance(order, list)` so a string is not read letter by letter. More crashes of the same kind sit outside
   the two paths: an entry of the wrong type in `needs`, `power` or a pin list (`["a"]`), `pin_order: [["a"]]`
   (unhashable), and maybe `controls: ["x"]` and chip `pins` that hold lists. All acted in the plan, and the rest
   is proposed as one later card.
2. Review (Sonnet, no shell): no defect. The `id=5` case did not go through `broken_problems`. Acted: one assertion.
3. Mutation run, `tools/mutate.py --copy tests/mutations/p262-shape.json`: 2 planted, 2 caught.
