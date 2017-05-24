from multiprocessing.queues import Empty
from will import settings
from will.decorators import require_settings


class GenerationBackend(object):
    is_will_generationbackend = True

    def __watch_input_queue(self):
        while True:
            try:
                message = self.__input_queue.get(timeout=settings.QUEUE_INTERVAL)
                # print "GenerationBackend heard: %s" % message
                self.__generate(message)
            except Empty:
                pass
            except (KeyboardInterrupt, SystemExit):
                pass

    def __generate(self, message):
        ret = self.do_generate(message)
        self.__output_queue.put(ret)

    def do_generate(self, message):
        # Take message, return a list of possible responses/matches
        raise NotImplemented

    def start(self, name, input_queue, output_queue, **kwargs):
        for k, v in kwargs.items():
            self.__dict__[k] = v

        self.name = name
        self.__input_queue = input_queue
        self.__output_queue = output_queue
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
