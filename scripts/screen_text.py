"""
Text for the screen (P403): a module with no spark imports, so that every reader that prints a name or a word from a
record can use it without importing another reader. `drawer.clean` is for storing a word. `printable` is for showing one.
"""


# --- MVP ---
def printable(text):
    """The text with each character that a terminal does not print as itself, such as a newline, shown as `?`."""
    return "".join(each if each.isprintable() else "?" for each in text)
