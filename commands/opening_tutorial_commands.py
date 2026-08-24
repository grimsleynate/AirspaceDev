"""Small choice surface for the launch tutorials."""

from time import time

from evennia.commands.default.muxcommand import MuxCommand


class CmdReact(MuxCommand):
    """Break a readable hostile telegraph with the universal reaction."""

    key = "react"
    aliases = ["defend", "brace"]
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        from world.combat import current_target
        from world.opening_tutorial import record_tutorial_proof

        hostile = current_target(self.caller)
        role = str(getattr(getattr(self.caller.location, "db", None), "tutorial_role", ""))
        if role in {"aux_workshop", "workshop_alcove"} and (
            not hostile or hostile.location != self.caller.location or hostile.db.tutorial_practice_target
        ):
            self.caller.db.combat_focus = min(3, int(self.caller.db.combat_focus or 0) + 1)
            self.caller.db.combat_balance = "ready"
            record_tutorial_proof(self.caller, "reaction_used")
            self.caller.msg("The console telegraphs a harmless strike. You break its line, keep your Balance, and gain one Focus for the next active ability.")
            return
        if not hostile or hostile.location != self.caller.location:
            self.caller.msg("You have no current hostile action to react to.")
            return
        intent = hostile.db.combat_intent
        if not intent:
            self.caller.msg("Wait for a clearly telegraphed action before spending your reaction.")
            return
        now = time()
        ready_at = float(self.caller.db.reaction_ready_at or 0)
        if ready_at > now:
            self.caller.msg(f"Your Balance has not recovered ({ready_at - now:.1f}s).")
            return
        hostile.db.combat_intent = None
        hostile.db.next_attack_at = now + 3.0
        self.caller.db.reaction_ready_at = now + 4.0
        self.caller.db.combat_balance = "recovering"
        self.caller.db.combat_focus = min(3, int(self.caller.db.combat_focus or 0) + 1)
        record_tutorial_proof(self.caller, "reaction_used")
        self.caller.msg(f"|cYou read and break {hostile.key}'s {intent.get('name', 'attack')}.|n Balance recovers in 4s; Focus rises to {self.caller.db.combat_focus}/3.")


class CmdOpeningDecision(MuxCommand):
    """
    Record the response your character takes at the tutorial climax.

    Usage:
        decide
        decide <choice>

    The command lists the choices valid in the current climax room. It stores
    an event, not an alignment score.
    """

    key = "decide"
    aliases = ["choose response"]
    locks = "cmd:all()"
    help_category = "Tutorial"

    HUMAN = {
        "warn openly": "warn_openly",
        "report authority": "report_authority",
        "protect vulnerable": "protect_vulnerable",
        "conceal": "conceal",
    }
    NATIVE = {
        "carry guest": "carry_guest",
        "surrender witnessed": "surrender_witnessed",
        "protect evidence": "protect_evidence",
        "negotiate review": "witnessed_review",
        "betray guest": "betray_guest_right",
    }

    def func(self):
        role = str(getattr(getattr(self.caller.location, "db", None), "tutorial_role", ""))
        choices = self.HUMAN if role in {"translation_annex", "observation_well"} else self.NATIVE if role == "return_pad" else None
        if not choices:
            self.caller.msg("There is no tutorial decision to record here.")
            return
        raw = " ".join(self.args.lower().split())
        if not raw:
            self.caller.msg("Choices: " + ", ".join(f"|w{name}|n" for name in choices))
            return
        selected = choices.get(raw)
        if not selected:
            self.caller.msg("Choose one of: " + ", ".join(choices))
            return
        self.caller.db.opening_tutorial_decision = selected
        self.caller.msg(f"|gDecision recorded:|n {raw}. This is remembered as an event, not a moral score.")
