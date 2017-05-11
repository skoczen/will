import datetime
import hashlib
from will import settings
from will.utils import Bunch


class IOBackend(object):
    is_will_iobackend = True

    # def send_direct_message(self, *args, **kwargs):
    #     # This needs to recieve the message and context, and is what's responsible
    #     # for returning the reply along the proper IO channel

    #     if "hipchat" in settings.CHAT_BACKENDS:
    #         b = HipChatBackend()
    #         b.send_direct_message(*args, **kwargs)

    #     if "shell" in settings.CHAT_BACKENDS:
    #         b = ShellBackend()
    #         b.send_direct_message(*args, **kwargs)

    # def send_direct_message_reply(self, *args, **kwargs):

    #     if "hipchat" in settings.CHAT_BACKENDS:
    #         b = HipChatBackend()
    #         b.send_direct_message_reply(*args, **kwargs)

    #     if "shell" in settings.CHAT_BACKENDS:
    #         b = ShellBackend()
    #         b.send_direct_message_reply(*args, **kwargs)

    # def send_room_message(self, *args, **kwargs):

    #     if "hipchat" in settings.CHAT_BACKENDS:
    #         b = HipChatBackend()
    #         b.send_room_message(*args, **kwargs)

    #     if "shell" in settings.CHAT_BACKENDS:
    #         b = ShellBackend()
    #         b.send_room_message(*args, **kwargs)

    # def set_room_topic(self, *args, **kwargs):

    #     if "hipchat" in settings.CHAT_BACKENDS:
    #         b = HipChatBackend()
    #         b.set_room_topic(*args, **kwargs)

    #     if "shell" in settings.CHAT_BACKENDS:
    #         b = ShellBackend()
    #         b.set_room_topic(*args, **kwargs)

    # def get_user(self, *args, **kwargs):

    #     if "hipchat" in settings.CHAT_BACKENDS:
    #         b = HipChatBackend()
    #         b.get_hipchat_user(*args, **kwargs)

    #     if "shell" in settings.CHAT_BACKENDS:
    #         b = ShellBackend()
    #         b.get_user(*args, **kwargs)

    # @property
    # def get_user_list(self, *args, **kwargs):

    #     if "hipchat" in settings.CHAT_BACKENDS:
    #         b = HipChatBackend()
    #         b.full_hipchat_user_list(*args, **kwargs)

    #     if "shell" in settings.CHAT_BACKENDS:
    #         b = ShellBackend()
    #         b.full_hipchat_user_list(*args, **kwargs)

    # def get_room_list(self, *args, **kwargs):
    #     pass

    # def handle_message(message, context, *args, **kwargs):
    #     context.platform = ""

    #     pass


MESSAGE_REQUIRED_FIELDS = [
    "is_direct",
    "body",
    "backend",
    # "timestamp",
]


class Message(object):

    def __init__(self, *args, **kwargs):
        # TODO: Decide whether to map all kwargs over.
        for f in MESSAGE_REQUIRED_FIELDS:
            if not f in kwargs:
                raise Exception("Missing %s in Message construction." % f)
            self.__dict__[f] = kwargs[f]

        if "timestamp" in kwargs:
            self.timestamp = kwargs["timestamp"]
        else:
            self.timestamp = datetime.datetime.now()

        h = hashlib.md5()
        h.update(self.timestamp.strftime("%s"))
        h.update(self.body)
        self.hash = h.hexdigest()

        self.metadata = Bunch()

    def __unicode__(self, *args, **kwargs):
        if len(self.body) > 20:
            body_str = "%s..." % self.body[:20]
        else:
            body_str = self.body
        return u"Message: \"%s\"\n  %s (%s) " % (
            body_str,
            self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            self.backend,
        )

    def __str__(self, *args, **kwargs):
        return self.__unicode__(*args, **kwargs)
