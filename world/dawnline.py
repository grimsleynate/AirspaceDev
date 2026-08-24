"""Idempotent builder for Dawnline's opening district and private footholds."""

from evennia import create_object, search_tag

from typeclasses.exits import Exit
from typeclasses.items import PortableItem
from typeclasses.objects import InspectableScenery
from typeclasses.opening_tutorial import BoundPorter
from typeclasses.rooms import Room

AREA_TAG = "dawnline_opening_district_v1"
AREA_CATEGORY = "quasar_world_area"
CITY_TAG_CATEGORY = "quasar_city"
PRIVATE_CATEGORY = "quasar_dawnline_room_owner"
PORTER_CATEGORY = "quasar_porter_owner"
ORIGIN_ITEM_CATEGORY = "quasar_origin_item_owner"
MAP_AREA_ID = 3101

ROOMS = {
    "hotel_hall": ("Wayfarers' Hotel Hall", (0, 0, 1), "A curved hotel corridor overlooks the traffic lanes through a programmable wall. Its carpet is clean, thin, and patterned to conceal luggage-wheel scars."),
    "lantern_row_w": ("Lantern Row — Hotel Block", (0, 0, 0), "Modest hotels, bathhouses, fitted-body laundries, and sleep clinics share a sheltered pedestrian block under thousands of practical lamps."),
    "lantern_row_e": ("Lantern Row — Wayhouse Steps", (1, 0, 0), "The row broadens around a public threshold where travelers exchange route warnings and hospitality tokens."),
    "crosswind_w": ("Crosswind Avenue — West", (0, 1, 0), "Pressurized trams whisper above a broad avenue. Human battery signage competes with native weather-charms and neither system owns the street."),
    "crosswind_c": ("Crosswind Avenue — Central", (1, 1, 0), "Traffic from the docks, Return House, and market crosses beneath an old convoy hull built permanently into Dawnline's frame."),
    "crosswind_e": ("Crosswind Avenue — East", (2, 1, 0), "The avenue bends toward workshops and the distant construction glare of Heimdall."),
    "return_forecourt": ("Return House Forecourt", (0, 2, 0), "A calm plaza surrounds Dawnline's registered Return House. Arrival circles are kept clear even when every bench is occupied."),
    "return_lobby": ("Dawnline Return House", (0, 3, 0), "Nested rings mark receiving pads, coverage desks, and medical alcoves. Porter traffic is treated as public infrastructure with a customer-service smile."),
    "market_w": ("Many-Suns Market — Provisioners", (1, 2, 0), "Stalls sell pressure brine, spectrum cloth, bearer-safe adhesives, thermal stone, sensory-crest braces, Human coffee, and several things advertised as coffee."),
    "market_e": ("Many-Suns Market — Tool Arcade", (2, 2, 0), "Toolmongers demonstrate mining heads beside ritual foci and psionic privacy screens. Every warranty has learned local pessimism."),
    "contract_square": ("Contract Square", (1, 3, 0), "Job boards, union tables, petitioners, and recruiters occupy a square designed to make promises visible before they become debts."),
    "archive_lane": ("Archive Lane", (2, 3, 0), "Evidence houses and public memory booths line a narrow lane. Several façades preserve Icarus hull numbers without claiming the ships arrived intact."),
    "foundry_steps": ("Foundry Steps", (3, 2, 0), "Broad heat-stained steps climb between fabrication halls. Crews carry components whose technical traditions do not share a common vocabulary."),
    "rigger_walk": ("Rigger Walk", (3, 1, 0), "A reinforced pedestrian span runs toward the gateworks. Memorial fasteners interrupt the handrail wherever a name was available."),
    "heimdall_overlook": ("Heimdall Overlook", (4, 1, 0), "Beyond armored glass, Heimdall hangs unfinished: Human equations, Oruun loadwork, Nimri field speech, Serev testimony, Kaelith resonance, and Veyari attention practice forced into one impossible machine."),
    "dockward_gate": ("Dockward Gate", (-1, 1, 0), "Cargo lanes descend toward berths and small frontier ships. A departure board contains more delays than destinations."),
    "orison_kiosk": ("Orison Security Kiosk", (-1, 2, 0), "A public incident board offers paid work against dangerous fauna, violent claim crews, and problems classified only as moving."),
    "survey_office": ("Unverified Line Survey Office", (2, 4, 0), "Hand-corrected charts cover a cooperative office wall. A blinking discrepancy waits for someone willing to discover why the last survey did not agree with itself."),
}

