"""Small, original combat foundation for Quasar.

All early balance values intentionally live in this module.  The commands,
NPC typeclasses, and web HUD consume this API rather than owning combat math.
That makes the prototype cheap to tune while its cadence is still changing.
"""

from __future__ import annotations

from enum import Enum
from math import ceil
from random import choice, randint
from time import time

from evennia.objects.models import ObjectDB

# ---------------------------------------------------------------------------
# Tuning: progression and cadence
# ---------------------------------------------------------------------------

MAX_LEVEL = 50
XP_PER_LEVEL_STEP = 100
HEALTH_PER_LEVEL = 10
PRIMARY_PER_LEVEL = 5
PRIMARY_REGEN_PER_TICK = 3

BASE_HIT_CHANCE = 75
MIN_HIT_CHANCE = 10
MAX_HIT_CHANCE = 95
BASE_CRIT_CHANCE = 5
CRIT_MULTIPLIER = 1.5
ARMOR_CURVE = 40
MAX_ARMOR_MITIGATION = 0.60
UNARMED_DAMAGE = (4, 7)
UNARMED_RECOVERY = 2.2

COMBAT_TAG_CATEGORY = "quasar_combat_state"
COMBAT_ACTIVE_TAG = "active"


class AttackCategory(str, Enum):
    """Narration families implemented by the current weapon roster."""

    UNARMED = "unarmed"
    RANGED_ENERGY = "ranged_energy"
    MELEE_ENERGY = "melee_energy"


# Each tuple is (attacker perspective, room-observer perspective). Keeping
# prose beside the category enum makes new weapon families easy to audit for
# repetition without coupling narration to individual item typeclasses.
ATTACK_DESCRIPTIONS = {
    AttackCategory.UNARMED: (
        (
            "You snap a straight punch into {target}, dealing {damage} damage.",
            "{attacker} snaps a straight punch into {target}, dealing {damage} damage.",
        ),
        (
            "You pivot through a low kick that catches {target} for {damage} damage.",
            "{attacker} pivots through a low kick that catches {target} for {damage} damage.",
        ),
        (
            "You lunge shoulder-first into {target}, driving through for {damage} damage.",
            "{attacker} lunges shoulder-first into {target}, driving through for {damage} damage.",
        ),
        (
            "You whip a backfist across {target}, landing {damage} damage.",
            "{attacker} whips a backfist across {target}, landing {damage} damage.",
        ),
        (
            "You step inside {target}'s guard and hammer in an elbow for {damage} damage.",
            "{attacker} steps inside {target}'s guard and hammers in an elbow for {damage} damage.",
        ),
        (
            "You drive a palm-heel strike into {target}, inflicting {damage} damage.",
            "{attacker} drives a palm-heel strike into {target}, inflicting {damage} damage.",
        ),
        (
            "You seize an opening and slam a rising knee into {target} for {damage} damage.",
            "{attacker} seizes an opening and slams a rising knee into {target} for {damage} damage.",
        ),
        (
            "You feint high, then bury a compact body blow in {target} for {damage} damage.",
            "{attacker} feints high, then buries a compact body blow in {target} for {damage} damage.",
        ),
    ),
    AttackCategory.RANGED_ENERGY: (
        (
            "You send a bright pulse from {weapon} into {target}, dealing {damage} damage.",
            "{attacker} sends a bright pulse from {weapon} into {target}, dealing {damage} damage.",
        ),
        (
            "You double-tap {weapon}; the second pulse bites into {target} for {damage} damage.",
            "{attacker} double-taps {weapon}; the second pulse bites into {target} for {damage} damage.",
        ),
        (
            "You sweep {weapon} onto target and scorch {target} for {damage} damage.",
            "{attacker} sweeps {weapon} onto target and scorches {target} for {damage} damage.",
        ),
        (
            "You fire a snap shot from {weapon}, catching {target} for {damage} damage.",
            "{attacker} fires a snap shot from {weapon}, catching {target} for {damage} damage.",
        ),
        (
            "You brace {weapon} and place a controlled pulse into {target} for {damage} damage.",
            "{attacker} braces {weapon} and places a controlled pulse into {target} for {damage} damage.",
        ),
        (
            "You fire {weapon} from the hip; its blue-white packet strikes {target} for {damage} damage.",
            "{attacker} fires {weapon} from the hip; its blue-white packet strikes {target} for {damage} damage.",
        ),
        (
            "You lead {target}'s movement and meet it with a pulse for {damage} damage.",
            "{attacker} leads {target}'s movement and meets it with a pulse for {damage} damage.",
        ),
        (
            "You squeeze off a measured burst from {weapon}, burning {target} for {damage} damage.",
            "{attacker} squeezes off a measured burst from {weapon}, burning {target} for {damage} damage.",
        ),
    ),
    AttackCategory.MELEE_ENERGY: (
        (
            "You carve a lateral arc with {weapon}, searing {target} for {damage} damage.",
            "{attacker} carves a lateral arc with {weapon}, searing {target} for {damage} damage.",
        ),
        (
            "You thrust {weapon}'s brilliant edge into {target} for {damage} damage.",
            "{attacker} thrusts {weapon}'s brilliant edge into {target} for {damage} damage.",
        ),
        (
            "You bring {weapon} up in a rising cut that scores {target} for {damage} damage.",
            "{attacker} brings {weapon} up in a rising cut that scores {target} for {damage} damage.",
        ),
        (
            "You reverse your grip and draw {weapon} across {target} for {damage} damage.",
            "{attacker} reverses their grip and draws {weapon} across {target} for {damage} damage.",
        ),
        (
            "You step through a diagonal slash, burning {target} for {damage} damage.",
            "{attacker} steps through a diagonal slash, burning {target} for {damage} damage.",
        ),
        (
            "You deliver a short, controlled chop with {weapon} for {damage} damage.",
            "{attacker} delivers a short, controlled chop with {weapon} for {damage} damage.",
        ),
        (
            "You feint with {weapon}'s hilt, then sweep its arc through {target} for {damage} damage.",
            "{attacker} feints with {weapon}'s hilt, then sweeps its arc through {target} for {damage} damage.",
        ),
        (
            "You catch an opening and rake {weapon} across {target} for {damage} damage.",
            "{attacker} catches an opening and rakes {weapon} across {target} for {damage} damage.",
        ),
    ),
}


