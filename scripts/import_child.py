#!/usr/bin/env python3
"""
The child process of import_firmware.py (P59, P443): it imports one firmware module and says how that went.

    python3 -I -B import_child.py MODULE FOLDER...

MODULE is imported with the FOLDERs first on sys.path, in that order. import_firmware.py runs it with -I, so the
child's own folder and the current folder stay off sys.path, and a firmware cannot import this file.
"""

import importlib
import sys


# --- MVP --- (P443)
def main(argv):
    sys.path[:0] = argv[1:]
    importlib.import_module(argv[0])


if __name__ == "__main__":
    main(sys.argv[1:])
