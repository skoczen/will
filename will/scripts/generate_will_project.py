#!/usr/bin/env python
"""
Creates the following structure:
/plugins
    __init__.py
    hello.py
/templates
run_will.py
requirements.txt
Procfile
"""


import os
current_dir = os.getcwd()
plugins_dir = os.path.join(current_dir, "plugins")
templates_dir = os.path.join(current_dir, "templates")

# Set up the directories
if not os.path.exists(plugins_dir):
    os.makedirs(plugins_dir)

if not os.path.exists(templates_dir):
    os.makedirs(templates_dir)

# Create the plugins __init__.py
with open(os.path.join(plugins_dir, "__init__.py"), 'w+') as f:
    pass

# Create the hello plugin
hello_file_path = os.path.join(plugins_dir, "hello.py")
if not os.path.exists(hello_file_path):
    with open(hello_file_path, 'w+') as f:
        f.write("""import datetime
from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template


class HelloPlugin(WillPlugin):

    @respond_to("^hello")
    def helllo(self, message):
        self.reply(message, "hi!")
""")

# Create run_will.py
run_will_path = os.path.join(current_dir, "run_will.py")
if not os.path.exists(run_will_path):
    with open(run_will_path, 'w+') as f:
        f.write("""#!/usr/bin/env python
from will.main import WillBot

if __name__ == '__main__':
    bot = WillBot(plugins_dirs=["plugins",], template_dirs=["templates",]
    bot.bootstrap()
""")


# Create requirements.txt
requirements_path = os.path.join(current_dir, "requirements.txt")
if not os.path.exists(requirements_path):
    with open(requirements_path, 'w+') as f:
        f.write("will")

# Create Procfile
requirements_path = os.path.join(current_dir, "Procfile")
if not os.path.exists(requirements_path):
    with open(requirements_path, 'w+') as f:
        f.write("web: python run_will.py")