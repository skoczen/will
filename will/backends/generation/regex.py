from will import settings
from will.decorators import require_settings
from will.utils import Bunch
from .base import GenerationBackend, GeneratedOption


class RegexBackend(GenerationBackend):

    def do_generate(self, message):
        print "regex generate"
        exclude_list = ["fn",]
        matches = []

        for name, l in self.bot.message_listeners.items():
            search_matches = l["regex"].search(message.body)
            if (
                    search_matches  # The search regex matches and
                    # # It's not from me, or this search includes me, and
                    # and (msg['mucnick'] != self.nick or l["include_me"])
                    # # I'm mentioned, or this is an overheard, or we're in a 1-1
                    # and (msg['type'] in ('chat', 'normal') or not l["direct_mentions_only"] or
                    #      self.handle_regex.search(body) or sent_directly_to_me)
                    # # It's from admins only and sender is an admin, or it's not from admins only
                    # and ((l['admin_only'] and self.message_is_from_admin(msg)) or (not l['admin_only']))
                    # # It's available only to the members of one or more ACLs, or no ACL in use
                    # and ((len(l['acl']) > 0 and self.message_is_allowed(msg, l['acl'])) or (len(l['acl']) == 0))
            ):
                context = Bunch()
                for k, v in l.items():
                    if k not in exclude_list:
                        context[k] = v
                context.search_matches = search_matches.groupdict()

                o = GeneratedOption(context=context, backend="regex")
                matches.append(o)

                # try:
                #     thread_args = [msg, ] + l["args"]

                #     def fn(listener, args, kwargs):
                #         try:
                #             listener["fn"](*args, **kwargs)
                #         except:
                #             content = "I ran into trouble running %s.%s:\n\n%s" % (
                #                 listener["class_name"],
                #                 listener["function_name"],
                #                 traceback.format_exc(),
                #             )

                #             if msg is None or msg["type"] == "groupchat":
                #                 if msg.sender and "nick" in msg.sender:
                #                     content = "@%s %s" % (msg.sender["nick"], content)
                #                 self.send_room_message(msg.room["room_id"], content, color="red")
                #             elif msg['type'] in ('chat', 'normal'):
                #                 self.send_direct_message(msg.sender["hipchat_id"], content)

                #     thread = threading.Thread(target=fn, args=(l, thread_args, search_matches.groupdict()))
                #     thread.start()
        return matches
