# -*- coding: utf-8 -*-
from will import settings


def get_acl_members(acl):
    acl_members = []
    acl = acl.lower()

    if getattr(settings, "ACL", None):
        try:
            # Case-insensitive checks
            for k in settings.ACL.keys():
                if k.lower() == acl:
                    acl_members = settings.ACL[k]
                    break
        except AttributeError:
            pass

    return acl_members


def is_acl_allowed(nick, acl):
    for a in acl:
        acl_members = get_acl_members(a)
        if nick in acl_members or nick.lower() in [x.lower() for x in acl_members]:
            return True

    return False