MISS_DESCRIPTIONS = {
    AttackCategory.UNARMED: (
        ("You throw a probing jab, but {target} slips aside.", "{attacker} throws a probing jab, but {target} slips aside."),
        ("Your kick cuts through the space {target} just abandoned.", "{attacker}'s kick cuts through the space {target} just abandoned."),
        ("You lunge at {target}, only to overrun the opening.", "{attacker} lunges at {target}, only to overrun the opening."),
        ("You swing a heavy hook that {target} ducks beneath.", "{attacker} swings a heavy hook that {target} ducks beneath."),
    ),
    AttackCategory.RANGED_ENERGY: (
        ("Your pulse flashes past {target} and fades against the bulkhead.", "{attacker}'s pulse flashes past {target} and fades against the bulkhead."),
        ("You fire {weapon}, but {target} moves before the packet arrives.", "{attacker} fires {weapon}, but {target} moves before the packet arrives."),
        ("A hurried shot from {weapon} burns empty air beside {target}.", "A hurried shot from {attacker}'s {weapon} burns empty air beside {target}."),
        ("You lead {target} too far and the pulse goes wide.", "{attacker} leads {target} too far and the pulse goes wide."),
    ),
    AttackCategory.MELEE_ENERGY: (
        ("You slash with {weapon}, but {target} recoils beyond the arc.", "{attacker} slashes with {weapon}, but {target} recoils beyond the arc."),
        ("The bright edge of {weapon} passes a breath short of {target}.", "The bright edge of {attacker}'s {weapon} passes a breath short of {target}."),
        ("You commit to a rising cut that {target} sidesteps.", "{attacker} commits to a rising cut that {target} sidesteps."),
        ("You sweep {weapon} across an opening that closes too quickly.", "{attacker} sweeps {weapon} across an opening that closes too quickly."),
    ),
}


SPECIALIZATION_KITS = {
    "marine": {
        "passive": {
            "key": "frontline_conditioning",
            "name": "Frontline Conditioning",
            "description": "+15 maximum Health and +2 Armor.",
        },
        "active": {
            "key": "breach_strike",
            "name": "Breach Strike",
            "aliases": ("breach", "strike", "power strike"),
            "description": "A committed weapon hit for 150% damage.",
            "cost": 25,
            "cooldown": 5.0,
            "recovery": 2.5,
            "damage_multiplier": 1.5,
        },
    },
    "scout": {
        "passive": {
            "key": "deadeye",
            "name": "Deadeye",
            "description": "+10 Accuracy and +5% critical chance with ranged weapons.",
        },
        "active": {
            "key": "snap_shot",
            "name": "Snap Shot",
            "aliases": ("snap", "quick shot"),
            "description": "A fast, highly accurate shot for 90% damage.",
            "cost": 20,
            "cooldown": 3.0,
            "recovery": 1.1,
            "damage_multiplier": 0.9,
            "accuracy_bonus": 20,
            "requires_ranged": True,
        },
    },
    "engineer": {
        "passive": {
            "key": "field_calibration",
            "name": "Field Calibration",
            "description": "+2 weapon damage and +3 Armor from calibrated gear.",
        },
        "active": {
            "key": "overcharge",
            "name": "Overcharge",
            "aliases": ("charge",),
            "description": "Push an equipped weapon to 135% damage with partial armor bypass.",
            "cost": 30,
            "cooldown": 5.0,
            "recovery": 2.1,
            "damage_multiplier": 1.35,
            "armor_pierce": 0.5,
        },
    },
    "systems_operator": {
        "passive": {
            "key": "threat_analysis",
            "name": "Threat Analysis",
            "description": "+5 Evasion and exact timing on hostile attack telegraphs.",
        },
        "active": {
            "key": "disrupt",
            "name": "Disrupt",
            "aliases": ("interrupt",),
            "description": "A light attack that cancels a telegraphed hostile action.",
            "cost": 25,
            "cooldown": 6.0,
            "recovery": 1.6,
            "damage_multiplier": 0.65,
            "accuracy_bonus": 10,
            "disrupt": True,
        },
    },
}


