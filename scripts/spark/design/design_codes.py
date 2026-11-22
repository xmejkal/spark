"""
The reasons a design cannot be loaded, placed or emitted, each a Code with its meaning and its fix (P700, W6-D2, P935): loader.load,
pin_assigner, board_emitter and footprint_emitter, and the design's own Operations.

A leaf: it imports nothing of spark but `spark.core.codes`. Each refusal names its code, so an agent decides on the code and never
on the English sentence (no magic strings, P260). A refusal that raises gives its error a `code` (DesignError, ImpossibleError,
RefusedInputError); one that returns a sentence returns a `Refusal` (`spark.core.result`), a str with a `code`, so every text and
JSON stays byte-equal. A SparkError and `Finding.of` take the fix from the code. A variant is another Code of its parent's word and
meaning, named after it, with a fix of its own; its parent may be the core's (BAD_ARGUMENT_PICK_PAIRS) or another leaf's
(RECORD_FILE_BROKEN_AUDIT, an equal literal of records_codes' word and meaning).

RULES_REFUSED is also check_codes' word, an equal literal in two leaves, with the same meaning.
"""

from spark.core import codes

# --- MVP ---
#: design.load: the requirements file, the project, and the records it names.
NO_REQUIREMENTS = codes.Code('no_requirements', 'there is no requirements file at the path given',
                              'give the path of a requirements file, or write one with parts.py --requirements')
REQUIREMENTS_UNREADABLE = codes.Code('requirements_unreadable', 'the requirements file is not JSON, or it cannot be read',
                                      'make the file the sentence names readable JSON, then run again')
REQUIREMENTS_FIELD_WRONG = codes.Code('requirements_field_wrong', 'a field of the requirements file is of the wrong kind, or names what no part or board has',
                                       'fix the field the sentence names in the requirements file, then run again')
NAME_USED_TWICE = codes.Code('name_used_twice', 'two parts or two signals of the design have one name, so the build would make them one',
                              'give one of the two a name of its own in the requirements file, then run again')
NO_PROJECT_FOLDER = codes.Code('no_project_folder', '--project names no folder, or the folder a project is looked for from is gone',
                                'give --project a folder that exists, or run from the project folder, with the requirements file in it')
PART_UNUSABLE = codes.Code('part_unusable', 'a part the design names is unknown, or its record cannot be read or breaks the part contract',
                            'fix the record the sentence names (`parts.py --validate` lists its problems), or give an id that `parts.py --need <words>` finds')
BOARD_UNUSABLE = codes.Code('board_unusable', 'the board the design names is unknown, or its record cannot be read or breaks the board contract',
                             'fix the board record the sentence names, or give a board id that boards.py --list shows')
RULES_REFUSED = codes.Code('rules_refused', 'the rules file cannot be used: it is not JSON, or a value is of the wrong kind or below its lowest',
                            'fix the value the sentence names in the rules file, or the error it gives, such as a JSON error at a line and column, then run again')
#: `parts.py --requirements` (P877): an entry that spark wrote for a pick that is gone, in `data.unexplained`.
ENTRY_PICK_GONE = codes.Code('entry_pick_gone', "an entry of the requirements file that spark wrote for a pick that is gone: said by --requirements, removed only on the person's yes",
                              'ask the person. On their yes, answer data.remove_key with true in a replies file of your own and run again with --replies')
#: assign_pins: an ImpossibleError, a signal no pin can take.
UNKNOWN_BUS = codes.Code('unknown_bus', 'a signal is on a bus spark does not know',
                          'put the signal on a bus the sentence lists, or drop `bus`')
NOT_A_BUS_LINE = codes.Code('not_a_bus_line', "a signal on a bus is not one of that bus's lines",
                             'give the signal one of the lines the sentence lists')
BUS_LINE_NOT_ON_BOARD = codes.Code('bus_line_not_on_board', 'a signal needs a bus line that the board labels no pin for',
                                    'use a board that labels this bus line, or take the signal off the bus')
UNKNOWN_NEED = codes.Code('unknown_need', 'a signal asks for something a pin cannot be asked for',
                           'give the signal only needs that the sentence lists')
NO_SUCH_PIN = codes.Code('no_such_pin', 'a signal names a pin the board does not bring out',
                          "name a pin label from the board record's `pins`, or drop `pin` so spark picks one")
NAMED_PIN_UNSUITABLE = codes.Code('named_pin_unsuitable', 'a signal names a pin that is a strapping pin, or that cannot do what the signal needs',
                                   'drop `pin` so spark picks a pin that can do it, or name another pin')
PIN_TAKEN = codes.Code('pin_taken', 'a signal names a pin another signal already holds',
                        'name another pin for one of the two signals, or drop `pin` from one of them')
NO_PIN_LEFT = codes.Code('no_pin_left', 'no free pin of the board can do what a signal needs',
                          'free a pin (fewer signals, or a part on a bus), or use a board with more pins of this kind')
SIGNAL_NAME_UNUSABLE = codes.Code('signal_name_unusable', "a signal's name is no Python name, or a name the pin map gives the board's own part",
                                   "rename the signal: a Python name (letters, digits and _, not starting with a digit), and not a name the pin map gives the board's own part")
