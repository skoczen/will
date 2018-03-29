from datetime import datetime
import json
import logging
from multiprocessing.queues import Empty
from multiprocessing import Process, Queue
import random
import re
import requests
import pickle
import sys
import time
import threading
import traceback

from sleekxmpp import ClientXMPP
from sleekxmpp.exceptions import IqError, IqTimeout

from .base import IOBackend
from will import settings
from will.utils import is_admin
from will.acl import is_acl_allowed
from will.abstractions import Event, Message, Person, Channel
from will.utils import Bunch, UNSURE_REPLIES, clean_for_pickling
from will.mixins import StorageMixin, PubSubMixin

ROOM_NOTIFICATION_URL = "https://%(server)s/v2/room/%(room_id)s/notification?auth_token=%(token)s"
ROOM_TOPIC_URL = "https://%(server)s/v2/room/%(room_id)s/topic?auth_token=%(token)s"
ROOM_URL = "https://%(server)s/v2/room/%(room_id)s/?auth_token=%(token)s"
SET_TOPIC_URL = "https://%(server)s/v2/room/%(room_id)s/topic?auth_token=%(token)s"
PRIVATE_MESSAGE_URL = "https://%(server)s/v2/user/%(user_id)s/message?auth_token=%(token)s"
USER_DETAILS_URL = "https://%(server)s/v2/user/%(user_id)s?auth_token=%(token)s"
ALL_USERS_URL = ("https://%(server)s/v2/user?auth_token=%(token)s&start-index"
                 "=%(start_index)s&max-results=%(max_results)s")
ALL_ROOMS_URL = ("https://%(server)s/v2/room?auth_token=%(token)s&start-index"
                 "=%(start_index)s&max-results=%(max_results)s&expand=items")

# From RoomsMixins
V1_TOKEN_URL = "https://%(server)s/v1/rooms/list?auth_token=%(token)s"
V2_TOKEN_URL = "https://%(server)s/v2/room?auth_token=%(token)s&expand=items"


class HipChatRosterMixin(object):
    @property
    def people(self):
        if not hasattr(self, "_people"):
            self._people = self.load('will_hipchat_people', {})
        return self._people

    @property
    def internal_roster(self):
        logging.warn(
            "mixin.internal_roster has been deprecated.  Please use mixin.people instead. "
            "internal_roster will be removed at the end of 2017"
        )
        return self.people

    def get_user_by_full_name(self, name):
        for jid, info in self.people.items():
            if info["name"] == name:
                return info

        return None

    def get_user_by_nick(self, nick):
        for jid, info in self.people.items():
            if info["nick"] == nick:
                return info
        return None

    def get_user_by_jid(self, jid):
        if jid in self.people:
            return self.people[jid]

        return None

    def get_user_from_message(self, message):
        if message["type"] == "groupchat":
            if "xmpp_jid" in message:
                user = self.get_user_by_jid(message["xmpp_jid"])
                if user:
                    return user
                elif "from" in message:
                    full_name = message["from"].split("/")[1]
                    user = self.get_user_by_full_name(full_name)
                    if user:
                        return user

            if "mucnick" in message:
                return self.get_user_by_full_name(message["mucnick"])

        elif message['type'] in ('chat', 'normal'):
            jid = ("%s" % message["from"]).split("@")[0].split("_")[1]
            return self.get_user_by_jid(jid)
        else:
            return None

    def message_is_from_admin(self, message):
        nick = self.get_user_from_message(message)['nick']
        return is_admin(nick)

    def message_is_allowed(self, message, acl):
        nick = self.get_user_from_message(message)['nick']
        return is_acl_allowed(nick, acl)

    def get_user_by_hipchat_id(self, id):
        for jid, info in self.people.items():
            if info["hipchat_id"] == id:
                return info
        return None


