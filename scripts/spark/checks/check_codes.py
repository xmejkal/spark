"""
The reasons a check could not look, each a code with one sentence (P693, W6-C2): check_all.py, check_physics.py,
check_footprints.py, compare_design.py, check_vendor_pins.py and check_bom.py.

A leaf: it imports nothing of spark. Each refusal names its code, so an agent decides on the code and never on the English
sentence (no magic strings, P260). A refusal that returns a sentence returns a `Refusal` (`spark.core.result`), a str with
a `code`, so every text and JSON stays byte-equal; one that raises gives its error a `code`. No check writes a code in its
JSON yet: the codes wait in the library for the Operation that comes later. A check's findings keep their `rule`.
"""


# --- MVP ---
#: The checks that read a built circuit and a rules file: check_physics, check_footprints, compare_design, check_all.
NO_CIRCUIT, NO_RULES_FILE, RULES_REFUSED = "no_circuit", "no_rules_file", "rules_refused"
#: check_all.py: what stops one check, or the whole run.
INPUT_AMBIGUOUS, CHECK_CRASHED, PROJECT_UNUSABLE = "input_ambiguous", "check_crashed", "project_unusable"
#: compare_design.py.
CIRCUIT_NOT_JSON, NO_RULE_STATED = "circuit_not_json", "no_rule_stated"
#: check_vendor_pins.py: one board file.
NO_VENDOR_VARIANT, NO_CACHED_HEADER, HEADER_HAS_NO_PINS = "no_vendor_variant", "no_cached_header", "header_has_no_pins"
BOARD_HAS_NO_PROJECT, HEADER_NOT_FETCHED, HEADER_NOT_KEPT = "board_has_no_project", "header_not_fetched", "header_not_kept"
#: check_bom.py.
NO_PACKAGE, NO_BOM_IN_PACKAGE = "no_package", "no_bom_in_package"
#: check_vendor_pins.py: a board file that is not there (P688).
NO_BOARD_FILE = "no_board_file"

#: Each code and the one sentence that says what it means.
CODES = {
    NO_CIRCUIT: "there is no built circuit at the path given, so there is nothing to check: build first",
    NO_RULES_FILE: "there is no rules file at the path given, so no rule can be checked",
    RULES_REFUSED: "the rules file cannot be used: it is not JSON, or a value is of the wrong kind or below its lowest",
    INPUT_AMBIGUOUS: "an input matched more than one file, and nothing chose between them",
    CHECK_CRASHED: "a check raised an error it did not expect, so it did not look",
    PROJECT_UNUSABLE: "the folder --project names is not a project folder spark can read",
    CIRCUIT_NOT_JSON: "the built circuit is not JSON",
    NO_RULE_STATED: "the rules file names no I2C line and no pin that must not float, so there is nothing to compare",
    NO_VENDOR_VARIANT: "the board file names no vendor.arduino_variant, so there is no vendor header to check it against",
    NO_CACHED_HEADER: "--offline, and neither the project nor spark keeps the vendor header",
    HEADER_HAS_NO_PINS: "the vendor header holds no pin definition this check can read",
    BOARD_HAS_NO_PROJECT: "a live check needs a project that owns the board file, to keep the header it fetches",
    HEADER_NOT_FETCHED: "the vendor header could not be fetched with gh",
    HEADER_NOT_KEPT: "the vendor header was fetched but could not be written to the project's cache",
    NO_BOARD_FILE: "there is no board file at the path given, so there is nothing to check",
    NO_PACKAGE: "there is no fab package at the path given: export it first",
    NO_BOM_IN_PACKAGE: "the fab package holds no bom.csv, so there is no order to check",
}
# --- end MVP ---
