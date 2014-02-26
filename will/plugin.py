import re
import requests

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
        if message is None or message["type"] == "groupchat":
            rooms = self._rooms_from_message_and_room(message, room)
            for r in rooms:
                self.send_room_message(r["room_id"], content, **kwargs)
        else:
            self.send_direct_message(message.sender["hipchat_id"], content)
       
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

            self.send_direct_message(message.sender["hipchat_id"], content)

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

    # Sends an email to a list of recipients using the default from email unless the from_email argument is specified
    #
    # from_email - Who the email is from, default to WILL_DEFAULT_FROM_EMAIL
    # email_list - A list of emails to.. email!
    # subject - The subject of the message
    # message - The body of the message to send
    #
    # Example:
    #     r = requests.get(url)
    #
    #     if r.status_code == 500:
    #         self._send_email(
    #             "ERROR! <errors@greenkahuna.com>",
    #             ["helper@scrapbin.com"],
    #             "Website 500 error - %s" % url,
    #             "%s is down!" % url
    #         )
    #
    # Returns nothing
    def send_email(self, from_email=None, email_list=[], subject="", message=""):
        if not hasattr(settings, 'WILL_MAILGUN_API_KEY'):
            raise Exception("Will requires a Mailgun api key in the environment variable WILL_MAILGUN_API_KEY")

        if from_email is None:
            from_email = settings.WILL_DEFAULT_FROM_EMAIL

            if from_email is None:
                raise ValueError("Couldn't send email, from_email was None and there was no WILL_DEFAULT_FROM_EMAIL")

        if email_list is None or len(email_list) == 0:
            raise ValueError("Couldn't send email, email_list was None or empty?!")

        resp = requests.post(
            "https://api.mailgun.net/v2/scrapbin.com/messages",
            auth=("api", settings.WILL_MAILGUN_API_KEY),
            data={
                "from": from_email,
                "to": email_list,
                "subject": "Website 500 error",
                "text": message
            }
        )

        if resp.status_code != 200:
            raise Exception("Could not send email, got a %s response" % resp.status_code)
