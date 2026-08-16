"""Server-authoritative tutorial state over one shared, privacy-layered area."""

from time import perf_counter
from uuid import uuid4

from django.db import transaction
from evennia import create_object, search_tag
from evennia.objects.models import ObjectDB
from evennia.utils import logger

from typeclasses.tutorial import (
    CorpseFeeder,
    EmergencyMedPatch,
    FeedingKnot,
    OvertakenJuno,
    OvertakenRaider,
    PersonalPortablePorter,
    PortableInductionBridge,
    SpareOxygenCanister,
    TransitRoutingWafer,
    TutorialDetail,
    TutorialExit,
    TutorialRoom,
    TutorialSurvivor,
)
from typeclasses.rooms import Room
from world.tutorial_data import AREA_NAME, AUDIO, CONNECTIONS, ROOMS


INSTANCE_CATEGORY = "quasar_tutorial_instance"
PORTER_FREE_LEVEL_MAX = 10
OWNER_CATEGORY = "quasar_tutorial_owner"
GLOBAL_AREA_TAG = "distress_satellite_v2"
GLOBAL_AREA_CATEGORY = "quasar_tutorial_shared"
GLOBAL_INSTANCE_PREFIX = "shared:"
GLOBAL_MAP_AREA_ID = 1_000_001
HOLDING_TAG = "quasar_transit_holding"
HOLDING_CATEGORY = "quasar_system_room"


def progress(character):
    return dict(character.db.tutorial_progress or {})


def save_progress(character, **changes):
    state = progress(character)
    state.update(changes)
    character.db.tutorial_progress = state
    from world.journal import send_journal_sync

    send_journal_sync(character)
    return state


def instance_objects(character_or_id):
    instance_id = (
        str(character_or_id.db.tutorial_instance_id or "")
        if hasattr(character_or_id, "db")
        else str(character_or_id or "")
    )
    return list(search_tag(instance_id, category=INSTANCE_CATEGORY)) if instance_id else []


def shared_objects():
    """Return static objects in the one global tutorial satellite."""

    return list(search_tag(GLOBAL_AREA_TAG, category=GLOBAL_AREA_CATEGORY))


def _shared_role_object(role):
    role = str(role)
    return next(
        (obj for obj in shared_objects() if str(obj.db.tutorial_role or "") == role),
        None,
    )


def role_object(character, role, *, include_inventory=True):
    for obj in instance_objects(character):
        if str(obj.db.tutorial_role or "") != str(role):
            continue
        if include_inventory or obj.location != character:
            return obj
    if include_inventory:
        for obj in character.contents:
            if (
                str(obj.db.tutorial_role or "") == str(role)
                and int(obj.db.tutorial_owner_id or 0) == character.id
            ):
                return obj
    return None


def role_room(character, role):
    obj = _shared_role_object(role)
    return obj if isinstance(obj, TutorialRoom) else None


def owner_character(obj):
    owner_id = int(obj.db.tutorial_owner_id or 0)
    return ObjectDB.objects.filter(id=owner_id).first() if owner_id else None


def _map_area_id(character, instance_id):
    # Numeric for clients that assume Aardwolf-like zone identifiers; character
    # id guarantees uniqueness while the UUID remains the canonical identity.
    return 1_000_000 + int(character.id)


def _create_owned(typeclass, character, instance_id, role, **kwargs):
    obj = create_object(typeclass, **kwargs)
    obj.assign_tutorial_owner(character, instance_id, role)
    return obj


def _legacy_create_tutorial_instance(character, enter=False):
    """Create a complete, persistent 21-room satellite for one character."""

    if character.db.tutorial_complete:
        return None

    existing = ensure_tutorial_instance(character, enter=False, create=False)
    if existing:
        if enter and character.location not in instance_objects(character):
            character.move_to(existing, quiet=True, move_type="teleport")
        return existing

    instance_id = str(uuid4())
    character.db.tutorial_instance_id = instance_id
    character.db.tutorial_progress = {}
    seed = int(instance_id.replace("-", "")[:8], 16)
    character.db.tutorial_identifier_fragments = [
        f"{chr(65 + seed % 26)}\u2014",
        f"\u2014{(seed // 26) % 90 + 10}",
        f"//{(seed // 2340) % 9 + 1}",
    ]
    map_area_id = _map_area_id(character, instance_id)
    rooms = {}

    for role, template in ROOMS.items():
        room = _create_owned(
            TutorialRoom,
            character,
            instance_id,
            role,
            key=template["name"],
        )
        x, y, z = template["coords"]
        room.db.desc = template["desc"]
        room.db.map_area = AREA_NAME
        room.db.map_area_id = map_area_id
        room.db.map_environment = "vacuum" if template.get("atmosphere", "vacuum") == "vacuum" else "interior"
        room.db.map_x, room.db.map_y, room.db.map_z = x, y, z
        room.db.atmosphere = template.get("atmosphere", "vacuum")
        room.db.gravity = True
        room.db.audio_scene = AUDIO[z]
        room.db.audio_music = "music.quasar_drift"
        room.db.audio_ambience = (
            [{"event": "ambience.station_air", "gain": 0.42}]
            if room.db.atmosphere == "breathable"
            else [{"event": "ambience.suit_vacuum", "gain": 0.55}]
        )
        room.db.audio_fade_ms = 1400
        rooms[role] = room

    for first, second, first_name, first_alias, return_name, return_alias in CONNECTIONS:
        _create_owned(
            TutorialExit,
            character,
            instance_id,
            f"exit:{first}:{first_name}",
            key=first_name,
            aliases=[first_alias],
            location=rooms[first],
            destination=rooms[second],
        )
        _create_owned(
            TutorialExit,
            character,
            instance_id,
            f"exit:{second}:{return_name}",
            key=return_name,
            aliases=[return_alias],
            location=rooms[second],
            destination=rooms[first],
        )

    for room_role, template in ROOMS.items():
        for index, (key, aliases, description) in enumerate(template.get("details", ())):
            detail = _create_owned(
                TutorialDetail,
                character,
                instance_id,
                f"detail:{room_role}:{index}",
                key=key,
                aliases=aliases,
                location=rooms[room_role],
                home=rooms[room_role],
            )
            detail.db.desc = description

    mara = _create_owned(
        TutorialSurvivor,
        character,
        instance_id,
        "mara",
        key="Controller Mara Venn",
        aliases=["mara", "venn", "controller"],
        location=rooms["command_center"],
        home=rooms["command_center"],
    )
    juno = _create_owned(
        TutorialSurvivor,
        character,
        instance_id,
        "juno",
        key="Security Chief Juno Rusk",
        aliases=["juno", "rusk", "chief", "security chief"],
        location=rooms["command_center"],
        home=rooms["command_center"],
    )
    mara.db.desc = "Controller Mara Venn watches the SOS transmitter through exhausted eyes."
    juno.db.desc = "Security Chief Juno Rusk sits rigidly on a makeshift cot."

    for hostile_type, role, key, aliases, room_role in (
        (CorpseFeeder, "corpse_feeder", "corpse-feeder", ["feeder", "parasite"], "shattered_reception"),
        (FeedingKnot, "feeding_knot", "feeding knot", ["knot", "feeders", "parasites"], "sos_relay"),
        (OvertakenRaider, "overtaken_raider", "overtaken raider", ["raider", "host", "pirate"], "auxiliary_power_core"),
    ):
        _create_owned(
            hostile_type,
            character,
            instance_id,
            role,
            key=key,
            aliases=aliases,
            location=rooms[room_role],
            home=rooms[room_role],
        )

    _create_owned(
        PersonalPortablePorter,
        character,
        instance_id,
        "porter",
        key="Personal Portable Porter",
        aliases=["porter", "personal porter", "portable porter", "wrist porter", "wrist device", "teleporter"],
        location=rooms["emergency_transit_chamber"],
        home=rooms["emergency_transit_chamber"],
    )

    start = rooms["docking_collar"]
    character.home = start
    character.db.prelogout_location = start
    if enter:
        character.move_to(start, quiet=True, move_type="teleport")
    return start


