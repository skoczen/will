import logging
import inspect
import importlib
import os
import pkgutil
import re
import sys
import time
import traceback
from os.path import abspath, join, curdir, isdir
from multiprocessing import Process
# Monkeypatch has to come early
from gevent import monkey; monkey.patch_all()

from bottle import route, run, template

from listen import WillXMPPClientMixin
from mixins import ScheduleMixin
from storage import StorageMixin
from scheduler import Scheduler
import settings
from plugin_base import WillPlugin


# Force UTF8
if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')
else:
    raw_input = input

# Update path
PROJECT_ROOT = abspath(curdir)
PLUGINS_ROOT = abspath(join(PROJECT_ROOT, "will", "plugins"))
sys.path.append(PROJECT_ROOT)
sys.path.append(join(PROJECT_ROOT, "will"))



class WillBot(WillXMPPClientMixin, StorageMixin, ScheduleMixin):

    def __init__(self):
        pass

    def bootstrap(self):
        self.bootstrap_storage()
        self.bootstrap_plugins()

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
            
            print "started"
            while True: time.sleep(100)
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

    def clear_locks(self):
        self.save("scheduler_add_lock", False)
        self.save("scheduler_lock", False)    
        self.save("will_periodic_list", [])

    def bootstrap_scheduler(self):
        self.scheduler = Scheduler()
        self.clear_locks()
        for cls, fn in self.periodic_tasks:
            self.add_periodic_task(cls, fn.sched_args, fn.sched_kwargs, fn,)
        for cls, fn in self.random_tasks:
            self.add_random_tasks(cls, fn, fn.start_hour, fn.end_hour, fn.day_of_week, fn.num_times_per_day)
        self.scheduler.start_loop(self)

    def bootstrap_bottle(self):
        print "bootstrapping bottle"
        run(host='localhost', port=settings.WILL_HTTPSERVER_PORT, server='gevent')
        pass

    def bootstrap_xmpp(self):
        print "bootstrapping xmpp"
        self.start_xmpp_client()
        self.connect()
        self.process(block=True)

    def bootstrap_plugins(self):
        print "Bootstrapping plugins..."
        plugin_modules = {}

        # Sure does feel like this should be a solved problem somehow.
        for root, dirs, files in os.walk(PLUGINS_ROOT, topdown=False):
            for f in files:
                if f[-3:] == ".py" and f != "__init__.py":
                    module = f[:-3]
                    parent_module = root.replace("%s" % PLUGINS_ROOT, "")
                    if parent_module != "":
                        module_paths = parent_module.split("/")[1:]
                        module_paths.append(module)
                        module_path = ".".join(module_paths)
                    else:
                        module_path = module
                    try:
                        plugin_modules[module] = importlib.import_module("will.plugins.%s" % module_path)
                    except:
                        logging.critical("Error will.plugins.%s.  \n\n%s\nContinuing...\n" % (module_path, traceback.format_exc() ))

        self.plugins = []
        for name, module in plugin_modules.items():
            try:
                for class_name, cls in inspect.getmembers(module, predicate=inspect.isclass):
                    try:
                        if hasattr(cls, "is_will_plugin") and cls.is_will_plugin and class_name != "WillPlugin":
                            self.plugins.append({"name": class_name, "class": cls})
                    except:
                        logging.critical("Error bootstrapping %s.  \n\n%s\nContinuing...\n" % (class_name, traceback.format_exc() ))
            except:
                logging.critical("Error bootstrapping %s.  \n\n%s\nContinuing...\n" % (name, traceback.format_exc() ))

        # Sift and Sort.
        self.message_listeners = []
        self.periodic_tasks = []
        self.random_tasks = []
        self.some_listeners_include_me = False
        for plugin_info in self.plugins:
            try:
                print "\n %s:" % plugin_info["name"]
                for function_name, fn in inspect.getmembers(plugin_info["class"], predicate=inspect.ismethod):
                    try:
                        if hasattr(fn, "listens_to_messages") and fn.listens_to_messages and hasattr(fn, "listener_regex"):
                            print " - %s" % function_name
                            regex = fn.listener_regex
                            if not fn.case_sensitive:
                                regex = "(?i)%s" % regex
                            self.message_listeners.append({
                                "function_name": function_name,
                                "regex_pattern": fn.listener_regex,
                                "regex": re.compile(regex),
                                "fn": getattr(plugin_info["class"](), function_name),
                                "args": fn.listener_args,
                                "include_me": fn.listener_includes_me,
                                "direct_mentions_only": fn.listens_only_to_direct_mentions,
                            })
                            if fn.listener_includes_me:
                                self.some_listeners_include_me = True
                        elif hasattr(fn, "periodic_task") and fn.periodic_task:
                            print " - %s" % function_name
                            self.periodic_tasks.append((plugin_info["class"], fn))
                        elif hasattr(fn, "random_task") and fn.random_task:
                            print " - %s" % function_name
                            self.random_tasks.append((plugin_info["class"], fn))
                    except:
                        logging.critical("Error bootstrapping %s.%s. \n\n%s\nContinuing...\n" % (plugin_info["class"], function_name, traceback.format_exc() ))
            except:
                logging.critical("Error bootstrapping %s.  \n\n%s\nContinuing...\n" % (plugin_info["class"], traceback.format_exc() ))


if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR, format='%(levelname)-8s %(message)s')
    bot = WillBot()
    bot.bootstrap()

    print "\nExiting."