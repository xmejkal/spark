"""
The style of the text view (P1032): whether this run's stdout may show colour, a line that redraws itself, and the
marks' symbols. It is decided once per run from the stream and the environment, never from CLAUDECODE, which an IDE's
terminal sets too. It imports nothing of spark. `replies.Terminal`, the one class that reads a tty, asks it.
"""

from collections import namedtuple

# --- MVP ---
#: Value: how the text view may look on this run's stream, decided once per run (P1032). `colour`: SGR codes.
#: `motion`: a line that redraws itself (the spinner card reads it). `symbols`: the stream can encode the marks.
TextStyle = namedtuple("TextStyle", "colour motion symbols")
#: The style of a pipe, a file and Claude's shell: no codes, no motion, and the marks' symbols.
PLAIN = TextStyle(False, False, True)
#: The TERM values that cannot show colour or motion. "" is an unset TERM (D9).
DUMB_TERMS = ("", "dumb", "unknown")
#: The marks' symbols, which the stream's encoding must encode (D8).
SYMBOLS = "✓✗!"


def is_terminal(stream):
    """Whether `stream` is a terminal. A stream that raises in isatty(), such as a closed one, is no terminal."""
    try:
        return bool(stream.isatty())
    except (ValueError, OSError):
        return False


def can_encode_marks(stream):
    """Whether `stream`'s encoding encodes SYMBOLS. A stream with no encoding (a StringIO) holds any character."""
    encoding = getattr(stream, "encoding", None)
    if not encoding:
        return True
    try:
        SYMBOLS.encode(encoding)
    except (UnicodeEncodeError, LookupError):
        return False
    return True


def text_style_of(stream, environ):
    """The TextStyle for `stream` and `environ` (a mapping). NO_COLOR set and not empty removes colour and wins.
    FORCE_COLOR set and not empty adds colour, never motion. Else colour and motion come only with a terminal whose TERM
    is not in DUMB_TERMS. `symbols` is False when the stream's encoding cannot encode SYMBOLS. CLAUDECODE decides nothing."""
    motion = is_terminal(stream) and environ.get("TERM", "") not in DUMB_TERMS
    colour = (motion or bool(environ.get("FORCE_COLOR"))) and not environ.get("NO_COLOR")
    return TextStyle(colour, motion, can_encode_marks(stream))
# --- end MVP ---
