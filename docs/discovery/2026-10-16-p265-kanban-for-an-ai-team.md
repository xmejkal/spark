# P265: Kanban for an AI team

Card: [P265 #297](https://github.com/xmejkal/spark/issues/297), a spike. Read on 2026-10-16. It feeds
[P266 #298](https://github.com/xmejkal/spark/issues/298), the coach skill.

## Short version

Spark already runs most of what the Kanban sources teach: a board, limits per stage, card age, a commitment point and
two cadences. Spark is missing the numbers that close the loop. Nothing flags a card past the service level, and
nobody measures cycle time or throughput, so the guess of 2026-10-06 is never corrected. For an AI team, the sources
add three ideas. Give each agent one deep job and keep the breadth in the main session. Keep a small bank of verified
lessons that each agent reads. Run each process change as an experiment with a hypothesis and a check date, the way
Toyota Kata does. The coach skill (P266) is the place for the last two.

## The tips

Each row says what to try, why, and how the team sees that it worked. "Keep" means that spark already does it.

| tip | source | spark today | try | how we see it worked |
|---|---|---|---|---|
| Limit the work in progress. More work at once makes each item take longer. | [Kanban Guide 2025.5](https://kanbanguides.org/the-kanban-guide/2025.5/pdf/kanban-guide.v2025.5.en.pdf) | the limits per stage, the gate (`scrum/README.md`) | keep | the gate stays green |
| Watch work item age, and act on an item that ages past the service level. | Kanban Guide 2025.5 | the status prints days in a stage, but nothing flags a card past "2 working days, 8 times in 10" (card C3, not built). P218 is at 3 days in Design today | build C3 in `tools/board.py status`: one `!` line per card past the service level | the day-close names each aging card, and the weekly look says what the team did about it |
| Measure cycle time and throughput, and set the service level from them. | Kanban Guide 2025.5 | the service level is a best guess. No tool counts Done cards per week or days from Build to Done | the weekly look adds two numbers, computed from the board: cards done, and the 85th percentile of days from Build to Done | the trial on 2026-11-02 replaces the guess with a measured value |
| Replenish at a commitment point, on a steady beat. | [Kanban cadences](https://businessmap.io/blog/kanban-cadences) | Ready is the commitment, and the PO orders it. At 2 cards in Ready, the hook warns | keep | Ready never runs empty while Build waits |
| Review the service as a whole, weekly. | Kanban cadences | the weekly look | keep. Put the two flow numbers above in it | the weekly look is posted each week |
| Make blockers visible. | Kanban Guide 2025.5 | "Waiting on" and "Waiting since", and the at-risk close after three days | keep | no undated wait |
| Give each member one deep skill and some breadth (T-shaped). Find the bottleneck with a skills matrix. | [Agile Pain Relief](https://agilepainrelief.com/blog/how-to-cross-skill-and-grow-t-shaped-team-members/), [InfoQ 2016](https://www.infoq.com/news/2016/12/skill-matrix-teams) | each agent has one job (the roster's test in `scrum/TEAM.md`). The main session holds all breadth, so it is the only member that can plan, write and merge | add one small table to `scrum/TEAM.md`: each kind of work, and who can do it (agent, lens, script or main session) and on which model | the retro names work that waited for one member, and the matrix shows it |
| Specialize for depth, but use more agents only for breadth work. | [Anthropic, multi-agent research](https://www.anthropic.com/engineering/multi-agent-research-system) | the roster's four tests: isolation, restricted tools, fan-out, context budget | keep. Add the source's number to the test: a multi-agent run used about 15 times the tokens of a chat | no agent joins without one of the four tests |
| Keep a bank of lessons. Agents that read verified lessons from earlier runs do better. | [Lessons Learned, NeurIPS 2025](https://arxiv.org/abs/2505.23946) | the findings go to `docs/observations/INDEX.md` and to memory. But each agent starts fresh and reads none of them | each agent file gets a "Lessons" part of at most five lines, taken from verified INDEX rows. The retro adds or removes lines | the same finding is raised less often across runs of one agent |
| Run each process change as an experiment: target, obstacle, one step, expected result, and what we learned. | [Toyota Kata](https://www.infoq.com/articles/book-review-toyota-kata-agile/), [the coaching kata](https://www.gembaacademy.com/school-of-lean/toyota-kata/coaching-kata-essentials/coaching-to-reflect-on-the-last-experiment) | the refuter is an experiment since P261, judged at the next retro. But it has no written hypothesis or check | the coach (P266) proposes one experiment per retro, in this form, and starts the next retro with the last one | each retro starts with the result of the last experiment |

## Notes for P266, the coach skill

- The coach uses the five coaching kata questions. What is the target? What is the condition now? What did the last
  step do, and what did we learn? What is the obstacle now? What is the next step, and what do we expect?
- The coach proposes one experiment, never a rule. The PO decides, as for any process change (`scrum/TEAM.md`).
- The source says that a step with an even chance to fail teaches the most. The coach says that chance.
- The scrum master agent was cut on 2026-09-29, because nothing routed to it. A cadence must call the coach, so that
  it passes that test. The retro is that cadence.
- The skill stays project-local. A plugin user has no use for how its author works.

## Limits of this finding

- Two sources are vendor blogs (Businessmap, Agile Pain Relief). They agree with the Kanban Guide on what they cover.
- The Lessons Learned paper measures small models on code optimization, not a team process. The "Lessons" tip is
  therefore a hypothesis for one retro, not a proven practice.
- The Kanban Guide was read from search summaries and its PDF title, not page by page. No page numbers are given.