def _number(value, default=0, minimum=None, maximum=None):
    try:
        value = int(value)
    except (TypeError, ValueError):
        value = default
    if minimum is not None:
        value = max(minimum, value)
    if maximum is not None:
        value = min(maximum, value)
    return value


def specialization_key(character):
    return str(character.db.specialization or "").strip().lower()


def specialization_kit(character):
    return SPECIALIZATION_KITS.get(specialization_key(character))


def experience_for_level(level):
    """Return cumulative XP required to begin ``level``."""

    level = max(1, _number(level, 1))
    return XP_PER_LEVEL_STEP * (level - 1) * level // 2


def ensure_character_progression(character):
    level = _number(character.attributes.get("level"), 1, 1, MAX_LEVEL)
    experience = _number(character.attributes.get("experience"), 0, 0)
    while level < MAX_LEVEL and experience >= experience_for_level(level + 1):
        level += 1
    character.db.level = level
    character.db.experience = experience
    if character.attributes.get("base_health_max") is None:
        character.db.base_health_max = 100
    if character.attributes.get("base_primary_resource_max") is None:
        character.db.base_primary_resource_max = 100
    return level, experience


def progression_payload(character):
    level, experience = ensure_character_progression(character)
    floor = experience_for_level(level)
    ceiling = experience_for_level(level + 1) if level < MAX_LEVEL else floor
    return {
        "level": level,
        "experience": experience,
        "level_experience": max(0, experience - floor),
        "level_experience_max": max(0, ceiling - floor),
        "next_level_at": ceiling if level < MAX_LEVEL else None,
        "max_level": MAX_LEVEL,
    }


def equipped_items(character):
    return [
        item
        for item in getattr(character, "contents", ())
        if getattr(item, "is_equipped", False)
    ]


def equipped_weapon(character):
    return next(
        (item for item in equipped_items(character) if getattr(item, "is_weapon", False)),
        None,
    )


def _equipment_stat(character, name):
    return sum(_number(item.attributes.get(name), 0) for item in equipped_items(character))


def calculate_max_health(character):
    level, _experience = ensure_character_progression(character)
    base = _number(character.attributes.get("base_health_max"), 100, 1)
    total = base + (level - 1) * HEALTH_PER_LEVEL + _equipment_stat(character, "health_bonus")
    if specialization_key(character) == "marine":
        total += 15
    return max(1, total)


def calculate_primary_max(character):
    level, _experience = ensure_character_progression(character)
    base = _number(character.attributes.get("base_primary_resource_max"), 100, 1)
    return max(1, base + (level - 1) * PRIMARY_PER_LEVEL)


def character_combat_stats(character):
    """Build player combat stats from level, specialization, and equipped gear."""

    level, _experience = ensure_character_progression(character)
    weapon = equipped_weapon(character)
    damage_min = _number(getattr(weapon.db, "damage_min", None), UNARMED_DAMAGE[0], 1) if weapon else UNARMED_DAMAGE[0]
    damage_max = _number(getattr(weapon.db, "damage_max", None), UNARMED_DAMAGE[1], damage_min) if weapon else UNARMED_DAMAGE[1]
    accuracy = _equipment_stat(character, "accuracy_bonus")
    evasion = 5 + _equipment_stat(character, "evasion_bonus")
    armor = _equipment_stat(character, "armor")
    crit = BASE_CRIT_CHANCE + _equipment_stat(character, "crit_bonus")
    damage_bonus = _equipment_stat(character, "damage_bonus") + max(0, level - 1)
    if not weapon and str(character.db.species_benefit or "") == "raking_bite":
        # A useful disarmed fallback, intentionally outscaled by real weapons.
        damage_bonus += 1
    spec = specialization_key(character)
    weapon_family = str(weapon.db.weapon_family or "unarmed") if weapon else "unarmed"
    attack_category = str(
        weapon.db.attack_category or AttackCategory.UNARMED.value
    ) if weapon else AttackCategory.UNARMED.value
    if spec == "marine":
        armor += 2
    elif spec == "scout" and weapon_family == "ranged":
        accuracy += 10
        crit += 5
    elif spec == "engineer":
        armor += 3
        damage_bonus += 2
    elif spec == "systems_operator":
        evasion += 5

    return {
        "level": level,
        "max_health": calculate_max_health(character),
        "armor": max(0, armor),
        "accuracy": accuracy,
        "evasion": max(0, evasion),
        "crit_chance": max(0, min(100, crit)),
        "damage_min": damage_min + damage_bonus,
        "damage_max": damage_max + damage_bonus,
        "weapon": weapon,
        "weapon_name": weapon.key if weapon else "unarmed strike",
        "weapon_family": weapon_family,
        "attack_category": attack_category,
        "recovery": float(weapon.db.recovery or UNARMED_RECOVERY) if weapon else UNARMED_RECOVERY,
    }


