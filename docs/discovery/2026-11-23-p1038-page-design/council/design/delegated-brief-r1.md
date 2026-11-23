# Delegated council, after round 1 of the P1038 design: the brief

2026-11-23, 18:30 CET. The PO is away, and the auto mode runs until he returns. His choices go to a council of three seats: the PO seat (Fable, it answers from his recorded words), the architect, and the tech lead (Opus). Each answer is recorded as delegated, his to change. Each seat answers alone and reads the same files. Their agreement is therefore not three independent views.

Read: [design.md](../../design.md) (the architect's draft), the four round 1 reports in this folder (r1-architecture.md, r1-ux.md, r1-tech-lead.md, r1-refuter.md), and [brief.md](../../brief.md) (D1 to D28, and the Hand-off).

For each question, answer with one option (or a change), one line of reason, and the D rows or report ids that you rest on.

## Q-A, open item 1: build before the PO confirms the design

The PO seat proposed "no build in this epic before the PO confirms the design" (D24, 1 of 3). Options: (a) yes for P1038's sub-issues, and slice 0 (P1043 and P1035, under P793) goes on. (b) No, slice 1 starts after round 2.

## Q-B, open item 2: the Flash and Deploy button no-go

P820's no-go: no Flash, Deploy or Run-live-code button on the page. The PO seat proposed "not now" (D24). Options: (a) keep the no-go through the walk. (b) Lift it now.

## Q-C, open item 3: the share window for issue titles

The published copy holds the private repository's issue titles. Spark cannot see a share made in the Artifact's own menu. Options:

- (a) Fail closed (P-3). When `.spark/page.json` holds an "owner only" value read from `get_artifact`, the page shows issue text. In all other cases it shows none. At each publish Claude says "This page shows your project's open issue titles. Before you share it, tell me, and I write it again without them" (UX's item 3).
- (b) No issue text on any published copy. The issues show only on the page on disk and in `show --json`.
- (c) (a) now. If the walk's A7 read finds a leak, then (b).

## Q-D, D23's clause "a failed fetch writes nothing" (UX-6, the refuter's item 10)

D23 says: with no file, no gh or no network, the page says "issues not read" with its cause, and a failed fetch writes nothing. No design meets both clauses for "no network". Options:

- (a) Keep "writes nothing". The page says "issues not read" or shows the old list with its read time. The cause reaches the person through Claude only. The narrowing is recorded for the PO.
- (b) A failed read keeps the old list and writes only `last_try: {at, code}`, so the page names the cause. This changes D23's "writes nothing".

## Q-E, D11 and story 1d (several picks at once)

D11, confirmed by the PO: slice 1 holds "several picks at once and the picks per need". D24: no new interface for the click path (P829 #1187, whose Done-when walk is still the PO's). D26: 1d is "click-path work decided with P829". Options:

- (a) 1d stays in slice 1, with `keys` on the request row, built after P829's walk. The walk after slice 1 can run without it (the draft, the refuter's S-1 verdict).
- (b) Cut 1d from slice 1 and file it under P829. Slice 1 groups the picks per need with today's one-click buttons (the tech lead's S-1). D11's item then misses this epic's walk.

## Q-F, the deploy run and the page (the refuter's R-1)

P1035 PR 2 writes page.html after a pick only. `deploy.py` has no follow-up, though a deploy writes a board log into the project. The stand that was wrong in the P934 walk was the deploy. Options:

- (a) Widen P1035 PR 2 (#1518) to give `DeployImage` the follow-up.
- (b) A new small story in slice 0, after P1035 PR 2.
- (c) State the limit. The page after a deploy is right only after `/spark:page`.

## Q-G, A7's shared-copy read in the walk (the refuter's R-2)

The parts phase prints other projects' names ("held by ..."). A7's pass line asks for zero such names on a shared copy. The share route itself is later (D9, D20). Options:

- (a) Build the held-by rule in 1f, so the walk's shared read can pass.
- (b) Drop the shared-copy read from this walk. A7 stays open for a share, on P834.
