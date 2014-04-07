import requests

from will import settings


class RoomMixin(object):
    def update_available_rooms(self):
        self._available_rooms = {}
        url = "https://api.hipchat.com/v2/room?auth_token=%s" % (settings.WILL_V2_TOKEN,)
        rooms = requests.get(url).json()

        for room in rooms["items"]:
            url = room["links"]["self"] + "/?auth_token=%s;expand=xmpp_jid" % (settings.WILL_V2_TOKEN,)
            room_details = requests.get(url).json()
            # map certain hipchat API v2 kv pairs to their v1 equivalent
            room["xmpp_jid"] = room_details["xmpp_jid"]
            room["room_id"] = room["id"]
            self._available_rooms[room["name"]] = room

        self.save("hipchat_rooms", self._available_rooms)

    @property
    def available_rooms(self):
        if not hasattr(self, "_available_rooms"):
            self._available_rooms = self.load('hipchat_rooms', None)
            if not self._available_rooms:
                self.update_available_rooms()

        return self._available_rooms

    def get_room_by_jid(self, jid):
        for name, room in self.available_rooms.items():
            if room["xmpp_jid"] == jid:
                return room
        return None

    def get_room_from_message(self, message):
        return self.get_room_by_jid(message.getMucroom())

    def get_room_from_name_or_id(self, name_or_id):
        for name, room in self.available_rooms.items():
            if name_or_id == name:
                return room
            if name_or_id == room["xmpp_jid"]:
                return room
            if name_or_id == room["room_id"]:
                return room
        return None

