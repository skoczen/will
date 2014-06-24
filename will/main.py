# -*- coding: utf-8 -*-

import logging
import inspect
import imp
import os
import operator
import re
import sys
import time
from clint.textui import colored
from clint.textui import puts, indent, columns
from os.path import abspath, dirname
from multiprocessing import Process

from gevent import monkey
# Monkeypatch has to come before bottle
monkey.patch_all()
import bottle

from listener import WillXMPPClientMixin
from mixins import ScheduleMixin, StorageMixin, ErrorMixin, HipChatMixin,\
    RoomMixin, PluginModulesLibraryMixin, EmailMixin
from scheduler import Scheduler
import settings
from utils import show_valid, error, warn, note


# Force UTF8
if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')
else:
    raw_input = input


# Update path
PROJECT_ROOT = abspath(os.path.join(dirname(__file__)))
PLUGINS_ROOT = abspath(os.path.join(PROJECT_ROOT, "plugins"))
TEMPLATES_ROOT = abspath(os.path.join(PROJECT_ROOT, "templates"))
sys.path.append(PROJECT_ROOT)
sys.path.append(os.path.join(PROJECT_ROOT, "will"))


class WillBot(EmailMixin, WillXMPPClientMixin, StorageMixin, ScheduleMixin,\
    ErrorMixin, RoomMixin, HipChatMixin, PluginModulesLibraryMixin):

    def __init__(self, **kwargs):
        if "template_dirs" in kwargs:
            warn("template_dirs is now depreciated")
        if "plugin_dirs" in kwargs:
            warn("plugin_dirs is now depreciated")

        log_level = getattr(settings, 'LOGLEVEL', logging.ERROR)
        logging.basicConfig(level=log_level,\
            format='%(levelname)-8s %(message)s')

        
        # Find all the PLUGINS modules
        plugins = settings.PLUGINS
        self.plugins_dirs = {}

        # Convert those to dirs
        for plugin in plugins:
            path_name = None
            for mod in plugin.split('.'):
                if path_name is not None:
                    path_name=[path_name]
                file_name, path_name, description = imp.find_module(mod, path_name)

            # Add, uniquely.
            self.plugins_dirs[os.path.abspath(path_name)] = plugin

        # Key by module name
        self.plugins_dirs = dict(zip(self.plugins_dirs.values(),self.plugins_dirs.keys()))

        full_path_template_dirs = []
        for t in settings.TEMPLATE_DIRS:
            full_path_template_dirs.append(os.path.abspath(t))
        if not TEMPLATES_ROOT in full_path_template_dirs:
            full_path_template_dirs += [TEMPLATES_ROOT, ]

        # Storing here because storage hasn't been bootstrapped yet.
        os.environ["WILL_TEMPLATE_DIRS_PICKLED"] =\
            ";;".join(full_path_template_dirs)

    def bootstrap(self):
        self.print_head()
        self.verify_environment()
        self.load_config()
        self.bootstrap_storage()
        self.bootstrap_plugins()

        puts("\nStarting core processes:\n")
        # Scheduler
        scheduler_thread = Process(target=self.bootstrap_scheduler)
        # scheduler_thread.daemon = True

        # Bottle
        bottle_thread = Process(target=self.bootstrap_bottle)
        # bottle_thread.daemon = True

        # XMPP Listener
        xmpp_thread = Process(target=self.bootstrap_xmpp)
        # xmpp_thread.daemon = True

        try:
            # Start up threads.
            xmpp_thread.start()
            scheduler_thread.start()
            bottle_thread.start()
            errors = self.get_startup_errors()
            if len(errors) > 0:
                default_room = self.get_room_from_name_or_id(settings.DEFAULT_ROOM)["room_id"]
                error_message = "FYI, I had some errors starting up:"
                for err in errors:
                    error_message += "\n%s\n" % err
                self.send_room_message(default_room, error_message)
                puts(colored.red(error_message))

            while True:
                time.sleep(100)
        except (KeyboardInterrupt, SystemExit):
            scheduler_thread.terminate()
            bottle_thread.terminate()
            xmpp_thread.terminate()
            print '\n\nReceived keyboard interrupt, quitting threads.',
            while scheduler_thread.is_alive() or\
                  bottle_thread.is_alive() or\
                  xmpp_thread.is_alive():
                    sys.stdout.write(".")
                    sys.stdout.flush()
                    time.sleep(0.5)


    def print_head(self):
        puts("""
      ___/-\___
  ___|_________|___
     |         |
     |--O---O--|
     |         |
     |         |
     |  \___/  |
     |_________|      
      Will: Hi!
""")

    def verify_individual_setting(self, test_setting, quiet=False):
        if hasattr(settings, test_setting["name"][5:]):
            with indent(2):
                show_valid(test_setting["name"])
            return True
        else:
            error("%(name)s... missing!" % test_setting)
            with indent(2):
                puts("""To obtain a %(name)s: \n%(obtain_at)s

To set your %(name)s:
1. On your local machine, add this to your virtual environment's bin/postactivate file:
   export %(name)s=YOUR_ACTUAL_%(name)s
2. If you've deployed will on heroku, run
   heroku config:set %(name)s=YOUR_ACTUAL_%(name)s
""" % test_setting)
            return False


    def verify_environment(self):
        missing_settings = False
        required_settings = [
            {
                "name": "WILL_USERNAME",
                "obtain_at": "1. Go to hipchat, and create a new user for will.\n2. Log into will, and go to Account settings>XMPP/Jabber Info.\n3. On that page, the 'Jabber ID' is the value you want to use."
            },
            {
                "name": "WILL_PASSWORD",
                "obtain_at": "1. Go to hipchat, and create a new user for will.  Note that password - this is the value you want.  It's used for signing in via XMPP."
            },
            {
                "name": "WILL_V2_TOKEN",
                "obtain_at": "1. Log into hipchat using will's user. 2. Go to https://your-org.hipchat.com/account/api 3. Create a token. 4. Copy the value - this is the WILL_V2 token."
            }
        ]

        print "Verifying environment..."

        for r in required_settings:
            if not self.verify_individual_setting(r):
                missing_settings = True

        if missing_settings:
            error("Will was unable to start because some required environment variables are missing.  Please fix them and try again!")
            sys.exit(0)
        else:
            print ""

    def load_config(self):
        print "Loading configuration..."
        with indent(2):
            settings.import_settings(quiet=False)
        print ""

    def bootstrap_scheduler(self):
        bootstrapped = False
        try:

            self.save("plugin_modules_library", self._plugin_modules_library)
            Scheduler.clear_locks(self)
            self.scheduler = Scheduler()

            for plugin_info, fn, function_name in self.periodic_tasks:
                self.add_periodic_task(plugin_info["full_module_name"], plugin_info["name"], function_name, fn.sched_args, fn.sched_kwargs, fn.function_name,)
            for plugin_info, fn, function_name in self.random_tasks:
                self.add_random_tasks(plugin_info["full_module_name"], plugin_info["name"], function_name, fn.start_hour, fn.end_hour, fn.day_of_week, fn.num_times_per_day)
            bootstrapped = True
        except Exception, e:
            self.startup_error("Error bootstrapping scheduler", e)
        if bootstrapped:
            show_valid("Scheduler started.")
            self.scheduler.start_loop(self)

    def bootstrap_bottle(self):
        bootstrapped = False
        try:
            for cls, function_name in self.bottle_routes:
                instantiated_cls = cls()
                instantiated_fn = getattr(instantiated_cls, function_name)
                bottle_route_args = {}
                for k, v in instantiated_fn.__dict__.items():
                    if "bottle_" in k and k != "bottle_route":
                        bottle_route_args[k[len("bottle_"):]] = v
                bottle.route(instantiated_fn.bottle_route, **bottle_route_args)(instantiated_fn)
            bootstrapped = True
        except Exception, e:
            self.startup_error("Error bootstrapping bottle", e)
        if bootstrapped:
            show_valid("Web server started.")
            bottle.run(host='0.0.0.0', port=settings.HTTPSERVER_PORT, server='gevent',)

    def bootstrap_xmpp(self):
        bootstrapped = False
        try:
            self.start_xmpp_client()
            sorted_help = {k: sorted(v) for k,v in self.help_modules.items()}
            self.save("help_modules", sorted_help)
            self.save("all_listener_regexes", self.all_listener_regexes)
            self.connect()
            bootstrapped = True
        except Exception, e:
            self.startup_error("Error bootstrapping xmpp", e)
        if bootstrapped:
            show_valid("Chat client started.")
            puts("")
            show_valid("Will is running.")
            self.process(block=True)

    def bootstrap_plugins(self):
        puts("Bootstrapping plugins...")
        OTHER_HELP_HEADING = "Other"
        plugin_modules = {}
        plugin_modules_library = {}

        # NOTE: You can't access self.storage here, or it will deadlock when the threads try to access redis.

        # Sure does feel like this should be a solved problem somehow.
        with indent(2):
            parent_help_text = None
            for plugin_name, plugin_root in self.plugins_dirs.items():
                for root, dirs, files in os.walk(plugin_root, topdown=False):
                    for f in files:
                        if f[-3:] == ".py" and f != "__init__.py":
                            try:
                                module_path = os.path.join(root, f)
                                path_components = os.path.split(module_path)
                                module_name = path_components[-1][:-3]
                                full_module_name = ".".join(path_components)
                                # Need to pass along module name, path all the way through

                                combined_name = ".".join([plugin_name, module_name])

                                # Check blacklist.
                                blacklisted = False
                                for b in settings.PLUGIN_BLACKLIST:
                                    if b in combined_name:
                                        blacklisted = True
                                        note("%s was found but ignored, since it is on PLUGIN_BLACKLIST." % combined_name)
                            
                                if not blacklisted:
                                    plugin_modules[full_module_name] = imp.load_source(module_name, module_path)
                                    parent_mod = path_components[-2].split("/")[-1]
                                    parent_help_text = parent_mod.title()
                                    try:
                                        parent_root = os.path.join(root, "__init__.py")
                                        parent = imp.load_source(parent_mod, parent_root)
                                        parent_help_text = getattr(parent, "MODULE_DESCRIPTION", parent_help_text)
                                    except:
                                        pass

                                    plugin_modules_library[full_module_name] = {
                                        "full_module_name": full_module_name,
                                        "file_path": module_path,
                                        "name": module_name,
                                        "parent_name": plugin_name,
                                        "parent_module_name": parent_mod,
                                        "parent_help_text": parent_help_text,
                                    }
                            except Exception, e:
                                self.startup_error("Error loading %s" % (module_path,), e)

                self.plugins = []
                for name, module in plugin_modules.items():
                    try:
                        for class_name, cls in inspect.getmembers(module, predicate=inspect.isclass):
                            try:
                                if hasattr(cls, "is_will_plugin") and cls.is_will_plugin and class_name != "WillPlugin":
                                    self.plugins.append({
                                        "name": class_name,
                                        "class": cls,
                                        "module": module,
                                        "full_module_name": name,
                                        "parent_name": plugin_modules_library[name]["parent_name"],
                                        "parent_module_name": plugin_modules_library[name]["parent_module_name"],
                                        "parent_help_text": plugin_modules_library[name]["parent_help_text"]
                                    })
                            except Exception, e:
                                self.startup_error("Error bootstrapping %s" % (class_name,), e)
                    except Exception, e:
                        self.startup_error("Error bootstrapping %s" % (name,), e)

            self._plugin_modules_library = plugin_modules_library

            # Sift and Sort.
            self.message_listeners = []
            self.periodic_tasks = []
            self.random_tasks = []
            self.bottle_routes = []
            self.all_listener_regexes = []
            self.help_modules = {}
            self.help_modules[OTHER_HELP_HEADING] = []
            self.some_listeners_include_me = False
            self.plugins.sort(key=operator.itemgetter("parent_name"))
            last_parent_name = None
            for plugin_info in self.plugins:
                try:
                    if last_parent_name != plugin_info["parent_help_text"]:
                        friendly_name = "%(parent_help_text)s " % plugin_info
                        module_name = " %(parent_name)s" % plugin_info
                        # Justify
                        friendly_name = friendly_name.ljust(50, '-')
                        module_name = module_name.rjust(40, '-')
                        puts("")
                        puts("%s%s" % (friendly_name, module_name))

                        last_parent_name = plugin_info["parent_help_text"]
                    with indent(2):
                        plugin_name = plugin_info["name"]
                        # Just a little nicety
                        if plugin_name[-6:] == "Plugin":
                            plugin_name = plugin_name[:-6]
                        show_valid(plugin_name)
                    for function_name, fn in inspect.getmembers(plugin_info["class"], predicate=inspect.ismethod):
                        try:
                            with indent(2):
                                if hasattr(fn, "listens_to_messages") and fn.listens_to_messages and hasattr(fn, "listener_regex"):
                                    # puts("- %s" % function_name)
                                    regex = fn.listener_regex
                                    if not fn.case_sensitive:
                                        regex = "(?i)%s" % regex
                                    help_regex = fn.listener_regex
                                    if fn.listens_only_to_direct_mentions:
                                        help_regex = "@%s %s" % (settings.HANDLE, help_regex)
                                    self.all_listener_regexes.append(help_regex)
                                    if fn.__doc__:
                                        pht = plugin_info.get("parent_help_text", None)
                                        if pht:
                                            if pht in self.help_modules:
                                                self.help_modules[pht].append(fn.__doc__)
                                            else:
                                                self.help_modules[pht] = [fn.__doc__,]
                                        else:
                                            self.help_modules[OTHER_HELP_HEADING].append(fn.__doc__)
                                    if fn.multiline:
                                        compiled_regex = re.compile(regex, re.MULTILINE | re.DOTALL)
                                    else:
                                        compiled_regex = re.compile(regex)
                                    self.message_listeners.append({
                                        "function_name": function_name,
                                        "class_name": plugin_info["name"],
                                        "regex_pattern": fn.listener_regex,
                                        "regex": compiled_regex,
                                        "fn": getattr(plugin_info["class"](), function_name),
                                        "args": fn.listener_args,
                                        "include_me": fn.listener_includes_me,
                                        "direct_mentions_only": fn.listens_only_to_direct_mentions,
                                        "admin_only": fn.listens_only_to_admin,
                                    })
                                    if fn.listener_includes_me:
                                        self.some_listeners_include_me = True
                                elif hasattr(fn, "periodic_task") and fn.periodic_task:
                                    # puts("- %s" % function_name)
                                    self.periodic_tasks.append((plugin_info, fn, function_name))
                                elif hasattr(fn, "random_task") and fn.random_task:
                                    # puts("- %s" % function_name)
                                    self.random_tasks.append((plugin_info, fn, function_name))
                                elif hasattr(fn, "bottle_route"):
                                    # puts("- %s" % function_name)
                                    self.bottle_routes.append((plugin_info["class"], function_name))

                        except Exception, e:
                            self.startup_error("Error bootstrapping %s.%s" % (plugin_info["class"], function_name,), e)
                except Exception, e:
                    self.startup_error("Error bootstrapping %s" % (plugin_info["class"],), e)
