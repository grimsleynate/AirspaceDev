"""Default character portrait catalog and character-creation previews."""

from random import choice


PORTRAITS = {
    "human_male": {
        "id": "human_male",
        "species": "human",
        "gender": "male",
        "label": "Human — Male",
        "url": "/static/webclient/portraits/human-masculine.png?v=20260815-2",
    },
    "human_female": {
        "id": "human_female",
        "species": "human",
        "gender": "female",
        "label": "Human — Female",
        "url": "/static/webclient/portraits/human-feminine.png?v=20260815-2",
    },
    "oruun_neutral": {
        "id": "oruun_neutral",
        "species": "oruun",
        "gender": None,
        "label": "Oruun",
        "url": "/static/webclient/portraits/oruun-neutral.png?v=20260823-1",
    },
    "nimri_neutral": {
        "id": "nimri_neutral",
        "species": "nimri",
        "gender": None,
        "label": "Nimri",
        "url": "/static/webclient/portraits/nimri-neutral.png?v=20260823-1",
    },
    "serev_neutral": {
        "id": "serev_neutral",
        "species": "serev",
        "gender": None,
        "label": "Serev",
        "url": "/static/webclient/portraits/serev-neutral.png?v=20260824-1",
    },
    "kaelith_neutral": {
        "id": "kaelith_neutral",
        "species": "kaelith",
        "gender": None,
        "label": "Kaelith",
        "url": "/static/webclient/portraits/kaelith-neutral.png?v=20260823-1",
    },
    "veyari_neutral": {
        "id": "veyari_neutral",
        "species": "veyari",
        "gender": None,
        "label": "Veyari",
        "url": "/static/webclient/portraits/veyari-neutral.png?v=20260824-1",
    },
    "synth_neutral": {
        "id": "synth_neutral",
        "species": "synth",
        "gender": None,
        "label": "Synth — Standard wheel chassis",
        "url": "/static/webclient/portraits/synth-neutral.png?v=20260815-3",
    },
}

GENDERS = {
    "male": {"name": "Male", "description": "You identify as male."},
    "female": {"name": "Female", "description": "You identify as female."},
    "neutral": {
        "name": "Gender-neutral",
        "description": "You do not identify exclusively as male or female.",
    },
}


def portrait_choices(species):
    return [portrait for portrait in PORTRAITS.values() if portrait["species"] == species]


def assign_default_portrait(character, species=None, gender=None):
    """Choose and persist one default. Neutral selection is randomized once."""

    species = str(species or character.db.species or "human").strip().lower()
    if species == "synth":
        portrait = PORTRAITS["synth_neutral"]
    elif species == "human":
        gender = str(gender or character.db.gender or "neutral").strip().lower()
        portrait_gender = gender if gender in {"male", "female"} else choice(("male", "female"))
        portrait = PORTRAITS[f"human_{portrait_gender}"]
    else:
        portrait = PORTRAITS.get(f"{species}_neutral")
        if not portrait:
            portrait = {
                "id": f"{species}_unillustrated",
                "species": species,
                "gender": gender,
                "label": f"{species.title()} — portrait pending",
                "url": "",
            }
    character.db.portrait_id = portrait["id"]
    character.db.portrait_url = portrait["url"]
    return portrait


def ensure_character_portrait(character):
    """Backfill gender and portrait data for characters created before portraits."""

    species = str(character.db.species or "human").strip().lower()
    if species == "synth":
        character.db.gender = None
    elif not character.db.gender:
        character.db.gender = "neutral"
    if species == "synth" and not character.db.pre_synth_gender:
        character.db.pre_synth_gender = "neutral"
    portrait_id = str(character.db.portrait_id or "")
    portrait = PORTRAITS.get(portrait_id)
    if not portrait or portrait["species"] != species:
        portrait = assign_default_portrait(character, species, character.db.gender)
    elif character.db.portrait_url != portrait["url"]:
        character.db.portrait_url = portrait["url"]
    return portrait


def send_chargen_preview(caller, character, step):
    """Send portrait choices/current selection to Quasar's native client."""

    species = str(character.db.species or "").strip().lower()
    portrait = PORTRAITS.get(str(character.db.portrait_id or ""))
    caller.msg(
        quasar_chargen_preview={
            "step": str(step),
            "species": species or None,
            "gender": str(character.db.gender or "") or None,
            "pre_synth_gender": str(character.db.pre_synth_gender or "") or None,
            "portrait": portrait,
            "choices": portrait_choices(species),
        }
    )
