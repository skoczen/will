import re
import logging

from bottle import request

from will import settings
from will.abstractions import Event, Message
# Backwards compatability with 1.x, eventually to be deprecated.
from will.backends.io_adapters.hipchat import HipChatRosterMixin, HipChatRoomMixin
from will.mixins import NaturalTimeMixin, ScheduleMixin, StorageMixin, SettingsMixin, \
    EmailMixin, PubSubMixin
from will.utils import html_to_text


class WillPlugin(EmailMixin, StorageMixin, NaturalTimeMixin, HipChatRoomMixin, HipChatRosterMixin,
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

    def _prepared_content(self, content, message, kwargs):
        content = re.sub(r'>\s+<', '><', content)
        return content

    def _trim_for_execution(self, message):
        # Trim it down
        if hasattr(message, "analysis"):
            message.analysis = None
        if hasattr(message, "source_message") and hasattr(message.source_message, "analysis"):
            message.source_message.analysis = None
        return message

    def get_backend(self, message, service=None):
        backend = False
        if service:
            for b in settings.IO_BACKENDS:
                if service in b:
                    return b

        if hasattr(message, "backend"):
            backend = message.backend
        elif message and hasattr(message, "data") and hasattr(message.data, "backend"):
            backend = message.data.backend
        else:
            backend = settings.DEFAULT_BACKEND
        return backend

    def get_message(self, message_passed):
        if not message_passed and hasattr(self, "message"):
            return self.message
        return message_passed

    def say(self, content, message=None, room=None, channel=None, service=None, package_for_scheduling=False, **kwargs):
        logging.info("self.say")
        logging.info(content)
        if channel:
            room = channel
        elif room:
            channel = room

        if not "channel" in kwargs and channel:
            kwargs["channel"] = channel

        message = self.get_message(message)
        message = self._trim_for_execution(message)
        backend = self.get_backend(message, service=service)

        if backend:
            e = Event(
                type="say",
                content=content,
                source_message=message,
                kwargs=kwargs,
            )
            if package_for_scheduling:
                return "message.outgoing.%s" % backend, e
            else:
                logging.info("putting in queue: %s" % content)
                self.publish("message.outgoing.%s" % backend, e)

    def reply(self, event, content=None, message=None, package_for_scheduling=False, **kwargs):
        message = self.get_message(message)

        if "channel" in kwargs:
            logging.error(
                "I was just asked to talk to %(channel)s, but I can't use channel using .reply() - "
                "it's just for replying to the person who talked to me.  Please use .say() instead." % kwargs
            )
            return
        if "service" in kwargs:
            logging.error(
                "I was just asked to talk to %(service)s, but I can't use a service using .reply() - "
                "it's just for replying to the person who talked to me.  Please use .say() instead." % kwargs
            )
            return
        if "room" in kwargs:
            logging.error(
                "I was just asked to talk to %(room)s, but I can't use room using .reply() - "
                "it's just for replying to the person who talked to me.  Please use .say() instead." % kwargs
            )
            return

        # Be really smart about what we're getting back.
        if (
            (
                (event and hasattr(event, "will_internal_type") and event.will_internal_type == "Message") or
                (event and hasattr(event, "will_internal_type") and event.will_internal_type == "Event")
            ) and type(content) == type("words")
        ):
            # "1.x world - user passed a message and a string.  Keep rolling."
            pass
        elif (
                (
                    (content and hasattr(content, "will_internal_type") and content.will_internal_type == "Message") or
                    (content and hasattr(content, "will_internal_type") and content.will_internal_type == "Event")
                ) and type(event) == type("words")
        ):
            # "User passed the string and message object backwards, and we're in a 1.x world"
            temp_content = content
            content = event
            event = temp_content
            del temp_content
        elif (
            type(event) == type("words") and
            not content
        ):
            # "We're in the Will 2.0 automagic event finding."
            content = event
            event = self.message

        else:
            # "No magic needed."
            pass

        # Be smart about backend.
        if hasattr(event, "data"):
            message = event.data
        elif hasattr(self, "message") and hasattr(self.message, "data"):
            message = self.message.data

        backend = self.get_backend(message)
        if backend:
            e = Event(
                type="reply",
                content=content,
                topic="message.outgoing.%s" % backend,
                source_message=message,
                kwargs=kwargs,
            )
            if package_for_scheduling:
                return e
            else:
                self.publish("message.outgoing.%s" % backend, e)

    def set_topic(self, topic, message=None, room=None, channel=None, service=None, **kwargs):
        if channel:
            room = channel
        elif room:
            channel = room

        message = self.get_message(message)
        message = self._trim_for_execution(message)
        backend = self.get_backend(message, service=service)
        e = Event(
            type="topic_change",
            content=topic,
            topic="message.outgoing.%s" % backend,
            source_message=message,
            kwargs=kwargs,
        )
        self.publish("message.outgoing.%s" % backend, e)

    def schedule_say(self, content, when, message=None, room=None, channel=None, service=None, *args, **kwargs):
        if channel:
            room = channel
        elif room:
            channel = room

        if "content" in kwargs:
            if content:
                del kwargs["content"]
            else:
                content = kwargs["content"]

        topic, packaged_event = self.say(
            content, message=message, channel=channel,
            service=service, package_for_scheduling=True, *args, **kwargs
        )
        self.add_outgoing_event_to_schedule(when, {
            "type": "message",
            "topic": topic,
            "event": packaged_event,
        })
