"""Portable objects, containers, equipment, and weapons."""

from evennia.contrib.base_systems.components import ComponentProperty
from evennia.contrib.game_systems.containers import ContribContainer
from evennia.server.models import ServerConfig

from .components.physical import (
    ContainerStorage,
    PhysicalDimensions,
    normalized_dimensions,
)
from .objects import Object
from .appearance import ITEM_NAME, style


CONTAINER_SIZE_CONFIG = "container_sizes_enabled"


def _sync_portable_move(item, source_location):
    """Refresh inventory and room GUIs affected by a portable object's move."""

    holders = {location for location in (source_location, item.location) if location}
    for holder in holders:
        if hasattr(holder, "inventory_items"):
            from world.resources import send_character_resources

            send_character_resources(holder, force=True)

    from world.room_events import mark_room_dirty

    for location in holders:
        mark_room_dirty(location)


def container_sizes_enabled():
    """Return the persistent, game-wide dimensional-fit setting."""

    return bool(ServerConfig.objects.conf(CONTAINER_SIZE_CONFIG, default=True))


def set_container_sizes_enabled(enabled):
    """Persist the game-wide dimensional-fit setting."""

    enabled = bool(enabled)
    ServerConfig.objects.conf(CONTAINER_SIZE_CONFIG, enabled)
    return enabled


_normalized_dimensions = normalized_dimensions


class PhysicalDimensionsMixin:
    """Compatibility API and lazy migration for dimensioned hosts."""

    def _physical_dimensions_component(self):
        component = self.components.get("physical_dimensions")
        if component:
            return component
        legacy = self.attributes.get("dimensions_cm")
        component = PhysicalDimensions.create(self, dimensions_cm=legacy)
        self.components.add(component)
        return component

    @property
    def dimensions_cm(self):
        return self._physical_dimensions_component().dimensions_cm

    @dimensions_cm.setter
    def dimensions_cm(self, value):
        self._physical_dimensions_component().set_dimensions(value)


class ContainerStorageMixin:
    """Compatibility API and lazy migration for container storage data."""

    def _container_storage_component(self):
        component = self.components.get("container_storage")
        if component:
            return component
        component = ContainerStorage.create(
            self,
            interior_dimensions_cm=self.attributes.get("interior_dimensions_cm"),
            max_items=self.attributes.get("capacity", default=20),
        )
        self.components.add(component)
        return component

    @property
    def interior_dimensions_cm(self):
        return self._container_storage_component().interior_dimensions_cm

    @interior_dimensions_cm.setter
    def interior_dimensions_cm(self, value):
        self._container_storage_component().set_interior_dimensions(value)

    @property
    def capacity(self):
        return int(self._container_storage_component().max_items or 0)

    @capacity.setter
    def capacity(self, value):
        self._container_storage_component().set_max_items(value)


def object_dimensions_cm(obj):
    """Read component dimensions, falling back to legacy prototype data."""

    dimensions = getattr(obj, "dimensions_cm", None)
    if dimensions is None:
        dimensions = obj.attributes.get("dimensions_cm")
    return normalized_dimensions(dimensions)


class PortableItem(PhysicalDimensionsMixin, Object):
    """Base typeclass for ordinary objects a character may carry."""

    is_portable_item = True
    physical_dimensions = ComponentProperty(
        "physical_dimensions", dimensions_cm=(15.0, 10.0, 5.0)
    )

    def at_post_move(self, source_location, **kwargs):
        # Mark views first; ObjectParent.at_post_move flushes them once.
        _sync_portable_move(self, source_location)
        super().at_post_move(source_location, **kwargs)

    def get_display_name(self, looker=None, **kwargs):
        """Make manipulable items scannable without coloring room prose."""

        return style(super().get_display_name(looker, **kwargs), ITEM_NAME)

    def at_object_creation(self):
        super().at_object_creation()
        self.locks.add("get:all();drop:all();give:all()")
        # A small utility-object envelope. Specialized items replace this with
        # measured dimensions appropriate to their real-world analogue.
        self.dimensions_cm = (15.0, 10.0, 5.0)


class BasicBackpack(PhysicalDimensionsMixin, ContainerStorageMixin, ContribContainer):
    """A 25 L daypack with the contrib's item-count capacity."""

    is_portable_item = True
    is_container = True
    physical_dimensions = ComponentProperty(
        "physical_dimensions", dimensions_cm=(50.0, 32.0, 20.0)
    )
    container_storage = ComponentProperty(
        "container_storage",
        interior_dimensions_cm=(47.0, 29.0, 17.0),
        max_items=20,
    )

    def at_post_move(self, source_location, **kwargs):
        # Mark views first; ObjectParent.at_post_move flushes them once.
        _sync_portable_move(self, source_location)
        super().at_post_move(source_location, **kwargs)

    def at_object_creation(self):
        super().at_object_creation()
        self.locks.add("get:all();drop:all();give:all()")
        self.capacity = 20
        # Typical external daypack and usable internal envelope measurements.
        self.dimensions_cm = (50.0, 32.0, 20.0)
        self.interior_dimensions_cm = (47.0, 29.0, 17.0)

    def get_display_name(self, looker=None, **kwargs):
        return style(super().get_display_name(looker, **kwargs), ITEM_NAME)

    def at_pre_put_in(self, putter, target, **kwargs):
        if target is self:
            putter.msg("You can't put a backpack inside itself.")
            return False
        if not super().at_pre_put_in(putter, target, **kwargs):
            return False
        item_dimensions = object_dimensions_cm(target)
        if container_sizes_enabled() and not self.container_storage.accepts_dimensions(
            item_dimensions
        ):
            item_dimensions = item_dimensions or (
                0,
                0,
                0,
            )
            inside_dimensions = _normalized_dimensions(
                self.interior_dimensions_cm
            ) or (0, 0, 0)
            item_measurements = " × ".join(
                f"{dimension:g}" for dimension in item_dimensions
            )
            inside_measurements = " × ".join(
                f"{dimension:g}" for dimension in inside_dimensions
            )
            putter.msg(
                f"{target.get_display_name(putter)} is too large to fit in "
                f"{self.get_display_name(putter)} ({item_measurements} cm item; "
                f"{inside_measurements} cm inside)."
            )
            return False
        return True


