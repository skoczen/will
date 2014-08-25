import re
import logging
import requests

import settings
from bottle import request
from mixins import NaturalTimeMixin, RosterMixin, RoomMixin, ScheduleMixin, HipChatMixin, StorageMixin, SettingsMixin, \
    EmailMixin
from utils import html_to_text


class WillPlugin(EmailMixin, StorageMixin, NaturalTimeMixin, RoomMixin, RosterMixin, ScheduleMixin, HipChatMixin, SettingsMixin):
    is_will_plugin = True
    request = request

    def _rooms_from_message_and_room(self, message, room):
        if room == "ALL_ROOMS":
            rooms = self.available_rooms
        elif room:
            rooms = [self.get_room_from_name_or_id(room),]
        else:
            if message:
                rooms = [self.get_room_from_message(message),]
            else:
                rooms = [self.get_room_from_name_or_id(settings.DEFAULT_ROOM), ]
        return rooms

    def _prepared_content(self, content, message, kwargs):
        if kwargs is None:
            kwargs = {}

        if kwargs.get("html", False) and (message and message['type'] in ('chat', 'normal')):
            # 1-1 can't have HTML.
            content = html_to_text(content)
        elif kwargs.get("html", True):
            # Hipchat is weird about spaces between tags.
            content = re.sub(r'>\s+<', '><', content)
        return content


    def say(self, content, message=None, room=None, **kwargs):
        # Valid kwargs:
        # color: yellow, red, green, purple, gray, random.  Default is green.
        # html: Display HTML or not. Default is False
        # notify: Ping everyone. Default is False

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
            self.send_direct_message(message.sender["hipchat_id"], content, **kwargs)
       
    def reply(self, message, content, **kwargs):
        # Valid kwargs:
        # color: yellow, red, green, purple, gray, random.  Default is green.
        # html: Display HTML or not. Default is False
        # notify: Ping everyone. Default is False

        content = self._prepared_content(content, message, kwargs)
        if message is None or message["type"] == "groupchat":
            # Reply, speaking to the room.
            content = "@%s %s" % (message.sender["nick"], content)

            self.say(content, message=message, **kwargs)

        elif message['type'] in ('chat', 'normal'):
            # Reply to the user (1-1 chat)

            self.send_direct_message(message.sender["hipchat_id"], content, **kwargs)

    def set_topic(self, topic, message=None, room=None):

        if message is None or message["type"] == "groupchat":
            rooms = self._rooms_from_message_and_room(message, room)
            for r in rooms:    
                self.set_room_topic(r["room_id"], topic)
        elif message['type'] in ('chat', 'normal'):
            self.send_direct_message(message.sender["hipchat_id"], "I can't set the topic of a one-to-one chat.  Let's just talk.")
   
    def schedule_say(self, content, when, message=None, room=None, *args, **kwargs):

        content = self._prepared_content(content, message, kwargs)
        if message is None or message["type"] == "groupchat":
            rooms = self._rooms_from_message_and_room(message, room)
            for r in rooms:
                self.add_room_message_to_schedule(when, content, r, *args, **kwargs)
        elif message['type'] in ('chat', 'normal'):
            self.add_direct_message_to_schedule(when, content, message, *args, **kwargs)
