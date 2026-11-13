"""
Which test modules a push runs, chosen from the files its branch changed (P714).

The PO, 2026-11-08: "you test the story. Maybe a few integration or some end-to-end tests, but just that part you
worked on." `check_commit.py` calls `select` with what it read from git and from the committed tree, so this module
holds no git and reads no file.

Each changed file adds the tests that name it and the golden net of its area, and ALWAYS_RUN_TESTS always run. A doubt
runs more: a file that only ALWAYS_RUN_TESTS name, the core, a package file or unread changes make it the whole quick
run, with a sentence that says why. The sweeps run what a story leaves out (`check_commit.py --full`).
"""

import re
from dataclasses import dataclass
from pathlib import PurePosixPath

#: The states of StoryTests: its modules run, or the whole quick run does and `why` says the reason.
CHOSEN = "chosen"
QUICK_RUN = "quick_run"

#: The words for the run a StoryTests asks for, in the gate's line.
RUN_STORY = "story"
RUN_QUICK = "quick"

#: These read the whole tree, so no file's name finds them. Together 38 s on 2026-11-09.
ALWAYS_RUN_TESTS = ("test_architecture", "test_self_confirmation", "test_docs", "test_map", "test_journey", "test_lint",
                    "test_no_magic_strings", "test_no_board_address", "test_observation_rows", "test_orphans",
                    "test_python_floor", "test_scripts_isolated", "test_routes", "test_json_contracts", "test_part_shape",
                    "test_suite_temp", "test_suite_runs")

#: An area whose golden net has another area's name. Every other area's net is test_golden_<area>. Idea's operation runs in
#: the records net (`parts.py --needs-drop`, P802).
GOLDEN_NET_ELSEWHERE = {"build": "design", "idea": "records", "sourcing": "records"}

CORE_FOLDER = "scripts/spark/core/"
PACKAGE_FILE = "__init__.py"
AREA_MODULE = re.compile(r"scripts/spark/([^/]+)/")
NO_TEST_OF_THEIR_OWN = ("docs/", "scrum/", "tests/mutations/")
ROOT_DOCUMENT_SUFFIX = ".md"
COMMAND_PAGE = re.compile(r"commands/([^/]+)\.md$")
TEST_FILE = re.compile(r"tests/(test_[^/]+)\.py$")
BENCH_NET_FOLDER = "tests/golden/"
BENCH_NET = "test_golden_bench"
AREA_NET_FOLDER = re.compile(r"tests/golden-([^/]+)/")
GOLDEN_NET = "test_golden_%s"
CONVERTER_FOLDER = "tools/circuit-to-wokwi/"
CONVERTER_TEST = "test_converter"

WHY_CHANGES_UNREAD = "the changes since origin/main could not be read"
WHY_NO_CHANGE = "nothing differs from origin/main, and the gate measures HEAD, not the ref pushed (P106)"
WHY_NOTHING_LEFT = "no test is left to run"
WHY_EVERY_AREA = "every area depends on %s"
WHY_UNNAMED = "no test names %s"


@dataclass(frozen=True)
class StoryTests:
    """Value: the test modules a push runs. `why` says the reason when `state` is QUICK_RUN, and is None when CHOSEN."""

    modules: tuple
    state: str
    why: str
    test_files: int = 0

    def run_word(self):
        """The word for this run in the gate's line."""
        return RUN_STORY if self.state == CHOSEN else RUN_QUICK

    def scope(self):
        """How much of the suite was chosen, for the gate's line; None for the quick run."""
        return "{:,} of {:,} test files".format(len(self.modules), self.test_files) if self.state == CHOSEN else None


def _quick_run(why):
    return StoryTests((), QUICK_RUN, why)


def _named_by(pattern, test_texts, golden_texts):
    """The test modules whose text matches, and the net of each golden helper whose text matches."""
    tests = {name for name, text in test_texts.items() if pattern.search(text)}
    return tests | {"test_%s" % name for name, text in golden_texts.items() if pattern.search(text)}


def _pattern_for(name):
    """What a test holds when it names the changed file `name`: the page of a command, or else the file's stem as a word."""
    page = COMMAND_PAGE.match(name)
    if page:
        return re.compile(r"commands/%s\b|\b%s\.md\b" % (re.escape(page.group(1)), re.escape(page.group(1))))
    return re.compile(r"\b%s\b" % re.escape(PurePosixPath(name).stem))


def _tests_for(name, test_texts, golden_texts):
    """The test modules that the changed file `name` adds, or None when no test of its own names it."""
    if name.startswith(NO_TEST_OF_THEIR_OWN) or ("/" not in name and name.endswith(ROOT_DOCUMENT_SUFFIX)):
        return set()
    if name.startswith(BENCH_NET_FOLDER):
        return {BENCH_NET}
    if name.startswith(CONVERTER_FOLDER):
        return {CONVERTER_TEST}
    area_net = AREA_NET_FOLDER.match(name)
    if area_net:
        return {GOLDEN_NET % area_net.group(1)}
    named = _named_by(_pattern_for(name), test_texts, golden_texts)
    test_file = TEST_FILE.match(name)
    if test_file and test_file.group(1) in test_texts:
        return named | {test_file.group(1)}
    if not named - set(ALWAYS_RUN_TESTS):  # a mention in a test that reads the whole tree does not test this file
        return None
    area = AREA_MODULE.match(name)
    if area:
        named.add(GOLDEN_NET % GOLDEN_NET_ELSEWHERE.get(area.group(1), area.group(1)))
    return named


def select(changed, test_texts, golden_texts):
    """
    StoryTests for the file names `changed`. A `changed` of None (git could not tell) gives the quick run. `test_texts`
    maps each module tests/test_*.py to its text, and `golden_texts` each helper tests/golden_*.py to its text.
    """
    if changed is None:
        return _quick_run(WHY_CHANGES_UNREAD)
    if not changed:
        return _quick_run(WHY_NO_CHANGE)
    chosen = set(ALWAYS_RUN_TESTS)
    for name in changed:
        if name.startswith(CORE_FOLDER) or PurePosixPath(name).name == PACKAGE_FILE:
            return _quick_run(WHY_EVERY_AREA % name)
        tests = _tests_for(name, test_texts, golden_texts)
        if tests is None:
            return _quick_run(WHY_UNNAMED % name)
        chosen |= tests
    modules = tuple(sorted(chosen & set(test_texts)))  # a test the rules name may not exist: a run of it would fail
    if not modules:
        return _quick_run(WHY_NOTHING_LEFT)
    return StoryTests(modules, CHOSEN, None, len(test_texts))
