"""
The reasons a check could not look, each a Code with its meaning and its fix (P693, W6-C2, P935): check_all.py, check_physics.py,
check_footprints.py, compare_design.py, check_vendor_pins.py and check_bom.py.

A leaf: it imports nothing of spark but `spark.core.codes`. Each refusal names its code, so an agent decides on the code and never
on the English sentence (no magic strings, P260). A refusal that returns a sentence returns a `Refusal` (`spark.core.result`), a str
with a `code`, so every text and JSON stays byte-equal; one that raises gives its error a `code`. A `Finding.of` takes the fix from
its code. Two checks write a code in their JSON (check_footprints.py's and check_vendor_pins.py's); the rest wait in the library
for the Operation that comes later. A check's findings keep their `rule`.

RULES_REFUSED is also design_codes' word, an equal literal in two leaves, with the same meaning and the same fix. INPUT_AMBIGUOUS
is also build_codes' word, a plain str there, with the same meaning.
"""

from spark.core import codes

# --- MVP ---
#: The checks that read a built circuit and a rules file: check_physics, check_footprints, compare_design, check_all.
NO_CIRCUIT = codes.Code("no_circuit", "there is no built circuit at the path given, so there is nothing to check: build first",
                        "give the path of the built circuit, usually dist/board/circuit.json, or build the board first with /spark:build")
NO_RULES_FILE = codes.Code("no_rules_file", "there is no rules file at the path given, so no rule can be checked",
                           "give --rules the path of a rules file, or write .spark/rules.json with /spark:init")
RULES_REFUSED = codes.Code("rules_refused", "the rules file cannot be used: it is not JSON, or a value is of the wrong kind or below its lowest",
                           "fix the value the sentence names in the rules file, or the error it gives, such as a JSON error at a line and column, then run again")
#: check_all.py: what stops one check, or the whole run.
INPUT_AMBIGUOUS = codes.Code("input_ambiguous", "an input matched more than one file, and nothing chose between them",
                             "pick one of the files the sentence lists and give it with the flag the sentence names, then run again")
CHECK_CRASHED = codes.Code("check_crashed", "a check raised an error it did not expect, so it did not look",
                           "if the sentence names your input file, fix that file and run again, or else report it at "
                           "https://github.com/xmejkal/spark/issues with the sentence and the command you ran")
PROJECT_UNUSABLE = codes.Code("project_unusable", "the folder --project names is not a project folder spark can read",
                              "give --project a folder that exists, or leave out --project and give each input with its own flag")
#: check_all.py's Findings (P804): one check found problems, one could not look, or every check was skipped.
CHECK_FOUND_PROBLEMS = codes.Code("check_found_problems", "a check ran and found problems in the design",
                                  "fix each problem the check lists, then run check_all.py again")
CHECK_COULD_NOT_LOOK = codes.Code("check_could_not_look", "a check was asked for and could not look, or left part of its input unchecked",
                                  "fix what the sentence names for this check, then run check_all.py again. If the sentence starts with an error name, such as KeyError, "
                                  "and names no file of yours, report it at https://github.com/xmejkal/spark/issues with the sentence and your command")
NOTHING_ASKED = codes.Code("nothing_asked", "every check was skipped, because no input was given or found, so the answer says nothing about the board",
                           "run again with --project and your project folder, or give the inputs with --circuit, --rules, --package or --boards")
#: compare_design.py.
CIRCUIT_NOT_JSON = codes.Code("circuit_not_json", "the built circuit is not JSON",
                              "build the board again with /spark:build, or give the path of the circuit.json that a build wrote")
NO_RULE_STATED = codes.Code("no_rule_stated", "the rules file names no I2C line and no pin that must not float, so there is nothing to compare",
                            "ask the person which I2C lines and which pins must not float, name them in i2c_buses and must_not_float in the rules file, then run again")
#: check_vendor_pins.py: one board file.
NO_VENDOR_VARIANT = codes.Code("no_vendor_variant", "the board file names no vendor.arduino_variant, so there is no vendor header to check it against",
                               "ask the person for the board's folder under variants/ in the Arduino core and add it to the board file as vendor.arduino_variant, "
                               "or say in the board file why it has no vendor header, then run again")
NO_CACHED_HEADER = codes.Code("no_cached_header", "--offline, and neither the project nor spark keeps the vendor header",
                              "run check_vendor_pins.py once without --offline on a board file that a project owns, so that it fetches and keeps the header")
HEADER_HAS_NO_PINS = codes.Code("header_has_no_pins", "the vendor header holds no pin definition this check can read",
                                "make sure vendor.arduino_variant names this board's variant, or compare the pins with the header by hand")
BOARD_HAS_NO_PROJECT = codes.Code("board_has_no_project", "a live check needs a project that owns the board file, to keep the header it fetches",
                                  "put the board file in the boards/ folder of a project that /spark:init set up, then run again")
HEADER_NOT_FETCHED = codes.Code("header_not_fetched", "the vendor header could not be fetched with gh",
                                "fix what gh says in the sentence (`gh auth status` shows your sign-in), then run again")
HEADER_NOT_KEPT = codes.Code("header_not_kept", "the vendor header was fetched but could not be written to the project's cache",
                             "make the folder that holds the file the sentence names writable, then run again")
#: check_bom.py.
NO_PACKAGE = codes.Code("no_package", "there is no fab package at the path given: export it first",
                        "in the project folder, give the path of the fab package, or export one with `npx --no tsci export board.tsx -f gerbers -o board-gerbers.zip`")
NO_BOM_IN_PACKAGE = codes.Code("no_bom_in_package", "the fab package holds no bom.csv, so there is no order to check",
                               "in the project folder, export the package again with `npx --no tsci export board.tsx -f gerbers -o board-gerbers.zip`, which writes bom.csv")

#: Each code and the one sentence that says what it means.
CODES = {code: code.meaning for code in (
    NO_CIRCUIT, NO_RULES_FILE, RULES_REFUSED, INPUT_AMBIGUOUS, CHECK_CRASHED, PROJECT_UNUSABLE, CHECK_FOUND_PROBLEMS,
    CHECK_COULD_NOT_LOOK, NOTHING_ASKED, CIRCUIT_NOT_JSON, NO_RULE_STATED, NO_VENDOR_VARIANT, NO_CACHED_HEADER,
    HEADER_HAS_NO_PINS, BOARD_HAS_NO_PROJECT, HEADER_NOT_FETCHED, HEADER_NOT_KEPT, NO_PACKAGE, NO_BOM_IN_PACKAGE)}
# --- end MVP ---
