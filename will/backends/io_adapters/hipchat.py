import json
import logging
import requests
import traceback

from will import settings
from .base import IOBackend

ROOM_NOTIFICATION_URL = "https://%(server)s/v2/room/%(room_id)s/notification?auth_token=%(token)s"
ROOM_TOPIC_URL = "https://%(server)s/v2/room/%(room_id)s/topic?auth_token=%(token)s"
PRIVATE_MESSAGE_URL = "https://%(server)s/v2/user/%(user_id)s/message?auth_token=%(token)s"
SET_TOPIC_URL = "https://%(server)s/v2/room/%(room_id)s/topic?auth_token=%(token)s"
USER_DETAILS_URL = "https://%(server)s/v2/user/%(user_id)s?auth_token=%(token)s"
ALL_USERS_URL = ("https://%(server)s/v2/user?auth_token=%(token)s&start-index"
                 "=%(start_index)s&max-results=%(max_results)s")


class HipChatBackend(IOBackend):
    friendly_name = "HipChat"
    use_stdin = False

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

    def send_direct_message_reply(self, message, message_body):
        try:
            message.reply(message_body).send()
        except:
            logging.critical("Error in send_direct_message_reply: \n%s" % traceback.format_exc())

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

    def start(self, name, incoming_queue, output_queue):
        self.name = name
        self.incoming_queue = incoming_queue
        self.output_queue = output_queue

        # Sort this out.
        # bootstrapped = False
        # try:
        #     self.xmpp_thread = Process(target=self.bootstrap_xmpp)
        #     self.output_backend = HipChatBackend()
        #     self.start_xmpp_client()
        #     sorted_help = {}
        #     # self.send_direct_message = self.output_backend.send_direct_message
        #     # self.send_direct_message_reply = self.output_backend.send_direct_message_reply
        #     # self.send_room_message = self.output_backend.send_room_message
        #     # self.set_room_topic = self.output_backend.set_room_topic
        #     # self.get_user = self.output_backend.get_hipchat_user
        #     # self.get_user_list = self.output_backend.full_hipchat_user_list

        #     for k, v in self.help_modules.items():
        #         sorted_help[k] = sorted(v)

        #     self.save("help_modules", sorted_help)
        #     self.save("all_listener_regexes", self.all_listener_regexes)
        #     self.connect()
        #     bootstrapped = True
        # except Exception, e:
        #     self.startup_error("Error bootstrapping xmpp", e)
        # if bootstrapped:
        #     show_valid("Chat client started.")
        #     show_valid("Will is running.")
        #     self.process(block=True)
