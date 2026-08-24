"""Portable objects and containers used by Quasar."""

from evennia import create_object, search_tag
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


TUTORIAL_BADGE_OWNER_CATEGORY = "quasar_tutorial_badge_owner"
STARTER_OXYGEN_OWNER_CATEGORY = "quasar_starter_oxygen_owner"
STARTER_COMBAT_OWNER_CATEGORY = "quasar_starter_combat_owner"
STARTER_BACKPACK_OWNER_CATEGORY = "quasar_starter_backpack_owner"
CONTAINER_SIZE_CONFIG = "quasar_container_sizes_enabled"
PHYSICAL_COMPONENT_MIGRATION_CONFIG = "quasar_physical_components_migrated_v1"


def _sync_portable_move(item, source_location):
    """Refresh inventory and room GUIs affected by a portable object's move."""

    holders = {location for location in (source_location, item.location) if location}
    for holder in holders:
        if hasattr(holder, "inventory_items"):
            from world.resources import send_character_resources

            send_character_resources(holder, force=True)

    rooms = set()
    for location in holders:
        current = location
        while current and not hasattr(current, "get_room_info"):
            current = current.location
        if current:
            rooms.add(current)
    for room in rooms:
        room.send_room_info()


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


def migrate_legacy_physical_components(force=False):
    """One-time conversion of existing sized objects into component hosts.

    New objects receive their components during ``basetype_setup``. This pass
    exists for objects created before Quasar adopted the components contrib so
    capability-tag searches are complete immediately after deployment.
    """

    if not force and ServerConfig.objects.conf(
        PHYSICAL_COMPONENT_MIGRATION_CONFIG, default=False
    ):
        return {"physical_dimensions": 0, "container_storage": 0}

    migrated = {"physical_dimensions": 0, "container_storage": 0}
    for item in PortableItem.objects.all_family():
        if not item.components.has("physical_dimensions"):
            item._physical_dimensions_component()
            migrated["physical_dimensions"] += 1

    for container in BasicBackpack.objects.all_family():
        if not container.components.has("physical_dimensions"):
            container._physical_dimensions_component()
            migrated["physical_dimensions"] += 1
        if not container.components.has("container_storage"):
            container._container_storage_component()
            migrated["container_storage"] += 1

    ServerConfig.objects.conf(PHYSICAL_COMPONENT_MIGRATION_CONFIG, True)
    return migrated


class PortableItem(PhysicalDimensionsMixin, Object):
    """Base typeclass for ordinary objects a character may carry."""

    is_portable_item = True
    physical_dimensions = ComponentProperty(
        "physical_dimensions", dimensions_cm=(15.0, 10.0, 5.0)
    )

    def at_post_move(self, source_location, **kwargs):
        super().at_post_move(source_location, **kwargs)
        _sync_portable_move(self, source_location)

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
        super().at_post_move(source_location, **kwargs)
        _sync_portable_move(self, source_location)

    def at_object_creation(self):
        super().at_object_creation()
        self.locks.add("get:all();drop:all();give:all()")
        self.capacity = 20
        # Typical external daypack and usable internal envelope measurements.
        self.dimensions_cm = (50.0, 32.0, 20.0)
        self.interior_dimensions_cm = (47.0, 29.0, 17.0)
        self.db.desc = (
            "A rugged 25-liter daypack with a clamshell opening, compression straps, "
            "and room for twenty separate items."
        )

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
        return bool(self.db.equipped)

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
        from world.resources import locomotion_chassis

        lower_body_slots = {"legs", "legwear", "pants", "lower_body"}
        if (
            self.equipment_slot in lower_body_slots
            and locomotion_chassis(wearer) != "bipedal"
            and not bool(self.db.wheel_compatible)
        ):
            if not quiet:
                wearer.msg(
                    f"{self.get_display_name(wearer)} requires bipedal legs; your current "
                    "wheel chassis cannot wear standard legwear."
                )
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
        self.db.equipped = False
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


