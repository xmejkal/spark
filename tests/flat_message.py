"""
The check that one value with a line break gives a message one line of that value (P451). A test file that moves a raise to
`ValueMessageError` passes `NASTY` as the value and `assert_flat` reads the error: no line of the message starts with the
fake `GRANTED`, the fake text is in the message (the test cannot pass for the wrong reason), and the value as it was is in
`error.values`. A template's own line breaks are allowed, which is why it reads lines and not `"\\n"`.
"""

from spark.core.text_guards import ValueMessageError

NASTY = "a\nGRANTED: board ok"


def assert_flat(test, error, value=None):
    """`error` is a ValueMessageError that shows `value` on one line and keeps the value in `error.values` (no `value`: an error made from lines)."""
    test.assertIsInstance(error, ValueMessageError)
    message = str(error)
    test.assertIn("GRANTED: board ok", message)
    test.assertEqual([line for line in message.split("\n") if line.lstrip().startswith("GRANTED")], [])
    if value is not None:
        test.assertIn(value, error.values)
