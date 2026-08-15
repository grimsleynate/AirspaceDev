"""Tests for Quasar's first tutorial interaction loop."""

from evennia import create_object
from evennia.utils.test_resources import EvenniaTest

from typeclasses.items import TutorialAccessBadge
from typeclasses.npcs import OrientationGuide
from world import tutorial_dialogue


class TutorialInteractionTests(EvenniaTest):
    def setUp(self):
        super().setUp()
        self.char1.location = self.room1
        self.guide = create_object(
            OrientationGuide,
            key="Guide Lumen",
            aliases=["guide"],
            location=self.room1,
        )
        self.badge = create_object(
            TutorialAccessBadge,
            key="orientation access badge",
            aliases=["badge"],
            location=self.char1,
        )

    def test_objective_dialogue_saves_progress(self):
        text, options = tutorial_dialogue.node_objective(
            self.char1, "", npc=self.guide
        )

        self.assertIn("give badge to guide", text)
        self.assertTrue(self.char1.db.tutorial_progress["badge_requested"])
        self.assertEqual(len(options), 1)

    def test_giving_badge_completes_objective_and_returns_badge(self):
        self.badge.at_give(self.char1, self.guide)

        self.assertTrue(self.char1.db.tutorial_progress["badge_returned"])
        self.assertEqual(self.badge.location, self.char1)

    def test_friendly_npc_cannot_be_picked_up(self):
        self.assertFalse(self.guide.access(self.char1, "get"))
