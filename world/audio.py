"""Semantic, session-aware audio events for the native web client."""

import re
from collections.abc import Mapping


AUDIO_PROTOCOL_REVISION = 1
EVENT_ID_PATTERN = re.compile(r"^[a-z][a-z0-9_]*(?:\.[a-z0-9_]+)+$")


def _supported_sessions(character):
    """Yield sessions which explicitly announced native audio support."""

    if not character:
        return []
    return [
        session
        for session in character.sessions.all()
        if getattr(session, "protocol_flags", {}).get("BENBEN_AUDIO")
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
        if not force and target.ndb.benben_audio_scene == target_payload:
            continue
        target.ndb.benben_audio_scene = target_payload
        target.msg(benben_audio_scene=target_payload)
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
            session.msg(benben_audio_play=payload)
    return payload


def stop_audio(character, session=None, **options):
    """Stop some or all audio for one or all native-client sessions."""

    payload = {"revision": AUDIO_PROTOCOL_REVISION, **options}
    targets = [session] if session else _supported_sessions(character)
    for target in targets:
        target.msg(benben_audio_stop=payload)
        if payload.get("all"):
            target.ndb.benben_audio_scene = None
    return payload
