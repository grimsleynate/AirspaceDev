"""Tests for numbered quest and task journal data."""

from evennia.utils.test_resources import EvenniaTest

from world.journal import build_journal_payload, format_journal


class JournalTests(EvenniaTest):
    def test_tutorial_progress_produces_numbered_tasks(self):
        self.char1.db.tutorial_progress = {"corpse_feeder_defeated": True}

        payload = build_journal_payload(self.char1)

        self.assertEqual(payload["tasks"][0]["number"], 1)
        self.assertEqual(payload["tasks"][0]["id"], "answer-channel")
        self.assertIn("Investigate the emergency channel", format_journal(self.char1, "task"))
        self.assertIn("Task 1", format_journal(self.char1, "task", number=1))

    def test_quests_are_separate_from_tasks(self):
        self.char1.db.tutorial_complete = True
        self.char1.db.quest_log = [{
            "id": "lost-signal",
            "title": "The Lost Signal",
            "summary": "Trace a vanished courier.",
            "detail": "Begin at the orbital exchange.",
        }]

        payload = build_journal_payload(self.char1)

        self.assertEqual(payload["quests"][0]["title"], "The Lost Signal")
        self.assertEqual(payload["tasks"], [])
        self.assertIn("Quest 1", format_journal(self.char1, "quest", number=1))

    def test_invalid_number_explains_how_to_list_entries(self):
        self.char1.db.tutorial_complete = True

        self.assertIn("no active task numbered 3", format_journal(self.char1, "task", number=3))
