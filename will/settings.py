import os
from utils import show_valid, warn, error

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


    # Import from config
    try:
        import config
        for k, v in config.__dict__.items():
            # Ignore private variables
            if "__" not in k:
                if k in os.environ:
                    if not quiet:
                        warn("%s is set in the environment as '%s', but overridden in config.py as '%s'." % (k, os.environ[k], v))
                settings[k] = v
    except:
        # TODO: Check to see if there's a config.py.dist
        if not quiet:
            warn("no config.py found.  This might be ok, but more likely, you haven't copied config.py.dist over to config.py")


    # Set defaults
    if "ROOMS" not in settings:
        warn("Warning: no rooms specified in the environment or config.  Will will still run his webserver, but won't join any chat rooms.")
        settings["ROOMS"] = []

    if not "DEFAULT_ROOM" in settings and len(settings["ROOMS"]) > 0:
        warn("Warning: no default room specified in the environment or config.  Defaulting to '%s', the first one." % settings["ROOMS"][0])
        settings["ROOMS"] = settings["ROOMS"][0]

    if not "HTTPSERVER_PORT" in settings:
        # For heroku
        if "PORT" in os.environ:
            settings["HTTPSERVER_PORT"] = os.environ["PORT"]
        else:
            warn("Warning: no http server port specified in the environment or config.  Defaulting to ':80'.")
            settings["HTTPSERVER_PORT"] = "80"

    if not "PUBLIC_URL" in settings:
        default_public = "http://localhost:%s" % settings["HTTPSERVER_PORT"]
        warn("Warning: no public url specified in the environment or config.  Defaulting to '%s'" % default_public)
        settings["PUBLIC_URL"] = default_public

    if not "ADMINS" in settings:
        settings["ADMINS"] = "*"
    else:
        settings["ADMINS"] = [a.strip().lower() for a in settings.get('ADMINS', '').split(';') if a.strip()]
    
    # Set them in the module namespace
    for k in sorted(settings, key=lambda x: x[0]):
        if not quiet:
            show_valid(k)
        globals()[k] = settings[k]

import_settings()