CONNECTIONS = (
    ("hotel_hall", "lantern_row_w", "down", "d", "up", "u"),
    ("lantern_row_w", "lantern_row_e", "east", "e", "west", "w"),
    ("lantern_row_w", "crosswind_w", "north", "n", "south", "s"),
    ("lantern_row_e", "crosswind_c", "north", "n", "south", "s"),
    ("crosswind_w", "crosswind_c", "east", "e", "west", "w"),
    ("crosswind_c", "crosswind_e", "east", "e", "west", "w"),
    ("crosswind_w", "return_forecourt", "north", "n", "south", "s"),
    ("return_forecourt", "return_lobby", "north", "n", "south", "s"),
    ("crosswind_c", "market_w", "north", "n", "south", "s"),
    ("crosswind_e", "market_e", "north", "n", "south", "s"),
    ("market_w", "market_e", "east", "e", "west", "w"),
    ("market_w", "contract_square", "north", "n", "south", "s"),
    ("market_e", "archive_lane", "north", "n", "south", "s"),
    ("contract_square", "archive_lane", "east", "e", "west", "w"),
    ("market_e", "foundry_steps", "east", "e", "west", "w"),
    ("crosswind_e", "rigger_walk", "east", "e", "west", "w"),
    ("rigger_walk", "heimdall_overlook", "east", "e", "west", "w"),
    ("crosswind_w", "dockward_gate", "west", "w", "east", "e"),
    ("dockward_gate", "orison_kiosk", "north", "n", "south", "s"),
    ("archive_lane", "survey_office", "north", "n", "south", "s"),
)


def _shared_objects():
    return list(search_tag(AREA_TAG, category=AREA_CATEGORY))


def _tag(obj, role):
    obj.db.dawnline_role = role
    obj.tags.add(AREA_TAG, category=AREA_CATEGORY)
    return obj


def _connect(rooms, first, second, first_key, first_alias, return_key, return_alias, existing=None):
    existing = existing if existing is not None else {}
    outward_role = f"exit:{first}:{first_key}"
    return_role = f"exit:{second}:{return_key}"
    for role, key, alias, location, destination in (
        (outward_role, first_key, first_alias, rooms[first], rooms[second]),
        (return_role, return_key, return_alias, rooms[second], rooms[first]),
    ):
        exit_obj = existing.get(role)
        if not isinstance(exit_obj, Exit):
            exit_obj = _tag(create_object(Exit, key=key, aliases=[alias], location=location, destination=destination), role)
            existing[role] = exit_obj
        else:
            exit_obj.key = key
            exit_obj.location = location
            exit_obj.destination = destination
            exit_obj.aliases.clear()
            exit_obj.aliases.add(alias)


