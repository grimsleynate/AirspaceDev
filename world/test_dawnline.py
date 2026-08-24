"""Tests for the walkable Dawnline opening district."""

from evennia.utils.test_resources import EvenniaTest

from typeclasses.opening_tutorial import BoundPorter
from world.dawnline import (
    ROOMS, ensure_bound_porter, ensure_dawnline, ensure_origin_possessions,
    ensure_personal_room,
)


class DawnlineTests(EvenniaTest):
    def test_builder_creates_eighteen_connected_public_rooms_idempotently(self):
        rooms = ensure_dawnline()
        again = ensure_dawnline()
        self.assertEqual(len(rooms), 18)
        self.assertEqual({role: room.id for role, room in rooms.items()}, {role: room.id for role, room in again.items()})
        visited = set()
        pending = [rooms["hotel_hall"]]
        while pending:
            room = pending.pop()
            if room.id in visited:
                continue
            visited.add(room.id)
            pending.extend(exit_obj.destination for exit_obj in room.exits if exit_obj.destination and exit_obj.destination in rooms.values())
        self.assertEqual(len(visited), len(ROOMS))
        self.assertTrue(rooms["market_w"].db.spectrum_desc)
        self.assertTrue(rooms["heimdall_overlook"].db.resonance_desc)

    def test_private_room_has_route_into_public_hotel_block(self):
        self.char1.db.species = "human"
        room = ensure_personal_room(self.char1)
        self.assertTrue(room.db.dawnline_private_owner_id)
        self.assertEqual(room.exits[0].destination, ensure_dawnline()["hotel_hall"])

    def test_two_private_room_commands_are_owner_filtered(self):
        first = ensure_personal_room(self.char1)
        second = ensure_personal_room(self.char2)
        hall = ensure_dawnline()["hotel_hall"]
        inbound = [exit_obj for exit_obj in hall.exits if exit_obj.destination in {first, second}]
        self.assertEqual(len(inbound), 2)
        self.assertEqual(sum(exit_obj.access(self.char1, "cmd") for exit_obj in inbound), 1)
        self.assertEqual(sum(exit_obj.access(self.char2, "cmd") for exit_obj in inbound), 1)

    def test_personal_room_repairs_a_missing_exit(self):
        room = ensure_personal_room(self.char1)
        room.exits[0].delete()
        repaired = ensure_personal_room(self.char1)
        self.assertTrue(any(exit_obj.destination == ensure_dawnline()["hotel_hall"] for exit_obj in repaired.exits))

    def test_porter_has_redundant_character_binding_and_is_recoverable(self):
        porter = ensure_bound_porter(self.char1)
        self.assertIsInstance(porter, BoundPorter)
        self.assertTrue(self.char1.db.porter_binding["bound"])
        self.assertFalse(self.char1.db.porter_binding["permadeath_enabled"])
        porter.location = ensure_personal_room(self.char1)
        recovered = ensure_bound_porter(self.char1)
        self.assertEqual(recovered.location, self.char1)

    def test_origin_possessions_are_selective_and_idempotent(self):
        self.char1.db.species = "oruun"
        self.char1.db.background = "heimdall_rigger"
        first = ensure_origin_possessions(self.char1)
        second = ensure_origin_possessions(self.char1)
        self.assertNotIn("species", first)
        self.assertEqual(first["background"].id, second["background"].id)
        self.assertEqual(first["background"].key, "retired calibration shard")
        self.assertEqual(self.char1.db.background_miniskill, "mixed_measure")

        self.char1.db.background = "hullborn"
        self.assertEqual(ensure_origin_possessions(self.char1), {})
