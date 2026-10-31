"""P461: a fake MicroPython interpreter that holds a partition table, for the tests that build an image from it."""

import hashlib
import struct

#: ESP-IDF v5.5.2 (the version string in the v1.29.0 interpreters), literals as in tests/test_flash_image.py.
TABLE_OFFSET = 0x8000                       # where the bootloader reads the table in the flash
TABLE_SIZE = 0xC00                          # components/partition_table/gen_esp32part.py:22 MAX_PARTITION_LENGTH
ENTRY = "<2sBBLL16sL"                      # gen_esp32part.py:607 STRUCT_FORMAT; magic 0xAA50 at :424 (bytes aa 50)
MD5_MAGIC = b"\xeb\xeb" + b"\xff" * 14      # gen_esp32part.py:23 MD5_PARTITION_BEGIN

#: The table of MicroPython v1.29.0's ESP32 builds, read from the three interpreters on 2026-10-31:
#: (label, type, subtype, offset, size). nvs and phy_init are data, factory is the app and ends at 0x200000.
MICROPYTHON_TABLE = (("nvs", 1, 2, 0x9000, 0x6000), ("phy_init", 1, 1, 0xf000, 0x1000), ("factory", 0, 0, 0x10000, 0x1f0000))


def table_bytes(entries=MICROPYTHON_TABLE, md5=True):
    """The partition table of `entries` as ESP-IDF writes it: each entry, an MD5 entry unless `md5` is False, 0xff."""
    body = b"".join(struct.pack(ENTRY, b"\xaa\x50", kind, subtype, offset, size, label.encode(), 0)
                    for label, kind, subtype, offset, size in entries)
    if md5:
        body += MD5_MAGIC + hashlib.md5(body).digest()
    return body.ljust(TABLE_SIZE, b"\xff")


def fake_interpreter(head=b"\xe9", size=0x9000, offset=0, table=None):
    """An interpreter that starts with `head`, then zeros, with `table` (the MicroPython table) where the flash
    has it, 0x8000 - `offset` in the interpreter, and `size` bytes long."""
    flash = bytearray(size)
    flash[:len(head)] = head
    start = TABLE_OFFSET - offset
    flash[start:start + TABLE_SIZE] = table_bytes() if table is None else table
    return bytes(flash[:size])