class HipChatRoom(Bunch):

    @property
    def id(self):
        if 'room_id' in self:
            # Using API v1
            return self['room_id']
        elif 'id' in self:
            # Using API v2
            return self['id']
        else:
            raise TypeError('Room ID not found')

    @property
    def history(self):
        payload = {"auth_token": settings.HIPCHAT_V2_TOKEN}
        response = requests.get("https://{1}/v2/room/{0}/history".format(str(self.id),
                                                                         settings.HIPCHAT_SERVER),
                                params=payload, **settings.REQUESTS_OPTIONS)
        data = json.loads(response.text)['items']
        for item in data:
            item['date'] = datetime.strptime(item['date'][:-13], "%Y-%m-%dT%H:%M:%S")
        return data

    @property
    def participants(self):
        payload = {"auth_token": settings.HIPCHAT_V2_TOKEN}
        response = requests.get(
            "https://{1}/v2/room/{0}/participant".format(
                str(self.id),
                settings.HIPCHAT_SERVER
            ),
            params=payload,
            **settings.REQUESTS_OPTIONS
        ).json()
        data = response['items']
        while 'next' in response['links']:
            response = requests.get(response['links']['next'],
                                    params=payload, **settings.REQUESTS_OPTIONS).json()
            data.extend(response['items'])
        return data


class HipChatRoomMixin(object):
    def update_available_rooms(self, q=None):
        self._available_rooms = {}
        # Use v1 token to grab a full room list if we can (good to avoid rate limiting)
        if hasattr(settings, "V1_TOKEN"):
            url = V1_TOKEN_URL % {"server": settings.HIPCHAT_SERVER,
                                  "token": settings.HIPCHAT_V1_TOKEN}
            r = requests.get(url, **settings.REQUESTS_OPTIONS)
            if r.status_code == requests.codes.unauthorized:
                raise Exception("V1_TOKEN authentication failed with HipChat")
            for room in r.json()["rooms"]:
                # Some integrations expect a particular name for the ID field.
                # Better to use room.id.
                room["id"] = room["room_id"]
                self._available_rooms[room["name"]] = HipChatRoom(**room)
        # Otherwise, grab 'em one-by-one via the v2 api.
        else:
            params = {}
            params['start-index'] = 0
            max_results = params['max-results'] = 1000
            url = V2_TOKEN_URL % {"server": settings.HIPCHAT_SERVER,
                                  "token": settings.HIPCHAT_V2_TOKEN}
            while True:
                resp = requests.get(url, params=params,
                                    **settings.REQUESTS_OPTIONS)
                if resp.status_code == requests.codes.unauthorized:
                    raise Exception("V2_TOKEN authentication failed with HipChat")
                rooms = resp.json()

                for room in rooms["items"]:
                    # Some integrations expect a particular name for the ID field.
                    # Better to use room.id
                    room["room_id"] = room["id"]
                    self._available_rooms[room["name"]] = HipChatRoom(**room)

                logging.info('Got %d rooms', len(rooms['items']))
                if len(rooms['items']) == max_results:
                    params['start-index'] += max_results
                else:
                    break

        self.save("hipchat_rooms", self._available_rooms)
        if q:
            q.put(self._available_rooms)

    @property
    def available_rooms(self):
        if not hasattr(self, "_available_rooms"):
            self._available_rooms = self.load('hipchat_rooms', None)
            if not self._available_rooms:
                self.update_available_rooms()

        return self._available_rooms

    def get_room_by_jid(self, jid):
        for room in self.available_rooms.values():
            if "xmpp_jid" in room and room["xmpp_jid"] == jid:
                return room
        return None

    def get_room_from_message(self, message):
        return self.get_room_from_name_or_id(message.data.channel.name)

    def get_room_from_name_or_id(self, name_or_id):
        for name, room in self.available_rooms.items():
            if name_or_id.lower() == name.lower():
                return room
            if "xmpp_jid" in room and name_or_id == room["xmpp_jid"]:
                return room
            if "room_id" in room and name_or_id == room["room_id"]:
                return room
        return None


