"""Legacy batch entry point for Quasar's shared tutorial topology.

The distress satellite topology is verified automatically at server startup by
``world.tutorial``. Running ``batchcode tutorial_area`` is no longer required;
this file remains as a safe manual repair and legacy-character migration tool.
"""

from typeclasses.characters import Character
from world.tutorial import (
    ensure_global_tutorial_area,
    ensure_tutorial_instance,
    is_legacy_tutorial_location,
)


ensure_global_tutorial_area()
migrated = []
for character in Character.objects.all_family():
    if character.db.tutorial_complete:
        continue
    should_enter = not character.location or is_legacy_tutorial_location(character.location)
    ensure_tutorial_instance(character, enter=should_enter)
    migrated.append(character.key)

print("Verified Quasar's shared tutorial topology and private character layers.")
if migrated:
    print("Verified unfinished tutorial characters: " + ", ".join(migrated))
else:
    print("No unfinished characters currently require a tutorial layer.")
