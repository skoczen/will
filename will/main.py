import logging
import inspect
import importlib
import os
import pkgutil
import sys
import time
from os.path import abspath, join, curdir, isdir
from multiprocessing import Process
# Monkeypatch has to come early
from gevent import monkey; monkey.patch_all()

from bottle import route, run, template
from celery.bin.celeryd_detach import detached_celeryd

from listen import WillClient
from celeryconfig import app
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



class WillBot(object):

    def bootstrap(self):
        self.bootstrap_plugins()

        # Start up threads.

        # # Celery
        # celery_thread = Process(target=self.bootstrap_celery)
        # # celery_thread.daemon = True
        
        # # Bottle
        # bottle_thread = Process(target=self.bootstrap_bottle)
        # # bottle_thread.daemon = True

        # # XMPP Listener
        # xmpp_thread = Process(target=self.bootstrap_xmpp)
        # # xmpp_thread.daemon = True

        # try:
        #     celery_thread.start()
        #     bottle_thread.start()
        #     xmpp_thread.start()

        #     while True: time.sleep(100)
        # except (KeyboardInterrupt, SystemExit):
        #     celery_thread.terminate()
        #     bottle_thread.terminate()
        #     xmpp_thread.terminate()
        #     print '\n\nReceived keyboard interrupt, quitting threads.',
        #     while celery_thread.is_alive() or\
        #           bottle_thread.is_alive() or\
        #           xmpp_thread.is_alive():
        #             sys.stdout.write(".")
        #             sys.stdout.flush()
        #             time.sleep(0.5)


    def bootstrap_celery(self):
        print "bootstrapping celery"
        import celery.app
        import importlib
        celery_app = celery.app.app_or_default()

        # The Celery config needs to be imported before it can be used with config_from_object().
        importlib.import_module('celeryconfig')
        celery_app.config_from_object("celeryconfig")

        celery_app.start(["celeryd", "worker", "--beat",])
        # detached_celeryd(app).execute_from_commandline()


    def bootstrap_bottle(self):
        print "bootstrapping bottle"
        run(host='localhost', port=settings.WILL_HTTPSERVER_PORT, server='gevent')
        pass

    def bootstrap_xmpp(self):
        print "bootstrapping xmpp"
        xmpp = WillClient()
        xmpp.connect()
        xmpp.process(block=True)

    def bootstrap_plugins(self):
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
                    print module_path
                    plugin_modules[module] = importlib.import_module("will.plugins.%s" % module_path)

        self.plugins = []
        for name, module in plugin_modules.items():
            print name
            for class_name, cls in inspect.getmembers(module, predicate=inspect.isclass):
                if hasattr(cls, "is_will_plugin") and cls.is_will_plugin:
                    self.plugins.append({"name": class_name, "class": cls})


        # Sift and Sort.
        self.message_listeners = []

        for plugin_info in self.plugins:
            for function_name, fn in inspect.getmembers(plugin_info["class"], predicate=inspect.ismethod):
                if hasattr(fn, "listens_to_messages") and fn.listens_to_messages:
                    self.message_listeners.append(fn)


        # def respond_to(regex):
        #     print "respond_to %s" % regex
        #     def wrap(f):
        #         def wrapped_f(*args):
        #             # print "Decorator arguments:", regex
        #             f(*args)
        #         wrapped_f.respond_to = regex
        #         return wrapped_f
        #     return wrap


        # def scheduled(run_every):
        #     def wrap(f):
        #         def wrapped_f(*args):
        #             # print "Decorator arguments:", regex
        #             f(*args)
        #         return wrapped_f
        #     return wrap

        # def one_time_task(when):
        #     def wrap(f):
        #         def wrapped_f(*args):
        #             # print "Decorator arguments:", regex
        #             f(*args)
        #         return wrapped_f
        #     return wrap

        # def hear(regex, include_me=False):
        #     def wrap(f):
        #         def wrapped_f(*args):
        #             # print "Decorator arguments:", regex
        #             f(*args)
        #         return wrapped_f
        #     return wrap


        # def randomly(start_hour=0, end_hour=23, weekdays_only=False):
        #     def wrap(f):
        #         def wrapped_f(*args):
        #             # print "Decorator arguments:", 
        #             f(*args)
        #         return wrapped_f
        #     return wrap


        # Get all methods on the plugin
        # inspect.getmembers(module, predicate=inspect.isfunction)



if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR, format='%(levelname)-8s %(message)s')
    bot = WillBot()
    bot.bootstrap()

    print "\nExiting."