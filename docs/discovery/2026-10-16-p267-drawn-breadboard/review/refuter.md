# PR #303 refuter (Opus), 2026-10-16

Every run was in memory with an empty SPARK_HOME. Plan mode was on, so the lead wrote this file from the reply.

1. HOLDS: four jumpers, 5 cyan, 6 blue, 7 purple, 8 magenta. The worst leg is 1.2 px off. The tolerance is per
   axis, so a leg can be 2.1 px off in a straight line.
2. PARTLY: the diagram's sha256 matches, and the screenshot shows the LED lit. Unproven: no part was run turned 180
   degrees, the generated breadboard.json was drawn but not simulated, and 1.5 px is above the 1.2 px seen to connect.
3. PARTLY: the turn formula and the XIAO's offsets are right (0.00005 px). Confirmed defect: wokwi-led is 40 x 50
   (wokwi-elements `src/led-element.ts`, lines 72 to 73), so its center is (20, 25), not (25, 20). The resistor's
   and the button's published sizes differ a little from twice their measured centers.
4. HOLDS for the fixture: the drawn nets equal the four points. Test gap: the row test ignores jumper ends.
5. PARTLY: the S3 line and the stale-file removal hold. Confirmed defect: a supply step is skipped without a word.
6. HOLDS: the same sha256 under PYTHONHASHSEED 0, 1, 42 and random.
