"""Coverage for writable datapads, journals, and preserved hacked notes."""

from unittest.mock import patch

from evennia import create_object
from evennia.utils.test_resources import EvenniaCommandTest, EvenniaTest

from commands.datapad_commands import (
    CmdHackDatapad,
    CmdReadDatapad,
    CmdTitleDatapad,
    CmdWriteDatapad,
    _read_default,
)
from typeclasses.datapads import Datapad, StarJournal, ensure_starter_datapad
from world.resources import build_resource_payload, initialize_character


class DatapadTests(EvenniaTest):
    def test_title_appends_author_and_removes_spoofed_byline(self):
        pad = create_object(Datapad, key="datapad", location=self.char1)

        self.assertTrue(pad.set_title(self.char1, "Field Notes by Somebody Else"))

        self.assertEqual(pad.key, f"Field Notes by {self.char1.key}")

    def test_hacking_preserves_original_and_signs_annotation(self):
        pad = create_object(Datapad, key="datalog", location=self.char1)
        pad.write_page(self.char1, 1, "Original mission orders.")

        pad.save_annotation(self.char2, 1, "Meet me behind the reactor.")
        rendered = pad.render_page(1)

        self.assertIn("Original mission orders.", rendered)
        self.assertIn("Meet me behind the reactor.", rendered)
        self.assertIn(self.char2.key, rendered)
        self.assertEqual(pad.page(1)["text"], "Original mission orders.")

    def test_original_is_author_locked_but_hacking_is_not(self):
        pad = create_object(Datapad, key="datalog", location=self.char1)
        pad.write_page(self.char1, 1, "Sealed original.")

        self.assertFalse(pad.write_page(self.char2, 1, "Replacement."))
        self.assertIsNotNone(pad.save_annotation(self.char2, 1, "Margin note."))
        self.assertEqual(pad.page(1)["text"], "Sealed original.")

    def test_journal_pages_receive_stardates(self):
        journal = create_object(StarJournal, key="journal", location=self.char1)

        journal.write_page(self.char1, 1, "First watch.")

        self.assertRegex(journal.page(1)["stardate"], r"^\d{4}\.\d{3}\.\d{4} UTC$")

    def test_blank_datapad_can_be_read_and_starter_is_idempotent(self):
        pad = ensure_starter_datapad(self.char1)

        self.assertIs(pad, ensure_starter_datapad(self.char1))
        self.assertIn("This page is blank", pad.render_page(1))
        self.assertEqual(pad.location, self.char1)

    def test_character_initialization_gives_datapad_with_gui_capabilities(self):
        initialize_character(self.char1, include_starter_gear=True)

        pad = ensure_starter_datapad(self.char1)
        payload = next(
            item for item in build_resource_payload(self.char1)["inventory"]
            if item["id"] == pad.id
        )
        self.assertTrue(payload["readable"])
        self.assertTrue(payload["writable"])
        self.assertTrue(payload["editable"])
        self.assertFalse(payload["journal"])


class DatapadCommandTests(EvenniaCommandTest):
    def setUp(self):
        super().setUp()
        self.pad = create_object(Datapad, key="test pad", location=self.char1)

    @patch("commands.datapad_commands.EvEditor")
    def test_write_opens_editor_and_saves_requested_page(self, editor):
        self.call(CmdWriteDatapad(), "test pad 1", msg=None)

        editor.call_args.kwargs["savefunc"](self.char1, "A transmission log.")
        self.assertEqual(self.pad.page(1)["text"], "A transmission log.")

    def test_title_command_accepts_document_followed_by_title(self):
        self.call(CmdTitleDatapad(), "test pad Colors Out Of Space", msg=None)

        self.assertEqual(self.pad.key, f"Colors Out Of Space by {self.char1.key}")

    @patch("commands.datapad_commands.EvMenu")
    def test_title_without_name_opens_prompt_with_selected_document(self, menu):
        self.call(CmdTitleDatapad(), "test pad", msg=None)

        self.assertEqual(
            menu.call_args.kwargs["startnode_input"][1]["document"],
            self.pad,
        )

    @patch("commands.datapad_commands.EvMenu")
    def test_read_can_start_at_an_explicit_page(self, menu):
        self.pad.write_page(self.char1, 1, "One")
        self.pad.write_page(self.char1, 2, "Two")

        self.call(CmdReadDatapad(), "test pad 2", msg=None)

        self.assertEqual(menu.call_args.kwargs["startnode_input"][1]["page_number"], 2)
        self.assertEqual(menu.call_args.kwargs["startnode_input"][1]["document"], self.pad)

    def test_enter_next_and_prev_navigation(self):
        self.assertEqual(_read_default(self.char1, "", page_number=1, total=2)[1]["page_number"], 2)
        self.assertEqual(
            _read_default(self.char1, "PREV", page_number=2, total=2)[1]["page_number"],
            1,
        )

    @patch("commands.datapad_commands.EvEditor")
    def test_hack_command_adds_note_without_replacing_page(self, editor):
        self.pad.write_page(self.char1, 1, "Untouched original")

        self.call(CmdHackDatapad(), "test pad 1", msg=None)
        editor.call_args.kwargs["savefunc"](self.char2, "Unauthorized addendum")

        self.assertEqual(self.pad.page(1)["text"], "Untouched original")
        self.assertEqual(self.pad.page(1)["annotations"][0]["text"], "Unauthorized addendum")