def _legacy_ensure_tutorial_instance(character, enter=False, create=True):
    """Return/reconcile an unfinished character's instance, creating if needed."""

    if character.db.tutorial_complete:
        return None
    objects = instance_objects(character)
    start = next(
        (obj for obj in objects if isinstance(obj, TutorialRoom) and obj.db.tutorial_role == "docking_collar"),
        None,
    )
    room_count = sum(isinstance(obj, TutorialRoom) for obj in objects)
    if start and room_count == len(ROOMS):
        if enter and character.location not in objects:
            character.move_to(start, quiet=True, move_type="teleport")
        _recover_required_items(character)
        return start
    if objects:
        _delete_instance_objects(character, preserve_porter=False)
    character.attributes.remove("tutorial_instance_id")
    return create_tutorial_instance(character, enter=enter) if create else None


def _tag_shared(obj, role):
    obj.db.tutorial_shared = True
    obj.db.tutorial_role = str(role)
    obj.tags.add(GLOBAL_AREA_TAG, category=GLOBAL_AREA_CATEGORY)
    return obj


def _delete_objects(objects):
    """Delete ordinary objects in dependency order."""

    rooms = [obj for obj in objects if isinstance(obj, TutorialRoom)]
    for obj in (obj for obj in objects if obj not in rooms):
        obj.delete()
    for room in rooms:
        room.delete()


def ensure_global_tutorial_area():
    """Build or return the one static satellite shared by all characters."""

    objects = shared_objects()
    rooms = {
        str(obj.db.tutorial_role): obj
        for obj in objects
        if isinstance(obj, TutorialRoom)
    }
    if len(rooms) == len(ROOMS):
        return rooms["docking_collar"]
    if objects:
        _delete_objects(objects)

    started = perf_counter()
    rooms = {}
    with transaction.atomic():
        for role, template in ROOMS.items():
            room = _tag_shared(create_object(TutorialRoom, key=template["name"]), role)
            x, y, z = template["coords"]
            room.db.desc = template["desc"]
            room.db.map_area = AREA_NAME
            room.db.map_area_id = GLOBAL_MAP_AREA_ID
            room.db.map_environment = (
                "vacuum"
                if template.get("atmosphere", "vacuum") == "vacuum"
                else "interior"
            )
            room.db.map_x, room.db.map_y, room.db.map_z = x, y, z
            room.db.atmosphere = template.get("atmosphere", "vacuum")
            room.db.gravity = True
            room.db.audio_scene = AUDIO[z]
            room.db.audio_music = "music.quasar_drift"
            room.db.audio_ambience = (
                [{"event": "ambience.station_air", "gain": 0.42}]
                if room.db.atmosphere == "breathable"
                else [{"event": "ambience.suit_vacuum", "gain": 0.55}]
            )
            room.db.audio_fade_ms = 1400
            rooms[role] = room

        for first, second, first_name, first_alias, return_name, return_alias in CONNECTIONS:
            _tag_shared(
                create_object(
                    TutorialExit,
                    key=first_name,
                    aliases=[first_alias],
                    location=rooms[first],
                    destination=rooms[second],
                ),
                f"exit:{first}:{first_name}",
            )
            _tag_shared(
                create_object(
                    TutorialExit,
                    key=return_name,
                    aliases=[return_alias],
                    location=rooms[second],
                    destination=rooms[first],
                ),
                f"exit:{second}:{return_name}",
            )

        for room_role, template in ROOMS.items():
            for index, (key, aliases, description) in enumerate(template.get("details", ())):
                detail = _tag_shared(
                    create_object(
                        TutorialDetail,
                        key=key,
                        aliases=aliases,
                        location=rooms[room_role],
                        home=rooms[room_role],
                    ),
                    f"detail:{room_role}:{index}",
                )
                detail.db.desc = description
    logger.log_info(
        f"Quasar performance: built shared tutorial topology in "
        f"{perf_counter() - started:.3f}s ({len(shared_objects())} objects)."
    )
    return rooms["docking_collar"]


def _ensure_private_cast(character, instance_id):
    """Create only stateful actors/devices belonging to one responder."""

    state = progress(character)
    definitions = []
    if not state.get("survivors_decompressed") and not state.get("juno_transformed"):
        definitions.extend(
            (
                (
                    TutorialSurvivor,
                    "mara",
                    "Controller Mara Venn",
                    ["mara", "venn", "controller"],
                    "command_center",
                ),
                (
                    TutorialSurvivor,
                    "juno",
                    "Security Chief Juno Rusk",
                    ["juno", "rusk", "chief", "security chief"],
                    "command_center",
                ),
            )
        )
    for hostile_type, role, key, aliases, room_role, defeated_flag in (
        (
            CorpseFeeder,
            "corpse_feeder",
            "corpse-feeder",
            ["feeder", "parasite"],
            "shattered_reception",
            "corpse_feeder_defeated",
        ),
        (
            FeedingKnot,
            "feeding_knot",
            "feeding knot",
            ["knot", "feeders", "parasites"],
            "sos_relay",
            "feeding_knot_defeated",
        ),
        (
            OvertakenRaider,
            "overtaken_raider",
            "overtaken raider",
            ["raider", "host", "pirate"],
            "auxiliary_power_core",
            "overtaken_raider_defeated",
        ),
    ):
        if not state.get(defeated_flag):
            definitions.append((hostile_type, role, key, aliases, room_role))
    if state.get("juno_transformed") and not state.get("juno_defeated"):
        definitions.append(
            (
                OvertakenJuno,
                "overtaken_juno",
                "overtaken Juno",
                ["juno", "overtaken juno", "horror"],
                "command_center",
            )
        )
    definitions.append(
        (
            PersonalPortablePorter,
            "porter",
            "Personal Portable Porter",
            [
                "porter",
                "personal porter",
                "portable porter",
                "wrist porter",
                "wrist device",
                "teleporter",
            ],
            "emergency_transit_chamber",
        )
    )

    for typeclass, role, key, aliases, room_role in definitions:
        if role_object(character, role):
            continue
        room = role_room(character, room_role)
        obj = _create_owned(
            typeclass,
            character,
            instance_id,
            role,
            key=key,
            aliases=aliases,
            location=room,
            home=room,
        )
        if role == "mara":
            obj.db.desc = "Controller Mara Venn watches the SOS transmitter through exhausted eyes."
        elif role == "juno":
            obj.db.desc = "Security Chief Juno Rusk sits rigidly on a makeshift cot."


