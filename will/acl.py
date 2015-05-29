# -*- coding: utf-8 -*-
from . import settings


def get_acl_members(acl):
    acl_members = []
    acl = acl.lower()

    if getattr(settings, "ACL", None):
        try:
            # Case-insensitive checks
            for k, v in settings.ACL.items():
                if k.lower() == acl:
                    acl_members = settings.ACL[k]
                    break
        except AttributeError:
            pass

    return acl_members


def is_acl_allowed(nick, acl):
    nick = nick.lower()
    for a in acl:
        acl_members = get_acl_members(a)
        if nick in acl_members:
            return True

    return False
