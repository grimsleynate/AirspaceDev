"""Tests for reusable city vermin populations and opt-in alerts."""

from unittest.mock import patch

from evennia.utils.test_resources import EvenniaCommandTest, EvenniaTest

from commands.vermin_commands import CmdVermin
from typeclasses.vermin import CityVermin, VerminCarcass
from world.dawnline import ensure_dawnline
from world.vermin import (
    CITY_PROFILES,
    city_rooms,
    city_vermin,
    cleanup_city_vermin,
    maintain_city_vermin,
    notify_vermin_presence,
    spawn_city_vermin,
)


def _first(rows):
    return rows[0]


class VerminPopulationTests(EvenniaTest):
    def setUp(self):
        super().setUp()
        self.rooms = ensure_dawnline()

    def test_dawnline_population_is_capped_balanced_and_idempotent(self):
        spawned = maintain_city_vermin("dawnline", chooser=_first)
        second = maintain_city_vermin("dawnline", chooser=_first)

        self.assertEqual(len(spawned), CITY_PROFILES["dawnline"]["population"])
        self.assertFalse(second)
        living = city_vermin("dawnline", include_defeated=False)
        self.assertEqual(len(living), CITY_PROFILES["dawnline"]["population"])
        self.assertEqual(len({mob.location for mob in living}), len(living))
        self.assertEqual(
            sorted(str(mob.db.vermin_species) for mob in living),
            ["brine_skitter", "brine_skitter", "echo_jackdaw", "echo_jackdaw", "wiregrazer", "wiregrazer"],
        )
        self.assertTrue(all(20 <= int(mob.db.health_max) <= 24 for mob in living))
        self.assertTrue(all(int(mob.db.damage_max) <= 3 for mob in living))

    def test_safe_civic_rooms_are_registered_but_not_spawnable(self):
        spawnable = set(city_rooms("dawnline"))

        self.assertNotIn(self.rooms["hotel_hall"], spawnable)
        self.assertNotIn(self.rooms["return_lobby"], spawnable)
        self.assertNotIn(self.rooms["orison_kiosk"], spawnable)
        self.assertTrue(self.rooms["hotel_hall"].tags.has("dawnline", category="quasar_city"))

    def test_reconciliation_repairs_excess_duplicates_and_protected_room_drift(self):
        maintain_city_vermin("dawnline", chooser=_first)
        definition = CITY_PROFILES["dawnline"]["vermin"][0]
        living = city_vermin("dawnline", include_defeated=False)
        duplicate = spawn_city_vermin("dawnline", living[0].location, definition)
        protected = spawn_city_vermin(
            "dawnline", self.rooms["return_lobby"], definition
        )
        unplaced = spawn_city_vermin(
            "dawnline", self.rooms["crosswind_c"], definition
        )
        unplaced.location = None

        maintain_city_vermin("dawnline", chooser=_first)

        repaired = city_vermin("dawnline", include_defeated=False)
        spawnable = set(city_rooms("dawnline"))
        self.assertEqual(len(repaired), CITY_PROFILES["dawnline"]["population"])
        self.assertEqual(len({mob.location for mob in repaired}), len(repaired))
        self.assertTrue(all(mob.location in spawnable for mob in repaired))
        remaining_ids = {mob.id for mob in repaired}
        self.assertNotIn(duplicate.id, remaining_ids)
        self.assertNotIn(protected.id, remaining_ids)
        self.assertNotIn(unplaced.id, remaining_ids)

    def test_defeat_leaves_one_bounty_carcass_then_cleanup_removes_mob(self):
        room = self.rooms["crosswind_c"]
        definition = CITY_PROFILES["dawnline"]["vermin"][0]
        mob = spawn_city_vermin("dawnline", room, definition)

        mob.at_defeat({str(self.char1.id): 10})
        mob.at_defeat({str(self.char1.id): 10})

        carcasses = [obj for obj in room.contents if isinstance(obj, VerminCarcass)]
        self.assertEqual(len(carcasses), 1)
        self.assertEqual(carcasses[0].db.vermin_species, "wiregrazer")
        self.assertEqual(carcasses[0].db.vermin_bounty, 2)
        mob.db.is_defeated = True
        cleanup_city_vermin("dawnline", now=float(mob.db.despawn_at) + 1)
        self.assertFalse(CityVermin.objects.filter_family(id=mob.id).exists())

    def test_awareness_is_silent_by_default_and_reports_when_enabled(self):
        room = self.rooms["crosswind_c"]
        self.char1.move_to(room, quiet=True)
        definition = CITY_PROFILES["dawnline"]["vermin"][1]
        mob = spawn_city_vermin("dawnline", room, definition)

        with patch.object(self.char1, "msg") as message:
            self.assertFalse(notify_vermin_presence(self.char1, [mob]))
            message.assert_not_called()
            self.char1.db.vermin_awareness = True
            self.assertTrue(notify_vermin_presence(self.char1, [mob]))
            self.assertIn("Vermin awareness", message.call_args.args[0])


class VerminCommandTests(EvenniaCommandTest):
    def test_vermin_toggles_from_default_off_and_accepts_explicit_state(self):
        self.assertFalse(bool(self.char1.db.vermin_awareness))

        result = self.call(CmdVermin(), "", caller=self.char1, msg=None)
        self.assertIn("enabled", result)
        self.assertTrue(self.char1.db.vermin_awareness)

        result = self.call(CmdVermin(), "off", caller=self.char1, msg=None)
        self.assertIn("disabled", result)
        self.assertFalse(self.char1.db.vermin_awareness)
