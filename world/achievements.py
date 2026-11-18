"""A small notification wrapper around Evennia's achievements contrib."""

from evennia.contrib.game_systems.achievements import (
    get_achievement,
    track_achievements,
)


def track_achievement(achiever, **event):
    """Track an event and announce newly completed achievements."""

    completed = track_achievements(achiever, **event)
    for key in completed:
        data = get_achievement(key) or {}
        achiever.msg(
            f"|h|cAchievement — {data.get('name', key)}|n\n"
            f"{data.get('desc', '')}"
        )
    return completed
