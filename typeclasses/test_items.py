"""Tests for equipment body-plan restrictions."""

from evennia import create_object
from evennia.utils.test_resources import EvenniaTest

from typeclasses.items import StandardLegwear, UtilityPressureSuit


class EquipmentBodyPlanTests(EvenniaTest):
    def setUp(self):
        super().setUp()
        self.char1.db.species = "synth"
        self.char1.db.locomotion_chassis = "wheel"

    def test_wheel_synth_cannot_equip_standard_pants(self):
        pants = create_object(StandardLegwear, key="utility pants", location=self.char1)

        self.assertFalse(pants.equip_to(self.char1, quiet=True))
        self.assertFalse(pants.is_equipped)

    def test_wheel_synth_can_equip_skin_tight_pressure_suit(self):
        suit = create_object(UtilityPressureSuit, key="pressure suit", location=self.char1)

        self.assertTrue(suit.equip_to(self.char1, quiet=True))
        self.assertTrue(suit.is_equipped)

    def test_bipedal_upgrade_unlocks_standard_pants(self):
        pants = create_object(StandardLegwear, key="utility pants", location=self.char1)
        self.char1.db.locomotion_chassis = "bipedal"

        self.assertTrue(pants.equip_to(self.char1, quiet=True))
        self.assertTrue(pants.is_equipped)
