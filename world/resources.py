"""Server-authoritative character resources and environmental survival."""

from math import ceil

from world.character_options import BACKGROUNDS, BASIC_SKILL_TREES, CAREERS


RESOURCE_PROTOCOL_REVISION = 6
DEFAULT_HEALTH = 100
DEFAULT_PRIMARY_RESOURCE = 100
ASPHYXIA_GRACE_SECONDS = 10
ASPHYXIA_DAMAGE_INTERVAL = 5
ASPHYXIA_DAMAGE_FRACTION = 0.05

RESOURCE_DEFINITIONS = {
    "tech": {"label": "Tech Points", "short_label": "Tech", "color": "cyan"},
    "acuity": {"label": "Acuity", "short_label": "Acuity", "color": "violet"},
    "skill": {"label": "Skill Points", "short_label": "Skill", "color": "amber"},
}

# These names prepare the resource model for future careers without granting
# mechanics to options which do not yet exist in character creation.
ACUITY_CAREERS = {"mystic", "psion", "seer", "adept", "occultist"}
ACUITY_SPECIALIZATIONS = {"mystic", "psion", "seer", "adept", "occultist"}
TECH_SPECIALIZATIONS = {"engineer", "systems_operator"}


def _bounded_int(value, minimum, maximum, default):
    try:
        value = int(value)
    except (TypeError, ValueError):
        value = default
    return max(minimum, min(maximum, value))


def is_synth(character):
    """Return whether a character is a synthetic and does not need oxygen."""

    return str(character.db.species or "").strip().lower() == "synth"


def locomotion_chassis(character):
    """Return the installed locomotion system used by wearable restrictions."""

    species = str(character.db.species or "human").strip().lower()
    default = {
        "synth": "wheel", "human": "bipedal", "oruun": "aquatic_dense",
        "nimri": "bipedal", "serev": "symbiotic", "kaelith": "radial",
        "veyari": "tripodal",
    }.get(species, "bipedal")
    chassis = str(character.db.locomotion_chassis or default).strip().lower()
    if chassis not in {"wheel", "bipedal", "aquatic_dense", "symbiotic", "radial", "tripodal"}:
        chassis = default
    character.db.locomotion_chassis = chassis
    return chassis


def primary_resource_kind(character):
    """Choose one primary resource from explicit configuration or career."""

    explicit = str(character.db.resource_kind or "").strip().lower()
    if explicit in RESOURCE_DEFINITIONS:
        return explicit

    career_key = str(character.db.career or "").strip().lower()
    specialization_key = str(character.db.specialization or "").strip().lower()
    career = CAREERS.get(career_key, {})
    specialization = career.get("specializations", {}).get(specialization_key, {})
    specialization_resource = str(specialization.get("resource", "")).strip().lower()
    if specialization_resource in RESOURCE_DEFINITIONS:
        return specialization_resource
    configured = str(career.get("resource", "")).strip().lower()
    if configured in RESOURCE_DEFINITIONS:
        return configured
    if specialization_key in TECH_SPECIALIZATIONS or career_key == "technician":
        return "tech"
    if career_key in ACUITY_CAREERS or specialization_key in ACUITY_SPECIALIZATIONS:
        return "acuity"
    return "skill"


def ensure_character_resources(character):
    """Initialize and repair the persistent numeric resource attributes."""

    locomotion_chassis(character)
    existing_health_max = _bounded_int(
        character.attributes.get("health_max"), 1, 1_000_000, DEFAULT_HEALTH
    )
    if character.attributes.get("base_health_max") is None:
        character.db.base_health_max = existing_health_max
    existing_primary_max = _bounded_int(
        character.attributes.get("primary_resource_max"),
        1,
        1_000_000,
        DEFAULT_PRIMARY_RESOURCE,
    )
    if character.attributes.get("base_primary_resource_max") is None:
        character.db.base_primary_resource_max = existing_primary_max

    from world.combat import calculate_max_health, calculate_primary_max

    health_max = calculate_max_health(character)
    health_current = _bounded_int(
        character.attributes.get("health_current"), 0, health_max, health_max
    )
    primary_max = calculate_primary_max(character)
    primary_current = _bounded_int(
        character.attributes.get("primary_resource_current"),
        0,
        primary_max,
        primary_max,
    )

    from world.character_traits import ensure_resource_traits

    ensure_resource_traits(
        character,
        health_max=health_max,
        health_current=health_current,
        primary_max=primary_max,
        primary_current=primary_current,
    )
    return character


