"""Quasar's deliberately compact launch character creator.

The resulting character has six authored facts: species, gender, Background,
two starting Ability Trees, and name. Archetypes only pre-fill four of those
facts and converge on the same final review.
"""

from random import choice

from evennia.utils import dedent

from typeclasses.characters import Character
from world.character_options import (
    ABILITY_TREES, ARCHETYPES, BACKGROUNDS, MINISKILLS, SPECIES,
    apply_archetype, apply_background, apply_species, opening_default,
    valid_creation,
)
from world.portraits import GENDERS, assign_default_portrait, send_chargen_preview


def _numbered_options(
    catalog, setter, argument, *, back=None, help_kind=None, return_node=None,
    surprise_component=None,
):
    options = []
    for index, (key, value) in enumerate(catalog.items(), 1):
        options.append({
            "key": (str(index), value["name"], key),
            "desc": f"{value['name']} — {value['description']}",
            "goto": (setter, {argument: key}),
        })
    if catalog is not ARCHETYPES:
        options.append({
            "key": ("s", "Surprise me", "surprise"),
            "desc": "Choose this one at random.",
            "goto": (_surprise_component, {"component": surprise_component or argument}),
        })
    if back:
        options.append({"key": ("b", "Back", "back"), "desc": "Go back.", "goto": back})
    if help_kind and return_node:
        options.append({
            "key": "_default",
            "goto": (
                _menu_help_dispatch,
                {"catalog_kind": help_kind, "return_node": return_node},
            ),
        })
    return options


def _help_catalog(catalog_kind):
    return {
        "species": SPECIES,
        "background": BACKGROUNDS,
        "ability_tree": ABILITY_TREES,
    }.get(catalog_kind, {})


def _menu_help_dispatch(
    caller, raw_string, catalog_kind=None, return_node=None, **kwargs
):
    """Make global option help readable without leaving the chargen EvMenu."""

    raw = " ".join(str(raw_string or "").strip().lower().split())
    if raw == "help" or raw == "?":
        return "menunode_option_help_index", {
            "catalog_kind": catalog_kind,
            "return_node": return_node,
        }
    if raw.startswith("help "):
        query = raw[5:].strip()
    elif raw.startswith("? "):
        query = raw[2:].strip()
    else:
        return return_node

    catalog = _help_catalog(catalog_kind)
    option_key = next(
        (
            key for key, option in catalog.items()
            if query in {key.lower(), key.replace("_", " ").lower(), option["name"].lower()}
        ),
        None,
    )
    if not option_key:
        return "menunode_option_help_index", {
            "catalog_kind": catalog_kind,
            "return_node": return_node,
            "error": f"No {catalog_kind.replace('_', ' ')} named '{query}' exists.",
        }
    return "menunode_option_help", {
        "catalog_kind": catalog_kind,
        "option_key": option_key,
        "return_node": return_node,
    }


def menunode_option_help_index(caller, raw_string="", **kwargs):
    catalog_kind = kwargs.get("catalog_kind")
    return_node = kwargs.get("return_node") or "menunode_welcome"
    catalog = _help_catalog(catalog_kind)
    error = kwargs.get("error")
    error_text = f"|r{error}|n\n\n" if error else ""
    names = ", ".join(option["name"] for option in catalog.values())
    return (
        f"|cAvailable {catalog_kind.replace('_', ' ').title()} Help|n\n\n"
        f"{error_text}{names}\n\n"
        f"Return to the selection and type |whelp <name>|n, such as "
        f"|whelp {next(iter(catalog.values()))['name'].lower()}|n."
        if catalog else "|cCharacter Creation Help|n\n\nNo option catalog is available here.",
        [{"key": ("b", "Back", "back"), "desc": "Return to your choice.", "goto": return_node}],
    )


def menunode_option_help(caller, raw_string="", **kwargs):
    from world.help_character_options import get_option_help

    catalog_kind = kwargs.get("catalog_kind")
    option_key = kwargs.get("option_key")
    return_node = kwargs.get("return_node") or "menunode_welcome"
    option = _help_catalog(catalog_kind).get(option_key, {})
    text = get_option_help(catalog_kind, option_key)
    if not text:
        return return_node
    return (
        f"|c{option['name']}|n\n\n{text}",
        [{"key": ("b", "Back", "back"), "desc": "Return to your choice.", "goto": return_node}],
    )


def _editing(character):
    return bool(character.db.chargen_editing)


def _set_step(caller, name):
    caller.new_char.db.chargen_step = name


def _name(catalog, key):
    return catalog.get(key, {}).get("name", "|rNot selected|n")


