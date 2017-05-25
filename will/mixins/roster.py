import logging
from ..utils import is_admin
from ..acl import is_acl_allowed

from will import settings


class RosterMixin(object):
    @property
    def people(self):
        if not hasattr(self, "_people"):
            self._people = self.load('will_hipchat_people', {})
        return self._people

    @property
    def internal_roster(self):
        logging.warn(
            "mixin.internal_roster has been deprecated.  Please use mixin.people instead. "
            "internal_roster will be removed at the end of 2017"
        )
        return self.people

    def get_user_by_full_name(self, name):
        # TODO: Fix this better for shell, etc
        for jid, info in self.people.items():
            if info["name"] == name:
                return info

        return {"jid": "123", "hipchat_id": "123"}

    def get_user_by_nick(self, nick):
        for jid, info in self.people.items():
            if info["nick"] == nick:
                return info
        return {"jid": "123", "hipchat_id": "123"}

    def get_user_by_jid(self, jid):
        if jid in self.people:
            return self.people[jid]

        return {"jid": "123", "hipchat_id": "123"}

    def get_user_from_message(self, message):
        if message["type"] == "groupchat":
            return self.get_user_by_full_name(message["mucnick"])
        elif message['type'] in ('chat', 'normal'):
            jid = ("%s" % message["from"]).split("/")[0]
            return self.get_user_by_jid(jid)
        else:
            return {"jid": "123", "hipchat_id": "123"}

    def message_is_from_admin(self, message):
        nick = self.get_user_from_message(message)['nick']
        return is_admin(nick)

    def message_is_allowed(self, message, acl):
        nick = self.get_user_from_message(message)['nick']
        return is_acl_allowed(nick, acl)

    def get_user_by_hipchat_id(self, id):
        for jid, info in self.people.items():
            if info["hipchat_id"] == id:
                return info
        return None
