# The lenses' questions and evidence

The folder is `docs/discovery/2026-11-26-p1193-change-tracking/`. Each lens reads `brief.md` and
`jobs-and-journeys.md` first, then its slice. The store is read-only. No web, except where a slice says so.

## Shared slice

- The card: `gh issue view 1738`. The project timeline: `gh issue view 1688 --comments`.
- The git discovery: `docs/discovery/2026-11-25-spark-and-git/brief.md` (D5 to D16) and `items.md`.
- The P1160 finding: `docs/discovery/2026-11-25-p1160-take-back-chain/finding.md`.
- The words: `docs/guide/words.md:14-29`.
- The store's shared side: `gh issue view 123 --comments`, `gh issue view 437`, `gh issue view 505`,
  `docs/archive/2026-10-04-store-discovery.md:140-220`, and
  `docs/archive/discovery/2026-10-10-p158-gaps-and-refactoring/proposal.md:400-450`.
- The past-breadboard council in the store: `councils/past-breadboard/architect.md` and `refuter.md`.

## po-assistant (Existing first, Risks and assumptions)

Questions: What already does each job J1 to J8, in spark, in git, and in the maker's own tools? Which of the PO's
earlier decisions does this epic keep, widen or conflict with (P1148 D5 to D14, P1160's answers, the 10-04 store
decision)? Which job is "maybe" in his words and which is "definitely"? Is anyone blocked without this now, against
the MVP bar? What must be true for one strategy to serve both the project and the store? The pre-mortem: "It is six
months after this shipped, and it failed. Why?"

## The user's journey, walked by the ux-ai-ux lens (D1 folded the user lens into it)

Questions: Walk the two journeys in `jobs-and-journeys.md` as the maker does them today. Use a real project in the
PO's folders, read-only, with `GIT_OPTIONAL_LOCKS=0` for any git read. Where does the maker stall, guess or come to harm?
What does an outside change look like today (a board.tsx edit, a hand edit of needs.json, a `git pull`)? What does
the maker need to see to trust a take-back to a named point? What is private in a part record and must never leave
the store?

## tech-lead (Feasibility, fit with the technical direction)

Questions: What does each job take and touch, in the code? Which claims can a read settle, and which need a spike?
Can one git-backed seam serve a project folder and the store's shared places, given the store's refusal of private
places inside git (`scripts/spark/records/store.py:380-392`)? What is the smallest first slice that serves the MVP
bar? Which existing cards (P1151, P1152, P1154, P1155, P1163, P342, P390) does this widen, and in what order?

## architecture (the core's fit, on Opus)

Questions: Where does the one strategy sit in the core, and what is its interface? Is it one Strategy with two callers, a
project and a store? Or is it one lower seam ("a versioned set of files") under two higher Strategies, the project
timeline and a shared store? How is it chosen by one configuration and handed in, never built inside an
Operation (`scripts/spark/core/`, `scripts/spark/operation_catalogue.py`, `scripts/spark/records/storage.py`,
`scripts/spark/records/project_commit.py`)? What do a human strategy and a server strategy do for each verb (keep,
list, mark, compare, merge, take back, push, pull)? Which verbs does a human strategy refuse? Where do LangGraph's
checkpoints and MCP's model fit (P1148 D12)? The PO: "the architecture needs to be well made so that we can change
these srtrategies and tools and its reusable, dry". Git's own documentation: at most 5 fetches, each naming the
decision it serves.

## ux-ai-ux (the person and Claude, the PO's rule of 2026-10-18)

Questions: What words does a person see for a mark, an outside change, a compare and a push? How does a compare
show a layout change (the drawing, or text)? What does Claude read to know that a file changed outside spark, and
which words tell it what to offer next? How does an interface with no Claude (the CLI, a server) show each moment?
Read the design canvas's "Moment: undo that, take a step back" as #1688's comment of 2026-11-25 describes it. Use
only files in the repository and the store's councils folder.
