# P669 spike: the two desk tests before the pin-conflict bridge

Issue: https://github.com/xmejkal/spark/issues/897. Epic: P663 #892. Run on 2026-11-07, desk only (R0), no code.
The plan, with its refuter check, is in the PR's description.

## Short version

> Both tests pass. A1: all 8 GDI pins in the record match the kept V1.3 schematic and the games' `gdi.py`. A2: one
> shape decides K1, K2, K3 and K5 with at most one rule left over per kind. P665 #894 can start once P664 #893 is done.

The schematic is the one independent source for A1, because `gdi.py` copied its pins from the record. A2 passes
under the strict count too, but the shape needs one more field (`movable` on `Claim`) and one shared reader of the
connector facts. The one-reader rival of Q17 leaves the same per-kind rules, so the model wins on its one `Conflict`
value for the JSON answer and the sheet, not on fewer rules.

## A1: the eight GDI pins

Pass line, set 2026-11-07 (brief.md:77): all 8 match both the kept V1.3 schematic and the games' working `gdi.py`.
Any mismatch stops the card.

The schematic was read first, before the record: `FireBeetle2_S3_schematic_DFRobot_V1.3.pdf`, sha256
`4062428ab603999097297ea1773e9fefcc4e6f0fd8fe9acf55a3503b90f89406`, page 1, connector P2, rendered at 600 dpi with
`pdftoppm`. Each net label sits above its wire. The record is `tests/data/parts/dfr0664-tft-2in.json`, fact
`gdi_on_firebeetle2_s3_gpio`. The firmware is `~/Development/firebeetle-games/games/gdi.py` and `pins.py` at commit
707e35a. All five copies of `gdi.py` on this Mac are the same file (sha1 c5d0281c).

| signal | P2 pin and net (image) | record | firmware, line | match | the firmware value's origin |
|---|---|---|---|---|---|
| BL | 17 BLK, IO21 | 21 | `gdi.py:19` 21 | yes | copied, and verified on the bench 2026-11-01 (`gdi_backlight_gpio_on_firebeetle2_s3`) |
| SCLK | 15 SCLK, IO17 | 17 | `pins.py:4` 17 | yes | spark's assigner. Exercised: the display ran (W4:30) |
| MOSI | 14 MOSI, IO15 | 15 | `pins.py:5` 15 | yes | spark's assigner. Exercised: the display ran (W4:30) |
| MISO | 13 MISO, IO16 | 16 | `pins.py:6` 16 | yes | spark's assigner. Not exercised: no firmware here reads the SPI bus, and the s3lcd path (`lcd.py:203`) does not take MISO |
| DC | 12 DC, IO3 | 3 | `gdi.py:15` 3 | yes | copied. Exercised: the display ran (W4:30) |
| RST | 11 RST, IO38 | 38 | `gdi.py:16` 38 | yes | copied. Used by the driver at start (`lcd.py:204`). A running screen does not prove it alone |
| CS | 10 LCS, IO18 | 18 | `gdi.py:17` 18 | yes | copied. Exercised: the display ran (W4:30) |
| SDCS | 9 SDCS, IO9 | 9 | `gdi.py:18` 9 | yes | copied. Not exercised: only held high (`app.py:128`) |

The reverse cable also agrees. `gdi_connector_pin_order` puts VCC to SDCS on module pins 1 to 10, so board pin 19-n
gives 18 to 9. Those are the P2 pins above and the GDI pin numbers in `gdi.py`'s comments.

Verdict: 8 of 8 match the schematic and 8 of 8 match `gdi.py`. A1 passes. The `gdi.py` column adds no independent
evidence for the five pins it copied. The bench adds evidence for BL, SCLK, MOSI, DC and CS.

A side finding: `pdftotext -bbox` alone ties each net label to the pin one row up (`NLIO21` lies nearer `PIP2018`
than `PIP2017`), because the label sits above its wire. Only the image gave the right pin. A tool that reads
schematic text needs the image check.

## A2: one shape for four kinds

Pass line, set 2026-11-07 (brief.md:77): at most one per-kind rule left over for 4 of 4 kinds. More than one means
the kinds are separate fixes, not a model.

The shape is AR-9's diagram: `Resource` (`kind`, `id`, `shareable_by`), `Claim` (`holder`, `resource`,
`source_fact`, `wanted_as`), `Conflict` (`kind`, `claims`, `resource`, `options`). The general rule: claims on one
resource whose holders `shareable_by` does not allow make a `Conflict`. Its `options` are the moves of the claims
that can move, and its outcome is a stop when an option exists and a note when none exists. Its `kind` (the K code)
comes from a table of the two holders' types, not from a branch.

