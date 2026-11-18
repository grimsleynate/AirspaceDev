"""
Input functions

Input functions are always called from the client (they handle server
input, hence the name).

This module is loaded by being included in the
`settings.INPUT_FUNC_MODULES` tuple.

All *global functions* included in this module are considered
input-handler functions and can be called by the client to handle
input.

An input function must have the following call signature:

    cmdname(session, *args, **kwargs)

Where session will be the active session and *args, **kwargs are extra
incoming arguments and keyword properties.

Evennia's protocols resolve the function by name, so no dispatcher is
needed here:

- Telnet GMCP ``Benben.Map.Get {...}`` is decoded to ``benben_map_get``
  (dots become underscores, lowercased, a ``Core.`` prefix is dropped).
- The websocket webclient sends ``["benben_map_get", [args], {kwargs}]``.

A special command is the "default" command, which is will be called
when no other cmdname matches. It also receives the non-found cmdname
as argument.

    default(session, cmdname, *args, **kwargs)

"""


def benben_map_get(session, *args, **kwargs):
    """Let the client request the active character's map snapshot."""

    character = session.puppet
    if character:
        from world.mapping import send_map_sync

        send_map_sync(character)


def benben_audio_supports(session, *args, **kwargs):
    """Negotiate native audio and immediately provide the active scene."""

    # update_flags syncs to the Portal so support survives a server reload.
    session.update_flags(BENBEN_AUDIO=True)
    character = session.puppet
    if character:
        from world.audio import send_audio_scene

        send_audio_scene(character, session=session, force=True)


def benben_room_effects_supports(session, *args, **kwargs):
    """Negotiate native room visuals and immediately provide the active scene."""

    session.update_flags(BENBEN_ROOM_EFFECTS=True)
    character = session.puppet
    if character:
        from world.room_effects import send_room_effects

        send_room_effects(character, session=session, force=True)


def benben_accessibility_get(session, *args, **kwargs):
    """Return persistent accessibility settings to the native client."""

    # Negotiation may arrive before the csessid login association. Preserve
    # support now so Account.at_post_login can synchronize immediately.
    session.update_flags(BENBEN_ACCESSIBILITY=True)
    account = session.account
    if account:
        from world.accessibility import apply_accessibility_preferences

        apply_accessibility_preferences(
            account, session=session, character=session.puppet
        )


def benben_character_get(session, *args, **kwargs):
    """Let clients request resources, inventory, and equipment."""

    character = session.puppet
    if character:
        from world.resources import send_character_resources

        send_character_resources(character, session=session, force=True)
