"""Isolated settings for running the automated test suite."""

from .settings import *  # noqa: F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Evennia 5.0.1's installed 0017/0018 Tag index migration pair cannot build a
# fresh SQLite database under Django 5.2. Sync the current Evennia models for
# tests instead; production still uses the normal migrations from settings.py.
MIGRATION_MODULES = {
    app_label: None
    for app_label in (
        "server",
        "typeclasses",
        "accounts",
        "objects",
        "comms",
        "help",
        "scripts",
        "web",
        "mapdata",
    )
}
