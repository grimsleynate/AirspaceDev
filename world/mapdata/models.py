"""Persistent character exploration records."""

from django.db import models


class CharacterMapVisit(models.Model):
    """Record that one character has personally visited one room."""

    character = models.ForeignKey(
        "objects.ObjectDB",
        on_delete=models.CASCADE,
        related_name="map_visits_as_character",
    )
    room = models.ForeignKey(
        "objects.ObjectDB",
        on_delete=models.CASCADE,
        related_name="map_visits_as_room",
    )
    visited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "quasar_character_map_visit"
        constraints = [
            models.UniqueConstraint(
                fields=("character", "room"),
                name="unique_quasar_character_room_visit",
            )
        ]

    def __str__(self):
        return f"Character #{self.character_id} visited room #{self.room_id}"
