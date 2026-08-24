"""Batch entry point for Quasar's private tutorial instances.

Running ``batchcode tutorial_area`` verifies or creates one complete distress
satellite for every unfinished character.
"""

from typeclasses.characters import Character
from world.tutorial import (
    ensure_tutorial_instance,
    is_legacy_tutorial_location,
)


migrated = []
for character in Character.objects.all_family():
    if character.db.tutorial_complete:
        continue
    should_enter = not character.location or is_legacy_tutorial_location(character.location)
    ensure_tutorial_instance(character, enter=should_enter)
    migrated.append(character.key)

print("Verified Quasar's private per-character tutorial instances.")
if migrated:
    print("Verified unfinished tutorial characters: " + ", ".join(migrated))
else:
    print("No unfinished characters currently require a tutorial layer.")