class EquipableItem(PortableItem):
    """Portable item which can occupy one named character equipment slot."""

    is_equipable = True

    @property
    def equipment_slot(self):
        return str(self.db.equipment_slot or "utility")

    @property
    def is_equipped(self):
        """Equipped only while carried by the character that equipped it."""

        if not self.db.equipped or not self.location:
            return False
        wearer_id = self.db.equipped_by
        # Legacy rows predate ``equipped_by``; trust their current holder.
        return wearer_id is None or wearer_id == self.location.id

    def _clear_equipped(self):
        self.db.equipped = False
        self.attributes.remove("equipped_by")

    def at_post_move(self, source_location, **kwargs):
        # Any move off the wearer (theft, script, admin teleport) unequips.
        if self.db.equipped:
            wearer_id = self.db.equipped_by
            if wearer_id is None and source_location:
                wearer_id = source_location.id  # legacy row: it was on the source
            if not self.location or self.location.id != wearer_id:
                self._clear_equipped()
        super().at_post_move(source_location, **kwargs)

    def combat_stat_summary(self):
        """Return short player-facing modifiers for equipment listings."""

        stats = []
        for attribute, label in (
            ("armor", "Armor"),
            ("health_bonus", "Health"),
            ("accuracy_bonus", "Accuracy"),
            ("evasion_bonus", "Evasion"),
            ("crit_bonus", "Crit"),
            ("damage_bonus", "Damage"),
        ):
            value = int(self.attributes.get(attribute, default=0) or 0)
            if value:
                stats.append(f"{label} {value:+d}")
        if getattr(self, "is_weapon", False):
            stats.insert(0, f"Damage {int(self.db.damage_min or 0)}–{int(self.db.damage_max or 0)}")
        return ", ".join(stats)

    def get_display_desc(self, looker, **kwargs):
        description = super().get_display_desc(looker, **kwargs)
        summary = self.combat_stat_summary()
        state = "equipped" if self.is_equipped else "not equipped"
        return f"{description}\n|wEquipment:|n {summary or 'no combat modifiers'}; {state}."

    def equip_to(self, wearer, quiet=False):
        if self.location != wearer:
            if not quiet:
                wearer.msg(f"You must be carrying {self.get_display_name(wearer)} first.")
            return False
        conflicts = [
            item
            for item in wearer.contents
            if item is not self
            and getattr(item, "is_equipped", False)
            and getattr(item, "equipment_slot", None) == self.equipment_slot
        ]
        if conflicts:
            if not quiet:
                wearer.msg(
                    f"Unequip {conflicts[0].get_display_name(wearer)} from your "
                    f"{self.equipment_slot.replace('_', ' ')} slot first."
                )
            return False
        self.db.equipped = True
        self.db.equipped_by = wearer.id
        if not quiet:
            wearer.msg(f"You equip {self.get_display_name(wearer)}.")
        from world.resources import ensure_character_resources, send_character_resources

        ensure_character_resources(wearer)
        send_character_resources(wearer, force=True)
        return True

    def unequip_from(self, wearer, quiet=False):
        if self.location != wearer or not self.is_equipped:
            if not quiet:
                wearer.msg(f"You do not have {self.get_display_name(wearer)} equipped.")
            return False
        inventory_items = getattr(wearer, "inventory_items", lambda: wearer.contents)()
        inventory_capacity = int(getattr(wearer, "inventory_capacity", 0) or 0)
        if inventory_capacity and len(inventory_items) >= inventory_capacity:
            if not quiet:
                wearer.msg(
                    f"Your direct inventory is full ({inventory_capacity} items). "
                    "Free a slot before unequipping it."
                )
            return False
        self._clear_equipped()
        if not quiet:
            wearer.msg(f"You unequip {self.get_display_name(wearer)}.")
        from world.resources import ensure_character_resources, send_character_resources

        ensure_character_resources(wearer)
        send_character_resources(wearer, force=True)
        return True

    def at_pre_drop(self, dropper, **kwargs):
        if self.is_equipped:
            dropper.msg(f"Unequip {self.get_display_name(dropper)} before dropping it.")
            return False
        return super().at_pre_drop(dropper, **kwargs)

    def at_pre_give(self, giver, getter, **kwargs):
        if self.is_equipped:
            giver.msg(f"Unequip {self.get_display_name(giver)} before giving it away.")
            return False
        return super().at_pre_give(giver, getter, **kwargs)


class Weapon(EquipableItem):
    """Base weapon occupying the single ready-weapon slot."""

    is_weapon = True

    def at_object_creation(self):
        super().at_object_creation()
        from world.combat import AttackCategory

        self.db.equipment_slot = "weapon"
        self.db.weapon_family = "melee"
        self.db.attack_category = AttackCategory.WEAPON.value
        self.db.damage_min = 5
        self.db.damage_max = 8
        self.db.recovery = 2.0
        self.db.equipped = False
