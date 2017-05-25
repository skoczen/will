# -- coding: utf-8 -
import datetime
import hashlib
from pytz import timezone as pytz_timezone
import time


from will import settings
from will.utils import Bunch
from multiprocessing.queues import Empty
from multiprocessing import Process


class IOBackend(object):
    is_will_iobackend = True

    def bootstrap(self):
        """Bootstrap must provide a way to to have:
        a) self.handle_incoming_event fired, or incoming events put into self.incoming_queue
        b) any necessary threads running for a)
        c) self.handle (string) defined
        d) self.me (Person) defined, with Will's info
        e) self.people (list of People) defined, with everyone in an organization/backend
        f) self.channels (list of Channels) defined, with all available channels/rooms.
           Note that Channel asks for members, a list of People.
        g) A way for self.handle, self.me, self.people, and self.channels to be kept accurate,
           with a maximum lag of 60 seconds.
        """
        raise NotImplemented

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
                    output_event = self.output_queue.get(timeout=settings.QUEUE_INTERVAL)
                    if output_event:
                        self.handle_outgoing_event(output_event)

                except Empty:
                    pass

                try:
                    input_event = self.input_queue.get(timeout=settings.QUEUE_INTERVAL)
                    if input_event:
                        self.handle_incoming_event(input_event)

                except Empty:
                    pass

                if hasattr(self, "stdin_queue") and self.stdin_queue:
                    try:
                        input_event = self.stdin_queue.get(timeout=settings.QUEUE_INTERVAL)
                        if input_event:
                            self.handle_incoming_event(input_event)

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
        if stdin_queue:
            self.stdin_queue = stdin_queue

        self.__event_listener_thread = Process(
            target=self.__start_event_listeners,
        )
        self.__event_listener_thread.start()

        self.bootstrap()


class StdInOutIOBackend(IOBackend):
    stdin_process = True


MESSAGE_REQUIRED_FIELDS = [
    # TODO: make sure we have all the context we need for ACL/etc.
    "is_direct",
    "is_private_chat",
    "is_group_chat",
    "will_is_mentioned",
    "will_said_it",
    "sender",
    "backend_supports_acl",
    "content",
    "backend",
    "source",
]

def clean_message_content(s):
    s = s.replace("’", "'").replace("‘", "'").replace('“','"').replace('”','"')
    s = s.replace(u"\u2018", "'").replace(u"\u2019", "'")
    s = s.replace(u"\u201c",'"').replace(u"\u201d", '"')
    return s


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

        # Clean content.
        self.content = clean_message_content(self.content)

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
        super(Event, self).__init__(*args, **kwargs)

        for f in EVENT_REQUIRED_FIELDS:
            if not f in kwargs:
                raise Exception("Missing %s in Event construction." % f)
        for f in kwargs:
            self.__dict__[f] = kwargs[f]

        if "timestamp" in kwargs:
            self.timestamp = kwargs["timestamp"]
        else:
            self.timestamp = datetime.datetime.now()


PERSON_REQUIRED_FIELDS = [
    "id",
    "handle",
    "source",
    "name",
    "first_name"
    # "timezone",
]


class Person(Bunch):
    will_is_person = True

    def __init__(self, *args, **kwargs):
        super(Person, self).__init__(*args, **kwargs)

        for f in kwargs:
            self.__dict__[f] = kwargs[f]

        # Provide first_name
        if "first_name" not in kwargs:
            self.first_name = self.name.split(" ")[0]

        for f in PERSON_REQUIRED_FIELDS:
            if not hasattr(self, f):
                raise Exception("Missing %s in Person construction." % f)

        # Set TZ offset.
        if self.timezone:
            self.timezone = pytz_timezone(self.timezone)
            self.utc_offset = self.timezone._utcoffset
        else:
            self.timezone = False
            self.utc_offset = False

    @property
    def nick(self):
        logging.warn("sender.nick is deprecated, and will be removed at the end of 2017")
        return self.handle

CHANNEL_REQUIRED_FIELDS = [
    "id",
    "name",
    "source",
    "members",
]


class Channel(Bunch):
    def __init__(self, *args, **kwargs):
        super(Channel, self).__init__(*args, **kwargs)

        for f in CHANNEL_REQUIRED_FIELDS:
            if not f in kwargs:
                raise Exception("Missing %s in Channel construction." % f)
        for f in kwargs:
            self.__dict__[f] = kwargs[f]

        for id, m in self.members.items():
            if not m.will_is_person:
                raise Exception("Someone in the member list is not a Person instance.\n%s" % m)

