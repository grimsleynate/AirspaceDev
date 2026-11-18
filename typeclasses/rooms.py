"""
Room

Rooms are simple containers that has no location of their own.

"""

import re
from collections import defaultdict

from evennia.objects.objects import DefaultRoom
from evennia.utils.utils import iter_to_str
from evennia.utils.ansi import strip_ansi
from evennia.contrib.rpg.rpsystem import ContribRPRoom

from .objects import ObjectParent, hostile_to
from .appearance import ROOM_NAME, style


# GMCP Room.Info convention used by Mudlet and MUSHclient mapper plugins.
# Evennia converts the Python output-command name ``room_info`` to
# ``Room.Info`` for GMCP clients automatically.
DIRECTION_NAMES = {
    "north": "n",
    "northeast": "ne",
    "east": "e",
    "southeast": "se",
    "south": "s",
    "southwest": "sw",
    "west": "w",
    "northwest": "nw",
    "up": "u",
    "down": "d",
    "in": "in",
    "out": "out",
}

ASCII_MAP_DIRECTIONS = {"n", "ne", "e", "se", "s", "sw", "w", "nw", "u", "d", "in", "out"}


def _map_direction(exit_obj):
    """Return a compact, mapper-friendly name for an exit."""

    key = exit_obj.key.strip().lower().replace(" ", "")
    return DIRECTION_NAMES.get(key, key)


def _exit_is_mapper_visible(exit_obj, looker=None):
    """Hide puzzle commands and builder-marked secret exits from map data."""

    visibility_hook = getattr(exit_obj, "is_visible_to_mapper", None)
    if visibility_hook:
        return visibility_hook(looker)
    if exit_obj.db.map_hidden:
        return False
    return not looker or exit_obj.access(looker, "view")


UNCHARTED_AREA_KEY = "uncharted"
UNCHARTED_AREA_NAME = "Uncharted"


def _slug(text):
    return "_".join(re.findall(r"[a-z0-9]+", str(text).lower()))