def hostile_combat_stats(hostile):
    return {
        "level": _number(hostile.db.level, 1, 1),
        "armor": _number(hostile.db.armor, 0, 0),
        "accuracy": _number(hostile.db.accuracy, 0),
        "evasion": _number(hostile.db.evasion, 0, 0),
        "crit_chance": _number(hostile.db.crit_chance, 0, 0, 100),
        "damage_min": _number(hostile.db.damage_min, 1, 1),
        "damage_max": _number(hostile.db.damage_max, 2, 1),
        "weapon_name": str(hostile.db.attack_name or "attack"),
    }


def combat_stats(combatant):
    return hostile_combat_stats(combatant) if getattr(combatant, "is_hostile", False) else character_combat_stats(combatant)


def armor_mitigation(armor):
    armor = max(0, float(armor or 0))
    return min(MAX_ARMOR_MITIGATION, armor / (armor + ARMOR_CURVE))


def resolve_object(dbref):
    try:
        return ObjectDB.objects.get(id=int(dbref))
    except (ObjectDB.DoesNotExist, TypeError, ValueError):
        return None


def current_target(character):
    target = resolve_object(character.db.combat_target_id)
    if (
        not target
        or not getattr(target, "is_hostile", False)
        or target.location != character.location
        or bool(target.db.is_defeated)
    ):
        character.db.combat_target_id = None
        return None
    return target


def combat_payload(character):
    stats = character_combat_stats(character)
    kit = specialization_kit(character) or {}
    active_skill = kit.get("active")
    target = current_target(character)
    now = time()
    target_data = None
    if target:
        target_data = {
            "id": target.id,
            "name": target.key,
            "level": _number(target.db.level, 1, 1),
            "health": _number(target.db.health_current, 0, 0),
            "health_max": _number(target.db.health_max, 1, 1),
            "intent": dict(target.db.combat_intent or {}) or None,
        }
    return {
        "target": target_data,
        "weapon": stats["weapon_name"],
        "weapon_family": stats["weapon_family"],
        "attack_category": stats["attack_category"],
        "damage": {"min": stats["damage_min"], "max": stats["damage_max"]},
        "armor": stats["armor"],
        "accuracy": stats["accuracy"],
        "evasion": stats["evasion"],
        "crit_chance": stats["crit_chance"],
        "recovery_remaining": max(0.0, float(character.db.combat_recovery_until or 0) - now),
        "active_skill": (
            {
                "key": active_skill["key"],
                "name": active_skill["name"],
                "command": f"cast {active_skill['key'].replace('_', ' ')}",
            }
            if active_skill
            else None
        ),
    }


def _message_attack(attacker, target, text_for_attacker, text_for_target, text_for_room):
    attacker.msg(text_for_attacker)
    if target is not attacker and hasattr(target, "msg"):
        target.msg(text_for_target)
    if attacker.location:
        attacker.location.msg_contents(
            text_for_room, exclude=(attacker, target), from_obj=attacker
        )


def _narration_category(attacker_stats):
    try:
        return AttackCategory(attacker_stats.get("attack_category"))
    except (TypeError, ValueError):
        return AttackCategory.UNARMED


def _weapon_narration(attacker, target, attacker_stats, damage=None):
    """Pick a category-specific basic-attack line for a hit or miss."""

    category = _narration_category(attacker_stats)
    descriptions = ATTACK_DESCRIPTIONS[category] if damage is not None else MISS_DESCRIPTIONS[category]
    attacker_template, observer_template = choice(descriptions)
    attacker_values = {
        "attacker": "You",
        "target": target.get_display_name(attacker),
        "weapon": attacker_stats["weapon_name"],
        "damage": damage,
    }
    observer_values = {
        "attacker": attacker.key,
        "target": target.key,
        "weapon": attacker_stats["weapon_name"],
        "damage": damage,
    }
    return (
        attacker_template.format(**attacker_values),
        observer_template.format(**observer_values),
    )


