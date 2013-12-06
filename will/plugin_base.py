import json
import requests
import settings
from storage import StorageMixin
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

ROOM_NOTIFICATION_URL = "https://api.hipchat.com/v2/room/%(room_id)s/notification?auth_token=%(token)s"
ROOM_TOPIC_URL = "https://api.hipchat.com/v2/room/%(room_id)s/topic?auth_token=%(token)s"
PRIVATE_MESSAGE_URL = "https://api.hipchat.com/v2/user/%(user_id)s/message?auth_token=%(token)s"
SET_TOPIC_URL = "https://api.hipchat.com/v2/room/%(room_id)s/topic?auth_token=%(token)s"

class WillPlugin(StorageMixin, object):
    is_will_plugin = True

    @property
    def internal_roster(self):
        if not hasattr(self, "_internal_roster"):
            self._internal_roster = self.load('will_roster', {})
        return self._internal_roster

    @property
    def available_rooms(self):
        if not hasattr(self, "_available_rooms"):
            self._available_rooms = self.load('hipchat_rooms', {})
        return self._available_rooms

    def get_room_by_jid(self, jid):
        for name, room in self.available_rooms.items():
            if room["xmpp_jid"] == jid:
                return room
        return None

    def get_user_by_full_name(self, name):
        for jid, info in self.internal_roster.items():
            if info["name"] == name:
                return info
        return None

    def say(self, message, content, **kwargs):
        # Valid kwargs:
        # color: yellow, red, green, purple, gray, random.  Default is green.
        # html: Display HTML or not. Default is False
        # notify: Ping everyone. Default is False
        if message["type"] == "groupchat":
            room = self.get_room_by_jid(message.getMucroom())
            self.send_room_message(room["room_id"], content, **kwargs)
        else:
            if kwargs.get("html", False):
                content = strip_tags(content)

            self.send_direct_message_reply(message, content)
       
    def reply(self, message, content, **kwargs):
        # Valid kwargs:
        # color: yellow, red, green, purple, gray, random.  Default is green.
        # html: Display HTML or not. Default is False
        # notify: Ping everyone. Default is False

        if message["type"] == "groupchat":
            # Reply, speaking to the room.
            sender = self.get_user_by_full_name(message["mucnick"])
            content = "@%s %s" % (sender["nick"], content)

            self.say(message, content, **kwargs)

        elif message['type'] in ('chat', 'normal'):
            # Reply to the user (1-1 chat)

            # 1-1 can't have HTML.
            if kwargs.get("html", False):
                content = strip_tags(content)

            self.send_direct_message_reply(message, content)

    def set_topic(self, message, topic):
        if message["type"] == "groupchat":
            room = self.get_room_by_jid(message.getMucroom())
            self.set_room_topic(room["room_id"], topic)
        elif message['type'] in ('chat', 'normal'):
            self.send_direct_message_reply(message, "I can't set the topic of a one-to-one chat.  Let's just talk.")

    def send_direct_message(self, user_id, message_body):
        # https://www.hipchat.com/docs/apiv2/method/private_message_user
        url = PRIVATE_MESSAGE_URL % {"user_id": user_id, "token": settings.WILL_V2_TOKEN}
        data = {"message": message_body}
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = requests.post(url, headers=headers, data=json.dumps(data))

    def send_direct_message_reply(self, message, message_body):
        message.reply(message_body).send()

    def send_room_message(self, room_id, message_body, html=False, color="green", notify=False, **kwargs):
        if kwargs:
            logger.warn("Unknown keyword args for send_room_message: %s" % kwargs)
        
        format = "text"
        if html:
            format = "html"

        try:
            # https://www.hipchat.com/docs/apiv2/method/send_room_notification
            url = ROOM_NOTIFICATION_URL % {"room_id": room_id, "token": settings.WILL_V2_TOKEN}
            
            data = {
                "message": message_body,
                "message_format": format,
                "color": color,
                "notify": notify,

            }
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            r = requests.post(url, headers=headers, data=json.dumps(data))
        except:
            import traceback; traceback.print_exc();


    def set_room_topic(self, room_id, topic):
        try:
            # https://www.hipchat.com/docs/apiv2/method/send_room_notification
            url = ROOM_TOPIC_URL % {"room_id": room_id, "token": settings.WILL_V2_TOKEN}
            
            data = {
                "topic": topic,
            }
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            r = requests.put(url, headers=headers, data=json.dumps(data))
        except:
            import traceback; traceback.print_exc();
