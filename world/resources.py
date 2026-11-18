"""Server-authoritative character health, vitals, and HUD snapshots."""

from math import ceil


RESOURCE_PROTOCOL_REVISION = 7
DEFAULT_HEALTH = 100


def _bounded_int(value, minimum, maximum, default):
    try:
        value = int(value)
    except (TypeError, ValueError):
        value = default
    return max(minimum, min(maximum, value))


def ensure_character_resources(character):
    """Initialize and repair the persistent Health gauge."""

    if character.attributes.get("base_health_max") is None:
        character.db.base_health_max = _bounded_int(
            character.attributes.get("health_max"), 1, 1_000_000, DEFAULT_HEALTH
        )

    from world.combat import calculate_max_health
    from world.character_traits import ensure_health_trait

    health_max = calculate_max_health(character)
    health_current = _bounded_int(
        character.attributes.get("health_current"), 0, health_max, health_max
    )
    ensure_health_trait(
        character, health_max=health_max, health_current=health_current
    )
    return character


def _item_payload(item):
    return {
        "id": item.id,
        "name": item.key,
        "description": str(item.db.desc or ""),
        "equipable": callable(getattr(item, "equip_to", None)),
        "equipped": bool(getattr(item, "is_equipped", False)),
        "container": bool(getattr(item, "is_container", False)),
        "capacity": int(getattr(item, "capacity", 0) or 0),
        "contents_count": len(item.contents),
    }


def build_resource_payload(character):
    """Build the character snapshot used by the native web HUD."""

    ensure_character_resources(character)
    from world.combat import combat_payload, progression_payload

    inventory = getattr(character, "inventory_items", lambda: character.contents)()
    equipment = [
        item for item in character.contents if getattr(item, "is_equipped", False)
    ]
    return {
        "revision": RESOURCE_PROTOCOL_REVISION,
        "character": {
            "id": character.id,
            "name": character.key,
            "level": int(character.db.level or 1),
        },
        "health": {
            "current": int(character.db.health_current),
            "max": int(character.db.health_max),
        },
        "progression": progression_payload(character),
        "combat": combat_payload(character),
        "inventory": [_item_payload(item) for item in inventory],
        "equipment": [_item_payload(item) for item in equipment],
    }


def build_standard_vitals(character):
    """Build common Char.Vitals and Char.StatusVars data for MUD clients."""

    payload = build_resource_payload(character)
    progression = payload["progression"]
    vitals = {
        "hp": payload["health"]["current"],
        "maxhp": payload["health"]["max"],
        "level": progression["level"],
        "xp": progression["experience"],
        "tnl": max(
            0,
            (progression["next_level_at"] or progression["experience"])
            - progression["experience"],
        ),
    }
    status_vars = {
        "hp": "Health",
        "level": "Level",
        "xp": "Experience",
        "tnl": "To Next Level",
    }
    return vitals, status_vars


def send_character_resources(character, session=None, force=False):
    """Send standard GMCP vitals and the richer HUD resource payload."""

    payload = build_resource_payload(character)
    vitals, status_vars = build_standard_vitals(character)
    targets = [session] if session else list(character.sessions.all())
    signature = (vitals, status_vars, payload)
    for target in targets:
        # Last-sent cache lives in ndb: protocol_flags are synced to the Portal.
        if not force and target.ndb.character_resource_state == signature:
            continue
        target.ndb.character_resource_state = signature
        target.msg(
            char_statusvars=status_vars,
            char_vitals=vitals,
            benben_character_resources=payload,
        )
    return payload


def clear_character_resources(session):
    """Clear the web HUD when a session leaves character play."""

    if not session:
        return
    session.ndb.character_resource_state = None
    session.msg(
        benben_character_resources={
            "revision": RESOURCE_PROTOCOL_REVISION,
            "character": None,
            "health": None,
            "progression": None,
            "combat": None,
            "inventory": [],
            "equipment": [],
        }
    )


def apply_damage(character, amount, damage_type="damage", message=True):
    """Apply damage to Health and publish the result."""

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
    """Restore Health up to its derived maximum; ``None`` heals fully."""

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
