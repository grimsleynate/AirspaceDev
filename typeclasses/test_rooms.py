"""Tests for Quasar room mapper output."""

from unittest.mock import patch

from evennia import create_object
from evennia.utils.ansi import strip_ansi
from evennia.utils.test_resources import EvenniaTest

from .exits import Exit
from .exits import HiddenExit
from .items import PortableItem
from .npcs import FriendlyNPC
from .objects import PuzzleClue
from .rooms import ASCII_MAP_DIRECTIONS, DIRECTION_NAMES


class RoomInfoTests(EvenniaTest):
    def setUp(self):
        super().setUp()
        self.room1.db.map_area = "Test Station"
        self.room1.db.map_area_id = 7
        self.room1.db.map_environment = "interior"
        self.room1.db.map_x = 3
        self.room1.db.map_y = -2
        self.room1.db.map_z = 1
        create_object(
            Exit,
            key="north",
            aliases=["n"],
            location=self.room1,
            destination=self.room2,
        )

    def test_room_info_uses_common_gmcp_shape(self):
        self.char2.location = self.room2
        info = self.room1.get_room_info(self.char1)

        self.assertEqual(info["num"], self.room1.id)
        self.assertEqual(info["name"], self.room1.key)
        self.assertEqual(info["area"], "Test Station")
        self.assertEqual(info["environment"], "interior")
        self.assertEqual(info["atmosphere"], "breathable")
        self.assertTrue(info["gravity"])
        self.assertEqual(info["exits"]["n"], self.room2.id)
        self.assertEqual(info["coords"], "7,3,-2,1")
        self.assertEqual(info["coord"], {"id": 7, "x": 3, "y": -2, "z": 1})
        self.assertIn("description", info)
        self.assertEqual(info["players"], [])
        self.assertEqual(info["npcs"], [])
        self.assertEqual(info["items"], [])

    def test_room_info_separates_visible_entities(self):
        self.char2.location = self.room1
        create_object(FriendlyNPC, key="Station Guide", location=self.room1)
        create_object(PortableItem, key="access badge", location=self.room1)

        info = self.room1.get_room_info(self.char1)

        self.assertEqual([entity["name"] for entity in info["players"]], ["Char2"])
        self.assertEqual([entity["name"] for entity in info["npcs"]], ["Station Guide"])
        self.assertEqual([entity["name"] for entity in info["items"]], ["access badge"])

    def test_looking_at_current_room_sends_room_info(self):
        self.char1.location = self.room1

        with patch.object(self.char1, "msg") as mocked_msg:
            self.room1.at_desc(self.char1)

        mocked_msg.assert_called_once_with(room_info=self.room1.get_room_info(self.char1))

    def test_remote_look_does_not_move_mapper(self):
        self.char1.location = self.room2

        with patch.object(self.char1, "msg") as mocked_msg:
            self.room1.at_desc(self.char1)

        mocked_msg.assert_not_called()

    def test_ascii_map_shows_standard_and_special_exits(self):
        ascii_map = strip_ansi(self.room1.get_ascii_map(self.char1))

        self.assertIn("[@]", ascii_map)
        self.assertIn("[ ]", ascii_map)
        self.assertIn("Special: [OUT]", ascii_map)

    def test_ascii_map_can_be_hidden_from_room_appearance(self):
        self.char1.location = self.room1

        self.char1.db.ascii_map_enabled = True
        shown = strip_ansi(self.room1.return_appearance(self.char1))
        self.assertIn("[@]", shown)

        self.char1.db.ascii_map_enabled = False
        hidden = strip_ansi(self.room1.return_appearance(self.char1))
        self.assertNotIn("[@]", hidden)

    def test_all_twelve_standard_directions_are_supported(self):
        for long_name, short_name in DIRECTION_NAMES.items():
            if short_name in {"n", "out"}:
                continue
            create_object(
                Exit,
                key=long_name,
                aliases=[short_name],
                location=self.room1,
                destination=self.room2,
            )

        self.assertEqual(self.room1.get_visible_map_exits(self.char1), ASCII_MAP_DIRECTIONS)

    def test_hidden_exit_is_not_leaked_to_maps(self):
        hidden = create_object(
            HiddenExit,
            key="crawl north",
            location=self.room1,
            destination=self.room2,
        )

        self.assertTrue(hidden.access(self.char1, "traverse"))
        self.assertFalse(hidden.access(self.char1, "view"))
        self.assertNotIn("crawlnorth", self.room1.get_room_info(self.char1)["exits"])

    def test_custom_visible_command_is_not_mistaken_for_compass_exit(self):
        create_object(
            Exit,
            key="crouch southwest",
            location=self.room1,
            destination=self.room2,
        )

        self.assertNotIn("crouchsouthwest", self.room1.get_room_info(self.char1)["exits"])

    def test_room_appearance_separates_players_npcs_items_and_details(self):
        self.char2.location = self.room1
        npc = create_object(FriendlyNPC, key="Station Guide", location=self.room1)
        item = create_object(PortableItem, key="access badge", location=self.room1)
        detail = create_object(PuzzleClue, key="scuffed panel", location=self.room1)

        appearance = self.room1.return_appearance(self.char1)

        self.assertIn("|wPlayers:|n", appearance)
        self.assertIn("|wPeople:|n", appearance)
        self.assertIn("|wItems:|n", appearance)
        self.assertIn("|wNotable details:|n", appearance)
        self.assertIn("|h|wChar2|n", appearance)
        self.assertIn("|h|gStation Guide|n", appearance)
        self.assertIn("|h|yaccess badge|n", appearance)
        self.assertIn("|h|mscuffed panel|n", appearance)
        self.assertNotEqual(npc.get_display_name(self.char1), self.room1.get_display_name(self.char1))
        self.assertTrue(item.get_display_name(self.char1).startswith("|h|y"))
        self.assertTrue(detail.get_display_name(self.char1).startswith("|h|m"))

    def test_puzzle_clue_keeps_prose_neutral_and_accents_authored_clue(self):
        detail = create_object(PuzzleClue, key="scuffed panel", location=self.room1)
        detail.db.desc = "The panel is scratched around one recessed fastener."
        detail.db.clue_desc = "The scratches form a shallow clockwise arc."

        description = detail.get_display_desc(self.char1)

        self.assertTrue(description.startswith("The panel is scratched"))
        self.assertIn("|mThe scratches form a shallow clockwise arc.|n", description)
