# Room effects

Room effects are reusable, composable semantic components. A room stores only
an ordered list of ids in `room.db.room_effect_ids`; executable behavior, CSS,
and media paths never live in the database.

For example:

```python
room.db.room_effect_ids = [
    "wayhouse.frontier_night",
    "wayhouse.electric_lamps",
    "wayhouse.low_wind",
]
room.db.room_effect_period = "night"
```

The registry in `world.room_effects.ROOM_EFFECTS` defines each id. Audio-only,
visual-only, and combined effects may be mixed freely across unrelated rooms.
Period conditions are resolved on the server. Unknown ids and malformed room
attributes fail closed.

Native clients receive trusted visual presets rather than CSS or URLs. Ambient
audio is folded into the existing semantic audio scene and resolved against the
client-owned same-origin catalog.

Visual presets are reusable too. For example, `night_insects` supplies several
grasshoppers hopping along the floor and fireflies drifting throughout the
Character/Gear/Comms panel wherever a registered room effect selects it; it is
not tied to Lone Lamp's room or background.

Account accessibility settings are authoritative. When screen-reader mode is
active—or room effects are disabled—the server sends silence and an empty
visual scene even if the client previously enabled audio.
