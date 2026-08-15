"""Build or upgrade Quasar's multi-deck tutorial station.

Run in-game as an administrator with ``batchcode tutorial_area``. The build is
idempotent: existing tagged rooms are updated and missing content is created.
"""

from evennia import create_object, search_tag

from typeclasses.exits import Exit
from typeclasses.items import TutorialAccessBadge
from typeclasses.npcs import OrientationGuide
from typeclasses.rooms import Room

AREA_TAG = "tutorial"
AREA_CATEGORY = "quasar_area"
AREA_NAME = "Quasar Orientation Annex"
AREA_ID = 1
START_TAG = "tutorial_start"
CONTENT_CATEGORY = "quasar_tutorial"

# Irregular coordinates make the station feel constructed rather than gridded.
# Different z values are separate decks in the web mapper.
ROOMS = {
    "Arrival Dock": ((-3, 0, 0), "A telescoping gangway clamps to the satellite's outer docking collar. Amber pressure lights chase toward a decontamination lock to the east, while the deck hums faintly beneath your boots."),
    "Decontamination Lock": ((-2, 0, 0), "Curved nozzles and sensor arches crowd this short pressure chamber. The sharp scent of filtered air gives way to the warmer station interior."),
    "Orientation Hall": ((-1, 0, 0), "A crescent-shaped reception area overlooks a slowly turning model of the satellite. Blue floor lighting leads east, while a narrower passage angles southwest."),
    "Transit Spine": ((0, 0, 0), "The satellite's main transit spine widens around a structural column webbed with conduits. Branch corridors depart at uneven angles toward sensors, systems, and lifts."),
    "Navigation Annex": ((1, 1, 0), "A bank of navigation displays follows the curve of the hull. Dim route projections trace the satellite's orbit and the distant lanes beyond it."),
    "Sensor Walk": ((2, 2, 0), "A narrow diagonal gallery passes between shielded sensor housings. Their status lights pulse in patient sequence toward the observation cupola."),
    "Observation Gallery": ((3, 2, 0), "A reinforced viewport frames the magnificent blaze of a distant quasar. Its radiance fades from electric blue through ghostly green into a white-hot heart."),
    "Systems Lab": ((1, -1, 0), "Diagnostic benches surround exposed teaching rigs. Every cable is color-coded, and safe training faults blink across a wall of simplified system diagrams."),
    "Power Monitoring": ((2, -1, 0), "Transparent panels reveal redundant power buses descending toward engineering. Meters whisper through their checks beneath a steady green readiness light."),
    "Cargo Checkpoint": ((-2, -1, 0), "Scanner hoops divide the concourse from a compact cargo branch. Yellow deck marks curve southwest around stacked inspection pallets."),
    "Supply Cage": ((-3, -2, 0), "Mesh lockers hold orientation equipment, emergency fabric, and sealed tool rolls. A blue-white access badge rests conspicuously on the issue counter."),
    "Lift Lobby": ((0, 1, 0), "Three lift shafts pierce the satellite's central axis. One car waits with controls for the operations deck above and engineering deck below."),
    "Operations Lift": ((0, 1, 1), "The lift opens onto a quiet upper-deck vestibule. A command ring curves south, while a relay accessway cuts northwest between dense signal trunks."),
    "Command Ring": ((0, 0, 1), "Unoccupied duty stations arc around a central holotable. Every console holds a calm standby pattern."),
    "Telemetry Alcove": ((1, 0, 1), "Live telemetry scrolls across tall glass displays. Tiny delays and course corrections make the satellite's seemingly motionless orbit feel alive."),
    "Crew Berth": ((1, -1, 1), "Compact sleep capsules and personal lockers follow the outer curve of the operations deck. Privacy screens glow softly in the otherwise quiet berth."),
    "Relay Control": ((-1, 2, 1), "Shielded racks translate a storm of distant transmissions into orderly streams. The deck vibrates whenever the primary dish realigns."),
    "Engineering Lift": ((0, 1, -1), "Warm air and a bass mechanical thrum greet the lift on the lower deck. Service stripes lead south toward maintenance passages."),
    "Maintenance Gallery": ((0, 0, -1), "Access hatches line a low gallery beneath bundled coolant pipes. A marked evacuation route angles southeast toward the station's departure facilities."),
    "Training Deck": ((-1, -1, -1), "A reinforced compartment holds marked practice lanes and inactive safety simulators. Observation glass separates it from the maintenance gallery."),
    "Departure Gate": ((1, -1, -1), "A compact shuttle vestibule sits behind heavy pressure doors. Beyond the inspection line lies the route out of orientation and into the wider station network."),
}