def initialize_character(character, include_starter_gear=False):
    """Initialize resource state and optionally reconcile species starter gear."""

    ensure_character_resources(character)
    from world.character_traits import ensure_skill_traits

    ensure_skill_traits(character)
    if include_starter_gear:
        from typeclasses.datapads import ensure_starter_datapad
        from typeclasses.items import (
            ensure_starter_backpack,
            ensure_starter_combat_gear,
            ensure_starter_oxygen_tank,
        )

        ensure_starter_oxygen_tank(character)
        ensure_starter_combat_gear(character)
        ensure_starter_backpack(character)
        ensure_starter_datapad(character)
        ensure_character_resources(character)
    return character


def room_atmosphere(room, character=None):
    """Return a normalized atmosphere name; legacy rooms remain breathable."""

    if not room:
        return "breathable"
    atmosphere_hook = getattr(room, "atmosphere_for", None)
    if atmosphere_hook:
        return str(atmosphere_hook(character) or "breathable").strip().lower()
    atmosphere = str(room.db.atmosphere or "breathable").strip().lower()
    return atmosphere or "breathable"


def is_breathable(room, character=None):
    return room_atmosphere(room, character=character) in {"breathable", "air", "pressurized"}


def equipped_oxygen_source(character, include_empty=True):
    """Find the equipped oxygen provider currently attached to a character."""

    sources = [
        item
        for item in character.contents
        if getattr(item, "provides_oxygen", False) and bool(item.db.equipped)
    ]
    sources.sort(key=lambda item: (int(item.db.equipment_priority or 0), -item.id), reverse=True)
    for source in sources:
        try:
            remaining = int(source.db.oxygen_remaining or 0)
        except (TypeError, ValueError):
            remaining = 0
        if include_empty or remaining > 0:
            return source
    return None


def build_resource_payload(character):
    """Build the rich Quasar resource payload used by the native HUD."""

    ensure_character_resources(character)
    kind = primary_resource_kind(character)
    definition = RESOURCE_DEFINITIONS[kind]
    atmosphere = room_atmosphere(character.location, character=character)
    breathable = is_breathable(character.location, character=character)
    synth = is_synth(character)
    oxygen = None
    if not synth:
        source = equipped_oxygen_source(character)
        try:
            current = max(0, int(source.db.oxygen_remaining or 0)) if source else 0
            maximum = max(0, int(source.db.oxygen_capacity or 0)) if source else 0
        except (TypeError, ValueError):
            current, maximum = 0, 0
        oxygen = {
            "current": min(current, maximum) if maximum else current,
            "max": maximum,
            "source": source.key if source else None,
            "active": not breathable and current > 0,
            "required": not breathable,
        }

    career_key = str(character.db.career or "").strip().lower()
    specialization_key = str(character.db.specialization or "").strip().lower()
    career = CAREERS.get(career_key, {})
    specialization = career.get("specializations", {}).get(specialization_key, {})
    background = BACKGROUNDS.get(str(character.db.background or ""), {})
    active_tree_names = [
        BASIC_SKILL_TREES.get(
            key, {"name": str(key).replace("_", " ").title()}
        )["name"]
        for key in list(character.db.active_skill_trees or [])
    ]
    from world.portraits import ensure_character_portrait

    portrait = ensure_character_portrait(character)

    from world.combat import combat_payload, progression_payload

    def item_payload(item):
        editable = getattr(item, "can_edit_original", None)
        return {
            "id": item.id,
            "name": item.key,
            "description": str(item.db.desc or ""),
            "equipable": callable(getattr(item, "equip_to", None)),
            "equipped": bool(getattr(item, "is_equipped", False)),
            "container": bool(getattr(item, "is_container", False)),
            "capacity": int(getattr(item, "capacity", 0) or 0),
            "contents_count": len(item.contents),
            "readable": bool(getattr(item, "is_readable_document", False)),
            "writable": bool(getattr(item, "is_writable_document", False)),
            "editable": bool(editable(character)) if callable(editable) else False,
            "journal": bool(getattr(item, "is_journal", False)),
        }

    inventory = getattr(character, "inventory_items", lambda: character.contents)()
    equipment = [
        item for item in character.contents if getattr(item, "is_equipped", False)
    ]
    return {
        "revision": RESOURCE_PROTOCOL_REVISION,
        "character": {
            "id": character.id,
            "name": character.key,
            "species": str(character.db.species or "unknown"),
            "gender": None if synth else str(character.db.gender or "neutral"),
            "pre_synth_gender": (
                str(character.db.pre_synth_gender or "neutral") if synth else None
            ),
            "locomotion_chassis": locomotion_chassis(character),
            "portrait_id": portrait["id"],
            "portrait_url": str(character.db.portrait_url or portrait["url"]),
            "career": career.get("name", str(character.db.career or "Unassigned")),
            "specialization": specialization.get(
                "name", str(character.db.specialization or "Unassigned")
            ),
            "background": background.get("name", str(character.db.background or "Unassigned")),
            "active_skill_trees": active_tree_names,
            "level": int(character.db.level or 1),
        },
        "health": {
            "current": int(character.db.health_current),
            "max": int(character.db.health_max),
        },
        "primary": {
            "kind": kind,
            "label": definition["label"],
            "short_label": definition["short_label"],
            "current": int(character.db.primary_resource_current),
            "max": int(character.db.primary_resource_max),
        },
        "oxygen": oxygen,
        "environment": {
            "atmosphere": atmosphere,
            "breathable": breathable,
            "gravity": bool(
                True
                if not character.location
                or character.location.attributes.get("gravity") is None
                else character.location.db.gravity
            ),
        },
        "progression": progression_payload(character),
        "combat": combat_payload(character),
        "inventory": [item_payload(item) for item in inventory],
        "equipment": [item_payload(item) for item in equipment],
    }


