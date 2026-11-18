"""
Command sets

All commands in the game must be grouped in a cmdset.  A given command
can be part of any number of cmdsets and cmdsets can be added/removed
and merged onto entities at runtime.

To create new commands to populate the cmdset, see
`commands/command.py`.

This module wraps the default command sets of Evennia; overloads them
to add/remove commands from the default lineup. You can create your
own cmdsets by inheriting from them or directly from `evennia.CmdSet`.

"""

from evennia import default_cmds
from evennia.contrib.rpg.character_creator.character_creator import ContribChargenCmdSet
from evennia.contrib.rpg.rpsystem import RPSystemCmdSet
from evennia.contrib.base_systems.building_menu import GenericBuildingCmd
from evennia.contrib.base_systems.ingame_reports import ReportsCmdSet
from evennia.contrib.game_systems.achievements import CmdAchieve
from evennia.contrib.game_systems.containers import ContainerCmdSet
from evennia.contrib.game_systems.mail import CmdMail

from commands.player_commands import (
    CmdAttack,
    CmdContainerSizes,
    CmdConsider,
    CmdEquip,
    CmdEquipment,
    CmdGreet,
    CmdInventory,
    CmdMap,
    CmdNumpadEast,
    CmdNumpadLook,
    CmdNumpadNorth,
    CmdNumpadNortheast,
    CmdNumpadNorthwest,
    CmdNumpadSouth,
    CmdNumpadSoutheast,
    CmdNumpadSouthwest,
    CmdNumpadWest,
    CmdSoundTest,
    CmdSheet,
    CmdTalk,
    CmdUnequip,
    CmdVitals,
)
from commands.account_commands import CmdCharDelete, CmdIC
from commands.accessibility_commands import CmdAccessibility


class CharacterCmdSet(default_cmds.CharacterCmdSet):
    """
    The `CharacterCmdSet` contains general in-game commands like `look`,
    `get`, etc available on in-game Character objects. It is merged with
    the `AccountCmdSet` when an Account puppets a Character.
    """

    key = "DefaultCharacter"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #
        self.add(CmdMap)
        self.add(CmdGreet)
        self.add(CmdInventory)
        self.add(CmdTalk)
        self.add(CmdSoundTest)
        self.add(CmdVitals)
        self.add(CmdEquipment)
        self.add(CmdEquip)
        self.add(CmdUnequip)
        self.add(CmdAttack)
        self.add(CmdSheet)
        self.add(CmdConsider)
        self.add(CmdContainerSizes)
        self.add(CmdNumpadNorthwest)
        self.add(CmdNumpadNorth)
        self.add(CmdNumpadNortheast)
        self.add(CmdNumpadWest)
        self.add(CmdNumpadLook)
        self.add(CmdNumpadEast)
        self.add(CmdNumpadSouthwest)
        self.add(CmdNumpadSouth)
        self.add(CmdNumpadSoutheast)
        self.add(CmdAchieve())
        self.add(GenericBuildingCmd())
        self.add(RPSystemCmdSet())
        self.add(ContainerCmdSet)


class AccountCmdSet(default_cmds.AccountCmdSet):
    """
    This is the cmdset available to the Account at all times. It is
    combined with the `CharacterCmdSet` when the Account puppets a
    Character. It holds game-account-specific commands, channel
    commands, etc.
    """

    key = "DefaultAccount"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #
        self.add(ContribChargenCmdSet)
        # Override the contrib's name-only IC command with Benben's numbered selector.
        self.add(CmdIC)
        self.add(CmdCharDelete)
        self.add(CmdAccessibility)
        self.add(CmdMail())
        self.add(ReportsCmdSet)


class UnloggedinCmdSet(default_cmds.UnloggedinCmdSet):
    """
    Command set available to the Session before being logged in.  This
    holds commands like creating a new account, logging in, etc.
    """

    key = "DefaultUnloggedin"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #


class SessionCmdSet(default_cmds.SessionCmdSet):
    """
    This cmdset is made available on Session level once logged in. It
    is empty by default.
    """

    key = "DefaultSession"

    def at_cmdset_creation(self):
        """
        This is the only method defined in a cmdset, called during
        its creation. It should populate the set with command instances.

        As and example we just add the empty base `Command` object.
        It prints some info.
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #
