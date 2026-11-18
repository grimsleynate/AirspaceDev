"""Typeclass mixin for anything that has health and can take damage."""

from evennia.contrib.rpg.traits import TraitHandler
from evennia.utils import lazy_property


class DamageableMixin:
    """Gives an entity the Health gauge used by ``world.health``.

    Override ``calculate_health_max`` to derive the maximum, and the
    ``at_damaged`` / ``at_healed`` / ``at_health_depleted`` hooks to react.
    """

    is_damageable = True

    @lazy_property
    def traits(self):
        return TraitHandler(self, db_attribute_key="character_traits")

    def calculate_health_max(self):
        base = self.attributes.get("base_health_max")
        if base is None:
            # One-time migration: older rows authored the maximum as health_max.
            base = self.attributes.get("health_max")
            if base is not None:
                self.db.base_health_max = base
        return base

    def at_damaged(self, amount, source=None, damage_type="damage", before=0, after=0, message=True):
        pass

    def at_healed(self, amount, source=None):
        pass

    def at_health_depleted(self, source=None, damage_type="damage"):
        pass
