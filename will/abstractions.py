# -- coding: utf-8 -
import datetime
import hashlib
import logging
from pytz import timezone as pytz_timezone

from will.utils import Bunch


class Message(object):
    will_internal_type = "Message"
    REQUIRED_FIELDS = [
        "is_direct",
        "is_private_chat",
        "is_group_chat",
        "will_is_mentioned",
        "will_said_it",
        "sender",
        "backend_supports_acl",
        "content",
        "backend",
        "original_incoming_event",
    ]

    def __init__(self, *args, **kwargs):
        for f in self.REQUIRED_FIELDS:
            if not f in kwargs:
                raise Exception("Missing %s in Message construction." % f)

        for f in kwargs:
            self.__dict__[f] = kwargs[f]

        if "timestamp" in kwargs:
            self.timestamp = kwargs["timestamp"]
        else:
            self.timestamp = datetime.datetime.now()

        # Clean content.
        self.content = self._clean_message_content(self.content)

        h = hashlib.md5()
        h.update(self.timestamp.strftime("%s").encode("utf-8"))
        h.update(self.content.encode("utf-8"))
        self.hash = h.hexdigest()

        self.metadata = Bunch()
        if not "original_incoming_event_hash" in kwargs:
            if hasattr(self, "original_incoming_event") and hasattr(self.original_incoming_event, "hash"):
                self.original_incoming_event_hash = self.original_incoming_event.hash
            else:
                self.original_incoming_event_hash = self.hash

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

    def _clean_message_content(self, s):
        # Clear out 'smart' quotes and the like.
        s = s.replace("’", "'").replace("‘", "'").replace('“', '"').replace('”', '"')
        s = s.replace(u"\u2018", "'").replace(u"\u2019", "'")
        s = s.replace(u"\u201c", '"').replace(u"\u201d", '"')
        return s


class Event(Bunch):
    will_internal_type = "Event"

    REQUIRED_FIELDS = [
        "type",
        "version",
    ]

    def __init__(self, *args, **kwargs):
        super(Event, self).__init__(*args, **kwargs)
        self.version = 1

        for f in self.REQUIRED_FIELDS:
            if not f in kwargs and not hasattr(self, f):
                raise Exception("Missing %s in Event construction." % f)

        if "timestamp" in kwargs:
            self.timestamp = kwargs["timestamp"]
        else:
            self.timestamp = datetime.datetime.now()

        h = hashlib.md5()
        h.update(self.timestamp.strftime("%s").encode("utf-8"))
        h.update(self.type.encode("utf-8"))
        self.hash = h.hexdigest()
        if not "original_incoming_event_hash" in kwargs:
            if hasattr(self, "original_incoming_event") and hasattr(self.original_incoming_event, "hash"):
                self.original_incoming_event_hash = self.original_incoming_event.hash
            else:
                self.original_incoming_event_hash = self.hash


class Person(Bunch):
    will_is_person = True
    will_internal_type = "Person"
    REQUIRED_FIELDS = [
        "id",
        "handle",
        "mention_handle",
        "source",
        "name",
        "first_name"
        # "timezone",
    ]

    def __init__(self, *args, **kwargs):
        super(Person, self).__init__(*args, **kwargs)

        for f in kwargs:
            self.__dict__[f] = kwargs[f]

        # Provide first_name
        if "first_name" not in kwargs:
            self.first_name = self.name.split(" ")[0]

        for f in self.REQUIRED_FIELDS:
            if not hasattr(self, f):
                raise Exception("Missing %s in Person construction." % f)

        # Set TZ offset.
        if hasattr(self, "timezone") and self.timezone:
            self.timezone = pytz_timezone(self.timezone)
            self.utc_offset = self.timezone._utcoffset
        else:
            self.timezone = False
            self.utc_offset = False

    @property
    def nick(self):
        logging.warn("sender.nick is deprecated and will be removed eventually. Please use sender.handle instead!")
        return self.handle


class Channel(Bunch):
    will_internal_type = "Channel"
    REQUIRED_FIELDS = [
        "id",
        "name",
        "source",
        "members",
    ]

    def __init__(self, *args, **kwargs):
        super(Channel, self).__init__(*args, **kwargs)

        for f in self.REQUIRED_FIELDS:
            if not f in kwargs:
                raise Exception("Missing %s in Channel construction." % f)
        for f in kwargs:
            self.__dict__[f] = kwargs[f]

        for id, m in self.members.items():
            if not m.will_is_person:
                raise Exception("Someone in the member list is not a Person instance.\n%s" % m)
