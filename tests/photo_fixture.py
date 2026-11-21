"""
A made-up photo for the tests of the store's location removal: JPEG bytes built in code whose EXIF carries a GPS block,
as a phone writes it. A helper module, no tests in it. No real photo: every byte is made here.
"""

import struct


def photo_with_location():
    """A minimal JPEG whose EXIF carries a GPS block: latitude N 50° 5' 12.34" — as a phone writes it."""
    latitude = struct.pack("<6I", 50, 1, 5, 1, 1234, 100)
    tiff = (b"II*\x00" + struct.pack("<I", 8)
            + struct.pack("<H", 1) + struct.pack("<HHII", 0x8825, 4, 1, 26) + struct.pack("<I", 0)
            + struct.pack("<H", 2) + struct.pack("<HHI4s", 1, 2, 2, b"N\x00\x00\x00")
            + struct.pack("<HHII", 2, 5, 3, 56) + struct.pack("<I", 0) + latitude)
    exif = b"Exif\x00\x00" + tiff
    return b"\xff\xd8\xff\xe1" + struct.pack(">H", len(exif) + 2) + exif + b"\xff\xd9", latitude