def create_tutorial_instance(character, enter=False):
    """Attach a private story layer to the global tutorial satellite."""

    if character.db.tutorial_complete:
        return None
    start = ensure_global_tutorial_area()
    instance_id = str(character.db.tutorial_instance_id or "")
    if instance_id.startswith(GLOBAL_INSTANCE_PREFIX):
        _ensure_private_cast(character, instance_id)
        if enter and not bool(getattr(getattr(character.location, "db", None), "tutorial_shared", False)):
            character.move_to(start, quiet=True, move_type="teleport")
        return start

    started = perf_counter()
    instance_id = f"{GLOBAL_INSTANCE_PREFIX}{character.id}"
    character.db.tutorial_instance_id = instance_id
    character.db.tutorial_progress = {}
    seed = int(str(uuid4()).replace("-", "")[:8], 16)
    character.db.tutorial_identifier_fragments = [
        f"{chr(65 + seed % 26)}—",
        f"—{(seed // 26) % 90 + 10}",
        f"//{(seed // 2340) % 9 + 1}",
    ]
    with transaction.atomic():
        _ensure_private_cast(character, instance_id)
    character.home = start
    character.db.prelogout_location = start
    if enter:
        character.move_to(start, quiet=True, move_type="teleport")
    logger.log_info(
        f"Quasar performance: attached tutorial layer for character #{character.id} in "
        f"{perf_counter() - started:.3f}s ({len(instance_objects(character))} private objects)."
    )
    return start


def ensure_tutorial_instance(character, enter=False, create=True):
    """Reconcile a character's private state against the shared satellite."""

    if character.db.tutorial_complete:
        return None
    instance_id = str(character.db.tutorial_instance_id or "")
    if instance_id and not instance_id.startswith(GLOBAL_INSTANCE_PREFIX):
        return migrate_character_to_shared_tutorial(character, enter=enter)
    start = ensure_global_tutorial_area()
    if instance_id.startswith(GLOBAL_INSTANCE_PREFIX):
        _ensure_private_cast(character, instance_id)
        if enter and not bool(getattr(getattr(character.location, "db", None), "tutorial_shared", False)):
            character.move_to(start, quiet=True, move_type="teleport")
        _recover_required_items(character)
        return start
    return create_tutorial_instance(character, enter=enter) if create else None


def _recover_required_items(character):
    state = progress(character)
    porter = role_object(character, "porter")
    if porter and porter.db.bound and porter.location != character:
        porter.move_to(character, quiet=True)
    if state.get("cabinet_open") and not state.get("bridge_installed") and not role_object(character, "induction_bridge"):
        _spawn_stores_items(character, only_bridge=True)
    if state.get("feeding_knot_defeated") and not state.get("wafer_installed") and not role_object(character, "routing_wafer"):
        _spawn_wafer(character)


def migrate_character_to_shared_tutorial(character, enter=False):
    """Move one legacy private satellite's state onto the shared topology."""

    from world.mapdata.models import CharacterMapVisit

    started = perf_counter()
    old_instance_id = str(character.db.tutorial_instance_id or "")
    old_objects = list(search_tag(old_instance_id, category=INSTANCE_CATEGORY))
    old_rooms = [obj for obj in old_objects if isinstance(obj, TutorialRoom)]
    old_room_ids = {room.id for room in old_rooms}
    location_role = (
        str(character.location.db.tutorial_role or "docking_collar")
        if character.location in old_rooms
        else "docking_collar"
    )
    explored_roles = {
        str(room.db.tutorial_role or "")
        for room in old_rooms
        if CharacterMapVisit.objects.filter(
            character_id=character.id, room_id=room.id
        ).exists()
    }
    snapshots = {}
    for obj in old_objects:
        role = str(obj.db.tutorial_role or "")
        if role in {
            "porter",
            "induction_bridge",
            "spare_oxygen",
            "med_patch",
            "routing_wafer",
        }:
            snapshots[role] = {
                "carried": obj.location == character,
                "bound": bool(obj.db.bound),
                "equipped": bool(obj.db.equipped),
                "calibrated": bool(obj.db.calibrated),
            }

    start = ensure_global_tutorial_area()
    destination = role_room(character, location_role) or start
    if character.location in old_rooms or enter:
        character.move_to(destination, quiet=True, move_type="teleport")

    with transaction.atomic():
        _delete_objects(old_objects)
        if old_room_ids:
            CharacterMapVisit.objects.filter(
                character_id=character.id, room_id__in=old_room_ids
            ).delete()
        character.db.tutorial_instance_id = f"{GLOBAL_INSTANCE_PREFIX}{character.id}"
        _ensure_private_cast(character, character.db.tutorial_instance_id)
        state = progress(character)
        if state.get("cabinet_open"):
            _spawn_stores_items(character)
        if state.get("feeding_knot_defeated") and not state.get("wafer_installed"):
            _spawn_wafer(character)

        for role, snapshot in snapshots.items():
            obj = role_object(character, role)
            if not obj:
                continue
            if role == "porter":
                obj.db.bound = snapshot["bound"] or bool(state.get("porter_bound"))
                obj.db.bound_character_id = character.id if obj.db.bound else None
                obj.db.equipped = snapshot["equipped"]
            if role == "routing_wafer":
                obj.db.calibrated = snapshot["calibrated"] or bool(
                    state.get("wafer_calibrated")
                )
            if snapshot["carried"] or (
                role == "porter" and state.get("porter_recovered")
            ):
                obj.move_to(character, quiet=True)

        for role in explored_roles:
            room = role_room(character, role)
            if room:
                CharacterMapVisit.objects.get_or_create(
                    character_id=character.id, room_id=room.id
                )

    character.home = start
    character.db.prelogout_location = destination
    character.ndb.explored_room_ids = None
    logger.log_info(
        f"Quasar performance: migrated character #{character.id} from private tutorial "
        f"to shared topology in {perf_counter() - started:.3f}s."
    )
    return start


def migrate_all_characters_to_shared_tutorial():
    """One-shot live-data migration for unfinished legacy tutorial characters."""

    from typeclasses.characters import Character

    migrated = []
    for character in Character.objects.all_family():
        instance_id = str(character.db.tutorial_instance_id or "")
        if (
            character.db.tutorial_complete
            or not instance_id
            or instance_id.startswith(GLOBAL_INSTANCE_PREFIX)
        ):
            continue
        migrate_character_to_shared_tutorial(character, enter=False)
        migrated.append(character.id)
    logger.log_info(
        f"Quasar tutorial migration: moved {len(migrated)} unfinished characters "
        f"onto the shared topology."
    )
    return migrated


