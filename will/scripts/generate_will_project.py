#!/usr/bin/env python
import argparse
import os
import stat
import sys
from six.moves import input

from clint.textui import puts
from will.utils import print_head

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.append(PROJECT_ROOT)
sys.path.append(os.getcwd())

parser = argparse.ArgumentParser()
parser.add_argument(
    '--config-dist-only',
    action='store_true',
    help='Only output a config.py.dist.'
)
args = parser.parse_args()
requirements_txt = "will\n"


class EmptyObj(object):
    pass


def cleaned(service_name):
    return service_name.lower().replace(".", ''),


def ask_user(question):
    response = "?"
    while response not in ["y", "n"]:
        response = input("%s [y/n] " % question)
        if response not in ["y", "n"]:
            print("Please enter 'y' or 'n'.")
    return response.startswith("y")


def enable_disable_service(service_name, source):
    global requirements_txt
    if ask_user("  Do you want to enable %s support?" % (service_name)):
        source = source.replace("# will.backends.io_adapters.%s" % cleaned(service_name), "will.backends.io_adapters.%s" % cleaned(service_name))
        req_path = os.path.join(os.path.join(PROJECT_ROOT, "..", "requirements"), "%s.txt" % cleaned(service_name))
        print(req_path)
        if os.path.exists(req_path):
            with open(req_path, 'r') as f:
                requirements_txt = "%s\n# %s\n%s" % (requirements_txt, service_name, f.read())
    else:
        source = source.replace("will.backends.io_adapters.%s" % cleaned(service_name), "# will.backends.io_adapters.%s" % cleaned(service_name))
    return source


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

    if args.config_dist_only:
        print("Generating config.py.dist...")

    else:
        print("\nGenerating will scaffold...")

    current_dir = os.getcwd()
    plugins_dir = os.path.join(current_dir, "plugins")
    templates_dir = os.path.join(current_dir, "templates")

    if not args.config_dist_only:
        print("  /plugins")
        # Set up the directories
        if not os.path.exists(plugins_dir):
            os.makedirs(plugins_dir)

        print("     __init__.py")
        # Create the plugins __init__.py
        with open(os.path.join(plugins_dir, "__init__.py"), 'w+') as f:
            pass

        print("     morning.py")
        # Create the morning plugin
        morning_file_path = os.path.join(plugins_dir, "morning.py")
        if not os.path.exists(morning_file_path):
            with open(morning_file_path, 'w+') as f:
                f.write("""from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings


class MorningPlugin(WillPlugin):

    @respond_to("^good morning")
    def good_morning(self, message):
        self.reply("oh, g'morning!")
""")

        print("  /templates")
        if not os.path.exists(templates_dir):
            os.makedirs(templates_dir)

        print("     blank.html")
        # Create the plugins __init__.py
        with open(os.path.join(templates_dir, "blank.html"), 'w+') as f:
            pass

        print("  .gitignore")
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
                if "shelf.db" not in f.read():
                    append_ignore = True
            if append_ignore:
                with open(gitignore_path, "a") as f:
                    f.write("\nshelf.db\n")

        # Create run_will.py
        print("  run_will.py")
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
        print("  config.py.dist")

    config_path = os.path.join(current_dir, "config.py.dist")
    if not os.path.exists(config_path) or ask_user("! config.py.dist exists.  Overwrite it?"):
        with open(os.path.join(PROJECT_ROOT, "config.py.dist"), "r") as source_f:
            source = source_f.read()
            # Ask on backends
            print("\nWill supports a few different service backends.  Let's set up the ones you want:\n")
            source = enable_disable_service("Slack", source)
            source = enable_disable_service("HipChat", source)
            source = enable_disable_service("Rocket.Chat", source)
            source = enable_disable_service("Shell", source)

            with open(config_path, "w+") as f:
                config = source
                f.write(config)

    if not args.config_dist_only:
        print("  requirements.txt")
        # Create requirements.txt
        requirements_path = os.path.join(current_dir, "requirements.txt")
        if not os.path.exists(requirements_path) or ask_user("! requirements.txt exists.  Overwrite it?"):
            with open(requirements_path, 'w+') as f:
                f.write(requirements_txt)

        print("  Procfile")
        # Create Procfile
        requirements_path = os.path.join(current_dir, "Procfile")
        if not os.path.exists(requirements_path):
            with open(requirements_path, 'w+') as f:
                f.write("web: python run_will.py")

        print("  README.md")
        # Create the readme
        readme_path = os.path.join(current_dir, "README.md")
        if not os.path.exists(readme_path):
            with open(readme_path, 'w+') as f:
                f.write("""
This is our bot, a [will](https://github.com/skoczen/will) bot.
    """)

        print("\nDone.")

        print("\n Your will is now ready to go. Run ./run_will.py to get started!")
    else:
        print("\nCreated a config.py.dist.  Open it up to see what's new!\n")


if __name__ == '__main__':
    main()
