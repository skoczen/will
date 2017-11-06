# -- coding: utf-8 -
from clint.textui import indent, puts
import datetime
import hashlib
import logging
from pytz import timezone as pytz_timezone
import signal
import time
import traceback

from will import settings
from will.utils import Bunch, show_valid, error, warn
from will.mixins import PubSubMixin, SleepMixin, SettingsMixin
from will.abstractions import Message, Event, Person
from multiprocessing import Process


class IOBackend(PubSubMixin, SleepMixin, SettingsMixin, object):
    is_will_iobackend = True
    required_settings = []

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
        try:
            m = self.normalize_incoming_event(event)
            if m:
                self.pubsub.publish("message.incoming", m, reference_message=m)
        except:
            logging.critical("Error handling incoming event %s: \n%s" % (
                event,
                traceback.format_exc(),
            ))

    def handle_outgoing_event(self, event):
        raise NotImplemented

    def terminate(self):
        pass

    def __publish_incoming_message(self, message):
        return self.pubsub.publish("message.incoming", message, reference_message=message)

    def __start_event_listeners(self):
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        running = True
        while running:
            try:
                pubsub_event = self.pubsub.get_message()
                if pubsub_event:
                    if pubsub_event.type == "message.incoming":
                        self.handle_incoming_event(pubsub_event)
                    elif pubsub_event.type == "message.outgoing.%s" % self.name:
                        self.handle_outgoing_event(pubsub_event.data)
                    elif pubsub_event.type == "message.incoming.stdin":
                        self.handle_incoming_event(pubsub_event)
                    elif pubsub_event.type == "message.no_response.%s" % self.name:
                        self.handle_outgoing_event(pubsub_event)
                    elif pubsub_event.type == "system.terminate":
                        self.__handle_terminate()
                        running = False
            except (KeyboardInterrupt, SystemExit):
                pass
            self.sleep_for_event_loop()

    def __handle_terminate(self):
        if hasattr(self, "__event_listener_thread"):
            logging.debug("__event_listener_thread")
            try:
                self.__event_listener_thread.terminate()
                while self.__event_listener_thread.is_alive():
                    self.sleep_for_event_loop()
            except (KeyboardInterrupt, SystemExit):
                pass
        if hasattr(self, "terminate"):
            try:
                self.terminate()
            except (KeyboardInterrupt, SystemExit):
                pass

    def _start(self, name):
        try:
            self.name = name
            self.bootstrap_pubsub()
            self.pubsub.subscribe([
                "message.incoming",
                "message.outgoing.%s" % self.name,
                "message.no_response.%s" % self.name,
                "system.terminate",
            ])
            if hasattr(self, "stdin_process") and self.stdin_process:
                self.pubsub.subscribe(["message.incoming.stdin", ])

            self.__event_listener_thread = Process(
                target=self.__start_event_listeners,
            )
            self.__event_listener_thread.start()

            self.bootstrap()
        except (KeyboardInterrupt, SystemExit):
            pass
        except:
            logging.critical("Error starting io adapter %s: \n%s" % (
                self.name,
                traceback.format_exc(),
            ))


class StdInOutIOBackend(IOBackend):
    stdin_process = True
