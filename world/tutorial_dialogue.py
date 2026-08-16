"""EvMenu dialogue for Mara Venn and Juno Rusk."""

from world.tutorial import choose_mara_fate, objective_hint, progress


def _npc(caller, kwargs):
    npc = kwargs.get("npc")
    if npc:
        return npc
    menu = getattr(caller.ndb, "_evmenu", None)
    return getattr(menu, "npc", None)


def _back():
    return ({"key": ("Back", "back", "b", "1"), "desc": "Return to the conversation.", "goto": "node_start"},)


def node_start(caller, raw_string="", **kwargs):
    npc = _npc(caller, kwargs)
    if not npc:
        return "The conversation breaks off unexpectedly.", None
    role = str(npc.db.tutorial_role or "")
    state = progress(caller)
    if role == "juno":
        return _juno_start(caller)
    if state.get("juno_defeated") and not state.get("mara_fate"):
        return _mara_choice_start(caller)
    return _mara_start(caller)


def _mara_start(caller):
    state = progress(caller)
    opening = (
        'Mara says, "You came back. Tell me the ring is ready."'
        if state.get("companion_transit_ready")
        else 'Mara keeps her voice low. "Ask what you need. Juno and I have had weeks to inventory the bad news."'
    )
    return opening, (
        {"key": ("What happened?", "happened", "raid", "1"), "desc": "Ask about the attack.", "goto": "node_raid"},
        {"key": ("How long?", "long", "time", "2"), "desc": "Ask how long they have been trapped.", "goto": "node_time"},
        {"key": ("Juno", "injury", "wrong", "3"), "desc": "Ask what is wrong with Juno.", "goto": "node_juno_injury"},
        {"key": ("Escape", "off", "leave", "4"), "desc": "Ask how everyone can escape.", "goto": "node_escape"},
        {"key": ("Parasites", "things", "feeders", "5"), "desc": "Ask about the organisms outside.", "goto": "node_parasites"},
        {"key": ("Next", "objective", "next", "6"), "desc": "Ask what to do next.", "goto": "node_objective"},
        {"key": ("End", "end", "quit", "q", "7"), "desc": "End the conversation.", "goto": "node_end"},
    )


def _juno_start(caller):
    return 'Juno studies you through the fever. "If this is pity, spend it somewhere useful."', (
        {"key": ("Injury", "wound", "1"), "desc": "Ask about her injured arm.", "goto": "node_juno_injury_direct"},
        {"key": ("Raid", "reavers", "2"), "desc": "Ask about the attack.", "goto": "node_juno_raid"},
        {"key": ("Parasites", "feeders", "3"), "desc": "Ask about the organisms.", "goto": "node_juno_parasites"},
        {"key": ("Next", "objective", "4"), "desc": "Ask what to do next.", "goto": "node_objective"},
        {"key": ("End", "end", "quit", "q", "5"), "desc": "End the conversation.", "goto": "node_end"},
    )


def _mara_choice_start(caller):
    return (
        "Mara keeps a bandage pressed over the fresh bite. Juno lies still beside the command ring.\n"
        '"You saw what this becomes without treatment. Decide while I can still understand the answer."',
        (
            {"key": ("Come with me", "rescue", "save", "1"), "desc": "Promise to seek treatment for Mara.", "goto": "node_choose_rescue"},
            {"key": ("Stay here", "abandon", "leave", "2"), "desc": "Leave Mara in the sealed Command Center.", "goto": "node_choose_abandon"},
            {"key": ("Mercy", "quick death", "3"), "desc": "Prevent her transformation at her request.", "goto": "node_choose_mercy"},
            {"key": ("I need time", "time", "wait", "4"), "desc": "Make no decision yet.", "goto": "node_end"},
        ),
    )


def node_raid(caller, raw_string="", **kwargs):
    return (
        '"The Shardwake Reavers," Mara says. "They saw an understaffed relay, cut the docking lock, '
        'and stripped anything worth reselling. We killed the lights and sealed Command while they worked."\n'
        'Juno looks over. "They had salvage manifests printed before the bodies were cold. Fractured-comet mark. Remember it."',
        _back(),
    )


def node_time(caller, raw_string="", **kwargs):
    return (
        '"Several weeks. The reclamation loop kept two people alive longer than its designers promised, but the reserve now estimates less than three days. Most identifying records are gone."',
        _back(),
    )


def node_juno_injury(caller, raw_string="", **kwargs):
    return (
        'Mara glances at the cot. "Her suit tore while we retreated from engineering. Antibiotics did nothing."\n'
        'Juno presses the bandaged arm against her side. "It is an infected cut. We have a larger problem."',
        _back(),
    )


def node_escape(caller, raw_string="", **kwargs):
    state = progress(caller)
    porter_line = (
        ' Mara nods toward your wrist device. "That is the personal unit. The ring should widen it for one passenger."'
        if state.get("porter_bound")
        else ""
    )
    return (
        '"There is an old transit amplifier below. The Reavers stripped its power bridge, and navigation lost the route. '
        'A manual wafer remains at the SOS relay. Emergency Stores has a portable bridge. Restore both, test the ring, and come back."'
        + porter_line,
        _back(),
    )


def node_parasites(caller, raw_string="", **kwargs):
    return (
        'Juno answers. "Small ones feed. Bigger ones use what they feed on. Vacuum slows them; it does not kill them. Do not let one bite through your suit."',
        _back(),
    )


def node_objective(caller, raw_string="", **kwargs):
    return objective_hint(caller, room=caller.location) or "There is nothing more to do here.", _back()


def node_juno_injury_direct(caller, raw_string="", **kwargs):
    return (
        '"Caught the forearm on a torn service hatch. Mara has spent enough time wrapping it." The pause before she says hatch lasts a fraction too long.',
        _back(),
    )


def node_juno_raid(caller, raw_string="", **kwargs):
    return (
        '"They depressurized compartments before boarding. Efficient if you own better suits than the people inside. They kept stripping the decks instead of spending charges to prove two quiet women were behind one reinforced door."',
        _back(),
    )


def node_juno_parasites(caller, raw_string="", **kwargs):
    return (
        '"Kill the small ones before they gather. If a body gets back up, stop thinking of it as the person it was."',
        _back(),
    )


def node_choose_rescue(caller, raw_string="", **kwargs):
    choose_mara_fate(caller, "rescue")
    return "Mara seals the last emergency suit and waits for you to lead her to the transit chamber.", None


def node_choose_abandon(caller, raw_string="", **kwargs):
    choose_mara_fate(caller, "abandon")
    return "Mara turns back toward the endlessly repeating SOS.", None


def node_choose_mercy(caller, raw_string="", **kwargs):
    choose_mara_fate(caller, "mercy")
    return "Only the SOS continues speaking inside Command.", None


def node_end(caller, raw_string="", **kwargs):
    return "The conversation ends, but the failing reserve display keeps counting down.", None
