r"""
Evennia settings file.

The available options are found in the default settings file found
here:

https://www.evennia.com/docs/latest/Setup/Settings-Default.html

Remember:

Don't copy more from the default file than you actually intend to
change; this will make sure that you don't overload upstream updates
unnecessarily.

When changing a setting requiring a file system path (like
path/to/actual/file.py), use GAME_DIR and EVENNIA_DIR to reference
your game folder and the Evennia library folders respectively. Python
paths (path.to.module) should be given relative to the game's root
folder (typeclasses.foo) whereas paths within the Evennia library
needs to be given explicitly (evennia.foo).

If you want to share your game dir, including its settings, you can
put secret game- or server-specific settings in secret_settings.py.

"""

# Use the defaults from Evennia unless explicitly overridden
from evennia.settings_default import *

# Quasar's authored game help extends the small stock/developer catalog.
FILE_HELP_ENTRY_MODULES = ["world.help_entries", "world.help_character_options"]
# Exploration, combat, and progression achievements live with Quasar content.
ACHIEVEMENT_CONTRIB_MODULES = ["world.achievement_data"]
import json
import os

######################################################################
# Evennia base server config
######################################################################

# This is the name of your game. Make it catchy!
SERVERNAME = "Quasar"

# Keep mutable runtime state away from the OneDrive-synchronized source tree.
# A PostgreSQL override in secret_settings.py supersedes the SQLite fallback.
QUASAR_RUNTIME_DIR = os.path.join(
    os.environ.get("LOCALAPPDATA", GAME_DIR), "Quasar", "runtime"
)
LOG_DIR = os.path.join(QUASAR_RUNTIME_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
SERVER_LOG_FILE = os.path.join(LOG_DIR, "server.log")
PORTAL_LOG_FILE = os.path.join(LOG_DIR, "portal.log")
HTTP_LOG_FILE = os.path.join(LOG_DIR, "http_requests.log")
LOCKWARNING_LOG_FILE = os.path.join(LOG_DIR, "lockwarnings.log")
if DATABASES["default"]["ENGINE"] == "django.db.backends.sqlite3":
    DATABASES["default"]["NAME"] = os.path.join(
        QUASAR_RUNTIME_DIR, "evennia.db3"
    )

#Account and Character config
AUTO_CREATE_CHARACTER_WITH_ACCOUNT = False
AUTO_PUPPET_ON_LOGIN = False
MAX_NR_CHARACTERS = 5
MAX_NR_SIMULTANEOUS_PUPPETS = 1
MULTISESSION_MODE = 0

#Character creation config
CMDSET_UNLOGGEDIN = "evennia.contrib.base_systems.menu_login.UnloggedinCmdSet"
CONNECTION_SCREEN_MODULE = "server.conf.connection_screens"
CHARGEN_MENU = "world.chargen_menu"

#Search config
SEARCH_MULTIMATCH_REGEX = (
    r"(?P<number>[0-9]+)-(?P<name>[^-]*)(?P<args>.*)"
)

SEARCH_MULTIMATCH_TEMPLATE = (
    " {number}-{name}{aliases}{info}\n"
)

# Persistent per-character room exploration.
INSTALLED_APPS += ["world.mapdata.apps.MapDataConfig"]

# One efficient global ticker updates oxygen only for connected characters.
GLOBAL_SCRIPTS["quasar_environment"] = {
    "typeclass": "typeclasses.scripts.OxygenSystem",
    "interval": 5,
    "repeats": 0,
    "persistent": True,
    "desc": "Quasar oxygen and environmental survival ticker",
}

# One global combat heartbeat is cheaper and easier to tune than one timer per
# monster. Only tagged active hostiles are advanced on each one-second tick.
GLOBAL_SCRIPTS["quasar_combat"] = {
    "typeclass": "typeclasses.scripts.CombatSystem",
    "interval": 1,
    "repeats": 0,
    "persistent": True,
    "desc": "Quasar combat and career-resource ticker",
}

GLOBAL_SCRIPTS["quasar_vermin"] = {
    "typeclass": "typeclasses.scripts.VerminSystem",
    "interval": 20,
    "repeats": 0,
    "persistent": True,
    "desc": "City vermin population and carcass cleanup ticker",
}

######################################################################
# Settings given in secret_settings.py override those in this file.
######################################################################
try:
    from server.conf.secret_settings import *
except ImportError:
    print("secret_settings.py file not found or failed to import.")

# Machine-local database credentials are generated outside the repository.
DATABASE_RUNTIME_FILE = os.path.join(QUASAR_RUNTIME_DIR, "database.json")
if os.path.exists(DATABASE_RUNTIME_FILE):
    with open(DATABASE_RUNTIME_FILE, encoding="utf-8") as database_file:
        DATABASES = {"default": json.load(database_file)}
