# -*- coding: utf-8 -*-
from . import settings


def get_acl_members(acl):
    acl_members = []

    if getattr(settings, "ACL", None) and acl in settings.ACL:
        try:
            acl_members = settings.ACL[acl]
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