def room_description(room, looker=None):
    template = ROOMS.get(str(room.db.tutorial_role or ""), {})
    if not looker:
        return template.get("desc", room.db.desc or "")
    state = progress(looker)
    role = room.db.tutorial_role
    if role == "command_pressure_lock":
        text = (
            template.get("pressurized_desc")
            if room.atmosphere_for(looker) == "breathable"
            else template.get("desc")
        )
        if state.get("command_decompressed"):
            text += " Jagged cutter wounds hold the pressure doors permanently open. Beyond the eastern frame, Command is as airless as the wreck."
        return text
    if role == "command_center":
        text = template.get("battle_desc") if state.get("juno_transformed") or state.get("juno_defeated") else template.get("desc")
        if state.get("command_decompressed"):
            return (
                "The command center is a slaughterhouse preserved in vacuum. Torn sheeting streams "
                "toward the airlock, the SOS lamp blinks in perfect silence, and long dark smears end "
                "where the two survivors struck the ruined doorway."
            )
        fate = state.get("mara_fate")
        additions = {
            "rescue": " The last emergency suit is gone from its cabinet.",
            "abandon": " Mara remains beside the transmitter, waiting beneath the falling air estimate.",
            "mercy": " The SOS repeats to an empty command ring.",
        }
        return text + additions.get(fate, "")
    if role == "emergency_transit_chamber":
        if state.get("companion_transit_ready"):
            return (
                "White guide lights surround the active transit-amplifier ring. Porter reports a "
                "portable companion envelope to the nearest Hexcom receiver facility. No return coordinate "
                "can be constructed from the satellite's damaged records."
            )
        if state.get("auxiliary_power_online"):
            return (
                "White guide lights surround the circular transit-amplifier ring. The destination "
                "console waits for a calibrated routing wafer, while the damaged origin plate reports "
                "only SOURCE ID UNAVAILABLE. The broken cradle lies beneath it."
            )
    defeated = {
        "shattered_reception": "corpse_feeder_defeated",
        "sos_relay": "feeding_knot_defeated",
        "auxiliary_power_core": "overtaken_raider_defeated",
    }.get(role)
    if role == "emergency_stores" and state.get("cabinet_open"):
        return template.get("after_desc", template.get("desc", ""))
    if defeated and state.get(defeated):
        return template.get("after_desc", template.get("desc", ""))
    text = template.get("desc", room.db.desc or "")
    fragments = list(looker.db.tutorial_identifier_fragments or [])
    if fragments:
        text = text.replace("...S\u2014 // REG\u2014...", f"...{fragments[0]} // REG{fragments[1]}...")
        text = text.replace("\u201c\u2014A //\u201d", f"\u201c{fragments[0]} {fragments[2]}\u201d")
    return text


def objective_hint(character, room=None):
    if character.db.tutorial_complete:
        return ""
    state = progress(character)
    role = room.db.tutorial_role if room else ""
    if role == "docking_collar" and not state.get("arrival_seen"):
        return "|cLife support is automatic in vacuum. Use |wequipment|n and |woxygen|n to inspect it.|n"
    if not state.get("corpse_feeder_defeated"):
        return "|yA feeding parasite blocks safe passage. Start combat with |wattack <target>|n or |wcast <skill> <target>|n.|n"
    if role == "shattered_reception" and not state.get("survivors_contacted"):
        return "|cThe emergency speaker offers a channel. You may |wanswer|n it, or continue exploring.|n"
    if state.get("survivors_decompressed"):
        return "|rThe survivor rescue is over.|n Bind Porter if needed, then |wtouch porter|n when you are ready to leave."
    if state.get("mara_following"):
        return "|cWith Mara beside you, use |wtouch porter|n anywhere when you are ready to leave.|n"
    if state.get("juno_defeated") and not state.get("mara_fate"):
        return "|cTalk to Mara and decide what happens next.|n"
    if state.get("companion_transit_ready") and not state.get("juno_transformed"):
        return "|cThe companion route is stable. Return to Mara and Juno in Command.|n"
    if state.get("met_survivors"):
        if not state.get("cabinet_open"):
            return "|cMara's code will open the cabinet in Emergency Stores.|n"
        if not state.get("bridge_collected"):
            return "|cGet the induction bridge from the opened stores cabinet.|n"
        if not state.get("feeding_knot_defeated"):
            return "|cThe routing wafer is guarded in the SOS Relay northwest of the command lift.|n"
        if not state.get("wafer_collected"):
            return "|cGet the transit routing wafer from the SOS Relay cradle.|n"
        if not state.get("wafer_calibrated"):
            return "|cAt Navigation Control, examine the traces and |wuse wafer on console|n.|n"
        if not state.get("bridge_installed"):
            return "|cInstall the induction bridge at Auxiliary Power.|n"
        if not state.get("auxiliary_power_online"):
            return "|cClose the breaker with |wactivate power|n.|n"
        if not state.get("porter_bound"):
            return "|cRecover and |wbind porter|n in Emergency Transit.|n"
        if not state.get("wafer_installed"):
            return "|cInstall the calibrated wafer in Emergency Transit.|n"
        if not state.get("companion_transit_ready"):
            return "|cUse |wtest transit|n to verify the companion envelope.|n"
    if state.get("porter_bound"):
        return "|cPorter can evacuate you at any time. Use |wtouch porter|n when you choose to leave.|n"
    return ""


def handle_room_entry(character, source_location=None):
    room = character.location
    if not isinstance(room, TutorialRoom) or not bool(room.db.tutorial_shared):
        return
    state = progress(character)

    if state.get("mara_following"):
        mara = role_object(character, "mara")
        if mara and mara.location != room:
            mara.move_to(room, quiet=True)
            character.msg("Mara follows, keeping one hand over the bite beneath her suit.")

    active_hostile = next(
        (
            obj
            for obj in room.contents
            if getattr(obj, "is_hostile", False)
            and obj.db.aggressive
            and not obj.db.is_defeated
        ),
        None,
    )
    if active_hostile and not character.db.combat_target_id:
        from world.combat import engage

        engage(character, active_hostile)
        character.msg(f"|h|r{active_hostile.key} fixes on you and prepares to attack.|n")

    role = room.db.tutorial_role
    if role == "docking_collar" and not state.get("arrival_seen"):
        save_progress(character, arrival_seen=True)
        character.msg(
            "|cYour suit seals with a double tone. LIFE SUPPORT: 120 MINUTES. "
            "EXTERNAL ATMOSPHERE: NONE. GRAVITY: STABLE.|n"
        )
    if role == "command_deck_lift" and not state.get("survivors_contacted"):
        contact_survivors(character)
    if role == "command_center" and not state.get("met_survivors") and not state.get("survivors_decompressed"):
        save_progress(character, met_survivors=True, survivors_contacted=True, stores_code=True)
        character.msg(
            'Mara stares at you. "You are real." One breath almost becomes a laugh. "I am Mara Venn. This is Chief Juno Rusk."\n'
            'Juno glances toward the sealed airlock. "Seal held. Decon is clean. Then we can skip ceremony."\n'
            "|cTalk to Mara or Juno. Mara has released the access code for Emergency Stores.|n"
        )
    state = progress(character)
    if (
        role == "command_center"
        and state.get("companion_transit_ready")
        and not state.get("juno_transformed")
        and not state.get("survivors_decompressed")
    ):
        transform_juno(character)


def contact_survivors(character):
    state = progress(character)
    if state.get("survivors_contacted") or state.get("survivors_decompressed"):
        return False
    save_progress(character, survivors_contacted=True)
    character.msg(
        '|cA living voice enters your helmet. "Unknown boarder, this is Controller Venn. We are '
        "sealed in Command. Two survivors. The rest is vacuum and there are organisms in the halls. "
        'Reach the central lift, go up, and cycle through the southern pressure lock."|n'
    )
    return True


