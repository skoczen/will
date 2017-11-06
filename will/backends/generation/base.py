import logging
import random
import time
import traceback
import dill as pickle
from will import settings
from will.decorators import require_settings
from will.mixins import PubSubMixin, SleepMixin
from will.abstractions import Event
from will.utils import Bunch


class GenerationBackend(PubSubMixin, SleepMixin, object):
    is_will_generationbackend = True

    def __watch_pubsub(self):
        while True:
            try:
                m = self.pubsub.get_message()
                if m:
                    self.__generate(m.data)
            except (KeyboardInterrupt, SystemExit):
                pass
            self.sleep_for_event_loop()

    def __generate(self, message):
        ret = self.do_generate(message)
        try:
            self.pubsub.publish("generation.complete", ret, reference_message=message)
        except (KeyboardInterrupt, SystemExit):
            pass
        except:
            logging.critical("Error publishing generation.complete: \n%s" % traceback.format_exc())

    def do_generate(self, message):
        # Take message, return a list of possible responses/matches
        raise NotImplemented

    def start(self, name, **kwargs):
        for k, v in kwargs.items():
            self.__dict__[k] = v

        self.name = name
        self.bootstrap_pubsub()
        self.subscribe("generation.start")
        self.__watch_pubsub()


OPTION_REQUIRED_FIELDS = [
    "backend",
    "context",
    "score",
]


class GeneratedOption(object):

    def __init__(self, *args, **kwargs):
        for o in OPTION_REQUIRED_FIELDS:
            if o not in kwargs:
                raise Exception("Missing '%s' argument to the generator backend." % o)

        for k, v in kwargs.items():
            self.__dict__[k] = v

        return super(GeneratedOption, self).__init__()

    def __unicode__(self):
        return "%s - %s" % (self.score, self.context)

    def __str__(self):
        return "%s - %s" % (self.score, self.context)