def _sync_tree_state(character):
    trees = [key for key in list(character.db.basic_trees or [])[:2] if key in ABILITY_TREES]
    character.db.basic_trees = trees
    character.db.known_skill_trees = list(trees)
    character.db.active_skill_trees = list(trees)
    character.db.skill_tree_proficiency = {key: 1 for key in trees}
    practice = int(SPECIES.get(character.db.species, {}).get("benefit", {}).get("starting_practice", 0))
    character.db.skill_tree_experience = {key: practice for key in trees}
    from world.character_traits import ensure_skill_traits

    ensure_skill_traits(character)


def _surprise_component(caller, raw_string, component=None, **kwargs):
    if component == "species_key":
        return _set_species(caller, raw_string, species_key=choice(tuple(SPECIES)))
    if component == "background_key":
        return _set_background(caller, raw_string, background_key=choice(tuple(BACKGROUNDS)))
    if component == "tree_one_key":
        return _set_tree_one(caller, raw_string, tree_key=choice(tuple(ABILITY_TREES)))
    if component == "tree_two_key":
        first = (list(caller.new_char.db.basic_trees or []) + [None])[0]
        return _set_tree_two(caller, raw_string, tree_key=choice([key for key in ABILITY_TREES if key != first]))
    return "menunode_welcome"


def _begin_path(caller, raw_string, path=None, **kwargs):
    character = caller.new_char
    character.db.chargen_path = path
    character.db.chargen_editing = False
    character.db.chargen_name_selected = False
    return "menunode_archetype" if path == "archetype" else "menunode_species"


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
    caller.new_char.db.chargen_editing = False
    return dedent("""
        |cWho crosses the frontier?|n

        Choose an archetype for a quick starting point or build freely. An
        archetype only fills in species, Background, and two Ability Trees.
        It grants no hidden bonus and every choice remains editable.

        Using a screen reader or prefer reduced visual output? Choose
        Accessibility before continuing.
    """), [
        {"key": ("1", "Archetype", "archetypes"), "desc": "Start from a compact, editable build.", "goto": (_begin_path, {"path": "archetype"})},
        {"key": ("2", "Build freely", "custom"), "desc": "Choose all six character facts yourself.", "goto": (_begin_path, {"path": "custom"})},
        {"key": ("3", "Accessibility", "access"), "desc": "Configure screen reader, ANSI color, maps, and room effects.", "goto": (_open_accessibility, {"return_node": "menunode_welcome"})},
    ]


def menunode_archetype(caller, raw_string="", **kwargs):
    _set_step(caller, "menunode_archetype")
    return "|cChoose an Editable Archetype|n\n\nA starting build, never a permanent class.", _numbered_options(
        ARCHETYPES, _set_archetype, "archetype_key", back="menunode_welcome"
    )


def _set_archetype(caller, raw_string, archetype_key=None, **kwargs):
    if archetype_key not in ARCHETYPES:
        return "menunode_archetype"
    apply_archetype(caller.new_char, archetype_key)
    caller.new_char.db.gender = None
    caller.new_char.db.portrait_id = None
    caller.new_char.db.portrait_url = None
    caller.new_char.db.chargen_name_selected = False
    return "menunode_species"


def menunode_species(caller, raw_string="", **kwargs):
    _set_step(caller, "menunode_species")
    if _editing(caller.new_char):
        back = "menunode_review"
    elif caller.new_char.db.chargen_path == "archetype":
        back = "menunode_archetype"
    else:
        back = "menunode_welcome"
    return "|cChoose Your Species|n\n\nEach species has one bounded innate benefit. None restricts which Ability Trees you may learn. Type |whelp <species>|n for the full in-game help entry.", _numbered_options(
        SPECIES, _set_species, "species_key", back=back,
        help_kind="species", return_node="menunode_species",
    )


def _set_species(caller, raw_string, species_key=None, **kwargs):
    if species_key not in SPECIES:
        return "menunode_species"
    old = caller.new_char.db.species
    apply_species(caller.new_char, species_key)
    _sync_tree_state(caller.new_char)
    caller.new_char.db.portrait_id = None
    caller.new_char.db.portrait_url = None
    if not caller.new_char.db.opening_premise or caller.new_char.db.opening_premise == opening_default(old):
        caller.new_char.db.opening_premise = opening_default(species_key)
    return "menunode_review" if _editing(caller.new_char) else "menunode_gender"


def menunode_gender(caller, raw_string="", **kwargs):
    _set_step(caller, "menunode_gender")
    send_chargen_preview(caller, caller.new_char, "gender")
    options = [
        {"key": (str(index), value["name"], key), "desc": f"{value['name']} — {value['description']}", "goto": (_set_gender, {"gender_key": key})}
        for index, (key, value) in enumerate(GENDERS.items(), 1)
    ]
    options.append({"key": ("b", "Back", "back"), "desc": "Choose a different species.", "goto": "menunode_species"})
    return "|cChoose Gender|n\n\nIdentity and presentation; never a mechanical trait.", options


