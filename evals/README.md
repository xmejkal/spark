# Evals

Each case asks whether the **agent** finds something, not whether a script does. Scripts have
unit tests; these measure the part that cannot be unit-tested.

## How to run one

```sh
claude plugin eval . --case 'finds-assembly-problems'
```

The runner adds a no-plugin baseline arm by default, so the number that matters is the
**delta**: how much better the agent does with this plugin than without it. A case where the
baseline already scores full marks is measuring the model's general knowledge, not the product.

## Why every design is inlined in the prompt

There used to be a `fixtures/` directory. Nothing read it.

The first version of `finds-unswitched-power` pointed the agent at files on disk and **scored
zero on every run**. The obvious reading was that the reviewer did not work. It was not: the
sandbox could not see the fixture directory, so every run correctly refused to review a board it
could not read — and a zero that means "could not look" is indistinguishable from a zero that
means "found nothing".

So cases carry their design inline. It makes them longer and it removes the entire question.
That lesson generalises beyond evals and is the reason several tools in this plugin distinguish
`could-not-run` from `ok`.

## What a good case looks like

- **A real defect, from a real board**, that a real review found. Invented defects measure
  whether the model can read a prompt.
- **A frozen design.** A case whose input tracks a live project breaks every time the project is
  fixed, which trains everyone to ignore it. The boards in these cases are snapshots and are
  meant to stay wrong.
- **Restricted context.** If a project's own notes spell the finding out, an agent allowed to
  read them passes by reading the answer.
- **Graded on consequence, not vocabulary.** A finding without a consequence is an observation.
- **Penalties for noise.** A dimension that repeats what a deterministic check already owns is
  producing false positives, however correct they are.
