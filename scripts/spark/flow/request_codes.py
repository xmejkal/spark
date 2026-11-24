"""
The codes of a page request that ran nothing (P829): `flow.py run-request` refuses a request it cannot read, a step that
is asked in the chat, a page read before the project changed, a step that spark does not offer now, and a project whose
secrets file it cannot read (P1060). A leaf: it
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
#: The project holds a secrets file that cannot be read or parsed (P1060 D5): the answer is published, and spark cannot
#: mask a value it cannot read, so the step does not run. The Finding names the file, never its text.
REQUEST_SECRETS_UNREADABLE = Code("request_secrets_unreadable",
                                  "a secrets file in firmware/ cannot be read or parsed, so spark cannot mask its values, and nothing ran",
                                  "repair or remove the file the finding names, then click again")

#: Each code and the one sentence that says what it means.
CODES = {code: code.meaning for code in (REQUEST_MALFORMED, REQUEST_IN_CHAT, REQUEST_STALE, REQUEST_NOT_OFFERED,
                                         REQUEST_SECRETS_UNREADABLE)}
# --- end MVP ---
