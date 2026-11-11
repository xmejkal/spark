"""
The questions an Operation cannot answer itself, and who answers them (P737). A `Question` is typed, so Claude or a person
reads what is asked, how to answer it and where the answer is. A `ReplyStrategy` answers it: from replies given ahead
(scripted), live in a terminal (step R2), or not now. `RepliesStore` keeps the project's replies file, the one scripted
channel. An unanswered question is unchecked: the run's status is `could-not-run`, and `data.open` holds the questions.
`OutsideWorld.replies` is the strategy's `reply`, given to an Operation that declares ASKS. `ConsentStrategy`
(`spark.bench.deploy_gate`) is the member that answers a yes or no: the deploy's yes. The first Operation that asks is
`ResearchPart` (step 4).
"""

import abc
import difflib
import getpass
import json
import math
import sys
from collections import namedtuple
from pathlib import Path

from spark.core import outcomes
from spark.core.codes import BAD_ARGUMENT, BAD_REPLY, NEEDS_REPLY, UNKNOWN_REPLY
from spark.core.errors import SparkError
from spark.core.result import Finding
from spark.core.text_guards import guard_lines

# --- MVP ---
#: The kinds of a Question: a yes or no, a value in `answer_form` and `unit`, or one of `choices`.
YES_NO, VALUE, CHOICE = "yes_no", "value", "choice"
KINDS = (YES_NO, VALUE, CHOICE)
#: Who a Question is asked of. An AGENT question is never shown to a person in a terminal; a PERSON question needs
#: the person's hands or eyes (a revision, a soldered header); EITHER goes to whoever is there.
PERSON, AGENT, EITHER = "person", "agent", "either"
ASKED_OF = (PERSON, AGENT, EITHER)
#: The replies file of a project: run 1 writes it as a template, Claude or the person fills it, run 2 reads it.
REPLIES_FILE = Path(".spark") / "research-replies.json"
#: The top key of the replies file.
REPLIES_KEY = "replies"
#: `Reply.answered_by` of a reply read from a file, and of one typed in a terminal (the deploy's yes says it too).
FROM_FILE = "replies file %s"
TYPED_BY = "typed in a terminal by %s"
#: The words of a question asked live: the hint after the text, what a yes or no takes, the cited page, and what Ctrl-C did.
LATER_HINT = "(%s, Enter = later)"
YES_OR_NO = "yes or no"
SEE_PAGE = "see %s, page %s"
LEFT_LINE = "Ctrl-C: the rest stays open"
YES_WORDS, NO_WORDS = ("yes", "y"), ("no", "n")
#: The sentence and the fix of an open question's Finding.
WAITING = "waiting on a reply: %s"
FILL_AND_RUN = "fill %s and run %s --replies %s"
#: What a reply lacks, by kind.
NOT_YES_NO = "the reply is %r, and a %s question takes yes or no (true or false)"
NOT_A_CHOICE = "the reply is %r, and the choices are %s"
EMPTY = "the reply is empty"
NOT_FINITE = "the reply is %r, not a finite number"
#: The sentences of `reply_problems`.
UNKNOWN_KEY = "no open question has the key %s"
NOT_OPEN = "the key %s is a fact already filled, not open; a reply to it would overwrite the fact"
NEAREST_FIX = "did you mean %s? Keys are in the run's data.open"
NO_NEAREST_FIX = "remove it, or take a key from the run's data.open"
MISFIT_FIX = "answer as the question's answer_form says, for example %s"
MISFIT_FORM_FIX = "answer as the question asks: %s"
#: What a kind takes, for a question with no `answer_form` and no `example`.
KIND_FORMS = {YES_NO: "true or false", VALUE: "a value that is not empty", CHOICE: "one of the choices"}
UNREADABLE_FIX = "run once without --replies to write the template, then fill its values"
WRONG_SHAPE = 'a replies file is {"replies": {"<key>": {"value": ..., "note": "...", "cites": {...}}}}, or a bare "<key>": value'


class Question(namedtuple("Question", "key text kind asked_of why unit answer_form example choices cites", defaults=(None,) * 6)):
    """
    Value: one thing an Operation cannot answer itself. `key` is the fact path it fills (`physical.mounting_holes`) or a
    decision's name. `text` is one sentence. `kind` is YES_NO, VALUE or CHOICE, `asked_of` PERSON, AGENT or EITHER.
    `answer_form` says the shape in words, `example` holds placeholders only, never a number Claude can copy, and `cites`
    is `{document, at}`: the kept document and the page, so the question is answerable from the store with no other reading.
    """

    def __new__(cls, *values, **named):
        question = super().__new__(cls, *values, **named)
        if question.kind not in KINDS or question.asked_of not in ASKED_OF or (question.kind == CHOICE and not question.choices):
            raise ValueError("a Question has a kind of %s and an asked_of of %s, and a choice has choices; got %r" % (KINDS, ASKED_OF, question))
        return question

    def to_dict(self):
        """The envelope's item in `data.open`."""
        return self._asdict()

    def misfit(self, value):
        """What `value` lacks as an answer to this question, or None when it fits its kind: a yes or no is a bool, a choice
        is one of `choices`, a value is not empty and, as a number, finite. The record's own rules check the fact itself."""
        if self.kind == YES_NO:
            return None if isinstance(value, bool) else NOT_YES_NO % (value, YES_NO)
        if self.kind == CHOICE:
            return None if value in self.choices else NOT_A_CHOICE % (value, ", ".join(self.choices))
        if isinstance(value, float) and not math.isfinite(value):
            return NOT_FINITE % (value,)
        return EMPTY if value in ("", [], {}, None) else None


