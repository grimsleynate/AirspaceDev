"""
Scripts

Scripts are powerful jacks-of-all-trades. They have no in-game
existence and can be used to represent persistent game systems in some
circumstances. Scripts can also have a time component that allows them
to "fire" regularly or a limited number of times.

There is generally no "tree" of Scripts inheriting from each other.
Rather, each script tends to inherit from the base Script class and
just overloads its hooks to have it perform its function.

"""

from evennia.scripts.scripts import DefaultScript


class Script(DefaultScript):
    """
    This is the base TypeClass for all Scripts. Scripts describe
    all entities/systems without a physical existence in the game world
    that require database storage (like an economic system or
    combat tracker). They
    can also have a timer/ticker component.

    A script type is customized by redefining some or all of its hook
    methods and variables.

    * available properties (check docs for full listing, this could be
      outdated).

     key (string) - name of object
     name (string)- same as key
     aliases (list of strings) - aliases to the object. Will be saved
              to database as AliasDB entries but returned as strings.
     dbref (int, read-only) - unique #id-number. Also "id" can be used.
     date_created (string) - time stamp of object creation
     permissions (list of strings) - list of permission strings

     desc (string)      - optional description of script, shown in listings
     obj (Object)       - optional object that this script is connected to
                          and acts on (set automatically by obj.scripts.add())
     interval (int)     - how often script should run, in seconds. <0 turns
                          off ticker
     start_delay (bool) - if the script should start repeating right away or
                          wait self.interval seconds
     repeats (int)      - how many times the script should repeat before
                          stopping. 0 means infinite repeats
     persistent (bool)  - if script should survive a server shutdown or not
     is_active (bool)   - if script is currently running

    * Handlers

     locks - lock-handler: use locks.add() to add new lock strings
     db - attribute-handler: store/retrieve database attributes on this
                        self.db.myattr=val, val=self.db.myattr
     ndb - non-persistent attribute handler: same as db but does not
                        create a database entry when storing data

    * Helper methods

     create(key, **kwargs)
     start() - start script (this usually happens automatically at creation
               and obj.script.add() etc)
     stop()  - stop script, and delete it
     pause() - put the script on hold, until unpause() is called. If script
               is persistent, the pause state will survive a shutdown.
     unpause() - restart a previously paused script. The script will continue
                 from the paused timer (but at_start() will be called).
     time_until_next_repeat() - if a timed script (interval>0), returns time
                 until next tick

    * Hook methods (should also include self as the first argument):

     at_script_creation() - called only once, when an object of this
                            class is first created.
     is_valid() - is called to check if the script is valid to be running
                  at the current time. If is_valid() returns False, the running
                  script is stopped and removed from the game. You can use this
                  to check state changes (i.e. an script tracking some combat
                  stats at regular intervals is only valid to run while there is
                  actual combat going on).
      at_start() - Called every time the script is started, which for persistent
                  scripts is at least once every server start. Note that this is
                  unaffected by self.delay_start, which only delays the first
                  call to at_repeat().
      at_repeat() - Called every self.interval seconds. It will be called
                  immediately upon launch unless self.delay_start is True, which
                  will delay the first call of this method by self.interval
                  seconds. If self.interval==0, this method will never
                  be called.
      at_pause()
      at_stop() - Called as the script object is stopped and is about to be
                  removed from the game, e.g. because is_valid() returned False.
      at_script_delete()
      at_server_reload() - Called when server reloads. Can be used to
                  save temporary variables you want should survive a reload.
      at_server_shutdown() - called at a full server shutdown.
      at_server_start()

    """

    pass


class OxygenSystem(Script):
    """Tick environmental survival only for actively connected characters."""

    def at_script_creation(self):
        self.key = "quasar_environment"
        self.desc = "Updates oxygen and asphyxiation for connected characters."
        self.interval = 5
        self.repeats = 0
        self.persistent = True
        self.start_delay = True

    @staticmethod
    def _connected_characters():
        from evennia import SESSION_HANDLER

        return {
            session.puppet
            for session in SESSION_HANDLER.get_sessions()
            if getattr(session, "puppet", None)
        }

    def at_start(self, **kwargs):
        """Reconcile live characters after a server reload or cold start."""

        from world.resources import initialize_character, send_character_resources

        for character in self._connected_characters():
            if hasattr(character, "apply_damage"):
                initialize_character(character, include_starter_gear=True)
                send_character_resources(character, force=True)

    def at_repeat(self):
        from world.resources import tick_character_environment

        characters = self._connected_characters()
        for character in characters:
            if hasattr(character, "apply_damage"):
                tick_character_environment(character, elapsed=self.interval or 5)


class CombatSystem(Script):
    """Advance telegraphed NPC actions and character resource regeneration."""

    def at_script_creation(self):
        self.key = "quasar_combat"
        self.desc = "Updates active combatants and regenerates career resources."
        self.interval = 1
        self.repeats = 0
        self.persistent = True
        self.start_delay = True

    def at_start(self, **kwargs):
        from world.combat import tick_combat

        tick_combat()

    def at_repeat(self):
        from world.combat import tick_combat

        tick_combat()


class VerminSystem(Script):
    """Maintain capped ambient-hostile populations in registered cities."""

    def at_script_creation(self):
        self.key = "quasar_vermin"
        self.desc = "Reconciles weak city vermin and expires old carcasses."
        self.interval = 20
        self.repeats = 0
        self.persistent = True
        self.start_delay = True

    def at_start(self, **kwargs):
        from world.vermin import maintain_vermin_population

        maintain_vermin_population()

    def at_repeat(self):
        from world.vermin import maintain_vermin_population

        maintain_vermin_population()
