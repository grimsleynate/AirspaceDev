"""Idempotent installation of the temporary tutorial combat proving ground."""

from evennia import create_object, search_tag

from typeclasses.npcs import ScavengerParasite, TrainingDrone


CONTENT_CATEGORY = "quasar_tutorial"

COMBATANTS = (
    (
        "training_drone",
        TrainingDrone,
        "training security drone",
        ["drone", "training drone"],
    ),
    (
        "contained_parasite",
        ScavengerParasite,
        "contained scavenger parasite",
        ["parasite", "scavenger"],
    ),
)


def reconcile_tutorial_combatants(room):
    """Create or relocate one of each repeatable training opponent."""

    results = []
    for tag_key, typeclass, key, aliases in COMBATANTS:
        matches = list(search_tag(tag_key, category=CONTENT_CATEGORY))
        combatant = (
            matches[0]
            if matches
            else create_object(typeclass, key=key, aliases=aliases)
        )
        combatant.location = room
        combatant.home = room
        combatant.tags.add(tag_key, category=CONTENT_CATEGORY)
        combatant.db.respawn_seconds = 20
        results.append(combatant)
    return results


def reconcile_existing_tutorial_combatants():
    """Install the proving ground when the tagged legacy Training Deck exists."""

    rooms = list(search_tag("tutorial", category="quasar_area"))
    training_deck = next((room for room in rooms if room.key == "Training Deck"), None)
    return reconcile_tutorial_combatants(training_deck) if training_deck else []
