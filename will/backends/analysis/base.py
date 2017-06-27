import time
from multiprocessing.queues import Empty
from will import settings
from will.decorators import require_settings
from will.mixins import PubSubMixin
from will.abstractions import Event


class AnalysisBackend(PubSubMixin, object):
    is_will_analysisbackend = True

    def __watch_input_queue(self):
        while True:
            try:
                m = self.pubsub.get_message()
                if m:
                    # print "about to __analyze"
                    # print m
                    self.__analyze(m)
                time.sleep(settings.QUEUE_INTERVAL)

                # message = self.__input_queue.get(timeout=settings.QUEUE_INTERVAL)
                # # print "AnalysisBackend heard: %s" % message
                # self.__analyze(message)
            except AttributeError:
                pass
            except (KeyboardInterrupt, SystemExit):
                pass

    def __analyze(self, data):
        try:
            self.pubsub.publish(
                "analysis.complete",
                self.do_analyze(data),
                reference_message=data
            )
            # print "published"
        except:
            # TODO: replace these with proper will error handling.
            import traceback; traceback.print_exc();
        # self.__output_queue.put(ret)

    def do_analyze(self, message):
        # Take message, return a dict to add to its context.
        raise NotImplemented

    def start(self, name, input_queue, output_queue, **kwargs):
        for k, v in kwargs.items():
            self.__dict__[k] = v

        self.name = name
        self.__input_queue = input_queue
        self.__output_queue = output_queue
        self.bootstrap_pubsub()
        self.subscribe("analysis.start")
        self.__watch_input_queue()
