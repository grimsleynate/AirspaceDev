"""Dialogue menu for Guide Lumen in the tutorial station."""


def _progress(caller):
    return dict(caller.db.tutorial_progress or {})


def node_start(caller, raw_string, **kwargs):
    npc = kwargs["npc"]
    progress = _progress(caller)
    if progress.get("badge_returned"):
        intro = f'|c{npc.key}|n says, "Your access is registered. What else can I explain?"'
    elif progress.get("badge_requested"):
        intro = f'|c{npc.key}|n says, "Have you found the access badge in the Supply Cage?"'
    else:
        intro = f'|c{npc.key}|n says, "Welcome to the Quasar Orientation Annex. How can I help?"'

    return intro, (
        {"desc": "Ask about the station", "goto": "node_station"},
        {"desc": "Ask what to do next", "goto": "node_objective"},
        {"desc": "Ask about movement and maps", "goto": "node_navigation"},
        {"desc": "End the conversation", "goto": "node_end"},
    )


def node_station(caller, raw_string, **kwargs):
    return (
        "This annex hangs from a communications satellite near the system's transfer lanes. "
        "Its three decks teach new arrivals how to move, explore, and interact safely.",
        ({"desc": "Return to the other topics", "goto": "node_start"},),
    )


def node_objective(caller, raw_string, **kwargs):
    progress = _progress(caller)
    if progress.get("badge_returned"):
        text = (
            "Your badge is registered. Take the lift up and down to inspect the other decks, "
            "then follow engineering's departure route when you are ready."
        )
    else:
        progress["badge_requested"] = True
        caller.db.tutorial_progress = progress
        text = (
            "Retrieve the |worientation access badge|n from the Supply Cage southwest of here. "
            "Use |wget badge|n, check |winventory|n, then return and type "
            "|wgive badge to guide|n."
        )
    return text, ({"desc": "Return to the other topics", "goto": "node_start"},)


def node_navigation(caller, raw_string, **kwargs):
    return (
        "Use cardinal directions such as |wnorth|n and diagonals such as |wnortheast|n. "
        "The lift accepts |wup|n and |wdown|n. Your map follows the deck you currently occupy.",
        ({"desc": "Return to the other topics", "goto": "node_start"},),
    )


def node_end(caller, raw_string, **kwargs):
    return "The guide nods. \"I'll be here when you need me.\"", None