#: Value: one answer. `answered_by` is spark's: "replies file <name>", "typed in a terminal by …", a consent's `who`. `at`
#: is the time when the answerer gave it, or None when the channel carries no time (a file). `cites` is `{document, at}` or None.
Reply = namedtuple("Reply", "key value answered_by at note cites", defaults=(None, None, None))


class ReplyStrategy(abc.ABC):
    """Strategy: how a Question gets its Reply. `reply(question)` gives a Reply, or None for "not now": the Operation puts
    the question on the run's open list."""

    @abc.abstractmethod
    def reply(self, question):
        """The Reply to `question`, or None."""


class GivenReplyStrategy(ReplyStrategy):
    """Strategy: replies given ahead, a dict of key to Reply (a RepliesStore's `load`). Scripted. It knows no file."""

    def __init__(self, replies):
        self.replies = dict(replies)

    def reply(self, question):
        return self.replies.get(question.key)


class DeferringReplyStrategy(ReplyStrategy):
    """Strategy: nothing is answered now. A null object with no state: every question stays open."""

    def reply(self, question):
        return None


class ChainedReplyStrategy(ReplyStrategy):
    """Strategy: the strategies in order, and the first Reply wins. None when none answers. The frontend chains the replies
    file before the terminal, so a person is asked only what the file left open."""

    def __init__(self, strategies):
        self.strategies = list(strategies)

    def reply(self, question):
        for strategy in self.strategies:
            reply = strategy.reply(question)
            if reply is not None:
                return reply
        return None


class Terminal:
    """Adapter: the person's terminal, stdin and stdout, behind spark's interface, read at the call so a redirected stream is the one
    used. `live` says whether both are a tty. `say` shows masked, guarded text; `ask` shows a prompt and reads one line, stripped, or
    None when the person pressed Ctrl-C (the caller keeps what it has; Ctrl-D reads as ""). The one class that reads a tty (rule X2);
    `TerminalConsentStrategy` and `TerminalReplyStrategy` go through it. `mask` is the run's Privacy, so a line shows no home path."""

    def __init__(self, stdin=None, stdout=None, mask=None):
        self.stdin, self.stdout = stdin or sys.stdin, stdout or sys.stdout
        self.mask = mask or (lambda text: text)

    @property
    def live(self):
        return self.stdin.isatty() and self.stdout.isatty()

    def say(self, text):
        self.stdout.write(guard_lines(self.mask(text)) + "\n")
        self.stdout.flush()

    def ask(self, prompt):
        self.stdout.write(guard_lines(self.mask(prompt)))
        self.stdout.flush()
        try:
            return self.stdin.readline().strip()
        except KeyboardInterrupt:
            return None


class TerminalReplyStrategy(ReplyStrategy):
    """Strategy: the questions asked live, one at a time, in a `Terminal`. It never shows an AGENT question. Enter leaves a question
    open; so does an answer that does not fit its kind, after the misfit is said, with no second try. Ctrl-C says LEFT_LINE once and
    leaves this and every later question open, so what was answered before is kept. `who` is the login of the person at the terminal."""

    def __init__(self, terminal, user_name=getpass.getuser):
        self.terminal, self.user_name, self.left = terminal, user_name, False

    @property
    def who(self):
        return TYPED_BY % self.user_name()

    def reply(self, question):
        if question.asked_of == AGENT or self.left:
            return None
        typed = self.terminal.ask(self._prompt(question))
        if typed is None:
            self.left = True
            self.terminal.say(LEFT_LINE)
            return None
        if typed == "":
            return None
        value = self._value(question, typed)
        lacks = question.misfit(value)
        if lacks:
            self.terminal.say(lacks)
            return None
        return Reply(question.key, value, self.who, None, None, question.cites)

    @staticmethod
    def _prompt(question):
        """The question as the person reads it: the text and the hint, `why`, the cited page, the numbered choices, then `> `."""
        hint = YES_OR_NO if question.kind == YES_NO else question.unit or question.answer_form or KIND_FORMS[question.kind]
        lines = ["%s %s" % (question.text, LATER_HINT % hint)]
        lines += [question.why] if question.why else []
        lines += [SEE_PAGE % (question.cites.get("document"), question.cites.get("at"))] if isinstance(question.cites, dict) else []
        lines += ["  %d %s" % (number, choice) for number, choice in enumerate(question.choices or (), 1)]
        return "\n".join(lines) + "\n> "

    @staticmethod
    def _value(question, typed):
        """What the typed line means for the question's kind: yes or no as a bool, a choice by number or by its text, a value as JSON
        when it parses (a number, a list, an object as `answer_form` asks) and the text itself when it does not."""
        if question.kind == YES_NO:
            return True if typed.lower() in YES_WORDS else False if typed.lower() in NO_WORDS else typed
        if question.kind == CHOICE:
            return question.choices[int(typed) - 1] if typed.isdigit() and 0 < int(typed) <= len(question.choices) else typed
        try:
            return json.loads(typed)
        except ValueError:
            return typed


