import json
import logging
import random
import re
import requests
import sys
import time
import traceback

from markdownify import MarkdownConverter

from will import settings
from .base import IOBackend
from will.utils import Bunch, UNSURE_REPLIES, clean_for_pickling
from multiprocessing import Process, Queue
from will.abstractions import Event, Message, Person, Channel
from multiprocessing.queues import Empty
from slackclient import SlackClient

SLACK_SEND_URL = "https://slack.com/api/chat.postMessage"


class SlackMarkdownConverter(MarkdownConverter):

    def convert_strong(self, el, text):
        return '*%s*' % text if text else ''


class SlackBackend(IOBackend):
    friendly_name = "Slack"
    internal_name = "will.backends.io_adapters.slack"

    def normalize_incoming_event(self, event):

        if (
            event["type"] == "message" and
            ("subtype" not in event or event["subtype"] != "message_changed")
        ):
            print "slack: normalize_incoming_event - %s" % event
            # Sample of group message
            # {u'source_team': u'T5ACF70KV', u'text': u'test',
            # u'ts': u'1495661121.838366', u'user': u'U5ACF70RH',
            # u'team': u'T5ACF70KV', u'type': u'message', u'channel': u'C5JDAR2S3'}

            # Sample of 1-1 message
            # {u'source_team': u'T5ACF70KV', u'text': u'test',
            # u'ts': u'1495662397.335424', u'user': u'U5ACF70RH',
            # u'team': u'T5ACF70KV', u'type': u'message', u'channel': u'D5HGP0YE7'}

            sender = self.people[event["user"]]
            channel = clean_for_pickling(self.channels[event["channel"]])
            interpolated_handle = "<@%s>" % self.me.id
            will_is_mentioned = False
            will_said_it = False

            is_private_chat = False

            if len(channel.members.keys()) == 0:
                is_private_chat = True

            # <@U5GUL9D9N> hi
            is_direct = False
            if is_private_chat or event["text"].startswith(interpolated_handle):
                is_direct = True

            if event["text"].startswith(interpolated_handle):
                event["text"] = event["text"][len(interpolated_handle):].strip()

            if interpolated_handle in event["text"]:
                will_is_mentioned = True

            if event["user"] == self.me.id:
                will_said_it = True

            m = Message(
                content=event["text"],
                type=event["type"],
                is_direct=is_direct,
                is_private_chat=is_private_chat,
                is_group_chat=not is_private_chat,
                backend=self.internal_name,
                sender=sender,
                channel=channel,
                will_is_mentioned=will_is_mentioned,
                will_said_it=will_said_it,
                backend_supports_acl=True,
                source=clean_for_pickling(event),
            )
            return m
            # self.input_queue.put(m)
        else:
            # An event type the slack ba has no idea how to handle.
            pass

    def handle_outgoing_event(self, event):
        # print "handle_outgoing_event"
        # print event

        if event.type in ["say", "reply"]:
            if "kwargs" in event and "html" in event.kwargs and event.kwargs["html"]:
                event.content = SlackMarkdownConverter().convert(event.content)

            event.content = event.content.replace("&", "&amp;")
            event.content = event.content.replace("<", "&lt;")
            event.content = event.content.replace(">", "&gt;")

            if hasattr(event, "source_message") and event.source_message:
                self.send_message(event)
            else:
                # Came from webhook/etc
                # TODO: finish this.
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

        elif (
            event.type == "no_response" and
            event.source_message.is_direct and
            event.source_message.will_said_it is False
        ):
            event.content = random.choice(UNSURE_REPLIES)
            self.send_message(event)

    def send_message(self, event):
        data = {}
        if hasattr(event, "kwargs"):
            data.update(event.kwargs)

            if "color" in event.kwargs:

                data.update({
                    "attachments": json.dumps([
                        {
                            "fallback": event.content,
                            "color": self._map_color(event.kwargs["color"]),
                            "text": event.content,
                        }
                    ]),
                })
            else:
                data.update({
                    "text": event.content,
                })
        else:
            data.update({
                "text": event.content,
            })

        data.update({
            "token": settings.SLACK_API_TOKEN,
            "channel": event.source_message.channel.id,
            "as_user": True,
        })
        if hasattr(event, "kwargs") and "html" in event.kwargs and event.kwargs["html"]:
            data.update({
                "parse": "full",
            })

        headers = {'Accept': 'text/plain'}
        r = requests.post(
            SLACK_SEND_URL,
            headers=headers,
            data=data,
            **settings.REQUESTS_OPTIONS
        )
        resp_json = r.json()
        if not resp_json["ok"]:
            print resp_json
            assert resp_json["ok"]

    def _map_color(self, color):
        # Turn colors into hex values, handling old slack colors, etc
        if color == "red":
            return "danger"
        elif color == "yellow":
            return "warning"
        elif color == "green":
            return "good"

        return color

    def _update_channels(self):
        channels = {}
        for c in self.client.server.channels:
            members = {}
            for m in c.members:
                members[m] = self.people[m]

            channels[c.id] = Channel(
                id=c.id,
                name=c.name,
                source=clean_for_pickling(c),
                members=members
            )
        self.channels = channels

    def _update_people(self):
        people = {}

        self.handle = self.client.server.username

        for k, v in self.client.server.users.items():
            user_timezone = None
            if v.tz:
                user_timezone = v.tz
            people[k] = Person(
                id=v.id,
                handle=v.name,
                source=clean_for_pickling(v),
                name=v.real_name,
                timezone=user_timezone,
            )
            if v.name == self.handle:
                self.me = Person(
                    id=v.id,
                    handle=v.name,
                    source=clean_for_pickling(v),
                    name=v.real_name,
                    timezone=user_timezone,
                )
        self.people = people

    def _update_backend_metadata(self):
        self._update_people()
        self._update_channels()

    def _watch_slack_rtm(self):
        if self.client.rtm_connect():
            self._update_backend_metadata()

            num_polls_between_updates = 20
            current_poll_count = 0
            while True:
                events = self.client.rtm_read()
                if len(events) > 0:
                    # TODO: only handle events that are new.
                    print len(events)
                    for e in events:
                        self.handle_incoming_event(e)

                # Update channels/people/me/etc every 10s or so.
                current_poll_count += 1
                if current_poll_count < num_polls_between_updates:
                    self._update_backend_metadata()
                    current_poll_count = 0

                time.sleep(0.5)

    def bootstrap(self):
        # Bootstrap must provide a way to to have:
        # a) self.normalize_incoming_event fired, or incoming events put into self.incoming_queue
        # b) any necessary threads running for a)
        # c) self.me (Person) defined, with Will's info
        # d) self.people (dict of People) defined, with everyone in an organization/backend
        # e) self.channels (dict of Channels) defined, with all available channels/rooms.
        #    Note that Channel asks for members, a list of People.
        # f) A way for self.handle, self.me, self.people, and self.channels to be kept accurate,
        #    with a maximum lag of 60 seconds.
        self.client = SlackClient(settings.SLACK_API_TOKEN)

        self.rtm_thread = Process(target=self._watch_slack_rtm)
        self.rtm_thread.start()

    def terminate(self):
        if hasattr(self, "rtm_thread"):
            self.rtm_thread.terminate()
            while self.rtm_thread.is_alive():
                time.sleep(0.2)
