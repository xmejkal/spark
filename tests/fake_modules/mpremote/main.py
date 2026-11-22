"""Fake `mpremote.main` for the bench goldens (P1007): QUIET_MPREMOTE calls main(), which gives __main__.py's canned answers."""

import runpy


def main():
    runpy.run_module("mpremote.__main__", run_name="__main__")  # its sys.exit ends the run