class TextFileWriter:
    """Adapter: `write(path, text)` writes a text file, making its folder first; the one place in the core that may (rule T1).
    `RepliesStore` writes through it. It is not an OutsideWorld field yet: `write` enters there with its first Operation."""

    def write(self, path, text):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


class RepliesStore:
    """
    Store: the one replies file of a project, `<project>/.spark/research-replies.json`, not the person's store. `dump`
    writes a template: every open key with `"value": null`, and keeps what is in the file, so a rerun adds nothing twice and
    Claude fills values and invents no key. `load` gives the dict of Reply for the keys with a value; a null is "not answered yet".
    """

    def __init__(self, path):
        self.path = Path(path)

    @classmethod
    def for_project(cls, project):
        return cls(Path(project) / REPLIES_FILE)

    def _read(self):
        """The file's `replies` object. A file that is missing, is not JSON or has another shape is a SparkError `bad_argument`."""
        try:
            given = json.loads(self.path.read_text(encoding="utf-8"))[REPLIES_KEY]
            if not isinstance(given, dict):
                raise TypeError(WRONG_SHAPE)
            return given
        except (OSError, ValueError, KeyError, TypeError) as why:
            raise SparkError("the replies file %s cannot be read: %s", self.path, why, code=BAD_ARGUMENT, fix=UNREADABLE_FIX)

    def load(self):
        """The replies in the file, by key, each with `answered_by` set. A bare `"<key>": value` is read as `{"value": value}`, an
        object too unless it carries `value` (the template always writes one). A file that cannot be read is `_read`'s SparkError."""
        entries = {key: entry if isinstance(entry, dict) and "value" in entry else {"value": entry} for key, entry in self._read().items()}
        return {key: Reply(key, entry["value"], FROM_FILE % self.path.name, None, entry.get("note"), entry.get("cites"))
                for key, entry in entries.items() if entry.get("value") is not None}

    def dump(self, questions):
        """Write the template: the file's entries as they are, plus `{"value": null, "note": "", "cites"}` per open key it lacks."""
        held = self._read() if self.path.exists() else {}
        for question in questions:
            held.setdefault(question.key, {"value": None, "note": "", "cites": question.cites})
        TextFileWriter().write(self.path, json.dumps({REPLIES_KEY: held}, indent=1, ensure_ascii=False) + "\n")


def order_open(questions):
    """The open list's order: a PERSON question first, the rest as asked."""
    return sorted(questions, key=lambda question: question.asked_of != PERSON)


def needs_reply_findings(questions, replies_path, line):
    """One unchecked Finding per open question, code `needs_reply`, the key as subject: the run is `could-not-run` until
    the replies come. `line` is the command that runs the Operation again; the fix adds `--replies`."""
    return [Finding(outcomes.COULD_NOT_RUN, question.key, NEEDS_REPLY, WAITING % question.text, FILL_AND_RUN % (replies_path, line, replies_path))
            for question in questions]


def misfit_fix(question):
    """The fix of a `bad_reply`: the question's `example` when it has one, else its `answer_form`, else what its kind takes."""
    if question.example is not None:
        return MISFIT_FIX % (json.dumps(question.example),)
    return MISFIT_FORM_FIX % (question.answer_form or KIND_FORMS[question.kind])


def reply_problems(replies, questions, filled=()):
    """The problems in `replies` (key to Reply) against the open `questions`: a key no question has is `unknown_reply`
    with the nearest open key, a key in `filled` (a fact the record holds) is `unknown_reply` too, because a stray reply
    would overwrite a fact, and a value that does not fit its question's kind is `bad_reply`. Nothing here is silent."""
    open_by_key = {question.key: question for question in questions}
    found = []
    for key, reply in replies.items():
        if key in open_by_key:
            lacks = open_by_key[key].misfit(reply.value)
            if lacks:
                found.append(Finding(outcomes.PROBLEMS, key, BAD_REPLY, lacks, misfit_fix(open_by_key[key])))
        elif key in filled:
            found.append(Finding(outcomes.PROBLEMS, key, UNKNOWN_REPLY, NOT_OPEN % key, NO_NEAREST_FIX))
        else:
            nearest = difflib.get_close_matches(key, list(open_by_key), n=1)
            found.append(Finding(outcomes.PROBLEMS, key, UNKNOWN_REPLY, UNKNOWN_KEY % key, NEAREST_FIX % nearest[0] if nearest else NO_NEAREST_FIX))
    return found
# --- end MVP ---
