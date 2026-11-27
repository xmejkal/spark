"""
The rule a printed command passes before a person pastes it into bash or zsh (P1256): `copyable(line, home)`. A leaf of the
core: it imports only the standard library. It checks what `shlex.quote` leaves to the line around the words it quotes: a
redirection, a line end, a quoted `~` that starts a word, an unquoted space of the home folder and a `!` of the shells'
history. It does not check `;`, `|`, `&`, `$(` or backticks, which shlex quotes.
"""

import re

# --- MVP ---
#: How the shell reads a character: outside quotes, inside single quotes, inside double quotes, or after a backslash.
PLAIN, SINGLE, DOUBLE, ESCAPED = "plain", "single", "double", "escaped"
#: The characters a backslash escapes inside double quotes (POSIX). Before any other, the backslash stays a backslash.
DOUBLE_ESCAPES = ('"', "\\", "$", "`")


def read_states(line):
    """How the shell reads each character of `line`, one state per character. A quote that opens or closes is read PLAIN,
    and a backslash outside single quotes makes the next character ESCAPED (inside double quotes, only one of
    DOUBLE_ESCAPES)."""
    states, state, escaped = [], PLAIN, False
    for index, char in enumerate(line):
        if escaped:
            states.append(ESCAPED)
            escaped = False
        elif state == PLAIN and char in "'\"":
            states.append(PLAIN)
            state = SINGLE if char == "'" else DOUBLE
        elif (state, char) in ((SINGLE, "'"), (DOUBLE, '"')):
            states.append(PLAIN)
            state = PLAIN
        else:
            states.append(state)
            escaped = char == "\\" and (state == PLAIN or state == DOUBLE and line[index + 1:index + 2] in DOUBLE_ESCAPES)
    return states


def starts_quoted_word(line, states, index):
    """Whether the character at `index` is the first one inside a quote that opens a word: the quote is read PLAIN and
    stands at the start of the line or after a space outside quotes."""
    opener = index - 1
    return (opener >= 0 and line[opener] in "'\"" and states[opener] == PLAIN and states[index] in (SINGLE, DOUBLE)
            and (opener == 0 or line[opener - 1].isspace() and states[opener - 1] == PLAIN))


def home_spaces(line, home):
    """The places in `line` of each space inside each place where `home`, the home folder's path, stands."""
    offsets = [offset for offset, char in enumerate(home) if char.isspace()]
    if not offsets:
        return []
    return [found.start() + offset for found in re.finditer("(?=%s)" % re.escape(home), line) for offset in offsets]


def copyable(line, home):
    """Whether a person can paste `line` into bash or zsh and it runs as printed. False at the first of these, else True:
    a line end (`\\n` or `\\r`), a `<` or `>` outside quotes (a redirection), a `!` outside single quotes (history
    expansion), a `~` that starts a quoted word (the shell does not expand it), or a space of `home`, the home folder's
    path, outside quotes where `home` stands in the line. A backslash escapes the next character, as the shell reads it."""
    if "\n" in line or "\r" in line:
        return False
    states = read_states(line)
    for index, (char, state) in enumerate(zip(line, states)):
        if char in "<>" and state == PLAIN or char == "!" and state in (PLAIN, DOUBLE):
            return False
        if char == "~" and starts_quoted_word(line, states, index):
            return False
    return all(states[index] != PLAIN for index in home_spaces(line, str(home)))
# --- end MVP ---
