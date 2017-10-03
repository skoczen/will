import logging
import random
import signal
import time
import traceback
from multiprocessing.queues import Empty
from will import settings
from will.decorators import require_settings
from will.mixins import PubSubMixin, SleepMixin
from will.abstractions import Event


class AnalysisBackend(PubSubMixin, SleepMixin, object):
    is_will_analysisbackend = True

    def __watch_pubsub(self):
        while True:
            try:
                m = self.pubsub.get_message()
                if m:
                    self.__analyze(m)

            except AttributeError:
                pass
            except (KeyboardInterrupt, SystemExit):
                pass
            self.sleep_for_event_loop()

    def __analyze(self, data):
        try:
            self.pubsub.publish(
                "analysis.complete",
                self.do_analyze(data),
                reference_message=data
            )
        except (KeyboardInterrupt, SystemExit):
            pass
        except:
            logging.critical("Error completing analysis: \n%s" % traceback.format_exc())

    def do_analyze(self, message):
        # Take message, return a dict to add to its context.
        raise NotImplemented

    def start(self, name, **kwargs):
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        for k, v in kwargs.items():
            self.__dict__[k] = v

        self.name = name
        self.bootstrap_pubsub()
        self.subscribe("analysis.start")
        self.__watch_pubsub()
