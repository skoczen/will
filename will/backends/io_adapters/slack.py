"""Slack adapter for willbot
"""
# pylint: disable=no-member
import json
import logging
import random
import sys
import time
import traceback
import urllib
from multiprocessing import Process
from threading import Thread
from typing import Dict, Optional

import slack_sdk
from markdownify import MarkdownConverter
from slack_sdk.rtm import RTMClient

from will import settings
from will.abstractions import Channel, Event, Message, Person
from will.mixins import SleepMixin, StorageMixin
from will.utils import UNSURE_REPLIES, clean_for_pickling

from .base import IOBackend

# https://api.slack.com/docs/rate-limits says the actual max is 16k, but that includes the entire POST content, and
# warns about multibyte characters.  Turns out the API will disconnect you if there are more than 4031 characters
# in the message.  Documentation is hard.
MAX_MESSAGE_SIZE = 4031


class SlackMarkdownConverter(MarkdownConverter):
    "Extended Markdown converter"

    def convert_strong(self, _, text):  # pylint: disable=no-self-use
        "Normal markup is incorrect for Slack"
        return "*%s*" % text if text else ""

    def convert_a(self, el, text):
        "dress up <a> links for Slack"
        href = el.get("href")
        title = el.get("title")
        if self.options["autolinks"] and text == href and not title:
            # Shortcut syntax
            return "<%s>" % href
        title_part = ' "%s"' % title.replace('"', r"\"") if title else ""
        return "<%s%s|%s>" % (href, title_part, text or "") if href else text or ""


