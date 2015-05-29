# -*- coding: utf-8 -*-
from . import settings


def get_acl_settings_name(acl):
    return "ACL_%s" % acl.upper()


def get_acl_members(acl):
    acl_name = get_acl_settings_name(acl)
    try:
        acl_members = eval("settings.%s" % acl_name)
    except AttributeError:
        acl_members = []

    return acl_members


def is_acl_allowed(nick, acl):
    for a in acl:
        acl_members = get_acl_members(a)
        if nick.lower() in acl_members:
            return True

    return False
