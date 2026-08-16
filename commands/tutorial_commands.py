"""Commands used by the private distress-satellite tutorial."""

from commands.command import Command


class CmdAnswerChannel(Command):
    """Answer the blinking emergency channel in Reception."""

    key = "answer"
    aliases = ["respond", "answer channel", "respond to channel"]
    locks = "cmd:all()"
    help_category = "Tutorial"

    def func(self):
        from world.tutorial import answer_channel

        answer_channel(self.caller)


class CmdOpenCabinet(Command):
    """Open the surviving cabinet in Emergency Stores."""

    key = "open cabinet"
    aliases = ["open equipment cabinet", "enter code", "use code on keypad"]
    locks = "cmd:all()"
    help_category = "Tutorial"

    def func(self):
        from world.tutorial import open_stores_cabinet

        open_stores_cabinet(self.caller)


class CmdOpenCradle(Command):
    """Release the wrist device from its damaged charging cradle."""

    key = "open cradle"
    aliases = ["take wrist device", "release porter", "open charging cradle"]
    locks = "cmd:all()"
    help_category = "Tutorial"

    def func(self):
        from world.tutorial import recover_porter

        recover_porter(self.caller)


class CmdUseTutorial(Command):
    """Use an item or tutorial control on its obvious target."""

    key = "use"
    locks = "cmd:all()"
    help_category = "Interaction"

    def func(self):
        query = " ".join(self.args.lower().split())
        from world import tutorial

        if not query:
            self.caller.msg("Use what?")
        elif "code" in query or "keypad" in query:
            tutorial.open_stores_cabinet(self.caller)
        elif "bridge" in query:
            tutorial.install_bridge(self.caller)
        elif "wafer" in query:
            if self.caller.location and self.caller.location.db.tutorial_role == "navigation_control":
                tutorial.calibrate_wafer(self.caller)
            else:
                tutorial.install_wafer(self.caller)
        elif "canister" in query or "oxygen" in query:
            tutorial.use_spare_oxygen(self.caller)
        elif "patch" in query:
            target = "mara" if "mara" in query else "self"
            tutorial.use_med_patch(self.caller, target=target)
        elif "porter" in query or "wrist device" in query or "teleporter" in query:
            porter = tutorial.role_object(self.caller, "porter")
            if porter and porter.db.bound:
                tutorial.porter_conversation(self.caller, "status")
            else:
                tutorial.bind_porter(self.caller)
        elif "breaker" in query or "power" in query:
            tutorial.activate_power(self.caller)
        elif "airlock" in query or "controls" in query:
            self.caller.msg("The interlock cycles automatically when you choose a pressure-door exit.")
        elif "cutter" in query and self.caller.location and self.caller.location.db.tutorial_role == "systems_workshop":
            state = tutorial.progress(self.caller)
            if state.get("workshop_log_revealed"):
                self.caller.msg("The emergency log cache is already open.")
            else:
                tutorial.save_progress(self.caller, workshop_log_revealed=True)
                self.caller.msg(
                    "Your cutter peels the fused plate away. The cache repeats one damaged line: "
                    "BOARDERS IN CARGO... PRESSURE FALLING... COMMAND SEALING... BEACON MANUAL FROM RELAY."
                )
        else:
            self.caller.msg("You cannot find a useful way to apply that here.")


class CmdInstallTutorial(Command):
    """Install a carried bridge or routing wafer."""

    key = "install"
    locks = "cmd:all()"
    help_category = "Tutorial"

    def func(self):
        query = self.args.lower()
        from world import tutorial

        if "bridge" in query:
            tutorial.install_bridge(self.caller)
        elif "wafer" in query or "route" in query:
            tutorial.install_wafer(self.caller)
        else:
            self.caller.msg("Install the |wbridge|n or the |wwafer|n?")


class CmdActivatePower(Command):
    """Close Auxiliary Power's manual breaker."""

    key = "activate power"
    aliases = ["use breaker", "close breaker", "activate breaker"]
    locks = "cmd:all()"
    help_category = "Tutorial"

    def func(self):
        from world.tutorial import activate_power

        activate_power(self.caller)


class CmdTestTransit(Command):
    """Ask Porter to verify the restored companion envelope."""

    key = "test transit"
    aliases = ["test amplifier", "activate console", "ask porter to test the amplifier"]
    locks = "cmd:all()"
    help_category = "Tutorial"

    def func(self):
        from world.tutorial import test_transit

        test_transit(self.caller)


class CmdBindPorter(Command):
    """Permanently bind the recovered Porter device to your identity."""

    key = "bind porter"
    aliases = ["bind device", "bind personal porter"]
    locks = "cmd:all()"
    help_category = "Tutorial"

    def func(self):
        from world.tutorial import bind_porter

        bind_porter(self.caller)


class CmdTouchPorter(Command):
    """Touch a carried, bound Porter's sensor anywhere and leave the tutorial."""

    key = "touch porter"
    aliases = ["touch device", "touch personal porter"]
    locks = "cmd:all()"
    help_category = "Tutorial"

    def func(self):
        from world.tutorial import touch_porter

        touch_porter(self.caller)


class CmdAskPorter(Command):
    """Ask Porter about a topic while carrying the device."""

    key = "ask porter"
    aliases = ["ask porter about"]
    locks = "cmd:all()"
    help_category = "Interaction"

    def func(self):
        from world.tutorial import porter_conversation

        topic = self.args.strip()
        if topic.lower().startswith("about "):
            topic = topic[6:].strip()
        porter_conversation(self.caller, topic=topic)


class CmdPorterStatus(Command):
    """Ask the carried Porter device for its current route status."""

    key = "porter status"
    locks = "cmd:all()"
    help_category = "Tutorial"

    def func(self):
        from world.tutorial import porter_conversation

        porter_conversation(self.caller, topic="status")


class CmdRescueMara(Command):
    """Choose to bring Mara with you to seek treatment."""

    key = "rescue mara"
    aliases = ["save mara", "take mara"]
    locks = "cmd:all()"
    help_category = "Tutorial"

    def func(self):
        from world.tutorial import choose_mara_fate

        choose_mara_fate(self.caller, "rescue")


class CmdAbandonMara(Command):
    """Choose to leave Mara inside Command."""

    key = "abandon mara"
    aliases = ["leave mara"]
    locks = "cmd:all()"
    help_category = "Tutorial"

    def func(self):
        from world.tutorial import choose_mara_fate

        choose_mara_fate(self.caller, "abandon")


class CmdMercyMara(Command):
    """Grant Mara's request for a quick death before she turns."""

    key = "mercy mara"
    aliases = ["grant mercy"]
    locks = "cmd:all()"
    help_category = "Tutorial"

    def func(self):
        from world.tutorial import choose_mara_fate

        choose_mara_fate(self.caller, "mercy")


class CmdCutDoor(Command):
    key = "cut door"
    locks = "cmd:all()"
    auto_help = False

    def func(self):
        from typeclasses.items import CompactArcCutter
        from world.tutorial import cut_airlock_door

        cutter = next(
            (item for item in self.caller.contents if isinstance(item, CompactArcCutter)),
            None,
        )
        if not cutter:
            self.caller.msg("You are not carrying a cutter capable of breaching a pressure door.")
            return
        cut_airlock_door(self.caller, self.args.strip())
