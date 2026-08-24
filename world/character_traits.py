"""Persistent character state built on Evennia's Traits contrib.

The legacy Attributes remain mirrored for saved-character and prototype
compatibility. New game code should use the helpers in this module so the
TraitHandlers stay authoritative at the mechanics boundary.
"""

from world.character_options import ABILITY_TREES, MINISKILLS


SKILL_DESCRIPTIONS = {
    0: "unpracticed",
    25: "familiar",
    100: "trained",
    300: "seasoned",
    750: "expert",
}


def ensure_resource_traits(
    character,
    *,
    health_max,
    health_current,
    primary_max,
    primary_current,
):
    """Create/update Health and primary-resource gauges and mirror Attributes."""

    health = character.traits.get("health")
    if health is None:
        character.traits.add(
            "health", "Health", trait_type="gauge", base=health_max, min=0
        )
        health = character.traits.health
    health.base = health_max
    health.current = health_current

    primary = character.traits.get("primary_resource")
    if primary is None:
        character.traits.add(
            "primary_resource",
            "Primary Resource",
            trait_type="gauge",
            base=primary_max,
            min=0,
        )
        primary = character.traits.primary_resource
    primary.base = primary_max
    primary.current = primary_current
    sync_resource_attributes(character)
    return health, primary


def sync_resource_attributes(character):
    """Mirror contrib gauges into compatibility Attributes and return them."""

    health = character.traits.get("health")
    primary = character.traits.get("primary_resource")
    if health is not None:
        character.db.health_max = int(health.max)
        character.db.health_current = int(health.current)
    if primary is not None:
        character.db.primary_resource_max = int(primary.max)
        character.db.primary_resource_current = int(primary.current)
    return health, primary


def ensure_skill_traits(character):
    """Mirror every known Ability Tree and miniskill into the Skills handler."""

    proficiency = dict(character.db.skill_tree_proficiency or {})
    experience = dict(character.db.skill_tree_experience or {})
    tree_keys = set(character.db.known_skill_trees or [])
    tree_keys.update(character.db.active_skill_trees or [])
    tree_keys.update(proficiency)
    tree_keys.update(experience)
    for trait_key in list(character.skills.all()):
        if trait_key in ABILITY_TREES and trait_key not in tree_keys:
            character.skills.remove(trait_key)
    for tree_key in sorted(tree_keys):
        if tree_key not in ABILITY_TREES:
            continue
        trait = character.skills.get(tree_key)
        practice = max(0, int(experience.get(tree_key, 0)))
        if trait is None:
            character.skills.add(
                tree_key,
                ABILITY_TREES[tree_key]["name"],
                trait_type="counter",
                base=0,
                min=0,
                descs=SKILL_DESCRIPTIONS,
            )
            trait = character.skills.get(tree_key)
        trait.current = practice
        trait.proficiency = max(1, int(proficiency.get(tree_key, 1)))

    unlocked_miniskills = set(character.db.unlocked_miniskills or [])
    current_miniskill = str(character.db.background_miniskill or "")
    if current_miniskill:
        unlocked_miniskills.add(current_miniskill)
    expected_miniskill_traits = {
        f"miniskill_{key}" for key in unlocked_miniskills if key in MINISKILLS
    }
    for trait_key in list(character.skills.all()):
        if trait_key.startswith("miniskill_") and trait_key not in expected_miniskill_traits:
            character.skills.remove(trait_key)
    for miniskill_key in sorted(unlocked_miniskills):
        definition = MINISKILLS.get(miniskill_key)
        if not definition:
            continue
        trait_key = f"miniskill_{miniskill_key}"
        trait = character.skills.get(trait_key)
        if trait is None:
            character.skills.add(
                trait_key,
                definition["name"],
                trait_type="static",
                base=1,
            )
            trait = character.skills.get(trait_key)
        trait.source = "background" if miniskill_key == current_miniskill else "learned"
    return character.skills


def ability_tree_progress(character, tree_key):
    """Return one Ability Tree's (proficiency, practice) from Skills."""

    ensure_skill_traits(character)
    trait = character.skills.get(tree_key)
    if trait is None:
        return 0, 0
    return max(1, int(getattr(trait, "proficiency", 1))), int(trait.current)


def add_ability_experience(character, tree_key, amount):
    """Advance a learned Ability Tree through use and mirror legacy data."""

    if tree_key not in ABILITY_TREES:
        return 0
    ensure_skill_traits(character)
    trait = character.skills.get(tree_key)
    if trait is None:
        return 0
    amount = max(0, int(amount))
    trait.current += amount
    experience = dict(character.db.skill_tree_experience or {})
    experience[tree_key] = int(trait.current)
    character.db.skill_tree_experience = experience
    proficiency = dict(character.db.skill_tree_proficiency or {})
    proficiency[tree_key] = max(1, int(getattr(trait, "proficiency", 1)))
    character.db.skill_tree_proficiency = proficiency
    if amount:
        from world.achievements import track_quasar_achievement

        track_quasar_achievement(
            character, category="ability_practice", tracking=tree_key, count=amount
        )
    return int(trait.current)
