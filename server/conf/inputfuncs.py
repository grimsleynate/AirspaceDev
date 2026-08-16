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

A special command is the "default" command, which is will be called
when no other cmdname matches. It also receives the non-found cmdname
as argument.

    default(session, cmdname, *args, **kwargs)

"""

def quasar_map_get(session, *args, **kwargs):
    """Let the React client request the active character's map snapshot."""

    character = session.puppet
    if character:
        from world.mapping import send_map_sync

        send_map_sync(character)


def quasar_audio_supports(session, *args, **kwargs):
    """Negotiate native audio and immediately provide the active scene."""

    session.protocol_flags["QUASAR_AUDIO"] = 1
    character = session.puppet
    if character:
        from world.audio import send_audio_scene

        send_audio_scene(character, session=session, force=True)


def quasar_character_get(session, *args, **kwargs):
    """Let web and GMCP clients request an authoritative resource snapshot."""

    character = session.puppet
    if character:
        from world.resources import send_character_resources

        send_character_resources(character, session=session, force=True)


def quasar_journal_get(session, *args, **kwargs):
    """Let clients request the active character's quest and task journals."""

    character = session.puppet
    if character:
        from world.journal import send_journal_sync

        send_journal_sync(character, session=session)


# def oob_echo(session, *args, **kwargs):
#     """
#     Example echo function. Echoes args, kwargs sent to it.
#
#     Args:
#         session (Session): The Session to receive the echo.
#         args (list of str): Echo text.
#         kwargs (dict of str, optional): Keyed echo text
#
#     """
#     session.msg(oob=("echo", args, kwargs))
#
#
# def default(session, cmdname, *args, **kwargs):
#     """
#     Handles commands without a matching inputhandler func.
#
#     Args:
#         session (Session): The active Session.
#         cmdname (str): The (unmatched) command name
#         args, kwargs (any): Arguments to function.
#
#     """
#     pass
