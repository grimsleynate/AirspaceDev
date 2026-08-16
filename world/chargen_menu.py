"""
Quasar character-generation menu.

This menu is used by Evennia's Character Creator contrib. The caller
is a Session, and caller.new_char is the character currently being built.
"""

from evennia.utils import dedent

from typeclasses.characters import Character
from world.character_options import BACKGROUNDS, CAREERS, SPECIES
from world.portraits import GENDERS, assign_default_portrait, send_chargen_preview


def _display_name(options, selected_key):
    """
    Return the player-facing name for a stored option key.
    """

    if not selected_key:
        return "|xNot selected|n"

    option = options.get(selected_key)
    if not option:
        return "|rInvalid selection|n"

    return option["name"]


# ---------------------------------------------------------------------
# Welcome
# ---------------------------------------------------------------------


def menunode_welcome(caller, raw_string="", **kwargs):
    """
    Starting point expected by Evennia's Character Creator contrib.
    """

    caller.new_char.db.chargen_step = "menunode_welcome"

    text = dedent(
        """
        |cWelcome to Quasar character creation.|n

        You will choose:

          |w1.|n A name
          |w2.|n A species
          |w3.|n A background
          |w4.|n A career
          |w5.|n A specialization

        These choices are descriptive only for now. They do not provide
        attributes, skills, traits, equipment, or combat abilities.

        You may quit character creation and resume it later with
        |wcharcreate|n.
        """
    )

    options = {
        "key": ("1", "Begin", "begin", "b"),
        "desc": "Begin — Start creating your character.",
        "goto": "menunode_name",
    }

    return text, options


# ---------------------------------------------------------------------
# Name
# ---------------------------------------------------------------------


def menunode_name(caller, raw_string="", **kwargs):
    """
    Ask the player to enter a character name.
    """

    caller.new_char.db.chargen_step = "menunode_name"

    error = kwargs.get("error")
    error_text = f"\n|r{error}|n\n" if error else ""

    text = dedent(
        f"""
        |cChoose a Name|n

        Enter a name between 3 and 30 characters long.
        {error_text}
        """
    )

    options = {
        "key": "_default",
        "goto": _validate_name,
    }

    return text, options


def _validate_name(caller, raw_string, **kwargs):
    """
    Validate and reserve the requested character name.
    """

    name = raw_string.strip()
    name = caller.account.normalize_username(name)

    if len(name) < 3 or len(name) > 30:
        return (
            "menunode_name",
            {"error": "Names must be between 3 and 30 characters long."},
        )

    if "|" in name:
        return (
            "menunode_name",
            {"error": "Names cannot contain Evennia color tags."},
        )

    existing = Character.objects.filter_family(db_key__iexact=name)

    # Ignore our own temporary character if the player returns to this node.
    existing = [character for character in existing if character != caller.new_char]

    if existing:
        return (
            "menunode_name",
            {"error": f"The name {name} is already in use."},
        )

    caller.new_char.key = name

    return "menunode_species"


# ---------------------------------------------------------------------
# Species
# ---------------------------------------------------------------------


def menunode_species(caller, raw_string="", **kwargs):
    """
    Display the available species.
    """

    caller.new_char.db.chargen_step = "menunode_species"

    text = dedent(
        """
        |cChoose a Species|n

        Species are descriptive only for now.
        """
    )

    options = []

    for index, (species_key, species) in enumerate(SPECIES.items(), start=1):
        options.append(
            {
                "key": (str(index), species["name"], species_key),
                "desc": f"{species['name']} — {species['description']}",
                "goto": (
                    _set_species,
                    {"species_key": species_key},
                ),
            }
        )

    options.append(
        {
            "key": (str(len(options) + 1), "Back", "back", "b"),
            "desc": "Choose a different name.",
            "goto": "menunode_name",
        }
    )

    return text, options


def _set_species(caller, raw_string, species_key=None, **kwargs):
    """
    Store the selected species key.
    """

    if species_key not in SPECIES:
        return "menunode_species"

    caller.new_char.db.species = species_key
    caller.new_char.db.locomotion_chassis = "wheel" if species_key == "synth" else "bipedal"
    caller.new_char.db.gender = None
    caller.new_char.db.pre_synth_gender = None
    caller.new_char.db.portrait_id = None
    caller.new_char.db.portrait_url = None

    return "menunode_synth_origin_gender" if species_key == "synth" else "menunode_human_gender"


# ---------------------------------------------------------------------
# Gender and default portrait
# ---------------------------------------------------------------------


def _gender_options(goto, back_node="menunode_species", back_description="Choose a different species."):
    options = []
    for index, (gender_key, gender) in enumerate(GENDERS.items(), start=1):
        options.append({
            "key": (str(index), gender["name"], gender_key),
            "desc": f"{gender['name']} — {gender['description']}",
            "goto": (goto, {"gender_key": gender_key}),
        })
    options.append({
        "key": ("4", "Back", "back", "b"),
        "desc": f"Back — {back_description}",
        "goto": back_node,
    })
    return options


