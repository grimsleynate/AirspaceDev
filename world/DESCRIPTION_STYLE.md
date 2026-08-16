# Quasar world-description style

Quasar uses color to make room output scannable, but color is never the only
signal. Every entity category also has a written section label, and clues must
remain understandable with ANSI disabled or through a screen reader.

## Research basis

- [Achaea's manual](https://www.achaea.com/local/Achaea_Manual.pdf) explicitly
  separates room items from room prose with color when ANSI is enabled. Its
  LOOK structure presents the room and then its exits, entities, and items.
- [Aardwolf's builder guidance](https://www.aardwolf.com/wiki/index.php/Builders/RoomGuidelines)
  keeps long room prose in neutral text, while
  [COLORSET](https://aardwolf.com/wiki/index.php/Help/Colorset) treats room
  names, mobs, exits, and other output categories as independent semantics.
- [Aetolia's ANSI configuration](https://newclient.aetolia.com/game-help?what=ansi-colour-support)
  likewise lets players configure categories instead of relying on colors
  embedded indiscriminately in prose.
- [Discworld's description guidelines](https://discworld.atuin.net/lpc/about/articles/ten_commandments.html)
  require meaningful nouns to be inspectable and dynamic NPCs to be separate
  objects, not permanent sentences in a room description. Its
  [player-housing example](https://discworld.atuin.net/lpc/about/features.html)
  demonstrates descriptions assembled from real room contents.
- [Alter Aeon's False Temple walkthrough](https://wiki.alteraeon.com/index.php/The_False_Temple)
  demonstrates layered puzzle writing: environmental wording points to a
  physical message or note, and examining that object reveals the actionable
  clue.
- [Medievia's new-player guide](https://www.medievia.com/firstlevels.html)
  describes ANSI as a means of distinguishing gameplay and communication
  categories. Its room and zone guidance also favors substantive room prose.

The lesson is consistency, not imitation: neutral prose carries the world;
semantic names and section labels carry interaction affordances.

## Semantic palette

| Category | Style | Room-output label |
| --- | --- | --- |
| Room title | bold cyan | first line |
| Player | bold white | `Players:` |
| Friendly NPC | bold green | `People:` |
| Hostile NPC | bold red | `People:` |
| Portable item | bold yellow | `Items:` |
| Inspectable scenery | bold magenta | `Notable details:` |
| Authored puzzle-clue line | magenta | part of examined detail |

Keep ordinary descriptive prose in the client's normal text color. Red is
reserved for danger and hostile entities; do not use it for decoration.

## Room structure

Room output follows this stable order:

1. Optional ASCII map
2. Room title
3. Neutral room description
4. Exits
5. Players
6. NPCs
7. Portable items
8. Inspectable scenery

Room descriptions should describe the durable environment in two to four
focused sentences. Do not permanently describe an NPC or movable item in the
room prose. Let the corresponding live object add itself to the proper line.

## Entity descriptions

- **Players:** The name is bold white. Their authored description remains
  neutral prose. Equipment or status belongs in later structured sections.
- **NPCs:** Friendly names are green; hostile names will be red. Their examined
  descriptions should cover appearance and readable demeanor. Their room
  presence must come from the NPC object so it disappears when they move.
- **Items:** Manipulable names are yellow and bold. The examined description
  should establish material, condition, obvious controls, and visible state.
  Do not hide a required basic command behind purely decorative prose.
- **Inspectable scenery:** Use `typeclasses.objects.InspectableScenery` for a
  named environmental detail that supports `look <noun>` but cannot be taken.

## Puzzle clues

Use progressive disclosure:

1. The room prose mentions a concrete sensory anomaly or noun.
2. A matching `InspectableScenery` or `PuzzleClue` exists under that noun.
3. Its ordinary description rewards examination without giving away the
   complete solution.
4. When an emphasized clue is appropriate, put only the actionable observation
   in `obj.db.clue_desc`; it will be accented separately from the prose.
5. The eventual action may use a hidden command, but the wording must make that
   action reasonably inferable.

Example:

```python
panel = create_object(
    "typeclasses.objects.PuzzleClue",
    key="scuffed maintenance panel",
    aliases=["panel", "scuffs", "fastener"],
    location=room,
)
panel.db.desc = "Fine scratches gather around one recessed fastener."
panel.db.clue_desc = "The scratches sweep clockwise, then stop sharply to the north."
```

Do not color random nouns merely to manufacture difficulty or importance.
Interaction should be discoverable through consistent object modeling and
careful prose, with color serving only as reinforcement.
