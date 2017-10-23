import os
import sys
import uuid
from will.utils import show_valid, warn, note, error
from clint.textui import puts, indent
from six.moves.urllib import parse
from six.moves import input


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

        # Set defaults
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

        if (
            "DEFAULT_BACKEND" not in settings and "IO_BACKENDS" in settings and
            settings["IO_BACKENDS"] and len(settings["IO_BACKENDS"]) > 0
        ):
            if not quiet:
                warn("no DEFAULT_BACKEND found in the environment or config.  "
                     "Defaulting to '%s', the first one." % settings["IO_BACKENDS"][0])
            settings["DEFAULT_BACKEND"] = settings["IO_BACKENDS"][0]

        for b in settings["IO_BACKENDS"]:
            if "slack" in b and "SLACK_DEFAULT_CHANNEL" not in settings and not quiet:
                warn(
                    "No SLACK_DEFAULT_CHANNEL set - any messages sent without an explicit channel will go "
                    "to a non-deterministic channel that will has access to "
                    "- this is almost certainly not what you want."
                )

        if "ENABLE_INTERNAL_ENCRYPTION" not in settings:
            settings["ENABLE_INTERNAL_ENCRYPTION"] = True

        if "HTTPSERVER_PORT" not in settings:
            # For heroku
            if "PORT" in os.environ:
                settings["HTTPSERVER_PORT"] = os.environ["PORT"]
            else:
                if not quiet:
                    warn("no HTTPSERVER_PORT found in the environment or config.  Defaulting to ':80'.")
                settings["HTTPSERVER_PORT"] = "80"

        if "STORAGE_BACKEND" not in settings:
            settings["STORAGE_BACKEND"] = "redis"

        if "PUBSUB_BACKEND" not in settings:
            settings["PUBSUB_BACKEND"] = "redis"

        if settings["STORAGE_BACKEND"] == "redis" or settings["PUBSUB_BACKEND"] == "redis":
            if "REDIS_URL" not in settings:
                # For heroku
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
                warn("no PUBLIC_URL found in the environment or config.  Defaulting to '%s'." % default_public)

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
            settings["REQUESTS_OPTIONS"] = {}

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

        if "SECRET_KEY" not in settings:
            if not quiet:
                note(
                    "No SECRET_KEY specified.  Auto-generating one specific to this run of Will.\n" +
                    "  Know that Will won't be able to catch up on old messages\n" +
                    "  or work in a multicomponent install without one."
                )
                settings["SECRET_KEY"] = uuid.uuid4().hex
                os.environ["WILL_SECRET_KEY"] = settings["SECRET_KEY"]
                os.environ["WILL_EPHEMERAL_SECRET_KEY"] = "True"

        # Set them in the module namespace
        for k in sorted(settings, key=lambda x: x[0]):
            if not quiet:
                show_valid(k)
            globals()[k] = settings[k]


import_settings()
