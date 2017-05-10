from multiprocessing.queues import Empty
from will import settings
from will.decorators import require_settings


class AnalysisBackend(object):
    is_will_analysisbackend = True

    def __watch_input_queue(self):
        while True:
            try:
                message = self.__input_queue.get(timeout=0.1)
                print "AnalysisBackend heard: %s" % message
                self.__analyze(message)
            except Empty:
                pass

    def __analyze(self, message):
        ret = self.do_analyze(message)
        self.__output_queue.put(ret)

    def do_analyze(self, message):
        # Take message, return a dict to add to its context.
        raise NotImplemented

    def start(self, name, input_queue, output_queue, **kwargs):
        for k, v in kwargs.items():
            self.__dict__[k] = v

        self.name = name
        self.__input_queue = input_queue
        self.__output_queue = output_queue
        self.__watch_input_queue()