class HipChatXMPPClient(ClientXMPP, HipChatRosterMixin, HipChatRoomMixin, StorageMixin, PubSubMixin):

    def start_xmpp_client(self, xmpp_bridge_queue=None, backend_name=""):
        logger = logging.getLogger(__name__)
        if not xmpp_bridge_queue:
            logger.error("Missing required bridge queue")

        self.xmpp_bridge_queue = xmpp_bridge_queue
        self.backend_name = backend_name

        ClientXMPP.__init__(self, "%s/bot" % settings.HIPCHAT_USERNAME, settings.HIPCHAT_PASSWORD)

        if settings.USE_PROXY:
            self.use_proxy = True
            self.proxy_config = {
                'host': settings.PROXY_HOSTNAME,
                'port': settings.PROXY_PORT,
                'username': settings.PROXY_USERNAME,
                'password': settings.PROXY_PASSWORD,
            }

        self.rooms = []
        self.default_room = settings.HIPCHAT_DEFAULT_ROOM

        my_user_url = "https://%(server)s/v2/user/%(user_id)s?auth_token=%(token)s" % {
            "user_id": settings.HIPCHAT_USERNAME.split("@")[0].split("_")[1],
            "server": settings.HIPCHAT_SERVER,
            "token": settings.HIPCHAT_V2_TOKEN,
        }

        r = requests.get(my_user_url, **settings.REQUESTS_OPTIONS)
        resp = r.json()
        if "email" in resp:
            settings.HIPCHAT_EMAIL = resp["email"]
            settings.HIPCHAT_HANDLE = resp["mention_name"]
            settings.HIPCHAT_NAME = resp["name"]
        else:
            raise EnvironmentError(
                "\n\nError getting user info from Hipchat. This is usually a problem with the\n"
                "username or V2 token, but here's what I heard back from them: \n\n   %s\n\n" % resp
            )

        self.available_rooms
        if hasattr(settings, "HIPCHAT_ROOMS") and settings.HIPCHAT_ROOMS:
            for r in settings.HIPCHAT_ROOMS:
                if r != "":
                    if not hasattr(self, "default_room"):
                        self.default_room = r

                    try:
                        self.rooms.append(self.available_rooms[r])
                    except KeyError:
                        logger.error(
                            u'"{0}" is not an available room, ask'
                            ' "@{1} what are the rooms?" for the full list.'
                            .format(r, settings.HIPCHAT_HANDLE))
        else:
            for name, r in self.available_rooms.items():
                if not hasattr(self, "default_room"):
                        self.default_room = r
                self.rooms.append(r)

        self.nick = settings.HIPCHAT_HANDLE
        self.handle = settings.HIPCHAT_HANDLE
        self.mention_handle = "@%s" % settings.HIPCHAT_HANDLE

        self.whitespace_keepalive = True
        self.whitespace_keepalive_interval = 30

        if settings.ALLOW_INSECURE_HIPCHAT_SERVER is True:
            self.add_event_handler('ssl_invalid_cert', lambda cert: True)

        self.add_event_handler("roster_update", self.join_rooms)
        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message_recieved)
        self.add_event_handler("groupchat_message", self.room_message)
        self.add_event_handler("groupchat_invite", self.room_invite)
        self.add_event_handler("error", self.handle_errors)
        self.add_event_handler("presence_error", self.handle_errors)

        self.register_plugin('xep_0045')  # MUC

    def session_start(self, event):
        self.send_presence()
        try:
            self.get_roster()
        except IqError as err:
            logging.error('There was an error getting the roster')
            logging.error(err.iq['error']['condition'])
            self.disconnect()
        except IqTimeout:
            logging.error('Server is taking too long to respond. Disconnecting.')
            self.disconnect()

    def join_rooms(self, event):
        for r in self.rooms:
            if "xmpp_jid" in r:
                self.plugin['xep_0045'].joinMUC(r["xmpp_jid"], settings.HIPCHAT_NAME, wait=True)

    def handle_errors(self, event):
        print("got error event")
        print(event)

    def room_invite(self, event):
        logging.info("Invite recieved for %s" % event)
        for r in self.rooms:
            if "xmpp_jid" in r:
                self.plugin['xep_0045'].joinMUC(r["xmpp_jid"], settings.HIPCHAT_NAME, wait=True)

    def update_will_roster_and_rooms(self):
        people = self.load('will_hipchat_people', {})

        # Loop through the connected rooms (self.roster comes from ClientXMPP)
        for roster_id in self.roster:

            cur_roster = self.roster[roster_id]
            # Loop through the users in a given room
            for user_id in cur_roster:
                user_data = cur_roster[user_id]
                if user_data["name"] != "":
                    # If we don't have this user in the people, add them.
                    if not user_id in people:
                        people[user_id] = Person()

                    hipchat_id = user_id.split("@")[0].split("_")[1]
                    # Update their info
                    people[user_id].update({
                        "name": user_data["name"],
                        "jid": user_id,
                        "hipchat_id": hipchat_id,
                    })

                    # If we don't have a nick yet, pull it and mention_name off the master user list.
                    if not hasattr(people[user_id], "nick") and hipchat_id in self.people:
                        user_data = self.get_user_list[hipchat_id]
                        people[user_id].nick = user_data["mention_name"]
                        people[user_id].mention_name = user_data["mention_name"]

                    # If it's me, save that info!
                    if people[user_id].get("name", "") == self.nick:
                        self.me = people[user_id]

        self.save("will_hipchat_people", people)

        self.update_available_rooms()

    def room_message(self, msg):
        self._send_to_backend(msg)

    def message_recieved(self, msg):
        if msg['type'] in ('chat', 'normal'):
            self._send_to_backend(msg)

    def real_sender_jid(self, msg):
        # There's a bug in sleekXMPP where it doesn't set the "from_jid" properly.
        # Thus, this hideous hack.
        msg_str = "%s" % msg
        start = 'from_jid="'
        start_pos = msg_str.find(start)
        if start_pos != -1:
            cut_start = start_pos + len(start)
            return msg_str[cut_start:msg_str.find('"', cut_start)]

        return msg["from"]

    def _send_to_backend(self, msg):
        stripped_msg = Bunch()
        # TODO: Find a faster way to do this - this is crazy.
        for k, v in msg.__dict__.items():
            try:
                pickle.dumps(v)
                stripped_msg[k] = v
            except:
                pass
        for k in msg.xml.keys():
            try:
                # print(k)
                # print(msg.xml.get(k))
                pickle.dumps(msg.xml.get(k))
                stripped_msg[k] = msg.xml.get(k)
            except:
                # print("failed to parse %s" % k)
                pass

        stripped_msg.xmpp_jid = msg.getMucroom()
        stripped_msg.body = msg["body"]
        self.xmpp_bridge_queue.put(stripped_msg)


