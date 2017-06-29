import logging
import signal
import traceback
from will import settings
from will.decorators import require_settings
from multiprocessing import Process


class ExecutionBackend(object):
    is_will_execution_backend = True

    def handle_execution(self, message, context):
        raise NotImplemented

    def execute(self, target, *args, **kwargs):
        try:
            t = Process(
                target=target,
                args=args,
                kwargs=kwargs,
            )
            self.bot.running_execution_threads.append(t)
            t.start()
        except (KeyboardInterrupt, SystemExit):
            pass
        except:
            logging.critical("Error running %s: \n%s" % (target, traceback.format_exc()))

    def __init__(self, bot=None, *args, **kwargs):
        self.bot = bot
        if not bot:
            raise Exception("Can't proceed without an instance of bot passed to the backend.")
        super(ExecutionBackend, self).__init__(*args, **kwargs)
