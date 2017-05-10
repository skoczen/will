import requests

from will import settings
from will.decorators import require_settings
from .base import ExecutionBackend


class AllBackend(ExecutionBackend):

    def execute(self, message):
        print "in execution"
        try:
            for m in message.generation_options:
                print "bot_fn"
                print m
                print m.__dict__
                print m.context.full_method_name
                print self.bot
                live_listener = self.bot.message_listeners[m.context.full_method_name]

                thread_args = [message, ] + m.context["args"]
                live_listener["fn"](*thread_args, **m.context.search_matches)
                print "did stuff"
            return {}
        except:
            import traceback; traceback.print_exc();