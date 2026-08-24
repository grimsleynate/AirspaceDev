"""Semantic, session-aware audio events for Quasar's native web client."""

import re
from collections.abc import Mapping


AUDIO_PROTOCOL_REVISION = 1
EVENT_ID_PATTERN = re.compile(r"^[a-z][a-z0-9_]*(?:\.[a-z0-9_]+)+$")
TUTORIAL_AREA = "Quasar Orientation Annex"
TUTORIAL_DECK_SCENES = {
    1: (
        "tutorial.operations_deck",
        [{"event": "ambience.station_air", "gain": 0.46}],
    ),
    0: (
        "tutorial.orientation_deck",
        [{"event": "ambience.station_air", "gain": 0.62}],
    ),
    -1: (
        "tutorial.engineering_deck",
        [
            {"event": "ambience.station_air", "gain": 0.38},
            {"event": "ambience.engineering_pulse", "gain": 0.58},
        ],
    ),
}


def _supported_sessions(character):
    """Yield sessions which explicitly announced native Quasar audio support."""

    if not character:
        return []
    return [
        session
        for session in character.sessions.all()
        if getattr(session, "protocol_flags", {}).get("QUASAR_AUDIO")
    ]


def _normalize_layers(value):
    """Normalize builder-friendly strings/dicts into the wire scene format."""

    if not value:
        return []
    if isinstance(value, str):
        value = [value]

    layers = []
    for layer in value:
        if isinstance(layer, str):
            event, gain = layer, 1.0
        elif isinstance(layer, Mapping):
            event = str(layer.get("event", ""))
            gain = layer.get("gain", 1.0)
        else:
            continue
        if not EVENT_ID_PATTERN.fullmatch(event):
            continue
        try:
            gain = float(gain)
        except (TypeError, ValueError):
            gain = 1.0
        layers.append({"event": event, "gain": max(0.0, min(1.0, gain))})
    return layers


def build_audio_scene(room):
    """Return the semantic audio scene assigned to a room."""

    if not room:
        return {
            "revision": AUDIO_PROTOCOL_REVISION,
            "scene": "silence",
            "music": None,
            "ambience": [],
            "fade_ms": 800,
        }

    scene = room.db.audio_scene
    music = room.db.audio_music or None
    ambience = room.db.audio_ambience
    from world.room_effects import room_effect_audio_layers

    ambience = [*_normalize_layers(ambience), *_normalize_layers(room_effect_audio_layers(room))]
    if not scene and room.db.map_area == TUTORIAL_AREA:
        scene, ambience = TUTORIAL_DECK_SCENES.get(
            room.db.map_z or 0,
            ("tutorial.orientation_deck", []),
        )
        music = music or "music.quasar_drift"
    scene = scene or f"room.{room.id}"
    if music and not EVENT_ID_PATTERN.fullmatch(str(music)):
        music = None
    try:
        fade_ms = int(room.db.audio_fade_ms or 1_800)
    except (TypeError, ValueError):
        fade_ms = 1_800
    return {
        "revision": AUDIO_PROTOCOL_REVISION,
        "scene": str(scene),
        "music": music,
        "ambience": ambience,
        "fade_ms": max(0, min(10_000, fade_ms)),
    }


def send_audio_scene(character, session=None, force=False):
    """Send the character's current room scene to one or all native clients."""

    payload = build_audio_scene(character.location if character else None)
    silence = build_audio_scene(None)
    targets = [session] if session else _supported_sessions(character)
    for target in targets:
        from world.accessibility import room_media_enabled

        target_payload = payload if room_media_enabled(character, target) else silence
        flags = getattr(target, "protocol_flags", {})
        if not force and flags.get("QUASAR_AUDIO_SCENE") == target_payload:
            continue
        flags["QUASAR_AUDIO_SCENE"] = target_payload
        target.msg(quasar_audio_scene=target_payload)
    return payload


def emit_audio(character, event, **options):
    """Emit a trusted semantic one-shot event to the character's web sessions."""

    if not EVENT_ID_PATTERN.fullmatch(event):
        raise ValueError(f"Invalid audio event id: {event!r}")

    payload = {"revision": AUDIO_PROTOCOL_REVISION, "event": event}
    for key in ("gain", "priority", "cooldown_ms", "pan"):
        if key in options and options[key] is not None:
            payload[key] = options[key]
    for session in _supported_sessions(character):
        from world.accessibility import room_media_enabled

        if room_media_enabled(character, session):
            session.msg(quasar_audio_play=payload)
    return payload


def stop_audio(character, session=None, **options):
    """Stop some or all audio for one or all native-client sessions."""

    payload = {"revision": AUDIO_PROTOCOL_REVISION, **options}
    targets = [session] if session else _supported_sessions(character)
    for target in targets:
        target.msg(quasar_audio_stop=payload)
        if payload.get("all"):
            getattr(target, "protocol_flags", {}).pop("QUASAR_AUDIO_SCENE", None)
    return payload
