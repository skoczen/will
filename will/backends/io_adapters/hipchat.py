import json
import logging
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
from multiprocessing import Process, Queue
from will.abstractions import Event, Message, Person, Channel
from multiprocessing.queues import Empty
from will.utils import Bunch, UNSURE_REPLIES, clean_for_pickling
from will.mixins import RoomMixin, StorageMixin, PubSubMixin

# TODO: Cleanup unused urls
ROOM_NOTIFICATION_URL = "https://%(server)s/v2/room/%(room_id)s/notification?auth_token=%(token)s"
ROOM_TOPIC_URL = "https://%(server)s/v2/room/%(room_id)s/topic?auth_token=%(token)s"
ROOM_URL = "https://%(server)s/v2/room/%(room_id)s/?auth_token=%(token)s"
PRIVATE_MESSAGE_URL = "https://%(server)s/v2/user/%(user_id)s/message?auth_token=%(token)s"
SET_TOPIC_URL = "https://%(server)s/v2/room/%(room_id)s/topic?auth_token=%(token)s"
USER_DETAILS_URL = "https://%(server)s/v2/user/%(user_id)s?auth_token=%(token)s"
ALL_USERS_URL = ("https://%(server)s/v2/user?auth_token=%(token)s&start-index"
                 "=%(start_index)s&max-results=%(max_results)s")
ALL_ROOMS_URL = ("https://%(server)s/v2/room?auth_token=%(token)s&start-index"
                 "=%(start_index)s&max-results=%(max_results)s&expand=items")


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
        # TODO: Fix this better for shell, etc
        for jid, info in self.people.items():
            if info["name"] == name:
                return info

        return {"jid": "123", "hipchat_id": "123"}

    def get_user_by_nick(self, nick):
        for jid, info in self.people.items():
            if info["nick"] == nick:
                return info
        return {"jid": "123", "hipchat_id": "123"}

    def get_user_by_jid(self, jid):
        if jid in self.people:
            return self.people[jid]

        return {"jid": "123", "hipchat_id": "123"}

    def get_user_from_message(self, message):
        if message["type"] == "groupchat":
            return self.get_user_by_full_name(message["mucnick"])
        elif message['type'] in ('chat', 'normal'):
            jid = ("%s" % message["from"]).split("/")[0]
            return self.get_user_by_jid(jid)
        else:
            return {"jid": "123", "hipchat_id": "123"}

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


class HipchatXMPPClient(ClientXMPP, HipChatRosterMixin, RoomMixin, StorageMixin, PubSubMixin):

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

        # TODO: Clean this up, and pass it in from the controlling thread,
        # then nuke RoomsMixin
        # Property boostraps the list
        self.available_rooms
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

        # TODO: Move this to the hipchat backend
        # if "hipchat" in settings.CHAT_BACKENDS:
        #     puts("Verifying rooms...")
        #     # If we're missing ROOMS, join all of them.
        #     with indent(2):
        #         if settings.HIPCHAT_ROOMS is None:
        #             # Yup. Thanks, BSDs.
        #             q = Queue()
        #             p = Process(target=self.update_available_rooms, args=(), kwargs={"q": q, })
        #             p.start()
        #             rooms_list = q.get()
        #             show_valid("Joining all %s known rooms." % len(rooms_list))
        #             os.environ["WILL_ROOMS"] = ";".join(rooms_list)
        #             p.join()
        #             settings.import_settings()
        #         else:
        #             show_valid(
        #                 "Joining the %s room%s specified." % (
        #                     len(settings.HIPCHAT_ROOMS),
        #                     "s" if len(settings.HIPCHAT_ROOMS) > 1 else ""
        #                 )
        #             )
        #     puts("")

        self.nick = settings.HIPCHAT_NAME
        self.handle = settings.HIPCHAT_HANDLE

        self.whitespace_keepalive = True
        self.whitespace_keepalive_interval = 30

        if settings.ALLOW_INSECURE_HIPCHAT_SERVER is True:
            self.add_event_handler('ssl_invalid_cert', lambda cert: True)

        self.add_event_handler("roster_update", self.join_rooms)
        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message_recieved)
        self.add_event_handler("groupchat_message", self.room_message)
        self.add_event_handler("groupchat_invite", self.room_invite)

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
        # TODO: Pull this and related.
        # self.update_will_roster_and_rooms()

        for r in self.rooms:
            if "xmpp_jid" in r:
                self.plugin['xep_0045'].joinMUC(r["xmpp_jid"], self.nick, wait=True)

    def room_invite(self, event):
        # TODO: Pull this and related.
        # self.update_will_roster_and_rooms()
        logging.info("Invite recieved for %s" % event)
        for r in self.rooms:
            if "xmpp_jid" in r:
                self.plugin['xep_0045'].joinMUC(r["xmpp_jid"], self.nick, wait=True)

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
        print "message_recieved"
        print msg.__dict__
        print msg['type']
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
        print("putting in bridge queue")
        print(stripped_msg)
        self.xmpp_bridge_queue.put(stripped_msg)


