import os
from utils import show_valid, warn, note
from clint.textui import puts, indent
from urlparse import urlparse


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
    if "ROOMS" in settings:
        settings["ROOMS"] = settings["ROOMS"].split(";")

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
            import config
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
        # Set defaults
        if "ROOMS" not in settings:
            if not quiet:
                warn("no ROOMS list found in the environment or config.  "
                     "This is ok - Will will just join all available rooms.")
                settings["ROOMS"] = None

        if "DEFAULT_ROOM" not in settings and "ROOMS" in settings and settings["ROOMS"] and len(settings["ROOMS"]) > 0:
            if not quiet:
                warn("no DEFAULT_ROOM found in the environment or config.  "
                     "Defaulting to '%s', the first one." % settings["ROOMS"][0])
            settings["DEFAULT_ROOM"] = settings["ROOMS"][0]

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

        if settings["STORAGE_BACKEND"] == "redis":
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

            if "REDIS_MAX_CONNECTIONS" not in settings:
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

        if "V1_TOKEN" not in settings:
            if not quiet:
                warn(
                    "no V1_TOKEN found in the environment or config."
                    "This is generally ok, but if you have more than 30 rooms, "
                    "you may recieve rate-limit errors without one."
                )

        if "TEMPLATE_DIRS" not in settings:
            if "WILL_TEMPLATE_DIRS_PICKLED" in os.environ:
                # All good
                pass
            else:
                settings["TEMPLATE_DIRS"] = []
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

        if "PROXY_URL" in settings:
            parsed_proxy_url = urlparse(settings["PROXY_URL"])
            settings["USE_PROXY"] = True
            settings["PROXY_HOSTNAME"] = parsed_proxy_url.hostname
            settings["PROXY_USERNAME"] = parsed_proxy_url.username
            settings["PROXY_PASSWORD"] = parsed_proxy_url.password
            settings["PROXY_PORT"] = parsed_proxy_url.port
        else:
            settings["USE_PROXY"] = False

        # Set them in the module namespace
        for k in sorted(settings, key=lambda x: x[0]):
            if not quiet:
                show_valid(k)
            globals()[k] = settings[k]


import_settings()
