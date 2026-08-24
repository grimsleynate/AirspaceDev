"""Tests for Quasar's vitals, career resources, and oxygen survival."""

from evennia import create_object
from evennia.utils.test_resources import EvenniaTest

from typeclasses.items import (
    BasicBackpack,
    PortableItem,
    UtilityPressureSuit,
    ensure_starter_oxygen_tank,
    find_starter_oxygen_tank,
)
from world.resources import (
    build_resource_payload,
    build_standard_vitals,
    locomotion_chassis,
    primary_resource_kind,
    tick_character_environment,
)


class CharacterResourceTests(EvenniaTest):
    def setUp(self):
        super().setUp()
        self.char1.db.species = "human"
        self.char1.db.career = "technician"
        self.char1.db.specialization = "engineer"

    def test_organic_gets_exactly_one_equipped_starter_tank(self):
        first = ensure_starter_oxygen_tank(self.char1)
        second = ensure_starter_oxygen_tank(self.char1)

        self.assertEqual(first, second)
        self.assertEqual(first.location, self.char1)
        self.assertTrue(first.is_equipped)
        self.assertEqual(first.equipment_slot, "life_support")

    def test_synth_gets_no_starter_tank_and_removes_an_automatic_one(self):
        ensure_starter_oxygen_tank(self.char1)
        self.char1.db.species = "synth"

        self.assertIsNone(ensure_starter_oxygen_tank(self.char1))
        self.assertIsNone(find_starter_oxygen_tank(self.char1))

    def test_primary_resource_follows_career_or_explicit_future_override(self):
        self.assertEqual(primary_resource_kind(self.char1), "tech")
        self.char1.db.career = "vanguard"
        self.char1.db.specialization = "marine"
        self.assertEqual(primary_resource_kind(self.char1), "skill")
        self.char1.db.resource_kind = "acuity"
        self.assertEqual(primary_resource_kind(self.char1), "acuity")

    def test_vacuum_consumes_equipped_oxygen_but_breathable_air_does_not(self):
        tank = ensure_starter_oxygen_tank(self.char1)
        tank.db.oxygen_remaining = 100
        self.char1.location = self.room1
        self.room1.db.atmosphere = "vacuum"

        tick_character_environment(self.char1, elapsed=5)
        self.assertEqual(tank.db.oxygen_remaining, 95)

        self.room1.db.atmosphere = "breathable"
        tick_character_environment(self.char1, elapsed=5)
        self.assertEqual(tank.db.oxygen_remaining, 95)

    def test_organic_without_oxygen_takes_damage_after_grace_period(self):
        self.char1.location = self.room1
        self.room1.db.atmosphere = "vacuum"
        self.char1.db.health_current = 100
        self.char1.db.health_max = 100

        tick_character_environment(self.char1, elapsed=5)
        self.assertEqual(self.char1.db.health_current, 100)
        tick_character_environment(self.char1, elapsed=5)
        self.assertEqual(self.char1.db.health_current, 95)

    def test_synth_ignores_vacuum_and_has_no_oxygen_resource(self):
        self.char1.db.species = "synth"
        self.char1.attributes.remove("locomotion_chassis")
        self.char1.location = self.room1
        self.room1.db.atmosphere = "vacuum"
        self.char1.db.health_current = 100

        tick_character_environment(self.char1, elapsed=30)
        payload = build_resource_payload(self.char1)

        self.assertEqual(self.char1.db.health_current, 100)
        self.assertIsNone(payload["oxygen"])
        self.assertEqual(payload["character"]["locomotion_chassis"], "wheel")
        self.assertIsNone(payload["character"]["gender"])

    def test_synth_defaults_to_wheel_but_can_later_install_legs(self):
        self.char1.db.species = "synth"
        self.char1.attributes.remove("locomotion_chassis")

        self.assertEqual(locomotion_chassis(self.char1), "wheel")
        self.char1.db.locomotion_chassis = "bipedal"
        self.assertEqual(locomotion_chassis(self.char1), "bipedal")

    def test_standard_gmcp_includes_organic_oxygen_but_omits_it_for_synths(self):
        ensure_starter_oxygen_tank(self.char1)
        organic_vitals, organic_labels = build_standard_vitals(self.char1)
        self.assertIn("oxygen", organic_vitals)
        self.assertEqual(organic_labels["tech"], "Tech Points")

        self.char1.db.species = "synth"
        synth_vitals, synth_labels = build_standard_vitals(self.char1)
        self.assertNotIn("oxygen", synth_vitals)
        self.assertNotIn("oxygen", synth_labels)

    def test_character_snapshot_describes_inventory_equipment_and_containers(self):
        backpack = create_object(BasicBackpack, key="backpack", location=self.char1)
        create_object(PortableItem, key="widget", location=backpack)
        suit = create_object(
            UtilityPressureSuit, key="pressure suit", location=self.char1
        )
        suit.equip_to(self.char1, quiet=True)

        payload = build_resource_payload(self.char1)

        self.assertEqual(payload["revision"], 6)
        self.assertEqual(payload["inventory"][0]["name"], "backpack")
        self.assertTrue(payload["inventory"][0]["container"])
        self.assertEqual(payload["inventory"][0]["contents_count"], 1)
        self.assertEqual(payload["equipment"][0]["name"], "pressure suit")

    def test_new_chargen_identity_fields_are_scoped_into_hud_payload(self):
        self.char1.db.background = "heimdall_rigger"
        self.char1.db.active_skill_trees = ["machinistry", "warding"]

        payload = build_resource_payload(self.char1)

        self.assertEqual(payload["character"]["background"], "Heimdall Rigger")
        self.assertEqual(
            payload["character"]["active_skill_trees"],
            ["Machinistry", "Warding"],
        )
