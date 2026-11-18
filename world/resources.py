"""Server-authoritative character health, vitals, and HUD snapshots."""


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

    from world.health import ensure_health

    ensure_health(character)
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
    from world.health import health_of

    health_current, health_max = health_of(character)
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
            "current": health_current,
            "max": health_max,
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
    """Compatibility alias for ``world.health.take_damage``."""

    from world.health import take_damage

    return take_damage(character, amount, damage_type=damage_type, message=message)


def restore_health(character, amount=None):
    """Compatibility alias for ``world.health.heal``."""

    from world.health import heal

    return heal(character, amount=amount)
