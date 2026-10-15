# P260 PR B (#285): the Opus refuter

The refuter compared `broken_problems` on main and on the branch for 14,096 record shapes: the 8 records under
`parts/`, each of the 10 owed keys set to 14 values, pairs of keys, and all 10 removed.

1. 40 shapes differ, all one case: `pin_order` is a wrong non-list (the int 5) and `pin_order_proof` is owed. Main
   gives one shape line (`'int' object is not iterable`), and the branch gives "pin_order must be a list of pad
   names, pad 1 first". The branch is right per §5.4. Acted: a test pins it.
2. Before this PR: with `pin_order=5` and a proof present, both versions give only the shape line, because
   `pin_order_problems` iterates the value before it checks that it is a list.
3. Name: `owed` says the role, `skip` says the action. Acted: renamed to `owed`.
4. The `"id" not in skip` chain is right only because of what `owes` returns. Acted: a one-line comment.
5. The footprint guard repeats `_absent`. Acted: removed.
6. No simpler form found.
