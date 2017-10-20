import logging
import re
import threading
import traceback
from sleekxmpp import ClientXMPP
from sleekxmpp.exceptions import IqError, IqTimeout

from will import settings
from will.utils import Bunch
from will.mixins import RosterMixin, RoomMixin, HipChatMixin


class WillXMPPClientMixin(ClientXMPP, RosterMixin, RoomMixin, HipChatMixin):

    def start_xmpp_client(self):
        logger = logging.getLogger(__name__)
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

        # Property boostraps the list
        for r in settings.ROOMS:
            if r != "":
                if not hasattr(self, "default_room"):
                    self.default_room = r

                try:
                    self.rooms.append(self.available_rooms[r])
                except KeyError:
                    logger.error(
                        u'"%s" is not an available room, ask'
                        ' "@%s what are the rooms?" for the full list.',
                        r,
                        settings.HANDLE,
                    )

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
        self.update_will_roster_and_rooms()

        for r in self.rooms:
            if "xmpp_jid" in r:
                self.plugin['xep_0045'].joinMUC(r["xmpp_jid"], self.nick, wait=True)

    def update_will_roster_and_rooms(self):
        internal_roster = self.load('will_roster', {})
        # Loop through the connected rooms
        for roster_id in self.roster:

            cur_roster = self.roster[roster_id]
            # Loop through the users in a given room
            for user_id in cur_roster:
                user_data = cur_roster[user_id]
                if user_data["name"] != "":
                    # If we don't have this user in the internal_roster, add them.
                    if not user_id in internal_roster:
                        internal_roster[user_id] = Bunch()

                    hipchat_id = user_id.split("@")[0].split("_")[1]
                    # Update their info
                    internal_roster[user_id].update({
                        "name": user_data["name"],
                        "jid": user_id,
                        "hipchat_id": hipchat_id,
                    })

                    # If we don't have a nick yet, pull it and mention_name off the master user list.
                    if not hasattr(internal_roster[user_id], "nick") and hipchat_id in self.full_hipchat_user_list:
                        user_data = self.full_hipchat_user_list[hipchat_id]
                        internal_roster[user_id].nick = user_data["mention_name"]
                        internal_roster[user_id].mention_name = user_data["mention_name"]

                    # If it's me, save that info!
                    if internal_roster[user_id].get("name", "") == self.nick:
                        self.me = internal_roster[user_id]

        self.save("will_roster", internal_roster)

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
        if (
            # I've been asked to listen to my own messages
            self.some_listeners_include_me or
            # or we're in a 1 on 1 chat and I didn't send it
            (msg['type'] in ('chat', 'normal') and self.real_sender_jid(msg) != self.me.jid) or
            # we're in group chat and I didn't send it
            (msg["type"] == "groupchat" and msg['mucnick'] != self.nick)
        ):
                body = msg["body"].strip()

                sent_directly_to_me = False
                # If it's sent directly to me, strip off "@will" from the start.
                if body[:len(self.handle) + 1].lower() == ("@%s" % self.handle).lower():
                    body = body[len(self.handle) + 1:].strip()
                    msg["body"] = body

                    sent_directly_to_me = True

                # Make the message object a bit friendlier
                msg.room = self.get_room_from_message(msg)
                msg.sender = self.get_user_from_message(msg)

                for l in self.message_listeners:
                    search_matches = l["regex"].search(body)
                    if (
                            # The search regex matches and
                            search_matches and
                            # It's not from me, or this search includes me, and
                            (msg['mucnick'] != self.nick or l["include_me"]) and
                            # I'm mentioned, or this is an overheard, or we're in a 1-1
                            (msg['type'] in ('chat', 'normal') or not l["direct_mentions_only"] or
                                self.handle_regex.search(body) or sent_directly_to_me) and
                            # It's from admins only and sender is an admin, or it's not from admins only
                            ((l['admin_only'] and self.message_is_from_admin(msg)) or (not l['admin_only'])) and
                            # It's available only to the members of one or more ACLs, or no ACL in use
                            ((len(l['acl']) > 0 and self.message_is_allowed(msg, l['acl'])) or (len(l['acl']) == 0))
                    ):
                        try:
                            thread_args = [msg, ] + l["args"]

                            def fn(listener, args, kwargs):
                                try:
                                    listener["fn"](*args, **kwargs)
                                except:
                                    content = "I ran into trouble running %s.%s:\n\n%s" % (
                                        listener["class_name"],
                                        listener["function_name"],
                                        traceback.format_exc(),
                                    )

                                    if msg is None or msg["type"] == "groupchat":
                                        if msg.sender and "nick" in msg.sender:
                                            content = "@%s %s" % (msg.sender["nick"], content)
                                        self.send_room_message(msg.room["room_id"], content, color="red")
                                    elif msg['type'] in ('chat', 'normal'):
                                        self.send_direct_message(msg.sender["hipchat_id"], content)

                            thread = threading.Thread(target=fn, args=(l, thread_args, search_matches.groupdict()))
                            thread.start()
                        except:
                            logging.critical(
                                "Error running %s.  \n\n%s\nContinuing...\n",
                                l["function_name"],
                                traceback.format_exc()
                            )