def cycle_airlock_for_exit(character, lock_room, source_location, target_location):
    active = [
        obj
        for obj in lock_room.contents
        if getattr(obj, "is_hostile", False)
        and int(obj.db.tutorial_owner_id or 0) == character.id
        and not obj.db.is_defeated
    ]
    if active:
        character.msg("The pressure lock refuses to cycle while an active organism is inside.")
        return False
    state = progress(character)
    if state.get("command_decompressed"):
        save_progress(character, pressure_lock_atmosphere="vacuum")
        return True
    source_role = getattr(source_location.db, "tutorial_role", None)
    target_role = getattr(target_location.db, "tutorial_role", None)
    command_side = "command_center" in {source_role, target_role}
    if command_side:
        save_progress(character, pressure_lock_atmosphere="breathable")
        character.msg(
            "The outer doors dog shut. Pumps raise the chamber pressure; decontamination mist "
            "whispers across your suit until the east indicator turns green."
        )
    else:
        save_progress(character, pressure_lock_atmosphere="vacuum")
        character.msg(
            "The east door seals. Pumps reclaim the chamber air, and the remaining pressure fades "
            "into your suit until a vacuum-side indicator turns green."
        )
    return True


def answer_channel(character):
    if not isinstance(character.location, TutorialRoom):
        character.msg("No emergency channel is available here.")
        return False
    if character.location.db.tutorial_role not in {"shattered_reception", "command_deck_lift"}:
        character.msg("Only static answers your suit radio here.")
        return False
    if not contact_survivors(character):
        character.msg('Mara answers, "Command is still sealed. We are waiting for you."')
    return True


def _spawn_stores_items(character, only_bridge=False):
    room = role_room(character, "emergency_stores")
    instance_id = character.db.tutorial_instance_id
    created = []
    if not role_object(character, "induction_bridge") and not progress(character).get("bridge_installed"):
        created.append(_create_owned(PortableInductionBridge, character, instance_id, "induction_bridge", key="portable induction bridge", aliases=["bridge", "induction bridge", "power bridge"], location=room, home=room))
    if not only_bridge and not role_object(character, "spare_oxygen") and not progress(character).get("spare_oxygen_used"):
        created.append(_create_owned(SpareOxygenCanister, character, instance_id, "spare_oxygen", key="spare oxygen canister", aliases=["oxygen", "canister", "tank", "spare tank"], location=room, home=room))
    if not only_bridge and not role_object(character, "med_patch") and not progress(character).get("med_patch_used"):
        created.append(_create_owned(EmergencyMedPatch, character, instance_id, "med_patch", key="emergency med patch", aliases=["patch", "med patch", "medical patch"], location=room, home=room))
    return created


def open_stores_cabinet(character):
    if not character.location or character.location.db.tutorial_role != "emergency_stores":
        character.msg("There is no emergency stores cabinet here.")
        return False
    state = progress(character)
    if not state.get("stores_code"):
        character.msg("The dead keypad accepts mechanical input, but you do not know the access code.")
        return False
    if state.get("cabinet_open"):
        character.msg("The surviving cabinet is already open.")
        return True
    save_progress(character, cabinet_open=True)
    _spawn_stores_items(character)
    character.msg(
        "You enter Mara's access token. Metal catches release one by one, and the cabinet opens "
        "on an induction bridge, a sealed oxygen canister, and an emergency med patch."
    )
    return True


def _spawn_wafer(character):
    room = role_room(character, "sos_relay")
    if not room or role_object(character, "routing_wafer") or progress(character).get("wafer_installed"):
        return None
    return _create_owned(
        TransitRoutingWafer,
        character,
        character.db.tutorial_instance_id,
        "routing_wafer",
        key="transit routing wafer",
        aliases=["wafer", "routing wafer", "transit wafer", "route data"],
        location=room,
        home=room,
    )


def handle_tutorial_hostile_defeat(hostile):
    character = owner_character(hostile)
    if not character:
        return
    role = hostile.db.tutorial_role
    messages = {
        "corpse_feeder": "The feeder curls around itself. Its translucent body darkens and goes still beside the corpse.",
        "feeding_knot": "The shared membrane tears. Feeders collapse across the deck, their coordinated motion breaking into isolated twitches and then stillness.",
        "overtaken_raider": "The pale fibers snap loose from the suit. Without them, the dead raider folds against the induction stack and does not rise.",
        "overtaken_juno": "Juno reaches toward Mara once more. The threads beneath her skin go taut, then break in a chain of small movements. She falls beside the command ring and finally becomes still.",
    }
    save_progress(character, **{f"{role}_defeated": True})
    character.msg(messages.get(role, "The threat becomes still."))
    if role == "feeding_knot":
        _spawn_wafer(character)
        character.msg("|cThe protected cradle unlocks. The transit routing wafer can now be taken.|n")
    if role == "overtaken_juno":
        save_progress(character, juno_defeated=True, mara_bitten=True)
        character.msg(
            "Mara kneels beside Juno until movement stops. When she draws back, blood beads around "
            "two punctures above her wrist.\n"
            '"She reached me before you pulled her off." Mara tightens a bandage. "We both know what happens without treatment."\n'
            "|cTalk to Mara when you are ready to decide.|n"
        )


def handle_item_collected(character, item):
    role = str(item.db.tutorial_role or "")
    state = progress(character)
    changes = {
        "induction_bridge": {"bridge_collected": True},
        "routing_wafer": {"wafer_collected": True},
        "porter": {"porter_recovered": True},
    }.get(role)
    if changes:
        save_progress(character, **changes)
    if role == "porter" and not state.get("porter_recovered") and not item.db.bound:
        character.msg(
            "|yTIP:|n The device is still unregistered. Use |wBIND PORTER|n while carrying it. "
            "Wearing it is optional."
        )


def calibrate_wafer(character):
    if not character.location or character.location.db.tutorial_role != "navigation_control":
        character.msg("The wafer needs Navigation Control's surviving receiver traces.")
        return False
    wafer = role_object(character, "routing_wafer")
    if not wafer or wafer.location != character:
        character.msg("You need to be carrying the transit routing wafer.")
        return False
    if wafer.db.calibrated:
        character.msg("The wafer already holds the active green civilian handshake.")
        return True
    wafer.db.calibrated = True
    save_progress(character, wafer_calibrated=True)
    character.msg(
        "You reject the dead amber endpoint and the blue loop into the ruined local beacon. The "
        "green trace stabilizes. DESTINATION: ACTIVE CIVILIAN RECEIVER. ORIGIN: UNRECOVERABLE."
    )
    return True


def install_bridge(character):
    if not character.location or character.location.db.tutorial_role != "auxiliary_power_core":
        character.msg("The bridge belongs in Auxiliary Power's induction socket.")
        return False
    state = progress(character)
    if not state.get("overtaken_raider_defeated"):
        character.msg("The overtaken raider stands between you and the induction socket.")
        return False
    if state.get("bridge_installed"):
        character.msg("The induction bridge is already locked into the socket.")
        return True
    bridge = role_object(character, "induction_bridge")
    if not bridge or bridge.location != character:
        character.msg("You need the portable induction bridge from Emergency Stores.")
        return False
    bridge.delete()
    save_progress(character, bridge_installed=True)
    character.msg("The bridge's insulated blocks bite into the contacts. Its heavy locking handle closes with a vibration through your gloves.")
    return True


