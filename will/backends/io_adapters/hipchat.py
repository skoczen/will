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

from will import settings
from .base import IOBackend
from multiprocessing import Process, Queue
from will.backends.io_adapters.base import Event, Message, Person, Channel
from multiprocessing.queues import Empty
from will.utils import Bunch, UNSURE_REPLIES, clean_for_pickling
from will.mixins import RosterMixin, RoomMixin, StorageMixin

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


class HipchatXMPPClient(ClientXMPP, RosterMixin, RoomMixin, StorageMixin):

    def start_xmpp_client(self, input_queue=None, output_queue=None, backend_name=""):
        logger = logging.getLogger(__name__)
        if not input_queue or not output_queue:
            logger.error("Missing required input and output queues")

        self.input_queue = input_queue
        self.output_queue = output_queue
        self.backend_name = backend_name

        ClientXMPP.__init__(self, "%s/bot" % settings.USERNAME, settings.PASSWORD)

        if settings.USE_PROXY:
            self.use_proxy = True
            self.proxy_config = {
                'host': settings.PROXY_HOSTNAME,
                'port': settings.PROXY_PORT,
                'username': settings.PROXY_USERNAME,
                'password': settings.PROXY_PASSWORD,
            }

        self.rooms = []
        self.default_room = settings.DEFAULT_ROOM

        # TODO: Clean this up, and pass it in from the controlling thread,
        # then nuke RoomsMixin
        # Property boostraps the list
        self.available_rooms
        for r in settings.ROOMS:
            if r != "":
                if not hasattr(self, "default_room"):
                    self.default_room = r

                try:
                    self.rooms.append(self.available_rooms[r])
                except KeyError:
                    logger.error(
                        u'"{0}" is not an available room, ask'
                        ' "@{1} what are the rooms?" for the full list.'
                        .format(r, settings.HANDLE))

        self.nick = settings.NAME
        self.handle = settings.HANDLE
        self.handle_regex = re.compile("@%s" % self.handle)

        self.whitespace_keepalive = True
        self.whitespace_keepalive_interval = 30

        if settings.ALLOW_INSECURE_HIPCHAT_SERVER is True:
            self.add_event_handler('ssl_invalid_cert', lambda cert: True)

        self.add_event_handler("roster_update", self.join_rooms)
        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message_recieved)
        self.add_event_handler("groupchat_message", self.room_message)

        self.register_plugin('xep_0045')  # MUC

    def session_start(self, event):
        self.send_presence()
        self.get_roster()

    def join_rooms(self, event):
        # TODO: Pull this and related.
        # self.update_will_roster_and_rooms()

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
        self._handle_message_listeners(msg)

    def message_recieved(self, msg):
        if msg['type'] in ('chat', 'normal'):
            self._handle_message_listeners(msg)

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

    def _handle_message_listeners(self, msg):
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
                # print k
                # print msg.xml.get(k)
                pickle.dumps(msg.xml.get(k))
                stripped_msg[k] = msg.xml.get(k)
            except:
                # print "failed to parse %s" % k
                pass

        stripped_msg.xmpp_jid = msg.getMucroom()
        stripped_msg.body = msg["body"]
        self.input_queue.put(stripped_msg)


