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

See [TUTORIAL_DESIGN.md](TUTORIAL_DESIGN.md) for the current two-shell tutorial
direction: the Human ancestral Gate dream, the native Open Hatch emergency,
shared combat and two-Basic proficiency lessons, bound Porter, voluntary
permadeath, and convergence on the next morning in private Dawnline rooms.

The implemented 21-room derelict-satellite tutorial is a retired learning
prototype. Its builders, commands, tests, and migration helpers remain in the
repository until an implementation plan replaces them; they are not current
world canon.

See [RESOURCES.md](RESOURCES.md) for the currently implemented prototype
resources and protocol payloads. Its career and creation-menu Synth assumptions
are superseded by the governing design.

See [COMBAT.md](COMBAT.md) for the playable plumbing prototype. Its
specialization kits are not the current three-active-tree combat design.
