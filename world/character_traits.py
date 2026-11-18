"""Persistent character state built on Evennia's Traits contrib.

Health is a contrib ``gauge`` trait and is mirrored into plain Attributes
(``health_max``/``health_current``) so prototypes and tests can read it
without the handler. Game code should use these helpers so the TraitHandler
stays authoritative.
"""


def ensure_health_trait(character, *, health_max, health_current):
    """Create or update the Health gauge and mirror it into Attributes."""

    health = character.traits.get("health")
    if health is None:
        character.traits.add(
            "health", "Health", trait_type="gauge", base=health_max, min=0
        )
        health = character.traits.health
    health.base = health_max
    health.current = health_current
    sync_resource_attributes(character)
    return health


def sync_resource_attributes(character):
    """Mirror the Health gauge into compatibility Attributes and return it."""

    health = character.traits.get("health")
    if health is not None:
        character.db.health_max = int(health.max)
        character.db.health_current = int(health.current)
    return health
