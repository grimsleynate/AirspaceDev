"""Room-owned arrival and departure plumbing, with coalesced room-view refresh.

Rooms learn about every mover, whether player, NPC or item, through
``Room.at_object_receive`` / ``Room.at_object_leave``. Those hooks run in the
middle of ``move_to``, so they only *record* work here:

* ``queue_arrival`` remembers that something arrived; ``settle_moves`` runs
  the room's ``at_arrival`` reactions once the move has finished
  (``ObjectParent.at_post_move`` calls it).
* ``mark_room_dirty`` flags a room whose client view changed;
  ``flush_room_views`` sends each flagged room's ``room_info`` once, no matter
  how many changes it saw.

Systems that change room state outside a move (combat ticks, defeat,
respawn) call ``mark_room_dirty`` and flush at the end of their own unit of
work.
"""

_dirty_rooms = {}
_pending_arrivals = []


def enclosing_room(obj):
    """Walk up locations to the first object that renders a room view."""

    current = obj
    while current is not None and not hasattr(current, "send_room_info"):
        current = current.location
    return current


def mark_room_dirty(obj):
    room = enclosing_room(obj)
    if room is not None:
        _dirty_rooms[room.id] = room


def flush_room_views():
    """Send one ``room_info`` refresh per dirty room."""

    while _dirty_rooms:
        _room_id, room = _dirty_rooms.popitem()
        room.send_room_info()


def queue_arrival(room, mover, source_location, move_type):
    _pending_arrivals.append((room, mover, source_location, move_type))


def settle_moves():
    """Run deferred arrival reactions, then refresh the affected views."""

    while _pending_arrivals:
        room, mover, source_location, move_type = _pending_arrivals.pop(0)
        if mover.location == room:
            room.at_arrival(mover, source_location=source_location, move_type=move_type)
    flush_room_views()


def discard_pending():
    """Drop queued work; used by tests and by failed moves."""

    _dirty_rooms.clear()
    _pending_arrivals.clear()
