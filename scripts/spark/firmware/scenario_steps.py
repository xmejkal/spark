"""
The run log's words and their reader (moved from run_scenario.py, P685): the step kinds a scenario holds, the lines of
a log's header, the verdict of a pass and its caveats, and ScenarioSteps, which counts and names the steps. It imports
nothing of a run, so the bench reads a log without the simulator.
"""

import re
from dataclasses import dataclass
from pathlib import Path

from spark.core import outcomes


# --- MVP ---
#: The kinds of wokwi-cli scenario step that this reads by name: the one that sets a control, the one that reads a pin
#: and the one that waits for serial text.
SET_CONTROL, EXPECT_PIN, WAIT_SERIAL = "set-control", "expect-pin", "wait-serial"
#: The key that names a component of the diagram inside a step's value (wokwi-cli's own word for a component id).
PART_ID_KEY = "part-id"
READY = "ready"
READY_STEP = '- %s: "%s"' % (WAIT_SERIAL, READY)
#: The log's line that names the image a run tested, by its sha256 (P192): deploy.py flashes only an image a passed run names.
IMAGE_LINE = "image sha256: "
#: The log's line for each file in the image, its sha256 then its path inside the image (P215, D20): the board's files
#: are checked against these after a flash.
FILE_LINE = "file sha256: "
#: The log's line that counts the scenario's steps by kind (P345): what a passed run did, read by the look and the deploy question.
STEP_COUNTS_LINE = "step counts: "
#: The log's two lines for the names of the steps (P345): a marker with the count, then one name line each. A step's name is a claim
#: that it tests the text it carries; the look compares the names with the brief's must lines. No marker means a log from before names.
STEP_NAMES_LINE = "step names: "
STEP_NAME_LINE = "step name: "
# --- MVP ---
#: P345 (moved here by P485): what a passed run's scenario did not do, for the look and for the run's own printed line. Each takes a
#: subject: the look says ONE_RUN_MESSAGE or names its logs, the printed line says THIS_RUN_MESSAGE.
NO_CONTROL_CAVEAT = "%s no set-control step (the step that presses a button or sets a sensor)"
NO_CONTROL_NO_PIN_CAVEAT = ("%s no set-control step (the step that presses a button or sets a sensor) and no expect-pin "
                            "step (the step that reads a pin)")
ONE_RUN_MESSAGE = "the passed run's scenario has"
THIS_RUN_MESSAGE = "it has"
#: What a pass prints when its steps could not be counted: %s is why (ScenarioSteps.why).
UNCOUNTED_MESSAGE = "its steps were not counted: %s"
#: The verdict of a pass, in the log's header and on the printed line; deploy finds a passed run by it.
PASSED = "passed"
#: What a pass prints when its scenario did less than a person expects (P485): the log's verdict stays PASSED.
PASSED_WITH_CAVEAT = PASSED + ", but %s"
# --- end MVP ---
#: What the line says when the steps are not RECORDED: a step has no key, so a kind would be a guess, or the log gave none.
STEPS_NOT_READ = "not read"
#: Why ScenarioSteps is outcomes.NOT_CHECKED (the reader rule is in outcomes.py), one sentence each.
WHY_NO_KEY = "a step of the scenario has no kind"
WHY_NOT_COUNTED = "the log says its steps were not counted"
WHY_BAD_COUNTS = "the log's step counts line is malformed"
WHY_BAD_NAMES = "the log's step names do not match its step names count"
WHY_NAMES_NOT_READ = "the log says its step names were not read"
#: Why the names of a scenario's steps are outcomes.NOT_CHECKED: a name is a block scalar or runs on over more than one line.
WHY_NAME_NOT_READ = "a step name is a block scalar or runs over more than one line"
#: Why a run log's reader (ScenarioSteps, SimulationLimits) found nothing: the file cannot be read (from sim_project.py, P685).
WHY_LOG_UNREADABLE = "the log cannot be read"
#: Why a project with no firmware/main.py cannot go on a board: %s are the project and READY.
NO_MAIN = "no firmware/main.py in %s: the board would boot to a bare prompt and never print %r"


# --- MVP ---
@dataclass(frozen=True)
class StepNames:
    """Value: the names of a scenario's steps, in order, and an outcomes word for them: RECORDED (perhaps none), NONE_RECORDED or NOT_CHECKED (`why` says why)."""

    names: tuple = ()
    state: str = outcomes.NONE_RECORDED
    why: str = None


