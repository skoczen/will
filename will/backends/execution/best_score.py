import imp
import logging
import traceback
import requests
import warnings

from will import settings
from will.decorators import require_settings
from will.plugin import Event
from will.utils import Bunch
from .base import ExecutionBackend


class BestScoreBackend(ExecutionBackend):

    def do_execute(self, message, option):

        # Question: do we need to do this via self.bot, or can we re-instantiate
        # the execution thread (and in the process, magically provide/handle self.message)?
        module = imp.load_source(option.context.plugin_info["parent_name"], option.context.plugin_info["parent_path"])
        cls = getattr(module, option.context.plugin_info["name"])
        # Do we need self.bot?
        instantiated_module = cls(message=message, bot=self.bot)
        method = getattr(instantiated_module, option.context.function_name)

        # live_listener = self.bot.message_listeners[option.context.full_method_name]
        thread_args = [message, ] + option.context["args"]

        self.execute(
            method,
            *thread_args,
            **option.context.search_matches
        )

    def _publish_fingerprint(self, option, message):
        return "%s - %s" % (option.context.plugin_info["full_module_name"], option.context.full_method_name)

    def handle_execution(self, message):
        published_list = []
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                had_one_reply = False
                logging.info("message.generation_options")
                logging.info(message.generation_options)
                top_score = -1
                for m in message.generation_options:
                    logging.debug(m)
                    if m.score > top_score:
                        top_score = m.score
                logging.debug("top_score")
                logging.debug(top_score)
                for m in message.generation_options:
                    if m.score >= top_score:
                        s = self._publish_fingerprint(m, message)
                        if not s in published_list:
                            published_list.append(s)
                            self.do_execute(message, m)
                            had_one_reply = True
                if not had_one_reply:
                    self.bot.pubsub.publish(
                        "message.no_response",
                        message.data,
                        reference_message=message.data.original_incoming_event
                    )

                return {}
            except:
                logging.critical(
                    "Error running %s.  \n\n%s\nContinuing...\n" % (
                        m.context.full_method_name,
                        traceback.format_exc()
                    )
                )
