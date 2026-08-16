# world/

This folder is meant as a miscellaneous folder for all that other stuff
related to the game. Code which are not commands or typeclasses go
here, like custom economy systems, combat code, batch-files etc. 

You can restructure and even rename this folder as best fits your
sense of organisation. Just remember that if you add new sub
directories, you must add (optionally empty) `__init__.py` files in
them for Python to be able to find the modules within. 

See [DESCRIPTION_STYLE.md](DESCRIPTION_STYLE.md) for Quasar's semantic color
palette, room-output structure, entity-description rules, and puzzle-clue
writing standard.

See [TUTORIAL_DESIGN.md](TUTORIAL_DESIGN.md) for The Long-Dead Signal's isolated
derelict-satellite tutorial flow, room copy, oxygen and vacuum rules,
interactions, the Personal Portable Porter and uploaded-intelligence canon,
Shardwake Reaver evidence, dialogue, items, survivors, enemies, morality,
persistence, acceptance criteria, and implementation sequence.

The tutorial uses one automatically verified 21-room topology. Character
creation adds only a private, invisible story layer of actors, items, state,
atmosphere, and explored-map visits; players sharing a physical room cannot see
or hear one another. Unfinished legacy characters migrate on their next login.
The old ``batchcode tutorial_area`` entry point is now only a manual repair and
migration tool.

See [RESOURCES.md](RESOURCES.md) for Health, Tech Points, Acuity, Skill Points,
the organic/Synth oxygen rules, equipment integration, and GMCP payloads.

See [COMBAT.md](COMBAT.md) for the playable combat prototype, commands, starter
gear, specialization kits, centralized math, XP curve, and tuning checklist.
