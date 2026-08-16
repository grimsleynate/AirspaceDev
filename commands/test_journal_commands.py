"""Parser-facing tests for quest and task commands."""

from evennia.utils.test_resources import EvenniaCommandTest

from commands.journal_commands import CmdQuestLog, CmdTaskLog


class JournalCommandTests(EvenniaCommandTest):
    def test_task_lists_and_opens_numbered_tutorial_tasks(self):
        self.char1.db.tutorial_progress = {"corpse_feeder_defeated": True}

        listing = self.call(CmdTaskLog(), "", msg=None)
        detail = self.call(CmdTaskLog(), "1", msg=None)

        self.assertIn("Active Tasks", listing)
        self.assertIn("Investigate the emergency channel", listing)
        self.assertIn("Task 1", detail)
        self.assertIn("ANSWER", detail)

    def test_quest_reads_only_quest_log(self):
        self.char1.db.tutorial_complete = True
        self.char1.db.quest_log = [{
            "title": "The Lost Signal",
            "summary": "Trace a vanished courier.",
            "detail": "Begin at the orbital exchange.",
        }]

        listing = self.call(CmdQuestLog(), "", msg=None)

        self.assertIn("Active Quests", listing)
        self.assertIn("The Lost Signal", listing)

    def test_aliases_are_the_requested_short_forms(self):
        self.assertIn("q", CmdQuestLog.aliases)
        self.assertIn("t", CmdTaskLog.aliases)
