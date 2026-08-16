"""Parser-facing tests for tutorial commands."""

from evennia.utils.test_resources import EvenniaCommandTest

from commands.tutorial_commands import (
    CmdBindPorter,
    CmdCutDoor,
    CmdOpenCabinet,
    CmdTouchPorter,
)
from world import tutorial
from world.resources import initialize_character


class TutorialCommandTests(EvenniaCommandTest):
    def setUp(self):
        super().setUp()
        self.char1.db.tutorial_complete = False
        self.char1.attributes.remove("tutorial_instance_id")
        self.char1.attributes.remove("tutorial_progress")
        tutorial.create_tutorial_instance(self.char1, enter=True)

    def _move(self, role):
        self.char1.move_to(tutorial.role_room(self.char1, role), quiet=True, move_type="teleport")

    def test_open_cabinet_command_creates_private_supplies(self):
        tutorial.save_progress(self.char1, stores_code=True)
        self._move("emergency_stores")

        result = self.call(CmdOpenCabinet(), "", msg=None)

        self.assertIn("cabinet opens", result)
        self.assertIsNotNone(tutorial.role_object(self.char1, "induction_bridge"))

    def test_bind_then_touch_completes_the_tutorial(self):
        self._move("emergency_transit_chamber")
        tutorial.recover_porter(self.char1)

        self.call(CmdBindPorter(), "", msg=None)
        self._move("navigation_control")
        result = self.call(CmdTouchPorter(), "", msg=None)

        self.assertIn("Tutorial complete", result)
        self.assertTrue(self.char1.db.tutorial_complete)

    def test_cut_door_is_hidden_and_accepts_direction_argument(self):
        initialize_character(self.char1, include_starter_gear=True)
        self._move("command_pressure_lock")

        self.call(CmdCutDoor(), "east", msg=None)
        self.call(CmdCutDoor(), "north", msg=None)

        self.assertFalse(CmdCutDoor.auto_help)
        self.assertTrue(tutorial.progress(self.char1)["survivors_decompressed"])
