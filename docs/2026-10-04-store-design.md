# The store and its ways in — design (P94), living draft

**Status:** being designed with the PO, one question at a time (his request, 2026-10-04: *"keep asking me and
iterating until we have a well designed system … that we don't produce unnecessary bloat, but it also is a
good and useful tool"*). Each answer lands here as it is given; nothing is planned until the PO has reviewed
the whole. Process (his choice): story map + flows + example mapping; a spec and a plan for the first slice
only. Input: the P85 discovery (`docs/2026-10-04-store-discovery.md`) and a four-lens design council
(flows and stories, domain model, architecture, skeptic and trust), read-only and offline.

## 1. What it is for — decided

- **The database gets better and better**, meaning: **more parts known** (researched once, found from every
  project), **proven by use** (a part that built and ran says so), **fewer requests, measured** (a project
  shows what it cost and what came from reuse). Not "every part complete": a record grows when a stage needs
  a fact (W21).
- **Store first:** general requirements and options first; then what the store already has that works
  similarly; research only for the gap.
- **Ways in**, all on one store: goal first, module first, a combination, the whole drawer, revive, swap,
  extend (P76).
- **No bloat, but useful** — every piece names the journey step it serves, or it is cut.
- **Later, kept in mind:** a viewer and manager (P86); a shared part database (P84, no selectable backends).

## 2. The journeys — the story map's backbone (draft, from the flows lens)

Every way in runs on one spine: **D** note what I own → **M** match a need against the store → **C** choose →
**G** research the gap (only when nothing similar) → **L** the part list the chain accepts → **T** tally what it
cost and record proof by use. Some ways add a step: **I** ideas from what I have (module first, combination,
whole drawer), **F** does it fit (combination, swap, extend), **R** reverse-engineer what stays (revive). I and
S (shaping the idea) are conversation: spark gives facts, the conversation writes ideas (as P56 does for
firmware).

| Way in | First sentence | Flow |
| --- | --- | --- |
| Goal first | "something that tells me my plant is thirsty" | S → M → C → G (gaps) → L → T |
| Module first | "I have this DS3231 — ideas?" | D → I → S → M → C → G? → L → T |
| Combination | "these 3 — ideas?" | D ×3 → F → I → S → M/C → L → T |
| Whole drawer | "what can I build with what I have?" | D → I (ranked by how much is owned) → S → M → G (minimal) → L → T |
| Revive | "my bin's board died" | R → D (salvaged parts) → S → M → C → G → L → T |
| Swap | "replace the DFR0641 in irrigation" | the part's role → M (same role) → C + F → G? → L → T |
| Extend | "add a buzzer to the quickstart" | the project's free pins → S → M → C + F → G? → L → T |

## 3. The drawer — decided so far

- **Owning is not researching.** A drawer entry is light — what it is, how many — and a part's facts are read
  only when a design considers it.
- **Four ways in, one entry** (the PO, 2026-10-04): **order history** (DFRobot account, AliExpress orders,
  confirmation emails — exported or pasted), **photos of the drawer** (read by `/spark:identify`), **a typed or
  dictated list**, and **adding as I go** (a part joins when a project or idea mentions it). Every route makes
  the same entry; none of them researches.

## 4. Architecture — options under review

From the architecture lens (details in the council's report, to be folded in when chosen):
- **A** — one home and one layer table inside `parts.py`; cheapest, but `parts.py` passes 1,000 lines with
  five concerns.
- **B** *(the lens's recommendation)* — `store.py` owns *where things are and how bytes move* (one home, one
  table of layers nearest-first, contained writes, the checked keep/fetch, the one network door); `parts.py`
  owns *what a record must be* and the commands; every command answers in JSON, which is the stable
  interface a viewer and agents use. About +90–110 of the 292 code lines left, built thin.
- **C** — also a separate `contract.py` and a generic get/put CLI; the most churn, no story needs it yet.

## 5. Open questions (asked one at a time)

- Which walking skeleton comes first.
- What a drawer entry holds beyond "what and how many".
- The architecture option.
- How "a similarly working thing" is matched (the capability vocabulary).
- How cost and proof by use are recorded.
