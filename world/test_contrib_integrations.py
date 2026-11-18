"""Regression coverage for adopted Evennia contribs."""

from evennia.contrib.rpg.traits import GaugeTrait
from django.test import override_settings
from evennia.utils.test_resources import EvenniaTest

from world.resources import apply_damage, ensure_character_resources
from world.achievements import track_achievement
from commands.default_cmdsets import AccountCmdSet, CharacterCmdSet


class ContribIntegrationTests(EvenniaTest):
    def test_health_is_a_contrib_gauge_trait(self):
        ensure_character_resources(self.char1)

        self.assertIsInstance(self.char1.traits.health, GaugeTrait)
        self.assertEqual(self.char1.traits.health.current, self.char1.db.health_current)

    def test_resource_changes_write_through_trait_gauge(self):
        ensure_character_resources(self.char1)
        before = int(self.char1.traits.health.current)

        apply_damage(self.char1, 7, message=False)

        self.assertEqual(self.char1.traits.health.current, before - 7)
        self.assertEqual(self.char1.db.health_current, before - 7)

    @override_settings(ACHIEVEMENT_CONTRIB_MODULES=[])
    def test_tracking_without_achievement_definitions_is_a_no_op(self):
        self.assertEqual(
            track_achievement(self.char1, category="defeat", tracking="anything"),
            (),
        )

    def test_adopted_commands_are_on_the_correct_global_cmdsets(self):
        character_keys = {
            alias
            for command in CharacterCmdSet(self.char1).commands
            for alias in command._keyaliases
        }
        account_keys = {
            alias
            for command in AccountCmdSet(self.account).commands
            for alias in command._keyaliases
        }

        self.assertIn("achievements", character_keys)
        self.assertNotIn("trade", character_keys)
        self.assertTrue({"mail", "bug", "idea", "report"}.issubset(account_keys))