class SlackBackend(
    IOBackend, SleepMixin, StorageMixin
):  # pylint: disable=too-many-instance-attributes
    "Adapter that lets Will talk to Slack"
    friendly_name = "Slack"
    internal_name = "will.backends.io_adapters.slack"
    required_settings = [
        {
            "name": "SLACK_API_TOKEN",
            "obtain_at": "1. Go to https://api.slack.com/apps?new_classic_app=1"
            " and Configure your app.\n"
            '2. Install app in your workspace.\n'
            "3. Set Bot User OAuth Token (beginning with xoxb) as SLACK_API_TOKEN.",
        }
    ]
    PAGE_LIMIT = 1000
    _channels: Dict[str, Channel] = dict()
    _people: Dict[str, Person] = dict()
    _default_channel = None
    rtm_thread: Optional[RTMClient] = None
    complained_about_default = False
    complained_uninvited = False
    _client = None
    me = None
    handle = None

    def get_channel_from_name(self, name):
        "Decodes human-readable name into the Slack channel name"
        for c in self.channels.values():
            if c.name.lower() == name.lower() or c.id.lower() == name.lower():
                return c
            # We need to check if a user id was passed as a channel
            # and get the correct IM channel if it was.
            elif name.startswith('U') or name.startswith('W'):
                return self.open_direct_message(name)
        webclient = self.client._web_client  # pylint: disable=protected-access
        try:
            channel_info = webclient.conversations_info(channel=name)["channel"]
        except slack_sdk.errors.SlackApiError:
            logging.warning('Error looking up Slack channel %s', name)
            return None
        channel_members = webclient.conversations_members(channel=name)
        now = time.time()
        members = {
            x: self.people[x]
            for x in channel_members.get("members", list())
            if x in self.people
        }
        logging.debug("took %0.2f seconds to scan people data", time.time() - now)
        return Channel(
            name=channel_info.get("name", name),
            id=channel_info["id"],
            members=members,
            source=name,
            is_channel=False,
            is_group=False,
            is_im=channel_info["is_im"],
            is_private=True,
        )

    def get_channel_name_from_id(self, name):
        for k, c in self.channels.items():
            if c.name.lower() == name.lower() or c.id.lower() == name.lower():
                return c.name

    @staticmethod
    def is_allowed_channel(channel):
        if hasattr(settings, "SLACK_ROOMS"):
            if channel.lower() in settings.SLACK_ROOMS:
                return True
            else:
                logging.warning('Will has been added to {0} but it should not be here!'.format(channel))
                return False
        else:
            return True

    def normalize_incoming_event(self, event):
        "Makes a Slack event look like all the other events we handle"
        event_type = event.get("type")
        event_subtype = event.get("subtype")
        logging.debug("event type: %s, subtype: %s", event_type, event_subtype)
        if (
            (
                event_subtype is None
                and event_type not in ["message_changed", "message.incoming"]
            )
            # Ignore thread summary events (for now.)
            and (
                event_subtype is None
                or ("message" in event and "thread_ts" not in event["message"])
            )
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
            logging.debug("we like that event!")
            if event_subtype == "bot_message":
                sender = Person(
                    id=event["bot_id"],
                    mention_handle="<@%s>" % event["bot_id"],
                    handle=event["username"],
                    source=event,
                    name=event["username"],
                )
            else:
                sender = self.people[event["user"]]
            try:
                channel = self.get_channel_from_name(event["channel"])
            except KeyError:
                self._update_channels()
                channel = self.get_channel_from_name(event["channel"])
            is_private_chat = getattr(channel, "is_private", False)
            is_direct = getattr(getattr(channel, "source", None), 'is_im', False)
            channel = clean_for_pickling(channel)
            # print "channel: %s" % channel
            interpolated_handle = "<@%s>" % self.me.id
            real_handle = "@%s" % self.me.handle
            will_is_mentioned = False
            will_said_it = False

            thread = None
            if "thread_ts" in event:
                thread = event["thread_ts"]

            if interpolated_handle in event["text"] or real_handle in event["text"]:
                will_is_mentioned = True

            if event["text"].startswith(interpolated_handle):
                event["text"] = event["text"][len(interpolated_handle):]

            if event["text"].startswith(real_handle):
                event["text"] = event["text"][len(real_handle):]

            # sometimes autocomplete adds a : to the usename, but it's certainly extraneous.
            if will_is_mentioned and event["text"][0] == ":":
                event["text"] = event["text"][1:]

            if event.get("user") == self.me.id:
                will_said_it = True

            m = Message(
                content=event["text"].strip(),
                type=event_type,
                is_direct=is_direct or will_is_mentioned,
                is_private_chat=is_private_chat,
                is_group_chat=not (is_private_chat or is_direct),
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
        # An event type the slack ba has no idea how to handle.
        return None

    def set_topic(self, event):
        """Sets the channel topic.  This doesn't actually work anymore since Slack has removed that ability from bots.
        Leaving the code here in case they re-enable it."""
        data = self.set_data_channel_and_thread(event)
        self.client._web_client.api_call(  # pylint: disable=protected-access
            "conversations.setTopic",
            topic=event.content,
            channel=data["channel"],
        )

    def send_file(self, event):
        'Sometimes you need to upload an image or file'

        try:
            logging.info('EVENT: %s', str(event))
            data = {}
            if hasattr(event, "kwargs"):
                data.update(event.kwargs)

            data.update({
                'filename': event.filename,
                'filetype': event.filetype
            })
            self.set_data_channel_and_thread(event, data)
            # This is just *silly*
            if 'thread_ts' in data:
                del data['thread_ts']
            data['channels'] = data['channel']
            del data['channel']

            logging.debug('calling files_uploads with: %s', data)
            result = self.client._web_client.api_call(  # pylint: disable=protected-access
                'files.upload', files={'file': event.file}, params=data)
            logging.debug('send_file result: %s', result)
        except Exception:
            logging.exception("Error in send_file handling %s", event)

    def handle_outgoing_event(self, event, retry=5):
        "Process an outgoing event"
        try:
            if event.type in ["say", "reply"]:
                if "kwargs" in event and "html" in event.kwargs and event.kwargs["html"]:
                    event.content = SlackMarkdownConverter().convert(event.content)

                event.content = event.content.replace("&", "&amp;")
                event.content = event.content.replace(r"\_", "_")

                kwargs = {}
                if "kwargs" in event:
                    kwargs.update(**event.kwargs)

                if kwargs.get('update', None) is not None:
                    self.update_message(event)
                elif (
                    hasattr(event, "source_message")
                    and event.source_message
                    and "channel" not in kwargs
                ):
                    self.send_message(event)
                else:
                    # Came from webhook/etc
                    target_channel = kwargs.get("room", kwargs.get("channel", None))
                    if target_channel:
                        event.channel = self.get_channel_from_name(target_channel)
                        if event.channel:
                            self.send_message(event)
                        else:
                            logging.error(
                                "I was asked to post to the slack %s channel, but it doesn't exist.",
                                target_channel,
                            )
                            if self.default_channel:
                                event.channel = self.get_channel_from_name(
                                    self.default_channel
                                )
                                event.content = (
                                    event.content + " (for #%s)" % target_channel
                                )
                                self.send_message(event)

                    elif self.default_channel:
                        event.channel = self.get_channel_from_name(self.default_channel)
                        self.send_message(event)
                    else:
                        logging.critical(
                            "I was asked to post to a slack default channel, but I'm nowhere."
                            "Please invite me somewhere with '/invite @%s'",
                            self.me.handle,
                        )

            elif event.type in [
                "topic_change",
            ]:
                self.set_topic(event)
            elif event.type in [
                "file.upload",
            ]:
                self.send_file(event)
            elif (
                event.type == "message.no_response"
                and event.data.is_direct
                and event.data.will_said_it is False
            ):
                event.content = random.choice(UNSURE_REPLIES)
                self.send_message(event)
        except (urllib.error.URLError, Exception):  # websocket got closed, no idea
            if retry < 1:
                sys.exit()
            del self._client
            time.sleep(5)  # pause 5 seconds just because
            self.client
            self.handle_outgoing_event(event, retry=retry-1)

    @staticmethod
    def set_data_channel_and_thread(event, data=None):
        "Update data with the channel/thread information from event"
        if event.type == "file.upload":
            # We already know what to do when it's a file DM
            if event.kwargs.get("is_direct") is True:
                return
        if data is None:
            data = dict()
        if "channel" in event:
            # We're coming off an explicit set.
            channel_id = event.channel.id
        else:
            if "source_message" in event:
                # Mentions that come back via self.say()
                if hasattr(event.source_message, "data"):
                    channel_id = event.source_message.data.channel.id
                    if hasattr(event.source_message.data, "thread"):
                        data.update({"thread_ts": event.source_message.data.thread})
                else:
                    # Mentions that come back via self.say() with a specific room (I think)
                    channel_id = event.source_message.channel.id
                    if hasattr(event.source_message, "thread"):
                        data.update({"thread_ts": event.source_message.thread})
            else:
                # Mentions that come back via self.reply()
                if hasattr(event.data, "original_incoming_event"):
                    if hasattr(event.data.original_incoming_event.channel, "id"):
                        channel_id = event.data.original_incoming_event.channel.id
                    else:
                        channel_id = event.data.original_incoming_event.channel
                else:
                    if hasattr(
                        event.data["original_incoming_event"].data.channel, "id"
                    ):
                        channel_id = event.data[
                            "original_incoming_event"
                        ].data.channel.id
                    else:
                        channel_id = event.data["original_incoming_event"].data.channel

            try:
                # If we're starting a thread
                if (
                    "kwargs" in event
                    and event.kwargs.get("start_thread", False)
                    and ("thread_ts" not in data or not data["thread_ts"])
                ):
                    if hasattr(event.source_message, "original_incoming_event"):
                        data.update(
                            {
                                "thread_ts": event.source_message.original_incoming_event["ts"]
                            }
                        )
                    elif (
                        hasattr(event.source_message, "data")
                        and hasattr(
                            event.source_message.data, "original_incoming_event"
                        )
                        and "ts" in event.source_message.data.original_incoming_event
                    ):
                        logging.error(
                            "Hm.  I was told to start a new thread, but while using .say(), instead of .reply().\n"
                            "This doesn't really make sense, but I'm going to make the best of it by pretending you "
                            "used .say() and threading off of your message.\n"
                            "Please update your plugin to use .reply() when you have a second!"
                        )
                        data.update(
                            {
                                "thread_ts": event.source_message.data.original_incoming_event[
                                    "ts"
                                ]
                            }
                        )
                else:
                    if hasattr(event.data.original_incoming_event, "thread_ts"):
                        data.update(
                            {"thread_ts": event.data.original_incoming_event.thread_ts}
                        )
                    elif "thread" in event.data.original_incoming_event.data:
                        data.update(
                            {
                                "thread_ts": event.data.original_incoming_event.data.thread
                            }
                        )
            except Exception:
                logging.info(traceback.format_exc().split(" ")[-1])

        data.update(
            {
                "channel": channel_id,
            }
        )
        return data

    def get_event_data(self, event):
        "Send a Slack message"
        data = {}
        if hasattr(event, "kwargs"):
            data.update(event.kwargs)

            # Add slack-specific functionality
            if "color" in event.kwargs:
                data.update(
                    {
                        "attachments": json.dumps(
                            [
                                {
                                    "fallback": event.content,
                                    "color": self._map_color(event.kwargs["color"]),
                                    "text": event.content,
                                }
                            ]
                        ),
                    }
                )
            elif "attachments" in event.kwargs:
                data.update(
                    {
                        "text": event.content,
                        "attachments": json.dumps(event.kwargs["attachments"]),
                    }
                )
            else:
                data.update(
                    {
                        "text": event.content,
                    }
                )
        else:
            data.update(
                {
                    "text": event.content,
                }
            )

        data = self.set_data_channel_and_thread(event, data=data)

        # Auto-link mention names
        if "text" in data:
            if data["text"].find("&lt;@") != -1:
                data["text"] = data["text"].replace("&lt;@", "<@")
                data["text"] = data["text"].replace("&gt;", ">")
            if len(data['text']) > MAX_MESSAGE_SIZE:
                new_event = Event(
                    type='file.upload',
                    # Removes "code" markers from around the item and then makes it bytes
                    file=data['text'].strip('```').encode('utf-8'),
                    filename=getattr(event, 'filename', getattr(event, 'title', 'response')),
                    filetype=getattr(event, 'filetype', 'text'),
                    source_message=event.source_message,
                    kwargs=event.kwargs,
                )
                try:
                    self.send_file(new_event)
                except Exception:
                    logging.exception('Error sending file')
                return None
        elif "attachments" in data and "text" in data["attachments"][0]:
            if data["attachments"][0]["text"].find("&lt;@") != -1:
                data["attachments"][0]["text"] = data["attachments"][0]["text"].replace(
                    "&lt;@", "<@"
                )
                data["attachments"][0]["text"] = data["attachments"][0]["text"].replace(
                    "&gt;", ">"
                )

        data.update(
            {
                "token": settings.SLACK_API_TOKEN,
                "as_user": True,
            }
        )
        if hasattr(event, "kwargs") and "html" in event.kwargs and event.kwargs["html"]:
            data.update(
                {
                    "parse": "none",
                }
            )
        return data

    def send_message(self, event):
        "Send a Slack message"
        if event.content == "" or event.content is None:
            # slack errors with no_text if empty message
            return
        data = self.get_event_data(event)
        if data is None:
            return
        self.client._web_client.api_call(  # pylint: disable=protected-access
            "chat.postMessage", data=data
        )

    def open_direct_message(self, user_id):
        """Opens a DM channel."""
        return self.client._web_client.api_call(  # pylint: disable=protected-access
            "conversations.open",
            users=[user_id]
        )['channel']['id']

    def update_message(self, event):
        "Update a Slack message"
        if event.content == "" or event.content is None:
            # slack errors with no_text if empty message
            return
        data = self.get_event_data(event)
        if data is None:
            return
        redis_key = f'slack_update_cache_{data["update"]}'
        if not hasattr(self, 'storage'):
            self.bootstrap_storage()
        timestamp = self.storage.redis.get(redis_key)
        if not timestamp:
            result = self.client._web_client.api_call(  # pylint: disable=protected-access
                "chat.postMessage", data=data
            )
            if result.get('ts', None):
                self.storage.redis.set(redis_key, result['ts'], ex=3600)
            else:
                logging.error('Failure sending %s: %s', event, result.get('error', 'Unknown error'))
        else:
            data['ts'] = timestamp
            result = self.client._web_client.api_call(  # pylint: disable=protected-access
                "chat.update", data=data
            )
            if result.get('ok', False) is False:
                logging.error('Failure updating %s: %s', event, result.get('error', 'Unknown error'))

    @staticmethod
    def _map_color(color):
        "Turn colors into hex values, handling old slack colors, etc"
        if color == "red":
            return "danger"
        if color == "yellow":
            return "warning"
        if color == "green":
            return "good"
        return color

    def join_channel(self, channel_id):
        "Join a channel"
        return self.client._web_client.api_call(  # pylint: disable=protected-access
            "channels.join",
            channel=channel_id,
        )

    @property
    def people(self):
        "References/initializes our internal people cache"
        if not self._people:
            self._update_people()
        return self._people

    @property
    def default_channel(self):
        "References/initializes our default channel"
        if not self._default_channel:
            self._decide_default_channel()
        return self._default_channel

    @property
    def channels(self):
        "References/initializes our internal channel cache"
        if not self._channels:
            self._update_channels()
        return self._channels

    @property
    def client(self):
        "References/initializes our RTM client"
        if self._client is None:
            self._client = RTMClient(
                token=settings.SLACK_API_TOKEN, run_async=False, auto_reconnect=True
            )
        return self._client

    def _decide_default_channel(self):
        "Selects a default channel"
        self._default_channel = None
        self.people  # Set self.me # pylint: disable=pointless-statement

        if hasattr(settings, "SLACK_DEFAULT_CHANNEL"):
            channel = self.get_channel_from_name(settings.SLACK_DEFAULT_CHANNEL)
            if channel:
                if self.me.id in channel.members:
                    self._default_channel = channel.id
                    return
            elif not self.complained_about_default:
                self.complained_about_default = True
                logging.error(
                    "The defined default channel(%s) does not exist!",
                    settings.SLACK_DEFAULT_CHANNEL,
                )

        for c in self.channels.values():
            if c.name != c.id and self.me.id in c.members:
                self._default_channel = c.id
        if not self._default_channel and not self.complained_uninvited:
            self.complained_uninvited = True
            logging.critical("No channels with me invited! No messages will be sent!")

    def _update_channels(self, client=None):
        "Updates our internal list of channels.  Kind of expensive."
        channels = {}
        if client:
            for page in client.conversations_list(
                limit=self.PAGE_LIMIT,
                exclude_archived=True,
                types="public_channel,private_channel,mpim,im",
            ):
                for channel in page["channels"]:
                    members = {}
                    for m in channel.get("members", list()):
                        if m in self.people:
                            members[m] = self.people[m]

                    channels[channel["id"]] = Channel(
                        id=channel["id"],
                        name=channel.get("name", channel["id"]),
                        source=clean_for_pickling(channel),
                        members=members,
                    )
        if len(channels.keys()) == 0:
            # Server isn't set up yet, and we're likely in a processing thread,
            if self.load("slack_channel_cache", None):
                self._channels = self.load("slack_channel_cache", None)
        else:
            self._channels = channels
            self.save("slack_channel_cache", channels)

    def _update_people(self, client=None):
        "Updates our internal list of Slack users.  Kind of expensive."
        people = {}
        if client:
            for page in client.users_list(limit=self.PAGE_LIMIT):
                for member in page["members"]:
                    if member["deleted"]:
                        continue
                    member_id = member["id"]
                    user_timezone = member.get("tz")
                    people[member_id] = Person(
                        id=member_id,
                        mention_handle=member.get("mention_handle", ""),
                        handle=member["name"],
                        source=clean_for_pickling(member),
                        name=member.get("real_name", ""),
                    )
                    if member["name"] == self.handle:
                        self.me = people[member_id]
                    if user_timezone and user_timezone != "unknown":
                        people[member_id].timezone = user_timezone
        if len(people.keys()) == 0:
            # Server isn't set up yet, and we're likely in a processing thread,
            if self.load("slack_people_cache", None):
                self._people = self.load("slack_people_cache", None)
            if self.me is None:
                self.me = self.load("slack_me_cache", None)
            if self.handle is None:
                self.handle = self.load("slack_handle_cache", None)
        else:
            self._people = people
            self.save("slack_people_cache", people)
            self.save("slack_me_cache", self.me)
            self.save("slack_handle_cache", self.handle)

    def _update_backend_metadata(self, **event):
        "Updates all our internal caches.  Very expenseive"
        logging.debug("updating backend on event: %s", event)
        name = event.get("data", dict()).get("self", dict()).get("name")
        if name is not None:
            self.__class__.handle = name
        Thread(
            target=self._update_people, args=(event["web_client"],), daemon=True
        ).start()
        Thread(
            target=self._update_channels, args=(event["web_client"],), daemon=True
        ).start()

    def _watch_slack_rtm(self):
        "This is our main loop."
        # The decorators don't work on unbound methods.  Sigh.
        # These are all events that should spark an update of our inventory
        RTMClient.run_on(event="open")(self._update_backend_metadata)
        RTMClient.run_on(event="channel_added")(self._update_backend_metadata)
        RTMClient.run_on(event="user_changed")(self._update_backend_metadata)
        # This just handles messages
        RTMClient.run_on(event="message")(self.handle_incoming_slack_event)
        self.client.start()

    def handle_incoming_slack_event(self, **kwargs):
        "Event handler"
        logging.debug("Handling incoming event: %s", kwargs)
        self.handle_incoming_event(kwargs["data"])

    def bootstrap(self):
        "This is Wills Process entry point for connecting to a backend"
        # Bootstrap must provide a way to to have:
        # a) self.normalize_incoming_event fired, or incoming events put into self.incoming_queue
        # b) any necessary threads running for a)
        # c) self.me (Person) defined, with Will's info
        # d) self.people (dict of People) defined, with everyone in an organization/backend
        # e) self.channels (dict of Channels) defined, with all available channels/rooms.
        #    Note that Channel asks for members, a list of People.
        # f) A way for self.handle, self.me, self.people, and self.channels to be kept accurate,
        #    with a maximum lag of 60 seconds.

        self.rtm_thread = Process(target=self._watch_slack_rtm, daemon=False)
        self.rtm_thread.start()

    def terminate(self):
        "Exit gracefully"
        if self.rtm_thread is not None:
            self.rtm_thread.terminate()
            while self.rtm_thread.is_alive():
                time.sleep(0.2)
