"""Regression coverage for Evennia contribs adopted by Quasar."""

from time import time

from evennia.contrib.rpg.traits import GaugeTrait
from evennia.contrib.game_systems.achievements import get_achievement_progress
from evennia.utils.test_resources import EvenniaTest

from world.character_options import apply_background
from world.character_traits import (
    ability_tree_progress,
    add_ability_experience,
    ensure_skill_traits,
)
from world.resources import apply_damage, ensure_character_resources
from world.achievements import track_quasar_achievement
from commands.default_cmdsets import AccountCmdSet, CharacterCmdSet


class ContribIntegrationTests(EvenniaTest):
    def setUp(self):
        super().setUp()
        self.char1.db.species = "human"
        self.char1.db.active_skill_trees = ["ballistics", "warding"]
        self.char1.db.known_skill_trees = ["ballistics", "warding"]
        self.char1.db.skill_tree_proficiency = {"ballistics": 1, "warding": 1}
        self.char1.db.skill_tree_experience = {"ballistics": 5, "warding": 5}

    def test_traits_back_resources_and_skills(self):
        ensure_character_resources(self.char1)
        ensure_skill_traits(self.char1)

        self.assertIsInstance(self.char1.traits.health, GaugeTrait)
        self.assertEqual(self.char1.traits.health.current, self.char1.db.health_current)
        self.assertEqual(ability_tree_progress(self.char1, "ballistics"), (1, 5))

        add_ability_experience(self.char1, "ballistics", 10)
        self.assertEqual(self.char1.skills.ballistics.current, 15)
        self.assertEqual(self.char1.db.skill_tree_experience["ballistics"], 15)

    def test_resource_changes_write_through_trait_gauge(self):
        ensure_character_resources(self.char1)
        before = int(self.char1.traits.health.current)

        apply_damage(self.char1, 7, message=False)

        self.assertEqual(self.char1.traits.health.current, before - 7)
        self.assertEqual(self.char1.db.health_current, before - 7)

    def test_background_change_removes_stale_miniskill_trait(self):
        apply_background(self.char1, "belt_prospector")
        self.assertIsNotNone(self.char1.skills.get("miniskill_claim_assay"))

        apply_background(self.char1, "political_operator")

        self.assertIsNone(self.char1.skills.get("miniskill_claim_assay"))
        self.assertIsNotNone(self.char1.skills.get("miniskill_coalition_barter"))

    def test_cooldown_handler_reuses_saved_timestamp_storage(self):
        expires = time() + 50
        self.char1.cooldowns.data["sightline"] = expires

        self.assertEqual(self.char1.db.skill_cooldowns["sightline"], expires)
        self.char1.cooldowns.clear()
        self.assertFalse(self.char1.db.skill_cooldowns)

    def test_authored_achievement_tracks_and_announces(self):
        completed = track_quasar_achievement(
            self.char1, category="tutorial", tracking="dawnline_arrival"
        )

        self.assertEqual(completed, ("dawnline_arrival",))
        progress = get_achievement_progress(self.char1, "dawnline_arrival")
        self.assertTrue(progress["completed"])

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
