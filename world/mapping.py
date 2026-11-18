"""Server-authoritative mapping services."""

from evennia.objects.models import ObjectDB

from world.mapdata.models import CharacterMapVisit


MAP_PROTOCOL_REVISION = 1


def explored_room_ids(character, refresh=False):
    """Return the character's explored IDs, cached only while it is active."""

    cached = character.ndb.explored_room_ids
    if cached is None or refresh:
        cached = set(
            CharacterMapVisit.objects.filter(character_id=character.id).values_list(
                "room_id", flat=True
            )
        )
        character.ndb.explored_room_ids = cached
    return cached


def record_room_visit(character, room):
    """Persist a first visit immediately; familiar movement performs no write."""

    if not character or not character.id or not room or not room.id:
        return False

    known = explored_room_ids(character)
    if room.id in known:
        return False

    _visit, created = CharacterMapVisit.objects.get_or_create(
        character_id=character.id,
        room_id=room.id,
    )
    known.add(room.id)
    if created:
        from world.achievements import track_achievement

        track_achievement(
            character,
            category="explore",
            tracking=str(room.db.map_area or "Uncharted"),
        )
    return created


def clear_character_map(character, keep_current=True):
    """Forget this character's exploration, optionally retaining its location."""

    CharacterMapVisit.objects.filter(character_id=character.id).delete()
    character.ndb.explored_room_ids = set()
    if keep_current and character.location:
        record_room_visit(character, character.location)


def build_map_sync(character):
    """Build an authoritative snapshot for the character's current area."""

    current = character.location
    if not current or not hasattr(current, "get_room_info"):
        return {
            "revision": MAP_PROTOCOL_REVISION,
            "character": {"id": character.id, "name": character.key},
            "current": None,
            "area": None,
            "rooms": [],
        }

    record_room_visit(character, current)
    area = current.db.map_area or "Uncharted"
    room_ids = explored_room_ids(character)
    rooms = []
    valid_ids = set()

    for room in ObjectDB.objects.filter(id__in=room_ids).order_by("id"):
        if not hasattr(room, "get_room_info"):
            continue
        valid_ids.add(room.id)
        if (room.db.map_area or "Uncharted") == area:
            rooms.append(room.get_room_info(character))

    # Remove visits whose rooms no longer exist or are no longer rooms.
    stale_ids = room_ids - valid_ids
    if stale_ids:
        CharacterMapVisit.objects.filter(
            character_id=character.id, room_id__in=stale_ids
        ).delete()
        room_ids.difference_update(stale_ids)

    return {
        "revision": MAP_PROTOCOL_REVISION,
        "character": {"id": character.id, "name": character.key},
        "current": current.id,
        "area": area,
        "rooms": rooms,
    }


def send_map_sync(character):
    """Send a per-character area snapshot through GMCP/JSON."""

    character.msg(benben_map_sync=build_map_sync(character))
