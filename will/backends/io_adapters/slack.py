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
from will.mixins import SleepMixin
from multiprocessing import Process
from will.abstractions import Event, Message, Person, Channel
from slackclient import SlackClient

SLACK_SEND_URL = "https://slack.com/api/chat.postMessage"


class SlackMarkdownConverter(MarkdownConverter):

    def convert_strong(self, el, text):
        return '*%s*' % text if text else ''


class SlackBackend(IOBackend, SleepMixin):
    friendly_name = "Slack"
    internal_name = "will.backends.io_adapters.slack"
    required_settings = [
        {
            "name": "SLACK_API_TOKEN",
            "obtain_at": """1. Go to https://api.slack.com/tokens, and sign in.
2. Search for Will, and then add will.
3. Generate a new token (These instructions are incorrect!).""",
        }
    ]

    def normalize_incoming_event(self, event):

        if (
            "type" in event and
            event["type"] == "message" and
            ("subtype" not in event or event["subtype"] != "message_changed") and
            # Ignore thread summary events (for now.)
            # TODO: We should stack these into the history.
            ("subtype" not in event or "thread_ts" not in event["message"])
        ):
            # print("slack: normalize_incoming_event - %s" % event)
            # Sample of group message
            # {u'source_team': u'T5ACF70KV', u'text': u'test',
            # u'ts': u'1495661121.838366', u'user': u'U5ACF70RH',
            # u'team': u'T5ACF70KV', u'type': u'message', u'channel': u'C5JDAR2S3'}

            # Sample of 1-1 message
            # {u'source_team': u'T5ACF70KV', u'text': u'test',
            # u'ts': u'1495662397.335424', u'user': u'U5ACF70RH',
            # u'team': u'T5ACF70KV', u'type': u'message', u'channel': u'D5HGP0YE7'}

            # Threaded message
            # {u'event_ts': u'1507601477.000073', u'ts': u'1507601477.000073',
            # u'subtype': u'message_replied', u'message':
            # {u'thread_ts': u'1507414046.000010', u'text': u'hello!',
            # u'ts': u'1507414046.000010', u'unread_count': 2,
            # u'reply_count': 2, u'user': u'U5GUL9D9N', u'replies':
            # [{u'user': u'U5ACF70RH', u'ts': u'1507601449.000007'}, {
            # u'user': u'U5ACF70RH', u'ts': u'1507601477.000063'}],
            # u'type': u'message', u'bot_id': u'B5HL9ABFE'},
            # u'type': u'message', u'hidden': True, u'channel': u'D5HGP0YE7'}

            sender = self.people[event["user"]]
            channel = clean_for_pickling(self.channels[event["channel"]])
            # print "channel: %s" % channel
            interpolated_handle = "<@%s>" % self.me.id
            real_handle = "@%s" % self.me.handle
            will_is_mentioned = False
            will_said_it = False

            is_private_chat = False

            thread = None
            if "thread_ts" in event:
                thread = event["thread_ts"]

            # If the parent thread is a 1-1 between Will and I, also treat that as direct.
            # Since members[] still comes in on the thread event, we can trust this, even if we're
            # in a thread.
            if len(channel.members.keys()) == 0:
                is_private_chat = True

            # <@U5GUL9D9N> hi
            # TODO: if there's a thread with just will and I on it, treat that as direct.
            is_direct = False
            if is_private_chat or event["text"].startswith(interpolated_handle) or event["text"].startswith(real_handle):
                is_direct = True

            if event["text"].startswith(interpolated_handle):
                event["text"] = event["text"][len(interpolated_handle):].strip()

            if event["text"].startswith(real_handle):
                event["text"] = event["text"][len(real_handle):].strip()

            if interpolated_handle in event["text"] or real_handle in event["text"]:
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
                thread=thread,
                will_is_mentioned=will_is_mentioned,
                will_said_it=will_said_it,
                backend_supports_acl=True,
                original_incoming_event=clean_for_pickling(event),
            )
            return m
        else:
            # An event type the slack ba has no idea how to handle.
            pass

    def handle_outgoing_event(self, event):
        if event.type in ["say", "reply"]:
            if "kwargs" in event and "html" in event.kwargs and event.kwargs["html"]:
                event.content = SlackMarkdownConverter().convert(event.content)

            event.content = event.content.replace("&", "&amp;")
            event.content = event.content.replace("<", "&lt;")
            event.content = event.content.replace(">", "&gt;")
            event.content = event.content.replace("\_", "_")

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
                    default_room = self.get_room_from_name_or_id(settings.HIPCHAT_DEFAULT_ROOM)["room_id"]
                    self.send_room_message(
                        default_room,
                        event.content,
                        **kwargs
                    )

        elif (
            event.type == "message.no_response" and
            event.data.is_direct and
            event.data.will_said_it is False
        ):
            event.content = random.choice(UNSURE_REPLIES)
            self.send_message(event)

    def send_message(self, event):
        data = {}
        if hasattr(event, "kwargs"):
            data.update(event.kwargs)

            # Add slack-specific functionality
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

        # TODO: This is terrifingly ugly.  Yes, it works.  No, I will not have any idea how
        # in a few months.  Abstract this stuff out!
        if "source_message" in event:
            # Mentions that come back via self.say()
            if hasattr(event.source_message, "data"):
                channel_id = event.source_message.data.channel.id
                if hasattr(event.source_message.data, "thread"):
                    data.update({
                        "thread_ts": event.source_message.data.thread
                    })
            else:
                # Mentions that come back via self.say() with a specific room (I think)
                channel_id = event.source_message.channel.id
                if hasattr(event.source_message, "thread"):
                    data.update({
                        "thread_ts": event.source_message.thread
                    })
        else:
            # Mentions that come back via self.reply()
            if hasattr(event.data, "original_incoming_event"):
                if hasattr(event.data.original_incoming_event.channel, "id"):
                    channel_id = event.data.original_incoming_event.channel.id
                else:
                    channel_id = event.data.original_incoming_event.channel
            else:
                if hasattr(event.data["original_incoming_event"].data.channel, "id"):
                    channel_id = event.data["original_incoming_event"].data.channel.id
                else:
                    channel_id = event.data["original_incoming_event"].data.channel

        try:
            data.update({
                "thread_ts": event.data["original_incoming_event"].data.thread
            })
        except:
            pass

        # Auto-link mention names
        if data["text"].find("&lt;@") != -1:
            data["text"] = data["text"].replace("&lt;@", "<@")
            data["text"] = data["text"].replace("&gt;", ">")

        data.update({
            "token": settings.SLACK_API_TOKEN,
            "channel": channel_id,
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
        if not hasattr(self, "client"):
            self.client = SlackClient(settings.SLACK_API_TOKEN)

        self.handle = self.client.server.username

        for k, v in self.client.server.users.items():
            user_timezone = None
            if v.tz:
                user_timezone = v.tz
            people[k] = Person(
                id=v.id,
                mention_handle="<@%s>" % v.id,
                handle=v.name,
                source=clean_for_pickling(v),
                name=v.real_name,
            )
            if v.name == self.handle:
                self.me = Person(
                    id=v.id,
                    mention_handle="<@%s>" % v.id,
                    handle=v.name,
                    source=clean_for_pickling(v),
                    name=v.real_name,
                )
            if user_timezone and user_timezone != 'unknown':
                people[k].timezone = user_timezone
                if v.name == self.handle:
                    self.me.timezone = user_timezone
        self.people = people

    def _update_backend_metadata(self):
        self._update_people()
        self._update_channels()

    def _watch_slack_rtm(self):
        try:
            if self.client.rtm_connect():
                self._update_backend_metadata()

                num_polls_between_updates = 30 / settings.EVENT_LOOP_INTERVAL  # Every 30 seconds
                current_poll_count = 0
                while True:
                    events = self.client.rtm_read()
                    if len(events) > 0:
                        # TODO: only handle events that are new.
                        # print(len(events))
                        for e in events:
                            self.handle_incoming_event(e)

                    # Update channels/people/me/etc every 10s or so.
                    current_poll_count += 1
                    if current_poll_count > num_polls_between_updates:
                        self._update_backend_metadata()
                        current_poll_count = 0

                    self.sleep_for_event_loop()
        except (KeyboardInterrupt, SystemExit):
            pass
        except:
            logging.critical("Error in watching slack RTM: \n%s" % traceback.format_exc())

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