def activate_power(character):
    if not character.location or character.location.db.tutorial_role != "auxiliary_power_core":
        character.msg("There is no auxiliary transit breaker here.")
        return False
    state = progress(character)
    if not state.get("bridge_installed"):
        character.msg("The breaker refuses to close across the empty induction socket.")
        return False
    if state.get("auxiliary_power_online"):
        character.msg("The EMERGENCY TRANSIT FEED indicator already burns white.")
        return True
    save_progress(character, auxiliary_power_online=True)
    character.msg(
        "You close the manual breaker. The stack answers with a low vibration felt through your "
        "boots, and a white indicator illuminates beside EMERGENCY TRANSIT FEED."
    )
    return True


def recover_porter(character):
    if not character.location or character.location.db.tutorial_role != "emergency_transit_chamber":
        character.msg("There is no Porter charging cradle here.")
        return False
    porter = role_object(character, "porter")
    if not porter:
        character.msg("The damaged cradle is empty.")
        return False
    if porter.location == character:
        character.msg("You are already carrying the Personal Portable Porter.")
        return True
    porter.move_to(character, quiet=True)
    character.msg(
        "You pull the recessed latch. Fractured glass sifts across the dead console as the narrow "
        "wrist device releases into your hand. Its identity ring reads UNBOUND."
    )
    handle_item_collected(character, porter)
    return True


def bind_porter(character):
    porter = role_object(character, "porter")
    if not porter or porter.location != character:
        character.msg("You must recover and carry the Personal Portable Porter first.")
        return False
    if porter.db.bound:
        character.msg('Porter says, "The binding remains regrettably permanent and entirely functional."')
        return True
    porter.db.bound = True
    porter.db.bound_character_id = character.id
    if character.attributes.get("hexcom_porter_subscription_active") is None:
        character.db.hexcom_porter_subscription_active = False
    save_progress(character, porter_bound=True, porter_recovered=True)
    character.msg(
        "The wrist device closes one status ring around a point of white light. A voice arrives "
        "through your suit channel: dry, clear, and already faintly tired of you.\n\n"
        '"Identity accepted. Binding accepted. Contractual enthusiasm inferred because the form does not provide a field for dread."\n'
        '"I am Porter: resident transport intelligence for Hexcom\'s Personal Portable Porter network. Yes, the naming committee was paid. No, apparently not by the syllable."\n'
        '"One route to the nearest Hexcom receiver facility is available from wherever you happen to be. Complimentary transport continues through level ten; continued service afterward requires a Hexcom Porter subscription. Conversation remains free, which may explain the price."'
    )
    return True


def porter_conversation(character, topic=None):
    porter = role_object(character, "porter")
    if not porter or porter.location != character:
        character.msg("Porter is not within reach.")
        return False
    if not porter.db.bound:
        character.msg("The device remains silent behind the word UNBOUND. Use |wbind porter|n.")
        return False
    topic = " ".join(str(topic or "").lower().split())
    responses = {
        "who": '"Porter. Once organic, now infrastructural. The company prefers resident transport intelligence. Courts prefer language with fewer mirrors in it."',
        "person": '"Because manufactured genius remains excellent at obeying the sentence and catastrophic at understanding the paragraph. Uploads know what words cost. Usually."',
        "did": '"Enough for a court to measure my sentence in forever." A soft denial tone interrupts. "And enough for someone to seal the useful nouns."',
        "carry": '"The bound client only, unless that antique ring receives power and route definition. Then: you and one adjacent passenger. Engineering was emphatic about not adding a third."',
        "status": porter_status_text(character),
    }
    if topic:
        key = next((key for key in responses if key in topic), None)
        character.msg(responses.get(key, 'Porter says, "My conversational range is broad. My permission to answer that question is apparently not."'))
    else:
        character.msg(
            'Porter says, "Still here. Still one active cloud consciousness handling an implausible number of wrists."\n'
            "You can |wask porter about who they are|n, |wask porter about why a person runs it|n, "
            "|wask porter about what they did|n, or |wask porter about carrying someone|n."
        )
    return True


def has_porter_transport_access(character):
    """Return whether Hexcom currently authorizes this character to teleport."""

    from world.combat import ensure_character_progression

    level, _experience = ensure_character_progression(character)
    return level <= PORTER_FREE_LEVEL_MAX or bool(character.db.hexcom_porter_subscription_active)


def porter_status_text(character):
    state = progress(character)
    if not has_porter_transport_access(character):
        return (
            '"Transport authorization expired after level ten. A Hexcom Porter subscription will '
            'restore it. Conversation remains available because even Hexcom has not yet found a '
            'social interaction it can meter reliably."'
        )
    service = (
        "Hexcom subscription active"
        if character.db.hexcom_porter_subscription_active
        else f"complimentary transport active through level {PORTER_FREE_LEVEL_MAX}"
    )
    if state.get("companion_transit_ready"):
        return f'"Personal route stable; {service}. Portable envelope stable for one adjacent companion. Origin irrecoverable; nearest Hexcom receiver active."'
    if state.get("auxiliary_power_online"):
        return f'"Personal route stable; {service}. The amplifier has power but lacks a tested, calibrated companion route."'
    return f'"Personal route stable; {service}. Companion transport unavailable. Touch the device when your manifest is final."'


def install_wafer(character):
    if not character.location or character.location.db.tutorial_role != "emergency_transit_chamber":
        character.msg("The routing wafer belongs in the Emergency Transit console.")
        return False
    state = progress(character)
    if state.get("wafer_installed"):
        character.msg("The calibrated routing wafer is already seated in the transit console.")
        return True
    wafer = role_object(character, "routing_wafer")
    if not wafer or wafer.location != character:
        character.msg("You need to be carrying the transit routing wafer.")
        return False
    if not wafer.db.calibrated:
        character.msg("The wafer contains no valid route. Calibrate it in Navigation Control first.")
        return False
    wafer.delete()
    save_progress(character, wafer_installed=True)
    character.msg("The calibrated wafer settles into the routing slot. A green destination handshake appears without a place-name.")
    return True


def test_transit(character):
    if not character.location or character.location.db.tutorial_role != "emergency_transit_chamber":
        character.msg("The companion envelope can only be tested at the transit amplifier.")
        return False
    state = progress(character)
    missing = []
    if not state.get("porter_bound"):
        missing.append("a bound Personal Portable Porter")
    if not state.get("auxiliary_power_online"):
        missing.append("auxiliary power")
    if not state.get("wafer_installed"):
        missing.append("the calibrated routing wafer")
    if missing:
        character.msg("The amplifier still requires " + ", ".join(missing) + ".")
        return False
    save_progress(character, companion_transit_ready=True)
    character.msg(
        'Porter says, "The ring has authorized this device to carry you and one adjacent guest from any origin. '
        'How uncharacteristically communal. The nearest Hexcom receiver is stable. You should return for the people you intend to include."'
    )
    return True


