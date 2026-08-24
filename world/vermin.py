"""Reusable, city-scoped ambient vermin spawning."""

from collections import Counter
from random import choice
from time import time

from evennia import create_object, search_tag

from typeclasses.rooms import Room
from typeclasses.vermin import CityVermin, VerminCarcass


CITY_TAG_CATEGORY = "quasar_city"
VERMIN_CITY_CATEGORY = "quasar_vermin_city"

CITY_PROFILES = {
    "dawnline": {
        "name": "Dawnline",
        "population": 6,
        "excluded_rooms": {"hotel_hall", "return_lobby", "orison_kiosk"},
        "vermin": (
            {
                "key": "wiregrazer",
                "name": "copper-toothed wiregrazer",
                "aliases": ("wiregrazer", "grazer", "vermin"),
                "desc": "A palm-long hexapod lies nearly flat against the deck, shaving bright curls from cable insulation with rotating copper teeth.",
                "corpse_desc": "The flat hexapod is dead, its copper dental wheels clogged with insulation. Municipal abatement marks wiregrazers as a low-value bounty.",
                "health": 22,
                "evasion": 1,
                "attack": "a snapping cable-tooth bite",
                "bounty": 2,
            },
            {
                "key": "brine_skitter",
                "name": "blue brine-skitter",
                "aliases": ("brine-skitter", "skitter", "vermin"),
                "desc": "A translucent, many-legged hitchhiker cups a leaking pipe joint, drinking pressure brine while its blue organs pulse in warning.",
                "corpse_desc": "The brine-skitter has collapsed into a blue, translucent knot. Its shell carries the assay stamp used for a small abatement bounty.",
                "health": 24,
                "evasion": 3,
                "attack": "a scissoring foreclaw",
                "bounty": 3,
            },
            {
                "key": "echo_jackdaw",
                "name": "echo jackdaw",
                "aliases": ("jackdaw", "bird", "vermin"),
                "desc": "A soot-feathered little scavenger watches from deck level. Its throat clicks through stolen door chimes while one clever foot worries a luminous fastener loose.",
                "corpse_desc": "The jackdaw's soot-dark feathers still catch stray station light. Abatement pays reluctantly for proof that it will steal no more signal hardware.",
                "health": 20,
                "evasion": 6,
                "attack": "a darting beak-and-talon strike",
                "bounty": 2,
            },
        ),
    }
}


def city_rooms(city_key):
    """Return spawnable rooms registered to one city."""

    profile = CITY_PROFILES.get(city_key, {})
    excluded = set(profile.get("excluded_rooms", ()))
    return [
        room
        for room in search_tag(city_key, category=CITY_TAG_CATEGORY)
        if isinstance(room, Room)
        and str(room.db.dawnline_role or room.db.city_role or "") not in excluded
    ]


def city_vermin(city_key, include_defeated=True):
    """Return all spawned vermin belonging to one city."""

    vermin = [
        obj
        for obj in search_tag(city_key, category=VERMIN_CITY_CATEGORY)
        if isinstance(obj, CityVermin)
    ]
    if include_defeated:
        return vermin
    return [obj for obj in vermin if not obj.db.is_defeated]


def visible_vermin(room):
    """Return living vermin currently present in a room."""

    return [
        obj
        for obj in getattr(room, "contents", ())
        if isinstance(obj, CityVermin) and not obj.db.is_defeated
    ]


def notify_vermin_presence(character, vermin=None):
    """Send the optional awareness alert without hiding normal room content."""

    if not bool(character.db.vermin_awareness) or not character.location:
        return False
    present = list(vermin or visible_vermin(character.location))
    if not present:
        return False
    names = ", ".join(obj.get_display_name(character) for obj in present)
    character.msg(f"|yVermin awareness:|n {names} {('are' if len(present) != 1 else 'is')} nearby.")
    return True


def spawn_city_vermin(city_key, room, definition):
    """Spawn and fully configure one weak hostile from a city profile."""

    vermin = create_object(
        CityVermin,
        key=definition["name"],
        aliases=list(definition.get("aliases", ())),
        location=room,
        home=room,
    )
    vermin.db.vermin_city = city_key
    vermin.db.vermin_species = definition["key"]
    vermin.db.health_max = int(definition.get("health", 22))
    vermin.db.health_current = vermin.db.health_max
    vermin.db.evasion = int(definition.get("evasion", 2))
    vermin.db.attack_name = definition.get("attack", "a desperate bite")
    vermin.db.desc = definition["desc"]
    vermin.db.corpse_desc = definition.get("corpse_desc", "")
    vermin.db.vermin_bounty = int(definition.get("bounty", 1))
    vermin.tags.add(city_key, category=VERMIN_CITY_CATEGORY)
    for occupant in room.contents:
        if hasattr(occupant, "inventory_items"):
            notify_vermin_presence(occupant, vermin=[vermin])
    return vermin


def cleanup_city_vermin(city_key, now=None):
    """Remove defeated bodies and expired carcasses without touching live mobs."""

    now = time() if now is None else float(now)
    removed = 0
    for obj in list(search_tag(city_key, category=VERMIN_CITY_CATEGORY)):
        if isinstance(obj, CityVermin):
            if obj.db.is_defeated and float(obj.db.despawn_at or 0) <= now:
                obj.delete()
                removed += 1
        elif isinstance(obj, VerminCarcass) and float(obj.db.expires_at or 0) <= now:
            obj.delete()
            removed += 1
    return removed


def maintain_city_vermin(city_key, chooser=choice, now=None):
    """Reconcile one city's capped population and return newly spawned mobs."""

    profile = CITY_PROFILES.get(city_key)
    if not profile:
        return []
    cleanup_city_vermin(city_key, now=now)
    rooms = city_rooms(city_key)
    target = min(int(profile.get("population", 0)), len(rooms))
    allowed = set(rooms)

    # Persistent worlds drift: builders move objects, caps change, rooms are
    # retired, and an interrupted deployment may leave duplicates. Reconcile
    # those states before filling shortages so protected rooms never become a
    # permanent vermin habitat.
    for mob in city_vermin(city_key):
        if mob.location not in allowed:
            mob.delete()

    keepers = []
    occupied = set()
    for mob in sorted(
        city_vermin(city_key, include_defeated=False), key=lambda obj: obj.id
    ):
        if mob.location in occupied or len(keepers) >= target:
            mob.delete()
            continue
        keepers.append(mob)
        occupied.add(mob.location)

    living = keepers
    available = [room for room in rooms if room not in occupied]
    counts = Counter(str(obj.db.vermin_species or "") for obj in living)
    spawned = []
    while len(living) + len(spawned) < target and available:
        room = chooser(available)
        available.remove(room)
        definitions = tuple(profile.get("vermin", ()))
        if not definitions:
            break
        least = min(counts.get(row["key"], 0) for row in definitions)
        candidates = [row for row in definitions if counts.get(row["key"], 0) == least]
        definition = chooser(candidates)
        mob = spawn_city_vermin(city_key, room, definition)
        spawned.append(mob)
        counts[definition["key"]] += 1
    return spawned


def maintain_vermin_population(now=None):
    """Reconcile every registered city profile."""

    return {
        city_key: maintain_city_vermin(city_key, now=now)
        for city_key in CITY_PROFILES
    }
