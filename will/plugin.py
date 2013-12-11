import settings
from bottle import request
from mixins import NaturalTimeMixin, RosterMixin, RoomMixin, ScheduleMixin, HipChatMixin, StorageMixin, SettingsMixin
from utils import html_to_text


class WillPlugin(StorageMixin, NaturalTimeMixin, RoomMixin, RosterMixin, ScheduleMixin, HipChatMixin, SettingsMixin):
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
                rooms = [self.get_room_from_name_or_id(settings.WILL_DEFAULT_ROOM), ]
        return rooms

    def say(self, content, message=None, room=None, **kwargs):
        # Valid kwargs:
        # color: yellow, red, green, purple, gray, random.  Default is green.
        # html: Display HTML or not. Default is False
        # notify: Ping everyone. Default is False

        if message is None or message["type"] == "groupchat":
            rooms = self._rooms_from_message_and_room(message, room)
            for r in rooms:
                self.send_room_message(r["room_id"], content, **kwargs)
        else:
            if kwargs.get("html", False):
                content = html_to_text(content)
            
            sender = self.get_user_from_message(message)
            self.send_direct_message(sender["hipchat_id"], content)
       
    def reply(self, message, content, **kwargs):
        # Valid kwargs:
        # color: yellow, red, green, purple, gray, random.  Default is green.
        # html: Display HTML or not. Default is False
        # notify: Ping everyone. Default is False

        sender = self.get_user_from_message(message)
        if message is None or message["type"] == "groupchat":
            # Reply, speaking to the room.
            content = "@%s %s" % (sender["nick"], content)

            self.say(content, message=message, **kwargs)

        elif message['type'] in ('chat', 'normal'):
            # Reply to the user (1-1 chat)

            # 1-1 can't have HTML.
            if kwargs.get("html", False):
                content = html_to_text(content)

            self.send_direct_message(sender["hipchat_id"], content)

    def set_topic(self, topic, message=None, room=None):

        if message is None or message["type"] == "groupchat":
            rooms = self._rooms_from_message_and_room(message, room)
            for r in rooms:    
                self.set_room_topic(room["room_id"], topic)
        elif message['type'] in ('chat', 'normal'):
            sender = self.get_user_from_message(message)
            self.send_direct_message(sender["hipchat_id"], "I can't set the topic of a one-to-one chat.  Let's just talk.")
   
    def schedule_say(self, content, when, message=None, room=None, *args, **kwargs):
        if message is None or message["type"] == "groupchat":
            rooms = self._rooms_from_message_and_room(message, room)
            for r in rooms:
                self.add_room_message_to_schedule(when, content, r, *args, **kwargs)
        elif message['type'] in ('chat', 'normal'):
            if kwargs.get("html", False):
                content = html_to_text(content)
            self.add_direct_message_to_schedule(when, content, message, *args, **kwargs)