def ensure_dawnline():
    """Build the shared 18-room walkable opening district exactly once."""

    existing = _shared_objects()
    rooms = {str(obj.db.dawnline_role): obj for obj in existing if isinstance(obj, Room)}
    existing_by_role = {str(obj.db.dawnline_role): obj for obj in existing}
    for role, (name, coords, desc) in ROOMS.items():
        room = rooms.get(role) or _tag(create_object(Room, key=name), role)
        room.key = name
        room.db.desc = desc
        room.db.map_area = "Dawnline — Opening District"
        room.db.map_area_id = MAP_AREA_ID
        room.db.map_x, room.db.map_y, room.db.map_z = coords
        room.db.map_environment = "station_city"
        room.db.city_key = "dawnline"
        room.db.city_role = role
        room.tags.add("dawnline", category=CITY_TAG_CATEGORY)
        rooms[role] = room
    for row in CONNECTIONS:
        _connect(rooms, *row, existing=existing_by_role)
    rooms["market_w"].db.spectrum_desc = (
        "Ordinary stall heat separates from a fading ultraviolet route mark. It points toward Archive Lane, "
        "then has been painted over in a pigment that only pretends to be opaque."
    )
    rooms["heimdall_overlook"].db.resonance_desc = (
        "Heimdall's frame answers in several incompatible harmonics. One quiet structural member carries load "
        "from no visible assembly, as though the unfinished Gate is braced against somewhere else."
    )
    details = {
        "return_lobby": ("coverage board", "Porter coverage is registered here. Missed payments generate reminders and ads; they do not cancel continuity protection."),
        "heimdall_overlook": ("Heimdall", "The incomplete gateway is not a Human gift to Andromeda. It is a coalition machine no people could finish alone."),
        "contract_square": ("job boards", "Three current headings stand out: FIGHT near Orison, EXPLORE an Unverified Line discrepancy, or WORK on Heimdall supply contracts."),
    }
    for role, (key, desc) in details.items():
        detail_role = f"detail:{role}:{key}"
        detail = existing_by_role.get(detail_role)
        detail = detail or _tag(create_object(InspectableScenery, key=key, location=rooms[role], home=rooms[role]), detail_role)
        detail.key = key
        detail.location = rooms[role]
        detail.home = rooms[role]
        detail.db.desc = desc
    return rooms


def ensure_personal_room(character):
    """Create one private reconnect room linked to the public hotel hall."""

    tagged = list(search_tag(str(character.id), category=PRIVATE_CATEGORY))
    public = ensure_dawnline()["hotel_hall"]
    room = next((obj for obj in tagged if isinstance(obj, Room)), None)
    human = character.db.species == "human"
    if not room:
        room = create_object(Room, key="A Modest Dawnline Hotel Room" if human else "Your Dawnline Room")
        room.tags.add(str(character.id), category=PRIVATE_CATEGORY)
    room.key = "A Modest Dawnline Hotel Room" if human else "Your Dawnline Room"
    room.db.dawnline_private_owner_id = character.id
    room.locks.add(f"view:id({character.id});search:id({character.id})")
    room.db.map_area = "Dawnline — Private Rooms"
    room.db.map_area_id = 3_200_000 + character.id
    room.db.map_x = room.db.map_y = room.db.map_z = 0
    room.db.desc = (
        "Cheap station dawn leaks through a programmable window. Your luggage is where you left it, your account is nearly empty, and a bound Personal Porter waits on its charging rest. Nothing from the Icarus dream is here."
        if human else
        "Morning light adjusts itself to your senses and fitted furnishings. This modest room is a foothold rather than a final home; Porter waits beside the belongings you carried back from the frontier."
    )
    private_by_role = {str(obj.db.dawnline_private_role): obj for obj in tagged}
    exit_out = private_by_role.get("exit_out") or next(
        (obj for obj in tagged if isinstance(obj, Exit) and obj.location == room and obj.destination == public), None
    )
    if not isinstance(exit_out, Exit):
        exit_out = create_object(Exit, key="out", aliases=["o", "hall"], location=room, destination=public)
        exit_out.tags.add(str(character.id), category=PRIVATE_CATEGORY)
    exit_out.db.dawnline_private_role = "exit_out"
    exit_out.location, exit_out.destination = room, public
    exit_in = private_by_role.get("exit_in") or next(
        (obj for obj in tagged if isinstance(obj, Exit) and obj.location == public and obj.destination == room), None
    )
    if not isinstance(exit_in, Exit):
        exit_in = create_object(Exit, key=f"room {character.id}", aliases=["my room"], location=public, destination=room)
        exit_in.tags.add(str(character.id), category=PRIVATE_CATEGORY)
    exit_in.db.dawnline_private_role = "exit_in"
    exit_in.location, exit_in.destination = public, room
    exit_in.locks.add(f"cmd:id({character.id});view:id({character.id});traverse:id({character.id})")
    for key, desc in (("bed", "A practical reconnect point with enough comfort to make leaving optional for several minutes."), ("window", "Dawnline fills the view: convoy metal, native stonework, market light, and Heimdall's unfinished glare.")):
        detail_role = f"detail:{key}"
        detail = private_by_role.get(detail_role) or next(
            (obj for obj in tagged if isinstance(obj, InspectableScenery) and obj.key.lower() == key), None
        )
        if not isinstance(detail, InspectableScenery):
            detail = create_object(InspectableScenery, key=key, location=room, home=room)
            detail.tags.add(str(character.id), category=PRIVATE_CATEGORY)
        detail.db.dawnline_private_role = detail_role
        detail.location, detail.home = room, room
        detail.db.desc = desc
        detail.locks.add(f"view:id({character.id});search:id({character.id})")
    character.db.next_leads = ["fight:orison", "explore:unverified_line", "work:heimdall"]
    return room


