import re
import logging

from will import settings
from bottle import request
from mixins import NaturalTimeMixin, RoomMixin, ScheduleMixin, StorageMixin, SettingsMixin, \
    EmailMixin, PubSubMixin
from will.backends.io_adapters.hipchat import HipChatRosterMixin
from utils import html_to_text
from will.abstractions import Event, Message


class WillPlugin(EmailMixin, StorageMixin, NaturalTimeMixin, RoomMixin, HipChatRosterMixin,
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

    def say(self, content, message=None, room=None, **kwargs):
        logging.info("self.say")
        logging.info(content)

        if not "room" in kwargs and room:
            kwargs["room"] = room

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

    def reply(self, event, content=None, **kwargs):
        # Be really smart about what we're getting back.
        if (
            (
                (event and hasattr(event, "will_internal_type") and event.will_internal_type == "Message") or
                (event and hasattr(event, "will_internal_type") and event.will_internal_type == "Event")
            ) and type(content) == type("words")
        ):
            # 1.x world - user passed a message and a string.  Keep rolling.
            pass
        elif (
                (
                    (content and hasattr(content, "will_internal_type") and content.will_internal_type == "Message") or
                    (content and hasattr(content, "will_internal_type") and content.will_internal_type == "Event")
                ) and type(event) == type("words")
        ):
            # User passed the string and message object backwards, and we're in a 1.x world
            temp_content = content
            content = event
            event = temp_content
            del temp_content
        elif (
            type(event) == type("words") and
            not content
        ):
            # We're in the Will 2.0 automagic event finding.
            content = event
            event = self.message

        else:
            # Who knows what happened.  Let it blow up.
            pass

        # Be smart about backend.
        message = event.data

        if hasattr(message, "backend"):
            self.publish("message.outgoing.%s" % message.backend, Event(
                type="reply",
                content=content,
                source_message=message,
                kwargs=kwargs,
            ))

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
