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

from commands.player_commands import (
    CmdAttack,
    CmdCombatDemo,
    CmdConsider,
    CmdEquip,
    CmdEquipment,
    CmdGreet,
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
    CmdOxygen,
    CmdSoundTest,
    CmdSheet,
    CmdSkill,
    CmdSkills,
    CmdTalk,
    CmdUnequip,
    CmdVitals,
)
from commands.journal_commands import CmdQuestLog, CmdTaskLog
from commands.account_commands import CmdCharDelete, CmdIC
from commands.tutorial_commands import (
    CmdAbandonMara,
    CmdActivatePower,
    CmdAnswerChannel,
    CmdAskPorter,
    CmdBindPorter,
    CmdCutDoor,
    CmdInstallTutorial,
    CmdMercyMara,
    CmdOpenCabinet,
    CmdOpenCradle,
    CmdPorterStatus,
    CmdRescueMara,
    CmdTestTransit,
    CmdTouchPorter,
    CmdUseTutorial,
)


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
        self.add(CmdTalk)
        self.add(CmdSoundTest)
        self.add(CmdVitals)
        self.add(CmdOxygen)
        self.add(CmdEquipment)
        self.add(CmdEquip)
        self.add(CmdUnequip)
        self.add(CmdAttack)
        self.add(CmdSkills)
        self.add(CmdSkill)
        self.add(CmdSheet)
        self.add(CmdConsider)
        self.add(CmdCombatDemo)
        self.add(CmdNumpadNorthwest)
        self.add(CmdNumpadNorth)
        self.add(CmdNumpadNortheast)
        self.add(CmdNumpadWest)
        self.add(CmdNumpadLook)
        self.add(CmdNumpadEast)
        self.add(CmdNumpadSouthwest)
        self.add(CmdNumpadSouth)
        self.add(CmdNumpadSoutheast)
        self.add(CmdAnswerChannel)
        self.add(CmdOpenCabinet)
        self.add(CmdOpenCradle)
        self.add(CmdUseTutorial)
        self.add(CmdInstallTutorial)
        self.add(CmdActivatePower)
        self.add(CmdTestTransit)
        self.add(CmdBindPorter)
        self.add(CmdTouchPorter)
        self.add(CmdAskPorter)
        self.add(CmdPorterStatus)
        self.add(CmdRescueMara)
        self.add(CmdAbandonMara)
        self.add(CmdMercyMara)
        self.add(CmdCutDoor)
        self.add(CmdQuestLog)
        self.add(CmdTaskLog)
        self.add(GenericBuildingCmd())
        self.add(RPSystemCmdSet())


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
        # Override the contrib's name-only IC command with Quasar's numbered selector.
        self.add(CmdIC)
        self.add(CmdCharDelete)


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