class Room(ObjectParent, ContribRPRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Objects.
    """

    appearance_template = """
{header}
{name}{extra_name_info}|n
{desc}
{exits}
{characters}
{things}
{footer}
    """

    def get_display_name(self, looker=None, **kwargs):
        """Keep room titles cyan while other entity types use their own color."""

        return style(super().get_display_name(looker, **kwargs), ROOM_NAME)

    def get_display_characters(self, looker, **kwargs):
        """List player characters separately from NPCs."""

        characters = self.filter_visible(
            self.contents_get(content_type="character"), looker, **kwargs
        )
        names = iter_to_str(
            (character.get_display_name(looker, **kwargs) for character in characters),
            endsep=", and",
        )
        return f"|wPlayers:|n {names}" if names else ""

    def get_display_things(self, looker, **kwargs):
        """Separate NPCs, portable items, and inspectable scenery into clear lines."""

        things = self.filter_visible(
            self.contents_get(content_type="object"), looker, **kwargs
        )
        categories = (
            ("Hostiles", [thing for thing in things if hostile_to(thing, looker)]),
            (
                "People",
                [
                    thing
                    for thing in things
                    if getattr(thing, "is_npc", False)
                    and not hostile_to(thing, looker)
                ],
            ),
            (
                "Items",
                [thing for thing in things if getattr(thing, "is_portable_item", False)],
            ),
            (
                "Notable details",
                [thing for thing in things if getattr(thing, "is_inspectable_detail", False)],
            ),
        )
        categorized = {thing for _label, members in categories for thing in members}
        categories += (("Other", [thing for thing in things if thing not in categorized]),)

        lines = []
        for label, members in categories:
            if not members:
                continue
            grouped = defaultdict(list)
            for thing in members:
                grouped[thing.get_display_name(looker, **kwargs)].append(thing)
            names = []
            for display_name, group in sorted(grouped.items()):
                count = len(group)
                names.append(display_name if count == 1 else f"{count}× {display_name}")
            lines.append(f"|w{label}:|n {iter_to_str(names, endsep=', and')}")
        return "\n".join(lines)

    def get_visible_map_exits(self, looker=None):
        """Return the standard directions visible to a particular looker."""

        directions = set()
        for exit_obj in self.exits:
            if not exit_obj.destination:
                continue
            if not _exit_is_mapper_visible(exit_obj, looker):
                continue
            direction = _map_direction(exit_obj)
            if direction in ASCII_MAP_DIRECTIONS:
                directions.add(direction)
        return directions

    def get_ascii_map(self, looker=None):
        """Render a compact local map centered on this room."""

        exits = self.get_visible_map_exits(looker)
        canvas = [[" " for _ in range(15)] for _ in range(5)]

        def put(row, column, text):
            for offset, character in enumerate(text):
                canvas[row][column + offset] = character

        # Current room.
        put(2, 6, "[@]")

        # Neighbor rooms and the lines connecting them to the player.
        neighbors = {
            "nw": (0, 0, 1, 4, "\\"),
            "n": (0, 6, 1, 7, "|"),
            "ne": (0, 12, 1, 10, "/"),
            "w": (2, 0, 2, 3, "---"),
            "e": (2, 12, 2, 9, "---"),
            "sw": (4, 0, 3, 4, "/"),
            "s": (4, 6, 3, 7, "|"),
            "se": (4, 12, 3, 10, "\\"),
        }
        for direction, (room_row, room_col, line_row, line_col, line) in neighbors.items():
            if direction in exits:
                put(room_row, room_col, "[ ]")
                put(line_row, line_col, line)

        lines = ["".join(row).rstrip() for row in canvas]
        while lines and not lines[-1]:
            lines.pop()

        special_exits = []
        for direction, label in (("u", "U"), ("d", "D"), ("in", "IN"), ("out", "OUT")):
            if direction in exits:
                special_exits.append(f"[{label}]")
        if special_exits:
            lines.append("Special: " + " ".join(special_exits))

        ascii_map = "\n".join(lines)
        return ascii_map.replace("[@]", "|c[@]|n").replace("[ ]", "|b[ ]|n")

    def return_appearance(self, looker, **kwargs):
        """Place the optional ASCII map above the normal room description."""

        appearance = super().return_appearance(looker, **kwargs)
        if not looker or looker.location != self:
            return appearance

        from world.accessibility import ascii_maps_enabled

        map_enabled = ascii_maps_enabled(looker)
        if not map_enabled:
            return appearance
        return f"{self.get_ascii_map(looker)}\n{appearance}"

    # -- Area identity -------------------------------------------------------
    # area_key     stable grouping key ("starting_vale"); never shown to players
    # map_area     display name ("Starting Vale"); safe to rename
    # map_area_id  mapper coordinate-system id; one area may span several
    # The Uncharted fallback lives here and nowhere else.

    @property
    def area_key(self):
        key = self.db.area_key
        if key:
            return str(key)
        # Rooms authored before area_key existed derive one from their name.
        return _slug(self.db.map_area or "") or UNCHARTED_AREA_KEY

    @property
    def area_name(self):
        name = self.db.map_area
        if name:
            return str(name)
        key = self.db.area_key
        return str(key).replace("_", " ").title() if key else UNCHARTED_AREA_NAME

    def get_room_info(self, looker=None):
        """
        Build one canonical room payload for external and web mappers.

        The first six fields are the common GMCP ``Room.Info`` shape.
        ``zone``, ``terrain`` and ``coord`` are harmless compatibility
        aliases used by some mapper packages.
        """

        exits = {}
        for exit_obj in self.exits:
            destination = exit_obj.destination
            if not destination:
                continue
            if not _exit_is_mapper_visible(exit_obj, looker):
                continue
            direction = _map_direction(exit_obj)
            # Bespoke movement phrases are valid MUD commands, but are not
            # compass exits and must never leak puzzle solutions through GMCP.
            if direction not in ASCII_MAP_DIRECTIONS:
                continue
            exits[direction] = destination.id

        area = self.area_name
        environment = self.db.map_environment or "interior"
        area_id = self.db.map_area_id or 0
        x = self.db.map_x
        y = self.db.map_y
        z = self.db.map_z or 0

        visible_characters = self.filter_visible(
            self.contents_get(content_type="character"), looker
        )
        visible_objects = self.filter_visible(
            self.contents_get(content_type="object"), looker
        )

        groups = {"player": [], "npc": [], "item": [], "object": []}
        for obj in [*visible_characters, *visible_objects]:
            if obj is looker:
                continue
            category_hook = getattr(obj, "get_client_category", None)
            category = category_hook(looker) if callable(category_hook) else None
            if category not in groups:
                continue
            entry = {"id": obj.id, "name": strip_ansi(obj.get_display_name(looker))}
            if category == "npc":
                entry["hostile"] = hostile_to(obj, looker)
            actions_hook = getattr(obj, "get_client_actions", None)
            actions = actions_hook(looker) if callable(actions_hook) else []
            if actions:
                entry["actions"] = actions
            groups[category].append(entry)

        info = {
            "num": self.id,
            "name": self.key,
            "area": area,
            # Stable key, so clients can tell apart areas that share a name.
            "area_key": self.area_key,
            "environment": environment,
            "details": list(self.db.map_details or []),
            "description": strip_ansi(self.get_display_desc(looker)),
            "players": groups["player"],
            "npcs": groups["npc"],
            "items": groups["item"],
            "objects": groups["object"],
            "exits": exits,
            # Compatibility names used by Aardwolf-style mappers.
            "zone": area,
            "terrain": environment,
        }

        # Coordinates are optional. Automappers can still discover and lay
        # out rooms from the exit graph when a builder has not assigned them.
        if x is not None and y is not None:
            info["coords"] = f"{area_id},{x},{y},{z}"
            info["coord"] = {"id": area_id, "x": x, "y": y, "z": z}

        return info

    def send_room_info(self):
        """Refresh structured room data for every connected character here."""

        for character in self.contents_get(content_type="character"):
            if character.sessions.all():
                character.msg(room_info=self.get_room_info(character))

    # -- Arrival and departure ---------------------------------------------
    # These fire for every mover (player, NPC, item) during move_to. They only
    # record work; world.room_events runs it once the move has finished.

    def at_object_receive(self, moved_obj, source_location, move_type="move", **kwargs):
        super().at_object_receive(moved_obj, source_location, move_type=move_type, **kwargs)
        from world.room_events import mark_room_dirty, queue_arrival

        mark_room_dirty(self)
        queue_arrival(self, moved_obj, source_location, move_type)

    def at_object_leave(self, moved_obj, target_location, move_type="move", **kwargs):
        super().at_object_leave(moved_obj, target_location, move_type=move_type, **kwargs)
        from world.room_events import mark_room_dirty

        mark_room_dirty(self)
        if moved_obj.attributes.get("combat_target_id"):
            from world.combat import leave_combat

            leave_combat(moved_obj, message=True)

    def at_arrival(self, arrival, source_location=None, move_type="move"):
        """Let everything already here react to ``arrival``.

        Rooms with their own behavior (traps, ambience, doors) override this
        and call ``super()``.
        """

        if getattr(arrival, "is_character", False):
            from world.mapping import record_room_visit

            record_room_visit(arrival, self)

        for occupant in list(self.contents):
            if occupant is arrival:
                continue
            hook = getattr(occupant, "at_entity_arrived", None)
            if callable(hook):
                hook(arrival, source_location=source_location, move_type=move_type)

    def at_desc(self, looker=None, **kwargs):
        """Send fresh mapper data for this room (visits are recorded on arrival)."""

        super().at_desc(looker=looker, **kwargs)
        if looker and looker.location == self:
            looker.msg(room_info=self.get_room_info(looker))