class HipChatBackend(IOBackend, RoomMixin, StorageMixin):
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
        },
        {
            "name": "HIPCHAT_HANDLE",
            "obtain_at": """1. Log into hipchat using will's user.
2. Set HIPCHAT_HANDLE to Will's users' mention name without the @, i.e. @will would be HIPCHAT_HANDLE='will'.""",
        },
    ]

    def send_direct_message(self, user_id, message_body, html=False, notify=False, **kwargs):
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
            }
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            requests.post(url, headers=headers, data=json.dumps(data), **settings.REQUESTS_OPTIONS)
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
                    all_rooms["%s" % (room['id'],)] = Channel(
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
            # Sample of group message
            # {u'source_team': u'T5ACF70KV', u'text': u'test',
            # u'ts': u'1495661121.838366', u'user': u'U5ACF70RH',
            # u'team': u'T5ACF70KV', u'type': u'message', u'channel': u'C5JDAR2S3'}

            # Sample of 1-1 message
            # {u'source_team': u'T5ACF70KV', u'text': u'test',
            # u'ts': u'1495662397.335424', u'user': u'U5ACF70RH',
            # u'team': u'T5ACF70KV', u'type': u'message', u'channel': u'D5HGP0YE7'}
            if "from_jid" in event:
                sender = event["from_jid"]
            else:
                sender = event["from"]

            event_sender_id = sender.split("@")[0].split("_")[1]

            sender = self.people[event_sender_id]
            channel = clean_for_pickling(self.channels[event["xmpp_jid"]])
            interpolated_handle = "@%s" % self.me.handle
            will_is_mentioned = False
            will_said_it = False

            is_private_chat = False

            if event["type"] in ("chat", "normal"):
                is_private_chat = True

            # <@U5GUL9D9N> hi
            is_direct = False
            if is_private_chat or event["body"].startswith(interpolated_handle):
                is_direct = True

            if event["body"].startswith(interpolated_handle):
                event["body"] = event["body"][len(interpolated_handle):].strip()

            if interpolated_handle in event["body"]:
                will_is_mentioned = True

            if sender == self.me.id:
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
            print("Unknown event type")
            print(event)
            return None

    def handle_outgoing_event(self, event):
        kwargs = {}
        if hasattr(event, "kwargs"):
            kwargs.update(event.kwargs)

        if event.type in ["say", "reply"]:
            event.content = re.sub(r'>\s+<', '><', event.content)

            if hasattr(event, "source_message") and event.source_message:
                if event.source_message.original_incoming_event.type == "groupchat":

                    sys.stdout.write("\n\n\n")
                    sys.stdout.write("%s" % event.source_message.channel)
                    sys.stdout.flush()
                    self.send_room_message(
                        event.source_message.channel.id,
                        event.content,
                        **kwargs
                    )
                else:
                    event.source_message
                    user_id = event.source_message.sender.id
                    self.send_direct_message(
                        user_id,
                        event.content,
                        **kwargs
                    )
            else:
                # Came from webhook/etc
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
            event.source_message.is_direct and
            event.source_message.will_said_it is False
        ):
            if event.source_message.original_incoming_event.type == "groupchat":
                self.send_room_message(
                    event.source_message.original_incoming_event.room.room_id,
                    random.choice(UNSURE_REPLIES),
                    **kwargs
                )
            else:
                self.send_direct_message(
                    event.source_message.original_incoming_event.sender["hipchat_id"],
                    random.choice(UNSURE_REPLIES),
                    **kwargs
                )

    def __handle_bridge_queue(self):
        while True:
            try:
                try:
                    input_event = self.xmpp_bridge_queue.get(timeout=settings.EVENT_LOOP_INTERVAL)
                    if input_event:
                        print "input_event"
                        print input_event
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
        self.client = HipchatXMPPClient("%s/bot" % settings.HIPCHAT_USERNAME, settings.HIPCHAT_PASSWORD)
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
