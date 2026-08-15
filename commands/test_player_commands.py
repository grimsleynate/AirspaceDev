"""Tests for Quasar's player-facing commands."""

from evennia.utils.test_resources import EvenniaCommandTest

from .player_commands import CmdMap


class MapCommandTests(EvenniaCommandTest):
    def test_map_on_is_case_insensitive(self):
        self.call(CmdMap(), "ON", "ASCII map enabled.")
        self.assertTrue(self.char1.db.ascii_map_enabled)

    def test_map_off_is_case_insensitive(self):
        self.call(CmdMap(), "oFf", "ASCII map disabled.")
        self.assertFalse(self.char1.db.ascii_map_enabled)

    def test_map_without_argument_displays_current_map(self):
        result = self.call(CmdMap(), "", msg=None)
        self.assertIn("[@]", result)

    def test_map_rejects_unknown_option(self):
        self.call(CmdMap(), "sometimes", "Usage: map, map on, map off, or map reset")

    def test_map_reset_requires_confirmation(self):
        self.call(
            CmdMap(),
            "reset",
            "This will permanently forget this character's explored map. Use map reset confirm to continue.",
        )
