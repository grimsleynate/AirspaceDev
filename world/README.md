# world/

This folder is meant as a miscellaneous folder for all that other stuff
related to the game. Code which are not commands or typeclasses go
here, like custom economy systems, combat code, batch-files etc. 

You can restructure and even rename this folder as best fits your
sense of organisation. Just remember that if you add new sub
directories, you must add (optionally empty) `__init__.py` files in
them for Python to be able to find the modules within.

## Scheduling convention

Before writing anything that waits or repeats, pick the matching primitive:

| What you need | Use |
|---|---|
| Transient one-shot (a message after a beat, a short animation) | `evennia.utils.delay(seconds, callback)`. It is lost on reload, which is fine for this. |
| Durable deadline (respawn, curse expiry, a door that relocks) | Store an absolute timestamp on the entity (e.g. `db.respawn_at`) and let the owning check compare it with `time()`. After a restart, the next check reconciles anything that came due while the server was down. |
| Recurring active behavior (a patrolling NPC, a ticking poison) | Register with the shared game loop, or give the entity its own Script when the behavior is only that entity's. |
| Shared periodic maintenance (world time, global cleanup) | The global ticker (`TickerHandler` or a `GLOBAL_SCRIPTS` entry). |

`delay(..., persistent=True)` exists in Evennia 5.0.1 (`evennia/utils/utils.py`). It pickles the callback and its arguments and replays overdue tasks at startup. Don't use it for game rules: a persisted timestamp is easier to inspect, change and test. The current `combat_system` ticker (`world.combat.tick_combat`) is a known temporary design; don't build new systems on it.
