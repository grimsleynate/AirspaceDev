"""Tests for character health, standard vitals, and the HUD snapshot."""

from evennia import create_object
from evennia.utils.test_resources import EvenniaTest

from typeclasses.items import BasicBackpack, EquipableItem, PortableItem
from world.resources import (
    RESOURCE_PROTOCOL_REVISION,
    apply_damage,
    build_resource_payload,
    build_standard_vitals,
    restore_health,
)


class CharacterResourceTests(EvenniaTest):
    def test_standard_gmcp_vitals_report_health_and_progression(self):
        vitals, labels = build_standard_vitals(self.char1)

        self.assertEqual(vitals["hp"], vitals["maxhp"])
        self.assertEqual(vitals["level"], 1)
        self.assertEqual(labels["hp"], "Health")
        self.assertEqual(set(vitals) - {"maxhp"}, set(labels))

    def test_damage_and_restore_write_through_health_gauge(self):
        before = int(self.char1.db.health_current)

        apply_damage(self.char1, 7, message=False)
        self.assertEqual(self.char1.traits.health.current, before - 7)
        self.assertEqual(self.char1.db.health_current, before - 7)

        restore_health(self.char1)
        self.assertEqual(self.char1.db.health_current, before)

    def test_character_snapshot_describes_inventory_equipment_and_containers(self):
        backpack = create_object(BasicBackpack, key="backpack", location=self.char1)
        create_object(PortableItem, key="widget", location=backpack)
        armor = create_object(EquipableItem, key="test armor", location=self.char1)
        armor.equip_to(self.char1, quiet=True)

        payload = build_resource_payload(self.char1)

        self.assertEqual(payload["revision"], RESOURCE_PROTOCOL_REVISION)
        self.assertEqual(payload["inventory"][0]["name"], "backpack")
        self.assertTrue(payload["inventory"][0]["container"])
        self.assertEqual(payload["inventory"][0]["contents_count"], 1)
        self.assertEqual(payload["equipment"][0]["name"], "test armor")


class HealthAuthorityRegressionTests(EvenniaTest):
    """Repair plan step 1 (audit P0-2): the Health trait is the authority."""

    def test_health_set_on_the_trait_survives_a_payload_rebuild(self):
        self.char1.traits.health.current = 40

        payload = build_resource_payload(self.char1)

        self.assertEqual(self.char1.traits.health.current, 40)
        self.assertEqual(payload["health"]["current"], 40)

    def test_one_take_damage_serves_characters_and_hostiles(self):
        from typeclasses.npcs import HostileNPC
        from world.health import health_of, take_damage

        hostile = create_object(HostileNPC, key="test hostile", location=self.room1)
        self.assertEqual(health_of(hostile), (55, 55))

        self.assertEqual(take_damage(hostile, 10, source=self.char1), 10)
        self.assertEqual(take_damage(self.char1, 10, source=hostile, message=False), 10)

        self.assertEqual(health_of(hostile)[0], 45)
        self.assertEqual(hostile.traits.health.current, 45)
        self.assertEqual(self.char1.traits.health.current, health_of(self.char1)[1] - 10)
