# Jobs and journeys

## Who
- The PO, a hobbyist in Prague who builds ESP32 gadgets with spark and owns 99 DFRobot drawer entries · E drawer, council/po-assistant.md PO-2 · n = 1 <!-- REQUIRED:who -->
- Claude, the agents and commands that pick and wire parts from records (`/spark:idea`, `/spark:build`, the researcher) · E commands/idea.md, commands/research.md
- The programs that read a record: the breadboard sheet, the Wokwi diagram, the board page · E council/tech-lead.md TL-3, TL-4

## Jobs
- Job 1 · When I pick a part for a goal [E commands/idea.md], I want spark to find the one I own by what it does [D the PO, P735 card], so I do not research or buy it again [E ★C4].
- Job 2 · When I wire a module on the breadboard [E STORY_MAP.md step 10], I want its real pin order and picture in front of me [D the PO, P735 card], so I do not swap 3V3 and GND [E ★C8]. <!-- REQUIRED:jobs -->
- Job 3 · When spark shows my gadget on the board page [D the PO, P735 card], I want each part's outline, holes and connectors [D the PO, P735 card], so I can plan the layout and the enclosure [H the user lens, USER-25].
- Job 4 · When Claude researches a part [E commands/research.md], it wants one flow with swappable sources and strategies [D2], so the same record comes from DFRobot today and from other shops later [D2].

## Today they…
- Job 1 · `--need` matches id, name, kind and alias, not the drawer's function, and does not search boards · E ★C4 <!-- REQUIRED:today -->
- Job 2 · the sheet prints "Put <Part> in the breadboard, each pin in its own row", and the drawing shows Wokwi's stock picture or stops · E council/user.md USER-2, USER-4, ★C3
- Job 3 · nothing shows holes or connectors. A board record holds `physical` header rows, a part record holds `body_mm` only · E ★C2
- Job 4 · the researcher runs about 20 commands and hand edits per part, reads code to learn the flow, and copies another record's shape · E walk/*/diary.md Steps and Gaps

## Journeys
### The PO: from an owned DFRobot part to a wired part <!-- REQUIRED:journey -->
| step | what they do | evidence | friction or harm | today | open question |
| --- | --- | --- | --- | --- | --- |
| 1 | owns the part, it is in the drawer | E drawer, ★C9 | about 19 of 112 entries link a record | partly | which entries are in scope (Q3) |
| 2 | asks spark for a part that does the job | E ★C4 | the owned part is not found, spark says "Research it" | not yet | none |
| 3 | spark researches the part | E walk diaries | about 20 steps, hand edits, zips cannot be kept, boards have no flow | partly | none |
| 4 | the record is checked | E ★C6 | `--validate` passes a bent record (SEL as a ground pin), `--read` picks the wrong row | partly | none |
| 5 | the record is linked to the drawer entry | E walk/sen0526/diary.md Gaps | no step does it | not yet | none |
| 6 | the breadboard sheet shows the part | E ★C3 | stock picture or no drawing, no real pin order on the sheet | not yet | needs P734 |
| 7 | the PO wires it | E ★C8 | a wrong vendor table swaps supply pins, a warning on a board has no place | not yet | did a wrong pin order ever cost him a part? |

```mermaid
flowchart LR
  s1["owns the part"] --> s2["asks for a part by job"]
  s2 --> s3["spark researches it"]
  s3 --> s4["record is checked"]
  s4 --> s5["record linked to the drawer"]
  s5 --> s6["sheet shows the part"]
  s6 --> s7["the PO wires it"]
```

### Claude: researching one owned part
| step | what they do | evidence | friction or harm | today | open question |
| --- | --- | --- | --- | --- | --- |
| 1 | reuse: `--need`, `--kept` | E ★C4 | misses owned parts and boards | partly | none |
| 2 | find the vendor pages | E walk diaries Steps | the wiki URL is guessed, search returns shops | partly | which strategy first (D2) |
| 3 | keep the documents | E ★C7 | zips refused, keys are CDN hashes, title and version stay null | partly | none |
| 4 | read the facts | E ★C6 | `--read` picks wrong rows, schematics need hand rendering | partly | none |
| 5 | write the record | E ★C2, ★C6 | no field for the physical facts, `--fact-set` refuses `legs` | partly | where geometry lives (PO-28) |
| 6 | check and hand over | E ★C5 | boards have no `--unverified` or `--sources` | partly | none |

```mermaid
flowchart LR
  c1["reuse"] --> c2["find vendor pages"] --> c3["keep documents"] --> c4["read facts"] --> c5["write record"] --> c6["check and hand over"]
```
