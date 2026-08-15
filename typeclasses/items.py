"""Portable objects used by Quasar."""

from .objects import Object


class PortableItem(Object):
    """Base typeclass for ordinary objects a character may carry."""

    def at_object_creation(self):
        super().at_object_creation()
        self.locks.add("get:all();drop:all();give:all()")


class TutorialAccessBadge(PortableItem):
    """The first tutorial objective item."""

    def at_object_creation(self):
        super().at_object_creation()
        self.db.desc = (
            "A slim blue-white access badge marked with the station's orientation crest. "
            "Its status strip is waiting to be registered."
        )

    def at_give(self, giver, getter, **kwargs):
        """Complete the orientation objective when handed to the guide."""

        super().at_give(giver, getter, **kwargs)
        if not getattr(getter, "accept_tutorial_badge", None):
            return
        getter.accept_tutorial_badge(giver, self)
