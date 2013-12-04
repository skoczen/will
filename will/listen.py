import datetime
import logging
from sleekxmpp import ClientXMPP
import settings

class WillClient(ClientXMPP):

    def __init__(self):
        ClientXMPP.__init__(self, settings.WILL_USERNAME, settings.WILL_PASSWORD)
        self.rooms = []

        if hasattr(settings, "WILL_DEFAULT_ROOM"):
            self.default_room = settings.WILL_DEFAULT_ROOM

        for r in settings.WILL_ROOMS:
            if r != "":
                if not hasattr(self, "default_room"):
                    self.default_room = r

                self.rooms.append(r)

        self.nick = settings.WILL_NAME

        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message)
        self.add_event_handler("groupchat_message", self.room_message)
        
        self.register_plugin('xep_0004') # Data Forms
        self.register_plugin('xep_0045') # MUC
        self.register_plugin('xep_0060') # PubSub

    def session_start(self, event):
        self.send_presence()
        self.get_roster()
        self.initialized_at = datetime.datetime.now()
        self.initial_messages_ignored = False
        for r in self.rooms:
            self.plugin['xep_0045'].joinMUC(r, self.nick, wait=True)

    def room_message(self, msg):
        # Ugly hack to ignore the room backlog when joining.
        if not self.initial_messages_ignored:
            if (datetime.datetime.now() - self.initialized_at).total_seconds() > 2:
                self.initial_messages_ignored = True
        
        if self.initial_messages_ignored:
            print msg["from"]
            print msg["type"]
            if msg['mucnick'] != self.nick:  #  and self.nick in msg['body']
                self.send_message(mto=msg['from'].bare,
                              mbody="I heard that, %s." % msg['mucnick'],
                              mtype='groupchat')


    def message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            msg.reply("Thanks for sending\n%(body)s" % msg).send()


