import logging
import sys
import time
from gevent import monkey; monkey.patch_all()
from multiprocessing import Process

from bottle import route, run, template
from celery.bin.celeryd_detach import detached_celeryd

from listen import WillClient
from celeryconfig import app
import settings
from plugins.keep_alive import *

# Force UTF8
if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')
else:
    raw_input = input


def bootstrap_celery():
    print "bootstrapping celery"
    import celery.app
    import importlib
    celery_app = celery.app.app_or_default()

    # The Celery config needs to be imported before it can be used with config_from_object().
    importlib.import_module('celeryconfig')
    celery_app.config_from_object("celeryconfig")

    celery_app.start(["celeryd", "worker", "--beat",])
    # detached_celeryd(app).execute_from_commandline()


def bootstrap_bottle():
    print "bootstrapping bottle"
    run(host='localhost', port=settings.WILL_HTTPSERVER_PORT, server='gevent')
    pass

def bootstrap_xmpp():
    print "bootstrapping xmpp"
    xmpp = WillClient()
    xmpp.connect()
    xmpp.process(block=True)


if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR, format='%(levelname)-8s %(message)s')

    # Start up threads.

    # Celery
    celery_thread = Process(target=bootstrap_celery)
    # celery_thread.daemon = True
    
    # Bottle
    bottle_thread = Process(target=bootstrap_bottle)
    # bottle_thread.daemon = True

    # XMPP Listener
    xmpp_thread = Process(target=bootstrap_xmpp)
    # xmpp_thread.daemon = True

    try:
        celery_thread.start()
        bottle_thread.start()
        xmpp_thread.start()

        while True: time.sleep(100)
    except (KeyboardInterrupt, SystemExit):
        celery_thread.terminate()
        bottle_thread.terminate()
        xmpp_thread.terminate()
        print '\n\nReceived keyboard interrupt, quitting threads.',
        while celery_thread.is_alive() or\
              bottle_thread.is_alive() or\
              xmpp_thread.is_alive():
                sys.stdout.write(".")
                sys.stdout.flush()
                time.sleep(0.5)


    print "\nExiting."