import re
from will import settings
from will.decorators import require_settings
from will.utils import Bunch
from .base import GenerationBackend, GeneratedOption


class RegexBackend(GenerationBackend):

    def do_generate(self, event):
        exclude_list = ["fn", ]
        matches = []

        message = event.data
        for name, l in self.bot.message_listeners.items():
            search_matches = l["regex"].search(message.content)
            if (
                    # The search regex matches and
                    search_matches

                    # It's not from me, or this search includes me, and
                    and (
                        message.will_said_it is False or
                        ("include_me" in l and l["include_me"])
                    )

                    # I'm mentioned, or this is an overheard, or we're in a 1-1
                    and (
                        message.is_private_chat or
                        ("direct_mentions_only" not in l or not l["direct_mentions_only"]) or
                        message.is_direct
                    )

                    # TOOD: Get ACL working again.
                    # It's from admins only and sender is an admin, or it's not from admins only
                    # and ((l['admin_only'] and self.message_is_from_admin(msg)) or (not l['admin_only']))
                    # # It's available only to the members of one or more ACLs, or no ACL in use
                    # and ((len(l['acl']) > 0 and self.message_is_allowed(msg, l['acl'])) or (len(l['acl']) == 0))
            ):
                context = Bunch()
                for k, v in l.items():
                    if k not in exclude_list:
                        context[k] = v
                context.search_matches = search_matches.groupdict()

                o = GeneratedOption(context=context, backend="regex", score=100)
                matches.append(o)

        return matches