class OxygenTank(EquipableItem):
    """An equipped life-support source consumed automatically in vacuum."""

    provides_oxygen = True

    def at_object_creation(self):
        super().at_object_creation()
        self.db.equipment_slot = "life_support"
        self.db.equipment_priority = 100
        self.db.oxygen_capacity = 7_200
        self.db.oxygen_remaining = 7_200
        self.db.equipped = False
        self.dimensions_cm = (52.0, 14.0, 14.0)
        self.db.desc = (
            "A compact life-support tank with a universal suit coupling. "
            "Its blue gauge reports the remaining breathable supply."
        )

    def consume_oxygen(self, amount):
        amount = max(0, int(amount))
        remaining = max(0, int(self.db.oxygen_remaining or 0))
        consumed = min(remaining, amount)
        self.db.oxygen_remaining = remaining - consumed
        return consumed

    def refill(self, amount=None):
        capacity = max(0, int(self.db.oxygen_capacity or 0))
        remaining = max(0, int(self.db.oxygen_remaining or 0))
        amount = capacity if amount is None else max(0, int(amount))
        self.db.oxygen_remaining = min(capacity, remaining + amount)
        if self.location and hasattr(self.location, "sessions"):
            self.location.db.oxygen_warning_level = 0
        return int(self.db.oxygen_remaining) - remaining

    def get_display_desc(self, looker, **kwargs):
        description = super().get_display_desc(looker, **kwargs)
        capacity = max(0, int(self.db.oxygen_capacity or 0))
        remaining = max(0, int(self.db.oxygen_remaining or 0))
        minutes, seconds = divmod(remaining, 60)
        state = "equipped" if self.is_equipped else "not equipped"
        return (
            f"{description}\nIts gauge reads {minutes}:{seconds:02d} of "
            f"{capacity // 60} minutes; it is {state}."
        )


class Weapon(EquipableItem):
    """Base weapon occupying the single ready-weapon slot."""

    is_weapon = True

    def at_object_creation(self):
        super().at_object_creation()
        from world.combat import AttackCategory

        self.db.equipment_slot = "weapon"
        self.db.weapon_family = "melee"
        self.db.attack_category = AttackCategory.MELEE_ENERGY.value
        self.db.damage_min = 5
        self.db.damage_max = 8
        self.db.recovery = 2.0
        self.db.equipped = False


class CompactArcCutter(Weapon):
    """Reliable starter melee tool and weapon."""

    def at_object_creation(self):
        super().at_object_creation()
        from world.combat import AttackCategory

        self.db.attack_category = AttackCategory.MELEE_ENERGY.value
        self.db.damage_min = 10
        self.db.damage_max = 14
        self.db.recovery = 2.0
        self.db.accuracy_bonus = 3
        self.dimensions_cm = (31.0, 11.0, 5.0)
        self.db.desc = (
            "A palm-safe industrial cutter that throws a short, brilliant cutting arc. "
            "It is meant for jammed hull panels, but its reinforced grip makes the other "
            "application obvious."
        )


class ServicePulseSidearm(Weapon):
    """Fast starter ranged weapon with better accuracy and lower damage."""

    def at_object_creation(self):
        super().at_object_creation()
        from world.combat import AttackCategory

        self.db.weapon_family = "ranged"
        self.db.attack_category = AttackCategory.RANGED_ENERGY.value
        self.db.damage_min = 7
        self.db.damage_max = 11
        self.db.recovery = 1.6
        self.db.accuracy_bonus = 7
        self.dimensions_cm = (24.0, 15.0, 4.0)
        self.db.desc = (
            "A compact pulse sidearm built for station security. Its low-power packets "
            "trade stopping force for controllability in cramped compartments."
        )


class UtilityPressureSuit(EquipableItem):
    """Starter body armor; life support connects through a separate slot."""

    def at_object_creation(self):
        super().at_object_creation()
        self.db.equipment_slot = "body"
        self.db.wheel_compatible = True
        self.db.equipped = False
        self.db.armor = 4
        self.db.health_bonus = 10
        self.dimensions_cm = (43.0, 31.0, 11.0)
        self.db.desc = (
            "A sealed utility pressure suit patched at the elbows and reinforced through "
            "the chest. It accepts standard life-support couplings but contains no oxygen itself."
        )


class StandardLegwear(EquipableItem):
    """Ordinary pants and similar garments that require bipedal legs."""

    def at_object_creation(self):
        super().at_object_creation()
        self.db.equipment_slot = "legs"
        self.db.wheel_compatible = False
        self.dimensions_cm = (30.0, 25.0, 6.0)
        self.db.desc = "Standard legwear cut for a bipedal body plan."


class TargetingVisor(EquipableItem):
    """Simple head-slot accuracy wearable for proving gear-derived stats."""

    def at_object_creation(self):
        super().at_object_creation()
        self.db.equipment_slot = "head"
        self.db.equipped = False
        self.db.accuracy_bonus = 4
        self.dimensions_cm = (22.0, 18.0, 8.0)
        self.db.desc = (
            "A clear protective visor with a modest rangefinder projected along its lower edge. "
            "A few careful calibration marks have been scratched into the frame."
        )