def _apply_combat_damage(attacker, target, damage):
    if getattr(target, "is_hostile", False):
        before = _number(target.db.health_current, 0, 0)
        target.db.health_current = max(0, before - damage)
        after = int(target.db.health_current)
        contributors = dict(target.db.combat_contributors or {})
        contributors[str(attacker.id)] = contributors.get(str(attacker.id), 0) + min(before, damage)
        target.db.combat_contributors = contributors
        damage_hook = getattr(target, "at_combat_damage", None)
        if damage_hook:
            damage_hook(attacker, min(before, damage), before, after)
        if after <= 0:
            defeat_hostile(target)
    else:
        target.apply_damage(damage, damage_type="combat", message=False)
        if _number(target.db.health_current, 0, 0) <= 0:
            handle_character_defeat(target)


def resolve_attack(
    attacker,
    target,
    *,
    action_name="attack",
    damage_multiplier=1.0,
    accuracy_bonus=0,
    armor_pierce=0.0,
    weapon_narration=False,
):
    """Resolve one attack and return a compact result dictionary."""

    attacker_stats = combat_stats(attacker)
    target_stats = combat_stats(target)
    chance = max(
        MIN_HIT_CHANCE,
        min(MAX_HIT_CHANCE, BASE_HIT_CHANCE + attacker_stats["accuracy"] + accuracy_bonus - target_stats["evasion"]),
    )
    attack_label = str(action_name or "attack")
    if randint(1, 100) > chance:
        if weapon_narration:
            attacker_text, observer_text = _weapon_narration(
                attacker, target, attacker_stats
            )
        else:
            attacker_text = f"Your {attack_label} misses {target.get_display_name(attacker)}."
            observer_text = f"{attacker.key}'s {attack_label} misses {target.key}."
        _message_attack(
            attacker,
            target,
            f"|y{attacker_text}|n",
            f"|gYou evade {attacker.get_display_name(target)}'s {attack_label}.|n",
            observer_text,
        )
        return {"hit": False, "critical": False, "damage": 0, "chance": chance}

    raw = randint(attacker_stats["damage_min"], attacker_stats["damage_max"])
    critical = randint(1, 100) <= attacker_stats["crit_chance"]
    if critical:
        raw *= CRIT_MULTIPLIER
    effective_armor = target_stats["armor"] * max(0.0, 1.0 - float(armor_pierce or 0))
    damage = max(1, ceil(raw * float(damage_multiplier) * (1.0 - armor_mitigation(effective_armor))))
    emphasis = " |h|rCritical hit!|n" if critical else ""
    if weapon_narration:
        attacker_text, observer_text = _weapon_narration(
            attacker, target, attacker_stats, damage=damage
        )
    else:
        attacker_text = (
            f"Your {attack_label} hits {target.get_display_name(attacker)} "
            f"for |r{damage}|n damage."
        )
        observer_text = f"{attacker.key}'s {attack_label} hits {target.key} for {damage} damage."
    _message_attack(
        attacker,
        target,
        f"|w{attacker_text}|n{emphasis}",
        f"|r{attacker.get_display_name(target)} hits you with {attack_label} for {damage} damage.|n",
        observer_text,
    )
    _apply_combat_damage(attacker, target, damage)
    return {"hit": True, "critical": critical, "damage": damage, "chance": chance}


def can_character_act(character, now=None, quiet=False):
    now = time() if now is None else now
    remaining = float(character.db.combat_recovery_until or 0) - now
    if remaining > 0:
        if not quiet:
            character.msg(f"You are still recovering ({remaining:.1f}s).")
        return False
    if character.db.incapacitated:
        if not quiet:
            character.msg("You cannot act while incapacitated.")
        return False
    return True


def engage(character, hostile, now=None):
    now = time() if now is None else now
    character.db.combat_target_id = hostile.id
    hostile.db.combat_target_id = character.id
    hostile.db.next_attack_at = min(float(hostile.db.next_attack_at or now + 1), now + 1)
    hostile.tags.add(COMBAT_ACTIVE_TAG, category=COMBAT_TAG_CATEGORY)
    from world.resources import send_character_resources

    send_character_resources(character, force=True)


def player_attack(character, hostile, now=None, automatic=False):
    now = time() if now is None else now
    if not can_character_act(character, now=now, quiet=automatic):
        return None
    if not hostile or not getattr(hostile, "is_hostile", False) or hostile.location != character.location:
        character.msg("You can only attack a hostile target in your current room.")
        return None
    if hostile.db.is_defeated:
        character.msg(f"{hostile.get_display_name(character)} is already down.")
        return None
    engage(character, hostile, now=now)
    stats = character_combat_stats(character)
    result = resolve_attack(
        character,
        hostile,
        action_name=stats["weapon_name"],
        weapon_narration=True,
    )
    character.db.combat_recovery_until = now + stats["recovery"]
    from world.audio import emit_audio
    from world.resources import send_character_resources

    emit_audio(character, "combat.energy_attack", priority=65)
    send_character_resources(character, force=True)
    return result