def _set_gender(caller, raw_string, gender_key=None, **kwargs):
    if gender_key not in GENDERS:
        return "menunode_gender"
    caller.new_char.db.gender = gender_key
    assign_default_portrait(caller.new_char, caller.new_char.db.species, gender_key)
    send_chargen_preview(caller, caller.new_char, "portrait_selected")
    if _editing(caller.new_char):
        return "menunode_review"
    return "menunode_name" if caller.new_char.db.chargen_path == "archetype" else "menunode_background"


menunode_human_gender = menunode_gender
_set_human_gender = _set_gender


def menunode_background(caller, raw_string="", **kwargs):
    _set_step(caller, "menunode_background")
    back = "menunode_review" if _editing(caller.new_char) else "menunode_gender"
    return "|cChoose a Background|n\n\nYour prior life unlocks one focused miniskill. It is useful context, not your class. Type |whelp <background>|n for the full in-game help entry.", _numbered_options(
        BACKGROUNDS, _set_background, "background_key", back=back,
        help_kind="background", return_node="menunode_background",
    )


def _set_background(caller, raw_string, background_key=None, **kwargs):
    if background_key not in BACKGROUNDS:
        return "menunode_background"
    apply_background(caller.new_char, background_key)
    return "menunode_review" if _editing(caller.new_char) else "menunode_tree_one"


def menunode_tree_one(caller, raw_string="", **kwargs):
    _set_step(caller, "menunode_tree_one")
    back = "menunode_review" if _editing(caller.new_char) else "menunode_background"
    return "|cChoose Starting Ability Tree A|n\n\nThis is practiced technique, not destiny. Other trees can be discovered in play. Type |whelp <tree>|n to read its full entry and ability list.", _numbered_options(
        ABILITY_TREES, _set_tree_one, "tree_key", back=back,
        help_kind="ability_tree", return_node="menunode_tree_one",
        surprise_component="tree_one_key",
    )


def _set_tree_one(caller, raw_string, tree_key=None, **kwargs):
    if tree_key not in ABILITY_TREES:
        return "menunode_tree_one"
    trees = (list(caller.new_char.db.basic_trees or []) + [None, None])[:2]
    trees[0] = tree_key
    if trees[1] == tree_key:
        trees[1] = None
    caller.new_char.db.basic_trees = trees
    _sync_tree_state(caller.new_char)
    return "menunode_review" if _editing(caller.new_char) and len(caller.new_char.db.basic_trees or []) == 2 else "menunode_tree_two"


def menunode_tree_two(caller, raw_string="", **kwargs):
    _set_step(caller, "menunode_tree_two")
    first = (list(caller.new_char.db.basic_trees or []) + [None])[0]
    catalog = {key: value for key, value in ABILITY_TREES.items() if key != first}
    options = _numbered_options(
        catalog, _set_tree_two, "tree_key",
        help_kind="ability_tree", return_node="menunode_tree_two",
        surprise_component="tree_two_key",
    )
    options.append({"key": ("b", "Back", "back"), "desc": "Choose Ability Tree A again.", "goto": "menunode_tree_one"})
    return f"|cChoose Starting Ability Tree B|n\n\nAbility Tree A: |w{_name(ABILITY_TREES, first)}|n. The two must be different. Type |whelp <tree>|n to read its full entry and ability list.", options


def _set_tree_two(caller, raw_string, tree_key=None, **kwargs):
    trees = list(caller.new_char.db.basic_trees or [])
    if tree_key not in ABILITY_TREES or not trees or tree_key == trees[0]:
        return "menunode_tree_two"
    caller.new_char.db.basic_trees = [trees[0], tree_key]
    _sync_tree_state(caller.new_char)
    return "menunode_review" if _editing(caller.new_char) else "menunode_name"


def menunode_name(caller, raw_string="", **kwargs):
    _set_step(caller, "menunode_name")
    error = kwargs.get("error")
    suffix = f"\n|r{error}|n" if error else ""
    return f"|cChoose Your Name|n\n\nEnter 3–30 characters. You can still change it during final review.{suffix}", {"key": "_default", "goto": _validate_name}


def _validate_name(caller, raw_string, **kwargs):
    name = caller.account.normalize_username(raw_string.strip())
    if len(name) < 3 or len(name) > 30 or "|" in name:
        return "menunode_name", {"error": "Use 3–30 characters and no color tags."}
    existing = [obj for obj in Character.objects.filter_family(db_key__iexact=name) if obj != caller.new_char]
    if existing:
        return "menunode_name", {"error": f"The name {name} is already in use."}
    caller.new_char.key = name
    caller.new_char.db.chargen_name_selected = True
    return "menunode_review"


def _ready_to_finalize(character):
    return bool(valid_creation(character) and character.db.gender in GENDERS and character.db.chargen_name_selected)