class LaserRifle(Weapon):
    """A full-length directed-energy rifle used to exercise container fit."""

    def at_object_creation(self):
        super().at_object_creation()
        from world.combat import AttackCategory

        self.db.weapon_family = "ranged"
        self.db.attack_category = AttackCategory.RANGED_ENERGY.value
        self.db.damage_min = 16
        self.db.damage_max = 24
        self.db.recovery = 2.8
        # Comparable to a conventional full-size service rifle, including stock.
        self.dimensions_cm = (88.0, 25.0, 7.0)
        self.db.desc = (
            "A full-length laser rifle with a fixed stock, focusing shroud, and "
            "substantial heat-management spine."
        )


class TutorialAccessBadge(PortableItem):
    """A private tutorial objective item belonging to one character."""

    def at_object_creation(self):
        super().at_object_creation()
        self.db.desc = (
            "A slim blue-white access badge marked with the station's orientation crest. "
            "Its status strip is waiting to be registered."
        )

    @property
    def tutorial_owner_id(self):
        return self.db.tutorial_owner_id

    def assign_to_character(self, character):
        """Bind this badge to one character and enforce private access."""

        self.db.tutorial_owner_id = character.id
        self.tags.add(str(character.id), category=TUTORIAL_BADGE_OWNER_CATEGORY)
        self.locks.add(
            f"view:id({character.id});get:id({character.id});"
            f"give:id({character.id});drop:false()"
        )

    def at_pre_get(self, getter, **kwargs):
        if getter.id != self.tutorial_owner_id:
            getter.msg("That access badge is registered for someone else.")
            return False
        return super().at_pre_get(getter, **kwargs)

    def at_pre_drop(self, dropper, **kwargs):
        dropper.msg("Keep your orientation badge with you until registration is complete.")
        return False

    def at_pre_give(self, giver, getter, **kwargs):
        if giver.id != self.tutorial_owner_id:
            giver.msg("That access badge is not registered to you.")
            return False
        if not getattr(getter, "accept_tutorial_badge", None):
            giver.msg("Your orientation badge should only be given to Guide Lumen.")
            return False
        return True

    def at_give(self, giver, getter, **kwargs):
        """Complete the orientation objective when handed to the guide."""

        super().at_give(giver, getter, **kwargs)
        if not getattr(getter, "accept_tutorial_badge", None):
            return
        getter.accept_tutorial_badge(giver, self)


def find_character_tutorial_badge(character):
    """Return this character's badge, if one already exists."""

    badges = search_tag(str(character.id), category=TUTORIAL_BADGE_OWNER_CATEGORY)
    return next(
        (
            badge
            for badge in badges
            if isinstance(badge, TutorialAccessBadge)
            and badge.tutorial_owner_id == character.id
        ),
        None,
    )


def ensure_character_tutorial_badge(character, supply_room):
    """Create exactly one private badge for an unfinished character."""

    existing = find_character_tutorial_badge(character)
    if existing:
        return existing
    if dict(character.db.tutorial_progress or {}).get("badge_returned"):
        return None

    badge = create_object(
        TutorialAccessBadge,
        key="orientation access badge",
        aliases=["badge", "access badge"],
        location=supply_room,
        home=supply_room,
    )
    badge.assign_to_character(character)
    return badge


def delete_character_tutorial_items(character):
    """Remove private tutorial objects when their owning character is deleted."""

    badge = find_character_tutorial_badge(character)
    if badge:
        badge.delete()


def find_starter_oxygen_tank(character):
    """Return the automatic starter tank assigned to this character."""

    tanks = search_tag(str(character.id), category=STARTER_OXYGEN_OWNER_CATEGORY)
    return next(
        (
            tank
            for tank in tanks
            if isinstance(tank, OxygenTank)
            and int(tank.db.starter_owner_id or 0) == character.id
        ),
        None,
    )


def ensure_starter_oxygen_tank(character):
    """Give organics one equipped tank and ensure Synths receive none."""

    from world.resources import is_synth

    existing = find_starter_oxygen_tank(character)
    if is_synth(character):
        if existing:
            existing.delete()
        return None

    if not existing:
        existing = create_object(
            OxygenTank,
            key="starter oxygen tank",
            aliases=["oxygen tank", "tank", "life support"],
            location=character,
            home=character,
        )
        existing.db.starter_owner_id = character.id
        existing.tags.add(str(character.id), category=STARTER_OXYGEN_OWNER_CATEGORY)
    elif existing.location != character:
        existing.move_to(character, quiet=True)
    existing.equip_to(character, quiet=True)
    return existing


def find_starter_combat_gear(character):
    """Return starter combat objects owned by one character, keyed by role."""

    gear = search_tag(str(character.id), category=STARTER_COMBAT_OWNER_CATEGORY)
    return {
        str(item.db.starter_combat_role): item
        for item in gear
        if int(item.db.starter_owner_id or 0) == character.id
        and item.db.starter_combat_role
    }


