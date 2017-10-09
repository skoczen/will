import re
import logging

from will import settings
from bottle import request
from mixins import NaturalTimeMixin, RosterMixin, RoomMixin, ScheduleMixin, StorageMixin, SettingsMixin, \
    EmailMixin, PubSubMixin
from utils import html_to_text
from will.abstractions import Event, Message


class WillPlugin(EmailMixin, StorageMixin, NaturalTimeMixin, RoomMixin, RosterMixin,
                 ScheduleMixin, SettingsMixin, PubSubMixin):
    is_will_plugin = True
    request = request

    def __init__(self, *args, **kwargs):
        if "bot" in kwargs:
            self.bot = kwargs["bot"]
            del kwargs["bot"]
        if "message" in kwargs:
            self.message = kwargs["message"]
            del kwargs["message"]

        super(WillPlugin, self).__init__(*args, **kwargs)

    # TODO: pull all the hipchat-specific logic out of this,

    def _rooms_from_message_and_room(self, message, room):
        if room == "ALL_ROOMS":
            rooms = self.available_rooms
        elif room:
            rooms = [self.get_room_from_name_or_id(room), ]
        else:
            if message:
                rooms = [self.get_room_from_message(message), ]
            else:
                rooms = [self.get_room_from_name_or_id(settings.HIPCHAT_DEFAULT_ROOM), ]
        return rooms

    def _prepared_content(self, content, message, kwargs):
        content = re.sub(r'>\s+<', '><', content)
        return content

    def say(self, content, message=None, room=None, card=None, **kwargs):
        # Valid kwargs:
        # color: yellow, red, green, purple, gray, random.  Default is green.
        # html: Display HTML or not. Default is False
        # notify: Ping everyone. Default is False
        logging.info("self.say")
        logging.info(content)

        if not "room" in kwargs and room:
            kwargs["room"] = room

        # TODO: Get this abstracted and working.
        # card: Card see: https://developer.atlassian.com/hipchat/guide/sending-messages
        if not "card" in kwargs and card:
            kwargs["card"] = card

        backend = False
        if not message:
            message = self.message
        logging.info(message)

        if hasattr(message, "backend"):
            # Events, content/type/timestamp
            # {
            #   message: message,
            #   type: "reply/say/topic_change/emoji/etc"
            # }
            backend = message.backend
        else:
            # TODO: need a clear, documented spec for this.
            if hasattr(message, "data") and hasattr(message.data, "backend"):
                logging.info(message.data)
                logging.info(message.data.__dict__)
                backend = message.data.backend
            else:
                backend = settings.DEFAULT_BACKEND

        logging.info("backend: %s" % backend)
        if backend:
            logging.info("putting in queue: %s" % content)
            self.publish("message.outgoing.%s" % backend, Event(
                type="say",
                content=content,
                source_message=message,
                kwargs=kwargs,
            ))

        # content = self._prepared_content(content, message, kwargs)
        # rooms = []
        # if room is not None:
        #     try:
        #         room_id = room["room_id"]
        #     except KeyError:
        #         logging.error(u'"{0}" is not a room object.'.format(room))
        #     else:
        #         self.send_room_message(room_id, content, card=card, **kwargs)
        # elif message is None or message["type"] == "groupchat":
        #     rooms = self._rooms_from_message_and_room(message, room)
        #     for r in rooms:
        #         self.send_room_message(r["room_id"], content, card=card, **kwargs)
        # else:
        #     if "sender" in message:
        #         sender = message["sender"]
        #     else:
        #         sender = message.sender
        #     self.send_direct_message(sender["hipchat_id"], content, **kwargs)

    def reply(self, event, content, **kwargs):
        # Be smart about backend.
        message = event.data

        if hasattr(message, "backend"):
            self.publish("message.outgoing.%s" % message.backend, Event(
                type="reply",
                content=content,
                source_message=message,
                kwargs=kwargs,
            ))

        # # Valid kwargs:
        # # color: yellow, red, green, purple, gray, random.  Default is green.
        # # html: Display HTML or not. Default is False
        # # notify: Ping everyone. Default is False
        # content = self._prepared_content(content, message, kwargs)
        # if message is None or message["type"] == "groupchat":
        #     # Reply, speaking to the room.
        #     try:
        #         content = "@%s %s" % (message.sender["nick"], content)
        #     except TypeError:
        #         content = "%s\nNote: I was told to reply, but this message didn't come from a person!" % (content,)

        #     self.say(content, message=message, **kwargs)

        # elif message['type'] in ('chat', 'normal'):
        #     # Reply to the user (1-1 chat)
        #     if "sender" in message:
        #         sender = message["sender"]
        #     else:
        #         sender = message.sender
        #     self.send_direct_message(sender["hipchat_id"], content, **kwargs)

    def set_topic(self, topic, message=None, room=None):

        if message is None or message["type"] == "groupchat":
            rooms = self._rooms_from_message_and_room(message, room)
            for r in rooms:
                self.set_room_topic(r["room_id"], topic)
        elif message['type'] in ('chat', 'normal'):
            self.send_direct_message(
                message.sender["hipchat_id"],
                "I can't set the topic of a one-to-one chat.  Let's just talk."
            )

    def schedule_say(self, content, when, message=None, room=None, *args, **kwargs):

        content = self._prepared_content(content, message, kwargs)
        if message is None or message["type"] == "groupchat":
            rooms = self._rooms_from_message_and_room(message, room)
            for r in rooms:
                self.add_room_message_to_schedule(when, content, r, *args, **kwargs)
        elif message['type'] in ('chat', 'normal'):
            self.add_direct_message_to_schedule(when, content, message, *args, **kwargs)
