"""Trusted, declarative ambience attached to rooms by semantic effect id.

Builders assign ``room.db.room_effect_ids``.  Database values never contain
CSS, media paths, or executable behavior: this registry resolves known ids
into a small wire format understood by Quasar's native client.
"""

from collections.abc import Mapping


ROOM_EFFECTS_PROTOCOL_REVISION = 1


ROOM_EFFECTS = {
    "wayhouse.frontier_night": {
        "periods": {"night"},
        "visual": {"preset": "frontier_wayhouse", "intensity": 0.82},
    },
    "wayhouse.low_wind": {
        "periods": {"night"},
        "audio": [{"event": "ambience.wayhouse_wind", "gain": 0.28}],
    },
    "wayhouse.electric_lamps": {
        "visual": {
            "preset": "electric_flicker",
            "intensity": 0.38,
            # Matches the authored twelve-second hum loop so ballast dropouts
            # and visible dimming share one cadence after scene entry.
            "period_ms": 12_000,
        },
        "audio": [{"event": "ambience.wayhouse_lamps", "gain": 0.32}],
    },
    "wayhouse.night_insects": {
        "periods": {"night"},
        "visual": {"preset": "night_insects", "intensity": 0.62},
        "audio": [{"event": "ambience.wayhouse_insects", "gain": 0.24}],
    },
}


def _room_period(room):
    """Return a builder-controlled local period, defaulting safely to day."""

    period = str(getattr(getattr(room, "db", None), "room_effect_period", "") or "day")
    return period.lower() if period.lower() in {"day", "night"} else "day"


def _effect_ids(room):
    value = getattr(getattr(room, "db", None), "room_effect_ids", None)
    if isinstance(value, str):
        value = [value]
    elif isinstance(value, Mapping) or not hasattr(value, "__iter__"):
        return []
    return [str(effect_id) for effect_id in (value or [])]


def _active_definitions(room):
    period = _room_period(room)
    for effect_id in _effect_ids(room):
        definition = ROOM_EFFECTS.get(effect_id)
        if not definition:
            continue
        periods = definition.get("periods")
        if periods and period not in periods:
            continue
        yield effect_id, definition


def build_room_effects(room):
    """Build the native-client payload for a room's active visual effects."""

    effects = []
    for effect_id, definition in _active_definitions(room):
        visual = definition.get("visual")
        if not isinstance(visual, Mapping):
            continue
        effect = {"id": effect_id, "visual": dict(visual)}
        effects.append(effect)
    return {
        "revision": ROOM_EFFECTS_PROTOCOL_REVISION,
        "room": getattr(room, "id", None),
        "period": _room_period(room) if room else "day",
        "effects": effects,
    }


def room_effect_audio_layers(room):
    """Return semantic audio layers contributed by active room effects."""

    layers = []
    for _, definition in _active_definitions(room):
        for layer in definition.get("audio", []):
            if isinstance(layer, Mapping):
                layers.append(dict(layer))
    return layers


def _supported_sessions(character):
    if not character:
        return []
    return [
        session
        for session in character.sessions.all()
        if getattr(session, "protocol_flags", {}).get("QUASAR_ROOM_EFFECTS")
    ]


def send_room_effects(character, session=None, force=False):
    """Synchronize the active room ambience to one or all native clients."""

    payload = build_room_effects(character.location if character else None)
    cleared = build_room_effects(None)
    targets = [session] if session else _supported_sessions(character)
    for target in targets:
        from world.accessibility import room_media_enabled

        target_payload = payload if room_media_enabled(character, target) else cleared
        flags = getattr(target, "protocol_flags", {})
        if not force and flags.get("QUASAR_ROOM_EFFECTS_SCENE") == target_payload:
            continue
        flags["QUASAR_ROOM_EFFECTS_SCENE"] = target_payload
        target.msg(quasar_room_effects_sync=target_payload)
    return payload


def clear_room_effects(session):
    """Clear visual ambience when a session leaves character play."""

    payload = build_room_effects(None)
    getattr(session, "protocol_flags", {}).pop("QUASAR_ROOM_EFFECTS_SCENE", None)
    session.msg(quasar_room_effects_sync=payload)
    return payload