class HipChatBackend(IOBackend, RoomMixin, StorageMixin):
    friendly_name = "HipChat"
    internal_name = "will.backends.io_adapters.hipchat"

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
                                         "token": settings.V2_TOKEN}
            data = {
                "message": message_body,
                "message_format": format,
                "notify": notify,
            }
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            requests.post(url, headers=headers, data=json.dumps(data), **settings.REQUESTS_OPTIONS)
        except:
            logging.critical("Error in send_direct_message: \n%s" % traceback.format_exc())

    def send_room_message(self, room_id, message_body, html=False, color="green", notify=False, **kwargs):
        if kwargs:
            logging.warn("Unknown keyword args for send_room_message: %s" % kwargs)

        format = "text"
        if html:
            format = "html"

        try:
            # https://www.hipchat.com/docs/apiv2/method/send_room_notification
            url = ROOM_NOTIFICATION_URL % {"server": settings.HIPCHAT_SERVER,
                                           "room_id": room_id,
                                           "token": settings.V2_TOKEN}
            data = {
                "message": message_body,
                "message_format": format,
                "color": color,
                "notify": notify,
            }
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            requests.post(url, headers=headers, data=json.dumps(data), **settings.REQUESTS_OPTIONS)

        except:
            logging.critical("Error in send_room_message: \n%s" % traceback.format_exc())

    def set_room_topic(self, room_id, topic):
        try:
            # https://www.hipchat.com/docs/apiv2/method/send_room_notification
            url = ROOM_TOPIC_URL % {"server": settings.HIPCHAT_SERVER,
                                    "room_id": room_id,
                                    "token": settings.V2_TOKEN}
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
                                  "token": settings.V2_TOKEN}
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
                                   "token": settings.V2_TOKEN,
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
                url = "%s&auth_token=%s" % (r.json()['links']['next'], settings.V2_TOKEN)
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
                if u.handle == settings.HANDLE:
                    self.me = u
        return self._people

    @property
    def channels(self):
        if not hasattr(self, "_channels"):
            all_rooms = {}

            # Grab the first roster page, and populate all_rooms
            url = ALL_ROOMS_URL % {"server": settings.HIPCHAT_SERVER,
                                   "token": settings.V2_TOKEN,
                                   "start_index": 0,
                                   "max_results": 1000}
            r = requests.get(url, **settings.REQUESTS_OPTIONS)
            for room in r.json()['items']:
                # print room
                all_rooms["%s" % (room['xmpp_jid'],)] = Channel(
                    id=room["id"],
                    name=room["name"],
                    source=clean_for_pickling(room),
                    members={},
                )

            # Keep going through the next pages until we're out of pages.
            while 'next' in r.json()['links']:
                url = "%s&auth_token=%s" % (r.json()['links']['next'], settings.V2_TOKEN)
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

    def handle_incoming_event(self, event):
        print "hipchat: handle_incoming_event - %s" % event

        if event["type"] in ("chat", "normal", "groupchat") and "from_jid" in event:
            # Sample of group message
            # {u'source_team': u'T5ACF70KV', u'text': u'test',
            # u'ts': u'1495661121.838366', u'user': u'U5ACF70RH',
            # u'team': u'T5ACF70KV', u'type': u'message', u'channel': u'C5JDAR2S3'}

            # Sample of 1-1 message
            # {u'source_team': u'T5ACF70KV', u'text': u'test',
            # u'ts': u'1495662397.335424', u'user': u'U5ACF70RH',
            # u'team': u'T5ACF70KV', u'type': u'message', u'channel': u'D5HGP0YE7'}
            event_sender_id = event["from_jid"].split("@")[0].split("_")[1]
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

            if event["from_jid"] == self.me.id:
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
                source=clean_for_pickling(event),
            )
            self.input_queue.put(m)

        else:
            # print "Unknown event type"
            # print event
            pass

    def handle_outgoing_event(self, event):
        kwargs = {}
        if hasattr(event, "kwargs"):
            kwargs.update(event.kwargs)

        if event.type in ["say", "reply"]:
            event.content = re.sub(r'>\s+<', '><', event.content)

            if hasattr(event, "source_message") and event.source_message:
                if event.source_message.source.type == "groupchat":

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
            if event.source_message.source.type == "groupchat":
                self.send_room_message(
                    event.source_message.source.room.room_id,
                    random.choice(UNSURE_REPLIES),
                    **kwargs
                )
            else:
                self.send_direct_message(
                    event.source_message.source.sender["hipchat_id"],
                    random.choice(UNSURE_REPLIES),
                    **kwargs
                )

    def __handle_bridge_queue(self):
        while True:
            try:
                try:
                    input_event = self.xmpp_bridge_queue.get(timeout=settings.QUEUE_INTERVAL)
                    if input_event:
                        self.handle_incoming_event(input_event)

                except Empty:
                    pass

            except (KeyboardInterrupt, SystemExit):
                pass

    def bootstrap(self):
        # Bootstrap must provide a way to to have:
        # a) self.handle_incoming_event fired, or incoming events put into self.incoming_queue
        # b) any necessary threads running for a)
        # c) self.me (Person) defined, with Will's info
        # d) self.people (dict of People) defined, with everyone in an organization/backend
        # e) self.channels (dict of Channels) defined, with all available channels/rooms.
        #    Note that Channel asks for members, a list of People.
        # f) A way for self.handle, self.me, self.people, and self.channels to be kept accurate,
        #    with a maximum lag of 60 seconds.
        self.client = HipchatXMPPClient("%s/bot" % settings.USERNAME, settings.PASSWORD)
        self.xmpp_bridge_queue = Queue()
        self.client.start_xmpp_client(
            input_queue=self.xmpp_bridge_queue,
            output_queue=self.output_queue,
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
