"""Small city hostiles and the evidence they leave behind."""

from time import time

from evennia import create_object

from typeclasses.items import PortableItem
from typeclasses.npcs import HostileNPC


class VerminCarcass(PortableItem):
    """A lightweight bounty item produced by one defeated vermin."""

    is_vermin_carcass = True

    def at_object_creation(self):
        super().at_object_creation()
        self.db.vermin_bounty = 1
        self.db.vermin_species = "unknown"
        self.db.expires_at = time() + 900
        self.dimensions_cm = (30.0, 18.0, 12.0)


class CityVermin(HostileNPC):
    """A weak, non-aggressive hostile maintained by the city spawner."""

    is_vermin = True

    def at_object_creation(self):
        super().at_object_creation()
        self.db.level = 1
        self.db.health_max = 22
        self.db.health_current = 22
        self.db.damage_min = 1
        self.db.damage_max = 3
        self.db.accuracy = -5
        self.db.evasion = 2
        self.db.armor = 0
        self.db.telegraph_seconds = 2.8
        self.db.attack_interval = 4.5
        self.db.experience_reward = 5
        self.db.respawn_seconds = 0
        self.db.aggressive = False
        self.db.vermin_corpse_created = False

    def at_defeat(self, contributors):
        """Leave one collectible carcass and let the spawner replace us."""

        if self.db.vermin_corpse_created or not self.location:
            return
        corpse = create_object(
            VerminCarcass,
            key=f"{self.key} carcass",
            aliases=["carcass", "vermin corpse", f"{self.db.vermin_species} carcass"],
            location=self.location,
            home=self.location,
        )
        corpse.db.vermin_species = str(self.db.vermin_species or self.key)
        corpse.db.vermin_bounty = max(1, int(self.db.vermin_bounty or 1))
        corpse.db.desc = str(
            self.db.corpse_desc
            or "A municipal abatement office would probably pay a few credits for this."
        )
        corpse.db.expires_at = time() + 900
        city_key = str(self.db.vermin_city or "")
        if city_key:
            corpse.tags.add(city_key, category="quasar_vermin_city")
        self.db.vermin_corpse_created = True
        self.db.despawn_at = time() + 4

