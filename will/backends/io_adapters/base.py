import datetime
import hashlib
from will import settings
from will.utils import Bunch


class IOBackend(object):
    is_will_iobackend = True


MESSAGE_REQUIRED_FIELDS = [
    "is_direct",
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
        # TODO: Decide whether to map all kwargs over.
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
