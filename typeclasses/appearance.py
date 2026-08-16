"""Semantic ANSI styling shared by Quasar's world-facing typeclasses.

Color is always paired with a textual section label or entity type. It helps
players scan a room, but is never the only way important information is
communicated.
"""


RESET = "|n"
ROOM_NAME = "|h|c"
PLAYER_NAME = "|h|w"
FRIENDLY_NPC_NAME = "|h|g"
HOSTILE_NPC_NAME = "|h|r"
ITEM_NAME = "|h|y"
INTERACTABLE_NAME = "|h|m"
CLUE_TEXT = "|m"


def style(text, ansi_style):
    """Apply a semantic style and guarantee a reset afterward."""

    return f"{ansi_style}{text}{RESET}"