def menunode_human_gender(caller, raw_string="", **kwargs):
    caller.new_char.db.chargen_step = "menunode_human_gender"
    send_chargen_preview(caller, caller.new_char, "gender")
    text = dedent(
        """
        |cChoose a Gender|n

        This choice selects your initial portrait. A gender-neutral character
        receives either default Human portrait at random.
        """
    )
    return text, _gender_options(_set_human_gender)


def _set_human_gender(caller, raw_string, gender_key=None, **kwargs):
    if gender_key not in GENDERS:
        return "menunode_human_gender"
    caller.new_char.db.gender = gender_key
    caller.new_char.db.pre_synth_gender = None
    assign_default_portrait(caller.new_char, "human", gender_key)
    send_chargen_preview(caller, caller.new_char, "portrait_selected")
    return "menunode_background"


def menunode_synth_origin_gender(caller, raw_string="", **kwargs):
    caller.new_char.db.chargen_step = "menunode_synth_origin_gender"
    send_chargen_preview(caller, caller.new_char, "pre_synth_gender")
    text = dedent(
        """
        |cChoose Your Pre-Synth Gender|n

        Before upload, how did you identify?
        """
    )
    return text, _gender_options(_set_synth_origin_gender)


def _set_synth_origin_gender(caller, raw_string, gender_key=None, **kwargs):
    if gender_key not in GENDERS:
        return "menunode_synth_origin_gender"
    caller.new_char.db.pre_synth_gender = gender_key
    caller.new_char.db.gender = None
    assign_default_portrait(caller.new_char, "synth")
    send_chargen_preview(caller, caller.new_char, "portrait_selected")
    return "menunode_background"


def menunode_synth_gender(caller, raw_string="", **kwargs):
    """Compatibility step for Synths paused in the removed gender menu."""

    if not caller.new_char.db.pre_synth_gender:
        return menunode_synth_origin_gender(caller, raw_string, **kwargs)
    caller.new_char.db.chargen_step = "menunode_synth_gender"
    caller.new_char.db.gender = None
    assign_default_portrait(caller.new_char, "synth")
    send_chargen_preview(caller, caller.new_char, "portrait_selected")
    text = dedent(
        """
        |cStandard Synth Chassis|n

        Synth chassis have no gender. Your pre-Synth identity has been recorded.
        """
    )
    return text, {
        "key": ("1", "Continue", "continue"),
        "desc": "Continue to background selection.",
        "goto": "menunode_background",
    }


# ---------------------------------------------------------------------
# Background
# ---------------------------------------------------------------------


def menunode_background(caller, raw_string="", **kwargs):
    """
    Display the available backgrounds.
    """

    caller.new_char.db.chargen_step = "menunode_background"

    text = dedent(
        """
        |cChoose a Background|n

        Backgrounds currently provide only a title and description.
        They do not provide traits or mechanical benefits.
        """
    )

    options = []

    for index, (background_key, background) in enumerate(BACKGROUNDS.items(), start=1):
        options.append(
            {
                "key": (str(index), background["name"], background_key),
                "desc": f"{background['name']} — {background['description']}",
                "goto": (
                    _set_background,
                    {"background_key": background_key},
                ),
            }
        )

    options.append(
        {
            "key": (str(len(options) + 1), "Back", "back", "b"),
            "desc": "Choose a different species.",
            "goto": "menunode_species",
        }
    )

    return text, options


def _set_background(caller, raw_string, background_key=None, **kwargs):
    """
    Store the selected background key.
    """

    if background_key not in BACKGROUNDS:
        return "menunode_background"

    caller.new_char.db.background = background_key

    return "menunode_career"


# ---------------------------------------------------------------------
# Career
# ---------------------------------------------------------------------


def menunode_career(caller, raw_string="", **kwargs):
    """
    Display the available careers.
    """

    caller.new_char.db.chargen_step = "menunode_career"

    text = dedent(
        """
        |cChoose a Career|n

        Careers are descriptive only for now.
        """
    )

    options = []

    for index, (career_key, career) in enumerate(CAREERS.items(), start=1):
        options.append(
            {
                "key": (str(index), career["name"], career_key),
                "desc": f"{career['name']} — {career['description']}",
                "goto": (
                    _set_career,
                    {"career_key": career_key},
                ),
            }
        )

    options.append(
        {
            "key": (str(len(options) + 1), "Back", "back", "b"),
            "desc": "Choose a different background.",
            "goto": "menunode_background",
        }
    )

    return text, options