class HipChatBackend(IOBackend, HipChatRosterMixin, HipChatRoomMixin, StorageMixin):
    friendly_name = "HipChat"
    internal_name = "will.backends.io_adapters.hipchat"
    required_settings = [
        {
            "name": "HIPCHAT_USERNAME",
            "obtain_at": """1. Go to hipchat, and create a new user for will.
2. Log into will, and go to Account settings>XMPP/Jabber Info.
3. On that page, the 'Jabber ID' is the value you want to use.""",
        },
        {
            "name": "HIPCHAT_PASSWORD",
            "obtain_at": (
                "1. Go to hipchat, and create a new user for will.  "
                "Note that password - this is the value you want. "
                "It's used for signing in via XMPP."
            ),
        },
        {
            "name": "HIPCHAT_V2_TOKEN",
            "obtain_at": """1. Log into hipchat using will's user.
2. Go to https://your-org.hipchat.com/account/api
3. Create a token.
4. Copy the value - this is the HIPCHAT_V2_TOKEN.""",
        }
    ]

    def send_direct_message(self, user_id, message_body, html=False, card=None, notify=False, **kwargs):
        if kwargs:
            logging.warn("Unknown keyword args for send_direct_message: %s" % kwargs)

        format = "text"
        if html:
            format = "html"

        try:
            # https://www.hipchat.com/docs/apiv2/method/private_message_user
            url = PRIVATE_MESSAGE_URL % {"server": settings.HIPCHAT_SERVER,
                                         "user_id": user_id,
                                         "token": settings.HIPCHAT_V2_TOKEN}
            data = {
                "message": message_body,
                "message_format": format,
                "notify": notify,
                "card": card,
            }
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            r = requests.post(url, headers=headers, data=json.dumps(data), **settings.REQUESTS_OPTIONS)
            r.raise_for_status()
        except:
            logging.critical("Error in send_direct_message: \n%s" % traceback.format_exc())

    def send_room_message(self, room_id, message_body, html=False, color="green", notify=False, card=None, **kwargs):
        if kwargs:
            logging.warn("Unknown keyword args for send_room_message: %s" % kwargs)

        format = "text"
        if html:
            format = "html"

        try:
            # https://www.hipchat.com/docs/apiv2/method/send_room_notification
            url = ROOM_NOTIFICATION_URL % {"server": settings.HIPCHAT_SERVER,
                                           "room_id": room_id,
                                           "token": settings.HIPCHAT_V2_TOKEN}
            data = {
                "message": message_body,
                "message_format": format,
                "color": color,
                "notify": notify,
                "card": card,
            }
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            r = requests.post(url, headers=headers, data=json.dumps(data), **settings.REQUESTS_OPTIONS)
            r.raise_for_status()

        except:
            logging.critical("Error in send_room_message: \n%s" % traceback.format_exc())

    def set_room_topic(self, room_id, topic):
        try:
            # https://www.hipchat.com/docs/apiv2/method/send_room_notification
            url = ROOM_TOPIC_URL % {"server": settings.HIPCHAT_SERVER,
                                    "room_id": room_id,
                                    "token": settings.HIPCHAT_V2_TOKEN}
            data = {
                "topic": topic,
            }
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            requests.put(url, headers=headers, data=json.dumps(data), **settings.REQUESTS_OPTIONS)
        except:
            logging.critical("Error in set_room_topic: \n%s" % traceback.format_exc())

    def get_room_from_message(self, event):
        kwargs = {}
        if hasattr(event, "kwargs"):
            kwargs.update(event.kwargs)
        if hasattr(event, "source_message") and event.source_message:
            send_source = event.source_message
            if hasattr(event.source_message, "data"):
                send_source = event.source_message.data

            if send_source.is_private_chat:
                # Private, 1-1 chats.
                return False
            else:
                # We're in a public room
                return send_source.channel.id
        else:
            # Came from webhook/etc
            if "room" in kwargs:
                return kwargs["room"],
            else:
                return self.get_room_from_name_or_id(settings.HIPCHAT_DEFAULT_ROOM)["room_id"]
        return False

    def get_hipchat_user(self, user_id, q=None):
        url = USER_DETAILS_URL % {"server": settings.HIPCHAT_SERVER,
                                  "user_id": user_id,
                                  "token": settings.HIPCHAT_V2_TOKEN}
        r = requests.get(url, **settings.REQUESTS_OPTIONS)
        if q:
            q.put(r.json())
        else:
            return r.json()

    @property
    def people(self):
        if not hasattr(self, "_people"):
            full_roster = {}

            # Grab the first roster page, and populate full_roster
            url = ALL_USERS_URL % {"server": settings.HIPCHAT_SERVER,
                                   "token": settings.HIPCHAT_V2_TOKEN,
                                   "start_index": 0,
                                   "max_results": 1000}
            r = requests.get(url, **settings.REQUESTS_OPTIONS)
            for user in r.json()['items']:
                full_roster["%s" % (user['id'],)] = Person(
                    id=user["id"],
                    handle=user["mention_name"],
                    mention_handle="@%s" % user["mention_name"],
                    source=clean_for_pickling(user),
                    name=user["name"],
                )
            # Keep going through the next pages until we're out of pages.
            while 'next' in r.json()['links']:
                url = "%s&auth_token=%s" % (r.json()['links']['next'], settings.HIPCHAT_V2_TOKEN)
                r = requests.get(url, **settings.REQUESTS_OPTIONS)

                for user in r.json()['items']:
                    full_roster["%s" % (user['id'],)] = Person(
                        id=user["id"],
                        handle=user["mention_name"],
                        mention_handle="@%s" % user["mention_name"],
                        source=clean_for_pickling(user),
                        name=user["name"],
                    )

            self._people = full_roster
            for k, u in full_roster.items():
                if u.handle == settings.HIPCHAT_HANDLE:
                    self.me = u
        return self._people

    @property
    def channels(self):
        if not hasattr(self, "_channels"):
            all_rooms = {}

            # Grab the first roster page, and populate all_rooms
            url = ALL_ROOMS_URL % {"server": settings.HIPCHAT_SERVER,
                                   "token": settings.HIPCHAT_V2_TOKEN,
                                   "start_index": 0,
                                   "max_results": 1000}
            r = requests.get(url, **settings.REQUESTS_OPTIONS)
            for room in r.json()['items']:
                # print(room)
                all_rooms["%s" % (room['xmpp_jid'],)] = Channel(
                    id=room["id"],
                    name=room["name"],
                    source=clean_for_pickling(room),
                    members={},
                )

            # Keep going through the next pages until we're out of pages.
            while 'next' in r.json()['links']:
                url = "%s&auth_token=%s" % (r.json()['links']['next'], settings.HIPCHAT_V2_TOKEN)
                r = requests.get(url, **settings.REQUESTS_OPTIONS)

                for room in r.json()['items']:
                    all_rooms["%s" % (room['xmpp_jid'],)] = Channel(
                        id=room["id"],
                        name=room["name"],
                        source=clean_for_pickling(room),
                        members={}
                    )

            self._channels = all_rooms
        return self._channels

    def normalize_incoming_event(self, event):
        logging.debug("hipchat: normalize_incoming_event - %s" % event)
        if event["type"] in ("chat", "normal", "groupchat") and ("from_jid" in event or "from" in event):

            sender = self.get_user_from_message(event)
            interpolated_handle = "@%s" % self.me.handle
            will_is_mentioned = False
            will_said_it = False
            channel = None
            if "xmpp_jid" in event and event["xmpp_jid"]:
                channel = clean_for_pickling(self.channels[event["xmpp_jid"]])
                is_private_chat = False
            else:
                if event["type"] in ("chat", "normal"):
                    is_private_chat = True

            is_direct = False
            if is_private_chat or event["body"].startswith(interpolated_handle):
                is_direct = True

            if event["body"].startswith(interpolated_handle):
                event["body"] = event["body"][len(interpolated_handle):].strip()

            if interpolated_handle in event["body"]:
                will_is_mentioned = True

            if sender and self.me and sender.id == self.me.id:
                will_said_it = True

            m = Message(
                content=event["body"],
                is_direct=is_direct,
                is_private_chat=is_private_chat,
                is_group_chat=not is_private_chat,
                backend=self.internal_name,
                sender=sender,
                channel=channel,
                will_is_mentioned=will_is_mentioned,
                will_said_it=will_said_it,
                backend_supports_acl=True,
                original_incoming_event=clean_for_pickling(event),
            )
            # print("normalized:")
            # print(m.__dict__)
            return m

        else:
            # print("Unknown event type")
            # print(event)
            return None

    def handle_outgoing_event(self, event):
        kwargs = {}
        if hasattr(event, "kwargs"):
            kwargs.update(event.kwargs)

        room = None
        passed_room = None
        if "room" in kwargs:
            passed_room = kwargs["room"]
        if "channel" in kwargs:
            passed_room = kwargs["channel"]

        if passed_room:
            if isinstance(passed_room, str):
                # User passed in a room string
                room = self.get_room_from_name_or_id(passed_room)
            else:
                # User found the internal HipChatRoom object and passed it.
                room = passed_room
        else:
            # Default to the room we heard this message in.
            room = self.get_room_from_message(event)

        room_id = None
        if room and hasattr(room, "id"):
            room_id = room.id
        else:
            room_id = room

        if event.type in ["say", "reply"]:
            event.content = re.sub(r'>\s+<', '><', event.content)

            if hasattr(event, "source_message") and event.source_message and not room:
                send_source = event.source_message

                if hasattr(event.source_message, "data"):
                    send_source = event.source_message.data

                if send_source.is_private_chat:
                    # Private, 1-1 chats.
                    self.send_direct_message(send_source.sender.id, event.content, **kwargs)
                    return

            # Otherwise trust room.
            self.send_room_message(
                room_id,
                event.content,
                **kwargs
            )

        elif event.type in ["topic_change", ]:
            if room_id:
                self.set_room_topic(room_id, event.content)
            else:
                if hasattr(event, "source_message") and event.source_message:
                    send_source = event.source_message

                    if hasattr(event.source_message, "data"):
                        send_source = event.source_message.data
                    self.send_direct_message(send_source.sender.id, "I can't set the topic of a one-to-one chat.  Let's just talk.", **kwargs)

        elif (
            event.type == "message.no_response" and
            event.data.is_direct and
            event.data.will_said_it is False
        ):
            if event.data.original_incoming_event.type == "groupchat":
                self.send_room_message(
                    event.data.channel.id,
                    random.choice(UNSURE_REPLIES),
                    **kwargs
                )
            else:
                self.send_direct_message(
                    event.data.sender.id,
                    random.choice(UNSURE_REPLIES),
                    **kwargs
                )

    def __handle_bridge_queue(self):
        while True:
            try:
                try:
                    input_event = self.xmpp_bridge_queue.get(timeout=settings.EVENT_LOOP_INTERVAL)
                    if input_event:
                        self.handle_incoming_event(input_event)

                except Empty:
                    pass

            except (KeyboardInterrupt, SystemExit):
                pass
            self.sleep_for_event_loop()

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
        self.client = HipChatXMPPClient("%s/bot" % settings.HIPCHAT_USERNAME, settings.HIPCHAT_PASSWORD)
        self.xmpp_bridge_queue = Queue()
        self.client.start_xmpp_client(
            xmpp_bridge_queue=self.xmpp_bridge_queue,
            backend_name=self.internal_name,
        )
        self.client.connect()
        # Even though these are properties, they do some gets and self-fillings.
        self.people
        self.channels

        self.bridge_thread = Process(target=self.__handle_bridge_queue)
        self.bridge_thread.start()
        self.xmpp_thread = Process(target=self.client.process, kwargs={"block": True})
        self.xmpp_thread.start()

    def terminate(self):
        if hasattr(self, "xmpp_thread"):
            self.xmpp_thread.terminate()
        if hasattr(self, "bridge_thread"):
            self.bridge_thread.terminate()

        while (
            (hasattr(self, "xmpp_thread") and self.xmpp_thread.is_alive()) or
            (hasattr(self, "bridge_thread") and self.bridge_thread.is_alive())
        ):
            time.sleep(0.2)
