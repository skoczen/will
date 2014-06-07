from will import settings
from ..utils import is_admin


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

    def message_is_from_admin(self, message):
        nick = self.get_user_from_message(message)['nick']
        return is_admin(nick)
