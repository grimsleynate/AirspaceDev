"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia.objects.objects import DefaultRoom

from .objects import ObjectParent


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


class Room(ObjectParent, DefaultRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Objects.
    """

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

        map_enabled = looker.attributes.get("ascii_map_enabled", default=True)
        if not map_enabled:
            return appearance
        return f"{self.get_ascii_map(looker)}\n{appearance}"

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

        area = self.db.map_area or "Uncharted"
        environment = self.db.map_environment or "interior"
        area_id = self.db.map_area_id or 0
        x = self.db.map_x
        y = self.db.map_y
        z = self.db.map_z or 0

        info = {
            "num": self.id,
            "name": self.key,
            "area": area,
            "environment": environment,
            "details": list(self.db.map_details or []),
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

    def at_desc(self, looker=None, **kwargs):
        """Record exploration and send fresh mapper data for this room."""

        super().at_desc(looker=looker, **kwargs)
        if looker and looker.location == self:
            from world.mapping import record_room_visit

            record_room_visit(looker, self)
            looker.msg(room_info=self.get_room_info(looker))
