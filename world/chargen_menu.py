"""Compact character creator used by Evennia's character_creator contrib.

``settings.CHARGEN_MENU`` points here. The contrib creates an in-progress
character as ``caller.new_char`` and sends it to ``settings.START_LOCATION``
once the menu ends.
"""

from evennia.utils import dedent

from typeclasses.characters import Character


def _set_step(caller, name):
    caller.new_char.db.chargen_step = name


def _set_accessibility_menu(caller, raw_string, setting=None, **kwargs):
    from world.accessibility import (
        apply_to_account_sessions,
        get_accessibility_preferences,
        set_accessibility_preferences,
    )

    account = caller.account
    preferences = get_accessibility_preferences(account)
    if setting == "screenreader":
        set_accessibility_preferences(
            account, screenreader=not preferences["screenreader"]
        )
    elif setting == "color":
        if preferences["screenreader"]:
            caller.msg("Turn screen-reader mode off before enabling color.")
        else:
            set_accessibility_preferences(
                account,
                color_mode="auto" if preferences["color_mode"] == "off" else "off",
            )
    elif setting in {"room_effects", "ascii_maps"}:
        if preferences["screenreader"]:
            caller.msg("Screen-reader mode keeps maps and room media disabled.")
        else:
            set_accessibility_preferences(
                account, **{setting: not preferences[setting]}
            )
    apply_to_account_sessions(account)
    return "menunode_accessibility"


def _open_accessibility(caller, raw_string, return_node="menunode_welcome", **kwargs):
    caller.new_char.db.accessibility_return_node = return_node
    return "menunode_accessibility"


def _close_accessibility(caller, raw_string, **kwargs):
    return caller.new_char.db.accessibility_return_node or "menunode_welcome"


def menunode_accessibility(caller, raw_string="", **kwargs):
    """Prominent account-wide accessibility setup inside character creation."""

    from world.accessibility import (
        apply_accessibility_preferences,
        get_accessibility_preferences,
    )

    menu_session = caller if isinstance(getattr(caller, "protocol_flags", None), dict) else None
    apply_accessibility_preferences(
        caller.account, session=menu_session, character=caller.new_char
    )
    preferences = get_accessibility_preferences(caller.account)
    state = lambda value: "ON" if value else "OFF"
    text = dedent(f"""
        Accessibility Settings

        Screen reader: {state(preferences['screenreader'])}
        Color: {preferences['color_mode']}
        Room audio and visuals: {state(preferences['room_effects'])}
        ASCII maps: {state(preferences['ascii_maps'])}

        Screen-reader mode removes ANSI and decorative transport noise and
        turns off ASCII maps plus room audio and visuals. It does not shorten
        or suppress room descriptions. These settings apply to every character
        and remain available later with CONFIG or ACCESSIBILITY.
    """)
    return text, [
        {"key": ("1", "Screen reader"), "desc": "Toggle the screen-reader profile.", "goto": (_set_accessibility_menu, {"setting": "screenreader"})},
        {"key": ("2", "Color"), "desc": "Toggle between automatic ANSI color and no color.", "goto": (_set_accessibility_menu, {"setting": "color"})},
        {"key": ("3", "Room effects"), "desc": "Toggle room audio and visual ambience.", "goto": (_set_accessibility_menu, {"setting": "room_effects"})},
        {"key": ("4", "ASCII maps"), "desc": "Toggle decorative text maps.", "goto": (_set_accessibility_menu, {"setting": "ascii_maps"})},
        {"key": ("5", "Back", "b"), "desc": "Return to character creation.", "goto": _close_accessibility},
    ]


def menunode_welcome(caller, raw_string="", **kwargs):
    _set_step(caller, "menunode_welcome")
    return dedent("""
        |cCharacter Creation|n

        Choose a name for your character.

        Using a screen reader or prefer reduced visual output? Choose
        Accessibility before continuing.
    """), [
        {"key": ("1", "Name", "continue"), "desc": "Choose your character's name.", "goto": "menunode_name"},
        {"key": ("2", "Accessibility", "access"), "desc": "Configure screen reader, ANSI color, maps, and room effects.", "goto": (_open_accessibility, {"return_node": "menunode_welcome"})},
    ]


def menunode_name(caller, raw_string="", **kwargs):
    _set_step(caller, "menunode_name")
    error = kwargs.get("error")
    suffix = f"\n|r{error}|n" if error else ""
    return f"|cChoose Your Name|n\n\nEnter 3–30 characters.{suffix}", {"key": "_default", "goto": _validate_name}


def _validate_name(caller, raw_string, **kwargs):
    name = caller.account.normalize_username(raw_string.strip())
    if len(name) < 3 or len(name) > 30 or "|" in name:
        return "menunode_name", {"error": "Use 3–30 characters and no color tags."}
    existing = [obj for obj in Character.objects.filter_family(db_key__iexact=name) if obj != caller.new_char]
    if existing:
        return "menunode_name", {"error": f"The name {name} is already in use."}
    caller.new_char.key = name
    caller.new_char.db.chargen_name_selected = True
    return "menunode_confirm"


def menunode_confirm(caller, raw_string="", **kwargs):
    if not caller.new_char.db.chargen_name_selected:
        return menunode_name(caller, raw_string)
    _set_step(caller, "menunode_confirm")
    return f"|cConfirm|n\n\nCreate |w{caller.new_char.key}|n?", [
        {"key": ("1", "Confirm", "yes", "y"), "desc": "Finish character creation.", "goto": "menunode_end"},
        {"key": ("2", "Rename", "name"), "desc": "Choose another name.", "goto": "menunode_name"},
        {"key": ("3", "Accessibility", "access"), "desc": "Adjust account-wide accessibility settings.", "goto": (_open_accessibility, {"return_node": "menunode_confirm"})},
    ]


def menunode_end(caller, raw_string="", **kwargs):
    character = caller.new_char
    if not character.db.chargen_name_selected:
        return menunode_name(caller, raw_string)
    from world.resources import ensure_character_resources

    ensure_character_resources(character)
    character.db.chargen_complete = True
    character.attributes.remove("chargen_step")
    character.attributes.remove("chargen_name_selected")
    character.attributes.remove("accessibility_return_node")
    return f"|gCharacter creation complete.|n\n\nWelcome, |w{character.key}|n.", None
