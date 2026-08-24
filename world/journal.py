"""Server-authoritative quest and task journals for text and web clients."""

from collections.abc import Mapping


JOURNAL_PROTOCOL_REVISION = 1


def _entry(entry_id, title, summary, detail, status="active"):
    return {
        "id": str(entry_id),
        "title": str(title),
        "summary": str(summary),
        "detail": str(detail),
        "status": str(status),
    }


def build_quest_log(character):
    """Return active, larger narrative arcs stored on the character."""

    quests = []
    for index, raw in enumerate(list(character.db.quest_log or []), start=1):
        if not isinstance(raw, Mapping) or raw.get("status", "active") != "active":
            continue
        quests.append(
            _entry(
                raw.get("id", f"quest-{index}"),
                raw.get("title", "Untitled quest"),
                raw.get("summary", raw.get("description", "")),
                raw.get("detail", raw.get("description", "No further information is available.")),
            )
        )
    return quests


def build_tutorial_tasks(character):
    """Derive the currently actionable tutorial tasks from persistent state."""

    if character.db.tutorial_complete:
        return []
    if character.db.chargen_complete:
        from world.opening_tutorial import room_prompt

        room = character.location
        role = str(getattr(getattr(room, "db", None), "tutorial_role", ""))
        state = dict(character.db.opening_tutorial_progress or {})
        shell = "The Last Night of Earth" if character.db.species == "human" else "Open Hatch"
        objective = room_prompt(character, room) if room else "Reconnect to your private tutorial instance."
        if role in {"aux_workshop", "workshop_alcove"}:
            practiced = set(state.get("trees_practiced", []))
            missing = [key for key in list(character.db.active_skill_trees or []) if key not in practiced]
            objective = "Demonstrate your remaining active practice: " + ", ".join(key.replace("_", " ").title() for key in missing)
        elif role in {"manifest_office", "guest_clinic"} and not state.get("background_used"):
            objective = "USE MINISKILL ON EVIDENCE before continuing."
        return [_entry("opening-tutorial", shell, objective, objective)]
    from world.tutorial import progress

    state = progress(character)
    tasks = []
    add = tasks.append

    if state.get("survivors_decompressed"):
        add(_entry(
            "depart-wreck",
            "Leave the dead satellite",
            "The Command survivors are dead. Porter remains your only exit.",
            "Recover and bind the Personal Portable Porter if necessary, then use TOUCH PORTER when you are ready to leave.",
        ))
        return tasks

    if not state.get("corpse_feeder_defeated"):
        role = str(character.location.db.tutorial_role or "") if character.location else ""
        if role == "shattered_reception":
            add(_entry(
                "survive-reception",
                "Survive Shattered Reception",
                "A corpse-feeder blocks the route into the satellite.",
                "The corpse-feeder is too intent on its meal to notice you. ATTACK it or use CAST <skill name> on it when you are ready; your equipped weapon attacks automatically once combat begins.",
            ))
        else:
            add(_entry(
                "investigate-sos",
                "Investigate the distress signal",
                "Board the unidentified satellite and find the source of its weeks-old SOS.",
                "Follow the dead guidance lamps east from the Docking Collar. Your suit supplies oxygen automatically in vacuum.",
            ))
        return tasks

    if not state.get("survivors_contacted"):
        add(_entry(
            "answer-channel",
            "Investigate the emergency channel",
            "The SOS handshake in Shattered Reception may still accept a response.",
            "Return to the emergency speaker in Shattered Reception and ANSWER, or continue toward the Command Deck Lift.",
        ))
        return tasks

    if not state.get("met_survivors"):
        add(_entry(
            "reach-command",
            "Reach the Command survivors",
            "Controller Venn reports two survivors sealed inside Command.",
            "Take the central lift up, enter the southern Command Pressure Lock, and travel east after its automatic decontamination cycle.",
        ))
        return tasks

    if not state.get("bridge_installed"):
        if not state.get("cabinet_open"):
            add(_entry(
                "open-stores",
                "Open Emergency Stores",
                "Mara supplied access to the last sealed equipment cabinet.",
                "Travel southwest through Cargo Inspection to Emergency Stores, then OPEN CABINET.",
            ))
        elif not state.get("bridge_collected"):
            add(_entry(
                "collect-bridge",
                "Collect the induction bridge",
                "The open Emergency Stores cabinet contains the missing power link.",
                "GET INDUCTION BRIDGE from the cabinet in Emergency Stores.",
            ))
        else:
            add(_entry(
                "install-bridge",
                "Restore the transit power link",
                "The portable induction bridge belongs in Auxiliary Power.",
                "Reach the Auxiliary Power Core on the engineering deck, defeat the overtaken raider, then INSTALL BRIDGE.",
            ))

    if not state.get("wafer_installed"):
        if not state.get("feeding_knot_defeated"):
            add(_entry(
                "recover-wafer",
                "Recover the routing wafer",
                "A manual transit wafer remains in the SOS Relay.",
                "Take the command lift northwest to the SOS Relay and defeat the feeding knot guarding the service cradle.",
            ))
        elif not state.get("wafer_collected"):
            add(_entry(
                "collect-wafer",
                "Collect the routing wafer",
                "The SOS Relay's protected service cradle is unlocked.",
                "GET TRANSIT ROUTING WAFER in the SOS Relay.",
            ))
        elif not state.get("wafer_calibrated"):
            add(_entry(
                "calibrate-wafer",
                "Calibrate the routing wafer",
                "The wafer needs a valid external destination handshake.",
                "Take the wafer to Navigation Control, examine the receiver traces, and USE WAFER ON CONSOLE.",
            ))
        else:
            add(_entry(
                "install-wafer",
                "Route the transit amplifier",
                "The calibrated wafer is ready for the Emergency Transit console.",
                "Carry the wafer to Emergency Transit on the engineering deck and INSTALL WAFER.",
            ))

    if not state.get("porter_bound"):
        action = "BIND PORTER" if state.get("porter_recovered") else "GET PORTER, then BIND PORTER"
        add(_entry(
            "bind-porter",
            "Recover and bind Porter",
            "The personal unit in Emergency Transit provides transport to the nearest Hexcom facility, complimentary through level 10.",
            f"Reach the Emergency Transit Chamber, {action}. Binding and carrying it are sufficient; equipping it is cosmetic and optional.",
        ))

    if state.get("bridge_installed") and not state.get("auxiliary_power_online"):
        add(_entry(
            "activate-power",
            "Activate auxiliary transit power",
            "The induction bridge is seated, but the manual breaker remains open.",
            "At the Auxiliary Power Core, use ACTIVATE POWER or CLOSE BREAKER.",
        ))

    ready_parts = (
        state.get("porter_bound")
        and state.get("auxiliary_power_online")
        and state.get("wafer_installed")
    )
    if ready_parts and not state.get("companion_transit_ready"):
        add(_entry(
            "test-transit",
            "Test the companion envelope",
            "Porter, power, and the calibrated route are connected.",
            "Stand in the Emergency Transit Chamber and use TEST TRANSIT.",
        ))

    if state.get("companion_transit_ready") and not state.get("juno_transformed"):
        add(_entry(
            "return-command",
            "Return to Command",
            "The transit ring can now carry one companion with you.",
            "Return to Mara and Juno in the Command Center. The central lift leads up to the pressure lock.",
        ))
    elif state.get("juno_transformed") and not state.get("juno_defeated"):
        add(_entry(
            "stop-juno",
            "Stop the overtaken security chief",
            "The parasite has taken control of Juno inside Command.",
            "Defeat overtaken Juno. Her attacks are faster in breathable air, but their telegraphs remain readable.",
        ))
    elif state.get("juno_defeated") and not state.get("mara_fate"):
        add(_entry(
            "decide-mara",
            "Decide Mara's fate",
            "Mara was bitten during the fight and understands what may follow.",
            "TALK MARA. Choose whether to seek treatment with her, leave her in Command, or grant the mercy she requests.",
        ))
    elif state.get("mara_fate") == "rescue":
        add(_entry(
            "escort-mara",
            "Evacuate Mara",
            "Mara is following in the final emergency suit, and Porter's companion authorization is active.",
            "With Mara beside you, use TOUCH PORTER from anywhere aboard the satellite.",
        ))
    elif state.get("mara_fate") in {"abandon", "mercy"}:
        add(_entry(
            "depart-wreck",
            "Leave the satellite",
            "Your decision in Command is final.",
            "Use TOUCH PORTER when you are ready to complete the emergency transit.",
        ))

    return tasks