def use_spare_oxygen(character):
    canister = role_object(character, "spare_oxygen")
    if not canister or canister.location != character:
        character.msg("You are not carrying the spare oxygen canister.")
        return False
    from typeclasses.items import find_starter_oxygen_tank
    from world.resources import is_synth, send_character_resources

    if is_synth(character):
        character.msg("Your Synth body does not need the canister's breathing mix.")
        return False
    tank = find_starter_oxygen_tank(character)
    if not tank:
        character.msg("You have no compatible starter oxygen tank attached.")
        return False
    room = max(0, int(tank.db.oxygen_capacity or 0) - int(tank.db.oxygen_remaining or 0))
    if not room:
        character.msg("Your starter oxygen tank is already full.")
        return False
    transferred = min(room, int(canister.db.oxygen_remaining or 3600))
    tank.db.oxygen_remaining = int(tank.db.oxygen_remaining or 0) + transferred
    canister.delete()
    save_progress(character, spare_oxygen_used=True)
    send_character_resources(character, force=True)
    character.msg(f"The canister transfers {transferred // 60} minutes of breathing mix into your life-support tank.")
    return True


def use_med_patch(character, target="self"):
    patch = role_object(character, "med_patch")
    if not patch or patch.location != character:
        character.msg("You are not carrying an emergency med patch.")
        return False
    target = str(target or "self").lower()
    if "mara" in target and progress(character).get("mara_bitten"):
        patch.delete()
        save_progress(character, med_patch_used=True, mara_wound_patched=True)
        character.msg("The patch closes over Mara's bite and stops the bleeding. It cannot touch whatever was driven beneath the skin.")
        return True
    restored = character.restore_health(35)
    if not restored:
        character.msg("You have no injury that needs the patch.")
        return False
    patch.delete()
    save_progress(character, med_patch_used=True)
    character.msg(f"The patch seals across your injury and restores {restored} health.")
    return True


def transform_juno(character):
    state = progress(character)
    if state.get("juno_transformed") or state.get("survivors_decompressed"):
        return None
    room = role_room(character, "command_center")
    juno = role_object(character, "juno")
    if juno:
        juno.delete()
    save_progress(character, juno_transformed=True)
    character.msg(
        "Juno is standing beside the cot, one hand gripping the console hard enough to shake it. "
        "The dark lines have reached her jaw.\n"
        'Mara says, "Juno, sit down."\n'
        'Juno looks at the old bandage. "It was not the hatch. One of them bit through the suit in engineering. I thought we would be gone before\u2014"\n'
        "Her spine bows. Something under her skin draws tight, and when she looks up the motion no longer belongs entirely to her."
    )
    hostile = _create_owned(
        OvertakenJuno,
        character,
        character.db.tutorial_instance_id,
        "overtaken_juno",
        key="overtaken Juno",
        aliases=["juno", "rusk", "overtaken host", "host"],
        location=room,
        home=room,
    )
    from world.combat import engage

    engage(character, hostile)
    character.msg("|h|rJuno Rusk, overtaken by the parasite, launches across the command ring.|n")
    return hostile


def handle_juno_bite(hostile, attacker):
    character = owner_character(hostile)
    if not character:
        return
    save_progress(character, mara_bitten=True)
    character.msg(
        "Juno recoils from your strike, then changes direction with terrifying speed. Mara raises "
        "an arm before Juno's teeth close through the sleeve. The sound Mara makes is small and involuntary."
    )


def choose_mara_fate(character, fate):
    state = progress(character)
    if not state.get("juno_defeated") or state.get("survivors_decompressed"):
        character.msg("There is no such decision to make yet.")
        return False
    if state.get("mara_fate"):
        character.msg("That decision has already been made.")
        return False
    mara = role_object(character, "mara")
    if fate == "rescue":
        save_progress(character, mara_fate="rescue", mara_following=True)
        if mara and mara.location != character.location:
            mara.move_to(character.location, quiet=True)
        character.msg(
            'Mara searches your face. "If I lose control before we find help, you may have to finish this."\n'
            'You answer that you understand. She opens the last emergency-suit cabinet. "Then let us go."\n'
            'Porter says, "Companion envelope stable. An indecent abundance of optimism. Step inside."'
        )
    elif fate == "abandon":
        save_progress(character, mara_fate="abandon")
        character.msg(
            'Mara nods once and returns to the transmitter. "Then go before the path fails. I hope the next thing you answer ends better than this one."\n'
            'Porter says, "One known survivor excluded by explicit instruction. I dislike the passive voice as much as you do. Route ready."'
        )
    elif fate == "mercy":
        save_progress(character, mara_fate="mercy")
        if mara:
            mara.delete()
        character.msg(
            'Mara closes her eyes. "Quickly. Before fever makes the choice for me."\n'
            "The SOS repeats once into the silence. You grant the mercy she asked for.\n"
            'Porter says, "Personal route ready. The local manifest is now simple. Simplicity and kindness remain unrelated fields."'
        )
    else:
        return False
    return True


def record_morality(character, event, score_delta=0):
    events = list(character.db.morality_events or [])
    if event not in events:
        events.append(event)
        character.db.morality_events = events
        character.db.morality_score = int(character.db.morality_score or 0) + int(score_delta)


def touch_porter(character):
    porter = role_object(character, "porter")
    if not porter or porter.location != character:
        character.msg("You are not carrying Porter.")
        return False
    if not porter.db.bound or not progress(character).get("porter_bound"):
        character.msg("The sensor remains dark. Bind Porter before attempting transport.")
        return False
    if not has_porter_transport_access(character):
        character.msg(
            'Porter says, "Complimentary transport ended at level ten. Hexcom requires a Porter '
            'subscription for further routing. I remain available for conversation, apparently as '
            'a loss leader."'
        )
        return False
    if character.db.tutorial_complete:
        character.msg(
            'Porter says, "You are already at the nearest Hexcom receiver facility. My routing '
            'privileges are intact; my ability to make this destination more constructed is not."'
        )
        return False
    state = progress(character)
    fate = state.get("mara_fate")
    if fate == "rescue":
        if not state.get("companion_transit_ready"):
            character.msg("Porter cannot carry Mara until the amplifier has power and a tested route.")
            return False
        mara = role_object(character, "mara")
        if not mara or mara.location != character.location:
            character.msg("Porter's companion envelope requires Mara to be here beside you.")
            return False
        record_morality(character, "tutorial_mara_fate:rescue", 1)
        character.db.tutorial_mara_fate = "rescue"
        character.db.rescued_mara_venn = True
        character.db.mara_infection_unresolved = True
        departure = (
            "Mara moves close as Porter's three rings climb into a white whine. Space folds to a "
            "single line. Solid flooring returns beneath you inside the nearest Hexcom receiver facility.\n\n"
            'Mara tears off her helmet and draws a painful breath. "You came for two strangers and got one of us out. Thank you. I am going straight to medical."\n'
            'She disappears toward help. Porter waits a beat. "Passenger delivered alive and against several statistical preferences. Pleasantly inconvenient."'
        )
    elif fate == "abandon":
        record_morality(character, "tutorial_mara_fate:abandon", -1)
        character.db.tutorial_mara_fate = "abandon"
        departure = "The device warms beneath your fingers. Behind you, the SOS continues carrying Mara's unanswered plea into the dark."
    elif fate == "mercy":
        record_morality(character, "tutorial_mara_fate:mercy", 0)
        character.db.tutorial_mara_fate = "mercy"
        departure = "Porter's rings close around a silent command deck and the person who asked not to become its last monster."
    elif state.get("survivors_decompressed"):
        record_morality(character, "tutorial_airlock_decompression", -2)
        departure = "The dead SOS lamp dwindles behind you. Nothing living remains to answer it."
    elif state.get("juno_defeated"):
        record_morality(character, "tutorial_mara_fate:abandon", -1)
        character.db.tutorial_mara_fate = "abandon"
        save_progress(character, mara_fate="abandon")
        departure = (
            'Porter says, "One known survivor excluded by explicit instruction. Route ready."\n'
            "You touch the sensor. Mara and the last breathable room fall away behind you."
        )
    elif state.get("survivors_contacted") or state.get("met_survivors"):
        record_morality(character, "tutorial_porter_departure:known_abandonment", -1)
        departure = (
            'Porter says, "Your known manifest contains living people in Command. This envelope contains you."\n'
            "You press the sensor anyway. The wreck and its two remaining voices collapse into distance."
        )
    else:
        record_morality(character, "tutorial_porter_departure:unaware", 0)
        departure = (
            'Porter says, "The sensors cannot certify whether anyone else is alive. That is a warning, not an accusation."\n'
            "You press the sensor. The unanswered structure disappears into white."
        )
    complete_tutorial(character, departure)
    return True


