# -*- coding: utf-8 -*-
import logging
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


def get_acl_groups():
    acl_groups = []
    if getattr(settings, "ACL", None):
        # Case-insensitive checks
        for k in settings.ACL.keys():
            print(k.lower())
            acl_groups.append(k.lower())

        return acl_groups


def is_acl_allowed(nick, acl):
    if not getattr(settings, "ACL", None):
        logging.warn(
            "%s was just allowed to perform actions in %s because no ACL settings exist. This can be a security risk." % (
                nick,
                acl,
            )
        )
        return True
    for a in acl:
        acl_members = get_acl_members(a)
        if nick in acl_members or nick.lower() in [x.lower() for x in acl_members]:
            return True

    return False


def test_acl(message, acl):
    try:
        if settings.DISABLE_ACL:
            return True

        allowed = is_acl_allowed(message.sender.handle, acl)
        if allowed:
            return True
        if hasattr(message, "data") and hasattr(message.data, "backend_supports_acl"):
            if not message.data.backend_supports_acl:
                logging.warn(
                    "%s was just allowed to perform actions in %s because the backend does not support ACL.  This can be a security risk." % (
                        message.sender.handle,
                        acl,
                    ) +
                    "To fix this, set ACL groups in your config.py, or set DISABLE_ACL = True"
                )
                return True
    except:
        pass

    return False