def find_active_skill(character, query=""):
    active_trees = list(character.db.active_skill_trees or [])
    if active_trees:
        from world.character_options import STARTER_TREE_ABILITIES

        skills = []
        for tree_key in active_trees:
            definition = STARTER_TREE_ABILITIES.get(tree_key)
            if definition:
                skills.append({**definition, "tree_key": tree_key})
        normalized = " ".join(str(query or "").lower().replace("_", " ").split())
        if not normalized:
            return skills[0] if skills else None
        for skill in skills:
            names = {skill["key"].replace("_", " "), skill["name"].lower(), *skill.get("aliases", ())}
            if normalized in names:
                return skill
        return None
    kit = specialization_kit(character)
    active = kit.get("active") if kit else None
    if not active:
        return None
    normalized = " ".join(str(query or "").lower().replace("_", " ").split())
    names = {active["key"].replace("_", " "), active["name"].lower(), *active.get("aliases", ())}
    return active if not normalized or normalized in names else None


def _cooldown_remaining(character, skill, now):
    return max(0.0, float(character.cooldowns.data.get(skill["key"], 0)) - now)


def use_active_skill(character, skill_query, hostile=None, now=None):
    now = time() if now is None else now
    skill = find_active_skill(character, skill_query)
    if not skill:
        character.msg("That ability is not in an active Ability Tree. Use |wskills|n to review your current build.")
        return None
    if character.db.incapacitated:
        character.msg("You cannot cast while incapacitated.")
        return None
    hostile = hostile or current_target(character)
    if not hostile or hostile.location != character.location or hostile.db.is_defeated:
        character.msg(f"{skill['name']} needs a living hostile target here.")
        return None
    stats = character_combat_stats(character)
    if skill.get("requires_ranged") and stats["weapon_family"] != "ranged":
        character.msg(f"{skill['name']} requires an equipped ranged weapon.")
        return None
    remaining = _cooldown_remaining(character, skill, now)
    if remaining > 0:
        character.msg(f"{skill['name']} is cooling down ({remaining:.1f}s).")
        return None

    from world.resources import spend_primary_resource

    if not spend_primary_resource(character, skill["cost"]):
        character.msg(f"You need {skill['cost']} resource points to use {skill['name']}.")
        return None

    engage(character, hostile, now=now)
    was_telegraphing = bool(hostile.db.combat_intent)
    focus = max(0, min(3, int(character.db.combat_focus or 0)))
    result = resolve_attack(
        character,
        hostile,
        action_name=skill["name"],
        damage_multiplier=skill.get("damage_multiplier", 1.0) + (0.1 * focus),
        accuracy_bonus=skill.get("accuracy_bonus", 0),
        armor_pierce=skill.get("armor_pierce", 0.0),
    )
    if skill.get("disrupt"):
        hostile.db.combat_intent = None
        hostile.db.next_attack_at = now + 3.0
        if was_telegraphing:
            character.msg(f"|c{skill['name']} breaks {hostile.key}'s prepared attack.|n")
        else:
            character.msg(f"{hostile.key} was not preparing an attack, but its next action is delayed.")
    if focus:
        character.db.combat_focus = 0
        character.msg(f"|c{skill['name']} consumes {focus} Focus for additional force.|n")
    # Write through the contrib handler. Explicit timestamps keep combat tests
    # and future simulations deterministic when they supply ``now``.
    character.cooldowns.data[skill["key"]] = now + float(skill["cooldown"])
    character.db.combat_recovery_until = now + float(skill["recovery"])
    tree_key = skill.get("tree_key")
    if tree_key:
        from typeclasses.opening_tutorial import OpeningRoom

        if isinstance(character.location, OpeningRoom) and not character.db.opening_tutorial_complete:
            pending = dict(character.db.tutorial_pending_skill_experience or {})
            pending[tree_key] = min(30, int(pending.get(tree_key, 0)) + 10)
            character.db.tutorial_pending_skill_experience = pending
            state = dict(character.db.opening_tutorial_progress or {})
            used = set(state.get("combat_trees_used", []))
            used.add(tree_key)
            state["combat_trees_used"] = sorted(used)
            character.db.opening_tutorial_progress = state
        else:
            from world.character_traits import add_ability_experience

            add_ability_experience(character, tree_key, 10)
    from world.resources import send_character_resources

    send_character_resources(character, force=True)
    return result


