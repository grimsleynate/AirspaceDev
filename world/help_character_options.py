"""Generated, file-based help for every launch character option."""

from world.character_options import ABILITY_TREES, BACKGROUNDS, MINISKILLS, SPECIES


HELP_ENTRY_DICTS = [
    {
        "key": "species",
        "aliases": ["races", "peoples"],
        "category": "Character Creation",
        "text": (
            "Species determines your character's body, cultural context, portrait family, and one bounded innate benefit. "
            "It never locks an Ability Tree or dictates a profession.\n\n"
            "Launch species: " + ", ".join(entry["name"] for entry in SPECIES.values()) + ". "
            "Use HELP <species name> for the full entry."
        ),
    },
    {
        "key": "backgrounds",
        "aliases": ["background", "origins"],
        "category": "Character Creation",
        "text": (
            "A Background describes the work, institution, or frontier circumstance that trained you before play. "
            "Every Background unlocks exactly one small miniskill; it is useful history, not a class.\n\n"
            "Some Backgrounds also provide a low-power keepsake or trade tool when the fiction calls for it. "
            "Use HELP <background name> for the full entry."
        ),
    },
    {
        "key": "ability trees",
        "aliases": ["ability tree", "trees", "basic trees"],
        "category": "Character Creation",
        "text": (
            "Ability Trees contain the commands that define your current play style. You choose two at creation, can "
            "discover others through play, and retain progress in trees that are not active.\n\n"
            "The two starting slots must hold different trees. Later progression unlocks a third slot and access to rarer "
            "advanced trees. Use HELP <tree name> for flavor and its ability-title list."
        ),
    },
]


for species_key, species in SPECIES.items():
    benefit = species["benefit"]
    HELP_ENTRY_DICTS.append({
        "key": species["name"],
        "aliases": [f"species {species_key}"],
        "category": "Species",
        "text": (
            f"{species['help']}\n\n"
            f"Innate benefit — {benefit['name']}: {benefit['description']}"
        ),
    })


for background_key, background in BACKGROUNDS.items():
    miniskill = MINISKILLS[background["miniskill"]]
    item = background.get("item")
    item_text = f"\nStarting keepsake — {item['name']}: {item['description']}" if item else ""
    HELP_ENTRY_DICTS.append({
        "key": background["name"],
        "aliases": [f"background {background_key.replace('_', ' ')}"],
        "category": "Backgrounds",
        "text": (
            f"{background['help']}\n\n"
            f"Miniskill — {miniskill['name']}: {miniskill['description']}"
            f"{item_text}"
        ),
    })


for tree_key, tree in ABILITY_TREES.items():
    ability_titles = "\n".join(f"  - {title}" for title in tree["abilities"])
    HELP_ENTRY_DICTS.append({
        "key": tree["name"],
        "aliases": [f"tree {tree_key}", f"ability tree {tree_key}"],
        "category": "Ability Trees",
        "text": f"{tree['help']}\n\nUnlockable abilities:\n{ability_titles}",
    })


def get_option_help(catalog_kind, option_key):
    """Return the same authored text used by global HELP for chargen menus."""

    catalogs = {
        "species": SPECIES,
        "background": BACKGROUNDS,
        "ability_tree": ABILITY_TREES,
    }
    option = catalogs.get(catalog_kind, {}).get(option_key)
    if not option:
        return None
    option_name = option["name"].lower()
    return next(
        (entry["text"] for entry in HELP_ENTRY_DICTS if entry["key"].lower() == option_name),
        None,
    )
