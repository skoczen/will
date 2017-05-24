import datetime
import hashlib
import time
from will import settings
from will.utils import Bunch
from multiprocessing.queues import Empty
from multiprocessing import Process


class IOBackend(object):
    is_will_iobackend = True

    def bootstrap(self):
        pass

    def handle_incoming_event(self, event):
        raise NotImplemented

    def handle_outgoing_event(self, event):
        raise NotImplemented

    def terminate(self):
        pass

    def __start_event_listeners(self):
        running = True
        while running:
            try:
                try:
                    output_event = self.output_queue.get(timeout=0.1)
                    if output_event:
                        self.handle_outgoing_event(output_event)

                except Empty:
                    pass

                try:
                    input_event = self.input_queue.get(timeout=0.1)
                    if input_event:
                        self.handle_incoming_event(input_event)

                except Empty:
                    pass

                if hasattr(self, "stdin_queue") and self.stdin_queue:
                    try:
                        input_event = self.stdin_queue.get(timeout=0.1)
                        if input_event:
                            self.handle_incoming_event(input_event)

                    except Empty:
                        pass

                try:
                    terminate_event = self.terminate_queue.get(timeout=0.1)
                    if terminate_event:
                        self.__handle_terminate()
                        running = False

                except Empty:
                    pass
            except (KeyboardInterrupt, SystemExit):
                pass

    def __handle_terminate(self):
        if hasattr(self, "__event_listener_thread"):
            self.__event_listener_thread.terminate()
            while self.__event_listener_thread.is_alive():
                time.sleep(0.1)
        if hasattr(self, "terminate"):
            self.terminate()

    def _start(self, name, input_queue, output_queue, terminate_queue, stdin_queue=None):
        self.name = name
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.terminate_queue = terminate_queue
        if stdin_queue:
            self.stdin_queue = stdin_queue

        self.__event_listener_thread = Process(
            target=self.__start_event_listeners,
        )
        self.__event_listener_thread.start()

        # Here's the problem - bootstrap is blocking, and I need to make sure the event listeners are 
        # handled properly and kick off
        self.bootstrap()


class StdInOutIOBackend(IOBackend):
    stdin_process = True


MESSAGE_REQUIRED_FIELDS = [
    # TODO: make sure we have all the context we need for ACL/etc.
    "is_direct",  # Direct to me (answer no matter what?)
    "environment",  # 1-1 or room
    "will_is_mentioned",
    "will_said_it",
    "sender",
    "backend_supports_acl",
    "content",
    "backend",
    # "timestamp",
]


class Message(object):

    def __init__(self, *args, **kwargs):
        for f in MESSAGE_REQUIRED_FIELDS:
            if not f in kwargs:
                raise Exception("Missing %s in Message construction." % f)

        for f in kwargs:
            self.__dict__[f] = kwargs[f]

        if "timestamp" in kwargs:
            self.timestamp = kwargs["timestamp"]
        else:
            self.timestamp = datetime.datetime.now()

        h = hashlib.md5()
        h.update(self.timestamp.strftime("%s"))
        h.update(self.content)
        self.hash = h.hexdigest()

        self.metadata = Bunch()

    def __unicode__(self, *args, **kwargs):
        if len(self.content) > 20:
            content_str = "%s..." % self.content[:20]
        else:
            content_str = self.content
        return u"Message: \"%s\"\n  %s (%s) " % (
            content_str,
            self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            self.backend,
        )

    def __str__(self, *args, **kwargs):
        return self.__unicode__(*args, **kwargs)


EVENT_REQUIRED_FIELDS = [
    "type",
    "content",
]


class Event(Bunch):

    def __init__(self, *args, **kwargs):
        for f in EVENT_REQUIRED_FIELDS:
            if not f in kwargs:
                raise Exception("Missing %s in Event construction." % f)
        for f in kwargs:
            self.__dict__[f] = kwargs[f]

        if "timestamp" in kwargs:
            self.timestamp = kwargs["timestamp"]
        else:
            self.timestamp = datetime.datetime.now()

        super(Event, self).__init__(*args, **kwargs)
