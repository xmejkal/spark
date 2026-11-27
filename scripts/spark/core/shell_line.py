"""
The rule a printed command passes before a person pastes it into bash or zsh (P1256): `copyable(command, home)`. A leaf of
the core: it imports only the standard library. It checks what `shlex.quote` leaves to the command around the words it
quotes: a redirection, a line end, a quote or a backslash left open, a `~` that the shell does not expand, zsh's `=word`,
an unquoted space of the home folder and a `!` of the shells' history. It does not check `;`, `|`, `&`, `#`, `*`, `(`,
`$(` or backticks, which shlex quotes, or a space in a path outside the home folder. Tests ask it today, of every command
the build and the follow-up print; the page's Copy line of P1286 (#1852) is its first caller in the product.
"""

import re

# --- MVP ---
#: How the shell reads a character: outside quotes, inside single quotes, inside double quotes, or after a backslash.
PLAIN, SINGLE, DOUBLE, ESCAPED = "plain", "single", "double", "escaped"
#: The characters a backslash escapes inside double quotes (POSIX). Before any other, the backslash stays a backslash.
DOUBLE_ESCAPES = ('"', "\\", "$", "`")


def read_states(command):
    """How the shell reads `command`: (one state per character, the state at its end). A quote that opens or closes is
    read PLAIN, and a backslash outside single quotes makes the next character ESCAPED (inside double quotes, only one
    of DOUBLE_ESCAPES). The end is PLAIN unless a quote or a backslash is left open."""
    states, state, escaped = [], PLAIN, False
    for index, char in enumerate(command):
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
            escaped = char == "\\" and (state == PLAIN or state == DOUBLE and command[index + 1:index + 2] in DOUBLE_ESCAPES)
    return states, ESCAPED if escaped else state


def starts_word(command, states, index):
    """Whether the character at `index` starts a word: it stands first, or after a space outside quotes."""
    return index == 0 or command[index - 1].isspace() and states[index - 1] == PLAIN


def unexpanded_tilde(command, states, index):
    """Whether the `~` at `index` is one the shell leaves as it is, where a person means the home folder: the first
    character inside a quote that opens a word or follows an unquoted `=`, or an unquoted `~` right after an unquoted `=`
    (`--project=~/lamp`). A leading `NAME=~/x` would expand, and the rule refuses it too: spark writes whole paths."""
    before = index - 1
    if before < 0 or states[before] != PLAIN:
        return False
    if command[before] == "=":
        return True
    return command[before] in "'\"" and states[index] in (SINGLE, DOUBLE) and (
        starts_word(command, states, before) or before > 0 and command[before - 1] == "=" and states[before - 1] == PLAIN)


def home_spaces(command, home):
    """The places in `command` of each space inside each place where `home`, the home folder's path, stands."""
    offsets = [offset for offset, char in enumerate(home) if char.isspace()]
    if not offsets:
        return []
    return [found.start() + offset for found in re.finditer("(?=%s)" % re.escape(home), command) for offset in offsets]


def copyable(command, home):
    """Whether a person can paste `command` into bash or zsh and it runs as printed, within what the module says it checks.
    False at the first of these, else True: a line end (`\\n` or `\\r`), a quote or a backslash left open at the end, a
    `<` or `>` outside quotes (a redirection), a `!` outside single quotes (history expansion), a `~` the shell does not
    expand (`unexpanded_tilde`), an unquoted `=` that starts a word (zsh runs `=ls` as the path of ls), or a space of
    `home`, the home folder's path, outside quotes where `home` stands in the command. Ask it of a command, never of a
    whole `next:` line, whose why can hold a `<part>`."""
    if "\n" in command or "\r" in command:
        return False
    states, end = read_states(command)
    if end != PLAIN:
        return False
    for index, (char, state) in enumerate(zip(command, states)):
        if char in "<>" and state == PLAIN or char == "!" and state in (PLAIN, DOUBLE):
            return False
        if char == "~" and unexpanded_tilde(command, states, index):
            return False
        if char == "=" and state == PLAIN and starts_word(command, states, index):
            return False
    return all(states[index] != PLAIN for index in home_spaces(command, str(home)))
# --- end MVP ---
