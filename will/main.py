# -*- coding: utf-8 -*-

import logging
import inspect
import imp
import os
import operator
import re
import requests
import sys
import time
import threading
from clint.textui import colored
from clint.textui import puts, indent, columns
from os.path import abspath, dirname
from multiprocessing import Process, Queue

from gevent import monkey
# Monkeypatch has to come before bottle
monkey.patch_all()
import bottle

from listener import WillXMPPClientMixin
from mixins import ScheduleMixin, StorageMixin, ErrorMixin, HipChatMixin,\
    RoomMixin, PluginModulesLibraryMixin, EmailMixin
from scheduler import Scheduler
import settings
from utils import show_valid, error, warn, note, print_head


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
PROJECT_TEMPLATE_ROOT = abspath(os.path.join(os.getcwd(), "templates"))
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
        
        # Add will's templates_root
        if not TEMPLATES_ROOT in full_path_template_dirs:
            full_path_template_dirs += [TEMPLATES_ROOT, ]

        # Add this project's templates_root
        if not PROJECT_TEMPLATE_ROOT in full_path_template_dirs:
            full_path_template_dirs += [PROJECT_TEMPLATE_ROOT, ]

        # Storing here because storage hasn't been bootstrapped yet.
        os.environ["WILL_TEMPLATE_DIRS_PICKLED"] =\
            ";;".join(full_path_template_dirs)

    def bootstrap(self):
        print_head()
        self.verify_environment()
        self.load_config()
        self.bootstrap_storage_mixin()
        self.bootstrap_plugins()
        self.verify_plugin_settings()

        puts("Bootstrapping complete.")
        puts("\nStarting core processes:")
        # Scheduler
        scheduler_thread = Process(target=self.bootstrap_scheduler)
        # scheduler_thread.daemon = True

        # Bottle
        bottle_thread = Process(target=self.bootstrap_bottle)
        # bottle_thread.daemon = True

        # XMPP Listener
        xmpp_thread = Process(target=self.bootstrap_xmpp)
        # xmpp_thread.daemon = True

        with indent(2):
            try:
                # Start up threads.
                xmpp_thread.start()
                scheduler_thread.start()
                bottle_thread.start()
                errors = self.get_startup_errors()
                if len(errors) > 0:
                    default_room = self.get_room_from_name_or_id(settings.DEFAULT_ROOM)["room_id"]
                    error_message = "FYI, I ran into some problems while starting up:"
                    for err in errors:
                        error_message += "\n%s\n" % err
                    self.send_room_message(default_room, error_message, color="yellow")
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
                "obtain_at": """1. Go to hipchat, and create a new user for will.
2. Log into will, and go to Account settings>XMPP/Jabber Info.
3. On that page, the 'Jabber ID' is the value you want to use.""",
            },
            {
                "name": "WILL_PASSWORD",
                "obtain_at": "1. Go to hipchat, and create a new user for will.  Note that password - this is the value you want.  It's used for signing in via XMPP.",
            },
            {
                "name": "WILL_V2_TOKEN",
                "obtain_at": """1. Log into hipchat using will's user.
2. Go to https://your-org.hipchat.com/account/api
3. Create a token.
4. Copy the value - this is the WILL_V2_TOKEN.""",
            },
            {
                "name": "WILL_REDIS_URL",
                "obtain_at": """1. Set up an accessible redis host locally or in production
2. Set WILL_REDIS_URL to its full value, i.e. redis://localhost:6379/7""",
            }
        ]

        puts("")
        puts("Verifying environment...")

        for r in required_settings:
            if not self.verify_individual_setting(r):
                missing_settings = True

        if missing_settings:
            error("Will was unable to start because some required environment variables are missing.  Please fix them and try again!")
            sys.exit(1)
        else:
            puts("")

        puts("Verifying credentials...")
        # Parse 11111_222222@chat.hipchat.com into id, where 222222 is the id.  Yup.
        user_id = settings.USERNAME[0:settings.USERNAME.find("@")][settings.USERNAME.find("_")+1:]

        # Splitting into a thread. Necessary because *BSDs (including OSX) don't have threadsafe DNS.
        # http://stackoverflow.com/questions/1212716/python-interpreter-blocks-multithreaded-dns-requests
        q = Queue()
        p = Process(target=self.get_hipchat_user, args=(user_id,), kwargs={"q":q,})
        p.start()
        user_data = q.get()
        p.join()

        if "error" in user_data:
            error("We ran into trouble: '%(message)s'" % user_data["error"])
            sys.exit(1)
        with indent(2):
            show_valid("%s authenticated" % user_data["name"])
            os.environ["WILL_NAME"] = user_data["name"]
            show_valid("@%s verified as handle" % user_data["mention_name"])
            os.environ["WILL_HANDLE"] = user_data["mention_name"]

        puts("")

    def load_config(self):
        puts("Loading configuration...")
        with indent(2):
            settings.import_settings(quiet=False)
        puts("")

        puts("Verifying rooms...")
        # If we're missing ROOMS, join all of them.
        with indent(2):
            if settings.ROOMS == None:
                # Yup. Thanks, BSDs.
                q = Queue()
                p = Process(target=self.update_available_rooms, args=(), kwargs={"q":q,})
                p.start()
                rooms_list = q.get()
                show_valid("Joining all %s known rooms." % len(rooms_list))
                os.environ["WILL_ROOMS"] = ";".join(rooms_list)
                p.join()
                settings.import_settings()
            else:
                show_valid("Joining the %s room%s specified." % (len(settings.ROOMS), "s" if len(settings.ROOMS)>1 else ""))
        puts("")
            

    def verify_plugin_settings(self):
        puts("Verifying settings requested by plugins...")

        missing_settings = False
        missing_setting_error_messages = []
        with indent(2):
            for name, meta in self.required_settings_from_plugins.items():
                if not hasattr(settings, name):
                    error_message = "%(setting_name)s is missing. It's required by the %(plugin_name)s plugin's '%(function_name)s' method." % meta
                    puts(colored.red("✗ %(setting_name)s" % meta))
                    missing_setting_error_messages.append(error_message)
                    missing_settings = True
                else:
                    show_valid("%(setting_name)s" % meta)

            if missing_settings:
                puts("")
                warn("Will is missing settings required by some plugins. He's starting up anyway, but you will run into errors if you try to use those plugins!")
                self.add_startup_error("\n".join(missing_setting_error_messages))
            else:
                puts("")

    def bootstrap_storage_mixin(self):
        puts("Bootstrapping storage...")
        try:
            self.bootstrap_storage()
            with indent(2):
                show_valid("Connection to %s successful." % settings.REDIS_URL)
            puts("")
        except:
            error("Unable to connect to %s" % settings.REDIS_URL)
            sys.exit(1)
        

    def bootstrap_scheduler(self):
        bootstrapped = False
        try:
            self.save("plugin_modules_library", self._plugin_modules_library)
            Scheduler.clear_locks(self)
            self.scheduler = Scheduler()

            for plugin_info, fn, function_name in self.periodic_tasks:
                meta = fn.will_fn_metadata
                self.add_periodic_task(plugin_info["full_module_name"], plugin_info["name"], function_name, meta["sched_args"], meta["sched_kwargs"], meta["function_name"],)
            for plugin_info, fn, function_name in self.random_tasks:
                meta = fn.will_fn_metadata
                self.add_random_tasks(plugin_info["full_module_name"], plugin_info["name"], function_name, meta["start_hour"], meta["end_hour"], meta["day_of_week"], meta["num_times_per_day"])
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
                for k, v in instantiated_fn.will_fn_metadata.items():
                    if "bottle_" in k and k != "bottle_route":
                        bottle_route_args[k[len("bottle_"):]] = v
                bottle.route(instantiated_fn.will_fn_metadata["bottle_route"], **bottle_route_args)(instantiated_fn)
            bootstrapped = True
        except Exception, e:
            self.startup_error("Error bootstrapping bottle", e)
        if bootstrapped:
            show_valid("Web server started.")
            bottle.run(host='0.0.0.0', port=settings.HTTPSERVER_PORT, server='gevent', quiet=True)

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
            show_valid("Will is running.")
            self.process(block=True)

    def bootstrap_plugins(self):
        puts("Bootstrapping plugins...")
        OTHER_HELP_HEADING = "Other"
        plugin_modules = {}
        plugin_modules_library = {}

        # NOTE: You can't access self.storage here, or it will deadlock when the threads try to access redis.
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
                            
                                try:
                                    plugin_modules[full_module_name] = imp.load_source(module_name, module_path)
                                except:
                                    # If it's blacklisted, don't worry if this blows up.
                                    if blacklisted:
                                        pass
                                    else:
                                        raise

                                parent_mod = path_components[-2].split("/")[-1]
                                parent_help_text = parent_mod.title()
                                try:
                                    parent_root = os.path.join(root, "__init__.py")
                                    parent = imp.load_source(parent_mod, parent_root)
                                    parent_help_text = getattr(parent, "MODULE_DESCRIPTION", parent_help_text)
                                except:
                                    # If it's blacklisted, don't worry if this blows up.
                                    if blacklisted:
                                        pass
                                    else:
                                        raise

                                plugin_modules_library[full_module_name] = {
                                    "full_module_name": full_module_name,
                                    "file_path": module_path,
                                    "name": module_name,
                                    "parent_name": plugin_name,
                                    "parent_module_name": parent_mod,
                                    "parent_help_text": parent_help_text,
                                    "blacklisted": blacklisted,
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
                                        "parent_help_text": plugin_modules_library[name]["parent_help_text"],
                                        "blacklisted": plugin_modules_library[name]["blacklisted"],
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
            self.plugins.sort(key=operator.itemgetter("parent_module_name"))
            self.required_settings_from_plugins = {}
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
                        if plugin_info["blacklisted"]:
                            puts("✗ %s (blacklisted)" % plugin_name)
                        else:
                            for function_name, fn in inspect.getmembers(plugin_info["class"], predicate=inspect.ismethod):
                                try:
                                    # Check for required_settings
                                    with indent(2):
                                        if hasattr(fn, "will_fn_metadata"):
                                            meta = fn.will_fn_metadata
                                            if "required_settings" in meta:
                                                for s in meta["required_settings"]:
                                                    self.required_settings_from_plugins[s] = {
                                                        "plugin_name": plugin_name,
                                                        "function_name": function_name,
                                                        "setting_name": s,
                                                    }
                                            if "listens_to_messages" in meta and meta["listens_to_messages"] and "listener_regex" in meta:
                                                # puts("- %s" % function_name)
                                                regex = meta["listener_regex"]
                                                if not meta["case_sensitive"]:
                                                    regex = "(?i)%s" % regex
                                                help_regex = meta["listener_regex"]
                                                if meta["listens_only_to_direct_mentions"]:
                                                    help_regex = "@%s %s" % (settings.HANDLE, help_regex)
                                                self.all_listener_regexes.append(help_regex)
                                                if meta["__doc__"]:
                                                    pht = plugin_info.get("parent_help_text", None)
                                                    if pht:
                                                        if pht in self.help_modules:
                                                            self.help_modules[pht].append(meta["__doc__"])
                                                        else:
                                                            self.help_modules[pht] = [meta["__doc__"],]
                                                    else:
                                                        self.help_modules[OTHER_HELP_HEADING].append(meta["__doc__"])
                                                if meta["multiline"]:
                                                    compiled_regex = re.compile(regex, re.MULTILINE | re.DOTALL)
                                                else:
                                                    compiled_regex = re.compile(regex)
                                                self.message_listeners.append({
                                                    "function_name": function_name,
                                                    "class_name": plugin_info["name"],
                                                    "regex_pattern": meta["listener_regex"],
                                                    "regex": compiled_regex,
                                                    "fn": getattr(plugin_info["class"](), function_name),
                                                    "args": meta["listener_args"],
                                                    "include_me": meta["listener_includes_me"],
                                                    "direct_mentions_only": meta["listens_only_to_direct_mentions"],
                                                    "admin_only": meta["listens_only_to_admin"],
                                                })
                                                if meta["listener_includes_me"]:
                                                    self.some_listeners_include_me = True
                                            elif "periodic_task" in meta and meta["periodic_task"]:
                                                # puts("- %s" % function_name)
                                                self.periodic_tasks.append((plugin_info, fn, function_name))
                                            elif "random_task" in meta and meta["random_task"]:
                                                # puts("- %s" % function_name)
                                                self.random_tasks.append((plugin_info, fn, function_name))
                                            elif "bottle_route" in meta:
                                                # puts("- %s" % function_name)
                                                self.bottle_routes.append((plugin_info["class"], function_name))
                                except Exception, e:
                                    error(plugin_name)
                                    self.startup_error("Error bootstrapping %s.%s" % (plugin_info["class"], function_name,), e)
                            show_valid(plugin_name)
                except Exception, e:
                    self.startup_error("Error bootstrapping %s" % (plugin_info["class"],), e)
        puts("")
