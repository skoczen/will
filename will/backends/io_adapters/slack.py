import json
import logging
import random
import re
import requests
import sys
import time
import traceback
from websocket import WebSocketConnectionClosedException

from markdownify import MarkdownConverter

from will import settings
from .base import IOBackend
from will.utils import Bunch, UNSURE_REPLIES, clean_for_pickling
from will.mixins import SleepMixin, StorageMixin
from multiprocessing import Process
from will.abstractions import Event, Message, Person, Channel
from slackclient import SlackClient
from slackclient.server import SlackConnectionError

SLACK_SEND_URL = "https://slack.com/api/chat.postMessage"
SLACK_SET_TOPIC_URL = "https://slack.com/api/channels.setTopic"
SLACK_PRIVATE_SET_TOPIC_URL = "https://slack.com/api/groups.setTopic"


class SlackMarkdownConverter(MarkdownConverter):

    def convert_strong(self, el, text):
        return '*%s*' % text if text else ''


class SlackBackend(IOBackend, SleepMixin, StorageMixin):
    friendly_name = "Slack"
    internal_name = "will.backends.io_adapters.slack"
    required_settings = [
        {
            "name": "SLACK_API_TOKEN",
            "obtain_at": """1. Go to https://api.slack.com/custom-integrations/legacy-tokens and sign in as yourself (or a user for Will).
2. Find the workspace you want to use, and click "Create token."
3. Set this token as SLACK_API_TOKEN."""
        }
    ]

    def get_channel_from_name(self, name):
        for k, c in self.channels.items():
            if c.name.lower() == name.lower() or c.id.lower() == name.lower():
                return c
            # We need to check if a user id was passed as a channel
            # and get the correct IM channel if it was.
            elif name.startswith('U') or name.startswith('W'):
                return self.get_im_channel(name)

    def get_im_channel(self, user_id):
        return self.client.api_call("im.open", user=user_id)['channel']['id']

    def normalize_incoming_event(self, event):

        if (
            "type" in event and
            event["type"] == "message" and
            ("subtype" not in event or event["subtype"] != "message_changed") and
            # Ignore thread summary events (for now.)
            # TODO: We should stack these into the history.
            ("subtype" not in event or ("message" in event and "thread_ts" not in event["message"]))
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
            if channel.id == channel.name:
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

    def set_topic(self, event):
        headers = {'Accept': 'text/plain'}
        data = self.set_data_channel_and_thread(event)
        data.update({
            "token": settings.SLACK_API_TOKEN,
            "as_user": True,
            "topic": event.content,
        })
        if data["channel"].startswith("G"):
            url = SLACK_PRIVATE_SET_TOPIC_URL
        else:
            url = SLACK_SET_TOPIC_URL
        r = requests.post(
            url,
            headers=headers,
            data=data,
            **settings.REQUESTS_OPTIONS
        )
        self.handle_request(r, data)

    def handle_outgoing_event(self, event):
        if event.type in ["say", "reply"]:
            if "kwargs" in event and "html" in event.kwargs and event.kwargs["html"]:
                event.content = SlackMarkdownConverter().convert(event.content)

            event.content = event.content.replace("&", "&amp;")
            event.content = event.content.replace("\_", "_")

            kwargs = {}
            if "kwargs" in event:
                kwargs.update(**event.kwargs)

            if hasattr(event, "source_message") and event.source_message and "channel" not in kwargs:
                self.send_message(event)
            else:
                # Came from webhook/etc
                # TODO: finish this.
                target_channel = kwargs.get("room", kwargs.get("channel", None))
                if target_channel:
                    event.channel = self.get_channel_from_name(target_channel)
                    if event.channel:
                        self.send_message(event)
                    else:
                        logging.error(
                            "I was asked to post to the slack %s channel, but it doesn't exist.",
                            target_channel
                        )
                        if self.default_channel:
                            event.channel = self.get_channel_from_name(self.default_channel)
                            event.content = event.content + " (for #%s)" % target_channel
                            self.send_message(event)

                elif self.default_channel:
                    event.channel = self.get_channel_from_name(self.default_channel)
                    self.send_message(event)
                else:
                    logging.critical(
                        "I was asked to post to a slack default channel, but I'm nowhere."
                        "Please invite me somewhere with '/invite @%s'" % (self.me.name if self.me.name else self.me.handle)
                    )

        if event.type in ["topic_change", ]:
            self.set_topic(event)
        elif (
            event.type == "message.no_response" and
            event.data.is_direct and
            event.data.will_said_it is False
        ):
            self.people  # get the object that contains bot's handle
            event.content = random.choice(UNSURE_REPLIES) + " Try `@%s help`" % (self.me.name if self.me.name else self.me.handle)
            self.send_message(event)

    def handle_request(self, r, data):
        resp_json = r.json()
        if not resp_json["ok"]:
            if resp_json["error"] == "not_in_channel":
                channel = self.get_channel_from_name(data["channel"])
                if not hasattr(self, "me") or not hasattr(self.me, "handle"):
                    self.people

                logging.critical(
                    "I was asked to post to the slack %s channel, but I haven't been invited. "
                    "Please invite me with '/invite @%s'" % (channel.name, (self.me.name if self.me.name else self.me.handle))
                )
            else:
                logging.error("Error sending to slack: %s" % resp_json["error"])
                logging.error(resp_json)
                assert resp_json["ok"]

    def set_data_channel_and_thread(self, event, data={}):
        if "channel" in event:
            # We're coming off an explicit set.
            try:
                channel_id = event.channel.id
            # This was a user ID so we will get channel from event.channel
            except AttributeError:
                channel_id = event.channel
        else:
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
                # If we're starting a thread
                if "kwargs" in event and "start_thread" in event.kwargs and event.kwargs["start_thread"] and ("thread_ts" not in data or not data["thread_ts"]):
                    if hasattr(event.source_message, "original_incoming_event"):
                        data.update({
                            "thread_ts": event.source_message.original_incoming_event["ts"]
                        })
                    elif (
                        hasattr(event.source_message, "data") and
                        hasattr(event.source_message.data, "original_incoming_event") and
                        "ts" in event.source_message.data.original_incoming_event
                    ):
                        logging.error(
                            "Hm.  I was told to start a new thread, but while using .say(), instead of .reply().\n"
                            "This doesn't really make sense, but I'm going to make the best of it by pretending you "
                            "used .say() and threading off of your message.\n"
                            "Please update your plugin to use .reply() when you have a second!"
                        )
                        data.update({
                            "thread_ts": event.source_message.data.original_incoming_event["ts"]
                        })
                else:
                    if hasattr(event.data.original_incoming_event, "thread_ts"):
                        data.update({
                            "thread_ts": event.data.original_incoming_event.thread_ts
                        })
                    elif "thread" in event.data.original_incoming_event.data:
                        data.update({
                            "thread_ts": event.data.original_incoming_event.data.thread
                        })
            except:
                logging.info(traceback.format_exc().split(" ")[-1])
                pass
        data.update({
            "channel": channel_id,
        })
        return data

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
            elif "attachments" in event.kwargs:
                data.update({
                    "text": event.content,
                    "attachments": json.dumps(event.kwargs["attachments"])
                })
            else:
                data.update({
                    "text": event.content,
                })
        else:
            data.update({
                "text": event.content,
            })

        data = self.set_data_channel_and_thread(event, data=data)

        # Auto-link mention names
        if "text" in data:
            if data["text"].find("&lt;@") != -1:
                data["text"] = data["text"].replace("&lt;@", "<@")
                data["text"] = data["text"].replace("&gt;", ">")
        elif "attachments" in data and "text" in data["attachments"][0]:
            if data["attachments"][0]["text"].find("&lt;@") != -1:
                data["attachments"][0]["text"] = data["attachments"][0]["text"].replace("&lt;@", "<@")
                data["attachments"][0]["text"] = data["attachments"][0]["text"].replace("&gt;", ">")

        data.update({
            "token": settings.SLACK_API_TOKEN,
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
        self.handle_request(r, data)

    def _map_color(self, color):
        # Turn colors into hex values, handling old slack colors, etc
        if color == "red":
            return "danger"
        elif color == "yellow":
            return "warning"
        elif color == "green":
            return "good"

        return color

    def join_channel(self, channel_id):
        return self.client.api_call(
            "channels.join",
            channel=channel_id,
        )

    @property
    def people(self):
        if not hasattr(self, "_people") or self._people is {}:
            self._update_people()
        return self._people

    @property
    def default_channel(self):
        if not hasattr(self, "_default_channel") or not self._default_channel:
            self._decide_default_channel()
        return self._default_channel

    @property
    def channels(self):
        if not hasattr(self, "_channels") or self._channels is {}:
            self._update_channels()
        return self._channels

    @property
    def client(self):
        if not hasattr(self, "_client"):
            self._client = SlackClient(settings.SLACK_API_TOKEN)
        return self._client

    def _decide_default_channel(self):
        self._default_channel = None
        if not hasattr(self, "complained_about_default"):
            self.complained_about_default = False
            self.complained_uninvited = False

        # Set self.me
        self.people

        if hasattr(settings, "SLACK_DEFAULT_CHANNEL"):
            channel = self.get_channel_from_name(settings.SLACK_DEFAULT_CHANNEL)
            if channel:
                if self.me.id in channel.members:
                    self._default_channel = channel.id
                    return
            elif not self.complained_about_default:
                self.complained_about_default = True
                logging.error("The defined default channel(%s) does not exist!",
                              settings.SLACK_DEFAULT_CHANNEL)

        for c in self.channels.values():
            if c.name != c.id and self.me.id in c.members:
                self._default_channel = c.id
        if not self._default_channel and not self.complained_uninvited:
            self.complained_uninvited = True
            logging.critical("No channels with me invited! No messages will be sent!")

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
        if len(channels.keys()) == 0:
            # Server isn't set up yet, and we're likely in a processing thread,
            if self.load("slack_channel_cache", None):
                self._channels = self.load("slack_channel_cache", None)
        else:
            self._channels = channels
            self.save("slack_channel_cache", channels)

    def _update_people(self):
        people = {}

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
        if len(people.keys()) == 0:
            # Server isn't set up yet, and we're likely in a processing thread,
            if self.load("slack_people_cache", None):
                self._people = self.load("slack_people_cache", None)
            if not hasattr(self, "me") or not self.me:
                self.me = self.load("slack_me_cache", None)
            if not hasattr(self, "handle") or not self.handle:
                self.handle = self.load("slack_handle_cache", None)
        else:
            self._people = people
            self.save("slack_people_cache", people)
            self.save("slack_me_cache", self.me)
            self.save("slack_handle_cache", self.handle)

    def _update_backend_metadata(self):
        self._update_people()
        self._update_channels()

    def _watch_slack_rtm(self):
        while True:
            try:
                if self.client.rtm_connect(auto_reconnect=True):
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
            except (WebSocketConnectionClosedException, SlackConnectionError):
                logging.error('Encountered connection error attempting reconnect in 2 seconds')
                time.sleep(2)
            except (KeyboardInterrupt, SystemExit):
                break
            except:
                logging.critical("Error in watching slack RTM: \n%s" % traceback.format_exc())
                break

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

        # Property, auto-inits.
        self.client

        self.rtm_thread = Process(target=self._watch_slack_rtm)
        self.rtm_thread.start()

    def terminate(self):
        if hasattr(self, "rtm_thread"):
            self.rtm_thread.terminate()
            while self.rtm_thread.is_alive():
                time.sleep(0.2)