#: board_emitter: a part record lacks what a board is placed and traced from.
NO_PART_FOOTPRINT = codes.Code('no_part_footprint', 'a part record states no footprint',
                                'add the footprint to the part record from its datasheet (/spark:research), then run again')
NO_PIN_ORDER = codes.Code('no_pin_order', 'a part record states no pin_order, so its pads cannot be numbered',
                           'add pin_order to the part record from its datasheet (/spark:research), then run again')
NO_OUTLINE = codes.Code('no_outline', 'a part record states no outline, and --assume-missing-sizes was not given',
                         'add the outline to the part record from its datasheet, or run `emit_board.py` with --assume-missing-sizes')
SERIES_RESISTOR_UNSIZED = codes.Code('series_resistor_unsized', 'a series resistor cannot be sized: a fact it needs is missing, or the pin cannot light the part',
                                      'add the fact the sentence names to the part record (/spark:research), or put the part on a pin that can light it')
#: footprint_emitter, and board_emitter's footprint stage: the board record cannot give a footprint.
BOARD_LACKS_FOOTPRINT = codes.Code('board_lacks_footprint', 'the board record lacks the facts its footprint is drawn from',
                                    'add the facts the sentence lists to the board record, then build again')
BOARD_DISAGREES = codes.Code('board_disagrees', 'the board record disagrees with itself: a value of the wrong kind, or a pad order that does not fit',
                              'fix the value the sentence names in the board record, then build again')
#: audit_records (P707): a drawer entry whose record nobody has, and a record or drawer file the disk would not give.
DRAWER_ENTRY_DANGLING = codes.Code('drawer_entry_dangling', 'a drawer entry points at a record nobody has: fix its `is`, or research the part',
                                    "point the entry's `is` at a record that exists, or research the part with /spark:research")
RECORD_UNREADABLE = codes.Code('record_unreadable', 'a record, a drawer file or a folder of them could not be read from disk: the sentence names it',
                                'fix the file the sentence names, then run --audit again')
RECORD_UNREADABLE_FOLDER = codes.Code(RECORD_UNREADABLE, RECORD_UNREADABLE.meaning,
                                      'give yourself read access to the folder the sentence names (chmod u+rx), then run --audit again')
#: the goal Operations (P726): a project nobody listed, an offer key nothing has, a project with no needs yet.
PROJECT_NOT_LISTED = codes.Code('project_not_listed', 'the folder is not on your list of projects, so no step of it was marked',
                                 'mark a step with parts.py --step <project> <step> in a Claude Code session: that puts it on the list')
OFFER_UNKNOWN = codes.Code('offer_unknown', 'no record and no live drawer entry has that key',
                            'give a key that `parts.py --drawer` or `parts.py --need <words>` lists, as `parts.py --offer KEY`')
NO_NEEDS_YET = codes.Code('no_needs_yet', 'the project has no needs yet: /spark:idea writes them',
                           'write the needs with /spark:idea, then run again')
#: A variant of the core's BAD_ARGUMENT: `parts.py --pick` was given a word that is no NEED=ID pair (pick_parts).
BAD_ARGUMENT_PICK_PAIRS = codes.Code(codes.BAD_ARGUMENT, codes.BAD_ARGUMENT.meaning,
                                     "parts.py --match <project> lists each need's candidates and their ids")
#: A variant of the core's BAD_ARGUMENT: the replies file `parts.py --requirements --replies` names cannot be read (entry_origin).
BAD_ARGUMENT_REQUIREMENTS_REPLIES = codes.Code(codes.BAD_ARGUMENT, codes.BAD_ARGUMENT.meaning,
                                               'write the replies file as {"replies": {"<key>": true}} with the key of the run before, or leave out --replies')
#: A variant of records_codes.RECORD_FILE_BROKEN, an equal literal of that leaf with its meaning: the audit's item names the broken
#: record in its `subject`, no file (audit_records).
RECORD_FILE_BROKEN_AUDIT = codes.Code("record_file_broken", "a file spark reads a record from is not JSON, or not in its shape: fix it by hand",
                                      "fix the record that `subject` names, then run `parts.py --audit` again")

#: Each code and the one sentence that says what it means.
CODES = {code: code.meaning for code in (
    NO_REQUIREMENTS, REQUIREMENTS_UNREADABLE, REQUIREMENTS_FIELD_WRONG, NAME_USED_TWICE, NO_PROJECT_FOLDER, PART_UNUSABLE,
    BOARD_UNUSABLE, RULES_REFUSED, ENTRY_PICK_GONE, UNKNOWN_BUS, NOT_A_BUS_LINE, BUS_LINE_NOT_ON_BOARD, UNKNOWN_NEED,
    NO_SUCH_PIN, NAMED_PIN_UNSUITABLE, PIN_TAKEN, NO_PIN_LEFT, SIGNAL_NAME_UNUSABLE, NO_PART_FOOTPRINT, NO_PIN_ORDER,
    NO_OUTLINE, SERIES_RESISTOR_UNSIZED, BOARD_LACKS_FOOTPRINT, BOARD_DISAGREES, DRAWER_ENTRY_DANGLING, RECORD_UNREADABLE,
    PROJECT_NOT_LISTED, OFFER_UNKNOWN, NO_NEEDS_YET)}
# --- end MVP ---
