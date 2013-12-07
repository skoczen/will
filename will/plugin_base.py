import logging
import settings
from storage import StorageMixin
from mixins import NaturalTimeMixin, RosterMixin, RoomMixin, ScheduleMixin, HipChatAPIMixin
from HTMLParser import HTMLParser

# To strip tags.
# Via http://stackoverflow.com/a/925630
class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


class WillPlugin(StorageMixin, NaturalTimeMixin, RoomMixin, RosterMixin, ScheduleMixin, HipChatAPIMixin):
    is_will_plugin = True

    def _rooms_from_message_and_room(self, message, room):
        if room == "ALL_ROOMS":
            rooms = self.available_rooms
        elif room:
            rooms = [room,]
        else:
            if message:
                rooms = [self.get_room_from_message(message),]
            else:
                rooms = self.available_rooms
        return rooms

    def say(self, message, content, room=None, **kwargs):
        # Valid kwargs:
        # color: yellow, red, green, purple, gray, random.  Default is green.
        # html: Display HTML or not. Default is False
        # notify: Ping everyone. Default is False

        if message["type"] == "groupchat":
            rooms = self._rooms_from_message_and_room(message, room)
            for r in rooms:
                self.send_room_message(r["room_id"], content, **kwargs)
        else:
            if kwargs.get("html", False):
                content = strip_tags(content)
            
            sender = self.get_user_from_message(message)
            self.send_direct_message(sender["hipchat_id"], content)
       
    def reply(self, message, content, **kwargs):
        # Valid kwargs:
        # color: yellow, red, green, purple, gray, random.  Default is green.
        # html: Display HTML or not. Default is False
        # notify: Ping everyone. Default is False

        sender = self.get_user_from_message(message)
        if message["type"] == "groupchat":
            # Reply, speaking to the room.
            content = "@%s %s" % (sender["nick"], content)

            self.say(message, content, **kwargs)

        elif message['type'] in ('chat', 'normal'):
            # Reply to the user (1-1 chat)

            # 1-1 can't have HTML.
            if kwargs.get("html", False):
                content = strip_tags(content)

            self.send_direct_message(sender["hipchat_id"], content)

    def set_topic(self, message, topic):
        if message["type"] == "groupchat":
            room = self.get_room_from_message(message)
            self.set_room_topic(room["room_id"], topic)
        elif message['type'] in ('chat', 'normal'):
            sender = self.get_user_from_message(message)
            self.send_direct_message(sender["hipchat_id"], "I can't set the topic of a one-to-one chat.  Let's just talk.")
   
    def schedule_say(self, message, content, when, *args, **kwargs):
        if message["type"] == "groupchat":
            rooms = self._rooms_from_message_and_room(message, None)
            for r in rooms:
                self.add_room_message_to_schedule(when, content, r, *args, **kwargs)
        elif message['type'] in ('chat', 'normal'):
            if kwargs.get("html", False):
                content = strip_tags(content)
            self.add_direct_message_to_schedule(when, content, message, *args, **kwargs)
        