def build_task_log(character):
    tasks = build_tutorial_tasks(character)
    for index, raw in enumerate(list(character.db.task_log or []), start=1):
        if not isinstance(raw, Mapping) or raw.get("status", "active") != "active":
            continue
        tasks.append(
            _entry(
                raw.get("id", f"task-{index}"),
                raw.get("title", "Untitled task"),
                raw.get("summary", raw.get("description", "")),
                raw.get("detail", raw.get("description", "No further information is available.")),
            )
        )
    return tasks


def _number(entries):
    return [{**entry, "number": index} for index, entry in enumerate(entries, start=1)]


def build_journal_payload(character):
    return {
        "revision": JOURNAL_PROTOCOL_REVISION,
        "character": {"id": character.id, "name": character.key},
        "quests": _number(build_quest_log(character)),
        "tasks": _number(build_task_log(character)),
    }


def send_journal_sync(character, session=None):
    payload = build_journal_payload(character)
    if session:
        session.msg(quasar_journal_sync=payload)
    else:
        character.msg(quasar_journal_sync=payload)
    return payload


def format_journal(character, kind, number=None):
    entries = build_quest_log(character) if kind == "quest" else build_task_log(character)
    label = "Quest" if kind == "quest" else "Task"
    if number is not None:
        if number < 1 or number > len(entries):
            return f"You have no active {kind} numbered {number}. Use |w{kind}|n to see the current list."
        entry = entries[number - 1]
        return (
            f"|h|c{label} {number}: {entry['title']}|n\n"
            f"{entry['summary']}\n\n{entry['detail']}"
        )
    if not entries:
        return f"You have no active {kind}s."
    lines = [f"|h|cActive {label}s|n"]
    for index, entry in enumerate(entries, start=1):
        lines.append(f"  |w{index}.|n {entry['title']} \u2014 {entry['summary']}")
    lines.append(f"Use |w{kind} <number>|n or |w{'q' if kind == 'quest' else 't'} <number>|n for details.")
    return "\n".join(lines)
