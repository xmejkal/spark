"""
P811 (#1153): one board reader, board_read.py, shared by the gate and the status. Its query asks what the limits and
the status need and nothing more — each field by its name, 100 items and 10 labels a page, the parent story with the
item — so a page costs 1 GraphQL point (a dry run, 2026-11-13), not 101 as `gh project item-list` asked. The numbers
and the field names are written out here (W2).
"""

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import board_read  # noqa: E402

NODE = {"content": {"number": 7, "title": "P7 — x", "body": "b", "repository": {"name": "spark"},
                    "labels": {"nodes": [{"name": "task"}]}, "parent": {"number": 3, "closed": False}},
        "status": {"name": "Build", "updatedAt": "2026-11-13T10:00:00Z"}, "slice": {"name": "10 The store"},
        "waitingOn": {"name": "the PO"}, "waitingSince": {"date": "2026-11-12"}}


def project(*nodes, held=None):
    return {"id": "P", "items": {"totalCount": len(nodes) if held is None else held, "nodes": list(nodes)},
            "statusUpdates": {"nodes": []}}


class TheReaderTest(unittest.TestCase):
    def test_the_query_asks_four_fields_by_name_and_no_list_of_field_values(self):
        self.assertEqual(re.findall(r"first:(\d+)", board_read.QUERY), ["100", "10", "20"])
        self.assertNotIn("fieldValues(", board_read.QUERY)
        for field in ('status:fieldValueByName(name:"Status")', 'slice:fieldValueByName(name:"Slice")',
                      'waitingOn:fieldValueByName(name:"Waiting on")', 'waitingSince:fieldValueByName(name:"Waiting since")',
                      "parent{number closed}", "repository{name}", "rateLimit{cost remaining limit}"):
            with self.subTest(field=field):
                self.assertIn(field, board_read.QUERY)

    def test_a_full_node_is_a_card_with_every_key(self):
        self.assertEqual(board_read.to_items(project(NODE)), [
            {"labels": ["task"], "parent": 3, "status": "Build", "slice": "10 The store", "waiting on": "the PO",
             "waiting since": "2026-11-12", "status_changed": "2026-11-13T10:00:00Z",
             "content": {"number": 7, "title": "P7 — x", "body": "b", "repo": "spark"}}])

    def test_a_draft_is_no_card_and_a_board_of_drafts_alone_is_short(self):
        draft = {"content": {}, "status": {"name": "Build"}}
        self.assertEqual(len(board_read.to_items(project(NODE, draft))), 1)
        self.assertIsNone(board_read.unread("it", project(NODE, draft)))
        self.assertEqual(board_read.unread("it", project(draft, draft)), "it holds 2 items and none of them was read as an issue")
        self.assertIsNone(board_read.unread("it", project()))

    def test_a_board_read_short_says_both_numbers(self):
        self.assertEqual(board_read.unread("the spark board", project(NODE, held=130)),
                         "the spark board holds 130 items, 1 were read")

    def test_each_page_s_cost_is_kept_and_a_failure_is_one_error_with_its_cause(self):
        def ask(*args):
            return {"data": {"rateLimit": {"cost": 1, "remaining": 9, "limit": 5000},
                             "user": {"projectV2": dict(project(NODE), items=dict(project(NODE)["items"],
                                                        pageInfo={"hasNextPage": False, "endCursor": None}))}}}
        spent = []
        board_read.read_board(2, ask, spent)
        self.assertEqual(spent, [{"cost": 1, "remaining": 9, "limit": 5000}])

        def null(*args):
            return {"data": {"user": {"projectV2": None}}}
        with self.assertRaisesRegex(board_read.Unreadable, "^TypeError$"):
            board_read.read_board(2, null)

        def refused(*args):
            raise RuntimeError("HTTP 502: Bad Gateway")
        with self.assertRaisesRegex(board_read.Unreadable, "^HTTP 502: Bad Gateway$"):
            board_read.projects(refused)


if __name__ == "__main__":
    unittest.main()
