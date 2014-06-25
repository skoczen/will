# Welcome to Will's settings.  You can change the settings here, or re-run
# setup_will_project on the command line to do it interactively.
# ------------------------------------------------------------------------------------
# Required
# ------------------------------------------------------------------------------------
# The following four settings must be set for will to work.

# This is the list of rooms will should join.
# Default if unset is all rooms.

# ROOMS = ['Testing, Will Kahuna',]


# This is the room will will talk to if the trigger 
# is a webhook and he isn't told a specific room. 
# Default if unset is the first of ROOMS.

# DEFAULT_ROOM = 'Testing, Will Kahuna'


# If will isn't accessible at localhost, you must set this for his keepalive to work.
# PUBLIC_URL = "http://my-will.herokuapp.com"  # Note no trailing slash.



# This is the list of plugins will should load. This list can contain:
# 
# Built-in core plugins:
# ----------------------
# All built-in modules:     will.plugins
# Built-in modules:         will.plugins.module_name
# Specific plugins:         will.plugins.module_name.plugin
#
# Plugins in your will:
# ----------------------
# All modules:              plugins
# A specific module:        plugins.module_name
# Specific plugins:         plugins.module_name.plugin
# 
# Two folders are automatically added to your PYTHONPATH
# 1. Will's folder
# 2. Your will's folder.

# This is a list of python modules from which will will *recursively*
# include all plugins contained inside it.
PLUGINS = [
    # Includes all the core will plugin modules by default.
    # Comment out or remove to disable modules.
    "will.plugins.admin",
    "will.plugins.chat_room",
    "will.plugins.devops",
    "will.plugins.friendly",
    "will.plugins.help",
    "will.plugins.productivity",
    "will.plugins.web",

    # Includes all plugins in the project's plugins module by default.
    "plugins",
]

# All plugins are enabled by default, unless in this list
PLUGIN_BLACKLIST = [
    # But who would deprive will of cookies??
    # "will.plugins.friendly.cookies",
    "will.plugins.productivity.world_time",  # Requires a WORLD_WEATHER_ONLINE key
]


# Additional directories to look for templates, beyond the ones auto-included:
# 1. will/templates
# 2. my_will/templates
TEMPLATE_DIRS = [

]

WILL_HANDLE="joe"

# ------------------------------------------------------------------------------------
# Optional
# ------------------------------------------------------------------------------------

# User handles who are allowed to perform "admin" actions.  Defaults to everyone.
# ADMINS = [
#     "steven",
#     "levi",
# ]

# Port to listen to (defaults to $PORT, then 80.) Set > 1024 to run without elevated permission.
# HTTPSERVER_PORT = "80"  


# Email address to send from, if your will sends emails.
# DEFAULT_FROM_EMAIL = "will@example.com"