def menunode_review(caller, raw_string="", **kwargs):
    _set_step(caller, "menunode_review")
    character = caller.new_char
    character.db.chargen_complete = False
    character.db.chargen_editing = True
    trees = (list(character.db.basic_trees or []) + [None, None])[:2]
    species = SPECIES.get(character.db.species, {})
    benefit = species.get("benefit", {})
    background = BACKGROUNDS.get(character.db.background, {})
    miniskill = MINISKILLS.get(background.get("miniskill"), {})
    item = background.get("item")
    item_line = f"\n|wBackground keepsake:|n {item['name']}" if item else ""
    text = dedent(f"""
        |cFinal Review|n

        |wName:|n {character.key if character.db.chargen_name_selected else '|rNot selected|n'}
        |wSpecies:|n {_name(SPECIES, character.db.species)}
        |wSpecies benefit:|n {benefit.get('name', '|rNot selected|n')} — {benefit.get('description', '')}
        |wGender:|n {GENDERS.get(character.db.gender, {}).get('name', '|rNot selected|n')}
        |wBackground:|n {_name(BACKGROUNDS, character.db.background)}
        |wMiniskill:|n {miniskill.get('name', '|rNot selected|n')} — {miniskill.get('description', '')}{item_line}
        |wAbility Tree A:|n {_name(ABILITY_TREES, trees[0])}
        |wAbility Tree B:|n {_name(ABILITY_TREES, trees[1])}

        Nothing here is a permanent class. Your two Ability Trees are simply
        the techniques you can use now; the frontier holds others.
    """)
    options = [
        {"key": ("1", "Finalize", "continue"), "desc": "Proceed to confirmation.", "goto": "menunode_confirm"},
        {"key": ("2", "Name"), "desc": "Choose another name.", "goto": "menunode_name"},
        {"key": ("3", "Species"), "desc": "Choose another species.", "goto": "menunode_species"},
        {"key": ("4", "Gender"), "desc": "Adjust gender.", "goto": "menunode_gender"},
        {"key": ("5", "Background"), "desc": "Choose another Background.", "goto": "menunode_background"},
        {"key": ("6", "Ability Tree A"), "desc": "Adjust the first active Ability Tree.", "goto": "menunode_tree_one"},
        {"key": ("7", "Ability Tree B"), "desc": "Adjust the second active Ability Tree.", "goto": "menunode_tree_two"},
        {"key": ("8", "Restart"), "desc": "Return to the entry paths.", "goto": "menunode_welcome"},
        {"key": ("9", "Accessibility"), "desc": "Adjust account-wide accessibility settings.", "goto": (_open_accessibility, {"return_node": "menunode_review"})},
    ]
    if not _ready_to_finalize(character):
        options[0] = {"key": ("1", "Incomplete"), "desc": "Complete the missing choices before finalizing.", "goto": "menunode_review"}
    return text, options


def menunode_confirm(caller, raw_string="", **kwargs):
    if not _ready_to_finalize(caller.new_char):
        return menunode_review(caller, raw_string)
    _set_step(caller, "menunode_confirm")
    return f"|cReady for Dawnline|n\n\nCreate |w{caller.new_char.key}|n and begin their opening?", [
        {"key": ("1", "Confirm", "yes", "y"), "desc": "Finish character creation.", "goto": "menunode_end"},
        {"key": ("2", "Rename", "name"), "desc": "Choose another name.", "goto": "menunode_name"},
        {"key": ("3", "Adjust", "back"), "desc": "Return to final review.", "goto": "menunode_review"},
    ]


def _remove_legacy_creation_fields(character):
    for attribute in (
        "attribute_inclination", "background_knack", "background_item",
        "background_relationship", "background_hook", "background_package_chain",
        "heritage", "obligation",
    ):
        character.attributes.remove(attribute)


def menunode_end(caller, raw_string="", **kwargs):
    character = caller.new_char
    if not _ready_to_finalize(character):
        return menunode_review(caller, raw_string)
    _remove_legacy_creation_fields(character)
    character.db.career = None
    character.db.specialization = None
    from world.resources import initialize_character
    initialize_character(character, include_starter_gear=False)
    from world.opening_tutorial import create_opening_tutorial
    start = create_opening_tutorial(character, enter=False)
    character.location = start
    character.db.prelogout_location = start
    character.db.chargen_complete = True
    character.attributes.remove("chargen_step")
    character.attributes.remove("chargen_editing")
    return f"|gCharacter creation complete.|n\n\nWelcome to Quasar, |w{character.key}|n.", None


# Paused characters inside removed long-form nodes recover without crashing.
menunode_inclination = menunode_background
menunode_knack = menunode_background
menunode_possession = menunode_background
menunode_relationship = menunode_background
menunode_hook = menunode_background
menunode_heritage = menunode_review
menunode_obligation = menunode_review
menunode_opening = menunode_review
