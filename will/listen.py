import datetime
import logging
import re
import requests
from sleekxmpp import ClientXMPP
import settings

class WillXMPPClientMixin(ClientXMPP):

    def start_xmpp_client(self):
        ClientXMPP.__init__(self, settings.WILL_USERNAME, settings.WILL_PASSWORD)
        self.rooms = []
        self.available_rooms = {}

        if hasattr(settings, "WILL_DEFAULT_ROOM"):
            self.default_room = settings.WILL_DEFAULT_ROOM

        url = "https://api.hipchat.com/v1/rooms/list?auth_token=%s" % (settings.WILL_TOKEN,)
        r = requests.get(url)
        for room in r.json()["rooms"]:
            self.available_rooms[room["name"]] = room

        self.save("hipchat_rooms", self.available_rooms)

        for r in settings.WILL_ROOMS:
            if r != "":
                if not hasattr(self, "default_room"):
                    self.default_room = r

                self.rooms.append(self.available_rooms[r])

        self.nick = settings.WILL_NAME
        self.handle = settings.WILL_HANDLE
        self.handle_regex = re.compile("@%s" % self.handle)
        
        self.whitespace_keepalive = True
        self.whitespace_keepalive_interval = 30

        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message)
        self.add_event_handler("groupchat_message", self.room_message)
        
        self.register_plugin('xep_0045') # MUC

    def session_start(self, event):
        print "session_start event happened"
        self.initialized_at = datetime.datetime.now()
        self.initial_ignoring_done = False
        
        self.send_presence()
        self.get_roster()
        self.update_will_roster_and_rooms()
        for r in self.rooms:
            self.plugin['xep_0045'].joinMUC(r["xmpp_jid"], self.nick, wait=True)

    def update_will_roster_and_rooms(self):
        internal_roster = self.load('will_roster', {})
        for roster_id in self.roster:
            cur_roster = self.roster[roster_id]
            for user_id in cur_roster:
                user_data = cur_roster[user_id]
                if user_data["name"] != "":
                    if not user_id in internal_roster:
                        internal_roster[user_id] = {}

                    hipchat_id = user_id.split("@")[0].split("_")[1]
                    internal_roster[user_id].update({
                        "name": user_data["name"],
                        "jid": user_id,
                        "hipchat_id": hipchat_id,
                    })

                    if not "nick" in internal_roster[user_id]:
                        url = "https://api.hipchat.com/v2/user/%s?auth_token=%s" % (hipchat_id, settings.WILL_V2_TOKEN)
                        r = requests.get(url)
                        nick = r.json()["mention_name"]
                        internal_roster[user_id]["nick"] = nick


    def room_message(self, msg):
        # Ugly hack to ignore the room backlog when joining.
        if not self.initial_ignoring_done:
            if (datetime.datetime.now() - self.initialized_at).total_seconds() > 4:
                self.initial_ignoring_done = True
        
        if self.initial_ignoring_done:
            self._handle_message_listeners(msg)


    def message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            self._handle_message_listeners(msg)

    def _handle_message_listeners(self, msg):
        if (self.some_listeners_include_me  # I've been asked to listen to my own messages
            or msg['type'] in ('chat', 'normal')  # or we're in a 1 on 1 chat
            or msg['mucnick'] != self.nick):  # or I didn't send it
                body = msg["body"]
                for l in self.message_listeners:
                    search_matches = l["regex"].search(body)
                    if (search_matches  # The search regex matches and
                        and (msg['mucnick'] != self.nick or l["include_me"])  # It's not from me, or this search includes me, and
                        and (msg['type'] in ('chat', 'normal') or not l["direct_mentions_only"] or self.handle_regex.search(body))  # I'm mentioned, or this is an overheard, or we're in a 1-1
                    ):
                        l["fn"](msg, *l["args"], **search_matches.groupdict())

