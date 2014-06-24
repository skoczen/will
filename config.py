# Welcome to Will's settings.  You'll need to set a few settings below,
# with some optional ones further down.
# ------------------------------------------------------------------------------------
# Required
# ------------------------------------------------------------------------------------
# The following four settings must be set for will to work.

# This is the list of rooms will should join.
ROOMS = ['Testing, Will Kahuna',]
# Default: ALL_ROOMS

# This is the room will will talk to if the trigger 
# is a webhook and he isn't told a specific room. 
# Defaults to the first of ROOMS.
DEFAULT_ROOM = 'Testing, Will Kahuna'

# If will isn't accessible at localhost, you must set this for his keepalive to work.
PUBLIC_URL = "http://my-will.herokuapp.com"  # Note no trailing slash.


# This is the list of plugins will should load. This list can contain:
# 
# Built-in core plugins:
# ----------------------
# All built-in modules:     will.core.plugins
# Built-in modules:         will.core.plugins.module_name
# Specific plugins:         will.core.plugins.module_name.plugin
#
# Plugins in your will:
# ----------------------
# All modules:              my_will.plugins
# A specific module:        my_will.plugins.module_name
# Specific plugins:         my_will.plugins.module_name.plugin
# 
# Plugins are automatically imported from one of three areas:
# 1. The global python namespace
# 2. Will's plugins folder
# 3. Your will's plugins folder.

PLUGINS = [
    "core.admin",
    "core.devops",
    "core.friendly",
    "core.help",
    "core.hipchat",
    "core.productivity",
    "core.web",
    "my_will.plugins",
]
WILL_HANDLE="joe"

# All plugins are enabled by default, unless in this list
PLUGIN_BLACKLIST = [
    # But who would deprive will of cookies??
    # "core.friendly.cookies",
]



# ------------------------------------------------------------------------------------
# Optional
# ------------------------------------------------------------------------------------

# User handles who are allowed to perform "admin" actions.  Defaults to everyone.
# ADMIN_HANDLES = [
#     "steven",
#     "levi",
# ]

# Port to listen to (defaults to $PORT, then 80.) Set > 1024 to run without elevated permission.
# HTTPSERVER_PORT = "80"  


# Email address to send from, if your will sends emails.
# WILL_DEFAULT_FROM_EMAIL = "will@example.com"