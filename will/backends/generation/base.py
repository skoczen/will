from multiprocessing.queues import Empty
from will import settings
from will.decorators import require_settings


class GenerationBackend(object):
    is_will_generationbackend = True

    def __watch_input_queue(self):
        while True:
            try:
                message = self.__input_queue.get(timeout=0.1)
                print "GenerationBackend heard: %s" % message
                self.__generate(message)
            except Empty:
                pass

    def __generate(self, message):
        ret = self.do_generate(message)
        self.__output_queue.put(ret)

    def do_generate(self, message):
        # Take message, return a list of possible responses/matches
        raise NotImplemented

    def start(self, name, input_queue, output_queue):
        self.name = name
        self.__input_queue = input_queue
        self.__output_queue = output_queue
        self.__watch_input_queue()
