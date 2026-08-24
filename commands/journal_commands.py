"""Player commands for numbered quest and task journals."""

from commands.command import Command
from world.journal import format_journal, send_journal_sync


class _JournalCommand(Command):
    journal_kind = "task"
    locks = "cmd:all()"
    help_category = "Journal"

    def func(self):
        raw = self.args.strip()
        number = None
        if raw:
            try:
                number = int(raw)
            except ValueError:
                self.caller.msg(
                    f"Usage: |w{self.key}|n or |w{self.key} <number>|n"
                )
                return
        self.caller.msg(format_journal(self.caller, self.journal_kind, number=number))
        send_journal_sync(self.caller)
        from world.opening_tutorial import record_tutorial_proof

        record_tutorial_proof(self.caller, "journal_checked")


class CmdQuestLog(_JournalCommand):
    """List active quests or inspect one numbered quest."""

    key = "quest"
    aliases = ["q"]
    journal_kind = "quest"


class CmdTaskLog(_JournalCommand):
    """List active tasks or inspect one numbered task."""

    key = "task"
    aliases = ["t"]
    journal_kind = "task"
