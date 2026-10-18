# R9 council: Agile/Scrum coach
Facts come from facts.md, the retro inbox, RETROSPECTIVES.md and scrum/README.md. Lines marked (opinion) are my view.

## 1. Why retros stopped after R8

- Cause: the only trigger is an epic's last story (README cadence table). The epic that fires it, P235 #224,
  is still in Build at slice Live 0. So the trigger has not fired in 17 days, while 134 PRs merged
  (the refuter's count; 51 of them since 10-15).
- The backup trigger is the weekly look with one retro line. It has no command (README: "has no command", posted by
  hand). A step done by hand, with no owner and no output check, is skipped under load. I found no weekly-look
  retro line in the files I read (opinion: it was not done, so the net had a hole).
- The inbox waits for "the epic's end" (inbox header). It holds 15 dated items, 6 of them experiments marked "to judge"
  (3-round plan council, chime hook, refuter on Opus, weekly retro line, the P261 table, agent-log reading).
  No experiment has a due date, so none returns.
- R8's "check at R9" actions belong to the old four-repository era, and nobody carried them forward.

## 2. Cadence proposal (opinion)

- Trigger: whichever comes first of 10 merged stories (cards, not PRs) or 7 days. An epic's end also fires it.
  Ten stories is about 3 days at the current rate, so the weekly clock is the usual one.
- Owner: Claude prepares, in one pass of a script over the board, the merged PR list and the agent logs. It writes
  one page of numbers (the table in facts.md) plus the inbox, before the session. The Lean/Agile council reads that
  page and returns at most 3 proposals.
- Length: 30 minutes with Petr, live. Order: last experiments' verdicts (10 min), the numbers (5), the inbox (10),
  pick at most 2 changes (5). Petr decides. Claude does not close a retro alone.
- Running inbox: keep retro-inbox.md, but each line gets a type (slip, question, experiment) and a date. A line
  of type experiment carries a "judge on" date and one measurable check, written when it starts.
- Return path: each retro entry lists its experiments in the table "change / check / due retro". The next retro opens
  with that table, and a result is one of held, did not hold, or dropped, with the number beside it. An unjudged
  experiment at its due retro is dropped by default, so none lives on silently.
- Safety net: the session-start hook prints "retro due" after 7 days or 10 stories. A prompt, not a gate.

## 3. Biggest PO-collaboration and DoD issues in the inbox

- WIP slips. Inbox 10-15, 10-17 and 10-18 show three slips (P239 and slice 0, P272 into Build, spike P295 started
  with 4 in flight). Rule: warn and ask first. The rule was written, the slip came back twice. The agent run, not the
  card move, is where the limit is bypassed. Small change: the rule counts agent launches. Before launching a
  builder or spike, Claude prints "in flight: N of 4" from board status as the first line of the launch note.
- Slots held by epics and PO-only waits. P218 #200 sits in Design 4+ days with no Waiting on, and an epic card
  takes a slot beside its child (inbox 10-16, 10-17). The push hook blocked a merge fix over it. Small change:
  count only cards of the type story, spike or chore against the limit, and every card waiting on Petr alone
  gets "Waiting on: PO" at once. Test it for one week and judge at the next retro.
- Done and Review lack a record. The board keeps no date for entering Review (facts.md), so the 2-day service level
  cannot be read. Mutation fields exist on 11 Done cards only. Small change: add one DoD line, "Waiting since is set
  on every card that enters Review", and let the day-close print the Review age. No new field is needed.
