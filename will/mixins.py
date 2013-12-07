import datetime
import json
import re
import requests
import time

from natural.date import day
import parsedatetime.parsedatetime as pdt

import settings

class NaturalTimeMixin(object):

    def strip_leading_zeros(self, date_str):
        date_str = date_str.replace(":0", "__&&")
        date_str = re.sub("0*(\d+)", "\g<1>", date_str)
        date_str = date_str.replace("__&&", ":0")
        return date_str

    def parse_natural_time(self, time_str):
        cal = pdt.Calendar()
        time_tuple = cal.parse(time_str)[0][:-2]

        return datetime.datetime(*time_tuple)

    def to_natural_day(self, dt):
        day_str = day(dt)
        return self.strip_leading_zeros(day_str)

    def to_natural_day_and_time(self, dt):
        if dt.minute == 0:
            time_str = dt.strftime("%I%p").lower()
        else:
            time_str = dt.strftime("%I:%M%p").lower()
        full_str = "%s at %s" % (self.to_natural_day(dt), time_str)
        return self.strip_leading_zeros(full_str)

class RoomMixin(object):
    @property
    def available_rooms(self):
        if not hasattr(self, "_available_rooms"):
            self._available_rooms = self.load('hipchat_rooms', None)
            if not self._available_rooms:
                import settings
                self._available_rooms = {}
                url = "https://api.hipchat.com/v1/rooms/list?auth_token=%s" % (settings.WILL_TOKEN,)
                r = requests.get(url)
                for room in r.json()["rooms"]:
                    self._available_rooms[room["name"]] = room

                self.save("hipchat_rooms", self._available_rooms)

        return self._available_rooms

    def get_room_by_jid(self, jid):
        for name, room in self.available_rooms.items():
            if room["xmpp_jid"] == jid:
                return room
        return None

    def get_room_from_message(self, message):
        return self.get_room_by_jid(message.getMucroom())


class RosterMixin(object):
    @property
    def internal_roster(self):
        if not hasattr(self, "_internal_roster"):
            self._internal_roster = self.load('will_roster', {})
        return self._internal_roster

    def get_user_by_full_name(self, name):
        for jid, info in self.internal_roster.items():
            if info["name"] == name:
                return info
        return None

    def get_user_by_jid(self, jid):

        if jid in self.internal_roster:
            return self.internal_roster[jid]

        return None

    def get_user_from_message(self, message):
        if message["type"] == "groupchat":
            return self.get_user_by_full_name(message["mucnick"])
        elif message['type'] in ('chat', 'normal'):
            jid = ("%s" % message["from"]).split("/")[0]
            return self.get_user_by_jid(jid)
        else:
            return None


class ScheduleMixin(object):

    def get_schedule_list(self):
        return self.load('will_schedule_list', [])

    def add_direct_message_to_schedule(self, when, content, message, *args, **kwargs):
        target_user = self.get_user_from_message(message)
        self.add_to_schedule(when, {
            "type": "direct_message",
            "content": content,
            "target_jid": target_user["jid"],
            "args": args,
            "kwargs": kwargs,
        })

    def add_room_message_to_schedule(self, when, content, room, *args, **kwargs):
        self.add_to_schedule(when, {
            "type": "room_message",
            "content": content,
            "room": room,
            "args": args,
            "kwargs": kwargs,
        })

    def add_to_schedule(self, when, item):
        while self.load("scheduler_lock", False) or self.load("scheduler_add_lock", False):
            print "waiting for lock to clear"
            time.sleep(0.5)

        self.save("scheduler_add_lock", True)
        sched_list = self.get_schedule_list()
        item["when"] = when
        sched_list.append(item)
        self.save('will_schedule_list', sched_list)
        self.save("scheduler_add_lock", False)

    def remove_from_schedule(self, index):
        # If this is ever called from anywhere outside the scheduler_lock, it needs its own lock.
        
        sched_list = self.get_schedule_list()
        del sched_list[index]
        self.save('will_schedule_list', sched_list)


ROOM_NOTIFICATION_URL = "https://api.hipchat.com/v2/room/%(room_id)s/notification?auth_token=%(token)s"
ROOM_TOPIC_URL = "https://api.hipchat.com/v2/room/%(room_id)s/topic?auth_token=%(token)s"
PRIVATE_MESSAGE_URL = "https://api.hipchat.com/v2/user/%(user_id)s/message?auth_token=%(token)s"
SET_TOPIC_URL = "https://api.hipchat.com/v2/room/%(room_id)s/topic?auth_token=%(token)s"
USER_DETAILS_URL = "https://api.hipchat.com/v2/user/%(user_id)s?auth_token=%(token)s"

class HipChatAPIMixin(object):

    def send_direct_message(self, user_id, message_body):
        # https://www.hipchat.com/docs/apiv2/method/private_message_user
        url = PRIVATE_MESSAGE_URL % {"user_id": user_id, "token": settings.WILL_V2_TOKEN}
        data = {"message": message_body}
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        requests.post(url, headers=headers, data=json.dumps(data))

    def send_direct_message_reply(self, message, message_body):
        message.reply(message_body).send()

    def send_room_message(self, room_id, message_body, html=False, color="green", notify=False, **kwargs):
        if kwargs:
            logging.warn("Unknown keyword args for send_room_message: %s" % kwargs)
        
        format = "text"
        if html:
            format = "html"

        try:
            # https://www.hipchat.com/docs/apiv2/method/send_room_notification
            url = ROOM_NOTIFICATION_URL % {"room_id": room_id, "token": settings.WILL_V2_TOKEN}
            
            data = {
                "message": message_body,
                "message_format": format,
                "color": color,
                "notify": notify,

            }
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            requests.post(url, headers=headers, data=json.dumps(data))
        except:
            import traceback; traceback.print_exc();

    def set_room_topic(self, room_id, topic):
        try:
            # https://www.hipchat.com/docs/apiv2/method/send_room_notification
            url = ROOM_TOPIC_URL % {"room_id": room_id, "token": settings.WILL_V2_TOKEN}
            
            data = {
                "topic": topic,
            }
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            requests.put(url, headers=headers, data=json.dumps(data))
        except:
            import traceback; traceback.print_exc();

    def get_hipchat_user(self, user_id):
        url = USER_DETAILS_URL % {"user_id": user_id, "token": settings.WILL_V2_TOKEN}
        r = requests.get(url)
        return r.json()
