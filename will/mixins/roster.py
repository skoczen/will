from ..utils import is_admin
from ..acl import is_acl_allowed


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

    def get_user_by_nick(self, nick):
        for jid, info in self.internal_roster.items():
            if info["nick"] == nick:
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

    def message_is_from_admin(self, message):
        nick = self.get_user_from_message(message)['nick']
        return is_admin(nick)

    def message_is_allowed(self, message, acl):
        nick = self.get_user_from_message(message)['nick']
        return is_acl_allowed(nick, acl)

    def get_user_by_hipchat_id(self, id):
        for jid, info in self.internal_roster.items():
            if info["hipchat_id"] == id:
                return info
        return None
