"""Tests for equipment slot rules."""

from evennia import create_object
from evennia.utils.test_resources import EvenniaTest

from typeclasses.items import EquipableItem


class EquipmentSlotTests(EvenniaTest):
    def _item(self, key, slot):
        item = create_object(EquipableItem, key=key, location=self.char1)
        item.db.equipment_slot = slot
        return item

    def test_one_item_per_slot(self):
        first = self._item("first hat", "head")
        second = self._item("second hat", "head")

        self.assertTrue(first.equip_to(self.char1, quiet=True))
        self.assertFalse(second.equip_to(self.char1, quiet=True))
        self.assertFalse(second.is_equipped)

    def test_equipped_items_cannot_be_dropped(self):
        item = self._item("hat", "head")
        item.equip_to(self.char1, quiet=True)

        self.assertFalse(item.at_pre_drop(self.char1))
        self.assertTrue(item.unequip_from(self.char1, quiet=True))
        self.assertFalse(item.is_equipped)


class EquippedStateRegressionTests(EvenniaTest):
    """Repair plan step 1 (audit P0-1): equipped state must follow the wearer."""

    def test_item_moved_off_its_wearer_stops_counting_as_equipped(self):
        from world.combat import character_combat_stats, equipped_items

        armor = create_object(EquipableItem, key="test armor", location=self.char1)
        armor.db.equipment_slot = "body"
        armor.db.armor = 4
        self.assertTrue(armor.equip_to(self.char1, quiet=True))

        # Any move other than unequip/drop/give, e.g. a theft or admin teleport.
        armor.move_to(self.char2, quiet=True, move_type="teleport")

        self.assertFalse(armor.is_equipped)
        self.assertNotIn(armor, equipped_items(self.char2))
        self.assertEqual(character_combat_stats(self.char2)["armor"], 0)
