# P136's discovery inputs, 2026-10-06

The reads run on 2026-10-06 to answer the PO's questions behind the epic P136 (#70, full circuit checks), P94 (#17,
the store and its ways in) and P76 (#5, from a vague idea). They are **inputs to a discovery, not decisions**. What the
PO decided is recorded on the cards. Each read was checked by a separate refuter; **where a read and its check disagree,
the check wins**.

| read | its check | the PO's question | summary on |
| --- | --- | --- | --- |
| [checks-architecture.md](checks-architecture.md) | [checks-architecture-verify.md](checks-architecture-verify.md) | Why so much I²C? Will spark check other buses? Can it learn new rules? | P136 |
| [data-chips-format.md](data-chips-format.md) | [data-chips-format-verify.md](data-chips-format-verify.md) | Easy data updates, modules downloaded with their chips, every form of a component | P94 |
| [remedies.md](remedies.md), with [remedies-b25-worked.md](remedies-b25-worked.md) | [remedies-verify-maths.md](remedies-verify-maths.md), [remedies-verify-claims.md](remedies-verify-claims.md) | Can spark say "here is a problem, add this", and calculate the parts? | P136, bin B25 |
| [suggestions.md](suggestions.md) | [suggestions-verify.md](suggestions-verify.md) | Function-first suggestions: from a need to options to pick | P76, P136 |
| [board-proposal.md](board-proposal.md) | — | The board's order and WIP limits | P146 (#80) |
| [process-proposal.md](process-proposal.md) | its own skeptic pass | A process that fits how we work | P146 (#80) |

Two corrections to read first:
- **remedies.md and B25.** Its passive-fix numbers ignore the VL6180X GPIO1's own input current (up to 10 µA). With it
  counted, no passive pull-down holds at the worst corner, and the transistor stage needs R_b 150 kΩ and R_be 68 kΩ
  (remedies-verify-maths.md).
- **data-chips-format.md §1.2.** rc-car wrote the button record first; spark adopted it and improved it four times
  (data-chips-format-verify.md).

Paths in these files are as they were on the machine the reads ran on.
