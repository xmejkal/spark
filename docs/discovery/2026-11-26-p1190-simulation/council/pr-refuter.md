# PR #1742: the refuter on the PR as it stands

Read on 2026-11-26 in the worktree at 8da2718d, with the cards read through `gh issue view`, `gh api .../parent` and `gh api graphql`.

1. CONFIRMED. Two card notes mix up item 14 with P1224 #1773. #1772's Notes say "takes over P1224 #1773 (the stand-in runner spike)", and #1773's Notes say "replaces P1224 #1773", which is the card itself. items.md:209 and :220 say "item 14", which was never filed (items.md:160). Fix: in both notes, write "the discovery's item 14 (not filed)" instead of "P1224 #1773".

2. CONFIRMED. P308 #374 closed as "absorbed", but half of it was lost. Its Value proven by reads "a stand-in pass opens deploy only when the project says so, and deploy says 'tested on the stand-in simulator only'". Its close comment names only "the run log names its simulator and grade" (P1213 #1762) and gate A (P1220 #1769). Neither Done when holds the deploy rule. Fix: add the deploy half to #1762's Notes, or say in #374's comment that it is dropped, and why.

3. CONFIRMED. D17 and D18 pull in two directions. D17 says "Item 19's first steps run before item 6's plan", and README.md:18-19 runs them "beside steps 1 to 3". But D18 parks item 19 (#1773) in "parked, after v0.10", while item 6 (#1761) sits in v0.10. #1761's Depends on reads only "P1078 #1582". Fix: add "its plan waits on P1224 #1773's first steps (D17)" to #1761, and relay to the PO that the parking delays a v0.10 card.

4. CONFIRMED. D15 claims more than the PO said. It reads "the PO reverses the delegated 'not now' (D4) and the non-goal reading". His quoted words ask for a spike "seeing how difficult or possible it would be". scrum/VISION.md:81 still lists "Reimplementing tscircuit, KiCad or Wokwi" as not a goal, and no item proposes changing it, as item 17 does for the v0.10 line. Fix: D15 says the non-goal stays until he changes it, and #1772 names the conflict.

5. CONFIRMED. D16 and D18 mix the PO's quote with a reading but do not say so, while D13 does ("the reading by spark-main"). D16 turns "basically what wokwi has" into "Wokwi's full set" and "maybe even the steps" into firm scope (item 10). D18's "File the v0.10 items now ... with no Ready order" is outside the quote marks, and it is not marked as a reading. Fix: mark both "So ..." parts "the session's reading".

6. CONFIRMED. brief.md's header is out of date. Line 13 still asks the PO about gate A, which D10 answered. Line 10 says "The PO filed the v0.10 cards", but line 134 says "Filed by the simulation session on spark-main's word". Fix: remove the gate A clause and write "the cards were filed on the PO's yes".

7. CONFIRMED. Lines in other files that are now untrue. items.md:6 says "Nothing is filed". items.md:208 gives item 18's slice as "ask the decider for a new one", but the card sits in parked, after v0.10. README.md:3 says "Nothing here is decided". README.md:142 says "D1 to D9", README.md:145 says "nine assumptions" (A1 to A12 exist), and README.md:146 says "Nothing is filed". story-map.md:28 keeps item 14, which item 19 replaced. story-map.md:30 puts item 15 under "later", but its card is in v0.10. Items 5, 17, 18, 19 and 20 are not on the map. risks-and-tests.md:6 and :40 still wait on Q9 "at his next message" (D13 answered it). risks-and-tests.md:25 tests A2 with "item 14's spike". Fix: update each line to match D13 to D18.

8. REJECTED: the claim that the cards and the folder might be unsafe or misfiled. All 19 titles match their items, and so do Needed by, Done when and Depends on (apart from points 1 and 3). Every parent matches brief.md:134: #1758 sits under P1038 #1521, #1769 under P79 #16, #1773 under #1772, and the rest under #1735. All 19 cards are in Idea, with #1772 and #1773 in "parked, after v0.10" and the other 17 in v0.10. #1452, #535, #536 and #374 are Done, and every card their comments name exists. The folder has no home path, token or vendor file. `.outside-snapshot.json` holds only repository paths and hashes, as in 15 other discovery folders.

Not checked: the PO's words as spark-main relayed them. "MVP part now" is not in the store, so neither the quotes in D10 to D19 nor which items count as "MVP" can be traced to him.

## Searches
none