@dataclass(frozen=True)
class StepComponents:
    """Value: what a scenario's steps say about the diagram (P399): the component ids in order, the text of each step that no id
    could be read from, and (kind, value) of each step in order. A log holds none of them."""

    ids: tuple = ()
    unread: tuple = ()
    kinds: tuple = ()


# --- MVP ---
class ScenarioSteps:
    """
    Value: the steps of a scenario counted by kind. `counts` maps a step kind (the key of a step, such as `set-control`) to
    how many steps have it. `state` is an outcomes word: RECORDED (counted), NONE_RECORDED (a log with no counts line, or a
    text with no step) or NOT_CHECKED (they could not be counted, and `why` says why). Nothing is derived from the counts
    of a state that is not RECORDED.

    `names` are the step names, in order, each with its spaces collapsed (P345). `names_state` is an outcomes word apart from
    `state`: RECORDED (the scenario or the log named them, perhaps none), NONE_RECORDED (a log from before names) or NOT_CHECKED
    (`names_why` says why).

    `component_ids` are the ids that the steps name, without repeats, and `unread_steps` the text of each step that no id could be
    read from (P399). The reader fails only toward unread: a shape it does not know is never a wrong id.
    """

    #: A key at the start of a step's text, plain or quoted. Anchored, so a kind named inside a value is no key.
    KEY = re.compile(r"""^\s*(?:"([\w-]+)"|'([\w-]+)'|([\w-]+))\s*:""")
    ITEM = re.compile(r"^(\s*)-(?:\s|$)")
    #: The one key a step carries beside its kind: wokwi-cli prints it as the step's name (TestScenario.ts, validStepKeys).
    NAME_KEY = "name"
    #: The kinds that must name a component, and the form of a component id that this reads.
    COMPONENT_KINDS = (SET_CONTROL, EXPECT_PIN)
    COMPONENT_ID = re.compile(r"[\w.-]+")

    def __init__(self, counts, state=outcomes.RECORDED, why=None, named=None, components=None):
        self.counts, self.state, self.why = dict(counts), state, why
        named = named or StepNames()
        self.names, self.names_state, self.names_why = tuple(named.names), named.state, named.why
        components = components or StepComponents()
        self.component_ids, self.unread_steps, self._kinds = components.ids, components.unread, components.kinds

    @classmethod
    def from_text(cls, steps):
        """The ScenarioSteps of a scenario's text, comments cut. Only the items at the indent of the first step count."""
        lines = [cls._uncomment(line).rstrip() for line in steps.splitlines()]
        start = next((i for i, line in enumerate(lines) if line == "steps:"), None)
        body = [] if start is None else [line for line in lines[start + 1:] if line.strip()]
        first = next((cls.ITEM.match(line) for line in body if cls.ITEM.match(line)), None)
        if first is None:
            return cls({}, outcomes.NONE_RECORDED, None, StepNames((), outcomes.RECORDED))
        steps = cls._steps_in(body, len(first.group(1)))
        kinds = [cls._kind_and_value(*step) for step in steps]
        components = cls._components_of(steps, kinds)
        counts, keyless, names, unread = {}, False, [], False
        for (texts, indent, flow), (kind, _) in zip(steps, kinds):
            if kind:
                counts[kind] = counts.get(kind, 0) + 1
            else:
                keyless = True
            try:
                name = cls._name(texts, indent, flow)
            except ValueError:
                unread = True
                continue
            if name:
                names.append(name)
        named = StepNames((), outcomes.NOT_CHECKED, WHY_NAME_NOT_READ) if unread else StepNames(names, outcomes.RECORDED)
        if keyless:
            return cls({}, outcomes.NOT_CHECKED, WHY_NO_KEY, named, components)
        return cls(counts, named=named, components=components)

    # --- MVP --- (P399)
    @classmethod
    def _steps_in(cls, body, width):
        """Each step of the list at this indent: [its lines, the indent of its own keys or None, in flow form]."""
        steps = []
        for line in body:
            item = cls.ITEM.match(line)
            if item and len(item.group(1)) == width:
                rest = line[item.end():].lstrip()
                steps.append([[rest.lstrip("{")], len(line) - len(rest) if rest else None, rest.startswith("{")])
            elif cls._indent(line) <= width:
                break  # the steps list ended: a key of the scenario at its own indent
            elif steps:
                steps[-1][0].append(line)
                if steps[-1][1] is None:
                    steps[-1][1] = cls._indent(line)
        return steps

    @staticmethod
    def _indent(text):
        """How many spaces the text starts with."""
        return len(text) - len(text.lstrip())

    @staticmethod
    def _key_of(match):
        """The key that `KEY` matched, with its quotes removed."""
        return match.group(1) or match.group(2) or match.group(3)

    @classmethod
    def _own_keys(cls, texts, indent, flow):
        """
        The step's own keys as (text, its line number or None in flow form): in flow form the keys outside any nested `{}` or `[]`, in
        block form the keys at the indent of its first key and outside any nested bracket.
        """
        if flow:
            return [(piece, None) for piece in cls._pieces(" ".join(texts))]
        own, depth = [], 0
        for number, text in enumerate(texts):
            if not depth and (number == 0 or cls._indent(text) == indent):
                own.append((text, number))
            depth = cls._depth(text, depth)
        return own

    @classmethod
    def _kind_and_value(cls, texts, indent, flow):
        """(a step's kind, the lines of its value), from the first of its own keys that is not `name`, or (None, [])."""
        own = cls._own_keys(texts, indent, flow)
        for place, (text, number) in enumerate(own):
            key = cls.KEY.match(text)
            if key and cls._key_of(key) != cls.NAME_KEY:
                end = own[place + 1][1] if place + 1 < len(own) else None
                return cls._key_of(key), [text[key.end():]] + ([] if number is None else texts[number + 1:end])
        return None, []

    @classmethod
    def _components_of(cls, steps, kinds):
        """The StepComponents of these steps and their (kind, value lines)."""
        ids, unread = [], []
        for (texts, _, _), (kind, value) in zip(steps, kinds):
            found = cls._ids_in(value) if kind in cls.COMPONENT_KINDS else None
            if found:
                ids += found
            elif kind is None or kind in cls.COMPONENT_KINDS or PART_ID_KEY in " ".join(texts):
                unread.append(" ".join(" ".join(texts).split()))
        return StepComponents(tuple(dict.fromkeys(ids)), tuple(unread),
                              tuple((kind, " ".join(value)) for kind, value in kinds))

    @classmethod
    def _ids_in(cls, value):
        """The component ids directly inside a step's value, as a list, or None when there is none or one is no plain id."""
        joined = " ".join(value).strip()
        if joined.startswith("{"):
            pieces = cls._pieces(joined[1:])
        else:
            pieces = [line for line in value[1:] if cls._indent(line) == cls._indent(value[1])]
        keyed = [(cls.KEY.match(piece), piece) for piece in pieces]
        ids = [cls._scalar(piece[key.end():].strip()) for key, piece in keyed if key and cls._key_of(key) == PART_ID_KEY]
        return ids if ids and all(cls.COMPONENT_ID.fullmatch(each) for each in ids) else None

    @staticmethod
    def _scalar(value):
        """A value's text: its quotes removed, as YAML reads them, or as it is when it has none."""
        if len(value) > 1 and value[0] == value[-1] and value[0] in "'\"":
            return value[1:-1].replace("''", "'") if value[0] == "'" else value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
        return value

    # --- MVP ---
    @classmethod
    def _name(cls, texts, indent, flow):
        """
        The step's own `name:` value, or None. Only the step's own keys count: in flow form the keys outside any nested `{}` or
        `[]`, in block form the keys at the indent of its first key and outside any nested bracket. So the `name:` inside
        `set-control: { part-id: b, name: pressed }` is the control's, not the step's. Raises ValueError for a name that is a block
        scalar (`>`, `|`) or that the next line goes on with: spark does not read those.
        """
        for piece, number in cls._own_keys(texts, indent, flow):
            key = cls.KEY.match(piece)
            if key and cls._key_of(key) == cls.NAME_KEY:
                value = " ".join(piece[key.end():].split())
                if value[:1] in (">", "|") or (number is not None and number + 1 < len(texts)
                                               and cls._indent(texts[number + 1]) > indent):
                    raise ValueError("a step name over more than one line")
                return " ".join(cls._scalar(value).split()) or None
        return None

    @classmethod
    def _uncomment(cls, line):
        """The line without its comment: a `#` outside quotes with white space before it, or at the start, and all after it."""
        for index, each in cls._unquoted(line):
            if each == "#" and (index == 0 or line[index - 1].isspace()):
                return line[:index]
        return line

    @staticmethod
    def _unquoted(text):
        """
        (index, character) of each character of `text` outside quotes. A quote opens only where a value starts, so `don't` holds none.
        Inside single quotes `''` is one quote, not the end; inside double quotes a backslash escapes the next character.
        """
        shut, last, skip = None, "", False
        for index, each in enumerate(text):
            if skip:
                skip = False
            elif shut:
                if each == "\\" and shut == '"':
                    skip = True
                elif each == shut and shut == "'" and text[index + 1:index + 2] == "'":
                    skip = True
                elif each == shut:
                    shut = None
            elif each in "'\"" and (not last or last in ":,{["):
                shut = each
            else:
                yield index, each
            if not each.isspace():
                last = each

    @classmethod
    def _depth(cls, text, depth):
        """The nesting depth of `{` and `[` after `text`, which began at `depth`."""
        for _, each in cls._unquoted(text):
            depth += (each in "{[") - (each in "}]")
        return max(depth, 0)

    @classmethod
    def _pieces(cls, text):
        """The comma-separated pieces of a flow step at its own level; the `}` that closes the step ends it."""
        pieces, start, depth, end = [], 0, 0, len(text)
        for index, each in cls._unquoted(text):
            if each in "{[":
                depth += 1
            elif each in "}]":
                if depth == 0:
                    end = index
                    break
                depth -= 1
            elif each == "," and depth == 0:
                pieces.append(text[start:index])
                start = index + 1
        return pieces + [text[start:end]]
    # --- end MVP ---

    @classmethod
    def from_log(cls, log):
        """The ScenarioSteps a log's header counts and names. A log with no counts line (older) is NONE_RECORDED, and one with no
        names marker has names_state NONE_RECORDED. One that says the steps were not read, a malformed one, a names marker that
        its name lines do not match and a file that cannot be read are NOT_CHECKED. It never raises. A log holds no component
        ids, so `component_ids` and `unread_steps` stay empty."""
        try:
            header = _header(log)
        except OSError:
            why = WHY_LOG_UNREADABLE
            return cls({}, outcomes.NOT_CHECKED, why, StepNames((), outcomes.NOT_CHECKED, why))
        counts = cls._counts_in(header)
        return cls(counts.counts, counts.state, counts.why, cls._names_in(header))

    @classmethod
    def _counts_in(cls, header):
        """The ScenarioSteps (counts only) that a header's counts line says."""
        said = next((line[len(STEP_COUNTS_LINE):] for line in header if line.startswith(STEP_COUNTS_LINE)), None)
        if said is None:
            return cls({}, outcomes.NONE_RECORDED)
        if said == STEPS_NOT_READ:
            return cls({}, outcomes.NOT_CHECKED, WHY_NOT_COUNTED)
        counts = {}
        for each in said.split(", "):
            kind, _, number = each.partition(" ")
            if not re.fullmatch(r"[\w-]+", kind) or not number.isascii() or not number.isdigit() or kind in counts:
                return cls({}, outcomes.NOT_CHECKED, WHY_BAD_COUNTS)
            counts[kind] = int(number)
        return cls(counts)

    # --- MVP ---
    @staticmethod
    def _names_in(header):
        """The StepNames that a header says: the marker line, then that many name lines."""
        marker = next((line[len(STEP_NAMES_LINE):] for line in header if line.startswith(STEP_NAMES_LINE)), None)
        if marker is None:
            return StepNames()
        if marker == STEPS_NOT_READ:
            return StepNames((), outcomes.NOT_CHECKED, WHY_NAMES_NOT_READ)
        names = [line[len(STEP_NAME_LINE):] for line in header if line.startswith(STEP_NAME_LINE)]
        if not marker.isascii() or not marker.isdigit() or int(marker) != len(names):
            return StepNames((), outcomes.NOT_CHECKED, WHY_BAD_NAMES)
        return StepNames(names, outcomes.RECORDED)
    # --- end MVP ---

    def count(self, kind):
        """How many steps have this kind."""
        return self.counts.get(kind, 0)

    def has_ready_wait(self):
        """Whether a wait-serial step whose text holds READY comes before the first set-control step."""
        for kind, value in self._kinds:
            if kind == SET_CONTROL:
                return False
            if kind == WAIT_SERIAL and READY in value:
                return True
        return False

    # --- MVP ---
    def control_caveat(self, subject):
        """The P345 sentence for steps that set no control, with this subject, or None: counted steps with a set-control step."""
        if self.state != outcomes.RECORDED or self.count(SET_CONTROL):
            return None
        return (NO_CONTROL_CAVEAT if self.count(EXPECT_PIN) else NO_CONTROL_NO_PIN_CAVEAT) % subject

    def passed_sentence(self):
        """What a pass with these steps prints (P485): `passed`, or with the control caveat, or with why the steps were not counted."""
        if self.state == outcomes.NOT_CHECKED:
            return PASSED_WITH_CAVEAT % (UNCOUNTED_MESSAGE % self.why)
        caveat = self.control_caveat(THIS_RUN_MESSAGE)
        return PASSED_WITH_CAVEAT % caveat if caveat else PASSED
    # --- end MVP ---

    # --- MVP ---
    @classmethod
    def merge(cls, steps):
        """
        The ScenarioSteps of several runs together: the sum of the counts of the RECORDED ones, and the union of the names of
        those whose names_state is RECORDED, each rule apart from the other. With none RECORDED, NONE_RECORDED.
        """
        steps = list(steps)
        named = [each for each in steps if each.names_state == outcomes.RECORDED]
        names = tuple(dict.fromkeys(name for each in named for name in each.names))
        state = outcomes.RECORDED if named else outcomes.NONE_RECORDED
        counted = [each for each in steps if each.state == outcomes.RECORDED]
        if not counted:
            return cls({}, outcomes.NONE_RECORDED, None, StepNames(names, state))
        total = {}
        for each in counted:
            for kind, number in each.counts.items():
                total[kind] = total.get(kind, 0) + number
        return cls(total, named=StepNames(names, state))
    # --- end MVP ---

    def line(self):
        """The log's counts line: every kind, sorted, with the two kinds that matter always shown, or `not read`."""
        if self.state != outcomes.RECORDED:
            return STEP_COUNTS_LINE + STEPS_NOT_READ
        kinds = sorted(set(self.counts) | {SET_CONTROL, EXPECT_PIN})
        return STEP_COUNTS_LINE + ", ".join("%s %d" % (kind, self.count(kind)) for kind in kinds)

    # --- MVP ---
    def log_lines(self):
        """The log header's lines for the steps: the counts line, then the names marker and one line per name. Names that were
        not read write `step names: not read`; a names_state of NONE_RECORDED writes no marker (nothing is claimed)."""
        if self.names_state == outcomes.NOT_CHECKED:
            return "\n".join([self.line(), STEP_NAMES_LINE + STEPS_NOT_READ])
        if self.names_state != outcomes.RECORDED:
            return self.line()
        return "\n".join([self.line(), STEP_NAMES_LINE + str(len(self.names))] + [STEP_NAME_LINE + name for name in self.names])
    # --- end MVP ---


def printed_text(output):
    """What a killed process printed, as text: subprocess hands it back as bytes, as text or as nothing."""
    return output.decode("utf-8", "replace") if isinstance(output, bytes) else (output or "")


def _header(log):
    """The log's header: the lines before the first blank line. What the board printed comes later, so it is never read."""
    return Path(log).read_text(errors="replace").split("\n\n", 1)[0].splitlines()


def run_record(log):
    """
    (verdict, the tested image's sha256 or None) of one run log, read from its header, so a firmware that prints
    `verdict: passed` cannot pass a run.
    """
    header = _header(log)

    def field(prefix):
        """The text after the first header line that starts with this prefix, or None."""
        return next((line[len(prefix):].strip() for line in header if line.startswith(prefix)), None)

    return field("verdict: "), field(IMAGE_LINE)


def file_hashes(log):
    """{path inside the image: sha256} of each file the run's image held, from the header; {} for an older log."""
    return dict(reversed(line[len(FILE_LINE):].split(" ", 1)) for line in _header(log) if line.startswith(FILE_LINE))

