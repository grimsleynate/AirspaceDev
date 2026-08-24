"""Declarative achievement catalog loaded by Evennia's contrib."""

DAWNLINE_ARRIVAL = {
    "name": "Morning, Still Unfinished",
    "desc": "Complete your opening and wake in Dawnline.",
    "category": "tutorial",
    "tracking": "dawnline_arrival",
}

OPENING_DISTRICT_WALK = {
    "name": "A Few Blocks of Tomorrow",
    "desc": "Explore six distinct places in Dawnline's Opening District.",
    "category": "explore",
    "tracking": "Dawnline — Opening District",
    "count": 6,
}

PRACTICED_HANDS = {
    "name": "The Hands Remember",
    "desc": "Gain one hundred practice through use of your Ability Trees.",
    "category": "ability_practice",
    "count": 100,
}

FIRST_HOSTILE = {
    "name": "Nothing Here Dies Symbolically",
    "desc": "Help defeat a hostile creature or machine.",
    "category": "defeat",
    "count": 1,
}
