#!/usr/bin/env python
import os
import stat
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.append(PROJECT_ROOT)
sys.path.append(os.getcwd())

from clint.textui import colored
from clint.textui import puts, indent, columns
from will.utils import show_valid, error, warn, note, print_head

class EmptyObj(object):
    pass

def main():
    """
    Creates the following structure:
    /plugins
        __init__.py
        hello.py
    /templates
        blank.html
    .gitignore
    run_will.py
    requirements.txt
    Procfile
    README.md
    """

    print_head()
    puts("Welcome to the will project generator.")
    puts("")

    print "\nGenerating will scaffold..."

    current_dir = os.getcwd()
    plugins_dir = os.path.join(current_dir, "plugins")
    templates_dir = os.path.join(current_dir, "templates")

    print "  /plugins"
    # Set up the directories
    if not os.path.exists(plugins_dir):
        os.makedirs(plugins_dir)
    
    print "     __init__.py"
    # Create the plugins __init__.py
    with open(os.path.join(plugins_dir, "__init__.py"), 'w+') as f:
        pass

    print "     hello.py"
    # Create the hello plugin
    hello_file_path = os.path.join(plugins_dir, "hello.py")
    if not os.path.exists(hello_file_path):
        with open(hello_file_path, 'w+') as f:
            f.write("""from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings


class HelloPlugin(WillPlugin):

    @respond_to("^hello")
    def hello(self, message):
        self.reply(message, "hi!")
    """)

    print "  /templates"
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    print "     blank.html"
    # Create the plugins __init__.py
    with open(os.path.join(templates_dir, "blank.html"), 'w+') as f:
        pass

    print "  .gitignore"
    # Create .gitignore, or at least add shelf.db
    gitignore_path = os.path.join(current_dir, ".gitignore")
    if not os.path.exists(gitignore_path):
        with open(gitignore_path, 'w+') as f:
            f.write("""*.py[cod]
pip-log.txt
shelf.db
    """)
    else:
        append_ignore = False
        with open(gitignore_path, "r+") as f:
            if not "shelf.db" in f.read():
                append_ignore = True
        if append_ignore:
            with open(gitignore_path, "a") as f:
                f.write("\nshelf.db\n")


    # Create run_will.py
    print "  run_will.py"
    run_will_path = os.path.join(current_dir, "run_will.py")
    if not os.path.exists(run_will_path):
        with open(run_will_path, 'w+') as f:
            f.write("""#!/usr/bin/env python
from will.main import WillBot

if __name__ == '__main__':
    bot = WillBot()
    bot.bootstrap()
    """)
    # And make it executable
    st = os.stat('run_will.py')
    os.chmod("run_will.py", st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    # Create config.py
    print "  config.py"
    config_path = os.path.join(current_dir, "config.py")
    if not os.path.exists(config_path):
        with open(config_path, 'w+') as f:
            f.write("""# Welcome to Will's settings.
# 

# Config and the environment:
# ---------------------------
# Will can use settings from the environment or this file, and sets reasonable defaults.
# 
# Best practices: set keys and the like in the environment, and anything you'd be ok 
# with other people knowing in this file.
# 
# To specify in the environment, just prefix with WILL_ 
# (i.e. WILL_DEFAULT_ROOM becomes DEFAULT_ROOM).  
# In case of conflict, you will see a warning message, and the value in this file will win.



# ------------------------------------------------------------------------------------
# Required settings
# ------------------------------------------------------------------------------------

# The list of plugin modules will should load. 
# Will recursively loads all plugins contained in each module.


# This list can contain:
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
# Plugins anywhere else on your PYTHONPATH:
# -----------------------------------------
# All modules:              someapp
# A specific module:        someapp.module_name
# Specific plugins:         someapp.module_name.plugin


# By default, the list below includes all the core will plugins and
# all your project's plugins.  

PLUGINS = [
    # Built-ins
    "will.plugins.admin",
    "will.plugins.chat_room",
    "will.plugins.devops",
    "will.plugins.friendly",
    "will.plugins.help",
    "will.plugins.productivity",
    "will.plugins.web",

    # All plugins in your project.
    "plugins",
]

# Don't load any of the plugins in this list.  Same options as above.
PLUGIN_BLACKLIST = [
    # "will.plugins.friendly.cookies",      # But who would deprive will of cookies??
    "will.plugins.productivity.hangout",    # Because it requires a HANGOUT_URL
    "will.plugins.productivity.world_time", # Because it requires a WORLD_WEATHER_ONLINE key
]


# ------------------------------------------------------------------------------------
# Potentially required settings
# ------------------------------------------------------------------------------------

# If will isn't accessible at localhost, you must set this for his keepalive to work.
# Note no trailing slash.
# PUBLIC_URL = "http://my-will.herokuapp.com"

# Port to bind the web server to (defaults to $PORT, then 80.)
# Set > 1024 to run without elevated permission.
# HTTPSERVER_PORT = "9000"


# ------------------------------------------------------------------------------------
# Optional settings
# ------------------------------------------------------------------------------------

# The list of rooms will should join.  Default is all rooms.
# ROOMS = ['Testing, Will Kahuna',]


# The room will will talk to if the trigger is a webhook and he isn't told a specific room. 
# Default is the first of ROOMS.
# DEFAULT_ROOM = 'Testing, Will Kahuna'


# Fully-qualified folders to look for templates in, beyond the two that 
# are always included: core will's templates folder, and your project's templates folder.
# 
# TEMPLATE_DIRS = [
#   os.path.abspath("other_folder/templates")
# ]


# User handles who are allowed to perform `admin_only` plugins.  Defaults to everyone.
# ADMINS = [
#     "steven",
#     "levi",
# ]


# Mailgun config, if you'd like will to send emails.
# DEFAULT_FROM_EMAIL="will@example.com"
# Set in your environment:
# export WILL_MAILGUN_API_KEY="key-12398912329381"
# export WILL_MAILGUN_API_URL="example.com"


# Logging level
# LOGLEVEL = "DEBUG"

    """)

    print "  requirements.txt"
    # Create requirements.txt
    requirements_path = os.path.join(current_dir, "requirements.txt")
    if not os.path.exists(requirements_path):
        with open(requirements_path, 'w+') as f:
            f.write("will")

    print "  Procfile"
    # Create Procfile
    requirements_path = os.path.join(current_dir, "Procfile")
    if not os.path.exists(requirements_path):
        with open(requirements_path, 'w+') as f:
            f.write("web: python run_will.py")

    print "  README.md"
    # Create the readme
    readme_path = os.path.join(current_dir, "README.md")
    if not os.path.exists(readme_path):
        with open(readme_path, 'w+') as f:
            f.write("""
This is our bot, a [https://github.com/greenkahuna/will](will) bot.
""")

    print "\nDone."


if __name__ == '__main__':
    main()