CONNECTIONS = (
    ("Arrival Dock", "Decontamination Lock", "east", "e", "west", "w"),
    ("Decontamination Lock", "Orientation Hall", "east", "e", "west", "w"),
    ("Orientation Hall", "Transit Spine", "east", "e", "west", "w"),
    ("Orientation Hall", "Cargo Checkpoint", "southwest", "sw", "northeast", "ne"),
    ("Cargo Checkpoint", "Supply Cage", "southwest", "sw", "northeast", "ne"),
    ("Transit Spine", "Navigation Annex", "northeast", "ne", "southwest", "sw"),
    ("Navigation Annex", "Sensor Walk", "northeast", "ne", "southwest", "sw"),
    ("Sensor Walk", "Observation Gallery", "east", "e", "west", "w"),
    ("Transit Spine", "Systems Lab", "southeast", "se", "northwest", "nw"),
    ("Systems Lab", "Power Monitoring", "east", "e", "west", "w"),
    ("Transit Spine", "Lift Lobby", "north", "n", "south", "s"),
    ("Lift Lobby", "Operations Lift", "up", "u", "down", "d"),
    ("Operations Lift", "Command Ring", "south", "s", "north", "n"),
    ("Command Ring", "Telemetry Alcove", "east", "e", "west", "w"),
    ("Command Ring", "Crew Berth", "southeast", "se", "northwest", "nw"),
    ("Operations Lift", "Relay Control", "northwest", "nw", "southeast", "se"),
    ("Lift Lobby", "Engineering Lift", "down", "d", "up", "u"),
    ("Engineering Lift", "Maintenance Gallery", "south", "s", "north", "n"),
    ("Maintenance Gallery", "Training Deck", "southwest", "sw", "northeast", "ne"),
    ("Maintenance Gallery", "Departure Gate", "southeast", "se", "northwest", "nw"),
)

DIRECTION_VECTORS = {
    "north": (0, 1, 0), "northeast": (1, 1, 0), "east": (1, 0, 0),
    "southeast": (1, -1, 0), "south": (0, -1, 0), "southwest": (-1, -1, 0),
    "west": (-1, 0, 0), "northwest": (-1, 1, 0), "up": (0, 0, 1), "down": (0, 0, -1),
}

# Refuse to build a direction/coordinate disagreement. Connector handles come
# from the exit name while node placement comes from coordinates, so allowing
# those two sources to diverge produces a visually crooked map.
for first, second, first_exit, _first_alias, _return_exit, _return_alias in CONNECTIONS:
    origin = ROOMS[first][0]
    destination = ROOMS[second][0]
    vector = DIRECTION_VECTORS[first_exit]
    expected = tuple(origin[index] + vector[index] for index in range(3))
    if destination != expected:
        raise RuntimeError(
            f"Tutorial map mismatch: {second} is {first_exit} of {first}, "
            f"so its coordinates must be {expected}, not {destination}."
        )


def tagged(key):
    return list(search_tag(key, category=CONTENT_CATEGORY))


existing = {room.key: room for room in search_tag(AREA_TAG, category=AREA_CATEGORY)}
rooms = {}
created_count = 0
for room_name, (coordinates, description) in ROOMS.items():
    room = existing.get(room_name)
    if not room:
        room = create_object(Room, key=room_name)
        created_count += 1
    room.db.desc = description
    room.db.map_area = AREA_NAME
    room.db.map_area_id = AREA_ID
    room.db.map_environment = "satellite interior"
    room.db.map_x, room.db.map_y, room.db.map_z = coordinates
    room.tags.add(AREA_TAG, category=AREA_CATEGORY)
    if room_name == "Arrival Dock":
        room.tags.add(START_TAG, category=AREA_CATEGORY)
    else:
        room.tags.remove(START_TAG, category=AREA_CATEGORY)
    rooms[room_name] = room

# Replace only internal tutorial links. This removes the old 3x3 grid while
# preserving future exits that lead from this station into the wider game.
for room in rooms.values():
    for exit_obj in list(room.exits):
        if exit_obj.destination and exit_obj.destination.tags.has(AREA_TAG, category=AREA_CATEGORY):
            exit_obj.delete()

for first, second, first_exit, first_alias, return_exit, return_alias in CONNECTIONS:
    create_object(Exit, key=first_exit, aliases=[first_alias], location=rooms[first], destination=rooms[second])
    create_object(Exit, key=return_exit, aliases=[return_alias], location=rooms[second], destination=rooms[first])

guides = tagged("orientation_guide")
guide = guides[0] if guides else create_object(OrientationGuide, key="Guide Lumen", aliases=["guide", "lumen"])
guide.location = rooms["Orientation Hall"]
guide.home = rooms["Orientation Hall"]
guide.db.desc = "A patient station guide in a slate-blue uniform stands beside the orientation display. A luminous name strip identifies them as Guide Lumen."
guide.tags.add("orientation_guide", category=CONTENT_CATEGORY)

badges = tagged("orientation_badge")
if badges:
    badge = badges[0]
else:
    badge = create_object(TutorialAccessBadge, key="orientation access badge", aliases=["badge", "access badge"], location=rooms["Supply Cage"], home=rooms["Supply Cage"])
badge.tags.add("orientation_badge", category=CONTENT_CATEGORY)

print(f"Quasar tutorial station ready: {len(rooms)} rooms ({created_count} newly created).")
print(f"Start room: Arrival Dock (#{rooms['Arrival Dock'].id})")
print("Guide Lumen and the orientation access badge are ready.")
