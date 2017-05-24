import json
import logging
import random
import re
import requests
import sys
import time
import traceback

from will import settings
from .base import IOBackend
from will.mixins import RoomMixin, StorageMixin
from will.utils import Bunch
from multiprocessing import Process, Queue
from will.backends.io_adapters.base import Event, Message
from multiprocessing.queues import Empty
from slackclient import SlackClient

SLACK_SEND_URL = "https://slack.com/api/chat.postMessage"


UNSURE_REPLIES = [
    "Hmm.  I'm not sure what to say.",
    "I didn't understand that.",
    "I heard you, but I'm not sure what to do.",
    "Darn.  I'm not sure what that means.  Maybe you can teach me?",
    "I really wish I knew how to do that.",
    "Hm. I understood you, but I'm not sure what to do.",
]
DO_NOT_PICKLE = [
    "api_requester",
    "dnapi_requester",
    "websocket",
    "parse_channel_data",
    "server",
    "send_message",
]


def clean_for_pickling(d):
    cleaned_obj = Bunch()
    if hasattr(d, "items"):
        for k, v in d.items():
            if k not in DO_NOT_PICKLE and "__" not in k:
                cleaned_obj[k] = v
    else:
        for k in dir(d):
            if k not in DO_NOT_PICKLE and "__" not in k:
                cleaned_obj[k] = getattr(d, k)

    return cleaned_obj


class SlackBackend(IOBackend):
    friendly_name = "Slack"
    internal_name = "will.backends.io_adapters.slack"

    def handle_incoming_event(self, event):
        if event["type"] == "message":
            # Sample of group message
            # {u'source_team': u'T5ACF70KV', u'text': u'test',
            # u'ts': u'1495661121.838366', u'user': u'U5ACF70RH',
            # u'team': u'T5ACF70KV', u'type': u'message', u'channel': u'C5JDAR2S3'}

            # Sample of 1-1 message
            # {u'source_team': u'T5ACF70KV', u'text': u'test',
            # u'ts': u'1495662397.335424', u'user': u'U5ACF70RH',
            # u'team': u'T5ACF70KV', u'type': u'message', u'channel': u'D5HGP0YE7'}

            sender = clean_for_pickling(self.client.server.users[event["user"]])
            channel = clean_for_pickling(self.channels[event["channel"]])
            interpolated_handle = "<@%s>" % self.user.id

            is_private_chat = False
            if len(channel.members) == 0:
                is_private_chat = True

            is_direct = False
            # <@U5GUL9D9N> hi
            if is_private_chat or event["text"].startswith(interpolated_handle):
                is_direct = True

            if event["text"].startswith(interpolated_handle):
                event["text"] = event["text"][len(interpolated_handle):].strip()

            print "incoming"
            print event

            m = Message(
                content=event["text"],
                type=event["type"],
                is_direct=is_direct,
                is_private_chat=is_private_chat,
                is_group_chat=not is_private_chat,
                backend=self.name,
                sender=sender,
                channel=channel,
                will_is_mentioned=False,
                will_said_it=False,
                backend_supports_acl=False,
                slack_message=clean_for_pickling(event),
            )

            self.input_queue.put(m)
        else:
            # An event type the shell has no idea how to handle.
            pass

    def handle_outgoing_event(self, event):
        print "handle_outgoing_event"
        print event

        if event.type in ["say", "reply"]:

            if hasattr(event, "source_message") and event.source_message:
                self.send_message(event)
            else:
                # Came from webhook/etc
                kwargs = {}
                if "kwargs" in event:
                    kwargs.update(**event.kwargs)

                if "room" in kwargs:
                    self.send_room_message(
                        kwargs["room"],
                        event.content,
                        **kwargs
                    )
                else:
                    default_room = self.get_room_from_name_or_id(settings.DEFAULT_ROOM)["room_id"]
                    self.send_room_message(
                        default_room,
                        event.content,
                        **kwargs
                    )

        elif event.type == "no_response" and event.source_message.is_direct:
            event.content = random.choice(UNSURE_REPLIES)
            self.send_message(event)

    def send_message(self, event):
        data = {}
        if hasattr(event, "kwargs"):
            data.update(event.kwargs)

        data.update({
            "token": settings.SLACK_API_TOKEN,
            "channel": event.source_message.channel.id,
            "text": event.content,
            "as_user": True,
        })
        print data
        headers = {'Accept': 'text/plain'}
        r = requests.post(
            SLACK_SEND_URL,
            headers=headers,
            data=data,
            **settings.REQUESTS_OPTIONS
        )
        resp_json = r.json()
        print resp_json
        assert resp_json["ok"]


    def __watch_slack_rtm(self):
        if self.client.rtm_connect():

            self.username = self.client.server.username

            self.channels = {}
            for c in self.client.server.channels:
                self.channels[c.id] = c

            self.users = {}
            for k, v in self.client.server.users.items():
                self.users[k] = v
                if v.name == self.username:
                    self.user = v

            while True:
                events = self.client.rtm_read()
                if len(events) > 0:
                    # TODO: only handle events that are new.
                    for e in events:
                        self.handle_incoming_event(e)

                # TODO: update channels/users/username/etc every 10s or so.
                time.sleep(0.5)

    def bootstrap(self):
        self.client = SlackClient(settings.SLACK_API_TOKEN)

        self.rtm_thread = Process(target=self.__watch_slack_rtm)
        self.rtm_thread.start()

    def terminate(self):
        if hasattr(self, "rtm_thread"):
            self.rtm_thread.terminate()
            while self.rtm_thread.is_alive():
                time.sleep(0.2)