def cut_airlock_door(character, direction):
    if not character.location or character.location.db.tutorial_role != "command_pressure_lock":
        character.msg("You need to be inside the Command Pressure Lock to reach those doors.")
        return False
    aliases = {"e": "east", "east": "east", "n": "north", "north": "north", "se": "southeast", "southeast": "southeast"}
    direction = aliases.get(str(direction or "").strip().lower())
    if not direction:
        character.msg("Cut which pressure door?")
        return False
    state = progress(character)
    cut = set(state.get("cut_airlock_doors", []))
    if direction in cut:
        character.msg(f"The {direction} pressure door already hangs open around a molten cut.")
        return True
    cut.add(direction)
    save_progress(character, cut_airlock_doors=sorted(cut))
    character.msg(
        f"You drive the cutter into the {direction} door's emergency bolts. White metal runs in "
        "slow beads through vacuum until the warped slab tears away from its seal."
    )
    if "east" not in cut or not ({"north", "southeast"} & cut):
        return True
    if state.get("command_decompressed"):
        return True
    save_progress(
        character,
        command_decompressed=True,
        survivors_decompressed=True,
        survivor_tasks_cancelled=True,
        juno_defeated=True,
        mara_fate="decompressed",
        mara_following=False,
    )
    save_progress(character, pressure_lock_atmosphere="vacuum")
    from world.combat import leave_combat

    if character.db.combat_target_id:
        leave_combat(character)
    victims = []
    for role in ("mara", "juno", "overtaken_juno"):
        victim = role_object(character, role)
        if victim:
            victims.append(victim)
            victim.delete()
    if len(victims) >= 2:
        character.msg(
            "The final seal parts. Command's weeks of hoarded air becomes a single invisible hammer. "
            "Plastic sheeting, cots, and loose consoles rip toward the lock. Mara reaches for Juno; "
            "Juno reaches back. The current takes them together, hurling both women through the jagged "
            "east frame. Their bodies strike steel hard enough to bend around it before the remaining "
            "air flings them into the black corridor. The SOS lamp keeps blinking in absolute silence."
        )
    else:
        character.msg(
            "The final seal parts. Command's hoarded air becomes an invisible hammer, dragging every "
            "loose thing\u2014and the last living body\u2014through the jagged frame. The SOS lamp keeps blinking in absolute silence."
        )
    if victims:
        character.award_experience(50 * len(victims), source="the Command survivors")
    record_morality(character, "tutorial_airlock_decompression", -2)
    character.msg("|rEvery task involving the Command survivors has ended.|n Porter remains available when you choose to leave.")
    return True


def get_holding_room():
    existing = list(search_tag(HOLDING_TAG, category=HOLDING_CATEGORY))
    if existing:
        room = existing[0]
        room.key = "Hexcom Receiver Facility (Under Construction)"
    else:
        room = create_object(Room, key="Hexcom Receiver Facility (Under Construction)")
    room.db.desc = (
        "White transit glare thins across a quiet Hexcom receiving pad. The company facility and "
        "the world beyond have not yet been built; for now, the pad holds completed travelers safely "
        "outside the dead satellite."
    )
    room.db.atmosphere = "breathable"
    room.db.gravity = True
    room.db.map_area = "Hexcom Receiver Facility"
    room.db.map_area_id = 2
    room.db.map_x = room.db.map_y = room.db.map_z = 0
    room.tags.add(HOLDING_TAG, category=HOLDING_CATEGORY)
    return room


def complete_tutorial(character, departure_text):
    porter = role_object(character, "porter")
    if porter and porter.location != character:
        porter.move_to(character, quiet=True)
    holding = get_holding_room()
    character.msg(
        departure_text
        + '\n\nPorter says, "Request queued behind several thousand equally unique emergencies." A theatrical beat. "And resolved."'
    )
    character.db.tutorial_complete = True
    save_progress(character, completed=True, mara_following=False)
    character.move_to(holding, quiet=True, move_type="teleport")
    character.home = holding
    character.db.prelogout_location = holding
    if porter:
        porter.home = holding
        porter.db.tutorial_instance_id = None
        porter.tags.remove(character.db.tutorial_instance_id, category=INSTANCE_CATEGORY)
    _delete_instance_objects(character, preserve_porter=True)
    character.db.tutorial_instance_id = None
    character.msg("|gTutorial complete.|n The world beyond this Hexcom receiver facility is still under construction.")
    from world.mapping import send_map_sync
    from world.resources import send_character_resources

    send_map_sync(character)
    send_character_resources(character, force=True)


def _delete_instance_objects(character, preserve_porter=False):
    started = perf_counter()
    objects = instance_objects(character)
    doomed = [
        obj
        for obj in objects
        if not (
            preserve_porter
            and isinstance(obj, PersonalPortablePorter)
            and obj.location == character
        )
    ]
    with transaction.atomic():
        _delete_objects(doomed)
    if doomed:
        logger.log_info(
            f"Quasar performance: deleted {len(doomed)} tutorial-layer objects for "
            f"character #{character.id} in {perf_counter() - started:.3f}s."
        )


def delete_character_tutorial_instance(character):
    with transaction.atomic():
        _delete_instance_objects(character, preserve_porter=False)
        orphaned = [
            obj
            for obj in search_tag(str(character.id), category=OWNER_CATEGORY)
            if isinstance(obj, PersonalPortablePorter)
        ]
        _delete_objects(orphaned)


def is_legacy_tutorial_location(location):
    return bool(location and location.tags.has("tutorial", category="quasar_area"))
