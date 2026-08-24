"""Typeclasses for the two launch tutorial shells."""

from typeclasses.exits import Exit
from typeclasses.items import BasicBackpack, EquipableItem
from typeclasses.npcs import HostileNPC
from typeclasses.objects import InspectableScenery
from typeclasses.rooms import Room


class OpeningRoom(Room):
    """One owner-private room in a launch tutorial instance."""

    def get_display_footer(self, looker, **kwargs):
        footer = super().get_display_footer(looker, **kwargs)
        if not looker or int(self.db.tutorial_owner_id or 0) != looker.id:
            return footer
        from world.opening_tutorial import room_prompt
        prompt = room_prompt(looker, self)
        return "\n".join(part for part in (footer, prompt) if part)


class OpeningExit(Exit):
    """Owner-only route that keeps unfinished encounters meaningful."""

    def at_traverse(self, traversing_object, target_location, **kwargs):
        owner_id = int(self.db.tutorial_owner_id or 0)
        if owner_id and traversing_object.id != owner_id and not traversing_object.check_permstring("Admin"):
            traversing_object.msg("That memory—or obligation—does not belong to you.")
            return
        active = [obj for obj in self.location.contents if getattr(obj, "is_hostile", False) and not obj.db.is_defeated and not obj.db.tutorial_practice_target]
        if active:
            traversing_object.msg(f"|r{active[0].key} controls the route. You must deal with it first.|n")
            return
        state = dict(traversing_object.db.opening_tutorial_progress or {})
        role = str(self.location.db.tutorial_role or "")
        if role in {"aux_workshop", "workshop_alcove"}:
            required = set(traversing_object.db.active_skill_trees or [])
            practiced = set(state.get("combat_trees_used", []))
            if not required.issubset(practiced):
                missing = ", ".join(sorted(required - practiced)).replace("_", " ").title()
                traversing_object.msg(f"The practice target still needs an actual ability from: |w{missing}|n. Use |wskills|n, then |wcast <ability> practice target|n.")
                return
            if not state.get("reaction_used"):
                traversing_object.msg("The console is holding one harmless telegraph. Use |wreact|n to turn Balance into Focus before continuing.")
                return
        if role in {"manifest_office", "guest_clinic"} and not state.get("background_used"):
            traversing_object.msg("Apply what your Background taught you first: |wuse miniskill on evidence|n.")
            return
        if self.key.lower() in {"wake", "return"}:
            required = set(traversing_object.db.active_skill_trees or [])
            demonstrated = set(state.get("combat_trees_used", []))
            if not required.issubset(demonstrated):
                missing = ", ".join(sorted(required - demonstrated)).replace("_", " ").title()
                traversing_object.msg(f"Before completion, demonstrate each chosen tree at the workshop console or in combat. Still missing: |w{missing}|n.")
                return
            proof_labels = {
                "inventory_checked": "INVENTORY",
                "practice_gear_equipped": "GET and EQUIP the fitted practice gear",
                "equipment_checked": "EQUIPMENT",
                "container_taken": "GET the tutorial container",
                "journal_checked": "TASK",
                "target_considered": "CONSIDER a hostile",
                "attack_started": "ATTACK a hostile",
                "reaction_used": "REACT to a telegraph or workshop simulation",
                "background_used": "USE MINISKILL ON EVIDENCE",
            }
            missing_proofs = [label for key, label in proof_labels.items() if not state.get(key)]
            if missing_proofs:
                traversing_object.msg("Finish the remaining tutorial proof first: |w" + "; ".join(missing_proofs) + "|n. Backtracking is always available.")
                return
            if not traversing_object.db.opening_tutorial_decision:
                traversing_object.msg("Choose what this event remembers first with |wdecide|n.")
                return
            from world.opening_tutorial import finish_opening_tutorial
            decision = traversing_object.db.opening_tutorial_decision
            finish_opening_tutorial(traversing_object, decision=decision)
            return
        return super().at_traverse(traversing_object, target_location, **kwargs)