def build_standard_vitals(character):
    """Build common Char.Vitals and Char.StatusVars data for MUD clients."""

    payload = build_resource_payload(character)
    primary = payload["primary"]
    kind = primary["kind"]
    vitals = {
        "hp": payload["health"]["current"],
        "maxhp": payload["health"]["max"],
        kind: primary["current"],
        f"max{kind}": primary["max"],
        "level": payload["progression"]["level"],
        "xp": payload["progression"]["experience"],
        "tnl": max(
            0,
            (payload["progression"]["next_level_at"] or payload["progression"]["experience"])
            - payload["progression"]["experience"],
        ),
    }
    status_vars = {
        "hp": "Health",
        kind: primary["label"],
        "level": "Level",
        "xp": "Experience",
        "tnl": "To Next Level",
    }
    if payload["oxygen"] is not None:
        vitals["oxygen"] = payload["oxygen"]["current"]
        vitals["maxoxygen"] = payload["oxygen"]["max"]
        status_vars["oxygen"] = "Oxygen"
    return vitals, status_vars


def send_character_resources(character, session=None, force=False):
    """Send standard GMCP vitals and the richer Quasar resource payload."""

    payload = build_resource_payload(character)
    vitals, status_vars = build_standard_vitals(character)
    targets = [session] if session else list(character.sessions.all())
    signature = (vitals, status_vars, payload)
    for target in targets:
        flags = getattr(target, "protocol_flags", {})
        if not force and flags.get("QUASAR_RESOURCE_STATE") == signature:
            continue
        flags["QUASAR_RESOURCE_STATE"] = signature
        target.msg(
            char_statusvars=status_vars,
            char_vitals=vitals,
            quasar_character_resources=payload,
        )
    return payload


def clear_character_resources(session):
    """Clear the web HUD when a session leaves character play."""

    if not session:
        return
    getattr(session, "protocol_flags", {}).pop("QUASAR_RESOURCE_STATE", None)
    session.msg(
        quasar_character_resources={
            "revision": RESOURCE_PROTOCOL_REVISION,
            "character": None,
            "health": None,
            "primary": None,
            "oxygen": None,
            "environment": None,
            "progression": None,
            "combat": None,
            "inventory": [],
            "equipment": [],
        }
    )


def apply_damage(character, amount, damage_type="damage", message=True):
    """Apply resource-aware damage and publish the result."""

    ensure_character_resources(character)
    amount = max(0, int(ceil(amount)))
    if not amount:
        return 0
    health = character.traits.health
    before = int(health.current)
    after = max(0, before - amount)
    actual = before - after
    health.current = after
    from world.character_traits import sync_resource_attributes

    sync_resource_attributes(character)
    if message and actual:
        if damage_type == "asphyxiation":
            character.msg(f"|rYou take {actual} asphyxiation damage.|n")
        else:
            character.msg(f"|rYou take {actual} damage.|n")
    if actual:
        from world.audio import emit_audio

        emit_audio(character, "combat.player_hurt", priority=80)
    if after <= 0 and not character.db.incapacitated:
        character.db.incapacitated = True
        character.msg("|rYour strength gives out and you lose consciousness.|n")
    send_character_resources(character)
    return actual


