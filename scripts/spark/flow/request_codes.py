"""
The codes of a page request that ran nothing (P829): `flow.py run-request` refuses a request it cannot read, a step that
is asked in the chat, a page read before the project changed, and a step that spark does not offer now. A leaf: it
imports only the core's Code. Each is a Code with its meaning, which is also the sentence of the refusal, and its fix
(P853, P935). A fix that a new page serves starts with writing the page again: only the build writes it by itself.
"""

from spark.core.codes import Code

# --- MVP ---
#: The request file is missing, is no regular file (a folder), is no JSON object, holds an id, key or seen that cannot
#: be read, or cannot be deleted. Claude writes the file, so the fix starts there.
REQUEST_MALFORMED = Code("request_malformed",
                         "the request file is missing, is no regular file or no JSON object, holds an id, key or seen that cannot be "
                         "read, or could not be deleted, so nothing ran",
                         "write the page's request to .spark/page-request.json as the page sent it. If it was written that way, ask "
                         "the person to click again")
#: The request names a step that is asked in the chat, never from the page: a need's drop.
REQUEST_IN_CHAT = Code("request_in_chat", "the request names a step that is asked in the chat, never from the page, so nothing ran",
                       "tell Claude in the chat, for example: drop the light need")
#: The page's fingerprint is not the project's now: the project changed after the page was read.
REQUEST_STALE = Code("request_stale", "the project changed after the page was read, so nothing ran",
                     "write the page again with flow.py page, then click again")
#: The request names a key that is not among the offers spark reads now, or a kind the page never runs.
REQUEST_NOT_OFFERED = Code("request_not_offered", "the request names a step that spark does not offer now, so nothing ran",
                           "write the page again with flow.py page, then click again: the page shows the steps spark offers now")

#: Each code and the one sentence that says what it means.
CODES = {code: code.meaning for code in (REQUEST_MALFORMED, REQUEST_IN_CHAT, REQUEST_STALE, REQUEST_NOT_OFFERED)}
# --- end MVP ---
