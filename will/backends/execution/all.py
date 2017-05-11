import logging
import traceback
import requests

from will import settings
from will.decorators import require_settings
from will.plugin import Event
from .base import ExecutionBackend


class AllBackend(ExecutionBackend):

    def execute(self, message):
        try:
            had_one_reply = False
            for m in message.generation_options:
                # print "bot_fn"
                # print m
                # print m.__dict__
                # print m.context.full_method_name
                # print self.bot
                live_listener = self.bot.message_listeners[m.context.full_method_name]

                thread_args = [message, ] + m.context["args"]
                live_listener["fn"](*thread_args, **m.context.search_matches)
                # print "did stuff"
                had_one_reply = True
            if not had_one_reply:
                self.bot.queues.io.output[message.backend].put(Event(
                    type="no_response",
                    content=None,
                    source_message=message,
                ))

            return {}
        except:
            logging.critical(
                "Error running %s.  \n\n%s\nContinuing...\n" % (
                    live_listener["function_name"],
                    traceback.format_exc()
                )
            )