class OpeningDetail(InspectableScenery):
    """Owner-private tutorial evidence."""

    def get_display_desc(self, looker, **kwargs):
        if looker and str(self.db.tutorial_role or "").endswith(":wall datapad"):
            state = dict(looker.db.opening_tutorial_progress or {})
            reads = int(state.get("datapad_reads", 0))
            stages = (
                "BIOLOGICAL CONTAMINATION: NONE REPORTED.",
                "BIOLOGICAL CONTAMINATION: REPORTED / DISMISSED. You are certain the line changed while you were reading it.",
                "BIOLOGICAL CONTAMINATION: YOU ALREADY READ THIS. A nearby crew member sees an ordinary manifest.",
            )
            state["datapad_reads"] = min(2, reads + 1)
            looker.db.opening_tutorial_progress = state
            return stages[min(reads, 2)]
        return super().get_display_desc(looker, **kwargs)


class OpeningHostile(HostileNPC):
    """A very forgiving, non-respawning tutorial combatant."""

    def at_object_creation(self):
        super().at_object_creation()
        self.db.health_max = self.db.health_current = 24
        self.db.damage_min, self.db.damage_max = 2, 4
        self.db.evasion = 0
        self.db.armor = 0
        self.db.telegraph_seconds = 3.2
        self.db.attack_interval = 5.0
        # Tutorial rewards are committed from a bounded character ledger only
        # after convergence; hostiles never pay repeatable global XP.
        self.db.experience_reward = 0
        self.db.respawn_seconds = 0
        self.db.aggressive = False

    def at_defeat(self, contributors):
        from world.combat import resolve_object

        owner_id = int(self.db.tutorial_owner_id or 0)
        characters = [resolve_object(dbref) for dbref in contributors]
        character = next((obj for obj in characters if obj and obj.id == owner_id), None)
        if character:
            state = dict(character.db.opening_tutorial_progress or {})
            state.setdefault("defeated", []).append(str(self.db.tutorial_role))
            character.db.opening_tutorial_progress = state


class OpeningPracticeGear(EquipableItem):
    """Temporary fitted gear that records the equipment lesson."""

    def equip_to(self, wearer, quiet=False):
        result = super().equip_to(wearer, quiet=quiet)
        if result:
            from world.opening_tutorial import record_tutorial_proof

            record_tutorial_proof(wearer, "practice_gear_equipped")
        return result


class OpeningPracticeContainer(BasicBackpack):
    """Temporary tutorial container removed during convergence."""

    def at_get(self, getter, **kwargs):
        super().at_get(getter, **kwargs)
        from world.opening_tutorial import record_tutorial_proof

        record_tutorial_proof(getter, "container_taken")


class BoundPorter(EquipableItem):
    """The player's bound continuity-service terminal."""

    def at_object_creation(self):
        super().at_object_creation()
        self.db.equipment_slot = "wrist"
        self.db.cosmetic_equipment = True
        self.db.bound = True
        self.db.coverage = "Dawnline Return House"
        self.db.billing_status = "introductory service"
        self.db.desc = "A black-ceramic wrist terminal with three nested pale rings. Its redundant continuity record identifies it as bound to you."
        self.locks.add("drop:false();give:false()")

    def at_pre_drop(self, dropper, **kwargs):
        dropper.msg("Porter refuses: its physical terminal is registered to your continuity record.")
        return False

    def at_pre_give(self, giver, getter, **kwargs):
        giver.msg("A bound Porter cannot be transferred by handing someone the terminal.")
        return False

    def at_talk(self, character, session=None):
        character.msg(
            'Porter says, "Coverage is active through the Dawnline Return House. Overdue fees produce reminders, not mortality. Only a deliberate, separately confirmed unbinding enables permanent death. I decline to provide that confirmation phrase casually."'
        )

    def at_greet(self, character):
        self.at_talk(character)
