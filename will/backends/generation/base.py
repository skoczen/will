import time
from multiprocessing.queues import Empty
import dill as pickle
from will import settings
from will.decorators import require_settings
from will.mixins import PubSubMixin
from will.abstractions import Event


class GenerationBackend(PubSubMixin, object):
    is_will_generationbackend = True

    def __watch_input_queue(self):
        while True:
            try:
                m = self.pubsub.get_message()
                # TODO: Stopping here, the above check needs to be cleaner, 
                # and then it's back to the event loop in main.py and moving that over.
                # Also, poke at the settings.QUEUE_INTERVAL. :) 
                if m:
                    # print "got generate message (this is busted.)"
                    # print m
                    self.__generate(m.data)
                time.sleep(settings.QUEUE_INTERVAL)
                # message = self.__input_queue.get(timeout=settings.QUEUE_INTERVAL)
                # # print "GenerationBackend heard: %s" % message
                # self.__generate(message)
            except Empty:
                pass
            except (KeyboardInterrupt, SystemExit):
                pass

    def __generate(self, message):
        ret = self.do_generate(message)
        try:
            self.pubsub.publish("generation.complete", ret, reference_message=message)
            # print "published generation.complete"
        except:
            import traceback; traceback.print_exc();
        # self.__output_queue.put(ret)

    def do_generate(self, message):
        # Take message, return a list of possible responses/matches
        raise NotImplemented

    def start(self, name, input_queue, output_queue, **kwargs):
        for k, v in kwargs.items():
            self.__dict__[k] = v

        self.name = name
        self.__input_queue = input_queue
        self.__output_queue = output_queue
        self.bootstrap_pubsub()
        self.subscribe("generation.start")
        self.__watch_input_queue()


OPTION_REQUIRED_FIELDS = [
    "backend",
    # "method",
    "context",
]


class GeneratedOption(object):

    def __init__(self, *args, **kwargs):
        for o in OPTION_REQUIRED_FIELDS:
            if not o in kwargs:
                raise Exception("Missing '%s' argument to the generator backend." % o)
            else:
                self.__dict__[o] = kwargs[o]
                del kwargs[o]

        super(GeneratedOption, self).__init__(*args, **kwargs)
