# -*- coding: utf-8 -*-

import copy
import datetime
import imp
from importlib import import_module
import inspect
import logging
from multiprocessing import Process, Queue
import operator
import os
from os.path import abspath, dirname
import re
import signal
import sys
import threading
import time
import traceback
try:
    from yappi import profile as yappi_profile
except:
    from will.decorators import passthrough_decorator as yappi_profile

from clint.textui import colored, puts, indent
import bottle


from will import settings
from will.backends import analysis, execution, generation, io_adapters
from will.backends.io_adapters.base import Event
from will.mixins import ScheduleMixin, StorageMixin, ErrorMixin, SleepMixin,\
    PluginModulesLibraryMixin, EmailMixin, PubSubMixin
from will.scheduler import Scheduler
from will.utils import show_valid, show_invalid, error, warn, note, print_head, Bunch


# Force UTF8
if sys.version_info < (3, 0):
    reload(sys)  # flake8: noqa
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


def yappi_aggregate(func, stats):
    if hasattr(settings, "PROFILING_ENABLED") and settings.PROFILING_ENABLED:
        fname = "callgrind.%s" % (func.__name__)

        try:
            stats.add(fname)
        except IOError:
            pass

        stats.save("will_profiles/%s" % fname, "callgrind")


class WillBot(EmailMixin, StorageMixin, ScheduleMixin, PubSubMixin, SleepMixin,
              ErrorMixin, PluginModulesLibraryMixin):

    def __init__(self, **kwargs):
        if "template_dirs" in kwargs:
            warn("template_dirs is now depreciated")
        if "plugin_dirs" in kwargs:
            warn("plugin_dirs is now depreciated")

        log_level = getattr(settings, 'LOGLEVEL', logging.ERROR)
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%a, %d %b %Y %H:%M:%S',
        )
        # Bootstrap exit code.
        self.exiting = False

        # Find all the PLUGINS modules
        try:
            plugins = settings.PLUGINS
            self.plugins_dirs = {}
        except:
            # We're missing settings. They handle that.
            sys.exit(1)

        # Set template dirs.
        full_path_template_dirs = []
        for t in settings.TEMPLATE_DIRS:
            full_path_template_dirs.append(os.path.abspath(t))

        # Add will's templates_root
        if TEMPLATES_ROOT not in full_path_template_dirs:
            full_path_template_dirs += [TEMPLATES_ROOT, ]

        # Add this project's templates_root
        if PROJECT_TEMPLATE_ROOT not in full_path_template_dirs:
            full_path_template_dirs += [PROJECT_TEMPLATE_ROOT, ]

        # Convert those to dirs
        for plugin in plugins:
            path_name = None
            for mod in plugin.split('.'):
                if path_name is not None:
                    path_name = [path_name]
                file_name, path_name, description = imp.find_module(mod, path_name)

            # Add, uniquely.
            self.plugins_dirs[os.path.abspath(path_name)] = plugin

            if os.path.exists(os.path.join(os.path.abspath(path_name), "templates")):
                full_path_template_dirs.append(
                    os.path.join(os.path.abspath(path_name), "templates")
                )

        # Key by module name
        self.plugins_dirs = dict(zip(self.plugins_dirs.values(), self.plugins_dirs.keys()))

        # Storing here because storage hasn't been bootstrapped yet.
        os.environ["WILL_TEMPLATE_DIRS_PICKLED"] =\
            ";;".join(full_path_template_dirs)

    @yappi_profile(return_callback=yappi_aggregate)
    def bootstrap(self):
        print_head()
        self.load_config()
        self.bootstrap_storage_mixin()
        self.bootstrap_pubsub_mixin()
        self.bootstrap_plugins()
        self.verify_plugin_settings()
        started = self.verify_io()
        if started:
            puts("Bootstrapping complete.")

            # Save help modules.
            self.save("help_modules", self.help_modules)

            puts("\nStarting core processes:")

            # try:
            # Exit handlers.
            # signal.signal(signal.SIGINT, self.handle_sys_exit)
            # # TODO this hangs for some reason.
            # signal.signal(signal.SIGTERM, self.handle_sys_exit)

            # Scheduler
            self.scheduler_thread = Process(target=self.bootstrap_scheduler)

            # Bottle
            self.bottle_thread = Process(target=self.bootstrap_bottle)

            # Event handler
            self.incoming_event_thread = Process(target=self.bootstrap_event_handler)

            self.io_threads = []
            self.analysis_threads = []
            self.generation_threads = []

            with indent(2):
                try:
                    # Start up threads.
                    self.bootstrap_io()
                    self.bootstrap_analysis()
                    self.bootstrap_generation()
                    self.bootstrap_execution()

                    self.scheduler_thread.start()
                    self.bottle_thread.start()
                    self.incoming_event_thread.start()

                    errors = self.get_startup_errors()
                    if len(errors) > 0:
                        error_message = "FYI, I ran into some problems while starting up:"
                        for err in errors:
                            error_message += "\n%s\n" % err
                        puts(colored.red(error_message))

                    self.stdin_listener_thread = False
                    if self.has_stdin_io_backend:

                        self.current_line = ""
                        while True:
                            for line in sys.stdin.readline():
                                if "\n" in line:
                                    self.publish(
                                        "message.incoming.stdin",
                                        Event(
                                            type="message.incoming.stdin",
                                            content=self.current_line,
                                        )
                                    )
                                    self.current_line = ""
                                else:
                                    self.current_line += line
                            self.sleep_for_event_loop(2)
                    else:
                        while True:
                            time.sleep(100)
                except (KeyboardInterrupt, SystemExit):
                    self.handle_sys_exit()

    def verify_individual_setting(self, test_setting, quiet=False):
        if not test_setting.get("only_if", True):
            return True

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

    def load_config(self):
        puts("Loading configuration...")
        with indent(2):
            settings.import_settings(quiet=False)
        puts("")

    @yappi_profile(return_callback=yappi_aggregate)
    def verify_io(self):
        puts("Verifying IO backends...")
        missing_settings = False
        missing_setting_error_messages = []
        one_valid_backend = False
        self.valid_io_backends = []

        if not hasattr(settings, "IO_BACKENDS"):
            settings.IO_BACKENDS = ["will.backends.io_adapters.shell", ]
        # Try to import them all, catch errors and output trouble if we hit it.
        for b in settings.IO_BACKENDS:
            with indent(2):
                try:
                    path_name = None
                    for mod in b.split('.'):
                        if path_name is not None:
                            path_name = [path_name]
                        file_name, path_name, description = imp.find_module(mod, path_name)

                    # show_valid("%s" % b)
                    module = import_module(b)
                    for class_name, cls in inspect.getmembers(module, predicate=inspect.isclass):
                        if (
                            hasattr(cls, "is_will_iobackend") and
                            cls.is_will_iobackend and
                            class_name != "IOBackend" and
                            class_name != "StdInOutIOBackend"
                        ):
                            c = cls()
                            show_valid(c.friendly_name)
                            c.verify_settings()
                            one_valid_backend = True
                            self.valid_io_backends.append(b)
                except EnvironmentError as e:
                    puts(colored.red("  ✗ %s is missing settings, and will be disabled." % b))
                    puts()

                    missing_settings = True

                except Exception as e:
                    error_message = (
                        "IO backend %s is missing. Please either remove it \nfrom config.py "
                        "or WILL_IO_BACKENDS, or provide it somehow (pip install, etc)."
                    ) % b
                    puts(colored.red("✗ %s" % b))
                    puts()
                    puts(error_message)
                    puts()
                    puts(traceback.format_exc())
                    missing_setting_error_messages.append(error_message)
                    missing_settings = True

        if missing_settings and not one_valid_backend:
            puts("")
            error(
                "Unable to find a valid IO backend - will has no way to talk "
                "or listen!\n       Quitting now, please look at the above errors!\n"
            )
            self.handle_sys_exit()
            return False
        puts()
        return True

    @yappi_profile(return_callback=yappi_aggregate)
    def verify_analysis(self):
        puts("Verifying Analysis backends...")
        missing_settings = False
        missing_setting_error_messages = []
        one_valid_backend = False

        if not hasattr(settings, "ANALYZE_BACKENDS"):
            settings.ANALYZE_BACKENDS = ["will.backends.analysis.nothing", ]
        # Try to import them all, catch errors and output trouble if we hit it.
        for b in settings.ANALYZE_BACKENDS:
            with indent(2):
                try:
                    path_name = None
                    for mod in b.split('.'):
                        if path_name is not None:
                            path_name = [path_name]
                        file_name, path_name, description = imp.find_module(mod, path_name)

                    one_valid_backend = True
                    show_valid("%s" % b)
                except ImportError as e:
                    error_message = (
                        "Analysis backend %s is missing. Please either remove it \nfrom config.py "
                        "or WILL_ANALYZE_BACKENDS, or provide it somehow (pip install, etc)."
                    ) % b
                    puts(colored.red("✗ %s" % b))
                    puts()
                    puts(error_message)
                    puts()
                    puts(traceback.format_exc())
                    missing_setting_error_messages.append(error_message)
                    missing_settings = True

        if missing_settings and not one_valid_backend:
            puts("")
            error(
                "Unable to find a valid IO backend - will has no way to talk "
                "or listen!\n       Quitting now, please look at the above errors!\n"
            )
            sys.exit(1)
        puts()

    @yappi_profile(return_callback=yappi_aggregate)
    def verify_generate(self):
        puts("Verifying Generation backends...")
        missing_settings = False
        missing_setting_error_messages = []
        one_valid_backend = False

        if not hasattr(settings, "GENERATION_BACKENDS"):
            settings.GENERATION_BACKENDS = ["will.backends.generation.strict_regex", ]
        # Try to import them all, catch errors and output trouble if we hit it.
        for b in settings.GENERATION_BACKENDS:
            with indent(2):
                try:
                    path_name = None
                    for mod in b.split('.'):
                        if path_name is not None:
                            path_name = [path_name]
                        file_name, path_name, description = imp.find_module(mod, path_name)

                    one_valid_backend = True
                    show_valid("%s" % b)
                except ImportError as e:
                    error_message = (
                        "Generation backend %s is missing. Please either remove it \nfrom config.py "
                        "or WILL_GENERATION_BACKENDS, or provide it somehow (pip install, etc)."
                    ) % b
                    puts(colored.red("✗ %s" % b))
                    puts()
                    puts(error_message)
                    puts()
                    puts(traceback.format_exc())
                    missing_setting_error_messages.append(error_message)
                    missing_settings = True

        if missing_settings and not one_valid_backend:
            puts("")
            error(
                "Unable to find a valid IO backend - will has no way to talk "
                "or listen!\n       Quitting now, please look at the above errors!\n"
            )
            sys.exit(1)
        puts()

    @yappi_profile(return_callback=yappi_aggregate)
    def verify_execution(self):
        puts("Verifying Execution backend...")
        missing_settings = False
        missing_setting_error_messages = []
        one_valid_backend = False

        if not hasattr(settings, "EXECUTION_BACKENDS"):
            settings.EXECUTION_BACKENDS = ["will.backends.execution.all", ]

        with indent(2):
            for b in settings.EXECUTION_BACKENDS:
                try:
                    path_name = None
                    for mod in b.split('.'):
                        if path_name is not None:
                            path_name = [path_name]
                        file_name, path_name, description = imp.find_module(mod, path_name)

                    one_valid_backend = True
                    show_valid("%s" % b)
                except ImportError as e:
                    error_message = (
                        "Execution backend %s is missing. Please either remove it \nfrom config.py "
                        "or WILL_EXECUTION_BACKENDS, or provide it somehow (pip install, etc)."
                    ) % b
                    puts(colored.red("✗ %s" % b))
                    puts()
                    puts(error_message)
                    puts()
                    puts(traceback.format_exc())
                    missing_setting_error_messages.append(error_message)
                    missing_settings = True

        if missing_settings and not one_valid_backend:
            puts("")
            error(
                "Unable to find a valid IO backend - will has no way to talk "
                "or listen!\n       Quitting now, please look at the above errors!\n"
            )
            sys.exit(1)
        puts()

    @yappi_profile(return_callback=yappi_aggregate)
    def bootstrap_execution(self):
        missing_setting_error_messages = []
        self.execution_backends = []
        self.running_execution_threads = []
        execution_backends = getattr(settings, "EXECUTION_BACKENDS", ["will.backends.execution.all", ])
        for b in execution_backends:
            module = import_module(b)
            for class_name, cls in inspect.getmembers(module, predicate=inspect.isclass):
                try:
                    if (
                        hasattr(cls, "is_will_execution_backend") and
                        cls.is_will_execution_backend and
                        class_name != "ExecutionBackend"
                    ):
                        c = cls(bot=self)
                        self.execution_backends.append(c)
                        show_valid("Execution: %s Backend started." % cls.__name__)
                except ImportError as e:
                    error_message = (
                        "Execution backend %s is missing. Please either remove it \nfrom config.py "
                        "or WILL_EXECUTION_BACKENDS, or provide it somehow (pip install, etc)."
                    ) % settings.EXECUTION_BACKENDS
                    puts(colored.red("✗ %s" % settings.EXECUTION_BACKENDS))
                    puts()
                    puts(error_message)
                    puts()
                    puts(traceback.format_exc())
                    missing_setting_error_messages.append(error_message)

        if len(self.execution_backends) == 0:
            puts("")
            error(
                "Unable to find a valid execution backend - will has no way to make decisions!"
                "\n       Quitting now, please look at the above error!\n"
            )
            sys.exit(1)

    @yappi_profile(return_callback=yappi_aggregate)
    def verify_plugin_settings(self):
        puts("Verifying settings requested by plugins...")

        missing_settings = False
        missing_setting_error_messages = []
        with indent(2):
            for name, meta in self.required_settings_from_plugins.items():
                if not hasattr(settings, name):
                    error_message = (
                        "%(setting_name)s is missing. It's required by the"
                        "%(plugin_name)s plugin's '%(function_name)s' method."
                    ) % meta
                    puts(colored.red("✗ %(setting_name)s" % meta))
                    missing_setting_error_messages.append(error_message)
                    missing_settings = True
                else:
                    show_valid("%(setting_name)s" % meta)

            if missing_settings:
                puts("")
                warn(
                    "Will is missing settings required by some plugins. "
                    "He's starting up anyway, but you will run into errors"
                    " if you try to use those plugins!"
                )
                self.add_startup_error("\n".join(missing_setting_error_messages))
            else:
                puts("")

    def handle_sys_exit(self, *args, **kwargs):
        # if not self.exiting:
        try:
            sys.stdout.write("\n\nReceived shutdown, quitting threads.")
            sys.stdout.flush()
            self.exiting = True

            if "WILL_EPHEMERAL_SECRET_KEY" in os.environ:
                os.environ["WILL_SECRET_KEY"] = ""
                os.environ["WILL_EPHEMERAL_SECRET_KEY"] = ""

            if hasattr(self, "scheduler_thread") and self.scheduler_thread:
                try:
                    self.scheduler_thread.terminate()
                except KeyboardInterrupt:
                    pass
            if hasattr(self, "bottle_thread") and self.bottle_thread:
                try:
                    self.bottle_thread.terminate()
                except KeyboardInterrupt:
                    pass
            if hasattr(self, "incoming_event_thread") and self.incoming_event_thread:
                try:
                    self.incoming_event_thread.terminate()
                except KeyboardInterrupt:
                    pass

            # if self.stdin_listener_thread:
            #     self.stdin_listener_thread.terminate()

            self.publish("system.terminate", {})

            if hasattr(self, "analysis_threads") and self.analysis_threads:
                for t in self.analysis_threads:
                    try:
                        t.terminate()
                    except KeyboardInterrupt:
                        pass

            if hasattr(self, "generation_threads") and self.generation_threads:
                for t in self.generation_threads:
                    try:
                        t.terminate()
                    except KeyboardInterrupt:
                        pass

            if hasattr(self, "running_execution_threads") and self.running_execution_threads:
                for t in self.running_execution_threads:
                    try:
                        t.terminate()
                    except KeyboardInterrupt:
                        pass
        except:
            print("\n\n\nException while exiting!!")
            import traceback
            traceback.print_exc()
            sys.exit(1)

        while (
            (hasattr(self, "scheduler_thread") and self.scheduler_thread and self.scheduler_thread and self.scheduler_thread.is_alive()) or
            (hasattr(self, "scheduler_thread") and self.scheduler_thread and self.bottle_thread and self.bottle_thread.is_alive()) or
            (hasattr(self, "scheduler_thread") and self.scheduler_thread and self.incoming_event_thread and self.incoming_event_thread.is_alive()) or
            # self.stdin_listener_thread.is_alive() or
            any([t.is_alive() for t in self.io_threads]) or
            any([t.is_alive() for t in self.analysis_threads]) or
            any([t.is_alive() for t in self.generation_threads]) or
            any([t.is_alive() for t in self.running_execution_threads])
            # or
            # ("hipchat" in settings.CHAT_BACKENDS and xmpp_thread and xmpp_thread.is_alive())
        ):
                sys.stdout.write(".")
                sys.stdout.flush()
                time.sleep(0.5)
        print(". done.\n")
        sys.exit(1)

    @yappi_profile(return_callback=yappi_aggregate)
    def bootstrap_event_handler(self):
        self.analysis_timeout = getattr(settings, "ANALYSIS_TIMEOUT_MS", 2000)
        self.generation_timeout = getattr(settings, "GENERATION_TIMEOUT_MS", 2000)
        self.pubsub.subscribe(["message.*", "analysis.*", "generation.*"])

        # TODO: change this to the number of running analysis threads
        num_analysis_threads = len(settings.ANALYZE_BACKENDS)
        num_generation_threads = len(settings.GENERATION_BACKENDS)
        analysis_threads = {}
        generation_threads = {}

        while True:
            try:
                event = self.pubsub.get_message()
                if event and hasattr(event, "type"):
                    now = datetime.datetime.now()
                    logging.info("%s - %s" % (event.type, event.original_incoming_event_hash))
                    logging.debug("\n\n *** Event (%s): %s\n\n" % (event.type, event))

                    # TODO: Order by most common.
                    if event.type == "message.incoming":
                        # A message just got dropped off one of the IO Backends.
                        # Send it to analysis.

                        analysis_threads[event.original_incoming_event_hash] = {
                            "count": 0,
                            "timeout_end": now + datetime.timedelta(seconds=self.analysis_timeout / 1000),
                            "original_incoming_event": event,
                            "working_event": event,
                        }
                        self.pubsub.publish("analysis.start", event.data.original_incoming_event, reference_message=event)

                    elif event.type == "analysis.complete":
                        q = analysis_threads[event.original_incoming_event_hash]
                        q["working_event"].update({"analysis": event.data})
                        q["count"] += 1
                        logging.info("Analysis for %s:  %s/%s" % (event.original_incoming_event_hash, q["count"], num_analysis_threads))

                        if q["count"] >= num_analysis_threads or now > q["timeout_end"]:
                            # done, move on.
                            generation_threads[event.original_incoming_event_hash] = {
                                "count": 0,
                                "timeout_end": (
                                    now +
                                    datetime.timedelta(seconds=self.generation_timeout / 1000)
                                ),
                                "original_incoming_event": q["original_incoming_event"],
                                "working_event": q["working_event"],
                            }
                            try:
                                del analysis_threads[event.original_incoming_event_hash]
                            except:
                                pass
                            self.pubsub.publish("generation.start", q["working_event"], reference_message=q["original_incoming_event"])

                    elif event.type == "generation.complete":
                        q = generation_threads[event.original_incoming_event_hash]
                        if not hasattr(q["working_event"], "generation_options"):
                            q["working_event"].generation_options = []
                        if hasattr(event, "data") and len(event.data) > 0:
                            for d in event.data:
                                q["working_event"].generation_options.append(d)
                        q["count"] += 1
                        logging.info("Generation for %s:  %s/%s" % (event.original_incoming_event_hash, q["count"], num_generation_threads))

                        if q["count"] >= num_generation_threads or now > q["timeout_end"]:
                            # done, move on to execution.
                            for b in self.execution_backends:
                                try:
                                    logging.info("Executing for %s on %s" % (b, event.original_incoming_event_hash))
                                    b.handle_execution(q["working_event"])
                                except:
                                    logging.critical(
                                        "Error running %s for %s.  \n\n%s\nContinuing...\n" % (
                                            b,
                                            event.original_incoming_event_hash,
                                            traceback.format_exc()
                                        )
                                    )
                                    break
                            try:
                                del generation_threads[event.original_incoming_event_hash]
                            except:
                                pass

                    elif event.type == "message.no_response":
                        logging.info("Publishing no response for %s" % (event.original_incoming_event_hash,))
                        logging.info(event.data.__dict__)
                        try:
                            self.publish("message.outgoing.%s" % event.data.backend, event)
                        except:
                            logging.critical(
                                "Error publishing no_response for %s.  \n\n%s\nContinuing...\n" % (
                                    event.original_incoming_event_hash,
                                    traceback.format_exc()
                                )
                            )
                            pass
                    elif event.type == "message.not_allowed":
                        logging.info("Publishing not allowed for %s" % (event.original_incoming_event_hash,))
                        try:
                            self.publish("message.outgoing.%s" % event.data.backend, event)
                        except:
                            logging.critical(
                                "Error publishing not_allowed for %s.  \n\n%s\nContinuing...\n" % (
                                    event.original_incoming_event_hash,
                                    traceback.format_exc()
                                )
                            )
                            pass
                else:
                    self.sleep_for_event_loop()
            # except KeyError:
            #     pass
            except:
                logging.exception("Error handling message")

    @yappi_profile(return_callback=yappi_aggregate)
    def bootstrap_storage_mixin(self):
        puts("Bootstrapping storage...")
        try:
            self.bootstrap_storage()
            # Make sure settings are there.
            self.storage.verify_settings()
            with indent(2):
                show_valid("Bootstrapped!")
            puts("")
        except ImportError :
            module_name = traceback.format_exc().split(" ")[-1]
            error("Unable to bootstrap storage - attempting to load %s" % module_name)
            puts(traceback.format_exc())
            sys.exit(1)
        except Exception:
            error("Unable to bootstrap storage!")
            puts(traceback.format_exc())
            sys.exit(1)

    @yappi_profile(return_callback=yappi_aggregate)
    def bootstrap_pubsub_mixin(self):
        puts("Bootstrapping pubsub...")
        try:
            self.bootstrap_pubsub()
            # Make sure settings are there.
            self.pubsub.verify_settings()
            with indent(2):
                show_valid("Bootstrapped!")
            puts("")
        except ImportError as e:
            module_name = traceback.format_exc().split(" ")[-1]
            error("Unable to bootstrap pubsub - attempting to load %s" % module_name)
            puts(traceback.format_exc())
            sys.exit(1)
        except Exception as e:
            error("Unable to bootstrap pubsub!")
            puts(traceback.format_exc())
            sys.exit(1)

    @yappi_profile(return_callback=yappi_aggregate)
    def bootstrap_scheduler(self):
        bootstrapped = False
        try:
            self.save("plugin_modules_library", self._plugin_modules_library)
            Scheduler.clear_locks(self)
            self.scheduler = Scheduler()

            for plugin_info, fn, function_name in self.periodic_tasks:
                meta = fn.will_fn_metadata
                self.add_periodic_task(
                    plugin_info["full_module_name"],
                    plugin_info["name"],
                    function_name,
                    meta["sched_args"],
                    meta["sched_kwargs"],
                    meta["function_name"],
                )
            for plugin_info, fn, function_name in self.random_tasks:
                meta = fn.will_fn_metadata
                self.add_random_tasks(
                    plugin_info["full_module_name"],
                    plugin_info["name"],
                    function_name,
                    meta["start_hour"],
                    meta["end_hour"],
                    meta["day_of_week"],
                    meta["num_times_per_day"]
                )
            bootstrapped = True
        except Exception as e:
            self.startup_error("Error bootstrapping scheduler", e)
        if bootstrapped:
            show_valid("Scheduler started.")
            self.scheduler.start_loop(self)

    @yappi_profile(return_callback=yappi_aggregate)
    def bootstrap_bottle(self):
        bootstrapped = False
        try:
            for cls, function_name in self.bottle_routes:
                instantiated_cls = cls(bot=self)
                instantiated_fn = getattr(instantiated_cls, function_name)
                bottle_route_args = {}
                for k, v in instantiated_fn.will_fn_metadata.items():
                    if "bottle_" in k and k != "bottle_route":
                        bottle_route_args[k[len("bottle_"):]] = v
                bottle.route(instantiated_fn.will_fn_metadata["bottle_route"], **bottle_route_args)(instantiated_fn)
            bootstrapped = True
        except Exception as e:
            self.startup_error("Error bootstrapping bottle", e)
        if bootstrapped:
            show_valid("Web server started at %s." % (settings.PUBLIC_URL,))
            bottle.run(host='0.0.0.0', port=settings.HTTPSERVER_PORT, server='cherrypy', quiet=True)

    @yappi_profile(return_callback=yappi_aggregate)
    def bootstrap_io(self):
        # puts("Bootstrapping IO...")
        self.has_stdin_io_backend = False
        self.io_backends = []
        self.io_threads = []
        self.stdin_io_backends = []
        for b in self.valid_io_backends:
            module = import_module(b)
            for class_name, cls in inspect.getmembers(module, predicate=inspect.isclass):
                try:
                    if (
                        hasattr(cls, "is_will_iobackend") and
                        cls.is_will_iobackend and
                        class_name != "IOBackend" and
                        class_name != "StdInOutIOBackend"
                    ):
                        c = cls()

                        if hasattr(c, "stdin_process") and c.stdin_process:
                            thread = Process(
                                target=c._start,
                                args=(b,),
                            )
                            thread.start()
                            self.has_stdin_io_backend = True
                            self.io_threads.append(thread)
                        else:
                            thread = Process(
                                target=c._start,
                                args=(
                                    b,
                                )
                            )
                            thread.start()
                            self.io_threads.append(thread)

                        show_valid("IO: %s Backend started." % cls.friendly_name)
                except Exception as e:
                    self.startup_error("Error bootstrapping %s io" % b, e)

            self.io_backends.append(b)

    @yappi_profile(return_callback=yappi_aggregate)
    def bootstrap_analysis(self):

        self.analysis_backends = []
        self.analysis_threads = []

        for b in settings.ANALYZE_BACKENDS:
            module = import_module(b)
            for class_name, cls in inspect.getmembers(module, predicate=inspect.isclass):
                try:
                    if (
                        hasattr(cls, "is_will_analysisbackend") and
                        cls.is_will_analysisbackend and
                        class_name != "AnalysisBackend"
                    ):
                        c = cls()
                        thread = Process(
                            target=c.start,
                            args=(b,),
                            kwargs={"bot": self},
                        )
                        thread.start()
                        self.analysis_threads.append(thread)
                        show_valid("Analysis: %s Backend started." % cls.__name__)
                except Exception as e:
                    self.startup_error("Error bootstrapping %s io" % b, e)

            self.analysis_backends.append(b)
        pass

    @yappi_profile(return_callback=yappi_aggregate)
    def bootstrap_generation(self):
        self.generation_backends = []
        self.generation_threads = []

        for b in settings.GENERATION_BACKENDS:
            module = import_module(b)
            for class_name, cls in inspect.getmembers(module, predicate=inspect.isclass):
                try:
                    if (
                        hasattr(cls, "is_will_generationbackend") and
                        cls.is_will_generationbackend and
                        class_name != "GenerationBackend"
                    ):
                        c = cls()
                        thread = Process(
                            target=c.start,
                            args=(b,),
                            kwargs={"bot": self},
                        )
                        thread.start()
                        self.generation_threads.append(thread)
                        show_valid("Generation: %s Backend started." % cls.__name__)
                except Exception as e:
                    self.startup_error("Error bootstrapping %s io" % b, e)

            self.generation_backends.append(b)
        pass

    @yappi_profile(return_callback=yappi_aggregate)
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
                                path_components = module_path.split(os.sep)
                                module_name = path_components[-1][:-3]
                                full_module_name = ".".join(path_components)

                                # Check blacklist.
                                blacklisted = False
                                for b in settings.PLUGIN_BLACKLIST:
                                    if b in full_module_name:
                                        blacklisted = True
                                        break

                                parent_mod = path_components[-2].split("/")[-1]
                                parent_help_text = parent_mod.title()
                                # Don't even *try* to load a blacklisted module.
                                if not blacklisted:
                                    try:
                                        plugin_modules[full_module_name] = imp.load_source(module_name, module_path)

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
                            except Exception as e:
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
                                        "parent_path": plugin_modules_library[name]["file_path"],
                                        "parent_module_name": plugin_modules_library[name]["parent_module_name"],
                                        "parent_help_text": plugin_modules_library[name]["parent_help_text"],
                                        "blacklisted": plugin_modules_library[name]["blacklisted"],
                                    })
                            except Exception as e:
                                self.startup_error("Error bootstrapping %s" % (class_name,), e)
                    except Exception as e:
                        self.startup_error("Error bootstrapping %s" % (name,), e)

            self._plugin_modules_library = plugin_modules_library

            # Sift and Sort.
            self.message_listeners = {}
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
                        plugin_warnings = []
                        # Just a little nicety
                        if plugin_name[-6:] == "Plugin":
                            plugin_name = plugin_name[:-6]
                        if plugin_info["blacklisted"]:
                            puts("✗ %s (blacklisted)" % plugin_name)
                        else:
                            plugin_instances = {}
                            for function_name, fn in inspect.getmembers(
                                plugin_info["class"],
                                predicate=lambda x: inspect.ismethod(x) or inspect.isfunction(x)
                            ):
                                try:
                                    # Check for required_settings
                                    with indent(2):
                                        if hasattr(fn, "will_fn_metadata"):
                                            meta = fn.will_fn_metadata
                                            if "warnings" in meta:
                                                plugin_warnings.append(meta["warnings"])
                                            if "required_settings" in meta:
                                                for s in meta["required_settings"]:
                                                    self.required_settings_from_plugins[s] = {
                                                        "plugin_name": plugin_name,
                                                        "function_name": function_name,
                                                        "setting_name": s,
                                                    }
                                            if (
                                                "listens_to_messages" in meta and
                                                meta["listens_to_messages"] and
                                                "listener_regex" in meta
                                            ):
                                                # puts("- %s" % function_name)
                                                regex = meta["listener_regex"]
                                                if not meta["case_sensitive"]:
                                                    regex = "(?i)%s" % regex
                                                help_regex = meta["listener_regex"]
                                                if meta["listens_only_to_direct_mentions"]:
                                                    help_regex = "@%s %s" % (settings.WILL_HANDLE, help_regex)
                                                self.all_listener_regexes.append(help_regex)
                                                if meta["__doc__"]:
                                                    pht = plugin_info.get("parent_help_text", None)
                                                    if pht:
                                                        if pht in self.help_modules:
                                                            self.help_modules[pht].append(u"%s" % meta["__doc__"])
                                                        else:
                                                            self.help_modules[pht] = [u"%s" % meta["__doc__"]]
                                                    else:
                                                        self.help_modules[OTHER_HELP_HEADING].append(u"%s" % meta["__doc__"])
                                                if meta["multiline"]:
                                                    compiled_regex = re.compile(regex, re.MULTILINE | re.DOTALL)
                                                else:
                                                    compiled_regex = re.compile(regex)

                                                if plugin_info["class"] in plugin_instances:
                                                    instance = plugin_instances[plugin_info["class"]]
                                                else:
                                                    instance = plugin_info["class"](bot=self)
                                                    plugin_instances[plugin_info["class"]] = instance

                                                full_method_name = "%s.%s" % (plugin_info["name"], function_name)
                                                cleaned_info = copy.copy(plugin_info)
                                                del cleaned_info["module"]
                                                del cleaned_info["class"]
                                                self.message_listeners[full_method_name] = {
                                                    "full_method_name": full_method_name,
                                                    "function_name": function_name,
                                                    "class_name": plugin_info["name"],
                                                    "regex_pattern": meta["listener_regex"],
                                                    "regex": compiled_regex,
                                                    "fn": getattr(instance, function_name),
                                                    "args": meta["listener_args"],
                                                    "include_me": meta["listener_includes_me"],
                                                    "case_sensitive": meta["case_sensitive"],
                                                    "multiline": meta["multiline"],
                                                    "direct_mentions_only": meta["listens_only_to_direct_mentions"],
                                                    "admin_only": meta["listens_only_to_admin"],
                                                    "acl": meta["listeners_acl"],
                                                    "plugin_info": cleaned_info,
                                                }
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

                                except Exception as e :
                                    error(plugin_name)
                                    self.startup_error(
                                        "Error bootstrapping %s.%s" % (
                                            plugin_info["class"],
                                            function_name,
                                        ), e
                                    )
                            if len(plugin_warnings) > 0:
                                show_invalid(plugin_name)
                                for w in plugin_warnings:
                                    warn(w)
                            else:
                                show_valid(plugin_name)
                except Exception as e:
                    self.startup_error("Error bootstrapping %s" % (plugin_info["class"],), e)
            self.save("all_listener_regexes", self.all_listener_regexes)
        puts("")
