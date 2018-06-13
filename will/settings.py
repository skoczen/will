import os
import sys
from will.utils import show_valid, warn, note, error
from clint.textui import puts, indent
from six.moves.urllib import parse
from six.moves import input


def auto_key():
    """This method attempts to auto-generate a unique cryptographic key based on the hardware ID.
    It should *NOT* be used in production, or to replace a proper key, but it can help get will
    running in local and test environments more easily."""
    import uuid
    import time
    import random
    import hashlib

    node = uuid.getnode()

    h = hashlib.md5()
    h.update(str("%s" % node).encode('utf-8'))
    key1 = h.hexdigest()

    time.sleep(random.uniform(0, 0.5))
    node = uuid.getnode()

    h = hashlib.md5()
    h.update(str("%s" % node).encode('utf-8'))
    key2 = h.hexdigest()

    time.sleep(random.uniform(0, 0.5))
    node = uuid.getnode()

    h = hashlib.md5()
    h.update(str("%s" % node).encode('utf-8'))
    key3 = h.hexdigest()

    if key1 == key2 and key2 == key3:
        return key1

    return False


def import_settings(quiet=True):
    """This method takes care of importing settings from the environment, and config.py file.

    Order of operations:
    1. Imports all WILL_ settings from the environment, and strips off the WILL_
    2. Imports settings from config.py
    3. Sets defaults for any missing, required settings.

    This method takes a quiet kwarg, that when False, prints helpful output. Called that way during bootstrapping.
    """

    settings = {}

    # Import from environment, handle environment-specific parsing.
    for k, v in os.environ.items():
        if k[:5] == "WILL_":
            k = k[5:]
            settings[k] = v
    if "HIPCHAT_ROOMS" in settings and type(settings["HIPCHAT_ROOMS"]) is type("tes"):
        settings["HIPCHAT_ROOMS"] = settings["HIPCHAT_ROOMS"].split(";")

    if "ROOMS" in settings:
        settings["ROOMS"] = settings["ROOMS"].split(";")

    if "PLUGINS" in settings:
        settings["PLUGINS"] = settings["PLUGINS"].split(";")

    if 'PLUGIN_BLACKLIST' in settings:
        settings["PLUGIN_BLACKLIST"] = (settings["PLUGIN_BLACKLIST"].split(";")
                                        if settings["PLUGIN_BLACKLIST"] else [])

    # If HIPCHAT_SERVER is set, we need to change the USERNAME slightly
    # for XMPP to work.
    if "HIPCHAT_SERVER" in settings:
        settings["USERNAME"] = "{user}@{host}".\
            format(user=settings["USERNAME"].split("@")[0],
                   host=settings["HIPCHAT_SERVER"])
    else:
        settings["HIPCHAT_SERVER"] = "api.hipchat.com"

    # Import from config
    if not quiet:
        puts("Importing config.py... ")
    with indent(2):
        try:
            had_warning = False
            try:
                import config
            except ImportError:
                # Missing config.py.  Check for config.py.dist
                if os.path.isfile("config.py.dist"):
                    confirm = input(
                        "Hi, looks like you're just starting up!\nI didn't find a config.py, but I do see config.py.dist here. Want me to use that? (y/n) "
                    ).lower()
                    if confirm in ["y", "yes"]:
                        print("Great! One moment.\n\n")
                        os.rename("config.py.dist", "config.py")
                        import config
                    else:
                        print("Ok.  I can't start without one though. Quitting now!")
                        sys.exit(1)
                else:
                    error("I'm missing my config.py file. Usually one comes with the installation - maybe it got lost?")
                    sys.exit(1)

            for k, v in config.__dict__.items():
                # Ignore private variables
                if "__" not in k:
                    if k in os.environ and v != os.environ[k] and not quiet:
                        warn("%s is set in the environment as '%s', but overridden in"
                             " config.py as '%s'." % (k, os.environ[k], v))
                        had_warning = True
                    settings[k] = v

            if not had_warning and not quiet:
                show_valid("Valid.")
        except:
            # TODO: Check to see if there's a config.py.dist
            if not quiet:
                warn("no config.py found.  This might be ok, but more likely, "
                     "you haven't copied config.py.dist over to config.py")

    if not quiet:
        puts("Verifying settings... ")

    with indent(2):
        # Deprecation and backwards-compatibility for Will 1.x-> 2.x
        DEPRECATED_BUT_MAPPED_SETTINGS = {
            "USERNAME": "HIPCHAT_USERNAME",
            "PASSWORD": "HIPCHAT_PASSWORD",
            "V1_TOKEN": "HIPCHAT_V1_TOKEN",
            "V2_TOKEN": "HIPCHAT_V2_TOKEN",
            "TOKEN": "HIPCHAT_V1_TOKEN",
            "ROOMS": "HIPCHAT_ROOMS",
            "NAME": "HIPCHAT_NAME",
            "HANDLE": "HIPCHAT_HANDLE",
            "DEFAULT_ROOM": "HIPCHAT_DEFAULT_ROOM",
            "SLACK_DEFAULT_ROOM": "SLACK_DEFAULT_CHANNEL",
        }
        deprecation_warn_shown = False
        for k, v in DEPRECATED_BUT_MAPPED_SETTINGS.items():
            if not v in settings and k in settings:
                if not deprecation_warn_shown and not quiet:
                    error("Deprecated settings. The following settings will stop working in Will 2.2:")
                    deprecation_warn_shown = True
                if not quiet:
                    warn("Please update %s to %s.  " % (k, v))
                settings[v] = settings[k]
                del settings[k]

        # Migrate from 1.x
        if "CHAT_BACKENDS" in settings and "IO_BACKENDS" not in settings:
            IO_BACKENDS = []
            for c in settings["CHAT_BACKENDS"]:
                IO_BACKENDS.append("will.backends.io_adapters.%s" % c)
            settings["IO_BACKENDS"] = IO_BACKENDS
            if not quiet:
                warn(
                    "Deprecated settings.  Please update your config.py from:"
                    "\n   CHAT_BACKENDS = %s\n   to\n   IO_BACKENDS = %s" %
                    (settings["CHAT_BACKENDS"], IO_BACKENDS)
                )
        if "CHAT_BACKENDS" not in settings and "IO_BACKENDS" not in settings:
            if not quiet:
                warn("""Deprecated settings.  No backend found, so we're defaulting to hipchat and shell only.
Please add this to your config.py:
IO_BACKENDS = "
    "will.backends.io_adapters.hipchat",
    "will.backends.io_adapters.shell",
#   "will.backends.io_adapters.slack",
#   "will.backends.io_adapters.rocketchat",
]
""")
            settings["IO_BACKENDS"] = [
                "will.backends.io_adapters.hipchat",
                "will.backends.io_adapters.shell",
            ]

        if "ANALYZE_BACKENDS" not in settings:
            if not quiet:
                note("No ANALYZE_BACKENDS specified.  Defaulting to history only.")
            settings["ANALYZE_BACKENDS"] = [
                "will.backends.analysis.nothing",
                "will.backends.analysis.history",
            ]

        if "GENERATION_BACKENDS" not in settings:
            if not quiet:
                note("No GENERATION_BACKENDS specified.  Defaulting to fuzzy_all_matches and strict_regex.")
            settings["GENERATION_BACKENDS"] = [
                "will.backends.generation.fuzzy_all_matches",
                "will.backends.generation.strict_regex",
            ]

        if "EXECUTION_BACKENDS" not in settings:
            if not quiet:
                note("No EXECUTION_BACKENDS specified.  Defaulting to best_score.")
            settings["EXECUTION_BACKENDS"] = [
                "will.backends.execution.best_score",
            ]

        # Set for hipchat
        for b in settings["IO_BACKENDS"]:
            if "hipchat" in b:
                if "ALLOW_INSECURE_HIPCHAT_SERVER" in settings and\
                        (settings["ALLOW_INSECURE_HIPCHAT_SERVER"] is True or
                         settings["ALLOW_INSECURE_HIPCHAT_SERVER"].lower() == "true"):
                    warn("You are choosing to run will with SSL disabled. "
                         "This is INSECURE and should NEVER be deployed outside a development environment.")
                    settings["ALLOW_INSECURE_HIPCHAT_SERVER"] = True
                    settings["REQUESTS_OPTIONS"] = {
                        "verify": False,
                    }
                else:
                    settings["ALLOW_INSECURE_HIPCHAT_SERVER"] = False

                if "HIPCHAT_ROOMS" not in settings:
                    if not quiet:
                        warn("no HIPCHAT_ROOMS list found in the environment or config.  "
                             "This is ok - Will will just join all available HIPCHAT_rooms.")
                        settings["HIPCHAT_ROOMS"] = None

                if (
                    "HIPCHAT_DEFAULT_ROOM" not in settings and "HIPCHAT_ROOMS" in settings and
                    settings["HIPCHAT_ROOMS"] and len(settings["HIPCHAT_ROOMS"]) > 0
                ):
                    if not quiet:
                        warn("no HIPCHAT_DEFAULT_ROOM found in the environment or config.  "
                             "Defaulting to '%s', the first one." % settings["HIPCHAT_ROOMS"][0])
                    settings["HIPCHAT_DEFAULT_ROOM"] = settings["HIPCHAT_ROOMS"][0]

            if "HIPCHAT_HANDLE" in settings and "HIPCHAT_HANDLE_NOTED" not in settings:
                if not quiet:
                    note(
                        "HIPCHAT_HANDLE is no longer required (or used), as Will knows how to get\n" +
                        "        his current handle from the HipChat servers."
                    )
                    settings["HIPCHAT_HANDLE_NOTED"] = True

            if "HIPCHAT_NAME" in settings and "HIPCHAT_NAME_NOTED" not in settings:
                if not quiet:
                    note(
                        "HIPCHAT_NAME is no longer required (or used), as Will knows how to get\n" +
                        "        his current name from the HipChat servers."
                    )
                    settings["HIPCHAT_NAME_NOTED"] = True

        # Rocket.chat
        for b in settings["IO_BACKENDS"]:
            if "rocketchat" in b:
                if "ROCKETCHAT_USERNAME" in settings and "ROCKETCHAT_EMAIL" not in settings:
                    settings["ROCKETCHAT_EMAIL"] = settings["ROCKETCHAT_USERNAME"]
                if "ROCKETCHAT_URL" in settings:
                    if settings["ROCKETCHAT_URL"].endswith("/"):
                        settings["ROCKETCHAT_URL"] = settings["ROCKETCHAT_URL"][:-1]

        if (
            "DEFAULT_BACKEND" not in settings and "IO_BACKENDS" in settings and
            settings["IO_BACKENDS"] and len(settings["IO_BACKENDS"]) > 0
        ):
            if not quiet:
                note("no DEFAULT_BACKEND found in the environment or config.\n  "
                     "      Defaulting to '%s', the first one." % settings["IO_BACKENDS"][0])
            settings["DEFAULT_BACKEND"] = settings["IO_BACKENDS"][0]

        for b in settings["IO_BACKENDS"]:
            if "slack" in b and "SLACK_DEFAULT_CHANNEL" not in settings and not quiet:
                warn(
                    "No SLACK_DEFAULT_CHANNEL set - any messages sent without an explicit channel will go "
                    "to a non-deterministic channel that will has access to "
                    "- this is almost certainly not what you want."
                )

        if "HTTPSERVER_PORT" not in settings:
            # For heroku
            if "PORT" in os.environ:
                settings["HTTPSERVER_PORT"] = os.environ["PORT"]
            else:
                if not quiet:
                    warn("no HTTPSERVER_PORT found in the environment or config.  Defaulting to ':80'.")
                settings["HTTPSERVER_PORT"] = "80"

        if "STORAGE_BACKEND" not in settings:
            if not quiet:
                warn("No STORAGE_BACKEND specified.  Defaulting to redis.")
            settings["STORAGE_BACKEND"] = "redis"

        if "PUBSUB_BACKEND" not in settings:
            if not quiet:
                warn("No PUBSUB_BACKEND specified.  Defaulting to redis.")
            settings["PUBSUB_BACKEND"] = "redis"

        if settings["STORAGE_BACKEND"] == "redis" or settings["PUBSUB_BACKEND"] == "redis":
            if "REDIS_URL" not in settings:
                # For heroku
                if "REDIS_URL" in os.environ:
                    settings["REDIS_URL"] = os.environ["REDIS_URL"]
                    if not quiet:
                        note("WILL_REDIS_URL not set, but it appears you're using Heroku Redis or another standard REDIS_URL. If so, all good.")
                if "REDISCLOUD_URL" in os.environ:
                    settings["REDIS_URL"] = os.environ["REDISCLOUD_URL"]
                    if not quiet:
                        note("WILL_REDIS_URL not set, but it appears you're using RedisCloud. If so, all good.")
                elif "REDISTOGO_URL" in os.environ:
                    settings["REDIS_URL"] = os.environ["REDISTOGO_URL"]
                    if not quiet:
                        note("WILL_REDIS_URL not set, but it appears you're using RedisToGo. If so, all good.")
                elif "OPENREDIS_URL" in os.environ:
                    settings["REDIS_URL"] = os.environ["OPENREDIS_URL"]
                    if not quiet:
                        note("WILL_REDIS_URL not set, but it appears you're using OpenRedis. If so, all good.")
                else:
                    settings["REDIS_URL"] = "redis://localhost:6379/7"
                    if not quiet:
                        note("WILL_REDIS_URL not set.  Defaulting to redis://localhost:6379/7.")

            if not settings["REDIS_URL"].startswith("redis://"):
                settings["REDIS_URL"] = "redis://%s" % settings["REDIS_URL"]

            if "REDIS_MAX_CONNECTIONS" not in settings or not settings["REDIS_MAX_CONNECTIONS"]:
                settings["REDIS_MAX_CONNECTIONS"] = 4
                if not quiet:
                    note("REDIS_MAX_CONNECTIONS not set. Defaulting to 4.")

        if settings["STORAGE_BACKEND"] == "file":
            if "FILE_DIR" not in settings:
                settings["FILE_DIR"] = "~/.will/"
                if not quiet:
                    note("FILE_DIR not set.  Defaulting to ~/.will/")

        if settings["STORAGE_BACKEND"] == "couchbase":
            if "COUCHBASE_URL" not in settings:
                settings["COUCHBASE_URL"] = "couchbase:///will"
                if not quiet:
                    note("COUCHBASE_URL not set.  Defaulting to couchbase:///will")

        if "PUBLIC_URL" not in settings:
            default_public = "http://localhost:%s" % settings["HTTPSERVER_PORT"]
            settings["PUBLIC_URL"] = default_public
            if not quiet:
                note("no PUBLIC_URL found in the environment or config.\n        Defaulting to '%s'." % default_public)

        if not "REQUESTS_OPTIONS" in settings:
            settings["REQUESTS_OPTIONS"] = {}

        if "TEMPLATE_DIRS" not in settings:
            if "WILL_TEMPLATE_DIRS_PICKLED" in os.environ:
                # All good
                pass
            else:
                settings["TEMPLATE_DIRS"] = []

        if "WILL_HANDLE" not in settings:
            if "HANDLE" in settings:
                settings["WILL_HANDLE"] = settings["HANDLE"]
            elif "SLACK_HANDLE" in settings:
                settings["WILL_HANDLE"] = settings["SLACK_HANDLE"]
            elif "HIPCHAT_HANDLE" in settings:
                settings["WILL_HANDLE"] = settings["HIPCHAT_HANDLE"]
            elif "ROCKETCHAT_HANDLE" in settings:
                settings["WILL_HANDLE"] = settings["ROCKETCHAT_HANDLE"]
            else:
                settings["WILL_HANDLE"] = "will"

        if "ADMINS" not in settings:
            settings["ADMINS"] = "*"
        else:
            if "WILL_ADMINS" in os.environ:
                settings["ADMINS"] = [a.strip().lower() for a in settings.get('ADMINS', '').split(';') if a.strip()]

        if "ADMINS" in settings and settings["ADMINS"] != "*":
            warn("ADMINS is now deprecated, and will be removed at the end of 2017.  Please use ACL instead. See below for details")
            note("Change your config.py to:\n  ACL = {\n     'admins': %s\n  }" % settings["ADMINS"])

        if "DISABLE_ACL" not in settings:
            settings["DISABLE_ACL"] = False

        if "PROXY_URL" in settings:
            parsed_proxy_url = parse.urlparse(settings["PROXY_URL"])
            settings["USE_PROXY"] = True
            settings["PROXY_HOSTNAME"] = parsed_proxy_url.hostname
            settings["PROXY_USERNAME"] = parsed_proxy_url.username
            settings["PROXY_PASSWORD"] = parsed_proxy_url.password
            settings["PROXY_PORT"] = parsed_proxy_url.port
        else:
            settings["USE_PROXY"] = False

        if "EVENT_LOOP_INTERVAL" not in settings:
            settings["EVENT_LOOP_INTERVAL"] = 0.025

        if "LOGLEVEL" not in settings:
            settings["LOGLEVEL"] = "ERROR"

        if "ENABLE_INTERNAL_ENCRYPTION" not in settings:
            settings["ENABLE_INTERNAL_ENCRYPTION"] = True

        if "SECRET_KEY" not in settings:
            if not quiet:
                if "ENABLE_INTERNAL_ENCRYPTION" in settings and settings["ENABLE_INTERNAL_ENCRYPTION"]:
                    key = auto_key()
                    if key:
                        warn(
                            "No SECRET_KEY specified and ENABLE_INTERNAL_ENCRYPTION is on.\n" +
                            "  Temporarily auto-generating a key specific to this computer:\n    %s\n" % (key,) +
                            "  Please set WILL_SECRET_KEY in the environment as soon as possible to ensure \n" +
                            "  Will is able to access information from previous runs."
                        )
                    else:
                        error(
                            "ENABLE_INTERNAL_ENCRYPTION is turned on, but a SECRET_KEY has not been given.\n" +
                            "We tried to automatically generate temporary SECRET_KEY, but this appears to be a \n" +
                            "shared or virtualized environment.\n Please set a unique secret key in the " +
                            "environment as WILL_SECRET_KEY to run will."
                        )
                        print("  Unable to start will without a SECRET_KEY while encryption is turned on. Shutting down.")
                        sys.exit(1)

                    settings["SECRET_KEY"] = key
                    os.environ["WILL_SECRET_KEY"] = settings["SECRET_KEY"]
                    os.environ["WILL_EPHEMERAL_SECRET_KEY"] = "True"

        if "FUZZY_MINIMUM_MATCH_CONFIDENCE" not in settings:
            settings["FUZZY_MINIMUM_MATCH_CONFIDENCE"] = 91
        if "FUZZY_REGEX_ALLOWABLE_ERRORS" not in settings:
            settings["FUZZY_REGEX_ALLOWABLE_ERRORS"] = 3

        # Set them in the module namespace
        for k in sorted(settings, key=lambda x: x[0]):
            if not quiet:
                show_valid(k)
            globals()[k] = settings[k]


import_settings()