A rule is left over for each of (a) a branch that tests the kind, (b) a fact it needs that no record holds today,
(c) an attribute that only this kind uses for its outcome. This test was fixed in the plan, before the table.

| kind | real case | `Resource` | claim 1 | claim 2 | outcome | left over |
|---|---|---|---|---|---|---|
| K1 | I2S_BCLK and JOY_SW on GPIO18 and GPIO9 (brief ★C4) | pin GPIO18, exclusive | the GDI connector as LCS, `gdi_on_firebeetle2_s3_gpio.CS` | the signal I2S_BCLK, from requirements.json | stop, move I2S_BCLK. Prevented when connector claims enter first (AR-13) | 0 |
| K2 | the connector's DC on the strap GPIO3 (P581 row 3) | pin GPIO3, exclusive | the GDI connector as DC, `.DC` | the chip at reset, `pin_roles.strapping` | note, no claim can move (D6) | 0 for this case. 1 with D7's case: a person names a strap with no connector. The general rule says stop, D7 says warn, and a flag lets it through. Only straps use that flag (c) |
| K3 | BL and ONBOARD_LED on GPIO21 (P581 row 4) | pin GPIO21, exclusive | the GDI connector as BL, `.BL` | the onboard LED, `pin_roles.onboard_led` | note, no claim can move (D6) | 0 for this case. 1 with today's placement: the assigner may put a signal on GPIO21 at a cost (`ROLE_PENALTY`, `assign_pins.py:85`), and the general rule would stop it. Keeping today's answer needs a soft onboard claim, used only by K3 (c) |
| K5 | two signals name one pin (`assign_pins.py:283`) | the named pin, exclusive, or shared by one bus line (`SHARED_LINES`) | signal 1, named | signal 2, named | stop, move either. A shared bus line is no conflict (`shareable_by`) | 0. The closest call is the SS branch (`:279-281`): a second SPI select goes anywhere. It tests a line name, not the kind, and its claim names a role, not a pin, so it is placement. Counted strictly, it is 1 |

Shared needs, counted once and not per kind:

- `movable` on `Claim`. All four kinds use it for their outcome, so the diagram needs it.
- A reader of the connector facts. K1, K2 and K3 need connector claims. The board record names no GDI connector,
  and the part record ties the pins to the board only in a key name (`gdi_on_firebeetle2_s3_gpio`). This is P460's
  `ConnectorPins`.

Verdict: the most per kind is 1 (K2 with D7's case, K3 with today's placement, K5 counted strictly). That is at most
one for 4 of 4 kinds. A2 passes.

## The rival: a one-reader fix for K1 (Q17)

The rival reads `gdi_on_firebeetle2_s3_gpio` when the board's id matches and adds its pins to `taken_gpio` before
placement. It ends K1. K5 keeps today's stop. K2 and K3 go silent, because connector pins enter as taken, not as
named, so `NAMED_STRAP_REFUSAL` never sees them. Each needs one more rule to name it. The rival leaves 0, 1, 1 and 0,
the same per-kind count as the model. The difference is the answer: the model returns one `Conflict` value that maps
onto today's `Finding` and `NextStep` (AR-9 item 3), so the JSON answer, the sheet and the stop text share it. The
rival writes three sentences in three places.

## The names (Q8)

- `Claim` clashes: GLOSSARY.md:539-540 uses "claim" for a statement that lands as a raised row.
- `Conflict` clashes: GLOSSARY.md:75,80 use `CONFLICT` for the arithmetic checker's output line.
- `Resource` has no match in `scripts/`, `docs/guide/patterns-and-names.md`, GLOSSARY.md or
  `docs/architecture/glossary.md`.

All four rows hold pins, so `PinClaim` and `PinConflict` remove both clashes. The P665 plan council decides.

## Does A1 settle Q7? (Q21, second half)

Not for every pin. A schematic read is not a bench run. Per pin: BL already has a bench fact. SCLK, MOSI, DC and CS
ran on the bench and match the schematic. RST, MISO and SDCS match the schematic only. The flag is a property of the
fact, not of each pin, so marking 5 of 8 needs a per-pin field or a split fact. This PR changes no record. P665 #894
decides the shape, or says which card does.

## Hand-off

- P665 #894, the bridge, may start once P664 #893 is done. A1 passed, so nothing stops it.
- For P665's plan: `movable` on `Claim`, the connector reader, D7's flag (Q20), the soft onboard claim, the two
  name clashes and the per-pin `verified` question.
- Not run: K4, K6 and K7, the eFuse question Q12, and any reset-level fact (PH-11), as the card asked.
