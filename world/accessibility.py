"""Persistent accessibility preferences shared by chargen, commands, and clients."""


ACCESSIBILITY_PROTOCOL_REVISION = 1
DEFAULT_PREFERENCES = {
    "screenreader": False,
    "color_mode": "auto",
    "room_effects": True,
    "ascii_maps": True,
}
COLOR_MODES = {"auto", "ansi", "256", "truecolor", "off"}


def get_accessibility_preferences(account):
    """Return a complete, validated copy of an account's preferences."""

    preferences = dict(DEFAULT_PREFERENCES)
    if account:
        stored = account.attributes.get("accessibility_preferences", default={}) or {}
        if hasattr(stored, "items"):
            preferences.update(
                {key: value for key, value in stored.items() if key in DEFAULT_PREFERENCES}
            )
    preferences["screenreader"] = bool(preferences["screenreader"])
    preferences["room_effects"] = bool(preferences["room_effects"])
    preferences["ascii_maps"] = bool(preferences["ascii_maps"])
    if preferences["color_mode"] not in COLOR_MODES:
        preferences["color_mode"] = "auto"
    if preferences["screenreader"]:
        preferences.update(color_mode="off", room_effects=False, ascii_maps=False)
    return preferences


def set_accessibility_preferences(account, **changes):
    """Persist validated changes, applying the screen-reader safety profile."""

    preferences = get_accessibility_preferences(account)
    for key, value in changes.items():
        if key not in DEFAULT_PREFERENCES:
            continue
        if key == "color_mode":
            value = str(value).lower()
            if value not in COLOR_MODES:
                continue
        else:
            value = bool(value)
        preferences[key] = value
    if preferences["screenreader"]:
        preferences.update(color_mode="off", room_effects=False, ascii_maps=False)
    account.attributes.add("accessibility_preferences", preferences)
    return preferences


def _protocol_color_flags(mode, capabilities=None):
    if mode == "off":
        return {"NOCOLOR": True, "ANSI": False, "XTERM256": False, "TRUECOLOR": False}
    if mode == "ansi":
        return {"NOCOLOR": False, "ANSI": True, "XTERM256": False, "TRUECOLOR": False}
    if mode == "256":
        return {"NOCOLOR": False, "ANSI": True, "XTERM256": True, "TRUECOLOR": False}
    if mode == "truecolor":
        return {"NOCOLOR": False, "ANSI": True, "XTERM256": True, "TRUECOLOR": True}
    capabilities = capabilities or {
        "ANSI": True,
        "XTERM256": False,
        "TRUECOLOR": False,
    }
    return {"NOCOLOR": False, **capabilities}


def accessibility_payload(account):
    preferences = get_accessibility_preferences(account)
    return {"revision": ACCESSIBILITY_PROTOCOL_REVISION, **preferences}


def apply_accessibility_preferences(account, session=None, character=None):
    """Apply persistent preferences to a transport and optional character."""

    session_flags = getattr(session, "protocol_flags", {}) if session else {}
    if (
        session
        and not account.attributes.has("accessibility_preferences")
        and isinstance(session_flags, dict)
        and session_flags.get("SCREENREADER")
    ):
        set_accessibility_preferences(account, screenreader=True)
    preferences = get_accessibility_preferences(account)
    capabilities = getattr(session, "_quasar_color_capabilities", None) if session else None
    if session and not isinstance(capabilities, dict):
        capabilities = {
            "ANSI": bool(session_flags.get("ANSI", True)),
            "XTERM256": bool(session_flags.get("XTERM256", False)),
            "TRUECOLOR": bool(session_flags.get("TRUECOLOR", False)),
        }
        session._quasar_color_capabilities = capabilities
    protocol = {
        "SCREENREADER": preferences["screenreader"],
        **_protocol_color_flags(preferences["color_mode"], capabilities),
    }
    saved = dict(account.attributes.get("_saved_protocol_flags", default={}) or {})
    # ANSI/XTERM256/TRUECOLOR describe this particular client's negotiated
    # capabilities. Persisting our display-mode overrides here poisons the
    # next session before its real capabilities can be captured (notably when
    # returning from ``color off`` to ``color auto``).  The chosen mode already
    # lives in accessibility_preferences, so only retain flags needed for safe
    # early login output and let every new transport negotiate its own colors.
    for key in ("ANSI", "XTERM256", "TRUECOLOR"):
        saved.pop(key, None)
    saved.update(
        SCREENREADER=protocol["SCREENREADER"],
        NOCOLOR=protocol["NOCOLOR"],
    )
    account.attributes.add("_saved_protocol_flags", saved)

    if character:
        character.db.ascii_map_enabled = preferences["ascii_maps"]
    if session:
        session.protocol_flags.update(protocol)
        if session.protocol_flags.get("QUASAR_ACCESSIBILITY"):
            session.msg(quasar_accessibility_sync=accessibility_payload(account))
        handler = getattr(session, "sessionhandler", None)
        if handler and hasattr(handler, "session_portal_sync"):
            try:
                handler.session_portal_sync(session)
            except AttributeError:
                # Unit tests and partially initialized maintenance sessions do
                # not have a live Server-to-Portal AMP transport.
                pass
    return preferences


def apply_to_account_sessions(account):
    """Apply settings to every current session and controlled character."""

    preferences = get_accessibility_preferences(account)
    for character in account.characters:
        character.db.ascii_map_enabled = preferences["ascii_maps"]
    for session in account.sessions.all():
        character = account.get_puppet(session)
        apply_accessibility_preferences(account, session=session, character=character)
        if not character:
            continue
        flags = getattr(session, "protocol_flags", {})
        if preferences["room_effects"] and not preferences["screenreader"]:
            from world.audio import send_audio_scene
            from world.room_effects import send_room_effects

            if flags.get("QUASAR_AUDIO"):
                send_audio_scene(character, session=session, force=True)
            if flags.get("QUASAR_ROOM_EFFECTS"):
                send_room_effects(character, session=session, force=True)
        else:
            from world.audio import stop_audio
            from world.room_effects import clear_room_effects

            if flags.get("QUASAR_AUDIO"):
                stop_audio(character, session=session, all=True, fade_ms=150)
            if flags.get("QUASAR_ROOM_EFFECTS"):
                clear_room_effects(session)
    return preferences


def room_media_enabled(character, session=None):
    """Return whether ambient audio/visual media is allowed for this player."""

    account = getattr(character, "account", None)
    preferences = get_accessibility_preferences(account)
    flags = getattr(session, "protocol_flags", {}) if session else {}
    if isinstance(flags, dict) and flags.get("SCREENREADER"):
        return False
    return bool(preferences["room_effects"] and not preferences["screenreader"])


def ascii_maps_enabled(character):
    """Keep decorative maps out of screen-reader output."""

    account = getattr(character, "account", None)
    preferences = get_accessibility_preferences(account)
    if preferences["screenreader"] or not preferences["ascii_maps"]:
        return False
    return bool(character.attributes.get("ascii_map_enabled", default=preferences["ascii_maps"]))
