"""
NEXT's words over a tell (P1290): `next_words.next_words` and `tell_of`. Every expectation is a literal, as
tests/test_self_confirmation.py asks. The pickers' cases (f) follow `TheNowSentenceTest` in tests/test_flow.py.

    python3 -m unittest tests.test_next_words
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from spark.flow import next_words  # noqa: E402
from spark.flow.guide import NO_IMAGE_FACT, ImageFact, now_of, now_sentence  # noqa: E402
from spark.flow.phase_readers import Phase  # noqa: E402

FIRMWARE_SAYS = "Ask Claude in the chat to write the firmware for this board. Keep main.py thin, with the code in modules it calls, so the free checks can import them."
SIMULATE_SAYS = "Ask Claude for the scenario command, and run it in your terminal. It uses Wokwi CI minutes."
SCENARIO_FIRST_SAYS = ("No scenario is written yet, so ask Claude to write one first. Then ask for the scenario command, and run it in "
                       "your terminal. It uses Wokwi CI minutes.")
TWO_JOBS_SAYS = ("Two jobs, in any order: wire the breadboard (10 steps, power off), and ask Claude to write the firmware. "
                 "Spark cannot see your wiring. Keep main.py thin, with the code in modules it calls, so the free checks can import them.")
THIN = "Keep main.py thin, with the code in modules it calls, so the free checks can import them."
FIRMWARE_WORDS = "No firmware yet. Paste the line below in Claude Code. " + THIN
SIMULATE_WORDS = ("No simulation tested this firmware yet. Paste the line below in Claude Code. "
                  "You run the scenario in your own terminal. It uses Wokwi CI minutes.")
SCENARIO_FIRST_WORDS = ("No scenario is written yet, so Claude writes one first. Paste the line below in Claude Code. "
                        "You run the scenario in your own terminal. It uses Wokwi CI minutes.")
TWO_JOBS_WORDS = ("Two jobs, in any order: wire the breadboard (10 steps, power off), and get the firmware from Claude. "
                  "Spark cannot see your wiring. Paste the line below in Claude Code. " + THIN)


def a_now(says, chat_offer, steps=None):
    return {"phase": "firmware", "by": ["claude"], "says": says, "offer": None, "chat_offer": chat_offer, "needs": [], "steps": steps}


class NextWordsTest(unittest.TestCase):
    def test_a_sentence_with_a_tell_gets_its_words_from_the_table(self):  # (a), (d)
        for says, offer, words in ((FIRMWARE_SAYS, "write-firmware", FIRMWARE_WORDS), (SIMULATE_SAYS, "run-simulation", SIMULATE_WORDS),
                                   (SCENARIO_FIRST_SAYS, "run-simulation", SCENARIO_FIRST_WORDS)):
            with self.subTest(offer=offer, says=says[:20]):
                self.assertEqual(next_words.next_words(a_now(says, offer)), words)

    def test_with_no_tell_the_whole_sentence_stays(self):  # (b)
        for offer in (None, "needs-drop", "no-such-offer"):
            with self.subTest(offer=offer):
                self.assertEqual(next_words.next_words(a_now(FIRMWARE_SAYS, offer)), FIRMWARE_SAYS)

    def test_the_two_jobs_are_filled_with_the_count_of_steps(self):  # (c)
        self.assertEqual(next_words.next_words(a_now(TWO_JOBS_SAYS, "write-firmware", 10)), TWO_JOBS_WORDS)
        self.assertEqual(next_words.next_words(a_now(TWO_JOBS_SAYS, "write-firmware", 3)), TWO_JOBS_WORDS.replace("10 steps", "3 steps"))

    def test_an_unknown_sentence_under_a_tell_stays_whole(self):
        self.assertEqual(next_words.next_words(a_now("Something else.", "write-firmware")), "Something else.")

    def test_tell_of(self):  # (e)
        self.assertEqual(next_words.tell_of(a_now("x", "look-at-board")), "Look at this project's board with me.")
        self.assertEqual(next_words.tell_of(a_now("x", "run-simulation")), "Help me run the simulation of this project.")
        self.assertEqual(next_words.tell_of(a_now("x", "write-firmware")),
                         "Write the firmware for this project's board, with a thin main that calls modules the free checks can import.")
        for offer in (None, "needs-drop", "no-such-offer"):
            self.assertIsNone(next_words.tell_of(a_now("x", offer)))
        self.assertIsNone(next_words.tell_of({"says": "x"}))


class TheGuidesNowHoldsNoRepeatTest(unittest.TestCase):
    """(f) and (g): for each picker case with a tell, NEXT's words are not the guide's sentence and say no "ask Claude"."""

    def now_for(self, phase, fact, count, written=True):
        sentence = now_sentence(phase, [], fact, count, written)
        return now_of(phase, sentence, [], count)

    def test_each_picker_case_with_a_tell_gives_words_with_no_ask(self):
        firmware = Phase("firmware", "not-started", "?", "Claude", ["said"], [])
        simulate = Phase("simulate", "not-started", "?", "you", ["said"], [])
        for name, now, offer in (("firmware", self.now_for(firmware, NO_IMAGE_FACT, None), "write-firmware"),
                                 ("two jobs", self.now_for(firmware, NO_IMAGE_FACT, 10), "write-firmware"),
                                 ("simulate with a scenario", self.now_for(simulate, NO_IMAGE_FACT, None), "run-simulation"),
                                 ("simulate with none", self.now_for(simulate, NO_IMAGE_FACT, None, False), "run-simulation"),
                                 ("image untested", self.now_for(simulate, ImageFact("image-untested", None), None), "run-simulation")):
            with self.subTest(name=name):
                words = next_words.next_words(now)
                self.assertEqual(now["chat_offer"], offer)
                self.assertNotEqual(words, now["says"])
                self.assertNotIn("ask claude", words.lower())

    def test_the_untested_image_path_says_the_simulate_words(self):  # (g)
        simulate = Phase("simulate", None, "?", "you", ["said"], [])
        now = self.now_for(simulate, ImageFact("image-untested", None), None)
        self.assertEqual((now["says"], now["chat_offer"]), (SIMULATE_SAYS, "run-simulation"))
        self.assertEqual(next_words.next_words(now), SIMULATE_WORDS)


if __name__ == "__main__":
    unittest.main()
