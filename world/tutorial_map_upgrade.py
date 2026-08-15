"""
Backfill mapper metadata on an already-built tutorial area.

This is safe to run more than once. In game, an administrator can run:

    batchcode tutorial_map_upgrade
"""

from evennia import search_tag


AREA_TAG = "tutorial"
AREA_CATEGORY = "quasar_area"
AREA_NAME = "Quasar Orientation Complex"
AREA_ID = 1
ENVIRONMENT = "station interior"

ROOM_COORDINATES = {
    "Observation Gallery": (-1, 1, 0),
    "Transit Spine": (0, 1, 0),
    "Navigation Annex": (1, 1, 0),
    "Arrival Dock": (-1, 0, 0),
    "Orientation Hall": (0, 0, 0),
    "Systems Lab": (1, 0, 0),
    "Crew Berth": (-1, -1, 0),
    "Training Deck": (0, -1, 0),
    "Departure Gate": (1, -1, 0),
}


rooms = search_tag(AREA_TAG, category=AREA_CATEGORY)
rooms_by_name = {room.key: room for room in rooms}
missing_rooms = sorted(set(ROOM_COORDINATES) - set(rooms_by_name))

if missing_rooms:
    raise RuntimeError(
        "Could not update the tutorial map because these rooms are missing: "
        + ", ".join(missing_rooms)
    )

for room_name, coordinates in ROOM_COORDINATES.items():
    room = rooms_by_name[room_name]
    room.db.map_area = AREA_NAME
    room.db.map_area_id = AREA_ID
    room.db.map_environment = ENVIRONMENT
    room.db.map_x, room.db.map_y, room.db.map_z = coordinates

print(f"Mapper metadata updated on {len(ROOM_COORDINATES)} tutorial rooms.")