def leave_combat(character, message=False):
    hostile = resolve_object(character.db.combat_target_id)
    character.db.combat_target_id = None
    character.db.combat_recovery_until = None
    if hostile and int(hostile.db.combat_target_id or 0) == character.id:
        hostile.db.combat_target_id = None
        hostile.db.combat_intent = None
        hostile.db.next_attack_at = None
        hostile.tags.remove(COMBAT_ACTIVE_TAG, category=COMBAT_TAG_CATEGORY)
    if message:
        character.msg("You break contact and leave the fight behind.")
    from world.resources import send_character_resources

    send_character_resources(character, force=True)


def award_experience(character, amount, source=None):
    amount = max(0, _number(amount, 0))
    if not amount:
        return 0
    old_level, old_xp = ensure_character_progression(character)
    character.db.experience = old_xp + amount
    new_level, _new_xp = ensure_character_progression(character)
    reason = f" from {source}" if source else ""
    character.msg(f"|cYou gain {amount} experience{reason}.|n")
    if new_level > old_level:
        from world.resources import ensure_character_resources, restore_health, restore_primary_resource

        ensure_character_resources(character)
        restore_health(character)
        restore_primary_resource(character)
        character.msg(f"|h|gLevel up! You are now level {new_level}.|n")
    from world.resources import send_character_resources

    send_character_resources(character, force=True)
    return new_level - old_level


