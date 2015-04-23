from datetime import datetime
import json
import requests

from will import settings
from will.utils import Bunch

V1_TOKEN_URL = "https://%(server)s/v1/rooms/list?auth_token=%(token)s"
V2_TOKEN_URL = "https://%(server)s/v2/room?auth_token=%(token)s"


class Room(Bunch):

    @property
    def history(self):
        payload = {"auth_token": settings.V2_TOKEN}
        room_id = int(self['id'])
        response = requests.get("https://{1}/v2/room/{0}/history".format(str(room_id),
                                                                         settings.HIPCHAT_SERVER),
                                params=payload, **settings.REQUESTS_OPTIONS)
        data = json.loads(response.text)['items']
        for item in data:
            item['date'] = datetime.strptime(item['date'][:-13], "%Y-%m-%dT%H:%M:%S")
        return data

    @property
    def participants(self):
        payload = {"auth_token": settings.V2_TOKEN}
        room_id = int(self['id'])
        response = requests.get(
            "https://{1}/v2/room/{0}/participant".format(
                str(room_id),
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


class RoomMixin(object):
    def update_available_rooms(self, q=None):
        self._available_rooms = {}
        # Use v1 token to grab a full room list if we can (good to avoid rate limiting)
        if hasattr(settings, "V1_TOKEN"):
            url = V1_TOKEN_URL % {"server": settings.HIPCHAT_SERVER,
                                  "token": settings.V1_TOKEN}
            r = requests.get(url, **settings.REQUESTS_OPTIONS)
            if r.status_code == requests.codes.unauthorized:
                raise Exception("V1_TOKEN authentication failed with HipChat")
            for room in r.json()["rooms"]:
                self._available_rooms[room["name"]] = room
        # Otherwise, grab 'em one-by-one via the v2 api.
        else:
            url = V2_TOKEN_URL % {"server": settings.HIPCHAT_SERVER,
                                  "token": settings.V2_TOKEN}
            resp = requests.get(url, **settings.REQUESTS_OPTIONS)
            if resp.status_code == requests.codes.unauthorized:
                raise Exception("V2_TOKEN authentication failed with HipChat")
            rooms = resp.json()

            for room in rooms["items"]:
                url = room["links"]["self"] + "?auth_token=%s;expand=xmpp_jid" % (settings.V2_TOKEN,)
                room_details = requests.get(url, **settings.REQUESTS_OPTIONS).json()
                # map missing hipchat API v1 data
                for k, v in room_details.items():
                    if k not in room:
                        room[k] = room_details[k]
                room["room_id"] = room["id"]
                self._available_rooms[room["name"]] = Room(**room)

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
        for name, room in self.available_rooms.items():
            if "xmpp_jid" in room and room["xmpp_jid"] == jid:
                return room
        return None

    def get_room_from_message(self, message):
        return self.get_room_by_jid(message.getMucroom())

    def get_room_from_name_or_id(self, name_or_id):
        for name, room in self.available_rooms.items():
            if name_or_id == name:
                return room
            if "xmpp_jid" in room and name_or_id == room["xmpp_jid"]:
                return room
            if "room_id" in room and name_or_id == room["room_id"]:
                return room
        return None
