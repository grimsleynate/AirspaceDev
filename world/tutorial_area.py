"""
Build Quasar's initial nine-room tutorial area.

Run in-game as an administrator with:

    batchcode tutorial_area

This script refuses to run if the tutorial already exists.
"""

from evennia import create_object, search_tag

from typeclasses.exits import Exit
from typeclasses.rooms import Room


AREA_TAG = "tutorial"
AREA_CATEGORY = "quasar_area"
START_TAG = "tutorial_start"


def create_room(key, description, is_start=False):
    """
    Create and tag one tutorial room.
    """

    room = create_object(
        Room,
        key=key,
    )

    room.db.desc = description
    room.tags.add(AREA_TAG, category=AREA_CATEGORY)

    if is_start:
        room.tags.add(START_TAG, category=AREA_CATEGORY)

    return room


def connect(
    first_room,
    second_room,
    first_exit,
    first_alias,
    return_exit,
    return_alias,
):
    """
    Connect two rooms in both directions.

    Evennia exits are one-way, so every two-way connection requires
    two Exit objects.
    """

    create_object(
        Exit,
        key=first_exit,
        aliases=[first_alias],
        location=first_room,
        destination=second_room,
    )

    create_object(
        Exit,
        key=return_exit,
        aliases=[return_alias],
        location=second_room,
        destination=first_room,
    )


# Prevent accidental duplicate builds.
existing_rooms = search_tag(
    AREA_TAG,
    category=AREA_CATEGORY,
)

if existing_rooms:
    raise RuntimeError(
        "The Quasar tutorial area already exists. "
        "The build was stopped to prevent duplicate rooms."
    )


# ---------------------------------------------------------------------
# Create the northern row.
# ---------------------------------------------------------------------

observation_gallery = create_room(
    "Observation Gallery",
    (
        "A reinforced viewport stretches across the outer wall. "
        "Beyond it, distant stars surround the magnificent glow of "
        "a quasar, its radiance fading from blue through green into "
        "brilliant white."
    ),
)

transit_spine = create_room(
    "Transit Spine",
    (
        "This broad passage runs through the northern side of the "
        "complex. Recessed lights divide the polished deck into "
        "orderly lanes beneath suspended directional signs."
    ),
)

navigation_annex = create_room(
    "Navigation Annex",
    (
        "A darkened chamber surrounds an inactive holographic "
        "projection table. Fine points of starlight remain etched "
        "across its glass surface like an unfinished map."
    ),
)


# ---------------------------------------------------------------------
# Create the middle row.
# ---------------------------------------------------------------------

arrival_dock = create_room(
    "Arrival Dock",
    (
        "A sealed gangway rests against the station's outer hull. "
        "Pale guide lights run along the deck toward the interior, "
        "while the structure vibrates softly with distant machinery."
    ),
    is_start=True,
)

orientation_hall = create_room(
    "Orientation Hall",
    (
        "A circular chamber marks the center of the training complex. "
        "Directional symbols glow across the floor, identifying each "
        "adjoining section in crisp blue-white light."
    ),
)

systems_lab = create_room(
    "Systems Lab",
    (
        "Rows of dormant consoles line the walls beneath bundled "
        "conduits and access panels. Their dark displays reflect the "
        "room's cool overhead lighting."
    ),
)


# ---------------------------------------------------------------------
# Create the southern row.
# ---------------------------------------------------------------------

crew_berth = create_room(
    "Crew Berth",
    (
        "Compact bunks and storage compartments occupy the walls of "
        "this quiet residential module. Everything has been secured "
        "for travel, leaving the room clean and undisturbed."
    ),
)

training_deck = create_room(
    "Training Deck",
    (
        "Reinforced flooring and marked boundaries divide this "
        "spacious chamber into practice zones. Target rails and "
        "observation windows stand dormant around its perimeter."
    ),
)

departure_gate = create_room(
    "Departure Gate",
    (
        "Heavy pressure doors dominate the far wall beneath a luminous "
        "departure indicator. The threshold represents the end of the "
        "orientation complex and the beginning of the wider station."
    ),
)


# ---------------------------------------------------------------------
# Connect rooms horizontally.
# ---------------------------------------------------------------------

connect(
    observation_gallery,
    transit_spine,
    "east",
    "e",
    "west",
    "w",
)

connect(
    transit_spine,
    navigation_annex,
    "east",
    "e",
    "west",
    "w",
)

connect(
    arrival_dock,
    orientation_hall,
    "east",
    "e",
    "west",
    "w",
)

connect(
    orientation_hall,
    systems_lab,
    "east",
    "e",
    "west",
    "w",
)

connect(
    crew_berth,
    training_deck,
    "east",
    "e",
    "west",
    "w",
)

connect(
    training_deck,
    departure_gate,
    "east",
    "e",
    "west",
    "w",
)


# ---------------------------------------------------------------------
# Connect rooms vertically.
# ---------------------------------------------------------------------

connect(
    observation_gallery,
    arrival_dock,
    "south",
    "s",
    "north",
    "n",
)

connect(
    arrival_dock,
    crew_berth,
    "south",
    "s",
    "north",
    "n",
)

connect(
    transit_spine,
    orientation_hall,
    "south",
    "s",
    "north",
    "n",
)

connect(
    orientation_hall,
    training_deck,
    "south",
    "s",
    "north",
    "n",
)

connect(
    navigation_annex,
    systems_lab,
    "south",
    "s",
    "north",
    "n",
)

connect(
    systems_lab,
    departure_gate,
    "south",
    "s",
    "north",
    "n",
)


print("Quasar tutorial area created successfully.")
print(f"Arrival Dock database reference: #{arrival_dock.id}")
print("Use that database reference with the teleport command if needed.")