def defeat_hostile(hostile):
    if hostile.db.is_defeated:
        return
    hostile.db.is_defeated = True
    hostile.db.health_current = 0
    hostile.db.combat_intent = None
    hostile.db.combat_target_id = None
    hostile.db.respawn_at = time() + max(0, float(hostile.db.respawn_seconds or 0))
    if hostile.location:
        hostile.location.msg_contents(
            f"|h|r{hostile.key}|n collapses, defeated.", from_obj=hostile
        )
    contributors = dict(hostile.db.combat_contributors or {})
    defeat_hook = getattr(hostile, "at_defeat", None)
    if defeat_hook:
        defeat_hook(contributors)
    eligible = [resolve_object(dbref) for dbref in contributors]
    eligible = [character for character in eligible if character and character.location == hostile.location]
    reward = _number(hostile.db.experience_reward, 0, 0)
    share = max(1, reward // len(eligible)) if reward and eligible else 0
    for character in eligible:
        character.db.combat_target_id = None
        from world.achievements import track_quasar_achievement

        track_quasar_achievement(
            character,
            category="defeat",
            tracking=str(hostile.db.achievement_key or hostile.key).lower(),
        )
        if share:
            award_experience(character, share, source=hostile.key)
        else:
            from world.resources import send_character_resources

            send_character_resources(character, force=True)
    if not hostile.db.respawn_seconds:
        hostile.tags.remove(COMBAT_ACTIVE_TAG, category=COMBAT_TAG_CATEGORY)


def reset_hostile(hostile, announce=True):
    hostile.db.is_defeated = False
    hostile.db.health_current = _number(hostile.db.health_max, 1, 1)
    hostile.db.combat_target_id = None
    hostile.db.combat_intent = None
    hostile.db.combat_contributors = {}
    hostile.db.next_attack_at = None
    hostile.db.respawn_at = None
    hostile.tags.remove(COMBAT_ACTIVE_TAG, category=COMBAT_TAG_CATEGORY)
    if announce and hostile.location:
        hostile.location.msg_contents(
            f"|y{hostile.key} reactivates and resumes its patrol.|n", from_obj=hostile
        )


def handle_character_defeat(character):
    """Prototype defeat: disengage and recover without an XP or item penalty."""

    hostile = resolve_object(character.db.combat_target_id)
    leave_combat(character)
    if hostile and getattr(hostile, "is_hostile", False):
        reset_hostile(hostile, announce=False)
    from world.resources import ensure_character_resources, restore_health, restore_primary_resource

    ensure_character_resources(character)
    restore_health(character)
    restore_primary_resource(character)
    from typeclasses.opening_tutorial import OpeningRoom, OpeningHostile

    if isinstance(character.location, OpeningRoom):
        owner_id = character.id
        rooms = [room for room in OpeningRoom.objects.all_family() if int(room.db.tutorial_owner_id or 0) == owner_id]
        state = dict(character.db.opening_tutorial_progress or {})
        defeats = int(state.get("defeat_count", 0)) + 1
        if character.db.species == "human":
            character.db.opening_tutorial_progress = {"shell": "human", "defeated": [], "defeat_count": defeats}
            character.db.tutorial_pending_skill_experience = {}
            character.cooldowns.clear()
            character.db.combat_focus = 0
            character.db.combat_balance = "ready"
            character.db.reaction_ready_at = 0
            character.db.opening_tutorial_decision = None
            character.db.opening_tutorial_build_complete = False
            from world.opening_tutorial import create_opening_tutorial

            create_opening_tutorial(character, enter=True)
            if defeats >= 2:
                new_rooms = [room for room in OpeningRoom.objects.all_family() if int(room.db.tutorial_owner_id or 0) == owner_id]
                for room in new_rooms:
                    for obj in room.contents:
                        if isinstance(obj, OpeningHostile):
                            obj.db.health_max = min(18, int(obj.db.health_max or 18))
                            obj.db.health_current = obj.db.health_max
                            obj.db.damage_min, obj.db.damage_max = 1, 2
            character.db.opening_tutorial_rooms_seen = []
            assistance = " Hostile output has been reduced." if defeats >= 2 else ""
            character.msg(f"|hYou wake violently in the shipboard berth.|n The Icarus alarm begins again. Your face, hands, and two practiced Ability Trees are exactly as the dream remembers them.{assistance}")
            return
        else:
            state["defeat_count"] = defeats
            state["clinic_recovery"] = True
            start_role = "guest_clinic"
        character.db.opening_tutorial_progress = state
        character.db.tutorial_pending_skill_experience = {}
        character.cooldowns.clear()
        character.db.combat_focus = 0
        character.db.combat_balance = "ready"
        character.db.reaction_ready_at = 0
        character.db.opening_tutorial_decision = None
        if defeats >= 2:
            for room in rooms:
                for obj in room.contents:
                    if isinstance(obj, OpeningHostile) and not obj.db.is_defeated:
                        obj.db.health_max = min(18, int(obj.db.health_max or 18))
                        obj.db.health_current = obj.db.health_max
                        obj.db.damage_min, obj.db.damage_max = 1, 2
        start = next((room for room in rooms if room.db.tutorial_role == start_role), None)
        if start:
            character.move_to(start, quiet=True, move_type="teleport")
        assistance = " Hostile output has been reduced." if defeats >= 2 else ""
        character.msg(f"Porter completes a local emergency recovery and returns you to the guest clinic. ‘Let us try awareness before unconsciousness this time.’{assistance}")
        return
    character.msg("|rYou black out.|n Emergency recovery protocols stabilize you and the hostile breaks contact.")


def telegraph_hostile(hostile, character, now):
    duration = max(0.5, float(hostile.db.telegraph_seconds or 2.0))
    intent = {
        "name": str(hostile.db.attack_name or "attack"),
        "resolves_at": now + duration,
        "duration": duration,
    }
    hostile.db.combat_intent = intent
    detail = ""
    if specialization_key(character) == "systems_operator":
        detail = f" |cThreat Analysis: impact in {duration:.1f}s.|n"
    character.msg(f"|h|y{hostile.key} telegraphs {intent['name']}.|n{detail}")
    from world.resources import send_character_resources

    send_character_resources(character, force=True)


def tick_hostile(hostile, now=None):
    now = time() if now is None else now
    if hostile.db.is_defeated:
        if hostile.db.respawn_seconds and float(hostile.db.respawn_at or 0) <= now:
            reset_hostile(hostile)
        return
    character = resolve_object(hostile.db.combat_target_id)
    if character and float(character.db.reaction_ready_at or 0) <= now:
        character.db.combat_balance = "ready"
    if (
        not character
        or character.location != hostile.location
        or character.db.incapacitated
    ):
        hostile.db.combat_target_id = None
        hostile.db.combat_intent = None
        hostile.tags.remove(COMBAT_ACTIVE_TAG, category=COMBAT_TAG_CATEGORY)
        return

    intent = dict(hostile.db.combat_intent or {})
    if intent:
        if float(intent.get("resolves_at", 0)) <= now:
            hostile.db.combat_intent = None
            resolve_attack(hostile, character, action_name=intent.get("name", "attack"))
            hostile.db.next_attack_at = now + max(1.0, float(hostile.db.attack_interval or 4.0))
            from world.resources import send_character_resources

            send_character_resources(character, force=True)
        return
    if float(hostile.db.next_attack_at or 0) <= now:
        telegraph_hostile(hostile, character, now)


def tick_character_combat(character, now=None):
    """Fill space between manual skills with equipped-weapon basic attacks."""

    now = time() if now is None else now
    hostile = current_target(character)
    if not hostile or not can_character_act(character, now=now, quiet=True):
        return None
    return player_attack(character, hostile, now=now, automatic=True)


def tick_combat(now=None):
    """Advance active monsters and regenerate connected character resources."""

    from evennia import SESSION_HANDLER, search_tag
    from world.resources import restore_primary_resource

    now = time() if now is None else now
    for hostile in search_tag(COMBAT_ACTIVE_TAG, category=COMBAT_TAG_CATEGORY):
        if getattr(hostile, "is_hostile", False):
            tick_hostile(hostile, now=now)
    characters = {
        session.puppet
        for session in SESSION_HANDLER.get_sessions()
        if getattr(session, "puppet", None)
    }
    for character in characters:
        if hasattr(character, "apply_damage"):
            restore_primary_resource(character, PRIMARY_REGEN_PER_TICK)
            tick_character_combat(character, now=now)
