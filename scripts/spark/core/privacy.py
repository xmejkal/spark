"""
The Privacy step (P605, the core contract's rule 4; S10, P677): `run_operation` masks each result and the values before
the trace and before any frontend sees them, and `MaskingReporter` masks each Event. Spark is public, and people paste
its output into issues: the project folder becomes `<project>` and a path under it relative to it, a path under the
store `<store>/...`, any other under the home folder `~/...`, and an account token `***` (data masking, OWASP's Logging
Cheat Sheet: mask or redact sensitive data before it is written).

A line a person or an agent acts on (pastes, runs or opens) keeps its real paths, or it would not work; its tokens are
masked all the same. To mark one, use the smallest of these: a Finding code in `board_codes.PASTED_CODES` (its fields,
and the same sentence wherever a line holds it), a data key in `board_envelope.PASTED_KEYS` (at any depth), a
`PastedLine` in `lines` or `diagnostics`, or `Event.line(code, text, raw=True)`. A NextStep's `argv` and `env` are raw.
"""

import re
from collections import namedtuple
from pathlib import Path, PurePath

from spark.core.events import Reporter

# --- MVP ---
#: What the project folder and a path under the store become. `<store>` is SPARK_HOME, as `docs/guide/agents.md` says.
PROJECT_PLACEHOLDER, STORE_PLACEHOLDER = "<project>", "<store>"
SECRET_MASK = "***"
#: After a path: the next character is no part of a name, so the rule of `/a/b` leaves `/a/bc` and `/a/b.bak` alone,
#: and masks `/a/b.` at the end of a sentence.
PATH_END = r"(?![\w-]|\.\w)"
#: After the project folder's slash: a name follows, so `/p/sim` becomes `sim` and `/p/ now` keeps `<project>/`.
NAME_FOLLOWS = r"(?=[\w.-])"
#: A string that a pasted sentence holds stays raw only from this length on, so a word such as `ok` gets no free pass.
KEPT_PART_MIN = 12
#: Value: one masking rule: the text it finds (`place`), the pattern that must follow it, and what it becomes.
MaskRule = namedtuple("MaskRule", "place after replacement")
#: Value: where a line a person or an agent acts on travels (pastes, runs or opens): the Finding codes whose sentence or
#: fix holds such a line, and the data keys that hold one.
Pasted = namedtuple("Pasted", "codes keys", defaults=((), ()))


class PastedLine(str):
    """Value: a line of `lines` or `diagnostics` that a person pastes, such as grant.py's `rm` line, where no pasted
    Finding marks it. Privacy masks only its tokens."""

    __slots__ = ()


class Replacer:
    """Value: MaskRules compiled into one pattern, the longest place first, so a store inside the project is the store.
    `sub` replaces each place in one pass; with no rules it changes nothing."""

    def __init__(self, rules):
        ordered = sorted(rules, key=lambda rule: -len(rule.place))
        self.replacements = [rule.replacement for rule in ordered]
        self.pattern = re.compile("|".join("(%s%s)" % (re.escape(rule.place), rule.after) for rule in ordered)) if ordered else None

    def sub(self, text):
        if self.pattern is None:
            return text
        return type(text)(self.pattern.sub(lambda found: self.replacements[found.lastindex - 1], text))


def forms_of(path):
    """A path as a run may print it: whole as written and resolved. None and the root give none, as they name no folder."""
    if path is None:
        return set()
    return {form for form in (str(Path(path).absolute()), str(Path(path).resolve())) if len(form) > 1}


