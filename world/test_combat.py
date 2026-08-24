"""Integration tests for Quasar's tunable combat vertical slice."""

from unittest.mock import patch

from evennia import create_object
from evennia.utils.test_resources import EvenniaTest

from typeclasses.items import ensure_starter_combat_gear, find_starter_combat_gear
from typeclasses.npcs import TrainingDrone
from world.combat import (
    ATTACK_DESCRIPTIONS,
    AttackCategory,
    award_experience,
    character_combat_stats,
    combat_payload,
    engage,
    experience_for_level,
    progression_payload,
    tick_hostile,
    tick_character_combat,
    use_active_skill,
)
from world.resources import ensure_character_resources


class CombatFoundationTests(EvenniaTest):
    def setUp(self):
        super().setUp()
        self.char1.location = self.room1
        self.char1.db.species = "human"
        self.char1.db.career = "vanguard"
        self.char1.db.specialization = "marine"
        ensure_starter_combat_gear(self.char1)
        ensure_character_resources(self.char1)
        self.drone = create_object(
            TrainingDrone,
            key="training drone",
            aliases=["drone"],
            location=self.room1,
            home=self.room1,
        )

    def test_starter_kit_is_idempotent_and_equips_one_weapon(self):
        first = ensure_starter_combat_gear(self.char1)
        second = ensure_starter_combat_gear(self.char1)

        self.assertEqual(set(first), {"arc_cutter", "sidearm", "pressure_suit", "visor"})
        self.assertEqual(first, second)
        self.assertEqual(len(find_starter_combat_gear(self.char1)), 4)
        self.assertEqual(
            len([item for item in first.values() if getattr(item, "is_weapon", False) and item.is_equipped]),
            1,
        )

    def test_equipment_and_marine_passive_feed_derived_stats(self):
        stats = character_combat_stats(self.char1)

        self.assertEqual(stats["weapon_name"], "compact arc cutter")
        self.assertEqual(stats["armor"], 6)
        self.assertEqual(stats["max_health"], 125)
        self.assertEqual(stats["accuracy"], 7)
        self.assertEqual(stats["attack_category"], AttackCategory.MELEE_ENERGY.value)

    def test_current_attack_categories_each_have_eight_basic_descriptions(self):
        self.assertEqual(set(ATTACK_DESCRIPTIONS), set(AttackCategory))
        self.assertTrue(all(len(descriptions) == 8 for descriptions in ATTACK_DESCRIPTIONS.values()))

    def test_each_specialization_has_a_distinct_passive_effect(self):
        self.char1.db.specialization = "scout"
        gear = ensure_starter_combat_gear(self.char1)
        gear["arc_cutter"].unequip_from(self.char1, quiet=True)
        gear["sidearm"].equip_to(self.char1, quiet=True)
        scout = character_combat_stats(self.char1)

        self.char1.db.career = "technician"
        self.char1.db.specialization = "engineer"
        engineer = character_combat_stats(self.char1)

        self.char1.db.specialization = "systems_operator"
        systems = character_combat_stats(self.char1)

        self.assertEqual(scout["accuracy"], 21)
        self.assertEqual(scout["crit_chance"], 10)
        self.assertGreater(engineer["damage_min"], scout["damage_min"])
        self.assertGreater(systems["evasion"], engineer["evasion"])

    def test_oruun_natural_weapon_is_a_bounded_disarmed_bonus(self):
        for item in find_starter_combat_gear(self.char1).values():
            if getattr(item, "is_weapon", False):
                item.unequip_from(self.char1, quiet=True)
        self.char1.db.career = None
        self.char1.db.specialization = None
        self.char1.db.species_benefit = None
        ordinary = character_combat_stats(self.char1)
        self.char1.db.species_benefit = "raking_bite"
        oruun = character_combat_stats(self.char1)
        self.assertEqual(oruun["damage_min"], ordinary["damage_min"] + 1)
        self.assertEqual(oruun["damage_max"], ordinary["damage_max"] + 1)

    def test_combat_payload_exposes_active_skill_for_client_hotbar(self):
        payload = combat_payload(self.char1)

        self.assertEqual(payload["active_skill"]["name"], "Breach Strike")
        self.assertEqual(payload["active_skill"]["command"], "cast breach strike")

    @patch("world.combat.randint", side_effect=[1, 12, 100])
    def test_active_attack_damages_target_spends_resource_and_sets_cooldown(self, _randint):
        self.char1.db.career = "technician"
        self.char1.db.specialization = "engineer"
        self.char1.db.primary_resource_current = 100

        self.assertFalse(self.drone.db.aggressive)
        self.assertIsNone(self.char1.db.combat_target_id)
        result = use_active_skill(self.char1, "overcharge", self.drone, now=100.0)

        self.assertTrue(result["hit"])
        self.assertLess(self.drone.db.health_current, self.drone.db.health_max)
        self.assertEqual(self.char1.db.primary_resource_current, 70)
        self.assertEqual(self.char1.db.combat_target_id, self.drone.id)
        self.assertEqual(self.char1.db.skill_cooldowns["overcharge"], 105.0)

    @patch("world.combat.randint", side_effect=[1, 8, 100])
    def test_systems_disrupt_cancels_a_telegraphed_attack(self, _randint):
        self.char1.db.career = "technician"
        self.char1.db.specialization = "systems_operator"
        gear = ensure_starter_combat_gear(self.char1)
        gear["arc_cutter"].unequip_from(self.char1, quiet=True)
        gear["sidearm"].equip_to(self.char1, quiet=True)
        self.drone.db.combat_intent = {"name": "shock", "resolves_at": 101.0}

        result = use_active_skill(self.char1, "disrupt", self.drone, now=100.0)

        self.assertTrue(result["hit"])
        self.assertIsNone(self.drone.db.combat_intent)
        self.assertEqual(self.drone.db.next_attack_at, 103.0)

    @patch("world.combat.randint", side_effect=[1, 12, 100])
    def test_manual_cast_preempts_basic_attack_recovery(self, _randint):
        self.char1.db.career = "technician"
        self.char1.db.specialization = "engineer"
        self.char1.db.combat_recovery_until = 999.0

        result = use_active_skill(self.char1, "overcharge", self.drone, now=100.0)

        self.assertTrue(result["hit"])
        self.assertEqual(self.char1.db.combat_recovery_until, 102.1)

    @patch("world.combat.randint", side_effect=[1, 12, 100])
    def test_combat_tick_pushes_basic_attack_after_weapon_recovery(self, _randint):
        engage(self.char1, self.drone, now=100.0)
        self.char1.db.combat_recovery_until = 100.0
        before = int(self.drone.db.health_current)

        result = tick_character_combat(self.char1, now=100.0)

        self.assertTrue(result["hit"])
        self.assertLess(self.drone.db.health_current, before)
        self.assertEqual(self.char1.db.combat_recovery_until, 102.0)

    @patch("world.combat.randint", side_effect=[1, 6, 100])
    def test_hostile_telegraphs_before_dealing_damage(self, _randint):
        engage(self.char1, self.drone, now=100.0)
        before = int(self.char1.db.health_current)

        tick_hostile(self.drone, now=101.0)
        self.assertIsNotNone(self.drone.db.combat_intent)
        self.assertEqual(self.char1.db.health_current, before)

        tick_hostile(self.drone, now=104.0)
        self.assertLess(self.char1.db.health_current, before)
        self.assertIsNone(self.drone.db.combat_intent)

    def test_experience_thresholds_level_and_expand_resources(self):
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
