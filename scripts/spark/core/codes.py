"""
The codes the core writes in an envelope item for every Operation (P442, W3-3), and `Code`, the value an area's table
holds a code as (P853). A leaf: it imports nothing. An area's own codes stay in its table (`spark/bench/board_codes.py`
for the bench); these are the ones `run_operation` and `run_cli` give whatever the Operation. `CODES` says each in one
sentence, as `board_codes.CODES` does, and `docs/guide/agents/json.md` names each. Each is a Code with its fix (P935):
a fix with `%` is a template its site fills, and a fix that differs in kind is a variant, another Code of the same word
and meaning, named after its parent. The variants here are the core's own contexts only; an area keeps its own.
"""

# --- MVP ---
class Code(str):
    """
    Value: a code, the word an agent decides on, with its `meaning` (what the code says in one sentence) and its `fix`
    (what to do), so a Finding and a SparkError take the fix from the code (P853). It is a str, so a key, a comparison
    and the JSON stay as they were. A Finding's `sentence` is the text of one case, never the code's meaning.
    """

    def __new__(cls, word, meaning, fix):
        code = super().__new__(cls, word)
        code.meaning, code.fix = meaning, fix
        return code

    def __getnewargs__(self):
        """The arguments copy, deepcopy and pickle make the Code again with."""
        return str(self), self.meaning, self.fix


def fix_of(code, fix=None):
    """`fix` when it is given, else the fix `code` holds: the one rule of `Finding.of` and `SparkError`. A TypeError that
    names the code when a plain str or a Code whose fix is a template (it holds `%`, P935) comes with no fix, so a raw
    `%s` never reaches the JSON."""
    if fix is not None:
        return fix
    if not isinstance(code, Code):
        raise TypeError("the code %r holds no fix: give fix=, or make it a Code" % (code,))
    if "%" in code.fix:
        raise TypeError("the fix of %r is a template: give fix=, filled with its values" % (code,))
    return code.fix


#: An argument the Operation cannot run with: `run_cli` answers it for every Operation (it was board_codes.BAD_ARGUMENT).
#: The fix is a template of the CLI's name.
BAD_ARGUMENT = Code("bad_argument", "an argument that the script cannot run with", "%s --help lists the arguments")
#: A variant of BAD_ARGUMENT: the replies file that --replies names cannot be read (`replies.RepliesStore`).
BAD_ARGUMENT_REPLIES_UNREADABLE = Code(BAD_ARGUMENT, BAD_ARGUMENT.meaning,
                                       "run once without --replies to write the template, then fill its values")
#: A variant of BAD_ARGUMENT: the replies file cannot be written, so a used reply is not marked (`replies.RepliesStore`).
BAD_ARGUMENT_REPLIES_UNWRITABLE = Code(BAD_ARGUMENT, BAD_ARGUMENT.meaning,
                                       "make the file writable, so that spark can mark the reply as used, then run again")
#: The Operation raised an exception it did not turn into a Finding: a defect in spark, never in the project.
CRASH = Code("crash", "the operation crashed, a defect in spark: the traceback is on stderr",
             "report this to the spark maintainers with the stderr traceback")
#: The Operation reached an outside its `effects` do not declare (it ran a program without `runs`): a defect in spark.
UNDECLARED_EFFECT = Code("undeclared_effect", "the operation reached an outside that its effects do not declare, a defect in spark",
                         "a defect in spark: report it, with the command")
#: A question the Operation could not answer itself and nobody answered yet (P737): the run is unchecked until a reply comes.
#: The fix is a template of the replies file, the command and the replies file again.
NEEDS_REPLY = Code("needs_reply", "a question nobody answered yet: run again with --replies once the file is filled",
                   "fill %s and run %s --replies %s")
#: A reply to a key that no open question has, or to a fact the record already holds (P737).
UNKNOWN_REPLY = Code("unknown_reply", "a reply to a key that no open question has, or to a fact already filled",
                     "remove it, or take a key from the run's data.open")
#: A variant of UNKNOWN_REPLY: an open key is near the reply's; the fix is a template of that key.
UNKNOWN_REPLY_NEAR = Code(UNKNOWN_REPLY, UNKNOWN_REPLY.meaning, "did you mean %s? Keys are in the run's data.open")
#: A reply whose value does not fit its question's kind: not a yes or no, not one of the choices, empty, or not a finite number (P737).
#: The fix is a template of the question's example, as JSON.
BAD_REPLY = Code("bad_reply", "a reply whose value does not fit its question's kind",
                 "answer as the question's answer_form says, for example %s")
#: A variant of BAD_REPLY: the question has no example; the fix is a template of its answer_form, or of what its kind takes.
BAD_REPLY_AS_ASKED = Code(BAD_REPLY, BAD_REPLY.meaning, "answer as the question asks: %s")
#: The JSON a payload Argument names, a file or stdin, cannot be read or is not JSON (P726 PR 3; it was sourcing_codes' since P717).
INPUT_UNREADABLE = Code("input_unreadable", "the JSON a write reads, from a file or from stdin, cannot be read or is not JSON",
                        "make the file or the stdin that the sentence names hold JSON, then run again")

#: Each code and the one sentence that says what it means.
CODES = {code: code.meaning for code in (BAD_ARGUMENT, CRASH, UNDECLARED_EFFECT, NEEDS_REPLY, UNKNOWN_REPLY, BAD_REPLY, INPUT_UNREADABLE)}
# --- end MVP ---
