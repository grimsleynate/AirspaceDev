"""The single health authority for every damageable entity.

Health lives in one Traits-contrib ``gauge`` named ``health`` on the entity's
TraitHandler (see ``typeclasses.damageable.DamageableMixin``). Everything
else goes through this module:

* ``health_of(entity)`` reads ``(current, maximum)``;
* ``take_damage(target, amount, source=None)`` is the one damage operation;
* ``heal(target, amount=None)`` restores health.

``db.health_current`` / ``db.health_max`` are a one-way, read-only mirror kept
for older tests and tooling. Nothing reads them back except the one-time
migration that runs when an entity's gauge is first created. Writing to them
has no effect on the game.

Authored data (prototypes) sets ``base_health_max``. Each typeclass derives
its real maximum from that in ``calculate_health_max()``.
"""

from math import ceil


DEFAULT_HEALTH = 100
MAX_HEALTH = 1_000_000


def _bounded_int(value, minimum, maximum, default):
    try:
        value = int(value)
    except (TypeError, ValueError):
        value = default
    return max(minimum, min(maximum, value))


def is_damageable(entity):
    return bool(getattr(entity, "is_damageable", False)) and hasattr(entity, "traits")


def _derived_max(entity):
    hook = getattr(entity, "calculate_health_max", None)
    if callable(hook):
        return _bounded_int(hook(), 1, MAX_HEALTH, DEFAULT_HEALTH)
    return _bounded_int(entity.attributes.get("base_health_max"), 1, MAX_HEALTH, DEFAULT_HEALTH)


def _mirror(entity, health):
    entity.db.health_max = int(health.max)
    entity.db.health_current = int(health.current)


def ensure_health(entity):
    """Create or repair the Health gauge and return it.

    The gauge is authoritative. Only when it does not exist yet is the legacy
    ``health_current`` attribute consulted, as a one-time migration.
    """

    maximum = _derived_max(entity)
    health = entity.traits.get("health")
    if health is None:
        legacy_current = entity.attributes.get("health_current")
        entity.traits.add("health", "Health", trait_type="gauge", base=maximum, min=0)
        health = entity.traits.health
        health.current = _bounded_int(legacy_current, 0, maximum, maximum)
    else:
        current = int(health.current)
        if int(health.base) != maximum:
            health.base = maximum
        if current > maximum:
            health.current = maximum
    _mirror(entity, health)
    return health


def health_of(entity):
    """Return ``(current, maximum)`` from the authoritative gauge."""

    if not is_damageable(entity):
        return 0, 1
    health = entity.traits.get("health") or ensure_health(entity)
    return int(health.current), max(1, int(health.max))


def take_damage(target, amount, source=None, damage_type="damage", message=True):
    """Apply damage to any damageable entity and return the health removed.

    This is the only place health goes down. ``target.at_damaged`` sees every
    hit, and ``target.at_health_depleted`` fires once, on the hit that brings
    health to zero.
    """

    if not is_damageable(target):
        return 0
    health = ensure_health(target)
    amount = max(0, int(ceil(amount or 0)))
    before = int(health.current)
    after = max(0, before - amount)
    actual = before - after
    if actual:
        health.current = after
        _mirror(target, health)
    hook = getattr(target, "at_damaged", None)
    if callable(hook):
        hook(actual, source=source, damage_type=damage_type, before=before, after=after, message=message)
    if before > 0 and after <= 0:
        depleted = getattr(target, "at_health_depleted", None)
        if callable(depleted):
            depleted(source=source, damage_type=damage_type)
    return actual


def heal(target, amount=None, source=None):
    """Restore health up to the derived maximum; ``None`` heals fully."""

    if not is_damageable(target):
        return 0
    health = ensure_health(target)
    maximum = int(health.max)
    amount = maximum if amount is None else max(0, int(amount))
    before = int(health.current)
    health.current = min(maximum, before + amount)
    _mirror(target, health)
    restored = int(health.current) - before
    hook = getattr(target, "at_healed", None)
    if callable(hook):
        hook(restored, source=source)
    return restored