def ensure_starter_combat_gear(character):
    """Give every character a small weapon-choice and wearable test kit."""

    from world.combat import AttackCategory

    definitions = {
        "arc_cutter": (CompactArcCutter, "compact arc cutter", ["cutter", "arc cutter"]),
        "sidearm": (
            ServicePulseSidearm,
            "service pulse sidearm",
            ["sidearm", "pistol", "pulse pistol"],
        ),
        "pressure_suit": (
            UtilityPressureSuit,
            "utility pressure suit",
            ["suit", "pressure suit", "utility suit"],
        ),
        "visor": (TargetingVisor, "targeting visor", ["visor"]),
    }
    existing = find_starter_combat_gear(character)
    created = False
    for role, (typeclass, key, aliases) in definitions.items():
        item = existing.get(role)
        if not item:
            item = create_object(typeclass, key=key, aliases=aliases, location=character, home=character)
            item.db.starter_owner_id = character.id
            item.db.starter_combat_role = role
            item.tags.add(str(character.id), category=STARTER_COMBAT_OWNER_CATEGORY)
            existing[role] = item
            created = True
        elif item.location != character:
            item.move_to(character, quiet=True)

    # Reconcile attributes added after a starter item was originally created.
    existing["arc_cutter"].db.attack_category = AttackCategory.MELEE_ENERGY.value
    existing["sidearm"].db.attack_category = AttackCategory.RANGED_ENERGY.value
    species = str(character.db.species or "human").strip().lower()
    for role in ("pressure_suit", "visor"):
        existing[role].db.fitted_for_species = species
    if species != "human":
        existing["pressure_suit"].db.desc = (
            f"A sealed utility pressure suit fitted for a {species.title()} body plan, with "
            "culture-appropriate environmental interfaces and standard Dawnline life-support couplings."
        )
        existing["visor"].db.desc = (
            f"A targeting and protection assembly fitted to {species.title()} sensory anatomy rather than assuming a Human head."
        )

    # Wearables begin equipped. The ready weapon follows specialization but
    # both weapons remain available so testers can immediately compare cadence.
    existing["pressure_suit"].equip_to(character, quiet=True)
    existing["visor"].equip_to(character, quiet=True)
    preferred_role = (
        "sidearm"
        if (
            str(character.db.specialization or "").strip().lower()
            in {"scout", "systems_operator"}
            or "ballistics" in list(character.db.active_skill_trees or [])
        )
        else "arc_cutter"
    )
    equipped_weapon = next(
        (item for item in existing.values() if getattr(item, "is_weapon", False) and item.is_equipped),
        None,
    )
    if not equipped_weapon:
        existing[preferred_role].equip_to(character, quiet=True)

    # A newly created character should begin at its complete derived maximum.
    if created:
        from world.resources import (
            ensure_character_resources,
            restore_health,
            restore_primary_resource,
        )

        ensure_character_resources(character)
        restore_health(character)
        restore_primary_resource(character)
    return existing


def find_starter_backpack(character):
    """Return the automatic basic backpack assigned to one character."""

    backpacks = search_tag(str(character.id), category=STARTER_BACKPACK_OWNER_CATEGORY)
    return next(
        (
            backpack
            for backpack in backpacks
            if int(backpack.db.starter_owner_id or 0) == character.id
        ),
        None,
    )


def ensure_starter_backpack(character):
    """Give a character exactly one persistent twenty-item basic backpack."""

    backpack = find_starter_backpack(character)
    if not backpack:
        backpack = create_object(
            BasicBackpack,
            key="basic backpack",
            aliases=["backpack", "pack", "bag"],
            location=character,
            home=character,
        )
        backpack.db.starter_owner_id = character.id
        backpack.tags.add(str(character.id), category=STARTER_BACKPACK_OWNER_CATEGORY)
    elif backpack.location != character:
        backpack.move_to(character, quiet=True)

    # Reconcile backpacks created before capacity or size tuning changed.
    backpack.capacity = 20
    backpack.dimensions_cm = (50.0, 32.0, 20.0)
    backpack.interior_dimensions_cm = (47.0, 29.0, 17.0)
    return backpack


def delete_character_starter_gear(character):
    """Remove tagged automatic equipment before deleting its character."""

    tank = find_starter_oxygen_tank(character)
    if tank:
        tank.delete()
    backpack = find_starter_backpack(character)
    if backpack:
        backpack.delete()
    for item in find_starter_combat_gear(character).values():
        item.delete()