class Privacy:
    """Strategy: what a run may show outside spark. With no rules it passes everything through, as a test's run does;
    `of` builds the rules of one run. `paths` holds every rule, `secrets` the token rules alone, for the raw places."""

    def __init__(self, rules=(), pasted=Pasted()):
        self.paths = Replacer(rules)
        self.secrets = Replacer([rule for rule in rules if rule.replacement == SECRET_MASK])
        self.pasted = pasted

    @classmethod
    def of(cls, project, store, home, secrets, pasted=Pasted()):
        """The Privacy of one run on `project`, with `store` the store's folder, `home` the person's and `secrets` the
        account tokens the run may hold (an empty one masks nothing)."""
        rules = [MaskRule(secret, "", SECRET_MASK) for secret in secrets if secret]
        for form in forms_of(project):
            rules += [MaskRule(form + "/", NAME_FOLLOWS, ""), MaskRule(form, PATH_END, PROJECT_PLACEHOLDER)]
        rules += [MaskRule(form, PATH_END, STORE_PLACEHOLDER) for form in forms_of(store)]
        rules += [MaskRule(form, PATH_END, "~") for form in forms_of(home)]
        return cls(rules, pasted)

    def mask_text(self, text):
        """`text` with the place of each rule replaced, in one pass."""
        return self.paths.sub(text) if isinstance(text, str) else text

    def masked(self, value, kept=(), raw=False):
        """`value` with every string masked, through lists, tuples and dicts; in a raw place (`raw`, a pasted key, a
        PastedLine) only its tokens. `kept` are the sentences and fixes of the pasted Findings (see `_masked_text`). A
        path becomes its string."""
        if self.paths.pattern is None:
            return value
        if isinstance(value, PurePath):
            value = str(value)
        if isinstance(value, str):
            return self._masked_text(value, kept, raw or isinstance(value, PastedLine))
        if isinstance(value, dict):
            return {key: self.masked(item, kept, raw or key in self.pasted.keys) for key, item in value.items()}
        if isinstance(value, (list, tuple)):
            items = [self.masked(item, kept, raw) for item in value]
            return items if isinstance(value, list) else tuple(items)
        return value

    def _masked_text(self, text, kept, raw):
        """A string that holds a pasted sentence keeps that sentence raw and masks the rest; one that a sentence holds, of
        KEPT_PART_MIN characters or more, stays raw, as the sentence shows it anyway. Tokens go everywhere."""
        if raw:
            return self.secrets.sub(text)
        for sentence in kept:
            if sentence in text:
                return self.secrets.sub(sentence).join(self._masked_text(part, kept, False) for part in text.split(sentence))
            if len(text) >= KEPT_PART_MIN and text in sentence:
                return self.secrets.sub(text)
        return self.paths.sub(text)

    def mask_result(self, result):
        """The OperationResult as a frontend and the trace may see it: `data`, `findings`, `next`, `lines`, `diagnostics`
        and `notes` masked, the raw places only of their tokens."""
        if self.paths.pattern is None:
            return result
        kept = [text for found in result.findings if found.code in self.pasted.codes for text in (found.sentence, found.fix) if text]
        findings = [self._masked_finding(found, kept, found.code in self.pasted.codes) for found in result.findings]
        steps = [step._replace(argv=self.masked(step.argv, raw=True), env=self.masked(step.env, raw=True), why=self.masked(step.why, kept))
                 for step in result.next]
        return result._replace(data=self.masked(result.data, kept), findings=findings, next=steps,
                               lines=self.masked(result.lines, kept), diagnostics=self.masked(result.diagnostics, kept),
                               notes=self.masked(result.notes, kept))

    def mask_values(self, values):
        """The values of a run as the trace may see them."""
        return self.masked(values)

    def mask_event(self, event):
        """The Event as a reader may see it; a raw one, which carries a line a person acts on, only of its tokens."""
        if event.text is None:
            return event
        return event._replace(text=self.secrets.sub(event.text) if event.raw else self.paths.sub(event.text))

    def _masked_finding(self, found, kept, raw):
        return found._replace(subject=self.masked(found.subject, kept, raw), sentence=self.masked(found.sentence, kept, raw),
                              fix=self.masked(found.fix, kept, raw))


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

    def mask(self, text):
        return self.privacy.mask_text(text)
# --- end MVP ---