def restore_health(character, amount=None):
    """Restore health for future medical and tutorial recovery systems."""

    ensure_character_resources(character)
    health = character.traits.health
    maximum = int(health.max)
    amount = maximum if amount is None else max(0, int(amount))
    before = int(health.current)
    health.current = min(maximum, before + amount)
    from world.character_traits import sync_resource_attributes

    sync_resource_attributes(character)
    if health.current > 0:
        character.db.incapacitated = False
    send_character_resources(character)
    return int(health.current) - before


def spend_primary_resource(character, amount):
    """Spend the career resource atomically; return False when insufficient."""

    ensure_character_resources(character)
    amount = max(0, int(amount))
    primary = character.traits.primary_resource
    current = int(primary.current)
    if amount > current:
        return False
    primary.current = current - amount
    from world.character_traits import sync_resource_attributes

    sync_resource_attributes(character)
    send_character_resources(character)
    return True


def restore_primary_resource(character, amount=None):
    """Restore skill, tech, or acuity points up to the derived maximum."""

    ensure_character_resources(character)
    primary = character.traits.primary_resource
    maximum = int(primary.max)
    amount = maximum if amount is None else max(0, int(amount))
    before = int(primary.current)
    primary.current = min(maximum, before + amount)
    from world.character_traits import sync_resource_attributes

    sync_resource_attributes(character)
    if primary.current != before:
        send_character_resources(character)
    return int(primary.current) - before


def _oxygen_warning_level(remaining, capacity):
    if remaining <= 0:
        return 5
    if remaining <= 60:
        return 4
    if remaining <= 300:
        return 3
    if capacity and remaining / capacity <= 0.10:
        return 2
    if capacity and remaining / capacity <= 0.25:
        return 1
    return 0


def _warn_for_oxygen(character, remaining, capacity):
    level = _oxygen_warning_level(remaining, capacity)
    previous = int(character.db.oxygen_warning_level or 0)
    character.db.oxygen_warning_level = level
    if level <= previous:
        return
    messages = {
        1: "|yYour oxygen supply has fallen below one quarter.|n",
        2: "|yOxygen critical: less than ten percent remains.|n",
        3: "|rOxygen critical: less than five minutes remain.|n",
        4: "|rOxygen critical: less than one minute remains.|n",
        5: "|rYour equipped oxygen supply is empty.|n",
    }
    character.msg(messages[level])


def process_environment_transition(character):
    """Publish atmosphere changes immediately after movement."""

    ensure_character_resources(character)
    atmosphere = room_atmosphere(character.location, character=character)
    if is_synth(character) or is_breathable(character.location, character=character):
        character.db.asphyxia_grace_remaining = None
    changed = character.ndb.last_resource_atmosphere != atmosphere
    character.ndb.last_resource_atmosphere = atmosphere
    send_character_resources(character, force=changed)


def tick_character_environment(character, elapsed=ASPHYXIA_DAMAGE_INTERVAL):
    """Consume equipped oxygen or apply asphyxiation to a connected character."""

    ensure_character_resources(character)
    elapsed = max(1, int(elapsed))

    if is_synth(character) or is_breathable(character.location, character=character):
        character.db.asphyxia_grace_remaining = None
        send_character_resources(character)
        return

    source = equipped_oxygen_source(character)
    remaining = max(0, int(source.db.oxygen_remaining or 0)) if source else 0
    capacity = max(0, int(source.db.oxygen_capacity or 0)) if source else 0
    if source and remaining > 0:
        remaining = max(0, remaining - elapsed)
        source.db.oxygen_remaining = remaining
        character.db.asphyxia_grace_remaining = None
        _warn_for_oxygen(character, remaining, capacity)
        send_character_resources(character)
        return

    _warn_for_oxygen(character, 0, capacity)
    grace = character.attributes.get("asphyxia_grace_remaining")
    if grace is None:
        grace = ASPHYXIA_GRACE_SECONDS
        character.msg("|rNo breathable supply reaches you. Your vision begins to narrow.|n")
    grace = max(0, int(grace) - elapsed)
    character.db.asphyxia_grace_remaining = grace
    if grace <= 0:
        damage = max(1, ceil(int(character.db.health_max) * ASPHYXIA_DAMAGE_FRACTION))
        apply_damage(character, damage, damage_type="asphyxiation")
    else:
        send_character_resources(character)
