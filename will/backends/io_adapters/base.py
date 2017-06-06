# -- coding: utf-8 -
import datetime
import hashlib
import logging
from pytz import timezone as pytz_timezone
import time


from will import settings
from will.utils import Bunch
from will.mixins import PubSubMixin
from will.abstractions import Message, Event
from multiprocessing.queues import Empty
from multiprocessing import Process


class IOBackend(PubSubMixin, object):
    is_will_iobackend = True

    def bootstrap(self):
        raise NotImplemented("""A .bootstrap() method was not provided.

        Bootstrap must provide a way to to have:
        a) self.normalize_incoming_event fired, or incoming events put into self.incoming_queue
        b) any necessary threads running for a)
        c) self.handle (string) defined
        d) self.me (Person) defined, with Will's info
        e) self.people (dict of People) defined, with everyone in an organization/backend
        f) self.channels (dict of Channels) defined, with all available channels/rooms.
           Note that Channel asks for members, a list of People.
        g) A way for self.handle, self.me, self.people, and self.channels to be kept accurate,
           with a maximum lag of 60 seconds.
        """)

    def normalize_incoming_event(self, event):
        # Takes a raw event, converts it into a Message, and returns the normalized Message.
        raise NotImplemented

    def handle_incoming_event(self, event):
        m = self.normalize_incoming_event(event)
        if m:
            print "\n\n\n\nhandle_incoming_event"
            print m
            self.pubsub.publish("message.incoming", m, reference_message=m)

    def handle_outgoing_event(self, event):
        raise NotImplemented

    def terminate(self):
        pass

    def __publish_incoming_message(self, message):
        # print "__publish_incoming_message"
        # print message
        return self.pubsub.publish("message.incoming", message, reference_message=message)

    def __start_event_listeners(self):
        running = True
        while running:
            try:
                try:
                    pubsub_event = self.pubsub.get_message()
                    if pubsub_event:
                        # print "pubsub event %s" % (self.name)
                        # print pubsub_event
                        if pubsub_event.type == "message.incoming":
                            self.handle_incoming_event(pubsub_event)
                        if pubsub_event.type == "message.outgoing.%s" % self.name:
                            self.handle_outgoing_event(pubsub_event.data)
                except:
                    import traceback; traceback.print_exc();

                # TODO: get rid of all of the below
                try:
                    output_event = self.output_queue.get(timeout=settings.QUEUE_INTERVAL)
                    if output_event:
                        self.handle_outgoing_event(output_event)

                except Empty:
                    pass

                try:
                    input_event = self.input_queue.get(timeout=settings.QUEUE_INTERVAL)
                    if input_event:
                        m = self.normalize_incoming_event(input_event)

                except Empty:
                    pass

                if hasattr(self, "stdin_queue") and self.stdin_queue:
                    try:
                        input_event = self.stdin_queue.get(timeout=settings.QUEUE_INTERVAL)
                        if input_event:
                            m = self.normalize_incoming_event(input_event)
                            # self.__publish_incoming_message(m)
                            # TODO: handle this as an event

                    except Empty:
                        pass

                try:
                    terminate_event = self.terminate_queue.get(timeout=settings.QUEUE_INTERVAL)
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
                time.sleep(settings.QUEUE_INTERVAL)
        if hasattr(self, "terminate"):
            self.terminate()

    def _start(self, name, input_queue, output_queue, terminate_queue, stdin_queue=None):
        self.name = name
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.terminate_queue = terminate_queue
        self.bootstrap_pubsub()
        self.pubsub.subscribe(["message.incoming.stdin", "message.outgoing.%s" % self.name])

        if stdin_queue:
            self.stdin_queue = stdin_queue

        self.__event_listener_thread = Process(
            target=self.__start_event_listeners,
        )
        self.__event_listener_thread.start()

        self.bootstrap()


class StdInOutIOBackend(IOBackend):
    stdin_process = True