def ensure_bound_porter(character):
    """Create the first literal Porter for Humans or recover the native one."""

    character.db.porter_binding = {
        "bound": True,
        "bound_to_id": character.id,
        "coverage": "Dawnline Return House",
        "billing_status": "introductory service",
        "permadeath_enabled": False,
    }
    character.db.permadeath_enabled = False
    carried = next((obj for obj in character.contents if isinstance(obj, BoundPorter)), None)
    if carried:
        carried.db.bound = True
        carried.db.bound_to_id = character.id
        carried.home = ensure_personal_room(character)
        carried.tags.add(str(character.id), category=PORTER_CATEGORY)
        return carried
    existing = list(search_tag(str(character.id), category=PORTER_CATEGORY))
    porter = existing[0] if existing else create_object(BoundPorter, key="Personal Porter", aliases=["porter", "watch"], location=character, home=ensure_personal_room(character))
    if porter.location != character:
        porter.move_to(character, quiet=True, move_type="teleport")
    porter.tags.add(str(character.id), category=PORTER_CATEGORY)
    porter.db.bound = True
    porter.db.bound_to_id = character.id
    return porter


def ensure_origin_possessions(character):
    """Materialize only the low-power origin items dictated by current choices."""

    from world.character_options import BACKGROUNDS, SPECIES, apply_background, apply_species

    species = SPECIES.get(character.db.species, {})
    background = BACKGROUNDS.get(character.db.background, {})
    if species:
        apply_species(character, character.db.species)
    if background:
        apply_background(character, character.db.background)

    desired = []
    for source, catalog in (("species", species), ("background", background)):
        item_data = catalog.get("item")
        if item_data:
            desired.append((source, item_data))

    owner_tag = str(character.id)
    existing = list(search_tag(owner_tag, category=ORIGIN_ITEM_CATEGORY))
    desired_keys = {data["key"] for _source, data in desired}
    for item in existing:
        if str(item.db.origin_item_key or "") not in desired_keys:
            item.delete()

    created = {}
    room = ensure_personal_room(character)
    for source, data in desired:
        item = next((obj for obj in existing if obj.db.origin_item_key == data["key"]), None)
        if not item:
            item = create_object(PortableItem, key=data["name"], location=character, home=room)
            item.tags.add(owner_tag, category=ORIGIN_ITEM_CATEGORY)
        elif item.location not in (character, room):
            item.move_to(character, quiet=True)
        item.key = data["name"]
        item.home = room
        item.db.desc = data["description"]
        item.db.origin_item_key = data["key"]
        item.db.origin_item_source = source
        item.db.origin_owner_id = character.id
        created[source] = item
    character.db.origin_possession_keys = sorted(desired_keys)
    return created


def ensure_background_possession(character):
    """Compatibility wrapper used by tutorial convergence."""

    return ensure_origin_possessions(character).get("background")


def delete_character_dawnline_assets(character):
    """Remove the private room, Porter terminal, and Background reward."""

    for porter in list(search_tag(str(character.id), category=PORTER_CATEGORY)):
        porter.delete()
    for item in list(search_tag(str(character.id), category=ORIGIN_ITEM_CATEGORY)):
        item.delete()
    possession_tag = str(character.db.background_possession_tag or "")
    if possession_tag:
        for item in list(search_tag(possession_tag, category="quasar_background_possession")):
            item.delete()
    tagged = list(search_tag(str(character.id), category=PRIVATE_CATEGORY))
    rooms = [obj for obj in tagged if isinstance(obj, Room)]
    for obj in tagged:
        if obj not in rooms:
            obj.delete()
    for room in rooms:
        room.delete()
