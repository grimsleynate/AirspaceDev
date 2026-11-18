"""Integration coverage for inventory and the Evennia containers contrib."""

from unittest.mock import patch

from evennia import create_object
from evennia.contrib.game_systems.containers.containers import CmdContainerGet, CmdPut
from evennia.server.models import ServerConfig
from evennia.utils.test_resources import EvenniaCommandTest, EvenniaTest

from typeclasses.items import (
    CONTAINER_SIZE_CONFIG,
    BasicBackpack,
    EquipableItem,
    PortableItem,
    set_container_sizes_enabled,
)
from typeclasses.components.physical import dimensions_fit, normalized_dimensions


class ContainerIntegrationTests(EvenniaTest):
    def tearDown(self):
        ServerConfig.objects.conf(CONTAINER_SIZE_CONFIG, delete=True)
        super().tearDown()

    def _long_item(self):
        """A rigid item longer than the default backpack's interior."""

        item = create_object(PortableItem, key="long item", location=self.char1)
        item.dimensions_cm = (88.0, 25.0, 7.0)
        return item

    def test_character_direct_inventory_is_limited_to_eight(self):
        for number in range(8):
            create_object(PortableItem, key=f"item {number}", location=self.char1)
        extra = create_object(PortableItem, key="ninth item", location=self.room1)

        self.assertFalse(extra.move_to(self.char1, quiet=True, move_type="get"))
        self.assertEqual(extra.location, self.room1)

    def test_equipped_items_do_not_consume_direct_inventory_slots(self):
        suit = create_object(EquipableItem, key="test armor", location=self.char1)
        self.assertTrue(suit.equip_to(self.char1, quiet=True))
        for number in range(7):
            create_object(PortableItem, key=f"item {number}", location=self.char1)
        eighth_item = create_object(
            PortableItem, key="eighth item", location=self.room1
        )

        self.assertTrue(eighth_item.move_to(self.char1, quiet=True, move_type="get"))
        self.assertEqual(len(self.char1.contents), 9)
        self.assertEqual(len(self.char1.inventory_items()), 8)

    def test_equipped_item_cannot_be_unequipped_into_a_full_inventory(self):
        suit = create_object(EquipableItem, key="test armor", location=self.char1)
        self.assertTrue(suit.equip_to(self.char1, quiet=True))
        for number in range(8):
            create_object(PortableItem, key=f"item {number}", location=self.char1)

        self.assertFalse(suit.unequip_from(self.char1, quiet=True))
        self.assertTrue(suit.is_equipped)

    @patch("world.resources.send_character_resources")
    def test_portable_moves_refresh_inventory_and_room_gui(self, send_resources):
        item = create_object(PortableItem, key="widget", location=self.room1)

        with patch.object(self.room1, "send_room_info") as send_room_info:
            item.move_to(self.char1, quiet=True, move_type="get")

        send_resources.assert_called_with(self.char1, force=True)
        send_room_info.assert_called_once_with()

    def test_backpack_holds_twenty_items(self):
        backpack = create_object(BasicBackpack, key="backpack", location=self.char1)

        self.assertTrue(backpack.components.has("physical_dimensions"))
        self.assertTrue(backpack.components.has("container_storage"))
        self.assertEqual(backpack.dimensions_cm, (50.0, 32.0, 20.0))
        self.assertEqual(backpack.interior_dimensions_cm, (47.0, 29.0, 17.0))
        self.assertEqual(backpack.capacity, 20)
        self.assertTrue(backpack.access(self.char1, "get_from"))
        for number in range(20):
            create_object(PortableItem, key=f"cargo {number}", location=backpack)
        overflow = create_object(PortableItem, key="overflow", location=self.char1)
        self.assertFalse(backpack.at_pre_put_in(self.char1, overflow))

    def test_oversized_item_does_not_fit_backpack_when_sizes_are_on(self):
        set_container_sizes_enabled(True)
        backpack = create_object(BasicBackpack, key="backpack", location=self.char1)
        item = self._long_item()

        self.assertTrue(item.components.has("physical_dimensions"))
        self.assertFalse(backpack.at_pre_put_in(self.char1, item))

    def test_dimension_components_are_searchable_capabilities(self):
        item = create_object(PortableItem, key="widget", location=self.char1)

        self.assertTrue(item.tags.has("physical_dimensions", category="components"))

    def test_legacy_dimensions_migrate_lazily_to_component_storage(self):
        item = create_object(PortableItem, key="legacy item", location=self.char1)
        item.components.remove_by_name("physical_dimensions")
        item.attributes.add("dimensions_cm", (42.0, 12.0, 3.0))

        self.assertEqual(item.dimensions_cm, (42.0, 12.0, 3.0))
        self.assertTrue(item.components.has("physical_dimensions"))

    def test_component_values_survive_evennia_runtime_reinitialization(self):
        backpack = create_object(BasicBackpack, key="backpack", location=self.char1)
        backpack.dimensions_cm = (51.0, 33.0, 21.0)
        backpack.interior_dimensions_cm = (48.0, 30.0, 18.0)
        backpack.capacity = 17

        backpack.at_init()

        self.assertEqual(backpack.dimensions_cm, (51.0, 33.0, 21.0))
        self.assertEqual(backpack.interior_dimensions_cm, (48.0, 30.0, 18.0))
        self.assertEqual(backpack.capacity, 17)
        self.assertTrue(backpack.components.has("physical_dimensions"))
        self.assertTrue(backpack.components.has("container_storage"))

    def test_size_toggle_allows_oversized_item_while_preserving_count_capacity(self):
        set_container_sizes_enabled(False)
        backpack = create_object(BasicBackpack, key="backpack", location=self.char1)
        item = self._long_item()

        self.assertTrue(backpack.at_pre_put_in(self.char1, item))
        for number in range(20):
            create_object(PortableItem, key=f"cargo {number}", location=backpack)
        self.assertFalse(backpack.at_pre_put_in(self.char1, item))


class ContainerCommandIntegrationTests(EvenniaCommandTest):
    def test_contrib_put_and_get_move_an_item_through_a_backpack(self):
        backpack = create_object(BasicBackpack, key="backpack", location=self.char1)
        widget = create_object(PortableItem, key="widget", location=self.char1)

        self.call(CmdPut(), "widget in backpack", msg=None)
        self.assertEqual(widget.location, backpack)
        self.call(CmdContainerGet(), "widget from backpack", msg=None)
        self.assertEqual(widget.location, self.char1)


class PhysicalDimensionUnitTests(EvenniaTest):
    def test_dimension_fit_allows_axis_rotation(self):
        self.assertTrue(dimensions_fit((20.0, 40.0, 10.0), (42.0, 12.0, 22.0)))

    def test_dimension_fit_rejects_oversized_rigid_envelope(self):
        self.assertFalse(dimensions_fit((88.0, 25.0, 7.0), (47.0, 29.0, 17.0)))

    def test_missing_or_invalid_dimensions_remain_backward_compatible(self):
        self.assertIsNone(normalized_dimensions((10.0, -1.0, 2.0)))
        self.assertTrue(dimensions_fit(None, (47.0, 29.0, 17.0)))

    def test_component_rejects_invalid_physical_measurements(self):
        item = create_object(PortableItem, key="widget", location=self.char1)

        with self.assertRaises(ValueError):
            item.dimensions_cm = (10.0, 0.0, 5.0)
