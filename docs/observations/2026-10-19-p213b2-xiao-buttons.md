# The XIAO ESP32-C6's BOOT and RESET buttons, from the PO's photo

The PO took a photo of his own XIAO ESP32-C6 on 2026-10-19, during the P213 b2 bench walk. The photo is not in
this repository, because a phone photo can carry GPS data. Its sha256 is
`87b43e78d09b05d0dbc1e31e7b92743491949f5a91c8a88316a07fe05d56f5a8`. The facts below are also on the card:
https://github.com/xmejkal/spark/issues/192#issuecomment-6262027325.

The photo shows the side with the USB-C socket and the metal shield, USB-C at the top:

- R (RESET): the small button in the top-left corner, beside the USB-C socket, with "R" in the silkscreen under it.
- B (BOOT): the small button in the top-right corner, beside the USB-C socket, with "B" in the silkscreen under it.

`boards/xiao-esp32-c6.json` records them as `physical.buttons`. The photo shows the board in hand, so the record
does not mark them UNVERIFIED.
