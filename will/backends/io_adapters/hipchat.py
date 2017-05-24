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
from .xmpp import WillXMPPClientMixin
from will.mixins import RoomMixin, StorageMixin
# from mixins import ScheduleMixin, StorageMixin, ErrorMixin,\
#    26      RoomMixin, PluginModulesLibraryMixin, EmailMixin
from multiprocessing import Process, Queue
from will.backends.io_adapters.base import Event, Message
from multiprocessing.queues import Empty


ROOM_NOTIFICATION_URL = "https://%(server)s/v2/room/%(room_id)s/notification?auth_token=%(token)s"
ROOM_TOPIC_URL = "https://%(server)s/v2/room/%(room_id)s/topic?auth_token=%(token)s"
PRIVATE_MESSAGE_URL = "https://%(server)s/v2/user/%(user_id)s/message?auth_token=%(token)s"
SET_TOPIC_URL = "https://%(server)s/v2/room/%(room_id)s/topic?auth_token=%(token)s"
USER_DETAILS_URL = "https://%(server)s/v2/user/%(user_id)s?auth_token=%(token)s"
ALL_USERS_URL = ("https://%(server)s/v2/user?auth_token=%(token)s&start-index"
                 "=%(start_index)s&max-results=%(max_results)s")

UNSURE_REPLIES = [
    "Hmm.  I'm not sure what to say.",
    "I didn't understand that.",
    "I heard you, but I'm not sure what to do.",
    "Darn.  I'm not sure what that means.  Maybe you can teach me?",
    "I really wish I knew how to do that.",
    "Hm. I understood you, but I'm not sure what to do.",
]


class HipChatBackend(IOBackend, RoomMixin, StorageMixin):
    friendly_name = "HipChat"
    internal_name = "will.backends.io_adapters.hipchat"

    def send_direct_message(self, user_id, message_body, html=False, notify=False, **kwargs):
        # user_id = settings.USERNAME.split('@')[0].split('_')[1]

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
    def full_hipchat_user_list(self):
        if not hasattr(self, "_full_hipchat_user_list"):
            full_roster = {}

            # Grab the first roster page, and populate full_roster
            url = ALL_USERS_URL % {"server": settings.HIPCHAT_SERVER,
                                   "token": settings.V2_TOKEN,
                                   "start_index": 0,
                                   "max_results": 1000}
            r = requests.get(url, **settings.REQUESTS_OPTIONS)
            for user in r.json()['items']:
                full_roster["%s" % (user['id'],)] = user

            # Keep going through the next pages until we're out of pages.
            while 'next' in r.json()['links']:
                url = "%s&auth_token=%s" % (r.json()['links']['next'], settings.V2_TOKEN)
                r = requests.get(url, **settings.REQUESTS_OPTIONS)

                for user in r.json()['items']:
                    full_roster["%s" % (user['id'],)] = user

            self._full_hipchat_user_list = full_roster
        return self._full_hipchat_user_list

    def handle_incoming_event(self, event):
        # Handled in XMPP (for now).
        pass

    def handle_outgoing_event(self, event):
        kwargs = {}
        if hasattr(event, "kwargs"):
            kwargs.update(event.kwargs)

        if event.type in ["say", "reply"]: 
            event.content = re.sub(r'>\s+<', '><', event.content)

            if hasattr(event, "source_message") and event.source_message:
                if event.source_message.hipchat_message.type == "groupchat":
                    self.send_room_message(
                        event.source_message.hipchat_message.room.room_id,
                        event.content,
                        **kwargs
                    )
                else:
                    event.source_message
                    user_id = event.source_message.hipchat_message.sender["hipchat_id"]
                    self.send_direct_message(
                        user_id,
                        event.content,
                        **kwargs
                    )
            else:
                # Came from webhook/etc
                if "room" in kwargs:
                    print kwargs
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
            if event.source_message.hipchat_message.type == "groupchat":
                self.send_room_message(
                    event.source_message.hipchat_message.room.room_id,
                    random.choice(UNSURE_REPLIES),
                    **kwargs
                )
            else:
                self.send_direct_message(
                    event.source_message.hipchat_message.sender["hipchat_id"],
                    random.choice(UNSURE_REPLIES),
                    **kwargs
                )

    def bootstrap(self):
        self.client = WillXMPPClientMixin("%s/bot" % settings.USERNAME, settings.PASSWORD)
        self.client.start_xmpp_client(
            input_queue=self.input_queue,
            output_queue=self.output_queue,
            backend_name=self.internal_name,
        )
        self.client.connect()

        self.xmpp_thread = Process(target=self.client.process, kwargs={"block": True})
        self.xmpp_thread.start()

    def terminate(self):
        if hasattr(self, "xmpp_thread"):
            self.xmpp_thread.terminate()
            while self.xmpp_thread.is_alive():
                time.sleep(0.2)
