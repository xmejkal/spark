"""
The Privacy step (P605, the core contract's rule 4; S10, P677): `run_operation` masks each result and the values before
the trace and before any frontend sees them, and `MaskingReporter` masks each Event. Spark is public, and people paste
its output into issues: a path under the project becomes relative to it, one under the store `<store>/...`, any other
under the home folder `~/...`, and an account token `***` (data masking, OWASP's Logging Cheat Sheet: mask or redact
sensitive data before it is written). A line a person pastes keeps its real paths, or it would not run: a Finding of a
pasted code and every string that holds its sentence, a value under a pasted data key, a NextStep's argv and env, a
PastedLine and a raw Event.
"""

import re
from collections import namedtuple
from pathlib import Path, PurePath

from spark.core.events import Reporter

# --- MVP ---
#: What a path under the store becomes. `<store>` is SPARK_HOME, as the docs and `store.PLACEHOLDER_HINT` say.
STORE_PLACEHOLDER = "<store>"
SECRET_MASK = "***"
#: After a path: the next character is no part of a name, so the rule of `/a/b` leaves `/a/bc` alone.
PATH_END = r"(?![\w.-])"
#: Value: one masking rule: the text it finds (`place`), the pattern that must follow it, and what it becomes.
MaskRule = namedtuple("MaskRule", "place after replacement")
#: Value: where a line a person or an agent acts on travels (pastes, runs or opens): the Finding codes whose sentence or
#: fix holds such a line, and the data keys that hold one.
Pasted = namedtuple("Pasted", "codes keys", defaults=((), ()))


class PastedLine(str):
    """Value: a line of `lines` or `diagnostics` that a person pastes, such as grant.py's `rm` line, where no pasted
    Finding marks it. Privacy leaves it as it is."""

    __slots__ = ()


def forms_of(path):
    """A path as a run may print it: whole as written and resolved. None and the root give none, as they name no folder."""
    if path is None:
        return set()
    return {form for form in (str(Path(path).absolute()), str(Path(path).resolve())) if len(form) > 1}


class Privacy:
    """Strategy: what a run may show outside spark. With no rules it passes everything through, as a test's run does;
    `of` builds the rules of one run. The longest place wins, so a store inside the project is the store."""

    def __init__(self, rules=(), pasted=Pasted()):
        ordered = sorted(rules, key=lambda rule: -len(rule.place))
        self.replacements = [rule.replacement for rule in ordered]
        self.pattern = re.compile("|".join("(%s%s)" % (re.escape(rule.place), rule.after) for rule in ordered)) if ordered else None
        self.pasted = pasted

    @classmethod
    def of(cls, project, store, home, secrets, pasted=Pasted()):
        """The Privacy of one run on `project`, with `store` the store's folder, `home` the person's and `secrets` the
        account tokens the run may hold (an empty one masks nothing)."""
        rules = [MaskRule(secret, "", SECRET_MASK) for secret in secrets if secret]
        for form in forms_of(project):
            rules += [MaskRule(form + "/", "", ""), MaskRule(form, PATH_END, ".")]
        rules += [MaskRule(form, PATH_END, STORE_PLACEHOLDER) for form in forms_of(store)]
        rules += [MaskRule(form, PATH_END, "~") for form in forms_of(home)]
        return cls(rules, pasted)

    def mask_text(self, text):
        """`text` with the place of each rule replaced, in one pass."""
        if self.pattern is None or not isinstance(text, str):
            return text
        return self.pattern.sub(lambda found: self.replacements[found.lastindex - 1], text)

    def masked(self, value, kept=()):
        """`value` with every string masked, through lists, tuples and dicts. A string that holds one of `kept` (a pasted
        sentence), or that one of them holds, stays, as that sentence shows it raw anyway; so does a value under a pasted
        key. A path becomes its masked string."""
        if isinstance(value, PastedLine):
            return value
        if isinstance(value, PurePath):
            value = str(value)
        if isinstance(value, str):
            return value if any(sentence in value or value in sentence for sentence in kept) else self.mask_text(value)
        if isinstance(value, dict):
            return {key: item if key in self.pasted.keys else self.masked(item, kept) for key, item in value.items()}
        if isinstance(value, (list, tuple)):
            items = [self.masked(item, kept) for item in value]
            return items if isinstance(value, list) else tuple(items)
        return value

    def mask_result(self, result):
        """The OperationResult as a frontend and the trace may see it: `data`, `findings`, the `why` of each NextStep,
        `lines`, `diagnostics` and `notes` masked, but the pasted places."""
        if self.pattern is None:
            return result
        kept = [found.sentence for found in result.findings if found.code in self.pasted.codes and found.sentence]
        findings = [found if found.code in self.pasted.codes else self._masked_finding(found, kept) for found in result.findings]
        return result._replace(data=self.masked(result.data, kept), findings=findings,
                               next=[step._replace(why=self.masked(step.why, kept)) for step in result.next],
                               lines=self.masked(result.lines, kept), diagnostics=self.masked(result.diagnostics, kept),
                               notes=self.masked(result.notes, kept))

    def mask_values(self, values):
        """The values of a run as the trace may see them."""
        return values if self.pattern is None else self.masked(values)

    def mask_event(self, event):
        """The Event as a reader may see it; a raw one, which carries a pasted line, as it is."""
        return event if event.raw or event.text is None else event._replace(text=self.mask_text(event.text))

    def _masked_finding(self, found, kept):
        return found._replace(subject=self.masked(found.subject, kept), sentence=self.masked(found.sentence, kept),
                              fix=self.masked(found.fix, kept))


class MaskingReporter(Reporter):
    """Decorator: a Reporter that passes each Event through `privacy.mask_event` to `inner`, which shows it. Its `stream`
    is the inner one's, where the terminal consent asks."""

    def __init__(self, inner, privacy):
        self.inner, self.privacy = inner, privacy
        self.stream = getattr(inner, "stream", None)

    def report(self, event):
        self.inner.report(self.privacy.mask_event(event))

    def echo_fd(self):
        return self.inner.echo_fd()
# --- end MVP ---
