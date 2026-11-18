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
