"""
The codes of a page request that ran nothing (P829): `flow.py run-request` refuses a request it cannot read, a step that
is asked in the chat, a step that spark does not offer now, and a page read before the project changed. A leaf: it
imports only the core's Code. Each is a Code with its meaning and its fix (P853, P935).
"""

from spark.core.codes import Code

# --- MVP ---
#: The request file is missing or is no JSON object, or its id, key or seen cannot be read.
REQUEST_MALFORMED = Code("request_malformed",
                         "the request file is missing or is no JSON object, or its id, key or seen cannot be read, so nothing ran",
                         "reload the page and click again")
#: The request names a step that is asked in the chat, never from the page: a need's drop.
REQUEST_IN_CHAT = Code("request_in_chat", "the request names a step that is asked in the chat, never from the page, so nothing ran",
                       "tell Claude in the chat, for example: drop the light need")
#: The request names a key that is not among the offers spark reads now, or a kind the page never runs.
REQUEST_NOT_OFFERED = Code("request_not_offered", "the request names a step that spark does not offer now, so nothing ran",
                           "reload the page: it shows the steps spark offers now")
#: The page's fingerprint is not the project's now: the project changed after the page was read.
REQUEST_STALE = Code("request_stale", "the project changed after the page was read, so nothing ran",
                     "reload the page and click again")

#: Each code and the one sentence that says what it means.
CODES = {code: code.meaning for code in (REQUEST_MALFORMED, REQUEST_IN_CHAT, REQUEST_NOT_OFFERED, REQUEST_STALE)}
# --- end MVP ---
