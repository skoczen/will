import requests

from will import settings


class RoomMixin(object):
    @property
    def available_rooms(self):
        if not hasattr(self, "_available_rooms"):
            self._available_rooms = self.load('hipchat_rooms', None)
            if not self._available_rooms:
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

    def get_room_from_name_or_id(self, name_or_id):
        for name, room in self.available_rooms.items():
            if name_or_id == name:
                return room
            if name_or_id == room["xmpp_jid"]:
                return room
            if name_or_id == room["room_id"]:
                return room
        return None

