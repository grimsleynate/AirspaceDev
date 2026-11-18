"""Integration tests for the tunable combat foundation."""

from unittest.mock import patch

from evennia import create_object
from evennia.utils.test_resources import EvenniaTest

from typeclasses.items import EquipableItem, Weapon
from typeclasses.npcs import HostileNPC
from world.combat import (
    ATTACK_DESCRIPTIONS,
    MISS_DESCRIPTIONS,
    AttackCategory,
    award_experience,
    character_combat_stats,
    combat_payload,
    engage,
    experience_for_level,
    progression_payload,
    tick_character_combat,
    tick_hostile,
)
from world.resources import ensure_character_resources


class CombatFoundationTests(EvenniaTest):
    def setUp(self):
        super().setUp()
        self.char1.location = self.room1
        ensure_character_resources(self.char1)
        self.weapon = create_object(Weapon, key="test weapon", location=self.char1)
        self.weapon.equip_to(self.char1, quiet=True)
        self.hostile = create_object(
            HostileNPC, key="test hostile", location=self.room1, home=self.room1
        )

    def test_every_attack_category_has_hit_and_miss_narration(self):
        self.assertEqual(set(ATTACK_DESCRIPTIONS), set(AttackCategory))
        self.assertEqual(set(MISS_DESCRIPTIONS), set(AttackCategory))

    def test_equipped_weapon_and_gear_feed_derived_stats(self):
        armor = create_object(EquipableItem, key="test armor", location=self.char1)
        armor.db.equipment_slot = "body"
        armor.db.armor = 4
        armor.db.health_bonus = 15
        armor.equip_to(self.char1, quiet=True)

        stats = character_combat_stats(self.char1)

        self.assertEqual(stats["weapon_name"], "test weapon")
        self.assertEqual(stats["attack_category"], AttackCategory.WEAPON.value)
        self.assertEqual(stats["armor"], 4)
        self.assertEqual(stats["max_health"], 115)

    def test_unarmed_stats_without_a_weapon(self):
        self.weapon.unequip_from(self.char1, quiet=True)

        stats = character_combat_stats(self.char1)

        self.assertEqual(stats["weapon_name"], "unarmed strike")
        self.assertEqual(stats["attack_category"], AttackCategory.UNARMED.value)

    def test_combat_payload_reports_current_target(self):
        engage(self.char1, self.hostile, now=100.0)

        payload = combat_payload(self.char1)

        self.assertEqual(payload["target"]["id"], self.hostile.id)
        self.assertEqual(payload["weapon"], "test weapon")

    @patch("world.combat.randint", side_effect=[1, 6, 100])
    def test_combat_tick_pushes_basic_attack_after_weapon_recovery(self, _randint):
        engage(self.char1, self.hostile, now=100.0)
        self.char1.db.combat_recovery_until = 100.0
        before = int(self.hostile.db.health_current)

        result = tick_character_combat(self.char1, now=100.0)

        self.assertTrue(result["hit"])
        self.assertLess(self.hostile.db.health_current, before)
        self.assertEqual(self.char1.db.combat_recovery_until, 102.0)

    @patch("world.combat.randint", side_effect=[1, 6, 100])
    def test_hostile_telegraphs_before_dealing_damage(self, _randint):
        engage(self.char1, self.hostile, now=100.0)
        before = int(self.char1.db.health_current)

        tick_hostile(self.hostile, now=101.0)
        self.assertIsNotNone(self.hostile.db.combat_intent)
        self.assertEqual(self.char1.db.health_current, before)

        tick_hostile(self.hostile, now=104.0)
        self.assertLess(self.char1.db.health_current, before)
        self.assertIsNone(self.hostile.db.combat_intent)

    def test_experience_thresholds_level_and_expand_health(self):
        self.assertEqual(experience_for_level(2), 100)
        self.assertEqual(experience_for_level(3), 300)
        self.char1.db.level = 1
        self.char1.db.experience = 0
        before_max = int(self.char1.db.health_max)

        levels = award_experience(self.char1, 100, source="test target")
        progress = progression_payload(self.char1)

        self.assertEqual(levels, 1)
        self.assertEqual(progress["level"], 2)
        self.assertEqual(progress["level_experience"], 0)
        self.assertGreater(self.char1.db.health_max, before_max)
        self.assertEqual(self.char1.db.health_current, self.char1.db.health_max)

    @patch("world.combat.randint", side_effect=[1, 6, 100])
    def test_defeat_disengages_the_hostile_that_landed_the_kill(self, _randint):
        """Repair plan step 1 (audit P0-3): defeat resets the real attacker."""

        striker = create_object(
            HostileNPC, key="second hostile", location=self.room1, home=self.room1
        )
        # Both hostiles target char1, but char1 remembers only self.hostile.
        engage(self.char1, striker, now=100.0)
        engage(self.char1, self.hostile, now=100.0)
        self.assertEqual(self.char1.db.combat_target_id, self.hostile.id)
        self.assertEqual(striker.db.combat_target_id, self.char1.id)
        self.char1.apply_damage(int(self.char1.db.health_current) - 1, message=False)

        tick_hostile(striker, now=101.0)  # telegraph
        tick_hostile(striker, now=104.0)  # lethal hit -> handle_character_defeat

        self.assertEqual(self.char1.db.health_current, self.char1.db.health_max)
        self.assertIsNone(striker.db.combat_target_id)
        self.assertIsNone(striker.db.combat_intent)
        self.assertIsNone(self.hostile.db.combat_target_id)

    def test_respawn_deadline_reconciles_after_downtime(self):
        """Scheduling convention example: a durable deadline is a timestamp
        that the next check reconciles, even if the server slept through it."""

        from world.combat import defeat_hostile

        defeat_hostile(self.hostile)
        self.assertTrue(self.hostile.db.is_defeated)
        due = float(self.hostile.db.respawn_at)

        tick_hostile(self.hostile, now=due - 1)
        self.assertTrue(self.hostile.db.is_defeated)

        # Simulate a restart long after the deadline: no timer was kept alive.
        tick_hostile(self.hostile, now=due + 3600)
        self.assertFalse(self.hostile.db.is_defeated)


class HostilityHookTests(EvenniaTest):
    """Repair plan step 9: hostility is a hook, defaulting to today's flag."""

    def setUp(self):
        super().setUp()
        self.char1.location = self.room1
        ensure_character_resources(self.char1)
        self.hostile = create_object(HostileNPC, key="test hostile", location=self.room1)

    def test_defaults_match_the_old_flag(self):
        from typeclasses.npcs import FriendlyNPC

        friendly = create_object(FriendlyNPC, key="guide", location=self.room1)

        self.assertTrue(self.hostile.is_hostile_to(self.char1))
        self.assertTrue(self.hostile.can_be_attacked_by(self.char1))
        self.assertFalse(friendly.is_hostile_to(self.char1))
        self.assertFalse(friendly.can_be_attacked_by(self.char1))
        self.assertFalse(self.char1.can_be_attacked_by(self.char2))  # no PvP yet

    def test_combat_and_room_payloads_ask_the_hook(self):
        from world.combat import player_attack

        # A pacified hostile: same class, but no longer an enemy of char1.
        with patch.object(self.hostile, "is_hostile_to", return_value=False):
            self.assertIsNone(player_attack(self.char1, self.hostile, now=100.0))
            npcs = self.room1.get_room_info(self.char1)["npcs"]

        self.assertEqual(npcs, [{"id": self.hostile.id, "name": "test hostile", "hostile": False}])
        self.assertIsNone(self.char1.db.combat_target_id)
