#!/usr/bin/env python
import os
import stat

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
            f.write("""import datetime
from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template


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
    bot = WillBot(plugins_dirs=["plugins",], template_dirs=["templates",])
    bot.bootstrap()
    """)
    # And make it executable
    st = os.stat('run_will.py')
    os.chmod("run_will.py", st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

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
