import re
import logging

import settings
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
                rooms = [self.get_room_from_name_or_id(settings.DEFAULT_ROOM), ]
        return rooms

    def say(self, content, message=None, room=None, **kwargs):
        # Valid kwargs:
        # color: yellow, red, green, purple, gray, random.  Default is green.
        # html: Display HTML or not. Default is False
        # notify: Ping everyone. Default is False
        if not "room" in kwargs and room:
            kwargs["room"] = room

        backend = False
        if hasattr(message, "backend"):
            # Events, content/type/timestamp
            # {
            #   message: message,
            #   type: "reply/say/topic_change/emoji/etc"
            # }
            backend = message.backend
        else:
            backend = settings.DEFAULT_BACKEND

        if backend:
            self.bot.queues.io.output[backend].put(Event(
                type="say",
                content=content,
                source_message=message,
                kwargs=kwargs,
            ))

        return

        content = self._prepared_content(content, message, kwargs)
        rooms = []
        if room is not None:
            try:
                room_id = room["room_id"]
            except KeyError:
                logging.error(u'"{0}" is not a room object.'.format(room))
            else:
                self.send_room_message(room_id, content, **kwargs)
        elif message is None or message["type"] == "groupchat":
            rooms = self._rooms_from_message_and_room(message, room)
            for r in rooms:
                self.send_room_message(r["room_id"], content, **kwargs)
        else:
            if "sender" in message:
                sender = message["sender"]
            else:
                sender = message.sender
            self.send_direct_message(sender["hipchat_id"], content, **kwargs)

    def reply(self, event, content, **kwargs):
        # Be smart about backend.
        message = event.data

        if hasattr(message, "backend"):
            # print "self.bot"
            # print self.bot.queues.io.output
            self.publish("message.outgoing.%s" % message.backend, Event(
                type="reply",
                content=content,
                source_message=message,
                kwargs=kwargs,
            ))
            # self.bot.queues.io.output[message.backend].put(Event(
            #     type="reply",
            #     content=content,
            #     source_message=message,
            #     kwargs=kwargs,
            # ))

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