def _set_career(caller, raw_string, career_key=None, **kwargs):
    """
    Store the selected career and clear any old specialization.
    """

    if career_key not in CAREERS:
        return "menunode_career"

    caller.new_char.db.career = career_key
    caller.new_char.db.specialization = None

    return "menunode_specialization"


# ---------------------------------------------------------------------
# Specialization
# ---------------------------------------------------------------------


def menunode_specialization(caller, raw_string="", **kwargs):
    """
    Display only the specializations belonging to the chosen career.
    """

    caller.new_char.db.chargen_step = "menunode_specialization"

    career_key = caller.new_char.db.career
    career = CAREERS.get(career_key)

    if not career:
        return "menunode_career"

    text = dedent(
        f"""
        |cChoose a Specialization|n

        Career: |w{career["name"]}|n

        Specializations are descriptive only for now.
        """
    )

    options = []

    for index, (specialization_key, specialization) in enumerate(
        career["specializations"].items(), start=1
    ):
        options.append(
            {
                "key": (
                    str(index),
                    specialization["name"],
                    specialization_key,
                ),
                "desc": f"{specialization['name']} — {specialization['description']}",
                "goto": (
                    _set_specialization,
                    {"specialization_key": specialization_key},
                ),
            }
        )

    options.append(
        {
            "key": (str(len(options) + 1), "Back", "back", "b"),
            "desc": "Choose a different career.",
            "goto": "menunode_career",
        }
    )

    return text, options


def _set_specialization(
    caller,
    raw_string,
    specialization_key=None,
    **kwargs,
):
    """
    Validate and store the specialization.
    """

    career_key = caller.new_char.db.career
    career = CAREERS.get(career_key)

    if not career:
        return "menunode_career"

    if specialization_key not in career["specializations"]:
        return "menunode_specialization"

    caller.new_char.db.specialization = specialization_key

    return "menunode_review"


# ---------------------------------------------------------------------
# Review and confirmation
# ---------------------------------------------------------------------


def menunode_review(caller, raw_string="", **kwargs):
    """
    Show every choice before final confirmation.
    """

    caller.new_char.db.chargen_step = "menunode_review"

    character = caller.new_char
    if character.db.species == "synth" and not character.db.pre_synth_gender:
        return "menunode_synth_origin_gender"
    if character.db.species != "synth" and not character.db.gender:
        return (
            "menunode_human_gender"
        )
    career = CAREERS.get(character.db.career)

    if not career:
        return "menunode_career"

    specialization = career["specializations"].get(
        character.db.specialization
    )

    if not specialization:
        return "menunode_specialization"

    species_name = _display_name(SPECIES, character.db.species)
    background_name = _display_name(
        BACKGROUNDS,
        character.db.background,
    )

    text = dedent(
        f"""
        |cReview Your Character|n

        |wName:|n {character.key}
        |wSpecies:|n {species_name}
        {f'|wPre-Synth Gender:|n {GENDERS.get(character.db.pre_synth_gender, {}).get("name", "Unselected")}' if character.db.species == "synth" else f'|wGender:|n {GENDERS.get(character.db.gender, {}).get("name", "Unselected")}' }
        |wBackground:|n {background_name}
        |wCareer:|n {career["name"]}
        |wSpecialization:|n {specialization["name"]}

        Confirm this character?
        """
    )

    options = [
        {
            "key": ("1", "Confirm", "confirm", "yes", "y"),
            "desc": "Confirm — Finish character creation.",
            "goto": "menunode_end",
        },
        {
            "key": ("2", "Back", "back", "no", "n"),
            "desc": "Back — Return to specialization selection.",
            "goto": "menunode_specialization",
        },
        {
            "key": ("3", "Restart", "restart"),
            "desc": "Restart — Return to name selection.",
            "goto": "menunode_name",
        },
    ]

    return text, options


# ---------------------------------------------------------------------
# Completion
# ---------------------------------------------------------------------


def menunode_end(caller, raw_string="", **kwargs):
    """
    Finish character creation and place the character in the tutorial.
    """

    character = caller.new_char

    # Initialize vitals and species-appropriate starter life support before the
    # contrib puppets the completed character. Synths receive no oxygen tank.
    from world.resources import initialize_character

    initialize_character(character, include_starter_gear=True)

    # Generate a persistent satellite unique to this character and enter it.
    from world.tutorial import create_tutorial_instance

    tutorial_start = create_tutorial_instance(character, enter=False)
    character.location = tutorial_start

    # Evennia uses this when restoring the character's location.
    character.db.prelogout_location = tutorial_start

    # Removing this attribute tells the contrib that chargen is complete.
    character.attributes.remove("chargen_step")

    text = dedent(
        f"""
        |gCharacter creation complete.|n

        Welcome to Quasar, |w{character.key}|n.
        """
    )

    # Returning no options exits EvMenu. The contrib will then execute
    # "ic <character name>" and place the account into the character.
    return text, None
